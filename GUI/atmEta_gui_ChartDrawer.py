#ATM Modules
from GUI import atmEta_gui_HitBoxes, atmEta_gui_TextControl, atmEta_gui_AdvancedPygletGroups, atmEta_gui_Generals
import atmEta_Auxillaries
import atmEta_Analyzers
import atmEta_IPC
import atmEta_NeuralNetworks
import atmEta_Constants

#Python Modules
import time
import math
import random
from datetime import datetime, timezone, tzinfo
import termcolor
import torch
import pyglet
import gc
import pprint
import bisect
import itertools

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
_NMAXLINES = {'SMA':        atmEta_Constants.NLINES_SMA,
              'WMA':        atmEta_Constants.NLINES_WMA,
              'EMA':        atmEta_Constants.NLINES_EMA,
              'PSAR':       atmEta_Constants.NLINES_PSAR,
              'BOL':        atmEta_Constants.NLINES_BOL,
              'IVP':        None,
              'SWING':      atmEta_Constants.NLINES_SWING,
              'VOL':        atmEta_Constants.NLINES_VOL,
              'NNA':        atmEta_Constants.NLINES_NNA,
              'MMACDSHORT': atmEta_Constants.NLINES_MMACDSHORT,
              'MMACDLONG':  atmEta_Constants.NLINES_MMACDLONG,
              'DMIxADX':    atmEta_Constants.NLINES_DMIxADX,
              'MFI':        atmEta_Constants.NLINES_MFI,
              'WOI':        atmEta_Constants.NLINES_WOI,
              'NES':        atmEta_Constants.NLINES_NES}

_FULLDRAWSIGNALS = {'KLINE':       0b1,
                    'SMA':         0b1,
                    'WMA':         0b1,
                    'EMA':         0b1,
                    'PSAR':        0b1,
                    'BOL':         0b11,
                    'IVP':         0b11,
                    'SWING':       0b1,
                    'VOL':         0b1,
                    'NNA':         0b1,
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
for siViewerIndex in range (len(_SITYPES)):
    siViewerCode = f'SIVIEWER{siViewerIndex}'
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
_TIMEINTERVAL_POSTDRAGWAITTIME       = 200e6
_TIMEINTERVAL_POSTSCROLLWAITTIME     = 200e6
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

_AUX_NANALYSISQUEUEDISPLAYUPDATEINTERVAL_NS = 100e6

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
            self.displayBox[f'SIVIEWER{siViewerIndex}']          = None
            self.displayBox[f'MAINGRID_SIVIEWER{siViewerIndex}'] = None
        self.displayBox_graphics = dict()
        for displayBoxName in self.displayBox: self.displayBox_graphics[displayBoxName] = dict()
        self.displayBox_graphics_visibleSIViewers = set()
        self.displayBox_VerticalSection_Order     = list()
        self.displayBox_VisibleBoxes              = list()
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
        self.klines            = {'raw': dict(), 'raw_status': dict(), 'TRADELOG': dict()}
        self.klines_timestamps = list()
        self.bidsAndAsks       = {'depth': dict(), 'WOI': dict()}
        self.aggTrades         = {'volumes': {'samples': list(), 'buy': 0, 'sell': 0}, 'NES': dict()}
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
                                         'SWING':      self.__klineDrawer_SWING,
                                         'VOL':        self.__klineDrawer_VOL,
                                         'NNA':        self.__klineDrawer_NNA,
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
        self.__onPHUs = {'KLINE':      self.__onPHU_KLINE,
                         'TRADELOG':   self.__onPHU_TRADELOG,
                         'IVP':        self.__onPHU_IVP,
                         'VOL':        self.__onPHU_VOL,
                         'NNA':        self.__onPHU_NNA,
                         'MMACDSHORT': self.__onPHU_MMACDSHORT,
                         'MMACDLONG':  self.__onPHU_MMACDLONG,
                         'DMIxADX':    self.__onPHU_DMIxADX,
                         'MFI':        self.__onPHU_MFI,
                         'WOI':        self.__onPHU_WOI,
                         'NES':        self.__onPHU_NES}

        #<Horizontal ViewRange & Vertical Grid>
        #---Horizontal ViewRange
        self.expectedKlineTemporalWidth = 1500
        self.horizontalViewRangeWidth_min = None; self.horizontalViewRangeWidth_max = None
        self.horizontalViewRangeWidth_m = None;   self.horizontalViewRangeWidth_b = None
        self.horizontalViewRange = [None, None]
        self.horizontalViewRange_timestampsInViewRange  = list()
        self.horizontalViewRange_timestampsInBufferZone = list()
        self.checkVerticalExtremas_SIs = {'VOL':        self.__checkVerticalExtremas_VOL,
                                          'NNA':        self.__checkVerticalExtremas_NNA,
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
            siViewerCode = f'SIVIEWER{siViewerIndex}'
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
            siViewerCode = f'SIVIEWER{siViewerIndex}'
            self.horizontalGridIntervals[siViewerCode]      = list()
            self.horizontalGridIntervalHeight[siViewerCode] = None
            self.nMaxHorizontalGridLines[siViewerCode]      = int((_GD_DISPLAYBOX_SIVIEWER_HEIGHT-_GD_DISPLAYBOX_GOFFSET*2)*self.scaler/_GD_DISPLAYBOX_GRID_HORIZONTALLINEPIXELINTERVAL_SIVIEWER)
        
        #Auxillaries
        self.__lastNumberOfAnalysisQueueDisplayUpdated = 0

        #Object Configuration
        self.sysFunc_editGUIOConfig = kwargs['sysFunctions']['EDITGUIOCONFIG']
        self.objectConfig = dict()
        oc_imported = kwargs['guioConfig'].get(self.name, None)
        if oc_imported is None: self.__initializeObjectConfig()
        else:                   self.objectConfig = oc_imported.copy()
        self.__configureDisplayBoxes(onInit = True)
        self.__matchGUIOsToConfig()
        
        #Object Status
        self.status = "DEFAULT"
        self.hidden = False

        #Chart Drawer Type Dependents
        self.analysisParams = dict()
        guios_MAIN       = self.settingsSubPages['MAIN'].GUIOs
        guios_SMA        = self.settingsSubPages['SMA'].GUIOs
        guios_WMA        = self.settingsSubPages['WMA'].GUIOs
        guios_EMA        = self.settingsSubPages['EMA'].GUIOs
        guios_PSAR       = self.settingsSubPages['PSAR'].GUIOs
        guios_BOL        = self.settingsSubPages['BOL'].GUIOs
        guios_IVP        = self.settingsSubPages['IVP'].GUIOs
        guios_SWING      = self.settingsSubPages['SWING'].GUIOs
        guios_VOL        = self.settingsSubPages['VOL'].GUIOs
        guios_NNA        = self.settingsSubPages['NNA'].GUIOs
        guios_MMACDSHORT = self.settingsSubPages['MMACDSHORT'].GUIOs
        guios_MMACDLONG  = self.settingsSubPages['MMACDLONG'].GUIOs
        guios_DMIxADX    = self.settingsSubPages['DMIxADX'].GUIOs
        guios_MFI        = self.settingsSubPages['MFI'].GUIOs
        guios_WOI        = self.settingsSubPages['WOI'].GUIOs
        guios_NES        = self.settingsSubPages['NES'].GUIOs
        if (self.chartDrawerType == 'CAVIEWER') or (self.chartDrawerType == 'TLVIEWER'): #Settings Subpage GUIOs Activation Setup 1
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
            guios_VOL["INDICATOR_VOLTYPESELECTION"].deactivate()
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
            #MMACDSHORT
            guios_MMACDSHORT["INDICATOR_SIGNALINTERVALTEXTINPUT"].deactivate()
            guios_MMACDSHORT["INDICATOR_MULTIPLIERTEXTINPUT"].deactivate()
            for lineIndex in range (_NMAXLINES['MMACDSHORT']):
                guios_MMACDSHORT[f"INDICATOR_MMACDMA{lineIndex}"].deactivate()
                guios_MMACDSHORT[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].deactivate()
            #MMACDLONG
            guios_MMACDLONG["INDICATOR_SIGNALINTERVALTEXTINPUT"].deactivate()
            guios_MMACDLONG["INDICATOR_MULTIPLIERTEXTINPUT"].deactivate()
            for lineIndex in range (_NMAXLINES['MMACDLONG']):
                guios_MMACDLONG[f"INDICATOR_MMACDMA{lineIndex}"].deactivate()
                guios_MMACDLONG[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].deactivate()
            #DMIxADX
            for lineIndex in range (_NMAXLINES['DMIxADX']):
                guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}"].deactivate()
                guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT"].deactivate()
            #MFI
            for lineIndex in range (_NMAXLINES['MFI']):
                guios_MFI[f"INDICATOR_MFI{lineIndex}"].deactivate()
                guios_MFI[f"INDICATOR_MFI{lineIndex}_INTERVALINPUT"].deactivate()
            #WOI
            for lineIndex in range (_NMAXLINES['WOI']):
                guios_WOI[f"INDICATOR_WOI{lineIndex}"].deactivate()
                guios_WOI[f"INDICATOR_WOI{lineIndex}_SIGMAINPUT"].deactivate()
                guios_WOI[f"INDICATOR_WOI{lineIndex}_INTERVALINPUT"].deactivate()
            #NES
            for lineIndex in range (_NMAXLINES['NES']):
                guios_NES[f"INDICATOR_NES{lineIndex}"].deactivate()
                guios_NES[f"INDICATOR_NES{lineIndex}_SIGMAINPUT"].deactivate()
                guios_NES[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].deactivate()
        if (self.chartDrawerType == 'CAVIEWER') or (self.chartDrawerType == 'ANALYZER'): #Settings Subpage GUIOs Activation Setup 2
            guios_MAIN["TRADELOGCOLOR_TARGETSELECTION"].deactivate()
            guios_MAIN["TRADELOGCOLOR_APPLYCOLOR"].deactivate()
            guios_MAIN["TRADELOGCOLOR_R_SLIDER"].deactivate()
            guios_MAIN["TRADELOGCOLOR_G_SLIDER"].deactivate()
            guios_MAIN["TRADELOGCOLOR_B_SLIDER"].deactivate()
            guios_MAIN["TRADELOGCOLOR_A_SLIDER"].deactivate()
            guios_MAIN["TRADELOGDISPLAY_SWITCH"].deactivate()
            guios_MAIN["TRADELOG_APPLYNEWSETTINGS"].deactivate()
        if (self.chartDrawerType == 'TLVIEWER'):                                         #Settings Subpage GUIOs Activation Setup 3
            guios_MAIN["BIDSANDASKSCOLOR_TARGETSELECTION"].deactivate()
            guios_MAIN["BIDSANDASKSCOLOR_APPLYCOLOR"].deactivate()
            guios_MAIN["BIDSANDASKSCOLOR_R_SLIDER"].deactivate()
            guios_MAIN["BIDSANDASKSCOLOR_G_SLIDER"].deactivate()
            guios_MAIN["BIDSANDASKSCOLOR_B_SLIDER"].deactivate()
            guios_MAIN["BIDSANDASKSCOLOR_A_SLIDER"].deactivate()
            guios_MAIN["BIDSANDASKSDISPLAY_SWITCH"].deactivate()
            guios_MAIN["BIDSANDASKS_APPLYNEWSETTINGS"].deactivate()
        if   (self.chartDrawerType == 'CAVIEWER'):
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
            self.neuralNetworkConnectionDataRequestIDs = dict()
            self.neuralNetworkInstances                = dict()
            self.analysisToProcess_Sorted = list()
            self.analysisQueue_list = list()
            self.analysisQueue_set  = set()
            self.klines_targetFetchRange_original = None
            self.klines_targetFetchRange_current  = None
            self.klines_fetchRequestRID           = None
            self.caRegeneration_nAnalysis_initial = None
            self.__setTarget_TLViewer(target = None)
        elif (self.chartDrawerType == 'ANALYZER'):
            self.canStartAnalysis                      = False
            self.analyzingStream                       = False
            self.neuralNetworkConnectionDataRequestIDs = dict()
            self.neuralNetworkInstances                = dict()
            self.analysisToProcess_Sorted = list()
            self.analysisQueue_list = list()
            self.analysisQueue_set  = set()
            self.klines_targetFetchRange_original = None
            self.klines_targetFetchRange_current  = None
            self.klines_fetchRequestRID           = None
            #WOI Prep
            self.siTypes_analysisCodes['WOI'] = list()
            for lineIndex in range (_NMAXLINES['WOI']):
                woiType = f"WOI_{lineIndex}"
                if self.objectConfig[f'WOI_{lineIndex}_LineActive']:
                    self.siTypes_analysisCodes['WOI'].append(woiType)
                    self.bidsAndAsks[woiType] = dict()
                else:
                    if (woiType in self.bidsAndAsks): del self.bidsAndAsks[woiType]
            #NES Prep
            self.siTypes_analysisCodes['NES'] = list()
            for lineIndex in range (_NMAXLINES['NES']):
                nesType = f"NES_{lineIndex}"
                if self.objectConfig[f'NES_{lineIndex}_LineActive']:
                    self.siTypes_analysisCodes['NES'].append(nesType)
                    self.aggTrades[nesType] = dict()
                else:
                    if (nesType in self.aggTrades): del self.aggTrades[nesType]
            #Target Set
            self.__setTarget_Analyzer(currencySymbol = None)
    #Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Object Configuration & GUIO Initialization ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __configureSettingsSubPageObjects(self):
        subPageViewSpaceWidth = 4000
        #<MAIN>
        if (True):
            ssp = self.settingsSubPages['MAIN']
            yPos_beg = 20000
            #Title
            ssp.addGUIO("TITLE_MAIN", atmEta_gui_Generals.passiveGraphics_wrapperTypeB, {'groupOrder': 0, 'xPos': 0, 'yPos': yPos_beg, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_CHARTSETTINGS')})
            #Main Indicators
            yPosPoint0 = yPos_beg-200
            ssp.addGUIO("TITLE_MAININDICATORS", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MAININDICATORS'), 'fontSize': 80})
            for i, miType in enumerate(_MITYPES):
                ssp.addGUIO(f"MAININDICATOR_{miType}",      atmEta_gui_Generals.switch_typeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-350-350*i, 'width': 3500, 'height': 250, 'style': 'styleB', 'name': f'MAIN_INDICATORSWITCH_{miType}', 'text': miType, 'fontSize': 80, 'releaseFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"MAININDICATORSETUP_{miType}", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 3600, 'yPos': yPosPoint0-350-350*i, 'width':  400, 'height': 250, 'style': 'styleA', 'name': f'navButton_MI_{miType}',         'text': ">",    'fontSize': 80, 'releaseFunction': self.__onSettingsNavButtonClick})
            #Sub Indicators
            yPosPoint1 = yPosPoint0-300-350*len(_MITYPES)
            ssp.addGUIO("TITLE_SUBINDICATORS", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SUBINDICATORS'), 'fontSize': 80})
            for i, siType in enumerate(_SITYPES):
                ssp.addGUIO(f"SUBINDICATOR_{siType}",      atmEta_gui_Generals.switch_typeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350-350*i, 'width': 3500, 'height': 250, 'style': 'styleB', 'name': f'MAIN_INDICATORSWITCH_{siType}', 'text': siType, 'fontSize': 80, 'releaseFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"SUBINDICATORSETUP_{siType}", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 3600, 'yPos': yPosPoint1-350-350*i, 'width':  400, 'height': 250, 'style': 'styleA', 'text': ">", 'fontSize': 80, 'name': f'navButton_SI_{siType}', 'releaseFunction': self.__onSettingsNavButtonClick})
            #Sub Indicators Display
            yPosPoint2 = yPosPoint1-300-350*len(_SITYPES)
            ssp.addGUIO("TITLE_SUBINDICATORSDISPLAY", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SUBINDICATORDISPLAY'), 'fontSize': 80})
            siSelection = dict()
            for siType in _SITYPES: siSelection[siType] = {'text': siType}
            for siViewerIndex in range (len(_SITYPES)):
                ssp.addGUIO(f"SUBINDICATOR_DISPLAYSWITCH{siViewerIndex}",    atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint2-350-350*siViewerIndex, 'width': 1100, 'height': 250, 'style': 'styleB', 'name': f'MAIN_SIVIEWERDISPLAYSWITCH_{siViewerIndex}',    'text': self.visualManager.getTextPack(f'GUIO_CHARTDRAWER:INDICATOR{siViewerIndex}'), 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"SUBINDICATOR_DISPLAYSELECTION{siViewerIndex}", atmEta_gui_Generals.selectionBox_typeB, {'groupOrder': 0, 'xPos': 1200, 'yPos': yPosPoint2-350-350*siViewerIndex, 'width': 2800, 'height': 250, 'style': 'styleA', 'name': f'MAIN_SIVIEWERDISPLAYSELECTION_{siViewerIndex}', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
                ssp.GUIOs[f"SUBINDICATOR_DISPLAYSELECTION{siViewerIndex}"].setSelectionList(selectionList = siSelection, displayTargets = 'all')
            #Analyzer
            yPosPoint3 = yPosPoint2-300-350*len(_SITYPES)
            ssp.addGUIO("TITLE_ANALYZER", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint3, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_ANALYZER'), 'fontSize': 80})
            ssp.addGUIO("ANALYZER_ANALYSISRANGEBEG_TEXT",       atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint3- 350, 'width': 2200, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:ANALYSISRANGEBEG'), 'fontSize': 80})
            ssp.addGUIO("ANALYZER_ANALYSISRANGEBEG_RANGEINPUT", atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2300, 'yPos': yPosPoint3- 350, 'width': 1700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MAIN_ANALYSISRANGETEXTINPUTBOX', 'textUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("ANALYZER_ANALYSISRANGEEND_TEXT",       atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint3- 700, 'width': 2200, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:ANALYSISRANGEEND'), 'fontSize': 80})
            ssp.addGUIO("ANALYZER_ANALYSISRANGEEND_RANGEINPUT", atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2300, 'yPos': yPosPoint3- 700, 'width': 1700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MAIN_ANALYSISRANGETEXTINPUTBOX', 'textUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("ANALYZER_STARTANALYSIS_BUTTON",        atmEta_gui_Generals.button_typeA,       {'groupOrder': 0, 'xPos': 0,    'yPos': yPosPoint3-1050, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:STARTANALYSIS'), 'fontSize': 80, 'name': 'MAIN_STARTANALYSIS', 'releaseFunction': self.__onSettingsContentUpdate})
            #Trade Log
            yPosPoint4 = yPosPoint3-1350
            ssp.addGUIO("TITLE_TRADELOG",                atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos':  yPosPoint4, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_TRADELOG'), 'fontSize': 80})
            ssp.addGUIO("TRADELOGCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint4-350, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("TRADELOGCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB, {'groupOrder': 2, 'xPos':  700, 'yPos': yPosPoint4-350, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'TRADELOG_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("TRADELOGCOLOR_LED",             atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2300, 'yPos': yPosPoint4-350, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("TRADELOGCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,       {'groupOrder': 0, 'xPos': 3350, 'yPos': yPosPoint4-350, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'TRADELOG_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"TRADELOGCOLOR_{componentType}_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint4-700-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"TRADELOGCOLOR_{componentType}_SLIDER", atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': yPosPoint4-700-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'TRADELOG_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"TRADELOGCOLOR_{componentType}_VALUE",  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': yPosPoint4-700-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            yPosPoint5 = yPosPoint4-2100
            ssp.addGUIO("TRADELOGDISPLAY_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 0,    'yPos': yPosPoint5, 'width': 1600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYTRADELOG'), 'fontSize': 80})
            ssp.addGUIO("TRADELOGDISPLAY_SWITCH", atmEta_gui_Generals.switch_typeB,  {'groupOrder': 0, 'xPos': 1700, 'yPos': yPosPoint5, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'TRADELOG_DisplaySwitch', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("TRADELOGCOLOR_BUY_LED",  atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 2300, 'yPos': yPosPoint5, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("TRADELOGCOLOR_SELL_LED", atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3200, 'yPos': yPosPoint5, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            lineSelections = {'BUY':  {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TRADELOG_BUY')},
                              'SELL': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TRADELOG_SELL')}}
            ssp.GUIOs["TRADELOGCOLOR_TARGETSELECTION"].setSelectionList(lineSelections, displayTargets = 'all')
            ssp.addGUIO("TRADELOG_APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint5-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'TRADELOG_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            #Bids and Asks
            yPosPoint6 = yPosPoint5-650
            ssp.addGUIO("TITLE_BIDSANDASKS",                atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos':  yPosPoint6, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_BIDSANDASKS'), 'fontSize': 80})
            ssp.addGUIO("BIDSANDASKSCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint6-350, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("BIDSANDASKSCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB, {'groupOrder': 2, 'xPos':  700, 'yPos': yPosPoint6-350, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'BIDSANDASKS_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("BIDSANDASKSCOLOR_LED",             atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2300, 'yPos': yPosPoint6-350, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("BIDSANDASKSCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,       {'groupOrder': 0, 'xPos': 3350, 'yPos': yPosPoint6-350, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'BIDSANDASKS_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"BIDSANDASKSCOLOR_{componentType}_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint6-700-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"BIDSANDASKSCOLOR_{componentType}_SLIDER", atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': yPosPoint6-700-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'BIDSANDASKS_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"BIDSANDASKSCOLOR_{componentType}_VALUE",  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': yPosPoint6-700-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            yPosPoint7 = yPosPoint6-2100
            ssp.addGUIO("BIDSANDASKSDISPLAY_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 0,    'yPos': yPosPoint7, 'width': 1600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYBIDSANDASKS'), 'fontSize': 80})
            ssp.addGUIO("BIDSANDASKSDISPLAY_SWITCH", atmEta_gui_Generals.switch_typeB,  {'groupOrder': 0, 'xPos': 1700, 'yPos': yPosPoint7, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'BIDSANDASKS_DisplaySwitch', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("BIDSANDASKSCOLOR_BIDS_LED", atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 2300, 'yPos': yPosPoint7, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("BIDSANDASKSCOLOR_ASKS_LED", atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3200, 'yPos': yPosPoint7, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            lineSelections = {'BIDS': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BIDSANDASKS_BIDS')},
                              'ASKS': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BIDSANDASKS_ASKS')}}
            ssp.GUIOs["BIDSANDASKSCOLOR_TARGETSELECTION"].setSelectionList(lineSelections, displayTargets = 'all')
            ssp.addGUIO("BIDSANDASKS_APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint7-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'BIDSANDASKS_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            #Aux Settings
            yPosPoint8 = yPosPoint7-700
            ssp.addGUIO("TITLE_AUX",                       atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos':  yPosPoint8,      'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_AUX'), 'fontSize': 80})
            ssp.addGUIO("AUX_KLINECOLORTYPE_TEXT",         atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos':  yPosPoint8- 350, 'width': 1750,                  'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:KLINECOLORTYPE'), 'fontSize': 80})
            ssp.addGUIO("AUX_KLINECOLORTYPE_SELECTIONBOX", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 1, 'xPos': 1850, 'yPos':  yPosPoint8- 350, 'width': 2150,                  'height': 250, 'style': 'styleA', 'name': 'MAIN_KLINECOLORTYPE_SELECTION', 'nDisplay': 5, 'fontSize': 80, 'expansionDir': 1, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("AUX_TIMEZONE_TEXT",               atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos':  yPosPoint8- 700, 'width': 1750,                  'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TIMEZONE'), 'fontSize': 80})
            ssp.addGUIO("AUX_TIMEZONE_SELECTIONBOX",       atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1850, 'yPos':  yPosPoint8- 700, 'width': 2150,                  'height': 250, 'style': 'styleA', 'name': 'MAIN_TIMEZONE_SELECTION', 'nDisplay': 10, 'fontSize': 80, 'expansionDir': 1, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("AUX_SAVECONFIGURATION",           atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 0,    'yPos':  yPosPoint8-1050, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SAVECONFIG'), 'fontSize': 80, 'name': 'MAIN_SAVECONFIG', 'releaseFunction': self.__onSettingsContentUpdate})
            #GUIO Setup
            ssp.GUIOs["AUX_KLINECOLORTYPE_SELECTIONBOX"].setSelectionList({1: {'text': 'TYPE1'}, 2: {'text': 'TYPE2'}}, displayTargets = 'all')
            timeZoneSelections = {'LOCAL': {'text': 'LOCAL'}}
            for hour in range (24): timeZoneSelections[f'UTC+{hour:d}'] = {'text': f'UTC+{hour:d}'}
            ssp.GUIOs["AUX_TIMEZONE_SELECTIONBOX"].setSelectionList(timeZoneSelections, displayTargets = 'all')
        #<SMA & WMA & EMA Settings>
        if (True):
            for miType in ('SMA', 'WMA', 'EMA'):
                ssp = self.settingsSubPages[miType]
                ssp.addGUIO("SUBPAGETITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack(f'GUIO_CHARTDRAWER:TITLE_MI_{miType}'), 'fontSize': 100})
                ssp.addGUIO("NAGBUTTON",    atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width':                   400, 'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
                ssp.addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
                ssp.addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
                ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': f'{miType}_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
                ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': f'{miType}_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
                for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                    ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                    ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'{miType}_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                    ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
                ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 800, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
                ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  900, 'yPos': 7550, 'width': 900, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
                ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1900, 'yPos': 7550, 'width': 750, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
                ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2750, 'yPos': 7550, 'width': 650, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
                ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",  atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
                maList = dict()
                for lineIndex in range (_NMAXLINES[miType]):
                    ssp.addGUIO(f"INDICATOR_{miType}{lineIndex}",               atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*lineIndex, 'width': 800, 'height': 250, 'style': 'styleB', 'name': f'{miType}_LineActivationSwitch_{lineIndex}', 'text': f'{miType} {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                    ssp.addGUIO(f"INDICATOR_{miType}{lineIndex}_INTERVALINPUT", atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  900, 'yPos': 7200-350*lineIndex, 'width': 900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'{miType}_IntervalTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
                    ssp.addGUIO(f"INDICATOR_{miType}{lineIndex}_WIDTHINPUT",    atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1900, 'yPos': 7200-350*lineIndex, 'width': 750, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'{miType}_WidthTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
                    ssp.addGUIO(f"INDICATOR_{miType}{lineIndex}_LINECOLOR",     atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2750, 'yPos': 7200-350*lineIndex, 'width': 650, 'height': 250, 'style': 'styleA', 'mode': True})
                    ssp.addGUIO(f"INDICATOR_{miType}{lineIndex}_DISPLAY",       atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'{miType}_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
                    maList[f"{lineIndex}"] = {'text': f"{miType} {lineIndex}"}
                ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = maList, displayTargets = 'all')
                ssp.addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': 7200-350*(_NMAXLINES[miType]-1)-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': f'{miType}_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
        #<PSAR Settings>
        if (True):
            ssp = self.settingsSubPages['PSAR']
            ssp.addGUIO("SUBPAGETITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MI_PSAR'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",    atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'PSAR_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'PSAR_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'PSAR_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",        atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),            'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORSTART_COLUMNTITLE",        atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  700, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:PSARSTART'),        'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORACCELERATION_COLUMNTITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1300, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:PSARACCELERATION'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORMAXIMUM_COLUMNTITLE",      atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1900, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:PSARMAXIMUM'),      'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORSIZE_COLUMNTITLE",         atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2500, 'yPos': 7550, 'width': 400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SIZE'),             'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",        atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3000, 'yPos': 7550, 'width': 400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),            'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",      atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),          'fontSize': 90, 'anchor': 'SW'})
            psarList = dict()
            for lineIndex in range (_NMAXLINES['PSAR']):
                ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}",            atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*lineIndex, 'width': 600, 'height': 250, 'style': 'styleB', 'name': f'PSAR_LineActivationSwitch_{lineIndex}', 'text': f'PSAR {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}_AF0INPUT",   atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  700, 'yPos': 7200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'PSAR_AF0TextInputBox_{lineIndex}',   'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}_AF+INPUT",   atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1300, 'yPos': 7200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'PSAR_AF+TextInputBox_{lineIndex}',   'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}_AFMAXINPUT", atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1900, 'yPos': 7200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'PSAR_AFMaxTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}_WIDTHINPUT", atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2500, 'yPos': 7200-350*lineIndex, 'width': 400, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'PSAR_WidthTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}_LINECOLOR",  atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 3000, 'yPos': 7200-350*lineIndex, 'width': 400, 'height': 250, 'style': 'styleA', 'mode': True})
                ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}_DISPLAY",    atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'PSAR_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
                psarList[f"{lineIndex}"] = {'text': f"PSAR {lineIndex}"}
            yPosPoint0 = 7200-350*(_NMAXLINES['PSAR']-1)
            ssp.addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'PSAR_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = psarList, displayTargets = 'all')
        #<BOL Settings>
        if (True):
            ssp = self.settingsSubPages['BOL']
            ssp.addGUIO("SUBPAGETITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MI_BOL'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",    atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'BOL_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'BOL_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'BOL_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ssp.addGUIO("INDICATOR_BLOCKTITLE_MATYPE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATOR_MATYPETEXT",        atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1550, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_MATYPESELECTION",   atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1650, 'yPos': 7200, 'width':                  2350, 'height': 250, 'style': 'styleA', 'name': 'BOL_MATypeSelection', 'nDisplay': 3, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            maTypes = {'SMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_SMA')},
                       'WMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_WMA')},
                       'EMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_EMA')}}
            ssp.GUIOs["INDICATOR_MATYPESELECTION"].setSelectionList(selectionList = maTypes, displayTargets = 'all')
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 800, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),         'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE",  atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  900, 'yPos': 6850, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVALSHORT'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORBANDWIDTH_COLUMNTITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1600, 'yPos': 6850, 'width': 550, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BANDWIDTH'),     'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2250, 'yPos': 6850, 'width': 550, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),         'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2900, 'yPos': 6850, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),         'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",   atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6850, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),       'fontSize': 90, 'anchor': 'SW'})
            bolList = dict()
            for lineIndex in range (_NMAXLINES['BOL']):
                ssp.addGUIO(f"INDICATOR_BOL{lineIndex}",                atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6500-350*lineIndex, 'width': 800, 'height': 250, 'style': 'styleB', 'name': f'BOL_LineActivationSwitch_{lineIndex}', 'text': f'BOL {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_BOL{lineIndex}_INTERVALINPUT",  atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  900, 'yPos': 6500-350*lineIndex, 'width': 600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'BOL_IntervalTextInputBox_{lineIndex}',  'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_BOL{lineIndex}_BANDWIDTHINPUT", atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1600, 'yPos': 6500-350*lineIndex, 'width': 550, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'BOL_BandWidthTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_BOL{lineIndex}_WIDTHINPUT",     atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2250, 'yPos': 6500-350*lineIndex, 'width': 550, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'BOL_WidthTextInputBox_{lineIndex}',     'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_BOL{lineIndex}_LINECOLOR",      atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2900, 'yPos': 6500-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'mode': True})
                ssp.addGUIO(f"INDICATOR_BOL{lineIndex}_DISPLAY",        atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'BOL_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
                bolList[f"{lineIndex}"] = {'text': f"BOL {lineIndex}"}
            yPosPoint0 = 6500-350*(_NMAXLINES['BOL']-1)
            ssp.addGUIO("INDICATOR_BLOCKTITLE_DISPLAYCONTENTS",      atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYCONTENTS'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATOR_DISPLAYCONTENTS_BOLCENTERTEXT",   atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 700, 'width':                  3400, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYBOLCENTER'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_DISPLAYCONTENTS_BOLCENTERSWITCH", atmEta_gui_Generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint0- 700, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'BOL_DisplayContentsSwitch_BolCenter', 'releaseFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_DISPLAYCONTENTS_BOLBANDTEXT",     atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-1050, 'width':                  3400, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYBOLBAND'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_DISPLAYCONTENTS_BOLBANDSWITCH",   atmEta_gui_Generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint0-1050, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'BOL_DisplayContentsSwitch_BolBand', 'releaseFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-1400, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'BOL_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = bolList, displayTargets = 'all')
        #<IVP Settings>
        if (True):
            ssp = self.settingsSubPages['IVP']
            ssp.addGUIO("SUBPAGETITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MI_IVP'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",    atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width':                  1500, 'height': 250, 'style': 'styleA', 'name': 'IVP_LineSelectionBox', 'nDisplay': 9, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':                   950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':                   650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'IVP_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'IVP_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ivpLineTargets = {'VPLP':  {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLP')},
                              'VPLPB': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLPB')}}
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = ivpLineTargets, displayTargets = 'all')
            ssp.addGUIO("INDICATOR_BLOCKTITLE_IVPDISPLAY", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPDISPLAY'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATOR_VPLP_DISPLAYTEXT",             atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLPDISPLAY'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_VPLP_DISPLAYSWITCH",           atmEta_gui_Generals.switch_typeB,  {'groupOrder': 0, 'xPos': 1900, 'yPos': 7200, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'IVP_DisplaySwitch_VPLP', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_VPLP_COLORTEXT",               atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 2500, 'yPos': 7200, 'width':  700, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_VPLP_COLOR",                   atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3300, 'yPos': 7200, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_VPLP_DISPLAYWIDTHTEXT",        atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYWIDTH'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_VPLP_DISPLAYWIDTHSLIDER",      atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos': 1300, 'yPos': 6900, 'width': 2000, 'height': 150, 'style': 'styleA', 'name': 'IVP_DisplayWidthSlider_VPLP', 'valueUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_VPLP_DISPLAYWIDTHVALUETEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3400, 'yPos': 6850, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            ssp.addGUIO("INDICATOR_VPLPB_DISPLAYTEXT",            atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 6500, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLPBDISPLAY'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_VPLPB_DISPLAYSWITCH",          atmEta_gui_Generals.switch_typeB,  {'groupOrder': 0, 'xPos': 1900, 'yPos': 6500, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'IVP_DisplaySwitch_VPLPB', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_VPLPB_COLORTEXT",              atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 2500, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_VPLPB_COLOR",                  atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3300, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_VPLPB_DISPLAYREGIONTEXT",      atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 6150, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYREGION'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_VPLPB_DISPLAYREGIONSLIDER",    atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos': 1400, 'yPos': 6200, 'width': 1800, 'height': 150, 'style': 'styleA', 'name': 'IVP_VPLPBDisplayRegion', 'valueUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_VPLPB_DISPLAYREGIONVALUETEXT", atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 6150, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            ssp.addGUIO("INDICATOR_BLOCKTITLE_IVPPARAMS", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': 5800, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPPARAMS'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATOR_INTERVAL_DISPLAYTEXT",    atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 5450, 'width': 1900, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_INTERVAL_INPUTTEXT",      atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2000, 'yPos': 5450, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'IVP_Interval', 'textUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_GAMMAFACTOR_DISPLAYTEXT", atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 5100, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPGAMMAFACTOR'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_GAMMAFACTOR_SLIDER",      atmEta_gui_Generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1100, 'yPos': 5150, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_GammaFactor', 'valueUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_GAMMAFACTOR_VALUETEXT",   atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': 5100, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            ssp.addGUIO("INDICATOR_DELTAFACTOR_DISPLAYTEXT", atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 4750, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPDELTAFACTOR'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_DELTAFACTOR_SLIDER",      atmEta_gui_Generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1100, 'yPos': 4800, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_DeltaFactor', 'valueUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_DELTAFACTOR_VALUETEXT",   atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': 4750, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            ssp.addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': 4400, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'IVP_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
        #<SWING Settings>
        if (True):
            ssp = self.settingsSubPages['SWING']
            ssp.addGUIO("SUBPAGETITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MI_SWING'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",    atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'SWING_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'SWING_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'SWING_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",      atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),      'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORSWINGRANGE_COLUMNTITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 7550, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SWINGRANGE'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",      atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2300, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),      'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",      atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2900, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),      'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),    'fontSize': 90, 'anchor': 'SW'})
            swingList = dict()
            for lineIndex in range (_NMAXLINES['SWING']):
                ssp.addGUIO(f"INDICATOR_SWING{lineIndex}",                 atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'SWING_LineActivationSwitch_{lineIndex}', 'text': f'SWING {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT", atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': 7200-350*lineIndex, 'width': 1100, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'SWING_SwingRangeTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_SWING{lineIndex}_WIDTHINPUT",      atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2300, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'SWING_WidthTextInputBox_{lineIndex}', 'text': "", 'fontSize': 80, 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_SWING{lineIndex}_LINECOLOR",       atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2900, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'mode': True})
                ssp.addGUIO(f"INDICATOR_SWING{lineIndex}_DISPLAY",         atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'SWING_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
                swingList[f"{lineIndex}"] = {'text': f"SWING {lineIndex}"}
            yPosPoint0 = 7200-350*(_NMAXLINES['SWING']-1)
            ssp.addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'SWING_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = swingList, displayTargets = 'all')
        #<VOL Settings>
        if (True):
            ssp = self.settingsSubPages['VOL']
            ssp.addGUIO("SUBPAGETITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_VOL'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",    atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'VOL_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'VOL_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'VOL_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ssp.addGUIO("INDICATORINDEX_BLOCKTITLE_MA",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLSETTINGS'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATOR_VOLTYPETEXT",      atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_VOLTYPESELECTION", atmEta_gui_Generals.selectionBox_typeB, {'groupOrder': 2, 'xPos': 1900, 'yPos': 7200, 'width': 2100, 'height': 250, 'style': 'styleA', 'name': 'VOL_VolTypeSelection', 'nDisplay': 4, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            volTypes = {'BASE':    {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE_BASE')},
                        'QUOTE':   {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE_QUOTE')},
                        'BASETB':  {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE_BASETB')},
                        'QUOTETB': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE_QUOTETB')}}
            ssp.GUIOs["INDICATOR_VOLTYPESELECTION"].setSelectionList(selectionList = volTypes, displayTargets = 'all')
            ssp.addGUIO("INDICATOR_MATYPETEXT",       atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_MATYPESELECTION",  atmEta_gui_Generals.selectionBox_typeB, {'groupOrder': 2, 'xPos': 1900, 'yPos': 6850, 'width': 2100, 'height': 250, 'style': 'styleA', 'name': 'VOL_MATypeSelection', 'nDisplay': 3, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            maTypes = {'SMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_SMA')},
                       'WMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_WMA')},
                       'EMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_EMA')}}
            ssp.GUIOs["INDICATOR_MATYPESELECTION"].setSelectionList(selectionList = maTypes, displayTargets = 'all')
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6500, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE",  atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1900, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2700, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",   atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
            volMAList = dict()
            for lineIndex in range (_NMAXLINES['VOL']):
                ssp.addGUIO(f"INDICATOR_VOL{lineIndex}",               atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6150-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'VOL_LineActivationSwitch_{lineIndex}', 'text': f'VOLMA {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_VOL{lineIndex}_INTERVALINPUT", atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6150-350*lineIndex, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'VOL_IntervalTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_VOL{lineIndex}_WIDTHINPUT",    atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1900, 'yPos': 6150-350*lineIndex, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'VOL_WidthTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_VOL{lineIndex}_LINECOLOR",     atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2700, 'yPos': 6150-350*lineIndex, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
                ssp.addGUIO(f"INDICATOR_VOL{lineIndex}_DISPLAY",       atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6150-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'VOL_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
                volMAList[f"{lineIndex}"] = {'text': f"VOLMA {lineIndex}"}
            yPosPoint0 = 6150-350*(_NMAXLINES['VOL']-1)
            ssp.addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'VOL_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = volMAList, displayTargets = 'all')
        #<NNA Settings>
        if (True):
            ssp = self.settingsSubPages['NNA']
            ssp.addGUIO("SUBPAGETITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_NNA'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",    atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'NNA_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'NNA_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'NNA_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",   atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),             'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORNNCODE_COLUMNTITLE",  atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  700, 'yPos': 7550, 'width':  900, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:NEURALNETWORKCODE'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORALPHA_COLUMNTITLE",   atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1700, 'yPos': 7550, 'width':  400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:ALPHA'),             'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORBETA_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2200, 'yPos': 7550, 'width':  300, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BETA'),              'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORSIZE_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2600, 'yPos': 7550, 'width':  300, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SIZE'),              'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",   atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3000, 'yPos': 7550, 'width':  400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),             'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),           'fontSize': 90, 'anchor': 'SW'})
            nnaList = dict()
            for lineIndex in range (_NMAXLINES['NNA']):
                ssp.addGUIO(f"INDICATOR_NNA{lineIndex}",             atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleB', 'name': f'NNA_LineActivationSwitch_{lineIndex}', 'text': f'NNA {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_NNCODEINPUT", atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  700, 'yPos': 7200-350*lineIndex, 'width':  900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_NNCodeTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_ALPHAINPUT",  atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1700, 'yPos': 7200-350*lineIndex, 'width':  400, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_AlphaTextInputBox_{lineIndex}',  'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_BETAINPUT",   atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2200, 'yPos': 7200-350*lineIndex, 'width':  300, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_BetaTextInputBox_{lineIndex}',   'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_WIDTHINPUT",  atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2600, 'yPos': 7200-350*lineIndex, 'width':  300, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_WidthTextInputBox_{lineIndex}',  'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_LINECOLOR",   atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 3000, 'yPos': 7200-350*lineIndex, 'width':  400, 'height': 250, 'style': 'styleA', 'mode': True})
                ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_DISPLAY",     atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'NNA_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
                nnaList[f"{lineIndex}"] = {'text': f"NNA {lineIndex}"}
            yPosPoint0 = 7200-350*(_NMAXLINES['NNA']-1)
            ssp.addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'NNA_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = nnaList, displayTargets = 'all')
        #<MMACDSHORT Settings>
        if (True):
            ssp = self.settingsSubPages['MMACDSHORT']
            ssp.addGUIO("SUBPAGETITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_MMACDSHORT'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",    atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':                   550, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width':                  1500, 'height': 250, 'style': 'styleA', 'name': 'MMACDSHORT_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':                   950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':                   650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'MMACDSHORT_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'MMACDSHORT_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            mmacdLineTargets = {'MMACD':      {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDMMACD')},
                                'SIGNAL':     {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNAL')},
                                'HISTOGRAM+': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAM+')},
                                'HISTOGRAM-': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAM-')}}
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = mmacdLineTargets, displayTargets = 'all')
            ssp.addGUIO("INDICATOR_BLOCKTITLE_DISPLAY",       atmEta_gui_Generals.passiveGraphics_wrapperTypeC,   {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDDISPLAY'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATOR_MMACD_DISPLAYTEXT",        atmEta_gui_Generals.textBox_typeA,                  {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDMMACDDISPLAY'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_MMACD_DISPLAYSWITCH",      atmEta_gui_Generals.switch_typeB,                   {'groupOrder': 0, 'xPos': 1600, 'yPos': 7200, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACDSHORT_DisplaySwitch_MMACD', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_MMACD_COLORTEXT",          atmEta_gui_Generals.textBox_typeA,                  {'groupOrder': 0, 'xPos': 2200, 'yPos': 7200, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_MMACD_COLOR",              atmEta_gui_Generals.LED_typeA,                      {'groupOrder': 0, 'xPos': 2900, 'yPos': 7200, 'width':                  1100, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_SIGNAL_DISPLAYTEXT",       atmEta_gui_Generals.textBox_typeA,                  {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNALDISPLAY'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_SIGNAL_DISPLAYSWITCH",     atmEta_gui_Generals.switch_typeB,                   {'groupOrder': 0, 'xPos': 1600, 'yPos': 6850, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACDSHORT_DisplaySwitch_SIGNAL', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_SIGNAL_COLORTEXT",         atmEta_gui_Generals.textBox_typeA,                  {'groupOrder': 0, 'xPos': 2200, 'yPos': 6850, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_SIGNAL_COLOR",             atmEta_gui_Generals.LED_typeA,                      {'groupOrder': 0, 'xPos': 2900, 'yPos': 6850, 'width':                  1100, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_HISTOGRAM_DISPLAYTEXT",    atmEta_gui_Generals.textBox_typeA,                  {'groupOrder': 0, 'xPos':    0, 'yPos': 6500, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAMDISPLAY'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_HISTOGRAM_DISPLAYSWITCH",  atmEta_gui_Generals.switch_typeB,                   {'groupOrder': 0, 'xPos': 1600, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACDSHORT_DisplaySwitch_HISTOGRAM', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_HISTOGRAM_COLORTEXT",      atmEta_gui_Generals.textBox_typeA,                  {'groupOrder': 0, 'xPos': 2200, 'yPos': 6500, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_HISTOGRAM+_COLOR",         atmEta_gui_Generals.LED_typeA,                      {'groupOrder': 0, 'xPos': 2900, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_HISTOGRAM-_COLOR",         atmEta_gui_Generals.LED_typeA,                      {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_BLOCKTITLE_MMACDSETTINGS",   atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6150, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSETTINGS'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATOR_SIGNALINTERVALTEXT",         atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 5800, 'width':                  3000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNALINTERVAL'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_SIGNALINTERVALTEXTINPUT",    atmEta_gui_Generals.textInputBox_typeA,           {'groupOrder': 0, 'xPos': 3100, 'yPos': 5800, 'width':                   900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MMACDSHORT_SignalIntervalTextInputBox', 'textUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_MULTIPLIERTEXT",             atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 5450, 'width':                  3000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MULTIPLIER'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_MULTIPLIERTEXTINPUT",        atmEta_gui_Generals.textInputBox_typeA,           {'groupOrder': 0, 'xPos': 3100, 'yPos': 5450, 'width':                   900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MMACDSHORT_MultiplierTextInputBox', 'textUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE1",          atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 5100, 'width':                  1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE1",       atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 5100, 'width':                   850, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE2",          atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2050, 'yPos': 5100, 'width':                  1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE2",       atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3150, 'yPos': 5100, 'width':                   850, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            for lineIndex in range (_NMAXLINES['MMACDSHORT']):
                rowNumber = math.ceil((lineIndex+1)/2)
                if (lineIndex%2 == 0): coordX = 0
                else:                  coordX = 2050
                ssp.addGUIO(f"INDICATOR_MMACDMA{lineIndex}",               atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos': coordX,      'yPos': 5100-rowNumber*350, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'MMACDSHORT_LineActivationSwitch_{lineIndex}', 'text': f'MA {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT", atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': coordX+1100, 'yPos': 5100-rowNumber*350, 'width':  850, 'height': 250, 'style': 'styleA', 'name': f'MMACDSHORT_IntervalTextInputBox_{lineIndex}', 'text': "",                'fontSize': 80, 'textUpdateFunction': self.__onSettingsContentUpdate})
            yPosPoint0 = 5100-math.ceil(_NMAXLINES['MMACDSHORT']/2)*350
            ssp.addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'MMACDSHORT_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
        #<MMACDLONG Settings>
        if (True):
            ssp = self.settingsSubPages['MMACDLONG']
            ssp.addGUIO("SUBPAGETITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_MMACDLONG'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",    atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':                   550, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width':                  1500, 'height': 250, 'style': 'styleA', 'name': 'MMACDLONG_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':                   950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':                   650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'MMACDLONG_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'MMACDLONG_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            mmacdLineTargets = {'MMACD':      {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDMMACD')},
                                'SIGNAL':     {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNAL')},
                                'HISTOGRAM+': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAM+')},
                                'HISTOGRAM-': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAM-')}}
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = mmacdLineTargets, displayTargets = 'all')
            ssp.addGUIO("INDICATOR_BLOCKTITLE_DISPLAY",       atmEta_gui_Generals.passiveGraphics_wrapperTypeC,   {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDDISPLAY'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATOR_MMACD_DISPLAYTEXT",        atmEta_gui_Generals.textBox_typeA,                  {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDMMACDDISPLAY'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_MMACD_DISPLAYSWITCH",      atmEta_gui_Generals.switch_typeB,                   {'groupOrder': 0, 'xPos': 1600, 'yPos': 7200, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACDLONG_DisplaySwitch_MMACD', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_MMACD_COLORTEXT",          atmEta_gui_Generals.textBox_typeA,                  {'groupOrder': 0, 'xPos': 2200, 'yPos': 7200, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_MMACD_COLOR",              atmEta_gui_Generals.LED_typeA,                      {'groupOrder': 0, 'xPos': 2900, 'yPos': 7200, 'width':                  1100, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_SIGNAL_DISPLAYTEXT",       atmEta_gui_Generals.textBox_typeA,                  {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNALDISPLAY'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_SIGNAL_DISPLAYSWITCH",     atmEta_gui_Generals.switch_typeB,                   {'groupOrder': 0, 'xPos': 1600, 'yPos': 6850, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACDLONG_DisplaySwitch_SIGNAL', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_SIGNAL_COLORTEXT",         atmEta_gui_Generals.textBox_typeA,                  {'groupOrder': 0, 'xPos': 2200, 'yPos': 6850, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_SIGNAL_COLOR",             atmEta_gui_Generals.LED_typeA,                      {'groupOrder': 0, 'xPos': 2900, 'yPos': 6850, 'width':                  1100, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_HISTOGRAM_DISPLAYTEXT",    atmEta_gui_Generals.textBox_typeA,                  {'groupOrder': 0, 'xPos':    0, 'yPos': 6500, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAMDISPLAY'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_HISTOGRAM_DISPLAYSWITCH",  atmEta_gui_Generals.switch_typeB,                   {'groupOrder': 0, 'xPos': 1600, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACDLONG_DisplaySwitch_HISTOGRAM', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_HISTOGRAM_COLORTEXT",      atmEta_gui_Generals.textBox_typeA,                  {'groupOrder': 0, 'xPos': 2200, 'yPos': 6500, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_HISTOGRAM+_COLOR",         atmEta_gui_Generals.LED_typeA,                      {'groupOrder': 0, 'xPos': 2900, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_HISTOGRAM-_COLOR",         atmEta_gui_Generals.LED_typeA,                      {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_BLOCKTITLE_MMACDSETTINGS",   atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6150, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSETTINGS'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATOR_SIGNALINTERVALTEXT",         atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 5800, 'width':                  3000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNALINTERVAL'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_SIGNALINTERVALTEXTINPUT",    atmEta_gui_Generals.textInputBox_typeA,           {'groupOrder': 0, 'xPos': 3100, 'yPos': 5800, 'width':                   900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MMACDLONG_SignalIntervalTextInputBox', 'textUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_MULTIPLIERTEXT",             atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 5450, 'width':                  3000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MULTIPLIER'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_MULTIPLIERTEXTINPUT",        atmEta_gui_Generals.textInputBox_typeA,           {'groupOrder': 0, 'xPos': 3100, 'yPos': 5450, 'width':                   900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MMACDLONG_MultiplierTextInputBox', 'textUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE1",          atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 5100, 'width':                  1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE1",       atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 5100, 'width':                   850, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE2",          atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2050, 'yPos': 5100, 'width':                  1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE2",       atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3150, 'yPos': 5100, 'width':                   850, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            for lineIndex in range (_NMAXLINES['MMACDLONG']):
                rowNumber = math.ceil((lineIndex+1)/2)
                if (lineIndex%2 == 0): coordX = 0
                else:                  coordX = 2050
                ssp.addGUIO(f"INDICATOR_MMACDMA{lineIndex}",               atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos': coordX,      'yPos': 5100-rowNumber*350, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'MMACDLONG_LineActivationSwitch_{lineIndex}', 'text': f'MA {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT", atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': coordX+1100, 'yPos': 5100-rowNumber*350, 'width':  850, 'height': 250, 'style': 'styleA', 'name': f'MMACDLONG_IntervalTextInputBox_{lineIndex}', 'text': "",                'fontSize': 80, 'textUpdateFunction': self.__onSettingsContentUpdate})
            yPosPoint0 = 5100-math.ceil(_NMAXLINES['MMACDLONG']/2)*350
            ssp.addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'MMACDLONG_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
        #<DMIxADX Settings>
        if (True):
            ssp = self.settingsSubPages['DMIxADX']
            ssp.addGUIO("SUBPAGETITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_DMIxADX'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",        atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'DMIxADX_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'DMIxADX_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'DMIxADX_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 1200, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1300, 'yPos': 7550, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2000, 'yPos': 7550, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2700, 'yPos': 7550, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",  atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
            dmixadxList = dict()
            for lineIndex in range (_NMAXLINES['DMIxADX']):
                ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}",               atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*lineIndex, 'width': 1200, 'height': 250, 'style': 'styleB', 'name': f'DMIxADX_LineActivationSwitch_{lineIndex}', 'text': f'DMIxADX {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT", atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1300, 'yPos': 7200-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'name': f'DMIxADX_IntervalTextInputBox_{lineIndex}', 'text': "",                     'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT",    atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2000, 'yPos': 7200-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'name': f'DMIxADX_WidthTextInputBox_{lineIndex}',    'text': "",                     'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}_LINECOLOR",     atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2700, 'yPos': 7200-350*lineIndex, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
                ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}_DISPLAY",       atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'DMIxADX_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
                dmixadxList[f"{lineIndex}"] = {'text': f"DMIxADX {lineIndex}"}
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = dmixadxList, displayTargets = 'all')
            yPosPoint0 = 7200-350*(_NMAXLINES['DMIxADX']-1)
            ssp.addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'DMIxADX_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
        #<MFI Settings>
        if (True):
            ssp = self.settingsSubPages['MFI']
            ssp.addGUIO("SUBPAGETITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_MFI'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",        atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'MFI_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'MFI_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'MFI_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 7550, 'width':  800, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2000, 'yPos': 7550, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2700, 'yPos': 7550, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",  atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
            mfiList = dict()
            for lineIndex in range (_NMAXLINES['MFI']):
                ssp.addGUIO(f"INDICATOR_MFI{lineIndex}",               atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'MFI_LineActivationSwitch_{lineIndex}', 'text': f'MFI {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_MFI{lineIndex}_INTERVALINPUT", atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': 7200-350*lineIndex, 'width':  800, 'height': 250, 'style': 'styleA', 'name': f'MFI_IntervalTextInputBox_{lineIndex}', 'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_MFI{lineIndex}_WIDTHINPUT",    atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2000, 'yPos': 7200-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'name': f'MFI_WidthTextInputBox_{lineIndex}',    'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_MFI{lineIndex}_LINECOLOR",     atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2700, 'yPos': 7200-350*lineIndex, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
                ssp.addGUIO(f"INDICATOR_MFI{lineIndex}_DISPLAY",       atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'MFI_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
                mfiList[f"{lineIndex}"] = {'text': f"MFI {lineIndex}"}
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = mfiList, displayTargets = 'all')
            yPosPoint0 = 7200-350*(_NMAXLINES['MFI']-1)
            ssp.addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'MFI_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
        #<WOI Settings>
        if (True):
            ssp = self.settingsSubPages['WOI']
            ssp.addGUIO("SUBPAGETITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_WOI'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",        atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'WOI_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'WOI_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'WOI_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ssp.addGUIO("INDICATOR_BLOCKTITLE_WOIBASE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WOIBASE'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATOR_DISPLAYWOIBASE_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width': 1600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WOIBASEDISPLAY'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_WOIBASE_DISPLAYSWITCH", atmEta_gui_Generals.switch_typeB,  {'groupOrder': 0, 'xPos': 1700, 'yPos': 7200, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'WOI_DisplaySwitch_WOIBase', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_WOIBASE+_LINECOLOR",    atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 2300, 'yPos': 7200, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_WOIBASE-_LINECOLOR",    atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3200, 'yPos': 7200, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_BLOCKTITLE_WOIGAUSSIANDELTA", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': 6850, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WOIGAUSSIANDELTA'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6550, 'width': 700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  800, 'yPos': 6550, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORSIGMA_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1500, 'yPos': 6550, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SIGMA'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2200, 'yPos': 6550, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2900, 'yPos': 6550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",  atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
            NESList = {'BASE+': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BASE+')},
                       'BASE-': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BASE-')}}
            for lineIndex in range (_NMAXLINES['WOI']):
                ssp.addGUIO(f"INDICATOR_WOI{lineIndex}",               atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6200-350*lineIndex, 'width': 700, 'height': 250, 'style': 'styleB', 'name': f'WOI_LineActivationSwitch_{lineIndex}', 'text': f'WOI {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_WOI{lineIndex}_INTERVALINPUT", atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  800, 'yPos': 6200-350*lineIndex, 'width': 600, 'height': 250, 'style': 'styleA', 'name': f'WOI_IntervalTextInputBox_{lineIndex}', 'text': "",                 'fontSize': 80, 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_WOI{lineIndex}_SIGMAINPUT",    atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1500, 'yPos': 6200-350*lineIndex, 'width': 600, 'height': 250, 'style': 'styleA', 'name': f'WOI_SigmaTextInputBox_{lineIndex}',    'text': "",                 'fontSize': 80, 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_WOI{lineIndex}_WIDTHINPUT",    atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2200, 'yPos': 6200-350*lineIndex, 'width': 600, 'height': 250, 'style': 'styleA', 'name': f'WOI_WidthTextInputBox_{lineIndex}',    'text': "",                 'fontSize': 80, 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_WOI{lineIndex}_LINECOLOR",     atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2900, 'yPos': 6200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'mode': True})
                ssp.addGUIO(f"INDICATOR_WOI{lineIndex}_DISPLAY",       atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'WOI_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
                NESList[f"{lineIndex}"] = {'text': f"WOI {lineIndex}"}
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = NESList, displayTargets = 'all')
            yPosPoint0 = 6200-350*(_NMAXLINES['WOI']-1)
            ssp.addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'WOI_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
        #<NES Settings>
        if (True):
            ssp = self.settingsSubPages['NES']
            ssp.addGUIO("SUBPAGETITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_NES'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",        atmEta_gui_Generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'NES_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'NES_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'NES_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ssp.addGUIO("INDICATOR_BLOCKTITLE_NESBASE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:NESBASE'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATOR_DISPLAYNESBASE_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width': 1600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:NESBASEDISPLAY'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_NESBASE_DISPLAYSWITCH", atmEta_gui_Generals.switch_typeB,  {'groupOrder': 0, 'xPos': 1700, 'yPos': 7200, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'NES_DisplaySwitch_NESBase', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_NESBASE+_LINECOLOR",    atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 2300, 'yPos': 7200, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_NESBASE-_LINECOLOR",    atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3200, 'yPos': 7200, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_BLOCKTITLE_NESGAUSSIANDELTA", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': 6850, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:NESGAUSSIANDELTA'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6550, 'width': 700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE", atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  800, 'yPos': 6550, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORSIGMA_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1500, 'yPos': 6550, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SIGMA'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2200, 'yPos': 6550, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",    atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2900, 'yPos': 6550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",  atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
            NESList = {'BASE+': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BASE+')},
                       'BASE-': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BASE-')}}
            for lineIndex in range (_NMAXLINES['NES']):
                ssp.addGUIO(f"INDICATOR_NES{lineIndex}",               atmEta_gui_Generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6200-350*lineIndex, 'width': 700, 'height': 250, 'style': 'styleB', 'name': f'NES_LineActivationSwitch_{lineIndex}', 'text': f'NES {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_NES{lineIndex}_INTERVALINPUT", atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  800, 'yPos': 6200-350*lineIndex, 'width': 600, 'height': 250, 'style': 'styleA', 'name': f'NES_IntervalTextInputBox_{lineIndex}', 'text': "",                 'fontSize': 80, 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_NES{lineIndex}_SIGMAINPUT",    atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1500, 'yPos': 6200-350*lineIndex, 'width': 600, 'height': 250, 'style': 'styleA', 'name': f'NES_SigmaTextInputBox_{lineIndex}',    'text': "",                 'fontSize': 80, 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_NES{lineIndex}_WIDTHINPUT",    atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2200, 'yPos': 6200-350*lineIndex, 'width': 600, 'height': 250, 'style': 'styleA', 'name': f'NES_WidthTextInputBox_{lineIndex}',    'text': "",                 'fontSize': 80, 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_NES{lineIndex}_LINECOLOR",     atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2900, 'yPos': 6200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'mode': True})
                ssp.addGUIO(f"INDICATOR_NES{lineIndex}_DISPLAY",       atmEta_gui_Generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'NES_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
                NESList[f"{lineIndex}"] = {'text': f"NES {lineIndex}"}
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = NESList, displayTargets = 'all')
            yPosPoint0 = 6200-350*(_NMAXLINES['NES']-1)
            ssp.addGUIO("APPLYNEWSETTINGS", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'NES_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})

    def __initializeObjectConfig(self):
        #---Default Object Configuration
        oc = dict()
        #--- MAIN Config
        for siViewerIndex in range (len(_SITYPES)): 
            oc[f'SIVIEWER{siViewerIndex}Display'] = False
            oc[f'SIVIEWER{siViewerIndex}SIAlloc'] = _SITYPES[siViewerIndex]
        oc['TimeZone']       = 'LOCAL'
        oc['KlineColorType'] = 1
        oc['AnalysisRangeBeg'] = None
        oc['AnalysisRangeEnd'] = None
        oc['TRADELOG_Display'] = True
        oc['TRADELOG_BUY_ColorR%DARK']  =100; oc['TRADELOG_BUY_ColorG%DARK']  =255; oc['TRADELOG_BUY_ColorB%DARK']  =180; oc['TRADELOG_BUY_ColorA%DARK']  =120
        oc['TRADELOG_BUY_ColorR%LIGHT'] = 80; oc['TRADELOG_BUY_ColorG%LIGHT'] =200; oc['TRADELOG_BUY_ColorB%LIGHT'] =150; oc['TRADELOG_BUY_ColorA%LIGHT'] =120
        oc['TRADELOG_SELL_ColorR%DARK'] =255; oc['TRADELOG_SELL_ColorG%DARK'] =100; oc['TRADELOG_SELL_ColorB%DARK'] =100; oc['TRADELOG_SELL_ColorA%DARK'] =120
        oc['TRADELOG_SELL_ColorR%LIGHT']=240; oc['TRADELOG_SELL_ColorG%LIGHT']= 80; oc['TRADELOG_SELL_ColorB%LIGHT']= 80; oc['TRADELOG_SELL_ColorA%LIGHT']=120
        oc['BIDSANDASKS_Display'] = True
        oc['BIDSANDASKS_BIDS_ColorR%DARK'] =100; oc['BIDSANDASKS_BIDS_ColorG%DARK'] =255; oc['BIDSANDASKS_BIDS_ColorB%DARK'] =180; oc['BIDSANDASKS_BIDS_ColorA%DARK'] =120
        oc['BIDSANDASKS_BIDS_ColorR%LIGHT']= 80; oc['BIDSANDASKS_BIDS_ColorG%LIGHT']=200; oc['BIDSANDASKS_BIDS_ColorB%LIGHT']=150; oc['BIDSANDASKS_BIDS_ColorA%LIGHT']=120
        oc['BIDSANDASKS_ASKS_ColorR%DARK'] =255; oc['BIDSANDASKS_ASKS_ColorG%DARK'] =100; oc['BIDSANDASKS_ASKS_ColorB%DARK'] =100; oc['BIDSANDASKS_ASKS_ColorA%DARK'] =120
        oc['BIDSANDASKS_ASKS_ColorR%LIGHT']=240; oc['BIDSANDASKS_ASKS_ColorG%LIGHT']= 80; oc['BIDSANDASKS_ASKS_ColorB%LIGHT']= 80; oc['BIDSANDASKS_ASKS_ColorA%LIGHT']=120
        #--- SMA Config
        oc['SMA_Master'] = False
        for lineIndex in range (_NMAXLINES['SMA']):
            oc[f'SMA_{lineIndex}_LineActive'] = False
            oc[f'SMA_{lineIndex}_NSamples']   = 10*(lineIndex+1)
            oc[f'SMA_{lineIndex}_Width'] = 1
            oc[f'SMA_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'SMA_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'SMA_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'SMA_{lineIndex}_ColorA%DARK'] =255
            oc[f'SMA_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'SMA_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'SMA_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'SMA_{lineIndex}_ColorA%LIGHT']=255
            oc[f'SMA_{lineIndex}_Display'] = True
        #--- WMA Config
        oc['WMA_Master'] = False
        for lineIndex in range (_NMAXLINES['WMA']):
            oc[f'WMA_{lineIndex}_LineActive'] = False
            oc[f'WMA_{lineIndex}_NSamples']   = 10*(lineIndex+1)
            oc[f'WMA_{lineIndex}_Width'] = 1
            oc[f'WMA_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'WMA_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'WMA_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'WMA_{lineIndex}_ColorA%DARK'] =255
            oc[f'WMA_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'WMA_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'WMA_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'WMA_{lineIndex}_ColorA%LIGHT']=255
            oc[f'WMA_{lineIndex}_Display'] = True
        #--- EMA Config
        oc['EMA_Master'] = False
        for lineIndex in range (_NMAXLINES['EMA']):
            oc[f'EMA_{lineIndex}_LineActive'] = False
            oc[f'EMA_{lineIndex}_NSamples']   = 10*(lineIndex+1)
            oc[f'EMA_{lineIndex}_Width'] = 1
            oc[f'EMA_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'EMA_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'EMA_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'EMA_{lineIndex}_ColorA%DARK'] =255
            oc[f'EMA_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'EMA_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'EMA_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'EMA_{lineIndex}_ColorA%LIGHT']=255
            oc[f'EMA_{lineIndex}_Display'] = True
        #--- PSAR Config
        oc['PSAR_Master'] = False
        for lineIndex in range (_NMAXLINES['PSAR']):
            oc[f'PSAR_{lineIndex}_LineActive'] = False
            oc[f'PSAR_{lineIndex}_AF0']   = 0.020
            oc[f'PSAR_{lineIndex}_AF+']   = 0.005*(lineIndex+1)
            oc[f'PSAR_{lineIndex}_AFMax'] = 0.200
            oc[f'PSAR_{lineIndex}_Width'] = 1
            oc[f'PSAR_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'PSAR_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'PSAR_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'PSAR_{lineIndex}_ColorA%DARK'] =255
            oc[f'PSAR_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'PSAR_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'PSAR_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'PSAR_{lineIndex}_ColorA%LIGHT']=255
            oc[f'PSAR_{lineIndex}_Display'] = True
        #--- BOL Config
        oc['BOL_Master'] = False
        for lineIndex in range (_NMAXLINES['BOL']):
            oc[f'BOL_{lineIndex}_LineActive'] = False
            oc[f'BOL_{lineIndex}_NSamples']  = 10*(lineIndex+1)
            oc[f'BOL_{lineIndex}_BandWidth'] = 2.0
            oc[f'BOL_{lineIndex}_Width'] = 1
            oc[f'BOL_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'BOL_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'BOL_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'BOL_{lineIndex}_ColorA%DARK'] =30
            oc[f'BOL_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'BOL_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'BOL_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'BOL_{lineIndex}_ColorA%LIGHT']=30
            oc[f'BOL_{lineIndex}_Display'] = True
        oc['BOL_MAType']            = 'SMA'
        oc['BOL_DisplayCenterLine'] = True
        oc['BOL_DisplayBand']       = True
        #--- IVP Config
        oc['IVP_Master'] = False
        oc['IVP_NSamples']    = 288
        oc['IVP_GammaFactor'] = 0.010 #0.005 ~ 0.100
        oc['IVP_DeltaFactor'] = 1.0   #0.1   ~ 10.0
        oc['IVP_VPLP_Display']      = True
        oc['IVP_VPLP_DisplayWidth'] = 0.2
        oc['IVP_VPLP_ColorR%DARK']  = random.randint(64,255); oc['IVP_VPLP_ColorG%DARK']  = random.randint(64,255); oc['IVP_VPLP_ColorB%DARK']  = random.randint(64,255); oc['IVP_VPLP_ColorA%DARK']  = 30
        oc['IVP_VPLP_ColorR%LIGHT'] = random.randint(64,255); oc['IVP_VPLP_ColorG%LIGHT'] = random.randint(64,255); oc['IVP_VPLP_ColorB%LIGHT'] = random.randint(64,255); oc['IVP_VPLP_ColorA%LIGHT'] = 30
        oc['IVP_VPLPB_Display'] = True
        oc['IVP_VPLPB_ColorR%DARK']  = random.randint(64,255); oc['IVP_VPLPB_ColorG%DARK']  = random.randint(64,255); oc['IVP_VPLPB_ColorB%DARK']  = random.randint(64,255); oc['IVP_VPLPB_ColorA%DARK']  = 150
        oc['IVP_VPLPB_ColorR%LIGHT'] = random.randint(64,255); oc['IVP_VPLPB_ColorG%LIGHT'] = random.randint(64,255); oc['IVP_VPLPB_ColorB%LIGHT'] = random.randint(64,255); oc['IVP_VPLPB_ColorA%LIGHT'] = 150
        oc['IVP_VPLPB_DisplayRegion'] = 0.100
        #--- SWING Config
        oc['SWING_Master'] = False
        for lineIndex in range (_NMAXLINES['SWING']):
            oc[f'SWING_{lineIndex}_LineActive'] = False
            oc[f'SWING_{lineIndex}_SwingRange'] = 0.005*(lineIndex+1)
            oc[f'SWING_{lineIndex}_Width'] = 1
            oc[f'SWING_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'SWING_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'SWING_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'SWING_{lineIndex}_ColorA%DARK'] =30
            oc[f'SWING_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'SWING_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'SWING_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'SWING_{lineIndex}_ColorA%LIGHT']=30
            oc[f'SWING_{lineIndex}_Display'] = True
        #---VOL Config
        oc['VOL_Master'] = False
        for lineIndex in range (_NMAXLINES['VOL']):
            oc[f'VOL_{lineIndex}_LineActive'] = False
            oc[f'VOL_{lineIndex}_NSamples'] = 10*(lineIndex+1)
            oc[f'VOL_{lineIndex}_Width'] = 1
            oc[f'VOL_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'VOL_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'VOL_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'VOL_{lineIndex}_ColorA%DARK'] =255
            oc[f'VOL_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'VOL_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'VOL_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'VOL_{lineIndex}_ColorA%LIGHT']=255
            oc[f'VOL_{lineIndex}_Display'] = True
        oc['VOL_VolumeType'] = 'BASE'
        oc['VOL_MAType']     = 'SMA'
        #---NNA Config
        oc['NNA_Master'] = False
        for lineIndex in range (_NMAXLINES['NNA']):
            oc[f'NNA_{lineIndex}_LineActive'] = False
            oc[f'NNA_{lineIndex}_NeuralNetworkCode'] = None
            oc[f'NNA_{lineIndex}_Alpha']             = 0.50
            oc[f'NNA_{lineIndex}_Beta']              = 2
            oc[f'NNA_{lineIndex}_Width'] = 1
            oc[f'NNA_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'NNA_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'NNA_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'NNA_{lineIndex}_ColorA%DARK'] =255
            oc[f'NNA_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'NNA_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'NNA_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'NNA_{lineIndex}_ColorA%LIGHT']=255
            oc[f'NNA_{lineIndex}_Display'] = True
        #---MMACDSHORT Config
        oc['MMACDSHORT_Master'] = False
        oc['MMACDSHORT_SignalNSamples']    = 10
        oc['MMACDSHORT_Multiplier']        = 12
        oc['MMACDSHORT_MMACD_Display']     = True
        oc['MMACDSHORT_SIGNAL_Display']    = True
        oc['MMACDSHORT_HISTOGRAM_Display'] = True
        oc['MMACDSHORT_MMACD_ColorR%DARK']   = random.randint(64,255); oc['MMACDSHORT_MMACD_ColorG%DARK']   = random.randint(64,255); oc['MMACDSHORT_MMACD_ColorB%DARK']   = random.randint(64,255); oc['MMACDSHORT_MMACD_ColorA%DARK']   = 255
        oc['MMACDSHORT_MMACD_ColorR%LIGHT']  = random.randint(64,255); oc['MMACDSHORT_MMACD_ColorG%LIGHT']  = random.randint(64,255); oc['MMACDSHORT_MMACD_ColorB%LIGHT']  = random.randint(64,255); oc['MMACDSHORT_MMACD_ColorA%LIGHT']  = 255
        oc['MMACDSHORT_SIGNAL_ColorR%DARK']  = random.randint(64,255); oc['MMACDSHORT_SIGNAL_ColorG%DARK']  = random.randint(64,255); oc['MMACDSHORT_SIGNAL_ColorB%DARK']  = random.randint(64,255); oc['MMACDSHORT_SIGNAL_ColorA%DARK']  = 255
        oc['MMACDSHORT_SIGNAL_ColorR%LIGHT'] = random.randint(64,255); oc['MMACDSHORT_SIGNAL_ColorG%LIGHT'] = random.randint(64,255); oc['MMACDSHORT_SIGNAL_ColorB%LIGHT'] = random.randint(64,255); oc['MMACDSHORT_SIGNAL_ColorA%LIGHT'] = 255
        oc['MMACDSHORT_HISTOGRAM+_ColorR%DARK']  = 100; oc['MMACDSHORT_HISTOGRAM+_ColorG%DARK']  = 255; oc['MMACDSHORT_HISTOGRAM+_ColorB%DARK']  = 180; oc['MMACDSHORT_HISTOGRAM+_ColorA%DARK']  = 255
        oc['MMACDSHORT_HISTOGRAM+_ColorR%LIGHT'] =  80; oc['MMACDSHORT_HISTOGRAM+_ColorG%LIGHT'] = 200; oc['MMACDSHORT_HISTOGRAM+_ColorB%LIGHT'] = 150; oc['MMACDSHORT_HISTOGRAM+_ColorA%LIGHT'] = 255
        oc['MMACDSHORT_HISTOGRAM-_ColorR%DARK']  = 255; oc['MMACDSHORT_HISTOGRAM-_ColorG%DARK']  = 100; oc['MMACDSHORT_HISTOGRAM-_ColorB%DARK']  = 100; oc['MMACDSHORT_HISTOGRAM-_ColorA%DARK']  = 255
        oc['MMACDSHORT_HISTOGRAM-_ColorR%LIGHT'] = 240; oc['MMACDSHORT_HISTOGRAM-_ColorG%LIGHT'] =  80; oc['MMACDSHORT_HISTOGRAM-_ColorB%LIGHT'] =  80; oc['MMACDSHORT_HISTOGRAM-_ColorA%LIGHT'] = 255
        for lineIndex in range (_NMAXLINES['MMACDSHORT']):
            oc[f'MMACDSHORT_MA{lineIndex}_LineActive'] = False
            oc[f'MMACDSHORT_MA{lineIndex}_NSamples']   = 20*(lineIndex+1)
        #---MMACDLONG Config
        oc['MMACDLONG_Master'] = False
        oc['MMACDLONG_SignalNSamples']    = 10
        oc['MMACDLONG_Multiplier']        = 48
        oc['MMACDLONG_MMACD_Display']     = True
        oc['MMACDLONG_SIGNAL_Display']    = True
        oc['MMACDLONG_HISTOGRAM_Display'] = True
        oc['MMACDLONG_MMACD_ColorR%DARK']   = random.randint(64,255); oc['MMACDLONG_MMACD_ColorG%DARK']   = random.randint(64,255); oc['MMACDLONG_MMACD_ColorB%DARK']   = random.randint(64,255); oc['MMACDLONG_MMACD_ColorA%DARK']   = 255
        oc['MMACDLONG_MMACD_ColorR%LIGHT']  = random.randint(64,255); oc['MMACDLONG_MMACD_ColorG%LIGHT']  = random.randint(64,255); oc['MMACDLONG_MMACD_ColorB%LIGHT']  = random.randint(64,255); oc['MMACDLONG_MMACD_ColorA%LIGHT']  = 255
        oc['MMACDLONG_SIGNAL_ColorR%DARK']  = random.randint(64,255); oc['MMACDLONG_SIGNAL_ColorG%DARK']  = random.randint(64,255); oc['MMACDLONG_SIGNAL_ColorB%DARK']  = random.randint(64,255); oc['MMACDLONG_SIGNAL_ColorA%DARK']  = 255
        oc['MMACDLONG_SIGNAL_ColorR%LIGHT'] = random.randint(64,255); oc['MMACDLONG_SIGNAL_ColorG%LIGHT'] = random.randint(64,255); oc['MMACDLONG_SIGNAL_ColorB%LIGHT'] = random.randint(64,255); oc['MMACDLONG_SIGNAL_ColorA%LIGHT'] = 255
        oc['MMACDLONG_HISTOGRAM+_ColorR%DARK']  = 100; oc['MMACDLONG_HISTOGRAM+_ColorG%DARK']  = 255; oc['MMACDLONG_HISTOGRAM+_ColorB%DARK']  = 180; oc['MMACDLONG_HISTOGRAM+_ColorA%DARK']  = 255
        oc['MMACDLONG_HISTOGRAM+_ColorR%LIGHT'] =  80; oc['MMACDLONG_HISTOGRAM+_ColorG%LIGHT'] = 200; oc['MMACDLONG_HISTOGRAM+_ColorB%LIGHT'] = 150; oc['MMACDLONG_HISTOGRAM+_ColorA%LIGHT'] = 255
        oc['MMACDLONG_HISTOGRAM-_ColorR%DARK']  = 255; oc['MMACDLONG_HISTOGRAM-_ColorG%DARK']  = 100; oc['MMACDLONG_HISTOGRAM-_ColorB%DARK']  = 100; oc['MMACDLONG_HISTOGRAM-_ColorA%DARK']  = 255
        oc['MMACDLONG_HISTOGRAM-_ColorR%LIGHT'] = 240; oc['MMACDLONG_HISTOGRAM-_ColorG%LIGHT'] =  80; oc['MMACDLONG_HISTOGRAM-_ColorB%LIGHT'] =  80; oc['MMACDLONG_HISTOGRAM-_ColorA%LIGHT'] = 255
        for lineIndex in range (_NMAXLINES['MMACDLONG']):
            oc[f'MMACDLONG_MA{lineIndex}_LineActive'] = False
            oc[f'MMACDLONG_MA{lineIndex}_NSamples']   = 20*(lineIndex+1)
        #---DMIxADX Config
        oc['DMIxADX_Master'] = False
        for lineIndex in range (_NMAXLINES['DMIxADX']):
            oc[f'DMIxADX_{lineIndex}_LineActive'] = False
            oc[f'DMIxADX_{lineIndex}_NSamples']   = 10*(lineIndex+1)
            oc[f'DMIxADX_{lineIndex}_Width'] = 1
            oc[f'DMIxADX_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'DMIxADX_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'DMIxADX_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'DMIxADX_{lineIndex}_ColorA%DARK'] =255
            oc[f'DMIxADX_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'DMIxADX_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'DMIxADX_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'DMIxADX_{lineIndex}_ColorA%LIGHT']=255
            oc[f'DMIxADX_{lineIndex}_Display'] = True
        #---MFI Config
        oc['MFI_Master'] = False
        for lineIndex in range (_NMAXLINES['MFI']):
            oc[f'MFI_{lineIndex}_LineActive'] = False
            oc[f'MFI_{lineIndex}_NSamples']   = 10*(lineIndex+1)
            oc[f'MFI_{lineIndex}_Width'] = 1
            oc[f'MFI_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'MFI_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'MFI_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'MFI_{lineIndex}_ColorA%DARK'] =255
            oc[f'MFI_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'MFI_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'MFI_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'MFI_{lineIndex}_ColorA%LIGHT']=255
            oc[f'MFI_{lineIndex}_Display'] = True
        #---WOI Config
        oc['WOI_Master'] = False
        oc['WOI_BASE_Display'] = True
        oc['WOI_BASE+_ColorR%DARK']  = 100; oc['WOI_BASE+_ColorG%DARK']  = 255; oc['WOI_BASE+_ColorB%DARK']  = 180; oc['WOI_BASE+_ColorA%DARK']  = 180
        oc['WOI_BASE+_ColorR%LIGHT'] =  80; oc['WOI_BASE+_ColorG%LIGHT'] = 200; oc['WOI_BASE+_ColorB%LIGHT'] = 150; oc['WOI_BASE+_ColorA%LIGHT'] = 180
        oc['WOI_BASE-_ColorR%DARK']  = 255; oc['WOI_BASE-_ColorG%DARK']  = 100; oc['WOI_BASE-_ColorB%DARK']  = 100; oc['WOI_BASE-_ColorA%DARK']  = 180
        oc['WOI_BASE-_ColorR%LIGHT'] = 240; oc['WOI_BASE-_ColorG%LIGHT'] =  80; oc['WOI_BASE-_ColorB%LIGHT'] =  80; oc['WOI_BASE-_ColorA%LIGHT'] = 180
        for lineIndex in range (_NMAXLINES['WOI']):
            oc[f'WOI_{lineIndex}_LineActive'] = False
            oc[f'WOI_{lineIndex}_NSamples']   = 10*(lineIndex+1)
            oc[f'WOI_{lineIndex}_Sigma']      = round(2.5*(lineIndex+1), 1)
            oc[f'WOI_{lineIndex}_Width'] = 1
            oc[f'WOI_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'WOI_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'WOI_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'WOI_{lineIndex}_ColorA%DARK'] =255
            oc[f'WOI_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'WOI_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'WOI_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'WOI_{lineIndex}_ColorA%LIGHT']=255
            oc[f'WOI_{lineIndex}_Display'] = True
        #---NES Config
        oc['NES_Master'] = False
        oc['NES_BASE_Display'] = True
        oc['NES_BASE+_ColorR%DARK']  = 100; oc['NES_BASE+_ColorG%DARK']  = 255; oc['NES_BASE+_ColorB%DARK']  = 180; oc['NES_BASE+_ColorA%DARK']  = 180
        oc['NES_BASE+_ColorR%LIGHT'] =  80; oc['NES_BASE+_ColorG%LIGHT'] = 200; oc['NES_BASE+_ColorB%LIGHT'] = 150; oc['NES_BASE+_ColorA%LIGHT'] = 180
        oc['NES_BASE-_ColorR%DARK']  = 255; oc['NES_BASE-_ColorG%DARK']  = 100; oc['NES_BASE-_ColorB%DARK']  = 100; oc['NES_BASE-_ColorA%DARK']  = 180
        oc['NES_BASE-_ColorR%LIGHT'] = 240; oc['NES_BASE-_ColorG%LIGHT'] =  80; oc['NES_BASE-_ColorB%LIGHT'] =  80; oc['NES_BASE-_ColorA%LIGHT'] = 180
        for lineIndex in range (_NMAXLINES['NES']):
            oc[f'NES_{lineIndex}_LineActive'] = False
            oc[f'NES_{lineIndex}_NSamples']   = 10*(lineIndex+1)
            oc[f'NES_{lineIndex}_Sigma']      = round(2.5*(lineIndex+1), 1)
            oc[f'NES_{lineIndex}_Width'] = 1
            oc[f'NES_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'NES_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'NES_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'NES_{lineIndex}_ColorA%DARK'] =255
            oc[f'NES_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'NES_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'NES_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'NES_{lineIndex}_ColorA%LIGHT']=255
            oc[f'NES_{lineIndex}_Display'] = True
        #Finally
        self.objectConfig = oc

    def __matchGUIOsToConfig(self):
        #<MAIN>
        if (True):
            oc   = self.objectConfig
            cgt  = self.currentGUITheme
            ssps = self.settingsSubPages
            guios_MAIN       = ssps['MAIN'].GUIOs
            guios_SMA        = ssps['SMA'].GUIOs
            guios_WMA        = ssps['WMA'].GUIOs
            guios_EMA        = ssps['EMA'].GUIOs
            guios_PSAR       = ssps['PSAR'].GUIOs
            guios_BOL        = ssps['BOL'].GUIOs
            guios_IVP        = ssps['IVP'].GUIOs
            guios_SWING      = ssps['SWING'].GUIOs
            guios_VOL        = ssps['VOL'].GUIOs
            guios_NNA        = ssps['NNA'].GUIOs
            guios_MMACDSHORT = ssps['MMACDSHORT'].GUIOs
            guios_MMACDLONG  = ssps['MMACDLONG'].GUIOs
            guios_DMIxADX    = ssps['DMIxADX'].GUIOs
            guios_MFI        = ssps['MFI'].GUIOs
            guios_WOI        = ssps['WOI'].GUIOs
            guios_NES        = ssps['NES'].GUIOs
            #---SI Viewer
            siIndices_unassigned = list(range(len(_SITYPES)))
            siTypes_unassigned   = list(_SITYPES)
            for siIdx in range (len(_SITYPES)):
                guios_MAIN[f"SUBINDICATOR_DISPLAYSWITCH{siIdx}"].setStatus(oc[f'SIVIEWER{siIdx}Display'], callStatusUpdateFunction = False)
                siAlloc = oc[f'SIVIEWER{siIdx}SIAlloc']
                if siAlloc in _SITYPES:
                    self.siTypes_siViewerAlloc[siAlloc] = siIdx
                    guios_MAIN[f"SUBINDICATOR_DISPLAYSELECTION{siIdx}"].setSelected(siAlloc, callSelectionUpdateFunction = False)
                    siIndices_unassigned.remove(siIdx)
                    siTypes_unassigned.remove(siAlloc)
            for i in range (len(siIndices_unassigned)):
                siIdx_unassigned  = siIndices_unassigned[i]
                siType_unassigned = siTypes_unassigned[i]
                oc[f'SIVIEWER{siIdx_unassigned}SIAlloc']      = siType_unassigned
                self.siTypes_siViewerAlloc[siType_unassigned] = siIdx_unassigned
                guios_MAIN[f"SUBINDICATOR_DISPLAYSELECTION{siIdx_unassigned}"].setSelected(siType_unassigned, callSelectionUpdateFunction = False)
            #---Analyzer
            ar_beg_str = "" if oc['AnalysisRangeBeg'] is None else datetime.fromtimestamp(oc['AnalysisRangeBeg'], tz=timezone.utc).strftime("%Y/%m/%d %H:%M")
            ar_end_str = "" if oc['AnalysisRangeEnd'] is None else datetime.fromtimestamp(oc['AnalysisRangeEnd'], tz=timezone.utc).strftime("%Y/%m/%d %H:%M")
            guios_MAIN["ANALYZER_ANALYSISRANGEBEG_RANGEINPUT"].updateText(text = ar_beg_str)
            guios_MAIN["ANALYZER_ANALYSISRANGEEND_RANGEINPUT"].updateText(text = ar_end_str)
            guios_MAIN["ANALYZER_STARTANALYSIS_BUTTON"].deactivate()
            #---Trade Log
            guios_MAIN["TRADELOGDISPLAY_SWITCH"].setStatus(oc['TRADELOG_Display'], callStatusUpdateFunction = False)
            guios_MAIN["TRADELOGCOLOR_BUY_LED"].updateColor(oc[f'TRADELOG_BUY_ColorR%{cgt}'], 
                                                            oc[f'TRADELOG_BUY_ColorG%{cgt}'], 
                                                            oc[f'TRADELOG_BUY_ColorB%{cgt}'], 
                                                            oc[f'TRADELOG_BUY_ColorA%{cgt}'])
            guios_MAIN["TRADELOGCOLOR_SELL_LED"].updateColor(oc[f'TRADELOG_SELL_ColorR%{cgt}'], 
                                                             oc[f'TRADELOG_SELL_ColorG%{cgt}'], 
                                                             oc[f'TRADELOG_SELL_ColorB%{cgt}'], 
                                                             oc[f'TRADELOG_SELL_ColorA%{cgt}'])
            guios_MAIN["TRADELOGCOLOR_TARGETSELECTION"].setSelected('BUY', callSelectionUpdateFunction = True)
            guios_MAIN["TRADELOG_APPLYNEWSETTINGS"].deactivate()
            #---Bids and Asks
            guios_MAIN["BIDSANDASKSDISPLAY_SWITCH"].setStatus(oc['BIDSANDASKS_Display'], callStatusUpdateFunction = False)
            guios_MAIN["BIDSANDASKSCOLOR_BIDS_LED"].updateColor(oc[f'BIDSANDASKS_BIDS_ColorR%{cgt}'], 
                                                                oc[f'BIDSANDASKS_BIDS_ColorG%{cgt}'], 
                                                                oc[f'BIDSANDASKS_BIDS_ColorB%{cgt}'], 
                                                                oc[f'BIDSANDASKS_BIDS_ColorA%{cgt}'])
            guios_MAIN["BIDSANDASKSCOLOR_ASKS_LED"].updateColor(oc[f'BIDSANDASKS_ASKS_ColorR%{cgt}'], 
                                                                oc[f'BIDSANDASKS_ASKS_ColorG%{cgt}'], 
                                                                oc[f'BIDSANDASKS_ASKS_ColorB%{cgt}'], 
                                                                oc[f'BIDSANDASKS_ASKS_ColorA%{cgt}'])
            guios_MAIN["BIDSANDASKSCOLOR_TARGETSELECTION"].setSelected('BIDS', callSelectionUpdateFunction = True)
            guios_MAIN["BIDSANDASKS_APPLYNEWSETTINGS"].deactivate()
            #---Auxillaries
            guios_MAIN["AUX_KLINECOLORTYPE_SELECTIONBOX"].setSelected(oc['KlineColorType'], callSelectionUpdateFunction = True)
            guios_MAIN["AUX_TIMEZONE_SELECTIONBOX"].setSelected(oc['TimeZone'],             callSelectionUpdateFunction = True)
        #<SMA>
        if (True):
            guios_MAIN["MAININDICATOR_SMA"].setStatus(oc['SMA_Master'], callStatusUpdateFunction = False)
            for lineIndex in range (_NMAXLINES['SMA']):
                lineActive = oc[f'SMA_{lineIndex}_LineActive']
                nSamples   = oc[f'SMA_{lineIndex}_NSamples']
                width      = oc[f'SMA_{lineIndex}_Width']
                color      = (oc[f'SMA_{lineIndex}_ColorR%{cgt}'],
                              oc[f'SMA_{lineIndex}_ColorG%{cgt}'],
                              oc[f'SMA_{lineIndex}_ColorB%{cgt}'],
                              oc[f'SMA_{lineIndex}_ColorA%{cgt}'])
                display    = oc[f'SMA_{lineIndex}_Display']
                guios_SMA[f"INDICATOR_SMA{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
                guios_SMA[f"INDICATOR_SMA{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
                guios_SMA[f"INDICATOR_SMA{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
                guios_SMA[f"INDICATOR_SMA{lineIndex}_LINECOLOR"].updateColor(*color)
                guios_SMA[f"INDICATOR_SMA{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
            guios_SMA["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
            guios_SMA["APPLYNEWSETTINGS"].deactivate()
        #<WMA>
        if (True):
            guios_MAIN["MAININDICATOR_WMA"].setStatus(oc['WMA_Master'], callStatusUpdateFunction = False)
            for lineIndex in range (_NMAXLINES['WMA']):
                lineActive = oc[f'WMA_{lineIndex}_LineActive']
                nSamples   = oc[f'WMA_{lineIndex}_NSamples']
                width      = oc[f'WMA_{lineIndex}_Width']
                color      = (oc[f'WMA_{lineIndex}_ColorR%{cgt}'],
                              oc[f'WMA_{lineIndex}_ColorG%{cgt}'],
                              oc[f'WMA_{lineIndex}_ColorB%{cgt}'],
                              oc[f'WMA_{lineIndex}_ColorA%{cgt}'])
                display    = oc[f'WMA_{lineIndex}_Display']
                guios_WMA[f"INDICATOR_WMA{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
                guios_WMA[f"INDICATOR_WMA{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
                guios_WMA[f"INDICATOR_WMA{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
                guios_WMA[f"INDICATOR_WMA{lineIndex}_LINECOLOR"].updateColor(*color)
                guios_WMA[f"INDICATOR_WMA{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
            guios_WMA["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
            guios_WMA["APPLYNEWSETTINGS"].deactivate()
        #<EMA>
        if (True):
            guios_MAIN["MAININDICATOR_EMA"].setStatus(oc['EMA_Master'], callStatusUpdateFunction = False)
            for lineIndex in range (_NMAXLINES['EMA']):
                lineActive = oc[f'EMA_{lineIndex}_LineActive']
                nSamples   = oc[f'EMA_{lineIndex}_NSamples']
                width      = oc[f'EMA_{lineIndex}_Width']
                color      = (oc[f'EMA_{lineIndex}_ColorR%{cgt}'],
                              oc[f'EMA_{lineIndex}_ColorG%{cgt}'],
                              oc[f'EMA_{lineIndex}_ColorB%{cgt}'],
                              oc[f'EMA_{lineIndex}_ColorA%{cgt}'])
                display    = oc[f'EMA_{lineIndex}_Display']
                guios_EMA[f"INDICATOR_EMA{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
                guios_EMA[f"INDICATOR_EMA{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
                guios_EMA[f"INDICATOR_EMA{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
                guios_EMA[f"INDICATOR_EMA{lineIndex}_LINECOLOR"].updateColor(*color)
                guios_EMA[f"INDICATOR_EMA{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
            guios_EMA["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
            guios_EMA["APPLYNEWSETTINGS"].deactivate()
        #<PSAR>
        if (True):
            guios_MAIN["MAININDICATOR_PSAR"].setStatus(oc['PSAR_Master'], callStatusUpdateFunction = False)
            for lineIndex in range (_NMAXLINES['PSAR']):
                lineActive = oc[f'PSAR_{lineIndex}_LineActive']
                af0        = oc[f'PSAR_{lineIndex}_AF0']
                afPlus     = oc[f'PSAR_{lineIndex}_AF+']
                afMax      = oc[f'PSAR_{lineIndex}_AFMax']
                width      = oc[f'PSAR_{lineIndex}_Width']
                color      = (oc[f'PSAR_{lineIndex}_ColorR%{cgt}'], 
                              oc[f'PSAR_{lineIndex}_ColorG%{cgt}'], 
                              oc[f'PSAR_{lineIndex}_ColorB%{cgt}'], 
                              oc[f'PSAR_{lineIndex}_ColorA%{cgt}'])
                display    = oc[f'PSAR_{lineIndex}_Display']
                guios_PSAR[f"INDICATOR_PSAR{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
                guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AF0INPUT"].updateText(text   = f"{af0:.3f}")
                guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AF+INPUT"].updateText(text   = f"{afPlus:.3f}")
                guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AFMAXINPUT"].updateText(text = f"{afMax:.3f}")
                guios_PSAR[f"INDICATOR_PSAR{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
                guios_PSAR[f"INDICATOR_PSAR{lineIndex}_LINECOLOR"].updateColor(*color)
                guios_PSAR[f"INDICATOR_PSAR{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
            guios_PSAR["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
            guios_PSAR["APPLYNEWSETTINGS"].deactivate()
        #<BOL>
        if (True):
            guios_MAIN["MAININDICATOR_BOL"].setStatus(oc['BOL_Master'], callStatusUpdateFunction = False)
            guios_BOL["INDICATOR_MATYPESELECTION"].setSelected(oc['BOL_MAType'], callSelectionUpdateFunction = False)
            for lineIndex in range (_NMAXLINES['BOL']):
                lineActive = oc[f'BOL_{lineIndex}_LineActive']
                nSamples   = oc[f'BOL_{lineIndex}_NSamples']
                bandWidth  = oc[f'BOL_{lineIndex}_BandWidth']
                width      = oc[f'BOL_{lineIndex}_Width']
                color      = (oc[f'BOL_{lineIndex}_ColorR%{cgt}'], 
                              oc[f'BOL_{lineIndex}_ColorG%{cgt}'], 
                              oc[f'BOL_{lineIndex}_ColorB%{cgt}'], 
                              oc[f'BOL_{lineIndex}_ColorA%{cgt}'])
                display    = oc[f'BOL_{lineIndex}_Display']
                guios_BOL[f"INDICATOR_BOL{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
                guios_BOL[f"INDICATOR_BOL{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
                guios_BOL[f"INDICATOR_BOL{lineIndex}_BANDWIDTHINPUT"].updateText(text = f"{bandWidth:.1f}")
                guios_BOL[f"INDICATOR_BOL{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
                guios_BOL[f"INDICATOR_BOL{lineIndex}_LINECOLOR"].updateColor(*color)
                guios_BOL[f"INDICATOR_BOL{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
            guios_BOL["INDICATOR_DISPLAYCONTENTS_BOLCENTERSWITCH"].setStatus(oc['BOL_DisplayCenterLine'], callStatusUpdateFunction = False)
            guios_BOL["INDICATOR_DISPLAYCONTENTS_BOLBANDSWITCH"].setStatus(oc['BOL_DisplayBand'], callStatusUpdateFunction = False)
            guios_BOL["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
            guios_BOL["APPLYNEWSETTINGS"].deactivate()
        #<IVP>
        if (True):
            guios_MAIN["MAININDICATOR_IVP"].setStatus(oc['IVP_Master'],                 callStatusUpdateFunction = False)
            guios_IVP["INDICATOR_VPLP_DISPLAYSWITCH"].setStatus(oc['IVP_VPLP_Display'], callStatusUpdateFunction = False)
            guios_IVP["INDICATOR_VPLP_COLOR"].updateColor(oc[f'IVP_VPLP_ColorR%{cgt}'], 
                                                          oc[f'IVP_VPLP_ColorG%{cgt}'], 
                                                          oc[f'IVP_VPLP_ColorB%{cgt}'], 
                                                          oc[f'IVP_VPLP_ColorA%{cgt}'])
            guios_IVP["INDICATOR_VPLP_DISPLAYWIDTHSLIDER"].setSliderValue(newValue = (oc['IVP_VPLP_DisplayWidth']-0.1)/0.9*100, callValueUpdateFunction = False)
            guios_IVP["INDICATOR_VPLP_DISPLAYWIDTHVALUETEXT"].updateText(str(oc['IVP_VPLP_DisplayWidth']))
            guios_IVP["INDICATOR_VPLPB_DISPLAYSWITCH"].setStatus(oc['IVP_VPLPB_Display'], callStatusUpdateFunction = False)
            guios_IVP["INDICATOR_VPLPB_COLOR"].updateColor(oc[f'IVP_VPLPB_ColorR%{cgt}'], 
                                                           oc[f'IVP_VPLPB_ColorG%{cgt}'], 
                                                           oc[f'IVP_VPLPB_ColorB%{cgt}'], 
                                                           oc[f'IVP_VPLPB_ColorA%{cgt}'])
            
            vplpb_dRegion = oc['IVP_VPLPB_DisplayRegion']
            nSamples      = oc['IVP_NSamples']
            gammaFactor   = oc['IVP_GammaFactor']
            deltaFactor   = oc['IVP_DeltaFactor']
            guios_IVP["INDICATOR_VPLPB_DISPLAYREGIONSLIDER"].setSliderValue(newValue = (vplpb_dRegion-0.050)*(100/0.950), callValueUpdateFunction = False)
            guios_IVP["INDICATOR_VPLPB_DISPLAYREGIONVALUETEXT"].updateText(f"{vplpb_dRegion*100:.1f} %")
            guios_IVP["INDICATOR_INTERVAL_INPUTTEXT"].updateText(text = f"{nSamples}")
            guios_IVP["INDICATOR_GAMMAFACTOR_SLIDER"].setSliderValue(newValue = (nSamples-0.005)*(100/0.095), callValueUpdateFunction = False)
            guios_IVP["INDICATOR_GAMMAFACTOR_VALUETEXT"].updateText(text = f"{gammaFactor*100:.1f} %")
            guios_IVP["INDICATOR_DELTAFACTOR_SLIDER"].setSliderValue(newValue = (deltaFactor-0.1)*(100/9.9), callValueUpdateFunction = False)
            guios_IVP["INDICATOR_DELTAFACTOR_VALUETEXT"].updateText(text = f"{int(deltaFactor*100)} %")
            guios_IVP["INDICATORCOLOR_TARGETSELECTION"].setSelected('VPLP')
            guios_IVP["APPLYNEWSETTINGS"].deactivate()
        #<SWING>
        if (True):
            guios_MAIN["MAININDICATOR_SWING"].setStatus(oc['SWING_Master'], callStatusUpdateFunction = False)
            for lineIndex in range (_NMAXLINES['SWING']):
                lineActive = oc[f'SWING_{lineIndex}_LineActive']
                swingRange = oc[f'SWING_{lineIndex}_SwingRange']
                width      = oc[f'SWING_{lineIndex}_Width']
                color      = (oc[f'SWING_{lineIndex}_ColorR%{cgt}'], 
                              oc[f'SWING_{lineIndex}_ColorG%{cgt}'], 
                              oc[f'SWING_{lineIndex}_ColorB%{cgt}'], 
                              oc[f'SWING_{lineIndex}_ColorA%{cgt}'])
                display    = oc[f'SWING_{lineIndex}_Display']
                guios_SWING[f"INDICATOR_SWING{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
                guios_SWING[f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT"].updateText(text = f"{swingRange:.4f}")
                guios_SWING[f"INDICATOR_SWING{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
                guios_SWING[f"INDICATOR_SWING{lineIndex}_LINECOLOR"].updateColor(*color)
                guios_SWING[f"INDICATOR_SWING{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
            guios_SWING["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
            guios_SWING["APPLYNEWSETTINGS"].deactivate()
        #<VOL>
        if (True):
            guios_MAIN["SUBINDICATOR_VOL"].setStatus(oc['VOL_Master'], callStatusUpdateFunction = False)
            for lineIndex in range (_NMAXLINES['VOL']):
                lineActive = oc[f'VOL_{lineIndex}_LineActive']
                nSamples   = oc[f'VOL_{lineIndex}_NSamples']
                width      = oc[f'VOL_{lineIndex}_Width']
                color      = (oc[f'VOL_{lineIndex}_ColorR%{cgt}'],
                              oc[f'VOL_{lineIndex}_ColorG%{cgt}'],
                              oc[f'VOL_{lineIndex}_ColorB%{cgt}'],
                              oc[f'VOL_{lineIndex}_ColorA%{cgt}'])
                display    = oc[f'VOL_{lineIndex}_Display']
                guios_VOL[f"INDICATOR_VOL{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
                guios_VOL[f"INDICATOR_VOL{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
                guios_VOL[f"INDICATOR_VOL{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
                guios_VOL[f"INDICATOR_VOL{lineIndex}_LINECOLOR"].updateColor(*color)
                guios_VOL[f"INDICATOR_VOL{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
            guios_VOL["INDICATOR_VOLTYPESELECTION"].setSelected(oc['VOL_VolumeType'], callSelectionUpdateFunction = False)
            guios_VOL["INDICATOR_MATYPESELECTION"].setSelected(oc['VOL_MAType'],      callSelectionUpdateFunction = False)
            guios_VOL["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
            guios_VOL["APPLYNEWSETTINGS"].deactivate()
        #<NNA>
        if (True):
            guios_MAIN["SUBINDICATOR_NNA"].setStatus(oc['NNA_Master'], callStatusUpdateFunction = False)
            for lineIndex in range (_NMAXLINES['NNA']):
                lineActive = oc[f'NNA_{lineIndex}_LineActive']
                nnCode     = oc[f'NNA_{lineIndex}_NeuralNetworkCode']
                alpha      = oc[f'NNA_{lineIndex}_Alpha']
                beta       = oc[f'NNA_{lineIndex}_Beta']
                width      = oc[f'NNA_{lineIndex}_Width']
                color      = (oc[f'NNA_{lineIndex}_ColorR%{cgt}'], 
                              oc[f'NNA_{lineIndex}_ColorG%{cgt}'], 
                              oc[f'NNA_{lineIndex}_ColorB%{cgt}'], 
                              oc[f'NNA_{lineIndex}_ColorA%{cgt}'])
                display    = oc[f'NNA_{lineIndex}_Display']
                guios_NNA[f"INDICATOR_NNA{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
                nnCode_str = "" if nnCode is None else f"{nnCode}"
                guios_NNA[f"INDICATOR_NNA{lineIndex}_NNCODEINPUT"].updateText(text = nnCode_str)
                guios_NNA[f"INDICATOR_NNA{lineIndex}_ALPHAINPUT"].updateText(text = f"{alpha:.2f}")
                guios_NNA[f"INDICATOR_NNA{lineIndex}_BETAINPUT"].updateText(text  = f"{beta}")
                guios_NNA[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
                guios_NNA[f"INDICATOR_NNA{lineIndex}_LINECOLOR"].updateColor(*color)
                guios_NNA[f"INDICATOR_NNA{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
            guios_NNA["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
            guios_NNA["APPLYNEWSETTINGS"].deactivate()
        #<MMACDSHORT>
        if (True):
            guios_MAIN["SUBINDICATOR_MMACDSHORT"].setStatus(oc['MMACDSHORT_Master'], callStatusUpdateFunction = False)
            guios_MMACDSHORT["INDICATOR_MMACD_DISPLAYSWITCH"].setStatus(oc['MMACDSHORT_MMACD_Display'], callStatusUpdateFunction = False)
            guios_MMACDSHORT["INDICATOR_SIGNAL_DISPLAYSWITCH"].setStatus(oc['MMACDSHORT_SIGNAL_Display'], callStatusUpdateFunction = False)
            guios_MMACDSHORT["INDICATOR_HISTOGRAM_DISPLAYSWITCH"].setStatus(oc['MMACDSHORT_HISTOGRAM_Display'], callStatusUpdateFunction = False)
            guios_MMACDSHORT["INDICATOR_MMACD_COLOR"].updateColor(oc[f'MMACDSHORT_MMACD_ColorR%{cgt}'], 
                                                                  oc[f'MMACDSHORT_MMACD_ColorG%{cgt}'], 
                                                                  oc[f'MMACDSHORT_MMACD_ColorB%{cgt}'], 
                                                                  oc[f'MMACDSHORT_MMACD_ColorA%{cgt}'])
            guios_MMACDSHORT["INDICATOR_SIGNAL_COLOR"].updateColor(oc[f'MMACDSHORT_SIGNAL_ColorR%{cgt}'], 
                                                                   oc[f'MMACDSHORT_SIGNAL_ColorG%{cgt}'], 
                                                                   oc[f'MMACDSHORT_SIGNAL_ColorB%{cgt}'], 
                                                                   oc[f'MMACDSHORT_SIGNAL_ColorA%{cgt}'])
            guios_MMACDSHORT["INDICATOR_HISTOGRAM+_COLOR"].updateColor(oc[f'MMACDSHORT_HISTOGRAM+_ColorR%{cgt}'], 
                                                                       oc[f'MMACDSHORT_HISTOGRAM+_ColorG%{cgt}'], 
                                                                       oc[f'MMACDSHORT_HISTOGRAM+_ColorB%{cgt}'], 
                                                                       oc[f'MMACDSHORT_HISTOGRAM+_ColorA%{cgt}'])
            guios_MMACDSHORT["INDICATOR_HISTOGRAM-_COLOR"].updateColor(oc[f'MMACDSHORT_HISTOGRAM-_ColorR%{cgt}'], 
                                                                       oc[f'MMACDSHORT_HISTOGRAM-_ColorG%{cgt}'], 
                                                                       oc[f'MMACDSHORT_HISTOGRAM-_ColorB%{cgt}'], 
                                                                       oc[f'MMACDSHORT_HISTOGRAM-_ColorA%{cgt}'])
            signalNSamples = oc['MMACDSHORT_SignalNSamples']
            multiplier     = oc['MMACDSHORT_Multiplier']
            guios_MMACDSHORT["INDICATOR_SIGNALINTERVALTEXTINPUT"].updateText(text = f"{signalNSamples}")
            guios_MMACDSHORT["INDICATOR_MULTIPLIERTEXTINPUT"].updateText(text     = f"{multiplier}")
            for lineIndex in range (_NMAXLINES['MMACDSHORT']):
                lineActive = oc[f'MMACDSHORT_MA{lineIndex}_LineActive']
                nSamples   = oc[f'MMACDSHORT_MA{lineIndex}_NSamples']
                guios_MMACDSHORT[f"INDICATOR_MMACDMA{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
                guios_MMACDSHORT[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
            guios_MMACDSHORT["INDICATORCOLOR_TARGETSELECTION"].setSelected('MMACD')
            guios_MMACDSHORT["APPLYNEWSETTINGS"].deactivate()
        #<MMACDLONG>
        if (True):
            guios_MAIN["SUBINDICATOR_MMACDLONG"].setStatus(oc['MMACDLONG_Master'], callStatusUpdateFunction = False)
            guios_MMACDLONG["INDICATOR_MMACD_DISPLAYSWITCH"].setStatus(oc['MMACDLONG_MMACD_Display'], callStatusUpdateFunction = False)
            guios_MMACDLONG["INDICATOR_SIGNAL_DISPLAYSWITCH"].setStatus(oc['MMACDLONG_SIGNAL_Display'], callStatusUpdateFunction = False)
            guios_MMACDLONG["INDICATOR_HISTOGRAM_DISPLAYSWITCH"].setStatus(oc['MMACDLONG_HISTOGRAM_Display'], callStatusUpdateFunction = False)
            guios_MMACDLONG["INDICATOR_MMACD_COLOR"].updateColor(oc[f'MMACDLONG_MMACD_ColorR%{cgt}'], 
                                                                 oc[f'MMACDLONG_MMACD_ColorG%{cgt}'], 
                                                                 oc[f'MMACDLONG_MMACD_ColorB%{cgt}'], 
                                                                 oc[f'MMACDLONG_MMACD_ColorA%{cgt}'])
            guios_MMACDLONG["INDICATOR_SIGNAL_COLOR"].updateColor(oc[f'MMACDLONG_SIGNAL_ColorR%{cgt}'], 
                                                                  oc[f'MMACDLONG_SIGNAL_ColorG%{cgt}'], 
                                                                  oc[f'MMACDLONG_SIGNAL_ColorB%{cgt}'], 
                                                                  oc[f'MMACDLONG_SIGNAL_ColorA%{cgt}'])
            guios_MMACDLONG["INDICATOR_HISTOGRAM+_COLOR"].updateColor(oc[f'MMACDLONG_HISTOGRAM+_ColorR%{cgt}'], 
                                                                      oc[f'MMACDLONG_HISTOGRAM+_ColorG%{cgt}'], 
                                                                      oc[f'MMACDLONG_HISTOGRAM+_ColorB%{cgt}'], 
                                                                      oc[f'MMACDLONG_HISTOGRAM+_ColorA%{cgt}'])
            guios_MMACDLONG["INDICATOR_HISTOGRAM-_COLOR"].updateColor(oc[f'MMACDLONG_HISTOGRAM-_ColorR%{cgt}'], 
                                                                      oc[f'MMACDLONG_HISTOGRAM-_ColorG%{cgt}'], 
                                                                      oc[f'MMACDLONG_HISTOGRAM-_ColorB%{cgt}'], 
                                                                      oc[f'MMACDLONG_HISTOGRAM-_ColorA%{cgt}'])
                            
            signalNSamples = oc['MMACDLONG_SignalNSamples']
            multiplier     = oc['MMACDLONG_Multiplier']
            guios_MMACDLONG["INDICATOR_SIGNALINTERVALTEXTINPUT"].updateText(text = f"{signalNSamples}")
            guios_MMACDLONG["INDICATOR_MULTIPLIERTEXTINPUT"].updateText(text     = f"{multiplier}")
            for lineIndex in range (_NMAXLINES['MMACDLONG']):
                lineActive = oc[f'MMACDLONG_MA{lineIndex}_LineActive']
                nSamples   = oc[f'MMACDLONG_MA{lineIndex}_NSamples']
                guios_MMACDLONG[f"INDICATOR_MMACDMA{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
                guios_MMACDLONG[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
            guios_MMACDLONG["INDICATORCOLOR_TARGETSELECTION"].setSelected('MMACD')
            guios_MMACDLONG["APPLYNEWSETTINGS"].deactivate()
        #<DMIxADX>
        if (True):
            guios_MAIN["SUBINDICATOR_DMIxADX"].setStatus(oc['DMIxADX_Master'], callStatusUpdateFunction = False)
            for lineIndex in range (_NMAXLINES['DMIxADX']):
                lineActive = oc[f'DMIxADX_{lineIndex}_LineActive']
                nSamples   = oc[f'DMIxADX_{lineIndex}_NSamples']
                width      = oc[f'DMIxADX_{lineIndex}_Width']
                color      = (oc[f'DMIxADX_{lineIndex}_ColorR%{cgt}'],
                              oc[f'DMIxADX_{lineIndex}_ColorG%{cgt}'],
                              oc[f'DMIxADX_{lineIndex}_ColorB%{cgt}'],
                              oc[f'DMIxADX_{lineIndex}_ColorA%{cgt}'])
                display    = oc[f'DMIxADX_{lineIndex}_Display']
                guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
                guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
                guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
                guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_LINECOLOR"].updateColor(*color)
                guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
            guios_DMIxADX["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
            guios_DMIxADX["APPLYNEWSETTINGS"].deactivate()
        #<MFI>
        if (True):
            guios_MAIN["SUBINDICATOR_MFI"].setStatus(oc['MFI_Master'], callStatusUpdateFunction = False)
            for lineIndex in range (_NMAXLINES['MFI']):
                lineActive = oc[f'MFI_{lineIndex}_LineActive']
                nSamples   = oc[f'MFI_{lineIndex}_NSamples']
                width      = oc[f'MFI_{lineIndex}_Width']
                color      = (oc[f'MFI_{lineIndex}_ColorR%{cgt}'],
                              oc[f'MFI_{lineIndex}_ColorG%{cgt}'],
                              oc[f'MFI_{lineIndex}_ColorB%{cgt}'],
                              oc[f'MFI_{lineIndex}_ColorA%{cgt}'])
                display    = oc[f'MFI_{lineIndex}_Display']
                guios_MFI[f"INDICATOR_MFI{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
                guios_MFI[f"INDICATOR_MFI{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
                guios_MFI[f"INDICATOR_MFI{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
                guios_MFI[f"INDICATOR_MFI{lineIndex}_LINECOLOR"].updateColor(*color)
                guios_MFI[f"INDICATOR_MFI{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
            guios_MFI["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
            guios_MFI["APPLYNEWSETTINGS"].deactivate()
        #<WOI>
        if (True):
            guios_MAIN["SUBINDICATOR_WOI"].setStatus(oc['WOI_Master'],                     callStatusUpdateFunction = False)
            guios_WOI["INDICATOR_WOIBASE_DISPLAYSWITCH"].setStatus(oc['WOI_BASE_Display'], callStatusUpdateFunction = False)
            for target in ('BASE+', 'BASE-'):
                guios_WOI[f"INDICATOR_WOI{target}_LINECOLOR"].updateColor(oc[f'WOI_{target}_ColorR%{cgt}'],
                                                                          oc[f'WOI_{target}_ColorG%{cgt}'],
                                                                          oc[f'WOI_{target}_ColorB%{cgt}'],
                                                                          oc[f'WOI_{target}_ColorA%{cgt}'])
            for lineIndex in range (_NMAXLINES['WOI']):
                lineActive = oc[f'WOI_{lineIndex}_LineActive']
                nSamples   = oc[f'WOI_{lineIndex}_NSamples']
                sigma      = oc[f'WOI_{lineIndex}_Sigma']
                width      = oc[f'WOI_{lineIndex}_Width']
                color      = (oc[f'WOI_{lineIndex}_ColorR%{cgt}'],
                              oc[f'WOI_{lineIndex}_ColorG%{cgt}'],
                              oc[f'WOI_{lineIndex}_ColorB%{cgt}'],
                              oc[f'WOI_{lineIndex}_ColorA%{cgt}'])
                display    = oc[f'WOI_{lineIndex}_Display']
                guios_WOI[f"INDICATOR_WOI{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
                guios_WOI[f"INDICATOR_WOI{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
                guios_WOI[f"INDICATOR_WOI{lineIndex}_SIGMAINPUT"].updateText(text    = f"{sigma:.1f}")
                guios_WOI[f"INDICATOR_WOI{lineIndex}_WIDTHINPUT"].updateText(text    = f"{width}")
                guios_WOI[f"INDICATOR_WOI{lineIndex}_LINECOLOR"].updateColor(*color)
                guios_WOI[f"INDICATOR_WOI{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
            guios_WOI["INDICATORCOLOR_TARGETSELECTION"].setSelected('BASE+')
            guios_WOI["APPLYNEWSETTINGS"].deactivate()
        #<NES>
        if (True):
            guios_MAIN["SUBINDICATOR_NES"].setStatus(oc['NES_Master'],                     callStatusUpdateFunction = False)
            guios_NES["INDICATOR_NESBASE_DISPLAYSWITCH"].setStatus(oc['NES_BASE_Display'], callStatusUpdateFunction = False)
            for target in ('BASE+', 'BASE-'):
                guios_NES[f"INDICATOR_NES{target}_LINECOLOR"].updateColor(oc[f'NES_{target}_ColorR%{cgt}'], 
                                                                          oc[f'NES_{target}_ColorG%{cgt}'], 
                                                                          oc[f'NES_{target}_ColorB%{cgt}'], 
                                                                          oc[f'NES_{target}_ColorA%{cgt}'])
            for lineIndex in range (_NMAXLINES['NES']):
                lineActive = oc[f'NES_{lineIndex}_LineActive']
                nSamples   = oc[f'NES_{lineIndex}_NSamples']
                sigma      = oc[f'NES_{lineIndex}_Sigma']
                width      = oc[f'NES_{lineIndex}_Width']
                color      = (oc[f'NES_{lineIndex}_ColorR%{cgt}'],
                              oc[f'NES_{lineIndex}_ColorG%{cgt}'],
                              oc[f'NES_{lineIndex}_ColorB%{cgt}'],
                              oc[f'NES_{lineIndex}_ColorA%{cgt}'])
                display    = oc[f'NES_{lineIndex}_Display']
                guios_NES[f"INDICATOR_NES{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
                guios_NES[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
                guios_NES[f"INDICATOR_NES{lineIndex}_SIGMAINPUT"].updateText(text = f"{sigma:.1f}")
                guios_NES[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
                guios_NES[f"INDICATOR_NES{lineIndex}_LINECOLOR"].updateColor(*color)
                guios_NES[f"INDICATOR_NES{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
            guios_NES["INDICATORCOLOR_TARGETSELECTION"].setSelected('BASE+')
            guios_NES["APPLYNEWSETTINGS"].deactivate()

        #Set SubIndicator Switch Activation
        if (True):
            for siViewerIndex in range (len(_SITYPES)):
                if (siViewerIndex < self.usableSIViewers): 
                    guios_MAIN[f"SUBINDICATOR_DISPLAYSWITCH{siViewerIndex}"].activate()
                else:
                    guios_MAIN[f"SUBINDICATOR_DISPLAYSWITCH{siViewerIndex}"].setStatus(False)
                    guios_MAIN[f"SUBINDICATOR_DISPLAYSWITCH{siViewerIndex}"].deactivate()

        #Final 'AUX_SAVECONFIGURATION' Deactivation
        guios_MAIN["AUX_SAVECONFIGURATION"].deactivate()
    #Object Configuration & GUIO Initialization END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #DisplayBox Control ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __configureDisplayBoxes(self, onInit = False):
        #[1]: Determine Vertical DisplayBox Order
        if (True):
            #--- Temporal Grid
            self.displayBox_VerticalSection_Order = ['TEMPORALGRID']
            self.displayBox_VisibleBoxes          = ['MAINGRID_TEMPORAL', 'SETTINGSBUTTONFRAME']
            #--- SI Viewers (Reverse Order)
            for siViewerIndex in range (self.usableSIViewers-1, -1, -1):
                if self.objectConfig[f'SIVIEWER{siViewerIndex}Display']:
                    self.displayBox_VerticalSection_Order.append(f'SIVIEWER{siViewerIndex}')
                    self.displayBox_VisibleBoxes.append(f'SIVIEWER{siViewerIndex}')
            #--- Klines Price
            self.displayBox_VerticalSection_Order.append('KLINESPRICE')
            self.displayBox_VisibleBoxes.append('KLINESPRICE')
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
        if displayBoxName.startswith('SIVIEWER') and (displayBoxName in self.displayBox_graphics_visibleSIViewers):
            siIndex = int(displayBoxName[8:])
            dBoxName          = f'SIVIEWER{siIndex}'
            dBoxName_MAINGRID = f'MAINGRID_SIVIEWER{siIndex}'
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
            
    def __setSIViewerDisplay(self, siViewerIndex, siViewerDisplay):
        #[1]: Update Object Config
        self.objectConfig[f'SIVIEWER{siViewerIndex}Display'] = siViewerDisplay

        #[2]: Reconfigure Display Boxes and Initialize SIViewer
        self.__configureDisplayBoxes()
        self.__initializeSIViewer(siViewerCode = f"SIVIEWER{siViewerIndex}")
        
        #[3]: Set ViewRanges
        self.__onHViewRangeUpdate(updateType = 1)
        self.__onVViewRangeUpdate(displayBoxName = 'KLINESPRICE', updateType = 1)
        for visibleSIViewerCode in self.displayBox_graphics_visibleSIViewers: self.__onVViewRangeUpdate(displayBoxName = visibleSIViewerCode, updateType = 1)
        
        #[4]: If siViewerDisplay == True, update Draw Queues
        siAlloc = self.objectConfig[f'SIVIEWER{siViewerIndex}SIAlloc']
        if siViewerDisplay and (self.siTypes_analysisCodes[siAlloc] is not None):
            self.checkVerticalExtremas_SIs[siAlloc]()
            if siAlloc == 'VOL': self.__addBufferZone_toDrawQueue('VOL', drawSignal = _FULLDRAWSIGNALS[siAlloc])
            if siAlloc in {'VOL', 'MMACDLONG', 'MMACDSHORT', 'DMIxADX', 'MFI'}:
                for analysisCode in self.siTypes_analysisCodes[siAlloc]: self.__addBufferZone_toDrawQueue(analysisCode, drawSignal = _FULLDRAWSIGNALS[siAlloc])
            elif siAlloc == 'WOI': self.__addALLWOI_toDrawQueue()
            elif siAlloc == 'NES': self.__addALLNES_toDrawQueue()

    def __setSIViewerDisplayTarget(self, siViewerIndex1, siViewerDisplayTarget1):
        #[1]: Identify DisplayTarget Swap Target
        siViewerIndex2         = self.siTypes_siViewerAlloc[siViewerDisplayTarget1]
        siViewerDisplayTarget2 = self.objectConfig[f'SIVIEWER{siViewerIndex1}SIAlloc']

        #[2]: Update Object Config and SIViewer Control Variables
        self.objectConfig[f'SIVIEWER{siViewerIndex1}SIAlloc'] = siViewerDisplayTarget1
        self.objectConfig[f'SIVIEWER{siViewerIndex2}SIAlloc'] = siViewerDisplayTarget2
        self.siTypes_siViewerAlloc[siViewerDisplayTarget1] = siViewerIndex1
        self.siTypes_siViewerAlloc[siViewerDisplayTarget2] = siViewerIndex2
        
        siViewerDisplay1 = self.objectConfig[f'SIVIEWER{siViewerIndex1}Display']
        siViewerDisplay2 = self.objectConfig[f'SIVIEWER{siViewerIndex2}Display']
        siViewerCode1 = f"SIVIEWER{siViewerIndex1}"
        siViewerCode2 = f"SIVIEWER{siViewerIndex2}"

        #[3]: Reconfigure Display Boxes and Initialize SIViewer
        if siViewerDisplay1: self.__initializeSIViewer(siViewerCode = siViewerCode1)
        if siViewerDisplay2: self.__initializeSIViewer(siViewerCode = siViewerCode2)

        #[4]: Set ViewRanges
        if siViewerDisplay1:
            if self.checkVerticalExtremas_SIs[siViewerDisplayTarget1]():
                if   siViewerDisplayTarget1 == 'VOL':        self.__editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex1}", extension_b = 0.0, extension_t = 0.2)
                elif siViewerDisplayTarget1 == 'NNA':        self.__editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex1}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget1 == 'MMACDLONG':  self.__editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex1}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget1 == 'MMACDSHORT': self.__editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex1}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget1 == 'DMIxADX':    self.__editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex1}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget1 == 'MFI':        self.__editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex1}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget1 == 'WOI':        self.__editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex1}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget1 == 'NES':        self.__editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex1}", extension_b = 0.1, extension_t = 0.1)
        if siViewerDisplay2: 
            if self.checkVerticalExtremas_SIs[siViewerDisplayTarget2]():
                if   siViewerDisplayTarget2 == 'VOL':        self.__editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex2}", extension_b = 0.0, extension_t = 0.2)
                elif siViewerDisplayTarget2 == 'NNA':        self.__editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex2}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget2 == 'MMACDLONG':  self.__editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex2}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget2 == 'MMACDSHORT': self.__editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex2}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget2 == 'DMIxADX':    self.__editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex2}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget2 == 'MFI':        self.__editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex2}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget2 == 'WOI':        self.__editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex2}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget2 == 'NES':        self.__editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex2}", extension_b = 0.1, extension_t = 0.1)

        #[5]: If siViewerDisplay == True, update Draw Queues
        if siViewerDisplay1 and (self.siTypes_analysisCodes[siViewerDisplayTarget1] is not None):
            if siViewerDisplayTarget1 == 'VOL': self.__addBufferZone_toDrawQueue('VOL', drawSignal = _FULLDRAWSIGNALS[siViewerDisplayTarget1])
            if siViewerDisplayTarget1 in {'VOL', 'MMACDLONG', 'MMACDSHORT', 'DMIxADX', 'MFI'}:
                for analysisCode in self.siTypes_analysisCodes[siViewerDisplayTarget1]: self.__addBufferZone_toDrawQueue(analysisCode, drawSignal = _FULLDRAWSIGNALS[siViewerDisplayTarget1])
            elif siViewerDisplayTarget1 == 'WOI': self.__addALLWOI_toDrawQueue()
            elif siViewerDisplayTarget1 == 'NES': self.__addALLNES_toDrawQueue()

        if siViewerDisplay2 and (self.siTypes_analysisCodes[siViewerDisplayTarget2] is not None):
            if siViewerDisplayTarget2 == 'VOL': self.__addBufferZone_toDrawQueue('VOL', drawSignal = _FULLDRAWSIGNALS[siViewerDisplayTarget2])
            if siViewerDisplayTarget2 in {'VOL', 'MMACDLONG', 'MMACDSHORT', 'DMIxADX', 'MFI'}:
                for analysisCode in self.siTypes_analysisCodes[siViewerDisplayTarget2]: self.__addBufferZone_toDrawQueue(analysisCode, drawSignal = _FULLDRAWSIGNALS[siViewerDisplayTarget2])
            elif siViewerDisplayTarget2 == 'WOI': self.__addALLWOI_toDrawQueue()
            elif siViewerDisplayTarget2 == 'NES': self.__addALLNES_toDrawQueue()

        #[6]: Return SIViewerIndex2 for reference
        return siViewerIndex2

    def __initializeRCLCGs(self, displayBoxName, verticalPrecision = None):
        if verticalPrecision is None: self.verticalViewRange_precision[displayBoxName] = self.__getRCLCGVerticalPrecision(displayBoxName = displayBoxName)
        else:                         self.verticalViewRange_precision[displayBoxName] = verticalPrecision
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
        if self.currencyInfo is None: 
            return 2
        else:
            if displayBoxName == 'KLINESPRICE': 
                return self.currencyInfo['precisions']['price']
            if displayBoxName.startswith('SIVIEWER'):
                siType = self.objectConfig[f'{displayBoxName}SIAlloc']
                if siType == 'VOL':
                    if 'VOL' not in self.analysisParams: return 0
                    volType = self.analysisParams['VOL']['volType']
                    if   volType == 'BASE':    return self.currencyInfo['precisions']['quantity']
                    elif volType == 'QUOTE':   return self.currencyInfo['precisions']['quote']
                    elif volType == 'BASETB':  return self.currencyInfo['precisions']['quantity']
                    elif volType == 'QUOTETB': return self.currencyInfo['precisions']['quote']
                elif siType == 'NNA':        return 2
                elif siType == 'MMACDLONG':  return self.currencyInfo['precisions']['price']+2
                elif siType == 'MMACDSHORT': return self.currencyInfo['precisions']['price']+2
                elif siType == 'DMIxADX':    return 2
                elif siType == 'MFI':        return 2
                elif siType == 'WOI':        return 2
                elif siType == 'NES':        return 2
            return None
    #DisplayBox Control END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Processings -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def process(self, t_elapsed_ns):
        mei_beg = time.perf_counter_ns()
        self.__process_SubPages(t_elapsed_ns)                                                               #[1]: Subpage Processing
        self.__process_MouseEventInterpretation()                                                           #[2]: Mouse Event Interpretation
        self.__process_PosHighlightUpdate(mei_beg)                                                          #[3]: PosHighlight Update
        if self.klines_fetchComplete:
            waitPostDrag   = (mei_beg-self.mouse_lastDragged_ns  <= _TIMEINTERVAL_POSTDRAGWAITTIME)
            waitPostScroll = (mei_beg-self.mouse_lastScrolled_ns <= _TIMEINTERVAL_POSTSCROLLWAITTIME)
            if not waitPostDrag and not waitPostScroll: processNext = not(self.__process_analysis(mei_beg)) #[4]: Process Analysis
            else:                                       processNext = True
            if processNext: processNext = not(self.__process_drawQueues(mei_beg))                           #[5]: Draw Queues Processing
            if processNext: processNext = not(self.__process_RCLCGs(mei_beg))                               #[6]: RCLCGs Processing
            if processNext: self.__process_drawRemovalQueues(mei_beg)                                       #[7]: Draw Removal Queues Processing
        return

    def __process_SubPages(self, t_elapsed_ns):
        self.settingsSubPages[self.settingsSubPage_Current].process(t_elapsed_ns)
        
    def __process_MouseEventInterpretation(self):
        if _TIMEINTERVAL_MOUSEINTERPRETATION_NS <= time.perf_counter_ns() - self.mouse_Event_lastInterpreted_ns:
            #[1-1]: Mouse Drag Handling
            if self.mouse_Dragged:
                for section in self.mouse_DragDX: #Iterating over 'self.mouseDragDX' or 'self.mouseDragDY' does not matter
                    #Drag Delta
                    drag_dx = self.mouse_DragDX[section]
                    drag_dy = self.mouse_DragDY[section]
                    if not (drag_dx or drag_dy): continue
                    #Drag Responses
                    if section == 'KLINESPRICE':          
                        self.__editVPosition(displayBoxName = 'KLINESPRICE', delta_drag = drag_dy)
                        self.__editHPosition(delta_drag = drag_dx)
                    elif section == 'MAINGRID_KLINESPRICE': 
                        self.__editVMagFactor(displayBoxName = 'KLINESPRICE', delta_drag = drag_dy)
                    elif section == 'MAINGRID_TEMPORAL':    
                        self.__editHMagFactor(delta_drag = drag_dx)
                    elif section.startswith('SIVIEWER'):    
                        self.__editHPosition(delta_drag = drag_dx)
                    elif section.startswith('MAINGRID_SIVIEWER'):
                        siViewerIndex = int(section[17:])
                        siAlloc = self.objectConfig[f'SIVIEWER{siViewerIndex}SIAlloc']
                        if siAlloc == 'VOL': self.__editVMagFactor(displayBoxName = section.split("_")[1], delta_drag = drag_dy, anchor = 'BOTTOM')
                        else:                self.__editVMagFactor(displayBoxName = section.split("_")[1], delta_drag = drag_dy)
                    #Delta Reset
                    self.mouse_DragDX[section] = 0
                    self.mouse_DragDY[section] = 0
                #Post-Interpretation
                self.mouseDragged = False
            #[1-2]: Mouse Scroll Handling
            if self.mouse_Scrolled:
                for section in self.mouse_ScrollDX: #Iterating over 'self.mouseScrollDX' or 'self.mouseScrollDY' does not matter
                    #Scroll Delta
                    scroll_dx = self.mouse_ScrollDX[section]
                    scroll_dy = self.mouse_ScrollDY[section]
                    if not (scroll_dx or scroll_dy): continue
                    #Scroll Responses
                    if section == 'SETTINGSFRAME':
                        self.internalGUIOs_SETTINGS_viewRange[0] += scroll_dy*5
                        self.internalGUIOs_SETTINGS_viewRange[1] += scroll_dy*5
                        self.__onSettingsViewRangeUpdate(byScrollBar=False)
                    elif section == 'KLINESPRICE':              
                        self.__editHMagFactor(delta_scroll = scroll_dy)
                        self.__updatePosHighlight(self.mouse_Event_lastRead['x'], self.mouse_Event_lastRead['y'], self.mouse_lastHoveredSection, updateType = 0)
                    elif section == 'MAINGRID_KLINESPRICE':     
                        pass
                    elif section == 'MAINGRID_TEMPORAL':        
                        self.__editHPosition(delta_drag = scroll_dy*500)
                    elif section.startswith('SIVIEWER'):          
                        self.__editHMagFactor(delta_scroll = scroll_dy)
                        self.__updatePosHighlight(self.mouse_Event_lastRead['x'], self.mouse_Event_lastRead['y'], self.mouse_lastHoveredSection, updateType = 0)
                    elif section.startswith('MAINGRID_SIVIEWER'): 
                        pass
                    #Delta Reset
                    self.mouse_ScrollDX[section] = 0
                    self.mouse_ScrollDY[section] = 0
                self.mouse_Scrolled = False
            #[1-3]: Period Counter Reset
            self.mouse_Event_lastInterpreted_ns = time.perf_counter_ns()

    def __process_PosHighlightUpdate(self, mei_beg):
        if (self.posHighlight_updatedPositions is not None) and (_TIMEINTERVAL_POSHIGHLIGHTUPDATE <= mei_beg - self.posHighlight_lastUpdated_ns): 
            self.__onPosHighlightUpdate()

    # * TLViewer and Analyzer Exclusive
    def __process_analysis(self, mei_beg):
        #[1]: ChartDrawerType Check
        if self.chartDrawerType == 'CAVIEWER': return False

        #[2]: Instances
        aQueueList = self.analysisQueue_list
        procKline  = self.__processKline

        #[3]: Analysis
        while aQueueList and (time.perf_counter_ns()-mei_beg <= _TIMELIMIT_KLINESPROCESS_NS): 
            procKline()

        #[4]: Post-Analysis Handling
        if not aQueueList or (_AUX_NANALYSISQUEUEDISPLAYUPDATEINTERVAL_NS <= time.perf_counter_ns()-self.__lastNumberOfAnalysisQueueDisplayUpdated):
            #[4-1]: TL Viewer
            if self.chartDrawerType == 'TLVIEWER':
                fetchCompletion_perc = round((self.caRegeneration_nAnalysis_initial-len(aQueueList))/self.caRegeneration_nAnalysis_initial*100, 3)
                self.klinesLoadingGaugeBar.updateGaugeValue(fetchCompletion_perc)
                self.klinesLoadingTextBox_perc.updateText(text = f"{fetchCompletion_perc:.3f} %")
                if not aQueueList: self.__TLViewer_onCurrencyAnalysisRegenerationComplete()
            #[4-2]: Analyzer
            elif self.chartDrawerType == 'ANALYZER':
                self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT3'].setText(f"Number of Remaining Analysis Queues: {len(aQueueList)}")
            #[4-3]: Last Analysis Queue Display Update Time
            self.__lastNumberOfAnalysisQueueDisplayUpdated = time.perf_counter_ns()

        #[5]: Return Analysis Queue Status
        return 0 < len(aQueueList)

    def __process_drawQueues(self, mei_beg):
        while time.perf_counter_ns()-mei_beg < _TIMELIMIT_KLINESDRAWQUEUE_NS:
            #Draw Target Selection
            while True:
                #Klines
                ts = None
                for ts in self.klines_drawQueue: 
                    for aCode in self.klines_drawQueue[ts]: 
                        self.__klineDrawer_sendDrawSignals(timestamp = ts, analysisCode = aCode)
                    break
                if ts is not None: 
                    del self.klines_drawQueue[ts]
                    break
                #WOI
                ts = None
                for ts in self.bidsAndAsks_WOI_drawQueue:
                    for woiType in self.bidsAndAsks_WOI_drawQueue[ts]: 
                        self.__WOIDrawer_Draw(time = ts, woiType = woiType)
                    break
                if ts is not None: 
                    del self.bidsAndAsks_WOI_drawQueue[ts]
                    break
                #NES
                ts = None
                for ts in self.aggTrades_NES_drawQueue:
                    for nesType in self.aggTrades_NES_drawQueue[ts]: 
                        self.__NESDrawer_Draw(time = ts, nesType = nesType)
                    break
                if ts is not None: 
                    del self.aggTrades_NES_drawQueue[ts]
                    break
                #Bids and Asks
                if self.bidsAndAsks_drawFlag:
                    self.__bidsAndAsksDrawer_Draw()
                #Finally (Will reach here if no drawing has occurred)
                return False
        return True

    def __process_RCLCGs(self, mei_beg):
        remainingProcTime = _TIMELIMIT_RCLCGPROCESSING_NS-(time.perf_counter_ns()-mei_beg)
        nRefedRCLCGs = len(self.__RCLCGReferences)
        #If there exist any shapes within the focus do draw, process them first
        RCLCGRefIndex = 0
        while (RCLCGRefIndex < nRefedRCLCGs) and (0 < remainingProcTime):
            if self.__RCLCGReferences[RCLCGRefIndex].processShapeGenerationQueue(remainingProcTime, currentFocusOnly = True): 
                return True #Will return True if timeout has occurred and there still exist more shapes to draw
            else:
                remainingProcTime = _TIMELIMIT_RCLCGPROCESSING_NS-(time.perf_counter_ns()-mei_beg)
                RCLCGRefIndex += 1
        #If there is no more shapes to draw in the current focus, draw shapes outside the focus
        RCLCGRefIndex = 0
        while (RCLCGRefIndex < nRefedRCLCGs) and (0 < remainingProcTime):
            if self.__RCLCGReferences[RCLCGRefIndex].processShapeGenerationQueue(remainingProcTime, currentFocusOnly = False): 
                return True #Will return True if timeout has occurred and there still exist more shapes to draw
            else:
                remainingProcTime = _TIMELIMIT_RCLCGPROCESSING_NS-(time.perf_counter_ns()-mei_beg)
                RCLCGRefIndex += 1
        #Return if there exist any more shapes to draw
        return False

    def __process_drawRemovalQueues(self, mei_beg):
        while time.perf_counter_ns()-mei_beg < _TIMELIMIT_KLINESDRAWREMOVAL_NS:
            if   self.klines_drawRemovalQueue:          self.__klineDrawer_RemoveExpiredDrawings(self.klines_drawRemovalQueue.pop())
            elif self.bidsAndAsks_WOI_drawRemovalQueue: self.__WOIDrawer_RemoveExpiredDrawings(self.bidsAndAsks_WOI_drawRemovalQueue.pop())
            elif self.aggTrades_NES_drawRemovalQueue:   self.__NESDrawer_RemoveExpiredDrawings(self.aggTrades_NES_drawRemovalQueue.pop())
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
                yValHovered = yWithinDrawBox/self.displayBox_graphics[hoveredSection]['DRAWBOX'][3]     *(self.verticalViewRange[hoveredSection][1]-self.verticalViewRange[hoveredSection][0])+self.verticalViewRange[hoveredSection][0]
                #Get Timestamp Interval Position
                tsHovered = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = xValHovered, mrktReg = self.mrktRegTS, nTicks = 0)

                #If there exist no previous hoveredPosition
                if (self.posHighlight_hoveredPos[2] == None): 
                    self.posHighlight_updatedPositions = [True, True]
                    self.posHighlight_hoveredPos = (tsHovered, yValHovered, hoveredSection, None)
                #If there exist a previous hoveredPoisiton
                else:
                    self.posHighlight_updatedPositions = [False, False]
                    if (self.posHighlight_hoveredPos[0] != tsHovered):      self.posHighlight_updatedPositions[0] = True
                    if (self.posHighlight_hoveredPos[1] != yValHovered):    self.posHighlight_updatedPositions[1] = True
                    if (self.posHighlight_hoveredPos[2] != hoveredSection): self.posHighlight_hoveredPos = (tsHovered, yValHovered, hoveredSection, self.posHighlight_hoveredPos[2])
                    else:                                                   self.posHighlight_hoveredPos = (tsHovered, yValHovered, hoveredSection, hoveredSection)
            except:
                self.posHighlight_hoveredPos = (None, None, None, self.posHighlight_hoveredPos[2])
                self.posHighlight_updatedPositions = [True, True]

        elif (updateType == 1):
            if (self.posHighlight_hoveredPos[2] != None):
                self.posHighlight_hoveredPos = (None, None, None, self.posHighlight_hoveredPos[2])
                self.posHighlight_updatedPositions = [True, True]

    def __onPosHighlightUpdate(self):
        #[1]: Instances
        oc           = self.objectConfig
        dBox_g_vSIVs = self.displayBox_graphics_visibleSIViewers
        dBox_g = self.displayBox_graphics
        dBox_g_kl = dBox_g['KLINESPRICE']
        dBox_g_kl_phh = dBox_g_kl['POSHIGHLIGHT_HOVERED']
        dBox_g_kl_dt1 = dBox_g_kl['DESCRIPTIONTEXT1']
        dBox_g_kl_dt2 = dBox_g_kl['DESCRIPTIONTEXT2']
        dBox_g_kl_hul = dBox_g_kl['HORIZONTALGUIDELINE']
        dBox_g_kl_hut = dBox_g_kl['HORIZONTALGUIDETEXT']
        updated_x, updated_y                             = self.posHighlight_updatedPositions
        tsHovered, yHovered, dBox_current, dBox_previous = self.posHighlight_hoveredPos

        #[2]: Horizontal Elements Update
        if updated_x:
            #[3-1]: If Hovering Over No Display Box
            if dBox_current is None: 
                dBox_g_kl_phh.visible = False
                dBox_g_kl_dt1.hide()
                dBox_g_kl_dt2.hide()
                for dBoxName in dBox_g_vSIVs:
                    dBox_g_this = dBox_g[dBoxName]
                    dBox_g_this['POSHIGHLIGHT_HOVERED'].visible = False
                    dBox_g_this['DESCRIPTIONTEXT1'].hide()
            #[3-2]: If Hovering Over A Display Box
            else:
                #[3-2-1]: Visibility Control
                if not dBox_g_kl_phh.visible: dBox_g_kl_phh.visible = True
                if dBox_g_kl_dt1.isHidden(): dBox_g_kl_dt1.show()
                if dBox_g_kl_dt2.isHidden(): dBox_g_kl_dt2.show()
                for dBoxName in dBox_g_vSIVs:
                    dBox_g_this = dBox_g[dBoxName]
                    dBox_g_this_phh = dBox_g_this['POSHIGHLIGHT_HOVERED']
                    dBox_g_this_dt1 = dBox_g_this['DESCRIPTIONTEXT1']
                    if not dBox_g_this_phh.visible: dBox_g_this_phh.visible = True
                    if dBox_g_this_dt1.isHidden():  dBox_g_this_dt1.show()
                #[3-2-2]: Update Highligter Graphics
                ts_rightEnd = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = tsHovered, mrktReg = self.mrktRegTS, nTicks = 1)
                pixelPerTS  = dBox_g['MAINGRID_TEMPORAL']['DRAWBOX'][2]*self.scaler / (self.horizontalViewRange[1]-self.horizontalViewRange[0])
                highlightShape_x     = round((tsHovered-self.verticalGrid_intervals[0])*pixelPerTS, 1)
                highlightShape_width = round((ts_rightEnd-tsHovered)*pixelPerTS,                    1)
                dBox_g_kl_phh.x     = highlightShape_x
                dBox_g_kl_phh.width = highlightShape_width
                if not dBox_g_kl_phh.visible: dBox_g_kl_phh.visible = True
                for dBoxName in dBox_g_vSIVs:
                    dBox_g_this_phh = dBox_g[dBoxName]['POSHIGHLIGHT_HOVERED']
                    dBox_g_this_phh.x     = highlightShape_x
                    dBox_g_this_phh.width = highlightShape_width
                    if not dBox_g_this_phh.visible: dBox_g_this_phh.visible = True
                #[3-2-3]: Update Horizontal Description Texts
                #---[3-2-3-1]: Kline
                self.__onPHUs['KLINE']()
                #---[3-2-3-2]: Main Indicators
                tMIFound = False
                for tMI in ('IVP', 'TRADELOG'):
                    tMIFound = self.__onPHUs[tMI]()
                    if tMIFound: break
                if not tMIFound: self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2'].setText("")
                #---[3-2-3-3]: Sub Indicators
                for dBoxName in dBox_g_vSIVs:
                    siViewerIndex = int(dBoxName[8:])
                    siAlloc       = oc[f'SIVIEWER{siViewerIndex}SIAlloc']
                    self.__onPHUs[siAlloc]()
                
        #[3]: Vertcial Elements Update
        if updated_y:
            #[3-1]: If Hovering Over No Display Box
            if dBox_current is None:
                dBox_g_kl_hul.visible = False
                dBox_g_kl_hut.hide()
                for dBoxName in dBox_g_vSIVs:
                    dBox_g_this = dBox_g[dBoxName]
                    dBox_g_this['HORIZONTALGUIDELINE'].visible = False
                    dBox_g_this['HORIZONTALGUIDETEXT'].hide()
            #[3-2]: If Hovering Over A Display Box
            else:
                dBox_g_prev    = dBox_g.get(dBox_previous, None)
                dBox_g_current = dBox_g.get(dBox_current,  None)
                #[3-2-1]: Visibility Control
                if (dBox_g_prev is not None) and (dBox_previous != dBox_current):
                    dBox_g_prev['HORIZONTALGUIDELINE'].visible = False
                    dBox_g_prev['HORIZONTALGUIDETEXT'].hide()
                else:
                    if not dBox_g_current['HORIZONTALGUIDELINE'].visible: dBox_g_current['HORIZONTALGUIDELINE'].visible = True
                    if dBox_g_current['HORIZONTALGUIDETEXT'].isHidden():  dBox_g_current['HORIZONTALGUIDETEXT'].show()
                #[3-2-2]: Update Highligter Graphics
                pixelPerVal = dBox_g_current['DRAWBOX'][3]*self.scaler / (self.verticalViewRange[dBox_current][1]-self.verticalViewRange[dBox_current][0])
                try:    verticalHoverLine_y = round((yHovered-self.horizontalGridIntervals[dBox_current][0])*pixelPerVal, 1)
                except: verticalHoverLine_y = round(yHovered*pixelPerVal,                                                 1)
                dBox_g_current['HORIZONTALGUIDELINE'].y  = verticalHoverLine_y
                dBox_g_current['HORIZONTALGUIDELINE'].y2 = verticalHoverLine_y
                #[3-2-3]: Update Vertical Value Text
                dFromCeiling = dBox_g_current['HORIZONTALGRID_CAMGROUP'].projection_y1-verticalHoverLine_y
                if dFromCeiling < _GD_DISPLAYBOX_GUIDE_HORIZONTALTEXTHEIGHT*self.scaler: dBox_g_current['HORIZONTALGUIDETEXT'].moveTo(y = verticalHoverLine_y/self.scaler-_GD_DISPLAYBOX_GUIDE_HORIZONTALTEXTHEIGHT)
                else:                                                                    dBox_g_current['HORIZONTALGUIDETEXT'].moveTo(y = verticalHoverLine_y/self.scaler)
                dBox_g_current['HORIZONTALGUIDETEXT'].setText(atmEta_Auxillaries.floatToString(number = yHovered, precision = self.verticalViewRange_precision[dBox_current]))
        
        #[4]: Reset Update Flag
        self.posHighlight_updatedPositions = None

    def __onPHU_KLINE(self):
        #[1]: Instances
        oc    = self.objectConfig
        kData = self.klines['raw']
        tsHovered     = self.posHighlight_hoveredPos[0]
        func_fts      = atmEta_Auxillaries.floatToString
        dBox_g_kl_dt1 = self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT1']

        #[2]: If Hovering Over A Kline Data
        if tsHovered in kData:
            kline = kData[tsHovered]
            p_open  = kline[KLINDEX_OPENPRICE]
            p_high  = kline[KLINDEX_HIGHPRICE]
            p_low   = kline[KLINDEX_LOWPRICE]
            p_close = kline[KLINDEX_CLOSEPRICE]
            kcType = oc['KlineColorType']
            if   p_open < p_close: klineColor = f'CONTENT_POSITIVE_{kcType}'
            elif p_open > p_close: klineColor = f'CONTENT_NEGATIVE_{kcType}'
            else:                  klineColor = f'CONTENT_NEUTRAL_{kcType}'
            displayText_time = datetime.fromtimestamp(tsHovered+self.timezoneDelta, tz = timezone.utc).strftime(" %Y/%m/%d %H:%M"); tp1 = len(displayText_time)
            pPrecision = self.verticalViewRange_precision['KLINESPRICE']
            p_open_str  = func_fts(number = p_open,  precision = pPrecision)
            p_high_str  = func_fts(number = p_high,  precision = pPrecision)
            p_low_str   = func_fts(number = p_low,   precision = pPrecision)
            p_close_str = func_fts(number = p_close, precision = pPrecision)
            displayText_open  = f" OPEN: {p_open_str}";   tp2 = tp1 + len(displayText_open) 
            displayText_high  = f" HIGH: {p_high_str}";   tp3 = tp2 + len(displayText_high)
            displayText_low   = f" LOW: {p_low_str}";     tp4 = tp3 + len(displayText_low)
            displayText_close = f" CLOSE: {p_close_str}"; tp5 = tp4 + len(displayText_close)
            dBox_g_kl_dt1.setText(displayText_time+displayText_open+displayText_high+displayText_low+displayText_close, [((0,     tp1+5), 'DEFAULT'),
                                                                                                                         ((tp1+6, tp2),   klineColor),
                                                                                                                         ((tp2+1, tp2+5), 'DEFAULT'),
                                                                                                                         ((tp2+6, tp3),   klineColor),
                                                                                                                         ((tp3+1, tp3+4), 'DEFAULT'),
                                                                                                                         ((tp3+5, tp4),   klineColor),
                                                                                                                         ((tp4+1, tp4+6), 'DEFAULT'),
                                                                                                                         ((tp4+7, tp5-1), klineColor)])
        #[3]: If Not Hovering Over A Kline Data
        else:
            displayText_time = datetime.fromtimestamp(tsHovered+self.timezoneDelta, tz = timezone.utc).strftime(" %Y/%m/%d %H:%M")
            displayText_open = " OPEN: - HIGH: - LOW: - CLOSE: -"
            dBox_g_kl_dt1.setText(displayText_time+displayText_open)
            dBox_g_kl_dt1.editTextStyle('all', 'DEFAULT')

    def __onPHU_IVP(self):
        #[1]: Instances
        oc        = self.objectConfig
        tsHovered = self.posHighlight_hoveredPos[0]
        klines    = self.klines
        dBox_g_kp_dt2 = self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2']
        
        #[2]: Existence & Display Check
        if 'IVP' not in klines:            return False
        if tsHovered not in klines['IVP']: return False
        if not oc['IVP_Master']:           return False

        #[3]: Base Text & Styles
        text_display = f" [IVP]"

        #[4]: Displaying Text & Style Construction
        ivpResult = klines['IVP'][tsHovered]
        ivpr_vplp    = ivpResult['volumePriceLevelProfile']
        ivpr_gFactor = ivpResult['gammaFactor']
        ivpr_bFactor = ivpResult['betaFactor']
        if ivpr_vplp is None: textBlock  = " nDivisions: NONE, Gamma Factor: NONE"
        else:                 textBlock  = f" nDivisions: {len(ivpr_vplp)}, Gamma Factor: {ivpr_gFactor*100:.2f} % [{ivpr_bFactor}]"
        text_display += textBlock

        #[5]: Update Text Element
        dBox_g_kp_dt2.setText(text_display, 'DEFAULT')

        #[6]: Return Result
        return True
    
    def __onPHU_TRADELOG(self):
        #[1]: Instances
        oc = self.objectConfig
        tsHovered = self.posHighlight_hoveredPos[0]
        klines    = self.klines
        dBox_g_kp_dt2 = self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2']
        func_fts = atmEta_Auxillaries.floatToString

        #[2]: Existence & Display Check
        if 'TRADELOG' not in klines:            return False
        if tsHovered not in klines['TRADELOG']: return False
        if not oc['TRADELOG_Display']:          return False

        #[3]: Base Text & Styles
        text_display = f" [TRADELOG]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Displaying Text & Style Construction
        tradeLog = klines['TRADELOG'][tsHovered]
        tl_entryPrice    = tradeLog['entryPrice']
        tl_quantity      = tradeLog['totalQuantity']
        tl_logicSource   = tradeLog['logicSource']
        tl_tradeQuantity = tradeLog['quantity']
        tl_tradePrice    = tradeLog['price']
        tl_profit        = tradeLog['profit']
        tl_tradingFee    = tradeLog['tradingFee']
        tBlocks = list()
        if tl_logicSource is None: tVals = ('entryPrice', 'totalQuantity')
        else:                      tVals = ('entryPrice', 'totalQuantity', 'logicSource', 'quantity', 'price', 'profit', 'tradingFee')
        tPrecisions = self.targetPrecisions
        precision_price    = tPrecisions['price']
        precision_quantity = tPrecisions['quantity']
        precision_quote    = tPrecisions['quote']
        for tVal in tVals:
            if tVal == 'entryPrice':
                tBlock_str = func_fts(number = tl_entryPrice, precision = precision_price)
                tBlock_col = 'DEFAULT'
                tBlocks.append((' Entry: ', 'DEFAULT'))
                tBlocks.append((tBlock_str, 'DEFAULT'))
            elif tVal == 'totalQuantity':
                tBlock_str = func_fts(number = tl_quantity, precision = precision_quantity)
                if   tl_quantity < 0: tBlock_col = 'RED_LIGHT'
                elif 0 < tl_quantity: tBlock_col = 'GREEN_LIGHT'
                else:                 tBlock_col = 'DEFAULT'
                tBlocks.append((' Quantity: ', 'DEFAULT'))
                tBlocks.append((tBlock_str, tBlock_col))
            elif tVal == 'logicSource':
                tBlock_str = tl_logicSource
                if   tl_logicSource == 'ENTRY':       tBlock_col = 'BLUE_LIGHT'
                elif tl_logicSource == 'CLEAR':       tBlock_col = 'ORANGE_DARK'
                elif tl_logicSource == 'EXIT':        tBlock_col = 'ORANGE_LIGHT'
                elif tl_logicSource == 'FSLIMMED':    tBlock_col = 'CYAN_DARK'
                elif tl_logicSource == 'FSLCLOSE':    tBlock_col = 'CYAN_DARK'
                elif tl_logicSource == 'LIQUIDATION': tBlock_col = 'VIOLET_LIGHT'
                elif tl_logicSource == 'FORCECLEAR':  tBlock_col = 'VIOLET'
                elif tl_logicSource == 'UNKNOWN':     tBlock_col = 'VIOLET_DARK'
                else:                                 tBlock_col = 'DEFAULT'
                tBlocks.append((' Logic Source: ', 'DEFAULT'))
                tBlocks.append((tBlock_str, tBlock_col))
            elif tVal == 'quantity':
                tBlock_str = func_fts(number = tl_tradeQuantity, precision = precision_quantity)
                tBlocks.append((' Trade Quantity: ', 'DEFAULT'))
                tBlocks.append((tBlock_str,          'DEFAULT'))
            elif tVal == 'price':
                tBlock_str = func_fts(number = tl_tradePrice, precision = precision_price)
                tBlocks.append((' Trade Price: ', 'DEFAULT'))
                tBlocks.append((tBlock_str,       'DEFAULT'))
            elif tVal == 'profit':
                tBlock_str = func_fts(number = tl_profit, precision = precision_quote)
                if   tl_profit < 0: tBlock_col = 'RED_LIGHT'
                elif 0 < tl_profit: tBlock_col = 'GREEN_LIGHT'
                else:               tBlock_col = 'DEFAULT'
                tBlocks.append((' Profit: ', 'DEFAULT'))
                tBlocks.append((tBlock_str, tBlock_col))
            elif tVal == 'tradingFee':
                tBlock_str = func_fts(number = tl_tradingFee, precision = precision_quote)
                tBlocks.append((' TradingFee: ', 'DEFAULT'))
                tBlocks.append((tBlock_str,      'DEFAULT'))

        for tb_display, tb_style in tBlocks:
            text_display += tb_display
            text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(tb_display)-1), tb_style))

        #[4]: Update Text Element
        dBox_g_kp_dt2.setText(text_display, 'DEFAULT')

        #[4]: Return Result
        return True
    
    def __onPHU_VOL(self):
        #[1]: Instances
        oc  = self.objectConfig
        ap  = self.analysisParams
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        klines    = self.klines
        kData     = klines['raw']
        cInfo     = self.currencyInfo
        siViewerIndex   = self.siTypes_siViewerAlloc['VOL']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']

        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - VOL]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        if tsHovered in kData and oc['VOL_Master']:
            kline = kData[tsHovered]
            #[3-1]: Volume Raw
            volType = oc['VOL_VolumeType']
            if   volType == 'BASE':    value = kline[KLINDEX_VOLBASE];          precision = cInfo['precisions']['quantity']; unit = cInfo['info_server']['baseAsset']
            elif volType == 'QUOTE':   value = kline[KLINDEX_VOLQUOTE];         precision = cInfo['precisions']['quote'];    unit = cInfo['info_server']['quoteAsset']
            elif volType == 'BASETB':  value = kline[KLINDEX_VOLBASETAKERBUY];  precision = cInfo['precisions']['quantity']; unit = cInfo['info_server']['baseAsset']
            elif volType == 'QUOTETB': value = kline[KLINDEX_VOLQUOTETAKERBUY]; precision = cInfo['precisions']['quote'];    unit = cInfo['info_server']['quoteAsset']
            kcType = oc['KlineColorType']
            p_open  = kline[KLINDEX_OPENPRICE]
            p_close = kline[KLINDEX_CLOSEPRICE]
            if   p_open < p_close: klineColor = f'CONTENT_POSITIVE_{kcType}'
            elif p_open > p_close: klineColor = f'CONTENT_NEGATIVE_{kcType}'
            else:                  klineColor = f'CONTENT_NEUTRAL_{kcType}'
            textBlock_front = " VOL_BASE: "
            textBlock = f"{textBlock_front}{atmEta_Auxillaries.floatToString(number = value, precision = precision)} {unit}"
            text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(textBlock_front)), 'DEFAULT'))
            text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1),     klineColor))
            text_display += textBlock
            #[3-2]: Volume Analysis
            for aCode in self.siTypes_analysisCodes['VOL']:
                #[3-2-1]: Existence Check
                if tsHovered not in klines[aCode]: continue

                #[3-2-2]: Display Check
                lineIndex     = ap[aCode]['lineIndex']
                lineIndex_str = f"{lineIndex}"
                if not oc[f'VOL_{lineIndex}_Display']: continue

                #[3-2-3]: TextStyle Check
                currentLine_style = dBox_g_this_dt1.getTextStyle(lineIndex_str)
                newLine_color = (oc[f'VOL_{lineIndex}_ColorR%{cgt}'],
                                 oc[f'VOL_{lineIndex}_ColorG%{cgt}'],
                                 oc[f'VOL_{lineIndex}_ColorB%{cgt}'],
                                 oc[f'VOL_{lineIndex}_ColorA%{cgt}'])
                if (currentLine_style is None) or (currentLine_style['color'] != newLine_color):
                    newLine_style = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                    newLine_style['color'] = newLine_color
                    dBox_g_this_dt1.addTextStyle(lineIndex_str, newLine_style)

                #[3-2-4]: Text & Format Array Construction
                value_MA = klines[aCode][tsHovered]['MA']
                if value_MA is None: textBlock = f" {aCode}: NONE"
                else:                textBlock = f" {aCode}: {atmEta_Auxillaries.floatToString(number = value_MA, precision = precision)} {unit}"
                text_display += textBlock
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(aCode)+3),     'DEFAULT'))
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1), lineIndex_str))

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)

        """
        if (self.posHighlight_hoveredPos[0] in self.klines['raw']):
            textBlock = " [SI{:d} - VOL]".format(siViewerIndex)
            displayText += textBlock; textFormats.append(((0, len(textBlock)-1), 'DEFAULT'))
            if (self.objectConfig['VOL_VolumeType'] == 'BASE'):    textBlock = " VOL_BASE: {:s} {:s}".format(atmEta_Auxillaries.floatToString(number    = self.klines['raw'][self.posHighlight_hoveredPos[0]][KLINDEX_VOLBASE],          precision = self.currencyInfo['precisions']['quantity']), self.currencyInfo['info_server']['baseAsset']);  textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][1]+10), 'DEFAULT')); textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][0]+len(textBlock)-1), klineColor))
            if (self.objectConfig['VOL_VolumeType'] == 'QUOTE'):   textBlock = " VOL_QUOTE: {:s} {:s}".format(atmEta_Auxillaries.floatToString(number   = self.klines['raw'][self.posHighlight_hoveredPos[0]][KLINDEX_VOLQUOTE],         precision = self.currencyInfo['precisions']['quote']),    self.currencyInfo['info_server']['quoteAsset']); textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][1]+11), 'DEFAULT')); textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][0]+len(textBlock)-1), klineColor))
            if (self.objectConfig['VOL_VolumeType'] == 'BASETB'):  textBlock = " VOL_BASETB: {:s} {:s}".format(atmEta_Auxillaries.floatToString(number  = self.klines['raw'][self.posHighlight_hoveredPos[0]][KLINDEX_VOLBASETAKERBUY],  precision = self.currencyInfo['precisions']['quantity']), self.currencyInfo['info_server']['baseAsset']);  textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][1]+12), 'DEFAULT')); textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][0]+len(textBlock)-1), klineColor))
            if (self.objectConfig['VOL_VolumeType'] == 'QUOTETB'): textBlock = " VOL_QUOTETB: {:s} {:s}".format(atmEta_Auxillaries.floatToString(number = self.klines['raw'][self.posHighlight_hoveredPos[0]][KLINDEX_VOLQUOTETAKERBUY], precision = self.currencyInfo['precisions']['quote']),    self.currencyInfo['info_server']['quoteAsset']); textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][1]+13), 'DEFAULT')); textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][0]+len(textBlock)-1), klineColor))
            displayText += textBlock
            for analysisCode in self.siTypes_analysisCodes[siAlloc]:
                if ((analysisCode != 'VOL') and (self.posHighlight_hoveredPos[0] in self.klines[analysisCode])):
                    #TextStyle Check
                    lineIndex = self.analysisParams[analysisCode]['lineIndex']
                    currentLineStyle = self.displayBox_graphics['SIVIEWER{:d}'.format(siViewerIndex)]['DESCRIPTIONTEXT1'].getTextStyle(lineIndex)
                    currentLineColor = (self.objectConfig['VOL_{:d}_ColorR%{:s}'.format(lineIndex, self.currentGUITheme)],
                                        self.objectConfig['VOL_{:d}_ColorG%{:s}'.format(lineIndex, self.currentGUITheme)],
                                        self.objectConfig['VOL_{:d}_ColorB%{:s}'.format(lineIndex, self.currentGUITheme)],
                                        self.objectConfig['VOL_{:d}_ColorA%{:s}'.format(lineIndex, self.currentGUITheme)])
                    if (currentLineStyle == None) or (currentLineStyle['color'] != currentLineColor):
                        newTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                        newTextStyle['color'] = currentLineColor
                        self.displayBox_graphics['SIVIEWER{:d}'.format(siViewerIndex)]['DESCRIPTIONTEXT1'].addTextStyle(str(lineIndex), newTextStyle)
                    #Text & Format Array Construction
                    textBlock = " {:s}: {:s}".format(analysisCode, str(self.klines[analysisCode][self.posHighlight_hoveredPos[0]]['MA']))
                    if (self.objectConfig['VOL_VolumeType'] == 'BASE'):    textBlock = " {:s}: {:s}".format(analysisCode, atmEta_Auxillaries.floatToString(number = self.klines[analysisCode][self.posHighlight_hoveredPos[0]]['MA'], precision = self.currencyInfo['precisions']['quantity']))
                    if (self.objectConfig['VOL_VolumeType'] == 'QUOTE'):   textBlock = " {:s}: {:s}".format(analysisCode, atmEta_Auxillaries.floatToString(number = self.klines[analysisCode][self.posHighlight_hoveredPos[0]]['MA'], precision = self.currencyInfo['precisions']['quote']))
                    if (self.objectConfig['VOL_VolumeType'] == 'BASETB'):  textBlock = " {:s}: {:s}".format(analysisCode, atmEta_Auxillaries.floatToString(number = self.klines[analysisCode][self.posHighlight_hoveredPos[0]]['MA'], precision = self.currencyInfo['precisions']['quantity']))
                    if (self.objectConfig['VOL_VolumeType'] == 'QUOTETB'): textBlock = " {:s}: {:s}".format(analysisCode, atmEta_Auxillaries.floatToString(number = self.klines[analysisCode][self.posHighlight_hoveredPos[0]]['MA'], precision = self.currencyInfo['precisions']['quote']))
                    displayText += textBlock
                    textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][1]+len(analysisCode)+3), 'DEFAULT'))
                    textFormats.append(((textFormats[-1][0][1]+1, textFormats[-1][0][0]+len(textBlock)-1),    str(lineIndex)))
            self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].setText(displayText, textFormats)
        else:
            self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].setText(" [SI{:d} - VOL]".format(siViewerIndex))
            self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].editTextStyle('all', 'DEFAULT')
        """

    def __onPHU_NNA(self):
        #[1]: Instances
        oc  = self.objectConfig
        ap  = self.analysisParams
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        klines    = self.klines
        siViewerIndex   = self.siTypes_siViewerAlloc['NNA']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']


        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - NNA]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        if oc['NNA_Master']:
            for aCode in self.siTypes_analysisCodes['NNA']:
                #[3-1]: Existence Check
                if tsHovered not in klines[aCode]: continue

                #[3-2]: Display Check
                lineIndex     = ap[aCode]['lineIndex']
                lineIndex_str = f"{lineIndex}"
                if not oc[f'NNA_{lineIndex}_Display']: continue

                #TextStyle Check
                currentLine_style = dBox_g_this_dt1.getTextStyle(lineIndex_str)
                newLine_color = (oc[f'NNA_{lineIndex}_ColorR%{cgt}'],
                                 oc[f'NNA_{lineIndex}_ColorG%{cgt}'],
                                 oc[f'NNA_{lineIndex}_ColorB%{cgt}'],
                                 oc[f'NNA_{lineIndex}_ColorA%{cgt}'])
                if (currentLine_style is None) or (currentLine_style['color'] != newLine_color):
                    newLine_style = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                    newLine_style['color'] = newLine_color
                    dBox_g_this_dt1.addTextStyle(lineIndex_str, newLine_style)

                #Text & Format Array Construction
                value_nna = klines[aCode][tsHovered]['NNA']
                if value_nna is None: textBlock = f" {aCode}: NONE"
                else:                 textBlock = f" {aCode}: {value_nna:.2f}"
                text_display += textBlock
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(aCode)+3),     'DEFAULT'))
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1), lineIndex_str))

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)

    def __onPHU_MMACDSHORT(self):
        #[1]: Instances
        oc  = self.objectConfig
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        klines    = self.klines
        siViewerIndex   = self.siTypes_siViewerAlloc['MMACDSHORT']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']

        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - MMACDSHORT]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        aCode = 'MMACDSHORT'
        if oc['MMACDSHORT_Master'] and aCode in klines and tsHovered in klines[aCode]:
            displayPrecision = self.currencyInfo['precisions']['price']+2
            for line, valCode in (('MMACD',     'MMACD'), 
                                  ('SIGNAL',    'SIGNAL'), 
                                  ('HISTOGRAM', 'MSDELTA')
                                  ):
                #[3-1]: Display Check
                if not oc[f'MMACDSHORT_{line}_Display']: continue

                #[3-2]: Display Value
                value_display = klines[aCode][tsHovered][valCode]

                #[3-2]: Text Style Check
                if line == 'HISTOGRAM':
                    if value_display is None: newLine_colType = None
                    else:
                        if   0 < value_display: newLine_colType = 'HISTOGRAM+'
                        elif value_display < 0: newLine_colType = 'HISTOGRAM-'
                        else:                   newLine_colType = None
                else: newLine_colType = line
                if newLine_colType is None: newLine_colType = 'DEFAULT'
                else:
                    currentLine_style = dBox_g_this_dt1.getTextStyle(newLine_colType)
                    newLine_color = (oc[f'MMACDSHORT_{newLine_colType}_ColorR%{cgt}'],
                                     oc[f'MMACDSHORT_{newLine_colType}_ColorG%{cgt}'],
                                     oc[f'MMACDSHORT_{newLine_colType}_ColorB%{cgt}'],
                                     oc[f'MMACDSHORT_{newLine_colType}_ColorA%{cgt}'])
                    if (currentLine_style is None) or (currentLine_style['color'] != newLine_color):
                        newLine_style = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                        newLine_style['color'] = newLine_color
                        dBox_g_this_dt1.addTextStyle(newLine_colType, newLine_style)
                #[3-3]: Text & Format Array Construction
                if value_display is None: textBlock = f" {line}: NONE"
                else:                     textBlock = f" {line}: {value_display:.{displayPrecision}f}"
                text_display += textBlock
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(line)+3),      'DEFAULT'))
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1), newLine_colType))

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)

    def __onPHU_MMACDLONG(self):
        #[1]: Instances
        oc  = self.objectConfig
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        klines    = self.klines
        siViewerIndex   = self.siTypes_siViewerAlloc['MMACDLONG']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']

        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - MMACDLONG]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        aCode = 'MMACDLONG'
        if oc['MMACDLONG_Master'] and aCode in klines and tsHovered in klines[aCode]:
            displayPrecision = self.currencyInfo['precisions']['price']+2
            for line, valCode in (('MMACD',     'MMACD'), 
                                  ('SIGNAL',    'SIGNAL'), 
                                  ('HISTOGRAM', 'MSDELTA')
                                  ):
                #[3-1]: Display Check
                if not oc[f'MMACDLONG_{line}_Display']: continue

                #[3-2]: Display Value
                value_display = klines[aCode][tsHovered][valCode]

                #[3-2]: Text Style Check
                if line == 'HISTOGRAM':
                    if value_display is None: newLine_colType = None
                    else:
                        if   0 < value_display: newLine_colType = 'HISTOGRAM+'
                        elif value_display < 0: newLine_colType = 'HISTOGRAM-'
                        else:                   newLine_colType = None
                else: newLine_colType = line
                if newLine_colType is None: newLine_colType = 'DEFAULT'
                else:
                    currentLine_style = dBox_g_this_dt1.getTextStyle(newLine_colType)
                    newLine_color = (oc[f'MMACDLONG_{newLine_colType}_ColorR%{cgt}'],
                                     oc[f'MMACDLONG_{newLine_colType}_ColorG%{cgt}'],
                                     oc[f'MMACDLONG_{newLine_colType}_ColorB%{cgt}'],
                                     oc[f'MMACDLONG_{newLine_colType}_ColorA%{cgt}'])
                    if (currentLine_style is None) or (currentLine_style['color'] != newLine_color):
                        newLine_style = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                        newLine_style['color'] = newLine_color
                        dBox_g_this_dt1.addTextStyle(newLine_colType, newLine_style)
                #[3-3]: Text & Format Array Construction
                if value_display is None: textBlock = f" {line}: NONE"
                else:                     textBlock = f" {line}: {value_display:.{displayPrecision}f}"
                text_display += textBlock
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(line)+3),      'DEFAULT'))
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1), newLine_colType))

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)

    def __onPHU_DMIxADX(self):
        #[1]: Instances
        oc  = self.objectConfig
        ap  = self.analysisParams
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        klines    = self.klines
        siViewerIndex   = self.siTypes_siViewerAlloc['DMIxADX']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']


        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - DMIxADX]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        if oc['DMIxADX_Master']:
            for aCode in self.siTypes_analysisCodes['DMIxADX']:
                #[3-1]: Existence Check
                if tsHovered not in klines[aCode]: continue

                #[3-2]: Display Check
                lineIndex     = ap[aCode]['lineIndex']
                lineIndex_str = f"{lineIndex}"
                if not oc[f'DMIxADX_{lineIndex}_Display']: continue

                #[3-3]: TextStyle Check
                currentLine_style = dBox_g_this_dt1.getTextStyle(lineIndex_str)
                newLine_color = (oc[f'DMIxADX_{lineIndex}_ColorR%{cgt}'],
                                 oc[f'DMIxADX_{lineIndex}_ColorG%{cgt}'],
                                 oc[f'DMIxADX_{lineIndex}_ColorB%{cgt}'],
                                 oc[f'DMIxADX_{lineIndex}_ColorA%{cgt}'])
                if (currentLine_style is None) or (currentLine_style['color'] != newLine_color):
                    newLine_style = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                    newLine_style['color'] = newLine_color
                    dBox_g_this_dt1.addTextStyle(lineIndex_str, newLine_style)

                #[3-4]: Text & Format Array Construction
                value_dmixadx_absAthRel = klines[aCode][tsHovered]['DMIxADX_ABSATHREL']
                if value_dmixadx_absAthRel is None: textBlock = f" {aCode}: NONE"
                else:                               textBlock = f" {aCode}: {value_dmixadx_absAthRel:.2f}"
                text_display += textBlock
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(aCode)+3),     'DEFAULT'))
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1), lineIndex_str))

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)
        
    def __onPHU_MFI(self):
        #[1]: Instances
        oc  = self.objectConfig
        ap  = self.analysisParams
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        klines    = self.klines
        siViewerIndex   = self.siTypes_siViewerAlloc['MFI']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']


        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - MFI]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        if oc['MFI_Master']:
            for aCode in self.siTypes_analysisCodes['MFI']:
                #[3-1]: Existence Check
                if tsHovered not in klines[aCode]: continue

                #[3-2]: Display Check
                lineIndex     = ap[aCode]['lineIndex']
                lineIndex_str = f"{lineIndex}"
                if not oc[f'MFI_{lineIndex}_Display']: continue

                #[3-3]: TextStyle Check
                currentLine_style = dBox_g_this_dt1.getTextStyle(lineIndex_str)
                newLine_color = (oc[f'MFI_{lineIndex}_ColorR%{cgt}'],
                                 oc[f'MFI_{lineIndex}_ColorG%{cgt}'],
                                 oc[f'MFI_{lineIndex}_ColorB%{cgt}'],
                                 oc[f'MFI_{lineIndex}_ColorA%{cgt}'])
                if (currentLine_style is None) or (currentLine_style['color'] != newLine_color):
                    newLine_style = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                    newLine_style['color'] = newLine_color
                    dBox_g_this_dt1.addTextStyle(lineIndex_str, newLine_style)

                #[3-4]: Text & Format Array Construction
                value_mfiAbsAthRel = klines[aCode][tsHovered]['MFI_ABSATHREL']
                if value_mfiAbsAthRel is None: textBlock = f" {aCode}: NONE"
                else:                          textBlock = f" {aCode}: {value_mfiAbsAthRel:.2f}"
                text_display += textBlock
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(aCode)+3),     'DEFAULT'))
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1), lineIndex_str))

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)

    def __onPHU_WOI(self):
        pass

    def __onPHU_NES(self):
        pass

    def __updatePosSelection(self, updateType):
        #[1]: Instances
        dBox_g_vSIVs = self.displayBox_graphics_visibleSIViewers
        dBox_g = self.displayBox_graphics
        dBox_g_kl = dBox_g['KLINESPRICE']
        dBox_g_kl_phh = dBox_g_kl['POSHIGHLIGHT_HOVERED']
        dBox_g_kl_phs = dBox_g_kl['POSHIGHLIGHT_SELECTED']
        tsHovered, yHovered, dBox_current, dBox_previous = self.posHighlight_hoveredPos

        #[2]: By button press->release
        if updateType == 0:
            #[2-1]: Hovering Over No Box
            if dBox_current is None: return
            #[2-2]: If Selected The Same Position
            if tsHovered == self.posHighlight_selectedPos:
                self.posHighlight_selectedPos = None
                dBox_g_kl_phs.visible = False
                for dBoxName in dBox_g_vSIVs:
                    dBox_g_this_phs = dBox_g[dBoxName]['POSHIGHLIGHT_SELECTED']
                    dBox_g_this_phs.visible = False
            #[2-3]: If Selected A Different Position
            else:
                self.posHighlight_selectedPos = tsHovered
                shape_xPos  = dBox_g_kl_phh.x
                shape_width = dBox_g_kl_phh.width
                dBox_g_kl_phs.x       = shape_xPos
                dBox_g_kl_phs.width   = shape_width
                dBox_g_kl_phs.visible = True
                for dBoxName in dBox_g_vSIVs: 
                    dBox_g_this_phs = dBox_g[dBoxName]['POSHIGHLIGHT_SELECTED']
                    dBox_g_this_phs.x     = shape_xPos
                    dBox_g_this_phs.width = shape_width
                    dBox_g_this_phs.visible = True
            #[2-4]: Position Selection Update Response
            self.__onPosSelectionUpdate()

        #[3]: By HorizontalViewRange Update
        elif updateType == 1:
            #[3-1]: If No Position Was Selected, Do Nothing
            if self.posHighlight_selectedPos is None: return
            #[3-2]: Reposition Highlight Shapes
            tsPosEnd = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = self.posHighlight_selectedPos, mrktReg = self.mrktRegTS, nTicks = 1)
            pixelPerTS = dBox_g['MAINGRID_TEMPORAL']['DRAWBOX'][2]*self.scaler / (self.horizontalViewRange[1]-self.horizontalViewRange[0])
            shape_xPos  = round((self.posHighlight_selectedPos-self.verticalGrid_intervals[0])*pixelPerTS, 1)
            shape_width = round((tsPosEnd-self.posHighlight_selectedPos)*pixelPerTS,                       1)
            dBox_g_kl_phs.x     = shape_xPos
            dBox_g_kl_phs.width = shape_width
            for dBoxName in dBox_g_vSIVs: 
                dBox_g_this_phs = dBox_g[dBoxName]['POSHIGHLIGHT_SELECTED']
                dBox_g_this_phs.x     = shape_xPos
                dBox_g_this_phs.width = shape_width

    def __onPosSelectionUpdate(self):
        ph_selPos = self.posHighlight_selectedPos
        kl        = self.klines
        dQueue    = self.klines_drawQueue
        #IVP Update
        if 'IVP' in self.analysisParams:
            if   ph_selPos is None: self.__klineDrawer_RemoveDrawings(analysisCode = 'IVP', gRemovalSignal = 0b01)
            elif ph_selPos in kl['IVP']: 
                if ph_selPos in dQueue: 
                    if 'IVP' in dQueue[ph_selPos]: 
                        if dQueue[ph_selPos]['IVP'] is not None: dQueue[ph_selPos]['IVP'] |= 0b01
                    else:                                        dQueue[ph_selPos]['IVP'] = 0b01
                else:                                            dQueue[ph_selPos] = {'IVP': 0b01}
        #SWING Update
        for lineIndex in range (_NMAXLINES['SWING']):
            aCode = f'SWING_{lineIndex}'
            if aCode in self.analysisParams:
                if ph_selPos is None: self.__klineDrawer_RemoveDrawings(analysisCode = aCode, gRemovalSignal = 0b1)
                elif ph_selPos in kl[aCode]:
                    if ph_selPos in dQueue: 
                        if aCode in dQueue[ph_selPos]: 
                            if dQueue[ph_selPos][aCode] is not None: dQueue[ph_selPos][aCode] |= 0b1
                        else:                                        dQueue[ph_selPos][aCode] = 0b1
                    else:                                            dQueue[ph_selPos] = {aCode: 0b1}

    def handleKeyEvent(self, event):
        if (self.hidden == False):
            if (self.mouse_lastSelectedSection == 'SETTINGSSUBPAGE'): self.settingsSubPages[self.settingsSubPage_Current].handleKeyEvent(event)
    #User Interaction Control END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Basic Object Control -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def show(self):
        self.hidden = False

        for dBoxName in self.frameSprites: 
            self.frameSprites[dBoxName].visible = True

            if dBoxName == 'MAINGRID_TEMPORAL':
                self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'].visible = True

            elif dBoxName == 'KLINESPRICE':
                self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].visible = True
                self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'].visible = True
                self.displayBox_graphics[dBoxName]['ANALYSISDISPLAY_CAMGROUP'].visible = True
                self.displayBox_graphics[dBoxName]['RCLCG'].show()
                self.displayBox_graphics[dBoxName]['RCLCG_XFIXED'].show()
                self.displayBox_graphics[dBoxName]['RCLCG_YFIXED'].show()
                self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT1'].show()
                self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT2'].show()
                self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT3'].show()

            elif dBoxName == 'MAINGRID_KLINESPRICE':
                self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].visible = True

            elif dBoxName.startswith('SIVIEWER'):
                siViewerIndex = int(dBoxName[8:])
                if self.objectConfig[f'SIVIEWER{siViewerIndex}Display']:
                    self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].visible = True
                    self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'].visible = True
                    self.displayBox_graphics[dBoxName]['RCLCG'].show()
                    self.displayBox_graphics[dBoxName]['RCLCG_XFIXED'].show()
                    self.displayBox_graphics[dBoxName]['RCLCG_YFIXED'].show()
                    self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT1'].show()

            elif (dBoxName.startswith('MAINGRID_SIVIEWER')):
                siViewerIndex = int(dBoxName[17:])
                if self.objectConfig[f'SIVIEWER{siViewerIndex}Display']: 
                    self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].visible = True

        if self.settingsSubPage_Opened: 
            self.settingsSubPages[self.settingsSubPage_Current].show()

        if (not self.klines_fetchComplete and self.klines_fetching) or (self.chartDrawerType == 'TLVIEWER' and self.analysisQueue_list):
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

        for dBoxName in self.frameSprites: 
            self.frameSprites[dBoxName].visible = False

            if dBoxName == 'MAINGRID_TEMPORAL':
                self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'].visible = False

            elif dBoxName == 'KLINESPRICE':
                self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].visible = False
                self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'].visible = False
                self.displayBox_graphics[dBoxName]['ANALYSISDISPLAY_CAMGROUP'].visible = False
                self.displayBox_graphics[dBoxName]['RCLCG'].hide()
                self.displayBox_graphics[dBoxName]['RCLCG_XFIXED'].hide()
                self.displayBox_graphics[dBoxName]['RCLCG_YFIXED'].hide()
                self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT1'].hide()
                self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT2'].hide()
                self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT3'].hide()

            elif dBoxName == 'MAINGRID_KLINESPRICE':
                self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].visible = False

            elif dBoxName.startswith('SIVIEWER'):
                self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].visible = False
                self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'].visible = False
                self.displayBox_graphics[dBoxName]['RCLCG'].hide()
                self.displayBox_graphics[dBoxName]['RCLCG_XFIXED'].hide()
                self.displayBox_graphics[dBoxName]['RCLCG_YFIXED'].hide()
                self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT1'].hide()

            elif dBoxName.startswith('MAINGRID_SIVIEWER'):
                self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].visible = False

        self.settingsSubPages[self.settingsSubPage_Current].hide()
        self.frameSprites['KLINELOADINGCOVER'].visible = False
        self.klinesLoadingGaugeBar.hide()
        self.klinesLoadingTextBox.hide()
        self.klinesLoadingTextBox_perc.hide()

    def isHidden(self): 
        return self.hidden
        
    def moveTo(self, x, y):
        dx = x-self.xPos
        dy = y-self.yPos
        self.xPos = x
        self.yPos = y

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
        self.width  = width
        self.height = height
        #Set SubIndicator Switch Activation
        self.usableSIViewers = min([int((self.height-_GD_OBJECT_MINHEIGHT-(_GD_DISPLAYBOX_AUXILLARYBAR_HEIGHT+_GD_DISPLAYBOX_GOFFSET))/(_GD_DISPLAYBOX_SIVIEWER_HEIGHT+_GD_DISPLAYBOX_GOFFSET)), len(_SITYPES)])
        for siViewerIndex in range (len(_SITYPES)):
            if siViewerIndex < self.usableSIViewers:
                self.settingsSubPages['MAIN'].GUIOs[f"SUBINDICATOR_SHOW{siViewerIndex}"].activate()
                self.settingsSubPages['MAIN'].GUIOs[f"SUBINDICATOR_SELECTION{siViewerIndex}"].activate()
                self.settingsSubPages['MAIN'].GUIOs[f"SUBINDICATOR_SHOW{siViewerIndex}"].setStatus(self.objectConfig[f'SI{siViewerIndex}Display'] == True)
            else:
                self.settingsSubPages['MAIN'].GUIOs[f"SUBINDICATOR_SHOW{siViewerIndex}"].deactivate()
                self.settingsSubPages['MAIN'].GUIOs[f"SUBINDICATOR_SELECTION{siViewerIndex}"].deactivate()
                self.settingsSubPages['MAIN'].GUIOs[f"SUBINDICATOR_SHOW{siViewerIndex}"].setStatus(False)
        self.__setDisplayBoxDimensions()
        for settingsSubPageName in self.settingsSubPages: self.settingsSubPages[settingsSubPageName].resize(width = 3700, height = self.height-100)
        self.hitBox_Object.resize(width = self.width, height = self.height)

    def isTouched(self, mouseX, mouseY):
        if self.hidden: return False
        return self.hitBox_Object.isTouched(mouseX, mouseY)

    def setName(self, name): 
        self.name = name

    def getName(self): 
        return self.name

    def on_GUIThemeUpdate(self, **kwargs):
        #Bring in updated textStyle and colors
        cgt = self.visualManager.getGUITheme()
        self.currentGUITheme = cgt

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
            if self.displayBox[displayBoxName] is not None:
                if displayBoxName == 'SETTINGSBUTTONFRAME':
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
            if displayBoxName == 'KLINESPRICE':
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

            elif displayBoxName[:8] == 'SIVIEWER':
                siIndex = int(displayBoxName[8:])
                dBoxName          = f'SIVIEWER{siIndex}'
                dBoxName_MAINGRID = f'MAINGRID_SIVIEWER{siIndex}'

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
        oc = self.objectConfig
        if (True): #<--- Placed simply for a better readability
            #<TRADELOG>
            self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_BUY_LED"].updateColor(oc[f'TRADELOG_BUY_ColorR%{cgt}'], 
                                                                                     oc[f'TRADELOG_BUY_ColorG%{cgt}'], 
                                                                                     oc[f'TRADELOG_BUY_ColorB%{cgt}'], 
                                                                                     oc[f'TRADELOG_BUY_ColorA%{cgt}'])
            self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_SELL_LED"].updateColor(oc[f'TRADELOG_SELL_ColorR%{cgt}'], 
                                                                                      oc[f'TRADELOG_SELL_ColorG%{cgt}'], 
                                                                                      oc[f'TRADELOG_SELL_ColorB%{cgt}'], 
                                                                                      oc[f'TRADELOG_SELL_ColorA%{cgt}'])
            self.__onSettingsContentUpdate(self.settingsSubPages['MAIN'].GUIOs["TRADELOGCOLOR_TARGETSELECTION"])
            #<BIDS AND ASKS>
            self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_BIDS_LED"].updateColor(oc[f'BIDSANDASKS_BIDS_ColorR%{cgt}'], 
                                                                                         oc[f'BIDSANDASKS_BIDS_ColorG%{cgt}'], 
                                                                                         oc[f'BIDSANDASKS_BIDS_ColorB%{cgt}'], 
                                                                                         oc[f'BIDSANDASKS_BIDS_ColorA%{cgt}'])
            self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_ASKS_LED"].updateColor(oc[f'BIDSANDASKS_ASKS_ColorR%{cgt}'], 
                                                                                         oc[f'BIDSANDASKS_ASKS_ColorG%{cgt}'], 
                                                                                         oc[f'BIDSANDASKS_ASKS_ColorB%{cgt}'], 
                                                                                         oc[f'BIDSANDASKS_ASKS_ColorA%{cgt}'])
            self.__onSettingsContentUpdate(self.settingsSubPages['MAIN'].GUIOs["BIDSANDASKSCOLOR_TARGETSELECTION"])
            #<MAs>
            for miType in ('SMA','WMA','EMA'):
                for lineIndex in range (_NMAXLINES[miType]):
                    self.settingsSubPages[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}_LINECOLOR"].updateColor(oc[f'{miType}_{lineIndex}_ColorR%{cgt}'], 
                                                                                                                oc[f'{miType}_{lineIndex}_ColorG%{cgt}'], 
                                                                                                                oc[f'{miType}_{lineIndex}_ColorB%{cgt}'], 
                                                                                                                oc[f'{miType}_{lineIndex}_ColorA%{cgt}'])
                self.__onSettingsContentUpdate(self.settingsSubPages[miType].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<PSAR>
            for lineIndex in range (_NMAXLINES['PSAR']):
                self.settingsSubPages['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}_LINECOLOR"].updateColor(oc[f'PSAR_{lineIndex}_ColorR%{cgt}'], 
                                                                                                        oc[f'PSAR_{lineIndex}_ColorG%{cgt}'], 
                                                                                                        oc[f'PSAR_{lineIndex}_ColorB%{cgt}'], 
                                                                                                        oc[f'PSAR_{lineIndex}_ColorA%{cgt}'])
            self.__onSettingsContentUpdate(self.settingsSubPages['PSAR'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<BOL>
            for lineIndex in range (_NMAXLINES['BOL']):
                self.settingsSubPages['BOL'].GUIOs[f"INDICATOR_BOL{lineIndex}_LINECOLOR"].updateColor(oc[f'BOL_{lineIndex}_ColorR%{cgt}'], 
                                                                                                      oc[f'BOL_{lineIndex}_ColorG%{cgt}'], 
                                                                                                      oc[f'BOL_{lineIndex}_ColorB%{cgt}'], 
                                                                                                      oc[f'BOL_{lineIndex}_ColorA%{cgt}'])
            self.__onSettingsContentUpdate(self.settingsSubPages['BOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<IVP>
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_VPLP_COLOR"].updateColor(oc[f'IVP_VPLP_ColorR%{cgt}'],
                                                                                   oc[f'IVP_VPLP_ColorG%{cgt}'],
                                                                                   oc[f'IVP_VPLP_ColorB%{cgt}'],
                                                                                   oc[f'IVP_VPLP_ColorA%{cgt}'])
            self.settingsSubPages['IVP'].GUIOs["INDICATOR_VPLPB_COLOR"].updateColor(oc[f'IVP_VPLPB_ColorR%{cgt}'],
                                                                                    oc[f'IVP_VPLPB_ColorG%{cgt}'],
                                                                                    oc[f'IVP_VPLPB_ColorB%{cgt}'],
                                                                                    oc[f'IVP_VPLPB_ColorA%{cgt}'])
            self.__onSettingsContentUpdate(self.settingsSubPages['IVP'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<VOL>
            for lineIndex in range (_NMAXLINES['VOL']):
                self.settingsSubPages['VOL'].GUIOs[f"INDICATOR_VOL{lineIndex}_LINECOLOR"].updateColor(oc[f'VOL_{lineIndex}_ColorR%{cgt}'], 
                                                                                                      oc[f'VOL_{lineIndex}_ColorG%{cgt}'], 
                                                                                                      oc[f'VOL_{lineIndex}_ColorB%{cgt}'], 
                                                                                                      oc[f'VOL_{lineIndex}_ColorA%{cgt}'])
            self.__onSettingsContentUpdate(self.settingsSubPages['VOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<MMACDSHORT>
            for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM+', 'HISTOGRAM-'):
                self.settingsSubPages['MMACDSHORT'].GUIOs[f"INDICATOR_{targetLine}_COLOR"].updateColor(oc[f'MMACDSHORT_{targetLine}_ColorR%{cgt}'], 
                                                                                                       oc[f'MMACDSHORT_{targetLine}_ColorG%{cgt}'], 
                                                                                                       oc[f'MMACDSHORT_{targetLine}_ColorB%{cgt}'], 
                                                                                                       oc[f'MMACDSHORT_{targetLine}_ColorA%{cgt}'])
            self.__onSettingsContentUpdate(self.settingsSubPages['MMACDSHORT'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<MMACDLONG>
            for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM+', 'HISTOGRAM-'):
                self.settingsSubPages['MMACDLONG'].GUIOs[f"INDICATOR_{targetLine}_COLOR"].updateColor(oc[f'MMACDLONG_{targetLine}_ColorR%{cgt}'], 
                                                                                                      oc[f'MMACDLONG_{targetLine}_ColorG%{cgt}'], 
                                                                                                      oc[f'MMACDLONG_{targetLine}_ColorB%{cgt}'], 
                                                                                                      oc[f'MMACDLONG_{targetLine}_ColorA%{cgt}'])
            self.__onSettingsContentUpdate(self.settingsSubPages['MMACDLONG'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<DMIxADX>
            for lineIndex in range (_NMAXLINES['DMIxADX']):
                self.settingsSubPages['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}_LINECOLOR"].updateColor(oc[f'DMIxADX_{lineIndex}_ColorR%{cgt}'], 
                                                                                                              oc[f'DMIxADX_{lineIndex}_ColorG%{cgt}'], 
                                                                                                              oc[f'DMIxADX_{lineIndex}_ColorB%{cgt}'], 
                                                                                                              oc[f'DMIxADX_{lineIndex}_ColorA%{cgt}'])
            self.__onSettingsContentUpdate(self.settingsSubPages['DMIxADX'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<MFI>
            for lineIndex in range (_NMAXLINES['MFI']):
                self.settingsSubPages['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}_LINECOLOR"].updateColor(oc[f'MFI_{lineIndex}_ColorR%{cgt}'], 
                                                                                                      oc[f'MFI_{lineIndex}_ColorG%{cgt}'], 
                                                                                                      oc[f'MFI_{lineIndex}_ColorB%{cgt}'], 
                                                                                                      oc[f'MFI_{lineIndex}_ColorA%{cgt}'])
            self.__onSettingsContentUpdate(self.settingsSubPages['MFI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<WOI>
            for line in ('BASE+', 'BASE-'):
                self.settingsSubPages['WOI'].GUIOs[f"INDICATOR_WOI{line}_LINECOLOR"].updateColor(oc[f'WOI_{line}_ColorR%{cgt}'], 
                                                                                                 oc[f'WOI_{line}_ColorG%{cgt}'], 
                                                                                                 oc[f'WOI_{line}_ColorB%{cgt}'], 
                                                                                                 oc[f'WOI_{line}_ColorA%{cgt}'])
            for lineIndex in range (_NMAXLINES['WOI']):
                self.settingsSubPages['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_LINECOLOR"].updateColor(oc[f'WOI_{lineIndex}_ColorR%{cgt}'], 
                                                                                                      oc[f'WOI_{lineIndex}_ColorG%{cgt}'], 
                                                                                                      oc[f'WOI_{lineIndex}_ColorB%{cgt}'], 
                                                                                                      oc[f'WOI_{lineIndex}_ColorA%{cgt}'])
            self.__onSettingsContentUpdate(self.settingsSubPages['WOI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
            #<NES>
            for line in ('BASE+', 'BASE-'):
                self.settingsSubPages['NES'].GUIOs[f"INDICATOR_NES{line}_LINECOLOR"].updateColor(oc[f'NES_{line}_ColorR%{cgt}'], 
                                                                                                 oc[f'NES_{line}_ColorG%{cgt}'], 
                                                                                                 oc[f'NES_{line}_ColorB%{cgt}'], 
                                                                                                 oc[f'NES_{line}_ColorA%{cgt}'])
            for lineIndex in range (_NMAXLINES['NES']):
                self.settingsSubPages['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_LINECOLOR"].updateColor(oc[f'NES_{lineIndex}_ColorR%{cgt}'], 
                                                                                                      oc[f'NES_{lineIndex}_ColorG%{cgt}'], 
                                                                                                      oc[f'NES_{lineIndex}_ColorB%{cgt}'], 
                                                                                                      oc[f'NES_{lineIndex}_ColorA%{cgt}'])
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

    def __onSettingsNavButtonClick(self, objectInstance):
        #[1]: Navigation Coordinates
        buttonName = objectInstance.getName()
        ssp_prev = self.settingsSubPage_Current
        if   buttonName == 'navButton_toHome':    ssp_new = 'MAIN'
        elif buttonName.startswith('navButton_'): ssp_new = buttonName.split("_")[2]
        else: return

        #[2]: Subpages Update
        self.settingsSubPages[ssp_prev].hide()
        self.settingsSubPages[ssp_new].show()
        self.settingsSubPage_Current = ssp_new
        
    def __onSettingsContentUpdate(self, objectInstnace):
        #Parameters
        guioName       = objectInstnace.getName()
        guioName_split = guioName.split("_")
        indicatorType  = guioName_split[0]

        ssps = self.settingsSubPages
        oc   = self.objectConfig
        cgt  = self.currentGUITheme

        activateSaveConfigButton = False

        #Subpage 'MAIN'
        if indicatorType == 'MAIN':
            setterType = guioName_split[1]
            if (setterType == 'KLINECOLORTYPE'):
                self.updateKlineColors(newType = ssps['MAIN'].GUIOs['AUX_KLINECOLORTYPE_SELECTIONBOX'].getSelected())
                activateSaveConfigButton = True
            elif (setterType == 'TIMEZONE'):
                self.updateTimeZone(newTimeZone = ssps['MAIN'].GUIOs['AUX_TIMEZONE_SELECTIONBOX'].getSelected())
                activateSaveConfigButton = True
            elif (setterType == 'SAVECONFIG'):
                self.sysFunc_editGUIOConfig(configName = self.name, targetContent = oc.copy())
                ssps['MAIN'].GUIOs["AUX_SAVECONFIGURATION"].deactivate()
            elif (setterType == 'INDICATORSWITCH'):
                aType = guioName_split[2]
                self.__onSettingsContentUpdate(ssps[aType].GUIOs["APPLYNEWSETTINGS"])
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis: 
                    ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'SIVIEWERDISPLAYSWITCH'):
                #Set SIViewerDisplay
                siViewerIndex   = int(guioName_split[2])
                siViewerDisplay = ssps['MAIN'].GUIOs[f"SUBINDICATOR_DISPLAYSWITCH{siViewerIndex}"].getStatus()
                self.__setSIViewerDisplay(siViewerIndex   = siViewerIndex, 
                                          siViewerDisplay = siViewerDisplay)
                #Activate Configuration Save Button
                activateSaveConfigButton = True
            elif (setterType == 'SIVIEWERDISPLAYSELECTION'):
                #Set SIViewer Display Target and Retreive the Swapped SIViewerIndex
                siViewerIndex1         = int(guioName_split[2])
                siViewerDisplayTarget1 = ssps['MAIN'].GUIOs[f"SUBINDICATOR_DISPLAYSELECTION{siViewerIndex1}"].getSelected()
                siViewerIndex2         = self.__setSIViewerDisplayTarget(siViewerIndex1 = siViewerIndex1, siViewerDisplayTarget1 = siViewerDisplayTarget1)
                siViewerDisplayTarget2 = oc[f'SIVIEWER{siViewerIndex2}SIAlloc']
                #Update GUIO for the Swapped SIViewer
                ssps['MAIN'].GUIOs[f"SUBINDICATOR_DISPLAYSELECTION{siViewerIndex2}"].setSelected(siViewerDisplayTarget2, callSelectionUpdateFunction = False)
                #Activate Configuration Save Button
                activateSaveConfigButton = True
            elif (setterType == 'ANALYSISRANGETEXTINPUTBOX'):
                try:    rangeBeg = int(datetime.strptime(ssps['MAIN'].GUIOs["ANALYZER_ANALYSISRANGEBEG_RANGEINPUT"].getText(), "%Y/%m/%d %H:%M").timestamp()-time.timezone)
                except: rangeBeg = None
                try:    rangeEnd = int(datetime.strptime(ssps['MAIN'].GUIOs["ANALYZER_ANALYSISRANGEEND_RANGEINPUT"].getText(), "%Y/%m/%d %H:%M").timestamp()-time.timezone)
                except: rangeEnd = None
                oc['AnalysisRangeBeg'] = rangeBeg
                oc['AnalysisRangeEnd'] = rangeEnd
                if self.chartDrawerType == 'ANALYZER': self.__Analyzer_checkIfCanPerformAnalysis()
                activateSaveConfigButton = True
            elif (setterType == 'STARTANALYSIS'):
                ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].deactivate()
                self.neuralNetworkConnectionDataRequestIDs = dict()
                self.neuralNetworkInstances                = dict()
                gc.collect()
                torch.cuda.empty_cache()
                #NNA Codes Collection
                nns_prd  = self.ipcA.getPRD(processName = 'NEURALNETWORKMANAGER', prdAddress = 'NEURALNETWORKS')
                nn_codes = set()
                if oc['NNA_Master']:
                    for lineIndex in range (_NMAXLINES['NNA']):
                        nn_lineActive = oc[f'NNA_{lineIndex}_LineActive']
                        nn_code       = oc[f'NNA_{lineIndex}_NeuralNetworkCode']
                        if not nn_lineActive:      continue
                        if nn_code is None:        continue
                        if nn_code not in nns_prd: continue
                        nn_codes.add(nn_code)
                if nn_codes: self.__Analyzer_requestNeuralNetworksConnectionsData(neuralNetworkCodes = nn_codes)
                else:        self.__Analyzer_startAnalysis()
        #---Trade Log
        if indicatorType == 'TRADELOG':
            setterType = guioName_split[1]
            if (setterType == 'LineSelectionBox'):
                lineSelected = ssps['MAIN'].GUIOs["TRADELOGCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps['MAIN'].GUIOs[f"TRADELOGCOLOR_{lineSelected}_LED"].getColor()
                ssps['MAIN'].GUIOs['TRADELOGCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps['MAIN'].GUIOs["TRADELOGCOLOR_R_VALUE"].updateText(text = f"{color_r}")
                ssps['MAIN'].GUIOs["TRADELOGCOLOR_G_VALUE"].updateText(text = f"{color_g}")
                ssps['MAIN'].GUIOs["TRADELOGCOLOR_B_VALUE"].updateText(text = f"{color_b}")
                ssps['MAIN'].GUIOs["TRADELOGCOLOR_A_VALUE"].updateText(text = f"{color_a}")
                ssps['MAIN'].GUIOs['TRADELOGCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps['MAIN'].GUIOs['TRADELOGCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps['MAIN'].GUIOs['TRADELOGCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps['MAIN'].GUIOs['TRADELOGCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps['MAIN'].GUIOs['TRADELOGCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):
                cType = guioName_split[2]
                ssps['MAIN'].GUIOs['TRADELOGCOLOR_LED'].updateColor(rValue = int(ssps['MAIN'].GUIOs['TRADELOGCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                    gValue = int(ssps['MAIN'].GUIOs['TRADELOGCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                    bValue = int(ssps['MAIN'].GUIOs['TRADELOGCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                    aValue = int(ssps['MAIN'].GUIOs['TRADELOGCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps['MAIN'].GUIOs[f'TRADELOGCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps['MAIN'].GUIOs[f"TRADELOGCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps['MAIN'].GUIOs['TRADELOGCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):
                lineSelected = ssps['MAIN'].GUIOs["TRADELOGCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps['MAIN'].GUIOs['TRADELOGCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps['MAIN'].GUIOs['TRADELOGCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps['MAIN'].GUIOs['TRADELOGCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps['MAIN'].GUIOs['TRADELOGCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps['MAIN'].GUIOs[f"TRADELOGCOLOR_{lineSelected}_LED"].updateColor(color_r, color_g, color_b, color_a)
                ssps['MAIN'].GUIOs['TRADELOGCOLOR_APPLYCOLOR'].deactivate()
                ssps['MAIN'].GUIOs["TRADELOG_APPLYNEWSETTINGS"].activate()
            elif (setterType == 'DisplaySwitch'):
                ssps['MAIN'].GUIOs["TRADELOG_APPLYNEWSETTINGS"].activate()
            elif (setterType == 'ApplySettings'):
                #UpdateTracker Initialization
                updateTracker = False
                #Check for any changes in the configuration
                #---Buy Color
                buyColor_previous = (oc[f'TRADELOG_BUY_ColorR%{cgt}'], 
                                     oc[f'TRADELOG_BUY_ColorG%{cgt}'], 
                                     oc[f'TRADELOG_BUY_ColorB%{cgt}'], 
                                     oc[f'TRADELOG_BUY_ColorA%{cgt}'])
                color_r, color_g, color_b, color_a = ssps['MAIN'].GUIOs["TRADELOGCOLOR_BUY_LED"].getColor()
                oc[f'TRADELOG_BUY_ColorR%{cgt}'] = color_r
                oc[f'TRADELOG_BUY_ColorG%{cgt}'] = color_g
                oc[f'TRADELOG_BUY_ColorB%{cgt}'] = color_b
                oc[f'TRADELOG_BUY_ColorA%{cgt}'] = color_a
                if (buyColor_previous != (color_r, color_g, color_b, color_a)): updateTracker = True
                #---Sell Color
                sellColor_previous = (oc[f'TRADELOG_SELL_ColorR%{cgt}'], 
                                      oc[f'TRADELOG_SELL_ColorG%{cgt}'], 
                                      oc[f'TRADELOG_SELL_ColorB%{cgt}'], 
                                      oc[f'TRADELOG_SELL_ColorA%{cgt}'])
                color_r, color_g, color_b, color_a = ssps['MAIN'].GUIOs["TRADELOGCOLOR_SELL_LED"].getColor()
                oc[f'TRADELOG_SELL_ColorR%{cgt}'] = color_r
                oc[f'TRADELOG_SELL_ColorG%{cgt}'] = color_g
                oc[f'TRADELOG_SELL_ColorB%{cgt}'] = color_b
                oc[f'TRADELOG_SELL_ColorA%{cgt}'] = color_a
                if (sellColor_previous != (color_r, color_g, color_b, color_a)): updateTracker = True
                #---Display
                display_previous = oc['TRADELOG_Display']
                oc['TRADELOG_Display'] = ssps['MAIN'].GUIOs["TRADELOGDISPLAY_SWITCH"].getStatus()
                if display_previous != oc['TRADELOG_Display']: updateTracker = True
                #Queue Update
                if updateTracker:
                    self.__klineDrawer_RemoveDrawings(analysisCode = 'TRADELOG', gRemovalSignal = _FULLDRAWSIGNALS['TRADELOG']) #Remove previous graphics
                    self.__addBufferZone_toDrawQueue(analysisCode  = 'TRADELOG', drawSignal     = _FULLDRAWSIGNALS['TRADELOG']) #Update draw queue
                #Control Buttons Handling
                ssps['MAIN'].GUIOs["TRADELOG_APPLYNEWSETTINGS"].deactivate()
                activateSaveConfigButton = True
        #---Bids and Asks
        if indicatorType == 'BIDSANDASKS':
            setterType = guioName_split[1]
            if (setterType == 'LineSelectionBox'):
                lineSelected = ssps['MAIN'].GUIOs["BIDSANDASKSCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps['MAIN'].GUIOs[f"BIDSANDASKSCOLOR_{lineSelected}_LED"].getColor()
                ssps['MAIN'].GUIOs['BIDSANDASKSCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps['MAIN'].GUIOs["BIDSANDASKSCOLOR_R_VALUE"].updateText(text = f"{color_r}")
                ssps['MAIN'].GUIOs["BIDSANDASKSCOLOR_G_VALUE"].updateText(text = f"{color_g}")
                ssps['MAIN'].GUIOs["BIDSANDASKSCOLOR_B_VALUE"].updateText(text = f"{color_b}")
                ssps['MAIN'].GUIOs["BIDSANDASKSCOLOR_A_VALUE"].updateText(text = f"{color_a}")
                ssps['MAIN'].GUIOs['BIDSANDASKSCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps['MAIN'].GUIOs['BIDSANDASKSCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps['MAIN'].GUIOs['BIDSANDASKSCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps['MAIN'].GUIOs['BIDSANDASKSCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps['MAIN'].GUIOs['BIDSANDASKSCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):
                cType = guioName_split[2]
                ssps['MAIN'].GUIOs['BIDSANDASKSCOLOR_LED'].updateColor(rValue = int(ssps['MAIN'].GUIOs['BIDSANDASKSCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                       gValue = int(ssps['MAIN'].GUIOs['BIDSANDASKSCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                       bValue = int(ssps['MAIN'].GUIOs['BIDSANDASKSCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                       aValue = int(ssps['MAIN'].GUIOs['BIDSANDASKSCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps['MAIN'].GUIOs[f'BIDSANDASKSCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps['MAIN'].GUIOs[f"BIDSANDASKSCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps['MAIN'].GUIOs['BIDSANDASKSCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):
                lineSelected = ssps['MAIN'].GUIOs["BIDSANDASKSCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps['MAIN'].GUIOs['BIDSANDASKSCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps['MAIN'].GUIOs['BIDSANDASKSCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps['MAIN'].GUIOs['BIDSANDASKSCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps['MAIN'].GUIOs['BIDSANDASKSCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps['MAIN'].GUIOs[f"BIDSANDASKSCOLOR_{lineSelected}_LED"].updateColor(color_r, color_g, color_b, color_a)
                ssps['MAIN'].GUIOs['BIDSANDASKSCOLOR_APPLYCOLOR'].deactivate()
                ssps['MAIN'].GUIOs["BIDSANDASKS_APPLYNEWSETTINGS"].activate()
            elif (setterType == 'DisplaySwitch'):
                ssps['MAIN'].GUIOs["BIDSANDASKS_APPLYNEWSETTINGS"].activate()
            elif (setterType == 'ApplySettings'):
                #UpdateTracker Initialization
                updateTracker = False
                #Check for any changes in the configuration
                #---Bids Color
                bidsColor_previous = (oc[f'BIDSANDASKS_BIDS_ColorR%{cgt}'], 
                                      oc[f'BIDSANDASKS_BIDS_ColorG%{cgt}'], 
                                      oc[f'BIDSANDASKS_BIDS_ColorB%{cgt}'], 
                                      oc[f'BIDSANDASKS_BIDS_ColorA%{cgt}'])
                color_r, color_g, color_b, color_a = ssps['MAIN'].GUIOs["BIDSANDASKSCOLOR_BIDS_LED"].getColor()
                oc[f'BIDSANDASKS_BIDS_ColorR%{cgt}'] = color_r
                oc[f'BIDSANDASKS_BIDS_ColorG%{cgt}'] = color_g
                oc[f'BIDSANDASKS_BIDS_ColorB%{cgt}'] = color_b
                oc[f'BIDSANDASKS_BIDS_ColorA%{cgt}'] = color_a
                if (bidsColor_previous != (color_r, color_g, color_b, color_a)): updateTracker = True
                #---Asks Color
                asksColor_previous = (oc[f'BIDSANDASKS_ASKS_ColorR%{cgt}'], 
                                      oc[f'BIDSANDASKS_ASKS_ColorG%{cgt}'], 
                                      oc[f'BIDSANDASKS_ASKS_ColorB%{cgt}'], 
                                      oc[f'BIDSANDASKS_ASKS_ColorA%{cgt}'])
                color_r, color_g, color_b, color_a = ssps['MAIN'].GUIOs["BIDSANDASKSCOLOR_ASKS_LED"].getColor()
                oc[f'BIDSANDASKS_ASKS_ColorR%{cgt}'] = color_r
                oc[f'BIDSANDASKS_ASKS_ColorG%{cgt}'] = color_g
                oc[f'BIDSANDASKS_ASKS_ColorB%{cgt}'] = color_b
                oc[f'BIDSANDASKS_ASKS_ColorA%{cgt}'] = color_a
                if asksColor_previous != (color_r, color_g, color_b, color_a): updateTracker = True
                #---Display
                display_previous = oc['BIDSANDASKS_Display']
                oc['BIDSANDASKS_Display'] = ssps['MAIN'].GUIOs["BIDSANDASKSDISPLAY_SWITCH"].getStatus()
                if display_previous != oc['BIDSANDASKS_Display']: updateTracker = True
                #Queue Update
                if updateTracker: 
                    self.__bidsAndAsksDrawer_Remove()
                    self.__bidsAndAsksDrawer_Draw()
                #Control Buttons Handling
                ssps['MAIN'].GUIOs["BIDSANDASKS_APPLYNEWSETTINGS"].deactivate()
                activateSaveConfigButton = True

        #Subpage 'SMA' 'WMA' 'EMA'
        elif indicatorType in ('SMA', 'WMA', 'EMA'):
            miType = indicatorType
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):    
                lineSelected = ssps[miType].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps[miType].GUIOs[f"INDICATOR_{miType}{lineSelected}_LINECOLOR"].getColor()
                ssps[miType].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps[miType].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                ssps[miType].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                ssps[miType].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                ssps[miType].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                ssps[miType].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps[miType].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps[miType].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps[miType].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps[miType].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):             
                cType = guioName_split[2]
                ssps[miType].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps[miType].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                     gValue = int(ssps[miType].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                     bValue = int(ssps[miType].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                     aValue = int(ssps[miType].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps[miType].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps[miType].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps[miType].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):        
                lineSelected = ssps[miType].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps[miType].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps[miType].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps[miType].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps[miType].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps[miType].GUIOs[f"INDICATOR_{miType}{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
                ssps[miType].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                ssps[miType].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'WidthTextInputBox'): 
                ssps[miType].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):     
                ssps[miType].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):     
                #UpdateTracker Initialization
                updateTracker = dict()
                #Check for any changes in the configuration
                for lineIndex in range (_NMAXLINES[miType]):
                    updateTracker[lineIndex] = False
                    #Width
                    width_previous = oc[f'{miType}_{lineIndex}_Width']
                    reset = False
                    try:
                        width = int(ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}_WIDTHINPUT"].getText())
                        if 0 < width: oc[f'{miType}_{lineIndex}_Width'] = width
                        else: reset = True
                    except: reset = True
                    if reset:
                        oc[f'{miType}_{lineIndex}_Width'] = 1
                        ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'{miType}_{lineIndex}_Width']))
                    if width_previous != oc[f'{miType}_{lineIndex}_Width']: updateTracker[lineIndex] = True
                    #Color
                    color_previous = (oc[f'{miType}_{lineIndex}_ColorR%{cgt}'], 
                                      oc[f'{miType}_{lineIndex}_ColorG%{cgt}'], 
                                      oc[f'{miType}_{lineIndex}_ColorB%{cgt}'], 
                                      oc[f'{miType}_{lineIndex}_ColorA%{cgt}'])
                    color_r, color_g, color_b, color_a = ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}_LINECOLOR"].getColor()
                    oc[f'{miType}_{lineIndex}_ColorR%{cgt}'] = color_r
                    oc[f'{miType}_{lineIndex}_ColorG%{cgt}'] = color_g
                    oc[f'{miType}_{lineIndex}_ColorB%{cgt}'] = color_b
                    oc[f'{miType}_{lineIndex}_ColorA%{cgt}'] = color_a
                    if (color_previous != (color_r, color_g, color_b, color_a)): updateTracker[lineIndex] = True
                    #Line Display
                    display_previous = oc[f'{miType}_{lineIndex}_Display']
                    oc[f'{miType}_{lineIndex}_Display'] = ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}_DISPLAY"].getStatus()
                    if display_previous != oc[f'{miType}_{lineIndex}_Display']: updateTracker[lineIndex] = True
                #MA Master
                maMaster_previous = oc[f'{miType}_Master']
                oc[f'{miType}_Master'] = ssps['MAIN'].GUIOs[f"MAININDICATOR_{miType}"].getStatus()
                if maMaster_previous != oc[f'{miType}_Master']:
                    for lineIndex in updateTracker: updateTracker[lineIndex] = True
                #Queue Update
                configuredMAs = set([aCode for aCode in self.analysisParams if aCode.startswith(miType)])
                for configuredMA in configuredMAs:
                    lineIndex = self.analysisParams[configuredMA]['lineIndex']
                    if not updateTracker[lineIndex]: continue
                    self.__klineDrawer_RemoveDrawings(analysisCode = configuredMA, gRemovalSignal = _FULLDRAWSIGNALS[miType]) #Remove previous graphics
                    self.__addBufferZone_toDrawQueue(analysisCode  = configuredMA, drawSignal     = _FULLDRAWSIGNALS[miType]) #Update draw queue
                #Control Buttons Handling
                ssps[miType].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'): 
                lineIndex = int(guioName_split[2])
                #Get new switch status
                _newStatus = ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}"].getStatus()
                oc[f'{miType}_{lineIndex}_LineActive'] = _newStatus
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER' and 
                    self.canStartAnalysis              and 
                    oc[f'{miType}_Master']
                    ): 
                    ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'): 
                lineIndex = int(guioName_split[2])
                #Get new nSamples
                try:    _nSamples = int(ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}_INTERVALINPUT"].getText())
                except: _nSamples = None
                #Save the new value to the object config dictionary
                oc[f'{miType}_{lineIndex}_NSamples'] = _nSamples
                #If needed, activate the start analysis button
                if ((self.chartDrawerType == 'ANALYZER')  and 
                    self.canStartAnalysis                 and 
                    oc[f'{miType}_Master'] and 
                    oc[f'{miType}_{lineIndex}_LineActive']
                    ): 
                    ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True

        #Subpage 'PSAR'
        elif indicatorType == 'PSAR':
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):    
                lineSelected = ssps['PSAR'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineSelected}_LINECOLOR"].getColor()
                ssps['PSAR'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps['PSAR'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                ssps['PSAR'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                ssps['PSAR'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                ssps['PSAR'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                ssps['PSAR'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps['PSAR'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps['PSAR'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps['PSAR'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps['PSAR'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):             
                cType = guioName_split[2]
                ssps['PSAR'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['PSAR'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                     gValue = int(ssps['PSAR'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                     bValue = int(ssps['PSAR'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                     aValue = int(ssps['PSAR'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps['PSAR'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps['PSAR'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps['PSAR'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):        
                lineSelected = ssps['PSAR'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps['PSAR'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps['PSAR'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps['PSAR'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps['PSAR'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
                ssps['PSAR'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                ssps['PSAR'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'WidthTextInputBox'): 
                ssps['PSAR'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):     
                ssps['PSAR'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):     
                #UpdateTracker Initialization
                updateTracker = dict()
                #Check for any changes in the configuration
                for lineIndex in range (_NMAXLINES['PSAR']):
                    updateTracker[lineIndex] = False
                    #Width
                    width_previous = oc[f'PSAR_{lineIndex}_Width']
                    reset = False
                    try:
                        width = int(ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}_WIDTHINPUT"].getText())
                        if 0 < width: oc[f'PSAR_{lineIndex}_Width'] = width
                        else: reset = True
                    except: reset = True
                    if reset:
                        oc[f'PSAR_{lineIndex}_Width'] = 1
                        ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'PSAR_{lineIndex}_Width']))
                    if width_previous != oc[f'PSAR_{lineIndex}_Width']: updateTracker[lineIndex] = True
                    #Color
                    color_previous = (oc[f'PSAR_{lineIndex}_ColorR%{cgt}'],
                                      oc[f'PSAR_{lineIndex}_ColorG%{cgt}'],
                                      oc[f'PSAR_{lineIndex}_ColorB%{cgt}'],
                                      oc[f'PSAR_{lineIndex}_ColorA%{cgt}'])
                    color_r, color_g, color_b, color_a = ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}_LINECOLOR"].getColor()
                    oc[f'PSAR_{lineIndex}_ColorR%{cgt}'] = color_r
                    oc[f'PSAR_{lineIndex}_ColorG%{cgt}'] = color_g
                    oc[f'PSAR_{lineIndex}_ColorB%{cgt}'] = color_b
                    oc[f'PSAR_{lineIndex}_ColorA%{cgt}'] = color_a
                    if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
                    #Line Display
                    display_previous = oc[f'PSAR_{lineIndex}_Display']
                    oc[f'PSAR_{lineIndex}_Display'] = ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}_DISPLAY"].getStatus()
                    if display_previous != oc[f'PSAR_{lineIndex}_Display']: updateTracker[lineIndex] = True
                #---PSAR Master
                psarMaster_previous = oc['PSAR_Master']
                oc['PSAR_Master'] = ssps['MAIN'].GUIOs["MAININDICATOR_PSAR"].getStatus()
                if psarMaster_previous != oc['PSAR_Master']:
                    for lineIndex in updateTracker: updateTracker[lineIndex] = True
                #Queue Update
                configuredPSARs = set(aCode for aCode in self.analysisParams if aCode.startswith('PSAR'))
                for configuredPSAR in configuredPSARs:
                    lineIndex = self.analysisParams[configuredPSAR]['lineIndex']
                    if updateTracker[lineIndex]:
                        self.__klineDrawer_RemoveDrawings(analysisCode = configuredPSAR, gRemovalSignal = _FULLDRAWSIGNALS['PSAR']) #Remove previous graphics
                        self.__addBufferZone_toDrawQueue(analysisCode  = configuredPSAR, drawSignal     = _FULLDRAWSIGNALS['PSAR']) #Update draw queue
                #Control Buttons Handling
                ssps['PSAR'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'): 
                lineIndex = int(guioName_split[2])
                #Get new switch status
                _newStatus = ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}"].getStatus()
                oc[f'PSAR_{lineIndex}_LineActive'] = _newStatus
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['PSAR_Master']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'AF0TextInputBox'):      
                lineIndex = int(guioName_split[2])
                #Get new AF0
                try:    _af0 = round(float(ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}_AF0INPUT"].getText()), 3)
                except: _af0 = None
                #Save the new value to the object config dictionary
                oc[f'PSAR_{lineIndex}_AF0'] = _af0
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['PSAR_Master'] and oc[f'PSAR_{lineIndex}_LineActive']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'AF+TextInputBox'):      
                lineIndex = int(guioName_split[2])
                #Get new AF+
                try:    _afAccel = round(float(ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}_AF+INPUT"].getText()), 3)
                except: _afAccel = None
                #Save the new value to the object config dictionary
                oc[f'PSAR_{lineIndex}_AF+'] = _afAccel
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['PSAR_Master'] and oc[f'PSAR_{lineIndex}_LineActive']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'AFMaxTextInputBox'):    
                lineIndex = int(guioName_split[2])
                #Get new AFMax
                try:    _afMax = round(float(ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}_AFMAXINPUT"].getText()), 3)
                except: _afMax = None
                #Save the new value to the object config dictionary
                oc[f'PSAR_{lineIndex}_AFMAX'] = _afMax
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['PSAR_Master'] and oc[f'PSAR_{lineIndex}_LineActive']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True

        #Subpage 'BOL'
        elif indicatorType == 'BOL':
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):        
                lineSelected = ssps['BOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineSelected}_LINECOLOR"].getColor()
                ssps['BOL'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps['BOL'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                ssps['BOL'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                ssps['BOL'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                ssps['BOL'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                ssps['BOL'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps['BOL'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps['BOL'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps['BOL'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps['BOL'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):                 
                cType = guioName_split[2]
                ssps['BOL'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['BOL'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                    gValue = int(ssps['BOL'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                    bValue = int(ssps['BOL'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                    aValue = int(ssps['BOL'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps['BOL'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps['BOL'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps['BOL'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):            
                lineSelected = ssps['BOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps['BOL'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps['BOL'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps['BOL'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps['BOL'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
                ssps['BOL'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                ssps['BOL'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'WidthTextInputBox'):     
                ssps['BOL'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):         
                ssps['BOL'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplayContentsSwitch'): 
                ssps['BOL'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):         
                #UpdateTracker Initialization
                updateTracker = dict()
                #Check for any changes in the configuration
                for lineIndex in range (_NMAXLINES['BOL']):
                    updateTracker[lineIndex] = [False, False] #[1]: Draw CenterLine, [2]: Draw Band
                    #Width
                    width_previous = oc[f'BOL_{lineIndex}_Width']
                    reset = False
                    try:
                        width = int(ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineIndex}_WIDTHINPUT"].getText())
                        if 0 < width: oc[f'BOL_{lineIndex}_Width'] = width
                        else: reset = True
                    except: reset = True
                    if reset == True:
                        oc[f'BOL_{lineIndex}_Width'] = 1
                        ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'BOL_{lineIndex}_Width']))
                    if (width_previous != oc[f'BOL_{lineIndex}_Width']): 
                        updateTracker[lineIndex][0] = True
                    #Color
                    color_previous = (oc[f'BOL_{lineIndex}_ColorR%{cgt}'],
                                      oc[f'BOL_{lineIndex}_ColorG%{cgt}'],
                                      oc[f'BOL_{lineIndex}_ColorB%{cgt}'],
                                      oc[f'BOL_{lineIndex}_ColorA%{cgt}'])
                    color_r, color_g, color_b, color_a = ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineIndex}_LINECOLOR"].getColor()
                    oc[f'BOL_{lineIndex}_ColorR%{cgt}'] = color_r
                    oc[f'BOL_{lineIndex}_ColorG%{cgt}'] = color_g
                    oc[f'BOL_{lineIndex}_ColorB%{cgt}'] = color_b
                    oc[f'BOL_{lineIndex}_ColorA%{cgt}'] = color_a
                    if (color_previous != (color_r, color_g, color_b, color_a)): 
                        updateTracker[lineIndex][0] = True
                        updateTracker[lineIndex][1] = True
                    #Line Display
                    display_previous = oc[f'BOL_{lineIndex}_Display']
                    oc[f'BOL_{lineIndex}_Display'] = ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineIndex}_DISPLAY"].getStatus()
                    if (display_previous != oc[f'BOL_{lineIndex}_Display']): 
                        updateTracker[lineIndex][0] = True
                        updateTracker[lineIndex][1] = True
                #---BOL Master
                bolMaster_previous = oc['BOL_Master']
                oc['BOL_Master'] = ssps['MAIN'].GUIOs["MAININDICATOR_BOL"].getStatus()
                if bolMaster_previous != oc['BOL_Master']:
                    for lineIndex in updateTracker: 
                        updateTracker[lineIndex][0] = True
                        updateTracker[lineIndex][1] = True
                #---CenterLine Display Switch
                display_bolCenter_previous = oc['BOL_DisplayCenterLine']
                oc['BOL_DisplayCenterLine'] = ssps['BOL'].GUIOs["INDICATOR_DISPLAYCONTENTS_BOLCENTERSWITCH"].getStatus()
                if display_bolCenter_previous != oc['BOL_DisplayCenterLine']: 
                    for lineIndex in updateTracker: updateTracker[lineIndex][0] = True
                #---Band Display Switch
                display_bolBand_previous = oc['BOL_DisplayBand']
                oc['BOL_DisplayBand'] = ssps['BOL'].GUIOs["INDICATOR_DISPLAYCONTENTS_BOLBANDSWITCH"].getStatus()
                if display_bolBand_previous != oc['BOL_DisplayBand']: 
                    for lineIndex in updateTracker: updateTracker[lineIndex][1] = True
                #Queue Update
                configuredBOLs = set(aCode for aCode in self.analysisParams if aCode.startswith == 'BOL')
                for configuredBOL in configuredBOLs:
                    lineIndex = self.analysisParams[configuredBOL]['lineIndex']
                    drawSignal = 0
                    drawSignal += 0b01*updateTracker[lineIndex][0] #CenterLine
                    drawSignal += 0b10*updateTracker[lineIndex][1] #Band
                    if drawSignal:
                        self.__klineDrawer_RemoveDrawings(analysisCode = configuredBOL, gRemovalSignal = drawSignal) #Remove previous graphics
                        self.__addBufferZone_toDrawQueue(analysisCode  = configuredBOL, drawSignal     = drawSignal) #Update draw queue
                #Control Buttons Handling
                ssps['BOL'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'):  
                lineIndex = int(guioName_split[2])
                #Get new switch status
                newStatus = ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineIndex}"].getStatus()
                oc[f'BOL_{lineIndex}_LineActive'] = newStatus
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['BOL_Master']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'):  
                lineIndex = int(guioName_split[2])
                #Get new nSamples
                try:    nSamples = int(ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineIndex}_INTERVALINPUT"].getText())
                except: nSamples = None
                #Save the new value to the object config dictionary
                oc[f'BOL_{lineIndex}_NSamples'] = nSamples
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['BOL_Master'] and oc[f'BOL_{lineIndex}_LineActive']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'BandWidthTextInputBox'): 
                lineIndex = int(guioName_split[2])
                #Get new bandwidth
                try:    bandWidth = int(ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineIndex}_BANDWIDTHINPUT"].getText())
                except: bandWidth = None
                #Save the new value to the object config dictionary
                oc[f'BOL_{lineIndex}_BandWidth'] = bandWidth
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['BOL_Master'] and oc[f'BOL_{lineIndex}_LineActive']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'MATypeSelection'): 
                #Get new MAType
                maType = ssps['BOL'].GUIOs["INDICATOR_MATYPESELECTION"].getSelected()
                #Save the new value to the object config dictionary
                oc['BOL_MAType'] = maType
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['BOL_Master']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True

        #Subpage 'IVP'
        elif indicatorType == 'IVP':
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):     
                lineSelected = ssps['IVP'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps['IVP'].GUIOs[f"INDICATOR_{lineSelected}_COLOR"].getColor()
                ssps['IVP'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps['IVP'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                ssps['IVP'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                ssps['IVP'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                ssps['IVP'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                ssps['IVP'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps['IVP'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps['IVP'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps['IVP'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps['IVP'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):              
                cType = guioName_split[2]
                ssps['IVP'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['IVP'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                    gValue = int(ssps['IVP'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                    bValue = int(ssps['IVP'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                    aValue = int(ssps['IVP'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps['IVP'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps['IVP'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps['IVP'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):         
                lineSelected = ssps['IVP'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps['IVP'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps['IVP'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps['IVP'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps['IVP'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps['IVP'].GUIOs[f"INDICATOR_{lineSelected}_COLOR"].updateColor(color_r, color_g, color_b, color_a)
                ssps['IVP'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                ssps['IVP'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplayWidthSlider'): 
                lineTarget = guioName_split[2]
                sliderValue = ssps['IVP'].GUIOs[f"INDICATOR_{lineTarget}_DISPLAYWIDTHSLIDER"].getSliderValue()
                ssps['IVP'].GUIOs[f"INDICATOR_{lineTarget}_DISPLAYWIDTHVALUETEXT"].updateText(str(round(sliderValue/100*0.9+0.1, 2)))
                ssps['IVP'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):      
                ssps['IVP'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'VPLPBDisplayRegion'): 
                #Get new VPLPBDisplayRegion
                sliderValue = ssps['IVP'].GUIOs["INDICATOR_VPLPB_DISPLAYREGIONSLIDER"].getSliderValue()
                drValue = sliderValue/100*0.950+0.050
                ssps['IVP'].GUIOs["INDICATOR_VPLPB_DISPLAYREGIONVALUETEXT"].updateText(f"{drValue*100:.1f} %")
                ssps['IVP'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):
                #UpdateTracker Initialization
                updateTracker = [False, False] #[0]: VPLP, [1]: VPLPB
                #Check for any changes in the configuration
                #---IVP Master
                ivpMaster_previous = oc['IVP_Master']
                oc['IVP_Master'] = ssps['MAIN'].GUIOs["MAININDICATOR_IVP"].getStatus()
                if ivpMaster_previous != oc['IVP_Master']: updateTracker = [True, True]
                #---displaySwitch - VPLP
                vplpDisplay_prev = oc['IVP_VPLP_Display']
                oc['IVP_VPLP_Display'] = ssps['IVP'].GUIOs["INDICATOR_VPLP_DISPLAYSWITCH"].getStatus()
                if vplpDisplay_prev != oc['IVP_VPLP_Display']: updateTracker[0] = True
                #---displaySwitch - VPLB
                vplpbDisplay_prev = oc['IVP_VPLPB_Display']
                oc['IVP_VPLPB_Display'] = ssps['IVP'].GUIOs["INDICATOR_VPLPB_DISPLAYSWITCH"].getStatus()
                if vplpbDisplay_prev != oc['IVP_VPLPB_Display']: updateTracker[1] = True
                #---displayWidth - VPLP
                vplpDisplayWidth_prev = oc['IVP_VPLP_DisplayWidth']
                oc['IVP_VPLP_DisplayWidth'] = round(ssps['IVP'].GUIOs["INDICATOR_VPLP_DISPLAYWIDTHSLIDER"].getSliderValue()/100*0.9+0.1, 2)
                if vplpDisplayWidth_prev != oc['IVP_VPLP_DisplayWidth']: updateTracker[0] = True
                #---VPLPB Display Region
                vplpbDisplayRegion_prev = oc['IVP_VPLPB_DisplayRegion']
                oc['IVP_VPLPB_DisplayRegion'] = round(ssps['IVP'].GUIOs["INDICATOR_VPLPB_DISPLAYREGIONSLIDER"].getSliderValue()/100*0.950+0.050, 3)
                if vplpbDisplayRegion_prev != oc['IVP_VPLPB_DisplayRegion']: updateTracker[1] = True
                #---Colors
                for targetLine in ('VPLP', 'VPLPB'):
                    color_previous = (oc[f'IVP_{targetLine}_ColorR%{cgt}'],
                                      oc[f'IVP_{targetLine}_ColorG%{cgt}'],
                                      oc[f'IVP_{targetLine}_ColorB%{cgt}'],
                                      oc[f'IVP_{targetLine}_ColorA%{cgt}'])
                    color_r, color_g, color_b, color_a = ssps['IVP'].GUIOs[f"INDICATOR_{targetLine}_COLOR"].getColor()
                    oc[f'IVP_{targetLine}_ColorR%{cgt}'] = color_r
                    oc[f'IVP_{targetLine}_ColorG%{cgt}'] = color_g
                    oc[f'IVP_{targetLine}_ColorB%{cgt}'] = color_b
                    oc[f'IVP_{targetLine}_ColorA%{cgt}'] = color_a
                    if color_previous != (color_r, color_g, color_b, color_a): 
                        if   targetLine == 'VPLP':  updateTracker[0] = True
                        elif targetLine == 'VPLPB': updateTracker[1] = True
                #Content Update Handling
                drawSignal = 0
                drawSignal += 0b01*updateTracker[0] #VPLP
                drawSignal += 0b10*updateTracker[1] #VPLPB
                if drawSignal:
                    self.__klineDrawer_RemoveDrawings(analysisCode = 'IVP', gRemovalSignal = drawSignal) #Remove previous graphics
                    self.__addBufferZone_toDrawQueue(analysisCode  = 'IVP', drawSignal     = drawSignal) #Update draw queue
                #Settings Control Button
                ssps['IVP'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'Interval'):
                #Get new nSamples
                try:    _nSamples = int(ssps['IVP'].GUIOs["INDICATOR_INTERVAL_INPUTTEXT"].getText())
                except: _nSamples = None
                #Save the new value to the object config dictionary
                oc['IVP_NSamples'] = _nSamples
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['IVP_Master']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'GammaFactor'):
                #Get new Gamma Factor
                gammaFactor = round(ssps['IVP'].GUIOs["INDICATOR_GAMMAFACTOR_SLIDER"].getSliderValue()/100*0.095+0.005, 3)
                ssps['IVP'].GUIOs["INDICATOR_GAMMAFACTOR_VALUETEXT"].updateText(f"{gammaFactor*100:.1f} %")
                oc['IVP_GammaFactor'] = gammaFactor
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['IVP_Master']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'DeltaFactor'):
                #Get new Delta Factor
                deltaFactor = round(ssps['IVP'].GUIOs["INDICATOR_DELTAFACTOR_SLIDER"].getSliderValue()/100*9.9+0.1, 1)
                ssps['IVP'].GUIOs["INDICATOR_DELTAFACTOR_VALUETEXT"].updateText(f"{int(deltaFactor*100)} %")
                oc['IVP_DeltaFactor'] = deltaFactor
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['IVP_Master']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
        
        #Subpage 'SWING'
        elif indicatorType == 'SWING':
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):    
                lineSelected = ssps['SWING'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineSelected}_LINECOLOR"].getColor()
                ssps['SWING'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps['SWING'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                ssps['SWING'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                ssps['SWING'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                ssps['SWING'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                ssps['SWING'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps['SWING'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps['SWING'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps['SWING'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps['SWING'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):             
                cType = guioName_split[2]
                ssps['SWING'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['SWING'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                      gValue = int(ssps['SWING'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                      bValue = int(ssps['SWING'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                      aValue = int(ssps['SWING'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps['SWING'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps['SWING'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps['SWING'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):        
                lineSelected = ssps['SWING'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps['SWING'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps['SWING'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps['SWING'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps['SWING'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
                ssps['SWING'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                ssps['SWING'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'WidthTextInputBox'): 
                ssps['SWING'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):     
                ssps['SWING'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):     
                #UpdateTracker Initialization
                updateTracker = dict()
                #Check for any changes in the configuration
                for lineIndex in range (_NMAXLINES['SWING']):
                    updateTracker[lineIndex] = False
                    #Width
                    width_previous = oc[f'SWING_{lineIndex}_Width']
                    reset = False
                    try:
                        width = int(ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineIndex}_WIDTHINPUT"].getText())
                        if 0 < width: oc[f'SWING_{lineIndex}_Width'] = width
                        else: reset = True
                    except: reset = True
                    if reset:
                        oc[f'SWING_{lineIndex}_Width'] = 1
                        ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'SWING_{lineIndex}_Width']))
                    if width_previous != oc[f'SWING_{lineIndex}_Width']: updateTracker[lineIndex] = True
                    #Color
                    color_previous = (oc[f'SWING_{lineIndex}_ColorR%{cgt}'],
                                      oc[f'SWING_{lineIndex}_ColorG%{cgt}'],
                                      oc[f'SWING_{lineIndex}_ColorB%{cgt}'],
                                      oc[f'SWING_{lineIndex}_ColorA%{cgt}'])
                    color_r, color_g, color_b, color_a = ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineIndex}_LINECOLOR"].getColor()
                    oc[f'SWING_{lineIndex}_ColorR%{cgt}'] = color_r
                    oc[f'SWING_{lineIndex}_ColorG%{cgt}'] = color_g
                    oc[f'SWING_{lineIndex}_ColorB%{cgt}'] = color_b
                    oc[f'SWING_{lineIndex}_ColorA%{cgt}'] = color_a
                    if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
                    #Line Display
                    display_previous = oc[f'SWING_{lineIndex}_Display']
                    oc[f'SWING_{lineIndex}_Display'] = ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineIndex}_DISPLAY"].getStatus()
                    if display_previous != oc[f'SWING_{lineIndex}_Display']: updateTracker[lineIndex] = True
                #---SWING Master
                swingMaster_previous = oc['SWING_Master']
                oc['SWING_Master'] = ssps['MAIN'].GUIOs["MAININDICATOR_SWING"].getStatus()
                if swingMaster_previous != oc['SWING_Master']:
                    for lineIndex in updateTracker: updateTracker[lineIndex] = True
                #Queue Update
                configuredSWINGs = set(aCode for aCode in self.analysisParams if aCode.startswith('SWING'))
                for configuredSWING in configuredSWINGs:
                    lineIndex = self.analysisParams[configuredSWING]['lineIndex']
                    if updateTracker[lineIndex]:
                        self.__klineDrawer_RemoveDrawings(analysisCode = configuredSWING, gRemovalSignal = _FULLDRAWSIGNALS['SWING']) #Remove previous graphics
                        self.__addBufferZone_toDrawQueue(analysisCode  = configuredSWING, drawSignal     = _FULLDRAWSIGNALS['SWING']) #Update draw queue
                #Control Buttons Handling
                ssps['SWING'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'): 
                lineIndex = int(guioName_split[2])
                #Get new switch status
                _newStatus = ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineIndex}"].getStatus()
                oc[f'SWING_{lineIndex}_LineActive'] = _newStatus
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['SWING_Master']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'SwingRangeTextInputBox'):
                lineIndex = int(guioName_split[2])
                #Get new Swing Range
                try:    swingRange = round(float(ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT"].getText()), 4)
                except: swingRange = None
                #Save the new value to the object config dictionary
                oc[f'SWING_{lineIndex}_SwingRange'] = swingRange
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['SWING_Master'] and oc[f'SWING_{lineIndex}_LineActive']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True

        #Subpage 'VOL'
        elif indicatorType == 'VOL':
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):    
                lineSelected = ssps['VOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps['VOL'].GUIOs[f"INDICATOR_VOL{lineSelected}_LINECOLOR"].getColor()
                ssps['VOL'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps['VOL'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                ssps['VOL'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                ssps['VOL'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                ssps['VOL'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                ssps['VOL'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps['VOL'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps['VOL'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps['VOL'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps['VOL'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):             
                cType = guioName_split[2]
                ssps['VOL'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['VOL'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                    gValue = int(ssps['VOL'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                    bValue = int(ssps['VOL'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                    aValue = int(ssps['VOL'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps['VOL'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps['VOL'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps['VOL'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):        
                lineSelected = ssps['VOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps['VOL'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps['VOL'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps['VOL'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps['VOL'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps['VOL'].GUIOs[f"INDICATOR_VOL{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
                ssps['VOL'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                ssps['VOL'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'WidthTextInputBox'): 
                ssps['VOL'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):     
                ssps['VOL'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):     
                #UpdateTracker Initialization
                updateTracker = dict()
                #Check for any changes in the configuration siTypes_analysisCodes
                for lineIndex in range (_NMAXLINES['VOL']):
                    updateTracker[lineIndex] = False
                    #Width
                    width_previous = oc[f'VOL_{lineIndex}_Width']
                    reset = False
                    try:
                        width = int(ssps['VOL'].GUIOs[f"INDICATOR_VOL{lineIndex}_WIDTHINPUT"].getText())
                        if 0 < width: oc[f'VOL_{lineIndex}_Width'] = width
                        else: reset = True
                    except: reset = True
                    if reset == True:
                        oc[f'VOL_{lineIndex}_Width'] = 1
                        ssps['VOL'].GUIOs[f"INDICATOR_VOL{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'VOL_{lineIndex}_Width']))
                    if width_previous != oc[f'VOL_{lineIndex}_Width']: updateTracker[lineIndex] = True
                    #Color
                    color_previous = (oc[f'VOL_{lineIndex}_ColorR%{cgt}'], 
                                      oc[f'VOL_{lineIndex}_ColorG%{cgt}'], 
                                      oc[f'VOL_{lineIndex}_ColorB%{cgt}'], 
                                      oc[f'VOL_{lineIndex}_ColorA%{cgt}'])
                    color_r, color_g, color_b, color_a = ssps['VOL'].GUIOs[f"INDICATOR_VOL{lineIndex}_LINECOLOR"].getColor()
                    oc[f'VOL_{lineIndex}_ColorR%{cgt}'] = color_r
                    oc[f'VOL_{lineIndex}_ColorG%{cgt}'] = color_g
                    oc[f'VOL_{lineIndex}_ColorB%{cgt}'] = color_b
                    oc[f'VOL_{lineIndex}_ColorA%{cgt}'] = color_a
                    if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
                    #Line Display
                    display_previous = oc[f'VOL_{lineIndex}_Display']
                    oc[f'VOL_{lineIndex}_Display'] = ssps['VOL'].GUIOs[f"INDICATOR_VOL{lineIndex}_DISPLAY"].getStatus()
                    if display_previous != oc[f'VOL_{lineIndex}_Display']: updateTracker[lineIndex] = True
                #---VOL Master
                volMaster_previous = oc['VOL_Master']
                oc['VOL_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_VOL"].getStatus()
                if volMaster_previous != oc['VOL_Master']:
                    for targetLine in updateTracker: updateTracker[targetLine] = True
                #Queue Update
                configuredVOLs = set(aCode for aCode in self.analysisParams if aCode.startswith('VOL'))
                for configuredVOL in configuredVOLs:
                    lineIndex = self.analysisParams[configuredVOL]['lineIndex']
                    if updateTracker[lineIndex]:
                        self.__klineDrawer_RemoveDrawings(analysisCode = configuredVOL, gRemovalSignal = _FULLDRAWSIGNALS['VOL']) #Remove previous graphics
                        self.__addBufferZone_toDrawQueue(analysisCode  = configuredVOL, drawSignal     = _FULLDRAWSIGNALS['VOL']) #Update draw queue
                #Control Buttons Handling
                ssps['VOL'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'): 
                lineIndex = int(guioName_split[2])
                #Get new switch status
                _newStatus = ssps['VOL'].GUIOs[f"INDICATOR_VOL{lineIndex}"].getStatus()
                oc[f'VOL_{lineIndex}_LineActive'] = _newStatus
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['VOL_Master']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'): 
                lineIndex = int(guioName_split[2])
                #Get new nSamples
                try:    _nSamples = int(ssps['VOL'].GUIOs[f"INDICATOR_VOL{lineIndex}_INTERVALINPUT"].getText())
                except: _nSamples = None
                #Save the new value to the object config dictionary
                oc[f'VOL_{lineIndex}_NSamples'] = _nSamples
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['VOL_Master'] and oc[f'VOL_{lineIndex}_LineActive']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'VolTypeSelection'):
                #Get new VolumeType
                volType = ssps['VOL'].GUIOs["INDICATOR_VOLTYPESELECTION"].getSelected()
                #Save the new value to the object config dictionary
                oc['VOL_VolumeType'] = volType
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['VOL_Master']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'MATypeSelection'): 
                #Get new MAType
                maType = ssps['VOL'].GUIOs["INDICATOR_MATYPESELECTION"].getSelected()
                #Save the new value to the object config dictionary
                oc['VOL_MAType'] = maType
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['VOL_Master']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True

        #Subpage 'NNA'
        elif indicatorType == 'NNA':
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):    
                lineSelected = ssps['NNA'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineSelected}_LINECOLOR"].getColor()
                ssps['NNA'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps['NNA'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                ssps['NNA'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                ssps['NNA'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                ssps['NNA'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                ssps['NNA'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps['NNA'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps['NNA'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps['NNA'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps['NNA'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):             
                cType = guioName_split[2]
                ssps['NNA'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['NNA'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                    gValue = int(ssps['NNA'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                    bValue = int(ssps['NNA'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                    aValue = int(ssps['NNA'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps['NNA'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps['NNA'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps['NNA'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):        
                lineSelected = ssps['NNA'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps['NNA'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps['NNA'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps['NNA'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps['NNA'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
                ssps['NNA'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                ssps['NNA'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'WidthTextInputBox'): 
                ssps['NNA'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):     
                ssps['NNA'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):     
                #UpdateTracker Initialization
                updateTracker = dict()
                #Check for any changes in the configuration
                for lineIndex in range (_NMAXLINES['NNA']):
                    updateTracker[lineIndex] = False
                    #Width
                    width_previous = oc[f'NNA_{lineIndex}_Width']
                    reset = False
                    try:
                        width = int(ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].getText())
                        if 0 < width: oc[f'NNA_{lineIndex}_Width'] = width
                        else: reset = True
                    except: reset = True
                    if reset:
                        oc[f'NNA_{lineIndex}_Width'] = 1
                        ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'NNA_{lineIndex}_Width']))
                    if width_previous != oc[f'NNA_{lineIndex}_Width']: updateTracker[lineIndex] = True
                    #Color
                    color_previous = (oc[f'NNA_{lineIndex}_ColorR%{cgt}'], 
                                      oc[f'NNA_{lineIndex}_ColorG%{cgt}'], 
                                      oc[f'NNA_{lineIndex}_ColorB%{cgt}'], 
                                      oc[f'NNA_{lineIndex}_ColorA%{cgt}'])
                    color_r, color_g, color_b, color_a = ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_LINECOLOR"].getColor()
                    oc[f'NNA_{lineIndex}_ColorR%{cgt}'] = color_r
                    oc[f'NNA_{lineIndex}_ColorG%{cgt}'] = color_g
                    oc[f'NNA_{lineIndex}_ColorB%{cgt}'] = color_b
                    oc[f'NNA_{lineIndex}_ColorA%{cgt}'] = color_a
                    if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
                    #Line Display
                    display_previous = oc[f'NNA_{lineIndex}_Display']
                    oc[f'NNA_{lineIndex}_Display'] = ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_DISPLAY"].getStatus()
                    if display_previous != oc[f'NNA_{lineIndex}_Display']: updateTracker[lineIndex] = True
                #---NNA Master
                mfiMaster_previous = oc['NNA_Master']
                oc['NNA_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_NNA"].getStatus()
                if mfiMaster_previous != oc['NNA_Master']:
                    for lineIndex in updateTracker: updateTracker[lineIndex] = True
                #Queue Update
                configuredNNAs = set(aCode for aCode in self.analysisParams if aCode.startswith('NNA'))
                for configuredNNA in configuredNNAs:
                    lineIndex = self.analysisParams[configuredNNA]['lineIndex']
                    if updateTracker[lineIndex]:
                        self.__klineDrawer_RemoveDrawings(analysisCode = configuredNNA, gRemovalSignal = _FULLDRAWSIGNALS['NNA']) #Remove previous graphics
                        self.__addBufferZone_toDrawQueue(analysisCode  = configuredNNA, drawSignal     = _FULLDRAWSIGNALS['NNA']) #Update draw queue
                #Control Buttons Handling
                ssps['NNA'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'): 
                lineIndex = int(guioName_split[2])
                #Get new switch status
                newStatus = ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}"].getStatus()
                oc[f'NNA_{lineIndex}_LineActive'] = newStatus
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['NNA_Master']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'NNCodeTextInputBox'): 
                lineIndex = int(guioName_split[2])
                #Get new Neural Network Code
                try:    nnCode = ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_NNCODEINPUT"].getText()
                except: nnCode = None
                #Save the new value to the object config dictionary
                oc[f'NNA_{lineIndex}_NeuralNetworkCode'] = nnCode
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['NNA_Master'] and oc[f'NNA_{lineIndex}_LineActive']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'AlphaTextInputBox'): 
                lineIndex = int(guioName_split[2])
                #Get new Alpha
                try:    alpha = round(float(ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_ALPHAINPUT"].getText()), 2)
                except: alpha = None
                #Save the new value to the object config dictionary
                oc[f'NNA_{lineIndex}_Alpha'] = alpha
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['NNA_Master'] and oc[f'NNA_{lineIndex}_LineActive']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'BetaTextInputBox'): 
                lineIndex = int(guioName_split[2])
                #Get new Beta
                try:    beta = int(ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_BETAINPUT"].getText())
                except: beta = None
                #Save the new value to the object config dictionary
                oc[f'NNA_{lineIndex}_Beta'] = beta
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['NNA_Master'] and oc[f'NNA_{lineIndex}_LineActive']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True

        #Subpage 'MMACDSHORT'
        elif indicatorType == 'MMACDSHORT':
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'): 
                lineSelected = ssps['MMACDSHORT'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps['MMACDSHORT'].GUIOs[f"INDICATOR_{lineSelected}_COLOR"].getColor()
                ssps['MMACDSHORT'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps['MMACDSHORT'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                ssps['MMACDSHORT'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                ssps['MMACDSHORT'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                ssps['MMACDSHORT'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                ssps['MMACDSHORT'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps['MMACDSHORT'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps['MMACDSHORT'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps['MMACDSHORT'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps['MMACDSHORT'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):          
                cType = guioName_split[2]
                ssps['MMACDSHORT'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['MMACDSHORT'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                           gValue = int(ssps['MMACDSHORT'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                           bValue = int(ssps['MMACDSHORT'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                           aValue = int(ssps['MMACDSHORT'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps['MMACDSHORT'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps['MMACDSHORT'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps['MMACDSHORT'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):     
                lineSelected = ssps['MMACDSHORT'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps['MMACDSHORT'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps['MMACDSHORT'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps['MMACDSHORT'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps['MMACDSHORT'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps['MMACDSHORT'].GUIOs[f"INDICATOR_{lineSelected}_COLOR"].updateColor(color_r, color_g, color_b, color_a)
                ssps['MMACDSHORT'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                ssps['MMACDSHORT'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):  
                ssps['MMACDSHORT'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):  
                #UpdateTracker Initialization
                updateTracker = [False, False, False] #[0]: Draw MMACD, [1]: Draw SIGNAL, [2]: Draw HISTOGRAM
                #Check for any changes in the configuration
                #---MMACDSHORT Master
                mmacdShortMaster_previous = oc['MMACDSHORT_Master']
                oc['MMACDSHORT_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_MMACDSHORT"].getStatus()
                if mmacdShortMaster_previous != oc['MMACDSHORT_Master']: 
                    updateTracker[0] = True
                    updateTracker[1] = True
                    updateTracker[2] = True
                #---Colors
                for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM+', 'HISTOGRAM-'):
                    color_previous = (oc[f'MMACDSHORT_{targetLine}_ColorR%{cgt}'],
                                      oc[f'MMACDSHORT_{targetLine}_ColorG%{cgt}'],
                                      oc[f'MMACDSHORT_{targetLine}_ColorB%{cgt}'],
                                      oc[f'MMACDSHORT_{targetLine}_ColorA%{cgt}'])
                    color_r, color_g, color_b, color_a = ssps['MMACDSHORT'].GUIOs[f"INDICATOR_{targetLine}_COLOR"].getColor()
                    oc[f'MMACDSHORT_{targetLine}_ColorR%{cgt}'] = color_r
                    oc[f'MMACDSHORT_{targetLine}_ColorG%{cgt}'] = color_g
                    oc[f'MMACDSHORT_{targetLine}_ColorB%{cgt}'] = color_b
                    oc[f'MMACDSHORT_{targetLine}_ColorA%{cgt}'] = color_a
                    if (color_previous != (color_r, color_g, color_b, color_a)): 
                        if   (targetLine == 'MMACD'):      updateTracker[0] = True
                        elif (targetLine == 'SIGNAL'):     updateTracker[1] = True
                        elif (targetLine == 'HISTOGRAM+'): updateTracker[2] = True
                        elif (targetLine == 'HISTOGRAM-'): updateTracker[2] = True
                #---Line Display
                for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM'):
                    displayStatus_prev = oc[f'MMACDSHORT_{targetLine}_Display']
                    oc[f'MMACDSHORT_{targetLine}_Display'] = ssps['MMACDSHORT'].GUIOs[f"INDICATOR_{targetLine}_DISPLAYSWITCH"].getStatus()
                    if displayStatus_prev != oc[f'MMACDSHORT_{targetLine}_Display']:
                        if   targetLine == 'MMACD':     updateTracker[0] = True
                        elif targetLine == 'SIGNAL':    updateTracker[1] = True
                        elif targetLine == 'HISTOGRAM': updateTracker[2] = True
                #Queue Update
                drawSignal = 0
                drawSignal += 0b001*updateTracker[0] #MMACD
                drawSignal += 0b010*updateTracker[1] #SIGNAL
                drawSignal += 0b100*updateTracker[2] #HISTOGRAM
                if drawSignal:
                    self.__klineDrawer_RemoveDrawings(analysisCode = 'MMACDSHORT', gRemovalSignal = drawSignal) #Remove previous graphics
                    self.__addBufferZone_toDrawQueue(analysisCode  = 'MMACDSHORT', drawSignal     = drawSignal) #Update draw queue
                #Control Buttons Handling
                ssps['MMACDSHORT'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'):          
                lineIndex = int(guioName_split[2])
                #Get new switch status
                newStatus = ssps['MMACDSHORT'].GUIOs[f"INDICATOR_MMACDMA{lineIndex}"].getStatus()
                oc[f'MMACDSHORT_MA{lineIndex}_LineActive'] = newStatus
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['MMACDSHORT_Master']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'):          
                lineIndex = int(guioName_split[2])
                #Get new nSamples
                try:    nSamples = int(ssps['MMACDSHORT'].GUIOs[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].getText())
                except: nSamples = None
                #Save the new value to the object config dictionary
                oc[f'MMACDSHORT_MA{lineIndex}_NSamples'] = nSamples
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['MMACDSHORT_Master'] and oc[f'MMACDSHORT_MA{lineIndex}_LineActive']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'SignalIntervalTextInputBox'):    
                #Get new nSamples
                try:    nSamples = int(ssps['MMACDSHORT'].GUIOs["INDICATOR_SIGNALINTERVALTEXTINPUT"].getText())
                except: nSamples = None
                #Save the new value to the object config dictionary
                oc['MMACDSHORT_SignalNSamples'] = nSamples
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['MMACDSHORT_Master']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'MultiplierTextInputBox'): 
                #Get new multiplier
                try:    multiplier = int(ssps['MMACDSHORT'].GUIOs["INDICATOR_MULTIPLIERTEXTINPUT"].getText())
                except: multiplier = None
                #Save the new value to the object config dictionary
                oc['MMACDSHORT_Multiplier'] = multiplier
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['MMACDSHORT_Master']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True

        #Subpage 'MMACDLONG'
        elif indicatorType == 'MMACDLONG':
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'): 
                lineSelected = ssps['MMACDLONG'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps['MMACDLONG'].GUIOs[f"INDICATOR_{lineSelected}_COLOR"].getColor()
                ssps['MMACDLONG'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps['MMACDLONG'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                ssps['MMACDLONG'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                ssps['MMACDLONG'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                ssps['MMACDLONG'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                ssps['MMACDLONG'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps['MMACDLONG'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps['MMACDLONG'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps['MMACDLONG'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps['MMACDLONG'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):          
                cType = guioName_split[2]
                ssps['MMACDLONG'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['MMACDLONG'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                          gValue = int(ssps['MMACDLONG'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                          bValue = int(ssps['MMACDLONG'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                          aValue = int(ssps['MMACDLONG'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps['MMACDLONG'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps['MMACDLONG'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps['MMACDLONG'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):     
                lineSelected = ssps['MMACDLONG'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps['MMACDLONG'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps['MMACDLONG'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps['MMACDLONG'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps['MMACDLONG'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps['MMACDLONG'].GUIOs[f"INDICATOR_{lineSelected}_COLOR"].updateColor(color_r, color_g, color_b, color_a)
                ssps['MMACDLONG'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                ssps['MMACDLONG'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):  
                ssps['MMACDLONG'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):  
                #UpdateTracker Initialization
                updateTracker = [False, False, False] #[0]: Draw MMACD, [1]: Draw SIGNAL, [2]: Draw HISTOGRAM
                #Check for any changes in the configuration
                #---MMACDLONG Master
                mmacdLongMaster_previous = oc['MMACDLONG_Master']
                oc['MMACDLONG_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_MMACDLONG"].getStatus()
                if mmacdLongMaster_previous != oc['MMACDLONG_Master']: 
                    updateTracker[0] = True
                    updateTracker[1] = True
                    updateTracker[2] = True
                #---Colors
                for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM+', 'HISTOGRAM-'):
                    color_previous = (oc[f'MMACDLONG_{targetLine}_ColorR%{cgt}'],
                                      oc[f'MMACDLONG_{targetLine}_ColorG%{cgt}'],
                                      oc[f'MMACDLONG_{targetLine}_ColorB%{cgt}'],
                                      oc[f'MMACDLONG_{targetLine}_ColorA%{cgt}'])
                    color_r, color_g, color_b, color_a = ssps['MMACDLONG'].GUIOs[f"INDICATOR_{targetLine}_COLOR"].getColor()
                    oc[f'MMACDLONG_{targetLine}_ColorR%{cgt}'] = color_r
                    oc[f'MMACDLONG_{targetLine}_ColorG%{cgt}'] = color_g
                    oc[f'MMACDLONG_{targetLine}_ColorB%{cgt}'] = color_b
                    oc[f'MMACDLONG_{targetLine}_ColorA%{cgt}'] = color_a
                    if (color_previous != (color_r, color_g, color_b, color_a)): 
                        if   (targetLine == 'MMACD'):      updateTracker[0] = True
                        elif (targetLine == 'SIGNAL'):     updateTracker[1] = True
                        elif (targetLine == 'HISTOGRAM+'): updateTracker[2] = True
                        elif (targetLine == 'HISTOGRAM-'): updateTracker[2] = True
                #---Line Display
                for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM'):
                    displayStatus_prev = oc[f'MMACDLONG_{targetLine}_Display']
                    oc[f'MMACDLONG_{targetLine}_Display'] = ssps['MMACDLONG'].GUIOs[f"INDICATOR_{targetLine}_DISPLAYSWITCH"].getStatus()
                    if displayStatus_prev != oc[f'MMACDLONG_{targetLine}_Display']:
                        if   targetLine == 'MMACD':     updateTracker[0] = True
                        elif targetLine == 'SIGNAL':    updateTracker[1] = True
                        elif targetLine == 'HISTOGRAM': updateTracker[2] = True
                #Queue Update
                drawSignal = 0
                drawSignal += 0b001*updateTracker[0] #MMACD
                drawSignal += 0b010*updateTracker[1] #SIGNAL
                drawSignal += 0b100*updateTracker[2] #HISTOGRAM
                if drawSignal:
                    self.__klineDrawer_RemoveDrawings(analysisCode = 'MMACDLONG', gRemovalSignal = drawSignal) #Remove previous graphics
                    self.__addBufferZone_toDrawQueue(analysisCode  = 'MMACDLONG', drawSignal     = drawSignal) #Update draw queue
                #Control Buttons Handling
                ssps['MMACDLONG'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'):          
                lineIndex = int(guioName_split[2])
                #Get new switch status
                newStatus = ssps['MMACDLONG'].GUIOs[f"INDICATOR_MMACDMA{lineIndex}"].getStatus()
                oc[f'MMACDLONG_MA{lineIndex}_LineActive'] = newStatus
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['MMACDLONG_Master']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'):          
                lineIndex = int(guioName_split[2])
                #Get new nSamples
                try:    nSamples = int(ssps['MMACDLONG'].GUIOs[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].getText())
                except: nSamples = None
                #Save the new value to the object config dictionary
                oc[f'MMACDLONG_MA{lineIndex}_NSamples'] = nSamples
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['MMACDLONG_Master'] and oc[f'MMACDLONG_MA{lineIndex}_LineActive']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'SignalIntervalTextInputBox'):    
                #Get new nSamples
                try:    nSamples = int(ssps['MMACDLONG'].GUIOs["INDICATOR_SIGNALINTERVALTEXTINPUT"].getText())
                except: nSamples = None
                #Save the new value to the object config dictionary
                oc['MMACDLONG_SignalNSamples'] = nSamples
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['MMACDLONG_Master']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'MultiplierTextInputBox'): 
                #Get new multiplier
                try:    multiplier = int(ssps['MMACDLONG'].GUIOs["INDICATOR_MULTIPLIERTEXTINPUT"].getText())
                except: multiplier = None
                #Save the new value to the object config dictionary
                oc['MMACDLONG_Multiplier'] = multiplier
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['MMACDLONG_Master']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True

        #Subpage 'DMIxADX'
        elif indicatorType == 'DMIxADX':
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):    
                lineSelected = ssps['DMIxADX'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineSelected}_LINECOLOR"].getColor()
                ssps['DMIxADX'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps['DMIxADX'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                ssps['DMIxADX'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                ssps['DMIxADX'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                ssps['DMIxADX'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                ssps['DMIxADX'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps['DMIxADX'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps['DMIxADX'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps['DMIxADX'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps['DMIxADX'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):             
                cType = guioName_split[2]
                ssps['DMIxADX'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                        gValue = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                        bValue = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                        aValue = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps['DMIxADX'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps['DMIxADX'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps['DMIxADX'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):        
                lineSelected = ssps['DMIxADX'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
                ssps['DMIxADX'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                ssps['DMIxADX'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'WidthTextInputBox'): 
                ssps['DMIxADX'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):     
                ssps['DMIxADX'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):     
                #UpdateTracker Initialization
                updateTracker = dict()
                #Check for any changes in the configuration
                for lineIndex in range (_NMAXLINES['DMIxADX']):
                    updateTracker[lineIndex] = False
                    #Width
                    width_previous = oc[f'DMIxADX_{lineIndex}_Width']
                    reset = False
                    try:
                        width = int(ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT"].getText())
                        if 0 < width: oc[f'DMIxADX_{lineIndex}_Width'] = width
                        else: reset = True
                    except: reset = True
                    if reset:
                        oc[f'DMIxADX_{lineIndex}_Width'] = 1
                        ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'DMIxADX_{lineIndex}_Width']))
                    if width_previous != oc[f'DMIxADX_{lineIndex}_Width']: updateTracker[lineIndex] = True
                    #Color
                    color_previous = (oc[f'DMIxADX_{lineIndex}_ColorR%{cgt}'], 
                                      oc[f'DMIxADX_{lineIndex}_ColorG%{cgt}'], 
                                      oc[f'DMIxADX_{lineIndex}_ColorB%{cgt}'], 
                                      oc[f'DMIxADX_{lineIndex}_ColorA%{cgt}'])
                    color_r, color_g, color_b, color_a = ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}_LINECOLOR"].getColor()
                    oc[f'DMIxADX_{lineIndex}_ColorR%{cgt}'] = color_r
                    oc[f'DMIxADX_{lineIndex}_ColorG%{cgt}'] = color_g
                    oc[f'DMIxADX_{lineIndex}_ColorB%{cgt}'] = color_b
                    oc[f'DMIxADX_{lineIndex}_ColorA%{cgt}'] = color_a
                    if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
                    #Line Display
                    display_previous = oc[f'DMIxADX_{lineIndex}_Display']
                    oc[f'DMIxADX_{lineIndex}_Display'] = ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}_DISPLAY"].getStatus()
                    if display_previous != oc[f'DMIxADX_{lineIndex}_Display']: updateTracker[lineIndex] = True
                #---DMIxADX Master
                dmixadxMaster_previous = oc['DMIxADX_Master']
                oc['DMIxADX_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_DMIxADX"].getStatus()
                if dmixadxMaster_previous != oc['DMIxADX_Master']:
                    for lineIndex in updateTracker: updateTracker[lineIndex] = True
                #Queue Update
                configuredDMIxADXs = set(aCode for aCode in self.analysisParams if aCode.startswith('DMIxADX'))
                for configuredDMIxADX in configuredDMIxADXs:
                    lineIndex = self.analysisParams[configuredDMIxADX]['lineIndex']
                    if updateTracker[lineIndex]:
                        self.__klineDrawer_RemoveDrawings(analysisCode = configuredDMIxADX, gRemovalSignal = _FULLDRAWSIGNALS['DMIxADX']) #Remove previous graphics
                        self.__addBufferZone_toDrawQueue(analysisCode  = configuredDMIxADX, drawSignal     = _FULLDRAWSIGNALS['DMIxADX']) #Update draw queue
                #Control Buttons Handling
                ssps['DMIxADX'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'): 
                lineIndex = int(guioName_split[2])
                #Get new switch status
                newStatus = ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}"].getStatus()
                oc[f'DMIxADX_{lineIndex}_LineActive'] = newStatus
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['DMIxADX_Master']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'): 
                lineIndex = int(guioName_split[2])
                #Get new nSamples
                try:    nSamples = int(ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT"].getText())
                except: nSamples = None
                #Save the new value to the object config dictionary
                oc[f'DMIxADX_{lineIndex}_NSamples'] = nSamples
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['DMIxADX_Master'] and oc[f'DMIxADX_{lineIndex}_LineActive']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True

        #Subpage 'MFI'
        elif indicatorType == 'MFI':
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):    
                lineSelected = ssps['MFI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineSelected}_LINECOLOR"].getColor()
                ssps['MFI'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps['MFI'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                ssps['MFI'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                ssps['MFI'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                ssps['MFI'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                ssps['MFI'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps['MFI'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps['MFI'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps['MFI'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps['MFI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):             
                cType = guioName_split[2]
                ssps['MFI'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['MFI'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                    gValue = int(ssps['MFI'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                    bValue = int(ssps['MFI'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                    aValue = int(ssps['MFI'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps['MFI'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps['MFI'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps['MFI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):        
                lineSelected = ssps['MFI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps['MFI'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps['MFI'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps['MFI'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps['MFI'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
                ssps['MFI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                ssps['MFI'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'WidthTextInputBox'): 
                ssps['MFI'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):     
                ssps['MFI'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):     
                #UpdateTracker Initialization
                updateTracker = dict()
                #Check for any changes in the configuration
                for lineIndex in range (_NMAXLINES['MFI']):
                    updateTracker[lineIndex] = False
                    #Width
                    width_previous = oc[f'MFI_{lineIndex}_Width']
                    reset = False
                    try:
                        width = int(ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}_WIDTHINPUT"].getText())
                        if 0 < width: oc[f'MFI_{lineIndex}_Width'] = width
                        else: reset = True
                    except: reset = True
                    if reset:
                        oc[f'MFI_{lineIndex}_Width'] = 1
                        ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'MFI_{lineIndex}_Width']))
                    if width_previous != oc[f'MFI_{lineIndex}_Width']: updateTracker[lineIndex] = True
                    #Color
                    color_previous = (oc[f'MFI_{lineIndex}_ColorR%{cgt}'], 
                                      oc[f'MFI_{lineIndex}_ColorG%{cgt}'], 
                                      oc[f'MFI_{lineIndex}_ColorB%{cgt}'], 
                                      oc[f'MFI_{lineIndex}_ColorA%{cgt}'])
                    color_r, color_g, color_b, color_a = ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}_LINECOLOR"].getColor()
                    oc[f'MFI_{lineIndex}_ColorR%{cgt}'] = color_r
                    oc[f'MFI_{lineIndex}_ColorG%{cgt}'] = color_g
                    oc[f'MFI_{lineIndex}_ColorB%{cgt}'] = color_b
                    oc[f'MFI_{lineIndex}_ColorA%{cgt}'] = color_a
                    if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
                    #Line Display
                    display_previous = oc[f'MFI_{lineIndex}_Display']
                    oc[f'MFI_{lineIndex}_Display'] = ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}_DISPLAY"].getStatus()
                    if display_previous != oc[f'MFI_{lineIndex}_Display']: updateTracker[lineIndex] = True
                #---MFI Master
                mfiMaster_previous = oc['MFI_Master']
                oc['MFI_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_MFI"].getStatus()
                if mfiMaster_previous != oc['MFI_Master']:
                    for lineIndex in updateTracker: updateTracker[lineIndex] = True
                #Queue Update
                configuredMFIs = set(aCode for aCode in self.analysisParams if aCode.startswith('MFI'))
                for configuredMFI in configuredMFIs:
                    lineIndex = self.analysisParams[configuredMFI]['lineIndex']
                    if updateTracker[lineIndex]:
                        self.__klineDrawer_RemoveDrawings(analysisCode = configuredMFI, gRemovalSignal = _FULLDRAWSIGNALS['MFI']) #Remove previous graphics
                        self.__addBufferZone_toDrawQueue(analysisCode  = configuredMFI, drawSignal     = _FULLDRAWSIGNALS['MFI']) #Update draw queue
                #Control Buttons Handling
                ssps['MFI'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'): 
                lineIndex = int(guioName_split[2])
                #Get new switch status
                newStatus = ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}"].getStatus()
                oc[f'MFI_{lineIndex}_LineActive'] = newStatus
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['MFI_Master']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'): 
                lineIndex = int(guioName_split[2])
                #Get new nSamples
                try:    nSamples = int(ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}_INTERVALINPUT"].getText())
                except: nSamples = None
                #Save the new value to the object config dictionary
                oc[f'MFI_{lineIndex}_NSamples'] = nSamples
                #If needed, activate the start analysis button
                if (self.chartDrawerType == 'ANALYZER') and self.canStartAnalysis and oc['MFI_Master'] and oc[f'MFI_{lineIndex}_LineActive']: ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
                activateSaveConfigButton = True

        #Subpage 'WOI'
        elif indicatorType == 'WOI':
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):    
                lineSelected = ssps['WOI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineSelected}_LINECOLOR"].getColor()
                ssps['WOI'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps['WOI'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                ssps['WOI'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                ssps['WOI'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                ssps['WOI'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                ssps['WOI'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps['WOI'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps['WOI'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps['WOI'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps['WOI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):             
                cType = guioName_split[2]
                ssps['WOI'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['WOI'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                    gValue = int(ssps['WOI'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                    bValue = int(ssps['WOI'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                    aValue = int(ssps['WOI'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps['WOI'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps['WOI'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps['WOI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):        
                lineSelected = ssps['WOI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps['WOI'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps['WOI'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps['WOI'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps['WOI'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
                ssps['WOI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                ssps['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'WidthTextInputBox'): 
                ssps['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):     
                ssps['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'):
                ssps['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'IntervalTextInputBox'):
                ssps['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'SigmaTextInputBox'):
                ssps['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
            #Both
            elif (setterType == 'ApplySettings'):
                #UpdateTracker Initialization
                updateTracker = {'BASE': False}
                #Check for any changes in the configuration
                #---[1]: Base
                #------Line Activation
                _display_prev = oc['WOI_BASE_Display']
                oc['WOI_BASE_Display'] = ssps['WOI'].GUIOs["INDICATOR_WOIBASE_DISPLAYSWITCH"].getStatus()
                if _display_prev != oc['WOI_BASE_Display']: updateTracker['BASE'] = True
                #------Colors
                for tLine in ('BASE+', 'BASE-'):
                    color_previous = (oc[f'WOI_{tLine}_ColorR%{cgt}'],
                                      oc[f'WOI_{tLine}_ColorG%{cgt}'],
                                      oc[f'WOI_{tLine}_ColorB%{cgt}'],
                                      oc[f'WOI_{tLine}_ColorA%{cgt}'])
                    color_r, color_g, color_b, color_a = ssps['WOI'].GUIOs[f"INDICATOR_WOI{tLine}_LINECOLOR"].getColor()
                    oc[f'WOI_{tLine}_ColorR%{cgt}'] = color_r
                    oc[f'WOI_{tLine}_ColorG%{cgt}'] = color_g
                    oc[f'WOI_{tLine}_ColorB%{cgt}'] = color_b
                    oc[f'WOI_{tLine}_ColorA%{cgt}'] = color_a
                    if color_previous != (color_r, color_g, color_b, color_a): updateTracker['BASE'] = True
                #---[2]: Gaussian Deltas
                for lineIndex in range (_NMAXLINES['WOI']):
                    updateTracker[lineIndex] = [False, False]
                    if self.chartDrawerType == 'ANALYZER':
                        #Line Activation
                        status_prev = oc[f'WOI_{lineIndex}_LineActive']
                        status_new  = ssps[f'WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}"].getStatus()
                        if status_prev != status_new:
                            oc[f'WOI_{lineIndex}_LineActive'] = status_new
                            updateTracker[lineIndex][0] = True
                        #Interval
                        nSamples_prev = oc[f'WOI_{lineIndex}_NSamples']
                        try:    nSamples_new = int(ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_INTERVALINPUT"].getText())
                        except: nSamples_new = None
                        if nSamples_new is None:
                            nSamples_new = 10*(lineIndex+1)
                        if nSamples_prev != nSamples_new:
                            oc[f'WOI_{lineIndex}_NSamples'] = nSamples_new
                            updateTracker[lineIndex][0] = True
                        ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples_new}")
                        #Sigma
                        sigma_prev = oc[f'WOI_{lineIndex}_Sigma']
                        try:    sigma_new = round(float(ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_SIGMAINPUT"].getText()), 1)
                        except: sigma_new = None
                        if sigma_new is None:
                            sigma_new = 2.5*(lineIndex+1)
                        if sigma_prev != sigma_new:
                            oc[f'WOI_{lineIndex}_Sigma'] = sigma_new
                            updateTracker[lineIndex][0] = True
                        ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_SIGMAINPUT"].updateText(text = f"{sigma_new:.1f}")
                    #Width
                    width_previous = oc[f'WOI_{lineIndex}_Width']
                    reset = False
                    try:
                        width = int(ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_WIDTHINPUT"].getText())
                        if 0 < width: oc[f'WOI_{lineIndex}_Width'] = width
                        else: reset = True
                    except: reset = True
                    if reset: oc[f'WOI_{lineIndex}_Width'] = 1
                    if width_previous != oc[f'WOI_{lineIndex}_Width']: updateTracker[lineIndex][1] = True
                    ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'WOI_{lineIndex}_Width']))
                    #Color
                    color_previous = (oc[f'WOI_{lineIndex}_ColorR%{cgt}'], 
                                      oc[f'WOI_{lineIndex}_ColorG%{cgt}'], 
                                      oc[f'WOI_{lineIndex}_ColorB%{cgt}'], 
                                      oc[f'WOI_{lineIndex}_ColorA%{cgt}'])
                    color_r, color_g, color_b, color_a = ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_LINECOLOR"].getColor()
                    oc[f'WOI_{lineIndex}_ColorR%{cgt}'] = color_r
                    oc[f'WOI_{lineIndex}_ColorG%{cgt}'] = color_g
                    oc[f'WOI_{lineIndex}_ColorB%{cgt}'] = color_b
                    oc[f'WOI_{lineIndex}_ColorA%{cgt}'] = color_a
                    if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex][1] = True
                    #Line Display
                    display_previous = oc[f'WOI_{lineIndex}_Display']
                    oc[f'WOI_{lineIndex}_Display'] = ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_DISPLAY"].getStatus()
                    if display_previous != oc[f'WOI_{lineIndex}_Display']: updateTracker[lineIndex][1] = True
                #---[3]: WOI Master
                WOIMaster_previous = oc['WOI_Master']
                oc['WOI_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_WOI"].getStatus()
                if WOIMaster_previous != oc['WOI_Master']:
                    for line in updateTracker: 
                        if line == 'BASE': updateTracker[line] = True
                        else:              updateTracker[line] = [True, True]
                #Control Variables Update
                if self.chartDrawerType == 'ANALYZER':
                    self.siTypes_analysisCodes['WOI'] = list()
                    for lineIndex in range (_NMAXLINES['WOI']):
                        woiType = f"WOI_{lineIndex}"
                        if oc[f'WOI_{lineIndex}_LineActive']:
                            self.siTypes_analysisCodes['WOI'].append(woiType)
                            if updateTracker[lineIndex][0]: self.bidsAndAsks[woiType] = dict()
                        elif woiType in self.bidsAndAsks: del self.bidsAndAsks[woiType]
                #Reprocess & Queue Update
                isMasterOn = ssps['MAIN'].GUIOs["SUBINDICATOR_WOI"].getStatus()
                #---[1]: Base
                if updateTracker['BASE']:
                    #Remove previous graphics
                    self.__WOIDrawer_RemoveDrawings(woiType = 'WOI')
                    #Draw Queue
                    if isMasterOn and oc['WOI_BASE_Display']:
                        for tt in self.bidsAndAsks['WOI']:
                            if tt in self.bidsAndAsks_WOI_drawQueue: self.bidsAndAsks_WOI_drawQueue[tt].add('WOI')
                            else:                                    self.bidsAndAsks_WOI_drawQueue[tt] = {'WOI',}
                #---[2]: Gaussian Deltas
                for lineIndex in range (_NMAXLINES['WOI']):
                    if not any(updateTracker[lineIndex]): continue
                    woiType = f"WOI_{lineIndex}"
                    #Remove previous graphics
                    self.__WOIDrawer_RemoveDrawings(woiType = woiType)
                    #Line Status
                    isActive   = (isMasterOn and ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}"].getStatus())
                    isVisible  = (isMasterOn and isActive and ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_DISPLAY"].getStatus())
                    #Reprocess (If needed)
                    if (self.chartDrawerType == 'ANALYZER') and isActive and updateTracker[lineIndex][0]:
                        nSamples  = oc[f'WOI_{lineIndex}_NSamples']
                        sigma     = oc[f'WOI_{lineIndex}_Sigma']
                        for tt in sorted(self.bidsAndAsks['WOI']):
                            atmEta_Analyzers.generateAnalysis_WOI(bidsAndAsks = self.bidsAndAsks, woiType = woiType, nSamples = nSamples, sigma = sigma, targetTime = tt)
                    #Draw Queue
                    if isVisible:
                        for tt in self.bidsAndAsks[woiType]:
                            if (tt in self.bidsAndAsks_WOI_drawQueue): self.bidsAndAsks_WOI_drawQueue[tt].add(woiType)
                            else:                                      self.bidsAndAsks_WOI_drawQueue[tt] = {woiType,}
                #Control Buttons Handling
                ssps['WOI'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True

        #Subpage 'NES'
        elif indicatorType == 'NES':
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):    
                lineSelected = ssps['NES'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps['NES'].GUIOs[f"INDICATOR_NES{lineSelected}_LINECOLOR"].getColor()
                ssps['NES'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps['NES'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                ssps['NES'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                ssps['NES'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                ssps['NES'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                ssps['NES'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps['NES'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps['NES'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps['NES'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps['NES'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):             
                cType = guioName_split[2]
                ssps['NES'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['NES'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                    gValue = int(ssps['NES'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                    bValue = int(ssps['NES'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                    aValue = int(ssps['NES'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps['NES'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps['NES'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps['NES'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):        
                lineSelected = ssps['NES'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps['NES'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps['NES'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps['NES'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps['NES'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps['NES'].GUIOs[f"INDICATOR_NES{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
                ssps['NES'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                ssps['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'WidthTextInputBox'): 
                ssps['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):     
                ssps['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'): 
                ssps['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'IntervalTextInputBox'): 
                ssps['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'SigmaTextInputBox'): 
                ssps['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
            #Both
            elif (setterType == 'ApplySettings'):     
                #UpdateTracker Initialization
                updateTracker = {'BASE': False}
                #Check for any changes in the configuration
                #---[1]: Base
                #------Line Activation
                display_prev = oc['NES_BASE_Display']
                oc['NES_BASE_Display'] = ssps['NES'].GUIOs["INDICATOR_NESBASE_DISPLAYSWITCH"].getStatus()
                if display_prev != oc['NES_BASE_Display']: updateTracker['BASE'] = True
                #------Colors
                for tLine in ('BASE+', 'BASE-'):
                    color_previous = (oc[f'NES_{tLine}_ColorR%{cgt}'],
                                      oc[f'NES_{tLine}_ColorG%{cgt}'],
                                      oc[f'NES_{tLine}_ColorB%{cgt}'],
                                      oc[f'NES_{tLine}_ColorA%{cgt}'])
                    color_r, color_g, color_b, color_a = ssps['NES'].GUIOs[f"INDICATOR_NES{tLine}_LINECOLOR"].getColor()
                    oc[f'NES_{tLine}_ColorR%{cgt}'] = color_r
                    oc[f'NES_{tLine}_ColorG%{cgt}'] = color_g
                    oc[f'NES_{tLine}_ColorB%{cgt}'] = color_b
                    oc[f'NES_{tLine}_ColorA%{cgt}'] = color_a
                    if color_previous != (color_r, color_g, color_b, color_a): updateTracker['BASE'] = True
                #---[2]: Gaussian Deltas
                for lineIndex in range (_NMAXLINES['NES']):
                    updateTracker[lineIndex] = [False, False]
                    if self.chartDrawerType == 'ANALYZER':
                        #Line Activation
                        status_prev = oc[f'NES_{lineIndex}_LineActive']
                        status_new  = ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}"].getStatus()
                        if status_prev != status_new:
                            oc[f'NES_{lineIndex}_LineActive'] = status_new
                            updateTracker[lineIndex][0] = True
                        #Interval
                        nSamples_prev = oc[f'NES_{lineIndex}_NSamples']
                        try:    nSamples_new = int(ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].getText())
                        except: nSamples_new = None
                        if nSamples_new is None:
                            nSamples_new = 10*(lineIndex+1)
                        if nSamples_prev != nSamples_new:
                            oc[f'NES_{lineIndex}_NSamples'] = nSamples_new
                            updateTracker[lineIndex][0] = True
                        ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples_new}")
                        #Sigma
                        sigma_prev = oc[f'NES_{lineIndex}_Sigma']
                        try:    sigma_new = round(float(ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_SIGMAINPUT"].getText()), 1)
                        except: sigma_new = None
                        if sigma_new is None:
                            sigma_new = 2.0
                        if sigma_prev != sigma_new:
                            oc[f'NES_{lineIndex}_Sigma'] = sigma_new
                            updateTracker[lineIndex][0] = True
                        ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_SIGMAINPUT"].updateText(text = f"{sigma_new:.1f}")
                    #Width
                    width_previous = oc[f'NES_{lineIndex}_Width']
                    reset = False
                    try:
                        width = int(ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].getText())
                        if 0 < width: oc[f'NES_{lineIndex}_Width'] = width
                        else: reset = True
                    except: reset = True
                    if reset: oc[f'NES_{lineIndex}_Width'] = 1
                    if width_previous != oc[f'NES_{lineIndex}_Width']: updateTracker[lineIndex][1] = True
                    ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'NES_{lineIndex}_Width']))
                    #Color
                    color_previous = (oc[f'NES_{lineIndex}_ColorR%{cgt}'], 
                                      oc[f'NES_{lineIndex}_ColorG%{cgt}'], 
                                      oc[f'NES_{lineIndex}_ColorB%{cgt}'], 
                                      oc[f'NES_{lineIndex}_ColorA%{cgt}'])
                    color_r, color_g, color_b, color_a = ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_LINECOLOR"].getColor()
                    oc[f'NES_{lineIndex}_ColorR%{cgt}'] = color_r
                    oc[f'NES_{lineIndex}_ColorG%{cgt}'] = color_g
                    oc[f'NES_{lineIndex}_ColorB%{cgt}'] = color_b
                    oc[f'NES_{lineIndex}_ColorA%{cgt}'] = color_a
                    if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex][1] = True
                    #Line Display
                    display_previous = oc[f'NES_{lineIndex}_Display']
                    oc[f'NES_{lineIndex}_Display'] = ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_DISPLAY"].getStatus()
                    if display_previous != oc[f'NES_{lineIndex}_Display']: updateTracker[lineIndex][1] = True
                #---[3]: NES Master
                NESMaster_previous = oc['NES_Master']
                oc['NES_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_NES"].getStatus()
                if NESMaster_previous != oc['NES_Master']:
                    for line in updateTracker: 
                        if line == 'BASE': updateTracker[line] = True
                        else:              updateTracker[line] = [True, True]
                #Control Variables Update
                if self.chartDrawerType == 'ANALYZER':
                    self.siTypes_analysisCodes['NES'] = list()
                    for lineIndex in range (_NMAXLINES['NES']):
                        nesType = f"NES_{lineIndex}"
                        if oc[f'NES_{lineIndex}_LineActive']: 
                            self.siTypes_analysisCodes['NES'].append(nesType)
                            if updateTracker[lineIndex][0]: self.aggTrades[nesType] = dict()
                        elif nesType in self.aggTrades: del self.aggTrades[nesType]
                #Reprocess & Queue Update
                isMasterOn = ssps['MAIN'].GUIOs["SUBINDICATOR_NES"].getStatus()
                #---[1]: Base
                if updateTracker['BASE']:
                    #Remove previous graphics
                    self.__NESDrawer_RemoveDrawings(nesType = 'NES')
                    #Draw Queue
                    if isMasterOn and oc['NES_BASE_Display']:
                        for tt in self.aggTrades['NES']:
                            if tt in self.aggTrades_NES_drawQueue: self.aggTrades_NES_drawQueue[tt].add('NES')
                            else:                                  self.aggTrades_NES_drawQueue[tt] = {'NES',}
                #---[2]: Gaussian Deltas
                for lineIndex in range (_NMAXLINES['NES']):
                    if not any(updateTracker[lineIndex]): continue
                    nesType = f"NES_{lineIndex}"
                    #Remove previous graphics
                    self.__NESDrawer_RemoveDrawings(nesType = nesType)
                    #Line Status
                    isActive  = (isMasterOn and ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}"].getStatus())
                    isVisible = (isMasterOn and isActive and ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_DISPLAY"].getStatus())
                    #Reprocess (If needed)
                    if (self.chartDrawerType == 'ANALYZER') and isActive and updateTracker[lineIndex][0]:
                        nSamples = oc[f'NES_{lineIndex}_NSamples']
                        sigma    = oc[f'NES_{lineIndex}_Sigma']
                        for tt in sorted(self.aggTrades['NES']): 
                            atmEta_Analyzers.generateAnalysis_NES(aggTrades = self.aggTrades, nesType = nesType, nSamples = nSamples, sigma = sigma, targetTime = tt)
                    #Draw Queue
                    if isVisible:
                        for tt in self.aggTrades[nesType]:
                            if tt in self.aggTrades_NES_drawQueue: self.aggTrades_NES_drawQueue[tt].add(nesType)
                            else:                                  self.aggTrades_NES_drawQueue[tt] = {nesType,}
                #Control Buttons Handling
                ssps['NES'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True

        if activateSaveConfigButton and ssps['MAIN'].GUIOs["AUX_SAVECONFIGURATION"].deactivated: ssps['MAIN'].GUIOs["AUX_SAVECONFIGURATION"].activate()

    def __addBufferZone_toDrawQueue(self, analysisCode, drawSignal):
        if analysisCode not in self.klines: return
        aData  = self.klines[analysisCode]
        dQueue = self.klines_drawQueue
        for ts in itertools.chain(self.horizontalViewRange_timestampsInViewRange, self.horizontalViewRange_timestampsInBufferZone):
            if ts not in aData: continue
            dQueue_ts = dQueue.get(ts, None)
            if dQueue_ts is None:
                dQueue[ts] = {analysisCode: drawSignal}
            else:
                if analysisCode in dQueue_ts and dQueue_ts[analysisCode] is not None: dQueue_ts[analysisCode] |= drawSignal
                else:                                                                 dQueue_ts[analysisCode]  = drawSignal

    def __addALLWOI_toDrawQueue(self):
        dQueue = self.bidsAndAsks_WOI_drawQueue
        baa    = self.bidsAndAsks
        aCodes = ['WOI',] + [aCode for aCode in self.siTypes_analysisCodes['WOI'] if self.objectConfig[f'{aCode}_Display']]
        for aCode in aCodes:
            for tt in baa[aCode]:
                if tt in dQueue: dQueue[tt].add(aCode)
                else:            dQueue[tt] = {aCode,}

    def __addALLNES_toDrawQueue(self):
        dQueue = self.aggTrades_NES_drawQueue
        at     = self.aggTrades
        aCodes = ['NES',] + [aCode for aCode in self.siTypes_analysisCodes['NES'] if self.objectConfig[f'{aCode}_Display']]
        for aCode in aCodes:
            for tt in at[aCode]:
                if tt in dQueue: dQueue[tt].add(aCode)
                else:            dQueue[tt] = {aCode,}

    def updateKlineColors(self, newType):
        if newType not in (1, 2): return False
        self.objectConfig['KlineColorType'] = newType
        self.settingsSubPages['MAIN'].GUIOs["AUX_KLINECOLORTYPE_SELECTIONBOX"].setSelected(newType, callSelectionUpdateFunction = False)
        k_drawn  = self.klines_drawn
        k_dQueue = self.klines_drawQueue
        for ts in k_drawn:
            if 'KLINE' in k_drawn[ts]:
                if ts in k_dQueue: k_dQueue[ts]['KLINE'] = None
                else:              k_dQueue[ts] = {'KLINE': None}
            if 'VOL' in k_drawn[ts]:
                if ts in k_dQueue: k_dQueue[ts]['VOL'] = None
                else:              k_dQueue[ts] = {'VOL': None}
        return True
        
    def updateTimeZone(self, newTimeZone):
        self.objectConfig['TimeZone'] = newTimeZone
        if   newTimeZone == 'LOCAL':        self.timezoneDelta = -time.timezone
        elif newTimeZone.startswith('UTC'): self.timezoneDelta = int(newTimeZone.split("+")[1])*3600
        #Update vertical grid texts (Temporal Texts)
        vgts = self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS']
        for index in range (len(self.verticalGrid_intervals)):
            timestamp_display = self.verticalGrid_intervals[index] + self.timezoneDelta
            #Grid Text
            if self.verticalGrid_intervalID <= 10:
                if timestamp_display % 86400 == 0: dateStrFormat = "%m/%d"
                else:                              dateStrFormat = "%H:%M"
            else:
                if atmEta_Auxillaries.isNewMonth(timestamp_display): dateStrFormat = "%Y/%m"
                else:                                                dateStrFormat = "%m/%d"
            #Text & Position Update
            vgt = vgts[index]
            vgt.setText(datetime.fromtimestamp(timestamp_display, tz = timezone.utc).strftime(dateStrFormat))
            vgt.moveTo(x = vgt.xPos)
    #Configuration Update Control END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Kline Drawing --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __klineDrawer_sendDrawSignals(self, timestamp, analysisCode, redraw = False):
        try:
            if redraw: drawSignal = None
            else:      drawSignal = self.klines_drawQueue[timestamp][analysisCode]
            drawn = self.__klines_drawerFunctions[analysisCode.split("_")[0]](drawSignal = drawSignal, timestamp = timestamp, analysisCode = analysisCode)
            if drawn is None: print(timestamp, analysisCode, drawn)
            if not drawn: return
            if timestamp in self.klines_drawn:
                if analysisCode in self.klines_drawn[timestamp]: self.klines_drawn[timestamp][analysisCode] |= drawn
                else:                                            self.klines_drawn[timestamp][analysisCode] = drawn
            else:                                                self.klines_drawn[timestamp] = {analysisCode: drawn}
        except Exception as e: print(termcolor.colored(f"An unexpected error occured while attempting to draw {analysisCode} at {timestamp}\n *", 'light_yellow'), termcolor.colored(e, 'light_yellow'))

    def __klineDrawer_KLINE(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        if timestamp not in self.klines['raw']: return 0b0
        kline_raw = self.klines['raw'][timestamp]
        ts_open  = kline_raw[KLINDEX_OPENTIME]
        ts_close = kline_raw[KLINDEX_CLOSETIME]
        p_open   = kline_raw[KLINDEX_OPENPRICE]
        p_high   = kline_raw[KLINDEX_HIGHPRICE]
        p_low    = kline_raw[KLINDEX_LOWPRICE]
        p_close  = kline_raw[KLINDEX_CLOSEPRICE]

        #[2]: Width determination
        tsWidth = ts_close-ts_open+1
        body_width = round(tsWidth*0.9, 1)
        body_xPos  = round(ts_open+(tsWidth-body_width)/2, 1)
        tail_width = round(tsWidth/5, 1)
        tail_xPos  = round(ts_open+(tsWidth-tail_width)/2, 1)

        #[3]: Color & Height determination
        kct = self.objectConfig['KlineColorType']
        if (p_open < p_close): #Incremental
            candleColor = self.visualManager.getFromColorTable(f'CHARTDRAWER_KLINECOLOR_TYPE{kct}_INCREMENTAL')
            body_height = p_close-p_open
            body_bottom = p_open
        elif (p_open > p_close): #Decremental
            candleColor = self.visualManager.getFromColorTable(f'CHARTDRAWER_KLINECOLOR_TYPE{kct}_DECREMENTAL')
            body_height = p_open-p_close
            body_bottom = p_close
        else: #Neutral
            candleColor = self.visualManager.getFromColorTable(f'CHARTDRAWER_KLINECOLOR_TYPE{kct}_NEUTRAL')
            body_height = 0
            body_bottom = p_close
        tail_height = p_high-p_low
        tail_bottom = p_low

        #[4]: Drawing
        if (0 < body_height): 
            self.displayBox_graphics['KLINESPRICE']['RCLCG'].addShape_Rectangle(x      = body_xPos, 
                                                                                y      = body_bottom, 
                                                                                width  = body_width, 
                                                                                height = body_height, 
                                                                                color = candleColor, 
                                                                                shapeName = ts_open, shapeGroupName = 'KLINEBODIES', layerNumber = 10)
        else:                 
            self.displayBox_graphics['KLINESPRICE']['RCLCG'].addShape_Line(x  = body_xPos, 
                                                                           y  = body_bottom, 
                                                                           x2 = body_xPos+body_width, 
                                                                           y2 = body_bottom, 
                                                                           width_y = 1, 
                                                                           color = candleColor, 
                                                                           shapeName = ts_open, shapeGroupName = 'KLINEBODIES', layerNumber = 10)
        self.displayBox_graphics['KLINESPRICE']['RCLCG'].addShape_Rectangle(x = tail_xPos, y = tail_bottom, width = tail_width, height = tail_height, color = candleColor, shapeName = ts_open, shapeGroupName = 'KLINETAILS', layerNumber = 10)
        
        #[5]: Return Drawn Flag
        return 0b1

    def __klineDrawer_SMA(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc    = self.objectConfig
        ap    = self.analysisParams[analysisCode]
        cgt   = self.currentGUITheme
        rclcg = self.displayBox_graphics['KLINESPRICE']['RCLCG']
        lineIndex = ap['lineIndex']

        #[2]: Master & Display Status
        if not oc['SMA_Master']:               return 0b0
        if not oc[f'SMA_{lineIndex}_Display']: return 0b0

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b1
        if not drawSignal:     return 0b0

        #[4]: Data Acquisition
        aData = self.klines[analysisCode]
        timestamp_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
        smaResult_prev = aData.get(timestamp_prev, None)
        smaResult      = aData[timestamp]

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: SMA
        if drawSignal&0b1:
            #[5-1-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[5-1-2]: Drawing
            if (smaResult_prev is not None) and (smaResult_prev['SMA'] is not None):
                #Shape Object Params
                timestampWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                shape_x2 = round(timestamp     +timestampWidth/2, 1)
                shape_y1 = smaResult_prev['SMA']
                shape_y2 = smaResult['SMA']
                width_y  = oc[f'SMA_{lineIndex}_Width']*2
                color = (oc[f'SMA_{lineIndex}_ColorR%{cgt}'], 
                         oc[f'SMA_{lineIndex}_ColorG%{cgt}'], 
                         oc[f'SMA_{lineIndex}_ColorB%{cgt}'], 
                         oc[f'SMA_{lineIndex}_ColorA%{cgt}'])
                #Shape Adding
                rclcg.addShape_Line(x  = shape_x1, y  = shape_y1, 
                                    x2 = shape_x2, y2 = shape_y2,
                                    width_y = width_y,
                                    color = color,
                                    shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = lineIndex)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1
            
        #[6]: Return Drawn Flag
        return drawn

    def __klineDrawer_WMA(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc    = self.objectConfig
        ap    = self.analysisParams[analysisCode]
        cgt   = self.currentGUITheme
        rclcg = self.displayBox_graphics['KLINESPRICE']['RCLCG']
        lineIndex = ap['lineIndex']

        #[2]: Master & Display Status
        if not oc['WMA_Master']:               return 0b0
        if not oc[f'WMA_{lineIndex}_Display']: return 0b0

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b1
        if not drawSignal:     return 0b0

        #[4]: Data Acquisition
        aData = self.klines[analysisCode]
        timestamp_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
        wmaResult_prev = aData.get(timestamp_prev, None)
        wmaResult      = aData[timestamp]
        
        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: WMA
        if drawSignal&0b1:
            #[5-1-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[5-1-2]: Drawing
            if (wmaResult_prev is not None) and (wmaResult_prev['WMA'] is not None):
                #Shape Object Params
                timestampWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                shape_x2 = round(timestamp     +timestampWidth/2, 1)
                shape_y1 = wmaResult_prev['WMA']
                shape_y2 = wmaResult['WMA']
                width_y  = oc[f'WMA_{lineIndex}_Width']*2
                color = (oc[f'WMA_{lineIndex}_ColorR%{cgt}'], 
                         oc[f'WMA_{lineIndex}_ColorG%{cgt}'], 
                         oc[f'WMA_{lineIndex}_ColorB%{cgt}'], 
                         oc[f'WMA_{lineIndex}_ColorA%{cgt}'])
                #Shape Adding
                rclcg.addShape_Line(x  = shape_x1, y  = shape_y1, 
                                    x2 = shape_x2, y2 = shape_y2,
                                    width_y = width_y,
                                    color = color,
                                    shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = lineIndex)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1
            
        #[6]: Return Drawn Flag
        return drawn

    def __klineDrawer_EMA(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc    = self.objectConfig
        ap    = self.analysisParams[analysisCode]
        cgt   = self.currentGUITheme
        rclcg = self.displayBox_graphics['KLINESPRICE']['RCLCG']
        lineIndex = ap['lineIndex']

        #[2]: Master & Display Status
        if not oc['EMA_Master']:               return 0b0
        if not oc[f'EMA_{lineIndex}_Display']: return 0b0

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b1
        if not drawSignal:     return 0b0

        #[4]: Data Acquisition
        aData = self.klines[analysisCode]
        timestamp_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
        emaResult_prev = aData.get(timestamp_prev, None)
        emaResult      = aData[timestamp]
        
        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: EMA
        if drawSignal&0b1:
            #[5-1-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[5-1-2]: Drawing
            if (emaResult_prev is not None) and (emaResult_prev['EMA'] is not None):
                #Shape Object Params
                timestampWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                shape_x2 = round(timestamp     +timestampWidth/2, 1)
                shape_y1 = emaResult_prev['EMA']
                shape_y2 = emaResult['EMA']
                width_y  = oc[f'EMA_{lineIndex}_Width']*2
                color = (oc[f'EMA_{lineIndex}_ColorR%{cgt}'], 
                         oc[f'EMA_{lineIndex}_ColorG%{cgt}'], 
                         oc[f'EMA_{lineIndex}_ColorB%{cgt}'], 
                         oc[f'EMA_{lineIndex}_ColorA%{cgt}'])
                #Shape Adding
                rclcg.addShape_Line(x  = shape_x1, y  = shape_y1, 
                                    x2 = shape_x2, y2 = shape_y2,
                                    width_y = width_y,
                                    color = color,
                                    shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = lineIndex)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1
            
        #[6]: Return Drawn Flag
        return drawn

    def __klineDrawer_PSAR(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc    = self.objectConfig
        ap    = self.analysisParams[analysisCode]
        cgt   = self.currentGUITheme
        rclcg = self.displayBox_graphics['KLINESPRICE']['RCLCG']
        lineIndex = ap['lineIndex']

        #[2]: Master & Display Status
        if not oc['PSAR_Master']:               return 0b0
        if not oc[f'PSAR_{lineIndex}_Display']: return 0b0

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b1
        if not drawSignal:     return 0b0

        #[4]: Data Acquisition
        kData = self.klines['raw']
        aData = self.klines[analysisCode]
        kline_raw = kData[timestamp]
        psar      = aData[timestamp]

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: PSAR
        if drawSignal&0b1:
            #[5-1-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[5-1-2]: Drawing
            if psar['PSAR'] is not None:
                #Shape Object Params
                ts_open  = kline_raw[KLINDEX_OPENTIME]
                ts_close = kline_raw[KLINDEX_CLOSETIME]
                tsWidth = ts_close-ts_open+1
                shape_width = round(tsWidth*0.9, 1)
                shape_xPos  = round(ts_open+(tsWidth-shape_width)/2, 1)
                shape_xPos2 = shape_xPos+shape_width
                shape_yPos  = psar['PSAR']
                shape_yPos2 = psar['PSAR']
                width_y = oc[f'PSAR_{lineIndex}_Width']*3
                color = (oc[f'PSAR_{lineIndex}_ColorR%{cgt}'],
                         oc[f'PSAR_{lineIndex}_ColorG%{cgt}'],
                         oc[f'PSAR_{lineIndex}_ColorB%{cgt}'],
                         oc[f'PSAR_{lineIndex}_ColorA%{cgt}'])
                #Shape Adding
                rclcg.addShape_Line(x  = shape_xPos,  y  = shape_yPos, 
                                    x2 = shape_xPos2, y2 = shape_yPos2,
                                    width_y = width_y,
                                    color = color,
                                    shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = lineIndex)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1

        #[6]: Return Drawn Flag
        return drawn

    def __klineDrawer_BOL(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc    = self.objectConfig
        ap    = self.analysisParams[analysisCode]
        cgt   = self.currentGUITheme
        rclcg = self.displayBox_graphics['KLINESPRICE']['RCLCG']
        lineIndex = ap['lineIndex']

        #[2]: Master & Display Status
        if not oc['BOL_Master']:               return 0b00
        if not oc[f'BOL_{lineIndex}_Display']: return 0b00

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b11
        if not drawSignal:     return 0b00

        #[4]: Data Acquisition
        aData = self.klines[analysisCode]
        timestamp_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
        bolResult_prev = aData.get(timestamp_prev, None)
        bolResult      = aData[timestamp]

        #[5]: Drawing
        drawn = 0b00
        #---[5-1]: Center Line
        if drawSignal&0b01 and oc['BOL_DisplayCenterLine']:
            #[5-1-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode+'_LINE')
            #[5-1-2]: Drawing
            if (ap['nSamples'] < bolResult['_analysisCount']):
                #Shape Object Params
                timestampWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                shape_x2 = round(timestamp     +timestampWidth/2, 1)
                shape_y2 = bolResult['MA']
                width_y  = oc[f'BOL_{lineIndex}_Width']*2
                color = (oc[f'BOL_{lineIndex}_ColorR%{cgt}'],
                         oc[f'BOL_{lineIndex}_ColorG%{cgt}'],
                         oc[f'BOL_{lineIndex}_ColorB%{cgt}'],
                         255)
                #Shape Adding
                rclcg.addShape_Line(x  = shape_x1, y  = bolResult_prev['MA'],
                                    x2 = shape_x2, y2 = shape_y2,
                                    width = None, 
                                    width_x = None, 
                                    width_y = width_y,
                                    color = color,
                                    shapeName = timestamp, shapeGroupName = f"{analysisCode}_LINE", layerNumber = lineIndex)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b01
        #---[5-2]: Band
        if drawSignal&0b10 and oc['BOL_DisplayBand']:
            #[5-2-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode+'_BAND')
            #[5-2-2]: Drawing
            if (ap['nSamples'] < bolResult['_analysisCount']):
                #Shape Object Params
                timestampWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                shape_x2 = round(timestamp     +timestampWidth/2, 1)
                br_bol_prev = bolResult_prev['BOL']
                br_bol      = bolResult['BOL']
                coordinates = ((shape_x1, br_bol_prev[0]),
                               (shape_x2, br_bol[0]),
                               (shape_x2, br_bol[1]),
                               (shape_x1, br_bol_prev[1]))
                color = (oc[f'BOL_{lineIndex}_ColorR%{cgt}'],
                         oc[f'BOL_{lineIndex}_ColorG%{cgt}'],
                         oc[f'BOL_{lineIndex}_ColorB%{cgt}'],
                         oc[f'BOL_{lineIndex}_ColorA%{cgt}'])
                #Shape Adding
                rclcg.addShape_Polygon(coordinates = coordinates, 
                                       color = color,
                                       shapeName = timestamp, shapeGroupName = f"{analysisCode}_BAND", layerNumber = lineIndex)
            #[5-2-3]: Drawn Flag Update
            drawn += 0b10

        #[6]: Return Drawn Flag
        return drawn

    def __klineDrawer_IVP(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        ap  = self.analysisParams[analysisCode]
        cgt = self.currentGUITheme
        rclcg        = self.displayBox_graphics['KLINESPRICE']['RCLCG']
        rclcg_xFixed = self.displayBox_graphics['KLINESPRICE']['RCLCG_XFIXED']

        #[2]: Master & Display Status
        if not oc['IVP_Master']: return 0b00

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b11
        if not drawSignal:     return 0b00

        #[4]: Data Acquisition
        kData = self.klines['raw']
        aData = self.klines[analysisCode]
        kline_raw = kData[timestamp]
        ivpResult = aData[timestamp]

        #[5]: Drawing
        drawn = 0b00
        #---[5-1]: Volume Price Level Profile
        if drawSignal&0b01 and oc['IVP_VPLP_Display'] and timestamp == self.posHighlight_selectedPos:
            #[5-1-1]: Previous Drawing Removal
            rclcg_xFixed.removeGroup(groupName = 'IVP_VPLP')
            #[5-1-2]: Drawing
            vplp_f    = ivpResult['volumePriceLevelProfile_Filtered']
            vplp_fMax = ivpResult['volumePriceLevelProfile_Filtered_Max']
            if vplp_fMax is not None:
                dHeight  = ivpResult['divisionHeight']
                widthMax = 100*oc['IVP_VPLP_DisplayWidth']
                color = (oc[f'IVP_VPLP_ColorR%{cgt}'],
                         oc[f'IVP_VPLP_ColorG%{cgt}'],
                         oc[f'IVP_VPLP_ColorB%{cgt}'],
                         oc[f'IVP_VPLP_ColorA%{cgt}'])
                for dIndex, dStrength in enumerate (vplp_f):
                    dWidth = round(widthMax*dStrength/vplp_fMax, 3)
                    shape_x      = 100-dWidth
                    shape_width  = dWidth
                    shape_y      = dHeight*dIndex
                    shape_height = dHeight
                    rclcg_xFixed.addShape_Rectangle(x = shape_x, width  = shape_width, 
                                                    y = shape_y, height = shape_height,
                                                    color = color,
                                                    shapeName = dIndex, shapeGroupName = 'IVP_VPLP', layerNumber = 0)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b01
        #---[5-2]: Volume Price Level Profile Boundaries
        if drawSignal&0b10 and oc['IVP_VPLPB_Display']:
            #[5-2-1]: Previous Drawing Removal
            rclcg.removeGroup(groupName = f'IVP_VPLPB_{timestamp}')
            #[5-2-2]: Drawing
            vplp_b = ivpResult['volumePriceLevelProfile_Boundaries']
            if vplp_b is not None:
                kl_cp    = kline_raw[KLINDEX_CLOSEPRICE]
                ts_open  = kline_raw[KLINDEX_OPENTIME]
                ts_close = kline_raw[KLINDEX_CLOSETIME]
                tsWidth  = ts_close-ts_open+1
                dr       = oc['IVP_VPLPB_DisplayRegion']
                dHeight  = ivpResult['divisionHeight']
                pb_dr_beg = kl_cp*(1-dr)
                pb_dr_end = kl_cp*(1+dr)
                dIdx_bdr_beg = max(int(pb_dr_beg/dHeight), 0)
                dIdx_bdr_end = min(int(pb_dr_end/dHeight), len(ivpResult['volumePriceLevelProfile'])-1)
                color_rgb = (oc[f'IVP_VPLPB_ColorR%{cgt}'],
                             oc[f'IVP_VPLPB_ColorG%{cgt}'],
                             oc[f'IVP_VPLPB_ColorB%{cgt}'])
                color_a   = oc[f'IVP_VPLPB_ColorA%{cgt}']
                vplp_f    = ivpResult['volumePriceLevelProfile_Filtered']
                vplp_fMax = ivpResult['volumePriceLevelProfile_Filtered_Max']
                shape_x      = ts_open
                shape_width  = tsWidth
                shape_height = dHeight
                for bIndex, dIndex in enumerate(vplp_b):
                    if not (dIdx_bdr_beg <= dIndex <= dIdx_bdr_end): continue
                    shape_y = dHeight*dIndex
                    color_a_eff = int(color_a*(vplp_f[dIndex]/vplp_fMax*0.5+0.5))
                    color = color_rgb+(color_a_eff,)
                    rclcg.addShape_Rectangle(x = shape_x, width  = shape_width, 
                                             y = shape_y, height = shape_height,
                                             color = color,
                                             shapeName = bIndex, shapeGroupName = f'IVP_VPLPB_{timestamp}', layerNumber = 0)
            #[5-2-3]: Drawn Flag Update
            drawn += 0b10
        #[6]: Return Drawn Flag
        return drawn

    def __klineDrawer_SWING(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc    = self.objectConfig
        ap    = self.analysisParams[analysisCode]
        cgt   = self.currentGUITheme
        rclcg = self.displayBox_graphics['KLINESPRICE']['RCLCG']
        lineIndex = ap['lineIndex']

        #[2]: Master & Display Status
        if not oc['SWING_Master']:               return 0b0
        if not oc[f'SWING_{lineIndex}_Display']: return 0b0

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b1
        if not drawSignal:     return 0b0

        #[4]: Data Acquisition
        aData       = self.klines[analysisCode]
        swingResult = aData[timestamp]

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: SWINGS
        if drawSignal&0b1:
            if timestamp == self.posHighlight_selectedPos:
                #[5-1]: Previous Drawing Removal
                rclcg.removeGroup(groupName = f'{analysisCode}_SWINGS')
                #[5-1-2]: Drawing
                swings = swingResult['SWINGS']
                timestamp_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
                timestampWidth = timestamp-timestamp_prev
                color = (oc[f'SWING_{lineIndex}_ColorR%{cgt}'], 
                         oc[f'SWING_{lineIndex}_ColorG%{cgt}'], 
                         oc[f'SWING_{lineIndex}_ColorB%{cgt}'], 
                         oc[f'SWING_{lineIndex}_ColorA%{cgt}'])
                width_y = oc[f'NNA_{lineIndex}_Width']*2
                for sIndex in range (1, len(swings)):
                    swing_prev    = swings[sIndex-1]
                    swing_current = swings[sIndex]
                    shape_x  = round(swing_prev[0]   +timestampWidth/2, 1)
                    shape_x2 = round(swing_current[0]+timestampWidth/2, 1)
                    shape_y  = swing_prev[1]
                    shape_y2 = swing_current[1]
                    rclcg.addShape_Line(x  = shape_x,  y  = shape_y,
                                        x2 = shape_x2, y2 = shape_y2,
                                        color = color,
                                        width   = None, 
                                        width_x = None, 
                                        width_y = width_y,
                                        shapeName = sIndex, shapeGroupName = f'{analysisCode}_SWINGS', layerNumber = 11)
                #[5-1-3]: Drawn Flag Update
                drawn += 0b1
        
        #[6]: Return Drawn Flag
        return drawn

    def __klineDrawer_VOL(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        ap  = self.analysisParams.get(analysisCode, None)
        cgt = self.currentGUITheme
        siViewerIndex = self.siTypes_siViewerAlloc['VOL']
        siViewerCode  = f'SIVIEWER{siViewerIndex}'
        rclcg = self.displayBox_graphics[siViewerCode]['RCLCG']

        #[2]: Master & Display Status
        if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b0
        if not oc['VOL_Master']:                      return 0b0
        if analysisCode != 'VOL':
            lineIndex = ap['lineIndex']
            if not oc[f'VOL_{lineIndex}_Display']: return 0b0

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b1
        if not drawSignal:     return 0b0

        #[4]: Data Acquisition
        #---EMPTY FOR THIS---#

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: Volume
        if drawSignal&0b1 and analysisCode == 'VOL':
            #[5-1-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = 'VOL')
            #[5-1-2]: Drawing
            #---Shape Object Params
            vType = oc['VOL_VolumeType']
            if   vType == 'BASE':    vaIdx = KLINDEX_VOLBASE
            elif vType == 'QUOTE':   vaIdx = KLINDEX_VOLQUOTE
            elif vType == 'BASETB':  vaIdx = KLINDEX_VOLBASETAKERBUY
            elif vType == 'QUOTETB': vaIdx = KLINDEX_VOLQUOTETAKERBUY
            kline_raw = self.klines['raw'][timestamp]
            kl_closeTime  = kline_raw[KLINDEX_CLOSETIME]
            kl_openPrice  = kline_raw[KLINDEX_OPENPRICE]
            kl_closePrice = kline_raw[KLINDEX_CLOSEPRICE]
            tsWidth = kl_closeTime-timestamp+1
            shape_width  = round(tsWidth*0.9, 1)
            shape_xPos   = round(timestamp+(tsWidth-shape_width)/2, 1)
            shape_yPos   = 0
            shape_height = kline_raw[vaIdx]
            kcType = oc['KlineColorType']
            if   kl_openPrice < kl_closePrice: color = self.visualManager.getFromColorTable(f'CHARTDRAWER_KLINECOLOR_TYPE{kcType}_INCREMENTAL') #Incremental
            elif kl_openPrice > kl_closePrice: color = self.visualManager.getFromColorTable(f'CHARTDRAWER_KLINECOLOR_TYPE{kcType}_DECREMENTAL') #Decremental
            else:                              color = self.visualManager.getFromColorTable(f'CHARTDRAWER_KLINECOLOR_TYPE{kcType}_NEUTRAL')     #Neutral
            #---Shape Adding
            rclcg.addShape_Rectangle(x = shape_xPos, y = shape_yPos, 
                                     width = shape_width, height = shape_height, 
                                     color = color, 
                                     shapeName = timestamp, shapeGroupName = 'VOL', layerNumber = 0)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1
        #---[5-2]: Volume MA
        if drawSignal&0b1 and analysisCode != 'VOL':
            aData     = self.klines[analysisCode]
            lineIndex = ap['lineIndex']
            #[5-2-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[5-2-2]: Drawing
            timestamp_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
            volResult_prev = aData.get(timestamp_prev, None)
            volResult      = aData[timestamp]
            if (volResult_prev is not None) and (volResult_prev['MA'] is not None):
                #Shape Object Params
                tsWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+tsWidth/2, 1)
                shape_x2 = round(timestamp     +tsWidth/2, 1)
                shape_y1 = volResult_prev['MA']
                shape_y2 = volResult['MA']
                width_y  = oc[f'VOL_{lineIndex}_Width']*5
                color = (oc[f'VOL_{lineIndex}_ColorR%{cgt}'],
                         oc[f'VOL_{lineIndex}_ColorG%{cgt}'],
                         oc[f'VOL_{lineIndex}_ColorB%{cgt}'],
                         oc[f'VOL_{lineIndex}_ColorA%{cgt}'])
                #Shape Adding
                rclcg.addShape_Line(x = shape_x1, x2 = shape_x2, 
                                    y = shape_y1, y2 = shape_y2, 
                                    width_y = width_y, 
                                    color = color, 
                                    shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = lineIndex+1)
            #[5-2-3]: Drawn Flag Update
            drawn += 0b1

        #[6]: Return Drawn Flag
        return drawn

    def __klineDrawer_NNA(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        ap  = self.analysisParams[analysisCode]
        cgt = self.currentGUITheme
        lineIndex = ap['lineIndex']
        siViewerIndex = self.siTypes_siViewerAlloc['NNA']
        siViewerCode  = f'SIVIEWER{siViewerIndex}'
        rclcg         = self.displayBox_graphics[siViewerCode]['RCLCG']

        #[2]: Master & Display Status
        if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b0
        if not oc['NNA_Master']:                      return 0b0
        if not oc[f'NNA_{lineIndex}_Display']:        return 0b0
        
        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b1
        if not drawSignal:     return 0b0

        #[4]: Data Acquisition
        aData = self.klines[analysisCode]
        timestamp_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
        nnaResult_prev = aData.get(timestamp_prev, None)
        nnaResult      = aData[timestamp]

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: ABSATHREL
        if drawSignal&0b1:
            #[5-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[5-1-2]: Drawing
            if (nnaResult_prev is not None) and (nnaResult_prev['NNA'] is not None):
                #Shape Object Params
                timestampWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                shape_x2 = round(timestamp     +timestampWidth/2, 1)
                shape_y1 = nnaResult_prev['NNA']
                shape_y2 = nnaResult['NNA']
                width_y  = oc[f'NNA_{lineIndex}_Width']*5
                lineColor = (oc[f'NNA_{lineIndex}_ColorR%{cgt}'],
                             oc[f'NNA_{lineIndex}_ColorG%{cgt}'],
                             oc[f'NNA_{lineIndex}_ColorB%{cgt}'],
                             oc[f'NNA_{lineIndex}_ColorA%{cgt}'])
                #Shape Object Params
                rclcg.addShape_Line(x  = shape_x1, 
                                    x2 = shape_x2, 
                                    y  = shape_y1, 
                                    y2 = shape_y2, 
                                    width_y = width_y, 
                                    color   = lineColor, 
                                    shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = lineIndex)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1

        #[6]: Return Drawn Flag
        return drawn

    def __klineDrawer_MMACDSHORT(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        ap  = self.analysisParams[analysisCode]
        cgt = self.currentGUITheme
        siViewerIndex = self.siTypes_siViewerAlloc['MMACDSHORT']
        siViewerCode  = f'SIVIEWER{siViewerIndex}'
        rclcg = self.displayBox_graphics[siViewerCode]['RCLCG']

        #[2]: Master & Display Status
        if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b000
        if not oc['MMACDSHORT_Master']:               return 0b000

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b111
        if not drawSignal:     return 0b000

        #[4]: Data Acquisition
        aData = self.klines[analysisCode]
        timestamp_prev   = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
        mmacdResult_prev = aData.get(timestamp_prev, None)
        mmacdResult      = aData[timestamp]

        #[5]: Common Coordinates
        tsWidth = timestamp-timestamp_prev
        shape_x1 = round(timestamp_prev+tsWidth/2, 1)
        shape_x2 = round(timestamp     +tsWidth/2, 1)

        #[6]: Drawing
        drawn = 0b000
        #---[6-1]: MMACD
        if drawSignal&0b001 and oc['MMACDSHORT_MMACD_Display']:
            #[6-1-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = 'MMACDSHORT_MMACD')
            #[6-1-2]: Drawing
            if (mmacdResult_prev is not None) and (mmacdResult_prev['MMACD'] is not None):
                #Shape Object Params
                shape_y       = mmacdResult_prev['MMACD']
                shape_y2      = mmacdResult['MMACD']
                shape_width_y = 5
                color = (oc[f'MMACDSHORT_MMACD_ColorR%{cgt}'],
                         oc[f'MMACDSHORT_MMACD_ColorG%{cgt}'],
                         oc[f'MMACDSHORT_MMACD_ColorB%{cgt}'],
                         oc[f'MMACDSHORT_MMACD_ColorA%{cgt}'])
                #Shape Adding
                rclcg.addShape_Line(x = shape_x1, x2 = shape_x2, 
                                    y = shape_y,  y2 = shape_y2, 
                                    width_y = shape_width_y, 
                                    color = color, 
                                    shapeName = timestamp, shapeGroupName = 'MMACDSHORT_MMACD', layerNumber = 1)
            #[6-1-3]: Drawn Flag Update
            drawn += 0b001
        #---[6-2]: SIGNAL
        if drawSignal&0b010 and oc['MMACDSHORT_SIGNAL_Display']:
            #[6-2-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = 'MMACDSHORT_SIGNAL')
            #[6-2-2]: Drawing
            if (mmacdResult_prev is not None) and (mmacdResult_prev['SIGNAL'] is not None):
                #Shape Object Params
                shape_y       = mmacdResult_prev['SIGNAL']
                shape_y2      = mmacdResult['SIGNAL']
                shape_width_y = 5
                color = (oc[f'MMACDSHORT_SIGNAL_ColorR%{cgt}'],
                         oc[f'MMACDSHORT_SIGNAL_ColorG%{cgt}'],
                         oc[f'MMACDSHORT_SIGNAL_ColorB%{cgt}'],
                         oc[f'MMACDSHORT_SIGNAL_ColorA%{cgt}'])
                #Shape Adding
                rclcg.addShape_Line(x = shape_x1, x2 = shape_x2,
                                    y = shape_y,  y2 = shape_y2,
                                    width_y = shape_width_y,
                                    color = color,
                                    shapeName = timestamp, shapeGroupName = 'MMACDSHORT_SIGNAL', layerNumber = 1)
            #[6-2-3]: Drawn Flag Update
            drawn += 0b010
        #---[6-3]: HISTOGRAM
        if drawSignal&0b100 and oc['MMACDSHORT_HISTOGRAM_Display']:
            #[6-3-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = 'MMACDSHORT_HISTOGRAM')
            #[6-3-2]: Drawing
            mr_mmacd = mmacdResult['MMACD']
            mr_msd   = mmacdResult['MSDELTA']
            if mr_msd is not None:
                #Shape Object Params
                shape_width = round(tsWidth*0.9, 1)
                shape_xPos  = round(timestamp+(tsWidth-shape_width)/2, 1)
                if 0 <= mr_msd:
                    if 0 <= mr_mmacd:
                        color = (oc[f'MMACDSHORT_HISTOGRAM+_ColorR%{cgt}'],
                                 oc[f'MMACDSHORT_HISTOGRAM+_ColorG%{cgt}'],
                                 oc[f'MMACDSHORT_HISTOGRAM+_ColorB%{cgt}'],
                                 oc[f'MMACDSHORT_HISTOGRAM+_ColorA%{cgt}'])
                    else:
                        color = (oc[f'MMACDSHORT_HISTOGRAM+_ColorR%{cgt}'],
                                 oc[f'MMACDSHORT_HISTOGRAM+_ColorG%{cgt}'],
                                 oc[f'MMACDSHORT_HISTOGRAM+_ColorB%{cgt}'],
                                 int(oc[f'MMACDSHORT_HISTOGRAM+_ColorA%{cgt}']/2))
                    body_y      = 0
                    body_height = mr_msd
                else:
                    if 0 <= mr_mmacd:
                        color = (oc[f'MMACDSHORT_HISTOGRAM-_ColorR%{cgt}'],
                                 oc[f'MMACDSHORT_HISTOGRAM-_ColorG%{cgt}'],
                                 oc[f'MMACDSHORT_HISTOGRAM-_ColorB%{cgt}'],
                                 int(oc[f'MMACDSHORT_HISTOGRAM-_ColorA%{cgt}']/2))
                    else:
                        color = (oc[f'MMACDSHORT_HISTOGRAM-_ColorR%{cgt}'],
                                 oc[f'MMACDSHORT_HISTOGRAM-_ColorG%{cgt}'],
                                 oc[f'MMACDSHORT_HISTOGRAM-_ColorB%{cgt}'],
                                 oc[f'MMACDSHORT_HISTOGRAM-_ColorA%{cgt}'])
                    body_y      = mr_msd
                    body_height = -mr_msd
                #Shape Adding
                rclcg.addShape_Rectangle(x = shape_xPos, y = body_y, 
                                         width = shape_width, height = body_height, 
                                         color = color, 
                                         shapeName = timestamp, shapeGroupName = 'MMACDSHORT_HISTOGRAM', layerNumber = 0)
            #[6-3-3]: Drawn Flag Update
            drawn += 0b100

        #[7]: Return Drawn Flag
        return drawn

    def __klineDrawer_MMACDLONG(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        ap  = self.analysisParams[analysisCode]
        cgt = self.currentGUITheme
        siViewerIndex = self.siTypes_siViewerAlloc['MMACDLONG']
        siViewerCode  = f'SIVIEWER{siViewerIndex}'
        rclcg = self.displayBox_graphics[siViewerCode]['RCLCG']

        #[2]: Master & Display Status
        if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b000
        if not oc['MMACDLONG_Master']:                return 0b000

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b111
        if not drawSignal:     return 0b000

        #[4]: Data Acquisition
        aData = self.klines[analysisCode]
        timestamp_prev   = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
        mmacdResult_prev = aData.get(timestamp_prev, None)
        mmacdResult      = aData[timestamp]

        #[5]: Common Coordinates
        tsWidth = timestamp-timestamp_prev
        shape_x1 = round(timestamp_prev+tsWidth/2, 1)
        shape_x2 = round(timestamp     +tsWidth/2, 1)

        #[6]: Drawing
        drawn = 0b000
        #---[6-1]: MMACD
        if drawSignal&0b001 and oc['MMACDLONG_MMACD_Display']:
            #[6-1-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = 'MMACDLONG_MMACD')
            #[6-1-2]: Drawing
            if (mmacdResult_prev is not None) and (mmacdResult_prev['MMACD'] is not None):
                #Shape Object Params
                shape_y       = mmacdResult_prev['MMACD']
                shape_y2      = mmacdResult['MMACD']
                shape_width_y = 5
                color = (oc[f'MMACDLONG_MMACD_ColorR%{cgt}'],
                         oc[f'MMACDLONG_MMACD_ColorG%{cgt}'],
                         oc[f'MMACDLONG_MMACD_ColorB%{cgt}'],
                         oc[f'MMACDLONG_MMACD_ColorA%{cgt}'])
                #Shape Adding
                rclcg.addShape_Line(x = shape_x1, x2 = shape_x2, 
                                    y = shape_y,  y2 = shape_y2, 
                                    width_y = shape_width_y, 
                                    color = color, 
                                    shapeName = timestamp, shapeGroupName = 'MMACDLONG_MMACD', layerNumber = 1)
            #[6-1-3]: Drawn Flag Update
            drawn += 0b001
        #---[6-2]: SIGNAL
        if drawSignal&0b010 and oc['MMACDLONG_SIGNAL_Display']:
            #[6-2-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = 'MMACDLONG_SIGNAL')
            #[6-2-2]: Drawing
            if (mmacdResult_prev is not None) and (mmacdResult_prev['SIGNAL'] is not None):
                #Shape Object Params
                shape_y       = mmacdResult_prev['SIGNAL']
                shape_y2      = mmacdResult['SIGNAL']
                shape_width_y = 5
                color = (oc[f'MMACDLONG_SIGNAL_ColorR%{cgt}'],
                         oc[f'MMACDLONG_SIGNAL_ColorG%{cgt}'],
                         oc[f'MMACDLONG_SIGNAL_ColorB%{cgt}'],
                         oc[f'MMACDLONG_SIGNAL_ColorA%{cgt}'])
                #Shape Adding
                rclcg.addShape_Line(x = shape_x1, x2 = shape_x2,
                                    y = shape_y,  y2 = shape_y2,
                                    width_y = shape_width_y,
                                    color = color,
                                    shapeName = timestamp, shapeGroupName = 'MMACDLONG_SIGNAL', layerNumber = 1)
            #[6-2-3]: Drawn Flag Update
            drawn += 0b010
        #---[6-3]: HISTOGRAM
        if drawSignal&0b100 and oc['MMACDLONG_HISTOGRAM_Display']:
            #[6-3-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = 'MMACDLONG_HISTOGRAM')
            #[6-3-2]: Drawing
            mr_mmacd = mmacdResult['MMACD']
            mr_msd   = mmacdResult['MSDELTA']
            if mr_msd is not None:
                #Shape Object Params
                shape_width = round(tsWidth*0.9, 1)
                shape_xPos  = round(timestamp+(tsWidth-shape_width)/2, 1)
                if 0 <= mr_msd:
                    if 0 <= mr_mmacd:
                        color = (oc[f'MMACDLONG_HISTOGRAM+_ColorR%{cgt}'],
                                 oc[f'MMACDLONG_HISTOGRAM+_ColorG%{cgt}'],
                                 oc[f'MMACDLONG_HISTOGRAM+_ColorB%{cgt}'],
                                 oc[f'MMACDLONG_HISTOGRAM+_ColorA%{cgt}'])
                    else:
                        color = (oc[f'MMACDLONG_HISTOGRAM+_ColorR%{cgt}'],
                                 oc[f'MMACDLONG_HISTOGRAM+_ColorG%{cgt}'],
                                 oc[f'MMACDLONG_HISTOGRAM+_ColorB%{cgt}'],
                                 int(oc[f'MMACDLONG_HISTOGRAM+_ColorA%{cgt}']/2))
                    body_y      = 0
                    body_height = mr_msd
                else:
                    if 0 <= mr_mmacd:
                        color = (oc[f'MMACDLONG_HISTOGRAM-_ColorR%{cgt}'],
                                 oc[f'MMACDLONG_HISTOGRAM-_ColorG%{cgt}'],
                                 oc[f'MMACDLONG_HISTOGRAM-_ColorB%{cgt}'],
                                 int(oc[f'MMACDLONG_HISTOGRAM-_ColorA%{cgt}']/2))
                    else:
                        color = (oc[f'MMACDLONG_HISTOGRAM-_ColorR%{cgt}'],
                                 oc[f'MMACDLONG_HISTOGRAM-_ColorG%{cgt}'],
                                 oc[f'MMACDLONG_HISTOGRAM-_ColorB%{cgt}'],
                                 oc[f'MMACDLONG_HISTOGRAM-_ColorA%{cgt}'])
                    body_y      = mr_msd
                    body_height = -mr_msd
                #Shape Adding
                rclcg.addShape_Rectangle(x = shape_xPos, y = body_y, 
                                         width = shape_width, height = body_height, 
                                         color = color, 
                                         shapeName = timestamp, shapeGroupName = 'MMACDLONG_HISTOGRAM', layerNumber = 0)
            #[6-3-3]: Drawn Flag Update
            drawn += 0b100

        #[7]: Return Drawn Flag
        return drawn

    def __klineDrawer_DMIxADX(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        ap  = self.analysisParams[analysisCode]
        cgt = self.currentGUITheme
        lineIndex = ap['lineIndex']
        siViewerIndex = self.siTypes_siViewerAlloc['DMIxADX']; 
        siViewerCode = f'SIVIEWER{siViewerIndex}'
        rclcg        = self.displayBox_graphics[siViewerCode]['RCLCG']

        #[2]: Master & Display Status
        if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b0
        if not oc['DMIxADX_Master']:                  return 0b0
        if not oc[f'DMIxADX_{lineIndex}_Display']:    return 0b0
        
        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b1
        if not drawSignal:     return 0b0

        #[4]: Data Acquisition
        aData = self.klines[analysisCode]
        timestamp_prev     = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
        dmixadxResult_prev = aData.get(timestamp_prev, None)
        dmixadxResult      = aData[timestamp]

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: ABSATHREL
        if drawSignal&0b1:
            #[5-1-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[5-1-2]: Drawing
            if (dmixadxResult_prev is not None) and (dmixadxResult_prev['DMIxADX_ABSATHREL'] is not None):
                #Shape Object Params
                timestampWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                shape_x2 = round(timestamp     +timestampWidth/2, 1)
                shape_y1 = dmixadxResult_prev['DMIxADX_ABSATHREL']
                shape_y2 = dmixadxResult['DMIxADX_ABSATHREL']
                width_y  = oc[f'DMIxADX_{lineIndex}_Width']*5
                lineColor = (oc[f'DMIxADX_{lineIndex}_ColorR%{cgt}'],
                             oc[f'DMIxADX_{lineIndex}_ColorG%{cgt}'],
                             oc[f'DMIxADX_{lineIndex}_ColorB%{cgt}'],
                             oc[f'DMIxADX_{lineIndex}_ColorA%{cgt}'])
                #Shape Adding
                rclcg.addShape_Line(x  = shape_x1, 
                                    x2 = shape_x2, 
                                    y  = shape_y1, 
                                    y2 = shape_y2, 
                                    width_y = width_y, 
                                    color   = lineColor, 
                                    shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = lineIndex)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1

        #[6]: Return Drawn Flag
        return drawn

    def __klineDrawer_MFI(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        ap  = self.analysisParams[analysisCode]
        cgt = self.currentGUITheme
        lineIndex = ap['lineIndex']
        siViewerIndex = self.siTypes_siViewerAlloc['MFI']; 
        siViewerCode  = f'SIVIEWER{siViewerIndex}'
        rclcg         = self.displayBox_graphics[siViewerCode]['RCLCG']

        #[2]: Master & Display Status
        if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b0
        if not oc['MFI_Master']:                      return 0b0
        if not oc[f'MFI_{lineIndex}_Display']:        return 0b0
        
        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b1
        if not drawSignal:     return 0b0

        #[4]: Data Acquisition
        aData = self.klines[analysisCode]
        timestamp_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = -1)
        mfiResult_prev = aData.get(timestamp_prev, None)
        mfiResult      = aData[timestamp]

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: ABSATHREL
        if drawSignal&0b1:
            #[5-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[5-1-2]: Drawing
            if (mfiResult_prev is not None) and (mfiResult_prev['MFI_ABSATHREL'] is not None):
                #Shape Object Params
                timestampWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                shape_x2 = round(timestamp     +timestampWidth/2, 1)
                shape_y1 = mfiResult_prev['MFI_ABSATHREL']
                shape_y2 = mfiResult['MFI_ABSATHREL']
                width_y  = oc[f'MFI_{lineIndex}_Width']*5
                lineColor = (oc[f'MFI_{lineIndex}_ColorR%{cgt}'],
                             oc[f'MFI_{lineIndex}_ColorG%{cgt}'],
                             oc[f'MFI_{lineIndex}_ColorB%{cgt}'],
                             oc[f'MFI_{lineIndex}_ColorA%{cgt}'])
                #Shape Object Params
                rclcg.addShape_Line(x  = shape_x1, 
                                    x2 = shape_x2, 
                                    y  = shape_y1, 
                                    y2 = shape_y2, 
                                    width_y = width_y, 
                                    color   = lineColor, 
                                    shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = lineIndex)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1

        #[6]: Return Drawn Flag
        return drawn

    def __klineDrawer_TRADELOG(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc    = self.objectConfig
        cgt   = self.currentGUITheme
        rclcg = self.displayBox_graphics['KLINESPRICE']['RCLCG']

        #[2]: Master & Display Status
        if not oc['TRADELOG_Display']: return 0b0

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b1
        if not drawSignal:     return 0b0

        #[4]: Data Acquisition
        kData = self.klines['raw']
        aData = self.klines[analysisCode]
        kline_raw = kData[timestamp]
        tradeLog  = aData[timestamp]

        #[5]: Drawing
        drawn = 0b0
        if drawSignal&0b1:
            #[5-1-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = 'TRADELOG_BODY')
            rclcg.removeShape(shapeName = timestamp, groupName = 'TRADELOG_LASTTRADE')
            #[5-1-2]: Drawing
            if tradeLog['totalQuantity']:
                #Common Coordinate
                timestamp_next = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = self.mrktRegTS, nTicks = 1)
                shape_x     = timestamp
                shape_x2    = timestamp_next
                shape_width = shape_x2-shape_x
                #Body
                kl_cp = kline_raw[KLINDEX_CLOSEPRICE]
                if 0 < tradeLog['totalQuantity']:
                    if tradeLog['entryPrice'] <= kl_cp: cType =  1
                    else:                               cType = -1
                elif tradeLog['totalQuantity'] < 0:
                    if tradeLog['entryPrice'] <= kl_cp: cType = -1
                    else:                               cType =  1
                if cType == 1:
                    color = (oc[f'TRADELOG_BUY_ColorR%{cgt}'],
                             oc[f'TRADELOG_BUY_ColorG%{cgt}'],
                             oc[f'TRADELOG_BUY_ColorB%{cgt}'],
                             int(oc[f'TRADELOG_BUY_ColorA%{cgt}']/5))
                    shape_y      = tradeLog['entryPrice']
                    shape_height = kl_cp-tradeLog['entryPrice']
                elif cType == -1:
                    color = (oc[f'TRADELOG_SELL_ColorR%{cgt}'],
                             oc[f'TRADELOG_SELL_ColorG%{cgt}'],
                             oc[f'TRADELOG_SELL_ColorB%{cgt}'],
                             int(oc[f'TRADELOG_SELL_ColorA%{cgt}']/5))
                    shape_y      = kl_cp
                    shape_height = tradeLog['entryPrice']-kl_cp
                rclcg.addShape_Rectangle(x = shape_x, y = shape_y, 
                                         width = shape_width, height = shape_height, 
                                         color = color, 
                                         shapeName = timestamp, shapeGroupName = 'TRADELOG_BODY', layerNumber = 11)
                #Last Trade
                if tradeLog['lastTrade'] is not None:
                    lastTrade = tradeLog['lastTrade']
                    if lastTrade[2] == 'BUY':
                        color = (oc[f'TRADELOG_BUY_ColorR%{cgt}'],
                                 oc[f'TRADELOG_BUY_ColorG%{cgt}'],
                                 oc[f'TRADELOG_BUY_ColorB%{cgt}'],
                                 oc[f'TRADELOG_BUY_ColorA%{cgt}'])
                    elif lastTrade[2] == 'SELL':
                        color = (oc[f'TRADELOG_SELL_ColorR%{cgt}'],
                                 oc[f'TRADELOG_SELL_ColorG%{cgt}'],
                                 oc[f'TRADELOG_SELL_ColorB%{cgt}'],
                                 oc[f'TRADELOG_SELL_ColorA%{cgt}'])
                    shape_y  = lastTrade[0]
                    shape_y2 = lastTrade[0]
                    width_y  = 3
                    rclcg.addShape_Line(x = shape_x, x2 = shape_x2, 
                                        y = shape_y, y2 = shape_y2, 
                                        color = color, width_y = width_y, 
                                        shapeName = timestamp, shapeGroupName = 'TRADELOG_LASTTRADE', layerNumber = 12)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1

        #[6]: Return Drawn Flag
        return drawn

    def __klineDrawer_RemoveExpiredDrawings(self, timestamp):
        for analysisCode in self.klines_drawn[timestamp]:
            targetType = analysisCode.split("_")[0]
            if   targetType == 'KLINE':
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = 'KLINEBODIES')
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = 'KLINETAILS')
            elif targetType == 'SMA':
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
            elif targetType == 'WMA':
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
            elif targetType == 'EMA':
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
            elif targetType == 'PSAR':
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
            elif targetType == 'BOL':
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode+'_BAND')
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode+'_LINE')
            elif targetType == 'IVP':
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = f'IVP_VPLPB_{timestamp}')
            elif targetType == 'SWING':
                pass
            elif targetType == 'VOL': 
                siViewerIndex = self.siTypes_siViewerAlloc['VOL']
                if siViewerIndex is not None: 
                    siViewerCode = f"SIVIEWER{siViewerIndex}"
                    self.displayBox_graphics[f"SIVIEWER{siViewerIndex}"]['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
            elif targetType == 'NNA':
                siViewerIndex = self.siTypes_siViewerAlloc['NNA']
                if siViewerIndex is not None: 
                    siViewerCode = f"SIVIEWER{siViewerIndex}"
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
            elif targetType == 'MMACDSHORT':
                siViewerIndex = self.siTypes_siViewerAlloc['MMACDSHORT']
                if siViewerIndex is not None: 
                    siViewerCode = f"SIVIEWER{siViewerIndex}"
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACDSHORT_MMACD')
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACDSHORT_SIGNAL')
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACDSHORT_HISTOGRAM')
            elif targetType == 'MMACDLONG':
                siViewerIndex = self.siTypes_siViewerAlloc['MMACDLONG']
                if siViewerIndex is not None: 
                    siViewerCode = f"SIVIEWER{siViewerIndex}"
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACDLONG_MMACD')
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACDLONG_SIGNAL')
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACDLONG_HISTOGRAM')
            elif targetType == 'DMIxADX':
                siViewerIndex = self.siTypes_siViewerAlloc['DMIxADX']
                if siViewerIndex is not None: 
                    siViewerCode = f"SIVIEWER{siViewerIndex}"
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
            elif targetType == 'MFI':
                siViewerIndex = self.siTypes_siViewerAlloc['MFI']
                if siViewerIndex is not None: 
                    siViewerCode = f"SIVIEWER{siViewerIndex}"
                    self.displayBox_graphics[siViewerCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = analysisCode)
            elif targetType == 'TRADELOG':
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = 'TRADELOG_BODY')
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = 'TRADELOG_LASTTRADE')
        del self.klines_drawn[timestamp]
        
    def __klineDrawer_RemoveDrawings(self, analysisCode, gRemovalSignal = None):
        analysisType = analysisCode.split("_")[0]
        if gRemovalSignal is None: gRemovalSignal = _FULLDRAWSIGNALS[analysisType]
        else:                      gRemovalSignal = gRemovalSignal
        dBox_g = self.displayBox_graphics
        if analysisType == 'SMA':
            if gRemovalSignal&0b1: dBox_g['KLINESPRICE']['RCLCG'].removeGroup(groupName = analysisCode)
        elif analysisType == 'WMA':
            if gRemovalSignal&0b1: dBox_g['KLINESPRICE']['RCLCG'].removeGroup(groupName = analysisCode)
        elif analysisType == 'EMA':
            if gRemovalSignal&0b1: dBox_g['KLINESPRICE']['RCLCG'].removeGroup(groupName = analysisCode)
        elif analysisType == 'PSAR':
            if gRemovalSignal&0b1: dBox_g['KLINESPRICE']['RCLCG'].removeGroup(groupName = analysisCode)
        elif analysisType == 'BOL':
            if gRemovalSignal&0b01: dBox_g['KLINESPRICE']['RCLCG'].removeGroup(groupName = f"{analysisCode}_LINE")
            if gRemovalSignal&0b10: dBox_g['KLINESPRICE']['RCLCG'].removeGroup(groupName = f"{analysisCode}_BAND")
        elif analysisType == 'IVP':
            if gRemovalSignal&0b01: dBox_g['KLINESPRICE']['RCLCG_XFIXED'].removeGroup(groupName = 'IVP_VPLP')
            for ts in self.klines_drawn:
                if 'IVP' not in self.klines_drawn[ts]: continue
                if gRemovalSignal&0b10: dBox_g['KLINESPRICE']['RCLCG'].removeGroup(groupName = f'IVP_VPLPB_{ts}')
        elif analysisType == 'SWING':
            if gRemovalSignal&0b1: dBox_g['KLINESPRICE']['RCLCG'].removeGroup(groupName = f"{analysisCode}_SWINGS")
        elif analysisType == 'VOL':
            siViewerIndex = self.siTypes_siViewerAlloc['VOL']
            if siViewerIndex is not None:
                siViewerCode = f"SIVIEWER{siViewerIndex}"
                if gRemovalSignal&0b1: dBox_g[siViewerCode]['RCLCG'].removeGroup(groupName = analysisCode)
        elif analysisType == 'NNA':
            siViewerIndex = self.siTypes_siViewerAlloc['NNA']
            if siViewerIndex is not None:
                siViewerCode = f"SIVIEWER{siViewerIndex}"
                if gRemovalSignal&0b1: dBox_g[siViewerCode]['RCLCG'].removeGroup(groupName = analysisCode)
        elif analysisType == 'MMACDSHORT':
            siViewerIndex = self.siTypes_siViewerAlloc['MMACDSHORT']
            if siViewerIndex is not None:
                siViewerCode = f"SIVIEWER{siViewerIndex}"
                if gRemovalSignal&0b001: dBox_g[siViewerCode]['RCLCG'].removeGroup(groupName = 'MMACDSHORT_MMACD')
                if gRemovalSignal&0b010: dBox_g[siViewerCode]['RCLCG'].removeGroup(groupName = 'MMACDSHORT_SIGNAL')
                if gRemovalSignal&0b100: dBox_g[siViewerCode]['RCLCG'].removeGroup(groupName = 'MMACDSHORT_HISTOGRAM')
        elif analysisType == 'MMACDLONG':
            siViewerIndex = self.siTypes_siViewerAlloc['MMACDLONG']
            if siViewerIndex is not None:
                siViewerCode = f"SIVIEWER{siViewerIndex}"
                if gRemovalSignal&0b001: dBox_g[siViewerCode]['RCLCG'].removeGroup(groupName = 'MMACDLONG_MMACD')
                if gRemovalSignal&0b010: dBox_g[siViewerCode]['RCLCG'].removeGroup(groupName = 'MMACDLONG_SIGNAL')
                if gRemovalSignal&0b100: dBox_g[siViewerCode]['RCLCG'].removeGroup(groupName = 'MMACDLONG_HISTOGRAM')
        elif analysisType == 'DMIxADX':
            siViewerIndex = self.siTypes_siViewerAlloc['DMIxADX']
            if siViewerIndex is not None:
                siViewerCode = f"SIVIEWER{siViewerIndex}"
                if gRemovalSignal&0b1: dBox_g[siViewerCode]['RCLCG'].removeGroup(groupName = analysisCode)
        elif analysisType == 'MFI':
            siViewerIndex = self.siTypes_siViewerAlloc['MFI']
            if siViewerIndex is not None:
                siViewerCode = f"SIVIEWER{siViewerIndex}"
                if gRemovalSignal&0b1: dBox_g[siViewerCode]['RCLCG'].removeGroup(groupName = analysisCode)
        elif analysisType == 'TRADELOG':
            if gRemovalSignal&0b1: 
                dBox_g['KLINESPRICE']['RCLCG'].removeGroup(groupName = 'TRADELOG_BODY')
                dBox_g['KLINESPRICE']['RCLCG'].removeGroup(groupName = 'TRADELOG_LASTTRADE')
        #---Draw Trackers Reset
        kDrawn     = self.klines_drawn
        kDrawQueue = self.klines_drawQueue
        for ts in kDrawn:
            if analysisCode not in kDrawn[ts]: 
                continue
            kDrawn[ts][analysisCode] &= ~gRemovalSignal
            if not kDrawn[ts][analysisCode]: del kDrawn[ts][analysisCode]
        for ts in kDrawQueue:
            if analysisCode not in kDrawQueue[ts]: 
                continue
            if kDrawQueue[ts][analysisCode] is None: kDrawQueue[ts][analysisCode] = _FULLDRAWSIGNALS[analysisType]&~gRemovalSignal
            else:                                    kDrawQueue[ts][analysisCode] &= ~gRemovalSignal
            if not kDrawQueue[ts][analysisCode]: del kDrawQueue[ts][analysisCode]

    def __bidsAndAsksDrawer_Draw(self):
        #[1]: Parameters
        oc         = self.objectConfig
        cgt        = self.currentGUITheme
        baa        = self.bidsAndAsks
        pPrecision = self.currencyInfo['precisions']['price']
        rclcg_xFixed = self.displayBox_graphics['KLINESPRICE']['RCLCG_XFIXED']

        #[2]: Master & Display Status
        if not oc['BIDSANDASKS_Display']: return

        #[3]: Draw Timer Check
        if time.perf_counter_ns() - self.bidsAndAsks_lastDrawn_ns < 200e6: return
        
        #[4]: Parameters
        lk = self.klines['raw'].get(self.klines_lastStreamedKlineOpenTS, None)
        if lk is None: return
        lk_closePrice = lk[KLINDEX_CLOSEPRICE]
        drawWidth     = 0.20
        id_multiplier = 1
        while True:
            initialDivision = 1e-3*id_multiplier
            plHeight        = round(lk_closePrice*initialDivision, pPrecision)
            if plHeight == 0: id_multiplier += 1
            else: break
            
        #[5]: Display Data
        plForDisplay = dict()
        quantity_max = 0
        for pl in baa['depth']:
            baa_pl         = baa['depth'][pl]
            pl_rounded     = round(int(pl/plHeight)*plHeight, pPrecision)
            if pl_rounded not in plForDisplay: plForDisplay[pl_rounded] = {'BID': 0, 'ASK': 0}
            plfd_this = plForDisplay[pl_rounded]
            plfd_this[baa_pl[0]] += baa_pl[1]
            quantity_max = max(quantity_max, plfd_this[baa_pl[0]])

        #[6]: Remove Previous Shapes
        rclcg_xFixed.removeGroup(groupName = 'BIDSANDASKS')

        #[7]: Drawing
        if 0 < quantity_max:
            color_bids = (oc[f'BIDSANDASKS_BIDS_ColorR%{cgt}'],
                          oc[f'BIDSANDASKS_BIDS_ColorG%{cgt}'],
                          oc[f'BIDSANDASKS_BIDS_ColorB%{cgt}'],
                          oc[f'BIDSANDASKS_BIDS_ColorA%{cgt}'])
            color_asks = (oc[f'BIDSANDASKS_ASKS_ColorR%{cgt}'],
                          oc[f'BIDSANDASKS_ASKS_ColorG%{cgt}'],
                          oc[f'BIDSANDASKS_ASKS_ColorB%{cgt}'],
                          oc[f'BIDSANDASKS_ASKS_ColorA%{cgt}'])
            for pl, pld in plForDisplay.items():
                color     = color_bids if pld['ASK'] < pld['BID'] else color_asks
                bodyWidth = max(pld['ASK'], pld['BID'])/quantity_max*drawWidth*100
                if 0 < bodyWidth: 
                    rclcg_xFixed.addShape_Rectangle(x      = 0, 
                                                    y      = pl-plHeight/2, 
                                                    width  = bodyWidth, 
                                                    height = plHeight, 
                                                    color = color, 
                                                    shapeName = pl, shapeGroupName = 'BIDSANDASKS', layerNumber = 11)
        rclcg_xFixed.processShapeGenerationQueue(timeout_ns = 1e9, currentFocusOnly = True, shapeFocus = ('BIDSANDASKS', None)) #Focused processing to remove blinking

        #[8]: Flag & Last Drawn Time Update
        self.bidsAndAsks_drawFlag     = False
        self.bidsAndAsks_lastDrawn_ns = time.perf_counter_ns()

    def __bidsAndAsksDrawer_Remove(self):
        self.displayBox_graphics['KLINESPRICE']['RCLCG_XFIXED'].removeGroup(groupName = 'BIDSANDASKS')
    
    def __WOIDrawer_Draw(self, time, woiType):
        #[1]: Parameters
        oc  = self.objectConfig
        cgt = self.currentGUITheme

        siViewerIndex = self.siTypes_siViewerAlloc['WOI']
        siViewerCode  = f'SIVIEWER{siViewerIndex}'
        rclcg         = self.displayBox_graphics[siViewerCode]['RCLCG']
        
        baa_WOI       = self.bidsAndAsks[woiType]
        baa_WOI_drawn = self.bidsAndAsks_WOI_drawn

        #[2]: Master & Display Status
        if not oc['WOI_Master']: return
        if woiType == 'WOI':
            if not oc['WOI_BASE_Display']: return
        else:
            lineIndex = int(woiType.split("_")[1])
            if not oc[f'WOI_{lineIndex}_Display']: return

        #[3]: Line-Dependent Drawings
        #---[3-1]: Base
        if woiType == 'WOI':
            woiValue = baa_WOI[time]
            #[3-1-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = time, groupName = woiType)
            #[3-1-2]: Drawing
            #---Shape Object Params
            shape_width = round(BIDSANDASKSSAMPLINGINTERVAL_S*0.9, 1)
            shape_x     = round(time+(BIDSANDASKSSAMPLINGINTERVAL_S-shape_width)/2, 1)
            shape_height = abs(woiValue)
            if   (woiValue < 0):  shape_y = -shape_height
            elif (0 <= woiValue): shape_y = 0
            if woiValue < 0: colorType = "-"
            else:            colorType = "+"
            color = (oc[f'WOI_BASE{colorType}_ColorR%{cgt}'],
                     oc[f'WOI_BASE{colorType}_ColorG%{cgt}'],
                     oc[f'WOI_BASE{colorType}_ColorB%{cgt}'],
                     oc[f'WOI_BASE{colorType}_ColorA%{cgt}'])
            #---Shape Adding
            rclcg.addShape_Rectangle(x = shape_x, y = shape_y, 
                                     width = shape_width, height = shape_height, 
                                     color = color, 
                                     shapeName = time, shapeGroupName = woiType, layerNumber = 0)
        #---[3-2]: Gaussian Deltas
        else:
            lineIndex  = int(woiType.split("_")[1])
            #[3-2-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = time, groupName = woiType)
            #[3-2-2]: Drawing
            basTS_prev = time-BIDSANDASKSSAMPLINGINTERVAL_S
            baa_prev = baa_WOI.get(basTS_prev, None)
            baa      = baa_WOI[time]
            if (baa_prev is not None) and (baa_prev[1] is not None):
                #Shape Object Params
                woiValue_prev = baa_prev[1]
                woiValue_this = baa[1]
                color = (oc[f'WOI_{lineIndex}_ColorR%{cgt}'],
                         oc[f'WOI_{lineIndex}_ColorG%{cgt}'],
                         oc[f'WOI_{lineIndex}_ColorB%{cgt}'],
                         oc[f'WOI_{lineIndex}_ColorA%{cgt}'])
                shape_x1 = round(time-BIDSANDASKSSAMPLINGINTERVAL_S/2, 1)
                shape_x2 = round(time+BIDSANDASKSSAMPLINGINTERVAL_S/2, 1)
                shape_y1 = woiValue_prev
                shape_y2 = woiValue_this
                shape_width_x = 0.1
                shape_width_y = oc[f'WOI_{lineIndex}_Width']*10
                #Shape Adding
                rclcg.addShape_Line(x = shape_x1, x2 = shape_x2, y = shape_y1, y2 = shape_y2, 
                                    width_x = shape_width_x, 
                                    width_y = shape_width_y, 
                                    color = color, 
                                    shapeName = time, shapeGroupName = woiType, layerNumber = lineIndex+1)
                    
        #[4]: Update Drawn Flag
        if time in baa_WOI_drawn: baa_WOI_drawn[time].add(woiType)
        else:                     baa_WOI_drawn[time] = {woiType}
        
    def __WOIDrawer_RemoveExpiredDrawings(self, time):
        if time not in self.bidsAndAsks_WOI_drawn: 
            return
        siViewerIndex = self.siTypes_siViewerAlloc['WOI']
        if siViewerIndex is not None:
            rclcg = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['RCLCG']
            for woiType in self.bidsAndAsks_WOI_drawn[time]: 
                rclcg.removeShape(shapeName = time, groupName = woiType)
        del self.bidsAndAsks_WOI_drawn[time]

    def __WOIDrawer_RemoveDrawings(self, woiType):
        #Drawing Removal
        siViewerIndex = self.siTypes_siViewerAlloc['WOI']
        if siViewerIndex is not None:
            self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['RCLCG'].removeGroup(groupName = woiType)
        #Draw Trackers Reset
        drawn     = self.bidsAndAsks_WOI_drawn
        drawQueue = self.bidsAndAsks_WOI_drawQueue
        #---Drawns
        for ts in drawn:                                    drawn[ts].discard(woiType)
        for ts in [_ts for _ts in drawn if not drawn[_ts]]: drawn.pop(ts, None)
        #---Draw Queues
        for ts in drawQueue:                                        drawQueue[ts].discard(woiType)
        for ts in [_ts for _ts in drawQueue if not drawQueue[_ts]]: drawQueue.pop(ts, None)

    def __NESDrawer_Draw(self, time, nesType):
        #[1]: Parameters
        oc  = self.objectConfig
        cgt = self.currentGUITheme

        siViewerIndex = self.siTypes_siViewerAlloc['NES']
        siViewerCode  = f'SIVIEWER{siViewerIndex}'
        rclcg         = self.displayBox_graphics[siViewerCode]['RCLCG']
        
        at_NES       = self.aggTrades[nesType]
        at_NES_drawn = self.aggTrades_NES_drawn

        #[2]: Master & Display Status
        if not oc['NES_Master']: return
        if nesType == 'NES':
            if not oc['NES_BASE_Display']: return
        else:
            lineIndex = int(nesType.split("_")[1])
            if not oc[f'NES_{lineIndex}_Display']: return

        #[3]: Line-Dependent Drawings
        #---[3-1]: Base
        if nesType == 'NES':
            nesValue = at_NES[time]
            #[3-1-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = time, groupName = nesType)
            #[3-1-2]: Drawing
            #---Shape Object Params
            shape_width = round(AGGTRADESAMPLINGINTERVAL_S*0.9, 1)
            shape_x     = round(time+(AGGTRADESAMPLINGINTERVAL_S-shape_width)/2, 1)
            shape_height = abs(nesValue)
            if   (nesValue < 0):  shape_y = -shape_height
            elif (0 <= nesValue): shape_y = 0
            if nesValue < 0: colorType = "-"
            else:            colorType = "+"
            color = (oc[f'NES_BASE{colorType}_ColorR%{cgt}'],
                     oc[f'NES_BASE{colorType}_ColorG%{cgt}'],
                     oc[f'NES_BASE{colorType}_ColorB%{cgt}'],
                     oc[f'NES_BASE{colorType}_ColorA%{cgt}'])
            #---Shape Adding
            rclcg.addShape_Rectangle(x = shape_x, y = shape_y, 
                                     width = shape_width, height = shape_height, 
                                     color = color, 
                                     shapeName = time, shapeGroupName = nesType, layerNumber = 0)
        #---[3-2]: Gaussian Deltas
        else:
            lineIndex  = int(nesType.split("_")[1])
            #[3-2-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = time, groupName = nesType)
            #[3-2-2]: Drawing
            atTS_prev = time-AGGTRADESAMPLINGINTERVAL_S
            at_prev = at_NES.get(atTS_prev, None)
            at      = at_NES[time]
            if (at_prev is not None) and (at_prev[1] is not None):
                #Shape Object Params
                nesValue_prev = at_prev[1]
                nesValue_this = at[1]
                color = (oc[f'NES_{lineIndex}_ColorR%{cgt}'],
                         oc[f'NES_{lineIndex}_ColorG%{cgt}'],
                         oc[f'NES_{lineIndex}_ColorB%{cgt}'],
                         oc[f'NES_{lineIndex}_ColorA%{cgt}'])
                shape_x1 = round(time-AGGTRADESAMPLINGINTERVAL_S/2, 1)
                shape_x2 = round(time+AGGTRADESAMPLINGINTERVAL_S/2, 1)
                shape_y1 = nesValue_prev
                shape_y2 = nesValue_this
                shape_width_x = 0.1
                shape_width_y = oc[f'NES_{lineIndex}_Width']*10
                #Shape Adding
                rclcg.addShape_Line(x = shape_x1, x2 = shape_x2, y = shape_y1, y2 = shape_y2, 
                                    width_x = shape_width_x, 
                                    width_y = shape_width_y, 
                                    color = color, 
                                    shapeName = time, shapeGroupName = nesType, layerNumber = lineIndex+1)
                    
        #[4]: Update Drawn Flag
        if time in at_NES_drawn: at_NES_drawn[time].add(nesType)
        else:                    at_NES_drawn[time] = {nesType}

    def __NESDrawer_RemoveExpiredDrawings(self, time):
        if time not in self.aggTrades_NES_drawn:
            return
        siViewerIndex = self.siTypes_siViewerAlloc['NES']
        if siViewerIndex is not None:
            rclcg = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['RCLCG']
            for nesType in self.aggTrades_NES_drawn[time]: 
                rclcg.removeShape(shapeName = time, groupName = nesType)
        del self.aggTrades_NES_drawn[time]

    def __NESDrawer_RemoveDrawings(self, nesType):
        #Drawing Removal
        siViewerIndex = self.siTypes_siViewerAlloc['NES']
        if siViewerIndex is not None:
            self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['RCLCG'].removeGroup(groupName = nesType)
        #Draw Trackers Reset
        drawn     = self.aggTrades_NES_drawn
        drawQueue = self.aggTrades_NES_drawQueue
        #---Drawns
        for ts in drawn:                                    drawn[ts].discard(nesType)
        for ts in [_ts for _ts in drawn if not drawn[_ts]]: drawn.pop(ts, None)
        #---Draw Queues
        for ts in drawQueue:                                        drawQueue[ts].discard(nesType)
        for ts in [_ts for _ts in drawQueue if not drawQueue[_ts]]: drawQueue.pop(ts, None)
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
        if self.currencySymbol is not None: self.__onHViewRangeUpdate_UpdateProcessQueue()
        #[2]: Update RCLCGs
        self.__onHViewRangeUpdate_UpdateRCLCGs()
        #[3]: Update Grids
        self.__onHViewRangeUpdate_UpdateGrids(updateType)
        #[4}: Find new vertical extrema within the new horizontalViewRange
        if self.currencySymbol is not None:
            if self.__checkVerticalExtremas_KLINES(): 
                self.__onVerticalExtremaUpdate('KLINESPRICE')
            for siViewerCode in self.displayBox_graphics_visibleSIViewers:
                siIndex = int(siViewerCode[8:])
                siAlloc = self.objectConfig[f'SIVIEWER{siIndex}SIAlloc']
                if self.checkVerticalExtremas_SIs[siAlloc]():
                    if   siAlloc == 'VOL':        self.__editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.0, extension_t = 0.2)
                    elif siAlloc == 'MMACDSHORT': self.__editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                    elif siAlloc == 'MMACDLONG':  self.__editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                    elif siAlloc == 'DMIxADX':    self.__editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                    elif siAlloc == 'MFI':        self.__editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                    elif siAlloc == 'WOI':        self.__editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                    elif siAlloc == 'NES':        self.__editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
        #[5]: Update PosSelection
        self.__updatePosSelection(updateType = 1)
        
    def __onHViewRangeUpdate_UpdateProcessQueue(self):
        #[1]: References
        klines_TSs       = self.klines_timestamps
        hvr_beg, hvr_end = self.horizontalViewRange
        klines_drawn  = self.klines_drawn
        klines_dQueue = self.klines_drawQueue
        klines        = self.klines

        #[2]: If No Timestamp Target Exists, Return
        if not klines_TSs: return

        #[3]: View Range Indices
        vr_idx_beg = bisect.bisect_left(klines_TSs,  hvr_beg)
        vr_idx_end = bisect.bisect_right(klines_TSs, hvr_end)
        
        #[4]: Buffer Zone Range Indices
        nTSsInView = vr_idx_end - vr_idx_beg
        bufLen_back    = int(nTSsInView * _GD_DISPLAYBOX_HVR_BACKWARDBUFFERFACTOR) + 1
        bufLen_forward = int(nTSsInView * _GD_DISPLAYBOX_HVR_FORWARDBUFFERFACTOR)  + 1
        br_idx_beg = max(0,               vr_idx_beg - bufLen_back)
        br_idx_end = min(len(klines_TSs), vr_idx_end + bufLen_forward)
        
        #[5]: View Range Timestamps Update
        self.horizontalViewRange_timestampsInViewRange  = klines_TSs[vr_idx_beg : vr_idx_end]
        self.horizontalViewRange_timestampsInBufferZone = klines_TSs[br_idx_beg : vr_idx_beg] + klines_TSs[vr_idx_end : br_idx_end]

        #[6]: Target Range Timestamps (List & Set)
        br_TSs_list = klines_TSs[br_idx_beg : br_idx_end]
        br_TSs_set  = set(br_TSs_list)

        #[7]: Draw Removal Queue Update
        self.klines_drawRemovalQueue = set(klines_drawn)-br_TSs_set

        #[8]: Draw Queue Update
        dQueue_TSs = set(klines_dQueue)
        for ts in (dQueue_TSs - br_TSs_set):
            del klines_dQueue[ts]
            
        #[9]: Draw Targets Determination
        drawTargets = [('KLINE', _FULLDRAWSIGNALS['KLINE'], klines['raw']), ('VOL', _FULLDRAWSIGNALS['VOL'], klines['raw'])]
        drawTargets.extend((dType, _FULLDRAWSIGNALS[dType.split("_")[0]], klines[dType]) for dType in klines if dType not in _DRAWTARGETRAWNAMEEXCEPTION)
        
        #[10]: Draw Queue Update
        for ts in br_TSs_list:
            #[10-1]: If Drawing Exists Already
            if ts in klines_drawn:
                drawn_ts   = klines_drawn[ts]
                draw_delta = {}
                for dType, fds, data_dict in drawTargets:
                    if ts not in data_dict: continue
                    current_sig = drawn_ts.get(dType, 0)
                    if current_sig != fds:
                        draw_delta[dType] = fds & ~current_sig
                if draw_delta:
                    if ts not in klines_dQueue: klines_dQueue[ts] = {}
                    klines_dQueue[ts].update(draw_delta)
            #[10-2]: If Drawing Does Not Exist
            else:
                klines_dQueue[ts] = {dType: None 
                                    for dType, fds, data_dict in drawTargets 
                                    if ts in data_dict}

    def __onHViewRangeUpdate_UpdateRCLCGs(self):
        dBox_g = self.displayBox_graphics
        hvr_beg, hvr_end = self.horizontalViewRange
        dBox_g['KLINESPRICE']['RCLCG'].updateProjection(projection_x0        = hvr_beg, projection_x1 = hvr_end)
        dBox_g['KLINESPRICE']['RCLCG_YFIXED'].updateProjection(projection_x0 = hvr_beg, projection_x1 = hvr_end)
        for dBoxName in self.displayBox_graphics_visibleSIViewers:
            dBox_g[dBoxName]['RCLCG'].updateProjection(projection_x0        = hvr_beg, projection_x1 = hvr_end)
            dBox_g[dBoxName]['RCLCG_YFIXED'].updateProjection(projection_x0 = hvr_beg, projection_x1 = hvr_end)
            
    def __onHViewRangeUpdate_UpdateGrids(self, updateType):
        #[1]: Parameters
        oc                      = self.objectConfig
        dBox_g                  = self.displayBox_graphics
        vGridIntervalID_current = self.verticalGrid_intervalID
        vGridIntervals_current  = self.verticalGrid_intervals
        mrktRegTS               = self.mrktRegTS
        hvr                     = self.horizontalViewRange

        #[2]: Determine Vertical Grid Intervals
        updateGridContents = False
        if updateType == 1:
            for giID in atmEta_Auxillaries.GRID_INTERVAL_IDs[self.intervalID:]:
                rightEnd       = atmEta_Auxillaries.getNextIntervalTickTimestamp_GRID(giID, hvr[1],           mrktReg = mrktRegTS, nTicks = 1)
                vGridIntervals = atmEta_Auxillaries.getTimestampList_byRange_GRID(giID,     hvr[0], rightEnd, mrktReg = mrktRegTS, lastTickInclusive = True)
                if len(vGridIntervals)+1 < self.nMaxVerticalGridLines: 
                    break
            self.verticalGrid_intervalID = giID
            self.verticalGrid_intervals  = vGridIntervals
            updateGridContents = True
        elif updateType == 0:
            rightEnd       = atmEta_Auxillaries.getNextIntervalTickTimestamp_GRID(vGridIntervalID_current, hvr[1],           mrktReg = mrktRegTS, nTicks = 1)
            vGridIntervals = atmEta_Auxillaries.getTimestampList_byRange_GRID(vGridIntervalID_current,     hvr[0], rightEnd, mrktReg = mrktRegTS, lastTickInclusive = True)
            if (vGridIntervals_current[0] != vGridIntervals[0]) or (vGridIntervals_current[-1] != vGridIntervals[-1]): 
                self.verticalGrid_intervals = vGridIntervals
                updateGridContents = True

        #[2]: Update Grid Position & Text
        vGridIntervalID_current = self.verticalGrid_intervalID
        vGridIntervals_current  = self.verticalGrid_intervals
        pixelPerTS = dBox_g['MAINGRID_TEMPORAL']['DRAWBOX'][2]*self.scaler / (hvr[1]-hvr[0])
        if updateGridContents:
            dBox_g_kp_vgLines  = dBox_g['KLINESPRICE']['VERTICALGRID_LINES']
            dBox_g_mgT_vgLines = dBox_g['MAINGRID_TEMPORAL']['VERTICALGRID_LINES']
            dBox_g_mgT_vgTexts = dBox_g['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS']
            for index in range (self.nMaxVerticalGridLines):
                if index < len(vGridIntervals_current):
                    timestamp         = vGridIntervals_current[index]
                    timestamp_display = timestamp + self.timezoneDelta
                    xPos_Line = round((timestamp-vGridIntervals_current[0])*pixelPerTS, 1)
                    #[1]: KLINESPRICE
                    dBox_g_kp_vgLines[index].x  = xPos_Line
                    dBox_g_kp_vgLines[index].x2 = xPos_Line
                    if not dBox_g_kp_vgLines[index].visible: dBox_g_kp_vgLines[index].visible = True
                    #[2]: MAINGRID_TEMPORAL
                    #---GridLines
                    dBox_g_mgT_vgLines[index].x  = xPos_Line
                    dBox_g_mgT_vgLines[index].x2 = xPos_Line
                    if not dBox_g_mgT_vgLines[index].visible: dBox_g_mgT_vgLines[index].visible = True
                    #---Grid Texts
                    if self.verticalGrid_intervalID <= 10:
                        if timestamp_display % 86400 == 0: dateStrFormat = "%m/%d"
                        else:                              dateStrFormat = "%H:%M"
                    else:
                        if atmEta_Auxillaries.isNewMonth(timestamp_display): dateStrFormat = "%Y/%m"
                        else:                                                dateStrFormat = "%m/%d"
                    dBox_g_mgT_vgTexts[index].setText(datetime.fromtimestamp(timestamp_display, tz = timezone.utc).strftime(dateStrFormat))
                    dBox_g_mgT_vgTexts[index].moveTo(x = round(xPos_Line/self.scaler-_GD_DISPLAYBOX_GRID_VERTICALTEXTWIDTH/2))
                    if dBox_g_mgT_vgTexts[index].hidden: dBox_g_mgT_vgTexts[index].show()
                    #[3]: SIVIEWERs (If Display == True)
                    for siIndex in range (len(_SITYPES)):
                        siCode = f'SIVIEWER{siIndex}'
                        if not oc[f'{siCode}Display']: continue
                        dBox_g_siv_vgLines = dBox_g[siCode]['VERTICALGRID_LINES'][index]
                        dBox_g_siv_vgLines.x  = xPos_Line
                        dBox_g_siv_vgLines.x2 = xPos_Line
                        if not dBox_g_siv_vgLines.visible: 
                            dBox_g_siv_vgLines.visible = True
                else:
                    #[1]: KLINESPRICE
                    if dBox_g_kp_vgLines[index].visible: dBox_g_kp_vgLines[index].visible = False
                    #[2]: MAINGRID_TEMPORAL
                    if dBox_g_mgT_vgLines[index].visible:    dBox_g_mgT_vgLines[index].visible = False
                    if not dBox_g_mgT_vgTexts[index].hidden: dBox_g_mgT_vgTexts[index].hide()
                    #[3]: SIVIEWERs (If Display == True)
                    for siIndex in range (len(_SITYPES)):
                        siCode = f'SIVIEWER{siIndex}'
                        if not oc[f'{siCode}Display']: continue
                        dBox_g_siv_vgLines = dBox_g[siCode]['VERTICALGRID_LINES'][index]
                        if dBox_g_siv_vgLines.visible: dBox_g_siv_vgLines.visible = False

        #Update Grid CamGroup Projections
        proj_x0 = (hvr[0]-vGridIntervals_current[0])*pixelPerTS
        proj_x1 = proj_x0+dBox_g['MAINGRID_TEMPORAL']['DRAWBOX'][2]*self.scaler
        dBox_g['KLINESPRICE']['VERTICALGRID_CAMGROUP'].updateProjection(projection_x0=proj_x0, projection_x1=proj_x1)
        for dBoxName in self.displayBox_graphics_visibleSIViewers: 
            dBox_g[dBoxName]['VERTICALGRID_CAMGROUP'].updateProjection(projection_x0=proj_x0, projection_x1=proj_x1)
        dBox_g['MAINGRID_TEMPORAL']['VERTICALGRID_CAMGROUP'].updateProjection(projection_x0=proj_x0, projection_x1=proj_x1)

    def __checkVerticalExtremas_KLINES(self):
        #[1]: Instances
        klines_raw  = self.klines['raw']
        hvr_tssInVR = self.horizontalViewRange_timestampsInViewRange

        #[2]: Timestamps Check
        if not hvr_tssInVR: return False

        #[3]: Extremas Search
        aIndex_low  = KLINDEX_LOWPRICE
        aIndex_high = KLINDEX_HIGHPRICE
        klines_raw_first = klines_raw[hvr_tssInVR[0]]
        valMin = klines_raw_first[aIndex_low]
        valMax = klines_raw_first[aIndex_high]
        for ts in hvr_tssInVR:
            kline = klines_raw[ts]
            kl_lp = kline[aIndex_low]
            kl_hp = kline[aIndex_high]
            if kl_lp < valMin: valMin = kl_lp
            if valMax < kl_hp: valMax = kl_hp

        #[4]: Change Check & Result Return
        if (self.verticalValue_min['KLINESPRICE'] != valMin) or (self.verticalValue_max['KLINESPRICE'] != valMax): 
            self.verticalValue_min['KLINESPRICE'] = valMin
            self.verticalValue_max['KLINESPRICE'] = valMax
            return True
        return False
            
    def __checkVerticalExtremas_VOL(self):
        #[1]: References
        oc          = self.objectConfig
        ap          = self.analysisParams
        klines      = self.klines
        klines_raw  = klines['raw']
        hvr_tssInVR = self.horizontalViewRange_timestampsInViewRange
        siViewerIndex = self.siTypes_siViewerAlloc['VOL']
        siViewerCode  = f"SIVIEWER{siViewerIndex}"

        #[2]: Timestamps Check
        if not hvr_tssInVR: return False

        #[3]: Extremas Search
        #---Volume Access Index
        volType = oc['VOL_VolumeType']
        if   volType == 'BASE':    aIndex = KLINDEX_VOLBASE
        elif volType == 'QUOTE':   aIndex = KLINDEX_VOLQUOTE
        elif volType == 'BASETB':  aIndex = KLINDEX_VOLBASETAKERBUY
        elif volType == 'QUOTETB': aIndex = KLINDEX_VOLQUOTETAKERBUY
        #---Analysis Codes To Consider
        searchTargets = [('raw', aIndex)]
        searchTargets.extend((dType, 'MA') 
                             for dType in self.siTypes_analysisCodes['VOL'] 
                             if ((dType != 'VOL')  and 
                                 (dType in klines) and 
                                 oc[f"VOL_{ap[dType]['lineIndex']}_Display"]))
        #---Initial Extrema
        klines_raw_first = klines_raw[hvr_tssInVR[0]]
        valMax = klines_raw_first[aIndex]
        #---Search Loop
        for dType, valCode in searchTargets:
            tData = klines[dType]
            if dType == 'raw':
                for ts in hvr_tssInVR:
                    value = tData[ts][valCode]
                    if valMax < value: valMax = value
            else:
                for ts in hvr_tssInVR:
                    if ts not in tData: continue
                    value = tData[ts][valCode]
                    if valMax < value: valMax = value

        #[4]: Change Check & Result Return
        if not self.verticalValue_loaded[siViewerCode] or (self.verticalValue_max[siViewerCode] != valMax):
            self.verticalValue_loaded[siViewerCode] = True
            self.verticalValue_min[siViewerCode] = 0
            self.verticalValue_max[siViewerCode] = valMax
            return True
        else: return False

    def __checkVerticalExtremas_NNA(self):
        #SI Viewer Allocation
        siViewerCode = "SIVIEWER{:d}".format(self.siTypes_siViewerAlloc['NNA'])
        #Extrema Value Init
        valMin = float('inf')
        valMax = float('-inf')
        #Find new vertical extremas
        if (self.siTypes_analysisCodes['NNA'] != None):
            aCodesToConsider = [aCode for aCode in self.siTypes_analysisCodes['NNA'] if self.objectConfig['NNA_{:d}_Display'.format(self.analysisParams[aCode]['lineIndex'])]]
            for ts in self.horizontalViewRange_timestampsInViewRange:
                for analysisCode in aCodesToConsider:
                    if ((analysisCode in self.klines) and (ts in self.klines[analysisCode])):
                        nnaResult = self.klines[analysisCode][ts]
                        nnaResult_nna = nnaResult['NNA']
                        values = []
                        if (nnaResult_nna != None): values.append(nnaResult_nna)
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
            aCodesToConsider = [aCode for aCode in self.siTypes_analysisCodes['DMIxADX'] if self.objectConfig['DMIxADX_{:d}_Display'.format(self.analysisParams[aCode]['lineIndex'])]]
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
            aCodesToConsider = [aCode for aCode in self.siTypes_analysisCodes['MFI'] if self.objectConfig['MFI_{:d}_Display'.format(self.analysisParams[aCode]['lineIndex'])]]
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
        vvr = self.verticalViewRange[displayBoxName]
        if   delta_drag   is not None: effectiveDelta = -delta_drag  *(vvr[1]-vvr[0])/self.displayBox_graphics[displayBoxName]['DRAWBOX'][3]
        elif delta_scroll is not None: effectiveDelta = -delta_scroll*(vvr[1]-vvr[0])/50
        vVR_effective = [vvr[0]+effectiveDelta, vvr[1]+effectiveDelta]
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
        if   self.chartDrawerType == 'CAVIEWER': self.__setTarget_CAViewer(currencyAnalysisCode = target)
        elif self.chartDrawerType == 'TLVIEWER': self.__setTarget_TLViewer(target = target)
        elif self.chartDrawerType == 'ANALYZER': self.__setTarget_Analyzer(currencySymbol = target)
   
    #<Currency Analysis Viewer>
    def __setTarget_CAViewer(self, currencyAnalysisCode):
        #If there was a subscribed currency, send a subscription unregistration request
        if (self.currencySymbol is not None) and (self.currencyAnalysis['allocatedAnalyzer'] is not None): 
            self.__CAViewer_sendCADataSubscriptionUnregistrationRequest()
        #Read Currency Analysis Info
        self.currencyAnalysisCode = currencyAnalysisCode
        if self.currencyAnalysisCode is None:
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
            for dataType in self.klines: self.klines[dataType].clear()
            self.klines_timestamps.clear()
            self.bidsAndAsks = {'depth': dict(), 'WOI': dict(), 'WOI_GD': dict()}
            self.aggTrades['volumes'] = {'samples': list(), 'buy': 0, 'sell': 0}
            for dataType in self.aggTrades: 
                if (dataType != 'volumes'): self.aggTrades[dataType].clear()
            self.klines_fetchComplete           = False
            self.klines_fetching                = False
            self.klines_lastStreamedKlineOpenTS = None
            self.bidsAndAsks_drawFlag             = False
            self.bidsAndAsks_lastDrawn_ns         = 0
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
            for dataType in self.klines: self.klines[dataType].clear()
            self.klines_timestamps.clear()
            self.bidsAndAsks = {'depth': dict(), 'WOI': dict(), 'WOI_GD': dict()}
            self.aggTrades['volumes'] = {'samples': list(), 'buy': 0, 'sell': 0}
            for dataType in self.aggTrades: 
                if (dataType != 'volumes'): self.aggTrades[dataType].clear()
            self.klines_fetchComplete           = False
            self.klines_fetching                = True
            self.klines_lastStreamedKlineOpenTS = None
            self.bidsAndAsks_drawFlag             = False
            self.bidsAndAsks_lastDrawn_ns         = 0
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
        #[1]: Currency Analysis Code Check
        if currencyAnalysisCode != self.currencyAnalysisCode: return

        #[2]: Update Handling
        #---[2-1]: Analyzer Update
        if updateType == 'UPDATE_ANALYZER':
            allocatedAnalyzer = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode, 'allocatedAnalyzer'))
            self.currencyAnalysis['allocatedAnalyzer'] = allocatedAnalyzer
            self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:LOADINGKLINES'))
            self.__CAViewer_sendCADataSubscriptionRegistrationRequest()
        #---[2-2]: Removal
        elif updateType == 'REMOVED': 
            self.setTarget(currencyAnalysisCode = None)
    def __CAViewer_sendCADataSubscriptionRegistrationRequest(self):
        #[1]: Klines Loading Text Box Update
        self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:REQUESTINGCADATASUBSCRIPTIONREGISTRATION'))

        #[2]: FAR Handler Setup & FAR Request Dispatch
        caDataReceiver    = f"caDataReceiver_{self.name}"
        allocatedAnalyzer = self.currencyAnalysis['allocatedAnalyzer']
        self.ipcA.addFARHandler(caDataReceiver, self.__CAViewer_receiveCAData_FAR, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.sendFAR(targetProcess  = f'ANALYZER{allocatedAnalyzer}',
                          functionID     = 'registerCurrencyAnalysisDataSubscription',
                          functionParams = {'currencyAnalysisCode': self.currencyAnalysisCode,
                                            'dataReceiver':         caDataReceiver},
                          farrHandler    = self.__CAViewer_sendCADataSubscriptionRegistrationRequest_FARR)
    def __CAViewer_sendCADataSubscriptionRegistrationRequest_FARR(self, responder, requestID, functionResult):
        #[1]: Source Check
        allocatedAnalyzer = self.currencyAnalysis['allocatedAnalyzer']
        if responder != f'ANALYZER{allocatedAnalyzer}': return

        #[2]: Klines Loading Text Box Update
        self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:LOADINGKLINES'))

        #[3]: Analysis Parameters Read
        self.analysisParams = functionResult['analysisParams']
        #---[3-1]: VOL
        self.siTypes_analysisCodes['VOL'] = {'VOL'}
        for aCode in self.analysisParams:
            if aCode.startswith('VOL'): self.siTypes_analysisCodes['VOL'].add(aCode)
        #---[3-2]: NNA
        aCodes_nna = [aCode for aCode in self.analysisParams if aCode.startswith('NNA')]
        if aCodes_nna: self.siTypes_analysisCodes['NNA'] = set(aCodes_nna)
        #---[3-3]: MMACDs
        if 'MMACDSHORT' in self.analysisParams: self.siTypes_analysisCodes['MMACDSHORT'] = set(['MMACDSHORT'])
        if 'MMACDLONG'  in self.analysisParams: self.siTypes_analysisCodes['MMACDLONG']  = set(['MMACDLONG'])
        #---[3-4]: MFI
        aCodes_mfi = [aCode for aCode in self.analysisParams if aCode.startswith('MFI')]
        if aCodes_mfi: self.siTypes_analysisCodes['MFI'] = set(aCodes_mfi)
        #---[3-5]: DMIxADX
        aCodes_dmixadx = [aCode for aCode in self.analysisParams if aCode.startswith('DMIxADX')]
        if aCodes_dmixadx: self.siTypes_analysisCodes['DMIxADX'] = set(aCodes_dmixadx)

        #[4]: Analysis Data Read
        fr_klines = functionResult['klines']
        fr_baa    = functionResult['bidsAndAsks']
        fr_at     = functionResult['aggTrades']
        if fr_klines is not None: self.__CAViewer_receiveCAData(dataType = 'KLINES',      caData = fr_klines)
        if fr_baa    is not None: self.__CAViewer_receiveCAData(dataType = 'BIDSANDASKS', caData = fr_baa)
        if fr_at     is not None: self.__CAViewer_receiveCAData(dataType = 'AGGTRADES',   caData = fr_at)
    def __CAViewer_sendCADataSubscriptionUnregistrationRequest(self):
        caDataReceiver    = f"caDataReceiver_{self.name}"
        allocatedAnalyzer = self.currencyAnalysis['allocatedAnalyzer']
        self.ipcA.removeFARHandler(caDataReceiver)
        self.ipcA.sendFAR(targetProcess  = f'ANALYZER{allocatedAnalyzer}',
                          functionID     = 'unregisterCurrencyAnalysisDataSubscription',
                          functionParams = {'currencyAnalysisCode': self.currencyAnalysisCode,
                                            'dataReceiver':         caDataReceiver},
                          farrHandler    = None)
    def __CAViewer_receiveCAData(self, dataType, caData):
        #[1]: Klines
        if dataType == 'KLINES':
            klines        = self.klines
            klines_TSs    = self.klines_timestamps
            klines_dQueue = self.klines_drawQueue
            #[1-1]: Data Import
            for kldType in caData:
                #[1-1]: Data Type Formatting
                if kldType not in klines: klines[kldType] = dict()
                #[1-2]: Instances
                kl_dType = klines[kldType]
                hvr_beg, hvr_end = self.horizontalViewRange
                #[1-3]: Receive Data And Update Queue
                for ts, cad_dType_ts in caData[kldType].items(): kl_dType[ts] = cad_dType_ts

            #[1-2]: Received Timestamps
            timestamps = sorted(caData['raw'])

            #[1-3]: Draw Queue Update
            dQueueUpdateTargets = [kldType for kldType in caData if kldType not in ('raw', 'raw_status')]+['KLINE',]
            for ts_open in timestamps:
                ts_close = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = ts_open, mrktReg = self.mrktRegTS, nTicks = 1)-1
                classification = 0
                classification += 0b1000*(0 <= ts_open -hvr_beg)
                classification += 0b0100*(0 <= ts_open -hvr_end)
                classification += 0b0010*(0 <  ts_close-hvr_beg)
                classification += 0b0001*(0 <  ts_close-hvr_end)
                if classification in (0b0010, 0b1010, 0b1011, 0b0011):
                    for dqu in dQueueUpdateTargets:
                        if ts_open in klines_dQueue: klines_dQueue[ts_open][dqu] = None
                        else:                        klines_dQueue[ts_open] = {dqu: None}
    #
            #[1-4]: Timestamps Tracker Update
            for ts in timestamps:
                ts_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = ts, mrktReg = self.mrktRegTS, nTicks = -1)
                if (self.klines_lastStreamedKlineOpenTS is None) or (self.klines_lastStreamedKlineOpenTS == ts_prev):
                    self.klines_lastStreamedKlineOpenTS = ts
                    klines_TSs.append(ts)
                elif self.klines_lastStreamedKlineOpenTS < ts:
                    print(termcolor.colored((f"[GUI-{self.name}] Data Discontinuity Detected While Importing Data From The Analyzer.\n"
                                             f" * Last Received Timestamp: {self.klines_lastStreamedKlineOpenTS}\n"
                                             f" * Received Timestamp:      {ts}\n"
                                             ), 
                                            'light_red'))
                
            #[1-5]: Fetch Completion Handler
            if not self.klines_fetchComplete: self.__CAViewer_onKlineFetchComplete()

        #[2]: Bids And Asks
        elif dataType == 'BIDSANDASKS':
            baa        = self.bidsAndAsks
            baa_dQueue = self.bidsAndAsks_WOI_drawQueue
            for baadType in caData:
                if baadType not in baa: baa[baadType] = dict()
                if baadType == 'depth': 
                    baa['depth'] = caData['depth']
                else:
                    baa_dType = baa[baadType]
                    for tt, cad_dType_tt in caData[baadType].items(): 
                        baa_dType[tt] = cad_dType_tt
                        if tt in baa_dQueue: baa_dQueue[tt].add(baadType)
                        else:                baa_dQueue[tt] = {baadType}
            self.bidsAndAsks_drawFlag = True

        #[3]: AggTrades
        elif dataType == 'AGGTRADES':
            at        = self.aggTrades
            at_dQueue = self.aggTrades_NES_drawQueue
            for atdType in caData:
                if atdType == 'volumes': continue
                if atdType not in at: at[atdType] = dict()
                at_dType = at[atdType]
                for tt, cad_dType_tt in caData[atdType].items():
                    at_dType[tt] = cad_dType_tt
                    if tt in at_dQueue: at_dQueue[tt].add(atdType)
                    else:               at_dQueue[tt] = {atdType}
    def __CAViewer_receiveCAData_FAR(self, requester, currencyAnalysisCode, dataType, caData):
        #[1]: Source Check
        allocatedAnalyzer = self.currencyAnalysis['allocatedAnalyzer']
        if allocatedAnalyzer is None:                         return
        if requester != f"ANALYZER{allocatedAnalyzer}":       return
        if currencyAnalysisCode != self.currencyAnalysisCode: return

        #[2]: Data Receive
        self.__CAViewer_receiveCAData(dataType = dataType, caData = caData)
    def __CAViewer_onKlineFetchComplete(self):
        #[1]: Control Variables Update
        self.klines_fetchComplete = True
        self.klines_fetching      = False

        #[2]: Loading Indicator Graphics Control
        self.frameSprites['KLINELOADINGCOVER'].visible = False
        self.klinesLoadingGaugeBar.hide()
        self.klinesLoadingTextBox_perc.hide()
        self.klinesLoadingTextBox.hide()

        #[3]: Horizontal ViewRange Reset
        self.horizontalViewRange_magnification = 80
        self.horizontalViewRange = [None, round(time.time()+self.expectedKlineTemporalWidth*2)]
        self.horizontalViewRange[0] = round(self.horizontalViewRange[1]-(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
        self.__onHViewRangeUpdate(1)

        #[4]: Vertical ViewRange Reset
        self.__editVVR_toExtremaCenter('KLINESPRICE')
        for siViewerCode in self.displayBox_graphics_visibleSIViewers: self.__editVVR_toExtremaCenter(siViewerCode)

    #<TradeLogViewer>
    def __setTarget_TLViewer(self, target):
        #Read Currency Analysis Info
        if target is None:
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
            for dataType in self.klines: self.klines[dataType].clear()
            self.klines_timestamps.clear()
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
            self.bidsAndAsks_lastDrawn_ns         = 0
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
            self.neuralNetworkConnectionDataRequestIDs = dict()
            self.neuralNetworkInstances                = dict()
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
            analysisParams, invalidLines = atmEta_Analyzers.constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration(_currencyAnalysisConfiguration)
            if invalidLines:
                invalidLines_str = atmEta_Auxillaries.formatInvalidLinesReportToString(invalidLines = invalidLines)
                print(termcolor.colored((f"[GUI-{self.name}] Invalid lines detected while attempting to construct analysis params for TL Viewing."+invalidLines_str), 'light_red'))
                analysisParams = dict()
            self.analysisParams = analysisParams
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
            for dataType in self.klines: self.klines[dataType].clear()
            self.klines_timestamps.clear()
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
            self.bidsAndAsks_lastDrawn_ns         = 0
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
            self.neuralNetworkConnectionDataRequestIDs = dict()
            self.neuralNetworkInstances                = dict()
            torch.cuda.empty_cache()
            #Horizontal ViewRange Params Setup
            self.__setHVRParams()
            #Get Currency Precisions & Update RCLCG Precisions
            self.__initializeRCLCGs('KLINESPRICE')
            for siViewerCode in self.displayBox_graphics_visibleSIViewers: self.__initializeSIViewer(siViewerCode)
            #Send a trade log fetch request
            if (self.klines_targetFetchRange_original != None): self.simulationTradeLog_RID = self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'fetchSimulationTradeLogs', functionParams = {'simulationCode': self.simulationCode}, farrHandler = self.__TLViewer_onTradeLogFetchResponse_FARR)
    def __TLViewer_onTradeLogFetchResponse_FARR(self, responder, requestID, functionResult):
        #[1]: Responder Check
        if responder != 'DATAMANAGER': return

        #[2]: Result Read
        result         = functionResult['result']
        simulationCode = functionResult['simulationCode']
        tradeLogs      = functionResult['tradeLogs']
        failureType    = functionResult['failureType']

        #[3]: Simulation Code & Request ID Check
        if simulationCode != self.simulationCode:         return
        if requestID      != self.simulationTradeLog_RID: return

        #[4]: Result Interpretation
        #---[4-1]: Failure Handling
        if not result:
            print(termcolor.colored(f"[GUI-{self.name}] A failure returned from DATAMANAGER while attempting to fetch tradeLog for simulation '{simulationCode}'.\n *", 'light_red'), termcolor.colored(failureType, 'light_red'))
            self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:TRADELOGDATAFETCHFAILED'))
            self.simulationTradeLog_RID = None
            return
        #---[4-2]: Record the TRADELOG data in a displayable format
        tData = self.klines['TRADELOG']
        for tIdx, tradeLog in enumerate(tradeLogs):
            if tradeLog['positionSymbol'] != self.currencySymbol: continue
            ts_effective = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = tradeLog['timestamp'], mrktReg = None, nTicks = 0)
            lastTrade = 0 if tradeLog['totalQuantity'] == 0 else (tradeLog['price'], tradeLog['logicSource'], tradeLog['side'])
            tData[ts_effective] = {'logIndex':               tIdx,
                                   'logicSource':         tradeLog['logicSource'],
                                   'side':                tradeLog['side'],
                                   'quantity':            tradeLog['quantity'],
                                   'price':               tradeLog['price'],
                                   'profit':              tradeLog['profit'],
                                   'tradingFee':          tradeLog['tradingFee'],
                                   'totalQuantity':       tradeLog['totalQuantity'],
                                   'entryPrice':          tradeLog['entryPrice'],
                                   'lastTrade':           lastTrade,
                                   'tradeControlTracker': tradeLog['tradeControlTracker']}
        for ts in atmEta_Auxillaries.getTimestampList_byRange(intervalID        = self.intervalID, 
                                                              timestamp_beg     = self.klines_targetFetchRange_original[0], 
                                                              timestamp_end     = self.klines_targetFetchRange_original[1], 
                                                              mrktReg           = self.mrktRegTS, 
                                                              lastTickInclusive = True): 
            if ts in tData: continue
            ts_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = ts, mrktReg = self.mrktRegTS, nTicks = -1)
            if ts_prev not in tData: continue
            prevTradeLog_Formatted = tData[ts_prev]
            tData[ts] = {'logIndex':            prevTradeLog_Formatted['logIndex'],
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
        #---[4-3]: Send Neural Network Connections Data Requests
        #------NNA Codes Collection
        cac = self.simulation['currencyAnalysisConfigurations'][self.simulation['positions'][self.currencySymbol]['currencyAnalysisConfigurationCode']]
        nns_prd  = self.ipcA.getPRD(processName = 'NEURALNETWORKMANAGER', prdAddress = 'NEURALNETWORKS')
        nn_codes = set()
        if cac['NNA_Master']:
            for lineIndex in range (_NMAXLINES['NNA']):
                nn_lineActive = cac[f'NNA_{lineIndex}_LineActive']
                nn_code       = cac[f'NNA_{lineIndex}_NeuralNetworkCode']
                if not nn_lineActive:      continue
                if nn_code is None:        continue
                if nn_code not in nns_prd: continue
                nn_codes.add(nn_code)
        #---Requests Dispatch
        if nn_codes:
            nns       = self.neuralNetworkInstances
            nncd_rIDs = self.neuralNetworkConnectionDataRequestIDs
            for nn_code in nn_codes:
                nncd_rID = self.ipcA.sendFAR(targetProcess = "NEURALNETWORKMANAGER",
                                            functionID     = 'getNeuralNetworkConnections',
                                            functionParams = {'neuralNetworkCode': nn_code},
                                            farrHandler    = self.__TLViewer_onNeuralNetworkConnectionsDataRequestResponse_FARR)
                nns[nn_code]        = None
                nncd_rIDs[nncd_rID] = nn_code
            return

        #[5]: Start Klines Fetch
        self.__TLViewer_startFetchingKlines()
    def __TLViewer_onNeuralNetworkConnectionsDataRequestResponse_FARR(self, responder, requestID, functionResult):
        nns       = self.neuralNetworkInstances
        nncd_rIDs = self.neuralNetworkConnectionDataRequestIDs

        #[1]: Source Validity Check
        if responder != 'NEURALNETWORKMANAGER': return
        if requestID not in nncd_rIDs:          return

        #[2]: RID Removal
        nnCode = nncd_rIDs.pop(requestID)

        #[3]: Result Handling
        if functionResult is not None:
            nKlines      = functionResult['nKlines']
            hiddenLayers = functionResult['hiddenLayers']
            outputLayer  = functionResult['outputLayer']
            connections  = functionResult['connections']
            nn = atmEta_NeuralNetworks.neuralNetwork_MLP(nKlines      = nKlines, 
                                                         hiddenLayers = hiddenLayers, 
                                                         outputLayer  = outputLayer, 
                                                         device = 'cpu')
            nn.importConnectionsData(connections = connections)
            nn.setEvaluationMode()
            nns[nnCode] = nn

        #[4]: Request Results Check
        if not nncd_rIDs:
            if all(nns[nnCode] is not None for nnCode in nns):
                self.__TLViewer_startFetchingKlines()
            else:
                eMsg = f"[GUI-{self.name}] A failure returned from NEURALNETWORKMANAGER while attempting to load neural network connections data for the following models."
                for nnCode in (nnCode for nnCode, nn in nns.items() if nn is None): eMsg += f"\n * '{nnCode}'"
                print(termcolor.colored(eMsg, 'light_red'))
                self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:NEURALNETWORKCONNECTIONSDATAREQUESTFAILED'))
    def __TLViewer_startFetchingKlines(self):
        #[1]: Display Objects Update
        self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:LOADINGKLINES'))
        self.klinesLoadingGaugeBar.updateGaugeValue(0)
        self.klinesLoadingTextBox_perc.updateText("0.000 %")

        #[2]: Determine The Effective Target Fetch Range
        tfRange_end_max = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = self.klines_targetFetchRange_current[0], mrktReg = None, nTicks = _KLINES_MAXFETCHLENGTH)-1
        tfRange_eff     = (self.klines_targetFetchRange_current[0], min(tfRange_end_max, self.klines_targetFetchRange_current[1]))
        
        #[3]: Send Fetch Request To The DATAMANAGER
        self.klines_fetchRequestRID = self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                                                        functionID     = 'fetchKlines', 
                                                        functionParams = {'symbol':    self.currencySymbol, 
                                                                          'fetchRange': tfRange_eff}, 
                                                        farrHandler    = self.__TLViewer_onKlineFetchResponse_FARR)
    def __TLViewer_onKlineFetchResponse_FARR(self, responder, requestID, functionResult):
        #[1]: Source Check
        if responder != 'DATAMANAGER':               return
        if requestID != self.klines_fetchRequestRID: return

        #[2]: Instances
        klines = self.klines
        klines_raw        = klines['raw']
        klines_raw_status = klines['raw_status']

        #[3]: Result Interpretation
        rr_result = functionResult['result']
        rr_klines = functionResult['klines']
        #---[3-1]: Successful Kline Fetch
        if rr_result == 'SKF':
            #[3-1-1]: Save the received klines
            for kline in rr_klines: 
                t_open = kline[0]
                klines_raw[t_open]        = kline[:11]+(True,)
                klines_raw_status[t_open] = {'p_max': kline[3]}
                t_open_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = t_open, mrktReg = self.mrktRegTS, nTicks = -1)
                if t_open_prev in klines_raw_status: klines_raw_status[t_open]['p_max'] = max(klines_raw_status[t_open_prev]['p_max'], kline[3])

            #[3-1-2]: Update the target fetch range
            fkRange = (rr_klines[0][0], rr_klines[-1][1])
            if (self.klines_targetFetchRange_current[0] == fkRange[0]) and (self.klines_targetFetchRange_current[1] == fkRange[1]): self.klines_targetFetchRange_current = None
            else:                                                                                                                   self.klines_targetFetchRange_current[0] = fkRange[1]+1

            #[3-1-3]: If Fetching Has Completed
            if self.klines_targetFetchRange_current is None:
                #[3-1-3-1]: Update Fetch Process Graphics
                self.klinesLoadingGaugeBar.updateGaugeValue(100)
                self.klinesLoadingTextBox_perc.updateText(text = "100 %")

                #[3-1-3-2]: Update Fetch Control Variables
                self.klines_fetchComplete = True
                self.klines_fetching      = False

                #[3-1-3-3]: Fetch Completion Handler
                self.__TLViewer_onKlineFetchComplete()

            #[3-1-4]: If Fetching Has Not Completed
            else:
                #[3-1-4-1]: Update The Fetch Progress Graphics
                tsLen_original = self.klines_targetFetchRange_original[1]-self.klines_targetFetchRange_original[0]+1
                tsLen_current  = self.klines_targetFetchRange_current[1] -self.klines_targetFetchRange_current[0] +1
                fetchCompletion_perc = round((tsLen_original-tsLen_current)/tsLen_original*100, 3)
                self.klinesLoadingGaugeBar.updateGaugeValue(fetchCompletion_perc)
                self.klinesLoadingTextBox_perc.updateText(text = f"{fetchCompletion_perc:.3f} %")

                #[3-1-4-2]: Send The Next Fetch Request
                tfRange_end_max = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = self.klines_targetFetchRange_current[0], mrktReg = None, nTicks = _KLINES_MAXFETCHLENGTH)-1
                tfRange_eff     = (self.klines_targetFetchRange_current[0], min(tfRange_end_max, self.klines_targetFetchRange_current[1]))
                self.klines_fetchRequestRID = self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                                                                functionID     = 'fetchKlines', 
                                                                functionParams = {'symbol':     self.currencySymbol, 
                                                                                  'fetchRange': tfRange_eff}, 
                                                                farrHandler    = self.__TLViewer_onKlineFetchResponse_FARR)
        
        #---[3-2]: Unexpected Error Occurrance
        elif rr_result == 'UEO': 
            pass
    def __TLViewer_onKlineFetchComplete(self):
        #[1]: Display Objects Update
        self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:REGENERATINGANALYSISDATA'))
        self.klinesLoadingGaugeBar.updateGaugeValue(0)
        self.klinesLoadingTextBox_perc.updateText(text = "0.000 %")

        #[2]: Preparation Range
        pRange = sorted(self.klines['raw'])

        #[3]: Timestamps Construction
        self.klines_timestamps = pRange.copy()

        #[4]: Analysis Setup
        self.analysisQueue_list = pRange.copy()
        self.analysisQueue_set.update(pRange)
        self.caRegeneration_nAnalysis_initial = len(pRange)
        self.analysisToProcess_Sorted         = list()
        for siType in _SITYPES:                  self.siTypes_analysisCodes[siType] = list()
        for aCode  in self.analysisParams:       self.klines[aCode] = dict()
        for aType  in _ANALYSIS_GENERATIONORDER: self.analysisToProcess_Sorted += [(aType, aCode) for aCode in self.analysisParams if aCode.startswith(aType)]
        for siType in _SITYPES:                  self.siTypes_analysisCodes[siType] = [aCode for aCode in self.analysisParams if aCode.startswith(siType)]

        #[5]: Fetch Control Variables Update
        self.klines_targetFetchRange_current = None
        self.klines_fetchComplete = True
        self.klines_fetching      = False

        #[6]: Reset ViewRange
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
        if self.currencySymbol is not None: 
            self.ipcA.removeFARHandler(functionID = f'onKlineStreamReceival_{self.name}')
            self.ipcA.removeFARHandler(functionID = f'onOrderbookUpdate_{self.name}')
            self.ipcA.removeFARHandler(functionID = f'onAggTradeStreamReceival_{self.name}')
            self.ipcA.sendFAR(targetProcess = 'BINANCEAPI', functionID = 'unregisterKlineStreamSubscription', functionParams = {'subscriptionID': self.name, 'currencySymbol': self.currencySymbol}, farrHandler = None)
        self.currencySymbol = currencySymbol
        if self.currencySymbol is None:
            self.currencyInfo = None
            #Setup Klines Loading Gauge Objects
            self.frameSprites['KLINELOADINGCOVER'].visible = False
            self.klinesLoadingGaugeBar.hide()
            self.klinesLoadingTextBox.hide()
            self.klinesLoadingTextBox_perc.hide()
            self.klinesLoadingGaugeBar.updateGaugeValue(0)
            self.klinesLoadingTextBox_perc.updateText("-")
            #Reset Klines
            for dType in self.klines: self.klines[dType].clear()
            self.klines_timestamps.clear()
            for dType in self.bidsAndAsks: self.bidsAndAsks[dType].clear()
            self.aggTrades['volumes'] = {'samples': list(), 'buy': 0, 'sell': 0}
            for dType in self.aggTrades: 
                if dType != 'volumes': self.aggTrades[dType].clear()
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
            self.bidsAndAsks_lastDrawn_ns         = 0
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
            self.neuralNetworkConnectionDataRequestIDs = dict()
            self.neuralNetworkInstances                = dict()
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
            for dType in self.klines: self.klines[dType].clear()
            self.klines_timestamps.clear()
            for dType in self.bidsAndAsks: self.bidsAndAsks[dType].clear()
            self.aggTrades['volumes'] = {'samples': list(), 'buy': 0, 'sell': 0}
            for dType in self.aggTrades: 
                if dType != 'volumes': self.aggTrades[dType].clear()
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
            self.bidsAndAsks_lastDrawn_ns         = 0
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
            self.neuralNetworkConnectionDataRequestIDs = dict()
            self.neuralNetworkInstances                = dict()
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
            self.ipcA.addFARHandler(f'onKlineStreamReceival_{self.name}',    self.__Analyzer_onKlineStreamReceival,    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
            self.ipcA.addFARHandler(f'onOrderbookUpdate_{self.name}',        self.__Analyzer_onOrderBookUpdate,        executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
            self.ipcA.addFARHandler(f'onAggTradeStreamReceival_{self.name}', self.__Analyzer_onAggTradeStreamReceival, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
            self.ipcA.sendFAR(targetProcess  = 'BINANCEAPI', 
                              functionID     = 'registerKlineStreamSubscription', 
                              functionParams = {'subscriptionID':       self.name, 
                                                'currencySymbol':       self.currencySymbol, 
                                                'subscribeBidsAndAsks': True,
                                                'subscribeAggTrades':   True},
                              farrHandler    = None)
    def __Analyzer_onKlineStreamReceival(self, requester, symbol, streamConnectionTime, kline, closed):
        #[1]: Requester & Symbol Check
        if requester != 'BINANCEAPI':     return
        if symbol != self.currencySymbol: return

        #[2]: Instances
        klines     = self.klines
        klines_TSs = self.klines_timestamps
        klines_raw        = klines['raw']
        klines_raw_status = klines['raw_status']
        klines_dQueue     = self.klines_drawQueue

        #[3]: Save the kline
        kline  = kline[:11]
        t_open = kline[0]
        klines_raw[t_open]        = kline+(closed,)
        klines_raw_status[t_open] = {'p_max': kline[3]}
        t_open_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = t_open, mrktReg = self.mrktRegTS, nTicks = -1)
        if t_open_prev in klines_raw_status: klines_raw_status[t_open]['p_max'] = max(klines_raw_status[t_open_prev]['p_max'], kline[3])
        self.klines_lastStreamedKlineOpenTS = t_open

        #[4]: Discontinuity Check
        newStreamConnection = (streamConnectionTime != self.klines_firstStreamedKlineOpenTS[1])
        discontinued        = (klines_TSs and t_open != klines_TSs[-1] and t_open_prev != klines_TSs[-1])

        #[5]: If New Stream Connection or Discontinuity Has Occurred
        if newStreamConnection or discontinued:
            #[5-1]: Stream Control Variables
            self.klines_fetchComplete = False
            self.klines_fetching      = True
            self.klines_prepStatus    = None
            self.klines_firstStreamedKlineOpenTS = (kline[0], streamConnectionTime)
            self.klines_fetchRequestRID          = None

            #[5-2]: Loading Graphics Update
            self.frameSprites['KLINELOADINGCOVER'].visible = True
            self.klinesLoadingGaugeBar.show()
            self.klinesLoadingTextBox.show()
            self.klinesLoadingTextBox_perc.show()
            self.klinesLoadingGaugeBar.updateGaugeValue(0)
            self.klinesLoadingTextBox_perc.updateText("-")
            self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGDATAAVAILABLE'))

            #[5-3]: If the first open TS is not yet identified, return
            if self.currencyInfo['kline_firstOpenTS'] is None: 
                self.klines_firstStreamedKlineOpenTS = None
                return
            
            #[5-4]: Determine the target fetch range and check data availability, and update the prep status
            if self.klines_lastPreparedKlineOpenTS is None: tfRange_beg = self.currencyInfo['kline_firstOpenTS']
            else:                                           tfRange_beg = self.klines_lastPreparedKlineOpenTS
            tfRange_end = kline[0]-1
            if tfRange_beg < tfRange_end:
                self.klines_prepStatus = _KLINES_PREPSTATUS_WAITINGDATAAVAILABLE
                self.klines_targetFetchRange_original = (tfRange_beg, tfRange_end)
                self.klines_targetFetchRange_current  = [tfRange_beg, tfRange_end]
                self.__Analyzer_checkKlineDataAvailable()
            else: 
                self.klines_fetchComplete = True
                self.klines_fetching      = False
                self.__Analyzer_onKlineFetchComplete()

        #[6]: If New Stream Connection or Discontinuity Has Not Occurred
        else:
            #[6-1]: If Not In A Fetching Status
            if self.klines_fetchComplete:
                #[6-1-1]: Update The Last Prepare Klines Open TS (This Means The Kline Is Ready For Further Processings)
                self.klines_lastPreparedKlineOpenTS = t_open
                if not klines_TSs or t_open != klines_TSs[-1]: klines_TSs.append(t_open)

                #[6-1-2]: Determine if this kline is within the horizontalViewRange, if it is, add to the drawing queue
                hvr_beg, hvr_end = self.horizontalViewRange
                t_close          = kline[1]
                classification = 0
                classification += 0b1000*(0 <= t_open -hvr_beg)
                classification += 0b0100*(0 <= t_open -hvr_end)
                classification += 0b0010*(0 <  t_close-hvr_beg)
                classification += 0b0001*(0 <  t_close-hvr_end)
                if classification in (0b0010, 0b1010, 0b1011, 0b0011):
                    if t_open in klines_dQueue: klines_dQueue[t_open]['KLINE'] = None
                    else:                       klines_dQueue[t_open] = {'KLINE': None}

                #[6-1-3]: If In A Streaming Analysis Mode, Add Analysis Queue
                if self.analyzingStream and t_open not in self.analysisQueue_set:
                    self.analysisQueue_set.add(t_open)
                    self.analysisQueue_list.append(t_open)

            #[6-2]: If In A Fetching Status
            elif self.klines_prepStatus == _KLINES_PREPSTATUS_WAITINGDATAAVAILABLE: 
                self.__Analyzer_checkKlineDataAvailable()
    def __Analyzer_onOrderBookUpdate(self, requester, symbol, streamConnectionTime, bids, asks):
        #[1]: Source Check
        if requester != 'BINANCEAPI':     return
        if symbol != self.currencySymbol: return

        #[2]: Instances
        oc     = self.objectConfig
        aCodes = self.siTypes_analysisCodes['WOI']

        #[3]: Data Read & Analysis Generation
        (newOldestComputed, 
         newLatestComputed, 
         updatedItems
         ) = atmEta_Analyzers.updateBidsAndAsks(bidsAndAsks    = self.bidsAndAsks,
                                                newBidsAndAsks = (bids, asks),
                                                oldestComputed = self.bidsAndAsks_WOI_oldestComputedS,
                                                latestComputed = self.bidsAndAsks_WOI_latestComputedS,
                                                analysisLines  = [(aCode, oc[f'{aCode}_NSamples'], oc[f'{aCode}_Sigma']) for aCode in aCodes])
        
        #[4]: Variables Update
        self.bidsAndAsks_WOI_oldestComputedS = newOldestComputed
        self.bidsAndAsks_WOI_latestComputedS = newLatestComputed
        self.bidsAndAsks_drawFlag = True

        #[5]: Draw Queue Update
        for updateType, woiType, tt in updatedItems:
            #[5-1]: Added
            if updateType == 1:
                if tt in self.bidsAndAsks_WOI_drawQueue: self.bidsAndAsks_WOI_drawQueue[tt].add(woiType)
                else:                                    self.bidsAndAsks_WOI_drawQueue[tt] = {woiType}
            #[5-2]: Removed
            elif updateType == -1: self.bidsAndAsks_WOI_drawRemovalQueue.add(tt)
    def __Analyzer_onAggTradeStreamReceival(self, requester, symbol, streamConnectionTime, aggTrade):
        #[1]: Source Check
        if requester != 'BINANCEAPI':     return
        if symbol != self.currencySymbol: return

        #[2]: Instances
        oc     = self.objectConfig
        aCodes = self.siTypes_analysisCodes['NES']

        #[3]: Data Read & Analysis Generation
        (newOldestComputed, 
         newLatestComputed, 
         updatedItems) = atmEta_Analyzers.updateAggTrades(aggTrades      = self.aggTrades,
                                                          newAggTrade    = aggTrade,
                                                          oldestComputed = self.aggTrades_NES_oldestComputedS,
                                                          latestComputed = self.aggTrades_NES_latestComputedS,
                                                          analysisLines  = [(aCode, oc[f'{aCode}_NSamples'], oc[f'{aCode}_Sigma']) for aCode in aCodes])
        #[4]: Variables Update
        self.aggTrades_NES_oldestComputedS = newOldestComputed
        self.aggTrades_NES_latestComputedS = newLatestComputed

        #[5]: Draw Queue Update
        for updateType, nesType, tt in updatedItems:
            #[5-1]: Added
            if updateType == 1:
                if tt in self.aggTrades_NES_drawQueue: self.aggTrades_NES_drawQueue[tt].add(nesType)
                else:                                  self.aggTrades_NES_drawQueue[tt] = {nesType}
            #[5-2]: Removed
            elif updateType == -1: self.aggTrades_NES_drawRemovalQueue.add(tt)
    def __Analyzer_checkKlineDataAvailable(self):
        #[1]: Kline Available Ranges Existence Check
        klineAvailableRanges = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', self.currencySymbol, 'kline_availableRanges'))
        if klineAvailableRanges is None: return

        #[2]: Data Ranges Check
        for dataRange in klineAvailableRanges:
            #[2-1]: Availability Check
            if not ((dataRange[0] <= self.klines_targetFetchRange_original[0]) and (self.klines_targetFetchRange_original[1] <= dataRange[1])): continue

            #[2-2]: Update the prep status and graphics
            self.klines_prepStatus = _KLINES_PREPSTATUS_FETCHING
            self.klinesLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_CHARTDRAWER:LOADINGKLINES'))
            self.klinesLoadingTextBox_perc.updateText("0.000 %")

            #[2-3]: Determine the effective target fetch range
            tfRange_end_max = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = self.klines_targetFetchRange_original[0], mrktReg = None, nTicks = _KLINES_MAXFETCHLENGTH)-1
            tfRange_eff = (self.klines_targetFetchRange_original[0], min(tfRange_end_max, self.klines_targetFetchRange_original[1]))
            
            #[2-4]: Send fetch request to the datamanager
            self.klines_fetchRequestRID = self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                                                            functionID     = 'fetchKlines', 
                                                            functionParams = {'symbol':     self.currencySymbol, 
                                                                              'fetchRange': tfRange_eff}, 
                                                            farrHandler    = self.__Analyzer_onKlineFetchResponse_FARR)

            #[2-5]: Exit Function
            return
    def __Analyzer_onKlineFetchResponse_FARR(self, responder, requestID, functionResult):
        #[1]: Source Check
        if responder != 'DATAMANAGER':               return
        if requestID != self.klines_fetchRequestRID: return

        #[2]: Instances
        klines = self.klines
        klines_raw        = klines['raw']
        klines_raw_status = klines['raw_status']

        #[3]: Result Interpretation
        rr_result = functionResult['result']
        rr_klines = functionResult['klines']
        #---[3-1]: Successful Kline Fetch
        if rr_result == 'SKF':
            #[3-1-1]: Save the received klines
            for kline in rr_klines: 
                t_open = kline[0]
                klines_raw[t_open]        = kline[:11]+(True,)
                klines_raw_status[t_open] = {'p_max': kline[3]}
                t_open_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = t_open, mrktReg = self.mrktRegTS, nTicks = -1)
                if t_open_prev not in klines_raw_status: continue
                klines_raw_status[t_open]['p_max'] = max(klines_raw_status[t_open_prev]['p_max'], kline[3])

            #[3-1-2]: Update the target fetch range
            fkRange = (rr_klines[0][0], rr_klines[-1][1])
            if (self.klines_targetFetchRange_current[0] == fkRange[0]) and (self.klines_targetFetchRange_current[1] == fkRange[1]): self.klines_targetFetchRange_current = None
            else:                                                                                                                   self.klines_targetFetchRange_current[0] = fkRange[1]+1
            
            #[3-1-3]: Update the fetch progress graphics
            #---[3-1-3-1]: Fetching Has Completed
            if self.klines_targetFetchRange_current is None:
                #Update the fetch progress graphics
                self.klinesLoadingGaugeBar.updateGaugeValue(100)
                self.klinesLoadingTextBox_perc.updateText(text = "100 %")
                self.klines_fetchComplete = True
                self.klines_fetching      = False
                self.__Analyzer_onKlineFetchComplete()
            #---[3-1-3-2]: Fetching Has Not Completed
            else:
                #Update the fetch progress graphics
                tsLen_original = self.klines_targetFetchRange_original[1]-self.klines_targetFetchRange_original[0]+1
                tsLen_current  = self.klines_targetFetchRange_current[1] -self.klines_targetFetchRange_current[0] +1
                fetchCompletion_perc = round((tsLen_original-tsLen_current)/tsLen_original*100, 3)
                self.klinesLoadingGaugeBar.updateGaugeValue(fetchCompletion_perc)
                self.klinesLoadingTextBox_perc.updateText(text = f"{fetchCompletion_perc:.3f} %")
                #Send another fetch request
                tfRange_end_max = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = self.klines_targetFetchRange_current[0], mrktReg = None, nTicks = _KLINES_MAXFETCHLENGTH)-1
                tfRange_end_eff = min(tfRange_end_max, self.klines_targetFetchRange_current[1])
                tfRange_eff = (self.klines_targetFetchRange_current[0], tfRange_end_eff)
                self.klines_fetchRequestRID = self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                                                                functionID     = 'fetchKlines', 
                                                                functionParams = {'symbol':     self.currencySymbol, 
                                                                                  'fetchRange': tfRange_eff}, 
                                                                farrHandler    = self.__Analyzer_onKlineFetchResponse_FARR)
        
        #---[3-2]: Unexpected Error Occurrance
        elif rr_result == 'UEO': 
            pass
    def __Analyzer_onKlineFetchComplete(self):
        #[1]: If this is the first ever kline fetch completion, reset the view
        resetView = (self.klines_lastPreparedKlineOpenTS is None)

        #[2]: Reset Fetch Control Variables
        self.klines_prepStatus                = None
        self.klines_targetFetchRange_original = None
        self.klines_targetFetchRange_current  = None
        self.klines_fetchRequestRID           = None

        #[3]: Klines Preparation
        if self.klines_fetchComplete:
            #[3-1]: Preparation Range
            pRange_beg = self.currencyInfo['kline_firstOpenTS'] if (self.klines_lastPreparedKlineOpenTS is None) else self.klines_lastPreparedKlineOpenTS
            pRange_end = self.klines_lastStreamedKlineOpenTS
            pRangeList = atmEta_Auxillaries.getTimestampList_byRange(intervalID = self.intervalID, timestamp_beg = pRange_beg, timestamp_end = pRange_end, mrktReg = self.mrktRegTS, lastTickInclusive = True)

            #[3-2]: Preparation
            self.klines_timestamps = sorted(self.klines['raw'])
            self.klines_lastPreparedKlineOpenTS = pRange_end

            #[3-3]: Draw Queue Update
            hvr_beg, hvr_end = self.horizontalViewRange
            kl_dQueue = self.klines_drawQueue
            for ts_open in pRangeList:
                ts_close = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = ts_open, mrktReg = None, nTicks = 1)-1
                classification = 0
                classification += 0b1000*(0 <= ts_open -hvr_beg)
                classification += 0b0100*(0 <= ts_open -hvr_end)
                classification += 0b0010*(0 <  ts_close-hvr_beg)
                classification += 0b0001*(0 <  ts_close-hvr_end)
                if classification not in (0b0010, 0b1010, 0b1011, 0b0011): continue
                if ts_open in kl_dQueue: kl_dQueue[ts_open]['KLINE'] = None
                else:                    kl_dQueue[ts_open] = {'KLINE': None}

            #[3-4]: Analysis Queue Update (If needed)
            if self.analyzingStream:
                aQueue_list = self.analysisQueue_list
                aQueue_set  = self.analysisQueue_set
                for ts in pRangeList:
                    if ts in aQueue_set: continue
                    aQueue_list.append(ts)
                    aQueue_set.add(ts)
                aQueue_list.sort()

        #[4]: Loading Indicator Graphics Control
        self.frameSprites['KLINELOADINGCOVER'].visible = False
        self.klinesLoadingGaugeBar.hide()
        self.klinesLoadingTextBox_perc.hide()
        self.klinesLoadingTextBox.hide()

        #[5]: Horizontal ViewRange Reset
        if resetView:
            self.horizontalViewRange_magnification = 80
            self.horizontalViewRange = [None, round(time.time()+self.expectedKlineTemporalWidth*2)]
            self.horizontalViewRange[0] = round(self.horizontalViewRange[1]-(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
            self.__onHViewRangeUpdate(1)
            #Vertical ViewRange Reset
            self.__editVVR_toExtremaCenter('KLINESPRICE')
            for siViewerCode in self.displayBox_graphics_visibleSIViewers: self.__editVVR_toExtremaCenter(siViewerCode)

        #[6]: Analysis Availability Check
        self.__Analyzer_checkIfCanPerformAnalysis()
    def __Analyzer_checkIfCanPerformAnalysis(self):
        #[1]: Analysis Range
        rangeBeg = self.objectConfig['AnalysisRangeBeg']
        rangeEnd = self.objectConfig['AnalysisRangeEnd']

        #[2]: Analyzable Check
        if self.currencySymbol is None: result = False
        else:
            if rangeBeg is None: result = False
            else:
                if (self.currencyInfo['kline_firstOpenTS'] <= rangeBeg) and (rangeBeg <= self.klines_lastStreamedKlineOpenTS): 
                    if rangeEnd is None: result = True
                    else:                result = (rangeBeg < rangeEnd) and (rangeEnd <= self.klines_lastStreamedKlineOpenTS)
                else: result = False

        #[3]: Result Interpretation
        if result: 
            self.canStartAnalysis = True
            self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
        else:                 
            self.canStartAnalysis = False
            self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].deactivate()
    def __Analyzer_requestNeuralNetworksConnectionsData(self, neuralNetworkCodes):
        nns       = self.neuralNetworkInstances
        nncd_rIDs = self.neuralNetworkConnectionDataRequestIDs
        for nn_code in neuralNetworkCodes:
            nncd_rID = self.ipcA.sendFAR(targetProcess = "NEURALNETWORKMANAGER",
                                        functionID     = 'getNeuralNetworkConnections',
                                        functionParams = {'neuralNetworkCode': nn_code},
                                        farrHandler    = self.__Analyzer_onNeuralNetworkConnectionsDataRequestResponse_FARR)
            nns[nn_code]        = None
            nncd_rIDs[nncd_rID] = nn_code
    def __Analyzer_onNeuralNetworkConnectionsDataRequestResponse_FARR(self, responder, requestID, functionResult):
        nns       = self.neuralNetworkInstances
        nncd_rIDs = self.neuralNetworkConnectionDataRequestIDs

        #[1]: Source Validity Check
        if responder != 'NEURALNETWORKMANAGER': return
        if requestID not in nncd_rIDs:          return

        #[2]: RID Removal
        nnCode = nncd_rIDs.pop(requestID)

        #[3]: Result Handling
        if functionResult is not None:
            nKlines      = functionResult['nKlines']
            hiddenLayers = functionResult['hiddenLayers']
            outputLayer  = functionResult['outputLayer']
            connections  = functionResult['connections']
            nn = atmEta_NeuralNetworks.neuralNetwork_MLP(nKlines      = nKlines, 
                                                         hiddenLayers = hiddenLayers, 
                                                         outputLayer  = outputLayer, 
                                                         device = 'cpu')
            nn.importConnectionsData(connections = connections)
            nn.setEvaluationMode()
            nns[nnCode] = nn

        #[4]: Request Results Check
        if not nncd_rIDs:
            if all(nns[nnCode] is not None for nnCode in nns):
                self.__Analyzer_startAnalysis()
            else:
                eMsg = f"[GUI-{self.name}] A failure returned from NEURALNETWORKMANAGER while attempting to load neural network connections data for the following models."
                for nnCode in (nnCode for nnCode, nn in nns.items() if nn is None): eMsg += f"\n * '{nnCode}'"
                print(termcolor.colored(eMsg, 'light_red'))
                self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
    def __Analyzer_startAnalysis(self):
        #[1]: Reset previous analysis Data, drawings and analysis process queue
        for aCode in [dType for dType in self.klines if dType not in ('raw', 'raw_status')]:
            self.__klineDrawer_RemoveDrawings(analysisCode = aCode, gRemovalSignal = None)
            del self.klines[aCode]
        self.analysisQueue_list.clear()
        self.analysisQueue_set.clear()
        self.klines_drawQueue.clear()
        #[2]: Construct a new analysis params
        self.analysisParams           = dict()
        self.analysisToProcess_Sorted = list()
        for siType in _SITYPES:
            if siType in ('WOI', 'NES'): continue
            self.siTypes_analysisCodes[siType] = list()
        analysisParams, invalidLines = atmEta_Analyzers.constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration(self.objectConfig)
        #[3]: Prepare Analysis
        if invalidLines:
            #[3-1]: Analysis Start Button
            self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()
            #[3-2]: Invalid Lines Display
            invalidLines_str = atmEta_Auxillaries.formatInvalidLinesReportToString(invalidLines = invalidLines)
            print(termcolor.colored((f"[GUI-{self.name}] Invalid lines detected while attempting to start currency analysis."+invalidLines_str), 'light_red'))
            #[3-3]: Exit Function
            return
        self.analysisParams = analysisParams
        for aCode in self.analysisParams: self.klines[aCode] = dict()
        for aType in _ANALYSIS_GENERATIONORDER: self.analysisToProcess_Sorted.extend([(aType, aCode) for aCode in self.analysisParams if aCode[:len(aType)] == aType])
        for siType in _SITYPES: 
            if siType in ('WOI', 'NES'): continue
            self.siTypes_analysisCodes[siType] = [aCode for aCode in self.analysisParams if aCode[:len(siType)] == siType]
        #Add Analysis Queue
        atTSs = atmEta_Auxillaries.getTimestampList_byRange(intervalID        = self.intervalID, 
                                                            timestamp_beg     = self.objectConfig['AnalysisRangeBeg'], 
                                                            timestamp_end     = self.klines_lastPreparedKlineOpenTS if self.objectConfig['AnalysisRangeEnd'] is None else self.objectConfig['AnalysisRangeEnd']+1, 
                                                            mrktReg           = self.mrktRegTS, 
                                                            lastTickInclusive = True)
        self.analysisQueue_list.extend(atTSs)
        self.analysisQueue_set.update(atTSs)
        #Stream Mode
        self.analyzingStream = (self.objectConfig['AnalysisRangeEnd'] is None)
        #Analysis Start Button
        self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].deactivate()

    # * <Shared>
    def __readCurrencyAnalysisConfiguration(self, currencyAnalysisConfiguration):
        oc  = self.objectConfig
        cac = currencyAnalysisConfiguration
        guios_MAIN       = self.settingsSubPages['MAIN'].GUIOs
        guios_SMA        = self.settingsSubPages['SMA'].GUIOs
        guios_WMA        = self.settingsSubPages['WMA'].GUIOs
        guios_EMA        = self.settingsSubPages['EMA'].GUIOs
        guios_PSAR       = self.settingsSubPages['PSAR'].GUIOs
        guios_BOL        = self.settingsSubPages['BOL'].GUIOs
        guios_IVP        = self.settingsSubPages['IVP'].GUIOs
        guios_SWING      = self.settingsSubPages['SWING'].GUIOs
        guios_VOL        = self.settingsSubPages['VOL'].GUIOs
        guios_NNA        = self.settingsSubPages['NNA'].GUIOs
        guios_MMACDSHORT = self.settingsSubPages['MMACDSHORT'].GUIOs
        guios_MMACDLONG  = self.settingsSubPages['MMACDLONG'].GUIOs
        guios_DMIxADX    = self.settingsSubPages['DMIxADX'].GUIOs
        guios_MFI        = self.settingsSubPages['MFI'].GUIOs
        guios_WOI        = self.settingsSubPages['WOI'].GUIOs
        guios_NES        = self.settingsSubPages['NES'].GUIOs
        #SMA
        if cac['SMA_Master']:
            guios_MAIN["MAININDICATOR_SMA"].activate()
            guios_MAIN["MAININDICATORSETUP_SMA"].activate()
            for lineIndex in range (_NMAXLINES['SMA']):
                if cac[f'SMA_{lineIndex}_LineActive']:
                    nSamples = cac[f'SMA_{lineIndex}_NSamples']
                    width    = oc[f'SMA_{lineIndex}_Width']
                    display  = oc[f'SMA_{lineIndex}_Display']
                    guios_SMA[f"INDICATOR_SMA{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
                    guios_SMA[f"INDICATOR_SMA{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
                    guios_SMA[f"INDICATOR_SMA{lineIndex}_WIDTHINPUT"].activate()
                    guios_SMA[f"INDICATOR_SMA{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
                    guios_SMA[f"INDICATOR_SMA{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                    guios_SMA[f"INDICATOR_SMA{lineIndex}_DISPLAY"].activate()
                else:
                    guios_SMA[f"INDICATOR_SMA{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_SMA[f"INDICATOR_SMA{lineIndex}_INTERVALINPUT"].updateText("-")
                    guios_SMA[f"INDICATOR_SMA{lineIndex}_WIDTHINPUT"].deactivate()
                    guios_SMA[f"INDICATOR_SMA{lineIndex}_DISPLAY"].deactivate()
                    guios_SMA[f"INDICATOR_SMA{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
        else:
            guios_MAIN["MAININDICATOR_SMA"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MAIN["MAININDICATOR_SMA"].deactivate()
            guios_MAIN["MAININDICATORSETUP_SMA"].deactivate()
        #WMA
        if cac['WMA_Master']:
            guios_MAIN["MAININDICATOR_WMA"].activate()
            guios_MAIN["MAININDICATORSETUP_WMA"].activate()
            for lineIndex in range (_NMAXLINES['WMA']):
                if cac[f'WMA_{lineIndex}_LineActive']:
                    nSamples = cac[f'WMA_{lineIndex}_NSamples']
                    width    = oc[f'WMA_{lineIndex}_Width']
                    display  = oc[f'WMA_{lineIndex}_Display']
                    guios_WMA[f"INDICATOR_WMA{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
                    guios_WMA[f"INDICATOR_WMA{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
                    guios_WMA[f"INDICATOR_WMA{lineIndex}_WIDTHINPUT"].activate()
                    guios_WMA[f"INDICATOR_WMA{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
                    guios_WMA[f"INDICATOR_WMA{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                    guios_WMA[f"INDICATOR_WMA{lineIndex}_DISPLAY"].activate()
                else:
                    guios_WMA[f"INDICATOR_WMA{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_WMA[f"INDICATOR_WMA{lineIndex}_INTERVALINPUT"].updateText("-")
                    guios_WMA[f"INDICATOR_WMA{lineIndex}_WIDTHINPUT"].deactivate()
                    guios_WMA[f"INDICATOR_WMA{lineIndex}_DISPLAY"].deactivate()
                    guios_WMA[f"INDICATOR_WMA{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
        else:
            guios_MAIN["MAININDICATOR_WMA"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MAIN["MAININDICATOR_WMA"].deactivate()
            guios_MAIN["MAININDICATORSETUP_WMA"].deactivate()
        #EMA
        if cac['EMA_Master']:
            guios_MAIN["MAININDICATOR_EMA"].activate()
            guios_MAIN["MAININDICATORSETUP_EMA"].activate()
            for lineIndex in range (_NMAXLINES['EMA']):
                if cac[f'EMA_{lineIndex}_LineActive']:
                    nSamples = cac[f'EMA_{lineIndex}_NSamples']
                    width    = oc[f'EMA_{lineIndex}_Width']
                    display  = oc[f'EMA_{lineIndex}_Display']
                    guios_EMA[f"INDICATOR_EMA{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
                    guios_EMA[f"INDICATOR_EMA{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
                    guios_EMA[f"INDICATOR_EMA{lineIndex}_WIDTHINPUT"].activate()
                    guios_EMA[f"INDICATOR_EMA{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
                    guios_EMA[f"INDICATOR_EMA{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                    guios_EMA[f"INDICATOR_EMA{lineIndex}_DISPLAY"].activate()
                else:
                    guios_EMA[f"INDICATOR_EMA{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_EMA[f"INDICATOR_EMA{lineIndex}_INTERVALINPUT"].updateText("-")
                    guios_EMA[f"INDICATOR_EMA{lineIndex}_WIDTHINPUT"].deactivate()
                    guios_EMA[f"INDICATOR_EMA{lineIndex}_DISPLAY"].deactivate()
                    guios_EMA[f"INDICATOR_EMA{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
        else:
            guios_MAIN["MAININDICATOR_EMA"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MAIN["MAININDICATOR_EMA"].deactivate()
            guios_MAIN["MAININDICATORSETUP_EMA"].deactivate()
        #PSAR
        if cac['PSAR_Master']:
            guios_MAIN["MAININDICATOR_PSAR"].activate()
            guios_MAIN["MAININDICATORSETUP_PSAR"].activate()
            for lineIndex in range (_NMAXLINES['PSAR']):
                if cac[f'PSAR_{lineIndex}_LineActive']:
                    af0     = cac[f'PSAR_{lineIndex}_AF0']
                    afPlus  = cac[f'PSAR_{lineIndex}_AF+']
                    afMax   = cac[f'PSAR_{lineIndex}_AFMax']
                    width   = oc[f'PSAR_{lineIndex}_Width']
                    display = oc[f'PSAR_{lineIndex}_Display']
                    guios_PSAR[f"INDICATOR_PSAR{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
                    guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AF0INPUT"].updateText(f"{af0:.3f}")
                    guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AF+INPUT"].updateText(f"{afPlus:.3f}")
                    guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AFMAXINPUT"].updateText(f"{afMax:.3f}")
                    guios_PSAR[f"INDICATOR_PSAR{lineIndex}_WIDTHINPUT"].activate()
                    guios_PSAR[f"INDICATOR_PSAR{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                    guios_PSAR[f"INDICATOR_PSAR{lineIndex}_DISPLAY"].activate()
                else:
                    guios_PSAR[f"INDICATOR_PSAR{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AF0INPUT"].updateText("-")
                    guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AF+INPUT"].updateText("-")
                    guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AFMAXINPUT"].updateText("-")
                    guios_PSAR[f"INDICATOR_PSAR{lineIndex}_WIDTHINPUT"].deactivate()
                    guios_PSAR[f"INDICATOR_PSAR{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_PSAR[f"INDICATOR_PSAR{lineIndex}_DISPLAY"].deactivate()
        else:
            guios_MAIN["MAININDICATOR_PSAR"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MAIN["MAININDICATOR_PSAR"].deactivate()
            guios_MAIN["MAININDICATORSETUP_PSAR"].deactivate()
        #BOL
        if cac['BOL_Master']:
            guios_MAIN["MAININDICATOR_BOL"].activate()
            guios_MAIN["MAININDICATORSETUP_BOL"].activate()
            for lineIndex in range (_NMAXLINES['BOL']):
                if cac[f'BOL_{lineIndex}_LineActive']:
                    nSamples  = cac[f'BOL_{lineIndex}_NSamples']
                    bandWidth = cac[f'BOL_{lineIndex}_BandWidth']
                    width     = oc[f'BOL_{lineIndex}_Width']
                    display   = oc[f'BOL_{lineIndex}_Display']
                    guios_BOL[f"INDICATOR_BOL{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
                    guios_BOL[f"INDICATOR_BOL{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
                    guios_BOL[f"INDICATOR_BOL{lineIndex}_BANDWIDTHINPUT"].updateText(f"{bandWidth:.1f}")
                    guios_BOL[f"INDICATOR_BOL{lineIndex}_WIDTHINPUT"].activate()
                    guios_BOL[f"INDICATOR_BOL{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
                    guios_BOL[f"INDICATOR_BOL{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                    guios_BOL[f"INDICATOR_BOL{lineIndex}_DISPLAY"].activate()
                else:
                    guios_BOL[f"INDICATOR_BOL{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_BOL[f"INDICATOR_BOL{lineIndex}_INTERVALINPUT"].updateText("-")
                    guios_BOL[f"INDICATOR_BOL{lineIndex}_BANDWIDTHINPUT"].updateText("-")
                    guios_BOL[f"INDICATOR_BOL{lineIndex}_WIDTHINPUT"].deactivate()
                    guios_BOL[f"INDICATOR_BOL{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_BOL[f"INDICATOR_BOL{lineIndex}_DISPLAY"].deactivate()
            guios_BOL["INDICATOR_MATYPESELECTION"].setSelected(itemKey = cac['BOL_MAType'], callSelectionUpdateFunction = False)
        else:
            guios_MAIN["MAININDICATOR_BOL"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MAIN["MAININDICATOR_BOL"].deactivate()
            guios_MAIN["MAININDICATORSETUP_BOL"].deactivate()
        #IVP
        if cac['IVP_Master']:
            guios_MAIN["MAININDICATOR_IVP"].activate()
            guios_MAIN["MAININDICATORSETUP_IVP"].activate()
            guios_IVP["INDICATOR_INTERVAL_INPUTTEXT"].updateText(text = f"{cac['IVP_NSamples']}")
            guios_IVP["INDICATOR_GAMMAFACTOR_SLIDER"].setSliderValue(newValue = (cac['IVP_GammaFactor']-0.005)*(100/0.095), callValueUpdateFunction = False)
            guios_IVP["INDICATOR_GAMMAFACTOR_VALUETEXT"].updateText(f"{cac['IVP_GammaFactor']*100:.1f} %")
            guios_IVP["INDICATOR_DELTAFACTOR_SLIDER"].setSliderValue(newValue = (cac['IVP_DeltaFactor']-0.1)*(100/9.9), callValueUpdateFunction = False)
            guios_IVP["INDICATOR_DELTAFACTOR_VALUETEXT"].updateText(f"{int(cac['IVP_DeltaFactor']*100):d} %")
        else:
            guios_MAIN["MAININDICATOR_IVP"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MAIN["MAININDICATOR_IVP"].deactivate()
            guios_MAIN["MAININDICATORSETUP_IVP"].deactivate()
        #SWING
        if cac['SWING_Master']:
            guios_MAIN["MAININDICATOR_SWING"].activate()
            guios_MAIN["MAININDICATORSETUP_SWING"].activate()
            for lineIndex in range (_NMAXLINES['SWING']):
                if cac[f'SWING_{lineIndex}_LineActive']:
                    swingRange = cac[f'SWING_{lineIndex}_SwingRange']
                    width      = oc[f'SWING_{lineIndex}_Width']
                    display    = oc[f'SWING_{lineIndex}_Display']
                    guios_SWING[f"INDICATOR_SWING{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
                    guios_SWING[f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT"].updateText(f"{swingRange:.4f}")
                    guios_SWING[f"INDICATOR_SWING{lineIndex}_WIDTHINPUT"].activate()
                    guios_SWING[f"INDICATOR_SWING{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                    guios_SWING[f"INDICATOR_SWING{lineIndex}_DISPLAY"].activate()
                else:
                    guios_SWING[f"INDICATOR_SWING{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_SWING[f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT"].updateText("-")
                    guios_SWING[f"INDICATOR_SWING{lineIndex}_WIDTHINPUT"].deactivate()
                    guios_PSAR[f"INDICATOR_SWING{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_SWING[f"INDICATOR_SWING{lineIndex}_DISPLAY"].deactivate()
        else:
            guios_MAIN["MAININDICATOR_SWING"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MAIN["MAININDICATOR_SWING"].deactivate()
            guios_MAIN["MAININDICATORSETUP_PSAR"].deactivate()
        #VOL
        if cac['VOL_Master']:
            guios_MAIN["SUBINDICATOR_VOL"].activate()
            guios_MAIN["SUBINDICATORSETUP_VOL"].activate()
            for lineIndex in range (_NMAXLINES['VOL']):
                if cac[f'VOL_{lineIndex}_LineActive']:
                    nSamples = cac[f'VOL_{lineIndex}_NSamples']
                    width    = oc[f'VOL_{lineIndex}_Width']
                    display  = oc[f'VOL_{lineIndex}_Display']
                    guios_VOL[f"INDICATOR_VOL{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
                    guios_VOL[f"INDICATOR_VOL{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
                    guios_VOL[f"INDICATOR_VOL{lineIndex}_WIDTHINPUT"].activate()
                    guios_VOL[f"INDICATOR_VOL{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
                    guios_VOL[f"INDICATOR_VOL{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                    guios_VOL[f"INDICATOR_VOL{lineIndex}_DISPLAY"].activate()
                else:
                    guios_VOL[f"INDICATOR_VOL{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_VOL[f"INDICATOR_VOL{lineIndex}_INTERVALINPUT"].updateText("-")
                    guios_VOL[f"INDICATOR_VOL{lineIndex}_WIDTHINPUT"].deactivate()
                    guios_VOL[f"INDICATOR_VOL{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_VOL[f"INDICATOR_VOL{lineIndex}_DISPLAY"].deactivate()
            guios_VOL["INDICATOR_VOLTYPESELECTION"].setSelected(itemKey = cac['VOL_VolumeType'], callSelectionUpdateFunction = False)
            guios_VOL["INDICATOR_MATYPESELECTION"].setSelected(itemKey  = cac['VOL_MAType'],     callSelectionUpdateFunction = False)
        else:
            guios_MAIN["SUBINDICATOR_VOL"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MAIN["SUBINDICATOR_VOL"].deactivate()
            guios_MAIN["SUBINDICATORSETUP_VOL"].deactivate()
        #NNA
        if cac['NNA_Master']:
            guios_MAIN["SUBINDICATOR_NNA"].activate()
            guios_MAIN["SUBINDICATORSETUP_NNA"].activate()
            for lineIndex in range (_NMAXLINES['NNA']):
                if cac[f'NNA_{lineIndex}_LineActive']:
                    nnCode   = cac[f'NNA_{lineIndex}_NeuralNetworkCode']
                    nnCode_str = "" if nnCode is None else f"{nnCode}"
                    alpha    = cac[f'NNA_{lineIndex}_Alpha']
                    beta     = cac[f'NNA_{lineIndex}_Beta']
                    width    = oc[f'NNA_{lineIndex}_Width']
                    display  = oc[f'NNA_{lineIndex}_Display']
                    guios_NNA[f"INDICATOR_NNA{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
                    guios_NNA[f"INDICATOR_NNA{lineIndex}_NNCODEINPUT"].updateText(nnCode_str)
                    guios_NNA[f"INDICATOR_NNA{lineIndex}_ALPHAINPUT"].updateText(f"{alpha:.2f}")
                    guios_NNA[f"INDICATOR_NNA{lineIndex}_BETAINPUT"].updateText(f"{beta}")
                    guios_NNA[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].activate()
                    guios_NNA[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
                    guios_NNA[f"INDICATOR_NNA{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                    guios_NNA[f"INDICATOR_NNA{lineIndex}_DISPLAY"].activate()
                else:
                    guios_NNA[f"INDICATOR_NNA{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_NNA[f"INDICATOR_NNA{lineIndex}_NNCODEINPUT"].updateText("-")
                    guios_NNA[f"INDICATOR_NNA{lineIndex}_ALPHAINPUT"].updateText("-")
                    guios_NNA[f"INDICATOR_NNA{lineIndex}_BETAINPUT"].updateText("-")
                    guios_NNA[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].deactivate()
                    guios_NNA[f"INDICATOR_NNA{lineIndex}_DISPLAY"].deactivate()
                    guios_NNA[f"INDICATOR_NNA{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
        else:
            guios_MAIN["SUBINDICATOR_NNA"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MAIN["SUBINDICATOR_NNA"].deactivate()
            guios_MAIN["SUBINDICATORSETUP_NNA"].deactivate()
        #MMACDSHORT
        if cac['MMACDSHORT_Master']:
            guios_MAIN["SUBINDICATOR_MMACDSHORT"].activate()
            guios_MAIN["SUBINDICATORSETUP_MMACDSHORT"].activate()
            for lineIndex in range (_NMAXLINES['MMACDSHORT']):
                if cac[f'MMACDSHORT_MA{lineIndex}_LineActive']:
                    nSamples = cac[f'MMACDSHORT_MA{lineIndex}_NSamples']
                    guios_MMACDSHORT[f"INDICATOR_MMACDMA{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
                    guios_MMACDSHORT[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
                else:
                    guios_MMACDSHORT[f"INDICATOR_MMACDMA{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_MMACDSHORT[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].updateText("-")
            signalNSamples = cac['MMACDSHORT_SignalNSamples']
            multiplier     = cac['MMACDSHORT_Multiplier']
            guios_MMACDSHORT["INDICATOR_SIGNALINTERVALTEXTINPUT"].updateText(f"{signalNSamples}")
            guios_MMACDSHORT["INDICATOR_MULTIPLIERTEXTINPUT"].updateText(f"{multiplier}")
        else:
            guios_MAIN["SUBINDICATOR_MMACDSHORT"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MAIN["SUBINDICATOR_MMACDSHORT"].deactivate()
            guios_MAIN["SUBINDICATORSETUP_MMACDSHORT"].deactivate()
        #MMACDLONG
        if cac['MMACDLONG_Master']:
            guios_MAIN["SUBINDICATOR_MMACDLONG"].activate()
            guios_MAIN["SUBINDICATORSETUP_MMACDLONG"].activate()
            for lineIndex in range (_NMAXLINES['MMACDLONG']):
                if cac[f'MMACDLONG_MA{lineIndex}_LineActive']:
                    nSamples = cac[f'MMACDLONG_MA{lineIndex}_NSamples']
                    guios_MMACDLONG[f"INDICATOR_MMACDMA{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
                    guios_MMACDLONG[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
                else:
                    guios_MMACDLONG[f"INDICATOR_MMACDMA{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_MMACDLONG[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].updateText("-")
            signalNSamples = cac['MMACDLONG_SignalNSamples']
            multiplier     = cac['MMACDLONG_Multiplier']
            guios_MMACDLONG["INDICATOR_SIGNALINTERVALTEXTINPUT"].updateText(f"{signalNSamples}")
            guios_MMACDLONG["INDICATOR_MULTIPLIERTEXTINPUT"].updateText(f"{multiplier}")
        else:
            guios_MAIN["SUBINDICATOR_MMACDLONG"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MAIN["SUBINDICATOR_MMACDLONG"].deactivate()
            guios_MAIN["SUBINDICATORSETUP_MMACDLONG"].deactivate()
        #DMIxADX
        if cac['DMIxADX_Master']:
            guios_MAIN["SUBINDICATOR_DMIxADX"].activate()
            guios_MAIN["SUBINDICATORSETUP_DMIxADX"].activate()
            for lineIndex in range (_NMAXLINES['DMIxADX']):
                if cac[f'DMIxADX_{lineIndex}_LineActive']:
                    nSamples = cac[f'DMIxADX_{lineIndex}_NSamples']
                    width    = oc[f'DMIxADX_{lineIndex}_Width']
                    display  = oc[f'DMIxADX_{lineIndex}_Display']
                    guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
                    guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
                    guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT"].activate()
                    guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
                    guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                    guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_DISPLAY"].activate()
                else:
                    guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT"].updateText("-")
                    guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT"].deactivate()
                    guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_DISPLAY"].deactivate()
                    guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
        else:
            guios_MAIN["SUBINDICATOR_DMIxADX"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MAIN["SUBINDICATOR_DMIxADX"].deactivate()
            guios_MAIN["SUBINDICATORSETUP_DMIxADX"].deactivate()
        #MFI
        if cac['MFI_Master']:
            guios_MAIN["SUBINDICATOR_MFI"].activate()
            guios_MAIN["SUBINDICATORSETUP_MFI"].activate()
            for lineIndex in range (_NMAXLINES['MFI']):
                if cac[f'MFI_{lineIndex}_LineActive']:
                    nSamples = cac[f'MFI_{lineIndex}_NSamples']
                    width    = oc[f'MFI_{lineIndex}_Width']
                    display  = oc[f'MFI_{lineIndex}_Display']
                    guios_MFI[f"INDICATOR_MFI{lineIndex}"].setStatus(status = True)
                    guios_MFI[f"INDICATOR_MFI{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
                    guios_MFI[f"INDICATOR_MFI{lineIndex}_WIDTHINPUT"].activate()
                    guios_MFI[f"INDICATOR_MFI{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
                    guios_MFI[f"INDICATOR_MFI{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                    guios_MFI[f"INDICATOR_MFI{lineIndex}_DISPLAY"].activate()
                else:
                    guios_MFI[f"INDICATOR_MFI{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_MFI[f"INDICATOR_MFI{lineIndex}_INTERVALINPUT"].updateText("-")
                    guios_MFI[f"INDICATOR_MFI{lineIndex}_WIDTHINPUT"].deactivate()
                    guios_MFI[f"INDICATOR_MFI{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_MFI[f"INDICATOR_MFI{lineIndex}_DISPLAY"].deactivate()
        else:
            guios_MAIN["SUBINDICATOR_MFI"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MAIN["SUBINDICATOR_MFI"].deactivate()
            guios_MAIN["SUBINDICATORSETUP_MFI"].deactivate()
        #WOI
        for lineIndex in range (_NMAXLINES['WOI']):
            if cac[f'WOI_{lineIndex}_LineActive']:
                nSamples = cac[f'WOI_{lineIndex}_NSamples']
                sigma    = cac[f'WOI_{lineIndex}_Sigma']
                width    = oc[f'WOI_{lineIndex}_Width']
                display  = oc[f'WOI_{lineIndex}_Display']
                guios_WOI[f"INDICATOR_WOI{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
                guios_WOI[f"INDICATOR_WOI{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
                guios_WOI[f"INDICATOR_WOI{lineIndex}_SIGMAINPUT"].updateText(f"{sigma:.1f}")
                guios_WOI[f"INDICATOR_WOI{lineIndex}_WIDTHINPUT"].activate()
                guios_WOI[f"INDICATOR_WOI{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
                guios_WOI[f"INDICATOR_WOI{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                guios_WOI[f"INDICATOR_WOI{lineIndex}_DISPLAY"].activate()
            else:
                guios_WOI[f"INDICATOR_WOI{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_WOI[f"INDICATOR_WOI{lineIndex}_INTERVALINPUT"].updateText("-")
                guios_WOI[f"INDICATOR_WOI{lineIndex}_INTERVALINPUT"].deactivate()
                guios_WOI[f"INDICATOR_WOI{lineIndex}_SIGMAINPUT"].updateText("-")
                guios_WOI[f"INDICATOR_WOI{lineIndex}_SIGMAINPUT"].deactivate()
                guios_WOI[f"INDICATOR_WOI{lineIndex}_WIDTHINPUT"].deactivate()
                guios_WOI[f"INDICATOR_WOI{lineIndex}_WIDTHINPUT"].updateText("-")
                guios_WOI[f"INDICATOR_WOI{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_WOI[f"INDICATOR_WOI{lineIndex}_DISPLAY"].deactivate()
        #NES
        for lineIndex in range (_NMAXLINES['NES']):
            if cac[f'NES_{lineIndex}_LineActive']:
                nSamples = cac[f'NES_{lineIndex}_NSamples']
                sigma    = cac[f'NES_{lineIndex}_Sigma']
                width    = oc[f'NES_{lineIndex}_Width']
                display  = oc[f'NES_{lineIndex}_Display']
                guios_NES[f"INDICATOR_NES{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
                guios_NES[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
                guios_NES[f"INDICATOR_NES{lineIndex}_SIGMAINPUT"].updateText(f"{sigma:.1f}")
                guios_NES[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].activate()
                guios_NES[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
                guios_NES[f"INDICATOR_NES{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                guios_NES[f"INDICATOR_NES{lineIndex}_DISPLAY"].activate()
            else:
                guios_NES[f"INDICATOR_NES{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_NES[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].updateText("-")
                guios_NES[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].deactivate()
                guios_NES[f"INDICATOR_NES{lineIndex}_SIGMAINPUT"].updateText("-")
                guios_NES[f"INDICATOR_NES{lineIndex}_SIGMAINPUT"].deactivate()
                guios_NES[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].deactivate()
                guios_NES[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].updateText("-")
                guios_NES[f"INDICATOR_NES{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_NES[f"INDICATOR_NES{lineIndex}_DISPLAY"].deactivate()
        #SI Viewers
        for siViewerIndex in range (len(_SITYPES)):
            if siViewerIndex < self.usableSIViewers:
                guios_MAIN[f"SUBINDICATOR_DISPLAYSWITCH{siViewerIndex}"].activate()
                guios_MAIN[f"SUBINDICATOR_DISPLAYSELECTION{siViewerIndex}"].activate()
            else:
                guios_MAIN[f"SUBINDICATOR_DISPLAYSWITCH{siViewerIndex}"].deactivate()
                guios_MAIN[f"SUBINDICATOR_DISPLAYSELECTION{siViewerIndex}"].deactivate()
        self.objectConfig['VOL_VolumeType'] = cac['VOL_VolumeType']
        self.objectConfig['VOL_MAType']     = cac['VOL_MAType']
        #WOI Prep
        self.siTypes_analysisCodes['WOI'] = list()
        for lineIndex in range (_NMAXLINES['WOI']):
            woiType = f"WOI_{lineIndex}"
            if cac[f'WOI_{lineIndex}_LineActive']:
                self.siTypes_analysisCodes['WOI'].append(woiType)
                self.bidsAndAsks[woiType] = dict()
            elif woiType in self.bidsAndAsks: del self.bidsAndAsks[woiType]
        #NES Prep
        self.siTypes_analysisCodes['NES'] = list()
        for lineIndex in range (_NMAXLINES['NES']):
            nesType = f"NES_{lineIndex}"
            if cac[f'NES_{lineIndex}_LineActive']:
                self.siTypes_analysisCodes['NES'].append(nesType)
                self.aggTrades[nesType] = dict()
            elif nesType in self.aggTrades: del self.aggTrades[nesType]
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
        addToDrawQueue = (classification in (0b0010, 0b1010, 0b1011, 0b0011))
        #Generate analysis for the analysis target
        for analysisType, analysisCode in self.analysisToProcess_Sorted:
            if self.chartDrawerType == 'TLVIEWER': 
                baa = None
                agt = None
            elif self.chartDrawerType == 'ANALYZER': 
                baa = self.bidsAndAsks
                agt = self.aggTrades
            atmEta_Analyzers.analysisGenerator(analysisType   = analysisType, 
                                               klineAccess    = self.klines, 
                                               intervalID     = self.intervalID, 
                                               mrktRegTS      = self.mrktRegTS, 
                                               precisions     = self.currencyInfo['precisions'], 
                                               timestamp      = analysisTargetTS,
                                               neuralNetworks = self.neuralNetworkInstances,
                                               bidsAndAsks    = baa,
                                               aggTrades      = agt,
                                               **self.analysisParams[analysisCode])
            if addToDrawQueue:
                kDrawQueue = self.klines_drawQueue
                if analysisTargetTS in kDrawQueue: kDrawQueue[analysisTargetTS][analysisCode] = None
                else:                              kDrawQueue[analysisTargetTS]={analysisCode: None}
    #Kline Data END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def getGroupRequirement(): return 30
#'chartDrawer' END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------