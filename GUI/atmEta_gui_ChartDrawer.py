#ATM Modules
from GUI import atmEta_gui_HitBoxes, atmEta_gui_TextControl, atmEta_gui_AdvancedPygletGroups, atmEta_gui_Generals
import atmEta_Auxillaries
import atmEta_Analyzers
import atmEta_IPC
import atmEta_NeuralNetworks
import atmEta_Constants

#Python Modules
import pyglet
import time
import math
import random
import numpy
from datetime import datetime, timezone, tzinfo
import pprint
import termcolor
import torch
import scipy.ndimage

#Constants
_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT
_IPC_PRD_INVALIDADDRESS    = atmEta_IPC._PRD_INVALIDADDRESS
_IPC_FAR_INVALIDFUNCTIONID = atmEta_IPC._FAR_INVALIDFUNCTIONID

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

_EXPECTEDTEMPORALWIDTHS = {0:       60, #  1m
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

_MITYPES = atmEta_Analyzers.ANALYSIS_MITYPES
_SITYPES = atmEta_Analyzers.ANALYSIS_SITYPES
_NMAXLINES = {'SMA':        10,
              'WMA':        10,
              'EMA':        10,
              'PSAR':       5,
              'BOL':        10,
              'IVP':        None,
              'PIP':        None,
              'VOL':        5,
              'MMACDSHORT': 6,
              'MMACDLONG':  6,
              'DMIxADX':    5,
              'MFI':        5,
              'WOI':        3,
              'NES':        3}

_FULLDRAWSIGNALS = {'KLINE':       0b1,
                    'SMA':         0b1,
                    'WMA':         0b1,
                    'EMA':         0b1,
                    'PSAR':        0b1,
                    'BOL':         0b11,
                    'IVP':         0b11,
                    'PIP':         0b11111,
                    'VOL':         0b1,
                    'MMACDSHORT':  0b111,
                    'MMACDLONG':   0b111,
                    'DMIxADX':     0b1,
                    'MFI':         0b1,
                    'TRADELOG':    0b1}

_GD_DISPLAYBOX_GOFFSET                 = 50
_GD_DISPLAYBOX_LEFTSECTION_MINWIDTH    = 4600
_GD_DISPLAYBOX_RIGHTSECTION_WIDTH      = 800
_GD_DISPLAYBOX_AUXILLARYBAR_HEIGHT     = 350
_GD_DISPLAYBOX_SIVIEWER_HEIGHT         = 1000
_GD_DISPLAYBOX_KLINESPRICE_MINHEIGHT   = 2000
_GD_DISPLAYBOX_MAINGRIDTEMPORAL_HEIGHT = 350

_GD_OBJECT_MINWIDTH  = _GD_DISPLAYBOX_LEFTSECTION_MINWIDTH  + _GD_DISPLAYBOX_RIGHTSECTION_WIDTH      + _GD_DISPLAYBOX_GOFFSET #4600 + 800 + 50 = 5450
_GD_OBJECT_MINHEIGHT = _GD_DISPLAYBOX_KLINESPRICE_MINHEIGHT + _GD_DISPLAYBOX_MAINGRIDTEMPORAL_HEIGHT + _GD_DISPLAYBOX_GOFFSET #2000 + 350 + 50 = 2400

_GD_SETTINGSSUBPAGE_WIDTH     = 4250
_GD_SETTINGSSUBPAGE_MAXHEIGHT = 8500

_GD_DISPLAYBOX_KLINESPRICE_MINPIXELWIDTH = 0.75
_GD_DISPLAYBOX_KLINESPRICE_MAXPIXELWIDTH = 500
_GD_DISPLAYBOX_KLINESPRICE_HVR_MINMAGNITUDE = 1
_GD_DISPLAYBOX_KLINESPRICE_HVR_MAXMAGNITUDE = 100

_GD_DISPLAYBOX_HVR_BACKWARDBUFFERFACTOR = 0.25
_GD_DISPLAYBOX_HVR_FORWARDBUFFERFACTOR  = 0.25

_GD_DISPLAYBOX_VVR_MAGNITUDE_MIN = {'KLINESPRICE': 10}
_GD_DISPLAYBOX_VVR_MAGNITUDE_MAX = {'KLINESPRICE': 100}
for siViewerNumber in range (1, len(_SITYPES)+1):
    siViewerCode = 'SIVIEWER{:d}'.format(siViewerNumber)
    _GD_DISPLAYBOX_VVR_MAGNITUDE_MIN[siViewerCode] = 20
    _GD_DISPLAYBOX_VVR_MAGNITUDE_MAX[siViewerCode] = 100

_GD_DISPLAYBOX_GRID_VERTICALLINEPIXELINTERVAL = 150
_GD_DISPLAYBOX_GRID_VERTICALTEXTWIDTH         = 500
_GD_DISPLAYBOX_GRID_VERTICALTEXTHEIGHT        = 120

_GD_DISPLAYBOX_GRID_HORIZONTALLINEPIXELINTERVAL          = 75
_GD_DISPLAYBOX_GRID_HORIZONTALLINEPIXELINTERVAL_SIVIEWER = 25
_GD_DISPLAYBOX_GRID_HORIZONTALTEXTWIDTH                  = 500
_GD_DISPLAYBOX_GRID_HORIZONTALTEXTHEIGHT                 = 120
_GD_DISPLAYBOX_GUIDE_HORIZONTALTEXTHEIGHT                = 120

_TIMEINTERVAL_MOUSEINTERPRETATION_NS = 10e6
_TIMEINTERVAL_POSTDRAGWAITTIME       = 500e6
_TIMEINTERVAL_POSTSCROLLWAITTIME     = 500e6
_TIMEINTERVAL_POSHIGHLIGHTUPDATE     = 10e6

_TIMELIMIT_KLINESDRAWQUEUE_NS   = 10e6
_TIMELIMIT_RCLCGPROCESSING_NS   = 10e6
_TIMELIMIT_KLINESDRAWREMOVAL_NS = 10e6

_DRAWTARGETRAWNAMEEXCEPTION = set(['raw', 'raw_status'])

_GD_KLINESLOADINGGAUGEBAR_HEIGHT = 150

_TIMELIMIT_KLINESPROCESS_NS = 100e6

_ANALYSIS_GENERATIONORDER = atmEta_Analyzers.ANALYSIS_GENERATIONORDER

_KLINES_PREPSTATUS_WAITINGFIRSTSTREAM   = 0
_KLINES_PREPSTATUS_WAITINGDATAAVAILABLE = 1
_KLINES_PREPSTATUS_FETCHING             = 2
_KLINES_MAXFETCHLENGTH = 10000

_AUX_NANALYSISQUEUEDISPLAYUPDATEINTERVAL_NS = 200e6

AGGTRADESAMPLINGINTERVAL_S    = atmEta_Constants.AGGTRADESAMPLINGINTERVAL_S
BIDSANDASKSSAMPLINGINTERVAL_S = atmEta_Constants.BIDSANDASKSSAMPLINGINTERVAL_S
NMAXAGGTRADESSAMPLES          = atmEta_Constants.NMAXAGGTRADESSAMPLES
NMAXBIDSANDASKSSAMPLES        = atmEta_Constants.NMAXBIDSANDASKSSAMPLES
#'chartDrawer' --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class chartDrawer:
    #Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.window = kwargs['windowInstance']
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        #Group Order
        if (True):
            groupOrder = kwargs.get('groupOrder', None)
            if (groupOrder == None):
                self.group_0 = kwargs['group_0']
                self.group_1 = kwargs['group_1']
                self.group_2 = kwargs['group_2']
                self.group_3 = kwargs['group_3']
                self.group_4 = kwargs['group_4']
                self.group_5 = kwargs['group_5']
                #Hovered Descriptor
                self.group_hd0 = kwargs['group_20']
                #For Settings Subpage
                self.group_ss0 = kwargs['group_21']
                self.group_ss1 = kwargs['group_22']
                self.group_ss2 = kwargs['group_23']
                self.group_ss3 = kwargs['group_24']
                self.groupOrder = self.group_0.order
                self.parentCameraGroup = self.group_0
            else:
                self.groupOrder = groupOrder
                self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
                self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)
                self.group_2 = pyglet.graphics.Group(order = self.groupOrder+2)
                self.group_3 = pyglet.graphics.Group(order = self.groupOrder+3)
                self.group_4 = pyglet.graphics.Group(order = self.groupOrder+4)
                self.group_5 = pyglet.graphics.Group(order = self.groupOrder+5)
                #Hovered Descriptor
                self.group_hd0 = pyglet.graphics.Group(order = self.groupOrder+20)
                #For Settings Subpage
                self.group_ss_order = self.groupOrder+21
                self.parentCameraGroup = None

        #External Connections
        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        self.currentGUITheme = self.visualManager.getGUITheme()
        self.ipcA = kwargs['ipcA']
        
        #Interal Basic Configurations
        self.name = kwargs.get('name', None)
        if (self.name == None): self.objectConfig_preset = None
        else:                   self.objectConfig_preset = kwargs['guioConfig'].get(self.name, None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.style = kwargs.get('style', 'styleA')
        
        self.textStyle = kwargs.get('textStyle', 'default')
        self.effectiveTextStyle = self.visualManager.getTextStyle('chartDrawer_'+self.textStyle)
        for textStyleCode in self.effectiveTextStyle: self.effectiveTextStyle[textStyleCode]['font_size'] = 80*self.scaler
        self.chartDrawerType = kwargs['chartDrawerType']

        #DisplayBox Dimension Standards & Interaction Control Variables
        self.hitBox = dict()
        self.hitBox_Object = atmEta_gui_HitBoxes.hitBox_Rectangular(self.xPos, self.yPos, self.width, self.height)
        self.images = dict()
        self.frameSprites = dict()
        if (self.width  < _GD_OBJECT_MINWIDTH):  self.width  = _GD_OBJECT_MINWIDTH  
        if (self.height < _GD_OBJECT_MINHEIGHT): self.height = _GD_OBJECT_MINHEIGHT 
        #---Information Displayers, priority goes: KLINESVOLUME -> AUXILLARYBAR -> SIVIEWERS
        self.usableSIViewers = min([int((self.height-_GD_OBJECT_MINHEIGHT-(_GD_DISPLAYBOX_AUXILLARYBAR_HEIGHT+_GD_DISPLAYBOX_GOFFSET))/(_GD_DISPLAYBOX_SIVIEWER_HEIGHT+_GD_DISPLAYBOX_GOFFSET)), len(_SITYPES)])
        self.displayBox = {'AUXILLARYBAR': None,
                           'KLINESPRICE':       None, 'MAINGRID_KLINESPRICE': None,
                           'MAINGRID_TEMPORAL': None, 'SETTINGSBUTTONFRAME':  None}
        for siViewerIndex in range (len(_SITYPES)):
            self.displayBox['SIVIEWER'+str(siViewerIndex+1)]          = None
            self.displayBox['MAINGRID_SIVIEWER'+str(siViewerIndex+1)] = None
        self.displayBox_graphics = dict()
        for displayBoxName in self.displayBox: self.displayBox_graphics[displayBoxName] = dict()
        self.displayBox_graphics_visibleSIViewers = set()
        self.displayBox_VerticalSection_Order = list()
        self.displayBox_VisibleBoxes = list()
        self.__RCLCGReferences = list()
        self.__auxBarGUIOs = dict()

        #Kline Loading Display Elements
        if (True):
            self.images['KLINELOADINGCOVER'] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_klinesLoadingCover", self.width*self.scaler, self.height*self.scaler)
            self.frameSprites['KLINELOADINGCOVER'] = pyglet.sprite.Sprite(x = self.xPos*self.scaler, y = self.yPos*self.scaler, img = self.images['KLINELOADINGCOVER'][0], batch = self.batch, group = self.group_1)
            self.frameSprites['KLINELOADINGCOVER'].visible = False
            self.klinesLoadingGaugeBar = atmEta_gui_Generals.gaugeBar_typeA(windowInstance = self.window, batch = self.batch, scaler = self.scaler, imageManager = self.imageManager, audioManager = self.audioManager, visualManager = self.visualManager,
                                                                            xPos = self.xPos, yPos = self.yPos, width = 100, height = _GD_KLINESLOADINGGAUGEBAR_HEIGHT,
                                                                            style = 'styleA', align = 'horizontal', group_0 = self.group_2, group_1 = self.group_3, value = 0)
            self.klinesLoadingTextBox_perc = atmEta_gui_Generals.textBox_typeA(windowInstance = self.window, batch = self.batch, scaler = self.scaler, imageManager = self.imageManager, audioManager = self.audioManager, visualManager = self.visualManager,
                                                                               xPos = self.xPos, yPos = self.yPos, width = 100, height = _GD_KLINESLOADINGGAUGEBAR_HEIGHT,
                                                                               style = None, group_0 = self.group_4, group_1 = self.group_5, text = '', fontSize = 60)
            self.klinesLoadingTextBox = atmEta_gui_Generals.textBox_typeA(windowInstance = self.window, batch = self.batch, scaler = self.scaler, imageManager = self.imageManager, audioManager = self.audioManager, visualManager = self.visualManager,
                                                                          xPos = self.xPos, yPos = self.yPos, width = 100, height = 200,
                                                                          style = None, group_0 = self.group_2, group_1 = self.group_3, text = "", fontSize = 80)
            self.klinesLoadingGaugeBar.hide()
            self.klinesLoadingTextBox_perc.hide()
            self.klinesLoadingTextBox.hide()

        #Mouse Control Variables
        self.mouse_lastHoveredSection  = None; self.mouse_lastSelectedSection = None
        self.mouse_Dragged  = False; self.mouse_DragDX   = dict(); self.mouse_DragDY   = dict(); self.mouse_lastDragged_ns  = 0
        self.mouse_Scrolled = False; self.mouse_ScrollDX = dict(); self.mouse_ScrollDY = dict(); self.mouse_lastScrolled_ns = 0
        self.mouse_Event_lastRead    = None
        self.mouse_Event_lastPressed = None
        self.mouse_Event_lastInterpreted_ns = 0
        
        #Kline & Analysis Control Variables
        #---Descriptors
        self.currencySymbol = None
        self.intervalID     = 0
        self.mrktRegTS      = None
        self.currencyInfo   = None
        #---Data
        self.klines      = {'raw': dict(), 'raw_status': dict(), 'TRADELOG': dict()}
        self.bidsAndAsks = {'depth': dict(), 'WOI': dict()}
        self.aggTrades   = {'volumes': {'samples': list(), 'buy': 0, 'sell': 0}, 'NES': dict()}
        #---Internal Control
        self.analysisParams = dict()
        self.klines_fetchComplete = False
        self.klines_fetching      = False
        self.klines_drawQueue        = dict()
        self.klines_drawn            = dict()
        self.klines_drawRemovalQueue = set()
        self.__klines_drawerFunctions = {'KLINE':      self.__klineDrawer_KLINE,
                                         'SMA':        self.__klineDrawer_SMA,
                                         'WMA':        self.__klineDrawer_WMA,
                                         'EMA':        self.__klineDrawer_EMA,
                                         'PSAR':       self.__klineDrawer_PSAR,
                                         'BOL':        self.__klineDrawer_BOL,
                                         'IVP':        self.__klineDrawer_IVP,
                                         'PIP':        self.__klineDrawer_PIP,
                                         'VOL':        self.__klineDrawer_VOL,
                                         'MMACDSHORT': self.__klineDrawer_MMACDSHORT,
                                         'MMACDLONG':  self.__klineDrawer_MMACDLONG,
                                         'DMIxADX':    self.__klineDrawer_DMIxADX,
                                         'MFI':        self.__klineDrawer_MFI,
                                         'TRADELOG':   self.__klineDrawer_TRADELOG}

        self.bidsAndAsks_drawFlag             = False
        self.bidsAndAsks_WOI_oldestComputedS  = None
        self.bidsAndAsks_WOI_latestComputedS  = None
        self.bidsAndAsks_WOI_drawQueue        = dict()
        self.bidsAndAsks_WOI_drawn            = dict()
        self.bidsAndAsks_WOI_drawRemovalQueue = set()
        self.aggTrades_NES_oldestComputedS    = None
        self.aggTrades_NES_latestComputedS    = None
        self.aggTrades_NES_drawQueue          = dict()
        self.aggTrades_NES_drawn              = dict()
        self.aggTrades_NES_drawRemovalQueue   = set()

        self.siTypes_siViewerAlloc = dict()
        self.siTypes_analysisCodes = dict()
        for siType in _SITYPES:
            self.siTypes_siViewerAlloc[siType] = None   #Allocated SIViewer Number for the corresponding SI Type
            self.siTypes_analysisCodes[siType] = list() #Allocated Analysis Codes for the corresponding SI type
        
        #Settings Sub Page Setup
        if (True):
            self.settingsSubPages = dict()
            settingsSubPageList = ('MAIN',) + _MITYPES + _SITYPES
            self.settingsSubPage_Current = 'MAIN'
            self.settingsSubPage_Opened = False
            self.settingsButtonStatus = 'DEFAULT'
            settingsSubPage_effectiveHeight = self.height-100
            if (_GD_SETTINGSSUBPAGE_MAXHEIGHT < settingsSubPage_effectiveHeight): settingsSubPage_effectiveHeight = _GD_SETTINGSSUBPAGE_MAXHEIGHT
            if (groupOrder == None):
                for subPageName in settingsSubPageList:
                    self.settingsSubPages[subPageName] = atmEta_gui_Generals.subPageBox_typeA(windowInstance = self.window, batch = self.batch, scaler = self.scaler, guioConfig = kwargs['guioConfig'], sysFunctions = kwargs['sysFunctions'], imageManager = self.imageManager, audioManager = self.audioManager, visualManager = self.visualManager, ipcA = self.ipcA,
                                                                                              xPos = self.xPos+50, yPos = self.yPos+self.height-50-settingsSubPage_effectiveHeight, width = _GD_SETTINGSSUBPAGE_WIDTH, height = settingsSubPage_effectiveHeight, 
                                                                                              useScrollBar_V = True, useScrollBar_H = False,
                                                                                              group_0 = self.group_ss0, group_1 = self.group_ss1, group_2 = self.group_ss2, group_3 = self.group_ss3)
                    self.settingsSubPages[subPageName].hide()
            else:
                for subPageName in settingsSubPageList:
                    self.settingsSubPages[subPageName] = atmEta_gui_Generals.subPageBox_typeA(windowInstance = self.window, batch = self.batch, scaler = self.scaler, guioConfig = kwargs['guioConfig'], sysFunctions = kwargs['sysFunctions'], imageManager = self.imageManager, audioManager = self.audioManager, visualManager = self.visualManager, ipcA = self.ipcA,
                                                                                              xPos = self.xPos+50, yPos = self.yPos+self.height-50-settingsSubPage_effectiveHeight, width = _GD_SETTINGSSUBPAGE_WIDTH, height = settingsSubPage_effectiveHeight, 
                                                                                              useScrollBar_V = True, useScrollBar_H = False,
                                                                                              groupOrder = self.group_ss_order)
                    self.settingsSubPages[subPageName].hide()
            self.__configureSettingsSubPageObjects()

        #ViewRange & Grid Control
        self.gridColor       = self.visualManager.getFromColorTable('CHARTDRAWER_GRID')
        self.gridColor_Heavy = self.visualManager.getFromColorTable('CHARTDRAWER_GRIDHEAVY')
        self.guideColor      = self.visualManager.getFromColorTable('CHARTDRAWER_GUIDECONTENT')
        self.posHighlightColor_hovered  = self.visualManager.getFromColorTable('CHARTDRAWER_POSHOVERED')
        self.posHighlightColor_selected = self.visualManager.getFromColorTable('CHARTDRAWER_POSSELECTED')

        #<Horizontal ViewRange & Vertical Grid>
        #---Horizontal ViewRange
        self.expectedKlineTemporalWidth = 1500
        self.horizontalViewRangeWidth_min = None; self.horizontalViewRangeWidth_max = None
        self.horizontalViewRangeWidth_m = None;   self.horizontalViewRangeWidth_b = None
        self.horizontalViewRange = [None, None]
        self.horizontalViewRange_timestampsInViewRange  = set()
        self.horizontalViewRange_timestampsInBufferZone = set()
        self.checkVerticalExtremas_SIs = {'VOL':        self.__checkVerticalExtremas_VOL,
                                          'MMACDSHORT': self.__checkVerticalExtremas_MMACDSHORT,
                                          'MMACDLONG':  self.__checkVerticalExtremas_MMACDLONG,
                                          'DMIxADX':    self.__checkVerticalExtremas_DMIxADX,
                                          'MFI':        self.__checkVerticalExtremas_MFI,
                                          'NES':        self.__checkVerticalExtremas_NES,
                                          'WOI':        self.__checkVerticalExtremas_WOI}
        #---Horizontal Position Highlighter
        self.posHighlight_hoveredPos       = (None, None, None, None)
        self.posHighlight_updatedPositions = None
        self.posHighlight_selectedPos      = None
        self.posHighlight_lastUpdated_ns   = 0
        #---Vertical Grid
        self.verticalGrid_intervalID = 0
        self.verticalGrid_intervals = list()
        self.nMaxVerticalGridLines = None
        #<Vertical ViewRange & Horizontal Grid>
        #---Vertical ViewRange
        self.verticalViewRange_magnification = dict()
        self.verticalValue_min = dict()
        self.verticalValue_max = dict()
        self.verticalValue_loaded = dict()
        self.verticalViewRange = dict()
        self.verticalViewRange_precision = dict()
        self.verticalViewRange_magnification['KLINESPRICE'] = 100
        self.verticalValue_min['KLINESPRICE'] = 0
        self.verticalValue_max['KLINESPRICE'] = 100000
        self.verticalViewRange['KLINESPRICE'] = [self.verticalValue_min['KLINESPRICE'], self.verticalValue_max['KLINESPRICE']]
        self.verticalViewRange_precision['KLINESPRICE'] = 3
        for siViewerIndex in range (len(_SITYPES)):
            siViewerCode = 'SIVIEWER'+str(siViewerIndex+1)
            self.verticalViewRange_magnification[siViewerCode] = 100
            self.verticalValue_min[siViewerCode] = -100
            self.verticalValue_max[siViewerCode] =  100
            self.verticalValue_loaded[siViewerCode] = False
            self.verticalViewRange[siViewerCode] = [self.verticalValue_min[siViewerCode], self.verticalValue_max[siViewerCode]]
            self.verticalViewRange_precision[siViewerCode] = 3
        #---Horizontal Grid
        self.horizontalGridIntervals      = dict()
        self.horizontalGridIntervalHeight = dict()
        self.nMaxHorizontalGridLines = dict()
        self.horizontalGridIntervals['KLINESPRICE']      = list()
        self.horizontalGridIntervalHeight['KLINESPRICE'] = None
        self.nMaxHorizontalGridLines['KLINESPRICE']      = None
        for siViewerIndex in range (len(_SITYPES)):
            siViewerCode = 'SIVIEWER'+str(siViewerIndex+1)
            self.horizontalGridIntervals[siViewerCode]      = list()
            self.horizontalGridIntervalHeight[siViewerCode] = None
            self.nMaxHorizontalGridLines[siViewerCode]      = int((_GD_DISPLAYBOX_SIVIEWER_HEIGHT-_GD_DISPLAYBOX_GOFFSET*2)*self.scaler/_GD_DISPLAYBOX_GRID_HORIZONTALLINEPIXELINTERVAL_SIVIEWER)
        
        #Auxillaries
        self.__lastNumberOfAnalysisQueueDisplayUpdated = 0

        #Object Configuration
        self.sysFunc_editGUIOConfig = kwargs['sysFunctions']['EDITGUIOCONFIG']
        self.objectConfig = dict()
        self.__initializeObjectConfig()
        if (self.name in kwargs['guioConfig']): self.objectConfig = kwargs['guioConfig'][self.name]
        else:                                   self.__initializeObjectConfig()
        self.__matchGUIOsToConfig()
        self.__configureDisplayBoxes(onInit = True)
        
        #Object Status
        self.status = "DEFAULT"
        self.hidden = False

        #Chart Drawer Type Dependents
        self.analysisParams = dict()
        if ((self.chartDrawerType == 'CAVIEWER') or (self.chartDrawerType == 'TLVIEWER')): #Settings Subpage GUIOs Activation Setup 1
            #MAIN
            self.settingsSubPages['MAIN'].GUIOs["ANALYZER_ANALYSISRANGEBEG_RANGEINPUT"].deactivate()
            self.settingsSubPages['MAIN'].GUIOs["ANALYZER_ANALYSISRANGEEND_RANGEINPUT"].deactivate()
            self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].deactivate()
            #SMA
            for i in range (_NMAXLINES['SMA']):
                lineNumber = i+1
                self.settingsSubPages['SMA'].GUIOs["INDICATOR_SMA{:d}".format(lineNumber)].deactivate()
                self.settingsSubPages['SMA'].GUIOs["INDICATOR_SMA{:d}_INTERVALINPUT".format(lineNumber)].deactivate()
            #WMA
            for i in range (_NMAXLINES['WMA']):
                lineNumber = i+1
                self.settingsSubPages['WMA'].GUIOs["INDICATOR_WMA{:d}".format(lineNumber)].deactivate()
                self.settingsSubPages['WMA'].GUIOs["INDICATOR_WMA{:d}_INTERVALINPUT".format(lineNumber)].deactivate()
            #EMA
            for i in range (_NMAXLINES['EMA']):
                lineNumber = i+1
                self.settingsSubPages['EMA'].GUIOs["INDICATOR_EMA{:d}".format(lineNumber)].deactivate()
                self.settingsSubPages['EMA'].GUIOs["INDICATOR_EMA{:d}_INTERVALINPUT".format(lineNumber)].deactivate()
            #PSAR
            for i in range (_NMAXLINES['PSAR']):
                lineNumber = i+1
                self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}".format(lineNumber)].deactivate()
                self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_AF0INPUT".format(lineNumber)].deactivate()
                self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_AF+INPUT".format(lineNumber)].deactivate()
                self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_AFMAXINPUT".format(lineNumber)].deactivate()
            #BOL
            self.settingsSubPages['BOL'].GUIOs["INDICATOR_MATYPESELECTION"].deactivate()
            for i in range (_NMAXLINES['BOL']):
                lineNumber = i+1
                self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}".format(lineNumber)].deactivate()
                self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_INTERVALINPUT".format(lineNumber)].deactivate()
                self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_BANDWIDTHINPUT".format(lineNumber)].deactivate()
            #IVP
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_INTERVAL_INPUTTEXT"].deactivate()
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_GAMMAFACTOR_SLIDER"].deactivate()
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_DELTAFACTOR_SLIDER"].deactivate()
            #PIP
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_SWINGRANGE_SLIDER"].deactivate()
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_NNAALPHA_SLIDER"].deactivate()
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_NNABETA_SLIDER"].deactivate()
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALALPHA_SLIDER"].deactivate()
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALBETA_SLIDER"].deactivate()
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALNSAMPLES_INPUTTEXT"].deactivate()
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALSIGMA_INPUTTEXT"].deactivate()
            #VOL
            self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOLTYPESELECTION"].deactivate()
            self.settingsSubPages['VOL'].GUIOs["INDICATOR_MATYPESELECTION"].deactivate()
            for lineIndex in range (_NMAXLINES['VOL']):
                lineNumber = lineIndex+1
                self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}".format(lineNumber)].deactivate()
                self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_INTERVALINPUT".format(lineNumber)].deactivate()
            #MMACDSHORT
            self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_SIGNALINTERVALTEXTINPUT"].deactivate()
            for lineIndex in range (_NMAXLINES['MMACDSHORT']):
                lineNumber = lineIndex+1
                self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_MMACDMA{:d}".format(lineNumber)].deactivate()
                self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_MMACDMA{:d}_INTERVALINPUT".format(lineNumber)].deactivate()
            #MMACDLONG
            self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_SIGNALINTERVALTEXTINPUT"].deactivate()
            self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_MULTIPLIERTEXTINPUT"].deactivate()
            for lineIndex in range (_NMAXLINES['MMACDLONG']):
                lineNumber = lineIndex+1
                self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_MMACDMA{:d}".format(lineNumber)].deactivate()
                self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_MMACDMA{:d}_INTERVALINPUT".format(lineNumber)].deactivate()
            #DMIxADX
            for i in range (_NMAXLINES['DMIxADX']):
                lineNumber = i+1
                self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}".format(lineNumber)].deactivate()
                self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_INTERVALINPUT".format(lineNumber)].deactivate()
            #MFI
            for i in range (_NMAXLINES['MFI']):
                lineNumber = i+1
                self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}".format(lineNumber)].deactivate()
                self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_INTERVALINPUT".format(lineNumber)].deactivate()
            #WOI
            for i in range (_NMAXLINES['WOI']):
                lineNumber = i+1
                self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}".format(lineNumber)].deactivate()
                self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_SIGMAINPUT".format(lineNumber)].deactivate()
                self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_INTERVALINPUT".format(lineNumber)].deactivate()
            #NES
            for i in range (_NMAXLINES['NES']):
                lineNumber = i+1
                self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}".format(lineNumber)].deactivate()
                self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_SIGMAINPUT".format(lineNumber)].deactivate()
                self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_INTERVALINPUT".format(lineNumber)].deactivate()
        if ((self.chartDrawerType == 'CAVIEWER') or (self.chartDrawerType == 'ANALYZER')): #Settings Subpage GUIOs Activation Setup 2
            self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_TARGETSELECTION"].deactivate()
            self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_APPLYCOLOR"].deactivate()
            self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_R_SLIDER"].deactivate()
            self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_G_SLIDER"].deactivate()
            self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_B_SLIDER"].deactivate()
            self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_A_SLIDER"].deactivate()
            self.settingsSubPages['MAIN'].GUIOs["TRADELOGDISPLAY_SWITCH"].deactivate()
            self.settingsSubPages['MAIN'].GUIOs["TRADELOG_APPLYNEWSETTINGS"].deactivate()
        if (self.chartDrawerType == 'TLVIEWER'):                                           #Settings Subpage GUIOs Activation Setup 3
            self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_TARGETSELECTION"].deactivate()
            self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_APPLYCOLOR"].deactivate()
            self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_R_SLIDER"].deactivate()
            self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_G_SLIDER"].deactivate()
            self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_B_SLIDER"].deactivate()
            self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_A_SLIDER"].deactivate()
            self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSDISPLAY_SWITCH"].deactivate()
            self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKS_APPLYNEWSETTINGS"].deactivate()
        if (self.chartDrawerType == 'CAVIEWER'):
            self.intervalID = atmEta_Constants.KLINTERVAL
            self.currencyAnalysisCode = None
            self.currencyAnalysis     = None
            self.__setTarget_CAViewer(currencyAnalysisCode = None)
        elif (self.chartDrawerType == 'TLVIEWER'):
            self.intervalID = atmEta_Constants.KLINTERVAL
            self.simulationCode = None
            self.simulation     = None
            self.targetPrecisions = None
            self.simulationTradeLog = dict()
            self.simulationTradeLog_RID = None
            self.neuralNetworkConnectionDataRequestID = None
            self.neuralNetworkInstance                = None
            self.analysisToProcess_Sorted = list()
            self.analysisQueue_list = list()
            self.analysisQueue_set  = set()
            self.klines_targetFetchRange_original = None
            self.klines_targetFetchRange_current  = None
            self.klines_fetchRequestRID           = None
            self.caRegeneration_nAnalysis_initial = None
            self.__setTarget_TLViewer(target = None)
        elif (self.chartDrawerType == 'ANALYZER'):
            self.canStartAnalysis                     = False
            self.analyzingStream                      = False
            self.neuralNetworkConnectionDataRequestID = None
            self.neuralNetworkInstance                = None
            self.analysisToProcess_Sorted = list()
            self.analysisQueue_list = list()
            self.analysisQueue_set  = set()
            self.klines_targetFetchRange_original = None
            self.klines_targetFetchRange_current  = None
            self.klines_fetchRequestRID           = None
            #WOI Prep
            self.siTypes_analysisCodes['WOI'] = list()
            for _lIndex in range (_NMAXLINES['WOI']):
                _lNumber = _lIndex+1
                _woiType = "WOI_{:d}".format(_lNumber)
                if (self.objectConfig['WOI_{:d}_LineActive'.format(_lNumber)] == True):
                    self.siTypes_analysisCodes['WOI'].append(_woiType)
                    self.bidsAndAsks[_woiType] = dict()
                else:
                    if (_woiType in self.bidsAndAsks): del self.bidsAndAsks[_woiType]
            #NES Prep
            self.siTypes_analysisCodes['NES'] = list()
            for _lIndex in range (_NMAXLINES['NES']):
                _lNumber = _lIndex+1
                _nesType = "NES_{:d}".format(_lNumber)
                if (self.objectConfig['NES_{:d}_LineActive'.format(_lNumber)] == True):
                    self.siTypes_analysisCodes['NES'].append(_nesType)
                    self.aggTrades[_nesType] = dict()
                else:
                    if (_nesType in self.aggTrades): del self.aggTrades[_nesType]
            #Target Set
            self.__setTarget_Analyzer(currencySymbol = None)
    #Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Object Configuration & GUIO Initialization ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __configureSettingsSubPageObjects(self):
        subPageViewSpaceWidth = 4000
        #<MAIN>
        if (True):
            yPos_beg = 20000
            #Title
            self.settingsSubPages['MAIN'].addGUIO("TITLE_MAIN", atmEta_gui_Generals.passiveGraphics_wrapperTypeB, {'groupOrder': 0, 'xPos': 0, 'yPos': yPos_beg, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_CHARTSETTINGS')})
            #Main Indicators
            yPosPoint0 = yPos_beg-200
            self.settingsSubPages['MAIN'].addGUIO("TITLE_MAININDICATORS", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MAININDICATORS'), 'fontSize': 80})
            for i, miType in enumerate(_MITYPES):
                self.settingsSubPages['MAIN'].addGUIO("MAININDICATOR_{:s}".format(miType),      atmEta_gui_Generals.switch_typeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-350-350*i, 'width': 3500, 'height': 250, 'style': 'styleB', 'name': 'MAIN_INDICATORSWITCH_{:s}'.format(miType), 'text': miType, 'fontSize': 80, 'releaseFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['MAIN'].addGUIO("MAININDICATORSETUP_{:s}".format(miType), atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 3600, 'yPos': yPosPoint0-350-350*i, 'width':  400, 'height': 250, 'style': 'styleA', 'text': ">".format(miType), 'fontSize': 80, 'name': 'navButton_MI_{:s}'.format(miType), 'releaseFunction': self.__onSettingsNavButtonClick})
            #Sub Indicators
            yPosPoint1 = yPosPoint0-300-350*len(_MITYPES)
            self.settingsSubPages['MAIN'].addGUIO("TITLE_SUBINDICATORS", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SUBINDICATORS'), 'fontSize': 80})
            for i, siType in enumerate(_SITYPES):
                self.settingsSubPages['MAIN'].addGUIO("SUBINDICATOR_{:s}".format(siType),      atmEta_gui_Generals.switch_typeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350-350*i, 'width': 3500, 'height': 250, 'style': 'styleB', 'name': 'MAIN_INDICATORSWITCH_{:s}'.format(siType), 'text': siType, 'fontSize': 80, 'releaseFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['MAIN'].addGUIO("SUBINDICATORSETUP_{:s}".format(siType), atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 3600, 'yPos': yPosPoint1-350-350*i, 'width':  400, 'height': 250, 'style': 'styleA', 'text': ">", 'fontSize': 80, 'name': 'navButton_SI_{:s}'.format(siType), 'releaseFunction': self.__onSettingsNavButtonClick})
            #Sub Indicators Display
            yPosPoint2 = yPosPoint1-300-350*len(_SITYPES)
            self.settingsSubPages['MAIN'].addGUIO("TITLE_SUBINDICATORSDISPLAY", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SUBINDICATORDISPLAY'), 'fontSize': 80})
            siSelection = dict()
            for siType in _SITYPES: siSelection[siType] = {'text': siType}
            for i in range (len(_SITYPES)):
                siViewerNumber = i+1
                self.settingsSubPages['MAIN'].addGUIO("SUBINDICATOR_DISPLAYSWITCH{:d}".format(siViewerNumber),    atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint2-350-350*i, 'width': 1100, 'height': 250, 'style': 'styleB', 'name': 'MAIN_SIVIEWERDISPLAYSWITCH_{:d}'.format(siViewerNumber),    'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDICATOR{:d}'.format(siViewerNumber)), 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['MAIN'].addGUIO("SUBINDICATOR_DISPLAYSELECTION{:d}".format(siViewerNumber), atmEta_gui_Generals.selectionBox_typeB, {'groupOrder': 0, 'xPos': 1200, 'yPos': yPosPoint2-350-350*i, 'width': 2800, 'height': 250, 'style': 'styleA', 'name': 'MAIN_SIVIEWERDISPLAYSELECTION_{:d}'.format(siViewerNumber), 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_DISPLAYSELECTION{:d}".format(siViewerNumber)].setSelectionList(selectionList = siSelection, displayTargets = 'all')
            #Analyzer
            yPosPoint3 = yPosPoint2-300-350*len(_SITYPES)
            self.settingsSubPages['MAIN'].addGUIO("TITLE_ANALYZER", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint3, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_ANALYZER'), 'fontSize': 80})
            self.settingsSubPages['MAIN'].addGUIO("ANALYZER_ANALYSISRANGEBEG_TEXT",       atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint3- 350, 'width': 2200, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:ANALYSISRANGEBEG'), 'fontSize': 80})
            self.settingsSubPages['MAIN'].addGUIO("ANALYZER_ANALYSISRANGEBEG_RANGEINPUT", atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2300, 'yPos': yPosPoint3- 350, 'width': 1700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MAIN_ANALYSISRANGETEXTINPUTBOX', 'textUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MAIN'].addGUIO("ANALYZER_ANALYSISRANGEEND_TEXT",       atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint3- 700, 'width': 2200, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:ANALYSISRANGEEND'), 'fontSize': 80})
            self.settingsSubPages['MAIN'].addGUIO("ANALYZER_ANALYSISRANGEEND_RANGEINPUT", atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2300, 'yPos': yPosPoint3- 700, 'width': 1700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MAIN_ANALYSISRANGETEXTINPUTBOX', 'textUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MAIN'].addGUIO("ANALYZER_STARTANALYSIS_BUTTON",        atmEta_gui_Generals.button_typeA,       {'groupOrder': 0, 'xPos': 0,    'yPos': yPosPoint3-1050, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:STARTANALYSIS'), 'fontSize': 80, 'name': 'MAIN_STARTANALYSIS', 'releaseFunction': self.__onSettingsContentUpdate})
            #Trade Log
            yPosPoint4 = yPosPoint3-1350
            self.settingsSubPages['MAIN'].addGUIO("TITLE_TRADELOG",                atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos':  yPosPoint4, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_TRADELOG'), 'fontSize': 80})
            self.settingsSubPages['MAIN'].addGUIO("TRADELOGCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint4-350, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            self.settingsSubPages['MAIN'].addGUIO("TRADELOGCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB, {'groupOrder': 2, 'xPos':  700, 'yPos': yPosPoint4-350, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'TRADELOG_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MAIN'].addGUIO("TRADELOGCOLOR_LED",             atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2300, 'yPos': yPosPoint4-350, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['MAIN'].addGUIO("TRADELOGCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,       {'groupOrder': 0, 'xPos': 3350, 'yPos': yPosPoint4-350, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'TRADELOG_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                self.settingsSubPages['MAIN'].addGUIO("TRADELOGCOLOR_{:s}_TEXT".format(componentType),   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint4-700-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                self.settingsSubPages['MAIN'].addGUIO("TRADELOGCOLOR_{:s}_SLIDER".format(componentType), atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': yPosPoint4-700-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': 'TRADELOG_Color_{:s}'.format(componentType), 'valueUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['MAIN'].addGUIO("TRADELOGCOLOR_{:s}_VALUE".format(componentType),  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': yPosPoint4-700-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            yPosPoint5 = yPosPoint4-2100
            self.settingsSubPages['MAIN'].addGUIO("TRADELOGDISPLAY_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 0,    'yPos': yPosPoint5, 'width': 1600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYTRADELOG'), 'fontSize': 80})
            self.settingsSubPages['MAIN'].addGUIO("TRADELOGDISPLAY_SWITCH", atmEta_gui_Generals.switch_typeB,  {'groupOrder': 0, 'xPos': 1700, 'yPos': yPosPoint5, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'TRADELOG_DisplaySwitch', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MAIN'].addGUIO("TRADELOGCOLOR_BUY_LED",  atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 2300, 'yPos': yPosPoint5, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['MAIN'].addGUIO("TRADELOGCOLOR_SELL_LED", atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3200, 'yPos': yPosPoint5, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            lineSelections = {'BUY':  {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TRADELOG_BUY')},
                              'SELL': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TRADELOG_SELL')}}
            self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_TARGETSELECTION"].setSelectionList(lineSelections, displayTargets = 'all')
            self.settingsSubPages['MAIN'].addGUIO("TRADELOG_APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint5-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'TRADELOG_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            #Bids and Asks
            yPosPoint6 = yPosPoint5-650
            self.settingsSubPages['MAIN'].addGUIO("TITLE_BIDSANDASKS",                atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos':  yPosPoint6, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_BIDSANDASKS'), 'fontSize': 80})
            self.settingsSubPages['MAIN'].addGUIO("BIDSANDASKSCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint6-350, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            self.settingsSubPages['MAIN'].addGUIO("BIDSANDASKSCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB, {'groupOrder': 2, 'xPos':  700, 'yPos': yPosPoint6-350, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'BIDSANDASKS_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MAIN'].addGUIO("BIDSANDASKSCOLOR_LED",             atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2300, 'yPos': yPosPoint6-350, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['MAIN'].addGUIO("BIDSANDASKSCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,       {'groupOrder': 0, 'xPos': 3350, 'yPos': yPosPoint6-350, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'BIDSANDASKS_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                self.settingsSubPages['MAIN'].addGUIO("BIDSANDASKSCOLOR_{:s}_TEXT".format(componentType),   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint6-700-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                self.settingsSubPages['MAIN'].addGUIO("BIDSANDASKSCOLOR_{:s}_SLIDER".format(componentType), atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': yPosPoint6-700-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': 'BIDSANDASKS_Color_{:s}'.format(componentType), 'valueUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['MAIN'].addGUIO("BIDSANDASKSCOLOR_{:s}_VALUE".format(componentType),  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': yPosPoint6-700-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            yPosPoint7 = yPosPoint6-2100
            self.settingsSubPages['MAIN'].addGUIO("BIDSANDASKSDISPLAY_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 0,    'yPos': yPosPoint7, 'width': 1600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYBIDSANDASKS'), 'fontSize': 80})
            self.settingsSubPages['MAIN'].addGUIO("BIDSANDASKSDISPLAY_SWITCH", atmEta_gui_Generals.switch_typeB,  {'groupOrder': 0, 'xPos': 1700, 'yPos': yPosPoint7, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'BIDSANDASKS_DisplaySwitch', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MAIN'].addGUIO("BIDSANDASKSCOLOR_BIDS_LED", atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 2300, 'yPos': yPosPoint7, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['MAIN'].addGUIO("BIDSANDASKSCOLOR_ASKS_LED", atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3200, 'yPos': yPosPoint7, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            lineSelections = {'BIDS': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BIDSANDASKS_BIDS')},
                              'ASKS': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BIDSANDASKS_ASKS')}}
            self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_TARGETSELECTION"].setSelectionList(lineSelections, displayTargets = 'all')
            self.settingsSubPages['MAIN'].addGUIO("BIDSANDASKS_APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint7-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'BIDSANDASKS_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            #Aux Settings
            yPosPoint8 = yPosPoint7-700
            self.settingsSubPages['MAIN'].addGUIO("TITLE_AUX",                       atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos':  yPosPoint8,      'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_AUX'), 'fontSize': 80})
            self.settingsSubPages['MAIN'].addGUIO("AUX_KLINECOLORTYPE_TEXT",         atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos':  yPosPoint8- 350, 'width': 1750,                  'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:KLINECOLORTYPE'), 'fontSize': 80})
            self.settingsSubPages['MAIN'].addGUIO("AUX_KLINECOLORTYPE_SELECTIONBOX", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 1, 'xPos': 1850, 'yPos':  yPosPoint8- 350, 'width': 2150,                  'height': 250, 'style': 'styleA', 'name': 'MAIN_KLINECOLORTYPE_SELECTION', 'nDisplay': 5, 'fontSize': 80, 'expansionDir': 1, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MAIN'].addGUIO("AUX_TIMEZONE_TEXT",               atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos':  yPosPoint8- 700, 'width': 1750,                  'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TIMEZONE'), 'fontSize': 80})
            self.settingsSubPages['MAIN'].addGUIO("AUX_TIMEZONE_SELECTIONBOX",       atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1850, 'yPos':  yPosPoint8- 700, 'width': 2150,                  'height': 250, 'style': 'styleA', 'name': 'MAIN_TIMEZONE_SELECTION', 'nDisplay': 10, 'fontSize': 80, 'expansionDir': 1, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MAIN'].addGUIO("AUX_SAVECONFIGURATION",           atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 0,    'yPos':  yPosPoint8-1050, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SAVECONFIG'), 'fontSize': 80, 'name': 'MAIN_SAVECONFIG', 'releaseFunction': self.__onSettingsContentUpdate})
            #GUIO Setup
            self.settingsSubPages['MAIN'].GUIOs["AUX_KLINECOLORTYPE_SELECTIONBOX"].setSelectionList({1: {'text': 'TYPE1'}, 2: {'text': 'TYPE2'}}, displayTargets = 'all')
            timeZoneSelections = {'LOCAL': {'text': 'LOCAL'}}
            for hour in range (24): timeZoneSelections['UTC+{:d}'.format(hour)] = {'text': 'UTC+{:d}'.format(hour)}
            self.settingsSubPages['MAIN'].GUIOs["AUX_TIMEZONE_SELECTIONBOX"].setSelectionList(timeZoneSelections, displayTargets = 'all')
        #<SMA & WMA & EMA Settings>
        if (True):
            for miType in ('SMA', 'WMA', 'EMA'):
                self.settingsSubPages[miType].addGUIO("SUBPAGETITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MI_{:s}'.format(miType)), 'fontSize': 100})
                self.settingsSubPages[miType].addGUIO("NAGBUTTON",    atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width':                   400, 'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
                self.settingsSubPages[miType].addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
                self.settingsSubPages[miType].addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
                self.settingsSubPages[miType].addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': '{:s}_LineSelectionBox'.format(miType), 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages[miType].addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
                self.settingsSubPages[miType].addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': '{:s}_ApplyColor'.format(miType), 'releaseFunction': self.__onSettingsContentUpdate})
                for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                    self.settingsSubPages[miType].addGUIO("INDICATORCOLOR_{:s}_TEXT".format(componentType),   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                    self.settingsSubPages[miType].addGUIO("INDICATORCOLOR_{:s}_SLIDER".format(componentType), atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': '{:s}_Color_{:s}'.format(miType,componentType), 'valueUpdateFunction': self.__onSettingsContentUpdate})
                    self.settingsSubPages[miType].addGUIO("INDICATORCOLOR_{:s}_VALUE".format(componentType),  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
                self.settingsSubPages[miType].addGUIO("INDICATORINDEX_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 800, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
                self.settingsSubPages[miType].addGUIO("INDICATORINTERVAL_COLUMNTITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  900, 'yPos': 7550, 'width': 900, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
                self.settingsSubPages[miType].addGUIO("INDICATORWIDTH_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1900, 'yPos': 7550, 'width': 750, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
                self.settingsSubPages[miType].addGUIO("INDICATORCOLOR_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2750, 'yPos': 7550, 'width': 650, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
                self.settingsSubPages[miType].addGUIO("INDICATORDISPLAY_COLUMNTITLE",  atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
                maList = dict()
                for i in range (_NMAXLINES[miType]):
                    lineNumber = i+1
                    self.settingsSubPages[miType].addGUIO("INDICATOR_{:s}{:d}".format(miType,lineNumber),               atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*i, 'width': 800, 'height': 250, 'style': 'styleB', 'name': '{:s}_LineActivationSwitch_{:d}'.format(miType,lineNumber), 'text': '{:s} {:d}'.format(miType,lineNumber), 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                    self.settingsSubPages[miType].addGUIO("INDICATOR_{:s}{:d}_INTERVALINPUT".format(miType,lineNumber), atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  900, 'yPos': 7200-350*i, 'width': 900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': '{:s}_IntervalTextInputBox_{:d}'.format(miType,lineNumber), 'textUpdateFunction': self.__onSettingsContentUpdate})
                    self.settingsSubPages[miType].addGUIO("INDICATOR_{:s}{:d}_WIDTHINPUT".format(miType,lineNumber),    atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1900, 'yPos': 7200-350*i, 'width': 750, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': '{:s}_WidthTextInputBox_{:d}'.format(miType,lineNumber), 'textUpdateFunction': self.__onSettingsContentUpdate})
                    self.settingsSubPages[miType].addGUIO("INDICATOR_{:s}{:d}_LINECOLOR".format(miType,lineNumber),     atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2750, 'yPos': 7200-350*i, 'width': 650, 'height': 250, 'style': 'styleA', 'mode': True})
                    self.settingsSubPages[miType].addGUIO("INDICATOR_{:s}{:d}_DISPLAY".format(miType,lineNumber),       atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*i, 'width': 500, 'height': 250, 'style': 'styleA', 'name': '{:s}_DisplaySwitch_{:d}'.format(miType,lineNumber), 'releaseFunction': self.__onSettingsContentUpdate})
                    maList[str(lineNumber)] = {'text': "{:s} {:d}".format(miType, lineNumber)}
                self.settingsSubPages[miType].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = maList, displayTargets = 'all')
                self.settingsSubPages[miType].addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': 7200-350*(_NMAXLINES[miType]-1)-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': '{:s}_ApplySettings'.format(miType), 'releaseFunction': self.__onSettingsContentUpdate})
        #<PSAR Settings>
        if (True):
            self.settingsSubPages['PSAR'].addGUIO("SUBPAGETITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MI_PSAR'), 'fontSize': 100})
            self.settingsSubPages['PSAR'].addGUIO("NAGBUTTON",    atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            self.settingsSubPages['PSAR'].addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['PSAR'].addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            self.settingsSubPages['PSAR'].addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'PSAR_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['PSAR'].addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['PSAR'].addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'PSAR_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                self.settingsSubPages['PSAR'].addGUIO("INDICATORCOLOR_{:s}_TEXT".format(componentType),   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                self.settingsSubPages['PSAR'].addGUIO("INDICATORCOLOR_{:s}_SLIDER".format(componentType), atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': 'PSAR_Color_{:s}'.format(componentType), 'valueUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['PSAR'].addGUIO("INDICATORCOLOR_{:s}_VALUE".format(componentType),  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            self.settingsSubPages['PSAR'].addGUIO("INDICATORINDEX_COLUMNTITLE",        atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),            'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['PSAR'].addGUIO("INDICATORSTART_COLUMNTITLE",        atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  700, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:PSARSTART'),        'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['PSAR'].addGUIO("INDICATORACCELERATION_COLUMNTITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1300, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:PSARACCELERATION'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['PSAR'].addGUIO("INDICATORMAXIMUM_COLUMNTITLE",      atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1900, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:PSARMAXIMUM'),      'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['PSAR'].addGUIO("INDICATORSIZE_COLUMNTITLE",         atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2500, 'yPos': 7550, 'width': 400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SIZE'),             'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['PSAR'].addGUIO("INDICATORCOLOR_COLUMNTITLE",        atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3000, 'yPos': 7550, 'width': 400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),            'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['PSAR'].addGUIO("INDICATORDISPLAY_COLUMNTITLE",      atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),          'fontSize': 90, 'anchor': 'SW'})
            psarList = dict()
            for i in range (_NMAXLINES['PSAR']):
                lineNumber = i+1
                self.settingsSubPages['PSAR'].addGUIO("INDICATOR_PSAR{:d}".format(lineNumber),            atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*i, 'width': 600, 'height': 250, 'style': 'styleB', 'name': 'PSAR_LineActivationSwitch_{:d}'.format(lineNumber), 'text': 'PSAR {:d}'.format(lineNumber), 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['PSAR'].addGUIO("INDICATOR_PSAR{:d}_AF0INPUT".format(lineNumber),   atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  700, 'yPos': 7200-350*i, 'width': 500, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'PSAR_AF0TextInputBox_{:d}'.format(lineNumber),   'textUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['PSAR'].addGUIO("INDICATOR_PSAR{:d}_AF+INPUT".format(lineNumber),   atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1300, 'yPos': 7200-350*i, 'width': 500, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'PSAR_AF+TextInputBox_{:d}'.format(lineNumber),   'textUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['PSAR'].addGUIO("INDICATOR_PSAR{:d}_AFMAXINPUT".format(lineNumber), atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1900, 'yPos': 7200-350*i, 'width': 500, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'PSAR_AFMaxTextInputBox_{:d}'.format(lineNumber), 'textUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['PSAR'].addGUIO("INDICATOR_PSAR{:d}_WIDTHINPUT".format(lineNumber), atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2500, 'yPos': 7200-350*i, 'width': 400, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'PSAR_WidthTextInputBox_{:d}'.format(lineNumber), 'textUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['PSAR'].addGUIO("INDICATOR_PSAR{:d}_LINECOLOR".format(lineNumber),  atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 3000, 'yPos': 7200-350*i, 'width': 400, 'height': 250, 'style': 'styleA', 'mode': True})
                self.settingsSubPages['PSAR'].addGUIO("INDICATOR_PSAR{:d}_DISPLAY".format(lineNumber),    atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*i, 'width': 500, 'height': 250, 'style': 'styleA', 'name': 'PSAR_DisplaySwitch_{:d}'.format(lineNumber), 'releaseFunction': self.__onSettingsContentUpdate})
                psarList[str(lineNumber)] = {'text': "PSAR {:d}".format(lineNumber)}
            yPosPoint0 = 7200-350*(_NMAXLINES['PSAR']-1)
            self.settingsSubPages['PSAR'].addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'PSAR_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['PSAR'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = psarList, displayTargets = 'all')
        #<BOL Settings>
        if (True):
            self.settingsSubPages['BOL'].addGUIO("SUBPAGETITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MI_BOL'), 'fontSize': 100})
            self.settingsSubPages['BOL'].addGUIO("NAGBUTTON",    atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            self.settingsSubPages['BOL'].addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['BOL'].addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            self.settingsSubPages['BOL'].addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'BOL_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['BOL'].addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['BOL'].addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'BOL_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                self.settingsSubPages['BOL'].addGUIO("INDICATORCOLOR_{:s}_TEXT".format(componentType),   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                self.settingsSubPages['BOL'].addGUIO("INDICATORCOLOR_{:s}_SLIDER".format(componentType), atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': 'BOL_Color_{:s}'.format(componentType), 'valueUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['BOL'].addGUIO("INDICATORCOLOR_{:s}_VALUE".format(componentType),  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            self.settingsSubPages['BOL'].addGUIO("INDICATOR_BLOCKTITLE_MATYPE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['BOL'].addGUIO("INDICATOR_MATYPETEXT",        atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1550, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE'), 'fontSize': 80})
            self.settingsSubPages['BOL'].addGUIO("INDICATOR_MATYPESELECTION",   atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1650, 'yPos': 7200, 'width':                  2350, 'height': 250, 'style': 'styleA', 'name': 'BOL_MATypeSelection', 'nDisplay': 3, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            maTypes = {'SMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_SMA')},
                       'WMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_WMA')},
                       'EMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_EMA')}}
            self.settingsSubPages['BOL'].GUIOs["INDICATOR_MATYPESELECTION"].setSelectionList(selectionList = maTypes, displayTargets = 'all')
            self.settingsSubPages['BOL'].addGUIO("INDICATORINDEX_COLUMNTITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 800, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),         'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['BOL'].addGUIO("INDICATORINTERVAL_COLUMNTITLE",  atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  900, 'yPos': 6850, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVALSHORT'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['BOL'].addGUIO("INDICATORBANDWIDTH_COLUMNTITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1600, 'yPos': 6850, 'width': 550, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BANDWIDTH'),     'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['BOL'].addGUIO("INDICATORWIDTH_COLUMNTITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2250, 'yPos': 6850, 'width': 550, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),         'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['BOL'].addGUIO("INDICATORCOLOR_COLUMNTITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2900, 'yPos': 6850, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),         'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['BOL'].addGUIO("INDICATORDISPLAY_COLUMNTITLE",   atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6850, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),       'fontSize': 90, 'anchor': 'SW'})
            bolList = dict()
            for i in range (_NMAXLINES['BOL']):
                lineNumber = i+1
                self.settingsSubPages['BOL'].addGUIO("INDICATOR_BOL{:d}".format(lineNumber),                atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6500-350*i, 'width': 800, 'height': 250, 'style': 'styleB', 'name': 'BOL_LineActivationSwitch_{:d}'.format(lineNumber), 'text': 'BOL {:d}'.format(lineNumber), 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['BOL'].addGUIO("INDICATOR_BOL{:d}_INTERVALINPUT".format(lineNumber),  atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  900, 'yPos': 6500-350*i, 'width': 600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'BOL_IntervalTextInputBox_{:d}'.format(lineNumber),  'textUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['BOL'].addGUIO("INDICATOR_BOL{:d}_BANDWIDTHINPUT".format(lineNumber), atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1600, 'yPos': 6500-350*i, 'width': 550, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'BOL_BandWidthTextInputBox_{:d}'.format(lineNumber), 'textUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['BOL'].addGUIO("INDICATOR_BOL{:d}_WIDTHINPUT".format(lineNumber),     atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2250, 'yPos': 6500-350*i, 'width': 550, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'BOL_WidthTextInputBox_{:d}'.format(lineNumber),     'textUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['BOL'].addGUIO("INDICATOR_BOL{:d}_LINECOLOR".format(lineNumber),      atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2900, 'yPos': 6500-350*i, 'width': 500, 'height': 250, 'style': 'styleA', 'mode': True})
                self.settingsSubPages['BOL'].addGUIO("INDICATOR_BOL{:d}_DISPLAY".format(lineNumber),        atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500-350*i, 'width': 500, 'height': 250, 'style': 'styleA', 'name': 'BOL_DisplaySwitch_{:d}'.format(lineNumber), 'releaseFunction': self.__onSettingsContentUpdate})
                bolList[str(lineNumber)] = {'text': "BOL {:d}".format(lineNumber)}
            yPosPoint0 = 6500-350*(_NMAXLINES['BOL']-1)
            self.settingsSubPages['BOL'].addGUIO("INDICATOR_BLOCKTITLE_DISPLAYCONTENTS",      atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYCONTENTS'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['BOL'].addGUIO("INDICATOR_DISPLAYCONTENTS_BOLCENTERTEXT",   atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 700, 'width':                  3400, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYBOLCENTER'), 'fontSize': 80})
            self.settingsSubPages['BOL'].addGUIO("INDICATOR_DISPLAYCONTENTS_BOLCENTERSWITCH", atmEta_gui_Generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint0- 700, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'BOL_DisplayContentsSwitch_BolCenter', 'releaseFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['BOL'].addGUIO("INDICATOR_DISPLAYCONTENTS_BOLBANDTEXT",     atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-1050, 'width':                  3400, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYBOLBAND'), 'fontSize': 80})
            self.settingsSubPages['BOL'].addGUIO("INDICATOR_DISPLAYCONTENTS_BOLBANDSWITCH",   atmEta_gui_Generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint0-1050, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'BOL_DisplayContentsSwitch_BolBand', 'releaseFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['BOL'].addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-1400, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'BOL_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['BOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = bolList, displayTargets = 'all')
        #<IVP Settings>
        if (True):
            self.settingsSubPages['IVP'].addGUIO("SUBPAGETITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MI_IVP'), 'fontSize': 100})
            self.settingsSubPages['IVP'].addGUIO("NAGBUTTON",    atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            self.settingsSubPages['IVP'].addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['IVP'].addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            self.settingsSubPages['IVP'].addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width':                  1500, 'height': 250, 'style': 'styleA', 'name': 'IVP_LineSelectionBox', 'nDisplay': 9, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['IVP'].addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':                   950, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['IVP'].addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':                   650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'IVP_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                self.settingsSubPages['IVP'].addGUIO("INDICATORCOLOR_{:s}_TEXT".format(componentType),   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                self.settingsSubPages['IVP'].addGUIO("INDICATORCOLOR_{:s}_SLIDER".format(componentType), atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': 'IVP_Color_{:s}'.format(componentType), 'valueUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['IVP'].addGUIO("INDICATORCOLOR_{:s}_VALUE".format(componentType),  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ivpLineTargets = {'VPLP':  {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLP')},
                              'VPLPB': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLPB')}}
            self.settingsSubPages['IVP'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = ivpLineTargets, displayTargets = 'all')
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_BLOCKTITLE_IVPDISPLAY", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPDISPLAY'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_VPLP_DISPLAYTEXT",             atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLPDISPLAY'), 'fontSize': 80})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_VPLP_DISPLAYSWITCH",           atmEta_gui_Generals.switch_typeB,  {'groupOrder': 0, 'xPos': 1900, 'yPos': 7200, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'IVP_DisplaySwitch_VPLP', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_VPLP_COLORTEXT",               atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 2500, 'yPos': 7200, 'width':  700, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_VPLP_COLOR",                   atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3300, 'yPos': 7200, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_VPLP_DISPLAYWIDTHTEXT",        atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYWIDTH'), 'fontSize': 80})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_VPLP_DISPLAYWIDTHSLIDER",      atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos': 1300, 'yPos': 6900, 'width': 2000, 'height': 150, 'style': 'styleA', 'name': 'IVP_DisplayWidthSlider_VPLP', 'valueUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_VPLP_DISPLAYWIDTHVALUETEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3400, 'yPos': 6850, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_VPLPB_DISPLAYTEXT",            atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 6500, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLPBDISPLAY'), 'fontSize': 80})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_VPLPB_DISPLAYSWITCH",          atmEta_gui_Generals.switch_typeB,  {'groupOrder': 0, 'xPos': 1900, 'yPos': 6500, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'IVP_DisplaySwitch_VPLPB', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_VPLPB_COLORTEXT",              atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 2500, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_VPLPB_COLOR",                  atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3300, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_VPLPB_DISPLAYREGIONTEXT",      atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 6150, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYREGION'), 'fontSize': 80})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_VPLPB_DISPLAYREGIONSLIDER",    atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos': 1400, 'yPos': 6200, 'width': 1800, 'height': 150, 'style': 'styleA', 'name': 'IVP_VPLPBDisplayRegion', 'valueUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_VPLPB_DISPLAYREGIONVALUETEXT", atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 6150, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_BLOCKTITLE_IVPPARAMS", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': 5800, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPPARAMS'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_INTERVAL_DISPLAYTEXT",    atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 5450, 'width': 1900, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 80})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_INTERVAL_INPUTTEXT",      atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2000, 'yPos': 5450, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'IVP_Interval', 'textUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_GAMMAFACTOR_DISPLAYTEXT", atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 5100, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPGAMMAFACTOR'), 'fontSize': 80})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_GAMMAFACTOR_SLIDER",      atmEta_gui_Generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1100, 'yPos': 5150, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_GammaFactor', 'valueUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_GAMMAFACTOR_VALUETEXT",   atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': 5100, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_DELTAFACTOR_DISPLAYTEXT", atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 4750, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPDELTAFACTOR'), 'fontSize': 80})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_DELTAFACTOR_SLIDER",      atmEta_gui_Generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1100, 'yPos': 4800, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_DeltaFactor', 'valueUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['IVP'].addGUIO("INDICATOR_DELTAFACTOR_VALUETEXT",   atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': 4750, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.settingsSubPages['IVP'].addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': 4400, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'IVP_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
        #<PIP Settings>
        if (True):
            self.settingsSubPages['PIP'].addGUIO("SUBPAGETITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MI_PIP'), 'fontSize': 100})
            self.settingsSubPages['PIP'].addGUIO("NAGBUTTON",    atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            self.settingsSubPages['PIP'].addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['PIP'].addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'PIP_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['PIP'].addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['PIP'].addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'PIP_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                self.settingsSubPages['PIP'].addGUIO("INDICATORCOLOR_{:s}_TEXT".format(componentType),   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                self.settingsSubPages['PIP'].addGUIO("INDICATORCOLOR_{:s}_SLIDER".format(componentType), atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': 'PIP_Color_{:s}'.format(componentType), 'valueUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['PIP'].addGUIO("INDICATORCOLOR_{:s}_VALUE".format(componentType),  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80}) #VIP
            pipLineTargets = {'SWING':            {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SWING')},
                              'NNASIGNAL+':       {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:NNASIGNAL+')},
                              'NNASIGNAL-':       {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:NNASIGNAL-')},
                              'WOISIGNAL+':       {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WOISIGNAL+')},
                              'WOISIGNAL-':       {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WOISIGNAL-')},
                              'NESSIGNAL+':       {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:NESSIGNAL+')},
                              'NESSIGNAL-':       {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:NESSIGNAL-')},
                              'CLASSICALSIGNAL+': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:CLASSICALSIGNAL+')},
                              'CLASSICALSIGNAL-': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:CLASSICALSIGNAL-')}}
            self.settingsSubPages['PIP'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = pipLineTargets, displayTargets = 'all')
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_BLOCKTITLE_PIPDISPLAY", atmEta_gui_Generals.passiveGraphics_wrapperTypeC,      {'groupOrder': 0, 'xPos': 0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:PIPDISPLAY'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_DISPLAYSWING_TEXT",                    atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width': 1600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYSWING'), 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_SWING_DISPLAYSWITCH",                  atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 1700, 'yPos': 7200, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'PIP_DisplaySwitch_Swing', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_SWING_COLOR",                          atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2300, 'yPos': 7200, 'width': 1700, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_DISPLAYNNASIGNAL_TEXT",                atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 1600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYNNASIGNAL'), 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_NNASIGNAL_DISPLAYSWITCH",              atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 1700, 'yPos': 6850, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'PIP_DisplaySwitch_NNASignal', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_NNASIGNAL+_COLOR",                     atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2300, 'yPos': 6850, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_NNASIGNAL-_COLOR",                     atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 3200, 'yPos': 6850, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_DISPLAYWOISIGNAL_TEXT",                atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 6500, 'width': 1600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYWOISIGNAL'), 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_WOISIGNAL_DISPLAYSWITCH",              atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 1700, 'yPos': 6500, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'PIP_DisplaySwitch_WOISignal', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_WOISIGNAL+_COLOR",                     atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2300, 'yPos': 6500, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_WOISIGNAL-_COLOR",                     atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 3200, 'yPos': 6500, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_DISPLAYNESSIGNAL_TEXT",                atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 6150, 'width': 1600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYNESSIGNAL'), 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_NESSIGNAL_DISPLAYSWITCH",              atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 1700, 'yPos': 6150, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'PIP_DisplaySwitch_NESSignal', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_NESSIGNAL+_COLOR",                     atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2300, 'yPos': 6150, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_NESSIGNAL-_COLOR",                     atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 3200, 'yPos': 6150, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_DISPLAYCLASSICALSIGNAL_TEXT",          atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 5800, 'width': 1600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYCLASSICALSIGNAL'), 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_CLASSICALSIGNAL_DISPLAYSWITCH",        atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 1700, 'yPos': 5800, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'PIP_DisplaySwitch_ClassicalSignal', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_CLASSICALSIGNAL+_COLOR",               atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2300, 'yPos': 5800, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_CLASSICALSIGNAL-_COLOR",               atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 3200, 'yPos': 5800, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_CLASSICALSIGNAL_DISPLAYTYPETITLETEXT", atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 5450, 'width': 1600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:CLASSICALSIGNALDISPLAYTYPE'), 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_CLASSICALSIGNAL_DISPLAYTYPESELECTION", atmEta_gui_Generals.selectionBox_typeB, {'groupOrder': 2, 'xPos': 1700, 'yPos': 5450, 'width': 2300, 'height': 250, 'style': 'styleA', 'name': 'PIP_DisplayType_ClassicalSignal', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            _csSignalDisplayTypes = {'UNFILTERED': {'text': 'UNFILTERED'},
                                     'FILTERED':   {'text': 'FILTERED'}}
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALSIGNAL_DISPLAYTYPESELECTION"].setSelectionList(selectionList = _csSignalDisplayTypes, displayTargets = 'all')
            _yPos = 5100
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_BLOCKTITLE_PIPSETTINGS", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPos, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:PIPSETTINGS'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_SWINGRANGE_TITLETEXT",                     atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': _yPos- 350, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SWINGRANGE'), 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_SWINGRANGE_SLIDER",                        atmEta_gui_Generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1300, 'yPos': _yPos- 300, 'width': 1900, 'height': 150, 'style': 'styleA', 'name': 'PIP_SwingRange', 'valueUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_SWINGRANGE_VALUETEXT",                     atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': _yPos- 350, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_NEURALNETWORKCODE_TITLETEXT",              atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': _yPos- 700, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:NEURALNETWORKCODE'), 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_NEURALNETWORKCODE_SELECTIONBOX",           atmEta_gui_Generals.selectionBox_typeB, {'groupOrder': 2, 'xPos': 1300, 'yPos': _yPos- 700, 'width': 1900, 'height': 250, 'style': 'styleA', 'name': 'PIP_NeuralNetworkCode', 'nDisplay': 9, 'fontSize': 80, 'expansionDir': 0, 'showIndex': True, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_NEURALNETWORKCODE_RELEASEBUTTON",          atmEta_gui_Generals.button_typeA,       {'groupOrder': 0, 'xPos': 3300, 'yPos': _yPos- 700, 'width':  700, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:RELEASE'), 'fontSize': 80, 'name': 'PIP_NeuralNetworkCodeRelease', 'releaseFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_NEURALNETWORKCODE_VALUETEXT",              atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 1300, 'yPos': _yPos- 700, 'width': 2700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_NNAALPHA_TITLETEXT",                       atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': _yPos-1050, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:NNAALPHA'), 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_NNAALPHA_SLIDER",                          atmEta_gui_Generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1300, 'yPos': _yPos-1000, 'width': 1900, 'height': 150, 'style': 'styleA', 'name': 'PIP_NNAAlpha', 'valueUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_NNAALPHA_VALUETEXT",                       atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': _yPos-1050, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_NNABETA_TITLETEXT",                        atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': _yPos-1400, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:NNABETA'), 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_NNABETA_SLIDER",                           atmEta_gui_Generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1300, 'yPos': _yPos-1350, 'width': 1900, 'height': 150, 'style': 'styleA', 'name': 'PIP_NNABeta', 'valueUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_NNABETA_VALUETEXT",                        atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': _yPos-1400, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_CLASSICALALPHA_TITLETEXT",                 atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': _yPos-1750, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:CLASSICALALPHA'), 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_CLASSICALALPHA_SLIDER",                    atmEta_gui_Generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1300, 'yPos': _yPos-1700, 'width': 1900, 'height': 150, 'style': 'styleA', 'name': 'PIP_ClassicalAlpha', 'valueUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_CLASSICALALPHA_VALUETEXT",                 atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': _yPos-1750, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_CLASSICALBETA_TITLETEXT",                  atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': _yPos-2100, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:CLASSICALBETA'), 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_CLASSICALBETA_SLIDER",                     atmEta_gui_Generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1300, 'yPos': _yPos-2050, 'width': 1900, 'height': 150, 'style': 'styleA', 'name': 'PIP_ClassicalBeta', 'valueUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_CLASSICALBETA_VALUETEXT",                  atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': _yPos-2100, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_CLASSICALNSAMPLES_DISPLAYTEXT",            atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': _yPos-2450, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:CLASSICALNSAMPLES'), 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_CLASSICALNSAMPLES_INPUTTEXT",              atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1300, 'yPos': _yPos-2450, 'width':  650, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'PIP_ClassicalNSamples', 'textUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_CLASSICALSIGMA_DISPLAYTEXT",               atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 2050, 'yPos': _yPos-2450, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:CLASSICALSIGMA'), 'fontSize': 80})
            self.settingsSubPages['PIP'].addGUIO("INDICATOR_CLASSICALSIGMA_INPUTTEXT",                 atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 3350, 'yPos': _yPos-2450, 'width':  650, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'PIP_ClassicalSigma', 'textUpdateFunction': self.__onSettingsContentUpdate})
            _yPos = _yPos-2800
            self.settingsSubPages['PIP'].addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPos, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'PIP_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
        #<VOL Settings>
        if (True):
            self.settingsSubPages['VOL'].addGUIO("SUBPAGETITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_VOL'), 'fontSize': 100})
            self.settingsSubPages['VOL'].addGUIO("NAGBUTTON",    atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            self.settingsSubPages['VOL'].addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['VOL'].addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            self.settingsSubPages['VOL'].addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'VOL_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['VOL'].addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['VOL'].addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'VOL_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                self.settingsSubPages['VOL'].addGUIO("INDICATORCOLOR_{:s}_TEXT".format(componentType),   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                self.settingsSubPages['VOL'].addGUIO("INDICATORCOLOR_{:s}_SLIDER".format(componentType), atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': 'VOL_Color_{:s}'.format(componentType), 'valueUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['VOL'].addGUIO("INDICATORCOLOR_{:s}_VALUE".format(componentType),  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            self.settingsSubPages['VOL'].addGUIO("INDICATORINDEX_BLOCKTITLE_MA",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLSETTINGS'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['VOL'].addGUIO("INDICATOR_VOLTYPETEXT",      atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE'), 'fontSize': 80})
            self.settingsSubPages['VOL'].addGUIO("INDICATOR_VOLTYPESELECTION", atmEta_gui_Generals.selectionBox_typeB, {'groupOrder': 2, 'xPos': 1900, 'yPos': 7200, 'width': 2100, 'height': 250, 'style': 'styleA', 'name': 'VOL_VolTypeSelection', 'nDisplay': 4, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            volTypes = {'BASE':    {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE_BASE')},
                        'QUOTE':   {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE_QUOTE')},
                        'BASETB':  {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE_BASETB')},
                        'QUOTETB': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE_QUOTETB')}}
            self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOLTYPESELECTION"].setSelectionList(selectionList = volTypes, displayTargets = 'all')
            self.settingsSubPages['VOL'].addGUIO("INDICATOR_MATYPETEXT",       atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE'), 'fontSize': 80})
            self.settingsSubPages['VOL'].addGUIO("INDICATOR_MATYPESELECTION",  atmEta_gui_Generals.selectionBox_typeB, {'groupOrder': 2, 'xPos': 1900, 'yPos': 6850, 'width': 2100, 'height': 250, 'style': 'styleA', 'name': 'VOL_MATypeSelection', 'nDisplay': 3, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            maTypes = {'SMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_SMA')},
                       'WMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_WMA')},
                       'EMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_EMA')}}
            self.settingsSubPages['VOL'].GUIOs["INDICATOR_MATYPESELECTION"].setSelectionList(selectionList = maTypes, displayTargets = 'all')
            self.settingsSubPages['VOL'].addGUIO("INDICATORINDEX_COLUMNTITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6500, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['VOL'].addGUIO("INDICATORINTERVAL_COLUMNTITLE",  atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['VOL'].addGUIO("INDICATORWIDTH_COLUMNTITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1900, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['VOL'].addGUIO("INDICATORCOLOR_COLUMNTITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2700, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['VOL'].addGUIO("INDICATORDISPLAY_COLUMNTITLE",   atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
            volMAList = dict()
            for i in range (_NMAXLINES['VOL']):
                lineNumber = i+1
                self.settingsSubPages['VOL'].addGUIO("INDICATOR_VOL{:d}".format(lineNumber),               atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6150-350*i, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': 'VOL_LineActivationSwitch_{:d}'.format(lineNumber), 'text': 'VOLMA{:d}'.format(lineNumber), 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['VOL'].addGUIO("INDICATOR_VOL{:d}_INTERVALINPUT".format(lineNumber), atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6150-350*i, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'VOL_IntervalTextInputBox_{:d}'.format(lineNumber), 'textUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['VOL'].addGUIO("INDICATOR_VOL{:d}_WIDTHINPUT".format(lineNumber),    atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1900, 'yPos': 6150-350*i, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'VOL_WidthTextInputBox_{:d}'.format(lineNumber), 'textUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['VOL'].addGUIO("INDICATOR_VOL{:d}_LINECOLOR".format(lineNumber),     atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2700, 'yPos': 6150-350*i, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
                self.settingsSubPages['VOL'].addGUIO("INDICATOR_VOL{:d}_DISPLAY".format(lineNumber),       atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6150-350*i, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'VOL_DisplaySwitch_{:d}'.format(lineNumber), 'releaseFunction': self.__onSettingsContentUpdate})
                volMAList[str(lineNumber)] = {'text': "VOLMA {:d}".format(lineNumber)}
            yPosPoint0 = 6150-350*(_NMAXLINES['VOL']-1)
            self.settingsSubPages['VOL'].addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'VOL_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['VOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = volMAList, displayTargets = 'all')
        #<MMACDSHORT Settings>
        if (True):
            self.settingsSubPages['MMACDSHORT'].addGUIO("SUBPAGETITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_MMACDSHORT'), 'fontSize': 100})
            self.settingsSubPages['MMACDSHORT'].addGUIO("NAGBUTTON",    atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':                   550, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width':                  1500, 'height': 250, 'style': 'styleA', 'name': 'MMACDSHORT_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':                   950, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':                   650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'MMACDSHORT_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATORCOLOR_{:s}_TEXT".format(componentType),   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATORCOLOR_{:s}_SLIDER".format(componentType), atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': 'MMACDSHORT_Color_{:s}'.format(componentType), 'valueUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATORCOLOR_{:s}_VALUE".format(componentType),  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            mmacdLineTargets = {'MMACD':      {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDMMACD')},
                                'SIGNAL':     {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNAL')},
                                'HISTOGRAM+': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAM+')},
                                'HISTOGRAM-': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAM-')}}
            self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = mmacdLineTargets, displayTargets = 'all')
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_BLOCKTITLE_DISPLAY",       atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDDISPLAY'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_MMACD_DISPLAYTEXT",        atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDMMACDDISPLAY'), 'fontSize': 80})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_MMACD_DISPLAYSWITCH",      atmEta_gui_Generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 1600, 'yPos': 7200, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACDSHORT_DisplaySwitch_MMACD', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_MMACD_COLORTEXT",          atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos': 2200, 'yPos': 7200, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_MMACD_COLOR",              atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2900, 'yPos': 7200, 'width':                  1100, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_SIGNAL_DISPLAYTEXT",       atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNALDISPLAY'), 'fontSize': 80})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_SIGNAL_DISPLAYSWITCH",     atmEta_gui_Generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 1600, 'yPos': 6850, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACDSHORT_DisplaySwitch_SIGNAL', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_SIGNAL_COLORTEXT",         atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos': 2200, 'yPos': 6850, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_SIGNAL_COLOR",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2900, 'yPos': 6850, 'width':                  1100, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_HISTOGRAM_DISPLAYTEXT",    atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 6500, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAMDISPLAY'), 'fontSize': 80})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_HISTOGRAM_DISPLAYSWITCH",  atmEta_gui_Generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 1600, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACDSHORT_DisplaySwitch_HISTOGRAM', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_HISTOGRAM_COLORTEXT",      atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos': 2200, 'yPos': 6500, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_HISTOGRAM+_COLOR",         atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2900, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_HISTOGRAM-_COLOR",         atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_BLOCKTITLE_MMACDSETTINGS",   atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6150, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSETTINGS'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_SIGNALINTERVALTEXT",         atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 5800, 'width':                  3000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNALINTERVAL'), 'fontSize': 80})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_SIGNALINTERVALTEXTINPUT",    atmEta_gui_Generals.textInputBox_typeA,           {'groupOrder': 0, 'xPos': 3100, 'yPos': 5800, 'width':                   900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MMACDSHORT_SignalIntervalTextInputBox', 'textUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_MULTIPLIERTEXT",             atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 5450, 'width':                  3000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MULTIPLIER'), 'fontSize': 80})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_MULTIPLIERTEXTINPUT",        atmEta_gui_Generals.textInputBox_typeA,           {'groupOrder': 0, 'xPos': 3100, 'yPos': 5450, 'width':                   900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MMACDSHORT_MultiplierTextInputBox', 'textUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATORINDEX_COLUMNTITLE1",          atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 5100, 'width':                  1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATORINTERVAL_COLUMNTITLE1",       atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 5100, 'width':                   850, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATORINDEX_COLUMNTITLE2",          atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2050, 'yPos': 5100, 'width':                  1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATORINTERVAL_COLUMNTITLE2",       atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3150, 'yPos': 5100, 'width':                   850, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            for lineIndex in range (_NMAXLINES['MMACDSHORT']):
                lineNumber = lineIndex+1; rowNumber = math.ceil(lineNumber/2)
                if (lineIndex%2 == 0): coordX = 0
                else:                  coordX = 2050
                self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_MMACDMA{:d}".format(lineNumber),               atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos': coordX,      'yPos': 5100-rowNumber*350, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': 'MMACDSHORT_LineActivationSwitch_{:d}'.format(lineNumber), 'text': 'MA {:d}'.format(lineNumber), 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['MMACDSHORT'].addGUIO("INDICATOR_MMACDMA{:d}_INTERVALINPUT".format(lineNumber), atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': coordX+1100, 'yPos': 5100-rowNumber*350, 'width':  850, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MMACDSHORT_IntervalTextInputBox_{:d}'.format(lineNumber),                           'textUpdateFunction': self.__onSettingsContentUpdate})
            yPosPoint0 = 5100-math.ceil(_NMAXLINES['MMACDSHORT']/2)*350
            self.settingsSubPages['MMACDSHORT'].addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'MMACDSHORT_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
        #<MMACDLONG Settings>
        if (True):
            self.settingsSubPages['MMACDLONG'].addGUIO("SUBPAGETITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_MMACDLONG'), 'fontSize': 100})
            self.settingsSubPages['MMACDLONG'].addGUIO("NAGBUTTON",    atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':                   550, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width':                  1500, 'height': 250, 'style': 'styleA', 'name': 'MMACDLONG_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':                   950, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':                   650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'MMACDLONG_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                self.settingsSubPages['MMACDLONG'].addGUIO("INDICATORCOLOR_{:s}_TEXT".format(componentType),   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                self.settingsSubPages['MMACDLONG'].addGUIO("INDICATORCOLOR_{:s}_SLIDER".format(componentType), atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': 'MMACDLONG_Color_{:s}'.format(componentType), 'valueUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['MMACDLONG'].addGUIO("INDICATORCOLOR_{:s}_VALUE".format(componentType),  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            mmacdLineTargets = {'MMACD':      {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDMMACD')},
                                'SIGNAL':     {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNAL')},
                                'HISTOGRAM+': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAM+')},
                                'HISTOGRAM-': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAM-')}}
            self.settingsSubPages['MMACDLONG'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = mmacdLineTargets, displayTargets = 'all')
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_BLOCKTITLE_DISPLAY",       atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDDISPLAY'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_MMACD_DISPLAYTEXT",        atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDMMACDDISPLAY'), 'fontSize': 80})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_MMACD_DISPLAYSWITCH",      atmEta_gui_Generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 1600, 'yPos': 7200, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACDLONG_DisplaySwitch_MMACD', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_MMACD_COLORTEXT",          atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos': 2200, 'yPos': 7200, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_MMACD_COLOR",              atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2900, 'yPos': 7200, 'width':                  1100, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_SIGNAL_DISPLAYTEXT",       atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNALDISPLAY'), 'fontSize': 80})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_SIGNAL_DISPLAYSWITCH",     atmEta_gui_Generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 1600, 'yPos': 6850, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACDLONG_DisplaySwitch_SIGNAL', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_SIGNAL_COLORTEXT",         atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos': 2200, 'yPos': 6850, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_SIGNAL_COLOR",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2900, 'yPos': 6850, 'width':                  1100, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_HISTOGRAM_DISPLAYTEXT",    atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 6500, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAMDISPLAY'), 'fontSize': 80})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_HISTOGRAM_DISPLAYSWITCH",  atmEta_gui_Generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 1600, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACDLONG_DisplaySwitch_HISTOGRAM', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_HISTOGRAM_COLORTEXT",      atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos': 2200, 'yPos': 6500, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_HISTOGRAM+_COLOR",         atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2900, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_HISTOGRAM-_COLOR",         atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_BLOCKTITLE_MMACDSETTINGS",   atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6150, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSETTINGS'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_SIGNALINTERVALTEXT",         atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 5800, 'width':                  3000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNALINTERVAL'), 'fontSize': 80})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_SIGNALINTERVALTEXTINPUT",    atmEta_gui_Generals.textInputBox_typeA,           {'groupOrder': 0, 'xPos': 3100, 'yPos': 5800, 'width':                   900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MMACDLONG_SignalIntervalTextInputBox', 'textUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_MULTIPLIERTEXT",             atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 5450, 'width':                  3000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MULTIPLIER'), 'fontSize': 80})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_MULTIPLIERTEXTINPUT",        atmEta_gui_Generals.textInputBox_typeA,           {'groupOrder': 0, 'xPos': 3100, 'yPos': 5450, 'width':                   900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MMACDLONG_MultiplierTextInputBox', 'textUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATORINDEX_COLUMNTITLE1",          atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 5100, 'width':                  1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATORINTERVAL_COLUMNTITLE1",       atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 5100, 'width':                   850, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATORINDEX_COLUMNTITLE2",          atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2050, 'yPos': 5100, 'width':                  1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['MMACDLONG'].addGUIO("INDICATORINTERVAL_COLUMNTITLE2",       atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3150, 'yPos': 5100, 'width':                   850, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            for lineIndex in range (_NMAXLINES['MMACDLONG']):
                lineNumber = lineIndex+1; rowNumber = math.ceil(lineNumber/2)
                if (lineIndex%2 == 0): coordX = 0
                else:                  coordX = 2050
                self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_MMACDMA{:d}".format(lineNumber),               atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos': coordX,      'yPos': 5100-rowNumber*350, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': 'MMACDLONG_LineActivationSwitch_{:d}'.format(lineNumber), 'text': 'MA {:d}'.format(lineNumber), 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['MMACDLONG'].addGUIO("INDICATOR_MMACDMA{:d}_INTERVALINPUT".format(lineNumber), atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': coordX+1100, 'yPos': 5100-rowNumber*350, 'width':  850, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MMACDLONG_IntervalTextInputBox_{:d}'.format(lineNumber),                           'textUpdateFunction': self.__onSettingsContentUpdate})
            yPosPoint0 = 5100-math.ceil(_NMAXLINES['MMACDLONG']/2)*350
            self.settingsSubPages['MMACDLONG'].addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'MMACDLONG_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
        #<DMIxADX Settings>
        if (True):
            self.settingsSubPages['DMIxADX'].addGUIO("SUBPAGETITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_DMIxADX'), 'fontSize': 100})
            self.settingsSubPages['DMIxADX'].addGUIO("NAGBUTTON",        atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            self.settingsSubPages['DMIxADX'].addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['DMIxADX'].addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            self.settingsSubPages['DMIxADX'].addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'DMIxADX_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['DMIxADX'].addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['DMIxADX'].addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'DMIxADX_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                self.settingsSubPages['DMIxADX'].addGUIO("INDICATORCOLOR_{:s}_TEXT".format(componentType),   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                self.settingsSubPages['DMIxADX'].addGUIO("INDICATORCOLOR_{:s}_SLIDER".format(componentType), atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': 'DMIxADX_Color_{:s}'.format(componentType), 'valueUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['DMIxADX'].addGUIO("INDICATORCOLOR_{:s}_VALUE".format(componentType),  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            self.settingsSubPages['DMIxADX'].addGUIO("INDICATORINDEX_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 1200, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['DMIxADX'].addGUIO("INDICATORINTERVAL_COLUMNTITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1300, 'yPos': 7550, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['DMIxADX'].addGUIO("INDICATORWIDTH_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2000, 'yPos': 7550, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['DMIxADX'].addGUIO("INDICATORCOLOR_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2700, 'yPos': 7550, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['DMIxADX'].addGUIO("INDICATORDISPLAY_COLUMNTITLE",  atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
            dmixadxList = dict()
            for i in range (_NMAXLINES['DMIxADX']):
                lineNumber = i+1
                self.settingsSubPages['DMIxADX'].addGUIO("INDICATOR_DMIxADX{:d}".format(lineNumber),               atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*i, 'width': 1200, 'height': 250, 'style': 'styleB', 'name': 'DMIxADX_LineActivationSwitch_{:d}'.format(lineNumber), 'text': 'DMIxADX {:d}'.format(lineNumber), 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['DMIxADX'].addGUIO("INDICATOR_DMIxADX{:d}_INTERVALINPUT".format(lineNumber), atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1300, 'yPos': 7200-350*i, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'DMIxADX_IntervalTextInputBox_{:d}'.format(lineNumber), 'textUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['DMIxADX'].addGUIO("INDICATOR_DMIxADX{:d}_WIDTHINPUT".format(lineNumber),    atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2000, 'yPos': 7200-350*i, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'DMIxADX_WidthTextInputBox_{:d}'.format(lineNumber), 'textUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['DMIxADX'].addGUIO("INDICATOR_DMIxADX{:d}_LINECOLOR".format(lineNumber),     atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2700, 'yPos': 7200-350*i, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
                self.settingsSubPages['DMIxADX'].addGUIO("INDICATOR_DMIxADX{:d}_DISPLAY".format(lineNumber),       atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*i, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'DMIxADX_DisplaySwitch_{:d}'.format(lineNumber), 'releaseFunction': self.__onSettingsContentUpdate})
                dmixadxList[str(lineNumber)] = {'text': "DMIxADX {:d}".format(lineNumber)}
            self.settingsSubPages['DMIxADX'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = dmixadxList, displayTargets = 'all')
            yPosPoint0 = 7200-350*(_NMAXLINES['DMIxADX']-1)
            self.settingsSubPages['DMIxADX'].addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'DMIxADX_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
        #<MFI Settings>
        if (True):
            self.settingsSubPages['MFI'].addGUIO("SUBPAGETITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_MFI'), 'fontSize': 100})
            self.settingsSubPages['MFI'].addGUIO("NAGBUTTON",        atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            self.settingsSubPages['MFI'].addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['MFI'].addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            self.settingsSubPages['MFI'].addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'MFI_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['MFI'].addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['MFI'].addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'MFI_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                self.settingsSubPages['MFI'].addGUIO("INDICATORCOLOR_{:s}_TEXT".format(componentType),   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                self.settingsSubPages['MFI'].addGUIO("INDICATORCOLOR_{:s}_SLIDER".format(componentType), atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': 'MFI_Color_{:s}'.format(componentType), 'valueUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['MFI'].addGUIO("INDICATORCOLOR_{:s}_VALUE".format(componentType),  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            self.settingsSubPages['MFI'].addGUIO("INDICATORINDEX_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['MFI'].addGUIO("INDICATORINTERVAL_COLUMNTITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 7550, 'width':  800, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['MFI'].addGUIO("INDICATORWIDTH_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2000, 'yPos': 7550, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['MFI'].addGUIO("INDICATORCOLOR_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2700, 'yPos': 7550, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['MFI'].addGUIO("INDICATORDISPLAY_COLUMNTITLE",  atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
            mfiList = dict()
            for i in range (_NMAXLINES['MFI']):
                lineNumber = i+1
                self.settingsSubPages['MFI'].addGUIO("INDICATOR_MFI{:d}".format(lineNumber),               atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*i, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': 'MFI_LineActivationSwitch_{:d}'.format(lineNumber), 'text': 'MFI {:d}'.format(lineNumber), 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['MFI'].addGUIO("INDICATOR_MFI{:d}_INTERVALINPUT".format(lineNumber), atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': 7200-350*i, 'width':  800, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MFI_IntervalTextInputBox_{:d}'.format(lineNumber), 'textUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['MFI'].addGUIO("INDICATOR_MFI{:d}_WIDTHINPUT".format(lineNumber),    atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2000, 'yPos': 7200-350*i, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MFI_WidthTextInputBox_{:d}'.format(lineNumber), 'textUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['MFI'].addGUIO("INDICATOR_MFI{:d}_LINECOLOR".format(lineNumber),     atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2700, 'yPos': 7200-350*i, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
                self.settingsSubPages['MFI'].addGUIO("INDICATOR_MFI{:d}_DISPLAY".format(lineNumber),       atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*i, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'MFI_DisplaySwitch_{:d}'.format(lineNumber), 'releaseFunction': self.__onSettingsContentUpdate})
                mfiList[str(lineNumber)] = {'text': "MFI {:d}".format(lineNumber)}
            self.settingsSubPages['MFI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = mfiList, displayTargets = 'all')
            yPosPoint0 = 7200-350*(_NMAXLINES['MFI']-1)
            self.settingsSubPages['MFI'].addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'MFI_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
        #<WOI Settings>
        if (True):
            self.settingsSubPages['WOI'].addGUIO("SUBPAGETITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_WOI'), 'fontSize': 100})
            self.settingsSubPages['WOI'].addGUIO("NAGBUTTON",        atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            self.settingsSubPages['WOI'].addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['WOI'].addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            self.settingsSubPages['WOI'].addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'WOI_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['WOI'].addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['WOI'].addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'WOI_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                self.settingsSubPages['WOI'].addGUIO("INDICATORCOLOR_{:s}_TEXT".format(componentType),   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                self.settingsSubPages['WOI'].addGUIO("INDICATORCOLOR_{:s}_SLIDER".format(componentType), atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': 'WOI_Color_{:s}'.format(componentType), 'valueUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['WOI'].addGUIO("INDICATORCOLOR_{:s}_VALUE".format(componentType),  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            self.settingsSubPages['WOI'].addGUIO("INDICATOR_BLOCKTITLE_WOIBASE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WOIBASE'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['WOI'].addGUIO("INDICATOR_DISPLAYWOIBASE_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width': 1600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WOIBASEDISPLAY'), 'fontSize': 80})
            self.settingsSubPages['WOI'].addGUIO("INDICATOR_WOIBASE_DISPLAYSWITCH", atmEta_gui_Generals.switch_typeB,  {'groupOrder': 0, 'xPos': 1700, 'yPos': 7200, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'WOI_DisplaySwitch_WOIBase', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['WOI'].addGUIO("INDICATOR_WOIBASE+_LINECOLOR",    atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 2300, 'yPos': 7200, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['WOI'].addGUIO("INDICATOR_WOIBASE-_LINECOLOR",    atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3200, 'yPos': 7200, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['WOI'].addGUIO("INDICATOR_BLOCKTITLE_WOIGAUSSIANDELTA", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': 6850, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WOIGAUSSIANDELTA'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['WOI'].addGUIO("INDICATORINDEX_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6550, 'width': 700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['WOI'].addGUIO("INDICATORINTERVAL_COLUMNTITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  800, 'yPos': 6550, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['WOI'].addGUIO("INDICATORSIGMA_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1500, 'yPos': 6550, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SIGMA'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['WOI'].addGUIO("INDICATORWIDTH_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2200, 'yPos': 6550, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['WOI'].addGUIO("INDICATORCOLOR_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2900, 'yPos': 6550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['WOI'].addGUIO("INDICATORDISPLAY_COLUMNTITLE",  atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
            NESList = {'BASE+': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BASE+')},
                       'BASE-': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BASE-')}}
            for i in range (_NMAXLINES['WOI']):
                lineNumber = i+1
                self.settingsSubPages['WOI'].addGUIO("INDICATOR_WOI{:d}".format(lineNumber),               atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6200-350*i, 'width': 700, 'height': 250, 'style': 'styleB', 'name': 'WOI_LineActivationSwitch_{:d}'.format(lineNumber), 'text': 'WOI {:d}'.format(lineNumber), 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['WOI'].addGUIO("INDICATOR_WOI{:d}_INTERVALINPUT".format(lineNumber), atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  800, 'yPos': 6200-350*i, 'width': 600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'WOI_IntervalTextInputBox_{:d}'.format(lineNumber), 'textUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['WOI'].addGUIO("INDICATOR_WOI{:d}_SIGMAINPUT".format(lineNumber),    atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1500, 'yPos': 6200-350*i, 'width': 600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'WOI_SigmaTextInputBox_{:d}'.format(lineNumber),    'textUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['WOI'].addGUIO("INDICATOR_WOI{:d}_WIDTHINPUT".format(lineNumber),    atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2200, 'yPos': 6200-350*i, 'width': 600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'WOI_WidthTextInputBox_{:d}'.format(lineNumber),    'textUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['WOI'].addGUIO("INDICATOR_WOI{:d}_LINECOLOR".format(lineNumber),     atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2900, 'yPos': 6200-350*i, 'width': 500, 'height': 250, 'style': 'styleA', 'mode': True})
                self.settingsSubPages['WOI'].addGUIO("INDICATOR_WOI{:d}_DISPLAY".format(lineNumber),       atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6200-350*i, 'width': 500, 'height': 250, 'style': 'styleA', 'name': 'WOI_DisplaySwitch_{:d}'.format(lineNumber), 'releaseFunction': self.__onSettingsContentUpdate})
                NESList[str(lineNumber)] = {'text': "WOI {:d}".format(lineNumber)}
            self.settingsSubPages['WOI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = NESList, displayTargets = 'all')
            yPosPoint0 = 6200-350*(_NMAXLINES['WOI']-1)
            self.settingsSubPages['WOI'].addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'WOI_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
        #<NES Settings>
        if (True):
            self.settingsSubPages['NES'].addGUIO("SUBPAGETITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_NES'), 'fontSize': 100})
            self.settingsSubPages['NES'].addGUIO("NAGBUTTON",        atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            self.settingsSubPages['NES'].addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['NES'].addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            self.settingsSubPages['NES'].addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'NES_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['NES'].addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['NES'].addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'NES_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                self.settingsSubPages['NES'].addGUIO("INDICATORCOLOR_{:s}_TEXT".format(componentType),   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                self.settingsSubPages['NES'].addGUIO("INDICATORCOLOR_{:s}_SLIDER".format(componentType), atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': 'NES_Color_{:s}'.format(componentType), 'valueUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['NES'].addGUIO("INDICATORCOLOR_{:s}_VALUE".format(componentType),  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            self.settingsSubPages['NES'].addGUIO("INDICATOR_BLOCKTITLE_NESBASE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:NESBASE'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['NES'].addGUIO("INDICATOR_DISPLAYNESBASE_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width': 1600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:NESBASEDISPLAY'), 'fontSize': 80})
            self.settingsSubPages['NES'].addGUIO("INDICATOR_NESBASE_DISPLAYSWITCH", atmEta_gui_Generals.switch_typeB,  {'groupOrder': 0, 'xPos': 1700, 'yPos': 7200, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'NES_DisplaySwitch_NESBase', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPages['NES'].addGUIO("INDICATOR_NESBASE+_LINECOLOR",    atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 2300, 'yPos': 7200, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['NES'].addGUIO("INDICATOR_NESBASE-_LINECOLOR",    atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3200, 'yPos': 7200, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPages['NES'].addGUIO("INDICATOR_BLOCKTITLE_NESGAUSSIANDELTA", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': 6850, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:NESGAUSSIANDELTA'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['NES'].addGUIO("INDICATORINDEX_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6550, 'width': 700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['NES'].addGUIO("INDICATORINTERVAL_COLUMNTITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  800, 'yPos': 6550, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['NES'].addGUIO("INDICATORSIGMA_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1500, 'yPos': 6550, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SIGMA'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['NES'].addGUIO("INDICATORWIDTH_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2200, 'yPos': 6550, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['NES'].addGUIO("INDICATORCOLOR_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2900, 'yPos': 6550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPages['NES'].addGUIO("INDICATORDISPLAY_COLUMNTITLE",  atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
            NESList = {'BASE+': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BASE+')},
                       'BASE-': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BASE-')}}
            for i in range (_NMAXLINES['NES']):
                lineNumber = i+1
                self.settingsSubPages['NES'].addGUIO("INDICATOR_NES{:d}".format(lineNumber),               atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6200-350*i, 'width': 700, 'height': 250, 'style': 'styleB', 'name': 'NES_LineActivationSwitch_{:d}'.format(lineNumber), 'text': 'NES {:d}'.format(lineNumber), 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['NES'].addGUIO("INDICATOR_NES{:d}_INTERVALINPUT".format(lineNumber), atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  800, 'yPos': 6200-350*i, 'width': 600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'NES_IntervalTextInputBox_{:d}'.format(lineNumber), 'textUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['NES'].addGUIO("INDICATOR_NES{:d}_SIGMAINPUT".format(lineNumber),    atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1500, 'yPos': 6200-350*i, 'width': 600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'NES_SigmaTextInputBox_{:d}'.format(lineNumber),    'textUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['NES'].addGUIO("INDICATOR_NES{:d}_WIDTHINPUT".format(lineNumber),    atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2200, 'yPos': 6200-350*i, 'width': 600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'NES_WidthTextInputBox_{:d}'.format(lineNumber),    'textUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPages['NES'].addGUIO("INDICATOR_NES{:d}_LINECOLOR".format(lineNumber),     atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2900, 'yPos': 6200-350*i, 'width': 500, 'height': 250, 'style': 'styleA', 'mode': True})
                self.settingsSubPages['NES'].addGUIO("INDICATOR_NES{:d}_DISPLAY".format(lineNumber),       atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6200-350*i, 'width': 500, 'height': 250, 'style': 'styleA', 'name': 'NES_DisplaySwitch_{:d}'.format(lineNumber), 'releaseFunction': self.__onSettingsContentUpdate})
                NESList[str(lineNumber)] = {'text': "NES {:d}".format(lineNumber)}
            self.settingsSubPages['NES'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = NESList, displayTargets = 'all')
            yPosPoint0 = 6200-350*(_NMAXLINES['NES']-1)
            self.settingsSubPages['NES'].addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'NES_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})

    def __initializeObjectConfig(self):
        #---Default Object Configuration
        self.objectConfig = dict()
        #--- MAIN Config
        for siViewerIndex in range (len(_SITYPES)): self.objectConfig['SIVIEWER{:d}Display'.format(siViewerIndex+1)] = False; self.objectConfig['SIVIEWER{:d}SIAlloc'.format(siViewerIndex+1)] = _SITYPES[siViewerIndex]
        self.objectConfig['TimeZone']       = 'LOCAL'
        self.objectConfig['KlineColorType'] = 1
        self.objectConfig['AnalysisRangeBeg'] = None
        self.objectConfig['AnalysisRangeEnd'] = None
        self.objectConfig['TRADELOG_Display'] = True
        self.objectConfig['TRADELOG_BUY_ColorR%DARK']  =100; self.objectConfig['TRADELOG_BUY_ColorG%DARK']  =255; self.objectConfig['TRADELOG_BUY_ColorB%DARK']  =180; self.objectConfig['TRADELOG_BUY_ColorA%DARK']  =120
        self.objectConfig['TRADELOG_BUY_ColorR%LIGHT'] = 80; self.objectConfig['TRADELOG_BUY_ColorG%LIGHT'] =200; self.objectConfig['TRADELOG_BUY_ColorB%LIGHT'] =150; self.objectConfig['TRADELOG_BUY_ColorA%LIGHT'] =120
        self.objectConfig['TRADELOG_SELL_ColorR%DARK'] =255; self.objectConfig['TRADELOG_SELL_ColorG%DARK'] =100; self.objectConfig['TRADELOG_SELL_ColorB%DARK'] =100; self.objectConfig['TRADELOG_SELL_ColorA%DARK'] =120
        self.objectConfig['TRADELOG_SELL_ColorR%LIGHT']=240; self.objectConfig['TRADELOG_SELL_ColorG%LIGHT']= 80; self.objectConfig['TRADELOG_SELL_ColorB%LIGHT']= 80; self.objectConfig['TRADELOG_SELL_ColorA%LIGHT']=120
        self.objectConfig['BIDSANDASKS_Display'] = True
        self.objectConfig['BIDSANDASKS_BIDS_ColorR%DARK'] =100; self.objectConfig['BIDSANDASKS_BIDS_ColorG%DARK'] =255; self.objectConfig['BIDSANDASKS_BIDS_ColorB%DARK'] =180; self.objectConfig['BIDSANDASKS_BIDS_ColorA%DARK'] =120
        self.objectConfig['BIDSANDASKS_BIDS_ColorR%LIGHT']= 80; self.objectConfig['BIDSANDASKS_BIDS_ColorG%LIGHT']=200; self.objectConfig['BIDSANDASKS_BIDS_ColorB%LIGHT']=150; self.objectConfig['BIDSANDASKS_BIDS_ColorA%LIGHT']=120
        self.objectConfig['BIDSANDASKS_ASKS_ColorR%DARK'] =255; self.objectConfig['BIDSANDASKS_ASKS_ColorG%DARK'] =100; self.objectConfig['BIDSANDASKS_ASKS_ColorB%DARK'] =100; self.objectConfig['BIDSANDASKS_ASKS_ColorA%DARK'] =120
        self.objectConfig['BIDSANDASKS_ASKS_ColorR%LIGHT']=240; self.objectConfig['BIDSANDASKS_ASKS_ColorG%LIGHT']= 80; self.objectConfig['BIDSANDASKS_ASKS_ColorB%LIGHT']= 80; self.objectConfig['BIDSANDASKS_ASKS_ColorA%LIGHT']=120
        #--- SMA Config
        self.objectConfig['SMA_Master'] = False
        for lineIndex in range (_NMAXLINES['SMA']):
            lineNumber = lineIndex+1
            self.objectConfig['SMA_{:d}_LineActive'.format(lineNumber)] = False
            self.objectConfig['SMA_{:d}_NSamples'.format(lineNumber)]   = 10*lineNumber
            self.objectConfig['SMA_{:d}_Width'.format(lineNumber)] = 1
            self.objectConfig['SMA_{:d}_ColorR%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['SMA_{:d}_ColorG%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['SMA_{:d}_ColorB%DARK'.format(lineNumber)] =random.randint(64, 255); self.objectConfig['SMA_{:d}_ColorA%DARK'.format(lineNumber)] =255
            self.objectConfig['SMA_{:d}_ColorR%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['SMA_{:d}_ColorG%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['SMA_{:d}_ColorB%LIGHT'.format(lineNumber)]=random.randint(64, 255); self.objectConfig['SMA_{:d}_ColorA%LIGHT'.format(lineNumber)]=255
            self.objectConfig['SMA_{:d}_Display'.format(lineNumber)] = True
        #--- WMA Config
        self.objectConfig['WMA_Master'] = False
        for lineIndex in range (_NMAXLINES['WMA']):
            lineNumber = lineIndex+1
            self.objectConfig['WMA_{:d}_LineActive'.format(lineNumber)] = False
            self.objectConfig['WMA_{:d}_NSamples'.format(lineNumber)]   = 10*lineNumber
            self.objectConfig['WMA_{:d}_Width'.format(lineNumber)] = 1
            self.objectConfig['WMA_{:d}_ColorR%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['WMA_{:d}_ColorG%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['WMA_{:d}_ColorB%DARK'.format(lineNumber)] =random.randint(64, 255); self.objectConfig['WMA_{:d}_ColorA%DARK'.format(lineNumber)] =255
            self.objectConfig['WMA_{:d}_ColorR%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['WMA_{:d}_ColorG%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['WMA_{:d}_ColorB%LIGHT'.format(lineNumber)]=random.randint(64, 255); self.objectConfig['WMA_{:d}_ColorA%LIGHT'.format(lineNumber)]=255
            self.objectConfig['WMA_{:d}_Display'.format(lineNumber)] = True
        #--- EMA Config
        self.objectConfig['EMA_Master'] = False
        for lineIndex in range (_NMAXLINES['EMA']):
            lineNumber = lineIndex+1
            self.objectConfig['EMA_{:d}_LineActive'.format(lineNumber)] = False
            self.objectConfig['EMA_{:d}_NSamples'.format(lineNumber)]   = 10*lineNumber
            self.objectConfig['EMA_{:d}_Width'.format(lineNumber)] = 1
            self.objectConfig['EMA_{:d}_ColorR%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['EMA_{:d}_ColorG%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['EMA_{:d}_ColorB%DARK'.format(lineNumber)] =random.randint(64, 255); self.objectConfig['EMA_{:d}_ColorA%DARK'.format(lineNumber)] =255
            self.objectConfig['EMA_{:d}_ColorR%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['EMA_{:d}_ColorG%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['EMA_{:d}_ColorB%LIGHT'.format(lineNumber)]=random.randint(64, 255); self.objectConfig['EMA_{:d}_ColorA%LIGHT'.format(lineNumber)]=255
            self.objectConfig['EMA_{:d}_Display'.format(lineNumber)] = True
        #--- PSAR Config
        self.objectConfig['PSAR_Master'] = False
        for lineIndex in range (_NMAXLINES['PSAR']):
            lineNumber = lineIndex+1
            self.objectConfig['PSAR_{:d}_LineActive'.format(lineNumber)] = False
            self.objectConfig['PSAR_{:d}_AF0'.format(lineNumber)]   = 0.020
            self.objectConfig['PSAR_{:d}_AF+'.format(lineNumber)]   = 0.005*lineNumber
            self.objectConfig['PSAR_{:d}_AFMax'.format(lineNumber)] = 0.200
            self.objectConfig['PSAR_{:d}_Width'.format(lineNumber)] = 1
            self.objectConfig['PSAR_{:d}_ColorR%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['PSAR_{:d}_ColorG%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['PSAR_{:d}_ColorB%DARK'.format(lineNumber)] =random.randint(64, 255); self.objectConfig['PSAR_{:d}_ColorA%DARK'.format(lineNumber)] =255
            self.objectConfig['PSAR_{:d}_ColorR%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['PSAR_{:d}_ColorG%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['PSAR_{:d}_ColorB%LIGHT'.format(lineNumber)]=random.randint(64, 255); self.objectConfig['PSAR_{:d}_ColorA%LIGHT'.format(lineNumber)]=255
            self.objectConfig['PSAR_{:d}_Display'.format(lineNumber)] = True
        #--- BOL Config
        self.objectConfig['BOL_Master'] = False
        for lineIndex in range (_NMAXLINES['BOL']):
            lineNumber = lineIndex+1
            self.objectConfig['BOL_{:d}_LineActive'.format(lineNumber)] = False
            self.objectConfig['BOL_{:d}_NSamples'.format(lineNumber)]  = 10*lineNumber
            self.objectConfig['BOL_{:d}_BandWidth'.format(lineNumber)] = 2.0
            self.objectConfig['BOL_{:d}_Width'.format(lineNumber)] = 1
            self.objectConfig['BOL_{:d}_ColorR%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['BOL_{:d}_ColorG%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['BOL_{:d}_ColorB%DARK'.format(lineNumber)] =random.randint(64, 255); self.objectConfig['BOL_{:d}_ColorA%DARK'.format(lineNumber)] =30
            self.objectConfig['BOL_{:d}_ColorR%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['BOL_{:d}_ColorG%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['BOL_{:d}_ColorB%LIGHT'.format(lineNumber)]=random.randint(64, 255); self.objectConfig['BOL_{:d}_ColorA%LIGHT'.format(lineNumber)]=30
            self.objectConfig['BOL_{:d}_Display'.format(lineNumber)] = True
        self.objectConfig['BOL_MAType']            = 'SMA'
        self.objectConfig['BOL_DisplayCenterLine'] = True
        self.objectConfig['BOL_DisplayBand']       = True
        #--- IVP Config
        self.objectConfig['IVP_Master'] = False
        self.objectConfig['IVP_NSamples']    = 288
        self.objectConfig['IVP_GammaFactor'] = 0.010 #0.005 ~ 0.100
        self.objectConfig['IVP_DeltaFactor'] = 1.0   #0.1   ~ 10.0
        self.objectConfig['IVP_VPLP_Display']      = True
        self.objectConfig['IVP_VPLP_DisplayWidth'] = 0.2
        self.objectConfig['IVP_VPLP_ColorR%DARK']  = random.randint(64,255); self.objectConfig['IVP_VPLP_ColorG%DARK']  = random.randint(64,255); self.objectConfig['IVP_VPLP_ColorB%DARK']  = random.randint(64,255); self.objectConfig['IVP_VPLP_ColorA%DARK']  = 30
        self.objectConfig['IVP_VPLP_ColorR%LIGHT'] = random.randint(64,255); self.objectConfig['IVP_VPLP_ColorG%LIGHT'] = random.randint(64,255); self.objectConfig['IVP_VPLP_ColorB%LIGHT'] = random.randint(64,255); self.objectConfig['IVP_VPLP_ColorA%LIGHT'] = 30
        self.objectConfig['IVP_VPLPB_Display'] = True
        self.objectConfig['IVP_VPLPB_ColorR%DARK']  = random.randint(64,255); self.objectConfig['IVP_VPLPB_ColorG%DARK']  = random.randint(64,255); self.objectConfig['IVP_VPLPB_ColorB%DARK']  = random.randint(64,255); self.objectConfig['IVP_VPLPB_ColorA%DARK']  = 150
        self.objectConfig['IVP_VPLPB_ColorR%LIGHT'] = random.randint(64,255); self.objectConfig['IVP_VPLPB_ColorG%LIGHT'] = random.randint(64,255); self.objectConfig['IVP_VPLPB_ColorB%LIGHT'] = random.randint(64,255); self.objectConfig['IVP_VPLPB_ColorA%LIGHT'] = 150
        self.objectConfig['IVP_VPLPB_DisplayRegion'] = 0.100
        #---PIP Config
        self.objectConfig['PIP_Master'] = False
        self.objectConfig['PIP_NeuralNetworkCode'] = None
        self.objectConfig['PIP_SwingRange']        = 0.0250
        self.objectConfig['PIP_NNAAlpha']          = 0.25
        self.objectConfig['PIP_NNABeta']           = 10
        self.objectConfig['PIP_ClassicalAlpha']    = 2.0
        self.objectConfig['PIP_ClassicalBeta']     = 10
        self.objectConfig['PIP_ClassicalNSamples'] = 10
        self.objectConfig['PIP_ClassicalSigma']    = 3.5
        self.objectConfig['PIP_SWING_Display']                 = True
        self.objectConfig['PIP_NNASIGNAL_Display']             = True
        self.objectConfig['PIP_WOISIGNAL_Display']             = True
        self.objectConfig['PIP_NESSIGNAL_Display']             = True
        self.objectConfig['PIP_CLASSICALSIGNAL_Display']       = True
        self.objectConfig['PIP_CLASSICALSIGNAL_DisplayType']   = 'UNFILTERED'
        self.objectConfig['PIP_SWING_ColorR%DARK']             = random.randint(64,255); self.objectConfig['PIP_SWING_ColorG%DARK']  = random.randint(64,255); self.objectConfig['PIP_SWING_ColorB%DARK']  = random.randint(64,255); self.objectConfig['PIP_SWING_ColorA%DARK']  = 255
        self.objectConfig['PIP_SWING_ColorR%LIGHT']            = random.randint(64,255); self.objectConfig['PIP_SWING_ColorG%LIGHT'] = random.randint(64,255); self.objectConfig['PIP_SWING_ColorB%LIGHT'] = random.randint(64,255); self.objectConfig['PIP_SWING_ColorA%LIGHT'] = 255
        self.objectConfig['PIP_NNASIGNAL+_ColorR%DARK']        = 100; self.objectConfig['PIP_NNASIGNAL+_ColorG%DARK']        = 255; self.objectConfig['PIP_NNASIGNAL+_ColorB%DARK']        = 180; self.objectConfig['PIP_NNASIGNAL+_ColorA%DARK']        = 255
        self.objectConfig['PIP_NNASIGNAL+_ColorR%LIGHT']       =  80; self.objectConfig['PIP_NNASIGNAL+_ColorG%LIGHT']       = 200; self.objectConfig['PIP_NNASIGNAL+_ColorB%LIGHT']       = 150; self.objectConfig['PIP_NNASIGNAL+_ColorA%LIGHT']       = 255
        self.objectConfig['PIP_NNASIGNAL-_ColorR%DARK']        = 255; self.objectConfig['PIP_NNASIGNAL-_ColorG%DARK']        = 100; self.objectConfig['PIP_NNASIGNAL-_ColorB%DARK']        = 100; self.objectConfig['PIP_NNASIGNAL-_ColorA%DARK']        = 255
        self.objectConfig['PIP_NNASIGNAL-_ColorR%LIGHT']       = 240; self.objectConfig['PIP_NNASIGNAL-_ColorG%LIGHT']       =  80; self.objectConfig['PIP_NNASIGNAL-_ColorB%LIGHT']       =  80; self.objectConfig['PIP_NNASIGNAL-_ColorA%LIGHT']       = 255
        self.objectConfig['PIP_WOISIGNAL+_ColorR%DARK']        = 100; self.objectConfig['PIP_WOISIGNAL+_ColorG%DARK']        = 255; self.objectConfig['PIP_WOISIGNAL+_ColorB%DARK']        = 180; self.objectConfig['PIP_WOISIGNAL+_ColorA%DARK']        = 255
        self.objectConfig['PIP_WOISIGNAL+_ColorR%LIGHT']       =  80; self.objectConfig['PIP_WOISIGNAL+_ColorG%LIGHT']       = 200; self.objectConfig['PIP_WOISIGNAL+_ColorB%LIGHT']       = 150; self.objectConfig['PIP_WOISIGNAL+_ColorA%LIGHT']       = 255
        self.objectConfig['PIP_WOISIGNAL-_ColorR%DARK']        = 255; self.objectConfig['PIP_WOISIGNAL-_ColorG%DARK']        = 100; self.objectConfig['PIP_WOISIGNAL-_ColorB%DARK']        = 100; self.objectConfig['PIP_WOISIGNAL-_ColorA%DARK']        = 255
        self.objectConfig['PIP_WOISIGNAL-_ColorR%LIGHT']       = 240; self.objectConfig['PIP_WOISIGNAL-_ColorG%LIGHT']       =  80; self.objectConfig['PIP_WOISIGNAL-_ColorB%LIGHT']       =  80; self.objectConfig['PIP_WOISIGNAL-_ColorA%LIGHT']       = 255
        self.objectConfig['PIP_NESSIGNAL+_ColorR%DARK']        = 100; self.objectConfig['PIP_NESSIGNAL+_ColorG%DARK']        = 255; self.objectConfig['PIP_NESSIGNAL+_ColorB%DARK']        = 180; self.objectConfig['PIP_NESSIGNAL+_ColorA%DARK']        = 255
        self.objectConfig['PIP_NESSIGNAL+_ColorR%LIGHT']       =  80; self.objectConfig['PIP_NESSIGNAL+_ColorG%LIGHT']       = 200; self.objectConfig['PIP_NESSIGNAL+_ColorB%LIGHT']       = 150; self.objectConfig['PIP_NESSIGNAL+_ColorA%LIGHT']       = 255
        self.objectConfig['PIP_NESSIGNAL-_ColorR%DARK']        = 255; self.objectConfig['PIP_NESSIGNAL-_ColorG%DARK']        = 100; self.objectConfig['PIP_NESSIGNAL-_ColorB%DARK']        = 100; self.objectConfig['PIP_NESSIGNAL-_ColorA%DARK']        = 255
        self.objectConfig['PIP_NESSIGNAL-_ColorR%LIGHT']       = 240; self.objectConfig['PIP_NESSIGNAL-_ColorG%LIGHT']       =  80; self.objectConfig['PIP_NESSIGNAL-_ColorB%LIGHT']       =  80; self.objectConfig['PIP_NESSIGNAL-_ColorA%LIGHT']       = 255
        self.objectConfig['PIP_CLASSICALSIGNAL+_ColorR%DARK']  = 100; self.objectConfig['PIP_CLASSICALSIGNAL+_ColorG%DARK']  = 255; self.objectConfig['PIP_CLASSICALSIGNAL+_ColorB%DARK']  = 180; self.objectConfig['PIP_CLASSICALSIGNAL+_ColorA%DARK']  = 255
        self.objectConfig['PIP_CLASSICALSIGNAL+_ColorR%LIGHT'] =  80; self.objectConfig['PIP_CLASSICALSIGNAL+_ColorG%LIGHT'] = 200; self.objectConfig['PIP_CLASSICALSIGNAL+_ColorB%LIGHT'] = 150; self.objectConfig['PIP_CLASSICALSIGNAL+_ColorA%LIGHT'] = 255
        self.objectConfig['PIP_CLASSICALSIGNAL-_ColorR%DARK']  = 255; self.objectConfig['PIP_CLASSICALSIGNAL-_ColorG%DARK']  = 100; self.objectConfig['PIP_CLASSICALSIGNAL-_ColorB%DARK']  = 100; self.objectConfig['PIP_CLASSICALSIGNAL-_ColorA%DARK']  = 255
        self.objectConfig['PIP_CLASSICALSIGNAL-_ColorR%LIGHT'] = 240; self.objectConfig['PIP_CLASSICALSIGNAL-_ColorG%LIGHT'] =  80; self.objectConfig['PIP_CLASSICALSIGNAL-_ColorB%LIGHT'] =  80; self.objectConfig['PIP_CLASSICALSIGNAL-_ColorA%LIGHT'] = 255
        #---VOL Config
        self.objectConfig['VOL_Master'] = False
        for lineIndex in range (_NMAXLINES['VOL']):
            lineNumber = lineIndex+1
            self.objectConfig['VOL_{:d}_LineActive'.format(lineNumber)] = False
            self.objectConfig['VOL_{:d}_NSamples'.format(lineNumber)] = 10*lineNumber
            self.objectConfig['VOL_{:d}_Width'.format(lineNumber)] = 1
            self.objectConfig['VOL_{:d}_ColorR%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['VOL_{:d}_ColorG%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['VOL_{:d}_ColorB%DARK'.format(lineNumber)] =random.randint(64, 255); self.objectConfig['VOL_{:d}_ColorA%DARK'.format(lineNumber)] =255
            self.objectConfig['VOL_{:d}_ColorR%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['VOL_{:d}_ColorG%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['VOL_{:d}_ColorB%LIGHT'.format(lineNumber)]=random.randint(64, 255); self.objectConfig['VOL_{:d}_ColorA%LIGHT'.format(lineNumber)]=255
            self.objectConfig['VOL_{:d}_Display'.format(lineNumber)] = True
        self.objectConfig['VOL_VolumeType'] = 'BASE'
        self.objectConfig['VOL_MAType']     = 'SMA'
        #---MMACDSHORT Config
        self.objectConfig['MMACDSHORT_Master'] = False
        self.objectConfig['MMACDSHORT_SignalNSamples']    = 10
        self.objectConfig['MMACDSHORT_Multiplier']        = 12
        self.objectConfig['MMACDSHORT_MMACD_Display']     = True
        self.objectConfig['MMACDSHORT_SIGNAL_Display']    = True
        self.objectConfig['MMACDSHORT_HISTOGRAM_Display'] = True
        self.objectConfig['MMACDSHORT_MMACD_ColorR%DARK']   = random.randint(64,255); self.objectConfig['MMACDSHORT_MMACD_ColorG%DARK']   = random.randint(64,255); self.objectConfig['MMACDSHORT_MMACD_ColorB%DARK']   = random.randint(64,255); self.objectConfig['MMACDSHORT_MMACD_ColorA%DARK']   = 255
        self.objectConfig['MMACDSHORT_MMACD_ColorR%LIGHT']  = random.randint(64,255); self.objectConfig['MMACDSHORT_MMACD_ColorG%LIGHT']  = random.randint(64,255); self.objectConfig['MMACDSHORT_MMACD_ColorB%LIGHT']  = random.randint(64,255); self.objectConfig['MMACDSHORT_MMACD_ColorA%LIGHT']  = 255
        self.objectConfig['MMACDSHORT_SIGNAL_ColorR%DARK']  = random.randint(64,255); self.objectConfig['MMACDSHORT_SIGNAL_ColorG%DARK']  = random.randint(64,255); self.objectConfig['MMACDSHORT_SIGNAL_ColorB%DARK']  = random.randint(64,255); self.objectConfig['MMACDSHORT_SIGNAL_ColorA%DARK']  = 255
        self.objectConfig['MMACDSHORT_SIGNAL_ColorR%LIGHT'] = random.randint(64,255); self.objectConfig['MMACDSHORT_SIGNAL_ColorG%LIGHT'] = random.randint(64,255); self.objectConfig['MMACDSHORT_SIGNAL_ColorB%LIGHT'] = random.randint(64,255); self.objectConfig['MMACDSHORT_SIGNAL_ColorA%LIGHT'] = 255
        self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorR%DARK']  = 100; self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorG%DARK']  = 255; self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorB%DARK']  = 180; self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorA%DARK']  = 255
        self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorR%LIGHT'] =  80; self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorG%LIGHT'] = 200; self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorB%LIGHT'] = 150; self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorA%LIGHT'] = 255
        self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorR%DARK']  = 255; self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorG%DARK']  = 100; self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorB%DARK']  = 100; self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorA%DARK']  = 255
        self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorR%LIGHT'] = 240; self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorG%LIGHT'] =  80; self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorB%LIGHT'] =  80; self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorA%LIGHT'] = 255
        for lineIndex in range (_NMAXLINES['MMACDSHORT']):
            lineNumber = lineIndex+1
            self.objectConfig['MMACDSHORT_MA{:d}_LineActive'.format(lineNumber)] = False
            self.objectConfig['MMACDSHORT_MA{:d}_NSamples'.format(lineNumber)]   = 10*lineNumber
        #---MMACDLONG Config
        self.objectConfig['MMACDLONG_Master'] = False
        self.objectConfig['MMACDLONG_SignalNSamples']    = 10
        self.objectConfig['MMACDLONG_Multiplier']        = 48
        self.objectConfig['MMACDLONG_MMACD_Display']     = True
        self.objectConfig['MMACDLONG_SIGNAL_Display']    = True
        self.objectConfig['MMACDLONG_HISTOGRAM_Display'] = True
        self.objectConfig['MMACDLONG_MMACD_ColorR%DARK']   = random.randint(64,255); self.objectConfig['MMACDLONG_MMACD_ColorG%DARK']   = random.randint(64,255); self.objectConfig['MMACDLONG_MMACD_ColorB%DARK']   = random.randint(64,255); self.objectConfig['MMACDLONG_MMACD_ColorA%DARK']   = 255
        self.objectConfig['MMACDLONG_MMACD_ColorR%LIGHT']  = random.randint(64,255); self.objectConfig['MMACDLONG_MMACD_ColorG%LIGHT']  = random.randint(64,255); self.objectConfig['MMACDLONG_MMACD_ColorB%LIGHT']  = random.randint(64,255); self.objectConfig['MMACDLONG_MMACD_ColorA%LIGHT']  = 255
        self.objectConfig['MMACDLONG_SIGNAL_ColorR%DARK']  = random.randint(64,255); self.objectConfig['MMACDLONG_SIGNAL_ColorG%DARK']  = random.randint(64,255); self.objectConfig['MMACDLONG_SIGNAL_ColorB%DARK']  = random.randint(64,255); self.objectConfig['MMACDLONG_SIGNAL_ColorA%DARK']  = 255
        self.objectConfig['MMACDLONG_SIGNAL_ColorR%LIGHT'] = random.randint(64,255); self.objectConfig['MMACDLONG_SIGNAL_ColorG%LIGHT'] = random.randint(64,255); self.objectConfig['MMACDLONG_SIGNAL_ColorB%LIGHT'] = random.randint(64,255); self.objectConfig['MMACDLONG_SIGNAL_ColorA%LIGHT'] = 255
        self.objectConfig['MMACDLONG_HISTOGRAM+_ColorR%DARK']  = 100; self.objectConfig['MMACDLONG_HISTOGRAM+_ColorG%DARK']  = 255; self.objectConfig['MMACDLONG_HISTOGRAM+_ColorB%DARK']  = 180; self.objectConfig['MMACDLONG_HISTOGRAM+_ColorA%DARK']  = 255
        self.objectConfig['MMACDLONG_HISTOGRAM+_ColorR%LIGHT'] =  80; self.objectConfig['MMACDLONG_HISTOGRAM+_ColorG%LIGHT'] = 200; self.objectConfig['MMACDLONG_HISTOGRAM+_ColorB%LIGHT'] = 150; self.objectConfig['MMACDLONG_HISTOGRAM+_ColorA%LIGHT'] = 255
        self.objectConfig['MMACDLONG_HISTOGRAM-_ColorR%DARK']  = 255; self.objectConfig['MMACDLONG_HISTOGRAM-_ColorG%DARK']  = 100; self.objectConfig['MMACDLONG_HISTOGRAM-_ColorB%DARK']  = 100; self.objectConfig['MMACDLONG_HISTOGRAM-_ColorA%DARK']  = 255
        self.objectConfig['MMACDLONG_HISTOGRAM-_ColorR%LIGHT'] = 240; self.objectConfig['MMACDLONG_HISTOGRAM-_ColorG%LIGHT'] =  80; self.objectConfig['MMACDLONG_HISTOGRAM-_ColorB%LIGHT'] =  80; self.objectConfig['MMACDLONG_HISTOGRAM-_ColorA%LIGHT'] = 255
        for lineIndex in range (_NMAXLINES['MMACDLONG']):
            lineNumber = lineIndex+1
            self.objectConfig['MMACDLONG_MA{:d}_LineActive'.format(lineNumber)] = False
            self.objectConfig['MMACDLONG_MA{:d}_NSamples'.format(lineNumber)]   = 10*lineNumber
        #---DMIxADX Config
        self.objectConfig['DMIxADX_Master'] = False
        for lineIndex in range (_NMAXLINES['DMIxADX']):
            lineNumber = lineIndex+1
            self.objectConfig['DMIxADX_{:d}_LineActive'.format(lineNumber)] = False
            self.objectConfig['DMIxADX_{:d}_NSamples'.format(lineNumber)]   = 10*lineNumber
            self.objectConfig['DMIxADX_{:d}_Width'.format(lineNumber)] = 1
            self.objectConfig['DMIxADX_{:d}_ColorR%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['DMIxADX_{:d}_ColorG%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['DMIxADX_{:d}_ColorB%DARK'.format(lineNumber)] =random.randint(64, 255); self.objectConfig['DMIxADX_{:d}_ColorA%DARK'.format(lineNumber)] =255
            self.objectConfig['DMIxADX_{:d}_ColorR%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['DMIxADX_{:d}_ColorG%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['DMIxADX_{:d}_ColorB%LIGHT'.format(lineNumber)]=random.randint(64, 255); self.objectConfig['DMIxADX_{:d}_ColorA%LIGHT'.format(lineNumber)]=255
            self.objectConfig['DMIxADX_{:d}_Display'.format(lineNumber)] = True
        #---MFI Config
        self.objectConfig['MFI_Master'] = False
        for lineIndex in range (_NMAXLINES['MFI']):
            lineNumber = lineIndex+1
            self.objectConfig['MFI_{:d}_LineActive'.format(lineNumber)] = False
            self.objectConfig['MFI_{:d}_NSamples'.format(lineNumber)]   = 10*lineNumber
            self.objectConfig['MFI_{:d}_Width'.format(lineNumber)] = 1
            self.objectConfig['MFI_{:d}_ColorR%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['MFI_{:d}_ColorG%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['MFI_{:d}_ColorB%DARK'.format(lineNumber)] =random.randint(64, 255); self.objectConfig['MFI_{:d}_ColorA%DARK'.format(lineNumber)] =255
            self.objectConfig['MFI_{:d}_ColorR%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['MFI_{:d}_ColorG%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['MFI_{:d}_ColorB%LIGHT'.format(lineNumber)]=random.randint(64, 255); self.objectConfig['MFI_{:d}_ColorA%LIGHT'.format(lineNumber)]=255
            self.objectConfig['MFI_{:d}_Display'.format(lineNumber)] = True
        #---WOI Config
        self.objectConfig['WOI_Master'] = False
        self.objectConfig['WOI_BASE_Display'] = True
        self.objectConfig['WOI_BASE+_ColorR%DARK']  = 100; self.objectConfig['WOI_BASE+_ColorG%DARK']  = 255; self.objectConfig['WOI_BASE+_ColorB%DARK']  = 180; self.objectConfig['WOI_BASE+_ColorA%DARK']  = 180
        self.objectConfig['WOI_BASE+_ColorR%LIGHT'] =  80; self.objectConfig['WOI_BASE+_ColorG%LIGHT'] = 200; self.objectConfig['WOI_BASE+_ColorB%LIGHT'] = 150; self.objectConfig['WOI_BASE+_ColorA%LIGHT'] = 180
        self.objectConfig['WOI_BASE-_ColorR%DARK']  = 255; self.objectConfig['WOI_BASE-_ColorG%DARK']  = 100; self.objectConfig['WOI_BASE-_ColorB%DARK']  = 100; self.objectConfig['WOI_BASE-_ColorA%DARK']  = 180
        self.objectConfig['WOI_BASE-_ColorR%LIGHT'] = 240; self.objectConfig['WOI_BASE-_ColorG%LIGHT'] =  80; self.objectConfig['WOI_BASE-_ColorB%LIGHT'] =  80; self.objectConfig['WOI_BASE-_ColorA%LIGHT'] = 180
        for lineIndex in range (_NMAXLINES['WOI']):
            lineNumber = lineIndex+1
            self.objectConfig['WOI_{:d}_LineActive'.format(lineNumber)] = False
            self.objectConfig['WOI_{:d}_NSamples'.format(lineNumber)]   = 10*lineNumber
            self.objectConfig['WOI_{:d}_Sigma'.format(lineNumber)]      = round(2.5*lineNumber, 1)
            self.objectConfig['WOI_{:d}_Width'.format(lineNumber)] = 1
            self.objectConfig['WOI_{:d}_ColorR%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['WOI_{:d}_ColorG%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['WOI_{:d}_ColorB%DARK'.format(lineNumber)] =random.randint(64, 255); self.objectConfig['WOI_{:d}_ColorA%DARK'.format(lineNumber)] =255
            self.objectConfig['WOI_{:d}_ColorR%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['WOI_{:d}_ColorG%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['WOI_{:d}_ColorB%LIGHT'.format(lineNumber)]=random.randint(64, 255); self.objectConfig['WOI_{:d}_ColorA%LIGHT'.format(lineNumber)]=255
            self.objectConfig['WOI_{:d}_Display'.format(lineNumber)] = True
        #---NES Config
        self.objectConfig['NES_Master'] = False
        self.objectConfig['NES_BASE_Display'] = True
        self.objectConfig['NES_BASE+_ColorR%DARK']  = 100; self.objectConfig['NES_BASE+_ColorG%DARK']  = 255; self.objectConfig['NES_BASE+_ColorB%DARK']  = 180; self.objectConfig['NES_BASE+_ColorA%DARK']  = 180
        self.objectConfig['NES_BASE+_ColorR%LIGHT'] =  80; self.objectConfig['NES_BASE+_ColorG%LIGHT'] = 200; self.objectConfig['NES_BASE+_ColorB%LIGHT'] = 150; self.objectConfig['NES_BASE+_ColorA%LIGHT'] = 180
        self.objectConfig['NES_BASE-_ColorR%DARK']  = 255; self.objectConfig['NES_BASE-_ColorG%DARK']  = 100; self.objectConfig['NES_BASE-_ColorB%DARK']  = 100; self.objectConfig['NES_BASE-_ColorA%DARK']  = 180
        self.objectConfig['NES_BASE-_ColorR%LIGHT'] = 240; self.objectConfig['NES_BASE-_ColorG%LIGHT'] =  80; self.objectConfig['NES_BASE-_ColorB%LIGHT'] =  80; self.objectConfig['NES_BASE-_ColorA%LIGHT'] = 180
        for lineIndex in range (_NMAXLINES['NES']):
            lineNumber = lineIndex+1
            self.objectConfig['NES_{:d}_LineActive'.format(lineNumber)] = False
            self.objectConfig['NES_{:d}_NSamples'.format(lineNumber)]   = 10*lineNumber
            self.objectConfig['NES_{:d}_Sigma'.format(lineNumber)]      = round(2.5*lineNumber, 1)
            self.objectConfig['NES_{:d}_Width'.format(lineNumber)] = 1
            self.objectConfig['NES_{:d}_ColorR%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['NES_{:d}_ColorG%DARK'.format(lineNumber)] =random.randint(64,255); self.objectConfig['NES_{:d}_ColorB%DARK'.format(lineNumber)] =random.randint(64, 255); self.objectConfig['NES_{:d}_ColorA%DARK'.format(lineNumber)] =255
            self.objectConfig['NES_{:d}_ColorR%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['NES_{:d}_ColorG%LIGHT'.format(lineNumber)]=random.randint(64,255); self.objectConfig['NES_{:d}_ColorB%LIGHT'.format(lineNumber)]=random.randint(64, 255); self.objectConfig['NES_{:d}_ColorA%LIGHT'.format(lineNumber)]=255
            self.objectConfig['NES_{:d}_Display'.format(lineNumber)] = True

    def __matchGUIOsToConfig(self):
        #<MAIN>
        if (True):
            #---SI Viewer
            unassignedSIViewerNumbers = list(range(1, len(_SITYPES)+1))
            unassignedSIType          = list(_SITYPES)
            for siViewerNumber in range (1, len(_SITYPES)+1):
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_DISPLAYSWITCH{:d}".format(siViewerNumber)].setStatus(self.objectConfig['SIVIEWER{:d}Display'.format(siViewerNumber)], callStatusUpdateFunction = False)
                siAlloc = self.objectConfig['SIVIEWER{:d}SIAlloc'.format(siViewerNumber)]
                if (siAlloc in _SITYPES):
                    self.siTypes_siViewerAlloc[siAlloc] = siViewerNumber
                    self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_DISPLAYSELECTION{:d}".format(siViewerNumber)].setSelected(siAlloc, callSelectionUpdateFunction = False)
                    unassignedSIViewerNumbers.remove(siViewerNumber); unassignedSIType.remove(siAlloc)
            for i in range (len(unassignedSIViewerNumbers)):
                unassignedSIViewerNumber = unassignedSIViewerNumbers[i]
                unassignedSIType         = unassignedSIType[i]
                self.objectConfig['SIVIEWER{:d}SIAlloc'.format(unassignedSIViewerNumber)] = unassignedSIType
                self.siTypes_siViewerAlloc[unassignedSIType] = unassignedSIViewerNumber
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_DISPLAYSELECTION{:d}".format(unassignedSIViewerNumber)].setSelected(unassignedSIType, callSelectionUpdateFunction = False)
            #---Analyzer
            if (self.objectConfig['AnalysisRangeBeg'] == None): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_ANALYSISRANGEBEG_RANGEINPUT"].updateText(text = "")
            else:                                               self.settingsSubPages['MAIN'].GUIOs["ANALYZER_ANALYSISRANGEBEG_RANGEINPUT"].updateText(text = datetime.fromtimestamp(self.objectConfig['AnalysisRangeBeg'], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
            if (self.objectConfig['AnalysisRangeEnd'] == None): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_ANALYSISRANGEEND_RANGEINPUT"].updateText(text = "")
            else:                                               self.settingsSubPages['MAIN'].GUIOs["ANALYZER_ANALYSISRANGEEND_RANGEINPUT"].updateText(text = datetime.fromtimestamp(self.objectConfig['AnalysisRangeEnd'], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
            self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].deactivate()
            #---Trade Log
            self.settingsSubPages['MAIN'].GUIOs["TRADELOGDISPLAY_SWITCH"].setStatus(self.objectConfig['TRADELOG_Display'], callStatusUpdateFunction = False)
            self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_BUY_LED"].updateColor(self.objectConfig['TRADELOG_BUY_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                                     self.objectConfig['TRADELOG_BUY_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                                     self.objectConfig['TRADELOG_BUY_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                                     self.objectConfig['TRADELOG_BUY_ColorA%{:s}'.format(self.currentGUITheme)])
            self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_SELL_LED"].updateColor(self.objectConfig['TRADELOG_SELL_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                                      self.objectConfig['TRADELOG_SELL_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                                      self.objectConfig['TRADELOG_SELL_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                                      self.objectConfig['TRADELOG_SELL_ColorA%{:s}'.format(self.currentGUITheme)])
            self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_TARGETSELECTION"].setSelected('BUY', callSelectionUpdateFunction = True)
            self.settingsSubPages['MAIN'].GUIOs["TRADELOG_APPLYNEWSETTINGS"].deactivate()
            #---Bids and Asks
            self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSDISPLAY_SWITCH"].setStatus(self.objectConfig['BIDSANDASKS_Display'], callStatusUpdateFunction = False)
            self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_BIDS_LED"].updateColor(self.objectConfig['BIDSANDASKS_BIDS_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                                         self.objectConfig['BIDSANDASKS_BIDS_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                                         self.objectConfig['BIDSANDASKS_BIDS_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                                         self.objectConfig['BIDSANDASKS_BIDS_ColorA%{:s}'.format(self.currentGUITheme)])
            self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_ASKS_LED"].updateColor(self.objectConfig['BIDSANDASKS_ASKS_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                                         self.objectConfig['BIDSANDASKS_ASKS_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                                         self.objectConfig['BIDSANDASKS_ASKS_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                                         self.objectConfig['BIDSANDASKS_ASKS_ColorA%{:s}'.format(self.currentGUITheme)])
            self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_TARGETSELECTION"].setSelected('BIDS', callSelectionUpdateFunction = True)
            self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKS_APPLYNEWSETTINGS"].deactivate()
            #---Auxillaries
            self.settingsSubPages['MAIN'].GUIOs["AUX_KLINECOLORTYPE_SELECTIONBOX"].setSelected(self.objectConfig['KlineColorType'], callSelectionUpdateFunction = True)
            self.settingsSubPages['MAIN'].GUIOs["AUX_TIMEZONE_SELECTIONBOX"].setSelected(self.objectConfig['TimeZone'], callSelectionUpdateFunction = True)
        #<MAs>
        if (True):
            for maType in ('SMA','WMA','EMA'):
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_{:s}".format(maType)].setStatus(self.objectConfig['{:s}_Master'.format(maType)], callStatusUpdateFunction = False)
                for lineIndex in range (_NMAXLINES[maType]):
                    lineNumber = lineIndex+1
                    self.settingsSubPages[maType].GUIOs["INDICATOR_{:s}{:d}".format(maType,lineNumber)].setStatus(self.objectConfig['{:s}_{:d}_LineActive'.format(maType,lineNumber)], callStatusUpdateFunction = False)
                    self.settingsSubPages[maType].GUIOs["INDICATOR_{:s}{:d}_INTERVALINPUT".format(maType,lineNumber)].updateText(str(self.objectConfig['{:s}_{:d}_NSamples'.format(maType,lineNumber)]))
                    self.settingsSubPages[maType].GUIOs["INDICATOR_{:s}{:d}_WIDTHINPUT".format(maType,lineNumber)].updateText(str(self.objectConfig['{:s}_{:d}_Width'.format(maType,lineNumber)]))
                    self.settingsSubPages[maType].GUIOs["INDICATOR_{:s}{:d}_LINECOLOR".format(maType,lineNumber)].updateColor(self.objectConfig['{:s}_{:d}_ColorR%{:s}'.format(maType,lineNumber,self.currentGUITheme)], 
                                                                                                                              self.objectConfig['{:s}_{:d}_ColorG%{:s}'.format(maType,lineNumber,self.currentGUITheme)], 
                                                                                                                              self.objectConfig['{:s}_{:d}_ColorB%{:s}'.format(maType,lineNumber,self.currentGUITheme)], 
                                                                                                                              self.objectConfig['{:s}_{:d}_ColorA%{:s}'.format(maType,lineNumber,self.currentGUITheme)])
                    self.settingsSubPages[maType].GUIOs["INDICATOR_{:s}{:d}_DISPLAY".format(maType,lineNumber)].setStatus(self.objectConfig['{:s}_{:d}_Display'.format(maType,lineNumber)], callStatusUpdateFunction = False)
                self.settingsSubPages[maType].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelected('1')
                self.settingsSubPages[maType].GUIOs["APPLYNEWSETTINGS"].deactivate()
        #<PSAR>
        if (True):
            self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_PSAR"].setStatus(self.objectConfig['PSAR_Master'], callStatusUpdateFunction = False)
            for lineIndex in range (_NMAXLINES['PSAR']):
                lineNumber = lineIndex+1
                self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}".format(lineNumber)].setStatus(self.objectConfig['PSAR_{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
                self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_AF0INPUT".format(lineNumber)].updateText(str(self.objectConfig['PSAR_{:d}_AF0'.format(lineNumber)]))
                self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_AF+INPUT".format(lineNumber)].updateText(str(self.objectConfig['PSAR_{:d}_AF+'.format(lineNumber)]))
                self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_AFMAXINPUT".format(lineNumber)].updateText(str(self.objectConfig['PSAR_{:d}_AFMax'.format(lineNumber)]))
                self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_WIDTHINPUT".format(lineNumber)].updateText(str(self.objectConfig['PSAR_{:d}_Width'.format(lineNumber)]))
                self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_LINECOLOR".format(lineNumber)].updateColor(self.objectConfig['PSAR_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                   self.objectConfig['PSAR_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                   self.objectConfig['PSAR_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                   self.objectConfig['PSAR_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)])
                self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_DISPLAY".format(lineNumber)].setStatus(self.objectConfig['PSAR_{:d}_Display'.format(lineNumber)], callStatusUpdateFunction = False)
            self.settingsSubPages['PSAR'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelected('1')
            self.settingsSubPages['PSAR'].GUIOs["APPLYNEWSETTINGS"].deactivate()
        #<BOL>
        if (True):
            self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_BOL"].setStatus(self.objectConfig['BOL_Master'], callStatusUpdateFunction = False)
            self.settingsSubPages['BOL'].GUIOs["INDICATOR_MATYPESELECTION"].setSelected(self.objectConfig['BOL_MAType'], callSelectionUpdateFunction = False)
            for lineIndex in range (_NMAXLINES['BOL']):
                lineNumber = lineIndex+1
                self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}".format(lineNumber)].setStatus(self.objectConfig['BOL_{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
                self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_INTERVALINPUT".format(lineNumber)].updateText(str(self.objectConfig['BOL_{:d}_NSamples'.format(lineNumber)]))
                self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_BANDWIDTHINPUT".format(lineNumber)].updateText(str(self.objectConfig['BOL_{:d}_BandWidth'.format(lineNumber)]))
                self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_WIDTHINPUT".format(lineNumber)].updateText(str(self.objectConfig['BOL_{:d}_Width'.format(lineNumber)]))
                self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_LINECOLOR".format(lineNumber)].updateColor(self.objectConfig['BOL_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['BOL_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['BOL_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['BOL_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)])
                self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_DISPLAY".format(lineNumber)].setStatus(self.objectConfig['BOL_{:d}_Display'.format(lineNumber)], callStatusUpdateFunction = False)
            self.settingsSubPages['BOL'].GUIOs["INDICATOR_DISPLAYCONTENTS_BOLCENTERSWITCH"].setStatus(self.objectConfig['BOL_DisplayCenterLine'], callStatusUpdateFunction = False)
            self.settingsSubPages['BOL'].GUIOs["INDICATOR_DISPLAYCONTENTS_BOLBANDSWITCH"].setStatus(self.objectConfig['BOL_DisplayBand'], callStatusUpdateFunction = False)
            self.settingsSubPages['BOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelected('1')
            self.settingsSubPages['BOL'].GUIOs["APPLYNEWSETTINGS"].deactivate()
        #<IVP>
        if (True):
            self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_IVP"].setStatus(self.objectConfig['IVP_Master'], callStatusUpdateFunction = False)
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_VPLP_DISPLAYSWITCH"].setStatus(self.objectConfig['IVP_VPLP_Display'], callStatusUpdateFunction = False)
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_VPLP_COLOR"].updateColor(self.objectConfig['IVP_VPLP_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                                   self.objectConfig['IVP_VPLP_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                                   self.objectConfig['IVP_VPLP_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                                   self.objectConfig['IVP_VPLP_ColorA%{:s}'.format(self.currentGUITheme)])
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_VPLP_DISPLAYWIDTHSLIDER"].setSliderValue(newValue = (self.objectConfig['IVP_VPLP_DisplayWidth']-0.1)/0.9*100, callValueUpdateFunction = False)
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_VPLP_DISPLAYWIDTHVALUETEXT"].updateText(str(self.objectConfig['IVP_VPLP_DisplayWidth']))
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_VPLPB_DISPLAYSWITCH"].setStatus(self.objectConfig['IVP_VPLPB_Display'], callStatusUpdateFunction = False)
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_VPLPB_COLOR"].updateColor(self.objectConfig['IVP_VPLPB_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                                    self.objectConfig['IVP_VPLPB_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                                    self.objectConfig['IVP_VPLPB_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                                    self.objectConfig['IVP_VPLPB_ColorA%{:s}'.format(self.currentGUITheme)])
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_VPLPB_DISPLAYREGIONSLIDER"].setSliderValue(newValue = (self.objectConfig['IVP_VPLPB_DisplayRegion']-0.050)*(100/0.950), callValueUpdateFunction = False)
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_VPLPB_DISPLAYREGIONVALUETEXT"].updateText("{:.1f} %".format(self.objectConfig['IVP_VPLPB_DisplayRegion']*100))
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_INTERVAL_INPUTTEXT"].updateText(text = "{:d}".format(self.objectConfig['IVP_NSamples']))
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_GAMMAFACTOR_SLIDER"].setSliderValue(newValue = (self.objectConfig['IVP_GammaFactor']-0.005)*(100/0.095), callValueUpdateFunction = False)
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_GAMMAFACTOR_VALUETEXT"].updateText(text = "{:.1f} %".format(self.objectConfig['IVP_GammaFactor']*100))
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_DELTAFACTOR_SLIDER"].setSliderValue(newValue = (self.objectConfig['IVP_DeltaFactor']-0.1)*(100/9.9), callValueUpdateFunction = False)
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_DELTAFACTOR_VALUETEXT"].updateText(text = "{:d} %".format(int(self.objectConfig['IVP_DeltaFactor']*100)))
            self.settingsSubPages['IVP'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelected('VPLP')
            self.settingsSubPages['IVP'].GUIOs["APPLYNEWSETTINGS"].deactivate()
        #<PIP>
        if (True):
            self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_PIP"].setStatus(self.objectConfig['PIP_Master'], callStatusUpdateFunction = False)
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_SWING_DISPLAYSWITCH"].setStatus(self.objectConfig['PIP_SWING_Display'],                     callStatusUpdateFunction = False)
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_NNASIGNAL_DISPLAYSWITCH"].setStatus(self.objectConfig['PIP_NNASIGNAL_Display'],             callStatusUpdateFunction = False)
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_WOISIGNAL_DISPLAYSWITCH"].setStatus(self.objectConfig['PIP_WOISIGNAL_Display'],             callStatusUpdateFunction = False)
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_NESSIGNAL_DISPLAYSWITCH"].setStatus(self.objectConfig['PIP_NESSIGNAL_Display'],             callStatusUpdateFunction = False)
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALSIGNAL_DISPLAYSWITCH"].setStatus(self.objectConfig['PIP_CLASSICALSIGNAL_Display'], callStatusUpdateFunction = False)
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALSIGNAL_DISPLAYTYPESELECTION"].setSelected(itemKey = self.objectConfig['PIP_CLASSICALSIGNAL_DisplayType'], callSelectionUpdateFunction = False)
            for _target in ('SWING', 'NNASIGNAL+', 'NNASIGNAL-', 'WOISIGNAL+', 'WOISIGNAL-', 'NESSIGNAL+', 'NESSIGNAL-', 'CLASSICALSIGNAL+', 'CLASSICALSIGNAL-'):
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_{:s}_COLOR".format(_target)].updateColor(self.objectConfig['PIP_{:s}_ColorR%{:s}'.format(_target, self.currentGUITheme)], 
                                                                                                       self.objectConfig['PIP_{:s}_ColorG%{:s}'.format(_target, self.currentGUITheme)], 
                                                                                                       self.objectConfig['PIP_{:s}_ColorB%{:s}'.format(_target, self.currentGUITheme)], 
                                                                                                       self.objectConfig['PIP_{:s}_ColorA%{:s}'.format(_target, self.currentGUITheme)])
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_SWINGRANGE_SLIDER"].setSliderValue(newValue = (self.objectConfig['PIP_SwingRange']-0.0010)*(100/0.0490), callValueUpdateFunction = False)
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_SWINGRANGE_VALUETEXT"].updateText(text = "{:.2f} %".format(self.objectConfig['PIP_SwingRange']*100))
            self.settingsSubPages['PIP'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelected('SWING')
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_NNAALPHA_SLIDER"].setSliderValue(newValue = (self.objectConfig['PIP_NNAAlpha']-0.05)*(100/0.95), callValueUpdateFunction = False)
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_NNAALPHA_VALUETEXT"].updateText(text = "{:.2f}".format(self.objectConfig['PIP_NNAAlpha']))
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_NNABETA_SLIDER"].setSliderValue(newValue = (self.objectConfig['PIP_NNABeta']-2)*(100/18), callValueUpdateFunction = False)
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_NNABETA_VALUETEXT"].updateText(text = "{:d}".format(self.objectConfig['PIP_NNABeta']))
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALALPHA_SLIDER"].setSliderValue(newValue = (self.objectConfig['PIP_ClassicalAlpha']-0.1)*(100/2.9), callValueUpdateFunction = False)
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALALPHA_VALUETEXT"].updateText(text = "{:.1f}".format(self.objectConfig['PIP_ClassicalAlpha']))
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALBETA_SLIDER"].setSliderValue(newValue = (self.objectConfig['PIP_ClassicalBeta']-2)*(100/18), callValueUpdateFunction = False)
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALBETA_VALUETEXT"].updateText(text = "{:d}".format(self.objectConfig['PIP_ClassicalBeta']))
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALNSAMPLES_INPUTTEXT"].updateText(text = "{:d}".format(self.objectConfig['PIP_ClassicalNSamples']))
            self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALSIGMA_INPUTTEXT"].updateText(text   = "{:.1f}".format(self.objectConfig['PIP_ClassicalSigma']))
            self.settingsSubPages['PIP'].GUIOs["APPLYNEWSETTINGS"].deactivate()
        #<VOL>
        if (True):
            self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_VOL"].setStatus(self.objectConfig['VOL_Master'], callStatusUpdateFunction = False)
            for lineIndex in range (_NMAXLINES['VOL']):
                lineNumber = lineIndex+1
                self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}".format(lineNumber)].setStatus(self.objectConfig['VOL_{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
                self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_INTERVALINPUT".format(lineNumber)].updateText(str(self.objectConfig['VOL_{:d}_NSamples'.format(lineNumber)]))
                self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_WIDTHINPUT".format(lineNumber)].updateText(str(self.objectConfig['VOL_{:d}_Width'.format(lineNumber)]))
                self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_LINECOLOR".format(lineNumber)].updateColor(self.objectConfig['VOL_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['VOL_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['VOL_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['VOL_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)])
                self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_DISPLAY".format(lineNumber)].setStatus(self.objectConfig['VOL_{:d}_Display'.format(lineNumber)], callStatusUpdateFunction = False)
            self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOLTYPESELECTION"].setSelected(self.objectConfig['VOL_VolumeType'], callSelectionUpdateFunction = False)
            self.settingsSubPages['VOL'].GUIOs["INDICATOR_MATYPESELECTION"].setSelected(self.objectConfig['VOL_MAType'], callSelectionUpdateFunction = False)
            self.settingsSubPages['VOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelected('1')
            self.settingsSubPages['VOL'].GUIOs["APPLYNEWSETTINGS"].deactivate()
        #<MMACDSHORT>
        if (True):
            self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_MMACDSHORT"].setStatus(self.objectConfig['MMACDSHORT_Master'], callStatusUpdateFunction = False)
            self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_MMACD_DISPLAYSWITCH"].setStatus(self.objectConfig['MMACDSHORT_MMACD_Display'], callStatusUpdateFunction = False)
            self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_SIGNAL_DISPLAYSWITCH"].setStatus(self.objectConfig['MMACDSHORT_SIGNAL_Display'], callStatusUpdateFunction = False)
            self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_HISTOGRAM_DISPLAYSWITCH"].setStatus(self.objectConfig['MMACDSHORT_HISTOGRAM_Display'], callStatusUpdateFunction = False)
            self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_MMACD_COLOR"].updateColor(self.objectConfig['MMACDSHORT_MMACD_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                                           self.objectConfig['MMACDSHORT_MMACD_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                                           self.objectConfig['MMACDSHORT_MMACD_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                                           self.objectConfig['MMACDSHORT_MMACD_ColorA%{:s}'.format(self.currentGUITheme)])
            self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_SIGNAL_COLOR"].updateColor(self.objectConfig['MMACDSHORT_SIGNAL_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                                            self.objectConfig['MMACDSHORT_SIGNAL_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                                            self.objectConfig['MMACDSHORT_SIGNAL_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                                            self.objectConfig['MMACDSHORT_SIGNAL_ColorA%{:s}'.format(self.currentGUITheme)])
            self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_HISTOGRAM+_COLOR"].updateColor(self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                                                self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                                                self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                                                self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorA%{:s}'.format(self.currentGUITheme)])
            self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_HISTOGRAM-_COLOR"].updateColor(self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                                                self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                                                self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                                                self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorA%{:s}'.format(self.currentGUITheme)])
            self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_SIGNALINTERVALTEXTINPUT"].updateText(str(self.objectConfig['MMACDSHORT_SignalNSamples']))
            self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_MULTIPLIERTEXTINPUT"].updateText(str(self.objectConfig['MMACDSHORT_Multiplier']))
            for lineIndex in range (_NMAXLINES['MMACDSHORT']):
                lineNumber = lineIndex+1
                self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_MMACDMA{:d}".format(lineNumber)].setStatus(self.objectConfig['MMACDSHORT_MA{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
                self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_MMACDMA{:d}_INTERVALINPUT".format(lineNumber)].updateText(str(self.objectConfig['MMACDSHORT_MA{:d}_NSamples'.format(lineNumber)]))
            self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelected('MMACD')
            self.settingsSubPages['MMACDSHORT'].GUIOs["APPLYNEWSETTINGS"].deactivate()
        #<MMACDLONG>
        if (True):
            self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_MMACDLONG"].setStatus(self.objectConfig['MMACDLONG_Master'], callStatusUpdateFunction = False)
            self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_MMACD_DISPLAYSWITCH"].setStatus(self.objectConfig['MMACDLONG_MMACD_Display'], callStatusUpdateFunction = False)
            self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_SIGNAL_DISPLAYSWITCH"].setStatus(self.objectConfig['MMACDLONG_SIGNAL_Display'], callStatusUpdateFunction = False)
            self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_HISTOGRAM_DISPLAYSWITCH"].setStatus(self.objectConfig['MMACDLONG_HISTOGRAM_Display'], callStatusUpdateFunction = False)
            self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_MMACD_COLOR"].updateColor(self.objectConfig['MMACDLONG_MMACD_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                                          self.objectConfig['MMACDLONG_MMACD_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                                          self.objectConfig['MMACDLONG_MMACD_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                                          self.objectConfig['MMACDLONG_MMACD_ColorA%{:s}'.format(self.currentGUITheme)])
            self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_SIGNAL_COLOR"].updateColor(self.objectConfig['MMACDLONG_SIGNAL_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                                           self.objectConfig['MMACDLONG_SIGNAL_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                                           self.objectConfig['MMACDLONG_SIGNAL_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                                           self.objectConfig['MMACDLONG_SIGNAL_ColorA%{:s}'.format(self.currentGUITheme)])
            self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_HISTOGRAM+_COLOR"].updateColor(self.objectConfig['MMACDLONG_HISTOGRAM+_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                                               self.objectConfig['MMACDLONG_HISTOGRAM+_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                                               self.objectConfig['MMACDLONG_HISTOGRAM+_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                                               self.objectConfig['MMACDLONG_HISTOGRAM+_ColorA%{:s}'.format(self.currentGUITheme)])
            self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_HISTOGRAM-_COLOR"].updateColor(self.objectConfig['MMACDLONG_HISTOGRAM-_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                                               self.objectConfig['MMACDLONG_HISTOGRAM-_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                                               self.objectConfig['MMACDLONG_HISTOGRAM-_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                                               self.objectConfig['MMACDLONG_HISTOGRAM-_ColorA%{:s}'.format(self.currentGUITheme)])
            self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_SIGNALINTERVALTEXTINPUT"].updateText(str(self.objectConfig['MMACDLONG_SignalNSamples']))
            self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_MULTIPLIERTEXTINPUT"].updateText(str(self.objectConfig['MMACDLONG_Multiplier']))
            for lineIndex in range (_NMAXLINES['MMACDLONG']):
                lineNumber = lineIndex+1
                self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_MMACDMA{:d}".format(lineNumber)].setStatus(self.objectConfig['MMACDLONG_MA{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
                self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_MMACDMA{:d}_INTERVALINPUT".format(lineNumber)].updateText(str(self.objectConfig['MMACDLONG_MA{:d}_NSamples'.format(lineNumber)]))
            self.settingsSubPages['MMACDLONG'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelected('MMACD')
            self.settingsSubPages['MMACDLONG'].GUIOs["APPLYNEWSETTINGS"].deactivate()
        #<DMIxADX>
        if (True):
            self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_DMIxADX"].setStatus(self.objectConfig['DMIxADX_Master'], callStatusUpdateFunction = False)
            for lineIndex in range (_NMAXLINES['DMIxADX']):
                lineNumber = lineIndex+1
                self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}".format(lineNumber)].setStatus(self.objectConfig['DMIxADX_{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
                self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_INTERVALINPUT".format(lineNumber)].updateText(str(self.objectConfig['DMIxADX_{:d}_NSamples'.format(lineNumber)]))
                self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_WIDTHINPUT".format(lineNumber)].updateText(str(self.objectConfig['DMIxADX_{:d}_Width'.format(lineNumber)]))
                self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_LINECOLOR".format(lineNumber)].updateColor(self.objectConfig['DMIxADX_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                         self.objectConfig['DMIxADX_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                         self.objectConfig['DMIxADX_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                         self.objectConfig['DMIxADX_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)])
                self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_DISPLAY".format(lineNumber)].setStatus(self.objectConfig['DMIxADX_{:d}_Display'.format(lineNumber)], callStatusUpdateFunction = False)
            self.settingsSubPages['DMIxADX'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelected('1')
            self.settingsSubPages['DMIxADX'].GUIOs["APPLYNEWSETTINGS"].deactivate()
        #<MFI>
        if (True):
            self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_MFI"].setStatus(self.objectConfig['MFI_Master'], callStatusUpdateFunction = False)
            for lineIndex in range (_NMAXLINES['MFI']):
                lineNumber = lineIndex+1
                self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}".format(lineNumber)].setStatus(self.objectConfig['MFI_{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
                self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_INTERVALINPUT".format(lineNumber)].updateText(str(self.objectConfig['MFI_{:d}_NSamples'.format(lineNumber)]))
                self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_WIDTHINPUT".format(lineNumber)].updateText(str(self.objectConfig['MFI_{:d}_Width'.format(lineNumber)]))
                self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_LINECOLOR".format(lineNumber)].updateColor(self.objectConfig['MFI_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['MFI_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['MFI_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['MFI_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)])
                self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_DISPLAY".format(lineNumber)].setStatus(self.objectConfig['MFI_{:d}_Display'.format(lineNumber)], callStatusUpdateFunction = False)
            self.settingsSubPages['MFI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelected('1')
            self.settingsSubPages['MFI'].GUIOs["APPLYNEWSETTINGS"].deactivate()
        #<WOI>
        if (True):
            self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_WOI"].setStatus(self.objectConfig['WOI_Master'], callStatusUpdateFunction = False)
            self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOIBASE_DISPLAYSWITCH"].setStatus(self.objectConfig['WOI_BASE_Display'], callStatusUpdateFunction = False)
            for _target in ('BASE+', 'BASE-'):
                self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:s}_LINECOLOR".format(_target)].updateColor(self.objectConfig['WOI_{:s}_ColorR%{:s}'.format(_target,self.currentGUITheme)], 
                                                                                                              self.objectConfig['WOI_{:s}_ColorG%{:s}'.format(_target,self.currentGUITheme)], 
                                                                                                              self.objectConfig['WOI_{:s}_ColorB%{:s}'.format(_target,self.currentGUITheme)], 
                                                                                                              self.objectConfig['WOI_{:s}_ColorA%{:s}'.format(_target,self.currentGUITheme)])
            for lineIndex in range (_NMAXLINES['WOI']):
                lineNumber = lineIndex+1
                self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}".format(lineNumber)].setStatus(self.objectConfig['WOI_{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
                self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_INTERVALINPUT".format(lineNumber)].updateText(text = "{:d}".format(self.objectConfig['WOI_{:d}_NSamples'.format(lineNumber)]))
                self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_SIGMAINPUT".format(lineNumber)].updateText(text = "{:.1f}".format(self.objectConfig['WOI_{:d}_Sigma'.format(lineNumber)]))
                self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_WIDTHINPUT".format(lineNumber)].updateText(text = "{:d}".format(self.objectConfig['WOI_{:d}_Width'.format(lineNumber)]))
                self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_LINECOLOR".format(lineNumber)].updateColor(self.objectConfig['WOI_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['WOI_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['WOI_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['WOI_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)])
                self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_DISPLAY".format(lineNumber)].setStatus(self.objectConfig['WOI_{:d}_Display'.format(lineNumber)], callStatusUpdateFunction = False)
            self.settingsSubPages['WOI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelected('BASE+')
            self.settingsSubPages['WOI'].GUIOs["APPLYNEWSETTINGS"].deactivate()
        #<NES>
        if (True):
            self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_NES"].setStatus(self.objectConfig['NES_Master'], callStatusUpdateFunction = False)
            self.settingsSubPages['NES'].GUIOs["INDICATOR_NESBASE_DISPLAYSWITCH"].setStatus(self.objectConfig['NES_BASE_Display'], callStatusUpdateFunction = False)
            for _target in ('BASE+', 'BASE-'):
                self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:s}_LINECOLOR".format(_target)].updateColor(self.objectConfig['NES_{:s}_ColorR%{:s}'.format(_target,self.currentGUITheme)], 
                                                                                                              self.objectConfig['NES_{:s}_ColorG%{:s}'.format(_target,self.currentGUITheme)], 
                                                                                                              self.objectConfig['NES_{:s}_ColorB%{:s}'.format(_target,self.currentGUITheme)], 
                                                                                                              self.objectConfig['NES_{:s}_ColorA%{:s}'.format(_target,self.currentGUITheme)])
            for lineIndex in range (_NMAXLINES['NES']):
                lineNumber = lineIndex+1
                self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}".format(lineNumber)].setStatus(self.objectConfig['NES_{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
                self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_INTERVALINPUT".format(lineNumber)].updateText(text = "{:d}".format(self.objectConfig['NES_{:d}_NSamples'.format(lineNumber)]))
                self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_SIGMAINPUT".format(lineNumber)].updateText(text = "{:.1f}".format(self.objectConfig['NES_{:d}_Sigma'.format(lineNumber)]))
                self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_WIDTHINPUT".format(lineNumber)].updateText(text = "{:d}".format(self.objectConfig['NES_{:d}_Width'.format(lineNumber)]))
                self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_LINECOLOR".format(lineNumber)].updateColor(self.objectConfig['NES_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['NES_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['NES_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['NES_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)])
                self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_DISPLAY".format(lineNumber)].setStatus(self.objectConfig['NES_{:d}_Display'.format(lineNumber)], callStatusUpdateFunction = False)
            self.settingsSubPages['NES'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelected('BASE+')
            self.settingsSubPages['NES'].GUIOs["APPLYNEWSETTINGS"].deactivate()

        #Set SubIndicator Switch Activation
        if (True):
            for siViewerNumber in range (1, len(_SITYPES)+1):
                if (siViewerNumber <= self.usableSIViewers): self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_DISPLAYSWITCH{:d}".format(siViewerNumber)].activate()
                else:
                    self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_DISPLAYSWITCH{:d}".format(siViewerNumber)].setStatus(False)
                    self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_DISPLAYSWITCH{:d}".format(siViewerNumber)].deactivate()

        #Final 'AUX_SAVECONFIGURATION' Deactivation
        self.settingsSubPages['MAIN'].GUIOs["AUX_SAVECONFIGURATION"].deactivate()
    #Object Configuration & GUIO Initialization END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #DisplayBox Control ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __configureDisplayBoxes(self, onInit = False):
        #[1]: Determine Vertical DisplayBox Order
        if (True):
            #--- Temporal Grid
            self.displayBox_VerticalSection_Order = ['TEMPORALGRID']; self.displayBox_VisibleBoxes = ['MAINGRID_TEMPORAL', 'SETTINGSBUTTONFRAME']
            #--- SI Viewers (Reverse Order)
            for siViewerNumber in range (self.usableSIViewers, 0, -1):
                if (self.objectConfig['SIVIEWER{:d}Display'.format(siViewerNumber)] == True):
                    self.displayBox_VerticalSection_Order.append('SIVIEWER{:d}'.format(siViewerNumber))
                    self.displayBox_VisibleBoxes += ['SIVIEWER{:d}'.format(siViewerNumber)]
            #--- Klines Price
            self.displayBox_VerticalSection_Order.append('KLINESPRICE')
            self.displayBox_VisibleBoxes += ['KLINESPRICE']
            #--- AUX Bar
            self.displayBox_VerticalSection_Order.append('AUXILLARYBAR')
            self.displayBox_VisibleBoxes.append('AUXILLARYBAR')
            
        #[2]: Determine DisplayBox Dimensions
        if (True):
            #---Determin General Section Width
            displayBoxWidth_leftSection  = self.width - _GD_DISPLAYBOX_RIGHTSECTION_WIDTH - _GD_DISPLAYBOX_GOFFSET
            displayBoxWidth_rightSection = _GD_DISPLAYBOX_RIGHTSECTION_WIDTH

            #---Determine Vertical Section Height
            nVisibleVerticalSections = len(self.displayBox_VerticalSection_Order)
            nVisibleSIViewers        = len([verticalSectionName for verticalSectionName in self.displayBox_VerticalSection_Order if verticalSectionName[:8] == 'SIVIEWER'])
            nAvailableHeight = self.height - _GD_DISPLAYBOX_GOFFSET*(nVisibleVerticalSections-1) - _GD_DISPLAYBOX_MAINGRIDTEMPORAL_HEIGHT
            nAvailableHeight -= _GD_DISPLAYBOX_SIVIEWER_HEIGHT*nVisibleSIViewers
            nAvailableHeight -= _GD_DISPLAYBOX_AUXILLARYBAR_HEIGHT
            displayBoxHeight_KLINESPRICE = nAvailableHeight
        
            #---Set DisplayBox Coordinates and Dimensions
            verticalSectionYPos = self.yPos
            for verticalSectionName in self.displayBox_VerticalSection_Order:
                if (verticalSectionName == 'TEMPORALGRID'):
                    #Define DisplayBox and DrawBox Dimensions for 'MAINGRID_TEMPORAL'
                    displayBox_MAINGRID_TEMPORAL = (self.xPos, verticalSectionYPos, displayBoxWidth_leftSection , _GD_DISPLAYBOX_MAINGRIDTEMPORAL_HEIGHT)
                    drawBox_MAINGRID_TEMPORAL    = (displayBox_MAINGRID_TEMPORAL[0]+_GD_DISPLAYBOX_GOFFSET, displayBox_MAINGRID_TEMPORAL[1]+_GD_DISPLAYBOX_GOFFSET, displayBox_MAINGRID_TEMPORAL[2]-_GD_DISPLAYBOX_GOFFSET*2, displayBox_MAINGRID_TEMPORAL[3]-_GD_DISPLAYBOX_GOFFSET*2)
                    self.displayBox['MAINGRID_TEMPORAL']                     = displayBox_MAINGRID_TEMPORAL
                    self.displayBox_graphics['MAINGRID_TEMPORAL']['DRAWBOX'] = drawBox_MAINGRID_TEMPORAL
                
                    #Define DisplayBox Dimensions for 'SETTINGSBUTTONFRAME'
                    displayBox_SETTINGSBUTTONFRAME = (self.xPos+displayBoxWidth_leftSection+_GD_DISPLAYBOX_GOFFSET, verticalSectionYPos, displayBoxWidth_rightSection, _GD_DISPLAYBOX_MAINGRIDTEMPORAL_HEIGHT)
                    self.displayBox['SETTINGSBUTTONFRAME'] = displayBox_SETTINGSBUTTONFRAME

                    verticalSectionYPos += _GD_DISPLAYBOX_MAINGRIDTEMPORAL_HEIGHT+_GD_DISPLAYBOX_GOFFSET

                elif (verticalSectionName[:8] == 'SIVIEWER'):
                    #Define DisplayBox and DrawBox Dimensions for 'SIVIEWER[X]'
                    displayBox_SIVIEWER = (self.xPos, verticalSectionYPos, displayBoxWidth_leftSection , _GD_DISPLAYBOX_SIVIEWER_HEIGHT)
                    drawBox_SIVIEWER    = (displayBox_SIVIEWER[0]+_GD_DISPLAYBOX_GOFFSET, displayBox_SIVIEWER[1]+_GD_DISPLAYBOX_GOFFSET, displayBox_SIVIEWER[2]-_GD_DISPLAYBOX_GOFFSET*2, displayBox_SIVIEWER[3]-_GD_DISPLAYBOX_GOFFSET*2)
                    self.displayBox[verticalSectionName]                     = displayBox_SIVIEWER
                    self.displayBox_graphics[verticalSectionName]['DRAWBOX'] = drawBox_SIVIEWER
                
                    #Define DisplayBox and DrawBox Dimensions for 'MAINGRID_SIVIEWER[X]'
                    displayBox_MAINGRID_SIVIEWER = (self.xPos+displayBoxWidth_leftSection+_GD_DISPLAYBOX_GOFFSET, verticalSectionYPos, displayBoxWidth_rightSection, _GD_DISPLAYBOX_SIVIEWER_HEIGHT)
                    drawBox_MAINGRID_SIVIEWER    = (displayBox_MAINGRID_SIVIEWER[0]+_GD_DISPLAYBOX_GOFFSET, displayBox_MAINGRID_SIVIEWER[1]+_GD_DISPLAYBOX_GOFFSET, displayBox_MAINGRID_SIVIEWER[2]-_GD_DISPLAYBOX_GOFFSET*2, displayBox_MAINGRID_SIVIEWER[3]-_GD_DISPLAYBOX_GOFFSET*2)
                    self.displayBox['MAINGRID_'+verticalSectionName]                     = displayBox_MAINGRID_SIVIEWER
                    self.displayBox_graphics['MAINGRID_'+verticalSectionName]['DRAWBOX'] = drawBox_MAINGRID_SIVIEWER

                    verticalSectionYPos += _GD_DISPLAYBOX_SIVIEWER_HEIGHT+_GD_DISPLAYBOX_GOFFSET

                elif (verticalSectionName == 'KLINESPRICE'):
                    #Define DisplayBox and DrawBox Dimensions for 'KLINESPRICE'
                    displayBox_KLINESPRICE = (self.xPos, verticalSectionYPos, displayBoxWidth_leftSection , displayBoxHeight_KLINESPRICE)
                    drawBox_KLINESPRICE    = (displayBox_KLINESPRICE[0]+_GD_DISPLAYBOX_GOFFSET, displayBox_KLINESPRICE[1]+_GD_DISPLAYBOX_GOFFSET, displayBox_KLINESPRICE[2]-_GD_DISPLAYBOX_GOFFSET*2, displayBox_KLINESPRICE[3]-_GD_DISPLAYBOX_GOFFSET*2)
                    self.displayBox['KLINESPRICE']                     = displayBox_KLINESPRICE
                    self.displayBox_graphics['KLINESPRICE']['DRAWBOX'] = drawBox_KLINESPRICE

                    #Define DisplayBox and DrawBox Dimensions for 'MAINGRID_KLINESPRICE'
                    displayBox_MAINGRID_KLINESPRICE = (self.xPos+displayBoxWidth_leftSection+_GD_DISPLAYBOX_GOFFSET, verticalSectionYPos, displayBoxWidth_rightSection, displayBoxHeight_KLINESPRICE)
                    drawBox_MAINGRID_KLINESPRICE    = (displayBox_MAINGRID_KLINESPRICE[0]+_GD_DISPLAYBOX_GOFFSET, displayBox_MAINGRID_KLINESPRICE[1]+_GD_DISPLAYBOX_GOFFSET, displayBox_MAINGRID_KLINESPRICE[2]-_GD_DISPLAYBOX_GOFFSET*2, displayBox_MAINGRID_KLINESPRICE[3]-_GD_DISPLAYBOX_GOFFSET*2)
                    self.displayBox['MAINGRID_KLINESPRICE']                     = displayBox_MAINGRID_KLINESPRICE
                    self.displayBox_graphics['MAINGRID_KLINESPRICE']['DRAWBOX'] = drawBox_MAINGRID_KLINESPRICE

                    verticalSectionYPos += displayBoxHeight_KLINESPRICE+_GD_DISPLAYBOX_GOFFSET

                elif (verticalSectionName == 'AUXILLARYBAR'):
                    #Define DisplayBox Dimensions for 'AUXILLARYBAR'
                    displayBox_AUXILLARYBAR = (self.xPos, verticalSectionYPos, self.width, _GD_DISPLAYBOX_AUXILLARYBAR_HEIGHT)
                    drawBox_AUXILLARYBAR    = (displayBox_KLINESPRICE[0]+_GD_DISPLAYBOX_GOFFSET, displayBox_KLINESPRICE[1]+_GD_DISPLAYBOX_GOFFSET, displayBox_KLINESPRICE[2]-_GD_DISPLAYBOX_GOFFSET*2, displayBox_KLINESPRICE[3]-_GD_DISPLAYBOX_GOFFSET*2)
                    self.displayBox['AUXILLARYBAR'] = displayBox_AUXILLARYBAR
                    self.displayBox_graphics['AUXILLARYBAR']['DRAWBOX'] = drawBox_AUXILLARYBAR
                
        #[3]: Set DisplayBox Objects (HitBox, Images, FrameSprites, CamGroups, RCLCGs, etc.)
        if (True):
            self.nMaxVerticalGridLines = int((self.displayBox['MAINGRID_TEMPORAL'][2]-_GD_DISPLAYBOX_GOFFSET*2)*self.scaler/_GD_DISPLAYBOX_GRID_VERTICALLINEPIXELINTERVAL)
            self.nMaxHorizontalGridLines['KLINESPRICE'] = int((self.displayBox['KLINESPRICE'][3]-_GD_DISPLAYBOX_GOFFSET*2)*self.scaler/_GD_DISPLAYBOX_GRID_HORIZONTALLINEPIXELINTERVAL)

            if (onInit == True):
                for displayBoxName in self.displayBox:
                    self.mouse_DragDX[displayBoxName] = 0; self.mouse_DragDY[displayBoxName] = 0; self.mouse_ScrollDX[displayBoxName] = 0; self.mouse_ScrollDY[displayBoxName] = 0
                    #---MAINGRID_TEMPORAL
                    if (displayBoxName == 'MAINGRID_TEMPORAL'):
                        displayBox = self.displayBox['MAINGRID_TEMPORAL']
                        drawBox    = self.displayBox_graphics['MAINGRID_TEMPORAL']['DRAWBOX']
                        
                        #Generate Graphic Sprites and Hitboxes
                        self.hitBox['MAINGRID_TEMPORAL'] = atmEta_gui_HitBoxes.hitBox_Rectangular(drawBox[0], drawBox[1], drawBox[2], drawBox[3])
                        self.images['MAINGRID_TEMPORAL'] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                        self.frameSprites['MAINGRID_TEMPORAL'] = pyglet.sprite.Sprite(x = displayBox[0]*self.scaler, y = displayBox[1]*self.scaler, img = self.images['MAINGRID_TEMPORAL'][0], batch = self.batch, group = self.group_0)

                        #Setup CamGroup
                        self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_CAMGROUP'] = atmEta_gui_AdvancedPygletGroups.cameraGroup(window = self.window, order = self.groupOrder+1, viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_y0 = 0, projection_y1 = drawBox[3]*self.scaler)

                        #Setup Grids
                        self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_LINES'] = list()
                        self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS'] = list()
                        for i in range (self.nMaxVerticalGridLines):
                            self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_LINES'].append(pyglet.shapes.Line(0, (_GD_DISPLAYBOX_GRID_VERTICALTEXTHEIGHT+_GD_DISPLAYBOX_GOFFSET)*self.scaler, 0, drawBox[3]*self.scaler, width = 3, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_CAMGROUP']))
                            self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS'].append(atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_CAMGROUP'], text = "-", defaultTextStyle = self.effectiveTextStyle['GRID'],
                                                                                                                                              xPos = 0, yPos = 0, width = _GD_DISPLAYBOX_GRID_VERTICALTEXTWIDTH, height = _GD_DISPLAYBOX_GRID_VERTICALTEXTHEIGHT, showElementBox = False, anchor = 'CENTER'))
                            self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_LINES'][-1].visible = False
                            self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS'][-1].hide()
                    #---SETTINGSBUTTONFRAME
                    elif (displayBoxName == 'SETTINGSBUTTONFRAME'):
                        self.hitBox['SETTINGSBUTTONFRAME'] = atmEta_gui_HitBoxes.hitBox_Rectangular(self.displayBox['SETTINGSBUTTONFRAME'][0], self.displayBox['SETTINGSBUTTONFRAME'][1], self.displayBox['SETTINGSBUTTONFRAME'][2], self.displayBox['SETTINGSBUTTONFRAME'][3])
                        self.images['SETTINGSBUTTONFRAME_DEFAULT'] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrameInteractable_DEFAULT", self.displayBox['SETTINGSBUTTONFRAME'][2]*self.scaler, self.displayBox['SETTINGSBUTTONFRAME'][3]*self.scaler)
                        self.images['SETTINGSBUTTONFRAME_HOVERED'] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrameInteractable_HOVERED", self.displayBox['SETTINGSBUTTONFRAME'][2]*self.scaler, self.displayBox['SETTINGSBUTTONFRAME'][3]*self.scaler)
                        self.images['SETTINGSBUTTONFRAME_PRESSED'] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrameInteractable_PRESSED", self.displayBox['SETTINGSBUTTONFRAME'][2]*self.scaler, self.displayBox['SETTINGSBUTTONFRAME'][3]*self.scaler)
                        self.images['SETTINGSBUTTONFRAME_ICON'] = self.imageManager.getImage('settingsIcon_512x512.png', (round(self.displayBox['SETTINGSBUTTONFRAME'][3]*0.65*self.scaler), round(self.displayBox['SETTINGSBUTTONFRAME'][3]*0.65*self.scaler)))

                        self.frameSprites['SETTINGSBUTTONFRAME'] = pyglet.sprite.Sprite(x = self.displayBox['SETTINGSBUTTONFRAME'][0]*self.scaler, y = self.displayBox['SETTINGSBUTTONFRAME'][1]*self.scaler, img = self.images['SETTINGSBUTTONFRAME_DEFAULT'][0], batch = self.batch, group = self.group_0)
                        self.frameSprites['SETTINGSBUTTONFRAME_ICON'] = pyglet.sprite.Sprite(x = (self.displayBox['SETTINGSBUTTONFRAME'][0]+self.displayBox['SETTINGSBUTTONFRAME'][2]/2)*self.scaler-self.images['SETTINGSBUTTONFRAME_ICON'].width/2, 
                                                                                                y = (self.displayBox['SETTINGSBUTTONFRAME'][1]+self.displayBox['SETTINGSBUTTONFRAME'][3]/2)*self.scaler-self.images['SETTINGSBUTTONFRAME_ICON'].height/2, 
                                                                                                img = self.images['SETTINGSBUTTONFRAME'+'_ICON'], batch = self.batch, group = self.group_1)
                        iconColoring = self.visualManager.getFromColorTable('ICON_COLORING')
                        self.frameSprites['SETTINGSBUTTONFRAME_ICON'].color = (iconColoring[0], iconColoring[1], iconColoring[2]); self.frameSprites['SETTINGSBUTTONFRAME'+'_ICON'].opacity = iconColoring[3]
                    #---KLINESPRICE
                    elif (displayBoxName == 'KLINESPRICE'):
                        displayBox          = self.displayBox['KLINESPRICE']
                        displayBox_MAINGRID = self.displayBox['MAINGRID_KLINESPRICE']
                        drawBox             = self.displayBox_graphics['KLINESPRICE']['DRAWBOX']
                        drawBox_MAINGRID    = self.displayBox_graphics['MAINGRID_KLINESPRICE']['DRAWBOX']

                        #Generate Graphic Sprites and Hitboxes
                        self.hitBox['KLINESPRICE'] = atmEta_gui_HitBoxes.hitBox_Rectangular(drawBox[0], drawBox[1], drawBox[2], drawBox[3])
                        self.images['KLINESPRICE'] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                        self.frameSprites['KLINESPRICE'] = pyglet.sprite.Sprite(x = displayBox[0]*self.scaler, y = displayBox[1]*self.scaler, img = self.images['KLINESPRICE'][0], batch = self.batch, group = self.group_0)
                        self.hitBox['MAINGRID_KLINESPRICE'] = atmEta_gui_HitBoxes.hitBox_Rectangular(drawBox_MAINGRID[0], drawBox_MAINGRID[1], drawBox_MAINGRID[2], drawBox_MAINGRID[3])
                        self.images['MAINGRID_KLINESPRICE'] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrame", displayBox_MAINGRID[2]*self.scaler, displayBox_MAINGRID[3]*self.scaler)
                        self.frameSprites['MAINGRID_KLINESPRICE'] = pyglet.sprite.Sprite(x = displayBox_MAINGRID[0]*self.scaler, y = displayBox_MAINGRID[1]*self.scaler, img = self.images['MAINGRID_KLINESPRICE'][0], batch = self.batch, group = self.group_0)

                        #Setup CamGroup and DisplaySpaceManager
                        self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_CAMGROUP']  = atmEta_gui_AdvancedPygletGroups.cameraGroup(window=self.window, order = self.groupOrder+1, viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_x0 = 0, projection_x1 = drawBox[2]*self.scaler)
                        self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_CAMGROUP']    = atmEta_gui_AdvancedPygletGroups.cameraGroup(window=self.window, order = self.groupOrder+1, viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_y0 = 0, projection_y1 = drawBox[3]*self.scaler)
                        self.displayBox_graphics['KLINESPRICE']['ANALYSISDISPLAY_CAMGROUP'] = atmEta_gui_AdvancedPygletGroups.cameraGroup(window=self.window, order = self.groupOrder+1, viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_y0 = 0, projection_y1 = drawBox[3]*self.scaler)
                        self.displayBox_graphics['KLINESPRICE']['RCLCG']        = atmEta_gui_AdvancedPygletGroups.resolutionControlledLayeredCameraGroup(window = self.window, batch = self.batch, viewport_x = drawBox[0]*self.scaler, viewport_y = drawBox[1]*self.scaler, viewport_width = drawBox[2]*self.scaler, viewport_height = drawBox[3]*self.scaler, order = self.groupOrder+2, parentCameraGroup = self.parentCameraGroup, fsdResolution_y = 2)
                        self.displayBox_graphics['KLINESPRICE']['RCLCG_XFIXED'] = atmEta_gui_AdvancedPygletGroups.resolutionControlledLayeredCameraGroup(window = self.window, batch = self.batch, viewport_x = drawBox[0]*self.scaler, viewport_y = drawBox[1]*self.scaler, viewport_width = drawBox[2]*self.scaler, viewport_height = drawBox[3]*self.scaler, order = self.groupOrder+2, parentCameraGroup = self.parentCameraGroup, projection_x0 = 0, projection_x1 = 100, fsdResolution_y = 5)
                        self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'] = atmEta_gui_AdvancedPygletGroups.resolutionControlledLayeredCameraGroup(window = self.window, batch = self.batch, viewport_x = drawBox[0]*self.scaler, viewport_y = drawBox[1]*self.scaler, viewport_width = drawBox[2]*self.scaler, viewport_height = drawBox[3]*self.scaler, order = self.groupOrder+2, parentCameraGroup = self.parentCameraGroup, projection_y0 = 0, projection_y1 = 100)
                        self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_CAMGROUP'] = atmEta_gui_AdvancedPygletGroups.cameraGroup(window = self.window, order = self.groupOrder+1, viewport_x=drawBox_MAINGRID[0]*self.scaler, viewport_y=drawBox_MAINGRID[1]*self.scaler, viewport_width=drawBox_MAINGRID[2]*self.scaler, viewport_height=drawBox_MAINGRID[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_x0 = 0, projection_x1 = drawBox_MAINGRID[2]*self.scaler)
                            
                        #Add RCLCGs to the reference list
                        self.__RCLCGReferences.append(self.displayBox_graphics['KLINESPRICE']['RCLCG'])
                        self.__RCLCGReferences.append(self.displayBox_graphics['KLINESPRICE']['RCLCG_XFIXED'])
                        self.__RCLCGReferences.append(self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'])

                        #Description Texts
                        self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT1'] = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_hd0, text = "", 
                                                                                                                             defaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle,
                                                                                                                             xPos = drawBox[0], yPos = drawBox[1]+drawBox[3]-200, width = drawBox[2], height = 200, showElementBox = False, anchor = 'W')
                        self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2'] = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_hd0, text = "", 
                                                                                                                             defaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle,
                                                                                                                             xPos = drawBox[0], yPos = drawBox[1]+drawBox[3]-400, width = drawBox[2], height = 200, showElementBox = False, anchor = 'W')
                        self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT3'] = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_hd0, text = "", 
                                                                                                                             defaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle,
                                                                                                                             xPos = drawBox[0], yPos = drawBox[1]+drawBox[3]-200, width = drawBox[2], height = 200, showElementBox = False, anchor = 'E')
                        #Setup Positional Highlight
                        self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_HOVERED']  = pyglet.shapes.Rectangle(x = 0, y = 0, width = 0, height = drawBox[3]*self.scaler, color = self.posHighlightColor_hovered,  batch = self.batch, group = self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_CAMGROUP'])
                        self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_SELECTED'] = pyglet.shapes.Rectangle(x = 0, y = 0, width = 0, height = drawBox[3]*self.scaler, color = self.posHighlightColor_selected, batch = self.batch, group = self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_CAMGROUP'])
                        self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_HOVERED'].visible  = False
                        self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_SELECTED'].visible = False
                        self.displayBox_graphics['KLINESPRICE']['HORIZONTALGUIDELINE'] = pyglet.shapes.Line(0, 0, drawBox[2]*self.scaler, 0, width = 3, color = self.guideColor, batch = self.batch, group = self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_CAMGROUP'])
                        self.displayBox_graphics['KLINESPRICE']['HORIZONTALGUIDETEXT'] = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_CAMGROUP'], text = "", defaultTextStyle = self.effectiveTextStyle['GUIDECONTENT'],
                                                                                                                                xPos = 0, yPos = 0, width = drawBox[2], height = _GD_DISPLAYBOX_GUIDE_HORIZONTALTEXTHEIGHT, showElementBox = False, anchor = 'E')
                        self.displayBox_graphics['KLINESPRICE']['HORIZONTALGUIDELINE'].visible = False
                        self.displayBox_graphics['KLINESPRICE']['HORIZONTALGUIDETEXT'].hide()

                        #Setup Grids
                        self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_LINES'] = list()
                        self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_LINES'] = list()
                        self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_LINES'] = list()
                        self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_TEXTS'] = list()
                        for i in range (self.nMaxHorizontalGridLines['KLINESPRICE']):
                            self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_LINES'].append(pyglet.shapes.Line(0, 0, drawBox[2]*self.scaler, 0, width = 1, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_CAMGROUP']))
                            self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_LINES'][-1].visible = False
                            self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_LINES'].append(pyglet.shapes.Line(0, 0, _GD_DISPLAYBOX_GOFFSET*self.scaler, 0, width = 3, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_CAMGROUP']))
                            self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_TEXTS'].append(atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_CAMGROUP'], text = "-", defaultTextStyle = self.effectiveTextStyle['GRID'],
                                                                                                                                                   xPos = _GD_DISPLAYBOX_GOFFSET*2, yPos = 0, width = _GD_DISPLAYBOX_GRID_HORIZONTALTEXTWIDTH, height = _GD_DISPLAYBOX_GRID_HORIZONTALTEXTHEIGHT, showElementBox = False, anchor = 'W'))
                            self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_LINES'][-1].visible = False
                            self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_TEXTS'][-1].hide()
                        for i in range (self.nMaxVerticalGridLines):
                            self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_LINES'].append(pyglet.shapes.Line(0, 0, 0, drawBox[3]*self.scaler, width = 1, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_CAMGROUP']))
                            self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_LINES'][-1].visible = False
                    #---SIVIEWER
                    elif (displayBoxName[:8] == 'SIVIEWER'):
                        siIndex = int(displayBoxName[8:])
                        dBoxName          = 'SIVIEWER{:d}'.format(siIndex)
                        dBoxName_MAINGRID = 'MAINGRID_SIVIEWER{:d}'.format(siIndex)
                        if (self.displayBox[displayBoxName] == None):
                            displayBox          = (0, 0, 10, 10)
                            displayBox_MAINGRID = (0, 0, 10, 10)
                            drawBox             = (0, 0, 10, 10)
                            drawBox_MAINGRID    = (0, 0, 10, 10)
                            displayed = False
                        else:
                            displayBox          = self.displayBox[dBoxName]
                            displayBox_MAINGRID = self.displayBox[dBoxName_MAINGRID]
                            drawBox             = self.displayBox_graphics[dBoxName]['DRAWBOX']
                            drawBox_MAINGRID    = self.displayBox_graphics[dBoxName_MAINGRID]['DRAWBOX']
                            displayed = True

                        #Generate Graphic Sprites and Hitboxes
                        self.hitBox[dBoxName] = atmEta_gui_HitBoxes.hitBox_Rectangular(drawBox[0], drawBox[1], drawBox[2], drawBox[3])
                        self.images[dBoxName] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                        self.frameSprites[dBoxName] = pyglet.sprite.Sprite(x = displayBox[0]*self.scaler, y = displayBox[1]*self.scaler, img = self.images[dBoxName][0], batch = self.batch, group = self.group_0)
                        self.hitBox[dBoxName_MAINGRID] = atmEta_gui_HitBoxes.hitBox_Rectangular(drawBox_MAINGRID[0], drawBox_MAINGRID[1], drawBox_MAINGRID[2], drawBox_MAINGRID[3])
                        self.images[dBoxName_MAINGRID] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrame", displayBox_MAINGRID[2]*self.scaler, displayBox_MAINGRID[3]*self.scaler)
                        self.frameSprites[dBoxName_MAINGRID] = pyglet.sprite.Sprite(x = displayBox_MAINGRID[0]*self.scaler, y = displayBox_MAINGRID[1]*self.scaler, img = self.images[dBoxName_MAINGRID][0], batch = self.batch, group = self.group_0)

                        #Setup CamGroup and DisplaySpaceManager
                        self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'] = atmEta_gui_AdvancedPygletGroups.cameraGroup(window = self.window, order = self.groupOrder+1, viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_x0 = 0, projection_x1 = drawBox[2]*self.scaler)
                        self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP']   = atmEta_gui_AdvancedPygletGroups.cameraGroup(window = self.window, order = self.groupOrder+1, viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_y0 = 0, projection_y1 = drawBox[3]*self.scaler)
                        self.displayBox_graphics[dBoxName]['RCLCG']                   = atmEta_gui_AdvancedPygletGroups.resolutionControlledLayeredCameraGroup(window = self.window, batch = self.batch, viewport_x = drawBox[0]*self.scaler, viewport_y = drawBox[1]*self.scaler, viewport_width = drawBox[2]*self.scaler, viewport_height = drawBox[3]*self.scaler, order = self.groupOrder+2, parentCameraGroup = self.parentCameraGroup, fsdResolution_y = 2)
                        self.displayBox_graphics[dBoxName]['RCLCG_XFIXED']            = atmEta_gui_AdvancedPygletGroups.resolutionControlledLayeredCameraGroup(window = self.window, batch = self.batch, viewport_x = drawBox[0]*self.scaler, viewport_y = drawBox[1]*self.scaler, viewport_width = drawBox[2]*self.scaler, viewport_height = drawBox[3]*self.scaler, order = self.groupOrder+2, parentCameraGroup = self.parentCameraGroup, projection_x0 = 0, projection_x1 = 100, fsdResolution_y = 5)
                        self.displayBox_graphics[dBoxName]['RCLCG_YFIXED']            = atmEta_gui_AdvancedPygletGroups.resolutionControlledLayeredCameraGroup(window = self.window, batch = self.batch, viewport_x = drawBox[0]*self.scaler, viewport_y = drawBox[1]*self.scaler, viewport_width = drawBox[2]*self.scaler, viewport_height = drawBox[3]*self.scaler, order = self.groupOrder+2, parentCameraGroup = self.parentCameraGroup, projection_y0 = 0, projection_y1 = 100)
                        self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_CAMGROUP'] = atmEta_gui_AdvancedPygletGroups.cameraGroup(window = self.window, order = self.groupOrder+1, viewport_x=drawBox_MAINGRID[0]*self.scaler, viewport_y=drawBox_MAINGRID[1]*self.scaler, viewport_width=drawBox_MAINGRID[2]*self.scaler, viewport_height=drawBox_MAINGRID[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_x0 = 0, projection_x1 = drawBox_MAINGRID[2]*self.scaler)
                            
                        #Add RCLCGs to the reference list
                        self.__RCLCGReferences.append(self.displayBox_graphics[dBoxName]['RCLCG'])
                        self.__RCLCGReferences.append(self.displayBox_graphics[dBoxName]['RCLCG_XFIXED'])
                        self.__RCLCGReferences.append(self.displayBox_graphics[dBoxName]['RCLCG_YFIXED'])

                        #Description Texts
                        self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT1'] = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_hd0, text = "", 
                                                                                                                        defaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle,
                                                                                                                        xPos = drawBox[0], yPos = drawBox[1]+drawBox[3]-200, width = drawBox[2], height = 200, showElementBox = False, anchor = 'W')

                        #Setup Positional Highlight
                        self.displayBox_graphics[dBoxName]['POSHIGHLIGHT_HOVERED']  = pyglet.shapes.Rectangle(x = 0, y = 0, width = 0, height = drawBox[3]*self.scaler, color = self.posHighlightColor_hovered,  batch = self.batch, group = self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'])
                        self.displayBox_graphics[dBoxName]['POSHIGHLIGHT_SELECTED'] = pyglet.shapes.Rectangle(x = 0, y = 0, width = 0, height = drawBox[3]*self.scaler, color = self.posHighlightColor_selected, batch = self.batch, group = self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'])
                        self.displayBox_graphics[dBoxName]['POSHIGHLIGHT_HOVERED'].visible  = False
                        self.displayBox_graphics[dBoxName]['POSHIGHLIGHT_SELECTED'].visible = False
                        self.displayBox_graphics[dBoxName]['HORIZONTALGUIDELINE'] = pyglet.shapes.Line(0, 0, drawBox[2]*self.scaler, 0, width = 3, color = self.guideColor, batch = self.batch, group = self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'])
                        self.displayBox_graphics[dBoxName]['HORIZONTALGUIDETEXT'] = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'], text = "", defaultTextStyle = self.effectiveTextStyle['GUIDECONTENT'],
                                                                                                                           xPos = 0, yPos = 0, width = drawBox[2], height = _GD_DISPLAYBOX_GUIDE_HORIZONTALTEXTHEIGHT, showElementBox = False, anchor = 'E')
                        self.displayBox_graphics[dBoxName]['HORIZONTALGUIDELINE'].visible = False
                        self.displayBox_graphics[dBoxName]['HORIZONTALGUIDETEXT'].hide()

                        #Setup Grids
                        self.displayBox_graphics[dBoxName]['HORIZONTALGRID_LINES'] = list()
                        self.displayBox_graphics[dBoxName]['VERTICALGRID_LINES'] = list()
                        self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_LINES'] = list()
                        self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_TEXTS'] = list()
                        for i in range (self.nMaxHorizontalGridLines[dBoxName]):
                            self.displayBox_graphics[dBoxName]['HORIZONTALGRID_LINES'].append(pyglet.shapes.Line(0, 0, drawBox[2]*self.scaler, 0, width = 1, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP']))
                            self.displayBox_graphics[dBoxName]['HORIZONTALGRID_LINES'][-1].visible = False
                            self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_LINES'].append(pyglet.shapes.Line(0, 0, _GD_DISPLAYBOX_GOFFSET*self.scaler, 0, width = 3, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_CAMGROUP']))
                            self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_TEXTS'].append(atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_CAMGROUP'], text = "-", defaultTextStyle = self.effectiveTextStyle['GRID'],
                                                                                                                                              xPos = _GD_DISPLAYBOX_GOFFSET*2, yPos = 0, width = _GD_DISPLAYBOX_GRID_HORIZONTALTEXTWIDTH, height = _GD_DISPLAYBOX_GRID_HORIZONTALTEXTHEIGHT, showElementBox = False, anchor = 'W'))
                            self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_LINES'][-1].visible = False
                            self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_TEXTS'][-1].hide()
                        for i in range (self.nMaxVerticalGridLines):
                            self.displayBox_graphics[dBoxName]['VERTICALGRID_LINES'].append(pyglet.shapes.Line(0, 0, 0, drawBox[3]*self.scaler, width = 1, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP']))
                            self.displayBox_graphics[dBoxName]['VERTICALGRID_LINES'][-1].visible = False

                        #If this SIViewer is activated, add it to the visibleSIViewers set. If not, hide it
                        if (displayed == True): self.displayBox_graphics_visibleSIViewers.add(dBoxName)
                        else:                   self.__hideDisplayBox(dBoxName)
                    #---AUXILLARYBAR
                    elif (displayBoxName == 'AUXILLARYBAR'):
                        displayBox = self.displayBox['AUXILLARYBAR']
                        drawBox    = self.displayBox_graphics['AUXILLARYBAR']['DRAWBOX']
                        #Generate Graphic Sprites and Hitboxes
                        self.images['AUXILLARYBAR'] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                        self.frameSprites['AUXILLARYBAR'] = pyglet.sprite.Sprite(x = displayBox[0]*self.scaler, y = displayBox[1]*self.scaler, img = self.images['AUXILLARYBAR'][0], batch = self.batch, group = self.group_0)
            else:
                for displayBoxName in self.displayBox:
                    if (displayBoxName in self.displayBox_VisibleBoxes):
                        self.mouse_DragDX[displayBoxName] = 0; self.mouse_DragDY[displayBoxName] = 0; self.mouse_ScrollDX[displayBoxName] = 0; self.mouse_ScrollDY[displayBoxName] = 0
                        #SETTINGSBUTTONFRAME
                        if (displayBoxName == 'SETTINGSBUTTONFRAME'):
                            displayBox = self.displayBox['SETTINGSBUTTONFRAME']
                            self.hitBox['SETTINGSBUTTONFRAME'].reposition(xPos = displayBox[0], yPos = displayBox[1])
                            self.frameSprites['SETTINGSBUTTONFRAME'].position = (displayBox[0]*self.scaler, displayBox[1]*self.scaler, self.frameSprites['SETTINGSBUTTONFRAME'].z)
                            self.frameSprites['SETTINGSBUTTONFRAME_ICON'].position = ((displayBox[0]+displayBox[2]/2)*self.scaler-self.images['SETTINGSBUTTONFRAME_ICON'].width/2,
                                                                                      (displayBox[1]+displayBox[3]/2)*self.scaler-self.images['SETTINGSBUTTONFRAME_ICON'].height/2,
                                                                                      self.frameSprites['SETTINGSBUTTONFRAME'].z)
                        #KLINESPRICE
                        elif (displayBoxName == 'KLINESPRICE'):
                            displayBox          = self.displayBox['KLINESPRICE']
                            displayBox_MAINGRID = self.displayBox['MAINGRID_KLINESPRICE']
                            drawBox             = self.displayBox_graphics['KLINESPRICE']['DRAWBOX']
                            drawBox_MAINGRID    = self.displayBox_graphics['MAINGRID_KLINESPRICE']['DRAWBOX']

                            #Reposition & Resize Graphics and Hitboxes
                            self.hitBox['KLINESPRICE'].reposition(xPos = drawBox[0], yPos = drawBox[1])
                            self.hitBox['KLINESPRICE'].resize(width = drawBox[2], height = drawBox[3])
                            self.images['KLINESPRICE'] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                            self.frameSprites['KLINESPRICE'].position = (displayBox[0]*self.scaler, displayBox[1]*self.scaler, self.frameSprites['KLINESPRICE'].z)
                            self.frameSprites['KLINESPRICE'].image = self.images['KLINESPRICE'][0]
                            self.hitBox['MAINGRID_KLINESPRICE'].reposition(xPos = drawBox_MAINGRID[0], yPos = drawBox_MAINGRID[1])
                            self.hitBox['MAINGRID_KLINESPRICE'].resize(width = drawBox_MAINGRID[2], height = drawBox_MAINGRID[3])
                            self.images['MAINGRID_KLINESPRICE'] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrame", displayBox_MAINGRID[2]*self.scaler, displayBox_MAINGRID[3]*self.scaler)
                            self.frameSprites['MAINGRID_KLINESPRICE'].position = (displayBox_MAINGRID[0]*self.scaler, displayBox_MAINGRID[1]*self.scaler, self.frameSprites['MAINGRID_KLINESPRICE'].z)
                            self.frameSprites['MAINGRID_KLINESPRICE'].image = self.images['MAINGRID_KLINESPRICE'][0]

                            #Reposition & Resize CamGroups and RCLCGs
                            self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_CAMGROUP'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_CAMGROUP'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics['KLINESPRICE']['ANALYSISDISPLAY_CAMGROUP'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_CAMGROUP'].updateProjection(projection_x0 = 0, projection_x1 = drawBox[2]*self.scaler)
                            self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_CAMGROUP'].updateProjection(projection_y0 = 0, projection_y1 = drawBox[3]*self.scaler)
                            self.displayBox_graphics['KLINESPRICE']['ANALYSISDISPLAY_CAMGROUP'].updateProjection(projection_x0 = 1, projection_x1 = drawBox[2]*self.scaler, projection_y0 = 0, projection_y1 = drawBox[3]*self.scaler)
                            self.displayBox_graphics['KLINESPRICE']['RCLCG'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics['KLINESPRICE']['RCLCG_XFIXED'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_CAMGROUP'].updateViewport(viewport_x=drawBox_MAINGRID[0]*self.scaler, viewport_y=drawBox_MAINGRID[1]*self.scaler, viewport_width=drawBox_MAINGRID[2]*self.scaler, viewport_height=drawBox_MAINGRID[3]*self.scaler)
                            self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_CAMGROUP'].updateProjection(projection_x0 = 0, projection_x1 = drawBox_MAINGRID[2]*self.scaler)

                            #Reposition & Resize Auxillary Objects
                            self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT1'].moveTo(x = drawBox[0], y = drawBox[1]+drawBox[3]-200)
                            self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT1'].changeSize(width = drawBox[2])
                            self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2'].moveTo(x = drawBox[0], y = drawBox[1]+drawBox[3]-400)
                            self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2'].changeSize(width = drawBox[2])
                            self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_HOVERED'].height  = drawBox[3]*self.scaler
                            self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_SELECTED'].height = drawBox[3]*self.scaler
                            self.displayBox_graphics['KLINESPRICE']['HORIZONTALGUIDELINE'].x2 = drawBox[2]*self.scaler
                            self.displayBox_graphics['KLINESPRICE']['HORIZONTALGUIDETEXT'].changeSize(width = drawBox[2])

                            #Setup Grids
                            for horizontalGridText in self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_TEXTS']: horizontalGridText.delete()
                            self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_LINES'] = list()
                            self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_LINES'] = list()
                            self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_LINES'] = list()
                            self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_TEXTS'] = list()
                            for i in range (self.nMaxHorizontalGridLines['KLINESPRICE']):
                                self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_LINES'].append(pyglet.shapes.Line(0, 0, drawBox[2]*self.scaler, 0, width = 1, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_CAMGROUP']))
                                self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_LINES'][-1].visible = False
                                self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_LINES'].append(pyglet.shapes.Line(0, 0, _GD_DISPLAYBOX_GOFFSET*self.scaler, 0, width = 3, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_CAMGROUP']))
                                self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_TEXTS'].append(atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_CAMGROUP'], text = "-", defaultTextStyle = self.effectiveTextStyle['GRID'],
                                                                                                                                                       xPos = _GD_DISPLAYBOX_GOFFSET*2, yPos = 0, width = _GD_DISPLAYBOX_GRID_HORIZONTALTEXTWIDTH, height = _GD_DISPLAYBOX_GRID_HORIZONTALTEXTHEIGHT, showElementBox = False, anchor = 'W'))
                                self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_LINES'][-1].visible = False
                                self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_TEXTS'][-1].hide()
                                
                            for i in range (self.nMaxVerticalGridLines):
                                self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_LINES'].append(pyglet.shapes.Line(0, 0, 0, drawBox[3]*self.scaler, width = 1, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_CAMGROUP']))
                                self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_LINES'][-1].visible = False
                        #MAINGRID_TEMPORAL
                        elif (displayBoxName == 'MAINGRID_TEMPORAL'):
                            displayBox = self.displayBox['MAINGRID_TEMPORAL']
                            drawBox    = self.displayBox_graphics['MAINGRID_TEMPORAL']['DRAWBOX']

                            #Reposition & Resize Graphics and Hitboxes
                            self.hitBox['MAINGRID_TEMPORAL'].reposition(xPos = drawBox[0], yPos = drawBox[1])
                            self.hitBox['MAINGRID_TEMPORAL'].resize(width = drawBox[2], height = drawBox[3])
                            self.images['MAINGRID_TEMPORAL'] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                            self.frameSprites['MAINGRID_TEMPORAL'].position = (displayBox[0]*self.scaler, displayBox[1]*self.scaler, self.frameSprites['MAINGRID_TEMPORAL'].z)
                            self.frameSprites['MAINGRID_TEMPORAL'].image = self.images['MAINGRID_TEMPORAL'][0]

                            #Reposition & Resize CamGroups and RCLCGs
                            self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_CAMGROUP'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)

                            #Setup Grids
                            for verticalGridText in self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS']: verticalGridText.delete()
                            self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_LINES'] = list()
                            self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS'] = list()
                            for i in range (self.nMaxVerticalGridLines):
                                self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_LINES'].append(pyglet.shapes.Line(0, (_GD_DISPLAYBOX_GRID_VERTICALTEXTHEIGHT+_GD_DISPLAYBOX_GOFFSET)*self.scaler, 0, drawBox[3]*self.scaler, width = 3, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_CAMGROUP']))
                                self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS'].append(atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_CAMGROUP'], text = "-", defaultTextStyle = self.effectiveTextStyle['GRID'],
                                                                                                                                                  xPos = 0, yPos = 0, width = _GD_DISPLAYBOX_GRID_VERTICALTEXTWIDTH, height = _GD_DISPLAYBOX_GRID_VERTICALTEXTHEIGHT, showElementBox = False, anchor = 'CENTER'))
                                self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_LINES'][-1].visible = False
                                self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS'][-1].hide()
                        #SIVIEWER
                        elif (displayBoxName[:8] == 'SIVIEWER'):
                            siIndex = int(displayBoxName[8:])
                            dBoxName          = 'SIVIEWER{:d}'.format(siIndex)
                            dBoxName_MAINGRID = 'MAINGRID_SIVIEWER{:d}'.format(siIndex)
                            displayBox          = self.displayBox[dBoxName]
                            displayBox_MAINGRID = self.displayBox[dBoxName_MAINGRID]
                            drawBox          = self.displayBox_graphics[dBoxName]['DRAWBOX']
                            drawBox_MAINGRID = self.displayBox_graphics[dBoxName_MAINGRID]['DRAWBOX']
                                
                            #Reposition & Resize Graphics and Hitboxes
                            self.hitBox[dBoxName].reposition(xPos = drawBox[0], yPos = drawBox[1])
                            self.hitBox[dBoxName].resize(width = drawBox[2], height = drawBox[3])
                            self.hitBox[dBoxName].activate()
                            self.images[dBoxName] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                            self.frameSprites[dBoxName].position = (displayBox[0]*self.scaler, displayBox[1]*self.scaler, self.frameSprites[dBoxName].z)
                            self.frameSprites[dBoxName].image = self.images[dBoxName][0]
                            self.frameSprites[dBoxName].visible = True
                            self.hitBox[dBoxName_MAINGRID].reposition(xPos = drawBox_MAINGRID[0], yPos = drawBox_MAINGRID[1])
                            self.hitBox[dBoxName_MAINGRID].resize(width = drawBox_MAINGRID[2], height = drawBox_MAINGRID[3])
                            self.hitBox[dBoxName_MAINGRID].activate()
                            self.images[dBoxName_MAINGRID] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrame", displayBox_MAINGRID[2]*self.scaler, displayBox_MAINGRID[3]*self.scaler)
                            self.frameSprites[dBoxName_MAINGRID].position = (displayBox_MAINGRID[0]*self.scaler, displayBox_MAINGRID[1]*self.scaler, self.frameSprites[dBoxName_MAINGRID].z)
                            self.frameSprites[dBoxName_MAINGRID].image = self.images[dBoxName_MAINGRID][0]
                            self.frameSprites[dBoxName_MAINGRID].visible = True
                                
                            #Reposition & Resize CamGroups and RCLCGs
                            self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].updateProjection(projection_x0 = 0, projection_x1 = drawBox[2]*self.scaler)
                            self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'].updateProjection(projection_y0 = 0, projection_y1 = drawBox[3]*self.scaler)
                            self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].show()
                            self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'].show()
                            self.displayBox_graphics[dBoxName]['RCLCG'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics[dBoxName]['RCLCG_XFIXED'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics[dBoxName]['RCLCG_YFIXED'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics[dBoxName]['RCLCG'].show()
                            self.displayBox_graphics[dBoxName]['RCLCG_XFIXED'].show()
                            self.displayBox_graphics[dBoxName]['RCLCG_YFIXED'].show()
                            self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_CAMGROUP'].updateViewport(viewport_x=drawBox_MAINGRID[0]*self.scaler, viewport_y=drawBox_MAINGRID[1]*self.scaler, viewport_width=drawBox_MAINGRID[2]*self.scaler, viewport_height=drawBox_MAINGRID[3]*self.scaler)
                            self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_CAMGROUP'].updateProjection(projection_x0 = 0, projection_x1 = drawBox_MAINGRID[2]*self.scaler)
                            self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_CAMGROUP'].show()
                                
                            #Reposition & Resize Auxillary Objects
                            self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT1'].moveTo(x = drawBox[0], y = drawBox[1]+drawBox[3]-200)
                            self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT1'].changeSize(width = drawBox[2], height = 200)
                            self.displayBox_graphics[dBoxName]['POSHIGHLIGHT_HOVERED'].height  = drawBox[3]*self.scaler
                            self.displayBox_graphics[dBoxName]['POSHIGHLIGHT_SELECTED'].height = drawBox[3]*self.scaler
                            self.displayBox_graphics[dBoxName]['HORIZONTALGUIDELINE'].x2 = drawBox[2]*self.scaler
                            self.displayBox_graphics[dBoxName]['HORIZONTALGUIDETEXT'].changeSize(width = drawBox[2])

                            #Setup Grids
                            for horizontalGridText in self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_TEXTS']: horizontalGridText.delete()
                            self.displayBox_graphics[dBoxName]['HORIZONTALGRID_LINES'] = list()
                            self.displayBox_graphics[dBoxName]['VERTICALGRID_LINES']   = list()
                            self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_LINES'] = list()
                            self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_TEXTS'] = list()
                            for i in range (self.nMaxHorizontalGridLines[dBoxName]):
                                self.displayBox_graphics[dBoxName]['HORIZONTALGRID_LINES'].append(pyglet.shapes.Line(0, 0, drawBox[2]*self.scaler, 0, width = 1, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP']))
                                self.displayBox_graphics[dBoxName]['HORIZONTALGRID_LINES'][-1].visible = False
                                self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_LINES'].append(pyglet.shapes.Line(0, 0, _GD_DISPLAYBOX_GOFFSET*self.scaler, 0, width = 3, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_CAMGROUP']))
                                self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_TEXTS'].append(atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_CAMGROUP'], text = "-", defaultTextStyle = self.effectiveTextStyle['GRID'],
                                                                                                                                                  xPos = _GD_DISPLAYBOX_GOFFSET*2, yPos = 0, width = _GD_DISPLAYBOX_GRID_HORIZONTALTEXTWIDTH, height = _GD_DISPLAYBOX_GRID_HORIZONTALTEXTHEIGHT, showElementBox = False, anchor = 'W'))
                                self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_LINES'][-1].visible = False
                                self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_TEXTS'][-1].hide()
                            for i in range (self.nMaxVerticalGridLines):
                                self.displayBox_graphics[dBoxName]['VERTICALGRID_LINES'].append(pyglet.shapes.Line(0, 0, 0, drawBox[3]*self.scaler, width = 1, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP']))
                                self.displayBox_graphics[dBoxName]['VERTICALGRID_LINES'][-1].visible = False

                            #Add to the visibleSIViewers set (If already exists, simply won't do anything)
                            self.displayBox_graphics_visibleSIViewers.add(displayBoxName)
                        #AUXILLARYBAR
                        elif (displayBoxName == 'AUXILLARYBAR'):
                            displayBox = self.displayBox['AUXILLARYBAR']
                            #Reposition & Resize Graphics
                            self.images['AUXILLARYBAR'] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrame", self.displayBox['AUXILLARYBAR'][2]*self.scaler, self.displayBox['AUXILLARYBAR'][3]*self.scaler)
                            self.frameSprites['AUXILLARYBAR'].position = (self.displayBox['AUXILLARYBAR'][0]*self.scaler, self.displayBox['AUXILLARYBAR'][1]*self.scaler, self.frameSprites['AUXILLARYBAR'].z)
                            self.frameSprites['AUXILLARYBAR'].image = self.images['AUXILLARYBAR'][0]
                            self.frameSprites['AUXILLARYBAR'].visible = True
                    else: self.__hideDisplayBox(displayBoxName)

        #[4]: Size and Position Klines Loading Gauge Bar and Text
        if (True):
            self.klinesLoadingGaugeBar.resize(width      = round(self.width*0.9), height = _GD_KLINESLOADINGGAUGEBAR_HEIGHT)
            self.klinesLoadingTextBox_perc.resize(width  = round(self.width*0.9), height = _GD_KLINESLOADINGGAUGEBAR_HEIGHT)
            self.klinesLoadingTextBox.resize(width       = round(self.width*0.9), height = 200)
            self.klinesLoadingGaugeBar.moveTo(x     = round(self.xPos+self.width*0.05), y = round(self.yPos+self.height/2-_GD_KLINESLOADINGGAUGEBAR_HEIGHT))
            self.klinesLoadingTextBox_perc.moveTo(x = round(self.xPos+self.width*0.05), y = round(self.yPos+self.height/2-_GD_KLINESLOADINGGAUGEBAR_HEIGHT))
            self.klinesLoadingTextBox.moveTo(x      = round(self.xPos+self.width*0.05), y = round(self.yPos+self.height/2))

    def __hideDisplayBox(self, displayBoxName):
        #Deactivate and hide SIVIEWER[X]
        if ((displayBoxName[:8] == 'SIVIEWER') and (displayBoxName in self.displayBox_graphics_visibleSIViewers)):
            siIndex = int(displayBoxName[8:])
            dBoxName          = 'SIVIEWER{:d}'.format(siIndex)
            dBoxName_MAINGRID = 'MAINGRID_SIVIEWER{:d}'.format(siIndex)
            #Hitbox & Frame Graphics
            self.hitBox[displayBoxName].deactivate()
            self.frameSprites[displayBoxName].visible = False
            #CamGroups and RCLCGs
            self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].hide()
            self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'].hide()
            self.displayBox_graphics[dBoxName]['RCLCG'].hide()
            self.displayBox_graphics[dBoxName]['RCLCG_XFIXED'].hide()
            self.displayBox_graphics[dBoxName]['RCLCG_YFIXED'].hide()
            self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_CAMGROUP'].hide()
            #Descriptors & Guides
            self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT1'].hide()
            self.displayBox_graphics[dBoxName]['POSHIGHLIGHT_HOVERED'].visible = False
            self.displayBox_graphics[dBoxName]['POSHIGHLIGHT_SELECTED'].visible = False
            self.displayBox_graphics[dBoxName]['HORIZONTALGUIDELINE'].visible = False
            self.displayBox_graphics[dBoxName]['HORIZONTALGUIDETEXT'].hide()
            #Grids
            for horizontalGridText in self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_TEXTS']: horizontalGridText.hide()
            self.displayBox_graphics_visibleSIViewers.remove(displayBoxName)
            
    def __setSIViewerDisplay(self, siViewerNumber, siViewerDisplay):
        #[1]: Update Object Config
        self.objectConfig['SIVIEWER{:d}Display'.format(siViewerNumber)] = siViewerDisplay

        #[2]: Reconfigure Display Boxes and Initialize SIViewer
        self.__configureDisplayBoxes()
        self.__initializeSIViewer(siViewerCode = "SIVIEWER{:d}".format(siViewerNumber))
        
        #[3]: Set ViewRanges
        self.__onHViewRangeUpdate(updateType = 1)
        self.__onVViewRangeUpdate(displayBoxName = 'KLINESPRICE', updateType = 1)
        for visibleSIViewerCode in self.displayBox_graphics_visibleSIViewers: self.__onVViewRangeUpdate(displayBoxName = visibleSIViewerCode, updateType = 1)
        
        #[4]: If siViewerDisplay == True, update Draw Queues
        siAlloc = self.objectConfig['SIVIEWER{:d}SIAlloc'.format(siViewerNumber)]
        if ((siViewerDisplay == True) and (self.siTypes_analysisCodes[siAlloc] != None)):
            self.checkVerticalExtremas_SIs[siAlloc]()
            if (siAlloc in {'VOL', 'MMACDLONG', 'MMACDSHORT', 'DMIxADX', 'MFI'}):
                for analysisCode in self.siTypes_analysisCodes[siAlloc]: self.__addBufferZone_toDrawQueue(analysisCode, drawSignal = _FULLDRAWSIGNALS[siAlloc])
            elif (siAlloc == 'WOI'): self.__addALLWOI_toDrawQueue()
            elif (siAlloc == 'NES'): self.__addALLNES_toDrawQueue()

    def __setSIViewerDisplayTarget(self, siViewerNumber1, siViewerDisplayTarget1):
        #[1]: Identify DisplayTarget Swap Target
        siViewerNumber2        = self.siTypes_siViewerAlloc[siViewerDisplayTarget1]
        siViewerDisplayTarget2 = self.objectConfig['SIVIEWER{:d}SIAlloc'.format(siViewerNumber1)]

        #[2]: Update Object Config and SIViewer Control Variables
        self.objectConfig['SIVIEWER{:d}SIAlloc'.format(siViewerNumber1)] = siViewerDisplayTarget1
        self.objectConfig['SIVIEWER{:d}SIAlloc'.format(siViewerNumber2)] = siViewerDisplayTarget2
        self.siTypes_siViewerAlloc[siViewerDisplayTarget1] = siViewerNumber1
        self.siTypes_siViewerAlloc[siViewerDisplayTarget2] = siViewerNumber2
        
        siViewerDisplay1 = self.objectConfig['SIVIEWER{:d}Display'.format(siViewerNumber1)]
        siViewerDisplay2 = self.objectConfig['SIVIEWER{:d}Display'.format(siViewerNumber2)]
        siViewerCode1 = "SIVIEWER{:d}".format(siViewerNumber1)
        siViewerCode2 = "SIVIEWER{:d}".format(siViewerNumber2)

        #[3]: Reconfigure Display Boxes and Initialize SIViewer
        if (siViewerDisplay1 == True): self.__initializeSIViewer(siViewerCode = siViewerCode1)
        if (siViewerDisplay2 == True): self.__initializeSIViewer(siViewerCode = siViewerCode2)

        #[4]: Set ViewRanges
        if (siViewerDisplay1 == True):
            if (self.checkVerticalExtremas_SIs[siViewerDisplayTarget1]() == True):
                if   (siViewerDisplayTarget1 == 'VOL'):        self.__editVVR_toExtremaCenter(displayBoxName = "SIVIEWER{:d}".format(siViewerNumber1), extension_b = 0.0, extension_t = 0.2)
                elif (siViewerDisplayTarget1 == 'MMACDLONG'):  self.__editVVR_toExtremaCenter(displayBoxName = "SIVIEWER{:d}".format(siViewerNumber1), extension_b = 0.1, extension_t = 0.1)
                elif (siViewerDisplayTarget1 == 'MMACDSHORT'): self.__editVVR_toExtremaCenter(displayBoxName = "SIVIEWER{:d}".format(siViewerNumber1), extension_b = 0.1, extension_t = 0.1)
                elif (siViewerDisplayTarget1 == 'DMIxADX'):    self.__editVVR_toExtremaCenter(displayBoxName = "SIVIEWER{:d}".format(siViewerNumber1), extension_b = 0.1, extension_t = 0.1)
                elif (siViewerDisplayTarget1 == 'MFI'):        self.__editVVR_toExtremaCenter(displayBoxName = "SIVIEWER{:d}".format(siViewerNumber1), extension_b = 0.1, extension_t = 0.1)
                elif (siViewerDisplayTarget1 == 'WOI'):        self.__editVVR_toExtremaCenter(displayBoxName = "SIVIEWER{:d}".format(siViewerNumber1), extension_b = 0.1, extension_t = 0.1)
                elif (siViewerDisplayTarget1 == 'NES'):        self.__editVVR_toExtremaCenter(displayBoxName = "SIVIEWER{:d}".format(siViewerNumber1), extension_b = 0.1, extension_t = 0.1)
        if (siViewerDisplay2 == True): 
            if (self.checkVerticalExtremas_SIs[siViewerDisplayTarget2]() == True):
                if   (siViewerDisplayTarget2 == 'VOL'):        self.__editVVR_toExtremaCenter(displayBoxName = "SIVIEWER{:d}".format(siViewerNumber2), extension_b = 0.0, extension_t = 0.2)
                elif (siViewerDisplayTarget2 == 'MMACDLONG'):  self.__editVVR_toExtremaCenter(displayBoxName = "SIVIEWER{:d}".format(siViewerNumber2), extension_b = 0.1, extension_t = 0.1)
                elif (siViewerDisplayTarget2 == 'MMACDSHORT'): self.__editVVR_toExtremaCenter(displayBoxName = "SIVIEWER{:d}".format(siViewerNumber2), extension_b = 0.1, extension_t = 0.1)
                elif (siViewerDisplayTarget2 == 'DMIxADX'):    self.__editVVR_toExtremaCenter(displayBoxName = "SIVIEWER{:d}".format(siViewerNumber2), extension_b = 0.1, extension_t = 0.1)
                elif (siViewerDisplayTarget2 == 'MFI'):        self.__editVVR_toExtremaCenter(displayBoxName = "SIVIEWER{:d}".format(siViewerNumber2), extension_b = 0.1, extension_t = 0.1)
                elif (siViewerDisplayTarget2 == 'WOI'):        self.__editVVR_toExtremaCenter(displayBoxName = "SIVIEWER{:d}".format(siViewerNumber2), extension_b = 0.1, extension_t = 0.1)
                elif (siViewerDisplayTarget2 == 'NES'):        self.__editVVR_toExtremaCenter(displayBoxName = "SIVIEWER{:d}".format(siViewerNumber2), extension_b = 0.1, extension_t = 0.1)

        #[5]: If siViewerDisplay == True, update Draw Queues
        if ((siViewerDisplay1 == True) and (self.siTypes_analysisCodes[siViewerDisplayTarget1] != None)):
            if (siViewerDisplayTarget1 in {'VOL', 'MMACDLONG', 'MMACDSHORT', 'DMIxADX', 'MFI'}):
                for analysisCode in self.siTypes_analysisCodes[siViewerDisplayTarget1]: self.__addBufferZone_toDrawQueue(analysisCode, drawSignal = _FULLDRAWSIGNALS[siViewerDisplayTarget1])
            elif (siViewerDisplayTarget1 == 'WOI'): self.__addALLWOI_toDrawQueue()
            elif (siViewerDisplayTarget1 == 'NES'): self.__addALLNES_toDrawQueue()

        if ((siViewerDisplay2 == True) and (self.siTypes_analysisCodes[siViewerDisplayTarget2] != None)):
            if (siViewerDisplayTarget2 in {'VOL', 'MMACDLONG', 'MMACDSHORT', 'DMIxADX', 'MFI'}):
                for analysisCode in self.siTypes_analysisCodes[siViewerDisplayTarget2]: self.__addBufferZone_toDrawQueue(analysisCode, drawSignal = _FULLDRAWSIGNALS[siViewerDisplayTarget2])
            elif (siViewerDisplayTarget2 == 'WOI'): self.__addALLWOI_toDrawQueue()
            elif (siViewerDisplayTarget2 == 'NES'): self.__addALLNES_toDrawQueue()

        #[6]: Return SIViewerNumber2 for reference
        return siViewerNumber2

    def __initializeRCLCGs(self, displayBoxName, verticalPrecision = None):
        if (verticalPrecision == None): self.verticalViewRange_precision[displayBoxName] = self.__getRCLCGVerticalPrecision(displayBoxName = displayBoxName)
        else:                           self.verticalViewRange_precision[displayBoxName] = verticalPrecision
        precision_x = math.floor(math.log(self.expectedKlineTemporalWidth, 10))
        precision_y = -self.verticalViewRange_precision[displayBoxName]
        self.displayBox_graphics[displayBoxName]['RCLCG'].setPrecision(precision_x = precision_x, precision_y = precision_y, transferObjects = False)
        self.displayBox_graphics[displayBoxName]['RCLCG_XFIXED'].setPrecision(precision_y = precision_y, precision_x = 0, transferObjects = False)
        self.displayBox_graphics[displayBoxName]['RCLCG_YFIXED'].setPrecision(precision_x = precision_x, precision_y = 0, transferObjects = False)
        
    def __initializeSIViewer(self, siViewerCode, verticalPrecision = None):
        self.__initializeRCLCGs(siViewerCode, verticalPrecision)
        self.verticalValue_min[siViewerCode] = -100
        self.verticalValue_max[siViewerCode] =  100
        self.verticalValue_loaded[siViewerCode] = False
        self.__onVerticalExtremaUpdate(displayBoxName = siViewerCode, updateType = 1)
        
    def __getRCLCGVerticalPrecision(self, displayBoxName):
        if (self.currencyInfo == None): return 2
        else:
            if (displayBoxName == 'KLINESPRICE'): return self.currencyInfo['precisions']['price']
            elif (displayBoxName[:8] == 'SIVIEWER'):
                siType = self.objectConfig['{:s}SIAlloc'.format(displayBoxName)]
                if (siType == 'VOL'):
                    if ('VOL' in self.analysisParams):
                        volType = self.analysisParams['VOL']['volType']
                        if   (volType == 'BASE'):    return self.currencyInfo['precisions']['quantity']
                        elif (volType == 'QUOTE'):   return self.currencyInfo['precisions']['quote']
                        elif (volType == 'BASETB'):  return self.currencyInfo['precisions']['quantity']
                        elif (volType == 'QUOTETB'): return self.currencyInfo['precisions']['quote']
                    else: return 0
                elif (siType == 'MMACDLONG'):  return self.currencyInfo['precisions']['price']+2
                elif (siType == 'MMACDSHORT'): return self.currencyInfo['precisions']['price']+2
                elif (siType == 'DMIxADX'):    return 2
                elif (siType == 'MFI'):        return 2
                elif (siType == 'WOI'):        return 2
                elif (siType == 'NES'):        return 2
            return None
    #DisplayBox Control END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Processings -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def process(self, t_elapsed_ns):
        mei_beg = time.perf_counter_ns()
        self.__process_SubPages(t_elapsed_ns)                                                                               #[1]: Subpage Processing
        self.__process_MouseEventInterpretation()                                                                           #[2]: Mouse Event Interpretation
        self.__process_PosHighlightUpdate(mei_beg)                                                                          #[3]: PosHighlight Update
        if (self.klines_fetchComplete == True):
            waitPostDrag   = (mei_beg-self.mouse_lastDragged_ns  <= _TIMEINTERVAL_POSTDRAGWAITTIME)
            waitPostScroll = (mei_beg-self.mouse_lastScrolled_ns <= _TIMEINTERVAL_POSTSCROLLWAITTIME)
            if ((waitPostDrag == False) and (waitPostScroll == False)): processNext = not(self.__process_analysis(mei_beg)) #[4]: Process Analysis
            else:                                                       processNext = True
            if (processNext == True): processNext = not(self.__process_drawQueues(mei_beg))                                 #[5]: Draw Queues Processing
            if (processNext == True): processNext = not(self.__process_RCLCGs(mei_beg))                                     #[6]: RCLCGs Processing
            if (processNext == True): self.__process_drawRemovalQueues(mei_beg)                                             #[7]: Draw Removal Queues Processing
        return

    def __process_SubPages(self, t_elapsed_ns):
        self.settingsSubPages[self.settingsSubPage_Current].process(t_elapsed_ns)
        
    def __process_MouseEventInterpretation(self):
        if (_TIMEINTERVAL_MOUSEINTERPRETATION_NS <= time.perf_counter_ns() - self.mouse_Event_lastInterpreted_ns):
            #[1-1]: Mouse Drag Handling
            if (self.mouse_Dragged == True):
                for section in self.mouse_DragDX: #Iterating over 'self.mouseDragDX' or 'self.mouseDragDY' does not matter
                    #Drag Delta
                    drag_dx = self.mouse_DragDX[section]; drag_dy = self.mouse_DragDY[section]
                    #Drag Responses
                    if ((drag_dx != 0) or (drag_dy != 0)):
                        if   (section == 'KLINESPRICE'):            self.__editVPosition(displayBoxName = 'KLINESPRICE', delta_drag = drag_dy); self.__editHPosition(delta_drag = drag_dx)
                        elif (section == 'MAINGRID_KLINESPRICE'):   self.__editVMagFactor(displayBoxName = 'KLINESPRICE', delta_drag = drag_dy)
                        elif (section == 'MAINGRID_TEMPORAL'):      self.__editHMagFactor(delta_drag = drag_dx)
                        elif (section[:8] == 'SIVIEWER'):           self.__editHPosition(delta_drag = drag_dx)
                        elif (section[:17] == 'MAINGRID_SIVIEWER'):
                            siViewerNumber = int(section[17:])
                            siAlloc = self.objectConfig['SIVIEWER{:d}SIAlloc'.format(siViewerNumber)]
                            if (siAlloc == 'VOL'): self.__editVMagFactor(displayBoxName = section.split("_")[1], delta_drag = drag_dy, anchor = 'BOTTOM')
                            else:                  self.__editVMagFactor(displayBoxName = section.split("_")[1], delta_drag = drag_dy)
                        #Delta Reset
                        self.mouse_DragDX[section] = 0; self.mouse_DragDY[section] = 0
                #Post-Interpretation
                self.mouseDragged = False
            #[1-2]: Mouse Scroll Handling
            if (self.mouse_Scrolled == True):
                for section in self.mouse_ScrollDX: #Iterating over 'self.mouseScrollDX' or 'self.mouseScrollDY' does not matter
                    #Scroll Delta
                    scroll_dx = self.mouse_ScrollDX[section]; scroll_dy = self.mouse_ScrollDY[section]
                    #Scroll Responses
                    if ((scroll_dx != 0) or (scroll_dy != 0)):
                        if (section == 'SETTINGSFRAME'):
                            self.internalGUIOs_SETTINGS_viewRange[0] += scroll_dy*5
                            self.internalGUIOs_SETTINGS_viewRange[1] += scroll_dy*5
                            self.__onSettingsViewRangeUpdate(byScrollBar=False)
                        elif (section == 'KLINESPRICE'):            self.__editHMagFactor(delta_scroll = scroll_dy); self.__updatePosHighlight(self.mouse_Event_lastRead['x'], self.mouse_Event_lastRead['y'], self.mouse_lastHoveredSection, updateType = 0)
                        elif (section == 'MAINGRID_KLINESPRICE'):   pass
                        elif (section == 'MAINGRID_TEMPORAL'):      self.__editHPosition(delta_drag = scroll_dy*500)
                        elif (section[:8] == 'SIVIEWER'):           self.__editHMagFactor(delta_scroll = scroll_dy); self.__updatePosHighlight(self.mouse_Event_lastRead['x'], self.mouse_Event_lastRead['y'], self.mouse_lastHoveredSection, updateType = 0)
                        elif (section[:17] == 'MAINGRID_SIVIEWER'): pass
                        #Delta Reset
                        self.mouse_ScrollDX[section] = 0; self.mouse_ScrollDY[section] = 0
                self.mouse_Scrolled = False
            #[1-3]: Period Counter Reset
            self.mouse_Event_lastInterpreted_ns = time.perf_counter_ns()

    def __process_PosHighlightUpdate(self, mei_beg):
        if (self.posHighlight_updatedPositions != None) and (_TIMEINTERVAL_POSHIGHLIGHTUPDATE <= mei_beg - self.posHighlight_lastUpdated_ns): self.__onPosHighlightUpdate()

    # * TLViewer and Analyzer Exclusive
    def __process_analysis(self, mei_beg):
        if ((self.chartDrawerType == 'TLVIEWER') and (0 < len(self.analysisQueue_list))):
            while ((0 < len(self.analysisQueue_list)) and (time.perf_counter_ns()-mei_beg <= _TIMELIMIT_KLINESPROCESS_NS)): self.__processKline()
            nAnalysisQueue = len(self.analysisQueue_list)
            t_current_ns = time.perf_counter_ns()
            if ((nAnalysisQueue == 0) or (_AUX_NANALYSISQUEUEDISPLAYUPDATEINTERVAL_NS <= time.perf_counter_ns()-self.__lastNumberOfAnalysisQueueDisplayUpdated)):
                fetchCompletion_perc = round((self.caRegeneration_nAnalysis_initial-nAnalysisQueue)/self.caRegeneration_nAnalysis_initial*100, 3)
                self.klinesLoadingGaugeBar.updateGaugeValue(fetchCompletion_perc)
                self.klinesLoadingTextBox_perc.updateText(text = "{:.3f} %".format(fetchCompletion_perc))
                if (nAnalysisQueue == 0): self.__TLViewer_onCurrencyAnalysisRegenerationComplete()

        elif ((self.chartDrawerType == 'ANALYZER') and (0 < len(self.analysisQueue_list))):
            while ((0 < len(self.analysisQueue_list)) and (time.perf_counter_ns()-mei_beg <= _TIMELIMIT_KLINESPROCESS_NS)): self.__processKline()
            nAnalysisQueue = len(self.analysisQueue_list)
            t_current_ns = time.perf_counter_ns()
            if ((nAnalysisQueue == 0) or (_AUX_NANALYSISQUEUEDISPLAYUPDATEINTERVAL_NS <= time.perf_counter_ns()-self.__lastNumberOfAnalysisQueueDisplayUpdated)):
                self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT3'].setText("Number of Remaining Analysis Queues: {:d}".format(nAnalysisQueue))
                self.__lastNumberOfAnalysisQueueDisplayUpdated = t_current_ns
            return (0 < len(self.analysisQueue_list))
        else: return False

    def __process_drawQueues(self, mei_beg):
        while (time.perf_counter_ns()-mei_beg < _TIMELIMIT_KLINESDRAWQUEUE_NS):
            #Draw Target Selection
            while (True):
                #Klines
                _ts = None
                for _ts in self.klines_drawQueue: 
                    for _aCode in self.klines_drawQueue[_ts]: self.__klineDrawer_sendDrawSignals(timestamp = _ts, analysisCode = _aCode)
                    break
                if (_ts != None): del self.klines_drawQueue[_ts]; break
                #WOI
                _t = None
                for _t in self.bidsAndAsks_WOI_drawQueue:
                    for _woiType in self.bidsAndAsks_WOI_drawQueue[_t]: self.__WOIDrawer_Draw(time = _t, woiType = _woiType)
                    break
                if (_t != None): del self.bidsAndAsks_WOI_drawQueue[_t]; break
                #NES
                _t = None
                for _t in self.aggTrades_NES_drawQueue:
                    for _nesType in self.aggTrades_NES_drawQueue[_t]: self.__NESDrawer_Draw(time = _t, nesType = _nesType)
                    break
                if (_t != None): del self.aggTrades_NES_drawQueue[_t]; break
                #Bids and Asks
                if (self.bidsAndAsks_drawFlag == True):
                    self.__bidsAndAsksDrawer_Draw()
                    self.bidsAndAsks_drawFlag = False
                    break
                #Finally (Will reach here if no drawing has occurred)
                return False
        return True

    def __process_RCLCGs(self, mei_beg):
        remainingProcTime = _TIMELIMIT_RCLCGPROCESSING_NS-(time.perf_counter_ns()-mei_beg)
        nRefedRCLCGs = len(self.__RCLCGReferences)
        #If there exist any shapes within the focus do draw, process them first
        RCLCGRefIndex = 0
        while ((RCLCGRefIndex < nRefedRCLCGs) and (0 < remainingProcTime)):
            if (self.__RCLCGReferences[RCLCGRefIndex].processShapeGenerationQueue(remainingProcTime, currentFocusOnly = True) == True): return True #Will return True if timeout has occurred and there still exist more shapes to draw
            else:
                remainingProcTime = _TIMELIMIT_RCLCGPROCESSING_NS-(time.perf_counter_ns()-mei_beg)
                RCLCGRefIndex += 1
        #If there is no more shapes to draw in the current focus, draw shapes outside the focus
        RCLCGRefIndex = 0
        while ((RCLCGRefIndex < nRefedRCLCGs) and (0 < remainingProcTime)):
            if (self.__RCLCGReferences[RCLCGRefIndex].processShapeGenerationQueue(remainingProcTime, currentFocusOnly = False) == True): return True #Will return True if timeout has occurred and there still exist more shapes to draw
            else:
                remainingProcTime = _TIMELIMIT_RCLCGPROCESSING_NS-(time.perf_counter_ns()-mei_beg)
                RCLCGRefIndex += 1
        #Return if there exist any more shapes to draw
        return False

    def __process_drawRemovalQueues(self, mei_beg):
        while (time.perf_counter_ns()-mei_beg < _TIMELIMIT_KLINESDRAWREMOVAL_NS):
            if   (0 < len(self.klines_drawRemovalQueue)):          self.__klineDrawer_RemoveExpiredDrawings(self.klines_drawRemovalQueue.pop())
            elif (0 < len(self.bidsAndAsks_WOI_drawRemovalQueue)): self.__WOIDrawer_RemoveExpiredDrawings(self.bidsAndAsks_WOI_drawRemovalQueue.pop())
            elif (0 < len(self.aggTrades_NES_drawRemovalQueue)):   self.__NESDrawer_RemoveExpiredDrawings(self.aggTrades_NES_drawRemovalQueue.pop())
            else: break
    #Processings END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #User Interaction Control ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def handleMouseEvent(self, event):
        _handleEvent = (self.klines_fetching == False)
        if ((self.chartDrawerType == 'TLVIEWER') and (0 < len(self.analysisQueue_list))): _handleEvent = False
        if (_handleEvent == True):
            if (event['eType'] == "MOVED"):
                #Find hovering section
                hoveredSection = None
                if (self.settingsSubPage_Opened == True) and (self.settingsSubPages[self.settingsSubPage_Current].isTouched(event['x'], event['y']) == True): hoveredSection = 'SETTINGSSUBPAGE'
                else:
                    for displayBoxName in self.hitBox:
                        if (self.hitBox[displayBoxName].isTouched(event['x'], event['y']) == True): hoveredSection = displayBoxName; break
                #Hovering Section Has Not Changed
                if (hoveredSection == self.mouse_lastHoveredSection):
                    if (hoveredSection == 'SETTINGSSUBPAGE'): self.settingsSubPages[self.settingsSubPage_Current].handleMouseEvent(event)
                #Hovering Section Changed
                else:
                    #[1]: New Hovered Section is 'SETTINGSBUTTONFRAME'
                    if (hoveredSection == 'SETTINGSBUTTONFRAME'):
                        self.frameSprites['SETTINGSBUTTONFRAME'].image = self.images['SETTINGSBUTTONFRAME_HOVERED'][0]
                        self.settingsButtonStatus = 'HOVERED'
                    #  or New Hovered Section is 'SETTINGSSUBPAGE'
                    elif (hoveredSection == 'SETTINGSSUBPAGE'):
                        self.settingsSubPages[self.settingsSubPage_Current].handleMouseEvent({'eType': "HOVERENTERED", 'x': event['x'], 'y': event['y']})
                    #  or New Hovered Section is None
                    elif (hoveredSection == None):
                        self.__updatePosHighlight(event['x'], event['y'], hoveredSection, updateType = 1)
                    #[2]: Last Hovered Section was 'SETTINGSBUTTONFRAME'
                    if (self.mouse_lastHoveredSection == 'SETTINGSBUTTONFRAME'):
                        self.frameSprites['SETTINGSBUTTONFRAME'].image = self.images['SETTINGSBUTTONFRAME_DEFAULT'][0]
                        self.settingsButtonStatus = 'DEFAULT'
                    #  or Last Hovered Section was 'SETTINGSSUBPAGE'
                    elif (self.mouse_lastHoveredSection == 'SETTINGSSUBPAGE'):
                        self.settingsSubPages[self.settingsSubPage_Current].handleMouseEvent({'eType': "HOVERESCAPED", 'x': event['x'], 'y': event['y']})
                #POSHIGHLIGHT Control
                if ((hoveredSection != None) and ((hoveredSection == 'KLINESPRICE') or (hoveredSection[:8] == 'SIVIEWER'))): self.__updatePosHighlight(event['x'], event['y'], hoveredSection, updateType = 0)
                #Recording
                self.mouse_lastHoveredSection = hoveredSection
        
            elif (event['eType'] == "PRESSED"):
                if (self.mouse_lastHoveredSection != self.mouse_lastSelectedSection):
                    if (self.mouse_lastSelectedSection == 'SETTINGSSUBPAGE'): self.settingsSubPages[self.settingsSubPage_Current].handleMouseEvent({'eType': "SELECTIONESCAPED", 'x': event['x'], 'y': event['y'], 'button': event['button'], 'modifiers': event['modifiers']})
                if (self.mouse_lastHoveredSection == 'SETTINGSBUTTONFRAME'):
                    self.frameSprites['SETTINGSBUTTONFRAME'].image = self.images['SETTINGSBUTTONFRAME_PRESSED'][0]
                    self.settingsButtonStatus = 'PRESSED'
                elif (self.mouse_lastHoveredSection == 'SETTINGSSUBPAGE'): self.settingsSubPages[self.settingsSubPage_Current].handleMouseEvent(event)
                #POSHIGHLIGHT Control
                if ((self.mouse_lastHoveredSection != None) and ((self.mouse_lastHoveredSection == 'KLINESPRICE') or (self.mouse_lastHoveredSection[:8] == 'SIVIEWER'))): self.__updatePosHighlight(event['x'], event['y'], self.mouse_lastHoveredSection, updateType = 1)
                #Recording
                self.mouse_lastSelectedSection = self.mouse_lastHoveredSection
                self.mouse_Event_lastPressed = event
        
            elif (event['eType'] == "RELEASED"):
                if (self.mouse_lastSelectedSection == self.mouse_lastHoveredSection):
                    if (self.mouse_lastHoveredSection == 'SETTINGSBUTTONFRAME'):
                        self.frameSprites['SETTINGSBUTTONFRAME'].image = self.images['SETTINGSBUTTONFRAME_HOVERED'][0]
                        self.settingsButtonStatus = 'HOVERED'
                        self.__onSettingsButtonClick()
                    elif (self.mouse_lastHoveredSection == 'SETTINGSSUBPAGE'): self.settingsSubPages[self.settingsSubPage_Current].handleMouseEvent(event)
                else:
                    if (self.mouse_lastSelectedSection == 'SETTINGSBUTTONFRAME'):
                        self.frameSprites['SETTINGSBUTTONFRAME'].image = self.images['SETTINGSBUTTONFRAME_DEFAULT'][0]
                        self.settingsButtonStatus = 'DEFAULT'
                    elif (self.mouse_lastSelectedSection == 'SETTINGSSUBPAGE'): self.settingsSubPages[self.settingsSubPage_Current].handleMouseEvent({'eType': "HOVERESCAPED", 'x': event['x'], 'y': event['y']})
                    if (self.mouse_lastHoveredSection == 'SETTINGSBUTTONFRAME'):
                        self.frameSprites['SETTINGSBUTTONFRAME'].image = self.images['SETTINGSBUTTONFRAME_HOVERED'][0]
                        self.settingsButtonStatus = 'HOVERED'
                    elif (self.mouse_lastHoveredSection == 'SETTINGSSUBPAGE'): self.settingsSubPages[self.settingsSubPage_Current].handleMouseEvent({'eType': "HOVEREENTERED", 'x': event['x'], 'y': event['y']})
                #POSHIGHLIGHT Control
                if ((self.mouse_lastHoveredSection != None) and ((self.mouse_lastHoveredSection == 'KLINESPRICE') or (self.mouse_lastHoveredSection[:8] == 'SIVIEWER'))): 
                    self.__updatePosHighlight(event['x'], event['y'], self.mouse_lastHoveredSection, updateType = 0)
                    if ((self.mouse_Event_lastPressed != None) and (self.mouse_Event_lastPressed['x'] == event['x']) and (self.mouse_Event_lastPressed['y'] == event['y'])):
                        #LEFT MOUSE BUTTON -> POSSELECTION Update
                        if (event['button'] == 1): self.__updatePosSelection(updateType = 0)   
                        #RIGHT MOUSE BUTTON -> moveToExtremaCenter
                        elif (event['button'] == 4):
                            if (self.mouse_lastHoveredSection == 'KLINESPRICE'): self.__editVVR_toExtremaCenter(displayBoxName = self.mouse_lastHoveredSection)
                            else:
                                siAlloc = self.objectConfig['SIVIEWER{:d}SIAlloc'.format(int(self.mouse_lastHoveredSection[8:]))]
                                if   (siAlloc == 'VOL'):   self.__editVVR_toExtremaCenter(displayBoxName = self.mouse_lastHoveredSection, extension_b = 0.0, extension_t = 0.2)
                                elif (siAlloc == 'MMACD'): self.__editVVR_toExtremaCenter(displayBoxName = self.mouse_lastHoveredSection, extension_b = 0.1, extension_t = 0.1)

            elif (event['eType'] == "DRAGGED"):
                #Find hovering section
                hoveredSection = None
                if (self.settingsSubPage_Opened == True) and (self.settingsSubPages[self.settingsSubPage_Current].isTouched(event['x'], event['y']) == True): hoveredSection = 'SETTINGSSUBPAGE'
                else:
                    for displayBoxName in self.hitBox:
                        if (self.hitBox[displayBoxName].isTouched(event['x'], event['y']) == True): hoveredSection = displayBoxName; break
                #Drag Source
                if (self.mouse_lastSelectedSection == 'SETTINGSSUBPAGE'): self.settingsSubPages[self.settingsSubPage_Current].handleMouseEvent(event)
                elif (self.mouse_lastSelectedSection != None) and (self.mouse_lastSelectedSection != 'SETTINGSBUTTONFRAME'): 
                    self.mouse_DragDX[self.mouse_lastSelectedSection] += event['dx']
                    self.mouse_DragDY[self.mouse_lastSelectedSection] += event['dy']
                    self.mouse_Dragged = True
                    self.mouse_lastDragged_ns = time.perf_counter_ns()
                self.mouse_lastHoveredSection = hoveredSection
        
            elif (event['eType'] == "SCROLLED"):
                if (self.mouse_lastSelectedSection == 'SETTINGSSUBPAGE'): self.settingsSubPages[self.settingsSubPage_Current].handleMouseEvent(event)
                elif (self.mouse_lastSelectedSection != None):
                    self.mouse_ScrollDX[self.mouse_lastSelectedSection] += event['scroll_x']
                    self.mouse_ScrollDY[self.mouse_lastSelectedSection] += event['scroll_y']
                    self.mouse_Scrolled = True
                    self.mouse_lastScrolled_ns = time.perf_counter_ns()
        
            elif (event['eType'] == "SELECTIONESCAPED"):
                if (self.mouse_lastSelectedSection == 'SETTINGSSUBPAGE'): self.settingsSubPages[self.settingsSubPage_Current].handleMouseEvent(event)
                self.mouse_lastSelectedSection = None
        
            elif (event['eType'] == "HOVERESCAPED"):
                self.__updatePosHighlight(event['x'], event['y'], None, updateType = 1)
                self.mouse_lastSelectedSection = None

        self.mouse_Event_lastRead = event

    def __updatePosHighlight(self, mouseX, mouseY, hoveredSection, updateType):
        if (updateType == 0):
            try:
                #Get Position Within the DrawBox
                xWithinDrawBox = mouseX-self.displayBox_graphics['MAINGRID_TEMPORAL']['DRAWBOX'][0]
                yWithinDrawBox = mouseY-self.displayBox_graphics[hoveredSection]['DRAWBOX'][1]
                #Compute Abstract Space Position
                xValHovered = xWithinDrawBox/self.displayBox_graphics['MAINGRID_TEMPORAL']['DRAWBOX'][2]*(self.horizontalViewRange[1]-self.horizontalViewRange[0])+self.horizontalViewRange[0]
                yValHovered = yWithinDrawBox/self.displayBox_graphics[hoveredSection]['DRAWBOX'][3]*(self.verticalViewRange[hoveredSection][1]-self.verticalViewRange[hoveredSection][0])+self.verticalViewRange[hoveredSection][0]
                #Get Timestamp Interval Position
                tsIntervalHovered_0 = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = xValHovered, mrktReg = self.mrktRegTS, nTicks = 0)

                #If there exist no previous hoveredPosition
                if (self.posHighlight_hoveredPos[2] == None): 
                    self.posHighlight_updatedPositions = [True, True]
                    self.posHighlight_hoveredPos = (tsIntervalHovered_0, yValHovered, hoveredSection, None)
                #If there exist a previous hoveredPoisiton
                else:
                    self.posHighlight_updatedPositions = [False, False]
                    if (self.posHighlight_hoveredPos[0] != tsIntervalHovered_0): self.posHighlight_updatedPositions[0] = True
                    if (self.posHighlight_hoveredPos[1] != yValHovered):         self.posHighlight_updatedPositions[1] = True
                    if (self.posHighlight_hoveredPos[2] != hoveredSection): self.posHighlight_hoveredPos = (tsIntervalHovered_0, yValHovered, hoveredSection, self.posHighlight_hoveredPos[2])
                    else:                                                   self.posHighlight_hoveredPos = (tsIntervalHovered_0, yValHovered, hoveredSection, hoveredSection)
            except:
                self.posHighlight_hoveredPos = (None, None, None, self.posHighlight_hoveredPos[2])
                self.posHighlight_updatedPositions = [True, True]

        elif (updateType == 1):
            if (self.posHighlight_hoveredPos[2] != None):
                self.posHighlight_hoveredPos = (None, None, None, self.posHighlight_hoveredPos[2])
                self.posHighlight_updatedPositions = [True, True]

    def __onPosHighlightUpdate(self):
        #Horizontal Elements Update
        if (self.posHighlight_updatedPositions[0] == True):
            if (self.posHighlight_hoveredPos[2] == None): 
                self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_HOVERED'].visible = False
                for displayBoxName in self.displayBox_graphics_visibleSIViewers: self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_HOVERED'].visible = False
                self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT1'].hide()
                self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2'].hide()
                for displayBoxName in self.displayBox_graphics_visibleSIViewers: self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].hide()
            else:
                #Visibility Control
                if (self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_HOVERED'].visible == False): self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_HOVERED'].visible = True
                if (self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT1'].isHidden() == True): self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT1'].show()
                if (self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2'].isHidden() == True): self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2'].show()
                for displayBoxName in self.displayBox_graphics_visibleSIViewers:
                    if (self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_HOVERED'].visible == False): self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_HOVERED'].visible = True
                    if (self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].isHidden() == True): self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].show()
                #Update Highligter Graphics
                ts_rightEnd = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = self.posHighlight_hoveredPos[0], mrktReg = self.mrktRegTS, nTicks = 1)
                pixelPerTS = self.displayBox_graphics['MAINGRID_TEMPORAL']['DRAWBOX'][2]*self.scaler / (self.horizontalViewRange[1]-self.horizontalViewRange[0])
                highlightShape_x     = round((self.posHighlight_hoveredPos[0]-self.verticalGrid_intervals[0])*pixelPerTS, 1)
                highlightShape_width = round((ts_rightEnd-self.posHighlight_hoveredPos[0])*pixelPerTS,                    1)
                self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_HOVERED'].x     = highlightShape_x
                self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_HOVERED'].width = highlightShape_width
                if (self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_HOVERED'].visible == False): self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_HOVERED'].visible = True
                for displayBoxName in self.displayBox_graphics_visibleSIViewers:
                    self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_HOVERED'].x     = highlightShape_x
                    self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_HOVERED'].width = highlightShape_width
                    if (self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_HOVERED'].visible == False): self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_HOVERED'].visible = True
                #Update Kline Descriptor
                if (self.posHighlight_hoveredPos[0] in self.klines['raw']):
                    p_open  = self.klines['raw'][self.posHighlight_hoveredPos[0]][2]
                    p_high  = self.klines['raw'][self.posHighlight_hoveredPos[0]][3]
                    p_low   = self.klines['raw'][self.posHighlight_hoveredPos[0]][4]
                    p_close = self.klines['raw'][self.posHighlight_hoveredPos[0]][5]
                    if   (p_open < p_close):  klineColor = 'CONTENT_POSITIVE_{:d}'.format(self.objectConfig['KlineColorType'])
                    elif (p_close < p_open):  klineColor = 'CONTENT_NEGATIVE_{:d}'.format(self.objectConfig['KlineColorType'])
                    elif (p_open == p_close): klineColor = 'CONTENT_NEUTRAL_{:d}'.format(self.objectConfig['KlineColorType'])
                    #DisplayBox 'KLINESPRICE'
                    #Klines
                    pPrecision = self.verticalViewRange_precision['KLINESPRICE']
                    displayText_time  = datetime.fromtimestamp(self.posHighlight_hoveredPos[0]+self.timezoneDelta, tz = timezone.utc).strftime(" %Y/%m/%d %H:%M"); tp1 = len(displayText_time)
                    p_open_str  = atmEta_Auxillaries.floatToString(number = p_open,  precision = pPrecision)
                    p_high_str  = atmEta_Auxillaries.floatToString(number = p_high,  precision = pPrecision)
                    p_low_str   = atmEta_Auxillaries.floatToString(number = p_low,   precision = pPrecision)
                    p_close_str = atmEta_Auxillaries.floatToString(number = p_close, precision = pPrecision)
                    displayText_open  = " OPEN: {:s}".format(p_open_str);   tp2 = tp1 + len(displayText_open) 
                    displayText_high  = " HIGH: {:s}".format(p_high_str);   tp3 = tp2 + len(displayText_high)
                    displayText_low   = " LOW: {:s}".format(p_low_str);     tp4 = tp3 + len(displayText_low)
                    displayText_close = " CLOSE: {:s}".format(p_close_str); tp5 = tp4 + len(displayText_close)
                    self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT1'].setText(displayText_time+displayText_open+displayText_high+displayText_low+displayText_close, [((0,     tp1+5), 'DEFAULT'),
                                                                                                                                                                                ((tp1+6, tp2),   klineColor),
                                                                                                                                                                                ((tp2+1, tp2+5), 'DEFAULT'),
                                                                                                                                                                                ((tp2+6, tp3),   klineColor),
                                                                                                                                                                                ((tp3+1, tp3+4), 'DEFAULT'),
                                                                                                                                                                                ((tp3+5, tp4),   klineColor),
                                                                                                                                                                                ((tp4+1, tp4+6), 'DEFAULT'),
                                                                                                                                                                                ((tp4+7, tp5-1), klineColor)])
                    #Main-Indicators
                    _toDisplay = None
                    if   (('TRADELOG' in self.klines) and (self.posHighlight_hoveredPos[0] in self.klines['TRADELOG']) and (self.objectConfig['TRADELOG_Display'] == True)): _toDisplay = 'TRADELOG'
                    elif (('IVP'      in self.klines) and (self.posHighlight_hoveredPos[0] in self.klines['IVP'])      and (self.objectConfig['IVP_Master']       == True)): _toDisplay = 'IVP'
                    if (_toDisplay != None):
                        if   (_toDisplay == 'TRADELOG'):
                            tradeLog = self.klines['TRADELOG'][self.posHighlight_hoveredPos[0]]
                            if (tradeLog['logicSource'] == None):
                                if (tradeLog['totalQuantity'] == 0): infoText2 = " [TRADELOG] Entry: N/A, Quantity: 0"
                                else:
                                    infoText2 = " [TRADELOG] Entry: {:s}, Quantity: {:s}".format(atmEta_Auxillaries.floatToString(number = tradeLog['entryPrice'],    precision = self.targetPrecisions['price']),
                                                                                                 atmEta_Auxillaries.floatToString(number = tradeLog['totalQuantity'], precision = self.targetPrecisions['quantity']))
                            else:
                                if (tradeLog['totalQuantity'] == 0):
                                    infoText2 = " [TRADELOG] Entry: N/A, Quantity: 0, logicSource: {:s}, TradeQuantity: {:s}, TradePrice: {:s}, Profit: {:s}, TradingFee: {:s}".format(tradeLog['logicSource'],
                                                                                                                                                                                       atmEta_Auxillaries.floatToString(number = tradeLog['quantity'],   precision = self.targetPrecisions['quantity']),
                                                                                                                                                                                       atmEta_Auxillaries.floatToString(number = tradeLog['price'],      precision = self.targetPrecisions['price']),
                                                                                                                                                                                       atmEta_Auxillaries.floatToString(number = tradeLog['profit'],     precision = self.targetPrecisions['quote']),
                                                                                                                                                                                       atmEta_Auxillaries.floatToString(number = tradeLog['tradingFee'], precision = self.targetPrecisions['quote']))
                                else:
                                    infoText2 = " [TRADELOG] Entry: {:s}, Quantity: {:s}, Logic Source: {:s}, TradeQuantity: {:s}, TradePrice: {:s}, Profit: {:s}, TradingFee: {:s}".format(atmEta_Auxillaries.floatToString(number = tradeLog['entryPrice'],    precision = self.targetPrecisions['price']),
                                                                                                                                                                                            atmEta_Auxillaries.floatToString(number = tradeLog['totalQuantity'], precision = self.targetPrecisions['quantity']),
                                                                                                                                                                                            tradeLog['logicSource'],
                                                                                                                                                                                            atmEta_Auxillaries.floatToString(number = tradeLog['quantity'],   precision = self.targetPrecisions['quantity']),
                                                                                                                                                                                            atmEta_Auxillaries.floatToString(number = tradeLog['price'],      precision = self.targetPrecisions['price']),
                                                                                                                                                                                            atmEta_Auxillaries.floatToString(number = tradeLog['profit'],     precision = self.targetPrecisions['quote']),
                                                                                                                                                                                            atmEta_Auxillaries.floatToString(number = tradeLog['tradingFee'], precision = self.targetPrecisions['quote']))
                        elif (_toDisplay == 'IVP'):
                            ivpResult = self.klines['IVP'][self.posHighlight_hoveredPos[0]]
                            try:    infoText2 = " [IVP] nDivisions: {:d}, Gamma Factor: {:.2f} % [{:s}]".format(len(ivpResult['volumePriceLevelProfile']), ivpResult['gammaFactor']*100, str(ivpResult['betaFactor']))
                            except: infoText2 = " [IVP] nDivisions: NONE, Gamma Factor: NONE"
                    else: infoText2 = ""
                    #---Check for this for info line 2, since cases where the previous text and the new text are the same are expected to occur frequently
                    previousText = self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2'].getText()
                    if (previousText != infoText2): self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2'].setText(infoText2)
                    #SIViewers
                    for displayBoxName in self.displayBox_graphics_visibleSIViewers:
                        siViewerNumber = int(displayBoxName[8:])
                        siAlloc = self.objectConfig['SIVIEWER{:d}SIAlloc'.format(siViewerNumber)]
                        displayText = ""
                        textFormats = list()
                        if (siAlloc == 'VOL'):
                            if (self.posHighlight_hoveredPos[0] in self.klines['raw']):
                                textBlock = " [SI{:d} - VOL]".format(siViewerNumber)
                                displayText += textBlock; textFormats.append(((0, len(textBlock)-1), 'DEFAULT'))
                                if (self.objectConfig['VOL_VolumeType'] == 'BASE'):    textBlock = " VOL_BASE: {:s} {:s}".format(atmEta_Auxillaries.floatToString(number    = self.klines['raw'][self.posHighlight_hoveredPos[0]][KLINDEX_VOLBASE],          precision = self.currencyInfo['precisions']['quantity']), self.currencyInfo['info_server']['baseAsset']);  textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][1]+10), 'DEFAULT')); textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][0]+len(textBlock)-1), klineColor))
                                if (self.objectConfig['VOL_VolumeType'] == 'QUOTE'):   textBlock = " VOL_QUOTE: {:s} {:s}".format(atmEta_Auxillaries.floatToString(number   = self.klines['raw'][self.posHighlight_hoveredPos[0]][KLINDEX_VOLQUOTE],         precision = self.currencyInfo['precisions']['quote']),    self.currencyInfo['info_server']['quoteAsset']); textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][1]+11), 'DEFAULT')); textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][0]+len(textBlock)-1), klineColor))
                                if (self.objectConfig['VOL_VolumeType'] == 'BASETB'):  textBlock = " VOL_BASETB: {:s} {:s}".format(atmEta_Auxillaries.floatToString(number  = self.klines['raw'][self.posHighlight_hoveredPos[0]][KLINDEX_VOLBASETAKERBUY],  precision = self.currencyInfo['precisions']['quantity']), self.currencyInfo['info_server']['baseAsset']);  textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][1]+12), 'DEFAULT')); textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][0]+len(textBlock)-1), klineColor))
                                if (self.objectConfig['VOL_VolumeType'] == 'QUOTETB'): textBlock = " VOL_QUOTETB: {:s} {:s}".format(atmEta_Auxillaries.floatToString(number = self.klines['raw'][self.posHighlight_hoveredPos[0]][KLINDEX_VOLQUOTETAKERBUY], precision = self.currencyInfo['precisions']['quote']),    self.currencyInfo['info_server']['quoteAsset']); textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][1]+13), 'DEFAULT')); textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][0]+len(textBlock)-1), klineColor))
                                displayText += textBlock
                                for analysisCode in self.siTypes_analysisCodes[siAlloc]:
                                    if ((analysisCode != 'VOL') and (self.posHighlight_hoveredPos[0] in self.klines[analysisCode])):
                                        #TextStyle Check
                                        lineNumber = self.analysisParams[analysisCode]['lineNumber']
                                        currentLineStyle = self.displayBox_graphics['SIVIEWER{:d}'.format(siViewerNumber)]['DESCRIPTIONTEXT1'].getTextStyle(lineNumber)
                                        currentLineColor = (self.objectConfig['VOL_{:d}_ColorR%{:s}'.format(lineNumber, self.currentGUITheme)],
                                                            self.objectConfig['VOL_{:d}_ColorG%{:s}'.format(lineNumber, self.currentGUITheme)],
                                                            self.objectConfig['VOL_{:d}_ColorB%{:s}'.format(lineNumber, self.currentGUITheme)],
                                                            self.objectConfig['VOL_{:d}_ColorA%{:s}'.format(lineNumber, self.currentGUITheme)])
                                        if (currentLineStyle == None) or (currentLineStyle['color'] != currentLineColor):
                                            newTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                                            newTextStyle['color'] = currentLineColor
                                            self.displayBox_graphics['SIVIEWER{:d}'.format(siViewerNumber)]['DESCRIPTIONTEXT1'].addTextStyle(str(lineNumber), newTextStyle)
                                        #Text & Format Array Construction
                                        textBlock = " {:s}: {:s}".format(analysisCode, str(self.klines[analysisCode][self.posHighlight_hoveredPos[0]]['MA']))
                                        if (self.objectConfig['VOL_VolumeType'] == 'BASE'):    textBlock = " {:s}: {:s}".format(analysisCode, atmEta_Auxillaries.floatToString(number = self.klines[analysisCode][self.posHighlight_hoveredPos[0]]['MA'], precision = self.currencyInfo['precisions']['quantity']))
                                        if (self.objectConfig['VOL_VolumeType'] == 'QUOTE'):   textBlock = " {:s}: {:s}".format(analysisCode, atmEta_Auxillaries.floatToString(number = self.klines[analysisCode][self.posHighlight_hoveredPos[0]]['MA'], precision = self.currencyInfo['precisions']['quote']))
                                        if (self.objectConfig['VOL_VolumeType'] == 'BASETB'):  textBlock = " {:s}: {:s}".format(analysisCode, atmEta_Auxillaries.floatToString(number = self.klines[analysisCode][self.posHighlight_hoveredPos[0]]['MA'], precision = self.currencyInfo['precisions']['quantity']))
                                        if (self.objectConfig['VOL_VolumeType'] == 'QUOTETB'): textBlock = " {:s}: {:s}".format(analysisCode, atmEta_Auxillaries.floatToString(number = self.klines[analysisCode][self.posHighlight_hoveredPos[0]]['MA'], precision = self.currencyInfo['precisions']['quote']))
                                        displayText += textBlock;
                                        textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][1]+len(analysisCode)+3), 'DEFAULT'))
                                        textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][0]+len(textBlock)-1),    str(lineNumber)))
                                self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].setText(displayText, textFormats)
                            else:
                                self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].setText(" [SI{:d} - VOL]".format(siViewerNumber))
                                self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].editTextStyle('all', 'DEFAULT')
                        elif (siAlloc == 'MMACDSHORT'):
                            if ('MMACDSHORT' in self.klines and self.posHighlight_hoveredPos[0] in self.klines['MMACDSHORT']):
                                textBlock = " [SI{:d} - MMACDSHORT]".format(siViewerNumber)
                                displayText += textBlock; textFormats.append(((0, len(textBlock)-1), 'DEFAULT'))
                                displayValues = {'MMACD':     self.klines['MMACDSHORT'][self.posHighlight_hoveredPos[0]]['MMACD'],
                                                 'SIGNAL':    self.klines['MMACDSHORT'][self.posHighlight_hoveredPos[0]]['SIGNAL'],
                                                 'HISTOGRAM': self.klines['MMACDSHORT'][self.posHighlight_hoveredPos[0]]['MSDELTA']}
                                for valueType in ('MMACD', 'SIGNAL', 'HISTOGRAM'):
                                    #TextStyle Check
                                    if (valueType == 'HISTOGRAM'):
                                        if (displayValues['HISTOGRAM'] == None): textStyleName = None
                                        else:
                                            if (0 <= displayValues['HISTOGRAM']): textStyleName = 'HISTOGRAM+'
                                            else:                                 textStyleName = 'HISTOGRAM-'
                                    else: textStyleName = valueType
                                    if (textStyleName == None): textStyleName = 'DEFAULT'
                                    else:
                                        currentLineStyle = self.displayBox_graphics['SIVIEWER{:d}'.format(siViewerNumber)]['DESCRIPTIONTEXT1'].getTextStyle(textStyleName)
                                        currentLineColor = (self.objectConfig['MMACDSHORT_{:s}_ColorR%{:s}'.format(textStyleName, self.currentGUITheme)],
                                                            self.objectConfig['MMACDSHORT_{:s}_ColorG%{:s}'.format(textStyleName, self.currentGUITheme)],
                                                            self.objectConfig['MMACDSHORT_{:s}_ColorB%{:s}'.format(textStyleName, self.currentGUITheme)],
                                                            self.objectConfig['MMACDSHORT_{:s}_ColorA%{:s}'.format(textStyleName, self.currentGUITheme)])
                                        if (currentLineStyle == None) or (currentLineStyle['color'] != currentLineColor):
                                            newTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                                            newTextStyle['color'] = currentLineColor
                                            self.displayBox_graphics['SIVIEWER{:d}'.format(siViewerNumber)]['DESCRIPTIONTEXT1'].addTextStyle(textStyleName, newTextStyle)
                                    #Text & Format Array Construction
                                    if (displayValues[valueType] == None): displayValue_str = "NONE"
                                    else:                                  displayValue_str = atmEta_Auxillaries.floatToString(number = displayValues[valueType], precision = self.currencyInfo['precisions']['price']+2)
                                    textBlock = " {:s}: {:s}".format(valueType, displayValue_str)
                                    displayText += textBlock;
                                    textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][1]+len(valueType)+3), 'DEFAULT'))
                                    textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][0]+len(textBlock)-1),  textStyleName))
                                self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].setText(displayText, textFormats)
                            else:
                                self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].setText(" [SI{:d} - MMACDSHORT]".format(siViewerNumber))
                                self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].editTextStyle('all', 'DEFAULT')
                        elif (siAlloc == 'MMACDLONG'):
                            if ('MMACDLONG' in self.klines and self.posHighlight_hoveredPos[0] in self.klines['MMACDLONG']):
                                textBlock = " [SI{:d} - MMACDLONG]".format(siViewerNumber)
                                displayText += textBlock; textFormats.append(((0, len(textBlock)-1), 'DEFAULT'))
                                displayValues = {'MMACD':     self.klines['MMACDLONG'][self.posHighlight_hoveredPos[0]]['MMACD'],
                                                 'SIGNAL':    self.klines['MMACDLONG'][self.posHighlight_hoveredPos[0]]['SIGNAL'],
                                                 'HISTOGRAM': self.klines['MMACDLONG'][self.posHighlight_hoveredPos[0]]['MSDELTA']}
                                for valueType in ('MMACD', 'SIGNAL', 'HISTOGRAM'):
                                    #TextStyle Check
                                    if (valueType == 'HISTOGRAM'):
                                        if (displayValues['HISTOGRAM'] == None): textStyleName = None
                                        else:
                                            if (0 <= displayValues['HISTOGRAM']): textStyleName = 'HISTOGRAM+'
                                            else:                                 textStyleName = 'HISTOGRAM-'
                                    else: textStyleName = valueType
                                    if (textStyleName == None): textStyleName = 'DEFAULT'
                                    else:
                                        currentLineStyle = self.displayBox_graphics['SIVIEWER{:d}'.format(siViewerNumber)]['DESCRIPTIONTEXT1'].getTextStyle(textStyleName)
                                        currentLineColor = (self.objectConfig['MMACDLONG_{:s}_ColorR%{:s}'.format(textStyleName, self.currentGUITheme)],
                                                            self.objectConfig['MMACDLONG_{:s}_ColorG%{:s}'.format(textStyleName, self.currentGUITheme)],
                                                            self.objectConfig['MMACDLONG_{:s}_ColorB%{:s}'.format(textStyleName, self.currentGUITheme)],
                                                            self.objectConfig['MMACDLONG_{:s}_ColorA%{:s}'.format(textStyleName, self.currentGUITheme)])
                                        if (currentLineStyle == None) or (currentLineStyle['color'] != currentLineColor):
                                            newTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                                            newTextStyle['color'] = currentLineColor
                                            self.displayBox_graphics['SIVIEWER{:d}'.format(siViewerNumber)]['DESCRIPTIONTEXT1'].addTextStyle(textStyleName, newTextStyle)
                                    #Text & Format Array Construction
                                    if (displayValues[valueType] == None): displayValue_str = "NONE"
                                    else:                                  displayValue_str = atmEta_Auxillaries.floatToString(number = displayValues[valueType], precision = self.currencyInfo['precisions']['price']+2)
                                    textBlock = " {:s}: {:s}".format(valueType, displayValue_str)
                                    displayText += textBlock;
                                    textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][1]+len(valueType)+3), 'DEFAULT'))
                                    textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][0]+len(textBlock)-1),  textStyleName))
                                self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].setText(displayText, textFormats)
                            else:
                                self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].setText(" [SI{:d} - MMACDLONG]".format(siViewerNumber))
                                self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].editTextStyle('all', 'DEFAULT')
                        elif (siAlloc == 'DMIxADX'):
                            textBlock = " [SI{:d} - DMIxADX]".format(siViewerNumber)
                            displayText += textBlock; textFormats.append(((0, len(textBlock)-1), 'DEFAULT'))
                            for analysisCode in self.siTypes_analysisCodes[siAlloc]:
                                if (self.posHighlight_hoveredPos[0] in self.klines[analysisCode]):
                                    #TextStyle Check
                                    lineNumber = self.analysisParams[analysisCode]['lineNumber']
                                    currentLineStyle = self.displayBox_graphics['SIVIEWER{:d}'.format(siViewerNumber)]['DESCRIPTIONTEXT1'].getTextStyle(lineNumber)
                                    currentLineColor = (self.objectConfig['DMIxADX_{:d}_ColorR%{:s}'.format(lineNumber, self.currentGUITheme)],
                                                        self.objectConfig['DMIxADX_{:d}_ColorG%{:s}'.format(lineNumber, self.currentGUITheme)],
                                                        self.objectConfig['DMIxADX_{:d}_ColorB%{:s}'.format(lineNumber, self.currentGUITheme)],
                                                        self.objectConfig['DMIxADX_{:d}_ColorA%{:s}'.format(lineNumber, self.currentGUITheme)])
                                    if (currentLineStyle == None) or (currentLineStyle['color'] != currentLineColor):
                                        newTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                                        newTextStyle['color'] = currentLineColor
                                        self.displayBox_graphics['SIVIEWER{:d}'.format(siViewerNumber)]['DESCRIPTIONTEXT1'].addTextStyle(str(lineNumber), newTextStyle)
                                    #Text & Format Array Construction
                                    value_dmixadx_absAthRel = self.klines[analysisCode][self.posHighlight_hoveredPos[0]]['DMIxADX_ABSATHREL']
                                    if (value_dmixadx_absAthRel == None): textBlock = " {:s}: NONE".format(analysisCode)
                                    else:                                 textBlock = " {:s}: {:s}".format(analysisCode, atmEta_Auxillaries.simpleValueFormatter(value = value_dmixadx_absAthRel))
                                    displayText += textBlock;
                                    textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][1]+len(analysisCode)+3), 'DEFAULT'))
                                    textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][0]+len(textBlock)-1),    str(lineNumber)))
                            self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].setText(displayText, textFormats)
                        elif (siAlloc == 'MFI'):
                            textBlock = " [SI{:d} - MFI]".format(siViewerNumber)
                            displayText += textBlock; textFormats.append(((0, len(textBlock)-1), 'DEFAULT'))
                            for analysisCode in self.siTypes_analysisCodes[siAlloc]:
                                if (self.posHighlight_hoveredPos[0] in self.klines[analysisCode]):
                                    #TextStyle Check
                                    lineNumber = self.analysisParams[analysisCode]['lineNumber']
                                    currentLineStyle = self.displayBox_graphics['SIVIEWER{:d}'.format(siViewerNumber)]['DESCRIPTIONTEXT1'].getTextStyle(lineNumber)
                                    currentLineColor = (self.objectConfig['MFI_{:d}_ColorR%{:s}'.format(lineNumber, self.currentGUITheme)],
                                                        self.objectConfig['MFI_{:d}_ColorG%{:s}'.format(lineNumber, self.currentGUITheme)],
                                                        self.objectConfig['MFI_{:d}_ColorB%{:s}'.format(lineNumber, self.currentGUITheme)],
                                                        self.objectConfig['MFI_{:d}_ColorA%{:s}'.format(lineNumber, self.currentGUITheme)])
                                    if (currentLineStyle == None) or (currentLineStyle['color'] != currentLineColor):
                                        newTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                                        newTextStyle['color'] = currentLineColor
                                        self.displayBox_graphics['SIVIEWER{:d}'.format(siViewerNumber)]['DESCRIPTIONTEXT1'].addTextStyle(str(lineNumber), newTextStyle)
                                    #Text & Format Array Construction
                                    value_mfiAbsAthRel = self.klines[analysisCode][self.posHighlight_hoveredPos[0]]['MFI_ABSATHREL']
                                    if (value_mfiAbsAthRel == None): textBlock = " {:s}: NONE".format(analysisCode)
                                    else:                            textBlock = " {:s}: {:.2f}".format(analysisCode, value_mfiAbsAthRel)
                                    displayText += textBlock;
                                    textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][1]+len(analysisCode)+3), 'DEFAULT'))
                                    textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][0]+len(textBlock)-1),    str(lineNumber)))
                            self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].setText(displayText, textFormats)
                else:
                    displayText_time  = datetime.fromtimestamp(self.posHighlight_hoveredPos[0]+self.timezoneDelta, tz = timezone.utc).strftime(" %Y/%m/%d %H:%M")
                    displayText_open  = " OPEN: -"
                    displayText_high  = " HIGH: -"
                    displayText_low   = " LOW: -"
                    displayText_close = " CLOSE: -"
                    self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT1'].setText(displayText_time+displayText_open+displayText_high+displayText_low+displayText_close)
                    self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT1'].editTextStyle('all', 'DEFAULT')
                    self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2'].setText("")
                    for displayBoxName in self.displayBox_graphics_visibleSIViewers:
                        siViewerNumber = int(displayBoxName[8:])
                        siAlloc = self.objectConfig['SIVIEWER{:d}SIAlloc'.format(siViewerNumber)]
                        self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].setText(" [SI{:d} - {:s}]".format(siViewerNumber, str(siAlloc)))
                        self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].editTextStyle('all', 'DEFAULT')
        #Vertcial Elements Update
        if (self.posHighlight_updatedPositions[1] == True):
            if (self.posHighlight_hoveredPos[2] == None):
                self.displayBox_graphics['KLINESPRICE']['HORIZONTALGUIDELINE'].visible = False
                self.displayBox_graphics['KLINESPRICE']['HORIZONTALGUIDETEXT'].hide()
                for displayBoxName in self.displayBox_graphics_visibleSIViewers: 
                    self.displayBox_graphics[displayBoxName]['HORIZONTALGUIDELINE'].visible = False
                    self.displayBox_graphics[displayBoxName]['HORIZONTALGUIDETEXT'].hide()
            else:
                dBox_current  = self.posHighlight_hoveredPos[2]
                dBox_previous = self.posHighlight_hoveredPos[3]
                #Visibility Control
                if ((dBox_previous != None) and (dBox_previous != dBox_current)):
                    self.displayBox_graphics[dBox_previous]['HORIZONTALGUIDELINE'].visible = False
                    self.displayBox_graphics[dBox_previous]['HORIZONTALGUIDETEXT'].hide()
                else:
                    if (self.displayBox_graphics[dBox_current]['HORIZONTALGUIDELINE'].visible == False): self.displayBox_graphics[dBox_current]['HORIZONTALGUIDELINE'].visible = True
                    if (self.displayBox_graphics[dBox_current]['HORIZONTALGUIDETEXT'].isHidden() == True): self.displayBox_graphics[dBox_current]['HORIZONTALGUIDETEXT'].show()
                #Update Highligter Graphics
                pixelPerVal = self.displayBox_graphics[dBox_current]['DRAWBOX'][3]*self.scaler / (self.verticalViewRange[dBox_current][1]-self.verticalViewRange[dBox_current][0])
                try:    verticalHoverLine_y = round((self.posHighlight_hoveredPos[1]-self.horizontalGridIntervals[dBox_current][0])*pixelPerVal, 1)
                except: verticalHoverLine_y = round(self.posHighlight_hoveredPos[1]*pixelPerVal,                                                 1)
                self.displayBox_graphics[dBox_current]['HORIZONTALGUIDELINE'].y  = verticalHoverLine_y
                self.displayBox_graphics[dBox_current]['HORIZONTALGUIDELINE'].y2 = verticalHoverLine_y
                #Update Vertical Value Text
                dFromCeiling = self.displayBox_graphics[dBox_current]['HORIZONTALGRID_CAMGROUP'].projection_y1-verticalHoverLine_y
                if (dFromCeiling < _GD_DISPLAYBOX_GUIDE_HORIZONTALTEXTHEIGHT*self.scaler): self.displayBox_graphics[dBox_current]['HORIZONTALGUIDETEXT'].moveTo(y = verticalHoverLine_y/self.scaler-_GD_DISPLAYBOX_GUIDE_HORIZONTALTEXTHEIGHT)
                else:                                                            self.displayBox_graphics[dBox_current]['HORIZONTALGUIDETEXT'].moveTo(y = verticalHoverLine_y/self.scaler)
                self.displayBox_graphics[dBox_current]['HORIZONTALGUIDETEXT'].setText(atmEta_Auxillaries.floatToString(number = self.posHighlight_hoveredPos[1], precision = self.verticalViewRange_precision[dBox_current]))
        self.posHighlight_updatedPositions = None

    def __updatePosSelection(self, updateType):
        #By button press->release
        if (updateType == 0):
            if (self.posHighlight_hoveredPos[2] != None):
                if (self.posHighlight_hoveredPos[0] == self.posHighlight_selectedPos):
                    self.posHighlight_selectedPos = None
                    self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_SELECTED'].visible = False
                    for displayBoxName in self.displayBox_graphics_visibleSIViewers: self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_SELECTED'].visible = False
                else:
                    self.posHighlight_selectedPos = self.posHighlight_hoveredPos[0]
                    shape_xPos  = self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_HOVERED'].x
                    shape_width = self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_HOVERED'].width
                    self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_SELECTED'].x     = shape_xPos
                    self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_SELECTED'].width = shape_width
                    self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_SELECTED'].visible = True
                    for displayBoxName in self.displayBox_graphics_visibleSIViewers: 
                        self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_SELECTED'].x     = shape_xPos
                        self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_SELECTED'].width = shape_width
                        self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_SELECTED'].visible = True
                self.__onPosSelectionUpdate()
        #By HorizontalViewRange Update
        elif (updateType == 1):
            if (self.posHighlight_selectedPos != None):
                tsPosEnd = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = self.posHighlight_selectedPos, mrktReg = self.mrktRegTS, nTicks = 1)
                pixelPerTS = self.displayBox_graphics['MAINGRID_TEMPORAL']['DRAWBOX'][2]*self.scaler / (self.horizontalViewRange[1]-self.horizontalViewRange[0])
                shape_xPos  = round((self.posHighlight_selectedPos-self.verticalGrid_intervals[0])*pixelPerTS, 1)
                shape_width = round((tsPosEnd-self.posHighlight_selectedPos)*pixelPerTS,                       1)
                self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_SELECTED'].x     = shape_xPos
                self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_SELECTED'].width = shape_width
                for displayBoxName in self.displayBox_graphics_visibleSIViewers: 
                    self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_SELECTED'].x     = shape_xPos
                    self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_SELECTED'].width = shape_width

    def __onPosSelectionUpdate(self):
        #IVP Update
        if ('IVP' in self.analysisParams):
            if (self.posHighlight_selectedPos == None): self.__klineDrawer_RemoveDrawings(analysisCode = 'IVP', gRemovalSignal = 0b01)
            else:
                if (self.posHighlight_selectedPos in self.klines['IVP']): 
                    if (self.posHighlight_selectedPos in self.klines_drawQueue): 
                        if ('IVP' in self.klines_drawQueue[self.posHighlight_selectedPos]): 
                            if (self.klines_drawQueue[self.posHighlight_selectedPos]['IVP'] != None): self.klines_drawQueue[self.posHighlight_selectedPos]['IVP'] |= 0b01
                        else:                                                                         self.klines_drawQueue[self.posHighlight_selectedPos]['IVP'] = 0b01
                    else:                                                                             self.klines_drawQueue[self.posHighlight_selectedPos] = {'IVP': 0b01}
        #PIP Update
        if ('PIP' in self.analysisParams):
            if (self.posHighlight_selectedPos == None): self.__klineDrawer_RemoveDrawings(analysisCode = 'PIP', gRemovalSignal = 0b0001)
            else:
                if (self.posHighlight_selectedPos in self.klines['PIP']):
                    if (self.posHighlight_selectedPos in self.klines_drawQueue): 
                        if ('PIP' in self.klines_drawQueue[self.posHighlight_selectedPos]): 
                            if (self.klines_drawQueue[self.posHighlight_selectedPos]['PIP'] != None): self.klines_drawQueue[self.posHighlight_selectedPos]['PIP'] |= 0b0001
                        else:                                                                         self.klines_drawQueue[self.posHighlight_selectedPos]['PIP'] = 0b0001
                    else:                                                                             self.klines_drawQueue[self.posHighlight_selectedPos] = {'PIP': 0b0001}

    def handleKeyEvent(self, event):
        if (self.hidden == False):
            if (self.mouse_lastSelectedSection == 'SETTINGSSUBPAGE'): self.settingsSubPages[self.settingsSubPage_Current].handleKeyEvent(event)
    #User Interaction Control END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Basic Object Control -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def show(self):
        self.hidden = False
        for displayBoxName in self.frameSprites: 
            self.frameSprites[displayBoxName].visible = True
            if (displayBoxName == 'MAINGRID_TEMPORAL'):
                self.displayBox_graphics[displayBoxName]['VERTICALGRID_CAMGROUP'].visible = True
            elif (displayBoxName == 'KLINESPRICE'):
                self.displayBox_graphics[displayBoxName]['HORIZONTALGRID_CAMGROUP'].visible = True
                self.displayBox_graphics[displayBoxName]['VERTICALGRID_CAMGROUP'].visible = True
                self.displayBox_graphics[displayBoxName]['ANALYSISDISPLAY_CAMGROUP'].visible = True
                self.displayBox_graphics[displayBoxName]['RCLCG'].show()
                self.displayBox_graphics[displayBoxName]['RCLCG_XFIXED'].show()
                self.displayBox_graphics[displayBoxName]['RCLCG_YFIXED'].show()
                self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].show()
                self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT2'].show()
                self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT3'].show()
            elif (displayBoxName == 'MAINGRID_KLINESPRICE'):
                self.displayBox_graphics[displayBoxName]['HORIZONTALGRID_CAMGROUP'].visible = True
            elif (displayBoxName[:8] == 'SIVIEWER'):
                siViewerNumber = int(displayBoxName[8])
                if (self.objectConfig['SIVIEWER{:d}Display'.format(siViewerNumber)] == True):
                    self.displayBox_graphics[displayBoxName]['HORIZONTALGRID_CAMGROUP'].visible = True
                    self.displayBox_graphics[displayBoxName]['VERTICALGRID_CAMGROUP'].visible = True
                    self.displayBox_graphics[displayBoxName]['RCLCG'].show()
                    self.displayBox_graphics[displayBoxName]['RCLCG_XFIXED'].show()
                    self.displayBox_graphics[displayBoxName]['RCLCG_YFIXED'].show()
                    self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].show()
            elif (displayBoxName[:17] == 'MAINGRID_SIVIEWER'):
                siViewerNumber = int(displayBoxName[17])
                if (self.objectConfig['SIVIEWER{:d}Display'.format(siViewerNumber)] == True): self.displayBox_graphics[displayBoxName]['HORIZONTALGRID_CAMGROUP'].visible = True
        if (self.settingsSubPage_Opened == True): self.settingsSubPages[self.settingsSubPage_Current].show()
        if (((self.klines_fetchComplete == False) and (self.klines_fetching == True)) or ((self.chartDrawerType == 'TLVIEWER') and (0 < len(self.analysisQueue_list)))):
            self.frameSprites['KLINELOADINGCOVER'].visible = True
            self.klinesLoadingGaugeBar.show()
            self.klinesLoadingTextBox.show()
            self.klinesLoadingTextBox_perc.show()
        else:
            self.frameSprites['KLINELOADINGCOVER'].visible = False
            self.klinesLoadingGaugeBar.hide()
            self.klinesLoadingTextBox.hide()
            self.klinesLoadingTextBox_perc.hide()

    def hide(self):
        self.hidden = True
        for displayBoxName in self.frameSprites: 
            self.frameSprites[displayBoxName].visible = False
            if (displayBoxName == 'MAINGRID_TEMPORAL'):
                self.displayBox_graphics[displayBoxName]['VERTICALGRID_CAMGROUP'].visible = False
            elif (displayBoxName == 'KLINESPRICE'):
                self.displayBox_graphics[displayBoxName]['HORIZONTALGRID_CAMGROUP'].visible = False
                self.displayBox_graphics[displayBoxName]['VERTICALGRID_CAMGROUP'].visible = False
                self.displayBox_graphics[displayBoxName]['ANALYSISDISPLAY_CAMGROUP'].visible = False
                self.displayBox_graphics[displayBoxName]['RCLCG'].hide()
                self.displayBox_graphics[displayBoxName]['RCLCG_XFIXED'].hide()
                self.displayBox_graphics[displayBoxName]['RCLCG_YFIXED'].hide()
                self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].hide()
                self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT2'].hide()
                self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT3'].hide()
            elif (displayBoxName == 'MAINGRID_KLINESPRICE'):
                self.displayBox_graphics[displayBoxName]['HORIZONTALGRID_CAMGROUP'].visible = False
            elif (displayBoxName[:8] == 'SIVIEWER'):
                self.displayBox_graphics[displayBoxName]['HORIZONTALGRID_CAMGROUP'].visible = False
                self.displayBox_graphics[displayBoxName]['VERTICALGRID_CAMGROUP'].visible = False
                self.displayBox_graphics[displayBoxName]['RCLCG'].hide()
                self.displayBox_graphics[displayBoxName]['RCLCG_XFIXED'].hide()
                self.displayBox_graphics[displayBoxName]['RCLCG_YFIXED'].hide()
                self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].hide()
            elif (displayBoxName[:17] == 'MAINGRID_SIVIEWER'):
                self.displayBox_graphics[displayBoxName]['HORIZONTALGRID_CAMGROUP'].visible = False
        self.settingsSubPages[self.settingsSubPage_Current].hide()
        self.frameSprites['KLINELOADINGCOVER'].visible = False
        self.klinesLoadingGaugeBar.hide()
        self.klinesLoadingTextBox.hide()
        self.klinesLoadingTextBox_perc.hide()

    def isHidden(self): 
        return self.hidden
        
    def moveTo(self, x, y):
        dx = x - self.xPos; dy = y - self.yPos
        self.xPos = x; self.yPos = y
        for displayBoxName in self.displayBox:
            if (self.displayBox[displayBoxName] != None):
                self.displayBox[displayBoxName] = (self.displayBox[displayBoxName][0]+dx, self.displayBox[displayBoxName][1]+dy, self.displayBox[displayBoxName][2], self.displayBox[displayBoxName][3])
                if (displayBoxName == 'SETTINGSBUTTONFRAME'):
                    self.hitBox['SETTINGSBUTTONFRAME'].reposition(xPos = self.displayBox['SETTINGSBUTTONFRAME'][0], yPos = self.displayBox['SETTINGSBUTTONFRAME'][1])
                    self.frameSprites['SETTINGSBUTTONFRAME'].position = (self.displayBox['SETTINGSBUTTONFRAME'][0]*self.scaler, self.displayBox['SETTINGSBUTTONFRAME'][1]*self.scaler, self.frameSprites['SETTINGSBUTTONFRAME'].z)
                    self.frameSprites['SETTINGSBUTTONFRAME_ICON'].position = ((self.displayBox['SETTINGSBUTTONFRAME'][0]+self.displayBox['SETTINGSBUTTONFRAME'][2]/2)*self.scaler-self.images['SETTINGSBUTTONFRAME_ICON'].width/2,
                                                                              (self.displayBox['SETTINGSBUTTONFRAME'][1]+self.displayBox['SETTINGSBUTTONFRAME'][3]/2)*self.scaler-self.images['SETTINGSBUTTONFRAME_ICON'].height/2,
                                                                              self.frameSprites['SETTINGSBUTTONFRAME_ICON'].z)
                else:
                    self.hitBox[displayBoxName].reposition(xPos = self.displayBox[displayBoxName][0]+_GD_DISPLAYBOX_GOFFSET, yPos = self.displayBox[displayBoxName][1]+_GD_DISPLAYBOX_GOFFSET)
                    self.frameSprites[displayBoxName].position = (self.displayBox[displayBoxName][0]*self.scaler, self.displayBox[displayBoxName][1]*self.scaler, self.frameSprites[displayBoxName].z)
        for settingsSubPageName in self.settingsSubPages: self.settingsSubPages[settingsSubPageName].moveTo(x = self.xPos+50, y = self.yPos+50)
        self.hitBox_Object.reposition(xPos = self.xPos, yPos = self.yPos)

    def resize(self, width, height):
        self.width = width; self.height = height
        #Set SubIndicator Switch Activation
        self.usableSIViewers = min([int((self.height-_GD_OBJECT_MINHEIGHT-(_GD_DISPLAYBOX_AUXILLARYBAR_HEIGHT+_GD_DISPLAYBOX_GOFFSET))/(_GD_DISPLAYBOX_SIVIEWER_HEIGHT+_GD_DISPLAYBOX_GOFFSET)), len(_SITYPES)])
        for siViewerIndex in range (len(_SITYPES)):
            if (siViewerIndex < self.usableSIViewers):
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_SHOW{:d}".format(siViewerIndex+1)].activate()
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_SELECTION{:d}".format(siViewerIndex+1)].activate()
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_SHOW{:d}".format(siViewerIndex+1)].setStatus(self.objectConfig['SI{:d}Display'.format(siViewerIndex+1)] == True)
            else:
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_SHOW{:d}".format(siViewerIndex+1)].deactivate()
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_SELECTION{:d}".format(siViewerIndex+1)].deactivate()
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_SHOW{:d}".format(siViewerIndex+1)].setStatus(False)
        self.__setDisplayBoxDimensions()
        for settingsSubPageName in self.settingsSubPages: self.settingsSubPages[settingsSubPageName].resize(width = 3700, height = self.height-100)
        self.hitBox_Object.resize(width = self.width, height = self.height)

    def isTouched(self, mouseX, mouseY):
        if (self.hidden == False): return self.hitBox_Object.isTouched(mouseX, mouseY)
        else: return False

    def setName(self, name): 
        self.name = name

    def getName(self): 
        return self.name

    def on_GUIThemeUpdate(self, **kwargs):
        #Bring in updated textStyle and colors
        self.currentGUITheme = self.visualManager.getGUITheme()

        newEffectiveTextStyle = self.visualManager.getTextStyle('chartDrawer_'+self.textStyle)
        for styleTarget in newEffectiveTextStyle: newEffectiveTextStyle[styleTarget]['font_size'] = self.effectiveTextStyle[styleTarget]['font_size']
        self.effectiveTextStyle = newEffectiveTextStyle
        
        self.gridColor                  = self.visualManager.getFromColorTable('CHARTDRAWER_GRID')
        self.gridColor_Heavy            = self.visualManager.getFromColorTable('CHARTDRAWER_GRIDHEAVY')
        self.guideColor                 = self.visualManager.getFromColorTable('CHARTDRAWER_GUIDECONTENT')
        self.posHighlightColor_hovered  = self.visualManager.getFromColorTable('CHARTDRAWER_POSHOVERED')
        self.posHighlightColor_selected = self.visualManager.getFromColorTable('CHARTDRAWER_POSSELECTED')

        #Object Image Update
        for displayBoxName in self.displayBox:
            if (self.displayBox[displayBoxName] != None):
                if (displayBoxName == 'SETTINGSBUTTONFRAME'):
                    self.images['SETTINGSBUTTONFRAME_DEFAULT'] = self.imageManager.getImageByLoadIndex(self.images['SETTINGSBUTTONFRAME_DEFAULT'][1])
                    self.images['SETTINGSBUTTONFRAME_HOVERED'] = self.imageManager.getImageByLoadIndex(self.images['SETTINGSBUTTONFRAME_HOVERED'][1])
                    self.images['SETTINGSBUTTONFRAME_PRESSED'] = self.imageManager.getImageByLoadIndex(self.images['SETTINGSBUTTONFRAME_PRESSED'][1])
                    iconColoring = self.visualManager.getFromColorTable('ICON_COLORING')
                    self.frameSprites[displayBoxName].image = self.images['SETTINGSBUTTONFRAME_'+self.settingsButtonStatus][0]
                    self.frameSprites['SETTINGSBUTTONFRAME_ICON'].color = (iconColoring[0], iconColoring[1], iconColoring[2]); self.frameSprites['SETTINGSBUTTONFRAME'+'_ICON'].opacity = iconColoring[3]
                else:
                    self.images[displayBoxName] = self.imageManager.getImageByLoadIndex(self.images[displayBoxName][1])
                    self.frameSprites[displayBoxName].image = self.images[displayBoxName][0]
                    
        #Grid and Guide Lines & Text Update
        for displayBoxName in self.displayBox:
            if (displayBoxName == 'KLINESPRICE'):
                self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT1'].on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle)
                self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2'].on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle)
                self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT3'].on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle)

                self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_HOVERED'].color  = self.posHighlightColor_hovered
                self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_SELECTED'].color = self.posHighlightColor_selected
                self.displayBox_graphics['KLINESPRICE']['HORIZONTALGUIDELINE'].color = self.guideColor
                self.displayBox_graphics['KLINESPRICE']['HORIZONTALGUIDETEXT'].on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['GUIDECONTENT'])

                for gridLineShape in self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_LINES']:          gridLineShape.color = self.gridColor
                for gridLineShape in self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_LINES']:            gridLineShape.color = self.gridColor
                for gridLineShape in self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_LINES']: gridLineShape.color = self.gridColor
                for gridLineText  in self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_TEXTS']: gridLineText.on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['GRID'])

            elif ((displayBoxName[:8] == 'SIVIEWER')):
                siIndex = int(displayBoxName[8:])
                dBoxName          = 'SIVIEWER{:d}'.format(siIndex)
                dBoxName_MAINGRID = 'MAINGRID_SIVIEWER{:d}'.format(siIndex)

                self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT1'].on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle)
                self.displayBox_graphics[dBoxName]['POSHIGHLIGHT_HOVERED'].color  = self.posHighlightColor_hovered
                self.displayBox_graphics[dBoxName]['POSHIGHLIGHT_SELECTED'].color = self.posHighlightColor_selected
                self.displayBox_graphics[dBoxName]['HORIZONTALGUIDELINE'].color = self.guideColor
                self.displayBox_graphics[dBoxName]['HORIZONTALGUIDETEXT'].on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['GUIDECONTENT'])

                for gridLineShape in self.displayBox_graphics[dBoxName]['HORIZONTALGRID_LINES']:          gridLineShape.color = self.gridColor
                for gridLineShape in self.displayBox_graphics[dBoxName]['VERTICALGRID_LINES']:            gridLineShape.color = self.gridColor
                for gridLineShape in self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_LINES']: gridLineShape.color = self.gridColor
                for gridLineText  in self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_TEXTS']: gridLineText.on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['GRID'])

            elif (displayBoxName == 'MAINGRID_TEMPORAL'):
                for gridLineShape in self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_LINES']: gridLineShape.color = self.gridColor
                for gridLineText  in self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS']: gridLineText.on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['GRID'])
        
        #Klines Loading GaugeBar Related
        self.images['KLINELOADINGCOVER'] = self.imageManager.getImageByLoadIndex(self.images['KLINELOADINGCOVER'][1])
        self.frameSprites['KLINELOADINGCOVER'].image = self.images['KLINELOADINGCOVER'][0]
        self.klinesLoadingGaugeBar.on_GUIThemeUpdate(**kwargs)
        self.klinesLoadingTextBox_perc.on_GUIThemeUpdate(**kwargs)
        self.klinesLoadingTextBox.on_GUIThemeUpdate(**kwargs)

        #Update Settings Subpages
        for subPageInstance in self.settingsSubPages.values(): subPageInstance.on_GUIThemeUpdate(**kwargs)
        
        #Update Configuration Objects Color
        if (True): #<--- Placed simply for a better readability
            #<TRADELOG>
            self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_BUY_LED"].updateColor(self.objectConfig['TRADELOG_BUY_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                                     self.objectConfig['TRADELOG_BUY_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                                     self.objectConfig['TRADELOG_BUY_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                                     self.objectConfig['TRADELOG_BUY_ColorA%{:s}'.format(self.currentGUITheme)])
            self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_SELL_LED"].updateColor(self.objectConfig['TRADELOG_SELL_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                                      self.objectConfig['TRADELOG_SELL_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                                      self.objectConfig['TRADELOG_SELL_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                                      self.objectConfig['TRADELOG_SELL_ColorA%{:s}'.format(self.currentGUITheme)])
            self.__onSettingsContentUpdate(self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_TARGETSELECTION"])
            #<BIDS AND ASKS>
            self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_BIDS_LED"].updateColor(self.objectConfig['BIDSANDASKS_BIDS_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                                         self.objectConfig['BIDSANDASKS_BIDS_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                                         self.objectConfig['BIDSANDASKS_BIDS_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                                         self.objectConfig['BIDSANDASKS_BIDS_ColorA%{:s}'.format(self.currentGUITheme)])
            self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_ASKS_LED"].updateColor(self.objectConfig['BIDSANDASKS_ASKS_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                                         self.objectConfig['BIDSANDASKS_ASKS_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                                         self.objectConfig['BIDSANDASKS_ASKS_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                                         self.objectConfig['BIDSANDASKS_ASKS_ColorA%{:s}'.format(self.currentGUITheme)])
            self.__onSettingsContentUpdate(self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_TARGETSELECTION"])
            #<MAs>
            for miType in ('SMA','WMA','EMA'):
                for lineIndex in range (_NMAXLINES[miType]):
                    lineNumber = lineIndex+1
                    self.settingsSubPages[miType].GUIOs["INDICATOR_{:s}{:d}_LINECOLOR".format(miType,lineNumber)].updateColor(self.objectConfig['{:s}_{:d}_ColorR%{:s}'.format(miType,lineNumber,self.currentGUITheme)], 
                                                                                                                              self.objectConfig['{:s}_{:d}_ColorG%{:s}'.format(miType,lineNumber,self.currentGUITheme)], 
                                                                                                                              self.objectConfig['{:s}_{:d}_ColorB%{:s}'.format(miType,lineNumber,self.currentGUITheme)], 
                                                                                                                              self.objectConfig['{:s}_{:d}_ColorA%{:s}'.format(miType,lineNumber,self.currentGUITheme)])
                self.__onSettingsContentUpdate(self.settingsSubPages[miType].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<PSAR>
            for lineIndex in range (_NMAXLINES['PSAR']):
                lineNumber = lineIndex+1
                self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_LINECOLOR".format(lineNumber)].updateColor(self.objectConfig['PSAR_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                   self.objectConfig['PSAR_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                   self.objectConfig['PSAR_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                   self.objectConfig['PSAR_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)])
            self.__onSettingsContentUpdate(self.settingsSubPages['PSAR'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<BOL>
            for lineIndex in range (_NMAXLINES['BOL']):
                lineNumber = lineIndex+1
                self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_LINECOLOR".format(lineNumber)].updateColor(self.objectConfig['BOL_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['BOL_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['BOL_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['BOL_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)])
            self.__onSettingsContentUpdate(self.settingsSubPages['BOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<IVP>
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_VPLP_COLOR"].updateColor(self.objectConfig['IVP_VPLP_ColorR%{:s}'.format(self.currentGUITheme)],
                                                                                   self.objectConfig['IVP_VPLP_ColorG%{:s}'.format(self.currentGUITheme)],
                                                                                   self.objectConfig['IVP_VPLP_ColorB%{:s}'.format(self.currentGUITheme)],
                                                                                   self.objectConfig['IVP_VPLP_ColorA%{:s}'.format(self.currentGUITheme)])
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_VPLPB_COLOR"].updateColor(self.objectConfig['IVP_VPLPB_ColorR%{:s}'.format(self.currentGUITheme)],
                                                                                    self.objectConfig['IVP_VPLPB_ColorG%{:s}'.format(self.currentGUITheme)],
                                                                                    self.objectConfig['IVP_VPLPB_ColorB%{:s}'.format(self.currentGUITheme)],
                                                                                    self.objectConfig['IVP_VPLPB_ColorA%{:s}'.format(self.currentGUITheme)])
            self.__onSettingsContentUpdate(self.settingsSubPages['IVP'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<PIP>
            for _line in ('SWING', 'NNASIGNAL+', 'NNASIGNAL-', 'WOISIGNAL+', 'WOISIGNAL-', 'NESSIGNAL+', 'NESSIGNAL-', 'CLASSICALSIGNAL+', 'CLASSICALSIGNAL-'):
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_{:s}_COLOR".format(_line)].updateColor(self.objectConfig['PIP_{:s}_ColorR%{:s}'.format(_line, self.currentGUITheme)],
                                                                                                     self.objectConfig['PIP_{:s}_ColorG%{:s}'.format(_line, self.currentGUITheme)],
                                                                                                     self.objectConfig['PIP_{:s}_ColorB%{:s}'.format(_line, self.currentGUITheme)],
                                                                                                     self.objectConfig['PIP_{:s}_ColorA%{:s}'.format(_line, self.currentGUITheme)])
            self.__onSettingsContentUpdate(self.settingsSubPages['PIP'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<VOL>
            for lineIndex in range (_NMAXLINES['VOL']):
                lineNumber = lineIndex+1
                self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_LINECOLOR".format(lineNumber)].updateColor(self.objectConfig['VOL_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['VOL_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['VOL_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['VOL_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)])
            self.__onSettingsContentUpdate(self.settingsSubPages['VOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<MMACDSHORT>
            for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM+', 'HISTOGRAM-'):
                self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_{:s}_COLOR".format(targetLine)].updateColor(self.objectConfig['MMACDSHORT_{:s}_ColorR%{:s}'.format(targetLine,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['MMACDSHORT_{:s}_ColorG%{:s}'.format(targetLine,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['MMACDSHORT_{:s}_ColorB%{:s}'.format(targetLine,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['MMACDSHORT_{:s}_ColorA%{:s}'.format(targetLine,self.currentGUITheme)])
            self.__onSettingsContentUpdate(self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<MMACDLONG>
            for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM+', 'HISTOGRAM-'):
                self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_{:s}_COLOR".format(targetLine)].updateColor(self.objectConfig['MMACDLONG_{:s}_ColorR%{:s}'.format(targetLine,self.currentGUITheme)], 
                                                                                                                self.objectConfig['MMACDLONG_{:s}_ColorG%{:s}'.format(targetLine,self.currentGUITheme)], 
                                                                                                                self.objectConfig['MMACDLONG_{:s}_ColorB%{:s}'.format(targetLine,self.currentGUITheme)], 
                                                                                                                self.objectConfig['MMACDLONG_{:s}_ColorA%{:s}'.format(targetLine,self.currentGUITheme)])
            self.__onSettingsContentUpdate(self.settingsSubPages['MMACDLONG'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<DMIxADX>
            for lineIndex in range (_NMAXLINES['DMIxADX']):
                lineNumber = lineIndex+1
                self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_LINECOLOR".format(lineNumber)].updateColor(self.objectConfig['DMIxADX_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                         self.objectConfig['DMIxADX_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                         self.objectConfig['DMIxADX_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                         self.objectConfig['DMIxADX_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)])
            self.__onSettingsContentUpdate(self.settingsSubPages['DMIxADX'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<MFI>
            for lineIndex in range (_NMAXLINES['MFI']):
                lineNumber = lineIndex+1
                self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_LINECOLOR".format(lineNumber)].updateColor(self.objectConfig['MFI_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['MFI_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['MFI_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                                                                                                 self.objectConfig['MFI_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)])
            self.__onSettingsContentUpdate(self.settingsSubPages['MFI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<WOI>
            for _line in ('BASE+', 'BASE-'):
                self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:s}_LINECOLOR".format(_line)].updateColor(self.objectConfig['WOI_{:s}_ColorR%{:s}'.format(_line,self.currentGUITheme)], 
                                                                                                            self.objectConfig['WOI_{:s}_ColorG%{:s}'.format(_line,self.currentGUITheme)], 
                                                                                                            self.objectConfig['WOI_{:s}_ColorB%{:s}'.format(_line,self.currentGUITheme)], 
                                                                                                            self.objectConfig['WOI_{:s}_ColorA%{:s}'.format(_line,self.currentGUITheme)])
            for _lineIndex in range (_NMAXLINES['WOI']):
                _lineNumber = _lineIndex+1
                self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_LINECOLOR".format(_lineNumber)].updateColor(self.objectConfig['WOI_{:d}_ColorR%{:s}'.format(_lineNumber,self.currentGUITheme)], 
                                                                                                                  self.objectConfig['WOI_{:d}_ColorG%{:s}'.format(_lineNumber,self.currentGUITheme)], 
                                                                                                                  self.objectConfig['WOI_{:d}_ColorB%{:s}'.format(_lineNumber,self.currentGUITheme)], 
                                                                                                                  self.objectConfig['WOI_{:d}_ColorA%{:s}'.format(_lineNumber,self.currentGUITheme)])
            self.__onSettingsContentUpdate(self.settingsSubPages['WOI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<NES>
            for _line in ('BASE+', 'BASE-'):
                self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:s}_LINECOLOR".format(_line)].updateColor(self.objectConfig['NES_{:s}_ColorR%{:s}'.format(_line,self.currentGUITheme)], 
                                                                                                            self.objectConfig['NES_{:s}_ColorG%{:s}'.format(_line,self.currentGUITheme)], 
                                                                                                            self.objectConfig['NES_{:s}_ColorB%{:s}'.format(_line,self.currentGUITheme)], 
                                                                                                            self.objectConfig['NES_{:s}_ColorA%{:s}'.format(_line,self.currentGUITheme)])
            for _lineIndex in range (_NMAXLINES['NES']):
                _lineNumber = _lineIndex+1
                self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_LINECOLOR".format(_lineNumber)].updateColor(self.objectConfig['NES_{:d}_ColorR%{:s}'.format(_lineNumber,self.currentGUITheme)], 
                                                                                                                  self.objectConfig['NES_{:d}_ColorG%{:s}'.format(_lineNumber,self.currentGUITheme)], 
                                                                                                                  self.objectConfig['NES_{:d}_ColorB%{:s}'.format(_lineNumber,self.currentGUITheme)], 
                                                                                                                  self.objectConfig['NES_{:d}_ColorA%{:s}'.format(_lineNumber,self.currentGUITheme)])
            self.__onSettingsContentUpdate(self.settingsSubPages['NES'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])

        #Register redraw queues
        for _ts in self.klines_drawn:
            for _aCode in self.klines_drawn[_ts]: self.__klineDrawer_sendDrawSignals(timestamp = _ts, analysisCode = _aCode, redraw = True)

    def on_LanguageUpdate(self, **kwargs):
        #Bring in updated textStyle
        newEffectiveTextStyle = self.visualManager.getTextStyle('chartDrawer_'+self.textStyle)
        for styleTarget in newEffectiveTextStyle: newEffectiveTextStyle[styleTarget]['font_size'] = self.effectiveTextStyle[styleTarget]['font_size']
        self.effectiveTextStyle = newEffectiveTextStyle
        
        #Grid and Guide Lines & Text Update
        for displayBoxName in self.displayBox:
            if (displayBoxName == 'KLINESPRICE'):
                self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT1'].on_LanguageUpdate(**kwargs)
                self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2'].on_LanguageUpdate(**kwargs)
                self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT3'].on_LanguageUpdate(**kwargs)
                self.displayBox_graphics['KLINESPRICE']['HORIZONTALGUIDETEXT'].on_LanguageUpdate(**kwargs)
                for gridLineText in self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_TEXTS']: gridLineText.on_LanguageUpdate(**kwargs)

            elif ((displayBoxName[:8] == 'SIVIEWER') and (displayBoxName in self.displayBox_graphics_visibleSIViewers)):
                siIndex = int(displayBoxName[8:])
                dBoxName          = 'SIVIEWER{:d}'.format(siIndex)
                dBoxName_MAINGRID = 'MAINGRID_SIVIEWER{:d}'.format(siIndex)
                self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT1'].on_LanguageUpdate(**kwargs)
                self.displayBox_graphics[dBoxName]['HORIZONTALGUIDETEXT'].on_LanguageUpdate(**kwargs)
                for gridLineText in self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_TEXTS']: gridLineText.on_LanguageUpdate(**kwargs)

            elif (displayBoxName == 'MAINGRID_TEMPORAL'):
                for gridLineText  in self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS']: gridLineText.on_LanguageUpdate(**kwargs)

        #Klines Loading GaugeBar Related
        self.klinesLoadingTextBox_perc.on_LanguageUpdate(**kwargs)
        self.klinesLoadingTextBox.on_LanguageUpdate(**kwargs)

        #Update Settings Subpages
        for subPageInstance in self.settingsSubPages.values(): subPageInstance.on_LanguageUpdate(**kwargs)
    #Basic Object Control END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Configuration Update Control -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __onSettingsButtonClick(self):
        #Close the settings subpage
        if (self.settingsSubPage_Opened == True): 
            self.settingsSubPages[self.settingsSubPage_Current].hide()
            self.settingsSubPage_Opened = False
        #Open the settings subpage
        else: 
            self.settingsSubPages[self.settingsSubPage_Current].show()
            self.settingsSubPage_Opened = True
            if ((self.chartDrawerType == 'CAVIEWER') or (self.chartDrawerType == 'TLVIEWER')):
                if (self.settingsSubPage_Current == 'PIP'):
                    self.settingsSubPages['PIP'].GUIOs["INDICATOR_NEURALNETWORKCODE_SELECTIONBOX"].hide()
                    self.settingsSubPages['PIP'].GUIOs["INDICATOR_NEURALNETWORKCODE_RELEASEBUTTON"].hide()
                    self.settingsSubPages['PIP'].GUIOs["INDICATOR_NEURALNETWORKCODE_VALUETEXT"].show()
            elif (self.chartDrawerType == 'ANALYZER'):
                if (self.settingsSubPage_Current == 'PIP'):
                    self.settingsSubPages['PIP'].GUIOs["INDICATOR_NEURALNETWORKCODE_SELECTIONBOX"].show()
                    self.settingsSubPages['PIP'].GUIOs["INDICATOR_NEURALNETWORKCODE_RELEASEBUTTON"].show()
                    self.settingsSubPages['PIP'].GUIOs["INDICATOR_NEURALNETWORKCODE_VALUETEXT"].hide()

    def __onSettingsNavButtonClick(self, objectInstance):
        buttonName = objectInstance.getName()
        previousSubPage = self.settingsSubPage_Current
        if   (buttonName == 'navButton_MI_SMA'):        self.settingsSubPage_Current = 'SMA'
        elif (buttonName == 'navButton_MI_WMA'):        self.settingsSubPage_Current = 'WMA'
        elif (buttonName == 'navButton_MI_EMA'):        self.settingsSubPage_Current = 'EMA'
        elif (buttonName == 'navButton_MI_BOL'):        self.settingsSubPage_Current = 'BOL'
        elif (buttonName == 'navButton_MI_PSAR'):       self.settingsSubPage_Current = 'PSAR'
        elif (buttonName == 'navButton_MI_IVP'):        self.settingsSubPage_Current = 'IVP'
        elif (buttonName == 'navButton_MI_PIP'):        self.settingsSubPage_Current = 'PIP'
        elif (buttonName == 'navButton_SI_VOL'):        self.settingsSubPage_Current = 'VOL'
        elif (buttonName == 'navButton_SI_MMACDSHORT'): self.settingsSubPage_Current = 'MMACDSHORT'
        elif (buttonName == 'navButton_SI_MMACDLONG'):  self.settingsSubPage_Current = 'MMACDLONG'
        elif (buttonName == 'navButton_SI_DMIxADX'):    self.settingsSubPage_Current = 'DMIxADX'
        elif (buttonName == 'navButton_SI_MFI'):        self.settingsSubPage_Current = 'MFI'
        elif (buttonName == 'navButton_SI_WOI'):        self.settingsSubPage_Current = 'WOI'
        elif (buttonName == 'navButton_SI_NES'):        self.settingsSubPage_Current = 'NES'
        elif (buttonName == 'navButton_toHome'):        self.settingsSubPage_Current = 'MAIN'
        self.settingsSubPages[previousSubPage].hide()
        self.settingsSubPages[self.settingsSubPage_Current].show()
        #Special Cases
        #---PIP Neural Networks
        if (self.settingsSubPage_Current == 'PIP'):
            _neuralNetworkCodesList = dict()
            for _nnCode in self.ipcA.getPRD(processName = 'NEURALNETWORKMANAGER', prdAddress = 'NEURALNETWORKS'): _neuralNetworkCodesList[_nnCode] = {'text': _nnCode, 'textAnchor': 'W'}
            self.settingsSubPages['PIP'].GUIOs['INDICATOR_NEURALNETWORKCODE_SELECTIONBOX'].setSelectionList(selectionList = _neuralNetworkCodesList, keepSelected = True, displayTargets = 'all')
            if (self.objectConfig['PIP_NeuralNetworkCode'] in _neuralNetworkCodesList): self.settingsSubPages['PIP'].GUIOs["INDICATOR_NEURALNETWORKCODE_SELECTIONBOX"].setSelected(itemKey = self.objectConfig['PIP_NeuralNetworkCode'], callSelectionUpdateFunction = False)
            if ((self.chartDrawerType == 'CAVIEWER') or (self.chartDrawerType == 'TLVIEWER')):
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_NEURALNETWORKCODE_SELECTIONBOX"].hide()
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_NEURALNETWORKCODE_RELEASEBUTTON"].hide()
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_NEURALNETWORKCODE_VALUETEXT"].show()
            elif (self.chartDrawerType == 'ANALYZER'):
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_NEURALNETWORKCODE_SELECTIONBOX"].show()
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_NEURALNETWORKCODE_RELEASEBUTTON"].show()
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_NEURALNETWORKCODE_VALUETEXT"].hide()
        
    def __onSettingsContentUpdate(self, objectInstnace):
        guioName = objectInstnace.getName()
        guioName_split = guioName.split("_")
        indicatorType = guioName_split[0]
        activateSaveConfigButton = False

        #Subpage 'MAIN'
        if (indicatorType == 'MAIN'):
            setterType = guioName_split[1]
            if (setterType == 'KLINECOLORTYPE'): 
                selectedColorType = self.settingsSubPages['MAIN'].GUIOs['AUX_KLINECOLORTYPE_SELECTIONBOX'].getSelected()
                self.updateKlineColors(newType = selectedColorType)
                activateSaveConfigButton = True
            elif (setterType == 'TIMEZONE'):       
                selectedTimeZone = self.settingsSubPages['MAIN'].GUIOs['AUX_TIMEZONE_SELECTIONBOX'].getSelected()
                self.updateTimeZone(newTimeZone = selectedTimeZone)
                activateSaveConfigButton = True
            elif (setterType == 'SAVECONFIG'): 
                self.sysFunc_editGUIOConfig(configName = self.name, targetContent = self.objectConfig.copy()); self.settingsSubPages['MAIN'].GUIOs["AUX_SAVECONFIGURATION"].deactivate()
            elif (setterType == 'INDICATORSWITCH'):
                analysisType = guioName_split[2]
                self.__onSettingsContentUpdate(self.settingsSubPages[analysisType].GUIOs["APPLYNEWSETTINGS"])
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'SIVIEWERDISPLAYSWITCH'):
                #Set SIViewerDisplay
                siViewerNumber  = int(guioName_split[2])
                siViewerDisplay = self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_DISPLAYSWITCH{:d}".format(siViewerNumber)].getStatus()
                self.__setSIViewerDisplay(siViewerNumber = siViewerNumber, siViewerDisplay = siViewerDisplay)
                #Activate Configuration Save Button
                activateSaveConfigButton = True
            elif (setterType == 'SIVIEWERDISPLAYSELECTION'):
                #Set SIViewer Display Target and Retreive the Swapped SIViewerNumber
                siViewerNumber1        = int(guioName_split[2])
                siViewerDisplayTarget1 = self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_DISPLAYSELECTION{:d}".format(siViewerNumber1)].getSelected()
                siViewerNumber2        = self.__setSIViewerDisplayTarget(siViewerNumber1 = siViewerNumber1, siViewerDisplayTarget1 = siViewerDisplayTarget1)
                siViewerDisplayTarget2 = self.objectConfig['SIVIEWER{:d}SIAlloc'.format(siViewerNumber2)]
                #Update GUIO for the Swapped SIViewer
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_DISPLAYSELECTION{:d}".format(siViewerNumber2)].setSelected(siViewerDisplayTarget2, callSelectionUpdateFunction = False)
                #Activate Configuration Save Button
                activateSaveConfigButton = True
            elif (setterType == 'ANALYSISRANGETEXTINPUTBOX'):
                rangeBeg_str = self.settingsSubPages['MAIN'].GUIOs["ANALYZER_ANALYSISRANGEBEG_RANGEINPUT"].getText()
                rangeEnd_str = self.settingsSubPages['MAIN'].GUIOs["ANALYZER_ANALYSISRANGEEND_RANGEINPUT"].getText()
                try:    rangeBeg = int(datetime.strptime(rangeBeg_str, "%Y/%m/%d %H:%M").timestamp()-time.timezone)
                except: rangeBeg = None
                try:    rangeEnd = int(datetime.strptime(rangeEnd_str, "%Y/%m/%d %H:%M").timestamp()-time.timezone)
                except: rangeEnd = None
                self.objectConfig['AnalysisRangeBeg'] = rangeBeg
                self.objectConfig['AnalysisRangeEnd'] = rangeEnd
                if (self.chartDrawerType == 'ANALYZER'): self.__Analyzer_checkIfCanPerformAnalysis()
                activateSaveConfigButton = True
            elif (setterType == 'STARTANALYSIS'):
                self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].deactivate()
                self.neuralNetworkConnectionDataRequestID = None
                self.neuralNetworkInstance                = None
                torch.cuda.empty_cache()
                if ((self.objectConfig['PIP_NeuralNetworkCode'] != None) and (self.objectConfig['PIP_NeuralNetworkCode'] in self.ipcA.getPRD(processName = 'NEURALNETWORKMANAGER', prdAddress = 'NEURALNETWORKS'))): self.__Analyzer_requestNeuralNetworkConnectionsData()
                else:                                                                                                                                                                                                self.__Analyzer_startAnalysis()
        #---Trade Log
        if (indicatorType == 'TRADELOG'):
            setterType = guioName_split[1]
            if (setterType == 'LineSelectionBox'):
                lineSelected = self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_{:s}_LED".format(lineSelected)].getColor()
                self.settingsSubPages['MAIN'].GUIOs['TRADELOGCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_R_VALUE"].updateText(str(color_r))
                self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_G_VALUE"].updateText(str(color_g))
                self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_B_VALUE"].updateText(str(color_b))
                self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_A_VALUE"].updateText(str(color_a))
                self.settingsSubPages['MAIN'].GUIOs['TRADELOGCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                self.settingsSubPages['MAIN'].GUIOs['TRADELOGCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                self.settingsSubPages['MAIN'].GUIOs['TRADELOGCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                self.settingsSubPages['MAIN'].GUIOs['TRADELOGCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                self.settingsSubPages['MAIN'].GUIOs['TRADELOGCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):
                contentType = guioName_split[2]
                self.settingsSubPages['MAIN'].GUIOs['TRADELOGCOLOR_LED'].updateColor(rValue = int(self.settingsSubPages['MAIN'].GUIOs['TRADELOGCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                                     gValue = int(self.settingsSubPages['MAIN'].GUIOs['TRADELOGCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                                     bValue = int(self.settingsSubPages['MAIN'].GUIOs['TRADELOGCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                                     aValue = int(self.settingsSubPages['MAIN'].GUIOs['TRADELOGCOLOR_A_SLIDER'].getSliderValue()*255/100))
                self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_{:s}_VALUE".format(contentType)].updateText(str(int(self.settingsSubPages['MAIN'].GUIOs['TRADELOGCOLOR_{:s}_SLIDER'.format(contentType)].getSliderValue()*255/100)))
                self.settingsSubPages['MAIN'].GUIOs['TRADELOGCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):
                lineSelected = self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(self.settingsSubPages['MAIN'].GUIOs['TRADELOGCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(self.settingsSubPages['MAIN'].GUIOs['TRADELOGCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(self.settingsSubPages['MAIN'].GUIOs['TRADELOGCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(self.settingsSubPages['MAIN'].GUIOs['TRADELOGCOLOR_A_SLIDER'].getSliderValue()*255/100)
                self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_{:s}_LED".format(lineSelected)].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['MAIN'].GUIOs['TRADELOGCOLOR_APPLYCOLOR'].deactivate()
                self.settingsSubPages['MAIN'].GUIOs["TRADELOG_APPLYNEWSETTINGS"].activate()
            elif (setterType == 'DisplaySwitch'):
                self.settingsSubPages['MAIN'].GUIOs["TRADELOG_APPLYNEWSETTINGS"].activate()
            elif (setterType == 'ApplySettings'):
                #UpdateTracker Initialization
                updateTracker = False
                #Check for any changes in the configuration
                if (True):
                    #Buy Color
                    buyColor_previous = (self.objectConfig['TRADELOG_BUY_ColorR%{:s}'.format(self.currentGUITheme)], 
                                         self.objectConfig['TRADELOG_BUY_ColorG%{:s}'.format(self.currentGUITheme)], 
                                         self.objectConfig['TRADELOG_BUY_ColorB%{:s}'.format(self.currentGUITheme)], 
                                         self.objectConfig['TRADELOG_BUY_ColorA%{:s}'.format(self.currentGUITheme)])
                    color_r, color_g, color_b, color_a = self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_BUY_LED"].getColor()
                    self.objectConfig['TRADELOG_BUY_ColorR%{:s}'.format(self.currentGUITheme)] = color_r
                    self.objectConfig['TRADELOG_BUY_ColorG%{:s}'.format(self.currentGUITheme)] = color_g
                    self.objectConfig['TRADELOG_BUY_ColorB%{:s}'.format(self.currentGUITheme)] = color_b
                    self.objectConfig['TRADELOG_BUY_ColorA%{:s}'.format(self.currentGUITheme)] = color_a
                    if (buyColor_previous != (color_r, color_g, color_b, color_a)): updateTracker = True
                    #Sell Color
                    sellColor_previous = (self.objectConfig['TRADELOG_SELL_ColorR%{:s}'.format(self.currentGUITheme)], 
                                          self.objectConfig['TRADELOG_SELL_ColorG%{:s}'.format(self.currentGUITheme)], 
                                          self.objectConfig['TRADELOG_SELL_ColorB%{:s}'.format(self.currentGUITheme)], 
                                          self.objectConfig['TRADELOG_SELL_ColorA%{:s}'.format(self.currentGUITheme)])
                    color_r, color_g, color_b, color_a = self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_SELL_LED"].getColor()
                    self.objectConfig['TRADELOG_SELL_ColorR%{:s}'.format(self.currentGUITheme)] = color_r
                    self.objectConfig['TRADELOG_SELL_ColorG%{:s}'.format(self.currentGUITheme)] = color_g
                    self.objectConfig['TRADELOG_SELL_ColorB%{:s}'.format(self.currentGUITheme)] = color_b
                    self.objectConfig['TRADELOG_SELL_ColorA%{:s}'.format(self.currentGUITheme)] = color_a
                    if (sellColor_previous != (color_r, color_g, color_b, color_a)): updateTracker = True
                    #Display
                    display_previous = self.objectConfig['TRADELOG_Display']
                    self.objectConfig['TRADELOG_Display'] = self.settingsSubPages['MAIN'].GUIOs["TRADELOGDISPLAY_SWITCH"].getStatus()
                    if (display_previous != self.objectConfig['TRADELOG_Display']): updateTracker = True
                #Queue Update
                if (updateTracker == True):
                    self.__klineDrawer_RemoveDrawings(analysisCode = 'TRADELOG', gRemovalSignal = _FULLDRAWSIGNALS['TRADELOG']) #Remove previous graphics
                    self.__addBufferZone_toDrawQueue(analysisCode = 'TRADELOG', drawSignal = _FULLDRAWSIGNALS['TRADELOG'])      #Update draw queue
                #Control Buttons Handling
                self.settingsSubPages['MAIN'].GUIOs["TRADELOG_APPLYNEWSETTINGS"].deactivate()
                activateSaveConfigButton = True
        #---Bids and Asks
        if (indicatorType == 'BIDSANDASKS'):
            setterType = guioName_split[1]
            if (setterType == 'LineSelectionBox'):
                lineSelected = self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_{:s}_LED".format(lineSelected)].getColor()
                self.settingsSubPages['MAIN'].GUIOs['BIDSANDASKSCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_R_VALUE"].updateText(str(color_r))
                self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_G_VALUE"].updateText(str(color_g))
                self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_B_VALUE"].updateText(str(color_b))
                self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_A_VALUE"].updateText(str(color_a))
                self.settingsSubPages['MAIN'].GUIOs['BIDSANDASKSCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                self.settingsSubPages['MAIN'].GUIOs['BIDSANDASKSCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                self.settingsSubPages['MAIN'].GUIOs['BIDSANDASKSCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                self.settingsSubPages['MAIN'].GUIOs['BIDSANDASKSCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                self.settingsSubPages['MAIN'].GUIOs['BIDSANDASKSCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):
                contentType = guioName_split[2]
                self.settingsSubPages['MAIN'].GUIOs['BIDSANDASKSCOLOR_LED'].updateColor(rValue = int(self.settingsSubPages['MAIN'].GUIOs['BIDSANDASKSCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                                        gValue = int(self.settingsSubPages['MAIN'].GUIOs['BIDSANDASKSCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                                        bValue = int(self.settingsSubPages['MAIN'].GUIOs['BIDSANDASKSCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                                        aValue = int(self.settingsSubPages['MAIN'].GUIOs['BIDSANDASKSCOLOR_A_SLIDER'].getSliderValue()*255/100))
                self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_{:s}_VALUE".format(contentType)].updateText(str(int(self.settingsSubPages['MAIN'].GUIOs['BIDSANDASKSCOLOR_{:s}_SLIDER'.format(contentType)].getSliderValue()*255/100)))
                self.settingsSubPages['MAIN'].GUIOs['BIDSANDASKSCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):
                lineSelected = self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(self.settingsSubPages['MAIN'].GUIOs['BIDSANDASKSCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(self.settingsSubPages['MAIN'].GUIOs['BIDSANDASKSCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(self.settingsSubPages['MAIN'].GUIOs['BIDSANDASKSCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(self.settingsSubPages['MAIN'].GUIOs['BIDSANDASKSCOLOR_A_SLIDER'].getSliderValue()*255/100)
                self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_{:s}_LED".format(lineSelected)].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['MAIN'].GUIOs['BIDSANDASKSCOLOR_APPLYCOLOR'].deactivate()
                self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKS_APPLYNEWSETTINGS"].activate()
            elif (setterType == 'DisplaySwitch'):
                self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKS_APPLYNEWSETTINGS"].activate()
            elif (setterType == 'ApplySettings'):
                #UpdateTracker Initialization
                updateTracker = False
                #Check for any changes in the configuration
                if (True):
                    #Bids Color
                    bidsColor_previous = (self.objectConfig['BIDSANDASKS_BIDS_ColorR%{:s}'.format(self.currentGUITheme)], 
                                          self.objectConfig['BIDSANDASKS_BIDS_ColorG%{:s}'.format(self.currentGUITheme)], 
                                          self.objectConfig['BIDSANDASKS_BIDS_ColorB%{:s}'.format(self.currentGUITheme)], 
                                          self.objectConfig['BIDSANDASKS_BIDS_ColorA%{:s}'.format(self.currentGUITheme)])
                    color_r, color_g, color_b, color_a = self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_BIDS_LED"].getColor()
                    self.objectConfig['BIDSANDASKS_BIDS_ColorR%{:s}'.format(self.currentGUITheme)] = color_r
                    self.objectConfig['BIDSANDASKS_BIDS_ColorG%{:s}'.format(self.currentGUITheme)] = color_g
                    self.objectConfig['BIDSANDASKS_BIDS_ColorB%{:s}'.format(self.currentGUITheme)] = color_b
                    self.objectConfig['BIDSANDASKS_BIDS_ColorA%{:s}'.format(self.currentGUITheme)] = color_a
                    if (bidsColor_previous != (color_r, color_g, color_b, color_a)): updateTracker = True
                    #Asks Color
                    asksColor_previous = (self.objectConfig['BIDSANDASKS_ASKS_ColorR%{:s}'.format(self.currentGUITheme)], 
                                          self.objectConfig['BIDSANDASKS_ASKS_ColorG%{:s}'.format(self.currentGUITheme)], 
                                          self.objectConfig['BIDSANDASKS_ASKS_ColorB%{:s}'.format(self.currentGUITheme)], 
                                          self.objectConfig['BIDSANDASKS_ASKS_ColorA%{:s}'.format(self.currentGUITheme)])
                    color_r, color_g, color_b, color_a = self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_ASKS_LED"].getColor()
                    self.objectConfig['BIDSANDASKS_ASKS_ColorR%{:s}'.format(self.currentGUITheme)] = color_r
                    self.objectConfig['BIDSANDASKS_ASKS_ColorG%{:s}'.format(self.currentGUITheme)] = color_g
                    self.objectConfig['BIDSANDASKS_ASKS_ColorB%{:s}'.format(self.currentGUITheme)] = color_b
                    self.objectConfig['BIDSANDASKS_ASKS_ColorA%{:s}'.format(self.currentGUITheme)] = color_a
                    if (asksColor_previous != (color_r, color_g, color_b, color_a)): updateTracker = True
                    #Display
                    display_previous = self.objectConfig['BIDSANDASKS_Display']
                    self.objectConfig['BIDSANDASKS_Display'] = self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSDISPLAY_SWITCH"].getStatus()
                    if (display_previous != self.objectConfig['BIDSANDASKS_Display']): updateTracker = True
                #Queue Update
                if (updateTracker == True): 
                    self.__bidsAndAsksDrawer_Remove()
                    self.__bidsAndAsksDrawer_Draw()
                #Control Buttons Handling
                self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKS_APPLYNEWSETTINGS"].deactivate()
                activateSaveConfigButton = True

        #Subpage 'SMA' 'WMA' 'EMA'
        elif ((indicatorType == 'SMA') or (indicatorType == 'WMA') or (indicatorType == 'EMA')):
            miType = indicatorType
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):    
                lineSelected = self.settingsSubPages[miType].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = self.settingsSubPages[miType].GUIOs["INDICATOR_{:s}{:s}_LINECOLOR".format(miType, lineSelected)].getColor()
                self.settingsSubPages[miType].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages[miType].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                self.settingsSubPages[miType].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                self.settingsSubPages[miType].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                self.settingsSubPages[miType].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                self.settingsSubPages[miType].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                self.settingsSubPages[miType].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                self.settingsSubPages[miType].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                self.settingsSubPages[miType].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                self.settingsSubPages[miType].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):             
                contentType = guioName_split[2]
                self.settingsSubPages[miType].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(self.settingsSubPages[miType].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                                      gValue = int(self.settingsSubPages[miType].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                                      bValue = int(self.settingsSubPages[miType].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                                      aValue = int(self.settingsSubPages[miType].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                self.settingsSubPages[miType].GUIOs["INDICATORCOLOR_{:s}_VALUE".format(contentType)].updateText(str(int(self.settingsSubPages[miType].GUIOs['INDICATORCOLOR_{:s}_SLIDER'.format(contentType)].getSliderValue()*255/100)))
                self.settingsSubPages[miType].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):        
                lineSelected = self.settingsSubPages[miType].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(self.settingsSubPages[miType].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(self.settingsSubPages[miType].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(self.settingsSubPages[miType].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(self.settingsSubPages[miType].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                self.settingsSubPages[miType].GUIOs["INDICATOR_{:s}{:s}_LINECOLOR".format(miType,lineSelected)].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages[miType].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                self.settingsSubPages[miType].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'WidthTextInputBox'): 
                self.settingsSubPages[miType].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):     
                self.settingsSubPages[miType].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):     
                #UpdateTracker Initialization
                updateTracker = dict()
                #Check for any changes in the configuration
                if (True):
                    for lineIndex in range (_NMAXLINES[miType]):
                        lineNumber = lineIndex+1
                        updateTracker[lineNumber] = False
                        #Width
                        width_previous = self.objectConfig['{:s}_{:d}_Width'.format(miType,lineNumber)]
                        reset = False
                        try:
                            width = int(self.settingsSubPages[miType].GUIOs["INDICATOR_{:s}{:d}_WIDTHINPUT".format(miType,lineNumber)].getText())
                            if (0 < width): self.objectConfig['{:s}_{:d}_Width'.format(miType,lineNumber)] = width
                            else: reset = True
                        except: reset = True
                        if (reset == True):
                            self.objectConfig['{:s}_{:d}_Width'.format(miType,lineNumber)] = 1
                            self.settingsSubPages[miType].GUIOs["INDICATOR_{:s}{:d}_WIDTHINPUT".format(miType,lineNumber)].updateText(str(self.objectConfig['{:s}_{:d}_Width'.format(miType,lineNumber)]))
                        if (width_previous != self.objectConfig['{:s}_{:d}_Width'.format(miType,lineNumber)]): updateTracker[lineNumber] = True
                        #Color
                        color_previous = (self.objectConfig['{:s}_{:d}_ColorR%{:s}'.format(miType,lineNumber,self.currentGUITheme)], 
                                          self.objectConfig['{:s}_{:d}_ColorG%{:s}'.format(miType,lineNumber,self.currentGUITheme)], 
                                          self.objectConfig['{:s}_{:d}_ColorB%{:s}'.format(miType,lineNumber,self.currentGUITheme)], 
                                          self.objectConfig['{:s}_{:d}_ColorA%{:s}'.format(miType,lineNumber,self.currentGUITheme)])
                        color_r, color_g, color_b, color_a = self.settingsSubPages[miType].GUIOs["INDICATOR_{:s}{:d}_LINECOLOR".format(miType,lineNumber)].getColor()
                        self.objectConfig['{:s}_{:d}_ColorR%{:s}'.format(miType,lineNumber,self.currentGUITheme)] = color_r
                        self.objectConfig['{:s}_{:d}_ColorG%{:s}'.format(miType,lineNumber,self.currentGUITheme)] = color_g
                        self.objectConfig['{:s}_{:d}_ColorB%{:s}'.format(miType,lineNumber,self.currentGUITheme)] = color_b
                        self.objectConfig['{:s}_{:d}_ColorA%{:s}'.format(miType,lineNumber,self.currentGUITheme)] = color_a
                        if (color_previous != (color_r, color_g, color_b, color_a)): updateTracker[lineNumber] = True
                        #Line Display
                        display_previous = self.objectConfig['{:s}_{:d}_Display'.format(miType,lineNumber)]
                        self.objectConfig['{:s}_{:d}_Display'.format(miType,lineNumber)] = self.settingsSubPages[miType].GUIOs["INDICATOR_{:s}{:d}_DISPLAY".format(miType,lineNumber)].getStatus()
                        if (display_previous != self.objectConfig['{:s}_{:d}_Display'.format(miType,lineNumber)]): updateTracker[lineNumber] = True
                    #MA Master
                    maMaster_previous = self.objectConfig['{:s}_Master'.format(miType)]
                    self.objectConfig['{:s}_Master'.format(miType)] = self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_{:s}".format(miType)].getStatus()
                    if (maMaster_previous != self.objectConfig['{:s}_Master'.format(miType)]):
                        for lineNumber in updateTracker: updateTracker[lineNumber] = True
                #Queue Update
                configuredMAs = set([analysisCode for analysisCode in self.analysisParams if analysisCode[:3] == miType])
                for configuredMA in configuredMAs:
                    lineNumber = self.analysisParams[configuredMA]['lineNumber']
                    if (updateTracker[lineNumber] == True):
                        self.__klineDrawer_RemoveDrawings(analysisCode = configuredMA, gRemovalSignal = _FULLDRAWSIGNALS[miType]) #Remove previous graphics
                        self.__addBufferZone_toDrawQueue(analysisCode = configuredMA, drawSignal = _FULLDRAWSIGNALS[miType])      #Update draw queue
                #Control Buttons Handling
                self.settingsSubPages[miType].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'): 
                lineNumber = int(guioName_split[2])
                #Get new switch status
                _newStatus = self.settingsSubPages[miType].GUIOs["INDICATOR_{:s}{:d}".format(miType,lineNumber)].getStatus()
                self.objectConfig['{:s}_{:d}_LineActive'.format(miType, lineNumber)] = _newStatus
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['{:s}_Master'.format(miType)] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'): 
                lineNumber = int(guioName_split[2])
                #Get new nSamples
                try:    _nSamples = int(self.settingsSubPages[miType].GUIOs["INDICATOR_{:s}{:d}_INTERVALINPUT".format(miType,lineNumber)].getText())
                except: _nSamples = None
                #Save the new value to the object config dictionary
                self.objectConfig['{:s}_{:d}_NSamples'.format(miType, lineNumber)] = _nSamples
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['{:s}_Master'.format(miType)] == True) and (self.objectConfig['{:s}_{:d}_LineActive'.format(miType, lineNumber)] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True

        #Subpage 'PSAR'
        elif (indicatorType == 'PSAR'):
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):    
                lineSelected = self.settingsSubPages['PSAR'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:s}_LINECOLOR".format(lineSelected)].getColor()
                self.settingsSubPages['PSAR'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['PSAR'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                self.settingsSubPages['PSAR'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                self.settingsSubPages['PSAR'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                self.settingsSubPages['PSAR'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                self.settingsSubPages['PSAR'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                self.settingsSubPages['PSAR'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                self.settingsSubPages['PSAR'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                self.settingsSubPages['PSAR'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                self.settingsSubPages['PSAR'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):             
                contentType = guioName_split[2]
                self.settingsSubPages['PSAR'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(self.settingsSubPages['PSAR'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                                      gValue = int(self.settingsSubPages['PSAR'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                                      bValue = int(self.settingsSubPages['PSAR'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                                      aValue = int(self.settingsSubPages['PSAR'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                self.settingsSubPages['PSAR'].GUIOs["INDICATORCOLOR_{:s}_VALUE".format(contentType)].updateText(str(int(self.settingsSubPages['PSAR'].GUIOs['INDICATORCOLOR_{:s}_SLIDER'.format(contentType)].getSliderValue()*255/100)))
                self.settingsSubPages['PSAR'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):        
                lineSelected = self.settingsSubPages['PSAR'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(self.settingsSubPages['PSAR'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(self.settingsSubPages['PSAR'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(self.settingsSubPages['PSAR'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(self.settingsSubPages['PSAR'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:s}_LINECOLOR".format(lineSelected)].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['PSAR'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                self.settingsSubPages['PSAR'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'WidthTextInputBox'): 
                self.settingsSubPages['PSAR'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):     
                self.settingsSubPages['PSAR'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):     
                #UpdateTracker Initialization
                updateTracker = dict()
                #Check for any changes in the configuration
                if (True):
                    for lineNumber in range (1, _NMAXLINES['PSAR']+1):
                        updateTracker[lineNumber] = False
                        #Width
                        width_previous = self.objectConfig['PSAR_{:d}_Width'.format(lineNumber)]
                        reset = False
                        try:
                            width = int(self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_WIDTHINPUT".format(lineNumber)].getText())
                            if (0 < width): self.objectConfig['PSAR_{:d}_Width'.format(lineNumber)] = width
                            else: reset = False
                        except: reset = False
                        if (reset == True):
                            self.objectConfig['PSAR_{:d}_Width'.format(lineNumber)] = 1
                            self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_WIDTHINPUT".format(lineNumber)].updateText(str(self.objectConfig['PSAR_{:d}_Width'.format(lineNumber)]))
                        if (width_previous != self.objectConfig['PSAR_{:d}_Width'.format(lineNumber)]): updateTracker[lineNumber] = True
                        #Color
                        color_previous = (self.objectConfig['PSAR_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)],
                                          self.objectConfig['PSAR_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)],
                                          self.objectConfig['PSAR_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)],
                                          self.objectConfig['PSAR_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)])
                        color_r, color_g, color_b, color_a = self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_LINECOLOR".format(lineNumber)].getColor()
                        self.objectConfig['PSAR_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)] = color_r
                        self.objectConfig['PSAR_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)] = color_g
                        self.objectConfig['PSAR_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)] = color_b
                        self.objectConfig['PSAR_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)] = color_a
                        if (color_previous != (color_r, color_g, color_b, color_a)): updateTracker[lineNumber] = True
                        #Line Display
                        display_previous = self.objectConfig['PSAR_{:d}_Display'.format(lineNumber)]
                        self.objectConfig['PSAR_{:d}_Display'.format(lineNumber)] = self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_DISPLAY".format(lineNumber)].getStatus()
                        if (display_previous != self.objectConfig['PSAR_{:d}_Display'.format(lineNumber)]): updateTracker[lineNumber] = True
                    #PSAR Master
                    psarMaster_previous = self.objectConfig['PSAR_Master']
                    self.objectConfig['PSAR_Master'] = self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_PSAR"].getStatus()
                    if (psarMaster_previous != self.objectConfig['PSAR_Master']):
                        for lineNumber in updateTracker: updateTracker[lineNumber] = True
                #Queue Update
                configuredPSARs = set([analysisCode for analysisCode in self.analysisParams if analysisCode[:4] == 'PSAR'])
                for configuredPSAR in configuredPSARs:
                    lineNumber = self.analysisParams[configuredPSAR]['lineNumber']
                    if (updateTracker[lineNumber] == True):
                        self.__klineDrawer_RemoveDrawings(analysisCode = configuredPSAR, gRemovalSignal = _FULLDRAWSIGNALS['PSAR']) #Remove previous graphics
                        self.__addBufferZone_toDrawQueue(analysisCode = configuredPSAR, drawSignal = _FULLDRAWSIGNALS['PSAR'])      #Update draw queue
                #Control Buttons Handling
                self.settingsSubPages['PSAR'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'): 
                lineNumber = int(guioName_split[2])
                #Get new switch status
                _newStatus = self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}".format(lineNumber)].getStatus()
                self.objectConfig['PSAR_{:d}_LineActive'.format(lineNumber)] = _newStatus
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['PSAR_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'AF0TextInputBox'):      
                lineNumber = int(guioName_split[2])
                #Get new AF0
                try:    _af0 = round(float(self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_AF0INPUT".format(lineNumber)].getText()), 3)
                except: _af0 = None
                #Save the new value to the object config dictionary
                self.objectConfig['PSAR_{:d}_AF0'.format(lineNumber)] = _af0
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['PSAR_Master'] == True) and (self.objectConfig['PSAR_{:d}_LineActive'.format(lineNumber)] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'AF+TextInputBox'):      
                lineNumber = int(guioName_split[2])
                #Get new AF+
                try:    _afAccel = round(float(self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_AF+INPUT".format(lineNumber)].getText()), 3)
                except: _afAccel = None
                #Save the new value to the object config dictionary
                self.objectConfig['PSAR_{:d}_AF+'.format(lineNumber)] = _afAccel
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['PSAR_Master'] == True) and (self.objectConfig['PSAR_{:d}_LineActive'.format(lineNumber)] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'AFMaxTextInputBox'):    
                lineNumber = int(guioName_split[2])
                #Get new AFMax
                try:    _afMax = round(float(self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_AFMAXINPUT".format(lineNumber)].getText()), 3)
                except: _afMax = None
                #Save the new value to the object config dictionary
                self.objectConfig['PSAR_{:d}_AFMAX'.format(lineNumber)] = _afMax
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['PSAR_Master'] == True) and (self.objectConfig['PSAR_{:d}_LineActive'.format(lineNumber)] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True

        #Subpage 'BOL'
        elif (indicatorType == 'BOL'):
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):        
                lineSelected = self.settingsSubPages['BOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:s}_LINECOLOR".format(lineSelected)].getColor()
                self.settingsSubPages['BOL'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['BOL'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                self.settingsSubPages['BOL'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                self.settingsSubPages['BOL'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                self.settingsSubPages['BOL'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                self.settingsSubPages['BOL'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                self.settingsSubPages['BOL'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                self.settingsSubPages['BOL'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                self.settingsSubPages['BOL'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                self.settingsSubPages['BOL'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):                 
                contentType = guioName_split[2]
                self.settingsSubPages['BOL'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(self.settingsSubPages['BOL'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                                     gValue = int(self.settingsSubPages['BOL'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                                     bValue = int(self.settingsSubPages['BOL'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                                     aValue = int(self.settingsSubPages['BOL'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                self.settingsSubPages['BOL'].GUIOs["INDICATORCOLOR_{:s}_VALUE".format(contentType)].updateText(str(int(self.settingsSubPages['BOL'].GUIOs['INDICATORCOLOR_{:s}_SLIDER'.format(contentType)].getSliderValue()*255/100)))
                self.settingsSubPages['BOL'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):            
                lineSelected = self.settingsSubPages['BOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(self.settingsSubPages['BOL'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(self.settingsSubPages['BOL'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(self.settingsSubPages['BOL'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(self.settingsSubPages['BOL'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:s}_LINECOLOR".format(lineSelected)].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['BOL'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                self.settingsSubPages['BOL'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'WidthTextInputBox'):     
                self.settingsSubPages['BOL'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):         
                self.settingsSubPages['BOL'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplayContentsSwitch'): 
                self.settingsSubPages['BOL'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):         
                #UpdateTracker Initialization
                updateTracker = dict()
                #Check for any changes in the configuration
                if (True):
                    for lineIndex in range (_NMAXLINES['BOL']):
                        lineNumber = lineIndex+1
                        updateTracker[lineNumber] = [False, False] #[1]: Draw CenterLine, [2]: Draw Band
                        #Width
                        width_previous = self.objectConfig['BOL_{:d}_Width'.format(lineNumber)]
                        reset = False
                        try:
                            width = int(self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_WIDTHINPUT".format(lineNumber)].getText())
                            if (0 < width): self.objectConfig['BOL_{:d}_Width'.format(lineNumber)] = width
                            else: reset = True
                        except: reset = True
                        if (reset == True):
                            self.objectConfig['BOL_{:d}_Width'.format(lineNumber)] = 1
                            self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_WIDTHINPUT".format(lineNumber)].updateText(str(self.objectConfig['BOL_{:d}_Width'.format(lineNumber)]))
                        if (width_previous != self.objectConfig['BOL_{:d}_Width'.format(lineNumber)]): updateTracker[lineNumber][0] = True
                        #Color
                        color_previous = (self.objectConfig['BOL_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)],
                                          self.objectConfig['BOL_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)],
                                          self.objectConfig['BOL_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)],
                                          self.objectConfig['BOL_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)])
                        color_r, color_g, color_b, color_a = self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_LINECOLOR".format(lineNumber)].getColor()
                        self.objectConfig['BOL_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)] = color_r
                        self.objectConfig['BOL_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)] = color_g
                        self.objectConfig['BOL_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)] = color_b
                        self.objectConfig['BOL_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)] = color_a
                        if (color_previous != (color_r, color_g, color_b, color_a)): updateTracker[lineNumber][0] = True; updateTracker[lineNumber][1] = True
                        #Line Display
                        display_previous = self.objectConfig['BOL_{:d}_Display'.format(lineNumber)]
                        self.objectConfig['BOL_{:d}_Display'.format(lineNumber)] = self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_DISPLAY".format(lineNumber)].getStatus()
                        if (display_previous != self.objectConfig['BOL_{:d}_Display'.format(lineNumber)]): updateTracker[lineNumber][0] = True; updateTracker[lineNumber][1] = True
                    #BOL Master
                    bolMaster_previous = self.objectConfig['BOL_Master']
                    self.objectConfig['BOL_Master'] = self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_BOL"].getStatus()
                    if (bolMaster_previous != self.objectConfig['BOL_Master']):
                        for lineNumber in updateTracker: updateTracker[lineNumber][0] = True; updateTracker[lineNumber][1] = True
                    #CenterLine Display Switch
                    display_bolCenter_previous = self.objectConfig['BOL_DisplayCenterLine']
                    self.objectConfig['BOL_DisplayCenterLine'] = self.settingsSubPages['BOL'].GUIOs["INDICATOR_DISPLAYCONTENTS_BOLCENTERSWITCH"].getStatus()
                    if (display_bolCenter_previous != self.objectConfig['BOL_DisplayCenterLine']): 
                        for lineNumber in updateTracker: updateTracker[lineNumber][0] = True
                    #Band Display Switch
                    display_bolBand_previous = self.objectConfig['BOL_DisplayBand']
                    self.objectConfig['BOL_DisplayBand'] = self.settingsSubPages['BOL'].GUIOs["INDICATOR_DISPLAYCONTENTS_BOLBANDSWITCH"].getStatus()
                    if (display_bolBand_previous != self.objectConfig['BOL_DisplayBand']): 
                        for lineNumber in updateTracker: updateTracker[lineNumber][1] = True
                #Queue Update
                configuredBOLs = set([analysisCode for analysisCode in self.analysisParams if analysisCode[:3] == 'BOL'])
                for configuredBOL in configuredBOLs:
                    lineNumber = self.analysisParams[configuredBOL]['lineNumber']
                    drawSignal = 0
                    drawSignal += 0b01*updateTracker[lineNumber][0] #CenterLine
                    drawSignal += 0b10*updateTracker[lineNumber][1] #Band
                    if (drawSignal != 0):
                        self.__klineDrawer_RemoveDrawings(analysisCode = configuredBOL, gRemovalSignal = drawSignal) #Remove previous graphics
                        self.__addBufferZone_toDrawQueue(analysisCode = configuredBOL, drawSignal = drawSignal)      #Update draw queue
                #Control Buttons Handling
                self.settingsSubPages['BOL'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'):  
                lineNumber = int(guioName_split[2])
                #Get new switch status
                _newStatus = self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}".format(lineNumber)].getStatus()
                self.objectConfig['BOL_{:d}_LineActive'.format(lineNumber)] = _newStatus
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['BOL_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'):  
                lineNumber = int(guioName_split[2])
                #Get new nSamples
                try:    _nSamples = int(self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_INTERVALINPUT".format(lineNumber)].getText())
                except: _nSamples = None
                #Save the new value to the object config dictionary
                self.objectConfig['BOL_{:d}_NSamples'.format(lineNumber)] = _nSamples
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['BOL_Master'] == True) and (self.objectConfig['BOL_{:d}_LineActive'.format(lineNumber)] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'BandWidthTextInputBox'): 
                lineNumber = int(guioName_split[2])
                #Get new bandwidth
                try:    _bandWidth = int(self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_BANDWIDTHINPUT".format(lineNumber)].getText())
                except: _bandWidth = None
                #Save the new value to the object config dictionary
                self.objectConfig['BOL_{:d}_BandWidth'.format(lineNumber)] = _bandWidth
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['BOL_Master'] == True) and (self.objectConfig['BOL_{:d}_LineActive'.format(lineNumber)] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'MATypeSelection'): 
                #Get new MAType
                _maType = self.settingsSubPages['BOL'].GUIOs["INDICATOR_MATYPESELECTION"].getSelected()
                #Save the new value to the object config dictionary
                self.objectConfig['BOL_MAType'] = _maType
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['BOL_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True

        #Subpage 'IVP'
        elif (indicatorType == 'IVP'):
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):     
                lineSelected = self.settingsSubPages['IVP'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = self.settingsSubPages['IVP'].GUIOs["INDICATOR_{:s}_COLOR".format(lineSelected)].getColor()
                self.settingsSubPages['IVP'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['IVP'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                self.settingsSubPages['IVP'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                self.settingsSubPages['IVP'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                self.settingsSubPages['IVP'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                self.settingsSubPages['IVP'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                self.settingsSubPages['IVP'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                self.settingsSubPages['IVP'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                self.settingsSubPages['IVP'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                self.settingsSubPages['IVP'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):              
                contentType = guioName_split[2]
                self.settingsSubPages['IVP'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(self.settingsSubPages['IVP'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                                     gValue = int(self.settingsSubPages['IVP'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                                     bValue = int(self.settingsSubPages['IVP'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                                     aValue = int(self.settingsSubPages['IVP'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                self.settingsSubPages['IVP'].GUIOs["INDICATORCOLOR_{:s}_VALUE".format(contentType)].updateText(str(int(self.settingsSubPages['IVP'].GUIOs['INDICATORCOLOR_{:s}_SLIDER'.format(contentType)].getSliderValue()*255/100)))
                self.settingsSubPages['IVP'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):         
                lineSelected = self.settingsSubPages['IVP'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(self.settingsSubPages['IVP'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(self.settingsSubPages['IVP'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(self.settingsSubPages['IVP'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(self.settingsSubPages['IVP'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                self.settingsSubPages['IVP'].GUIOs["INDICATOR_{:s}_COLOR".format(lineSelected)].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['IVP'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                self.settingsSubPages['IVP'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplayWidthSlider'): 
                lineTarget = guioName_split[2]
                sliderValue = self.settingsSubPages['IVP'].GUIOs["INDICATOR_{:s}_DISPLAYWIDTHSLIDER".format(lineTarget)].getSliderValue()
                self.settingsSubPages['IVP'].GUIOs["INDICATOR_{:s}_DISPLAYWIDTHVALUETEXT".format(lineTarget)].updateText(str(round(sliderValue/100*0.9+0.1, 2)))
                self.settingsSubPages['IVP'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):      
                self.settingsSubPages['IVP'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'VPLPBDisplayRegion'): 
                #Get new VPLPBDisplayRegion
                _sliderValue = self.settingsSubPages['IVP'].GUIOs["INDICATOR_VPLPB_DISPLAYREGIONSLIDER"].getSliderValue()
                self.settingsSubPages['IVP'].GUIOs["INDICATOR_VPLPB_DISPLAYREGIONVALUETEXT"].updateText("{:.1f} %".format((_sliderValue/100*0.950+0.050)*100))
                self.settingsSubPages['IVP'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):
                #UpdateTracker Initialization
                updateTracker = [False, False] #[0]: VPLP, [1]: VPLPB
                #Check for any changes in the configuration
                if (True):
                    #IVP Master
                    ivpMaster_previous = self.objectConfig['IVP_Master']
                    self.objectConfig['IVP_Master'] = self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_IVP"].getStatus()
                    if (ivpMaster_previous != self.objectConfig['IVP_Master']): updateTracker = [True, True]
                    #displaySwitch - VPLP
                    vplpDisplay_prev = self.objectConfig['IVP_VPLP_Display']
                    self.objectConfig['IVP_VPLP_Display'] = self.settingsSubPages['IVP'].GUIOs["INDICATOR_VPLP_DISPLAYSWITCH"].getStatus()
                    if (vplpDisplay_prev != self.objectConfig['IVP_VPLP_Display']): updateTracker[0] = True
                    #displaySwitch - VPLB
                    vplpbDisplay_prev = self.objectConfig['IVP_VPLPB_Display']
                    self.objectConfig['IVP_VPLPB_Display'] = self.settingsSubPages['IVP'].GUIOs["INDICATOR_VPLPB_DISPLAYSWITCH"].getStatus()
                    if (vplpbDisplay_prev != self.objectConfig['IVP_VPLPB_Display']): updateTracker[1] = True
                    #displayWidth - VPLP
                    vplpDisplayWidth_prev = self.objectConfig['IVP_VPLP_DisplayWidth']
                    self.objectConfig['IVP_VPLP_DisplayWidth'] = round(self.settingsSubPages['IVP'].GUIOs["INDICATOR_VPLP_DISPLAYWIDTHSLIDER"].getSliderValue()/100*0.9+0.1, 2)
                    if (vplpDisplayWidth_prev != self.objectConfig['IVP_VPLP_DisplayWidth']): updateTracker[0] = True
                    #VPLPB Display Region
                    vplpbDisplayRegion_prev = self.objectConfig['IVP_VPLPB_DisplayRegion']
                    self.objectConfig['IVP_VPLPB_DisplayRegion'] = round(self.settingsSubPages['IVP'].GUIOs["INDICATOR_VPLPB_DISPLAYREGIONSLIDER"].getSliderValue()/100*0.950+0.050, 3)
                    if (vplpbDisplayRegion_prev != self.objectConfig['IVP_VPLPB_DisplayRegion']): updateTracker[1] = True
                    #Colors
                    for targetLine in ('VPLP', 'VPLPB'):
                        color_previous = (self.objectConfig['IVP_{:s}_ColorR%{:s}'.format(targetLine, self.currentGUITheme)],
                                          self.objectConfig['IVP_{:s}_ColorG%{:s}'.format(targetLine, self.currentGUITheme)],
                                          self.objectConfig['IVP_{:s}_ColorB%{:s}'.format(targetLine, self.currentGUITheme)],
                                          self.objectConfig['IVP_{:s}_ColorA%{:s}'.format(targetLine, self.currentGUITheme)])
                        color_r, color_g, color_b, color_a = self.settingsSubPages['IVP'].GUIOs["INDICATOR_{:s}_COLOR".format(targetLine.upper())].getColor()
                        self.objectConfig['IVP_{:s}_ColorR%{:s}'.format(targetLine, self.currentGUITheme)] = color_r
                        self.objectConfig['IVP_{:s}_ColorG%{:s}'.format(targetLine, self.currentGUITheme)] = color_g
                        self.objectConfig['IVP_{:s}_ColorB%{:s}'.format(targetLine, self.currentGUITheme)] = color_b
                        self.objectConfig['IVP_{:s}_ColorA%{:s}'.format(targetLine, self.currentGUITheme)] = color_a
                        if (color_previous != (color_r, color_g, color_b, color_a)): 
                            if   (targetLine == 'VPLP'):  updateTracker[0] = True
                            elif (targetLine == 'VPLPB'): updateTracker[1] = True
                #Content Update Handling
                drawSignal = 0
                drawSignal += 0b01*updateTracker[0] #VPLP
                drawSignal += 0b10*updateTracker[1] #VPLPB
                if (drawSignal != 0):
                    self.__klineDrawer_RemoveDrawings(analysisCode = 'IVP', gRemovalSignal = drawSignal) #Remove previous graphics
                    self.__addBufferZone_toDrawQueue(analysisCode = 'IVP', drawSignal = drawSignal)      #Update draw queue
                #Settings Control Button
                self.settingsSubPages['IVP'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'Interval'):
                #Get new nSamples
                try:    _nSamples = int(self.settingsSubPages['IVP'].GUIOs["INDICATOR_INTERVAL_INPUTTEXT"].getText())
                except: _nSamples = None
                #Save the new value to the object config dictionary
                self.objectConfig['IVP_NSamples'] = _nSamples
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['IVP_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'GammaFactor'):
                #Get new Gamma Factor
                _gammaFactor = round(self.settingsSubPages['IVP'].GUIOs["INDICATOR_GAMMAFACTOR_SLIDER"].getSliderValue()/100*0.095+0.005, 3)
                self.settingsSubPages['IVP'].GUIOs["INDICATOR_GAMMAFACTOR_VALUETEXT"].updateText("{:.1f} %".format(_gammaFactor*100))
                self.objectConfig['IVP_GammaFactor'] = _gammaFactor
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['IVP_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'DeltaFactor'):
                #Get new Delta Factor
                _deltaFactor = round(self.settingsSubPages['IVP'].GUIOs["INDICATOR_DELTAFACTOR_SLIDER"].getSliderValue()/100*9.9+0.1, 1)
                self.settingsSubPages['IVP'].GUIOs["INDICATOR_DELTAFACTOR_VALUETEXT"].updateText("{:d} %".format(int(_deltaFactor*100)))
                self.objectConfig['IVP_DeltaFactor'] = _deltaFactor
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['IVP_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
                
        #Subpage 'PIP'
        elif (indicatorType == 'PIP'):
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'): 
                lineSelected = self.settingsSubPages['PIP'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = self.settingsSubPages['PIP'].GUIOs["INDICATOR_{:s}_COLOR".format(lineSelected)].getColor()
                self.settingsSubPages['PIP'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['PIP'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                self.settingsSubPages['PIP'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                self.settingsSubPages['PIP'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                self.settingsSubPages['PIP'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                self.settingsSubPages['PIP'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                self.settingsSubPages['PIP'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                self.settingsSubPages['PIP'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                self.settingsSubPages['PIP'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                self.settingsSubPages['PIP'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):          
                contentType = guioName_split[2]
                self.settingsSubPages['PIP'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(self.settingsSubPages['PIP'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                                     gValue = int(self.settingsSubPages['PIP'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                                     bValue = int(self.settingsSubPages['PIP'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                                     aValue = int(self.settingsSubPages['PIP'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                self.settingsSubPages['PIP'].GUIOs["INDICATORCOLOR_{:s}_VALUE".format(contentType)].updateText(str(int(self.settingsSubPages['PIP'].GUIOs['INDICATORCOLOR_{:s}_SLIDER'.format(contentType)].getSliderValue()*255/100)))
                self.settingsSubPages['PIP'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):     
                lineSelected = self.settingsSubPages['PIP'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(self.settingsSubPages['PIP'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(self.settingsSubPages['PIP'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(self.settingsSubPages['PIP'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(self.settingsSubPages['PIP'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_{:s}_COLOR".format(lineSelected)].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['PIP'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                self.settingsSubPages['PIP'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):  
                self.settingsSubPages['PIP'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplayType'):
                self.settingsSubPages['PIP'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):  
                #UpdateTracker Initialization
                updateTracker = [False, False, False, False, False]
                #Check for any changes in the configuration
                if (True):
                    #PIP Master
                    pipMaster_previous = self.objectConfig['PIP_Master']
                    self.objectConfig['PIP_Master'] = self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_PIP"].getStatus()
                    if (pipMaster_previous != self.objectConfig['PIP_Master']): updateTracker = [True,True,True,True,True]
                    #Display Switches
                    for _target in ('SWING', 'NNASIGNAL', 'WOISIGNAL', 'NESSIGNAL', 'CLASSICALSIGNAL'):
                        _display_prev = self.objectConfig['PIP_{:s}_Display'.format(_target)]
                        self.objectConfig['PIP_{:s}_Display'.format(_target)] = self.settingsSubPages['PIP'].GUIOs["INDICATOR_{:s}_DISPLAYSWITCH".format(_target)].getStatus()
                        if (_display_prev != self.objectConfig['PIP_{:s}_Display'.format(_target)]): 
                            if   (_target == 'SWING'):           updateTracker[0] = True
                            elif (_target == 'NNASIGNAL'):       updateTracker[1] = True
                            elif (_target == 'WOISIGNAL'):       updateTracker[2] = True
                            elif (_target == 'NESSIGNAL'):       updateTracker[3] = True
                            elif (_target == 'CLASSICALSIGNAL'): updateTracker[4] = True
                    #Colors
                    for _target in ('SWING', 'NNASIGNAL+', 'NNASIGNAL-', 'WOISIGNAL+', 'WOISIGNAL-', 'NESSIGNAL+', 'NESSIGNAL-', 'CLASSICALSIGNAL+', 'CLASSICALSIGNAL-'):
                        color_previous = (self.objectConfig['PIP_{:s}_ColorR%{:s}'.format(_target, self.currentGUITheme)],
                                          self.objectConfig['PIP_{:s}_ColorG%{:s}'.format(_target, self.currentGUITheme)],
                                          self.objectConfig['PIP_{:s}_ColorB%{:s}'.format(_target, self.currentGUITheme)],
                                          self.objectConfig['PIP_{:s}_ColorA%{:s}'.format(_target, self.currentGUITheme)])
                        color_r, color_g, color_b, color_a = self.settingsSubPages['PIP'].GUIOs["INDICATOR_{:s}_COLOR".format(_target)].getColor()
                        self.objectConfig['PIP_{:s}_ColorR%{:s}'.format(_target, self.currentGUITheme)] = color_r
                        self.objectConfig['PIP_{:s}_ColorG%{:s}'.format(_target, self.currentGUITheme)] = color_g
                        self.objectConfig['PIP_{:s}_ColorB%{:s}'.format(_target, self.currentGUITheme)] = color_b
                        self.objectConfig['PIP_{:s}_ColorA%{:s}'.format(_target, self.currentGUITheme)] = color_a
                        if (color_previous != (color_r, color_g, color_b, color_a)):
                            if   (_target == 'SWING'):                                                 updateTracker[0] = True
                            elif ((_target == 'NNASIGNAL+')       or (_target == 'NNASIGNAL-')):       updateTracker[1] = True
                            elif ((_target == 'WOISIGNAL+')       or (_target == 'WOISIGNAL-')):       updateTracker[2] = True
                            elif ((_target == 'NESSIGNAL+')       or (_target == 'NESSIGNAL-')):       updateTracker[3] = True
                            elif ((_target == 'CLASSICALSIGNAL+') or (_target == 'CLASSICALSIGNAL-')): updateTracker[4] = True
                    #CS Signal Display Type
                    _displayType_prev = self.objectConfig['PIP_CLASSICALSIGNAL_DisplayType']
                    self.objectConfig['PIP_CLASSICALSIGNAL_DisplayType'] = self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALSIGNAL_DISPLAYTYPESELECTION"].getSelected()
                    if ((self.objectConfig['PIP_CLASSICALSIGNAL_Display'] == True) and (_displayType_prev != self.objectConfig['PIP_CLASSICALSIGNAL_DisplayType'])): updateTracker[4] = True
                #Content Update Handling
                drawSignal = 0b00000
                drawSignal += 0b00001*updateTracker[0] #Swing 0
                drawSignal += 0b00010*updateTracker[1] #NNA Signal
                drawSignal += 0b00100*updateTracker[2] #WOI Signal
                drawSignal += 0b01000*updateTracker[3] #NES Signal
                drawSignal += 0b10000*updateTracker[4] #Classical Signal
                if (drawSignal != 0):
                    self.__klineDrawer_RemoveDrawings(analysisCode = 'PIP', gRemovalSignal = drawSignal) #Remove previous graphics
                    self.__addBufferZone_toDrawQueue(analysisCode = 'PIP', drawSignal = drawSignal)      #Update draw queue
                #Settings Control Button
                self.settingsSubPages['PIP'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'SwingRange'):
                #Get new swing range
                _swingRange = round(self.settingsSubPages['PIP'].GUIOs["INDICATOR_SWINGRANGE_SLIDER"].getSliderValue()/100*0.0490+0.0010, 3)
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_SWINGRANGE_VALUETEXT"].updateText("{:.2f} %".format(_swingRange*100))
                self.objectConfig['PIP_SwingRange'] = _swingRange
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['PIP_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'NeuralNetworkCode'):
                #Update Neural Network Code
                _neuralNetworkCode = self.settingsSubPages['PIP'].GUIOs["INDICATOR_NEURALNETWORKCODE_SELECTIONBOX"].getSelected()
                self.objectConfig['PIP_NeuralNetworkCode'] = _neuralNetworkCode
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['PIP_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'NeuralNetworkCodeRelease'):
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_NEURALNETWORKCODE_SELECTIONBOX"].setSelected(itemKey = None, callSelectionUpdateFunction = False)
                self.objectConfig['PIP_NeuralNetworkCode'] = None
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['PIP_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'NNAAlpha'):
                #Get new NNAAlpha
                _nnaAlpha = round(self.settingsSubPages['PIP'].GUIOs["INDICATOR_NNAALPHA_SLIDER"].getSliderValue()/100*0.95+0.05, 2)
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_NNAALPHA_VALUETEXT"].updateText("{:.2f}".format(_nnaAlpha))
                self.objectConfig['PIP_NNAAlpha'] = _nnaAlpha
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['PIP_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'NNABeta'):
                #Get new NNABeta
                _nnaBeta = int(round(self.settingsSubPages['PIP'].GUIOs["INDICATOR_NNABETA_SLIDER"].getSliderValue()/100*18+2, 0))
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_NNABETA_VALUETEXT"].updateText("{:d}".format(_nnaBeta))
                self.objectConfig['PIP_NNABeta'] = _nnaBeta
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['PIP_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'ClassicalAlpha'):
                #Get new ClassicalAlpha
                _classicalAlpha = round(self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALALPHA_SLIDER"].getSliderValue()/100*2.9+0.1, 1)
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALALPHA_VALUETEXT"].updateText("{:.1f}".format(_classicalAlpha))
                self.objectConfig['PIP_ClassicalAlpha'] = _classicalAlpha
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['PIP_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'ClassicalBeta'):
                #Get new ClassicalBeta
                _classicalBeta = int(round(self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALBETA_SLIDER"].getSliderValue()/100*18+2, 0))
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALBETA_VALUETEXT"].updateText("{:d}".format(_classicalBeta))
                self.objectConfig['PIP_ClassicalBeta'] = _classicalBeta
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['PIP_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'ClassicalNSamples'):
                #Get new nSamples
                try:    _nSamples = int(self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALNSAMPLES_INPUTTEXT"].getText())
                except: _nSamples = None
                #Save the new value to the object config dictionary
                self.objectConfig['PIP_ClassicalNSamples'] = _nSamples
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['PIP_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'ClassicalSigma'):
                #Get new nSamples
                try:    _sigma = round(float(self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALSIGMA_INPUTTEXT"].getText()), 1)
                except: _sigma = None
                #Save the new value to the object config dictionary
                self.objectConfig['PIP_ClassicalSigma'] = _sigma
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['PIP_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True

        #Subpage 'VOL'
        elif (indicatorType == 'VOL'):
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):    
                lineSelected = self.settingsSubPages['VOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:s}_LINECOLOR".format(lineSelected)].getColor()
                self.settingsSubPages['VOL'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['VOL'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                self.settingsSubPages['VOL'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                self.settingsSubPages['VOL'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                self.settingsSubPages['VOL'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                self.settingsSubPages['VOL'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                self.settingsSubPages['VOL'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                self.settingsSubPages['VOL'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                self.settingsSubPages['VOL'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                self.settingsSubPages['VOL'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):             
                contentType = guioName_split[2]
                self.settingsSubPages['VOL'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(self.settingsSubPages['VOL'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                                     gValue = int(self.settingsSubPages['VOL'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                                     bValue = int(self.settingsSubPages['VOL'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                                     aValue = int(self.settingsSubPages['VOL'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                self.settingsSubPages['VOL'].GUIOs["INDICATORCOLOR_{:s}_VALUE".format(contentType)].updateText(str(int(self.settingsSubPages['VOL'].GUIOs['INDICATORCOLOR_{:s}_SLIDER'.format(contentType)].getSliderValue()*255/100)))
                self.settingsSubPages['VOL'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):        
                lineSelected = self.settingsSubPages['VOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(self.settingsSubPages['VOL'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(self.settingsSubPages['VOL'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(self.settingsSubPages['VOL'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(self.settingsSubPages['VOL'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:s}_LINECOLOR".format(lineSelected)].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['VOL'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                self.settingsSubPages['VOL'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'WidthTextInputBox'): 
                self.settingsSubPages['VOL'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):     
                self.settingsSubPages['VOL'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):     
                #UpdateTracker Initialization
                updateTracker = dict()
                #Check for any changes in the configuration
                if (True):
                    for lineIndex in range (_NMAXLINES['VOL']):
                        lineNumber = lineIndex+1
                        updateTracker[lineNumber] = False
                        #Width
                        width_previous = self.objectConfig['VOL_{:d}_Width'.format(lineNumber)]
                        reset = False
                        try:
                            width = int(self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_WIDTHINPUT".format(lineNumber)].getText())
                            if (0 < width): self.objectConfig['VOL_{:d}_Width'.format(lineNumber)] = width
                            else: reset = True
                        except: reset = True
                        if (reset == True):
                            self.objectConfig['VOL_{:d}_Width'.format(lineNumber)] = 1
                            self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_WIDTHINPUT".format(lineNumber)].updateText(str(self.objectConfig['VOL_{:d}_Width'.format(lineNumber)]))
                        if (width_previous != self.objectConfig['VOL_{:d}_Width'.format(lineNumber)]): updateTracker[lineNumber] = True
                        #Color
                        color_previous = (self.objectConfig['VOL_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                          self.objectConfig['VOL_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                          self.objectConfig['VOL_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                          self.objectConfig['VOL_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)])
                        color_r, color_g, color_b, color_a = self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_LINECOLOR".format(lineNumber)].getColor()
                        self.objectConfig['VOL_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)] = color_r
                        self.objectConfig['VOL_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)] = color_g
                        self.objectConfig['VOL_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)] = color_b
                        self.objectConfig['VOL_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)] = color_a
                        if (color_previous != (color_r, color_g, color_b, color_a)): updateTracker[lineNumber] = True
                        #Line Display
                        display_previous = self.objectConfig['VOL_{:d}_Display'.format(lineNumber)]
                        self.objectConfig['VOL_{:d}_Display'.format(lineNumber)] = self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_DISPLAY".format(lineNumber)].getStatus()
                        if (display_previous != self.objectConfig['VOL_{:d}_Display'.format(lineNumber)]): updateTracker[lineNumber] = True
                    #VOL Master
                    volMaster_previous = self.objectConfig['VOL_Master']
                    self.objectConfig['VOL_Master'] = self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_VOL"].getStatus()
                    if (volMaster_previous != self.objectConfig['VOL_Master']):
                        for targetLine in updateTracker: updateTracker[targetLine] = True
                #Queue Update
                configuredVOLs = set([analysisCode for analysisCode in self.analysisParams if analysisCode[:3] == 'VOL'])
                for configuredVOL in configuredVOLs:
                    lineNumber = self.analysisParams[configuredVOL]['lineNumber']
                    if (updateTracker[lineNumber] == True):
                        self.__klineDrawer_RemoveDrawings(analysisCode = configuredVOL, gRemovalSignal = _FULLDRAWSIGNALS['VOL']) #Remove previous graphics
                        self.__addBufferZone_toDrawQueue(analysisCode = configuredVOL, drawSignal = _FULLDRAWSIGNALS['VOL'])      #Update draw queue
                #Control Buttons Handling
                self.settingsSubPages['VOL'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'): 
                lineNumber = int(guioName_split[2])
                #Get new switch status
                _newStatus = self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}".format(lineNumber)].getStatus()
                self.objectConfig['VOL_{:d}_LineActive'.format(lineNumber)] = _newStatus
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['VOL_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'): 
                lineNumber = int(guioName_split[2])
                #Get new nSamples
                try:    _nSamples = int(self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_INTERVALINPUT".format(lineNumber)].getText())
                except: _nSamples = None
                #Save the new value to the object config dictionary
                self.objectConfig['VOL_{:d}_NSamples'.format(lineNumber)] = _nSamples
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['VOL_Master'] == True) and (self.objectConfig['VOL_{:d}_LineActive'.format(lineNumber)] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'VolTypeSelection'):
                #Get new VolumeType
                _volType = self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOLTYPESELECTION"].getSelected()
                #Save the new value to the object config dictionary
                self.objectConfig['VOL_VolumeType'] = _volType
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['VOL_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'MATypeSelection'): 
                #Get new MAType
                _maType = self.settingsSubPages['VOL'].GUIOs["INDICATOR_MATYPESELECTION"].getSelected()
                #Save the new value to the object config dictionary
                self.objectConfig['VOL_MAType'] = _maType
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['VOL_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True

        #Subpage 'MMACDSHORT'
        elif (indicatorType == 'MMACDSHORT'):
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'): 
                lineSelected = self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_{:s}_COLOR".format(lineSelected)].getColor()
                self.settingsSubPages['MMACDSHORT'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                self.settingsSubPages['MMACDSHORT'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                self.settingsSubPages['MMACDSHORT'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                self.settingsSubPages['MMACDSHORT'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                self.settingsSubPages['MMACDSHORT'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                self.settingsSubPages['MMACDSHORT'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):          
                contentType = guioName_split[2]
                self.settingsSubPages['MMACDSHORT'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(self.settingsSubPages['MMACDSHORT'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                                            gValue = int(self.settingsSubPages['MMACDSHORT'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                                            bValue = int(self.settingsSubPages['MMACDSHORT'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                                            aValue = int(self.settingsSubPages['MMACDSHORT'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATORCOLOR_{:s}_VALUE".format(contentType)].updateText(str(int(self.settingsSubPages['MMACDSHORT'].GUIOs['INDICATORCOLOR_{:s}_SLIDER'.format(contentType)].getSliderValue()*255/100)))
                self.settingsSubPages['MMACDSHORT'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):     
                lineSelected = self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(self.settingsSubPages['MMACDSHORT'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(self.settingsSubPages['MMACDSHORT'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(self.settingsSubPages['MMACDSHORT'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(self.settingsSubPages['MMACDSHORT'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_{:s}_COLOR".format(lineSelected)].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['MMACDSHORT'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                self.settingsSubPages['MMACDSHORT'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):  
                self.settingsSubPages['MMACDSHORT'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):  
                #UpdateTracker Initialization
                updateTracker = [False, False, False] #[0]: Draw MMACD, [1]: Draw SIGNAL, [2]: Draw HISTOGRAM
                #Check for any changes in the configuration
                if (True):
                    #MMACDSHORT Master
                    mmacdShortMaster_previous = self.objectConfig['MMACDSHORT_Master']
                    self.objectConfig['MMACDSHORT_Master'] = self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_MMACDSHORT"].getStatus()
                    if (mmacdShortMaster_previous != self.objectConfig['MMACDSHORT_Master']): 
                        updateTracker[0] = True
                        updateTracker[1] = True
                        updateTracker[2] = True
                    #Colors
                    for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM+', 'HISTOGRAM-'):
                        color_previous = (self.objectConfig['MMACDSHORT_{:s}_ColorR%{:s}'.format(targetLine, self.currentGUITheme)],
                                          self.objectConfig['MMACDSHORT_{:s}_ColorG%{:s}'.format(targetLine, self.currentGUITheme)],
                                          self.objectConfig['MMACDSHORT_{:s}_ColorB%{:s}'.format(targetLine, self.currentGUITheme)],
                                          self.objectConfig['MMACDSHORT_{:s}_ColorA%{:s}'.format(targetLine, self.currentGUITheme)])
                        color_r, color_g, color_b, color_a = self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_{:s}_COLOR".format(targetLine)].getColor()
                        self.objectConfig['MMACDSHORT_{:s}_ColorR%{:s}'.format(targetLine, self.currentGUITheme)] = color_r
                        self.objectConfig['MMACDSHORT_{:s}_ColorG%{:s}'.format(targetLine, self.currentGUITheme)] = color_g
                        self.objectConfig['MMACDSHORT_{:s}_ColorB%{:s}'.format(targetLine, self.currentGUITheme)] = color_b
                        self.objectConfig['MMACDSHORT_{:s}_ColorA%{:s}'.format(targetLine, self.currentGUITheme)] = color_a
                        if (color_previous != (color_r, color_g, color_b, color_a)): 
                            if   (targetLine == 'MMACD'):      updateTracker[0] = True
                            elif (targetLine == 'SIGNAL'):     updateTracker[1] = True
                            elif (targetLine == 'HISTOGRAM+'): updateTracker[2] = True
                            elif (targetLine == 'HISTOGRAM-'): updateTracker[2] = True
                    #Line Display
                    for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM'):
                        displayStatus_prev = self.objectConfig['MMACDSHORT_{:s}_Display'.format(targetLine)]
                        self.objectConfig['MMACDSHORT_{:s}_Display'.format(targetLine)] = self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_{:s}_DISPLAYSWITCH".format(targetLine)].getStatus()
                        if (displayStatus_prev != self.objectConfig['MMACDSHORT_{:s}_Display'.format(targetLine)]):
                            if   (targetLine == 'MMACD'):     updateTracker[0] = True
                            elif (targetLine == 'SIGNAL'):    updateTracker[1] = True
                            elif (targetLine == 'HISTOGRAM'): updateTracker[2] = True
                #Queue Update
                drawSignal = 0
                drawSignal += 0b001*updateTracker[0] #MMACD
                drawSignal += 0b010*updateTracker[1] #SIGNAL
                drawSignal += 0b100*updateTracker[2] #HISTOGRAM
                if (drawSignal != 0): 
                    self.__klineDrawer_RemoveDrawings(analysisCode = 'MMACDSHORT', gRemovalSignal = drawSignal) #Remove previous graphics
                    self.__addBufferZone_toDrawQueue(analysisCode = 'MMACDSHORT', drawSignal = drawSignal)      #Update draw queue
                #Control Buttons Handling
                self.settingsSubPages['MMACDSHORT'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'):          
                lineNumber = int(guioName_split[2])
                #Get new switch status
                _newStatus = self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_MMACDMA{:d}".format(lineNumber)].getStatus()
                self.objectConfig['MMACDSHORT_MA{:d}_LineActive'.format(lineNumber)] = _newStatus
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['MMACDSHORT_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'):          
                lineNumber = int(guioName_split[2])
                #Get new nSamples
                try:    _nSamples = int(self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_MMACDMA{:d}_INTERVALINPUT".format(lineNumber)].getText())
                except: _nSamples = None
                #Save the new value to the object config dictionary
                self.objectConfig['MMACDSHORT_MA{:d}_NSamples'.format(lineNumber)] = _nSamples
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['MMACDSHORT_Master'] == True) and (self.objectConfig['MMACDSHORT_MA{:d}_LineActive'.format(lineNumber)] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'SignalIntervalTextInputBox'):    
                #Get new nSamples
                try:    _nSamples = int(self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_SIGNALINTERVALTEXTINPUT"].getText())
                except: _nSamples = None
                #Save the new value to the object config dictionary
                self.objectConfig['MMACDSHORT_SignalNSamples'] = _nSamples
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['MMACDSHORT_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'MultiplierTextInputBox'): 
                #Get new multiplier
                try:    _multiplier = int(self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_MULTIPLIERTEXTINPUT"].getText())
                except: _multiplier = None
                #Save the new value to the object config dictionary
                self.objectConfig['MMACDSHORT_Multiplier'] = _multiplier
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['MMACDSHORT_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True

        #Subpage 'MMACDLONG'
        elif (indicatorType == 'MMACDLONG'):
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'): 
                lineSelected = self.settingsSubPages['MMACDLONG'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_{:s}_COLOR".format(lineSelected)].getColor()
                self.settingsSubPages['MMACDLONG'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['MMACDLONG'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                self.settingsSubPages['MMACDLONG'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                self.settingsSubPages['MMACDLONG'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                self.settingsSubPages['MMACDLONG'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                self.settingsSubPages['MMACDLONG'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                self.settingsSubPages['MMACDLONG'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                self.settingsSubPages['MMACDLONG'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                self.settingsSubPages['MMACDLONG'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                self.settingsSubPages['MMACDLONG'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):          
                contentType = guioName_split[2]
                self.settingsSubPages['MMACDLONG'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(self.settingsSubPages['MMACDLONG'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                                            gValue = int(self.settingsSubPages['MMACDLONG'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                                            bValue = int(self.settingsSubPages['MMACDLONG'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                                            aValue = int(self.settingsSubPages['MMACDLONG'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                self.settingsSubPages['MMACDLONG'].GUIOs["INDICATORCOLOR_{:s}_VALUE".format(contentType)].updateText(str(int(self.settingsSubPages['MMACDLONG'].GUIOs['INDICATORCOLOR_{:s}_SLIDER'.format(contentType)].getSliderValue()*255/100)))
                self.settingsSubPages['MMACDLONG'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):     
                lineSelected = self.settingsSubPages['MMACDLONG'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(self.settingsSubPages['MMACDLONG'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(self.settingsSubPages['MMACDLONG'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(self.settingsSubPages['MMACDLONG'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(self.settingsSubPages['MMACDLONG'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_{:s}_COLOR".format(lineSelected)].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['MMACDLONG'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                self.settingsSubPages['MMACDLONG'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):  
                self.settingsSubPages['MMACDLONG'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):  
                #UpdateTracker Initialization
                updateTracker = [False, False, False] #[0]: Draw MMACD, [1]: Draw SIGNAL, [2]: Draw HISTOGRAM
                #Check for any changes in the configuration
                if (True):
                    #MMACDLONG Master
                    MMACDLONGMaster_previous = self.objectConfig['MMACDLONG_Master']
                    self.objectConfig['MMACDLONG_Master'] = self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_MMACDLONG"].getStatus()
                    if (MMACDLONGMaster_previous != self.objectConfig['MMACDLONG_Master']): 
                        updateTracker[0] = True
                        updateTracker[1] = True
                        updateTracker[2] = True
                    #Colors
                    for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM+', 'HISTOGRAM-'):
                        color_previous = (self.objectConfig['MMACDLONG_{:s}_ColorR%{:s}'.format(targetLine, self.currentGUITheme)],
                                          self.objectConfig['MMACDLONG_{:s}_ColorG%{:s}'.format(targetLine, self.currentGUITheme)],
                                          self.objectConfig['MMACDLONG_{:s}_ColorB%{:s}'.format(targetLine, self.currentGUITheme)],
                                          self.objectConfig['MMACDLONG_{:s}_ColorA%{:s}'.format(targetLine, self.currentGUITheme)])
                        color_r, color_g, color_b, color_a = self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_{:s}_COLOR".format(targetLine)].getColor()
                        self.objectConfig['MMACDLONG_{:s}_ColorR%{:s}'.format(targetLine, self.currentGUITheme)] = color_r
                        self.objectConfig['MMACDLONG_{:s}_ColorG%{:s}'.format(targetLine, self.currentGUITheme)] = color_g
                        self.objectConfig['MMACDLONG_{:s}_ColorB%{:s}'.format(targetLine, self.currentGUITheme)] = color_b
                        self.objectConfig['MMACDLONG_{:s}_ColorA%{:s}'.format(targetLine, self.currentGUITheme)] = color_a
                        if (color_previous != (color_r, color_g, color_b, color_a)): 
                            if   (targetLine == 'MMACD'):      updateTracker[0] = True
                            elif (targetLine == 'SIGNAL'):     updateTracker[1] = True
                            elif (targetLine == 'HISTOGRAM+'): updateTracker[2] = True
                            elif (targetLine == 'HISTOGRAM-'): updateTracker[2] = True
                    #Line Display
                    for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM'):
                        displayStatus_prev = self.objectConfig['MMACDLONG_{:s}_Display'.format(targetLine)]
                        self.objectConfig['MMACDLONG_{:s}_Display'.format(targetLine)] = self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_{:s}_DISPLAYSWITCH".format(targetLine)].getStatus()
                        if (displayStatus_prev != self.objectConfig['MMACDLONG_{:s}_Display'.format(targetLine)]):
                            if   (targetLine == 'MMACD'):     updateTracker[0] = True
                            elif (targetLine == 'SIGNAL'):    updateTracker[1] = True
                            elif (targetLine == 'HISTOGRAM'): updateTracker[2] = True
                #Queue Update
                drawSignal = 0
                drawSignal += 0b001*updateTracker[0] #MMACD
                drawSignal += 0b010*updateTracker[1] #SIGNAL
                drawSignal += 0b100*updateTracker[2] #HISTOGRAM
                if (drawSignal != 0): 
                    self.__klineDrawer_RemoveDrawings(analysisCode = 'MMACDLONG', gRemovalSignal = drawSignal) #Remove previous graphics
                    self.__addBufferZone_toDrawQueue(analysisCode = 'MMACDLONG', drawSignal = drawSignal)      #Update draw queue
                #Control Buttons Handling
                self.settingsSubPages['MMACDLONG'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'):          
                lineNumber = int(guioName_split[2])
                #Get new switch status
                _newStatus = self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_MMACDMA{:d}".format(lineNumber)].getStatus()
                self.objectConfig['MMACDLONG_MA{:d}_LineActive'.format(lineNumber)] = _newStatus
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['MMACDLONG_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'):          
                lineNumber = int(guioName_split[2])
                #Get new nSamples
                try:    _nSamples = int(self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_MMACDMA{:d}_INTERVALINPUT".format(lineNumber)].getText())
                except: _nSamples = None
                #Save the new value to the object config dictionary
                self.objectConfig['MMACDLONG_MA{:d}_NSamples'.format(lineNumber)] = _nSamples
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['MMACDLONG_Master'] == True) and (self.objectConfig['MMACDLONG_MA{:d}_LineActive'.format(lineNumber)] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'SignalIntervalTextInputBox'):    
                #Get new nSamples
                try:    _nSamples = int(self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_SIGNALINTERVALTEXTINPUT"].getText())
                except: _nSamples = None
                #Save the new value to the object config dictionary
                self.objectConfig['MMACDLONG_SignalNSamples'] = _nSamples
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['MMACDLONG_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'MultiplierTextInputBox'): 
                #Get new multiplier
                try:    _multiplier = int(self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_MULTIPLIERTEXTINPUT"].getText())
                except: _multiplier = None
                #Save the new value to the object config dictionary
                self.objectConfig['MMACDLONG_Multiplier'] = _multiplier
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['MMACDLONG_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True

        #Subpage 'DMIxADX'
        elif (indicatorType == 'DMIxADX'):
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):    
                lineSelected = self.settingsSubPages['DMIxADX'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:s}_LINECOLOR".format(lineSelected)].getColor()
                self.settingsSubPages['DMIxADX'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['DMIxADX'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                self.settingsSubPages['DMIxADX'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                self.settingsSubPages['DMIxADX'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                self.settingsSubPages['DMIxADX'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                self.settingsSubPages['DMIxADX'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                self.settingsSubPages['DMIxADX'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                self.settingsSubPages['DMIxADX'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                self.settingsSubPages['DMIxADX'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                self.settingsSubPages['DMIxADX'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):             
                contentType = guioName_split[2]
                self.settingsSubPages['DMIxADX'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(self.settingsSubPages['DMIxADX'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                                         gValue = int(self.settingsSubPages['DMIxADX'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                                         bValue = int(self.settingsSubPages['DMIxADX'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                                         aValue = int(self.settingsSubPages['DMIxADX'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                self.settingsSubPages['DMIxADX'].GUIOs["INDICATORCOLOR_{:s}_VALUE".format(contentType)].updateText(str(int(self.settingsSubPages['DMIxADX'].GUIOs['INDICATORCOLOR_{:s}_SLIDER'.format(contentType)].getSliderValue()*255/100)))
                self.settingsSubPages['DMIxADX'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):        
                lineSelected = self.settingsSubPages['DMIxADX'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(self.settingsSubPages['DMIxADX'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(self.settingsSubPages['DMIxADX'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(self.settingsSubPages['DMIxADX'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(self.settingsSubPages['DMIxADX'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:s}_LINECOLOR".format(lineSelected)].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['DMIxADX'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                self.settingsSubPages['DMIxADX'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'WidthTextInputBox'): 
                self.settingsSubPages['DMIxADX'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):     
                self.settingsSubPages['DMIxADX'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):     
                #UpdateTracker Initialization
                updateTracker = dict()
                #Check for any changes in the configuration
                if (True):
                    for lineIndex in range (_NMAXLINES['DMIxADX']):
                        lineNumber = lineIndex+1
                        updateTracker[lineNumber] = False
                        #Width
                        width_previous = self.objectConfig['DMIxADX_{:d}_Width'.format(lineNumber)]
                        reset = False
                        try:
                            width = int(self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_WIDTHINPUT".format(lineNumber)].getText())
                            if (0 < width): self.objectConfig['DMIxADX_{:d}_Width'.format(lineNumber)] = width
                            else: reset = True
                        except: reset = True
                        if (reset == True):
                            self.objectConfig['DMIxADX_{:d}_Width'.format(lineNumber)] = 1
                            self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_WIDTHINPUT".format(lineNumber)].updateText(str(self.objectConfig['DMIxADX_{:d}_Width'.format(lineNumber)]))
                        if (width_previous != self.objectConfig['DMIxADX_{:d}_Width'.format(lineNumber)]): updateTracker[lineNumber] = True
                        #Color
                        color_previous = (self.objectConfig['DMIxADX_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                            self.objectConfig['DMIxADX_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                            self.objectConfig['DMIxADX_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                            self.objectConfig['DMIxADX_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)])
                        color_r, color_g, color_b, color_a = self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_LINECOLOR".format(lineNumber)].getColor()
                        self.objectConfig['DMIxADX_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)] = color_r
                        self.objectConfig['DMIxADX_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)] = color_g
                        self.objectConfig['DMIxADX_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)] = color_b
                        self.objectConfig['DMIxADX_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)] = color_a
                        if (color_previous != (color_r, color_g, color_b, color_a)): updateTracker[lineNumber] = True
                        #Line Display
                        display_previous = self.objectConfig['DMIxADX_{:d}_Display'.format(lineNumber)]
                        self.objectConfig['DMIxADX_{:d}_Display'.format(lineNumber)] = self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_DISPLAY".format(lineNumber)].getStatus()
                        if (display_previous != self.objectConfig['DMIxADX_{:d}_Display'.format(lineNumber)]): updateTracker[lineNumber] = True
                    #DMIxADX Master
                    dmixadxMaster_previous = self.objectConfig['DMIxADX_Master']
                    self.objectConfig['DMIxADX_Master'] = self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_DMIxADX"].getStatus()
                    if (dmixadxMaster_previous != self.objectConfig['DMIxADX_Master']):
                        for lineNumber in updateTracker: updateTracker[lineNumber] = True
                #Queue Update
                configuredDMIxADXs = set([analysisCode for analysisCode in self.analysisParams if analysisCode[:7] == 'DMIxADX'])
                for configuredDMIxADX in configuredDMIxADXs:
                    lineNumber = self.analysisParams[configuredDMIxADX]['lineNumber']
                    if (updateTracker[lineNumber] == True):
                        self.__klineDrawer_RemoveDrawings(analysisCode = configuredDMIxADX, gRemovalSignal = _FULLDRAWSIGNALS['DMIxADX']) #Remove previous graphics
                        self.__addBufferZone_toDrawQueue(analysisCode = configuredDMIxADX, drawSignal = _FULLDRAWSIGNALS['DMIxADX'])      #Update draw queue
                #Control Buttons Handling
                self.settingsSubPages['DMIxADX'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'): 
                lineNumber = int(guioName_split[2])
                #Get new switch status
                _newStatus = self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}".format(lineNumber)].getStatus()
                self.objectConfig['DMIxADX_{:d}_LineActive'.format(lineNumber)] = _newStatus
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['DMIxADX_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'): 
                lineNumber = int(guioName_split[2])
                #Get new nSamples
                try:    _nSamples = int(self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_INTERVALINPUT".format(lineNumber)].getText())
                except: _nSamples = None
                #Save the new value to the object config dictionary
                self.objectConfig['DMIxADX_{:d}_NSamples'.format(lineNumber)] = _nSamples
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['DMIxADX_Master'] == True) and (self.objectConfig['DMIxADX_{:d}_LineActive'.format(lineNumber)] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True

        #Subpage 'MFI'
        elif (indicatorType == 'MFI'):
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):    
                lineSelected = self.settingsSubPages['MFI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:s}_LINECOLOR".format(lineSelected)].getColor()
                self.settingsSubPages['MFI'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['MFI'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                self.settingsSubPages['MFI'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                self.settingsSubPages['MFI'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                self.settingsSubPages['MFI'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                self.settingsSubPages['MFI'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                self.settingsSubPages['MFI'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                self.settingsSubPages['MFI'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                self.settingsSubPages['MFI'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                self.settingsSubPages['MFI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):             
                contentType = guioName_split[2]
                self.settingsSubPages['MFI'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(self.settingsSubPages['MFI'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                                     gValue = int(self.settingsSubPages['MFI'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                                     bValue = int(self.settingsSubPages['MFI'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                                     aValue = int(self.settingsSubPages['MFI'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                self.settingsSubPages['MFI'].GUIOs["INDICATORCOLOR_{:s}_VALUE".format(contentType)].updateText(str(int(self.settingsSubPages['MFI'].GUIOs['INDICATORCOLOR_{:s}_SLIDER'.format(contentType)].getSliderValue()*255/100)))
                self.settingsSubPages['MFI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):        
                lineSelected = self.settingsSubPages['MFI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(self.settingsSubPages['MFI'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(self.settingsSubPages['MFI'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(self.settingsSubPages['MFI'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(self.settingsSubPages['MFI'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:s}_LINECOLOR".format(lineSelected)].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['MFI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                self.settingsSubPages['MFI'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'WidthTextInputBox'): 
                self.settingsSubPages['MFI'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):     
                self.settingsSubPages['MFI'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):     
                #UpdateTracker Initialization
                updateTracker = dict()
                #Check for any changes in the configuration
                if (True):
                    for lineIndex in range (_NMAXLINES['MFI']):
                        lineNumber = lineIndex+1
                        updateTracker[lineNumber] = False
                        #Width
                        width_previous = self.objectConfig['MFI_{:d}_Width'.format(lineNumber)]
                        reset = False
                        try:
                            width = int(self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_WIDTHINPUT".format(lineNumber)].getText())
                            if (0 < width): self.objectConfig['MFI_{:d}_Width'.format(lineNumber)] = width
                            else: reset = True
                        except: reset = True
                        if (reset == True):
                            self.objectConfig['MFI_{:d}_Width'.format(lineNumber)] = 1
                            self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_WIDTHINPUT".format(lineNumber)].updateText(str(self.objectConfig['MFI_{:d}_Width'.format(lineNumber)]))
                        if (width_previous != self.objectConfig['MFI_{:d}_Width'.format(lineNumber)]): updateTracker[lineNumber] = True
                        #Color
                        color_previous = (self.objectConfig['MFI_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                          self.objectConfig['MFI_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                          self.objectConfig['MFI_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)], 
                                          self.objectConfig['MFI_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)])
                        color_r, color_g, color_b, color_a = self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_LINECOLOR".format(lineNumber)].getColor()
                        self.objectConfig['MFI_{:d}_ColorR%{:s}'.format(lineNumber,self.currentGUITheme)] = color_r
                        self.objectConfig['MFI_{:d}_ColorG%{:s}'.format(lineNumber,self.currentGUITheme)] = color_g
                        self.objectConfig['MFI_{:d}_ColorB%{:s}'.format(lineNumber,self.currentGUITheme)] = color_b
                        self.objectConfig['MFI_{:d}_ColorA%{:s}'.format(lineNumber,self.currentGUITheme)] = color_a
                        if (color_previous != (color_r, color_g, color_b, color_a)): updateTracker[lineNumber] = True
                        #Line Display
                        display_previous = self.objectConfig['MFI_{:d}_Display'.format(lineNumber)]
                        self.objectConfig['MFI_{:d}_Display'.format(lineNumber)] = self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_DISPLAY".format(lineNumber)].getStatus()
                        if (display_previous != self.objectConfig['MFI_{:d}_Display'.format(lineNumber)]): updateTracker[lineNumber] = True
                    #MFI Master
                    mfiMaster_previous = self.objectConfig['MFI_Master']
                    self.objectConfig['MFI_Master'] = self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_MFI"].getStatus()
                    if (mfiMaster_previous != self.objectConfig['MFI_Master']):
                        for lineNumber in updateTracker: updateTracker[lineNumber] = True
                #Queue Update
                configuredMFIs = set([analysisCode for analysisCode in self.analysisParams if analysisCode[:3] == 'MFI'])
                for configuredMFI in configuredMFIs:
                    lineNumber = self.analysisParams[configuredMFI]['lineNumber']
                    if (updateTracker[lineNumber] == True):
                        self.__klineDrawer_RemoveDrawings(analysisCode = configuredMFI, gRemovalSignal = _FULLDRAWSIGNALS['MFI']) #Remove previous graphics
                        self.__addBufferZone_toDrawQueue(analysisCode = configuredMFI, drawSignal = _FULLDRAWSIGNALS['MFI'])      #Update draw queue
                #Control Buttons Handling
                self.settingsSubPages['MFI'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'): 
                lineNumber = int(guioName_split[2])
                #Get new switch status
                _newStatus = self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}".format(lineNumber)].getStatus()
                self.objectConfig['MFI_{:d}_LineActive'.format(lineNumber)] = _newStatus
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['MFI_Master'] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'): 
                lineNumber = int(guioName_split[2])
                #Get new nSamples
                try:    _nSamples = int(self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_INTERVALINPUT".format(lineNumber)].getText())
                except: _nSamples = None
                #Save the new value to the object config dictionary
                self.objectConfig['MFI_{:d}_NSamples'.format(lineNumber)] = _nSamples
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER') and (self.canStartAnalysis == True) and (self.objectConfig['MFI_Master'] == True) and (self.objectConfig['MFI_{:d}_LineActive'.format(lineNumber)] == True)): self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True

        #Subpage 'WOI'
        elif (indicatorType == 'WOI'):
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):    
                lineSelected = self.settingsSubPages['WOI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:s}_LINECOLOR".format(lineSelected)].getColor()
                self.settingsSubPages['WOI'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['WOI'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                self.settingsSubPages['WOI'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                self.settingsSubPages['WOI'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                self.settingsSubPages['WOI'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                self.settingsSubPages['WOI'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                self.settingsSubPages['WOI'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                self.settingsSubPages['WOI'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                self.settingsSubPages['WOI'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                self.settingsSubPages['WOI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):             
                contentType = guioName_split[2]
                self.settingsSubPages['WOI'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(self.settingsSubPages['WOI'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                                     gValue = int(self.settingsSubPages['WOI'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                                     bValue = int(self.settingsSubPages['WOI'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                                     aValue = int(self.settingsSubPages['WOI'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                self.settingsSubPages['WOI'].GUIOs["INDICATORCOLOR_{:s}_VALUE".format(contentType)].updateText(str(int(self.settingsSubPages['WOI'].GUIOs['INDICATORCOLOR_{:s}_SLIDER'.format(contentType)].getSliderValue()*255/100)))
                self.settingsSubPages['WOI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):        
                lineSelected = self.settingsSubPages['WOI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(self.settingsSubPages['WOI'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(self.settingsSubPages['WOI'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(self.settingsSubPages['WOI'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(self.settingsSubPages['WOI'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:s}_LINECOLOR".format(lineSelected)].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['WOI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                self.settingsSubPages['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'WidthTextInputBox'): 
                self.settingsSubPages['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):     
                self.settingsSubPages['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'): 
                self.settingsSubPages['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'IntervalTextInputBox'): 
                self.settingsSubPages['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'SigmaTextInputBox'): 
                self.settingsSubPages['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
            #Both
            elif (setterType == 'ApplySettings'):     
                #UpdateTracker Initialization
                updateTracker = {'BASE': False}
                #Check for any changes in the configuration
                if (True):
                    #---[1]: Base
                    #------Line Activation
                    _display_prev = self.objectConfig['WOI_BASE_Display']
                    self.objectConfig['WOI_BASE_Display'] = self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOIBASE_DISPLAYSWITCH"].getStatus()
                    if (_display_prev != self.objectConfig['WOI_BASE_Display']): updateTracker['BASE'] = True
                    #------Colors
                    for _target in ('BASE+', 'BASE-'):
                        color_previous = (self.objectConfig['WOI_{:s}_ColorR%{:s}'.format(_target, self.currentGUITheme)],
                                          self.objectConfig['WOI_{:s}_ColorG%{:s}'.format(_target, self.currentGUITheme)],
                                          self.objectConfig['WOI_{:s}_ColorB%{:s}'.format(_target, self.currentGUITheme)],
                                          self.objectConfig['WOI_{:s}_ColorA%{:s}'.format(_target, self.currentGUITheme)])
                        color_r, color_g, color_b, color_a = self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:s}_LINECOLOR".format(_target)].getColor()
                        self.objectConfig['WOI_{:s}_ColorR%{:s}'.format(_target, self.currentGUITheme)] = color_r
                        self.objectConfig['WOI_{:s}_ColorG%{:s}'.format(_target, self.currentGUITheme)] = color_g
                        self.objectConfig['WOI_{:s}_ColorB%{:s}'.format(_target, self.currentGUITheme)] = color_b
                        self.objectConfig['WOI_{:s}_ColorA%{:s}'.format(_target, self.currentGUITheme)] = color_a
                        if (color_previous != (color_r, color_g, color_b, color_a)): updateTracker['BASE'] = True
                    #---[2]: Gaussian Deltas
                    for _lIndex in range (_NMAXLINES['WOI']):
                        _lNumber = _lIndex+1
                        updateTracker[_lNumber] = [False, False]
                        if (self.chartDrawerType == 'ANALYZER'):
                            #------Line Activation
                            _status_prev = self.objectConfig['WOI_{:d}_LineActive'.format(_lNumber)]
                            _status_new  = self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}".format(_lNumber)].getStatus()
                            if (_status_prev != _status_new):
                                self.objectConfig['WOI_{:d}_LineActive'.format(_lNumber)] = _status_new
                                updateTracker[_lNumber][0] = True
                            #------Interval
                            _nSamples_prev = self.objectConfig['WOI_{:d}_NSamples'.format(_lNumber)]
                            try:    _nSamples_new = int(self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_INTERVALINPUT".format(_lNumber)].getText())
                            except: _nSamples_new = None
                            if (_nSamples_new == None):
                                _nSamples_new = 10*_lNumber
                            if (_nSamples_prev != _nSamples_new):
                                self.objectConfig['WOI_{:d}_NSamples'.format(_lNumber)] = _nSamples_new
                                updateTracker[_lNumber][0] = True
                            self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_INTERVALINPUT".format(_lNumber)].updateText(text = "{:d}".format(_nSamples_new))
                            #------Sigma
                            _sigma_prev = self.objectConfig['WOI_{:d}_Sigma'.format(_lNumber)]
                            try:    _sigma_new = round(float(self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_SIGMAINPUT".format(_lNumber)].getText()), 1)
                            except: _sigma_new = None
                            if (_sigma_new == None):
                                _sigma_new = 2.0
                            if (_sigma_prev != _sigma_new):
                                self.objectConfig['WOI_{:d}_Sigma'.format(_lNumber)] = _sigma_new
                                updateTracker[_lNumber][0] = True
                            self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_SIGMAINPUT".format(_lNumber)].updateText(text = "{:.1f}".format(_sigma_new))
                        #------Width
                        width_previous = self.objectConfig['WOI_{:d}_Width'.format(_lNumber)]
                        reset = False
                        try:
                            width = int(self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_WIDTHINPUT".format(_lNumber)].getText())
                            if (0 < width): self.objectConfig['WOI_{:d}_Width'.format(_lNumber)] = width
                            else: reset = True
                        except: reset = True
                        if (reset == True): self.objectConfig['WOI_{:d}_Width'.format(_lNumber)] = 1
                        if (width_previous != self.objectConfig['WOI_{:d}_Width'.format(_lNumber)]): updateTracker[_lNumber][1] = True
                        self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_WIDTHINPUT".format(_lNumber)].updateText(str(self.objectConfig['WOI_{:d}_Width'.format(_lNumber)]))
                        #------Color
                        color_previous = (self.objectConfig['WOI_{:d}_ColorR%{:s}'.format(_lNumber,self.currentGUITheme)], 
                                          self.objectConfig['WOI_{:d}_ColorG%{:s}'.format(_lNumber,self.currentGUITheme)], 
                                          self.objectConfig['WOI_{:d}_ColorB%{:s}'.format(_lNumber,self.currentGUITheme)], 
                                          self.objectConfig['WOI_{:d}_ColorA%{:s}'.format(_lNumber,self.currentGUITheme)])
                        color_r, color_g, color_b, color_a = self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_LINECOLOR".format(_lNumber)].getColor()
                        self.objectConfig['WOI_{:d}_ColorR%{:s}'.format(_lNumber,self.currentGUITheme)] = color_r
                        self.objectConfig['WOI_{:d}_ColorG%{:s}'.format(_lNumber,self.currentGUITheme)] = color_g
                        self.objectConfig['WOI_{:d}_ColorB%{:s}'.format(_lNumber,self.currentGUITheme)] = color_b
                        self.objectConfig['WOI_{:d}_ColorA%{:s}'.format(_lNumber,self.currentGUITheme)] = color_a
                        if (color_previous != (color_r, color_g, color_b, color_a)): updateTracker[_lNumber][1] = True
                        #------Line Display
                        display_previous = self.objectConfig['WOI_{:d}_Display'.format(_lNumber)]
                        self.objectConfig['WOI_{:d}_Display'.format(_lNumber)] = self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_DISPLAY".format(_lNumber)].getStatus()
                        if (display_previous != self.objectConfig['WOI_{:d}_Display'.format(_lNumber)]): updateTracker[_lNumber][1] = True
                    #---[3]: WOI Master
                    WOIMaster_previous = self.objectConfig['WOI_Master']
                    self.objectConfig['WOI_Master'] = self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_WOI"].getStatus()
                    if (WOIMaster_previous != self.objectConfig['WOI_Master']):
                        for _line in updateTracker: 
                            if (_line == 'BASE'): updateTracker[_line] = True
                            else:                 updateTracker[_line] = [True, True]
                #Control Variables Update
                if (self.chartDrawerType == 'ANALYZER'):
                    self.siTypes_analysisCodes['WOI'] = list()
                    for _lIndex in range (_NMAXLINES['WOI']):
                        _lNumber = _lIndex+1
                        _woiType = "WOI_{:d}".format(_lNumber)
                        if (self.objectConfig['WOI_{:d}_LineActive'.format(_lNumber)] == True): 
                            self.siTypes_analysisCodes['WOI'].append(_woiType)
                            if (updateTracker[_lNumber][0] == True): self.bidsAndAsks[_woiType] = dict()
                        elif (_woiType in self.bidsAndAsks): del self.bidsAndAsks[_woiType]
                #Reprocess & Queue Update
                _isMasterOn = self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_WOI"].getStatus()
                #---[1]: Base
                if (updateTracker['BASE'] == True):
                    #Remove previous graphics
                    self.__WOIDrawer_RemoveDrawings(woiType = 'WOI')
                    #Draw Queue
                    if ((_isMasterOn == True) and (self.objectConfig['WOI_BASE_Display'] == True)):
                        for _tt in self.bidsAndAsks['WOI']:
                            if (_tt in self.bidsAndAsks_WOI_drawQueue): self.bidsAndAsks_WOI_drawQueue[_tt].add('WOI')
                            else:                                       self.bidsAndAsks_WOI_drawQueue[_tt] = {'WOI',}
                #---[2]: Gaussian Deltas
                for _lIndex in range (_NMAXLINES['WOI']):
                    _lNumber = _lIndex+1
                    _woiType = "WOI_{:d}".format(_lNumber)
                    if ((updateTracker[_lNumber][0] == True) or (updateTracker[_lNumber][1] == True)):
                        #Remove previous graphics
                        self.__WOIDrawer_RemoveDrawings(woiType = _woiType)
                        #Line Status
                        _isActive   = ((_isMasterOn == True) and (self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}".format(_lNumber)].getStatus()))
                        _isVisible  = ((_isMasterOn == True) and (_isActive == True) and (self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_DISPLAY".format(_lNumber)].getStatus()))
                        #Reprocess (If needed)
                        if ((self.chartDrawerType == 'ANALYZER') and (_isActive == True) and (updateTracker[_lNumber][0] == True)):
                            _nSamples  = self.objectConfig['WOI_{:d}_NSamples'.format(_lNumber)]
                            _sigma     = self.objectConfig['WOI_{:d}_Sigma'.format(_lNumber)]
                            _targetTTs = list(self.bidsAndAsks['WOI'].keys()); _targetTTs.sort()
                            for _tt in _targetTTs: atmEta_Analyzers.generateAnalysis_WOI(bidsAndAsks = self.bidsAndAsks, woiType = _woiType, nSamples = _nSamples, sigma = _sigma, targetTime = _tt)
                        #Draw Queue
                        if (_isVisible == True):
                            for _tt in self.bidsAndAsks[_woiType]:
                                if (_tt in self.bidsAndAsks_WOI_drawQueue): self.bidsAndAsks_WOI_drawQueue[_tt].add(_woiType)
                                else:                                       self.bidsAndAsks_WOI_drawQueue[_tt] = {_woiType,}
                #Control Buttons Handling
                self.settingsSubPages['WOI'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True

        #Subpage 'NES'
        elif (indicatorType == 'NES'):
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):    
                lineSelected = self.settingsSubPages['NES'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:s}_LINECOLOR".format(lineSelected)].getColor()
                self.settingsSubPages['NES'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['NES'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                self.settingsSubPages['NES'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                self.settingsSubPages['NES'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                self.settingsSubPages['NES'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                self.settingsSubPages['NES'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                self.settingsSubPages['NES'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                self.settingsSubPages['NES'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                self.settingsSubPages['NES'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                self.settingsSubPages['NES'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):             
                contentType = guioName_split[2]
                self.settingsSubPages['NES'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(self.settingsSubPages['NES'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                                     gValue = int(self.settingsSubPages['NES'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                                     bValue = int(self.settingsSubPages['NES'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                                     aValue = int(self.settingsSubPages['NES'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                self.settingsSubPages['NES'].GUIOs["INDICATORCOLOR_{:s}_VALUE".format(contentType)].updateText(str(int(self.settingsSubPages['NES'].GUIOs['INDICATORCOLOR_{:s}_SLIDER'.format(contentType)].getSliderValue()*255/100)))
                self.settingsSubPages['NES'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):        
                lineSelected = self.settingsSubPages['NES'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(self.settingsSubPages['NES'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(self.settingsSubPages['NES'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(self.settingsSubPages['NES'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(self.settingsSubPages['NES'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:s}_LINECOLOR".format(lineSelected)].updateColor(color_r, color_g, color_b, color_a)
                self.settingsSubPages['NES'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                self.settingsSubPages['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'WidthTextInputBox'): 
                self.settingsSubPages['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):     
                self.settingsSubPages['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'): 
                self.settingsSubPages['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'IntervalTextInputBox'): 
                self.settingsSubPages['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'SigmaTextInputBox'): 
                self.settingsSubPages['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
            #Both
            elif (setterType == 'ApplySettings'):     
                #UpdateTracker Initialization
                updateTracker = {'BASE': False}
                #Check for any changes in the configuration
                if (True):
                    #---[1]: Base
                    #------Line Activation
                    _display_prev = self.objectConfig['NES_BASE_Display']
                    self.objectConfig['NES_BASE_Display'] = self.settingsSubPages['NES'].GUIOs["INDICATOR_NESBASE_DISPLAYSWITCH"].getStatus()
                    if (_display_prev != self.objectConfig['NES_BASE_Display']): updateTracker['BASE'] = True
                    #------Colors
                    for _target in ('BASE+', 'BASE-'):
                        color_previous = (self.objectConfig['NES_{:s}_ColorR%{:s}'.format(_target, self.currentGUITheme)],
                                          self.objectConfig['NES_{:s}_ColorG%{:s}'.format(_target, self.currentGUITheme)],
                                          self.objectConfig['NES_{:s}_ColorB%{:s}'.format(_target, self.currentGUITheme)],
                                          self.objectConfig['NES_{:s}_ColorA%{:s}'.format(_target, self.currentGUITheme)])
                        color_r, color_g, color_b, color_a = self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:s}_LINECOLOR".format(_target)].getColor()
                        self.objectConfig['NES_{:s}_ColorR%{:s}'.format(_target, self.currentGUITheme)] = color_r
                        self.objectConfig['NES_{:s}_ColorG%{:s}'.format(_target, self.currentGUITheme)] = color_g
                        self.objectConfig['NES_{:s}_ColorB%{:s}'.format(_target, self.currentGUITheme)] = color_b
                        self.objectConfig['NES_{:s}_ColorA%{:s}'.format(_target, self.currentGUITheme)] = color_a
                        if (color_previous != (color_r, color_g, color_b, color_a)): updateTracker['BASE'] = True
                    #---[2]: Gaussian Deltas
                    for _lIndex in range (_NMAXLINES['NES']):
                        _lNumber = _lIndex+1
                        updateTracker[_lNumber] = [False, False]
                        if (self.chartDrawerType == 'ANALYZER'):
                            #------Line Activation
                            _status_prev = self.objectConfig['NES_{:d}_LineActive'.format(_lNumber)]
                            _status_new  = self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}".format(_lNumber)].getStatus()
                            if (_status_prev != _status_new):
                                self.objectConfig['NES_{:d}_LineActive'.format(_lNumber)] = _status_new
                                updateTracker[_lNumber][0] = True
                            #------Interval
                            _nSamples_prev = self.objectConfig['NES_{:d}_NSamples'.format(_lNumber)]
                            try:    _nSamples_new = int(self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_INTERVALINPUT".format(_lNumber)].getText())
                            except: _nSamples_new = None
                            if (_nSamples_new == None):
                                _nSamples_new = 10*_lNumber
                            if (_nSamples_prev != _nSamples_new):
                                self.objectConfig['NES_{:d}_NSamples'.format(_lNumber)] = _nSamples_new
                                updateTracker[_lNumber][0] = True
                            self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_INTERVALINPUT".format(_lNumber)].updateText(text = "{:d}".format(_nSamples_new))
                            #------Sigma
                            _sigma_prev = self.objectConfig['NES_{:d}_Sigma'.format(_lNumber)]
                            try:    _sigma_new = round(float(self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_SIGMAINPUT".format(_lNumber)].getText()), 1)
                            except: _sigma_new = None
                            if (_sigma_new == None):
                                _sigma_new = 2.0
                            if (_sigma_prev != _sigma_new):
                                self.objectConfig['NES_{:d}_Sigma'.format(_lNumber)] = _sigma_new
                                updateTracker[_lNumber][0] = True
                            self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_SIGMAINPUT".format(_lNumber)].updateText(text = "{:.1f}".format(_sigma_new))
                        #------Width
                        width_previous = self.objectConfig['NES_{:d}_Width'.format(_lNumber)]
                        reset = False
                        try:
                            width = int(self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_WIDTHINPUT".format(_lNumber)].getText())
                            if (0 < width): self.objectConfig['NES_{:d}_Width'.format(_lNumber)] = width
                            else: reset = True
                        except: reset = True
                        if (reset == True): self.objectConfig['NES_{:d}_Width'.format(_lNumber)] = 1
                        if (width_previous != self.objectConfig['NES_{:d}_Width'.format(_lNumber)]): updateTracker[_lNumber][1] = True
                        self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_WIDTHINPUT".format(_lNumber)].updateText(str(self.objectConfig['NES_{:d}_Width'.format(_lNumber)]))
                        #------Color
                        color_previous = (self.objectConfig['NES_{:d}_ColorR%{:s}'.format(_lNumber,self.currentGUITheme)], 
                                          self.objectConfig['NES_{:d}_ColorG%{:s}'.format(_lNumber,self.currentGUITheme)], 
                                          self.objectConfig['NES_{:d}_ColorB%{:s}'.format(_lNumber,self.currentGUITheme)], 
                                          self.objectConfig['NES_{:d}_ColorA%{:s}'.format(_lNumber,self.currentGUITheme)])
                        color_r, color_g, color_b, color_a = self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_LINECOLOR".format(_lNumber)].getColor()
                        self.objectConfig['NES_{:d}_ColorR%{:s}'.format(_lNumber,self.currentGUITheme)] = color_r
                        self.objectConfig['NES_{:d}_ColorG%{:s}'.format(_lNumber,self.currentGUITheme)] = color_g
                        self.objectConfig['NES_{:d}_ColorB%{:s}'.format(_lNumber,self.currentGUITheme)] = color_b
                        self.objectConfig['NES_{:d}_ColorA%{:s}'.format(_lNumber,self.currentGUITheme)] = color_a
                        if (color_previous != (color_r, color_g, color_b, color_a)): updateTracker[_lNumber][1] = True
                        #------Line Display
                        display_previous = self.objectConfig['NES_{:d}_Display'.format(_lNumber)]
                        self.objectConfig['NES_{:d}_Display'.format(_lNumber)] = self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_DISPLAY".format(_lNumber)].getStatus()
                        if (display_previous != self.objectConfig['NES_{:d}_Display'.format(_lNumber)]): updateTracker[_lNumber][1] = True
                    #---[3]: NES Master
                    NESMaster_previous = self.objectConfig['NES_Master']
                    self.objectConfig['NES_Master'] = self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_NES"].getStatus()
                    if (NESMaster_previous != self.objectConfig['NES_Master']):
                        for _line in updateTracker: 
                            if (_line == 'BASE'): updateTracker[_line] = True
                            else:                 updateTracker[_line] = [True, True]
                #Control Variables Update
                if (self.chartDrawerType == 'ANALYZER'):
                    self.siTypes_analysisCodes['NES'] = list()
                    for _lIndex in range (_NMAXLINES['NES']):
                        _lNumber = _lIndex+1
                        _nesType = "NES_{:d}".format(_lNumber)
                        if (self.objectConfig['NES_{:d}_LineActive'.format(_lNumber)] == True): 
                            self.siTypes_analysisCodes['NES'].append(_nesType)
                            if (updateTracker[_lNumber][0] == True): self.aggTrades[_nesType] = dict()
                        elif (_nesType in self.aggTrades): del self.aggTrades[_nesType]
                #Reprocess & Queue Update
                _isMasterOn = self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_NES"].getStatus()
                #---[1]: Base
                if (updateTracker['BASE'] == True):
                    #Remove previous graphics
                    self.__NESDrawer_RemoveDrawings(nesType = 'NES')
                    #Draw Queue
                    if ((_isMasterOn == True) and (self.objectConfig['NES_BASE_Display'] == True)):
                        for _tt in self.aggTrades['NES']:
                            if (_tt in self.aggTrades_NES_drawQueue): self.aggTrades_NES_drawQueue[_tt].add('NES')
                            else:                                     self.aggTrades_NES_drawQueue[_tt] = {'NES',}
                #---[2]: Gaussian Deltas
                for _lIndex in range (_NMAXLINES['NES']):
                    _lNumber = _lIndex+1
                    _nesType = "NES_{:d}".format(_lNumber)
                    if ((updateTracker[_lNumber][0] == True) or (updateTracker[_lNumber][1] == True)):
                        #Remove previous graphics
                        self.__NESDrawer_RemoveDrawings(nesType = _nesType)
                        #Line Status
                        _isActive   = ((_isMasterOn == True) and (self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}".format(_lNumber)].getStatus()))
                        _isVisible  = ((_isMasterOn == True) and (_isActive == True) and (self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_DISPLAY".format(_lNumber)].getStatus()))
                        #Reprocess (If needed)
                        if ((self.chartDrawerType == 'ANALYZER') and (_isActive == True) and (updateTracker[_lNumber][0] == True)):
                            _nSamples  = self.objectConfig['NES_{:d}_NSamples'.format(_lNumber)]
                            _sigma     = self.objectConfig['NES_{:d}_Sigma'.format(_lNumber)]
                            _targetTTs = list(self.aggTrades['NES'].keys()); _targetTTs.sort()
                            for _tt in _targetTTs: atmEta_Analyzers.generateAnalysis_NES(aggTrades = self.aggTrades, nesType = _nesType, nSamples = _nSamples, sigma = _sigma, targetTime = _tt)
                        #Draw Queue
                        if (_isVisible == True):
                            for _tt in self.aggTrades[_nesType]:
                                if (_tt in self.aggTrades_NES_drawQueue): self.aggTrades_NES_drawQueue[_tt].add(_nesType)
                                else:                                     self.aggTrades_NES_drawQueue[_tt] = {_nesType,}
                #Control Buttons Handling
                self.settingsSubPages['NES'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True

        if ((activateSaveConfigButton == True) and (self.settingsSubPages['MAIN'].GUIOs["AUX_SAVECONFIGURATION"].deactivated == True)): self.settingsSubPages['MAIN'].GUIOs["AUX_SAVECONFIGURATION"].activate()

    def __addBufferZone_toDrawQueue(self, analysisCode, drawSignal):
        if (analysisCode in self.klines):
            for _ts in self.horizontalViewRange_timestampsInViewRange.union(self.horizontalViewRange_timestampsInBufferZone):
                if (_ts in self.klines[analysisCode]):
                    if (_ts in self.klines_drawQueue):
                        if (analysisCode in self.klines_drawQueue[_ts]): 
                            if (self.klines_drawQueue[_ts][analysisCode] != None): self.klines_drawQueue[_ts][analysisCode] |= drawSignal
                        else:                                                      self.klines_drawQueue[_ts][analysisCode] = drawSignal
                    else:                                                          self.klines_drawQueue[_ts] = {analysisCode: drawSignal}

    def __addALLWOI_toDrawQueue(self):
        _aCodesToConsider = ['WOI',] + [_aCode for _aCode in self.siTypes_analysisCodes['WOI'] if (self.objectConfig['WOI_{:d}_Display'.format(int(_aCode.split("_")[1]))] == True)]
        for _baaDataType in _aCodesToConsider:
            for _tt in self.bidsAndAsks[_baaDataType]:
                if (_tt in self.bidsAndAsks_WOI_drawQueue): self.bidsAndAsks_WOI_drawQueue[_tt].add(_baaDataType)
                else:                                       self.bidsAndAsks_WOI_drawQueue[_tt] = {_baaDataType,}

    def __addALLNES_toDrawQueue(self):
        _aCodesToConsider = ['NES',] + [_aCode for _aCode in self.siTypes_analysisCodes['NES'] if (self.objectConfig['NES_{:d}_Display'.format(int(_aCode.split("_")[1]))] == True)]
        for _atDataType in _aCodesToConsider:
            for _tt in self.aggTrades[_atDataType]:
                if (_tt in self.aggTrades_NES_drawQueue): self.aggTrades_NES_drawQueue[_tt].add(_atDataType)
                else:                                     self.aggTrades_NES_drawQueue[_tt] = {_atDataType,}

    def updateKlineColors(self, newType):
        if ((newType == 1) or (newType == 2)):
            self.objectConfig['KlineColorType'] = newType
            self.settingsSubPages['MAIN'].GUIOs["AUX_KLINECOLORTYPE_SELECTIONBOX"].setSelected(self.objectConfig['KlineColorType'], callSelectionUpdateFunction = False)
            for _ts in self.klines_drawn:
                if ('KLINE' in self.klines_drawn[_ts]):
                    if (_ts in self.klines_drawQueue): self.klines_drawQueue[_ts]['KLINE'] = None
                    else:                              self.klines_drawQueue[_ts] = {'KLINE': None}
                if ('VOL' in self.klines_drawn[_ts]):
                    if (_ts in self.klines_drawQueue): self.klines_drawQueue[_ts]['VOL'] = None
                    else:                              self.klines_drawQueue[_ts] = {'VOL': None}
            return True
        else: return False
        
    def updateTimeZone(self, newTimeZone):
        self.objectConfig['TimeZone'] = newTimeZone
        if   (newTimeZone     == 'LOCAL'): self.timezoneDelta = -time.timezone
        elif (newTimeZone[:3] == 'UTC'):   self.timezoneDelta = int(newTimeZone.split("+")[1])*3600
        #Update vertical grid texts (Temporal Texts)
        for index in range (len(self.verticalGrid_intervals)):
            timestamp_display = self.verticalGrid_intervals[index] + self.timezoneDelta
            #Grid Text
            if (self.verticalGrid_intervalID <= 10):
                if (timestamp_display % 86400 != 0): dateStrFormat = "%H:%M"
                else:                                dateStrFormat = "%m/%d"
            else:
                if (atmEta_Auxillaries.isNewMonth(timestamp_display) == True): dateStrFormat = "%Y/%m"
                else:                                                          dateStrFormat = "%m/%d"
            self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS'][index].setText(datetime.fromtimestamp(timestamp_display, tz = timezone.utc).strftime(dateStrFormat))
            self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS'][index].moveTo(x = self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS'][index].xPos)
    #Configuration Update Control END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Kline Drawing --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __klineDrawer_sendDrawSignals(self, timestamp, analysisCode, redraw = False):
        try:
            if (redraw == True): drawSignal = None
            else:                drawSignal = self.klines_drawQueue[timestamp][analysisCode]
            drawn = self.__klines_drawerFunctions[analysisCode.split("_")[0]](drawSignal = drawSignal, timestamp = timestamp, analysisCode = analysisCode)
            if (0 < drawn):
                if (timestamp in self.klines_drawn):
                    if (analysisCode in self.klines_drawn[timestamp]): self.klines_drawn[timestamp][analysisCode] |= drawn
                    else:                                              self.klines_drawn[timestamp][analysisCode] = drawn
                else:                                                  self.klines_drawn[timestamp] = {analysisCode: drawn}
        except Exception as e: print(termcolor.colored("An unexpected error occured while attempting to draw {:s} at {:d}\n *".format(analysisCode, timestamp), 'light_yellow'), termcolor.colored(e, 'light_yellow'))

    def __klineDrawer_KLINE(self, drawSignal, timestamp, analysisCode):
        if (timestamp in self.klines['raw']):
            kline_raw = self.klines['raw'][timestamp]
            ts_open  = kline_raw[0]
            ts_close = kline_raw[1]
            p_open   = kline_raw[2]
            p_high   = kline_raw[3]
            p_low    = kline_raw[4]
            p_close  = kline_raw[5]
            #Width determination
            tsWidth = ts_close-ts_open+1
            body_width = round(tsWidth*0.9, 1)
            body_xPos  = round(ts_open+(tsWidth-body_width)/2, 1)
            tail_width = round(tsWidth/5, 1)
            tail_xPos  = round(ts_open+(tsWidth-tail_width)/2, 1)
            #Color & Height determination
            if (p_open < p_close): #Incremental
                candleColor = self.visualManager.getFromColorTable('CHARTDRAWER_KLINECOLOR_TYPE{:d}_INCREMENTAL'.format(self.objectConfig['KlineColorType']))
                body_height = p_close-p_open
                body_bottom = p_open
            elif (p_open > p_close): #Decremental
                candleColor = self.visualManager.getFromColorTable('CHARTDRAWER_KLINECOLOR_TYPE{:d}_DECREMENTAL'.format(self.objectConfig['KlineColorType']))
                body_height = p_open-p_close
                body_bottom = p_close
            else: #Neutral
                candleColor = self.visualManager.getFromColorTable('CHARTDRAWER_KLINECOLOR_TYPE{:d}_NEUTRAL'.format(self.objectConfig['KlineColorType']))
                body_height = 0
                body_bottom = p_close
            tail_height = p_high-p_low
            tail_bottom = p_low
            #Drawing
            if (0 < body_height): self.displayBox_graphics['KLINESPRICE']['RCLCG'].addShape_Rectangle(x = body_xPos, y = body_bottom, width = body_width, height = body_height, color = candleColor, shapeName = ts_open, shapeGroupName = 'KLINEBODIES', layerNumber = 10)
            else:                 self.displayBox_graphics['KLINESPRICE']['RCLCG'].addShape_Line(x = body_xPos, y = body_bottom, x2 = body_xPos+body_width, y2 = body_bottom, color = candleColor, width_y = 1, shapeName = ts_open, shapeGroupName = 'KLINEBODIES', layerNumber = 10)
            self.displayBox_graphics['KLINESPRICE']['RCLCG'].addShape_Rectangle(x = tail_xPos, y = tail_bottom, width = tail_width, height = tail_height, color = candleColor, shapeName = ts_open, shapeGroupName = 'KLINETAILS', layerNumber = 10)
            return 0b1
        return 0b0

    def __klineDrawer_SMA(self, drawSignal, timestamp, analysisCode):
        drawn = 0b0
        if (self.objectConfig['SMA_Master'] == True):
            _analysisParams = self.analysisParams[analysisCode]
            if (self.objectConfig['SMA_{:d}_Display'.format(_analysisParams['lineNumber'])] == True):
                if (drawSignal == None): drawSignal = 0b1
                if (0 < drawSignal):
                    #Previous Drawing Removal
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
                    #Data Acquisition & Check
                    timestamp_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
                    if (timestamp_prev in self.klines[analysisCode]): smaResult_prev = self.klines[analysisCode][timestamp_prev]
                    else:                                             smaResult_prev = None
                    if ((smaResult_prev != None) and (smaResult_prev['SMA'] != None)):
                        smaResult = self.klines[analysisCode][timestamp]
                        #Coordinate Determination
                        timestampWidth = timestamp-timestamp_prev
                        shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                        shape_x2 = round(timestamp     +timestampWidth/2, 1)
                        shape_y1 = smaResult_prev['SMA']
                        shape_y2 = smaResult['SMA']
                        #Drawing
                        self.displayBox_graphics['KLINESPRICE']['RCLCG'].addShape_Line(x  = shape_x1, y  = shape_y1, 
                                                                                       x2 = shape_x2, y2 = shape_y2,
                                                                                       color = (self.objectConfig['SMA_{:d}_ColorR%{:s}'.format(_analysisParams['lineNumber'], self.currentGUITheme)],
                                                                                                self.objectConfig['SMA_{:d}_ColorG%{:s}'.format(_analysisParams['lineNumber'], self.currentGUITheme)],
                                                                                                self.objectConfig['SMA_{:d}_ColorB%{:s}'.format(_analysisParams['lineNumber'], self.currentGUITheme)],
                                                                                                self.objectConfig['SMA_{:d}_ColorA%{:s}'.format(_analysisParams['lineNumber'], self.currentGUITheme)]),
                                                                                       width_y = self.objectConfig['SMA_{:d}_Width'.format(_analysisParams['lineNumber'])]*2,
                                                                                       shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = _analysisParams['lineNumber']-1)
                    drawn += 0b1
        return drawn

    def __klineDrawer_WMA(self, drawSignal, timestamp, analysisCode):
        drawn = 0b0
        if (self.objectConfig['WMA_Master'] == True):
            _analysisParams = self.analysisParams[analysisCode]
            if (self.objectConfig['WMA_{:d}_Display'.format(_analysisParams['lineNumber'])] == True):
                if (drawSignal == None): drawSignal = 0b1
                if (0 < drawSignal):
                    #Previous Drawing Removal
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
                    #Data Acquisition & Check
                    timestamp_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
                    if (timestamp_prev in self.klines[analysisCode]): wmaResult_prev = self.klines[analysisCode][timestamp_prev]
                    else:                                             wmaResult_prev = None
                    if ((wmaResult_prev != None) and (wmaResult_prev['WMA'] != None)):
                        wmaResult = self.klines[analysisCode][timestamp]
                        #Coordinate Determination
                        timestampWidth = timestamp-timestamp_prev
                        shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                        shape_x2 = round(timestamp     +timestampWidth/2, 1)
                        shape_y1 = wmaResult_prev['WMA']
                        shape_y2 = wmaResult['WMA']
                        #Drawing
                        self.displayBox_graphics['KLINESPRICE']['RCLCG'].addShape_Line(x  = shape_x1, y  = shape_y1, 
                                                                                        x2 = shape_x2, y2 = shape_y2,
                                                                                        color = (self.objectConfig['WMA_{:d}_ColorR%{:s}'.format(_analysisParams['lineNumber'], self.currentGUITheme)],
                                                                                                self.objectConfig['WMA_{:d}_ColorG%{:s}'.format(_analysisParams['lineNumber'], self.currentGUITheme)],
                                                                                                self.objectConfig['WMA_{:d}_ColorB%{:s}'.format(_analysisParams['lineNumber'], self.currentGUITheme)],
                                                                                                self.objectConfig['WMA_{:d}_ColorA%{:s}'.format(_analysisParams['lineNumber'], self.currentGUITheme)]),
                                                                                        width_y = self.objectConfig['WMA_{:d}_Width'.format(_analysisParams['lineNumber'])]*2,
                                                                                        shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = _analysisParams['lineNumber']-1)
                    drawn += 0b1
        return drawn

    def __klineDrawer_EMA(self, drawSignal, timestamp, analysisCode):
        drawn = 0b0
        if (self.objectConfig['EMA_Master'] == True):
            _analysisParams = self.analysisParams[analysisCode]
            if (self.objectConfig['EMA_{:d}_Display'.format(_analysisParams['lineNumber'])] == True):
                if (drawSignal == None): drawSignal = 0b1
                if (0 < drawSignal):
                    #Previous Drawing Removal
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
                    #Data Acquisition & Check
                    timestamp_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
                    if (timestamp_prev in self.klines[analysisCode]): emaResult_prev = self.klines[analysisCode][timestamp_prev]
                    else:                                             emaResult_prev = None
                    if ((emaResult_prev != None) and (emaResult_prev['EMA'] != None)):
                        emaResult = self.klines[analysisCode][timestamp]
                        #Coordinate Determination
                        timestampWidth = timestamp-timestamp_prev
                        shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                        shape_x2 = round(timestamp     +timestampWidth/2, 1)
                        shape_y1 = emaResult_prev['EMA']
                        shape_y2 = emaResult['EMA']
                        #Drawing
                        self.displayBox_graphics['KLINESPRICE']['RCLCG'].addShape_Line(x  = shape_x1, y  = shape_y1, 
                                                                                       x2 = shape_x2, y2 = shape_y2,
                                                                                       color = (self.objectConfig['EMA_{:d}_ColorR%{:s}'.format(_analysisParams['lineNumber'], self.currentGUITheme)],
                                                                                                self.objectConfig['EMA_{:d}_ColorG%{:s}'.format(_analysisParams['lineNumber'], self.currentGUITheme)],
                                                                                                self.objectConfig['EMA_{:d}_ColorB%{:s}'.format(_analysisParams['lineNumber'], self.currentGUITheme)],
                                                                                                self.objectConfig['EMA_{:d}_ColorA%{:s}'.format(_analysisParams['lineNumber'], self.currentGUITheme)]),
                                                                                       width_y = self.objectConfig['EMA_{:d}_Width'.format(_analysisParams['lineNumber'])]*2,
                                                                                       shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = _analysisParams['lineNumber']-1)
                    drawn += 0b1
        return drawn

    def __klineDrawer_PSAR(self, drawSignal, timestamp, analysisCode):
        if (self.objectConfig['PSAR_Master'] == True):
            lineNumber = self.analysisParams[analysisCode]['lineNumber']
            if (self.objectConfig['PSAR_{:d}_Display'.format(lineNumber)] == True):
                psar = self.klines[analysisCode][timestamp]
                if (psar['PSAR'] != None):
                    kline_raw = self.klines['raw'][timestamp]
                    ts_open  = kline_raw[0]
                    ts_close = kline_raw[1]
                    #Width determination
                    tsWidth = ts_close-ts_open+1
                    shape_width = round(tsWidth*0.9, 1)
                    shape_xPos  = round(ts_open+(tsWidth-shape_width)/2, 1)
                    #Drawing
                    self.displayBox_graphics['KLINESPRICE']['RCLCG'].addShape_Line(x  = shape_xPos,             y  = psar['PSAR'], 
                                                                                   x2 = shape_xPos+shape_width, y2 = psar['PSAR'],
                                                                                   color = (self.objectConfig['PSAR_{:d}_ColorR%{:s}'.format(lineNumber, self.currentGUITheme)],
                                                                                            self.objectConfig['PSAR_{:d}_ColorG%{:s}'.format(lineNumber, self.currentGUITheme)],
                                                                                            self.objectConfig['PSAR_{:d}_ColorB%{:s}'.format(lineNumber, self.currentGUITheme)],
                                                                                            self.objectConfig['PSAR_{:d}_ColorA%{:s}'.format(lineNumber, self.currentGUITheme)]),
                                                                                   width_y = self.objectConfig['PSAR_{:d}_Width'.format(lineNumber)]*3,
                                                                                   shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = lineNumber-1)
                return 0b1
        return 0b0

    def __klineDrawer_BOL(self, drawSignal, timestamp, analysisCode):
        drawn = 0b00
        if (self.objectConfig['BOL_Master'] == True):
            _analysisParams = self.analysisParams[analysisCode]
            if (self.objectConfig['BOL_{:d}_Display'.format(_analysisParams['lineNumber'])] == True):
                if (drawSignal == None): drawSignal = 0b11
                if (0 < drawSignal):
                    timestamp_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
                    if (timestamp_prev in self.klines[analysisCode]): bolResult_prev = self.klines[analysisCode][timestamp_prev]
                    else:                                             bolResult_prev = None
                    if ((bolResult_prev != None) and (bolResult_prev['BOL'] != None)):
                        bolResult = self.klines[analysisCode][timestamp]
                        #Coordinate Determination
                        timestampWidth = timestamp-timestamp_prev
                        shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                        shape_x2 = round(timestamp     +timestampWidth/2, 1)
                        #[1]: CenterLine
                        if (0 < drawSignal&0b01):
                            #Previous Drawing Removal
                            self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode+'_LINE')
                            #Drawing
                            if (self.objectConfig['BOL_DisplayCenterLine'] == True):
                                if (_analysisParams['nSamples'] < bolResult['_analysisCount']):
                                    self.displayBox_graphics['KLINESPRICE']['RCLCG'].addShape_Line(x  = shape_x1, y  = bolResult_prev['MA'],
                                                                                                   x2 = shape_x2, y2 = bolResult['MA'],
                                                                                                   color = (self.objectConfig['BOL_{:d}_ColorR%{:s}'.format(_analysisParams['lineNumber'], self.currentGUITheme)],
                                                                                                            self.objectConfig['BOL_{:d}_ColorG%{:s}'.format(_analysisParams['lineNumber'], self.currentGUITheme)],
                                                                                                            self.objectConfig['BOL_{:d}_ColorB%{:s}'.format(_analysisParams['lineNumber'], self.currentGUITheme)],
                                                                                                            255),
                                                                                                   width = None, width_x = None, width_y = self.objectConfig['BOL_{:d}_Width'.format(_analysisParams['lineNumber'])]*2,
                                                                                                   shapeName = timestamp, shapeGroupName = analysisCode+'_LINE', layerNumber = _analysisParams['lineNumber']-1)
                                drawn += 0b01
                        #[2]: Band
                        if (0 < drawSignal&0b10):
                            #Previous Drawing Removal
                            self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode+'_BAND')
                            #Drawing
                            if (self.objectConfig['BOL_DisplayBand'] == True):
                                if (_analysisParams['nSamples'] < bolResult['_analysisCount']):
                                    self.displayBox_graphics['KLINESPRICE']['RCLCG'].addShape_Polygon(coordinates = ((shape_x1, bolResult_prev['BOL'][0]), (shape_x2, bolResult['BOL'][0]), (shape_x2, bolResult['BOL'][1]), (shape_x1, bolResult_prev['BOL'][1])), 
                                                                                                      color = (self.objectConfig['BOL_{:d}_ColorR%{:s}'.format(_analysisParams['lineNumber'], self.currentGUITheme)],
                                                                                                               self.objectConfig['BOL_{:d}_ColorG%{:s}'.format(_analysisParams['lineNumber'], self.currentGUITheme)],
                                                                                                               self.objectConfig['BOL_{:d}_ColorB%{:s}'.format(_analysisParams['lineNumber'], self.currentGUITheme)],
                                                                                                               self.objectConfig['BOL_{:d}_ColorA%{:s}'.format(_analysisParams['lineNumber'], self.currentGUITheme)]),
                                                                                                      shapeName = timestamp, shapeGroupName = analysisCode+'_BAND', layerNumber = _analysisParams['lineNumber']-1)
                                drawn += 0b10
        return drawn

    def __klineDrawer_IVP(self, drawSignal, timestamp, analysisCode):
        drawn = 0b00
        if (self.objectConfig['IVP_Master'] == True):
            if (drawSignal == None): drawSignal = 0b11
            if (0 < drawSignal):
                kline_raw = self.klines['raw'][timestamp]
                ts_open          = kline_raw[0]
                ts_close         = kline_raw[1]
                kline_closePrice = kline_raw[KLINDEX_CLOSEPRICE]
                ivpResult = self.klines['IVP'][timestamp]
                #Width determination
                tsWidth = ts_close-ts_open+1
                #Drawing
                #[1]: Volume Price Level Profile
                if (0 < drawSignal&0b01):
                    if (timestamp == self.posHighlight_selectedPos):
                        self.displayBox_graphics['KLINESPRICE']['RCLCG_XFIXED'].removeGroup(groupName = 'IVP_VPLP')
                        if (self.objectConfig['IVP_VPLP_Display'] == True):
                            if (ivpResult['volumePriceLevelProfile_Filtered_Max'] != None):
                                widthMax = 100*self.objectConfig['IVP_VPLP_DisplayWidth']
                                for _dIndex in range (0, len(ivpResult['volumePriceLevelProfile_Filtered'])):
                                    _dWidth = round(widthMax*ivpResult['volumePriceLevelProfile_Filtered'][_dIndex]/ivpResult['volumePriceLevelProfile_Filtered_Max'], 3)
                                    self.displayBox_graphics['KLINESPRICE']['RCLCG_XFIXED'].addShape_Rectangle(x = 100-_dWidth,                         width  = _dWidth, 
                                                                                                               y = ivpResult['divisionHeight']*_dIndex, height = ivpResult['divisionHeight'],
                                                                                                               color = (self.objectConfig['IVP_VPLP_ColorR%{:s}'.format(self.currentGUITheme)],
                                                                                                                        self.objectConfig['IVP_VPLP_ColorG%{:s}'.format(self.currentGUITheme)],
                                                                                                                        self.objectConfig['IVP_VPLP_ColorB%{:s}'.format(self.currentGUITheme)],
                                                                                                                        self.objectConfig['IVP_VPLP_ColorA%{:s}'.format(self.currentGUITheme)]),
                                                                                                               shapeName = _dIndex, shapeGroupName = 'IVP_VPLP', layerNumber = 0)
                        drawn += 0b01
                #[2]: Volume Price Level Profile Boundaries
                if (0 < drawSignal&0b10):
                    self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = 'IVP_VPLPB_{:d}'.format(timestamp))
                    if (self.objectConfig['IVP_VPLPB_Display'] == True):
                        if (ivpResult['volumePriceLevelProfile_Boundaries'] != None):
                            _pBoundariesDisplayRegion_beg = kline_closePrice*(1-self.objectConfig['IVP_VPLPB_DisplayRegion'])
                            _pBoundariesDisplayRegion_end = kline_closePrice*(1+self.objectConfig['IVP_VPLPB_DisplayRegion'])
                            _dIndex_BoundariesDisplayRegion_beg = int(_pBoundariesDisplayRegion_beg/ivpResult['divisionHeight'])
                            _dIndex_BoundariesDisplayRegion_end = int(_pBoundariesDisplayRegion_end/ivpResult['divisionHeight'])
                            if (_dIndex_BoundariesDisplayRegion_beg < 0):                                          _dIndex_BoundariesDisplayRegion_beg = 0
                            if (len(ivpResult['volumePriceLevelProfile']) <= _dIndex_BoundariesDisplayRegion_end): _dIndex_BoundariesDisplayRegion_end = len(ivpResult['volumePriceLevelProfile'])-1
                            for _bIndex, _dIndex in enumerate(ivpResult['volumePriceLevelProfile_Boundaries']):
                                if ((_dIndex_BoundariesDisplayRegion_beg <= _dIndex) and (_dIndex <= _dIndex_BoundariesDisplayRegion_end)):
                                    _relStrength = ivpResult['volumePriceLevelProfile_Filtered'][_dIndex]/ivpResult['volumePriceLevelProfile_Filtered_Max']
                                    self.displayBox_graphics['KLINESPRICE']['RCLCG'].addShape_Rectangle(x = ts_open,                             width = tsWidth, 
                                                                                                        y = ivpResult['divisionHeight']*_dIndex, height = ivpResult['divisionHeight'],
                                                                                                        color = (self.objectConfig['IVP_VPLPB_ColorR%{:s}'.format(self.currentGUITheme)],
                                                                                                                 self.objectConfig['IVP_VPLPB_ColorG%{:s}'.format(self.currentGUITheme)],
                                                                                                                 self.objectConfig['IVP_VPLPB_ColorB%{:s}'.format(self.currentGUITheme)],
                                                                                                                 int(self.objectConfig['IVP_VPLPB_ColorA%{:s}'.format(self.currentGUITheme)]*(_relStrength*0.5+0.5))),
                                                                                                        shapeName = _bIndex, shapeGroupName = 'IVP_VPLPB_{:d}'.format(timestamp), layerNumber = 0)
                        drawn += 0b10
        return drawn

    def __klineDrawer_PIP(self, drawSignal, timestamp, analysisCode):
        drawn = 0b00000
        if (self.objectConfig['PIP_Master'] == True):
            if (drawSignal == None): drawSignal = 0b11111
            if (0 < drawSignal):
                kline_raw = self.klines['raw'][timestamp]
                ts_open  = kline_raw[0]
                ts_close = kline_raw[1]
                #Width determination
                tsWidth = ts_close-ts_open+1
                shape_width = round(tsWidth*0.9, 1)
                shape_xPos  = round(ts_open+(tsWidth-shape_width)/2, 1)
                #Drawing Prep
                pipResult = self.klines[analysisCode][timestamp]
                #[1]: Swings 0
                if (0 < drawSignal&0b00001):
                    if (timestamp == self.posHighlight_selectedPos):
                        self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = 'PIP_SWINGS')
                        if (self.objectConfig['PIP_SWING_Display'] == True):
                            timestamp_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
                            timestampWidth = timestamp-timestamp_prev
                            _swings = pipResult['SWINGS']
                            for _swingIndex in range (1, len(_swings)):
                                _swing_prev    = _swings[_swingIndex-1]
                                _swing_current = _swings[_swingIndex]
                                self.displayBox_graphics['KLINESPRICE']['RCLCG'].addShape_Line(x  = round(_swing_prev[0]   +timestampWidth/2, 1), y  = _swing_prev[1],
                                                                                               x2 = round(_swing_current[0]+timestampWidth/2, 1), y2 = _swing_current[1],
                                                                                               color = (self.objectConfig['PIP_SWING_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                                                        self.objectConfig['PIP_SWING_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                                                        self.objectConfig['PIP_SWING_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                                                        self.objectConfig['PIP_SWING_ColorA%{:s}'.format(self.currentGUITheme)]),
                                                                                               width = None, width_x = None, width_y = 2,
                                                                                               shapeName = _swingIndex, shapeGroupName = 'PIP_SWINGS', layerNumber = 11)
                            drawn += 0b000001
                #[2]: NNA Signal
                if (0 < drawSignal&0b00010): 
                    self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'].removeShape(shapeName = timestamp, groupName = 'PIP_NNA')
                    if (self.objectConfig['PIP_NNASIGNAL_Display'] == True):
                        _nnaSignal = pipResult['NNASIGNAL']
                        if (_nnaSignal != None):
                            if (0 <= _nnaSignal): 
                                _color = (self.objectConfig['PIP_NNASIGNAL+_ColorR%{:s}'.format(self.currentGUITheme)], 
                                          self.objectConfig['PIP_NNASIGNAL+_ColorG%{:s}'.format(self.currentGUITheme)], 
                                          self.objectConfig['PIP_NNASIGNAL+_ColorB%{:s}'.format(self.currentGUITheme)], 
                                          self.objectConfig['PIP_NNASIGNAL+_ColorA%{:s}'.format(self.currentGUITheme)])
                            elif (_nnaSignal < 0): 
                                _color = (self.objectConfig['PIP_NNASIGNAL-_ColorR%{:s}'.format(self.currentGUITheme)], 
                                          self.objectConfig['PIP_NNASIGNAL-_ColorG%{:s}'.format(self.currentGUITheme)], 
                                          self.objectConfig['PIP_NNASIGNAL-_ColorB%{:s}'.format(self.currentGUITheme)],
                                          self.objectConfig['PIP_NNASIGNAL-_ColorA%{:s}'.format(self.currentGUITheme)])
                            self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'].addShape_Rectangle(x = shape_xPos, width = shape_width, y = 7.5, height = abs(_nnaSignal)*2.5, color = _color, shapeName = timestamp, shapeGroupName = 'PIP_NNA', layerNumber = 11)
                        drawn += 0b000010
                #[3]: WOI Signal
                if (0 < drawSignal&0b00100): 
                    self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'].removeShape(shapeName = timestamp, groupName = 'PIP_WOI')
                    if (self.objectConfig['PIP_WOISIGNAL_Display'] == True):
                        _woiSignal = pipResult['WOISIGNAL_ABSMAREL']
                        if (_woiSignal != None):
                            if (_woiSignal == 'LONG'): 
                                _color = (self.objectConfig['PIP_WOISIGNAL+_ColorR%{:s}'.format(self.currentGUITheme)], 
                                          self.objectConfig['PIP_WOISIGNAL+_ColorG%{:s}'.format(self.currentGUITheme)], 
                                          self.objectConfig['PIP_WOISIGNAL+_ColorB%{:s}'.format(self.currentGUITheme)], 
                                          self.objectConfig['PIP_WOISIGNAL+_ColorA%{:s}'.format(self.currentGUITheme)])
                            elif (_woiSignal == 'SHORT'): 
                                _color = (self.objectConfig['PIP_WOISIGNAL-_ColorR%{:s}'.format(self.currentGUITheme)], 
                                          self.objectConfig['PIP_WOISIGNAL-_ColorG%{:s}'.format(self.currentGUITheme)], 
                                          self.objectConfig['PIP_WOISIGNAL-_ColorB%{:s}'.format(self.currentGUITheme)],
                                          self.objectConfig['PIP_WOISIGNAL-_ColorA%{:s}'.format(self.currentGUITheme)])
                            self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'].addShape_Rectangle(x = shape_xPos, width = shape_width, y = 5.0, height = 2.5, color = _color, shapeName = timestamp, shapeGroupName = 'PIP_WOI', layerNumber = 11)
                        drawn += 0b000100
                #[4]: NES Signal
                if (0 < drawSignal&0b01000): 
                    self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'].removeShape(shapeName = timestamp, groupName = 'PIP_NES')
                    if (self.objectConfig['PIP_NESSIGNAL_Display'] == True):
                        _nesSignal = pipResult['NESSIGNAL_ABSMAREL']
                        if (_nesSignal != None):
                            if (0 <= _nesSignal): _color = (self.objectConfig['PIP_NESSIGNAL+_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                            self.objectConfig['PIP_NESSIGNAL+_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                            self.objectConfig['PIP_NESSIGNAL+_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                            self.objectConfig['PIP_NESSIGNAL+_ColorA%{:s}'.format(self.currentGUITheme)])
                            elif (_nesSignal < 0): _color = (self.objectConfig['PIP_NESSIGNAL-_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                             self.objectConfig['PIP_NESSIGNAL-_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                             self.objectConfig['PIP_NESSIGNAL-_ColorB%{:s}'.format(self.currentGUITheme)],
                                                             self.objectConfig['PIP_NESSIGNAL-_ColorA%{:s}'.format(self.currentGUITheme)])
                            self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'].addShape_Rectangle(x = shape_xPos, width = shape_width, y = 2.5, height = abs(_nesSignal)*2.5, color = _color, shapeName = timestamp, shapeGroupName = 'PIP_NES', layerNumber = 11)
                        drawn += 0b001000
                #[5]: Classical Signal
                if (0 < drawSignal&0b10000): 
                    self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'].removeShape(shapeName = timestamp, groupName = 'PIP_CLASSICAL')
                    if (self.objectConfig['PIP_CLASSICALSIGNAL_Display'] == True):
                        if   (self.objectConfig['PIP_CLASSICALSIGNAL_DisplayType'] == 'UNFILTERED'): _signalValue = pipResult['CLASSICALSIGNAL']
                        elif (self.objectConfig['PIP_CLASSICALSIGNAL_DisplayType'] == 'FILTERED'):   _signalValue = pipResult['CLASSICALSIGNAL_FILTERED']
                        if (_signalValue != None):
                            if (0 <= _signalValue): _color = (self.objectConfig['PIP_CLASSICALSIGNAL+_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                              self.objectConfig['PIP_CLASSICALSIGNAL+_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                              self.objectConfig['PIP_CLASSICALSIGNAL+_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                              self.objectConfig['PIP_CLASSICALSIGNAL+_ColorA%{:s}'.format(self.currentGUITheme)])
                            elif (_signalValue < 0): _color = (self.objectConfig['PIP_CLASSICALSIGNAL-_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                               self.objectConfig['PIP_CLASSICALSIGNAL-_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                               self.objectConfig['PIP_CLASSICALSIGNAL-_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                               self.objectConfig['PIP_CLASSICALSIGNAL-_ColorA%{:s}'.format(self.currentGUITheme)])
                            self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'].addShape_Rectangle(x = shape_xPos, width = shape_width, y = 0.0, height = abs(_signalValue)*2.5, color = _color, shapeName = timestamp, shapeGroupName = 'PIP_CLASSICAL', layerNumber = 11)
                        drawn += 0b010000
        return drawn

    def __klineDrawer_VOL(self, drawSignal, timestamp, analysisCode):
        drawn = 0b0
        if (self.objectConfig['VOL_Master'] == True):
            if (analysisCode == 'VOL'):
                viewerNumber = self.siTypes_siViewerAlloc['VOL']; siViewerCode = 'SIVIEWER{:d}'.format(viewerNumber)
                if (self.objectConfig['SIVIEWER{:d}Display'.format(viewerNumber)] == True):
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'VOL')
                    if   (self.objectConfig['VOL_VolumeType'] == 'BASE'):    volAccessIndex = KLINDEX_VOLBASE
                    elif (self.objectConfig['VOL_VolumeType'] == 'QUOTE'):   volAccessIndex = KLINDEX_VOLQUOTE
                    elif (self.objectConfig['VOL_VolumeType'] == 'BASETB'):  volAccessIndex = KLINDEX_VOLBASETAKERBUY
                    elif (self.objectConfig['VOL_VolumeType'] == 'QUOTETB'): volAccessIndex = KLINDEX_VOLQUOTETAKERBUY
                    #Width determination
                    kline_raw = self.klines['raw'][timestamp]
                    ts_open  = kline_raw[0]
                    ts_close = kline_raw[1]
                    tsWidth = ts_close-ts_open+1
                    shape_width = round(tsWidth*0.9, 1)
                    shape_xPos  = round(ts_open+(tsWidth-shape_width)/2, 1)
                    #Color & Height determination
                    p_open  = kline_raw[2]
                    p_close = kline_raw[5]
                    if (p_open < p_close):   candleColor = self.visualManager.getFromColorTable('CHARTDRAWER_KLINECOLOR_TYPE{:d}_INCREMENTAL'.format(self.objectConfig['KlineColorType'])) #Incremental
                    elif (p_open > p_close): candleColor = self.visualManager.getFromColorTable('CHARTDRAWER_KLINECOLOR_TYPE{:d}_DECREMENTAL'.format(self.objectConfig['KlineColorType'])) #Decremental
                    else:                    candleColor = self.visualManager.getFromColorTable('CHARTDRAWER_KLINECOLOR_TYPE{:d}_NEUTRAL'.format(self.objectConfig['KlineColorType']))     #Neutral
                    self.displayBox_graphics[siViewerCode]['RCLCG'].addShape_Rectangle(x = shape_xPos, y = 0, width = shape_width, height = kline_raw[volAccessIndex], color = candleColor, shapeName = ts_open, shapeGroupName = 'VOL', layerNumber = 10)
                    drawn += 0b1
            else:
                _analysisParams = self.analysisParams[analysisCode]
                if (self.objectConfig['VOL_{:d}_Display'.format(_analysisParams['lineNumber'])] == True):
                    if (drawSignal == None): drawSignal = 0b1
                    if (0 < drawSignal):
                        viewerNumber = self.siTypes_siViewerAlloc['VOL']; siViewerCode = 'SIVIEWER{:d}'.format(viewerNumber)
                        if (self.objectConfig['SIVIEWER{:d}Display'.format(viewerNumber)] == True):
                            #Previous Drawing Removal
                            self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'VOL_{:d}'.format(_analysisParams['lineNumber']))
                            #Data Acquisition & Check
                            timestamp_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
                            if (timestamp_prev in self.klines[analysisCode]): volResult_prev = self.klines[analysisCode][timestamp_prev]
                            else:                                             volResult_prev = None
                            if (volResult_prev != None) and (volResult_prev['MA'] != None):
                                volResult = self.klines[analysisCode][timestamp]
                                #Coordinate Determination
                                timestamp_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
                                timestampWidth = timestamp-timestamp_prev
                                shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                                shape_x2 = round(timestamp     +timestampWidth/2, 1)
                                volResult_prev = self.klines[analysisCode][timestamp_prev]
                                shape_y1 = volResult_prev['MA']
                                shape_y2 = volResult['MA']
                                #Drawing
                                lineColor = (self.objectConfig['VOL_{:d}_ColorR%{:s}'.format(_analysisParams['lineNumber'],self.currentGUITheme)],
                                             self.objectConfig['VOL_{:d}_ColorG%{:s}'.format(_analysisParams['lineNumber'],self.currentGUITheme)],
                                             self.objectConfig['VOL_{:d}_ColorB%{:s}'.format(_analysisParams['lineNumber'],self.currentGUITheme)],
                                             self.objectConfig['VOL_{:d}_ColorA%{:s}'.format(_analysisParams['lineNumber'],self.currentGUITheme)])
                                self.displayBox_graphics[siViewerCode]['RCLCG'].addShape_Line(x = shape_x1, x2 = shape_x2, y = shape_y1, y2 = shape_y2, 
                                                                                                color = lineColor, width_y = self.objectConfig['VOL_{:d}_Width'.format(_analysisParams['lineNumber'])]*5, 
                                                                                                shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = 10+_analysisParams['lineNumber']+1)
                            drawn += 0b1
        return drawn

    def __klineDrawer_MMACDSHORT(self, drawSignal, timestamp, analysisCode):
        drawn = 0b000
        if (self.objectConfig['MMACDSHORT_Master'] == True):
            if (drawSignal == None): drawSignal = 0b111
            if (0 < drawSignal):
                viewerNumber = self.siTypes_siViewerAlloc['MMACDSHORT']; siViewerCode = 'SIVIEWER{:d}'.format(viewerNumber)
                if (self.objectConfig['SIVIEWER{:d}Display'.format(viewerNumber)] == True):
                    mmacdResult = self.klines['MMACDSHORT'][timestamp]
                    #X Coordinate Determination
                    timestamp_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
                    if (timestamp_prev in self.klines[analysisCode]): mmacdResult_prev = self.klines[analysisCode][timestamp_prev]
                    else:                                             mmacdResult_prev = None
                    timestampWidth = timestamp-timestamp_prev
                    shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                    shape_x2 = round(timestamp     +timestampWidth/2, 1)
                    #Drawing
                    #[1]: MMACD
                    if (0 < drawSignal&0b001):
                        self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACDSHORT_MMACD')
                        if (self.objectConfig['MMACDSHORT_MMACD_Display'] == True):
                            if ((mmacdResult_prev != None) and (mmacdResult_prev['MMACD'] != None)):
                                lineColor = (self.objectConfig['MMACDSHORT_MMACD_ColorR%{:s}'.format(self.currentGUITheme)],
                                             self.objectConfig['MMACDSHORT_MMACD_ColorG%{:s}'.format(self.currentGUITheme)],
                                             self.objectConfig['MMACDSHORT_MMACD_ColorB%{:s}'.format(self.currentGUITheme)],
                                             self.objectConfig['MMACDSHORT_MMACD_ColorA%{:s}'.format(self.currentGUITheme)])
                                self.displayBox_graphics[siViewerCode]['RCLCG'].addShape_Line(x = shape_x1, x2 = shape_x2, y = mmacdResult_prev['MMACD'], y2 = mmacdResult['MMACD'], color = lineColor, width_y = 5, shapeName = timestamp, shapeGroupName = 'MMACDSHORT_MMACD', layerNumber = 1)
                            drawn += 0b001
                    #[2]: SIGNAL
                    if (0 < drawSignal&0b010):
                        self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACDSHORT_SIGNAL')
                        if (self.objectConfig['MMACDSHORT_SIGNAL_Display'] == True):
                            if ((mmacdResult_prev != None) and (mmacdResult_prev['SIGNAL'] != None)):
                                lineColor = (self.objectConfig['MMACDSHORT_SIGNAL_ColorR%{:s}'.format(self.currentGUITheme)],
                                             self.objectConfig['MMACDSHORT_SIGNAL_ColorG%{:s}'.format(self.currentGUITheme)],
                                             self.objectConfig['MMACDSHORT_SIGNAL_ColorB%{:s}'.format(self.currentGUITheme)],
                                             self.objectConfig['MMACDSHORT_SIGNAL_ColorA%{:s}'.format(self.currentGUITheme)])
                                self.displayBox_graphics[siViewerCode]['RCLCG'].addShape_Line(x = shape_x1, x2 = shape_x2, y = mmacdResult_prev['SIGNAL'], y2 = mmacdResult['SIGNAL'], color = lineColor, width_y = 5, shapeName = timestamp, shapeGroupName = 'MMACDSHORT_SIGNAL', layerNumber = 1)
                            drawn += 0b010
                    #[3]: HISTOGRAM
                    if (0 < drawSignal&0b100):
                        self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACDSHORT_HISTOGRAM')
                        if (self.objectConfig['MMACDSHORT_HISTOGRAM_Display'] == True):
                            _mmacdVal = mmacdResult['MSDELTA']
                            if (_mmacdVal != None):
                                #Width determination
                                kline_raw = self.klines['raw'][timestamp]
                                ts_open  = kline_raw[0]
                                ts_close = kline_raw[1]
                                tsWidth = ts_close-ts_open+1
                                shape_width = round(tsWidth*0.9, 1)
                                shape_xPos  = round(ts_open+(tsWidth-shape_width)/2, 1)
                                if (0 <= _mmacdVal):
                                    if (0 <= mmacdResult['MMACD']):
                                        lineColor = (self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorR%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorG%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorB%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorA%{:s}'.format(self.currentGUITheme)])
                                    else:
                                        lineColor = (self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorR%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorG%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorB%{:s}'.format(self.currentGUITheme)],
                                                     int(self.objectConfig['MMACDSHORT_HISTOGRAM+_ColorA%{:s}'.format(self.currentGUITheme)]/2))
                                    body_y      = 0
                                    body_height = _mmacdVal
                                else:
                                    if (0 <= mmacdResult['MMACD']):
                                        lineColor = (self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorR%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorG%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorB%{:s}'.format(self.currentGUITheme)],
                                                     int(self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorA%{:s}'.format(self.currentGUITheme)]/2))
                                    else:
                                        lineColor = (self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorR%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorG%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorB%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDSHORT_HISTOGRAM-_ColorA%{:s}'.format(self.currentGUITheme)])
                                    body_y      = _mmacdVal
                                    body_height = -_mmacdVal
                                self.displayBox_graphics[siViewerCode]['RCLCG'].addShape_Rectangle(x = shape_xPos, y = body_y, width = shape_width, height = body_height, color = lineColor, shapeName = timestamp, shapeGroupName = 'MMACDSHORT_HISTOGRAM', layerNumber = 0)
                            drawn += 0b100
        return drawn

    def __klineDrawer_MMACDLONG(self, drawSignal, timestamp, analysisCode):
        drawn = 0b000
        if (self.objectConfig['MMACDLONG_Master'] == True):
            if (drawSignal == None): drawSignal = 0b111
            if (0 < drawSignal):
                viewerNumber = self.siTypes_siViewerAlloc['MMACDLONG']; siViewerCode = 'SIVIEWER{:d}'.format(viewerNumber)
                if (self.objectConfig['SIVIEWER{:d}Display'.format(viewerNumber)] == True):
                    mmacdResult = self.klines['MMACDLONG'][timestamp]
                    #X Coordinate Determination
                    timestamp_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
                    if (timestamp_prev in self.klines[analysisCode]): mmacdResult_prev = self.klines[analysisCode][timestamp_prev]
                    else:                                             mmacdResult_prev = None
                    timestampWidth = timestamp-timestamp_prev
                    shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                    shape_x2 = round(timestamp     +timestampWidth/2, 1)
                    #Drawing
                    #[1]: MMACD
                    if (0 < drawSignal&0b001):
                        self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACDLONG_MMACD')
                        if (self.objectConfig['MMACDLONG_MMACD_Display'] == True):
                            if ((mmacdResult_prev != None) and (mmacdResult_prev['MMACD'] != None)):
                                lineColor = (self.objectConfig['MMACDLONG_MMACD_ColorR%{:s}'.format(self.currentGUITheme)],
                                             self.objectConfig['MMACDLONG_MMACD_ColorG%{:s}'.format(self.currentGUITheme)],
                                             self.objectConfig['MMACDLONG_MMACD_ColorB%{:s}'.format(self.currentGUITheme)],
                                             self.objectConfig['MMACDLONG_MMACD_ColorA%{:s}'.format(self.currentGUITheme)])
                                self.displayBox_graphics[siViewerCode]['RCLCG'].addShape_Line(x = shape_x1, x2 = shape_x2, y = mmacdResult_prev['MMACD'], y2 = mmacdResult['MMACD'], color = lineColor, width_y = 5, shapeName = timestamp, shapeGroupName = 'MMACDLONG_MMACD', layerNumber = 1)
                            drawn += 0b001
                    #[2]: SIGNAL
                    if (0 < drawSignal&0b010):
                        self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACDLONG_SIGNAL')
                        if (self.objectConfig['MMACDLONG_SIGNAL_Display'] == True):
                            if ((mmacdResult_prev != None) and (mmacdResult_prev['SIGNAL'] != None)):
                                lineColor = (self.objectConfig['MMACDLONG_SIGNAL_ColorR%{:s}'.format(self.currentGUITheme)],
                                             self.objectConfig['MMACDLONG_SIGNAL_ColorG%{:s}'.format(self.currentGUITheme)],
                                             self.objectConfig['MMACDLONG_SIGNAL_ColorB%{:s}'.format(self.currentGUITheme)],
                                             self.objectConfig['MMACDLONG_SIGNAL_ColorA%{:s}'.format(self.currentGUITheme)])
                                self.displayBox_graphics[siViewerCode]['RCLCG'].addShape_Line(x = shape_x1, x2 = shape_x2, y = mmacdResult_prev['SIGNAL'], y2 = mmacdResult['SIGNAL'], color = lineColor, width_y = 5, shapeName = timestamp, shapeGroupName = 'MMACDLONG_SIGNAL', layerNumber = 1)
                            drawn += 0b010
                    #[3]: HISTOGRAM
                    if (0 < drawSignal&0b100):
                        self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACDLONG_HISTOGRAM')
                        if (self.objectConfig['MMACDLONG_HISTOGRAM_Display'] == True):
                            _mmacdVal = mmacdResult['MSDELTA']
                            if (_mmacdVal != None):
                                #Width determination
                                kline_raw = self.klines['raw'][timestamp]
                                ts_open  = kline_raw[0]
                                ts_close = kline_raw[1]
                                tsWidth = ts_close-ts_open+1
                                shape_width = round(tsWidth*0.9, 1)
                                shape_xPos  = round(ts_open+(tsWidth-shape_width)/2, 1)
                                if (0 <= _mmacdVal):
                                    if (0 <= mmacdResult['MMACD']):
                                        lineColor = (self.objectConfig['MMACDLONG_HISTOGRAM+_ColorR%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDLONG_HISTOGRAM+_ColorG%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDLONG_HISTOGRAM+_ColorB%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDLONG_HISTOGRAM+_ColorA%{:s}'.format(self.currentGUITheme)])
                                    else:
                                        lineColor = (self.objectConfig['MMACDLONG_HISTOGRAM+_ColorR%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDLONG_HISTOGRAM+_ColorG%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDLONG_HISTOGRAM+_ColorB%{:s}'.format(self.currentGUITheme)],
                                                     int(self.objectConfig['MMACDLONG_HISTOGRAM+_ColorA%{:s}'.format(self.currentGUITheme)]/2))
                                    body_y      = 0
                                    body_height = _mmacdVal
                                else:
                                    if (0 <= mmacdResult['MMACD']):
                                        lineColor = (self.objectConfig['MMACDLONG_HISTOGRAM-_ColorR%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDLONG_HISTOGRAM-_ColorG%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDLONG_HISTOGRAM-_ColorB%{:s}'.format(self.currentGUITheme)],
                                                     int(self.objectConfig['MMACDLONG_HISTOGRAM-_ColorA%{:s}'.format(self.currentGUITheme)]/2))
                                    else:
                                        lineColor = (self.objectConfig['MMACDLONG_HISTOGRAM-_ColorR%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDLONG_HISTOGRAM-_ColorG%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDLONG_HISTOGRAM-_ColorB%{:s}'.format(self.currentGUITheme)],
                                                     self.objectConfig['MMACDLONG_HISTOGRAM-_ColorA%{:s}'.format(self.currentGUITheme)])
                                    body_y      = _mmacdVal
                                    body_height = -_mmacdVal
                                self.displayBox_graphics[siViewerCode]['RCLCG'].addShape_Rectangle(x = shape_xPos, y = body_y, width = shape_width, height = body_height, color = lineColor, shapeName = timestamp, shapeGroupName = 'MMACDLONG_HISTOGRAM', layerNumber = 0)
                            drawn += 0b100
        return drawn

    def __klineDrawer_DMIxADX(self, drawSignal, timestamp, analysisCode):
        drawn = 0b0
        if (self.objectConfig['DMIxADX_Master'] == True):
            _analysisParams = self.analysisParams[analysisCode]
            if (self.objectConfig['DMIxADX_{:d}_Display'.format(_analysisParams['lineNumber'])] == True):
                if (drawSignal == None): drawSignal = 0b1
                if (0 < drawSignal):
                    viewerNumber = self.siTypes_siViewerAlloc['DMIxADX']; siViewerCode = 'SIVIEWER{:d}'.format(viewerNumber)
                    if (self.objectConfig['SIVIEWER{:d}Display'.format(viewerNumber)] == True):
                        #Previous Drawing Removal
                        self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
                        #Data Acquisition & Check
                        timestamp_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
                        if (timestamp_prev in self.klines[analysisCode]): dmixadxResult_prev = self.klines[analysisCode][timestamp_prev]
                        else:                                             dmixadxResult_prev = None
                        if ((dmixadxResult_prev != None) and (dmixadxResult_prev['DMIxADX_ABSATHREL'] != None)):
                            dmixadxResult = self.klines[analysisCode][timestamp]
                            #Coordinate Determination
                            timestampWidth = timestamp-timestamp_prev
                            shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                            shape_x2 = round(timestamp     +timestampWidth/2, 1)
                            shape_y1 = dmixadxResult_prev['DMIxADX_ABSATHREL']
                            shape_y2 = dmixadxResult['DMIxADX_ABSATHREL']
                            #Drawing
                            self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
                            if ((dmixadxResult_prev != None) and (dmixadxResult_prev['DMIxADX_ABSATHREL'] != None) and (dmixadxResult['DMIxADX_ABSATHREL'] != None)):
                                lineColor = (self.objectConfig['DMIxADX_{:d}_ColorR%{:s}'.format(_analysisParams['lineNumber'],self.currentGUITheme)],
                                             self.objectConfig['DMIxADX_{:d}_ColorG%{:s}'.format(_analysisParams['lineNumber'],self.currentGUITheme)],
                                             self.objectConfig['DMIxADX_{:d}_ColorB%{:s}'.format(_analysisParams['lineNumber'],self.currentGUITheme)],
                                             self.objectConfig['DMIxADX_{:d}_ColorA%{:s}'.format(_analysisParams['lineNumber'],self.currentGUITheme)])
                                self.displayBox_graphics[siViewerCode]['RCLCG'].addShape_Line(x = shape_x1, x2 = shape_x2, y = dmixadxResult_prev['DMIxADX_ABSATHREL'], y2 = dmixadxResult['DMIxADX_ABSATHREL'], 
                                                                                                color = lineColor, width_y = self.objectConfig['DMIxADX_{:d}_Width'.format(_analysisParams['lineNumber'])]*5, 
                                                                                                shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = _analysisParams['lineNumber']-1)
                        drawn += 0b1
        return drawn

    def __klineDrawer_MFI(self, drawSignal, timestamp, analysisCode):
        drawn = 0b0
        if (self.objectConfig['MFI_Master'] == True):
            _analysisParams = self.analysisParams[analysisCode]
            if (self.objectConfig['MFI_{:d}_Display'.format(_analysisParams['lineNumber'])] == True):
                if (drawSignal == None): drawSignal = 0b1
                if (0 < drawSignal):
                    viewerNumber = self.siTypes_siViewerAlloc['MFI']; siViewerCode = 'SIVIEWER{:d}'.format(viewerNumber)
                    if (self.objectConfig['SIVIEWER{:d}Display'.format(viewerNumber)] == True):
                        #Previous Drawing Removal
                        self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MFI_{:d}'.format(_analysisParams['lineNumber']))
                        #Data Acquisition & Check
                        timestamp_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
                        if (timestamp_prev in self.klines[analysisCode]): mfiResult_prev = self.klines[analysisCode][timestamp_prev]
                        else:                                             mfiResult_prev = None
                        if ((mfiResult_prev != None) and (mfiResult_prev['MFI_ABSATHREL'] != None)):
                            mfiResult = self.klines[analysisCode][timestamp]
                            #Coordinate Determination
                            timestampWidth = timestamp-timestamp_prev
                            shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                            shape_x2 = round(timestamp     +timestampWidth/2, 1)
                            shape_y1 = mfiResult_prev['MFI_ABSATHREL']
                            shape_y2 = mfiResult['MFI_ABSATHREL']
                            #Drawing
                            lineColor = (self.objectConfig['MFI_{:d}_ColorR%{:s}'.format(_analysisParams['lineNumber'],self.currentGUITheme)],
                                         self.objectConfig['MFI_{:d}_ColorG%{:s}'.format(_analysisParams['lineNumber'],self.currentGUITheme)],
                                         self.objectConfig['MFI_{:d}_ColorB%{:s}'.format(_analysisParams['lineNumber'],self.currentGUITheme)],
                                         self.objectConfig['MFI_{:d}_ColorA%{:s}'.format(_analysisParams['lineNumber'],self.currentGUITheme)])
                            self.displayBox_graphics[siViewerCode]['RCLCG'].addShape_Line(x = shape_x1, x2 = shape_x2, y = shape_y1, y2 = shape_y2, 
                                                                                          color = lineColor, width_y = self.objectConfig['MFI_{:d}_Width'.format(_analysisParams['lineNumber'])]*5, 
                                                                                          shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = _analysisParams['lineNumber']-1)
                        drawn += 0b1
        return drawn

    def __klineDrawer_TRADELOG(self, drawSignal, timestamp, analysisCode):
        drawn = 0b0
        if (self.objectConfig['TRADELOG_Display'] == True):
            if (drawSignal == None): drawSignal = 0b1
            if (0 < drawSignal):
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = 'TRADELOG_BODY')
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = 'TRADELOG_LASTTRADE')
                tradeLog = self.klines[analysisCode][timestamp]
                closedPrice = self.klines['raw'][timestamp][5]
                if (tradeLog['totalQuantity'] != 0):
                    #Coordinate Determination
                    timestamp_next = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = 1)
                    shape_x1    = timestamp
                    shape_x2    = timestamp_next
                    shape_width = shape_x2-shape_x1
                    #Body
                    if (0 < tradeLog['totalQuantity']):
                        if (tradeLog['entryPrice'] <= closedPrice): _colorType = 'GAINING'
                        else:                                       _colorType = 'LOSING'
                    elif (tradeLog['totalQuantity'] < 0):
                        if (tradeLog['entryPrice'] <= closedPrice): _colorType = 'LOSING'
                        else:                                       _colorType = 'GAINING'
                    if (_colorType == 'GAINING'):
                        color_body = (self.objectConfig['TRADELOG_BUY_ColorR%{:s}'.format(self.currentGUITheme)],
                                      self.objectConfig['TRADELOG_BUY_ColorG%{:s}'.format(self.currentGUITheme)],
                                      self.objectConfig['TRADELOG_BUY_ColorB%{:s}'.format(self.currentGUITheme)],
                                      int(self.objectConfig['TRADELOG_BUY_ColorA%{:s}'.format(self.currentGUITheme)]/5))
                        shape_y = tradeLog['entryPrice']; shape_height = closedPrice-tradeLog['entryPrice']
                    elif (_colorType == 'LOSING'):
                        color_body = (self.objectConfig['TRADELOG_SELL_ColorR%{:s}'.format(self.currentGUITheme)],
                                      self.objectConfig['TRADELOG_SELL_ColorG%{:s}'.format(self.currentGUITheme)],
                                      self.objectConfig['TRADELOG_SELL_ColorB%{:s}'.format(self.currentGUITheme)],
                                      int(self.objectConfig['TRADELOG_SELL_ColorA%{:s}'.format(self.currentGUITheme)]/5))
                        shape_y = closedPrice; shape_height = tradeLog['entryPrice']-closedPrice
                    self.displayBox_graphics['KLINESPRICE']['RCLCG'].addShape_Rectangle(x = shape_x1, y = shape_y, width = shape_width, height = shape_height, color = color_body, shapeName = timestamp, shapeGroupName = 'TRADELOG_BODY', layerNumber = 11)
                    #Last Trade
                    if (tradeLog['lastTrade'] != None):
                        _lastTrade = tradeLog['lastTrade']
                        if (_lastTrade[2] == 'BUY'):
                            color_lastTrade = (self.objectConfig['TRADELOG_BUY_ColorR%{:s}'.format(self.currentGUITheme)],
                                               self.objectConfig['TRADELOG_BUY_ColorG%{:s}'.format(self.currentGUITheme)],
                                               self.objectConfig['TRADELOG_BUY_ColorB%{:s}'.format(self.currentGUITheme)],
                                               self.objectConfig['TRADELOG_BUY_ColorA%{:s}'.format(self.currentGUITheme)])
                        elif (_lastTrade[2] == 'SELL'):
                            color_lastTrade = (self.objectConfig['TRADELOG_SELL_ColorR%{:s}'.format(self.currentGUITheme)],
                                               self.objectConfig['TRADELOG_SELL_ColorG%{:s}'.format(self.currentGUITheme)],
                                               self.objectConfig['TRADELOG_SELL_ColorB%{:s}'.format(self.currentGUITheme)],
                                               self.objectConfig['TRADELOG_SELL_ColorA%{:s}'.format(self.currentGUITheme)])
                        self.displayBox_graphics['KLINESPRICE']['RCLCG'].addShape_Line(x = shape_x1, x2 = shape_x2, y = _lastTrade[0], y2 = _lastTrade[0], color = color_lastTrade, width_y = 3, shapeName = timestamp, shapeGroupName = 'TRADELOG_LASTTRADE', layerNumber = 12)
                drawn += 0b1
        return drawn

    def __klineDrawer_RemoveExpiredDrawings(self, timestamp):
        for analysisCode in self.klines_drawn[timestamp]:
            targetType = analysisCode.split("_")[0]
            if   (targetType == 'KLINE'):
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = 'KLINEBODIES')
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = 'KLINETAILS')
            elif (targetType == 'SMA'):
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
            elif (targetType == 'WMA'):
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
            elif (targetType == 'EMA'):
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
            elif (targetType == 'PSAR'):
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
            elif (targetType == 'BOL'):
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode+'_BAND')
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode+'_LINE')
            elif (targetType == 'IVP'):
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = 'IVP_VPLPB_{:d}'.format(timestamp))
            elif (targetType == 'PIP'):
                self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'].removeShape(shapeName = timestamp, groupName = 'PIP_NNA')
                self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'].removeShape(shapeName = timestamp, groupName = 'PIP_WOI')
                self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'].removeShape(shapeName = timestamp, groupName = 'PIP_NES')
                self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'].removeShape(shapeName = timestamp, groupName = 'PIP_CLASSICAL')
            elif (targetType == 'VOL'): 
                siViewerNumber = self.siTypes_siViewerAlloc['VOL']
                if (siViewerNumber != None): 
                    siViewerCode = "SIVIEWER{:d}".format(siViewerNumber)
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
            elif (targetType == 'MMACDSHORT'):
                siViewerNumber = self.siTypes_siViewerAlloc['MMACDSHORT']
                if (siViewerNumber != None): 
                    siViewerCode = "SIVIEWER{:d}".format(siViewerNumber)
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACDSHORT_MMACD')
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACDSHORT_SIGNAL')
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACDSHORT_HISTOGRAM')
            elif (targetType == 'MMACDLONG'):
                siViewerNumber = self.siTypes_siViewerAlloc['MMACDLONG']
                if (siViewerNumber != None): 
                    siViewerCode = "SIVIEWER{:d}".format(siViewerNumber)
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACDLONG_MMACD')
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACDLONG_SIGNAL')
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACDLONG_HISTOGRAM')
            elif (targetType == 'DMIxADX'):
                siViewerNumber = self.siTypes_siViewerAlloc['DMIxADX']
                if (siViewerNumber != None): 
                    siViewerCode = "SIVIEWER{:d}".format(siViewerNumber)
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
            elif (targetType == 'MFI'):
                siViewerNumber = self.siTypes_siViewerAlloc['MFI']
                if (siViewerNumber != None): 
                    siViewerCode = "SIVIEWER{:d}".format(siViewerNumber)
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
            elif (targetType == 'TRADELOG'):
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = 'TRADELOG_BODY')
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = 'TRADELOG_LASTTRADE')
        del self.klines_drawn[timestamp]
        
    def __klineDrawer_RemoveDrawings(self, analysisCode, gRemovalSignal = None):
        analysisType = analysisCode.split("_")[0]
        if (gRemovalSignal == None): gRemovalSignal = _FULLDRAWSIGNALS[analysisType]
        else:                        gRemovalSignal = gRemovalSignal
        if (analysisType == 'SMA'):
            if (0 < gRemovalSignal&0b1): self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = analysisCode)
        elif (analysisType == 'WMA'):
            if (0 < gRemovalSignal&0b1): self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = analysisCode)
        elif (analysisType == 'EMA'):
            if (0 < gRemovalSignal&0b1): self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = analysisCode)
        elif (analysisType == 'PSAR'):
            if (0 < gRemovalSignal&0b1): self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = analysisCode)
        elif (analysisType == 'BOL'):
            if (0 < gRemovalSignal&0b01): self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = analysisCode+'_LINE')
            if (0 < gRemovalSignal&0b10): self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = analysisCode+'_BAND')
        elif (analysisType == 'IVP'):
            if (0 < gRemovalSignal&0b01): self.displayBox_graphics['KLINESPRICE']['RCLCG_XFIXED'].removeGroup(groupName = 'IVP_VPLP')
            for ts in self.klines_drawn:
                if ('IVP' in self.klines_drawn[ts]):
                    if (0 < gRemovalSignal&0b10): self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = 'IVP_VPLPB_{:d}'.format(ts))
        elif (analysisType == 'PIP'):
            if (0 < gRemovalSignal&0b00001): self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = 'PIP_SWINGS')
            if (0 < gRemovalSignal&0b00010): self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'].removeGroup(groupName = 'PIP_NNA')
            if (0 < gRemovalSignal&0b00100): self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'].removeGroup(groupName = 'PIP_WOI')
            if (0 < gRemovalSignal&0b01000): self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'].removeGroup(groupName = 'PIP_NES')
            if (0 < gRemovalSignal&0b10000): self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'].removeGroup(groupName = 'PIP_CLASSICAL')
        elif (analysisType == 'VOL'):
            siViewerNumber = self.siTypes_siViewerAlloc['VOL']
            if (siViewerNumber != None):
                siViewerCode = "SIVIEWER{:d}".format(siViewerNumber)
                if (0 < gRemovalSignal&0b1): self.displayBox_graphics[siViewerCode]['RCLCG'].removeGroup(groupName = analysisCode)
        elif (analysisType == 'MMACDSHORT'):
            siViewerNumber = self.siTypes_siViewerAlloc['MMACDSHORT']
            if (siViewerNumber != None):
                siViewerCode = "SIVIEWER{:d}".format(siViewerNumber)
                if (0 < gRemovalSignal&0b001): self.displayBox_graphics[siViewerCode]['RCLCG'].removeGroup(groupName = 'MMACDSHORT_MMACD')
                if (0 < gRemovalSignal&0b010): self.displayBox_graphics[siViewerCode]['RCLCG'].removeGroup(groupName = 'MMACDSHORT_SIGNAL')
                if (0 < gRemovalSignal&0b100): self.displayBox_graphics[siViewerCode]['RCLCG'].removeGroup(groupName = 'MMACDSHORT_HISTOGRAM')
        elif (analysisType == 'MMACDLONG'):
            siViewerNumber = self.siTypes_siViewerAlloc['MMACDLONG']
            if (siViewerNumber != None):
                siViewerCode = "SIVIEWER{:d}".format(siViewerNumber)
                if (0 < gRemovalSignal&0b001): self.displayBox_graphics[siViewerCode]['RCLCG'].removeGroup(groupName = 'MMACDLONG_MMACD')
                if (0 < gRemovalSignal&0b010): self.displayBox_graphics[siViewerCode]['RCLCG'].removeGroup(groupName = 'MMACDLONG_SIGNAL')
                if (0 < gRemovalSignal&0b100): self.displayBox_graphics[siViewerCode]['RCLCG'].removeGroup(groupName = 'MMACDLONG_HISTOGRAM')
        elif (analysisType == 'DMIxADX'):
            siViewerNumber = self.siTypes_siViewerAlloc['DMIxADX']
            if (siViewerNumber != None):
                siViewerCode = "SIVIEWER{:d}".format(siViewerNumber)
                if (0 < gRemovalSignal&0b1): self.displayBox_graphics[siViewerCode]['RCLCG'].removeGroup(groupName = analysisCode)
        elif (analysisType == 'MFI'):
            siViewerNumber = self.siTypes_siViewerAlloc['MFI']
            if (siViewerNumber != None):
                siViewerCode = "SIVIEWER{:d}".format(siViewerNumber)
                if (0 < gRemovalSignal&0b1): self.displayBox_graphics[siViewerCode]['RCLCG'].removeGroup(groupName = analysisCode)
        elif (analysisType == 'TRADELOG'):
            if (0 < gRemovalSignal&0b1): 
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = 'TRADELOG_BODY')
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = 'TRADELOG_LASTTRADE')
        #---Draw Trackers Reset
        for _ts in self.klines_drawn:
            if (analysisCode in self.klines_drawn[_ts]):
                self.klines_drawn[_ts][analysisCode] &= ~gRemovalSignal
                if (self.klines_drawn[_ts][analysisCode] == 0): del self.klines_drawn[_ts][analysisCode]
        for _ts in self.klines_drawQueue:
            if (analysisCode in self.klines_drawQueue[_ts]):
                if (self.klines_drawQueue[_ts][analysisCode] == None): self.klines_drawQueue[_ts][analysisCode] = _FULLDRAWSIGNALS[analysisType]&~gRemovalSignal
                else:                                                  self.klines_drawQueue[_ts][analysisCode] &= ~gRemovalSignal
                if (self.klines_drawQueue[_ts][analysisCode] == 0): del self.klines_drawQueue[_ts][analysisCode]

    def __bidsAndAsksDrawer_Draw(self):
        if (self.objectConfig['BIDSANDASKS_Display'] == True):
            #Params
            try:    _lastKline_closePrice = self.klines['raw'][self.klines_lastStreamedKlineOpenTS][KLINDEX_CLOSEPRICE]
            except: _lastKline_closePrice = None
            if (_lastKline_closePrice is not None):
                _drawWidth     = 0.20
                _id_multiplier = 1
                while (True):
                    _initialDivision = 1e-3*_id_multiplier
                    _plHeight = round(_lastKline_closePrice*_initialDivision, self.currencyInfo['precisions']['price'])
                    if (_plHeight == 0): _id_multiplier += 1
                    else: break
                #Display Data
                _plForDisplay = dict()
                _quantity_max = 0
                for _pl in self.bidsAndAsks['depth']:
                    _baa        = self.bidsAndAsks['depth'][_pl]
                    _pl_rounded = round(int(_pl/_plHeight)*_plHeight, self.currencyInfo['precisions']['price'])
                    if (_pl_rounded not in _plForDisplay): _plForDisplay[_pl_rounded] = {'bidSum': 0, 'askSum': 0, 'greater': 0}
                    if (_baa[0] == 'BID'): 
                        _plForDisplay[_pl_rounded]['bidSum'] += _baa[1]
                        if (_plForDisplay[_pl_rounded]['greater'] < _plForDisplay[_pl_rounded]['bidSum']): _plForDisplay[_pl_rounded]['greater'] = _plForDisplay[_pl_rounded]['bidSum']
                    elif (_baa[0] == 'ASK'): 
                        _plForDisplay[_pl_rounded]['askSum'] += _baa[1]
                        if (_plForDisplay[_pl_rounded]['greater'] < _plForDisplay[_pl_rounded]['askSum']): _plForDisplay[_pl_rounded]['greater'] = _plForDisplay[_pl_rounded]['askSum']
                    if (_quantity_max < _plForDisplay[_pl_rounded]['greater']): _quantity_max = _plForDisplay[_pl_rounded]['greater']
                #Drawing
                self.displayBox_graphics['KLINESPRICE']['RCLCG_XFIXED'].removeGroup(groupName = 'BIDSANDASKS')
                for _pl in _plForDisplay:
                    _pld = _plForDisplay[_pl]
                    if (_pld['askSum'] < _pld['bidSum']):
                        _color = (self.objectConfig['BIDSANDASKS_BIDS_ColorR%{:s}'.format(self.currentGUITheme)],
                                  self.objectConfig['BIDSANDASKS_BIDS_ColorG%{:s}'.format(self.currentGUITheme)],
                                  self.objectConfig['BIDSANDASKS_BIDS_ColorB%{:s}'.format(self.currentGUITheme)],
                                  self.objectConfig['BIDSANDASKS_BIDS_ColorA%{:s}'.format(self.currentGUITheme)])
                    else:
                        _color = (self.objectConfig['BIDSANDASKS_ASKS_ColorR%{:s}'.format(self.currentGUITheme)],
                                  self.objectConfig['BIDSANDASKS_ASKS_ColorG%{:s}'.format(self.currentGUITheme)],
                                  self.objectConfig['BIDSANDASKS_ASKS_ColorB%{:s}'.format(self.currentGUITheme)],
                                  self.objectConfig['BIDSANDASKS_ASKS_ColorA%{:s}'.format(self.currentGUITheme)])
                    _bodyWidth = _pld['greater']/_quantity_max*_drawWidth*100
                    if (0 < _bodyWidth): self.displayBox_graphics['KLINESPRICE']['RCLCG_XFIXED'].addShape_Rectangle(x = 0, y = _pl-_plHeight/2, width = _bodyWidth, height = _plHeight, color = _color, shapeName = _pl, shapeGroupName = 'BIDSANDASKS', layerNumber = 11)

    def __bidsAndAsksDrawer_Remove(self):
        self.displayBox_graphics['KLINESPRICE']['RCLCG_XFIXED'].removeGroup(groupName = 'BIDSANDASKS')
    
    def __WOIDrawer_Draw(self, time, woiType):
        if (self.objectConfig['WOI_Master'] == True):
            try:    _lineNumber = int(woiType.split("_")[1])
            except: _lineNumber = None
            _viewerNumber = self.siTypes_siViewerAlloc['WOI']
            _siViewerCode = 'SIVIEWER{:d}'.format(_viewerNumber)
            #Draw Setup Check
            _drawGo = (self.objectConfig['SIVIEWER{:d}Display'.format(_viewerNumber)] == True)
            if (_lineNumber == None): _drawGo = ((_drawGo == True) and (self.objectConfig['WOI_BASE_Display'.format(_lineNumber)] == True) and (time in self.bidsAndAsks['WOI']))
            else:                     _drawGo = ((_drawGo == True) and (self.objectConfig['WOI_{:d}_Display'.format(_lineNumber)] == True) and (time in self.bidsAndAsks[woiType]))
            if (_drawGo == True):
                #Previous Drawing Removal
                self.displayBox_graphics[_siViewerCode]['RCLCG'].removeShape(shapeName = time, groupName = woiType)
                #Line-Dependent Drawings
                #---[1]: Base
                if (_lineNumber == None):
                    #WOI Value
                    _woiValue = self.bidsAndAsks['WOI'][time]
                    #Color
                    if (_woiValue < 0): _colorType = "-"
                    else:               _colorType = "+"
                    _color = (self.objectConfig['WOI_BASE{:s}_ColorR%{:s}'.format(_colorType,self.currentGUITheme)],
                              self.objectConfig['WOI_BASE{:s}_ColorG%{:s}'.format(_colorType,self.currentGUITheme)],
                              self.objectConfig['WOI_BASE{:s}_ColorB%{:s}'.format(_colorType,self.currentGUITheme)],
                              self.objectConfig['WOI_BASE{:s}_ColorA%{:s}'.format(_colorType,self.currentGUITheme)])
                    #X Coord
                    _width = round(BIDSANDASKSSAMPLINGINTERVAL_S*0.9, 1)
                    _x     = round(time+(BIDSANDASKSSAMPLINGINTERVAL_S-_width)/2, 1)
                    #Y Coord
                    _height = abs(_woiValue)
                    if   (_woiValue < 0):  _y = -_height
                    elif (0 <= _woiValue): _y = 0
                    #Drawing
                    self.displayBox_graphics[_siViewerCode]['RCLCG'].addShape_Rectangle(x = _x, y = _y, width = _width, height = _height, color = _color, shapeName = time, shapeGroupName = woiType, layerNumber = 0)
                #---[2]: Gaussian Deltas
                else:
                    if (time-BIDSANDASKSSAMPLINGINTERVAL_S in self.bidsAndAsks[woiType]):
                        #WOI Value
                        _woiValue_prev = self.bidsAndAsks[woiType][time-BIDSANDASKSSAMPLINGINTERVAL_S][1]
                        _woiValue_this = self.bidsAndAsks[woiType][time][1]
                        if (_woiValue_prev != None):
                            #Color
                            _color = (self.objectConfig['WOI_{:d}_ColorR%{:s}'.format(_lineNumber,self.currentGUITheme)],
                                      self.objectConfig['WOI_{:d}_ColorG%{:s}'.format(_lineNumber,self.currentGUITheme)],
                                      self.objectConfig['WOI_{:d}_ColorB%{:s}'.format(_lineNumber,self.currentGUITheme)],
                                      self.objectConfig['WOI_{:d}_ColorA%{:s}'.format(_lineNumber,self.currentGUITheme)])
                            #Coordinate Determination
                            shape_x1 = round(time-BIDSANDASKSSAMPLINGINTERVAL_S/2, 1)
                            shape_x2 = round(time+BIDSANDASKSSAMPLINGINTERVAL_S/2, 1)
                            shape_y1 = _woiValue_prev
                            shape_y2 = _woiValue_this
                            self.displayBox_graphics[_siViewerCode]['RCLCG'].addShape_Line(x = shape_x1, x2 = shape_x2, y = shape_y1, y2 = shape_y2, 
                                                                                           color = _color, width_x = 0.1, width_y = self.objectConfig['WOI_{:d}_Width'.format(_lineNumber)]*10, 
                                                                                           shapeName = time, shapeGroupName = woiType, layerNumber = _lineNumber+1)
                #Drawn Tracker Update
                if (time in self.bidsAndAsks_WOI_drawn): self.bidsAndAsks_WOI_drawn[time].add(woiType)
                else:                                    self.bidsAndAsks_WOI_drawn[time] = {woiType}

    def __WOIDrawer_RemoveExpiredDrawings(self, time):
        if (time in self.bidsAndAsks_WOI_drawn):
            _siViewerNumber = self.siTypes_siViewerAlloc['WOI']
            if (_siViewerNumber != None):  
                _siViewerCode = 'SIVIEWER{:d}'.format(_siViewerNumber)
                for _woiType in self.bidsAndAsks_WOI_drawn[time]: self.displayBox_graphics[_siViewerCode]['RCLCG'].removeShape(shapeName = time, groupName = _woiType)
            del self.bidsAndAsks_WOI_drawn[time]

    def __WOIDrawer_RemoveDrawings(self, woiType):
        #Drawing Removal
        _siViewerNumber = self.siTypes_siViewerAlloc['WOI']
        if (_siViewerNumber != None): 
            _siViewerCode = 'SIVIEWER{:d}'.format(_siViewerNumber)
            self.displayBox_graphics[_siViewerCode]['RCLCG'].removeGroup(groupName = woiType)
        #Draw Trackers Reset
        #---Drawns
        _tToRemove = list()
        for _t in self.bidsAndAsks_WOI_drawn: 
            if (woiType in self.bidsAndAsks_WOI_drawn[_t]): self.bidsAndAsks_WOI_drawn[_t].remove(woiType)
            if (len(self.bidsAndAsks_WOI_drawn[_t]) == 0): _tToRemove.append(_t)
        for _t in _tToRemove: del self.bidsAndAsks_WOI_drawn[_t]
        #---Draw Queues
        _tToRemove = list()
        for _t in self.bidsAndAsks_WOI_drawQueue:
            if (woiType in self.bidsAndAsks_WOI_drawQueue[_t]): self.bidsAndAsks_WOI_drawQueue[_t].remove(woiType)
            if (len(self.bidsAndAsks_WOI_drawQueue[_t]) == 0): _tToRemove.append(_t)
        for _t in _tToRemove: del self.bidsAndAsks_WOI_drawQueue[_t]

    def __NESDrawer_Draw(self, time, nesType):
        if (self.objectConfig['NES_Master'] == True):
            try:    _lineNumber = int(nesType.split("_")[1])
            except: _lineNumber = None
            _viewerNumber = self.siTypes_siViewerAlloc['NES']
            _siViewerCode = 'SIVIEWER{:d}'.format(_viewerNumber)
            #Draw Setup Check
            _drawGo = (self.objectConfig['SIVIEWER{:d}Display'.format(_viewerNumber)] == True)
            if (_lineNumber == None): _drawGo = ((_drawGo == True) and (self.objectConfig['NES_BASE_Display'.format(_lineNumber)] == True) and (time in self.aggTrades['NES']))
            else:                     _drawGo = ((_drawGo == True) and (self.objectConfig['NES_{:d}_Display'.format(_lineNumber)] == True) and (time in self.aggTrades[nesType]))
            if (_drawGo == True):
                #Previous Drawing Removal
                self.displayBox_graphics[_siViewerCode]['RCLCG'].removeShape(shapeName = time, groupName = nesType)
                #Line-Dependent Drawings
                #---[1]: Base
                if (_lineNumber == None):
                    #NES Value
                    _nesValue = self.aggTrades['NES'][time]
                    #Color
                    if (_nesValue < 0): _colorType = "-"
                    else:               _colorType = "+"
                    _color = (self.objectConfig['NES_BASE{:s}_ColorR%{:s}'.format(_colorType,self.currentGUITheme)],
                              self.objectConfig['NES_BASE{:s}_ColorG%{:s}'.format(_colorType,self.currentGUITheme)],
                              self.objectConfig['NES_BASE{:s}_ColorB%{:s}'.format(_colorType,self.currentGUITheme)],
                              self.objectConfig['NES_BASE{:s}_ColorA%{:s}'.format(_colorType,self.currentGUITheme)])
                    #X Coord
                    _width = round(AGGTRADESAMPLINGINTERVAL_S*0.9, 1)
                    _x     = round(time+(AGGTRADESAMPLINGINTERVAL_S-_width)/2, 1)
                    #Y Coord
                    _height = abs(_nesValue)
                    if   (_nesValue < 0):  _y = -_height
                    elif (0 <= _nesValue): _y = 0
                    #Drawing
                    self.displayBox_graphics[_siViewerCode]['RCLCG'].addShape_Rectangle(x = _x, y = _y, width = _width, height = _height, color = _color, shapeName = time, shapeGroupName = nesType, layerNumber = 0)
                #---[2]: Gaussian Deltas
                else:
                    if (time-AGGTRADESAMPLINGINTERVAL_S in self.aggTrades[nesType]):
                        #NES Value
                        _nesValue_prev = self.aggTrades[nesType][time-AGGTRADESAMPLINGINTERVAL_S][1]
                        _nesValue_this = self.aggTrades[nesType][time][1]
                        if (_nesValue_prev != None):
                            #Color
                            _color = (self.objectConfig['NES_{:d}_ColorR%{:s}'.format(_lineNumber,self.currentGUITheme)],
                                      self.objectConfig['NES_{:d}_ColorG%{:s}'.format(_lineNumber,self.currentGUITheme)],
                                      self.objectConfig['NES_{:d}_ColorB%{:s}'.format(_lineNumber,self.currentGUITheme)],
                                      self.objectConfig['NES_{:d}_ColorA%{:s}'.format(_lineNumber,self.currentGUITheme)])
                            #Coordinate Determination
                            shape_x1 = round(time-AGGTRADESAMPLINGINTERVAL_S/2, 1)
                            shape_x2 = round(time+AGGTRADESAMPLINGINTERVAL_S/2, 1)
                            shape_y1 = _nesValue_prev
                            shape_y2 = _nesValue_this
                            self.displayBox_graphics[_siViewerCode]['RCLCG'].addShape_Line(x = shape_x1, x2 = shape_x2, y = shape_y1, y2 = shape_y2, 
                                                                                           color = _color, width_x = 0.1, width_y = self.objectConfig['NES_{:d}_Width'.format(_lineNumber)]*10, 
                                                                                           shapeName = time, shapeGroupName = nesType, layerNumber = _lineNumber+1)
                #Drawn Tracker Update
                if (time in self.aggTrades_NES_drawn): self.aggTrades_NES_drawn[time].add(nesType)
                else:                                  self.aggTrades_NES_drawn[time] = {nesType}

    def __NESDrawer_RemoveExpiredDrawings(self, time):
        if (time in self.aggTrades_NES_drawn):
            _siViewerNumber = self.siTypes_siViewerAlloc['NES']
            if (_siViewerNumber != None):  
                _siViewerCode = 'SIVIEWER{:d}'.format(_siViewerNumber)
                for _nesType in self.aggTrades_NES_drawn[time]: self.displayBox_graphics[_siViewerCode]['RCLCG'].removeShape(shapeName = time, groupName = _nesType)
            del self.aggTrades_NES_drawn[time]

    def __NESDrawer_RemoveDrawings(self, nesType):
        #Drawing Removal
        _siViewerNumber = self.siTypes_siViewerAlloc['NES']
        if (_siViewerNumber != None): 
            _siViewerCode = 'SIVIEWER{:d}'.format(_siViewerNumber)
            self.displayBox_graphics[_siViewerCode]['RCLCG'].removeGroup(groupName = nesType)
        #Draw Trackers Reset
        #---Drawns
        _tToRemove = list()
        for _t in self.aggTrades_NES_drawn: 
            if (nesType in self.aggTrades_NES_drawn[_t]): self.aggTrades_NES_drawn[_t].remove(nesType)
            if (len(self.aggTrades_NES_drawn[_t]) == 0): _tToRemove.append(_t)
        for _t in _tToRemove: del self.aggTrades_NES_drawn[_t]
        #---Draw Queues
        _tToRemove = list()
        for _t in self.aggTrades_NES_drawQueue:
            if (nesType in self.aggTrades_NES_drawQueue[_t]): self.aggTrades_NES_drawQueue[_t].remove(nesType)
            if (len(self.aggTrades_NES_drawQueue[_t]) == 0): _tToRemove.append(_t)
        for _t in _tToRemove: del self.aggTrades_NES_drawQueue[_t]
    #Kline Drawing End ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #View Control ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #[1]: Horizontal Position and Magnification
    #---ViewRange Control Params
    def __setHVRParams(self):
        self.expectedKlineTemporalWidth = _EXPECTEDTEMPORALWIDTHS[self.intervalID]
        nKlinesDisplayable_min = self.displayBox['KLINESPRICE'][2]*self.scaler / _GD_DISPLAYBOX_KLINESPRICE_MAXPIXELWIDTH
        nKlinesDisplayable_max = self.displayBox['KLINESPRICE'][2]*self.scaler / _GD_DISPLAYBOX_KLINESPRICE_MINPIXELWIDTH
        self.horizontalViewRangeWidth_min = nKlinesDisplayable_min * self.expectedKlineTemporalWidth
        self.horizontalViewRangeWidth_max = nKlinesDisplayable_max * self.expectedKlineTemporalWidth
        self.horizontalViewRangeWidth_m = (self.horizontalViewRangeWidth_min-self.horizontalViewRangeWidth_max)/(_GD_DISPLAYBOX_KLINESPRICE_HVR_MAXMAGNITUDE-_GD_DISPLAYBOX_KLINESPRICE_HVR_MINMAGNITUDE)
        self.horizontalViewRangeWidth_b = (self.horizontalViewRangeWidth_min*_GD_DISPLAYBOX_KLINESPRICE_HVR_MINMAGNITUDE-self.horizontalViewRangeWidth_max*_GD_DISPLAYBOX_KLINESPRICE_HVR_MAXMAGNITUDE)/(_GD_DISPLAYBOX_KLINESPRICE_HVR_MINMAGNITUDE-_GD_DISPLAYBOX_KLINESPRICE_HVR_MAXMAGNITUDE)

    #---Horizontal Position
    def __editHPosition(self, delta_drag = None, delta_scroll = None):
        if   (delta_drag   != None): effectiveDelta = -delta_drag*(self.horizontalViewRange[1]-self.horizontalViewRange[0])/self.displayBox_graphics['KLINESPRICE']['DRAWBOX'][2]
        elif (delta_scroll != None): effectiveDelta = -delta_scroll*self.expectedKlineTemporalWidth
        hVR_new = [round(self.horizontalViewRange[0]+effectiveDelta), round(self.horizontalViewRange[1]+effectiveDelta)]
        #Above-Zero Container
        if (hVR_new[0] < 0): hVR_new = [0, hVR_new[1]-hVR_new[0]]
        self.horizontalViewRange = hVR_new
        self.__onHViewRangeUpdate(0)
        
    #---Horizontal Magnification
    def __editHMagFactor(self, delta_drag = None, delta_scroll = None):
        if   (delta_drag   != None): newMagnitudeFactor = self.horizontalViewRange_magnification - delta_drag*100/self.displayBox_graphics['KLINESPRICE']['DRAWBOX'][2]
        elif (delta_scroll != None): newMagnitudeFactor = self.horizontalViewRange_magnification + delta_scroll*(-self.horizontalViewRange_magnification/100+1.05)
        #Rounding
        newMagnitudeFactor = round(newMagnitudeFactor, 2)
        if   (newMagnitudeFactor < _GD_DISPLAYBOX_KLINESPRICE_HVR_MINMAGNITUDE): newMagnitudeFactor = _GD_DISPLAYBOX_KLINESPRICE_HVR_MINMAGNITUDE
        elif (_GD_DISPLAYBOX_KLINESPRICE_HVR_MAXMAGNITUDE < newMagnitudeFactor): newMagnitudeFactor = _GD_DISPLAYBOX_KLINESPRICE_HVR_MAXMAGNITUDE
        #Variation Check and response
        if (newMagnitudeFactor != self.horizontalViewRange_magnification):
            self.horizontalViewRange_magnification = newMagnitudeFactor
            hVR_new = (round(self.horizontalViewRange[1]-(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b)), self.horizontalViewRange[1])
            if (hVR_new[0] < 0): hVR_new = [0, hVR_new[1]-hVR_new[0]]
            self.horizontalViewRange = hVR_new
            self.__onHViewRangeUpdate(1)
            
    #---Post Horizontal View-Range Update
    def __onHViewRangeUpdate(self, updateType):
        #[1]: Update Process Queue
        if (self.currencySymbol != None): self.__onHViewRangeUpdate_UpdateProcessQueue()
        #[2]: Update RCLCGs
        self.__onHViewRangeUpdate_UpdateRCLCGs()
        #[3]: Update Grids
        self.__onHViewRangeUpdate_UpdateGrids(updateType)
        #[4}: Find new vertical extrema within the new horizontalViewRange
        if (self.currencySymbol != None):
            if (self.__checkVerticalExtremas_KLINES() == True): self.__onVerticalExtremaUpdate('KLINESPRICE')
            for siViewerCode in self.displayBox_graphics_visibleSIViewers:
                siAlloc = self.objectConfig['SIVIEWER{:d}SIAlloc'.format(int(siViewerCode[8:]))]
                if (self.checkVerticalExtremas_SIs[siAlloc]() == True):
                    if   (siAlloc == 'VOL'):        self.__editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.0, extension_t = 0.2)
                    elif (siAlloc == 'MMACDSHORT'): self.__editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                    elif (siAlloc == 'MMACDLONG'):  self.__editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                    elif (siAlloc == 'DMIxADX'):    self.__editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                    elif (siAlloc == 'MFI'):        self.__editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                    elif (siAlloc == 'WOI'):        self.__editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                    elif (siAlloc == 'NES'):        self.__editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
        #[5]: Update PosSelection
        self.__updatePosSelection(updateType = 1)
        
    def __onHViewRangeUpdate_UpdateProcessQueue(self):
        #[1]: Update Target Timestamps (Within ViewRange & BufferZone)
        self.horizontalViewRange_timestampsInViewRange = set(atmEta_Auxillaries.getTimestampList_byRange(self.intervalID, self.horizontalViewRange[0], self.horizontalViewRange[1], lastTickInclusive = True))
        nTSsInViewRange = len(self.horizontalViewRange_timestampsInViewRange)
        timestampsInBufferZone1 = set(atmEta_Auxillaries.getTimestampList_byNTicks(self.intervalID, self.horizontalViewRange[0], nTicks = int(nTSsInViewRange*_GD_DISPLAYBOX_HVR_BACKWARDBUFFERFACTOR)+1, direction = False, mrktReg = self.mrktRegTS)[1:])
        timestampsInBufferZone2 = set(atmEta_Auxillaries.getTimestampList_byNTicks(self.intervalID, self.horizontalViewRange[1], nTicks = int(nTSsInViewRange*_GD_DISPLAYBOX_HVR_FORWARDBUFFERFACTOR) +1, direction = True,  mrktReg = self.mrktRegTS)[1:])
        self.horizontalViewRange_timestampsInBufferZone = timestampsInBufferZone1.union(timestampsInBufferZone2)
        #[2]: Determine which targets to draw and update the drawQueue
        _targetZone = self.horizontalViewRange_timestampsInViewRange.union(self.horizontalViewRange_timestampsInBufferZone)
        for _ts in [_ts for _ts in self.klines_drawQueue if (_ts not in _targetZone)]: del self.klines_drawQueue[_ts]
        _potentialDrawTargets = [(_dataName, _FULLDRAWSIGNALS[_dataName.split("_")[0]]) for _dataName in self.klines if (_dataName not in _DRAWTARGETRAWNAMEEXCEPTION)]
        for _ts in _targetZone:
            if (_ts in self.klines['raw']):
                if (_ts in self.klines_drawn):
                    drawTargets = [_dt for _dt in _potentialDrawTargets if ((_ts in self.klines[_dt[0]]) and ((_dt[0] not in self.klines_drawn[_ts]) or (self.klines_drawn[_ts][_dt[0]] != _dt[1])))]
                    if (('KLINE' not in self.klines_drawn[_ts]) or (self.klines_drawn[_ts]['KLINE'] != _FULLDRAWSIGNALS['KLINE'])): drawTargets.append(('KLINE', _FULLDRAWSIGNALS['KLINE']))
                    if (('VOL'   not in self.klines_drawn[_ts]) or (self.klines_drawn[_ts]['VOL']   != _FULLDRAWSIGNALS['VOL'])):   drawTargets.append(('VOL',   _FULLDRAWSIGNALS['VOL']))
                else: drawTargets = [_dt for _dt in _potentialDrawTargets if (_ts in self.klines[_dt[0]])] + [('KLINE', _FULLDRAWSIGNALS['KLINE']), ('VOL', _FULLDRAWSIGNALS['VOL'])]
                #Add drawTargets to the drawQueue
                if (0 < len(drawTargets)):
                    if (_ts not in self.klines_drawQueue): self.klines_drawQueue[_ts] = dict()
                    if (_ts in self.klines_drawn):
                        for _dt in drawTargets:
                            if (_dt[0] in self.klines_drawn[_ts]): 
                                _drawn = self.klines_drawn[_ts][_dt[0]]
                                self.klines_drawQueue[_ts][_dt[0]] = _dt[1]&~_drawn
                            else: self.klines_drawQueue[_ts][_dt[0]] = None
                    else:
                        for _dt in drawTargets: self.klines_drawQueue[_ts][_dt[0]] = None
        #[3]: Update Draw Removal Queue
        self.klines_drawRemovalQueue = [ts for ts in self.klines_drawn if ((ts not in self.horizontalViewRange_timestampsInViewRange) and (ts not in self.horizontalViewRange_timestampsInBufferZone))]

    def __onHViewRangeUpdate_UpdateRCLCGs(self):
        self.displayBox_graphics['KLINESPRICE']['RCLCG'].updateProjection(projection_x0 = self.horizontalViewRange[0], projection_x1 = self.horizontalViewRange[1])
        self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'].updateProjection(projection_x0 = self.horizontalViewRange[0], projection_x1 = self.horizontalViewRange[1])
        for displayBoxName in self.displayBox_graphics_visibleSIViewers:
            self.displayBox_graphics[displayBoxName]['RCLCG'].updateProjection(projection_x0=self.horizontalViewRange[0], projection_x1=self.horizontalViewRange[1])
            self.displayBox_graphics[displayBoxName]['RCLCG_YFIXED'].updateProjection(projection_x0=self.horizontalViewRange[0], projection_x1=self.horizontalViewRange[1])
            
    def __onHViewRangeUpdate_UpdateGrids(self, updateType):
        #[1]: Determine Vertical Grid Intervals
        gridContentsUpdateFlag = False
        if (updateType == 1):
            for gridIntervalID in atmEta_Auxillaries.GRID_INTERVAL_IDs[self.intervalID:]:
                rightEnd = atmEta_Auxillaries.getNextIntervalTickTimestamp_GRID(gridIntervalID, self.horizontalViewRange[1], mrktReg = self.mrktRegTS, nTicks = 1)
                verticalGrid_intervals = atmEta_Auxillaries.getTimestampList_byRange_GRID(gridIntervalID, self.horizontalViewRange[0], rightEnd, mrktReg = self.mrktRegTS, lastTickInclusive = True)
                if (len(verticalGrid_intervals)+1 < self.nMaxVerticalGridLines): break
            self.verticalGrid_intervalID = gridIntervalID
            gridContentsUpdateFlag = True
        elif (updateType == 0):
            rightEnd = atmEta_Auxillaries.getNextIntervalTickTimestamp_GRID(self.verticalGrid_intervalID, self.horizontalViewRange[1], mrktReg = self.mrktRegTS, nTicks = 1)
            verticalGrid_intervals = atmEta_Auxillaries.getTimestampList_byRange_GRID(self.verticalGrid_intervalID, self.horizontalViewRange[0], rightEnd, mrktReg = self.mrktRegTS, lastTickInclusive = True)
            if ((self.verticalGrid_intervals[0] != verticalGrid_intervals[0]) or (self.verticalGrid_intervals[-1] != verticalGrid_intervals[-1])): gridContentsUpdateFlag = True

        #[2]: Update Grid Position & Text
        pixelPerTS = self.displayBox_graphics['MAINGRID_TEMPORAL']['DRAWBOX'][2]*self.scaler / (self.horizontalViewRange[1]-self.horizontalViewRange[0])
        if (gridContentsUpdateFlag == True):
            self.verticalGrid_intervals = verticalGrid_intervals
            for index in range (self.nMaxVerticalGridLines):
                if (index < len(self.verticalGrid_intervals)):
                    timestamp = self.verticalGrid_intervals[index]
                    timestamp_display = timestamp + self.timezoneDelta
                    xPos_Line = round((timestamp-self.verticalGrid_intervals[0])*pixelPerTS, 1)
                    #[1]: KLINESPRICE
                    self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_LINES'][index].x = xPos_Line; self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_LINES'][index].x2 = xPos_Line
                    if (self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_LINES'][index].visible == False): self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_LINES'][index].visible = True
                    #[2]: MAINGRID_TEMPORAL
                    #---GridLines
                    self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_LINES'][index].x = xPos_Line; self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_LINES'][index].x2 = xPos_Line
                    if (self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_LINES'][index].visible == False): self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_LINES'][index].visible = True
                    #---Grid Texts
                    if (self.verticalGrid_intervalID <= 10):
                        if (timestamp_display % 86400 != 0): dateStrFormat = "%H:%M"
                        else:                                dateStrFormat = "%m/%d"
                    else:
                        if (atmEta_Auxillaries.isNewMonth(timestamp_display) == True): dateStrFormat = "%Y/%m"
                        else:                                                            dateStrFormat = "%m/%d"
                    self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS'][index].setText(datetime.fromtimestamp(timestamp_display, tz = timezone.utc).strftime(dateStrFormat))
                    self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS'][index].moveTo(x = round((xPos_Line)/self.scaler-_GD_DISPLAYBOX_GRID_VERTICALTEXTWIDTH/2))
                    if (self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS'][index].hidden == True): self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS'][index].show()
                    #[3]: SIVIEWERs (If Display == True)
                    for siViewerNumber in range (1, len(_SITYPES)+1):
                        if (self.objectConfig['SIVIEWER{:d}Display'.format(siViewerNumber)] == True):
                            self.displayBox_graphics['SIVIEWER{:d}'.format(siViewerNumber)]['VERTICALGRID_LINES'][index].x = xPos_Line; self.displayBox_graphics['SIVIEWER{:d}'.format(siViewerNumber)]['VERTICALGRID_LINES'][index].x2 = xPos_Line
                            if (self.displayBox_graphics['SIVIEWER{:d}'.format(siViewerNumber)]['VERTICALGRID_LINES'][index].visible == False): self.displayBox_graphics['SIVIEWER{:d}'.format(siViewerNumber)]['VERTICALGRID_LINES'][index].visible = True
                else:
                    #[1]: KLINESPRICE
                    if (self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_LINES'][index].visible       == True): self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_LINES'][index].visible       = False
                    #[2]: MAINGRID_TEMPORAL
                    if (self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_LINES'][index].visible == True): self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_LINES'][index].visible = False
                    if (self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS'][index].hidden == False): self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS'][index].hide()
                    #[3]: SIVIEWERs (If Display == True)
                    for siViewerNumber in range (1, len(_SITYPES)+1):
                        if (self.objectConfig['SIVIEWER{:d}Display'.format(siViewerNumber)] == True):
                            if (self.displayBox_graphics['SIVIEWER{:d}'.format(siViewerNumber)]['VERTICALGRID_LINES'][index].visible == True): self.displayBox_graphics['SIVIEWER{:d}'.format(siViewerNumber)]['VERTICALGRID_LINES'][index].visible = False

        #Update Grid CamGroup Projections
        projectionX0 = (self.horizontalViewRange[0]-self.verticalGrid_intervals[0])*pixelPerTS
        projectionX1 = projectionX0+self.displayBox_graphics['MAINGRID_TEMPORAL']['DRAWBOX'][2]*self.scaler
        self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_CAMGROUP'].updateProjection(projection_x0=projectionX0, projection_x1=projectionX1)                                                                   #KLINESPRICE
        for displayBoxName in self.displayBox_graphics_visibleSIViewers: self.displayBox_graphics[displayBoxName]['VERTICALGRID_CAMGROUP'].updateProjection(projection_x0=projectionX0, projection_x1=projectionX1) #SIVIEWERS
        self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_CAMGROUP'].updateProjection(projection_x0=projectionX0, projection_x1=projectionX1)                                                             #MAINGRID_TEMPORAL
        return

    def __checkVerticalExtremas_KLINES(self):
        valMin = float('inf')
        valMax = float('-inf')
        for ts in self.horizontalViewRange_timestampsInViewRange:
            if (ts in self.klines['raw']):
                if (self.klines['raw'][ts][4] < valMin): valMin = self.klines['raw'][ts][4]
                if (valMax < self.klines['raw'][ts][3]): valMax = self.klines['raw'][ts][3]

        if (((valMin != float('inf')) and (valMax != float('-inf'))) and ((self.verticalValue_min['KLINESPRICE'] != valMin) or (self.verticalValue_max['KLINESPRICE'] != valMax))): #The found extremas are different
            self.verticalValue_min['KLINESPRICE'] = valMin
            self.verticalValue_max['KLINESPRICE'] = valMax
            return True
        else: return False
            
    def __checkVerticalExtremas_VOL(self):
        #SI Viewer Allocation
        siViewerCode = "SIVIEWER{:d}".format(self.siTypes_siViewerAlloc['VOL'])

        #Extrema Value Init
        valMax = float('-inf')
        
        #Find new vertical extremas
        aCodesToConsider = [analysisCode for analysisCode in self.siTypes_analysisCodes['VOL'] if ((analysisCode != 'VOL') and (self.objectConfig['VOL_{:d}_Display'.format(self.analysisParams[analysisCode]['lineNumber'])] == True))]
        if   (self.objectConfig['VOL_VolumeType'] == 'BASE'):    volAccessIndex = KLINDEX_VOLBASE
        elif (self.objectConfig['VOL_VolumeType'] == 'QUOTE'):   volAccessIndex = KLINDEX_VOLQUOTE
        elif (self.objectConfig['VOL_VolumeType'] == 'BASETB'):  volAccessIndex = KLINDEX_VOLBASETAKERBUY
        elif (self.objectConfig['VOL_VolumeType'] == 'QUOTETB'): volAccessIndex = KLINDEX_VOLQUOTETAKERBUY
        for ts in self.horizontalViewRange_timestampsInViewRange:
            for analysisCode in aCodesToConsider:
                if ((analysisCode in self.klines) and (ts in self.klines[analysisCode])):
                    value = self.klines[analysisCode][ts]['MA']
                    if (valMax < value): valMax = value
            if (ts in self.klines['raw']):
               value = self.klines['raw'][ts][volAccessIndex]
               if (valMax < value): valMax = value
        #If the extremas within the horizontalViewRange are updated
        if ((valMax != float('-inf')) and ((self.verticalValue_loaded[siViewerCode] == False) or (self.verticalValue_max[siViewerCode] != valMax))): #The found extremas are different
            self.verticalValue_loaded[siViewerCode] = True
            self.verticalValue_min[siViewerCode] = 0
            self.verticalValue_max[siViewerCode] = valMax
            return True
        else: return False

    def __checkVerticalExtremas_MMACDSHORT(self):
        #SI Viewer Allocation
        siViewerCode = "SIVIEWER{:d}".format(self.siTypes_siViewerAlloc['MMACDSHORT'])
        #Extrema Value Init
        valMin = float('inf')
        valMax = float('-inf')
        #Find new vertical extremas
        if (self.siTypes_analysisCodes['MMACDSHORT'] != None):
            for ts in self.horizontalViewRange_timestampsInViewRange:
                for analysisCode in self.siTypes_analysisCodes['MMACDSHORT']:
                    if ((analysisCode in self.klines) and (ts in self.klines[analysisCode])):
                        mmacdResult = self.klines['MMACDSHORT'][ts]
                        mmacdResult_MMACD     = mmacdResult['MMACD']
                        mmacdResult_SIGNAL    = mmacdResult['SIGNAL']
                        mmacdResult_HISTOGRAM = mmacdResult['MSDELTA']
                        values = []
                        if ((self.objectConfig['MMACDSHORT_MMACD_Display']     == True) and (mmacdResult_MMACD     != None)): values.append(mmacdResult_MMACD)
                        if ((self.objectConfig['MMACDSHORT_SIGNAL_Display']    == True) and (mmacdResult_SIGNAL    != None)): values.append(mmacdResult_SIGNAL)
                        if ((self.objectConfig['MMACDSHORT_HISTOGRAM_Display'] == True) and (mmacdResult_HISTOGRAM != None)): values.append(mmacdResult_HISTOGRAM)
                        if (0 < len(values)):
                            value_min = min(values)
                            value_max = max(values)
                            if (value_min < valMin): valMin = value_min
                            if (valMax < value_max): valMax = value_max
        #If the extremas within the horizontalViewRange are updated
        if (((valMin != float('inf')) and (valMax != float('-inf'))) and ((self.verticalValue_loaded[siViewerCode] == False) or (self.verticalValue_min[siViewerCode] != valMin) or (self.verticalValue_max[siViewerCode] != valMax))): #The found extremas are different
            self.verticalValue_loaded[siViewerCode] = True
            self.verticalValue_min[siViewerCode] = valMin
            self.verticalValue_max[siViewerCode] = valMax
            return True
        else: return False

    def __checkVerticalExtremas_MMACDLONG(self):
        #SI Viewer Allocation
        siViewerCode = "SIVIEWER{:d}".format(self.siTypes_siViewerAlloc['MMACDLONG'])
        #Extrema Value Init
        valMin = float('inf')
        valMax = float('-inf')
        #Find new vertical extremas
        if (self.siTypes_analysisCodes['MMACDLONG'] != None):
            for ts in self.horizontalViewRange_timestampsInViewRange:
                for analysisCode in self.siTypes_analysisCodes['MMACDLONG']:
                    if ((analysisCode in self.klines) and (ts in self.klines[analysisCode])):
                        mmacdResult = self.klines['MMACDLONG'][ts]
                        mmacdResult_MMACD     = mmacdResult['MMACD']
                        mmacdResult_SIGNAL    = mmacdResult['SIGNAL']
                        mmacdResult_HISTOGRAM = mmacdResult['MSDELTA']
                        values = []
                        if ((self.objectConfig['MMACDLONG_MMACD_Display']     == True) and (mmacdResult_MMACD     != None)): values.append(mmacdResult_MMACD)
                        if ((self.objectConfig['MMACDLONG_SIGNAL_Display']    == True) and (mmacdResult_SIGNAL    != None)): values.append(mmacdResult_SIGNAL)
                        if ((self.objectConfig['MMACDLONG_HISTOGRAM_Display'] == True) and (mmacdResult_HISTOGRAM != None)): values.append(mmacdResult_HISTOGRAM)
                        if (0 < len(values)):
                            value_min = min(values)
                            value_max = max(values)
                            if (value_min < valMin): valMin = value_min
                            if (valMax < value_max): valMax = value_max
        #If the extremas within the horizontalViewRange are updated
        if (((valMin != float('inf')) and (valMax != float('-inf'))) and ((self.verticalValue_loaded[siViewerCode] == False) or (self.verticalValue_min[siViewerCode] != valMin) or (self.verticalValue_max[siViewerCode] != valMax))): #The found extremas are different
            self.verticalValue_loaded[siViewerCode] = True
            self.verticalValue_min[siViewerCode] = valMin
            self.verticalValue_max[siViewerCode] = valMax
            return True
        else: return False

    def __checkVerticalExtremas_DMIxADX(self):
        #SI Viewer Allocation
        siViewerCode = "SIVIEWER{:d}".format(self.siTypes_siViewerAlloc['DMIxADX'])
        #Extrema Value Init
        valMin = float('inf')
        valMax = float('-inf')
        #Find new vertical extremas
        if (self.siTypes_analysisCodes['DMIxADX'] != None):
            aCodesToConsider = [analysisCode for analysisCode in self.siTypes_analysisCodes['DMIxADX'] if (self.objectConfig['DMIxADX_{:d}_Display'.format(self.analysisParams[analysisCode]['lineNumber'])] == True)]
            for ts in self.horizontalViewRange_timestampsInViewRange:
                for analysisCode in aCodesToConsider:
                    if ((analysisCode in self.klines) and (ts in self.klines[analysisCode])):
                        dmixadxResult = self.klines[analysisCode][ts]
                        dmixadxResult_DMIxADXabsAthRel = dmixadxResult['DMIxADX_ABSATHREL']
                        if (dmixadxResult_DMIxADXabsAthRel != None):
                            if (dmixadxResult_DMIxADXabsAthRel < valMin): valMin = dmixadxResult_DMIxADXabsAthRel
                            if (valMax < dmixadxResult_DMIxADXabsAthRel): valMax = dmixadxResult_DMIxADXabsAthRel
        #If the extremas within the horizontalViewRange are updated
        if (((valMin != float('inf')) and (valMax != float('-inf'))) and ((self.verticalValue_loaded[siViewerCode] == False) or (self.verticalValue_min[siViewerCode] != valMin) or (self.verticalValue_max[siViewerCode] != valMax))): #The found extremas are different
            self.verticalValue_loaded[siViewerCode] = True
            self.verticalValue_min[siViewerCode] = valMin
            self.verticalValue_max[siViewerCode] = valMax
            return True
        else: return False

    def __checkVerticalExtremas_MFI(self):
        #SI Viewer Allocation
        siViewerCode = "SIVIEWER{:d}".format(self.siTypes_siViewerAlloc['MFI'])
        #Extrema Value Init
        valMin = float('inf')
        valMax = float('-inf')
        #Find new vertical extremas
        if (self.siTypes_analysisCodes['MFI'] != None):
            aCodesToConsider = [analysisCode for analysisCode in self.siTypes_analysisCodes['MFI'] if (self.objectConfig['MFI_{:d}_Display'.format(self.analysisParams[analysisCode]['lineNumber'])] == True)]
            for ts in self.horizontalViewRange_timestampsInViewRange:
                for analysisCode in aCodesToConsider:
                    if ((analysisCode in self.klines) and (ts in self.klines[analysisCode])):
                        mfiResult = self.klines[analysisCode][ts]
                        mfiResult_MFIabsATHRel = mfiResult['MFI_ABSATHREL']
                        values = []
                        if (mfiResult_MFIabsATHRel != None): values.append(mfiResult_MFIabsATHRel)
                        if (0 < len(values)):
                            value_min = min(values)
                            value_max = max(values)
                            if (value_min < valMin): valMin = value_min
                            if (valMax < value_max): valMax = value_max
        #If the extremas within the horizontalViewRange are updated
        if (((valMin != float('inf')) and (valMax != float('-inf'))) and ((self.verticalValue_loaded[siViewerCode] == False) or (self.verticalValue_min[siViewerCode] != valMin) or (self.verticalValue_max[siViewerCode] != valMax))): #The found extremas are different
            self.verticalValue_loaded[siViewerCode] = True
            self.verticalValue_min[siViewerCode] = valMin
            self.verticalValue_max[siViewerCode] = valMax
            return True
        else: return False

    def __checkVerticalExtremas_WOI(self):
        #SI Viewer Allocation
        siViewerCode = "SIVIEWER{:d}".format(self.siTypes_siViewerAlloc['WOI'])
        #Extrema Value Init
        valMin = float('inf')
        valMax = float('-inf')
        #Find new vertical extremas
        if (self.siTypes_analysisCodes['WOI'] != None):
            _aCodesToConsider = [_aCode for _aCode in self.siTypes_analysisCodes['WOI'] if ((_aCode in self.bidsAndAsks) and (self.objectConfig['WOI_{:d}_Display'.format(int(_aCode.split("_")[1]))] == True))]
            if (self.objectConfig['WOI_BASE_Display'] == True): _aCodesToConsider.insert(0, 'WOI')
            _tt_beg = int(self.horizontalViewRange[0])
            _tt_end = math.ceil(self.horizontalViewRange[1])
            for _aCode in _aCodesToConsider:
                for _tt in self.bidsAndAsks[_aCode]:
                    if ((_tt_beg <= _tt) and (_tt <= _tt_end)):
                        if (_aCode == 'WOI'): _woiResult = self.bidsAndAsks[_aCode][_tt]
                        else:                 _woiResult = self.bidsAndAsks[_aCode][_tt][1]
                        if (_woiResult != None):
                            if (_woiResult < valMin): valMin = _woiResult
                            if (valMax < _woiResult): valMax = _woiResult
            if (0 < valMin): valMin = 0
            if (valMax < 0): valMax = 0
            valMin_abs = abs(valMin)
            valMax_abs = abs(valMax)
            if (valMin_abs < valMax_abs): valMin = -valMax_abs; valMax = valMax_abs
            else:                         valMin = -valMin_abs; valMax = valMin_abs
            if ((valMin == 0) and (valMax == 0)): valMin = -1; valMax = 1
        #If the extremas within the horizontalViewRange are updated
        if (((valMin != float('inf')) and (valMax != float('-inf'))) and ((self.verticalValue_loaded[siViewerCode] == False) or (self.verticalValue_min[siViewerCode] != valMin) or (self.verticalValue_max[siViewerCode] != valMax))): #The found extremas are different
            self.verticalValue_loaded[siViewerCode] = True
            self.verticalValue_min[siViewerCode] = valMin
            self.verticalValue_max[siViewerCode] = valMax
            return True
        else: return False

    def __checkVerticalExtremas_NES(self):
        #SI Viewer Allocation
        siViewerCode = "SIVIEWER{:d}".format(self.siTypes_siViewerAlloc['NES'])
        #Extrema Value Init
        valMin = float('inf')
        valMax = float('-inf')
        #Find new vertical extremas
        if (self.siTypes_analysisCodes['NES'] != None):
            _aCodesToConsider = [_aCode for _aCode in self.siTypes_analysisCodes['NES'] if ((_aCode in self.aggTrades) and (self.objectConfig['NES_{:d}_Display'.format(int(_aCode.split("_")[1]))] == True))]
            if (self.objectConfig['NES_BASE_Display'] == True): _aCodesToConsider.insert(0, 'NES')
            _tt_beg = int(self.horizontalViewRange[0])
            _tt_end = math.ceil(self.horizontalViewRange[1])
            for _aCode in _aCodesToConsider:
                for _tt in self.aggTrades[_aCode]:
                    if ((_tt_beg <= _tt) and (_tt <= _tt_end)):
                        if (_aCode == 'NES'): _nesResult = self.aggTrades[_aCode][_tt]
                        else:                 _nesResult = self.aggTrades[_aCode][_tt][1]
                        if (_nesResult != None):
                            if (_nesResult < valMin): valMin = _nesResult
                            if (valMax < _nesResult): valMax = _nesResult
            if (0 < valMin): valMin = 0
            if (valMax < 0): valMax = 0
            valMin_abs = abs(valMin)
            valMax_abs = abs(valMax)
            if (valMin_abs < valMax_abs): valMin = -valMax_abs; valMax = valMax_abs
            else:                         valMin = -valMin_abs; valMax = valMin_abs
            if ((valMin == 0) and (valMax == 0)): valMin = -1; valMax = 1
        #If the extremas within the horizontalViewRange are updated
        if (((valMin != float('inf')) and (valMax != float('-inf'))) and ((self.verticalValue_loaded[siViewerCode] == False) or (self.verticalValue_min[siViewerCode] != valMin) or (self.verticalValue_max[siViewerCode] != valMax))): #The found extremas are different
            self.verticalValue_loaded[siViewerCode] = True
            self.verticalValue_min[siViewerCode] = valMin
            self.verticalValue_max[siViewerCode] = valMax
            return True
        else: return False

    def __onVerticalExtremaUpdate(self, displayBoxName, updateType = 0):
        verticalExtremaDelta = self.verticalValue_max[displayBoxName]-self.verticalValue_min[displayBoxName]
        newViewRangeHeight_min = verticalExtremaDelta*100/_GD_DISPLAYBOX_VVR_MAGNITUDE_MAX[displayBoxName]
        newViewRangeHeight_max = verticalExtremaDelta*100/_GD_DISPLAYBOX_VVR_MAGNITUDE_MIN[displayBoxName]
        if (updateType == 0):
            previousViewRangeCenter = (self.verticalViewRange[displayBoxName][0]+self.verticalViewRange[displayBoxName][1])/2
            previousViewRangeHeight = self.verticalViewRange[displayBoxName][1]-self.verticalViewRange[displayBoxName][0]
            if   (previousViewRangeHeight < newViewRangeHeight_min): vVR_effective = [previousViewRangeCenter-newViewRangeHeight_min*0.5, previousViewRangeCenter+newViewRangeHeight_min*0.5]; self.verticalViewRange_magnification[displayBoxName] = _GD_DISPLAYBOX_VVR_MAGNITUDE_MAX[displayBoxName]
            elif (newViewRangeHeight_max < previousViewRangeHeight): vVR_effective = [previousViewRangeCenter-newViewRangeHeight_max*0.5, previousViewRangeCenter+newViewRangeHeight_max*0.5]; self.verticalViewRange_magnification[displayBoxName] = _GD_DISPLAYBOX_VVR_MAGNITUDE_MIN[displayBoxName]
            else:                                                    vVR_effective = self.verticalViewRange[displayBoxName];                                                                   self.verticalViewRange_magnification[displayBoxName] = round(verticalExtremaDelta/previousViewRangeHeight*100, 1)
            self.verticalViewRange[displayBoxName] = [round(vVR_effective[0], self.verticalViewRange_precision[displayBoxName]), round(vVR_effective[1], self.verticalViewRange_precision[displayBoxName])]
            if (previousViewRangeHeight == self.verticalViewRange[displayBoxName][1]-self.verticalViewRange[displayBoxName][0]): self.__onVViewRangeUpdate(displayBoxName, 0)
            else:                                                                                                                self.__onVViewRangeUpdate(displayBoxName, 1)
        elif (updateType == 1):
            extremaCenter = (self.verticalValue_min[displayBoxName]+self.verticalValue_max[displayBoxName])/2
            self.verticalViewRange_magnification[displayBoxName] = _GD_DISPLAYBOX_VVR_MAGNITUDE_MAX[displayBoxName]
            self.verticalViewRange[displayBoxName] = [round(extremaCenter-newViewRangeHeight_min*0.5, self.verticalViewRange_precision[displayBoxName]), round(extremaCenter+newViewRangeHeight_min*0.5, self.verticalViewRange_precision[displayBoxName])]
            self.__onVViewRangeUpdate(displayBoxName, 1)
        
    #[2]: Vertical Position and Magnification
    #---Vertical Position
    def __editVPosition(self, displayBoxName, delta_drag = None, delta_scroll = None):
        if   (delta_drag   != None): effectiveDelta = -delta_drag  *(self.verticalViewRange[displayBoxName][1]-self.verticalViewRange[displayBoxName][0])/self.displayBox_graphics[displayBoxName]['DRAWBOX'][3]
        elif (delta_scroll != None): effectiveDelta = -delta_scroll*(self.verticalViewRange[displayBoxName][1]-self.verticalViewRange[displayBoxName][0])/50
        vVR_effective = [self.verticalViewRange[displayBoxName][0]+effectiveDelta, self.verticalViewRange[displayBoxName][1]+effectiveDelta]
        self.verticalViewRange[displayBoxName] = vVR_effective
        self.__onVViewRangeUpdate(displayBoxName, 0)
        
    #---Vertical Magnification
    def __editVMagFactor(self, displayBoxName, delta_drag = None, delta_scroll = None, anchor = 'CENTER'):
        if   (delta_drag   != None): newMagnitudeFactor = self.verticalViewRange_magnification[displayBoxName] + delta_drag*200/self.displayBox_graphics[displayBoxName]['DRAWBOX'][3]
        elif (delta_scroll != None): newMagnitudeFactor = self.verticalViewRange_magnification[displayBoxName] + delta_scroll
        #Rounding
        newMagnitudeFactor = round(newMagnitudeFactor, 1)
        #Boundary Control
        if   (newMagnitudeFactor < _GD_DISPLAYBOX_VVR_MAGNITUDE_MIN[displayBoxName]): newMagnitudeFactor = _GD_DISPLAYBOX_VVR_MAGNITUDE_MIN[displayBoxName]
        elif (_GD_DISPLAYBOX_VVR_MAGNITUDE_MAX[displayBoxName] < newMagnitudeFactor): newMagnitudeFactor = _GD_DISPLAYBOX_VVR_MAGNITUDE_MAX[displayBoxName]
        #Variation Check and response
        if (newMagnitudeFactor != self.verticalViewRange_magnification[displayBoxName]):
            #Calculate new viewRange
            self.verticalViewRange_magnification[displayBoxName] = newMagnitudeFactor
            verticalExtremaDelta = self.verticalValue_max[displayBoxName]-self.verticalValue_min[displayBoxName]
            verticalExtremaDelta_magnified = verticalExtremaDelta*100/self.verticalViewRange_magnification[displayBoxName]
            if (anchor == 'CENTER'):
                vVRCenter = (self.verticalViewRange[displayBoxName][0]+self.verticalViewRange[displayBoxName][1])/2
                vVR_effective = [vVRCenter-verticalExtremaDelta_magnified*0.5, vVRCenter+verticalExtremaDelta_magnified*0.5]
            elif (anchor == 'BOTTOM'): vVR_effective = [self.verticalViewRange[displayBoxName][0], self.verticalViewRange[displayBoxName][0]+verticalExtremaDelta_magnified]
            elif (anchor == 'TOP'):    vVR_effective = [self.verticalViewRange[displayBoxName][1]-verticalExtremaDelta_magnified, self.verticalViewRange[displayBoxName][1]]
            self.verticalViewRange[displayBoxName] = [vVR_effective[0], vVR_effective[1]]
            self.__onVViewRangeUpdate(displayBoxName, 1)
            
    #---Reset vVR_price
    def __editVVR_toExtremaCenter(self, displayBoxName, extension_b = 0.1, extension_t = 0.1):
        #Extension Limit Control
        if (extension_b < 0): extension_b = 0
        if (extension_t < 0): extension_t = 0
        extensionLimit_min = (100/_GD_DISPLAYBOX_VVR_MAGNITUDE_MAX[displayBoxName])-1
        extensionLimit_max = (100/_GD_DISPLAYBOX_VVR_MAGNITUDE_MIN[displayBoxName])-1
        extensionSum = extension_b + extension_t
        if ((extensionLimit_min <= extensionSum) and (extensionSum <= extensionLimit_max)):
            extension_b = extension_b
            extension_t = extension_t
        else:
            extensionSumScaler = extensionSum / extensionLimit_max
            extension_b = extension_b / extensionSumScaler
            extension_t = extension_t / extensionSumScaler
        #ViewRange and new Magnification Computation
        verticalExtremaCenter = (self.verticalValue_min[displayBoxName]+self.verticalValue_max[displayBoxName])/2
        verticalExtremaDelta = self.verticalValue_max[displayBoxName]-self.verticalValue_min[displayBoxName]
        if (verticalExtremaDelta == 0):
            verticalExtremaDelta = 1
            vVR_effective = [-verticalExtremaDelta*0.5, verticalExtremaDelta*0.5]
        else:
            verticalExtremaDelta_b = verticalExtremaDelta*(0.5+extension_b)
            verticalExtremaDelta_t = verticalExtremaDelta*(0.5+extension_t)
            vVR_effective = [verticalExtremaCenter-verticalExtremaDelta_b, verticalExtremaCenter+verticalExtremaDelta_t]
        self.verticalViewRange[displayBoxName] = [vVR_effective[0], vVR_effective[1]]
        self.verticalViewRange_magnification[displayBoxName] = round(verticalExtremaDelta/(vVR_effective[1]-vVR_effective[0])*100, 1)
        self.__onVViewRangeUpdate(displayBoxName, 1)
        
    #---Post Vertical ViewRange Update
    def __onVViewRangeUpdate(self, displayBoxName, updateType):
        #Update RCLCGs
        self.displayBox_graphics[displayBoxName]['RCLCG'].updateProjection(projection_y0        = self.verticalViewRange[displayBoxName][0], projection_y1 = self.verticalViewRange[displayBoxName][1])
        self.displayBox_graphics[displayBoxName]['RCLCG_XFIXED'].updateProjection(projection_y0 = self.verticalViewRange[displayBoxName][0], projection_y1 = self.verticalViewRange[displayBoxName][1])

        #Horizontal Grid Lines
        gridContentsUpdateFlag = False
        if (updateType == 1):
            viewRangeHeight = self.verticalViewRange[displayBoxName][1]-self.verticalViewRange[displayBoxName][0]
            viewRangeHeight_OOM = math.floor(math.log(viewRangeHeight, 10))
            for intervalFactor in (0.1, 0.25, 0.5, 0.75, 1, 2.5, 5, 7.5):
                intervalHeight = intervalFactor*pow(10, viewRangeHeight_OOM)
                if (intervalHeight == 0): return # <--- Temporary fix
                bottomEnd = int(self.verticalViewRange[displayBoxName][0]/intervalHeight)    *intervalHeight
                topEnd    = (int(self.verticalViewRange[displayBoxName][1]/intervalHeight)+1)*intervalHeight
                nIntervals = int((topEnd-bottomEnd)/intervalHeight)+1
                if (nIntervals+1 <= self.nMaxHorizontalGridLines[displayBoxName]): 
                    horizontalGridIntervals = list()
                    value = bottomEnd
                    while (value <= topEnd): horizontalGridIntervals.append(value); value += intervalHeight
                    self.horizontalGridIntervalHeight[displayBoxName] = intervalHeight
                    break
            gridContentsUpdateFlag = True
        elif (updateType == 0):
            bottomEnd = int(self.verticalViewRange[displayBoxName][0]/self.horizontalGridIntervalHeight[displayBoxName])*self.horizontalGridIntervalHeight[displayBoxName]
            topEnd    = (int(self.verticalViewRange[displayBoxName][1]/self.horizontalGridIntervalHeight[displayBoxName])+1)*self.horizontalGridIntervalHeight[displayBoxName]
            if ((self.horizontalGridIntervals[displayBoxName][0] != bottomEnd) or (self.horizontalGridIntervals[displayBoxName][-1] != topEnd)):
                horizontalGridIntervals = list()
                value = bottomEnd
                while (value <= topEnd): horizontalGridIntervals.append(value); value += self.horizontalGridIntervalHeight[displayBoxName]
                gridContentsUpdateFlag = True
                
        pixelPerUnitHeight = self.displayBox_graphics[displayBoxName]['DRAWBOX'][3]*self.scaler / (self.verticalViewRange[displayBoxName][1]-self.verticalViewRange[displayBoxName][0])
        if (gridContentsUpdateFlag == True):
            self.horizontalGridIntervals[displayBoxName] = horizontalGridIntervals
            for index in range (self.nMaxHorizontalGridLines[displayBoxName]):
                if (index < len(self.horizontalGridIntervals[displayBoxName])):
                    verticalValue = self.horizontalGridIntervals[displayBoxName][index]
                    yPos_Line = round((verticalValue-self.horizontalGridIntervals[displayBoxName][0])*pixelPerUnitHeight, 1)
                    #Grid Lines
                    self.displayBox_graphics[displayBoxName]['HORIZONTALGRID_LINES'][index].y             = yPos_Line; self.displayBox_graphics[displayBoxName]['HORIZONTALGRID_LINES'][index].y2             = yPos_Line
                    self.displayBox_graphics['MAINGRID_'+displayBoxName]['HORIZONTALGRID_LINES'][index].y = yPos_Line; self.displayBox_graphics['MAINGRID_'+displayBoxName]['HORIZONTALGRID_LINES'][index].y2 = yPos_Line
                    if (self.displayBox_graphics[displayBoxName]['HORIZONTALGRID_LINES'][index].visible == False):             self.displayBox_graphics[displayBoxName]['HORIZONTALGRID_LINES'][index].visible             = True
                    if (self.displayBox_graphics['MAINGRID_'+displayBoxName]['HORIZONTALGRID_LINES'][index].visible == False): self.displayBox_graphics['MAINGRID_'+displayBoxName]['HORIZONTALGRID_LINES'][index].visible = True
                    #Grid Text
                    if (verticalValue == 0): verticalValue_formatted = "0"
                    else:                    verticalValue_formatted = atmEta_Auxillaries.simpleValueFormatter(value = verticalValue, precision = 2)
                    self.displayBox_graphics['MAINGRID_'+displayBoxName]['HORIZONTALGRID_TEXTS'][index].setText(verticalValue_formatted)
                    self.displayBox_graphics['MAINGRID_'+displayBoxName]['HORIZONTALGRID_TEXTS'][index].moveTo(y = round((yPos_Line)/self.scaler-_GD_DISPLAYBOX_GRID_HORIZONTALTEXTHEIGHT/2))
                    if (self.displayBox_graphics['MAINGRID_'+displayBoxName]['HORIZONTALGRID_TEXTS'][index].hidden == True): self.displayBox_graphics['MAINGRID_'+displayBoxName]['HORIZONTALGRID_TEXTS'][index].show()
                else:
                    if (self.displayBox_graphics[displayBoxName]['HORIZONTALGRID_LINES'][index].visible == True):             self.displayBox_graphics[displayBoxName]['HORIZONTALGRID_LINES'][index].visible             = False
                    if (self.displayBox_graphics['MAINGRID_'+displayBoxName]['HORIZONTALGRID_LINES'][index].visible == True): self.displayBox_graphics['MAINGRID_'+displayBoxName]['HORIZONTALGRID_LINES'][index].visible = False
                    if (self.displayBox_graphics['MAINGRID_'+displayBoxName]['HORIZONTALGRID_TEXTS'][index].hidden == False): self.displayBox_graphics['MAINGRID_'+displayBoxName]['HORIZONTALGRID_TEXTS'][index].hide()
        projectionY0 = (self.verticalViewRange[displayBoxName][0]-self.horizontalGridIntervals[displayBoxName][0])*pixelPerUnitHeight
        projectionY1 = projectionY0+self.displayBox_graphics[displayBoxName]['DRAWBOX'][3]*self.scaler
        self.displayBox_graphics[displayBoxName]['HORIZONTALGRID_CAMGROUP'].updateProjection(projection_y0=projectionY0, projection_y1=projectionY1)
        self.displayBox_graphics['MAINGRID_'+displayBoxName]['HORIZONTALGRID_CAMGROUP'].updateProjection(projection_y0=projectionY0, projection_y1=projectionY1)
    #View Control END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    


    #Kline Data -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def setTarget(self, target, intervalID = None):
        self.intervalID = atmEta_Constants.KLINTERVAL
        if   (self.chartDrawerType == 'CAVIEWER'): self.__setTarget_CAViewer(currencyAnalysisCode = target)
        elif (self.chartDrawerType == 'TLVIEWER'): self.__setTarget_TLViewer(target = target)
        elif (self.chartDrawerType == 'ANALYZER'): self.__setTarget_Analyzer(currencySymbol = target)
   
    #<Currency Analysis Viewer>
    def __setTarget_CAViewer(self, currencyAnalysisCode):
        #If there was a subscribed currency, send a subscription unregistration request
        if ((self.currencySymbol != None) and (self.currencyAnalysis['allocatedAnalyzer'] != None)): self.__CAViewer_sendCADataSubscriptionUnregistrationRequest()
        #Read Currency Analysis Info
        self.currencyAnalysisCode = currencyAnalysisCode
        if (self.currencyAnalysisCode == None):
            self.currencyAnalysis = None
            self.analysisParams = dict()
            self.currencySymbol = None
            self.currencyInfo   = None
            #Setup Klines Loading Gauge Objects
            self.frameSprites['KLINELOADINGCOVER'].visible = False
            self.klinesLoadingGaugeBar.hide()
            self.klinesLoadingTextBox.hide()
            self.klinesLoadingTextBox_perc.hide()
            self.klinesLoadingGaugeBar.updateGaugeValue(0)
            self.klinesLoadingTextBox_perc.updateText("-")
            #Reset Klines
            for dataType in self.klines:      self.klines[dataType].clear()
            self.bidsAndAsks = {'depth': dict(), 'WOI': dict(), 'WOI_GD': dict()}
            self.aggTrades['volumes'] = {'samples': list(), 'buy': 0, 'sell': 0}
            for dataType in self.aggTrades: 
                if (dataType != 'volumes'): self.aggTrades[dataType].clear()
            self.klines_fetchComplete           = False
            self.klines_fetching                = False
            self.klines_lastStreamedKlineOpenTS = None
            self.bidsAndAsks_drawFlag             = False
            self.bidsAndAsks_WOI_oldestComputedS  = None
            self.bidsAndAsks_WOI_latestComputedS  = None
            self.bidsAndAsks_WOI_drawQueue        = dict()
            self.bidsAndAsks_WOI_drawn            = dict()
            self.bidsAndAsks_WOI_drawRemovalQueue = set()
            self.aggTrades_NES_oldestComputedS    = None
            self.aggTrades_NES_latestComputedS    = None
            self.aggTrades_NES_drawQueue          = dict()
            self.aggTrades_NES_drawn              = dict()
            self.aggTrades_NES_drawRemovalQueue   = set()
            self.klines_drawn.clear()
            self.klines_drawRemovalQueue.clear()
            self.klines_drawQueue.clear()
            #Horizontal ViewRange Params Setup
            self.__setHVRParams()
            #Call this now since no klines will be fetched
            self.__CAViewer_onKlineFetchComplete()
        else:
            self.currencyAnalysis = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode))
            self.analysisParams = dict()
            self.__readCurrencyAnalysisConfiguration(currencyAnalysisConfiguration = self.currencyAnalysis['currencyAnalysisConfiguration'])
            self.currencySymbol = self.currencyAnalysis['currencySymbol']
            self.currencyInfo   = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', self.currencySymbol))
            #Setup Klines Loading Gauge Objects
            self.frameSprites['KLINELOADINGCOVER'].visible = True
            self.klinesLoadingGaugeBar.show()
            self.klinesLoadingTextBox.show()
            self.klinesLoadingTextBox_perc.show()
            self.klinesLoadingGaugeBar.updateGaugeValue(0)
            self.klinesLoadingTextBox_perc.updateText("-")
            if (self.currencyAnalysis['allocatedAnalyzer'] == None): self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGANALYZERALLOCATION'))
            else:                                                    self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:REQUESTINGCADATASUBSCRIPTIONREGISTRATION'))
            #Update Highlighters and Descriptors
            self.posHighlight_hoveredPos       = (None, None, None, None)
            self.posHighlight_updatedPositions = None
            self.posHighlight_selectedPos      = None
            self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_HOVERED'].visible  = False
            self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_SELECTED'].visible = False
            self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT1'].setText("")
            self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2'].setText("")
            for siViewerName in self.displayBox_graphics_visibleSIViewers:
                self.displayBox_graphics[siViewerName]['POSHIGHLIGHT_HOVERED'].visible  = False 
                self.displayBox_graphics[siViewerName]['POSHIGHLIGHT_SELECTED'].visible = False
                self.displayBox_graphics[siViewerName]['DESCRIPTIONTEXT1'].setText("")
            #Reset Klines
            for dataType in self.klines:      self.klines[dataType].clear()
            self.bidsAndAsks = {'depth': dict(), 'WOI': dict(), 'WOI_GD': dict()}
            self.aggTrades['volumes'] = {'samples': list(), 'buy': 0, 'sell': 0}
            for dataType in self.aggTrades: 
                if (dataType != 'volumes'): self.aggTrades[dataType].clear()
            self.klines_fetchComplete           = False
            self.klines_fetching                = True
            self.klines_lastStreamedKlineOpenTS = None
            self.bidsAndAsks_drawFlag             = False
            self.bidsAndAsks_WOI_oldestComputedS  = None
            self.bidsAndAsks_WOI_latestComputedS  = None
            self.bidsAndAsks_WOI_drawQueue        = dict()
            self.bidsAndAsks_WOI_drawn            = dict()
            self.bidsAndAsks_WOI_drawRemovalQueue = set()
            self.aggTrades_NES_oldestComputedS    = None
            self.aggTrades_NES_latestComputedS    = None
            self.aggTrades_NES_drawQueue          = dict()
            self.aggTrades_NES_drawn              = dict()
            self.aggTrades_NES_drawRemovalQueue   = set()
            self.klines_drawn.clear()
            self.klines_drawRemovalQueue.clear()
            self.klines_drawQueue.clear()
            #Horizontal ViewRange Params Setup
            self.__setHVRParams()
            #Get Currency Precisions & Update RCLCG Precisions
            self.__initializeRCLCGs('KLINESPRICE')
            for siViewerCode in self.displayBox_graphics_visibleSIViewers: self.__initializeSIViewer(siViewerCode)
            #Send a subscription registration request
            if (self.currencyAnalysis['allocatedAnalyzer'] != None): self.__CAViewer_sendCADataSubscriptionRegistrationRequest()
    def CAViewer_onCurrencyAnalysisUpdate(self, updateType, currencyAnalysisCode):
        if (currencyAnalysisCode == self.currencyAnalysisCode):
            if (updateType == 'UPDATE_ANALYZER'):
                allocatedAnalyzer = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode, 'allocatedAnalyzer'))
                self.currencyAnalysis['allocatedAnalyzer'] = allocatedAnalyzer
                self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:LOADINGKLINES'))
                self.__CAViewer_sendCADataSubscriptionRegistrationRequest()
            elif (updateType == 'REMOVED'): self.setTarget(currencyAnalysisCode = None)
    def __CAViewer_sendCADataSubscriptionRegistrationRequest(self):
        self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:REQUESTINGCADATASUBSCRIPTIONREGISTRATION'))
        caDataReceiver = "caDataReceiver_{:s}".format(self.name)
        self.ipcA.addFARHandler(caDataReceiver, self.__CAViewer_receiveCAData_FAR, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.sendFAR(targetProcess  = 'ANALYZER{:d}'.format(self.currencyAnalysis['allocatedAnalyzer']),
                          functionID     = 'registerCurrencyAnalysisDataSubscription',
                          functionParams = {'currencyAnalysisCode': self.currencyAnalysisCode,
                                            'dataReceiver': caDataReceiver},
                          farrHandler    = self.__CAViewer_sendCADataSubscriptionRegistrationRequest_FARR)
    def __CAViewer_sendCADataSubscriptionRegistrationRequest_FARR(self, responder, requestID, functionResult):
        if (responder == 'ANALYZER{:d}'.format(self.currencyAnalysis['allocatedAnalyzer'])):
            self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:LOADINGKLINES'))
            #Analysis Params Read & Analysis Codes by SITypes Configuration
            if (True):
                #---Analysis Params
                self.analysisParams = functionResult['analysisParams']
                #---Analysis Codes by SITypes
                self.siTypes_analysisCodes['VOL'] = {'VOL'}
                for analysisCode in self.analysisParams:
                    if (analysisCode[:3] == 'VOL'): self.siTypes_analysisCodes['VOL'].add(analysisCode)
                if ('MMACDSHORT' in self.analysisParams): self.siTypes_analysisCodes['MMACDSHORT'] = set(['MMACDSHORT'])
                if ('MMACDLONG'  in self.analysisParams): self.siTypes_analysisCodes['MMACDLONG']  = set(['MMACDLONG'])
                analysisCodes_mfi = [analysisCode for analysisCode in self.analysisParams if analysisCode[:3] == 'MFI']
                if (0 < len(analysisCodes_mfi)): self.siTypes_analysisCodes['MFI'] = set(analysisCodes_mfi)
                analysisCodes_dmixadx = [analysisCode for analysisCode in self.analysisParams if analysisCode[:7] == 'DMIxADX']
                if (0 < len(analysisCodes_dmixadx)): self.siTypes_analysisCodes['DMIxADX'] = set(analysisCodes_dmixadx)
                #---Analysis Codes by SITypes (WOI and NES)
            if (functionResult['klines']      != None): self.__CAViewer_receiveCAData(dataType = 'KLINES',      caData = functionResult['klines'])
            if (functionResult['bidsAndAsks'] != None): self.__CAViewer_receiveCAData(dataType = 'BIDSANDASKS', caData = functionResult['bidsAndAsks'])
            if (functionResult['aggTrades']   != None): self.__CAViewer_receiveCAData(dataType = 'AGGTRADES',   caData = functionResult['aggTrades'])
    def __CAViewer_sendCADataSubscriptionUnregistrationRequest(self):
        caDataReceiver = "caDataReceiver_{:s}".format(self.name)
        self.ipcA.removeFARHandler(caDataReceiver)
        self.ipcA.sendFAR(targetProcess  = 'ANALYZER{:d}'.format(self.currencyAnalysis['allocatedAnalyzer']),
                          functionID     = 'unregisterCurrencyAnalysisDataSubscription',
                          functionParams = {'currencyAnalysisCode': self.currencyAnalysisCode,
                                            'dataReceiver': caDataReceiver},
                          farrHandler    = None)
    def __CAViewer_receiveCAData(self, dataType, caData):
        #[1]: Klines
        if (dataType == 'KLINES'):
            for _klDataType in caData:
                if (_klDataType not in self.klines): self.klines[_klDataType] = dict()
                for _ts_open in caData[_klDataType]:
                    self.klines[_klDataType][_ts_open] = caData[_klDataType][_ts_open]
                    _ts_close = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = _ts_open, mrktReg = self.mrktRegTS, nTicks = 1)-1
                    if (_klDataType != 'raw_status'):
                        classification = 0
                        classification += 0b1000*(0 <= _ts_open -self.horizontalViewRange[0])
                        classification += 0b0100*(0 <= _ts_open -self.horizontalViewRange[1])
                        classification += 0b0010*(0 <  _ts_close-self.horizontalViewRange[0])
                        classification += 0b0001*(0 <  _ts_close-self.horizontalViewRange[1])
                        if ((classification == 0b0010) or (classification == 0b1010) or (classification == 0b1011) or (classification == 0b0011)):
                            if (_klDataType == 'raw'): _drawQueueCode = 'KLINE'
                            else:                      _drawQueueCode = _klDataType
                            if (_ts_open in self.klines_drawQueue): self.klines_drawQueue[_ts_open][_drawQueueCode] = None
                            else:                                   self.klines_drawQueue[_ts_open] = {_drawQueueCode: None}
                    if (_klDataType == 'raw'):
                        if ((self.klines_lastStreamedKlineOpenTS == None) or (self.klines_lastStreamedKlineOpenTS < _ts_open)): self.klines_lastStreamedKlineOpenTS = _ts_open
            if (self.klines_fetchComplete == False): self.__CAViewer_onKlineFetchComplete()
        #[2]: Bids And Asks
        elif (dataType == 'BIDSANDASKS'):
            for _baaDataType in caData:
                if (_baaDataType not in self.bidsAndAsks): self.bidsAndAsks[_baaDataType] = dict()
                if (_baaDataType == 'depth'): self.bidsAndAsks['depth'] = caData['depth']
                else:
                    for _tt in caData[_baaDataType]: 
                        self.bidsAndAsks[_baaDataType][_tt] = caData[_baaDataType][_tt]
                        if (_tt in self.bidsAndAsks_WOI_drawQueue): self.bidsAndAsks_WOI_drawQueue[_tt].add(_baaDataType)
                        else:                                       self.bidsAndAsks_WOI_drawQueue[_tt] = {_baaDataType}
            self.bidsAndAsks_drawFlag = True
        #[3]: AggTrades
        elif (dataType == 'AGGTRADES'):
            for _atDataType in caData:
                if (_atDataType not in self.aggTrades): self.aggTrades[_atDataType] = dict()
                if (_atDataType != 'volumes'):
                    for _tt in caData[_atDataType]:
                        self.aggTrades[_atDataType][_tt] = caData[_atDataType][_tt]
                        if (_tt in self.aggTrades_NES_drawQueue): self.aggTrades_NES_drawQueue[_tt].add(_atDataType)
                        else:                                     self.aggTrades_NES_drawQueue[_tt] = {_atDataType}
    def __CAViewer_receiveCAData_FAR(self, requester, currencyAnalysisCode, dataType, caData):
        if ((self.currencyAnalysis['allocatedAnalyzer'] != None) and (requester == "ANALYZER{:d}".format(self.currencyAnalysis['allocatedAnalyzer'])) and (currencyAnalysisCode == self.currencyAnalysisCode)): self.__CAViewer_receiveCAData(dataType = dataType, caData = caData)
    def __CAViewer_onKlineFetchComplete(self):
        #Control Variables Update
        self.klines_fetchComplete = True
        self.klines_fetching      = False
        #Loading Indicator Graphics Control
        self.frameSprites['KLINELOADINGCOVER'].visible = False
        self.klinesLoadingGaugeBar.hide()
        self.klinesLoadingTextBox_perc.hide()
        self.klinesLoadingTextBox.hide()
        #Horizontal ViewRange Reset
        self.horizontalViewRange_magnification = 80
        self.horizontalViewRange = [None, round(time.time()+self.expectedKlineTemporalWidth*2)]
        self.horizontalViewRange[0] = round(self.horizontalViewRange[1]-(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
        self.__onHViewRangeUpdate(1)
        #Vertical ViewRange Reset
        self.__editVVR_toExtremaCenter('KLINESPRICE')
        for siViewerCode in self.displayBox_graphics_visibleSIViewers: self.__editVVR_toExtremaCenter(siViewerCode)

    #<TradeLogViewer>
    def __setTarget_TLViewer(self, target):
        #Read Currency Analysis Info
        if (target == None):
            self.simulationCode = None
            self.simulation     = None
            self.currencySymbol = None
            self.currencyInfo   = None
            #Klines Fetch Range
            self.klines_targetFetchRange_original = None
            self.klines_targetFetchRange_current  = None
            #CA Regeneration
            self.caRegeneration_nAnalysis_initial = None
            self.analysisParams           = dict()
            self.analysisToProcess_Sorted = list()
            for siType in _SITYPES: self.siTypes_analysisCodes[siType] = list()
            self.analysisQueue_list.clear()
            self.analysisQueue_set.clear()
            #Setup Klines Loading Gauge Objects
            self.frameSprites['KLINELOADINGCOVER'].visible = False
            self.klinesLoadingGaugeBar.hide()
            self.klinesLoadingTextBox.hide()
            self.klinesLoadingTextBox_perc.hide()
            self.klinesLoadingGaugeBar.updateGaugeValue(0)
            self.klinesLoadingTextBox_perc.updateText("-")
            #Reset Klines
            for dataType in self.klines:      self.klines[dataType].clear()
            self.bidsAndAsks = {'depth': dict(), 'WOI': dict(), 'WOI_GD': dict()}
            self.aggTrades['volumes'] = {'samples': list(), 'buy': 0, 'sell': 0}
            for dataType in self.aggTrades: 
                if (dataType != 'volumes'): self.aggTrades[dataType].clear()
            self.klines_fetchComplete = False
            self.klines_fetching      = False
            self.klines_drawn.clear()
            self.klines_drawRemovalQueue.clear()
            self.klines_drawQueue.clear()
            self.klines_fetchRequestRID = None
            self.bidsAndAsks_drawFlag             = False
            self.bidsAndAsks_WOI_oldestComputedS  = None
            self.bidsAndAsks_WOI_latestComputedS  = None
            self.bidsAndAsks_WOI_drawQueue        = dict()
            self.bidsAndAsks_WOI_drawn            = dict()
            self.bidsAndAsks_WOI_drawRemovalQueue = set()
            self.aggTrades_NES_oldestComputedS    = None
            self.aggTrades_NES_latestComputedS    = None
            self.aggTrades_NES_drawQueue          = dict()
            self.aggTrades_NES_drawn              = dict()
            self.aggTrades_NES_drawRemovalQueue   = set()
            #Reset Neural Networks
            self.neuralNetworkConnectionDataRequestID = None
            self.neuralNetworkInstance                = None
            torch.cuda.empty_cache()
            #Horizontal ViewRange Params Setup
            self.__setHVRParams()
            #Reset ViewRange
            self.horizontalViewRange_magnification = 100
            self.horizontalViewRange = [None, round(time.time()+self.expectedKlineTemporalWidth*5)]
            self.horizontalViewRange[0] = round(self.horizontalViewRange[1]-(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
            self.__onHViewRangeUpdate(1)
            self.__editVVR_toExtremaCenter('KLINESPRICE')
            for siViewerCode in self.displayBox_graphics_visibleSIViewers: self.__editVVR_toExtremaCenter(siViewerCode)
        else:
            self.simulationCode = target[0]
            self.currencySymbol = target[1]
            self.simulation = self.ipcA.getPRD(processName = 'SIMULATIONMANAGER', prdAddress = ('SIMULATIONS', self.simulationCode))
            _currencyAnalysisConfiguration = self.simulation['currencyAnalysisConfigurations'][self.simulation['positions'][self.currencySymbol]['currencyAnalysisConfigurationCode']]
            self.__readCurrencyAnalysisConfiguration(currencyAnalysisConfiguration = _currencyAnalysisConfiguration)
            self.currencyInfo = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', self.currencySymbol))
            self.targetPrecisions = self.simulation['positions'][self.currencySymbol]['precisions'].copy()
            #Klines Fetch Range
            _positionDataRange = self.simulation['positions'][self.currencySymbol]['dataRange']
            _simulationRange = (atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = self.simulation['simulationRange'][0], mrktReg = None, nTicks = 0),
                                atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = self.simulation['simulationRange'][1], mrktReg = None, nTicks = 1)-1)
            if (_simulationRange[0] <= _positionDataRange[0]):
                if (_simulationRange[1] <= _positionDataRange[1]): _targetFetchRange = (_positionDataRange[0], _simulationRange[1])
                else:                                              _targetFetchRange = (_positionDataRange[0], _positionDataRange[1])
            else:
                if (_simulationRange[1] <= _positionDataRange[1]): _targetFetchRange = (_simulationRange[0], _simulationRange[1])
                else:                                              _targetFetchRange = (_simulationRange[0], _positionDataRange[1])
            if (_targetFetchRange[0] < _targetFetchRange[1]):
                self.klines_targetFetchRange_original = _targetFetchRange
                self.klines_targetFetchRange_current  = [_targetFetchRange[0], _targetFetchRange[1]]
            else:
                self.klines_targetFetchRange_original = None
                self.klines_targetFetchRange_current  = None
            #CA Regeneration
            self.caRegeneration_nAnalysis_initial = None
            self.analysisParams           = atmEta_Analyzers.constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration(_currencyAnalysisConfiguration)
            self.analysisToProcess_Sorted = list()
            for siType in _SITYPES: self.siTypes_analysisCodes[siType] = list()
            self.analysisQueue_list.clear()
            self.analysisQueue_set.clear()
            #Setup Klines Loading Gauge Objects
            self.frameSprites['KLINELOADINGCOVER'].visible = True
            self.klinesLoadingGaugeBar.show()
            self.klinesLoadingTextBox.show()
            self.klinesLoadingTextBox_perc.show()
            self.klinesLoadingGaugeBar.updateGaugeValue(0)
            self.klinesLoadingTextBox_perc.updateText("-")
            if (self.klines_targetFetchRange_original != None): self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:FETCHINGTRADELOGDATA'))
            else:                                               self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:NOTARGETDATARANGEINTERSECTION'))
            #Update Highlighters and Descriptors
            self.posHighlight_hoveredPos       = (None, None, None, None)
            self.posHighlight_updatedPositions = None
            self.posHighlight_selectedPos      = None
            self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_HOVERED'].visible  = False
            self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_SELECTED'].visible = False
            self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT1'].setText("")
            self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2'].setText("")
            self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT3'].setText("")
            for siViewerName in self.displayBox_graphics_visibleSIViewers:
                self.displayBox_graphics[siViewerName]['POSHIGHLIGHT_HOVERED'].visible  = False 
                self.displayBox_graphics[siViewerName]['POSHIGHLIGHT_SELECTED'].visible = False
                self.displayBox_graphics[siViewerName]['DESCRIPTIONTEXT1'].setText("")
            #Reset Klines
            for dataType in self.klines:      self.klines[dataType].clear()
            self.bidsAndAsks = {'depth': dict(), 'WOI': dict(), 'WOI_GD': dict()}
            self.aggTrades['volumes'] = {'samples': list(), 'buy': 0, 'sell': 0}
            for dataType in self.aggTrades: 
                if (dataType != 'volumes'): self.aggTrades[dataType].clear()
            self.klines_fetchComplete = False
            self.klines_fetching      = True
            self.klines_drawn.clear()
            self.klines_drawRemovalQueue.clear()
            self.klines_drawQueue.clear()
            self.klines_fetchRequestRID = None
            self.bidsAndAsks_drawFlag             = False
            self.bidsAndAsks_WOI_oldestComputedS  = None
            self.bidsAndAsks_WOI_latestComputedS  = None
            self.bidsAndAsks_WOI_drawQueue        = dict()
            self.bidsAndAsks_WOI_drawn            = dict()
            self.bidsAndAsks_WOI_drawRemovalQueue = set()
            self.aggTrades_NES_oldestComputedS    = None
            self.aggTrades_NES_latestComputedS    = None
            self.aggTrades_NES_drawQueue          = dict()
            self.aggTrades_NES_drawn              = dict()
            self.aggTrades_NES_drawRemovalQueue   = set()
            #Reset Neural Networks
            self.neuralNetworkConnectionDataRequestID = None
            self.neuralNetworkInstance                = None
            torch.cuda.empty_cache()
            #Horizontal ViewRange Params Setup
            self.__setHVRParams()
            #Get Currency Precisions & Update RCLCG Precisions
            self.__initializeRCLCGs('KLINESPRICE')
            for siViewerCode in self.displayBox_graphics_visibleSIViewers: self.__initializeSIViewer(siViewerCode)
            #Send a trade log fetch request
            if (self.klines_targetFetchRange_original != None): self.simulationTradeLog_RID = self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'fetchSimulationTradeLogs', functionParams = {'simulationCode': self.simulationCode}, farrHandler = self.__TLViewer_onTradeLogFetchResponse_FARR)
    def __TLViewer_onTradeLogFetchResponse_FARR(self, responder, requestID, functionResult):
        if (responder == 'DATAMANAGER'):
            _result         = functionResult['result']
            _simulationCode = functionResult['simulationCode']
            _tradeLogs      = functionResult['tradeLogs']
            _failureType    = functionResult['failureType']
            if ((_simulationCode == self.simulationCode) and (requestID == self.simulationTradeLog_RID)):
                if (_result == True):
                    #Record the TRADELOG data in a displayable format
                    for _index, _tradeLog in enumerate(_tradeLogs):
                        if (_tradeLog['positionSymbol'] == self.currencySymbol):
                            ts_effective = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = _tradeLog['timestamp'], mrktReg = None, nTicks = 0)
                            if (_tradeLog['totalQuantity'] != 0): _lastTrade = (_tradeLog['price'], _tradeLog['logicSource'], _tradeLog['side'])
                            else:                                 _lastTrade = None
                            self.klines['TRADELOG'][ts_effective] = {'logIndex':            _index,
                                                                     'logicSource':         _tradeLog['logicSource'],
                                                                     'side':                _tradeLog['side'],
                                                                     'quantity':            _tradeLog['quantity'],
                                                                     'price':               _tradeLog['price'],
                                                                     'profit':              _tradeLog['profit'],
                                                                     'tradingFee':          _tradeLog['tradingFee'],
                                                                     'totalQuantity':       _tradeLog['totalQuantity'],
                                                                     'entryPrice':          _tradeLog['entryPrice'],
                                                                     'lastTrade':           _lastTrade,
                                                                     'tradeControlTracker': _tradeLog['tradeControlTracker']}
                    for targetTS in atmEta_Auxillaries.getTimestampList_byRange(intervalID = self.intervalID, timestamp_beg = self.klines_targetFetchRange_original[0], timestamp_end = self.klines_targetFetchRange_original[1], mrktReg = self.mrktRegTS, lastTickInclusive = True): 
                        if (targetTS not in self.klines['TRADELOG']):
                            targetTS_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = targetTS, mrktReg = self.mrktRegTS, nTicks = -1)
                            if (targetTS_prev in self.klines['TRADELOG']): 
                                prevTradeLog_Formatted = self.klines['TRADELOG'][targetTS_prev]
                                self.klines['TRADELOG'][targetTS] = {'logIndex':            prevTradeLog_Formatted['logIndex'],
                                                                     'logicSource':         None,
                                                                     'side':                None,
                                                                     'quantity':            None,
                                                                     'price':               None,
                                                                     'profit':              None,
                                                                     'tradingFee':          None,
                                                                     'totalQuantity':       prevTradeLog_Formatted['totalQuantity'],
                                                                     'entryPrice':          prevTradeLog_Formatted['entryPrice'],
                                                                     'lastTrade':           prevTradeLog_Formatted['lastTrade'],
                                                                     'tradeControlTracker': None}
                    #Send neural network connections data request
                    _currencyAnalysisConfiguration = self.simulation['currencyAnalysisConfigurations'][self.simulation['positions'][self.currencySymbol]['currencyAnalysisConfigurationCode']]
                    _neuralNetworkCode             = _currencyAnalysisConfiguration['PIP_NeuralNetworkCode']
                    if (_neuralNetworkCode != None): 
                        self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:LOADINGNEURALNETWORKCONNECTIONSDATA'))
                        self.neuralNetworkConnectionDataRequestID = self.ipcA.sendFAR(targetProcess  = "NEURALNETWORKMANAGER",
                                                                                      functionID     = 'getNeuralNetworkConnections',
                                                                                      functionParams = {'neuralNetworkCode': _neuralNetworkCode},
                                                                                      farrHandler    = self.__TLViewer_onNeuralNetworkConnectionsDataRequestResponse_FARR)
                    else: self.__TLViewer_startFetchingKlines()
                else: 
                    print(termcolor.colored("[GUI-{:s}] A failure returned from DATAMANAGER while attempting to fetch tradeLog for simulation '{:s}'.\n *".format(str(self.name), _simulationCode), 'light_red'), termcolor.colored(_failureType, 'light_red'))
                    self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:TRADELOGDATAFETCHFAILED'))
                self.simulationTradeLog_RID = None
    def __TLViewer_onNeuralNetworkConnectionsDataRequestResponse_FARR(self, responder, requestID, functionResult):
        if (responder == 'NEURALNETWORKMANAGER'):
            if (requestID == self.neuralNetworkConnectionDataRequestID):
                self.neuralNetworkConnectionDataRequestID = None
                if (functionResult != None):
                    _nKlines            = functionResult['nKlines']
                    _analysisReferences = functionResult['analysisReferences']
                    _hiddenLayers       = functionResult['hiddenLayers']
                    _outputLayer        = functionResult['outputLayer']
                    _connections        = functionResult['connections']
                    self.neuralNetworkInstance = atmEta_NeuralNetworks.neuralNetwork_MLP(nKlines = _nKlines, analysisReferences = _analysisReferences, hiddenLayers = _hiddenLayers, outputLayer = _outputLayer, device = 'cpu')
                    self.neuralNetworkInstance.importConnectionsData(connections = _connections)
                    self.neuralNetworkInstance.setEvaluationMode()
                    self.__TLViewer_startFetchingKlines()
                else:
                    print(termcolor.colored("[GUI-{:s}] A failure returned from NEURALNETWORKMANAGER while attempting to load neural network connections data for simulation '{:s}'.\n *".format(str(self.name), self.simulationCode), 'light_red'))
                    self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:NEURALNETWORKCONNECTIONSDATAREQUESTFAILED'))
    def __TLViewer_startFetchingKlines(self):
        self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:LOADINGKLINES'))
        self.klinesLoadingGaugeBar.updateGaugeValue(0)
        self.klinesLoadingTextBox_perc.updateText("0.000 %")
        #Determine the effective target fetch range
        _targetFetchRange_end_max = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = self.klines_targetFetchRange_current[0], mrktReg = None, nTicks = _KLINES_MAXFETCHLENGTH)-1
        if (_targetFetchRange_end_max < self.klines_targetFetchRange_current[1]): _targetFetchRange_effective = (self.klines_targetFetchRange_current[0], _targetFetchRange_end_max)
        else:                                                                     _targetFetchRange_effective = (self.klines_targetFetchRange_current[0], self.klines_targetFetchRange_current[1])
        #Send fetch request to the datamanager
        self.klines_fetchRequestRID = self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'fetchKlines', functionParams = {'symbol': self.currencySymbol, 'fetchRange': _targetFetchRange_effective}, farrHandler = self.__TLViewer_onKlineFetchResponse_FARR)
    def __TLViewer_onKlineFetchResponse_FARR(self, responder, requestID, functionResult):
        if (responder == 'DATAMANAGER'):
            if (requestID == self.klines_fetchRequestRID):
                requestResult_result = functionResult['result']
                requestResult_klines = functionResult['klines']
                #[1]: Successful Kline Fetch
                if (requestResult_result == 'SKF'):
                    #Save the received klines
                    for kline in requestResult_klines: 
                        t_open = kline[0]
                        self.klines['raw'][t_open]        = kline[:11]+(True,)
                        self.klines['raw_status'][t_open] = {'p_max': kline[3]}
                        t_open_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = t_open, mrktReg = self.mrktRegTS, nTicks = -1)
                        if (t_open_prev in self.klines['raw_status']): 
                            p_max_prev = self.klines['raw_status'][t_open_prev]['p_max']
                            if (kline[3] < p_max_prev): self.klines['raw_status'][t_open]['p_max'] = p_max_prev
                    #Update the target fetch range
                    fetchedKlinesRange = (requestResult_klines[0][0], requestResult_klines[-1][1])
                    if ((self.klines_targetFetchRange_current[0] == fetchedKlinesRange[0]) and (self.klines_targetFetchRange_current[1] == fetchedKlinesRange[1])): self.klines_targetFetchRange_current = None
                    else:                                                                                                                                           self.klines_targetFetchRange_current[0] = fetchedKlinesRange[1]+1
                    #Update the fetch progress graphics
                    if (self.klines_targetFetchRange_current == None):
                        #Update the fetch progress graphics
                        self.klinesLoadingGaugeBar.updateGaugeValue(100)
                        self.klinesLoadingTextBox_perc.updateText(text = "100 %")
                        self.klines_fetchComplete = True
                        self.klines_fetching      = False
                        self.__TLViewer_onKlineFetchComplete()
                    #If fetching has not completed
                    else:
                        #Update the fetch progress graphics
                        tsLen_original = self.klines_targetFetchRange_original[1]-self.klines_targetFetchRange_original[0]+1
                        tsLen_current  = self.klines_targetFetchRange_current[1] -self.klines_targetFetchRange_current[0] +1
                        fetchCompletion_perc = round((tsLen_original-tsLen_current)/tsLen_original*100, 3)
                        self.klinesLoadingGaugeBar.updateGaugeValue(fetchCompletion_perc)
                        self.klinesLoadingTextBox_perc.updateText(text = "{:.3f} %".format(fetchCompletion_perc))
                        #Send another fetch request
                        _targetFetchRange_end_max = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = self.klines_targetFetchRange_current[0], mrktReg = None, nTicks = _KLINES_MAXFETCHLENGTH)-1
                        if (_targetFetchRange_end_max < self.klines_targetFetchRange_current[1]): _targetFetchRange_effective = (self.klines_targetFetchRange_current[0], _targetFetchRange_end_max)
                        else:                                                                     _targetFetchRange_effective = (self.klines_targetFetchRange_current[0], self.klines_targetFetchRange_current[1])
                        self.klines_fetchRequestRID = self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'fetchKlines', functionParams = {'symbol': self.currencySymbol, 'fetchRange': _targetFetchRange_effective}, farrHandler = self.__TLViewer_onKlineFetchResponse_FARR)
                #[2]: Unexpected Error Occurrance
                elif (requestResult_result == 'UEO'): pass
    def __TLViewer_onKlineFetchComplete(self):
        self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:REGENERATINGANALYSISDATA'))
        self.klinesLoadingGaugeBar.updateGaugeValue(0)
        self.klinesLoadingTextBox_perc.updateText(text = "0.000 %")
        for analysisTargetTS in atmEta_Auxillaries.getTimestampList_byRange(intervalID = self.intervalID, timestamp_beg = self.klines_targetFetchRange_original[0], timestamp_end = self.klines_targetFetchRange_original[1], mrktReg = self.mrktRegTS, lastTickInclusive = True):
            self.analysisQueue_list.append(analysisTargetTS)
            self.analysisQueue_set.add(analysisTargetTS)
        self.caRegeneration_nAnalysis_initial = len(self.analysisQueue_set)
        self.analysisToProcess_Sorted = list()
        for siType in _SITYPES: self.siTypes_analysisCodes[siType] = list()
        for analysisCode in self.analysisParams: self.klines[analysisCode] = dict()
        for analysisType in _ANALYSIS_GENERATIONORDER: self.analysisToProcess_Sorted += [(analysisType, analysisCode) for analysisCode in self.analysisParams if analysisCode[:len(analysisType)] == analysisType]
        for siType in _SITYPES: self.siTypes_analysisCodes[siType] = [analysisCode for analysisCode in self.analysisParams if analysisCode[:len(siType)] == siType]
        self.klines_targetFetchRange_current = None
        self.klines_fetchComplete = True
        self.klines_fetching      = False
        #Reset ViewRange
        self.horizontalViewRange_magnification = 80
        self.horizontalViewRange = [self.klines_targetFetchRange_original[0], None]
        self.horizontalViewRange[1] = round(self.horizontalViewRange[0]+(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
        self.__onHViewRangeUpdate(1)
        self.__editVVR_toExtremaCenter('KLINESPRICE')
        for siViewerCode in self.displayBox_graphics_visibleSIViewers: self.__editVVR_toExtremaCenter(siViewerCode)
    def __TLViewer_onCurrencyAnalysisRegenerationComplete(self):
        self.frameSprites['KLINELOADINGCOVER'].visible = False
        self.klinesLoadingGaugeBar.hide()
        self.klinesLoadingTextBox.hide()
        self.klinesLoadingTextBox_perc.hide()

    #<Analyzer>
    def __setTarget_Analyzer(self, currencySymbol):
        if (self.currencySymbol != None): 
            self.ipcA.removeFARHandler(functionID = 'onKlineStreamReceival_{:s}'.format(self.name))
            self.ipcA.removeFARHandler(functionID = 'onOrderbookUpdate_{:s}'.format(self.name))
            self.ipcA.removeFARHandler(functionID = 'onAggTradeStreamReceival_{:s}'.format(self.name))
            self.ipcA.sendFAR(targetProcess = 'BINANCEAPI', functionID = 'unregisterKlineStreamSubscription', functionParams = {'subscriptionID': self.name, 'currencySymbol': self.currencySymbol}, farrHandler = None)
        self.currencySymbol = currencySymbol
        if (self.currencySymbol == None):
            self.currencyInfo = None
            #Setup Klines Loading Gauge Objects
            self.frameSprites['KLINELOADINGCOVER'].visible = False
            self.klinesLoadingGaugeBar.hide()
            self.klinesLoadingTextBox.hide()
            self.klinesLoadingTextBox_perc.hide()
            self.klinesLoadingGaugeBar.updateGaugeValue(0)
            self.klinesLoadingTextBox_perc.updateText("-")
            #Reset Klines
            for dataType in self.klines:      self.klines[dataType].clear()
            for dataType in self.bidsAndAsks: self.bidsAndAsks[dataType].clear()
            self.aggTrades['volumes'] = {'samples': list(), 'buy': 0, 'sell': 0}
            for dataType in self.aggTrades: 
                if (dataType != 'volumes'): self.aggTrades[dataType].clear()
            self.klines_drawQueue.clear()
            self.klines_drawn.clear()
            self.klines_drawRemovalQueue.clear()
            self.klines_fetchComplete = False
            self.klines_fetching      = False
            self.klines_prepStatus                = None
            self.klines_lastStreamedKlineOpenTS   = None
            self.klines_firstStreamedKlineOpenTS  = [None, None]
            self.klines_lastPreparedKlineOpenTS   = None
            self.klines_targetFetchRange_original = None
            self.klines_targetFetchRange_current  = None
            self.klines_fetchRequestRID           = None
            self.bidsAndAsks_drawFlag             = False
            self.bidsAndAsks_WOI_oldestComputedS  = None
            self.bidsAndAsks_WOI_latestComputedS  = None
            self.bidsAndAsks_WOI_drawQueue        = dict()
            self.bidsAndAsks_WOI_drawn            = dict()
            self.bidsAndAsks_WOI_drawRemovalQueue = set()
            self.aggTrades_NES_oldestComputedS    = None
            self.aggTrades_NES_latestComputedS    = None
            self.aggTrades_NES_drawQueue          = dict()
            self.aggTrades_NES_drawn              = dict()
            self.aggTrades_NES_drawRemovalQueue   = set()
            self.analysisQueue_list.clear()
            self.analysisQueue_set.clear()
            self.analyzingStream = False
            #Reset Neural Networks
            self.neuralNetworkConnectionDataRequestID = None
            self.neuralNetworkInstance                = None
            torch.cuda.empty_cache()
            #Horizontal ViewRange Params Setup
            self.__setHVRParams()
            #Call this now since no klines will be fetched
            self.__Analyzer_onKlineFetchComplete()
        else:
            self.currencyInfo = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', self.currencySymbol))
            #Setup Klines Loading Gauge Objects
            self.frameSprites['KLINELOADINGCOVER'].visible = True
            self.klinesLoadingGaugeBar.show()
            self.klinesLoadingTextBox.show()
            self.klinesLoadingTextBox_perc.show()
            self.klinesLoadingGaugeBar.updateGaugeValue(0)
            self.klinesLoadingTextBox_perc.updateText("-")
            self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGFIRSTSTREAM'))
            #Reset Klines
            for dataType in self.klines:      self.klines[dataType].clear()
            for dataType in self.bidsAndAsks: self.bidsAndAsks[dataType].clear()
            self.aggTrades['volumes'] = {'samples': list(), 'buy': 0, 'sell': 0}
            for dataType in self.aggTrades: 
                if (dataType != 'volumes'): self.aggTrades[dataType].clear()
            self.klines_drawQueue.clear()
            self.klines_drawn.clear()
            self.klines_drawRemovalQueue.clear()
            self.klines_fetchComplete = False
            self.klines_fetching      = True
            self.klines_prepStatus                = _KLINES_PREPSTATUS_WAITINGFIRSTSTREAM
            self.klines_lastStreamedKlineOpenTS   = None
            self.klines_firstStreamedKlineOpenTS  = [None, None]
            self.klines_lastPreparedKlineOpenTS   = None
            self.klines_targetFetchRange_original = None
            self.klines_targetFetchRange_current  = None
            self.klines_fetchRequestRID           = None
            self.bidsAndAsks_drawFlag             = False
            self.bidsAndAsks_WOI_oldestComputedS  = None
            self.bidsAndAsks_WOI_latestComputedS  = None
            self.bidsAndAsks_WOI_drawQueue        = dict()
            self.bidsAndAsks_WOI_drawn            = dict()
            self.bidsAndAsks_WOI_drawRemovalQueue = set()
            self.aggTrades_NES_oldestComputedS    = None
            self.aggTrades_NES_latestComputedS    = None
            self.aggTrades_NES_drawQueue          = dict()
            self.aggTrades_NES_drawn              = dict()
            self.aggTrades_NES_drawRemovalQueue   = set()
            self.analysisQueue_list.clear()
            self.analysisQueue_set.clear()
            self.analyzingStream = False
            #Reset Neural Networks
            self.neuralNetworkConnectionDataRequestID = None
            self.neuralNetworkInstance                = None
            torch.cuda.empty_cache()
            #Update Highlighters and Descriptors
            self.posHighlight_hoveredPos       = (None, None, None, None)
            self.posHighlight_updatedPositions = None
            self.posHighlight_selectedPos      = None
            self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_HOVERED'].visible  = False
            self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_SELECTED'].visible = False
            self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT1'].setText("")
            self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2'].setText("")
            for siViewerName in self.displayBox_graphics_visibleSIViewers:
                self.displayBox_graphics[siViewerName]['POSHIGHLIGHT_HOVERED'].visible  = False 
                self.displayBox_graphics[siViewerName]['POSHIGHLIGHT_SELECTED'].visible = False
                self.displayBox_graphics[siViewerName]['DESCRIPTIONTEXT1'].setText("")
            #Horizontal ViewRange Params Setup
            self.__setHVRParams()
            #Get Currency Precisions & Update RCLCG Precisions
            self.__initializeRCLCGs('KLINESPRICE')
            for siViewerCode in self.displayBox_graphics_visibleSIViewers: self.__initializeSIViewer(siViewerCode)
            #Send a kline subscription request
            self.ipcA.addFARHandler('onKlineStreamReceival_{:s}'.format(self.name),    self.__Analyzer_onKlineStreamReceival,    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
            self.ipcA.addFARHandler('onOrderbookUpdate_{:s}'.format(self.name),        self.__Analyzer_onOrderBookUpdate,        executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
            self.ipcA.addFARHandler('onAggTradeStreamReceival_{:s}'.format(self.name), self.__Analyzer_onAggTradeStreamReceival, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
            self.ipcA.sendFAR(targetProcess = 'BINANCEAPI', 
                              functionID = 'registerKlineStreamSubscription', 
                              functionParams = {'subscriptionID':       self.name, 
                                                'currencySymbol':       self.currencySymbol, 
                                                'subscribeBidsAndAsks': True,
                                                'subscribeAggTrades':   True},
                              farrHandler = None)
    def __Analyzer_onKlineStreamReceival(self, requester, symbol, streamConnectionTime, kline, closed):
        if (requester == 'BINANCEAPI'):
            if (symbol == self.currencySymbol):
                kline = kline[:11]
                #[1]: Save the kline
                t_open = kline[0]
                self.klines['raw'][t_open] = kline+(closed,)
                self.klines['raw_status'][t_open] = {'p_max': kline[3]}
                t_open_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = t_open, mrktReg = self.mrktRegTS, nTicks = -1)
                if (t_open_prev in self.klines['raw_status']): 
                    p_max_prev = self.klines['raw_status'][t_open_prev]['p_max']
                    if (kline[3] < p_max_prev): self.klines['raw_status'][t_open]['p_max'] = p_max_prev
                self.klines_lastStreamedKlineOpenTS = t_open
                #[2-1]: The same stream conneciton
                if (streamConnectionTime == self.klines_firstStreamedKlineOpenTS[1]):
                    if (self.klines_fetchComplete == True):
                        self.klines_lastPreparedKlineOpenTS = t_open
                        #Determine if this kline is within the horizontalViewRange, if it is, add the processing queue
                        t_close = kline[1]
                        classification = 0
                        classification += 0b1000*(0 <= t_open -self.horizontalViewRange[0])
                        classification += 0b0100*(0 <= t_open -self.horizontalViewRange[1])
                        classification += 0b0010*(0 <  t_close-self.horizontalViewRange[0])
                        classification += 0b0001*(0 <  t_close-self.horizontalViewRange[1])
                        if ((classification == 0b0010) or (classification == 0b1010) or (classification == 0b1011) or (classification == 0b0011)):
                            if (t_open in self.klines_drawQueue): self.klines_drawQueue[t_open]['KLINE'] = None
                            else:                                 self.klines_drawQueue[t_open] = {'KLINE': None}
                        #Analysis Continuation
                        if ((self.chartDrawerType == 'ANALYZER') and (self.analyzingStream == True)):
                            if (t_open not in self.analysisQueue_set): 
                                self.analysisQueue_set.add(t_open)
                                self.analysisQueue_list.append(t_open)
                    elif (self.klines_prepStatus == _KLINES_PREPSTATUS_WAITINGDATAAVAILABLE): self.__Analyzer_checkKlineDataAvailable()
                #[2-2]: Stream connection renewed
                else:
                    #[1]: Stream Control Variables
                    self.klines_fetchComplete = False
                    self.klines_fetching      = True
                    self.klines_prepStatus    = None
                    self.klines_firstStreamedKlineOpenTS = (kline[0], streamConnectionTime)
                    self.klines_fetchRequestRID          = None
                    #[2]: Loading Graphics Update
                    self.frameSprites['KLINELOADINGCOVER'].visible = True
                    self.klinesLoadingGaugeBar.show()
                    self.klinesLoadingTextBox.show()
                    self.klinesLoadingTextBox_perc.show()
                    self.klinesLoadingGaugeBar.updateGaugeValue(0)
                    self.klinesLoadingTextBox_perc.updateText("-")
                    self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGDATAAVAILABLE'))
                    #[3]: Determine the target fetch range and check data availability, and update the prep status
                    if (self.klines_lastPreparedKlineOpenTS == None): targetFetchRange_beg = self.currencyInfo['kline_firstOpenTS']
                    else:                                             targetFetchRange_beg = self.klines_lastPreparedKlineOpenTS
                    targetFetchRange_end = kline[0]-1
                    if (targetFetchRange_beg < targetFetchRange_end):
                        self.klines_prepStatus = _KLINES_PREPSTATUS_WAITINGDATAAVAILABLE
                        self.klines_targetFetchRange_original = (targetFetchRange_beg, targetFetchRange_end)
                        self.klines_targetFetchRange_current  = [targetFetchRange_beg, targetFetchRange_end]
                        self.__Analyzer_checkKlineDataAvailable()
                    else: 
                        self.klines_fetchComplete = True
                        self.klines_fetching      = False
                        self.__Analyzer_onKlineFetchComplete()
    def __Analyzer_onOrderBookUpdate(self, requester, symbol, streamConnectionTime, bids, asks):
        if (requester == 'BINANCEAPI'):
            if (symbol == self.currencySymbol):
                #Data Read & Analysis Generation
                _newOldestComputed, _newLatestComputed, _updatedItems = atmEta_Analyzers.updateBidsAndAsks(bidsAndAsks    = self.bidsAndAsks,
                                                                                                           newBidsAndAsks = (bids, asks),
                                                                                                           oldestComputed = self.bidsAndAsks_WOI_oldestComputedS,
                                                                                                           latestComputed = self.bidsAndAsks_WOI_latestComputedS,
                                                                                                           analysisLines  = [(_aCode, self.objectConfig['{:s}_NSamples'.format(_aCode)], self.objectConfig['{:s}_Sigma'.format(_aCode)]) for _aCode in self.siTypes_analysisCodes['WOI']])
                #Variables Update
                self.bidsAndAsks_WOI_oldestComputedS = _newOldestComputed
                self.bidsAndAsks_WOI_latestComputedS = _newLatestComputed
                self.bidsAndAsks_drawFlag = True
                for _updateType, _woiType, _tt in _updatedItems:
                    #Added
                    if (_updateType == 1):
                        if (_tt in self.bidsAndAsks_WOI_drawQueue): self.bidsAndAsks_WOI_drawQueue[_tt].add(_woiType)
                        else:                                       self.bidsAndAsks_WOI_drawQueue[_tt] = {_woiType}
                    #Removed
                    elif (_updateType == -1): self.bidsAndAsks_WOI_drawRemovalQueue.add(_tt)
    def __Analyzer_onAggTradeStreamReceival(self, requester, symbol, streamConnectionTime, aggTrade):
        if (requester == 'BINANCEAPI'):
            if (symbol == self.currencySymbol):
                #Data Read & Analysis Generation
                _newOldestComputed, _newLatestComputed, _updatedItems = atmEta_Analyzers.updateAggTrades(aggTrades      = self.aggTrades,
                                                                                                         newAggTrade    = aggTrade,
                                                                                                         oldestComputed = self.aggTrades_NES_oldestComputedS,
                                                                                                         latestComputed = self.aggTrades_NES_latestComputedS,
                                                                                                         analysisLines  = [(_aCode, self.objectConfig['{:s}_NSamples'.format(_aCode)], self.objectConfig['{:s}_Sigma'.format(_aCode)]) for _aCode in self.siTypes_analysisCodes['NES']])
                #Variables Update
                self.aggTrades_NES_oldestComputedS = _newOldestComputed
                self.aggTrades_NES_latestComputedS = _newLatestComputed
                for _updateType, _nesType, _tt in _updatedItems:
                    #Added
                    if (_updateType == 1):
                        if (_tt in self.aggTrades_NES_drawQueue): self.aggTrades_NES_drawQueue[_tt].add(_nesType)
                        else:                                     self.aggTrades_NES_drawQueue[_tt] = {_nesType}
                    #Removed
                    elif (_updateType == -1): self.aggTrades_NES_drawRemovalQueue.add(_tt)
    def __Analyzer_checkKlineDataAvailable(self):
        klineAvailableRanges = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', self.currencySymbol, 'kline_availableRanges'))
        if (klineAvailableRanges != None):
            for dataRange in klineAvailableRanges:
                if (dataRange[0] <= self.klines_targetFetchRange_original[0]) and (self.klines_targetFetchRange_original[1] <= dataRange[1]):
                    #If data is available
                    #[1]: Update the prep status and graphics
                    self.klines_prepStatus = _KLINES_PREPSTATUS_FETCHING
                    self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:LOADINGKLINES'))
                    self.klinesLoadingTextBox_perc.updateText("0.000 %")
                    #[2]: Determine the effective target fetch range
                    _targetFetchRange_end_max = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = self.klines_targetFetchRange_original[0], mrktReg = None, nTicks = _KLINES_MAXFETCHLENGTH)-1
                    if (_targetFetchRange_end_max < self.klines_targetFetchRange_original[1]): _targetFetchRange_effective = (self.klines_targetFetchRange_original[0], _targetFetchRange_end_max)
                    else:                                                                      _targetFetchRange_effective = (self.klines_targetFetchRange_original[0], self.klines_targetFetchRange_original[1])
                    #[3]: Send fetch request to the datamanager
                    self.klines_fetchRequestRID = self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'fetchKlines', functionParams = {'symbol': self.currencySymbol, 'fetchRange': _targetFetchRange_effective}, farrHandler = self.__Analyzer_onKlineFetchResponse_FARR)
                    break
    def __Analyzer_onKlineFetchResponse_FARR(self, responder, requestID, functionResult):
        if (responder == 'DATAMANAGER'):
            if (requestID == self.klines_fetchRequestRID):
                requestResult_result = functionResult['result']
                requestResult_klines = functionResult['klines']
                #[1]: Successful Kline Fetch
                if (requestResult_result == 'SKF'):
                    #Save the received klines
                    for kline in requestResult_klines: 
                        t_open = kline[0]
                        self.klines['raw'][t_open]        = kline[:11]+(True,)
                        self.klines['raw_status'][t_open] = {'p_max': kline[3]}
                        t_open_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = t_open, mrktReg = self.mrktRegTS, nTicks = -1)
                        if (t_open_prev in self.klines['raw_status']): 
                            p_max_prev = self.klines['raw_status'][t_open_prev]['p_max']
                            if (kline[3] < p_max_prev): self.klines['raw_status'][t_open]['p_max'] = p_max_prev
                    #Update the target fetch range
                    fetchedKlinesRange = (requestResult_klines[0][0], requestResult_klines[-1][1])
                    if ((self.klines_targetFetchRange_current[0] == fetchedKlinesRange[0]) and (self.klines_targetFetchRange_current[1] == fetchedKlinesRange[1])): self.klines_targetFetchRange_current = None
                    else:                                                                                                                                           self.klines_targetFetchRange_current[0] = fetchedKlinesRange[1]+1
                    #Update the fetch progress graphics
                    if (self.klines_targetFetchRange_current == None):
                        #Update the fetch progress graphics
                        self.klinesLoadingGaugeBar.updateGaugeValue(100)
                        self.klinesLoadingTextBox_perc.updateText(text = "100 %")
                        self.klines_fetchComplete = True
                        self.klines_fetching      = False
                        self.__Analyzer_onKlineFetchComplete()
                    #If fetching has not completed
                    else:
                        #Update the fetch progress graphics
                        tsLen_original = self.klines_targetFetchRange_original[1]-self.klines_targetFetchRange_original[0]+1
                        tsLen_current  = self.klines_targetFetchRange_current[1] -self.klines_targetFetchRange_current[0] +1
                        fetchCompletion_perc = round((tsLen_original-tsLen_current)/tsLen_original*100, 3)
                        self.klinesLoadingGaugeBar.updateGaugeValue(fetchCompletion_perc)
                        self.klinesLoadingTextBox_perc.updateText(text = "{:.3f} %".format(fetchCompletion_perc))
                        #Send another fetch request
                        _targetFetchRange_end_max = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = self.klines_targetFetchRange_current[0], mrktReg = None, nTicks = _KLINES_MAXFETCHLENGTH)-1
                        if (_targetFetchRange_end_max < self.klines_targetFetchRange_current[1]): _targetFetchRange_effective = (self.klines_targetFetchRange_current[0], _targetFetchRange_end_max)
                        else:                                                                     _targetFetchRange_effective = (self.klines_targetFetchRange_current[0], self.klines_targetFetchRange_current[1])
                        self.klines_fetchRequestRID = self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'fetchKlines', functionParams = {'symbol': self.currencySymbol, 'fetchRange': _targetFetchRange_effective}, farrHandler = self.__Analyzer_onKlineFetchResponse_FARR)
                #[2]: Unexpected Error Occurrance
                elif (requestResult_result == 'UEO'): pass
    def __Analyzer_onKlineFetchComplete(self):
        #If this is the first ever kline fetch completion, reset the view
        _resetView = (self.klines_lastPreparedKlineOpenTS == None)
        #Update fetch control variables
        self.klines_prepStatus                = None
        self.klines_targetFetchRange_original = None
        self.klines_targetFetchRange_current  = None
        self.klines_fetchRequestRID           = None
        #Klines Preparation
        if (self.klines_fetchComplete == True):
            _prepRange_end = self.klines_lastStreamedKlineOpenTS
            if (self.klines_lastPreparedKlineOpenTS == None): _prepRange_beg = self.currencyInfo['kline_firstOpenTS']
            else:                                             _prepRange_beg = self.klines_lastPreparedKlineOpenTS
            #[1]: Update draw & analysis queue 
            for t_open in atmEta_Auxillaries.getTimestampList_byRange(intervalID = self.intervalID, timestamp_beg = _prepRange_beg, timestamp_end = _prepRange_end, mrktReg = self.mrktRegTS, lastTickInclusive = True):
                t_close = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = t_open, mrktReg = None, nTicks = 1)-1
                classification = 0
                classification += 0b1000*(0 <= t_open -self.horizontalViewRange[0])
                classification += 0b0100*(0 <= t_open -self.horizontalViewRange[1])
                classification += 0b0010*(0 <  t_close-self.horizontalViewRange[0])
                classification += 0b0001*(0 <  t_close-self.horizontalViewRange[1])
                if ((classification == 0b0010) or (classification == 0b1010) or (classification == 0b1011) or (classification == 0b0011)):
                    if (t_open in self.klines_drawQueue): self.klines_drawQueue[t_open]['KLINE'] = None
                    else:                                 self.klines_drawQueue[t_open] = {'KLINE': None}
            self.klines_lastPreparedKlineOpenTS = _prepRange_end
            #[2]: If needed, update the analysis queue
            if ((self.chartDrawerType == 'ANALYZER') and (self.analyzingStream == True)):
                for t_open in atmEta_Auxillaries.getTimestampList_byRange(intervalID = self.intervalID, timestamp_beg = _prepRange_beg, timestamp_end = _prepRange_end, mrktReg = self.mrktRegTS, lastTickInclusive = True):
                    if (t_open not in self.analysisQueue_set):
                        self.analysisQueue_list.append(t_open)
                        self.analysisQueue_set.add(t_open)
                self.analysisQueue_list.sort()
        #Loading Indicator Graphics Control
        self.frameSprites['KLINELOADINGCOVER'].visible = False
        self.klinesLoadingGaugeBar.hide()
        self.klinesLoadingTextBox_perc.hide()
        self.klinesLoadingTextBox.hide()
        #Horizontal ViewRange Reset
        if (_resetView == True):
            self.horizontalViewRange_magnification = 80
            self.horizontalViewRange = [None, round(time.time()+self.expectedKlineTemporalWidth*2)]
            self.horizontalViewRange[0] = round(self.horizontalViewRange[1]-(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
            self.__onHViewRangeUpdate(1)
            #Vertical ViewRange Reset
            self.__editVVR_toExtremaCenter('KLINESPRICE')
            for siViewerCode in self.displayBox_graphics_visibleSIViewers: self.__editVVR_toExtremaCenter(siViewerCode)
        #Analysis Availability Check
        self.__Analyzer_checkIfCanPerformAnalysis()
    def __Analyzer_checkIfCanPerformAnalysis(self):
        rangeBeg = self.objectConfig['AnalysisRangeBeg']
        rangeEnd = self.objectConfig['AnalysisRangeEnd']
        if (self.currencySymbol == None): _result = False
        else:
            if (rangeBeg == None): _result = False
            else:
                if ((self.currencyInfo['kline_firstOpenTS'] <= rangeBeg) and (rangeBeg <= self.klines_lastStreamedKlineOpenTS)): 
                    if (rangeEnd == None): _result = True
                    else:
                        if ((rangeBeg < rangeEnd) and (rangeEnd <= self.klines_lastStreamedKlineOpenTS)): _result = True
                        else:                                                                             _result = False
                else: _result = False
        if (_result == True): self.canStartAnalysis = True;  self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
        else:                 self.canStartAnalysis = False; self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].deactivate()
    def __Analyzer_requestNeuralNetworkConnectionsData(self):
        self.neuralNetworkConnectionDataRequestID = self.ipcA.sendFAR(targetProcess  = "NEURALNETWORKMANAGER",
                                                                      functionID     = 'getNeuralNetworkConnections',
                                                                      functionParams = {'neuralNetworkCode': self.objectConfig['PIP_NeuralNetworkCode']},
                                                                      farrHandler    = self.__Analyzer_onNeuralNetworkConnectionsDataRequestResponse_FARR)
    def __Analyzer_onNeuralNetworkConnectionsDataRequestResponse_FARR(self, responder, requestID, functionResult):
        if (responder == 'NEURALNETWORKMANAGER'):
            if (requestID == self.neuralNetworkConnectionDataRequestID):
                self.neuralNetworkConnectionDataRequestID = None
                if (functionResult != None):
                    _nKlines            = functionResult['nKlines']
                    _analysisReferences = functionResult['analysisReferences']
                    _hiddenLayers       = functionResult['hiddenLayers']
                    _outputLayer        = functionResult['outputLayer']
                    _connections        = functionResult['connections']
                    self.neuralNetworkInstance = atmEta_NeuralNetworks.neuralNetwork_MLP(nKlines = _nKlines, analysisReferences = _analysisReferences, hiddenLayers = _hiddenLayers, outputLayer = _outputLayer, device = 'cpu')
                    self.neuralNetworkInstance.importConnectionsData(connections = _connections)
                    self.neuralNetworkInstance.setEvaluationMode()
                    self.__Analyzer_startAnalysis()
                else: self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
    def __Analyzer_startAnalysis(self):
        #[1]: Reset previous analysis Data, drawings and analysis process queue
        klineDataTypesToRemove = [dataType for dataType in self.klines.keys() if ((dataType != 'raw') and (dataType != 'raw_status'))]
        for analysisCode in klineDataTypesToRemove:
            self.__klineDrawer_RemoveDrawings(analysisCode = analysisCode, gRemovalSignal = None)
            del self.klines[analysisCode]
        self.analysisQueue_list.clear()
        self.analysisQueue_set.clear()
        self.klines_drawQueue.clear()
        #[2]: Construct a new analysis params
        self.analysisParams           = dict()
        self.analysisToProcess_Sorted = list()
        for siType in _SITYPES: 
            if not((siType == 'WOI') or (siType == 'NES')): self.siTypes_analysisCodes[siType] = list()
        _analysisParams = atmEta_Analyzers.constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration(self.objectConfig)
        if (_analysisParams != None):
            self.analysisParams = _analysisParams
            for analysisCode in self.analysisParams: self.klines[analysisCode] = dict()
            for analysisType in _ANALYSIS_GENERATIONORDER: self.analysisToProcess_Sorted += [(analysisType, analysisCode) for analysisCode in self.analysisParams if analysisCode[:len(analysisType)] == analysisType]
            for siType in _SITYPES: 
                if not((siType == 'WOI') or (siType == 'NES')): self.siTypes_analysisCodes[siType] = [analysisCode for analysisCode in self.analysisParams if analysisCode[:len(siType)] == siType]
            #Add Analysis Queue
            if (self.objectConfig['AnalysisRangeEnd'] == None):
                for analysisTargetTS in atmEta_Auxillaries.getTimestampList_byRange(intervalID = self.intervalID, timestamp_beg = self.objectConfig['AnalysisRangeBeg'], timestamp_end = self.klines_lastPreparedKlineOpenTS, mrktReg = self.mrktRegTS, lastTickInclusive = True): 
                    self.analysisQueue_list.append(analysisTargetTS)
                    self.analysisQueue_set.add(analysisTargetTS)
                    self.analyzingStream = True
            else:
                for analysisTargetTS in atmEta_Auxillaries.getTimestampList_byRange(intervalID = self.intervalID, timestamp_beg = self.objectConfig['AnalysisRangeBeg'], timestamp_end = self.objectConfig['AnalysisRangeEnd']+1, mrktReg = self.mrktRegTS, lastTickInclusive = True):
                    self.analysisQueue_list.append(analysisTargetTS)
                    self.analysisQueue_set.add(analysisTargetTS)
                    self.analyzingStream = False
            self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].deactivate()
        else: self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()

    # * <Shared>
    def __readCurrencyAnalysisConfiguration(self, currencyAnalysisConfiguration):
        _caConfig = currencyAnalysisConfiguration
        if (True): #SMA
            if (_caConfig['SMA_Master'] == True):
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_SMA"].activate()
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATORSETUP_SMA"].activate()
                for lineIndex in range (_NMAXLINES['SMA']):
                    lineNumber = lineIndex+1
                    if (_caConfig['SMA_{:d}_LineActive'.format(lineNumber)] == True):
                        self.settingsSubPages['SMA'].GUIOs["INDICATOR_SMA{:d}".format(lineNumber)].setStatus(status = True, callStatusUpdateFunction = False)
                        self.settingsSubPages['SMA'].GUIOs["INDICATOR_SMA{:d}_INTERVALINPUT".format(lineNumber)].updateText("{:d}".format(_caConfig['SMA_{:d}_NSamples'.format(lineNumber)]))
                        self.settingsSubPages['SMA'].GUIOs["INDICATOR_SMA{:d}_WIDTHINPUT".format(lineNumber)].activate()
                        self.settingsSubPages['SMA'].GUIOs["INDICATOR_SMA{:d}_WIDTHINPUT".format(lineNumber)].updateText("{:d}".format(self.objectConfig['SMA_{:d}_Width'.format(lineNumber)]))
                        self.settingsSubPages['SMA'].GUIOs["INDICATOR_SMA{:d}_DISPLAY".format(lineNumber)].setStatus(status = self.objectConfig['SMA_{:d}_Display'.format(lineNumber)], callStatusUpdateFunction = False)
                        self.settingsSubPages['SMA'].GUIOs["INDICATOR_SMA{:d}_DISPLAY".format(lineNumber)].activate()
                    else:
                        self.settingsSubPages['SMA'].GUIOs["INDICATOR_SMA{:d}".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
                        self.settingsSubPages['SMA'].GUIOs["INDICATOR_SMA{:d}_INTERVALINPUT".format(lineNumber)].updateText("-")
                        self.settingsSubPages['SMA'].GUIOs["INDICATOR_SMA{:d}_WIDTHINPUT".format(lineNumber)].deactivate()
                        self.settingsSubPages['SMA'].GUIOs["INDICATOR_SMA{:d}_DISPLAY".format(lineNumber)].deactivate()
                        self.settingsSubPages['SMA'].GUIOs["INDICATOR_SMA{:d}_DISPLAY".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
            else:
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_SMA"].setStatus(status = False, callStatusUpdateFunction = False)
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_SMA"].deactivate()
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATORSETUP_SMA"].deactivate()
        if (True): #WMA
            if (_caConfig['WMA_Master'] == True):
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_WMA"].activate()
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATORSETUP_WMA"].activate()
                for lineIndex in range (_NMAXLINES['WMA']):
                    lineNumber = lineIndex+1
                    if (_caConfig['WMA_{:d}_LineActive'.format(lineNumber)] == True):
                        self.settingsSubPages['WMA'].GUIOs["INDICATOR_WMA{:d}".format(lineNumber)].setStatus(status = True, callStatusUpdateFunction = False)
                        self.settingsSubPages['WMA'].GUIOs["INDICATOR_WMA{:d}_INTERVALINPUT".format(lineNumber)].updateText("{:d}".format(_caConfig['WMA_{:d}_NSamples'.format(lineNumber)]))
                        self.settingsSubPages['WMA'].GUIOs["INDICATOR_WMA{:d}_WIDTHINPUT".format(lineNumber)].activate()
                        self.settingsSubPages['WMA'].GUIOs["INDICATOR_WMA{:d}_WIDTHINPUT".format(lineNumber)].updateText("{:d}".format(self.objectConfig['WMA_{:d}_Width'.format(lineNumber)]))
                        self.settingsSubPages['WMA'].GUIOs["INDICATOR_WMA{:d}_DISPLAY".format(lineNumber)].setStatus(status = self.objectConfig['WMA_{:d}_Display'.format(lineNumber)], callStatusUpdateFunction = False)
                        self.settingsSubPages['WMA'].GUIOs["INDICATOR_WMA{:d}_DISPLAY".format(lineNumber)].activate()
                    else:
                        self.settingsSubPages['WMA'].GUIOs["INDICATOR_WMA{:d}".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
                        self.settingsSubPages['WMA'].GUIOs["INDICATOR_WMA{:d}_INTERVALINPUT".format(lineNumber)].updateText("-")
                        self.settingsSubPages['WMA'].GUIOs["INDICATOR_WMA{:d}_WIDTHINPUT".format(lineNumber)].deactivate()
                        self.settingsSubPages['WMA'].GUIOs["INDICATOR_WMA{:d}_DISPLAY".format(lineNumber)].deactivate()
                        self.settingsSubPages['WMA'].GUIOs["INDICATOR_WMA{:d}_DISPLAY".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
            else:
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_WMA"].setStatus(status = False, callStatusUpdateFunction = False)
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_WMA"].deactivate()
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATORSETUP_WMA"].deactivate()
        if (True): #EMA
            if (_caConfig['EMA_Master'] == True):
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_EMA"].activate()
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATORSETUP_EMA"].activate()
                for lineIndex in range (_NMAXLINES['EMA']):
                    lineNumber = lineIndex+1
                    if (_caConfig['EMA_{:d}_LineActive'.format(lineNumber)] == True):
                        self.settingsSubPages['EMA'].GUIOs["INDICATOR_EMA{:d}".format(lineNumber)].setStatus(status = True, callStatusUpdateFunction = False)
                        self.settingsSubPages['EMA'].GUIOs["INDICATOR_EMA{:d}_INTERVALINPUT".format(lineNumber)].updateText("{:d}".format(_caConfig['EMA_{:d}_NSamples'.format(lineNumber)]))
                        self.settingsSubPages['EMA'].GUIOs["INDICATOR_EMA{:d}_WIDTHINPUT".format(lineNumber)].activate()
                        self.settingsSubPages['EMA'].GUIOs["INDICATOR_EMA{:d}_WIDTHINPUT".format(lineNumber)].updateText("{:d}".format(self.objectConfig['EMA_{:d}_Width'.format(lineNumber)]))
                        self.settingsSubPages['EMA'].GUIOs["INDICATOR_EMA{:d}_DISPLAY".format(lineNumber)].setStatus(status = self.objectConfig['EMA_{:d}_Display'.format(lineNumber)], callStatusUpdateFunction = False)
                        self.settingsSubPages['EMA'].GUIOs["INDICATOR_EMA{:d}_DISPLAY".format(lineNumber)].activate()
                    else:
                        self.settingsSubPages['EMA'].GUIOs["INDICATOR_EMA{:d}".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
                        self.settingsSubPages['EMA'].GUIOs["INDICATOR_EMA{:d}_INTERVALINPUT".format(lineNumber)].updateText("-")
                        self.settingsSubPages['EMA'].GUIOs["INDICATOR_EMA{:d}_WIDTHINPUT".format(lineNumber)].deactivate()
                        self.settingsSubPages['EMA'].GUIOs["INDICATOR_EMA{:d}_DISPLAY".format(lineNumber)].deactivate()
                        self.settingsSubPages['EMA'].GUIOs["INDICATOR_EMA{:d}_DISPLAY".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
            else:
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_EMA"].setStatus(status = False, callStatusUpdateFunction = False)
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_EMA"].deactivate()
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATORSETUP_EMA"].deactivate()
        if (True): #PSAR
            if (_caConfig['PSAR_Master'] == True):
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_PSAR"].activate()
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATORSETUP_PSAR"].activate()
                for lineIndex in range (_NMAXLINES['PSAR']):
                    lineNumber = lineIndex+1
                    if (_caConfig['PSAR_{:d}_LineActive'.format(lineNumber)] == True):
                        self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}".format(lineNumber)].setStatus(status = True, callStatusUpdateFunction = False)
                        self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_AF0INPUT".format(lineNumber)].updateText("{:.3f}".format(_caConfig['PSAR_{:d}_AF0'.format(lineNumber)]))
                        self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_AF+INPUT".format(lineNumber)].updateText("{:.3f}".format(_caConfig['PSAR_{:d}_AF+'.format(lineNumber)]))
                        self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_AFMAXINPUT".format(lineNumber)].updateText("{:.3f}".format(_caConfig['PSAR_{:d}_AFMax'.format(lineNumber)]))
                        self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_WIDTHINPUT".format(lineNumber)].activate()
                        self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_WIDTHINPUT".format(lineNumber)].updateText("{:d}".format(self.objectConfig['PSAR_{:d}_Width'.format(lineNumber)]))
                        self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_DISPLAY".format(lineNumber)].setStatus(status = self.objectConfig['PSAR_{:d}_Display'.format(lineNumber)], callStatusUpdateFunction = False)
                        self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_DISPLAY".format(lineNumber)].activate()
                    else:
                        self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
                        self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_AF0INPUT".format(lineNumber)].updateText("-")
                        self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_AF+INPUT".format(lineNumber)].updateText("-")
                        self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_AFMAXINPUT".format(lineNumber)].updateText("-")
                        self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_WIDTHINPUT".format(lineNumber)].deactivate()
                        self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_DISPLAY".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
                        self.settingsSubPages['PSAR'].GUIOs["INDICATOR_PSAR{:d}_DISPLAY".format(lineNumber)].deactivate()
            else:
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_PSAR"].setStatus(status = False, callStatusUpdateFunction = False)
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_PSAR"].deactivate()
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATORSETUP_PSAR"].deactivate()
        if (True): #BOL
            if (_caConfig['BOL_Master'] == True):
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_BOL"].activate()
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATORSETUP_BOL"].activate()
                for lineIndex in range (_NMAXLINES['BOL']):
                    lineNumber = lineIndex+1
                    if (_caConfig['BOL_{:d}_LineActive'.format(lineNumber)] == True):
                        self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}".format(lineNumber)].setStatus(status = True, callStatusUpdateFunction = False)
                        self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_INTERVALINPUT".format(lineNumber)].updateText("{:d}".format(_caConfig['BOL_{:d}_NSamples'.format(lineNumber)]))
                        self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_BANDWIDTHINPUT".format(lineNumber)].updateText("{:.1f}".format(_caConfig['BOL_{:d}_BandWidth'.format(lineNumber)]))
                        self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_WIDTHINPUT".format(lineNumber)].activate()
                        self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_WIDTHINPUT".format(lineNumber)].updateText("{:d}".format(self.objectConfig['BOL_{:d}_Width'.format(lineNumber)]))
                        self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_DISPLAY".format(lineNumber)].setStatus(status = self.objectConfig['BOL_{:d}_Display'.format(lineNumber)], callStatusUpdateFunction = False)
                        self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_DISPLAY".format(lineNumber)].activate()
                    else:
                        self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
                        self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_INTERVALINPUT".format(lineNumber)].updateText("-")
                        self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_BANDWIDTHINPUT".format(lineNumber)].updateText("-")
                        self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_WIDTHINPUT".format(lineNumber)].deactivate()
                        self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_DISPLAY".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
                        self.settingsSubPages['BOL'].GUIOs["INDICATOR_BOL{:d}_DISPLAY".format(lineNumber)].deactivate()
                self.settingsSubPages['BOL'].GUIOs["INDICATOR_MATYPESELECTION"].setSelected(itemKey = _caConfig['BOL_MAType'], callSelectionUpdateFunction = False)
            else:
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_BOL"].setStatus(status = False, callStatusUpdateFunction = False)
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_BOL"].deactivate()
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATORSETUP_BOL"].deactivate()
        if (True): #IVP
            if (_caConfig['IVP_Master'] == True):
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_IVP"].activate()
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATORSETUP_IVP"].activate()
                self.settingsSubPages['IVP'].GUIOs["INDICATOR_INTERVAL_INPUTTEXT"].updateText(text = "{:d}".format(_caConfig['IVP_NSamples']))
                self.settingsSubPages['IVP'].GUIOs["INDICATOR_GAMMAFACTOR_SLIDER"].setSliderValue(newValue = (_caConfig['IVP_GammaFactor']-0.005)*(100/0.095), callValueUpdateFunction = False)
                self.settingsSubPages['IVP'].GUIOs["INDICATOR_GAMMAFACTOR_VALUETEXT"].updateText("{:.1f} %".format(_caConfig['IVP_GammaFactor']*100))
                self.settingsSubPages['IVP'].GUIOs["INDICATOR_DELTAFACTOR_SLIDER"].setSliderValue(newValue = (_caConfig['IVP_DeltaFactor']-0.1)*(100/9.9), callValueUpdateFunction = False)
                self.settingsSubPages['IVP'].GUIOs["INDICATOR_DELTAFACTOR_VALUETEXT"].updateText("{:d} %".format(int(_caConfig['IVP_DeltaFactor']*100)))
            else:
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_IVP"].setStatus(status = False, callStatusUpdateFunction = False)
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_IVP"].deactivate()
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATORSETUP_IVP"].deactivate()
        if (True): #PIP
            if (_caConfig['PIP_Master'] == True):
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_PIP"].activate()
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATORSETUP_PIP"].activate()
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_SWINGRANGE_SLIDER"].setSliderValue(newValue = (_caConfig['PIP_SwingRange']-0.0010)*(100/0.0490), callValueUpdateFunction = False)
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_SWINGRANGE_VALUETEXT"].updateText(text = "{:.2f} %".format(_caConfig['PIP_SwingRange']*100))
                if (_caConfig['PIP_NeuralNetworkCode'] == None): self.settingsSubPages['PIP'].GUIOs["INDICATOR_NEURALNETWORKCODE_VALUETEXT"].updateText(text = "-")
                else:                                            self.settingsSubPages['PIP'].GUIOs["INDICATOR_NEURALNETWORKCODE_VALUETEXT"].updateText(text = _caConfig['PIP_NeuralNetworkCode'])
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_NNAALPHA_SLIDER"].setSliderValue(newValue = (_caConfig['PIP_NNAAlpha']-0.05)*(100/0.95), callValueUpdateFunction = False)
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_NNAALPHA_VALUETEXT"].updateText(text = "{:.2f}".format(_caConfig['PIP_NNAAlpha']))
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_NNABETA_SLIDER"].setSliderValue(newValue = (_caConfig['PIP_NNABeta']-2)*(100/18), callValueUpdateFunction = False)
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_NNABETA_VALUETEXT"].updateText(text = "{:d}".format(_caConfig['PIP_NNABeta']))
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALALPHA_SLIDER"].setSliderValue(newValue = (_caConfig['PIP_ClassicalAlpha']-0.1)*(100/2.9), callValueUpdateFunction = False)
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALALPHA_VALUETEXT"].updateText(text = "{:.1f}".format(_caConfig['PIP_ClassicalAlpha']))
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALBETA_SLIDER"].setSliderValue(newValue = (_caConfig['PIP_ClassicalBeta']-2)*(100/18), callValueUpdateFunction = False)
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALBETA_VALUETEXT"].updateText(text = "{:d}".format(_caConfig['PIP_ClassicalBeta']))
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALNSAMPLES_INPUTTEXT"].updateText(text = "{:d}".format(_caConfig['PIP_ClassicalNSamples']))
                self.settingsSubPages['PIP'].GUIOs["INDICATOR_CLASSICALSIGMA_INPUTTEXT"].updateText(text    = "{:.1f}".format(_caConfig['PIP_ClassicalSigma']))
            else:
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_PIP"].setStatus(status = False, callStatusUpdateFunction = False)
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATOR_PIP"].deactivate()
                self.settingsSubPages['MAIN'].GUIOs["MAININDICATORSETUP_PIP"].deactivate()
        if (True): #VOL
            if (_caConfig['VOL_Master'] == True):
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_VOL"].activate()
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATORSETUP_VOL"].activate()
                for lineIndex in range (_NMAXLINES['VOL']):
                    lineNumber = lineIndex+1
                    if (_caConfig['VOL_{:d}_LineActive'.format(lineNumber)] == True):
                        self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}".format(lineNumber)].setStatus(status = True, callStatusUpdateFunction = False)
                        self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_INTERVALINPUT".format(lineNumber)].updateText("{:d}".format(_caConfig['VOL_{:d}_NSamples'.format(lineNumber)]))
                        self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_WIDTHINPUT".format(lineNumber)].activate()
                        self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_WIDTHINPUT".format(lineNumber)].updateText("{:d}".format(self.objectConfig['VOL_{:d}_Width'.format(lineNumber)]))
                        self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_DISPLAY".format(lineNumber)].setStatus(status = self.objectConfig['VOL_{:d}_Display'.format(lineNumber)], callStatusUpdateFunction = False)
                        self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_DISPLAY".format(lineNumber)].activate()
                    else:
                        self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
                        self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_INTERVALINPUT".format(lineNumber)].updateText("-")
                        self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_WIDTHINPUT".format(lineNumber)].deactivate()
                        self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_DISPLAY".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
                        self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOL{:d}_DISPLAY".format(lineNumber)].deactivate()
                self.settingsSubPages['VOL'].GUIOs["INDICATOR_VOLTYPESELECTION"].setSelected(itemKey = _caConfig['VOL_VolumeType'], callSelectionUpdateFunction = False)
                self.settingsSubPages['VOL'].GUIOs["INDICATOR_MATYPESELECTION"].setSelected(itemKey  = _caConfig['VOL_MAType'],     callSelectionUpdateFunction = False)
            else:
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_VOL"].setStatus(status = False, callStatusUpdateFunction = False)
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_VOL"].deactivate()
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATORSETUP_VOL"].deactivate()
        if (True): #MMACDSHORT
            if (_caConfig['MMACDSHORT_Master'] == True):
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_MMACDSHORT"].activate()
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATORSETUP_MMACDSHORT"].activate()
                for lineIndex in range (_NMAXLINES['MMACDSHORT']):
                    lineNumber = lineIndex+1
                    if (_caConfig['MMACDSHORT_MA{:d}_LineActive'.format(lineNumber)] == True):
                        self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_MMACDMA{:d}".format(lineNumber)].setStatus(status = True, callStatusUpdateFunction = False)
                        self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_MMACDMA{:d}_INTERVALINPUT".format(lineNumber)].updateText("{:d}".format(_caConfig['MMACDSHORT_MA{:d}_NSamples'.format(lineNumber)]))
                    else:
                        self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_MMACDMA{:d}".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
                        self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_MMACDMA{:d}_INTERVALINPUT".format(lineNumber)].updateText("-")
                self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_SIGNALINTERVALTEXTINPUT"].updateText("{:d}".format(_caConfig['MMACDSHORT_SignalNSamples']))
                self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATOR_MULTIPLIERTEXTINPUT"].updateText("{:d}".format(_caConfig['MMACDSHORT_Multiplier']))
            else:
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_MMACDSHORT"].setStatus(status = False, callStatusUpdateFunction = False)
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_MMACDSHORT"].deactivate()
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATORSETUP_MMACDSHORT"].deactivate()
        if (True): #MMACDLONG
            if (_caConfig['MMACDLONG_Master'] == True):
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_MMACDLONG"].activate()
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATORSETUP_MMACDLONG"].activate()
                for lineIndex in range (_NMAXLINES['MMACDLONG']):
                    lineNumber = lineIndex+1
                    if (_caConfig['MMACDLONG_MA{:d}_LineActive'.format(lineNumber)] == True):
                        self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_MMACDMA{:d}".format(lineNumber)].setStatus(status = True, callStatusUpdateFunction = False)
                        self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_MMACDMA{:d}_INTERVALINPUT".format(lineNumber)].updateText("{:d}".format(_caConfig['MMACDLONG_MA{:d}_NSamples'.format(lineNumber)]))
                    else:
                        self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_MMACDMA{:d}".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
                        self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_MMACDMA{:d}_INTERVALINPUT".format(lineNumber)].updateText("-")
                self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_SIGNALINTERVALTEXTINPUT"].updateText("{:d}".format(_caConfig['MMACDLONG_SignalNSamples']))
                self.settingsSubPages['MMACDLONG'].GUIOs["INDICATOR_MULTIPLIERTEXTINPUT"].updateText("{:d}".format(_caConfig['MMACDLONG_Multiplier']))
            else:
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_MMACDLONG"].setStatus(status = False, callStatusUpdateFunction = False)
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_MMACDLONG"].deactivate()
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATORSETUP_MMACDLONG"].deactivate()
        if (True): #DMIxADX
            if (_caConfig['DMIxADX_Master'] == True):
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_DMIxADX"].activate()
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATORSETUP_DMIxADX"].activate()
                for lineIndex in range (_NMAXLINES['DMIxADX']):
                    lineNumber = lineIndex+1
                    if (_caConfig['DMIxADX_{:d}_LineActive'.format(lineNumber)] == True):
                        self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}".format(lineNumber)].setStatus(status = True, callStatusUpdateFunction = False)
                        self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_INTERVALINPUT".format(lineNumber)].updateText("{:d}".format(_caConfig['DMIxADX_{:d}_NSamples'.format(lineNumber)]))
                        self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_WIDTHINPUT".format(lineNumber)].activate()
                        self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_WIDTHINPUT".format(lineNumber)].updateText("{:d}".format(self.objectConfig['DMIxADX_{:d}_Width'.format(lineNumber)]))
                        self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_DISPLAY".format(lineNumber)].setStatus(status = self.objectConfig['DMIxADX_{:d}_Display'.format(lineNumber)], callStatusUpdateFunction = False)
                        self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_DISPLAY".format(lineNumber)].activate()
                    else:
                        self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
                        self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_INTERVALINPUT".format(lineNumber)].updateText("-")
                        self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_WIDTHINPUT".format(lineNumber)].deactivate()
                        self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_DISPLAY".format(lineNumber)].deactivate()
                        self.settingsSubPages['DMIxADX'].GUIOs["INDICATOR_DMIxADX{:d}_DISPLAY".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
            else:
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_DMIxADX"].setStatus(status = False, callStatusUpdateFunction = False)
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_DMIxADX"].deactivate()
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATORSETUP_DMIxADX"].deactivate()
        if (True): #MFI
            if (_caConfig['MFI_Master'] == True):
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_MFI"].activate()
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATORSETUP_MFI"].activate()
                for lineIndex in range (_NMAXLINES['MFI']):
                    lineNumber = lineIndex+1
                    if (_caConfig['MFI_{:d}_LineActive'.format(lineNumber)] == True):
                        self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}".format(lineNumber)].setStatus(status = True)
                        self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_INTERVALINPUT".format(lineNumber)].updateText("{:d}".format(_caConfig['MFI_{:d}_NSamples'.format(lineNumber)]))
                        self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_WIDTHINPUT".format(lineNumber)].activate()
                        self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_WIDTHINPUT".format(lineNumber)].updateText("{:d}".format(self.objectConfig['MFI_{:d}_Width'.format(lineNumber)]))
                        self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_DISPLAY".format(lineNumber)].setStatus(status = self.objectConfig['MFI_{:d}_Display'.format(lineNumber)], callStatusUpdateFunction = False)
                        self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_DISPLAY".format(lineNumber)].activate()
                    else:
                        self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
                        self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_INTERVALINPUT".format(lineNumber)].updateText("-")
                        self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_WIDTHINPUT".format(lineNumber)].deactivate()
                        self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_DISPLAY".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
                        self.settingsSubPages['MFI'].GUIOs["INDICATOR_MFI{:d}_DISPLAY".format(lineNumber)].deactivate()
            else:
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_MFI"].setStatus(status = False, callStatusUpdateFunction = False)
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_MFI"].deactivate()
                self.settingsSubPages['MAIN'].GUIOs["SUBINDICATORSETUP_MFI"].deactivate()
        if (True): #WOI
            for lineIndex in range (_NMAXLINES['WOI']):
                lineNumber = lineIndex+1
                if (_caConfig['WOI_{:d}_LineActive'.format(lineNumber)] == True):
                    self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}".format(lineNumber)].setStatus(status = True, callStatusUpdateFunction = False)
                    self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_INTERVALINPUT".format(lineNumber)].updateText("{:d}".format(_caConfig['WOI_{:d}_NSamples'.format(lineNumber)]))
                    self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_SIGMAINPUT".format(lineNumber)].updateText("{:.1f}".format(_caConfig['WOI_{:d}_Sigma'.format(lineNumber)]))
                    self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_WIDTHINPUT".format(lineNumber)].activate()
                    self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_WIDTHINPUT".format(lineNumber)].updateText("{:d}".format(self.objectConfig['WOI_{:d}_Width'.format(lineNumber)]))
                    self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_DISPLAY".format(lineNumber)].setStatus(status = self.objectConfig['WOI_{:d}_Display'.format(lineNumber)], callStatusUpdateFunction = False)
                    self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_DISPLAY".format(lineNumber)].activate()
                else:
                    self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
                    self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_INTERVALINPUT".format(lineNumber)].updateText("-")
                    self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_INTERVALINPUT".format(lineNumber)].deactivate()
                    self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_SIGMAINPUT".format(lineNumber)].updateText("-")
                    self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_SIGMAINPUT".format(lineNumber)].deactivate()
                    self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_WIDTHINPUT".format(lineNumber)].deactivate()
                    self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_WIDTHINPUT".format(lineNumber)].updateText("-")
                    self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_DISPLAY".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
                    self.settingsSubPages['WOI'].GUIOs["INDICATOR_WOI{:d}_DISPLAY".format(lineNumber)].deactivate()
        if (True): #NES
            for lineIndex in range (_NMAXLINES['NES']):
                lineNumber = lineIndex+1
                if (_caConfig['NES_{:d}_LineActive'.format(lineNumber)] == True):
                    self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}".format(lineNumber)].setStatus(status = True, callStatusUpdateFunction = False)
                    self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_INTERVALINPUT".format(lineNumber)].updateText("{:d}".format(_caConfig['NES_{:d}_NSamples'.format(lineNumber)]))
                    self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_SIGMAINPUT".format(lineNumber)].updateText("{:.1f}".format(_caConfig['NES_{:d}_Sigma'.format(lineNumber)]))
                    self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_WIDTHINPUT".format(lineNumber)].activate()
                    self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_WIDTHINPUT".format(lineNumber)].updateText("{:d}".format(self.objectConfig['NES_{:d}_Width'.format(lineNumber)]))
                    self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_DISPLAY".format(lineNumber)].setStatus(status = self.objectConfig['NES_{:d}_Display'.format(lineNumber)], callStatusUpdateFunction = False)
                    self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_DISPLAY".format(lineNumber)].activate()
                else:
                    self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
                    self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_INTERVALINPUT".format(lineNumber)].updateText("-")
                    self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_INTERVALINPUT".format(lineNumber)].deactivate()
                    self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_SIGMAINPUT".format(lineNumber)].updateText("-")
                    self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_SIGMAINPUT".format(lineNumber)].deactivate()
                    self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_WIDTHINPUT".format(lineNumber)].deactivate()
                    self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_WIDTHINPUT".format(lineNumber)].updateText("-")
                    self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_DISPLAY".format(lineNumber)].setStatus(status = False, callStatusUpdateFunction = False)
                    self.settingsSubPages['NES'].GUIOs["INDICATOR_NES{:d}_DISPLAY".format(lineNumber)].deactivate()
        if (True): #SI Viewers
            for siViewerIndex in range (len(_SITYPES)):
                siViewerNumber = siViewerIndex+1
                if (siViewerNumber <= self.usableSIViewers):
                    self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_DISPLAYSWITCH{:d}".format(siViewerNumber)].activate()
                    self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_DISPLAYSELECTION{:d}".format(siViewerNumber)].activate()
                else:
                    self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_DISPLAYSWITCH{:d}".format(siViewerNumber)].deactivate()
                    self.settingsSubPages['MAIN'].GUIOs["SUBINDICATOR_DISPLAYSELECTION{:d}".format(siViewerNumber)].deactivate()
        self.objectConfig['VOL_VolumeType'] = _caConfig['VOL_VolumeType']
        self.objectConfig['VOL_MAType']     = _caConfig['VOL_MAType']
        #WOI Prep
        self.siTypes_analysisCodes['WOI'] = list()
        for _lIndex in range (_NMAXLINES['WOI']):
            _lNumber = _lIndex+1
            _woiType = "WOI_{:d}".format(_lNumber)
            if (_caConfig['WOI_{:d}_LineActive'.format(_lNumber)] == True):
                self.siTypes_analysisCodes['WOI'].append(_woiType)
                self.bidsAndAsks[_woiType] = dict()
            else:
                if (_woiType in self.bidsAndAsks): del self.bidsAndAsks[_woiType]
        #NES Prep
        self.siTypes_analysisCodes['NES'] = list()
        for _lIndex in range (_NMAXLINES['NES']):
            _lNumber = _lIndex+1
            _nesType = "NES_{:d}".format(_lNumber)
            if (_caConfig['NES_{:d}_LineActive'.format(_lNumber)] == True):
                self.siTypes_analysisCodes['NES'].append(_nesType)
                self.aggTrades[_nesType] = dict()
            else:
                if (_nesType in self.aggTrades): del self.aggTrades[_nesType]
    def __processKline(self):
        analysisTargetTS = self.analysisQueue_list.pop(0)
        self.analysisQueue_set.remove(analysisTargetTS)
        #Determine wheter to draw this analysis result
        t_open  = analysisTargetTS
        t_close = self.klines['raw'][analysisTargetTS][1]
        classification = 0
        classification += 0b1000*(0 <= t_open -self.horizontalViewRange[0])
        classification += 0b0100*(0 <= t_open -self.horizontalViewRange[1])
        classification += 0b0010*(0 <  t_close-self.horizontalViewRange[0])
        classification += 0b0001*(0 <  t_close-self.horizontalViewRange[1])
        if ((classification == 0b0010) or (classification == 0b1010) or (classification == 0b1011) or (classification == 0b0011)): _addToDrawQueue = True
        else:                                                                                                                      _addToDrawQueue = False
        #Generate analysis for the analysis target
        for analysisPair in self.analysisToProcess_Sorted:
            analysisType = analysisPair[0]
            analysisCode = analysisPair[1]
            if   (self.chartDrawerType == 'TLVIEWER'): _baa = None;             _agt = None
            elif (self.chartDrawerType == 'ANALYZER'): _baa = self.bidsAndAsks; _agt = self.aggTrades
            atmEta_Analyzers.analysisGenerator(analysisType  = analysisType, 
                                               klineAccess   = self.klines, 
                                               intervalID    = self.intervalID, 
                                               mrktRegTS     = self.mrktRegTS, 
                                               precisions    = self.currencyInfo['precisions'], 
                                               timestamp     = analysisTargetTS,
                                               neuralNetwork = self.neuralNetworkInstance,
                                               bidsAndAsks   = _baa,
                                               aggTrades     = _agt,
                                               **self.analysisParams[analysisCode])
            if (_addToDrawQueue == True):
                if (analysisTargetTS in self.klines_drawQueue): self.klines_drawQueue[analysisTargetTS][analysisCode]=None
                else:                                           self.klines_drawQueue[analysisTargetTS]={analysisCode: None}
    #Kline Data END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def getGroupRequirement(): return 30
#'chartDrawer' END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------