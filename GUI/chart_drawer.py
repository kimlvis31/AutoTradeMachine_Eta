#ATM Modules
from GUI import advanced_pyglet_groups, generals, hit_boxes, text_control
import auxiliaries
import analyzers
import ipc
import neural_networks
import constants

#Python Modules
import time
import math
import random
import termcolor
import pyglet
import bisect
import itertools
from datetime import datetime, timezone, tzinfo

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

KLINTERVAL   = constants.KLINTERVAL
KLINTERVAL_S = constants.KLINTERVAL_S

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

_MITYPES = analyzers.ANALYSIS_MITYPES
_SITYPES = analyzers.ANALYSIS_SITYPES
_NMAXLINES = {'SMA':     constants.NLINES_SMA,
              'WMA':     constants.NLINES_WMA,
              'EMA':     constants.NLINES_EMA,
              'PSAR':    constants.NLINES_PSAR,
              'BOL':     constants.NLINES_BOL,
              'IVP':     None,
              'SWING':   constants.NLINES_SWING,
              'VOL':     constants.NLINES_VOL,
              'NNA':     constants.NLINES_NNA,
              'MMACD':   constants.NLINES_MMACD,
              'DMIxADX': constants.NLINES_DMIxADX,
              'MFI':     constants.NLINES_MFI,
              'TPD':     constants.NLINES_TPD}

_FULLDRAWSIGNALS = {'KLINE':        0b1,
                    'DEPTHOVERLAY': 0b11,
                    'SMA':          0b1,
                    'WMA':          0b1,
                    'EMA':          0b1,
                    'PSAR':         0b1,
                    'BOL':          0b11,
                    'IVP':          0b11,
                    'SWING':        0b1,
                    'VOL':          0b1,
                    'DEPTH':        0b11,
                    'AGGTRADE':     0b11,
                    'NNA':          0b1,
                    'MMACD':        0b111,
                    'DMIxADX':      0b1,
                    'MFI':          0b1,
                    'TPD':          0b1,
                    'TRADELOG':     0b1}

_DEPTHBINS = {DEPTHINDEX_BIDS5: (-5.0, -4.0),
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
_DEPTHBINS_MIN = min(db[0] for db in _DEPTHBINS.values())
_DEPTHBINS_MAX = max(db[1] for db in _DEPTHBINS.values())

_GD_DISPLAYBOX_GOFFSET                 = 50
_GD_DISPLAYBOX_LEFTSECTION_MINWIDTH    = 4600
_GD_DISPLAYBOX_RIGHTSECTION_WIDTH      = 1000
_GD_DISPLAYBOX_AUXILLARYBAR_HEIGHT     = 300
_GD_DISPLAYBOX_SIVIEWER_HEIGHT         = 1200
_GD_DISPLAYBOX_KLINESPRICE_MINHEIGHT   = 2000
_GD_DISPLAYBOX_MAINGRIDTEMPORAL_HEIGHT = 350

_GD_OBJECT_MINWIDTH  = _GD_DISPLAYBOX_LEFTSECTION_MINWIDTH  + _GD_DISPLAYBOX_RIGHTSECTION_WIDTH      + _GD_DISPLAYBOX_GOFFSET #4600 +1000 + 50 = 5650
_GD_OBJECT_MINHEIGHT = _GD_DISPLAYBOX_KLINESPRICE_MINHEIGHT + _GD_DISPLAYBOX_MAINGRIDTEMPORAL_HEIGHT + _GD_DISPLAYBOX_GOFFSET #2000 + 550 + 50 = 2600

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

_GD_KLINESLOADINGGAUGEBAR_HEIGHT = 150

_TIMEINTERVAL_MOUSEINTERPRETATION_NS = 10e6
_TIMEINTERVAL_POSTDRAGWAITTIME       = 200e6
_TIMEINTERVAL_POSTSCROLLWAITTIME     = 200e6
_TIMEINTERVAL_POSHIGHLIGHTUPDATE     = 10e6
_TIMELIMIT_KLINESDRAWQUEUE_NS        = 10e6
_TIMELIMIT_RCLCGPROCESSING_NS        = 10e6
_TIMELIMIT_KLINESDRAWREMOVAL_NS      = 10e6

_VVR_PRECISIONUPDATETHRESHOLD = 2
_VVR_PRECISIONCOMPENSATOR = {'KLINESPRICE': -2,
                             'VOL':         -2,
                             'DEPTH':       -2,
                             'AGGTRADE':    -2,
                             'NNA':         -2,
                             'MMACD':       -2,
                             'DMIxADX':     -2,
                             'MFI':         -2,
                             'TPD':         -2
                            }
_VVR_HGLCENTERS = {'KLINESPRICE': 0,
                   'VOL':         0,
                   'DEPTH':       0,
                   'AGGTRADE':    0,
                   'NNA':         0,
                   'MMACD':       0,
                   'DMIxADX':     0,
                   'MFI':         0.5,
                   'TPD':         0
                  }

_DRAWTARGETRAWNAMEEXCEPTION = set(['kline', 'depth', 'aggTrade'])

#'chartDrawer' --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class chartDrawer:
    #Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, **kwargs):
        #[1]: Base Graphics Parameters
        self.window = kwargs['windowInstance']
        self.scaler = kwargs['scaler']
        self.batch  = kwargs['batch']
        
        #[2]: Group Order
        groupOrder = kwargs.get('groupOrder', None)
        if groupOrder is None:
            #[2-1]: Object Base
            self.group_0  = kwargs['group_0']
            self.group_1  = kwargs['group_1']
            self.group_46 = kwargs['group_46']
            self.group_47 = kwargs['group_47']
            self.group_48 = kwargs['group_48']
            self.group_49 = kwargs['group_49']
            self.group_50 = kwargs['group_50']
            #[2-2]: Hovered Descriptor
            self.group_hd0 = kwargs['group_27']
            #[2-4]: For AuxBar
            self.group_ab0 = kwargs['group_28']
            self.group_ab1 = kwargs['group_29']
            self.group_ab2 = kwargs['group_30']
            self.group_ab3 = kwargs['group_31']
            #[2-3]: For Settings Subpage
            self.group_ss0 = kwargs['group_32']
            self.group_ss1 = kwargs['group_33']
            self.group_ss2 = kwargs['group_34']
            self.group_ss3 = kwargs['group_35']
            self.groupOrder = self.group_0.order
            #[2-5]: Parent Cam Group
            self.parentCameraGroup = self.group_0
        else:
            self.groupOrder = groupOrder
            #[2-1]: Object Base
            self.group_0  = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1  = pyglet.graphics.Group(order = self.groupOrder+1)
            self.group_46 = pyglet.graphics.Group(order = self.groupOrder+46)
            self.group_47 = pyglet.graphics.Group(order = self.groupOrder+47)
            self.group_48 = pyglet.graphics.Group(order = self.groupOrder+48)
            self.group_49 = pyglet.graphics.Group(order = self.groupOrder+49)
            self.group_50 = pyglet.graphics.Group(order = self.groupOrder+50)
            #[2-2]: Hovered Descriptor
            self.group_hd0 = pyglet.graphics.Group(order = self.groupOrder+27)
            #[2-4]: For AuxBar
            self.group_ab_order = self.groupOrder+28
            #[2-3]: For Settings Subpage
            self.group_ss_order = self.groupOrder+32
            #[2-5]: Parent Cam Group
            self.parentCameraGroup = None

        #[3]: External Connections
        self.imageManager    = kwargs['imageManager']
        self.audioManager    = kwargs['audioManager']
        self.visualManager   = kwargs['visualManager']
        self.currentGUITheme = self.visualManager.getGUITheme()
        self.ipcA = kwargs['ipcA']
        
        #[4]: Object Basic Configurations
        self.name               = kwargs.get('name', None)
        self.xPos               = kwargs.get('xPos', 0)
        self.yPos               = kwargs.get('yPos', 0)
        self.width              = max(kwargs.get('width',  0), _GD_OBJECT_MINWIDTH)
        self.height             = max(kwargs.get('height', 0), _GD_OBJECT_MINHEIGHT)
        self.style              = kwargs.get('style', 'styleA')
        self.textStyle          = kwargs.get('textStyle', 'default')
        self.effectiveTextStyle = self.visualManager.getTextStyle('chartDrawer_'+self.textStyle)
        for textStyleCode in self.effectiveTextStyle: self.effectiveTextStyle[textStyleCode]['font_size'] = 80*self.scaler

        #[5]: DisplayBox Dimension Standards & Interaction Control Variables
        self.hitBox        = dict()
        self.hitBox_Object = hit_boxes.hitBox_Rectangular(self.xPos, self.yPos, self.width, self.height)
        self.images        = dict()
        self.frameSprites  = dict()
        #---[5-1]: Displayers (Priority Goes: KLINESVOLUME -> AUXILLARYBAR -> SIVIEWERS)
        self.usableSIViewers = min([int((self.height-_GD_OBJECT_MINHEIGHT-(_GD_DISPLAYBOX_AUXILLARYBAR_HEIGHT+_GD_DISPLAYBOX_GOFFSET))/(_GD_DISPLAYBOX_SIVIEWER_HEIGHT+_GD_DISPLAYBOX_GOFFSET)), len(_SITYPES)])
        self.displayBox = {'AUXILLARYBAR':         None,
                           'KLINESPRICE':          None, 
                           'MAINGRID_KLINESPRICE': None,
                           'MAINGRID_TEMPORAL':    None, 
                           'SETTINGSBUTTONFRAME':  None}
        for sivIdx in range (len(_SITYPES)):
            self.displayBox[f'SIVIEWER{sivIdx}']          = None
            self.displayBox[f'MAINGRID_SIVIEWER{sivIdx}'] = None
        self.displayBox_graphics                  = {dBoxName: dict() for dBoxName in self.displayBox}
        self.displayBox_graphics_visibleSIViewers = set()
        self.displayBox_VerticalSection_Order     = list()
        self.displayBox_VisibleBoxes              = list()
        self.__RCLCGReferences = list()

        #[6]: Mouse Control Variables
        self.mouse_lastHoveredSection       = None
        self.mouse_lastSelectedSection      = None
        self.mouse_Dragged                  = False
        self.mouse_DragDX                   = dict()
        self.mouse_DragDY                   = dict()
        self.mouse_lastDragged_ns           = 0
        self.mouse_Scrolled                 = False
        self.mouse_ScrollDX                 = dict()
        self.mouse_ScrollDY                 = dict()
        self.mouse_lastScrolled_ns          = 0
        self.mouse_Event_lastRead           = None
        self.mouse_Event_lastPressed        = None
        self.mouse_Event_lastInterpreted_ns = 0

        #[7]: Internal Objects
        #---[7-1]: GUIOs Initialization Base Parameters
        baseKwargs = {'windowInstance': self.window,
                      'batch':          self.batch,
                      'scaler':         self.scaler,
                      'imageManager':   self.imageManager,
                      'audioManager':   self.audioManager,
                      'visualManager':  self.visualManager}
        #---[7-1]: Kline Loading Display Elements
        self.__loading = False
        self.images['KLINELOADINGCOVER'] = self.imageManager.getImageByCode(imageCode    = f"chartDrawer_typeA_{self.style}_klinesLoadingCover", 
                                                                            scaledWidth  = self.width *self.scaler, 
                                                                            scaledHeight = self.height*self.scaler)
        self.frameSprites['KLINELOADINGCOVER'] = pyglet.sprite.Sprite(x     = self.xPos*self.scaler, 
                                                                      y     = self.yPos*self.scaler, 
                                                                      img   = self.images['KLINELOADINGCOVER'][0], 
                                                                      batch = self.batch, 
                                                                      group = self.group_46)
        self.frameSprites['KLINELOADINGCOVER'].visible = False
        self.loadingGaugeBar = generals.gaugeBar_typeA(**baseKwargs,
                                                                  xPos    = self.xPos, 
                                                                  yPos    = self.yPos, 
                                                                  width   = 100, 
                                                                  height  = _GD_KLINESLOADINGGAUGEBAR_HEIGHT,
                                                                  style   = 'styleA', 
                                                                  align   = 'horizontal', 
                                                                  group_0 = self.group_47,
                                                                  group_1 = self.group_48,
                                                                  value   = 0)
        self.loadingTextBox_perc = generals.textBox_typeA(**baseKwargs,
                                                                     xPos     = self.xPos, 
                                                                     yPos     = self.yPos, 
                                                                     width    = 100, 
                                                                     height   = _GD_KLINESLOADINGGAUGEBAR_HEIGHT,
                                                                     style    = None, 
                                                                     group_0  = self.group_49, 
                                                                     group_1  = self.group_50, 
                                                                     text     = '', 
                                                                     fontSize = 60)
        self.loadingTextBox = generals.textBox_typeA(**baseKwargs,
                                                                xPos     = self.xPos, 
                                                                yPos     = self.yPos,
                                                                width    = 100, 
                                                                height   = 200,
                                                                style    = None, 
                                                                group_0  = self.group_47, 
                                                                group_1  = self.group_48, 
                                                                text     = "", 
                                                                fontSize = 80)
        self.loadingGaugeBar.hide()
        self.loadingTextBox_perc.hide()
        self.loadingTextBox.hide()
        
        #---[7-2]: Settings Sub Page Setup
        self.settingsSubPages        = dict()
        self.settingsSubPage_Current = 'MAIN'
        self.settingsSubPage_Opened  = False
        self.settingsButtonStatus    = 'DEFAULT'
        if groupOrder is None:
            groupKwargs = {'group_0': self.group_ss0,
                           'group_1': self.group_ss1,
                           'group_2': self.group_ss2,
                           'group_3': self.group_ss3}
        else:
            groupKwargs = {'groupOrder': self.group_ss_order}
        ssp_effHeight = min(self.height-100, _GD_SETTINGSSUBPAGE_MAXHEIGHT)
        for subPageName in ('MAIN',)+_MITYPES+_SITYPES:
            ssp = generals.subPageBox_typeA(**baseKwargs,
                                                       guioConfig     = kwargs['guioConfig'], 
                                                       sysFunctions   = kwargs['sysFunctions'], 
                                                       ipcA           = self.ipcA,
                                                       xPos           = self.xPos+50, 
                                                       yPos           = self.yPos+self.height-50-ssp_effHeight, 
                                                       width          = _GD_SETTINGSSUBPAGE_WIDTH, 
                                                       height         = ssp_effHeight, 
                                                       useScrollBar_V = True, 
                                                       useScrollBar_H = False,
                                                       **groupKwargs)
            ssp.hide()
            self.settingsSubPages[subPageName] = ssp

        #---[7-3]: AuxBar SubPage Setup
        if groupOrder is None:
            groupKwargs = {'group_0': self.group_ab0,
                           'group_1': self.group_ab1,
                           'group_2': self.group_ab2,
                           'group_3': self.group_ab3}
        else:
            groupKwargs = {'groupOrder': self.group_ab_order}
        self.auxBarPage = generals.subPageBox_typeA(**baseKwargs,
                                                               guioConfig     = kwargs['guioConfig'], 
                                                               sysFunctions   = kwargs['sysFunctions'], 
                                                               ipcA           = self.ipcA,
                                                               xPos           = self.xPos, 
                                                               yPos           = self.yPos, 
                                                               width          = self.width, 
                                                               height         = _GD_DISPLAYBOX_AUXILLARYBAR_HEIGHT, 
                                                               style          = None,
                                                               useScrollBar_V = False, 
                                                               useScrollBar_H = False,
                                                               **groupKwargs)

        #[8]: View Control
        #---[8-1]: Descriptors
        self.__onPHUs = {'KLINE':    self.__onPHU_KLINE,
                         'TRADELOG': self.__onPHU_TRADELOG,
                         'IVP':      self.__onPHU_IVP,
                         'VOL':      self.__onPHU_VOL,
                         'DEPTH':    self.__onPHU_DEPTH,
                         'AGGTRADE': self.__onPHU_AGGTRADE,
                         'NNA':      self.__onPHU_NNA,
                         'MMACD':    self.__onPHU_MMACD,
                         'DMIxADX':  self.__onPHU_DMIxADX,
                         'MFI':      self.__onPHU_MFI,
                         'TPD':      self.__onPHU_TPD}

        #---[8-2]: Horizontal View Range
        self.expectedKlineTemporalWidth = 1500
        self.horizontalViewRangeWidth_min = None
        self.horizontalViewRangeWidth_max = None
        self.horizontalViewRangeWidth_m = None
        self.horizontalViewRangeWidth_b = None
        self.horizontalViewRange = [None, None]
        self.horizontalViewRange_timestampsInViewRange  = list()
        self.horizontalViewRange_timestampsInBufferZone = list()
        self.checkVerticalExtremas_SIs = {'VOL':      self.__checkVerticalExtremas_VOL,
                                          'DEPTH':    self.__checkVerticalExtremas_DEPTH,
                                          'AGGTRADE': self.__checkVerticalExtremas_AGGTRADE,
                                          'NNA':      self.__checkVerticalExtremas_NNA,
                                          'MMACD':    self.__checkVerticalExtremas_MMACD,
                                          'DMIxADX':  self.__checkVerticalExtremas_DMIxADX,
                                          'MFI':      self.__checkVerticalExtremas_MFI,
                                          'TPD':      self.__checkVerticalExtremas_TPD}

        #---[8-3]: Vertical View Range
        self.verticalViewRange_magnification = dict()
        self.verticalValue_min = dict()
        self.verticalValue_max = dict()
        self.verticalViewRange = dict()
        self.verticalViewRange_precision = dict()
        self.verticalViewRange_magnification['KLINESPRICE'] = 100
        self.verticalValue_min['KLINESPRICE'] = 0
        self.verticalValue_max['KLINESPRICE'] = 100000
        self.verticalViewRange['KLINESPRICE'] = [self.verticalValue_min['KLINESPRICE'], self.verticalValue_max['KLINESPRICE']]
        self.verticalViewRange_precision['KLINESPRICE'] = 0
        for siViewerIndex in range (len(_SITYPES)):
            siViewerCode = f'SIVIEWER{siViewerIndex}'
            self.verticalViewRange_magnification[siViewerCode] = 100
            self.verticalValue_min[siViewerCode] = -1
            self.verticalValue_max[siViewerCode] =  1
            self.verticalViewRange[siViewerCode] = [self.verticalValue_min[siViewerCode], self.verticalValue_max[siViewerCode]]
            self.verticalViewRange_precision[siViewerCode] = 0

        #---[8-4]: Highlight
        self.posHighlightColor_hovered  = self.visualManager.getFromColorTable('CHARTDRAWER_POSHOVERED')
        self.posHighlightColor_selected = self.visualManager.getFromColorTable('CHARTDRAWER_POSSELECTED')
        self.posHighlight_hoveredPos       = (None, None, None, None)
        self.posHighlight_updatedPositions = [False, False]
        self.posHighlight_selectedPos      = None
        self.posHighlight_lastUpdated_ns   = 0

        #---[8-5]: Grid
        #------[8-5-1]: Grid Base
        self.gridColor       = self.visualManager.getFromColorTable('CHARTDRAWER_GRID')
        self.gridColor_Heavy = self.visualManager.getFromColorTable('CHARTDRAWER_GRIDHEAVY')
        self.guideColor      = self.visualManager.getFromColorTable('CHARTDRAWER_GUIDECONTENT')
        #------[8-5-2]: Vertical Grid
        self.verticalGrid_intervalID = 0
        self.verticalGrid_intervals  = list()
        self.nMaxVerticalGridLines   = None
        #------[8-5-3]: Horizontal Grid Base
        self.horizontalGridIntervals      = dict()
        self.horizontalGridIntervalHeight = dict()
        self.nMaxHorizontalGridLines      = dict()
        self.horizontalGridIntervals['KLINESPRICE']      = list()
        self.horizontalGridIntervalHeight['KLINESPRICE'] = None
        self.nMaxHorizontalGridLines['KLINESPRICE']      = None
        for sivIdx in range (len(_SITYPES)):
            siViewerCode = f'SIVIEWER{sivIdx}'
            self.horizontalGridIntervals[siViewerCode]      = list()
            self.horizontalGridIntervalHeight[siViewerCode] = None
            self.nMaxHorizontalGridLines[siViewerCode]      = int((_GD_DISPLAYBOX_SIVIEWER_HEIGHT-_GD_DISPLAYBOX_GOFFSET*2)*self.scaler/_GD_DISPLAYBOX_GRID_HORIZONTALLINEPIXELINTERVAL_SIVIEWER)

        #[9]: Data & Analysis
        #---Descriptor
        self.currencySymbol = None
        self.currencyInfo   = None
        self.intervalID     = auxiliaries.KLINE_INTERVAL_ID_1m
        #---Data
        self._data_raw        = {target: dict() for target in ('kline', 'depth', 'aggTrade')}                    #self._data_raw[dataType][timestamp]
        self._data_agg        = {self.intervalID: {target: dict() for target in ('kline', 'depth', 'aggTrade')}} #self._data_agg[intervalID][dataType][timestamp]
        self._data_timestamps = {self.intervalID: {target: list() for target in ('kline', 'depth', 'aggTrade')}}
        #---Analysis Control
        self.analysisParams = {self.intervalID: dict()}
        #---Display Control
        self.__drawQueue        = dict()
        self.__drawn            = dict()
        self.__drawRemovalQueue = set()
        self.__drawerFunctions = {'KLINE':        self.__drawer_KLINE,
                                  'DEPTHOVERLAY': self.__drawer_DEPTHOVERLAY,
                                  'SMA':          self.__drawer_SMA,
                                  'WMA':          self.__drawer_WMA,
                                  'EMA':          self.__drawer_EMA,
                                  'PSAR':         self.__drawer_PSAR,
                                  'BOL':          self.__drawer_BOL,
                                  'IVP':          self.__drawer_IVP,
                                  'SWING':        self.__drawer_SWING,
                                  'VOL':          self.__drawer_VOL,
                                  'DEPTH':        self.__drawer_DEPTH,
                                  'AGGTRADE':     self.__drawer_AGGTRADE,
                                  'NNA':          self.__drawer_NNA,
                                  'MMACD':        self.__drawer_MMACD,
                                  'DMIxADX':      self.__drawer_DMIxADX,
                                  'MFI':          self.__drawer_MFI,
                                  'TPD':          self.__drawer_TPD,
                                  'TRADELOG':     self.__drawer_TRADELOG}
        self.siTypes_siViewerAlloc = {siType: None  for siType in _SITYPES} #Allocated SIViewer Number for the corresponding SI Type
        self.siTypes_analysisCodes = {siType: set() for siType in _SITYPES} #Allocated Analysis Codes for the corresponding SI type

        #[10]: Object Configuration
        self.sysFunc_editGUIOConfig = kwargs['sysFunctions']['EDITGUIOCONFIG']
        self.objectConfig = dict()
        oc_imported = kwargs['guioConfig'].get(self.name, None)
        if oc_imported is None: self.__initializeObjectConfig()
        else:                   self.objectConfig = oc_imported.copy()

        #[11]: Initialization Final
        self.status = "DEFAULT"
        self.hidden = False
        self.__configureDisplayBoxes(onInit = True)
        self.__initializeAuxBar()
        self.__initializeSettingsSubPage()
        self.__matchGUIOsToConfig()
    #Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #DisplayBox Control ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __configureDisplayBoxes(self, onInit = False):
        #[1]: Determine Vertical DisplayBox Order
        #---[1-1]: Temporal Grid
        self.displayBox_VerticalSection_Order = ['TEMPORALGRID']
        self.displayBox_VisibleBoxes          = ['MAINGRID_TEMPORAL', 'SETTINGSBUTTONFRAME']
        #---[1-2]: SI Viewers (Reverse Order)
        for siViewerIndex in range (self.usableSIViewers-1, -1, -1):
            if self.objectConfig[f'SIVIEWER{siViewerIndex}Display']:
                self.displayBox_VerticalSection_Order.append(f'SIVIEWER{siViewerIndex}')
                self.displayBox_VisibleBoxes.append(f'SIVIEWER{siViewerIndex}')
        #---[1-3]: Klines Price
        self.displayBox_VerticalSection_Order.append('KLINESPRICE')
        self.displayBox_VisibleBoxes.append('KLINESPRICE')
        #---[1-4]: AUX Bar
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
                    drawBox_AUXILLARYBAR    = (displayBox_AUXILLARYBAR[0]+_GD_DISPLAYBOX_GOFFSET, displayBox_AUXILLARYBAR[1]+_GD_DISPLAYBOX_GOFFSET, displayBox_AUXILLARYBAR[2]-_GD_DISPLAYBOX_GOFFSET*2, displayBox_AUXILLARYBAR[3]-_GD_DISPLAYBOX_GOFFSET*2)
                    self.displayBox['AUXILLARYBAR'] = displayBox_AUXILLARYBAR
                    self.displayBox_graphics['AUXILLARYBAR']['DRAWBOX'] = drawBox_AUXILLARYBAR
                
        #[3]: Set DisplayBox Objects (HitBox, Images, FrameSprites, CamGroups, RCLCGs, etc.)
        if (True):
            self.nMaxVerticalGridLines = int((self.displayBox['MAINGRID_TEMPORAL'][2]-_GD_DISPLAYBOX_GOFFSET*2)*self.scaler/_GD_DISPLAYBOX_GRID_VERTICALLINEPIXELINTERVAL)
            self.nMaxHorizontalGridLines['KLINESPRICE'] = int((self.displayBox['KLINESPRICE'][3]-_GD_DISPLAYBOX_GOFFSET*2)*self.scaler/_GD_DISPLAYBOX_GRID_HORIZONTALLINEPIXELINTERVAL)

            if onInit:
                for displayBoxName in self.displayBox:
                    self.mouse_DragDX[displayBoxName] = 0; self.mouse_DragDY[displayBoxName] = 0; self.mouse_ScrollDX[displayBoxName] = 0; self.mouse_ScrollDY[displayBoxName] = 0
                    #---MAINGRID_TEMPORAL
                    if (displayBoxName == 'MAINGRID_TEMPORAL'):
                        displayBox = self.displayBox['MAINGRID_TEMPORAL']
                        drawBox    = self.displayBox_graphics['MAINGRID_TEMPORAL']['DRAWBOX']
                        
                        #Generate Graphic Sprites and Hitboxes
                        self.hitBox['MAINGRID_TEMPORAL'] = hit_boxes.hitBox_Rectangular(drawBox[0], drawBox[1], drawBox[2], drawBox[3])
                        self.images['MAINGRID_TEMPORAL'] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                        self.frameSprites['MAINGRID_TEMPORAL'] = pyglet.sprite.Sprite(x = displayBox[0]*self.scaler, y = displayBox[1]*self.scaler, img = self.images['MAINGRID_TEMPORAL'][0], batch = self.batch, group = self.group_0)

                        #Setup CamGroup
                        self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_CAMGROUP'] = advanced_pyglet_groups.cameraGroup(window = self.window, order = self.groupOrder+1, viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_y0 = 0, projection_y1 = drawBox[3]*self.scaler)

                        #Setup Grids
                        self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_LINES'] = list()
                        self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS'] = list()
                        for i in range (self.nMaxVerticalGridLines):
                            self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_LINES'].append(pyglet.shapes.Line(0, (_GD_DISPLAYBOX_GRID_VERTICALTEXTHEIGHT+_GD_DISPLAYBOX_GOFFSET)*self.scaler, 0, drawBox[3]*self.scaler, width = 3, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_CAMGROUP']))
                            self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS'].append(text_control.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_CAMGROUP'], text = "-", defaultTextStyle = self.effectiveTextStyle['GRID'],
                                                                                                                                              xPos = 0, yPos = 0, width = _GD_DISPLAYBOX_GRID_VERTICALTEXTWIDTH, height = _GD_DISPLAYBOX_GRID_VERTICALTEXTHEIGHT, showElementBox = False, anchor = 'CENTER'))
                            self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_LINES'][-1].visible = False
                            self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS'][-1].hide()
                    #---SETTINGSBUTTONFRAME
                    elif (displayBoxName == 'SETTINGSBUTTONFRAME'):
                        self.hitBox['SETTINGSBUTTONFRAME'] = hit_boxes.hitBox_Rectangular(self.displayBox['SETTINGSBUTTONFRAME'][0], self.displayBox['SETTINGSBUTTONFRAME'][1], self.displayBox['SETTINGSBUTTONFRAME'][2], self.displayBox['SETTINGSBUTTONFRAME'][3])
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
                        self.hitBox['KLINESPRICE']                = hit_boxes.hitBox_Rectangular(drawBox[0], drawBox[1], drawBox[2], drawBox[3])
                        self.images['KLINESPRICE']                = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                        self.frameSprites['KLINESPRICE']          = pyglet.sprite.Sprite(x = displayBox[0]*self.scaler, y = displayBox[1]*self.scaler, img = self.images['KLINESPRICE'][0], batch = self.batch, group = self.group_0)
                        self.hitBox['MAINGRID_KLINESPRICE']       = hit_boxes.hitBox_Rectangular(drawBox_MAINGRID[0], drawBox_MAINGRID[1], drawBox_MAINGRID[2], drawBox_MAINGRID[3])
                        self.images['MAINGRID_KLINESPRICE']       = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrame", displayBox_MAINGRID[2]*self.scaler, displayBox_MAINGRID[3]*self.scaler)
                        self.frameSprites['MAINGRID_KLINESPRICE'] = pyglet.sprite.Sprite(x = displayBox_MAINGRID[0]*self.scaler, y = displayBox_MAINGRID[1]*self.scaler, img = self.images['MAINGRID_KLINESPRICE'][0], batch = self.batch, group = self.group_0)

                        #Setup CamGroup and DisplaySpaceManager
                        self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_CAMGROUP']    = advanced_pyglet_groups.cameraGroup(window=self.window, order = self.groupOrder+1,  viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_x0 = 0, projection_x1 = drawBox[2]*self.scaler)
                        self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_CAMGROUP']      = advanced_pyglet_groups.cameraGroup(window=self.window, order = self.groupOrder+1,  viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_y0 = 0, projection_y1 = drawBox[3]*self.scaler)
                        self.displayBox_graphics['KLINESPRICE']['DESCRIPTORDISPLAY_CAMGROUP'] = advanced_pyglet_groups.cameraGroup(window=self.window, order = self.groupOrder+27, viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_x0 = 0, projection_x1 = drawBox[2]*self.scaler)
                        self.displayBox_graphics['KLINESPRICE']['RCLCG']        = advanced_pyglet_groups.resolutionControlledLayeredCameraGroup(window = self.window, batch = self.batch, viewport_x = drawBox[0]*self.scaler, viewport_y = drawBox[1]*self.scaler, viewport_width = drawBox[2]*self.scaler, viewport_height = drawBox[3]*self.scaler, order = self.groupOrder+2, parentCameraGroup = self.parentCameraGroup, fsdResolution_y = 2)
                        self.displayBox_graphics['KLINESPRICE']['RCLCG_XFIXED'] = advanced_pyglet_groups.resolutionControlledLayeredCameraGroup(window = self.window, batch = self.batch, viewport_x = drawBox[0]*self.scaler, viewport_y = drawBox[1]*self.scaler, viewport_width = drawBox[2]*self.scaler, viewport_height = drawBox[3]*self.scaler, order = self.groupOrder+2, parentCameraGroup = self.parentCameraGroup, projection_x0 = 0, projection_x1 = 100, fsdResolution_y = 5)
                        self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'] = advanced_pyglet_groups.resolutionControlledLayeredCameraGroup(window = self.window, batch = self.batch, viewport_x = drawBox[0]*self.scaler, viewport_y = drawBox[1]*self.scaler, viewport_width = drawBox[2]*self.scaler, viewport_height = drawBox[3]*self.scaler, order = self.groupOrder+2, parentCameraGroup = self.parentCameraGroup, projection_y0 = 0, projection_y1 = 100)
                        self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_CAMGROUP'] = advanced_pyglet_groups.cameraGroup(window = self.window, order = self.groupOrder+1, viewport_x=drawBox_MAINGRID[0]*self.scaler, viewport_y=drawBox_MAINGRID[1]*self.scaler, viewport_width=drawBox_MAINGRID[2]*self.scaler, viewport_height=drawBox_MAINGRID[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_x0 = 0, projection_x1 = drawBox_MAINGRID[2]*self.scaler)
                            
                        #Add RCLCGs to the reference list
                        self.__RCLCGReferences.append(self.displayBox_graphics['KLINESPRICE']['RCLCG'])
                        self.__RCLCGReferences.append(self.displayBox_graphics['KLINESPRICE']['RCLCG_XFIXED'])
                        self.__RCLCGReferences.append(self.displayBox_graphics['KLINESPRICE']['RCLCG_YFIXED'])

                        #Description Texts
                        self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT1'] = text_control.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_hd0, text = "", 
                                                                                                                 defaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle,
                                                                                                                 xPos = drawBox[0], yPos = drawBox[1]+drawBox[3]-200, width = drawBox[2], height = 200, showElementBox = False, anchor = 'W')
                        self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2'] = text_control.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_hd0, text = "", 
                                                                                                                 defaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle,
                                                                                                                 xPos = drawBox[0], yPos = drawBox[1]+drawBox[3]-400, width = drawBox[2], height = 200, showElementBox = False, anchor = 'W')
                        self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT3'] = text_control.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_hd0, text = "", 
                                                                                                                 defaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle,
                                                                                                                 xPos = drawBox[0], yPos = drawBox[1]+drawBox[3]-200, width = drawBox[2], height = 200, showElementBox = False, anchor = 'E')
                        #Setup Positional Highlight
                        self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_HOVERED']  = pyglet.shapes.Rectangle(x = 0, y = 0, width = 0, height = drawBox[3]*self.scaler, color = self.posHighlightColor_hovered,  batch = self.batch, group = self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_CAMGROUP'])
                        self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_SELECTED'] = pyglet.shapes.Rectangle(x = 0, y = 0, width = 0, height = drawBox[3]*self.scaler, color = self.posHighlightColor_selected, batch = self.batch, group = self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_CAMGROUP'])
                        self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_HOVERED'].visible  = False
                        self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_SELECTED'].visible = False
                        self.displayBox_graphics['KLINESPRICE']['HORIZONTALGUIDELINE'] = pyglet.shapes.Line(0, 0, drawBox[2]*self.scaler, 0, width = 3, color = self.guideColor, batch = self.batch, group = self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_CAMGROUP'])
                        self.displayBox_graphics['KLINESPRICE']['HORIZONTALGUIDETEXT'] = text_control.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics['KLINESPRICE']['DESCRIPTORDISPLAY_CAMGROUP'], text = "", defaultTextStyle = self.effectiveTextStyle['GUIDECONTENT'],
                                                                                                                              xPos = 0, yPos = 0, width = drawBox[2], height = _GD_DISPLAYBOX_GUIDE_HORIZONTALTEXTHEIGHT, showElementBox = False, anchor = 'E')
                        self.displayBox_graphics['KLINESPRICE']['HORIZONTALGUIDELINE'].visible = False
                        self.displayBox_graphics['KLINESPRICE']['HORIZONTALGUIDETEXT'].hide()

                        #Setup Grids
                        self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_LINES']          = list()
                        self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_LINES']            = list()
                        self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_LINES'] = list()
                        self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_TEXTS'] = list()
                        for i in range (self.nMaxHorizontalGridLines['KLINESPRICE']):
                            self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_LINES'].append(pyglet.shapes.Line(0, 0, drawBox[2]*self.scaler, 0, width = 1, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_CAMGROUP']))
                            self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_LINES'][-1].visible = False
                            self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_LINES'].append(pyglet.shapes.Line(0, 0, _GD_DISPLAYBOX_GOFFSET*self.scaler, 0, width = 3, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_CAMGROUP']))
                            self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_TEXTS'].append(text_control.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_CAMGROUP'], text = "-", defaultTextStyle = self.effectiveTextStyle['GRID'],
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
                        self.hitBox[dBoxName] = hit_boxes.hitBox_Rectangular(drawBox[0], drawBox[1], drawBox[2], drawBox[3])
                        self.images[dBoxName] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                        self.frameSprites[dBoxName] = pyglet.sprite.Sprite(x = displayBox[0]*self.scaler, y = displayBox[1]*self.scaler, img = self.images[dBoxName][0], batch = self.batch, group = self.group_0)
                        self.hitBox[dBoxName_MAINGRID] = hit_boxes.hitBox_Rectangular(drawBox_MAINGRID[0], drawBox_MAINGRID[1], drawBox_MAINGRID[2], drawBox_MAINGRID[3])
                        self.images[dBoxName_MAINGRID] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrame", displayBox_MAINGRID[2]*self.scaler, displayBox_MAINGRID[3]*self.scaler)
                        self.frameSprites[dBoxName_MAINGRID] = pyglet.sprite.Sprite(x = displayBox_MAINGRID[0]*self.scaler, y = displayBox_MAINGRID[1]*self.scaler, img = self.images[dBoxName_MAINGRID][0], batch = self.batch, group = self.group_0)

                        #Setup CamGroup and DisplaySpaceManager
                        self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP']    = advanced_pyglet_groups.cameraGroup(window = self.window, order = self.groupOrder+1,  viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_x0 = 0, projection_x1 = drawBox[2]*self.scaler)
                        self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP']      = advanced_pyglet_groups.cameraGroup(window = self.window, order = self.groupOrder+1,  viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_y0 = 0, projection_y1 = drawBox[3]*self.scaler)
                        self.displayBox_graphics[dBoxName]['DESCRIPTORDISPLAY_CAMGROUP'] = advanced_pyglet_groups.cameraGroup(window = self.window, order = self.groupOrder+12, viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_x0 = 0, projection_x1 = drawBox[2]*self.scaler)
                        self.displayBox_graphics[dBoxName]['RCLCG']                      = advanced_pyglet_groups.resolutionControlledLayeredCameraGroup(window = self.window, batch = self.batch, viewport_x = drawBox[0]*self.scaler, viewport_y = drawBox[1]*self.scaler, viewport_width = drawBox[2]*self.scaler, viewport_height = drawBox[3]*self.scaler, order = self.groupOrder+2, parentCameraGroup = self.parentCameraGroup, fsdResolution_y = 2)
                        self.displayBox_graphics[dBoxName]['RCLCG_XFIXED']               = advanced_pyglet_groups.resolutionControlledLayeredCameraGroup(window = self.window, batch = self.batch, viewport_x = drawBox[0]*self.scaler, viewport_y = drawBox[1]*self.scaler, viewport_width = drawBox[2]*self.scaler, viewport_height = drawBox[3]*self.scaler, order = self.groupOrder+2, parentCameraGroup = self.parentCameraGroup, projection_x0 = 0, projection_x1 = 100, fsdResolution_y = 5)
                        self.displayBox_graphics[dBoxName]['RCLCG_YFIXED']               = advanced_pyglet_groups.resolutionControlledLayeredCameraGroup(window = self.window, batch = self.batch, viewport_x = drawBox[0]*self.scaler, viewport_y = drawBox[1]*self.scaler, viewport_width = drawBox[2]*self.scaler, viewport_height = drawBox[3]*self.scaler, order = self.groupOrder+2, parentCameraGroup = self.parentCameraGroup, projection_y0 = 0, projection_y1 = 100)
                        self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_CAMGROUP'] = advanced_pyglet_groups.cameraGroup(window = self.window, order = self.groupOrder+1, viewport_x=drawBox_MAINGRID[0]*self.scaler, viewport_y=drawBox_MAINGRID[1]*self.scaler, viewport_width=drawBox_MAINGRID[2]*self.scaler, viewport_height=drawBox_MAINGRID[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_x0 = 0, projection_x1 = drawBox_MAINGRID[2]*self.scaler)
                            
                        #Add RCLCGs to the reference list
                        self.__RCLCGReferences.append(self.displayBox_graphics[dBoxName]['RCLCG'])
                        self.__RCLCGReferences.append(self.displayBox_graphics[dBoxName]['RCLCG_XFIXED'])
                        self.__RCLCGReferences.append(self.displayBox_graphics[dBoxName]['RCLCG_YFIXED'])

                        #Description Texts
                        self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT1'] = text_control.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_hd0, text = "", 
                                                                                                                        defaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle,
                                                                                                                        xPos = drawBox[0], yPos = drawBox[1]+drawBox[3]-200, width = drawBox[2], height = 200, showElementBox = False, anchor = 'W')

                        #Setup Positional Highlight
                        self.displayBox_graphics[dBoxName]['POSHIGHLIGHT_HOVERED']  = pyglet.shapes.Rectangle(x = 0, y = 0, width = 0, height = drawBox[3]*self.scaler, color = self.posHighlightColor_hovered,  batch = self.batch, group = self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'])
                        self.displayBox_graphics[dBoxName]['POSHIGHLIGHT_SELECTED'] = pyglet.shapes.Rectangle(x = 0, y = 0, width = 0, height = drawBox[3]*self.scaler, color = self.posHighlightColor_selected, batch = self.batch, group = self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'])
                        self.displayBox_graphics[dBoxName]['POSHIGHLIGHT_HOVERED'].visible  = False
                        self.displayBox_graphics[dBoxName]['POSHIGHLIGHT_SELECTED'].visible = False
                        self.displayBox_graphics[dBoxName]['HORIZONTALGUIDELINE'] = pyglet.shapes.Line(0, 0, drawBox[2]*self.scaler, 0, width = 3, color = self.guideColor, batch = self.batch, group = self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'])
                        self.displayBox_graphics[dBoxName]['HORIZONTALGUIDETEXT'] = text_control.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics[dBoxName]['DESCRIPTORDISPLAY_CAMGROUP'], text = "", defaultTextStyle = self.effectiveTextStyle['GUIDECONTENT'],
                                                                                                                         xPos = 0, yPos = 0, width = drawBox[2], height = _GD_DISPLAYBOX_GUIDE_HORIZONTALTEXTHEIGHT, showElementBox = False, anchor = 'E')
                        self.displayBox_graphics[dBoxName]['HORIZONTALGUIDELINE'].visible = False
                        self.displayBox_graphics[dBoxName]['HORIZONTALGUIDETEXT'].hide()

                        #Setup Grids
                        self.displayBox_graphics[dBoxName]['HORIZONTALGRID_LINES']          = list()
                        self.displayBox_graphics[dBoxName]['VERTICALGRID_LINES']            = list()
                        self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_LINES'] = list()
                        self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_TEXTS'] = list()
                        for i in range (self.nMaxHorizontalGridLines[dBoxName]):
                            self.displayBox_graphics[dBoxName]['HORIZONTALGRID_LINES'].append(pyglet.shapes.Line(0, 0, drawBox[2]*self.scaler, 0, width = 1, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP']))
                            self.displayBox_graphics[dBoxName]['HORIZONTALGRID_LINES'][-1].visible = False
                            self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_LINES'].append(pyglet.shapes.Line(0, 0, _GD_DISPLAYBOX_GOFFSET*self.scaler, 0, width = 3, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_CAMGROUP']))
                            self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_TEXTS'].append(text_control.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_CAMGROUP'], text = "-", defaultTextStyle = self.effectiveTextStyle['GRID'],
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
                        #Generate Graphic Sprites and Hitboxes
                        self.hitBox['AUXILLARYBAR'] = hit_boxes.hitBox_Rectangular(displayBox[0], displayBox[1], displayBox[2], displayBox[3])
                        self.images['AUXILLARYBAR'] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                        self.frameSprites['AUXILLARYBAR'] = pyglet.sprite.Sprite(x = displayBox[0]*self.scaler, y = displayBox[1]*self.scaler, img = self.images['AUXILLARYBAR'][0], batch = self.batch, group = self.group_0)
                        #Position & Size AuxBarPage
                        self.auxBarPage.moveTo(x = displayBox[0]+50, y = displayBox[1]+50)
                        self.auxBarPage.resize(width = displayBox[2]-100, height = displayBox[3]-100)
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
                            self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_CAMGROUP'].updateViewport(viewport_x    =drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_CAMGROUP'].updateViewport(viewport_x      =drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics['KLINESPRICE']['DESCRIPTORDISPLAY_CAMGROUP'].updateViewport(viewport_x =drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics['KLINESPRICE']['HORIZONTALGRID_CAMGROUP'].updateProjection(projection_x0   =0, projection_x1=drawBox[2]*self.scaler)
                            self.displayBox_graphics['KLINESPRICE']['VERTICALGRID_CAMGROUP'].updateProjection(projection_y0     =0, projection_y1=drawBox[3]*self.scaler)
                            self.displayBox_graphics['KLINESPRICE']['DESCRIPTORDISPLAY_CAMGROUP'].updateProjection(projection_x0=0, projection_x1=drawBox[2]*self.scaler)
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
                                self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_TEXTS'].append(text_control.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics['MAINGRID_KLINESPRICE']['HORIZONTALGRID_CAMGROUP'], text = "-", defaultTextStyle = self.effectiveTextStyle['GRID'],
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
                                self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS'].append(text_control.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics['MAINGRID_TEMPORAL']['VERTICALGRID_CAMGROUP'], text = "-", defaultTextStyle = self.effectiveTextStyle['GRID'],
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
                            self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].updateViewport(   viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'].updateViewport(     viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics[dBoxName]['DESCRIPTORDISPLAY_CAMGROUP'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].updateProjection(projection_x0    = 0, projection_x1 = drawBox[2]*self.scaler)
                            self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'].updateProjection(projection_y0      = 0, projection_y1 = drawBox[3]*self.scaler)
                            self.displayBox_graphics[dBoxName]['DESCRIPTORDISPLAY_CAMGROUP'].updateProjection(projection_x0 = 0, projection_x1 = drawBox[2]*self.scaler)
                            self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].show()
                            self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'].show()
                            self.displayBox_graphics[dBoxName]['DESCRIPTORDISPLAY_CAMGROUP'].show()
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
                                self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_TEXTS'].append(text_control.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics[dBoxName_MAINGRID]['HORIZONTALGRID_CAMGROUP'], text = "-", defaultTextStyle = self.effectiveTextStyle['GRID'],
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
                            #Reposition & Resize Graphics and Hitboxes
                            self.hitBox['AUXILLARYBAR'].reposition(xPos = displayBox[0], yPos = displayBox[1])
                            self.hitBox['AUXILLARYBAR'].resize(width = displayBox[2], height = displayBox[3])
                            self.images['AUXILLARYBAR'] = self.imageManager.getImageByCode("chartDrawer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                            self.frameSprites['AUXILLARYBAR'].position = (displayBox[0]*self.scaler, displayBox[1]*self.scaler, self.frameSprites['AUXILLARYBAR'].z)
                            self.frameSprites['AUXILLARYBAR'].image = self.images['AUXILLARYBAR'][0]
                            self.frameSprites['AUXILLARYBAR'].visible = True
                            #Reposition & Resize AuxBarPage
                            self.auxBarPage.moveTo(x = displayBox[0]+50, y = displayBox[1]+50)
                            self.auxBarPage.resize(width = displayBox[2]-100, height = displayBox[3]-100)
                    else: self.__hideDisplayBox(displayBoxName)

        #[4]: Size and Position Klines Loading Gauge Bar and Text
        self.loadingGaugeBar.resize(width      = round(self.width*0.9), height = _GD_KLINESLOADINGGAUGEBAR_HEIGHT)
        self.loadingTextBox_perc.resize(width  = round(self.width*0.9), height = _GD_KLINESLOADINGGAUGEBAR_HEIGHT)
        self.loadingTextBox.resize(width       = round(self.width*0.9), height = 200)
        self.loadingGaugeBar.moveTo(x     = round(self.xPos+self.width*0.05), y = round(self.yPos+self.height/2-_GD_KLINESLOADINGGAUGEBAR_HEIGHT))
        self.loadingTextBox_perc.moveTo(x = round(self.xPos+self.width*0.05), y = round(self.yPos+self.height/2-_GD_KLINESLOADINGGAUGEBAR_HEIGHT))
        self.loadingTextBox.moveTo(x      = round(self.xPos+self.width*0.05), y = round(self.yPos+self.height/2))

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
            self.displayBox_graphics[dBoxName]['DESCRIPTORDISPLAY_CAMGROUP'].hide()
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
        self._initializeSIViewer(siViewerCode = f"SIVIEWER{siViewerIndex}")
        
        #[3]: Set ViewRanges
        self._onHViewRangeUpdate(updateType = 1)
        self.__onVViewRangeUpdate(displayBoxName = 'KLINESPRICE', updateType = 1)
        for visibleSIViewerCode in self.displayBox_graphics_visibleSIViewers: self.__onVViewRangeUpdate(displayBoxName = visibleSIViewerCode, updateType = 1)
        
        #[4]: If siViewerDisplay == True, update Draw Queues
        siAlloc = self.objectConfig[f'SIVIEWER{siViewerIndex}SIAlloc']
        if siViewerDisplay:
            self.checkVerticalExtremas_SIs[siAlloc]()
            if siAlloc in {'VOL', 'DEPTH', 'AGGTRADE', 'MMACD', 'DMIxADX', 'MFI', 'TPD'}:
                if siAlloc in {'VOL', 'DEPTH', 'AGGTRADE'}: 
                    self.__addBufferZone_toDrawQueue(analysisCode = siAlloc, 
                                                     drawSignal   = _FULLDRAWSIGNALS[siAlloc])
                if self.siTypes_analysisCodes[siAlloc] is not None:
                    for aCode in self.siTypes_analysisCodes[siAlloc]: self.__addBufferZone_toDrawQueue(analysisCode = aCode, drawSignal = _FULLDRAWSIGNALS[siAlloc])

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
        if siViewerDisplay1: self._initializeSIViewer(siViewerCode = siViewerCode1)
        if siViewerDisplay2: self._initializeSIViewer(siViewerCode = siViewerCode2)

        #[4]: Set ViewRanges
        if siViewerDisplay1:
            if self.checkVerticalExtremas_SIs[siViewerDisplayTarget1]():
                if   siViewerDisplayTarget1 == 'VOL':      self._editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex1}", extension_b = 0.0, extension_t = 0.2)
                elif siViewerDisplayTarget1 == 'DEPTH':    self._editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex1}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget1 == 'AGGTRADE': self._editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex1}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget1 == 'NNA':      self._editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex1}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget1 == 'MMACD':    self._editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex1}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget1 == 'DMIxADX':  self._editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex1}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget1 == 'MFI':      self._editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex1}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget1 == 'TPD':      self._editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex1}", extension_b = 0.1, extension_t = 0.1)
        if siViewerDisplay2: 
            if self.checkVerticalExtremas_SIs[siViewerDisplayTarget2]():
                if   siViewerDisplayTarget2 == 'VOL':      self._editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex2}", extension_b = 0.0, extension_t = 0.2)
                elif siViewerDisplayTarget2 == 'DEPTH':    self._editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex2}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget2 == 'AGGTRADE': self._editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex2}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget2 == 'NNA':      self._editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex2}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget2 == 'MMACD':    self._editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex2}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget2 == 'DMIxADX':  self._editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex2}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget2 == 'MFI':      self._editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex2}", extension_b = 0.1, extension_t = 0.1)
                elif siViewerDisplayTarget2 == 'TPD':      self._editVVR_toExtremaCenter(displayBoxName = f"SIVIEWER{siViewerIndex2}", extension_b = 0.1, extension_t = 0.1)

        #[5]: If siViewerDisplay == True, update Draw Queues
        if siViewerDisplay1:
            if siViewerDisplayTarget1 in {'VOL', 'DEPTH', 'AGGTRADE', 'MMACD', 'DMIxADX', 'MFI', 'TPD'}:
                if siViewerDisplayTarget1 in {'VOL', 'DEPTH', 'AGGTRADE'}: 
                    self.__addBufferZone_toDrawQueue(analysisCode = siViewerDisplayTarget1, 
                                                     drawSignal   = _FULLDRAWSIGNALS[siViewerDisplayTarget1])

                if self.siTypes_analysisCodes[siViewerDisplayTarget1] is not None:
                    for aCode in self.siTypes_analysisCodes[siViewerDisplayTarget1]:
                        self.__addBufferZone_toDrawQueue(analysisCode = aCode, drawSignal = _FULLDRAWSIGNALS[siViewerDisplayTarget1])

        if siViewerDisplay2:
            if siViewerDisplayTarget2 in {'VOL', 'DEPTH', 'AGGTRADE', 'MMACD', 'DMIxADX', 'MFI', 'TPD'}:
                if siViewerDisplayTarget2 in {'VOL', 'DEPTH', 'AGGTRADE'}: 
                    self.__addBufferZone_toDrawQueue(analysisCode = siViewerDisplayTarget2, 
                                                     drawSignal   = _FULLDRAWSIGNALS[siViewerDisplayTarget2])
                if self.siTypes_analysisCodes[siViewerDisplayTarget2] is not None:
                    for aCode in self.siTypes_analysisCodes[siViewerDisplayTarget2]: 
                        self.__addBufferZone_toDrawQueue(analysisCode = aCode, drawSignal = _FULLDRAWSIGNALS[siViewerDisplayTarget2])

        #[6]: Return SIViewerIndex2 for reference
        return siViewerIndex2

    def _initializeRCLCGs(self, displayBoxName):
        self.verticalViewRange_precision[displayBoxName] = 0
        precision_x = math.floor(math.log(self.expectedKlineTemporalWidth, 10))
        dBox_g_this = self.displayBox_graphics[displayBoxName]
        dBox_g_this['RCLCG'].setPrecision(precision_x        = precision_x, precision_y = 0, transferObjects = False)
        dBox_g_this['RCLCG_XFIXED'].setPrecision(precision_x = 0,           precision_y = 0, transferObjects = False)
        dBox_g_this['RCLCG_YFIXED'].setPrecision(precision_x = precision_x, precision_y = 0, transferObjects = False)
        
    def _initializeSIViewer(self, siViewerCode):
        self._initializeRCLCGs(siViewerCode)
        self.verticalValue_min[siViewerCode] = -1
        self.verticalValue_max[siViewerCode] =  1
        self.__onVerticalExtremaUpdate(displayBoxName = siViewerCode, updateType = 1)
    #DisplayBox Control END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Object Configuration & GUIO Initialization ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
        oc['DEPTHOVERLAY_Display'] = True
        oc['DEPTHOVERLAY_BIDS_ColorR%DARK'] =100; oc['DEPTHOVERLAY_BIDS_ColorG%DARK'] =255; oc['DEPTHOVERLAY_BIDS_ColorB%DARK'] =180; oc['DEPTHOVERLAY_BIDS_ColorA%DARK'] =120
        oc['DEPTHOVERLAY_BIDS_ColorR%LIGHT']= 80; oc['DEPTHOVERLAY_BIDS_ColorG%LIGHT']=200; oc['DEPTHOVERLAY_BIDS_ColorB%LIGHT']=150; oc['DEPTHOVERLAY_BIDS_ColorA%LIGHT']=120
        oc['DEPTHOVERLAY_ASKS_ColorR%DARK'] =255; oc['DEPTHOVERLAY_ASKS_ColorG%DARK'] =100; oc['DEPTHOVERLAY_ASKS_ColorB%DARK'] =100; oc['DEPTHOVERLAY_ASKS_ColorA%DARK'] =120
        oc['DEPTHOVERLAY_ASKS_ColorR%LIGHT']=240; oc['DEPTHOVERLAY_ASKS_ColorG%LIGHT']= 80; oc['DEPTHOVERLAY_ASKS_ColorB%LIGHT']= 80; oc['DEPTHOVERLAY_ASKS_ColorA%LIGHT']=120
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
            oc[f'SWING_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'SWING_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'SWING_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'SWING_{lineIndex}_ColorA%DARK'] =255
            oc[f'SWING_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'SWING_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'SWING_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'SWING_{lineIndex}_ColorA%LIGHT']=255
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
        #---DEPTH Config
        oc['DEPTH_Master'] = False
        oc['DEPTH_BIDS_ColorR%DARK'] =100; oc['DEPTH_BIDS_ColorG%DARK'] =255; oc['DEPTH_BIDS_ColorB%DARK'] =180; oc['DEPTH_BIDS_ColorA%DARK'] =255
        oc['DEPTH_BIDS_ColorR%LIGHT']= 80; oc['DEPTH_BIDS_ColorG%LIGHT']=200; oc['DEPTH_BIDS_ColorB%LIGHT']=150; oc['DEPTH_BIDS_ColorA%LIGHT']=255
        oc['DEPTH_ASKS_ColorR%DARK'] =255; oc['DEPTH_ASKS_ColorG%DARK'] =100; oc['DEPTH_ASKS_ColorB%DARK'] =100; oc['DEPTH_ASKS_ColorA%DARK'] =255
        oc['DEPTH_ASKS_ColorR%LIGHT']=240; oc['DEPTH_ASKS_ColorG%LIGHT']= 80; oc['DEPTH_ASKS_ColorB%LIGHT']= 80; oc['DEPTH_ASKS_ColorA%LIGHT']=255
        #---AGGTRADE Config
        oc['AGGTRADE_Master'] = False
        oc['AGGTRADE_BUY_ColorR%DARK']  =100; oc['AGGTRADE_BUY_ColorG%DARK']  =255; oc['AGGTRADE_BUY_ColorB%DARK']  =180; oc['AGGTRADE_BUY_ColorA%DARK']  =255
        oc['AGGTRADE_BUY_ColorR%LIGHT'] = 80; oc['AGGTRADE_BUY_ColorG%LIGHT'] =200; oc['AGGTRADE_BUY_ColorB%LIGHT'] =150; oc['AGGTRADE_BUY_ColorA%LIGHT'] =255
        oc['AGGTRADE_SELL_ColorR%DARK'] =255; oc['AGGTRADE_SELL_ColorG%DARK'] =100; oc['AGGTRADE_SELL_ColorB%DARK'] =100; oc['AGGTRADE_SELL_ColorA%DARK'] =255
        oc['AGGTRADE_SELL_ColorR%LIGHT']=240; oc['AGGTRADE_SELL_ColorG%LIGHT']= 80; oc['AGGTRADE_SELL_ColorB%LIGHT']= 80; oc['AGGTRADE_SELL_ColorA%LIGHT']=255
        oc['AGGTRADE_DisplayType'] = 'QUANTITY'
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
        #---MMACD Config
        oc['MMACD_Master'] = False
        oc['MMACD_SignalNSamples']      = 10
        oc['MMACD_MMACD_Display']       = True
        oc['MMACD_SIGNAL_Display']      = True
        oc['MMACD_HISTOGRAM_Display']   = True
        oc['MMACD_HISTOGRAM_Type']      = 'MSDELTA'
        oc['MMACD_MMACD_ColorR%DARK']   = random.randint(64,255); oc['MMACD_MMACD_ColorG%DARK']   = random.randint(64,255); oc['MMACD_MMACD_ColorB%DARK']   = random.randint(64,255); oc['MMACD_MMACD_ColorA%DARK']   = 255
        oc['MMACD_MMACD_ColorR%LIGHT']  = random.randint(64,255); oc['MMACD_MMACD_ColorG%LIGHT']  = random.randint(64,255); oc['MMACD_MMACD_ColorB%LIGHT']  = random.randint(64,255); oc['MMACD_MMACD_ColorA%LIGHT']  = 255
        oc['MMACD_SIGNAL_ColorR%DARK']  = random.randint(64,255); oc['MMACD_SIGNAL_ColorG%DARK']  = random.randint(64,255); oc['MMACD_SIGNAL_ColorB%DARK']  = random.randint(64,255); oc['MMACD_SIGNAL_ColorA%DARK']  = 255
        oc['MMACD_SIGNAL_ColorR%LIGHT'] = random.randint(64,255); oc['MMACD_SIGNAL_ColorG%LIGHT'] = random.randint(64,255); oc['MMACD_SIGNAL_ColorB%LIGHT'] = random.randint(64,255); oc['MMACD_SIGNAL_ColorA%LIGHT'] = 255
        oc['MMACD_HISTOGRAM+_ColorR%DARK']  = 100; oc['MMACD_HISTOGRAM+_ColorG%DARK']  = 255; oc['MMACD_HISTOGRAM+_ColorB%DARK']  = 180; oc['MMACD_HISTOGRAM+_ColorA%DARK']  = 255
        oc['MMACD_HISTOGRAM+_ColorR%LIGHT'] =  80; oc['MMACD_HISTOGRAM+_ColorG%LIGHT'] = 200; oc['MMACD_HISTOGRAM+_ColorB%LIGHT'] = 150; oc['MMACD_HISTOGRAM+_ColorA%LIGHT'] = 255
        oc['MMACD_HISTOGRAM-_ColorR%DARK']  = 255; oc['MMACD_HISTOGRAM-_ColorG%DARK']  = 100; oc['MMACD_HISTOGRAM-_ColorB%DARK']  = 100; oc['MMACD_HISTOGRAM-_ColorA%DARK']  = 255
        oc['MMACD_HISTOGRAM-_ColorR%LIGHT'] = 240; oc['MMACD_HISTOGRAM-_ColorG%LIGHT'] =  80; oc['MMACD_HISTOGRAM-_ColorB%LIGHT'] =  80; oc['MMACD_HISTOGRAM-_ColorA%LIGHT'] = 255
        for lineIndex in range (_NMAXLINES['MMACD']):
            oc[f'MMACD_MA{lineIndex}_LineActive'] = False
            oc[f'MMACD_MA{lineIndex}_NSamples']   = 20*(lineIndex+1)
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
        #---TPD Config
        oc['TPD_Master'] = False
        for lineIndex in range (_NMAXLINES['TPD']):
            oc[f'TPD_{lineIndex}_LineActive'] = False
            oc[f'TPD_{lineIndex}_ViewLength'] = 15  *(lineIndex+1)
            oc[f'TPD_{lineIndex}_NSamples']   = 1000*(lineIndex+1)
            oc[f'TPD_{lineIndex}_NSamplesMA'] = 20  *(lineIndex+1)
            oc[f'TPD_{lineIndex}_Width'] = 1
            oc[f'TPD_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'TPD_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'TPD_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'TPD_{lineIndex}_ColorA%DARK'] =255
            oc[f'TPD_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'TPD_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'TPD_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'TPD_{lineIndex}_ColorA%LIGHT']=255
            oc[f'TPD_{lineIndex}_Display'] = True
        #Finally
        self.objectConfig = oc

    def __initializeAuxBar(self):
        #[1]: Instances
        vm  = self.visualManager
        aux = auxiliaries
        aggIntervals = [(aux.KLINE_INTERVAL_ID_1m,  'GUIO_CHARTDRAWER:AGGINTERVAL_1M'),
                        (aux.KLINE_INTERVAL_ID_3m,  'GUIO_CHARTDRAWER:AGGINTERVAL_3M'),
                        (aux.KLINE_INTERVAL_ID_5m,  'GUIO_CHARTDRAWER:AGGINTERVAL_5M'),
                        (aux.KLINE_INTERVAL_ID_15m, 'GUIO_CHARTDRAWER:AGGINTERVAL_15M'),
                        (aux.KLINE_INTERVAL_ID_30m, 'GUIO_CHARTDRAWER:AGGINTERVAL_30M'),
                        (aux.KLINE_INTERVAL_ID_1h,  'GUIO_CHARTDRAWER:AGGINTERVAL_1H'),
                        (aux.KLINE_INTERVAL_ID_2h,  'GUIO_CHARTDRAWER:AGGINTERVAL_2H'),
                        (aux.KLINE_INTERVAL_ID_4h,  'GUIO_CHARTDRAWER:AGGINTERVAL_4H'),
                        (aux.KLINE_INTERVAL_ID_6h,  'GUIO_CHARTDRAWER:AGGINTERVAL_6H'),
                        (aux.KLINE_INTERVAL_ID_8h,  'GUIO_CHARTDRAWER:AGGINTERVAL_8H'),
                        (aux.KLINE_INTERVAL_ID_12h, 'GUIO_CHARTDRAWER:AGGINTERVAL_12H'),
                        (aux.KLINE_INTERVAL_ID_1d,  'GUIO_CHARTDRAWER:AGGINTERVAL_1D'),
                        (aux.KLINE_INTERVAL_ID_3d,  'GUIO_CHARTDRAWER:AGGINTERVAL_3D'),
                        (aux.KLINE_INTERVAL_ID_1W,  'GUIO_CHARTDRAWER:AGGINTERVAL_1W'),
                        (aux.KLINE_INTERVAL_ID_1M,  'GUIO_CHARTDRAWER:AGGINTERVAL_1MONTH')]

        #[2]: Size Calculation
        auxBar        = self.displayBox['AUXILLARYBAR']
        availWidth    = auxBar[2] - 100
        availHeight   = auxBar[3] - 100
        textBoxWidth  = _GD_DISPLAYBOX_RIGHTSECTION_WIDTH * 2
        buttonWidth   = (availWidth - textBoxWidth - 50*15) // 15
        buttonHeight  = availHeight
        textBoxX      = 15*(buttonWidth+50)

        #[3]: GUIOs
        #---[3-1]: Aggregation Interval Switches
        for colIndex, (intervalID, textPackKey) in enumerate(aggIntervals):
            xPos = colIndex * (buttonWidth + 50)
            self.auxBarPage.addGUIO(f'AGGINTERVAL_{intervalID}', generals.switch_typeC,
                                    {'groupOrder': 0, 'xPos': xPos, 'yPos': 0, 'width': buttonWidth, 'height': buttonHeight,
                                     'style': 'styleB', 'name': intervalID,
                                     'text': vm.getTextPack(textPackKey), 'fontSize': 80,
                                     'statusUpdateFunction': self.__onAggIntervalButtonClick})
            self.auxBarPage.GUIOs[f'AGGINTERVAL_{intervalID}'].setStatus(self.intervalID == intervalID, callStatusUpdateFunction = False)
        #---[3-2]: Target Text
        self.auxBarPage.addGUIO('TARGETTEXT', generals.textBox_typeA,
                                {'groupOrder': 0, 'xPos': textBoxX, 'yPos': 0, 'width': textBoxWidth, 'height': buttonHeight,
                                 'style': 'styleB', 'text': '-', 'fontSize': 80})
    
    def __initializeSettingsSubPage(self):
        subPageViewSpaceWidth = 4000
        #<MAIN>
        if (True):
            ssp = self.settingsSubPages['MAIN']
            yPos_beg = 20000
            #Title
            ssp.addGUIO("TITLE_MAIN", generals.passiveGraphics_wrapperTypeB, {'groupOrder': 0, 'xPos': 0, 'yPos': yPos_beg, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_CHARTSETTINGS')})
            #Main Indicators
            yPosPoint0 = yPos_beg-200
            ssp.addGUIO("TITLE_MAININDICATORS", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MAININDICATORS'), 'fontSize': 80})
            for i, miType in enumerate(_MITYPES):
                ssp.addGUIO(f"MAININDICATOR_{miType}",      generals.switch_typeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-350-350*i, 'width': 3500, 'height': 250, 'style': 'styleB', 'name': f'MAIN_INDICATORSWITCH_{miType}', 'text': miType, 'fontSize': 80, 'releaseFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"MAININDICATORSETUP_{miType}", generals.button_typeA, {'groupOrder': 0, 'xPos': 3600, 'yPos': yPosPoint0-350-350*i, 'width':  400, 'height': 250, 'style': 'styleA', 'name': f'navButton_MI_{miType}',         'text': ">",    'fontSize': 80, 'releaseFunction': self.__onSettingsNavButtonClick})
            #Sub Indicators
            yPosPoint1 = yPosPoint0-300-350*len(_MITYPES)
            ssp.addGUIO("TITLE_SUBINDICATORS", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SUBINDICATORS'), 'fontSize': 80})
            for i, siType in enumerate(_SITYPES):
                ssp.addGUIO(f"SUBINDICATOR_{siType}",      generals.switch_typeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350-350*i, 'width': 3500, 'height': 250, 'style': 'styleB', 'name': f'MAIN_INDICATORSWITCH_{siType}', 'text': siType, 'fontSize': 80, 'releaseFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"SUBINDICATORSETUP_{siType}", generals.button_typeA, {'groupOrder': 0, 'xPos': 3600, 'yPos': yPosPoint1-350-350*i, 'width':  400, 'height': 250, 'style': 'styleA', 'text': ">", 'fontSize': 80, 'name': f'navButton_SI_{siType}', 'releaseFunction': self.__onSettingsNavButtonClick})
            #Sub Indicators Display
            yPosPoint2 = yPosPoint1-300-350*len(_SITYPES)
            ssp.addGUIO("TITLE_SUBINDICATORSDISPLAY", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SUBINDICATORDISPLAY'), 'fontSize': 80})
            siSelection = dict()
            for siType in _SITYPES: siSelection[siType] = {'text': siType}
            for siViewerIndex in range (len(_SITYPES)):
                ssp.addGUIO(f"SUBINDICATOR_DISPLAYSWITCH{siViewerIndex}",    generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint2-350-350*siViewerIndex, 'width': 1100, 'height': 250, 'style': 'styleB', 'name': f'MAIN_SIVIEWERDISPLAYSWITCH_{siViewerIndex}',    'text': self.visualManager.getTextPack(f'GUIO_CHARTDRAWER:INDICATOR{siViewerIndex}'), 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"SUBINDICATOR_DISPLAYSELECTION{siViewerIndex}", generals.selectionBox_typeB, {'groupOrder': 0, 'xPos': 1200, 'yPos': yPosPoint2-350-350*siViewerIndex, 'width': 2800, 'height': 250, 'style': 'styleA', 'name': f'MAIN_SIVIEWERDISPLAYSELECTION_{siViewerIndex}', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
                ssp.GUIOs[f"SUBINDICATOR_DISPLAYSELECTION{siViewerIndex}"].setSelectionList(selectionList = siSelection, displayTargets = 'all')
            #Analyzer
            yPosPoint3 = yPosPoint2-300-350*len(_SITYPES)
            ssp.addGUIO("TITLE_ANALYZER", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint3, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_ANALYZER'), 'fontSize': 80})
            ssp.addGUIO("ANALYZER_ANALYSISRANGEBEG_TEXT",       generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint3- 350, 'width': 2200, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:ANALYSISRANGEBEG'), 'fontSize': 80})
            ssp.addGUIO("ANALYZER_ANALYSISRANGEBEG_RANGEINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2300, 'yPos': yPosPoint3- 350, 'width': 1700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MAIN_ANALYSISRANGETEXTINPUTBOX', 'textUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("ANALYZER_ANALYSISRANGEEND_TEXT",       generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint3- 700, 'width': 2200, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:ANALYSISRANGEEND'), 'fontSize': 80})
            ssp.addGUIO("ANALYZER_ANALYSISRANGEEND_RANGEINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2300, 'yPos': yPosPoint3- 700, 'width': 1700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MAIN_ANALYSISRANGETEXTINPUTBOX', 'textUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("ANALYZER_STARTANALYSIS_BUTTON",        generals.button_typeA,       {'groupOrder': 0, 'xPos': 0,    'yPos': yPosPoint3-1050, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:STARTANALYSIS'), 'fontSize': 80, 'name': 'MAIN_STARTANALYSIS', 'releaseFunction': self.__onSettingsContentUpdate})
            #Trade Log
            yPosPoint4 = yPosPoint3-1350
            ssp.addGUIO("TITLE_TRADELOG",                generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos':  yPosPoint4, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_TRADELOG'), 'fontSize': 80})
            ssp.addGUIO("TRADELOGCOLOR_TEXT",            generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint4-350, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("TRADELOGCOLOR_TARGETSELECTION", generals.selectionBox_typeB, {'groupOrder': 2, 'xPos':  700, 'yPos': yPosPoint4-350, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'TRADELOG_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("TRADELOGCOLOR_LED",             generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2300, 'yPos': yPosPoint4-350, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("TRADELOGCOLOR_APPLYCOLOR",      generals.button_typeA,       {'groupOrder': 0, 'xPos': 3350, 'yPos': yPosPoint4-350, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'TRADELOG_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"TRADELOGCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint4-700-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"TRADELOGCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': yPosPoint4-700-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'TRADELOG_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"TRADELOGCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': yPosPoint4-700-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            yPosPoint5 = yPosPoint4-2100
            ssp.addGUIO("TRADELOGDISPLAY_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos': 0,    'yPos': yPosPoint5, 'width': 1600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYTRADELOG'), 'fontSize': 80})
            ssp.addGUIO("TRADELOGDISPLAY_SWITCH", generals.switch_typeB,  {'groupOrder': 0, 'xPos': 1700, 'yPos': yPosPoint5, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'TRADELOG_DisplaySwitch', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("TRADELOGCOLOR_BUY_LED",  generals.LED_typeA,     {'groupOrder': 0, 'xPos': 2300, 'yPos': yPosPoint5, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("TRADELOGCOLOR_SELL_LED", generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3200, 'yPos': yPosPoint5, 'width':  800, 'height': 250, 'style': 'styleA', 'mode': True})
            lineSelections = {'BUY':  {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TRADELOG_BUY')},
                              'SELL': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TRADELOG_SELL')}}
            ssp.GUIOs["TRADELOGCOLOR_TARGETSELECTION"].setSelectionList(lineSelections, displayTargets = 'all')
            ssp.addGUIO("TRADELOG_APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint5-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'TRADELOG_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            #Bids and Asks
            yPosPoint6 = yPosPoint5-650
            ssp.addGUIO("TITLE_DEPTHOVERLAY",                generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos':  yPosPoint6, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_DEPTHOVERLAY'), 'fontSize': 80})
            ssp.addGUIO("DEPTHOVERLAYCOLOR_TEXT",            generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint6-350, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("DEPTHOVERLAYCOLOR_TARGETSELECTION", generals.selectionBox_typeB, {'groupOrder': 2, 'xPos':  700, 'yPos': yPosPoint6-350, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'DEPTHOVERLAY_LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("DEPTHOVERLAYCOLOR_LED",             generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2300, 'yPos': yPosPoint6-350, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("DEPTHOVERLAYCOLOR_APPLYCOLOR",      generals.button_typeA,       {'groupOrder': 0, 'xPos': 3350, 'yPos': yPosPoint6-350, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'DEPTHOVERLAY_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"DEPTHOVERLAYCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint6-700-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"DEPTHOVERLAYCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': yPosPoint6-700-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'DEPTHOVERLAY_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"DEPTHOVERLAYCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': yPosPoint6-700-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            yPosPoint7 = yPosPoint6-2100
            ssp.addGUIO("DEPTHOVERLAYDISPLAY_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos': 0,    'yPos': yPosPoint7, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYDEPTHOVERLAY'), 'fontSize': 80})
            ssp.addGUIO("DEPTHOVERLAYDISPLAY_SWITCH", generals.switch_typeB,  {'groupOrder': 0, 'xPos': 2100, 'yPos': yPosPoint7, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'DEPTHOVERLAY_DisplaySwitch', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("DEPTHOVERLAYCOLOR_BIDS_LED", generals.LED_typeA,     {'groupOrder': 0, 'xPos': 2700, 'yPos': yPosPoint7, 'width':  600, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("DEPTHOVERLAYCOLOR_ASKS_LED", generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3400, 'yPos': yPosPoint7, 'width':  600, 'height': 250, 'style': 'styleA', 'mode': True})
            lineSelections = {'BIDS': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DEPTHOVERLAY_BIDS')},
                              'ASKS': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DEPTHOVERLAY_ASKS')}}
            ssp.GUIOs["DEPTHOVERLAYCOLOR_TARGETSELECTION"].setSelectionList(lineSelections, displayTargets = 'all')
            ssp.addGUIO("DEPTHOVERLAY_APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint7-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'DEPTHOVERLAY_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            #Aux Settings
            yPosPoint8 = yPosPoint7-700
            ssp.addGUIO("TITLE_AUX",                       generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos':  yPosPoint8,      'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_AUX'), 'fontSize': 80})
            ssp.addGUIO("AUX_KLINECOLORTYPE_TEXT",         generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos':  yPosPoint8- 350, 'width': 1750,                  'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:KLINECOLORTYPE'), 'fontSize': 80})
            ssp.addGUIO("AUX_KLINECOLORTYPE_SELECTIONBOX", generals.selectionBox_typeB,           {'groupOrder': 1, 'xPos': 1850, 'yPos':  yPosPoint8- 350, 'width': 2150,                  'height': 250, 'style': 'styleA', 'name': 'MAIN_KLINECOLORTYPE_SELECTION', 'nDisplay': 5, 'fontSize': 80, 'expansionDir': 1, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("AUX_TIMEZONE_TEXT",               generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos':  yPosPoint8- 700, 'width': 1750,                  'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TIMEZONE'), 'fontSize': 80})
            ssp.addGUIO("AUX_TIMEZONE_SELECTIONBOX",       generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1850, 'yPos':  yPosPoint8- 700, 'width': 2150,                  'height': 250, 'style': 'styleA', 'name': 'MAIN_TIMEZONE_SELECTION', 'nDisplay': 10, 'fontSize': 80, 'expansionDir': 1, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("AUX_SAVECONFIGURATION",           generals.button_typeA,                 {'groupOrder': 0, 'xPos': 0,    'yPos':  yPosPoint8-1050, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SAVECONFIG'), 'fontSize': 80, 'name': 'MAIN_SAVECONFIG', 'releaseFunction': self.__onSettingsContentUpdate})
            #GUIO Setup
            ssp.GUIOs["AUX_KLINECOLORTYPE_SELECTIONBOX"].setSelectionList({1: {'text': 'TYPE1'}, 2: {'text': 'TYPE2'}}, displayTargets = 'all')
            timeZoneSelections = {'LOCAL': {'text': 'LOCAL'}}
            for hour in range (24): timeZoneSelections[f'UTC+{hour:d}'] = {'text': f'UTC+{hour:d}'}
            ssp.GUIOs["AUX_TIMEZONE_SELECTIONBOX"].setSelectionList(timeZoneSelections, displayTargets = 'all')
        #<SMA & WMA & EMA Settings>
        if (True):
            for miType in ('SMA', 'WMA', 'EMA'):
                ssp = self.settingsSubPages[miType]
                ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack(f'GUIO_CHARTDRAWER:TITLE_MI_{miType}'), 'fontSize': 100})
                ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width':                   400, 'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
                ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
                ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
                ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': f'{miType}_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
                ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': f'{miType}_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
                for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                    ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                    ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'{miType}_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                    ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
                ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 800, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
                ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  900, 'yPos': 7550, 'width': 900, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
                ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1900, 'yPos': 7550, 'width': 750, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
                ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2750, 'yPos': 7550, 'width': 650, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
                ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",  generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
                maList = dict()
                for lineIndex in range (_NMAXLINES[miType]):
                    ssp.addGUIO(f"INDICATOR_{miType}{lineIndex}",               generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*lineIndex, 'width': 800, 'height': 250, 'style': 'styleB', 'name': f'{miType}_LineActivationSwitch_{lineIndex}', 'text': f'{miType} {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                    ssp.addGUIO(f"INDICATOR_{miType}{lineIndex}_INTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  900, 'yPos': 7200-350*lineIndex, 'width': 900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'{miType}_IntervalTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
                    ssp.addGUIO(f"INDICATOR_{miType}{lineIndex}_WIDTHINPUT",    generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1900, 'yPos': 7200-350*lineIndex, 'width': 750, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'{miType}_WidthTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
                    ssp.addGUIO(f"INDICATOR_{miType}{lineIndex}_LINECOLOR",     generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2750, 'yPos': 7200-350*lineIndex, 'width': 650, 'height': 250, 'style': 'styleA', 'mode': True})
                    ssp.addGUIO(f"INDICATOR_{miType}{lineIndex}_DISPLAY",       generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'{miType}_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
                    maList[f"{lineIndex}"] = {'text': f"{miType} {lineIndex}"}
                ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = maList, displayTargets = 'all')
                ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': 7200-350*(_NMAXLINES[miType]-1)-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': f'{miType}_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
        #<PSAR Settings>
        if (True):
            ssp = self.settingsSubPages['PSAR']
            ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MI_PSAR'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'PSAR_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'PSAR_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'PSAR_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",        generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),            'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORSTART_COLUMNTITLE",        generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  700, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:PSARSTART'),        'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORACCELERATION_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1300, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:PSARACCELERATION'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORMAXIMUM_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1900, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:PSARMAXIMUM'),      'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORSIZE_COLUMNTITLE",         generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2500, 'yPos': 7550, 'width': 400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SIZE'),             'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",        generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3000, 'yPos': 7550, 'width': 400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),            'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),          'fontSize': 90, 'anchor': 'SW'})
            psarList = dict()
            for lineIndex in range (_NMAXLINES['PSAR']):
                ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}",            generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*lineIndex, 'width': 600, 'height': 250, 'style': 'styleB', 'name': f'PSAR_LineActivationSwitch_{lineIndex}', 'text': f'PSAR {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}_AF0INPUT",   generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  700, 'yPos': 7200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'PSAR_AF0TextInputBox_{lineIndex}',   'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}_AF+INPUT",   generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1300, 'yPos': 7200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'PSAR_AF+TextInputBox_{lineIndex}',   'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}_AFMAXINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1900, 'yPos': 7200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'PSAR_AFMaxTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}_WIDTHINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2500, 'yPos': 7200-350*lineIndex, 'width': 400, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'PSAR_WidthTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}_LINECOLOR",  generals.LED_typeA,          {'groupOrder': 0, 'xPos': 3000, 'yPos': 7200-350*lineIndex, 'width': 400, 'height': 250, 'style': 'styleA', 'mode': True})
                ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}_DISPLAY",    generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'PSAR_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
                psarList[f"{lineIndex}"] = {'text': f"PSAR {lineIndex}"}
            yPosPoint0 = 7200-350*(_NMAXLINES['PSAR']-1)
            ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'PSAR_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = psarList, displayTargets = 'all')
        #<BOL Settings>
        if (True):
            ssp = self.settingsSubPages['BOL']
            ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MI_BOL'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'BOL_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'BOL_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'BOL_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ssp.addGUIO("INDICATOR_BLOCKTITLE_MATYPE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATOR_MATYPETEXT",        generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1550, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_MATYPESELECTION",   generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1650, 'yPos': 7200, 'width':                  2350, 'height': 250, 'style': 'styleA', 'name': 'BOL_MATypeSelection', 'nDisplay': 3, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            maTypes = {'SMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_SMA')},
                       'WMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_WMA')},
                       'EMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_EMA')}}
            ssp.GUIOs["INDICATOR_MATYPESELECTION"].setSelectionList(selectionList = maTypes, displayTargets = 'all')
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 800, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),         'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE",  generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  900, 'yPos': 6850, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVALSHORT'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORBANDWIDTH_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1600, 'yPos': 6850, 'width': 550, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BANDWIDTH'),     'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2250, 'yPos': 6850, 'width': 550, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),         'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2900, 'yPos': 6850, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),         'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",   generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6850, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),       'fontSize': 90, 'anchor': 'SW'})
            bolList = dict()
            for lineIndex in range (_NMAXLINES['BOL']):
                ssp.addGUIO(f"INDICATOR_BOL{lineIndex}",                generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6500-350*lineIndex, 'width': 800, 'height': 250, 'style': 'styleB', 'name': f'BOL_LineActivationSwitch_{lineIndex}', 'text': f'BOL {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_BOL{lineIndex}_INTERVALINPUT",  generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  900, 'yPos': 6500-350*lineIndex, 'width': 600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'BOL_IntervalTextInputBox_{lineIndex}',  'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_BOL{lineIndex}_BANDWIDTHINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1600, 'yPos': 6500-350*lineIndex, 'width': 550, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'BOL_BandWidthTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_BOL{lineIndex}_WIDTHINPUT",     generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2250, 'yPos': 6500-350*lineIndex, 'width': 550, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'BOL_WidthTextInputBox_{lineIndex}',     'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_BOL{lineIndex}_LINECOLOR",      generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2900, 'yPos': 6500-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'mode': True})
                ssp.addGUIO(f"INDICATOR_BOL{lineIndex}_DISPLAY",        generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'BOL_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
                bolList[f"{lineIndex}"] = {'text': f"BOL {lineIndex}"}
            yPosPoint0 = 6500-350*(_NMAXLINES['BOL']-1)
            ssp.addGUIO("INDICATOR_BLOCKTITLE_DISPLAYCONTENTS",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYCONTENTS'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATOR_DISPLAYCONTENTS_BOLCENTERTEXT",   generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 700, 'width':                  3400, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYBOLCENTER'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_DISPLAYCONTENTS_BOLCENTERSWITCH", generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint0- 700, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'BOL_DisplayContentsSwitch_BolCenter', 'releaseFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_DISPLAYCONTENTS_BOLBANDTEXT",     generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-1050, 'width':                  3400, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYBOLBAND'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_DISPLAYCONTENTS_BOLBANDSWITCH",   generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint0-1050, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'BOL_DisplayContentsSwitch_BolBand', 'releaseFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-1400, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'BOL_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = bolList, displayTargets = 'all')
        #<IVP Settings>
        if (True):
            ssp = self.settingsSubPages['IVP']
            ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MI_IVP'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width':                  1500, 'height': 250, 'style': 'styleA', 'name': 'IVP_LineSelectionBox', 'nDisplay': 9, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':                   950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':                   650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'IVP_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'IVP_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ivpLineTargets = {'VPLP':  {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLP')},
                              'VPLPB': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLPB')}}
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = ivpLineTargets, displayTargets = 'all')
            ssp.addGUIO("INDICATOR_BLOCKTITLE_IVPDISPLAY", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPDISPLAY'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATOR_VPLP_DISPLAYTEXT",             generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLPDISPLAY'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_VPLP_DISPLAYSWITCH",           generals.switch_typeB,  {'groupOrder': 0, 'xPos': 1900, 'yPos': 7200, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'IVP_DisplaySwitch_VPLP', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_VPLP_COLORTEXT",               generals.textBox_typeA, {'groupOrder': 0, 'xPos': 2500, 'yPos': 7200, 'width':  700, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_VPLP_COLOR",                   generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3300, 'yPos': 7200, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_VPLP_DISPLAYWIDTHTEXT",        generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYWIDTH'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_VPLP_DISPLAYWIDTHSLIDER",      generals.slider_typeA,  {'groupOrder': 0, 'xPos': 1300, 'yPos': 6900, 'width': 2000, 'height': 150, 'style': 'styleA', 'name': 'IVP_DisplayWidthSlider_VPLP', 'valueUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_VPLP_DISPLAYWIDTHVALUETEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3400, 'yPos': 6850, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            ssp.addGUIO("INDICATOR_VPLPB_DISPLAYTEXT",            generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 6500, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLPBDISPLAY'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_VPLPB_DISPLAYSWITCH",          generals.switch_typeB,  {'groupOrder': 0, 'xPos': 1900, 'yPos': 6500, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'IVP_DisplaySwitch_VPLPB', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_VPLPB_COLORTEXT",              generals.textBox_typeA, {'groupOrder': 0, 'xPos': 2500, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_VPLPB_COLOR",                  generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3300, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_VPLPB_DISPLAYREGIONTEXT",      generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 6150, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYREGION'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_VPLPB_DISPLAYREGIONSLIDER",    generals.slider_typeA,  {'groupOrder': 0, 'xPos': 1400, 'yPos': 6200, 'width': 1800, 'height': 150, 'style': 'styleA', 'name': 'IVP_VPLPBDisplayRegion', 'valueUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_VPLPB_DISPLAYREGIONVALUETEXT", generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 6150, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            ssp.addGUIO("INDICATOR_BLOCKTITLE_IVPPARAMS", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': 5800, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPPARAMS'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATOR_INTERVAL_DISPLAYTEXT",    generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 5450, 'width': 1900, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_INTERVAL_INPUTTEXT",      generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2000, 'yPos': 5450, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'IVP_Interval', 'textUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_GAMMAFACTOR_DISPLAYTEXT", generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 5100, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPGAMMAFACTOR'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_GAMMAFACTOR_SLIDER",      generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1100, 'yPos': 5150, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_GammaFactor', 'valueUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_GAMMAFACTOR_VALUETEXT",   generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': 5100, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            ssp.addGUIO("INDICATOR_DELTAFACTOR_DISPLAYTEXT", generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 4750, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPDELTAFACTOR'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_DELTAFACTOR_SLIDER",      generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1100, 'yPos': 4800, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_DeltaFactor', 'valueUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_DELTAFACTOR_VALUETEXT",   generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': 4750, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': 4400, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'IVP_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
        #<SWING Settings>
        if (True):
            ssp = self.settingsSubPages['SWING']
            ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MI_SWING'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'SWING_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'SWING_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'SWING_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),      'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORSWINGRANGE_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 7550, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SWINGRANGE'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2300, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),      'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2900, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),      'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),    'fontSize': 90, 'anchor': 'SW'})
            swingList = dict()
            for lineIndex in range (_NMAXLINES['SWING']):
                ssp.addGUIO(f"INDICATOR_SWING{lineIndex}",                 generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'SWING_LineActivationSwitch_{lineIndex}', 'text': f'SWING {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': 7200-350*lineIndex, 'width': 1100, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'SWING_SwingRangeTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_SWING{lineIndex}_WIDTHINPUT",      generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2300, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'SWING_WidthTextInputBox_{lineIndex}', 'text': "", 'fontSize': 80, 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_SWING{lineIndex}_LINECOLOR",       generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2900, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'mode': True})
                ssp.addGUIO(f"INDICATOR_SWING{lineIndex}_DISPLAY",         generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'SWING_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
                swingList[f"{lineIndex}"] = {'text': f"SWING {lineIndex}"}
            yPosPoint0 = 7200-350*(_NMAXLINES['SWING']-1)
            ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'SWING_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = swingList, displayTargets = 'all')
        #<VOL Settings>
        if (True):
            ssp = self.settingsSubPages['VOL']
            ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_VOL'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'VOL_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'VOL_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'VOL_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ssp.addGUIO("INDICATORINDEX_BLOCKTITLE_MA",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLSETTINGS'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATOR_VOLTYPETEXT",      generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_VOLTYPESELECTION", generals.selectionBox_typeB, {'groupOrder': 2, 'xPos': 1900, 'yPos': 7200, 'width': 2100, 'height': 250, 'style': 'styleA', 'name': 'VOL_VolTypeSelection', 'nDisplay': 4, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            volTypes = {'BASE':    {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE_BASE')},
                        'QUOTE':   {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE_QUOTE')},
                        'BASETB':  {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE_BASETB')},
                        'QUOTETB': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE_QUOTETB')}}
            ssp.GUIOs["INDICATOR_VOLTYPESELECTION"].setSelectionList(selectionList = volTypes, displayTargets = 'all')
            ssp.addGUIO("INDICATOR_MATYPETEXT",       generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_MATYPESELECTION",  generals.selectionBox_typeB, {'groupOrder': 2, 'xPos': 1900, 'yPos': 6850, 'width': 2100, 'height': 250, 'style': 'styleA', 'name': 'VOL_MATypeSelection', 'nDisplay': 3, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            maTypes = {'SMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_SMA')},
                       'WMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_WMA')},
                       'EMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_EMA')}}
            ssp.GUIOs["INDICATOR_MATYPESELECTION"].setSelectionList(selectionList = maTypes, displayTargets = 'all')
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6500, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE",  generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1900, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2700, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",   generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
            volMAList = dict()
            for lineIndex in range (_NMAXLINES['VOL']):
                ssp.addGUIO(f"INDICATOR_VOL{lineIndex}",               generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6150-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'VOL_LineActivationSwitch_{lineIndex}', 'text': f'VOLMA {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_VOL{lineIndex}_INTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6150-350*lineIndex, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'VOL_IntervalTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_VOL{lineIndex}_WIDTHINPUT",    generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1900, 'yPos': 6150-350*lineIndex, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'VOL_WidthTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_VOL{lineIndex}_LINECOLOR",     generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2700, 'yPos': 6150-350*lineIndex, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
                ssp.addGUIO(f"INDICATOR_VOL{lineIndex}_DISPLAY",       generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6150-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'VOL_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
                volMAList[f"{lineIndex}"] = {'text': f"VOLMA {lineIndex}"}
            yPosPoint0 = 6150-350*(_NMAXLINES['VOL']-1)
            ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'VOL_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = volMAList, displayTargets = 'all')
        #<DEPTH Settings>
        if (True):
            ssp = self.settingsSubPages['DEPTH']
            ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_DEPTH'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'DEPTH_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'DEPTH_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'DEPTH_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ssp.addGUIO("INDICATOR_BIDS_TEXT",  generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 1150, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DEPTH_BIDS'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_BIDS_LINECOLOR", generals.LED_typeA, {'groupOrder': 0, 'xPos': 1250, 'yPos': 7550, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_ASKS_TEXT",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 2050, 'yPos': 7550, 'width': 1150, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DEPTH_ASKS'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_ASKS_LINECOLOR", generals.LED_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 7550, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
            depthLines = {'BIDS': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DEPTH_BIDS')},
                          'ASKS': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DEPTH_ASKS')}}
            ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': 7200, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'DEPTH_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = depthLines, displayTargets = 'all')
        #<AGGTRADE Settings>
        if (True):
            ssp = self.settingsSubPages['AGGTRADE']
            ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_AGGTRADE'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'AGGTRADE_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'AGGTRADE_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'AGGTRADE_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ssp.addGUIO("INDICATOR_DISPLAYTYPETEXT",       generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 1950, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYTYPE'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_DISPLAYTYPESELECTION",  generals.selectionBox_typeB, {'groupOrder': 2, 'xPos': 2050, 'yPos': 7550, 'width': 1950, 'height': 250, 'style': 'styleA', 'name': 'AGGTRADE_DisplayTypeSelection', 'nDisplay': 3, 'expansionDir': 1, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            displayTypes = {'QUANTITY': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:ATTYPE_QUANTITY')},
                            'NTRADES':  {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:ATTYPE_NTRADES')},
                            'NOTIONAL': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:ATTYPE_NOTIONAL')}}
            ssp.GUIOs["INDICATOR_DISPLAYTYPESELECTION"].setSelectionList(selectionList = displayTypes, displayTargets = 'all')
            ssp.addGUIO("INDICATOR_BUY_TEXT",  generals.textBox_typeA,  {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width': 1150, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:AGGTRADE_BUY'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_BUY_LINECOLOR", generals.LED_typeA,  {'groupOrder': 0, 'xPos': 1250, 'yPos': 7200, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_SELL_TEXT",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 2050, 'yPos': 7200, 'width': 1150, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:AGGTRADE_SELL'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_SELL_LINECOLOR", generals.LED_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 7200, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
            atLines = {'BUY':  {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:AGGTRADE_BUY')},
                       'SELL': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:AGGTRADE_SELL')}}
            ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': 6850, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'AGGTRADE_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = atLines, displayTargets = 'all')
        #<NNA Settings>
        if (True):
            ssp = self.settingsSubPages['NNA']
            ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_NNA'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'NNA_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'NNA_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'NNA_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",   generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),             'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORNNCODE_COLUMNTITLE",  generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  700, 'yPos': 7550, 'width':  900, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:NEURALNETWORKCODE'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORALPHA_COLUMNTITLE",   generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1700, 'yPos': 7550, 'width':  400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:ALPHA'),             'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORBETA_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2200, 'yPos': 7550, 'width':  300, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BETA'),              'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORSIZE_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2600, 'yPos': 7550, 'width':  300, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SIZE'),              'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",   generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3000, 'yPos': 7550, 'width':  400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),             'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),           'fontSize': 90, 'anchor': 'SW'})
            nnaList = dict()
            for lineIndex in range (_NMAXLINES['NNA']):
                ssp.addGUIO(f"INDICATOR_NNA{lineIndex}",             generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleB', 'name': f'NNA_LineActivationSwitch_{lineIndex}', 'text': f'NNA {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_NNCODEINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  700, 'yPos': 7200-350*lineIndex, 'width':  900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_NNCodeTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_ALPHAINPUT",  generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1700, 'yPos': 7200-350*lineIndex, 'width':  400, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_AlphaTextInputBox_{lineIndex}',  'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_BETAINPUT",   generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2200, 'yPos': 7200-350*lineIndex, 'width':  300, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_BetaTextInputBox_{lineIndex}',   'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_WIDTHINPUT",  generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2600, 'yPos': 7200-350*lineIndex, 'width':  300, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_WidthTextInputBox_{lineIndex}',  'textUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_LINECOLOR",   generals.LED_typeA,          {'groupOrder': 0, 'xPos': 3000, 'yPos': 7200-350*lineIndex, 'width':  400, 'height': 250, 'style': 'styleA', 'mode': True})
                ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_DISPLAY",     generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'NNA_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
                nnaList[f"{lineIndex}"] = {'text': f"NNA {lineIndex}"}
            yPosPoint0 = 7200-350*(_NMAXLINES['NNA']-1)
            ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'NNA_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = nnaList, displayTargets = 'all')
        #<MMACD Settings>
        if (True):
            ssp = self.settingsSubPages['MMACD']
            ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_MMACD'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':                   550, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width':                  1500, 'height': 250, 'style': 'styleA', 'name': 'MMACD_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':                   950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':                   650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'MMACD_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'MMACD_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            mmacdLineTargets = {'MMACD':      {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDMMACD')},
                                'SIGNAL':     {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNAL')},
                                'HISTOGRAM+': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAM+')},
                                'HISTOGRAM-': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAM-')}}
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = mmacdLineTargets, displayTargets = 'all')
            ssp.addGUIO("INDICATOR_BLOCKTITLE_DISPLAY",        generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDDISPLAY'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATOR_MMACD_DISPLAYTEXT",         generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDMMACDDISPLAY'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_MMACD_DISPLAYSWITCH",       generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 1600, 'yPos': 7200, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACD_DisplaySwitch_MMACD', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_MMACD_COLORTEXT",           generals.textBox_typeA,                {'groupOrder': 0, 'xPos': 2200, 'yPos': 7200, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_MMACD_COLOR",               generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2900, 'yPos': 7200, 'width':                  1100, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_SIGNAL_DISPLAYTEXT",        generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNALDISPLAY'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_SIGNAL_DISPLAYSWITCH",      generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 1600, 'yPos': 6850, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACD_DisplaySwitch_SIGNAL', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_SIGNAL_COLORTEXT",          generals.textBox_typeA,                {'groupOrder': 0, 'xPos': 2200, 'yPos': 6850, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_SIGNAL_COLOR",              generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2900, 'yPos': 6850, 'width':                  1100, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_HISTOGRAM_DISPLAYTEXT",     generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 6500, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAMDISPLAY'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_HISTOGRAM_DISPLAYSWITCH",   generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 1600, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACD_DisplaySwitch_HISTOGRAM', 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATOR_HISTOGRAM_COLORTEXT",       generals.textBox_typeA,                {'groupOrder': 0, 'xPos': 2200, 'yPos': 6500, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_HISTOGRAM+_COLOR",          generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2900, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_HISTOGRAM-_COLOR",          generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATOR_HISTOGRAMTYPE_DISPLAYTEXT", generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 6150, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAMTYPE'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_HISTOGRAMTYPE_SELECTION",   generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1600, 'yPos': 6150, 'width':                  2400, 'height': 250, 'style': 'styleA', 'name': 'MMACD_HistrogramTypeSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            histogramTypes = {'MSDELTA':          {'text': 'MSDELTA'},
                              'MSDELTA_ABSMA':    {'text': 'MSDELTA_ABSMA'},
                              'MSDELTA_ABSMAREL': {'text': 'MSDELTA_ABSMAREL'}}
            ssp.GUIOs["INDICATOR_HISTOGRAMTYPE_SELECTION"].setSelectionList(selectionList = histogramTypes, displayTargets = 'all')
            ssp.addGUIO("INDICATOR_BLOCKTITLE_MMACDSETTINGS",   generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 5800, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSETTINGS'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATOR_SIGNALINTERVALTEXT",         generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 5450, 'width':                  3000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNALINTERVAL'), 'fontSize': 80})
            ssp.addGUIO("INDICATOR_SIGNALINTERVALTEXTINPUT",    generals.textInputBox_typeA,           {'groupOrder': 0, 'xPos': 3100, 'yPos': 5450, 'width':                   900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MMACD_SignalIntervalTextInputBox', 'textUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE1",          generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 5100, 'width':                  1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE1",       generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 5100, 'width':                   850, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE2",          generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2050, 'yPos': 5100, 'width':                  1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE2",       generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3150, 'yPos': 5100, 'width':                   850, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            for lineIndex in range (_NMAXLINES['MMACD']):
                rowNumber = math.ceil((lineIndex+1)/2)
                if (lineIndex%2 == 0): coordX = 0
                else:                  coordX = 2050
                ssp.addGUIO(f"INDICATOR_MMACDMA{lineIndex}",               generals.switch_typeC,       {'groupOrder': 0, 'xPos': coordX,      'yPos': 5100-rowNumber*350, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'MMACD_LineActivationSwitch_{lineIndex}', 'text': f'MA {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': coordX+1100, 'yPos': 5100-rowNumber*350, 'width':  850, 'height': 250, 'style': 'styleA', 'name': f'MMACD_IntervalTextInputBox_{lineIndex}', 'text': "",                'fontSize': 80, 'textUpdateFunction': self.__onSettingsContentUpdate})
            yPosPoint0 = 5100-math.ceil(_NMAXLINES['MMACD']/2)*350
            ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'MMACD_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
        #<DMIxADX Settings>
        if (True):
            ssp = self.settingsSubPages['DMIxADX']
            ssp.addGUIO("SUBPAGETITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_DMIxADX'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",        generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'DMIxADX_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'DMIxADX_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'DMIxADX_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 1200, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1300, 'yPos': 7550, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2000, 'yPos': 7550, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2700, 'yPos': 7550, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",  generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
            dmixadxList = dict()
            for lineIndex in range (_NMAXLINES['DMIxADX']):
                ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}",               generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*lineIndex, 'width': 1200, 'height': 250, 'style': 'styleB', 'name': f'DMIxADX_LineActivationSwitch_{lineIndex}', 'text': f'DMIxADX {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1300, 'yPos': 7200-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'name': f'DMIxADX_IntervalTextInputBox_{lineIndex}', 'text': "",                     'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT",    generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2000, 'yPos': 7200-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'name': f'DMIxADX_WidthTextInputBox_{lineIndex}',    'text': "",                     'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}_LINECOLOR",     generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2700, 'yPos': 7200-350*lineIndex, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
                ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}_DISPLAY",       generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'DMIxADX_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
                dmixadxList[f"{lineIndex}"] = {'text': f"DMIxADX {lineIndex}"}
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = dmixadxList, displayTargets = 'all')
            yPosPoint0 = 7200-350*(_NMAXLINES['DMIxADX']-1)
            ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'DMIxADX_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
        #<MFI Settings>
        if (True):
            ssp = self.settingsSubPages['MFI']
            ssp.addGUIO("SUBPAGETITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_MFI'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",        generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'MFI_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'MFI_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'MFI_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 7550, 'width':  800, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2000, 'yPos': 7550, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2700, 'yPos': 7550, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",  generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
            mfiList = dict()
            for lineIndex in range (_NMAXLINES['MFI']):
                ssp.addGUIO(f"INDICATOR_MFI{lineIndex}",               generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'MFI_LineActivationSwitch_{lineIndex}', 'text': f'MFI {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_MFI{lineIndex}_INTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': 7200-350*lineIndex, 'width':  800, 'height': 250, 'style': 'styleA', 'name': f'MFI_IntervalTextInputBox_{lineIndex}', 'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_MFI{lineIndex}_WIDTHINPUT",    generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2000, 'yPos': 7200-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'name': f'MFI_WidthTextInputBox_{lineIndex}',    'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_MFI{lineIndex}_LINECOLOR",     generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2700, 'yPos': 7200-350*lineIndex, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
                ssp.addGUIO(f"INDICATOR_MFI{lineIndex}_DISPLAY",       generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'MFI_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
                mfiList[f"{lineIndex}"] = {'text': f"MFI {lineIndex}"}
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = mfiList, displayTargets = 'all')
            yPosPoint0 = 7200-350*(_NMAXLINES['MFI']-1)
            ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'MFI_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
        #<TPD Settings>
        if (True):
            ssp = self.settingsSubPages['TPD']
            ssp.addGUIO("SUBPAGETITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_TPD'), 'fontSize': 100})
            ssp.addGUIO("NAGBUTTON",        generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
            ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'TPD_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'TPD_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'TPD_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),         'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORVIEWLENGTH_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  700, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VIEWLENGTH'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE",   generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1300, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVALSHORT'), 'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORMAINTERVAL_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1900, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MAINTERVAL'),    'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2500, 'yPos': 7550, 'width': 400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),         'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3000, 'yPos': 7550, 'width': 400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),         'fontSize': 90, 'anchor': 'SW'})
            ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),       'fontSize': 90, 'anchor': 'SW'})
            tpdList = dict()
            for lineIndex in range (_NMAXLINES['TPD']):
                ssp.addGUIO(f"INDICATOR_TPD{lineIndex}",                 generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*lineIndex, 'width': 600, 'height': 250, 'style': 'styleB', 'name': f'TPD_LineActivationSwitch_{lineIndex}',   'text': f'TPD {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  700, 'yPos': 7200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'TPD_ViewLengthTextInputBox_{lineIndex}', 'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_TPD{lineIndex}_INTERVALINPUT",   generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1300, 'yPos': 7200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'TPD_IntervalTextInputBox_{lineIndex}',   'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1900, 'yPos': 7200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'TPD_MAIntervalTextInputBox_{lineIndex}', 'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_TPD{lineIndex}_WIDTHINPUT",      generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2500, 'yPos': 7200-350*lineIndex, 'width': 400, 'height': 250, 'style': 'styleA', 'name': f'TPD_WidthTextInputBox_{lineIndex}',      'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
                ssp.addGUIO(f"INDICATOR_TPD{lineIndex}_LINECOLOR",       generals.LED_typeA,          {'groupOrder': 0, 'xPos': 3000, 'yPos': 7200-350*lineIndex, 'width': 400, 'height': 250, 'style': 'styleA', 'mode': True})
                ssp.addGUIO(f"INDICATOR_TPD{lineIndex}_DISPLAY",         generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'TPD_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
                tpdList[f"{lineIndex}"] = {'text': f"TPD {lineIndex}"}
            ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = tpdList, displayTargets = 'all')
            yPosPoint0 = 7200-350*(_NMAXLINES['TPD']-1)
            ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'TPD_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})

    def __matchGUIOsToConfig(self):
        #<MAIN>
        if (True):
            oc   = self.objectConfig
            cgt  = self.currentGUITheme
            ssps = self.settingsSubPages
            guios_MAIN     = ssps['MAIN'].GUIOs
            guios_SMA      = ssps['SMA'].GUIOs
            guios_WMA      = ssps['WMA'].GUIOs
            guios_EMA      = ssps['EMA'].GUIOs
            guios_PSAR     = ssps['PSAR'].GUIOs
            guios_BOL      = ssps['BOL'].GUIOs
            guios_IVP      = ssps['IVP'].GUIOs
            guios_SWING    = ssps['SWING'].GUIOs
            guios_VOL      = ssps['VOL'].GUIOs
            guios_DEPTH    = ssps['DEPTH'].GUIOs
            guios_AGGTRADE = ssps['AGGTRADE'].GUIOs
            guios_NNA      = ssps['NNA'].GUIOs
            guios_MMACD    = ssps['MMACD'].GUIOs
            guios_DMIxADX  = ssps['DMIxADX'].GUIOs
            guios_MFI      = ssps['MFI'].GUIOs
            guios_TPD      = ssps['TPD'].GUIOs
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
            guios_MAIN["DEPTHOVERLAYDISPLAY_SWITCH"].setStatus(oc['DEPTHOVERLAY_Display'], callStatusUpdateFunction = False)
            guios_MAIN["DEPTHOVERLAYCOLOR_BIDS_LED"].updateColor(oc[f'DEPTHOVERLAY_BIDS_ColorR%{cgt}'], 
                                                                 oc[f'DEPTHOVERLAY_BIDS_ColorG%{cgt}'], 
                                                                 oc[f'DEPTHOVERLAY_BIDS_ColorB%{cgt}'], 
                                                                 oc[f'DEPTHOVERLAY_BIDS_ColorA%{cgt}'])
            guios_MAIN["DEPTHOVERLAYCOLOR_ASKS_LED"].updateColor(oc[f'DEPTHOVERLAY_ASKS_ColorR%{cgt}'], 
                                                                 oc[f'DEPTHOVERLAY_ASKS_ColorG%{cgt}'], 
                                                                 oc[f'DEPTHOVERLAY_ASKS_ColorB%{cgt}'], 
                                                                 oc[f'DEPTHOVERLAY_ASKS_ColorA%{cgt}'])
            guios_MAIN["DEPTHOVERLAYCOLOR_TARGETSELECTION"].setSelected('BIDS', callSelectionUpdateFunction = True)
            guios_MAIN["DEPTHOVERLAY_APPLYNEWSETTINGS"].deactivate()
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
            guios_IVP["INDICATOR_GAMMAFACTOR_SLIDER"].setSliderValue(newValue = (gammaFactor-0.005)*(100/0.095), callValueUpdateFunction = False)
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
        #<DEPTH>
        if (True):
            guios_MAIN["SUBINDICATOR_DEPTH"].setStatus(oc['DEPTH_Master'], callStatusUpdateFunction = False)
            guios_DEPTH["INDICATOR_BIDS_LINECOLOR"].updateColor(oc[f'DEPTH_BIDS_ColorR%{cgt}'], 
                                                                oc[f'DEPTH_BIDS_ColorG%{cgt}'], 
                                                                oc[f'DEPTH_BIDS_ColorB%{cgt}'], 
                                                                oc[f'DEPTH_BIDS_ColorA%{cgt}'])
            guios_DEPTH["INDICATOR_ASKS_LINECOLOR"].updateColor(oc[f'DEPTH_ASKS_ColorR%{cgt}'], 
                                                                oc[f'DEPTH_ASKS_ColorG%{cgt}'], 
                                                                oc[f'DEPTH_ASKS_ColorB%{cgt}'], 
                                                                oc[f'DEPTH_ASKS_ColorA%{cgt}'])
            guios_DEPTH["INDICATORCOLOR_TARGETSELECTION"].setSelected('BIDS')
            guios_DEPTH["APPLYNEWSETTINGS"].deactivate()
        #<AGGTRADE>
        if (True):
            guios_MAIN["SUBINDICATOR_AGGTRADE"].setStatus(oc['AGGTRADE_Master'], callStatusUpdateFunction = False)
            guios_AGGTRADE["INDICATOR_BUY_LINECOLOR"].updateColor(oc[f'AGGTRADE_BUY_ColorR%{cgt}'], 
                                                                  oc[f'AGGTRADE_BUY_ColorG%{cgt}'], 
                                                                  oc[f'AGGTRADE_BUY_ColorB%{cgt}'], 
                                                                  oc[f'AGGTRADE_BUY_ColorA%{cgt}'])
            guios_AGGTRADE["INDICATOR_SELL_LINECOLOR"].updateColor(oc[f'AGGTRADE_SELL_ColorR%{cgt}'], 
                                                                   oc[f'AGGTRADE_SELL_ColorG%{cgt}'], 
                                                                   oc[f'AGGTRADE_SELL_ColorB%{cgt}'], 
                                                                   oc[f'AGGTRADE_SELL_ColorA%{cgt}'])
            guios_AGGTRADE["INDICATOR_DISPLAYTYPESELECTION"].setSelected(oc['AGGTRADE_DisplayType'], callSelectionUpdateFunction = False)
            guios_AGGTRADE["INDICATORCOLOR_TARGETSELECTION"].setSelected('BUY')
            guios_AGGTRADE["APPLYNEWSETTINGS"].deactivate()
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
        #<MMACD>
        if (True):
            guios_MAIN["SUBINDICATOR_MMACD"].setStatus(oc['MMACD_Master'], callStatusUpdateFunction = False)
            guios_MMACD["INDICATOR_MMACD_DISPLAYSWITCH"].setStatus(oc['MMACD_MMACD_Display'], callStatusUpdateFunction = False)
            guios_MMACD["INDICATOR_SIGNAL_DISPLAYSWITCH"].setStatus(oc['MMACD_SIGNAL_Display'], callStatusUpdateFunction = False)
            guios_MMACD["INDICATOR_HISTOGRAM_DISPLAYSWITCH"].setStatus(oc['MMACD_HISTOGRAM_Display'], callStatusUpdateFunction = False)
            guios_MMACD["INDICATOR_MMACD_COLOR"].updateColor(oc[f'MMACD_MMACD_ColorR%{cgt}'], 
                                                                 oc[f'MMACD_MMACD_ColorG%{cgt}'], 
                                                                 oc[f'MMACD_MMACD_ColorB%{cgt}'], 
                                                                 oc[f'MMACD_MMACD_ColorA%{cgt}'])
            guios_MMACD["INDICATOR_SIGNAL_COLOR"].updateColor(oc[f'MMACD_SIGNAL_ColorR%{cgt}'], 
                                                                  oc[f'MMACD_SIGNAL_ColorG%{cgt}'], 
                                                                  oc[f'MMACD_SIGNAL_ColorB%{cgt}'], 
                                                                  oc[f'MMACD_SIGNAL_ColorA%{cgt}'])
            guios_MMACD["INDICATOR_HISTOGRAM+_COLOR"].updateColor(oc[f'MMACD_HISTOGRAM+_ColorR%{cgt}'], 
                                                                      oc[f'MMACD_HISTOGRAM+_ColorG%{cgt}'], 
                                                                      oc[f'MMACD_HISTOGRAM+_ColorB%{cgt}'], 
                                                                      oc[f'MMACD_HISTOGRAM+_ColorA%{cgt}'])
            guios_MMACD["INDICATOR_HISTOGRAM-_COLOR"].updateColor(oc[f'MMACD_HISTOGRAM-_ColorR%{cgt}'], 
                                                                      oc[f'MMACD_HISTOGRAM-_ColorG%{cgt}'], 
                                                                      oc[f'MMACD_HISTOGRAM-_ColorB%{cgt}'], 
                                                                      oc[f'MMACD_HISTOGRAM-_ColorA%{cgt}'])
            guios_MMACD["INDICATOR_HISTOGRAMTYPE_SELECTION"].setSelected(itemKey = oc['MMACD_HISTOGRAM_Type'], callSelectionUpdateFunction = False)
            signalNSamples = oc['MMACD_SignalNSamples']
            guios_MMACD["INDICATOR_SIGNALINTERVALTEXTINPUT"].updateText(text = f"{signalNSamples}")
            for lineIndex in range (_NMAXLINES['MMACD']):
                lineActive = oc[f'MMACD_MA{lineIndex}_LineActive']
                nSamples   = oc[f'MMACD_MA{lineIndex}_NSamples']
                guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
                guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
            guios_MMACD["INDICATORCOLOR_TARGETSELECTION"].setSelected('MMACD')
            guios_MMACD["APPLYNEWSETTINGS"].deactivate()
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
            #<MFI>
        #<TPD>
        if (True):
            guios_MAIN["SUBINDICATOR_TPD"].setStatus(oc['TPD_Master'], callStatusUpdateFunction = False)
            for lineIndex in range (_NMAXLINES['TPD']):
                lineActive = oc[f'TPD_{lineIndex}_LineActive']
                viewLength = oc[f'TPD_{lineIndex}_ViewLength']
                nSamples   = oc[f'TPD_{lineIndex}_NSamples']
                nSamplesMA = oc[f'TPD_{lineIndex}_NSamplesMA']
                width      = oc[f'TPD_{lineIndex}_Width']
                color      = (oc[f'TPD_{lineIndex}_ColorR%{cgt}'],
                              oc[f'TPD_{lineIndex}_ColorG%{cgt}'],
                              oc[f'TPD_{lineIndex}_ColorB%{cgt}'],
                              oc[f'TPD_{lineIndex}_ColorA%{cgt}'])
                display    = oc[f'TPD_{lineIndex}_Display']
                guios_TPD[f"INDICATOR_TPD{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
                guios_TPD[f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT"].updateText(text = f"{viewLength}")
                guios_TPD[f"INDICATOR_TPD{lineIndex}_INTERVALINPUT"].updateText(text   = f"{nSamples}")
                guios_TPD[f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT"].updateText(text = f"{nSamplesMA}")
                guios_TPD[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
                guios_TPD[f"INDICATOR_TPD{lineIndex}_LINECOLOR"].updateColor(*color)
                guios_TPD[f"INDICATOR_TPD{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
            guios_TPD["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
            guios_TPD["APPLYNEWSETTINGS"].deactivate()

        #Set SubIndicator Switch Activation
        for sivIdx in range (len(_SITYPES)):
            if sivIdx < self.usableSIViewers: 
                guios_MAIN[f"SUBINDICATOR_DISPLAYSWITCH{sivIdx}"].activate()
            else:
                guios_MAIN[f"SUBINDICATOR_DISPLAYSWITCH{sivIdx}"].setStatus(False)
                guios_MAIN[f"SUBINDICATOR_DISPLAYSWITCH{sivIdx}"].deactivate()

        #Final 'AUX_SAVECONFIGURATION' Deactivation
        guios_MAIN["AUX_SAVECONFIGURATION"].deactivate()
    #Object Configuration & GUIO Initialization END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Processings -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def process(self, t_elapsed_ns):
        mei_beg = time.perf_counter_ns()
        self.__process_SubPages(t_elapsed_ns)                                                            #[1]: Subpage Processing
        self.__process_MouseEventInterpretation()                                                        #[2]: Mouse Event Interpretation
        self.__process_PosHighlightUpdate(mei_beg)                                                       #[3]: PosHighlight Update
        waitPostDrag   = (mei_beg-self.mouse_lastDragged_ns  <= _TIMEINTERVAL_POSTDRAGWAITTIME)
        waitPostScroll = (mei_beg-self.mouse_lastScrolled_ns <= _TIMEINTERVAL_POSTSCROLLWAITTIME)
        if not waitPostDrag and not waitPostScroll: processNext = not(self._process_typeUnique(mei_beg)) #[4]: Process Analysis
        else:                                       processNext = True
        if processNext: processNext = not(self.__process_drawQueues(mei_beg))                            #[5]: Draw Queues Processing
        if processNext: processNext = not(self.__process_RCLCGs(mei_beg))                                #[6]: RCLCGs Processing
        if processNext: self.__process_drawRemovalQueues(mei_beg)                                        #[7]: Draw Removal Queues Processing
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
        if any(self.posHighlight_updatedPositions) and (_TIMEINTERVAL_POSHIGHLIGHTUPDATE <= mei_beg - self.posHighlight_lastUpdated_ns): 
            self.__onPosHighlightUpdate()

    def _process_typeUnique(self, mei_beg):
        return False

    def __process_drawQueues(self, mei_beg):
        #[1]: Instances
        dQueue   = self.__drawQueue
        func_sds = self.__drawer_sendDrawSignals

        #[2]: Draw Loop
        while time.perf_counter_ns()-mei_beg < _TIMELIMIT_KLINESDRAWQUEUE_NS:
            if not dQueue:
                return False
            ts, aCodes = next(iter(dQueue.items()))
            for aCode in aCodes:
                func_sds(timestamp = ts, analysisCode = aCode)
            del dQueue[ts]
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
            if   self.__drawRemovalQueue: self._drawer_RemoveExpiredDrawings(self.__drawRemovalQueue.pop())
            else: break
    #Processings END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #User Interaction Control ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def handleMouseEvent(self, event):
        #[1]: Status Check
        _handleEvent = (not self.__loading)
        if not _handleEvent:
            self.mouse_Event_lastRead = event
            return

        #[2]: Instances
        eType        = event['eType']
        lastHovered  = self.mouse_lastHoveredSection
        lastSelected = self.mouse_lastSelectedSection
        ssps         = self.settingsSubPages
        ssp_current  = self.settingsSubPage_Current
        auxBarPage   = self.auxBarPage
        ex, ey       = event['x'], event['y']

        #[3]: Event Handling
        #---[3-1]: MOVED
        if eType == "MOVED":
            #Find hovering section
            hoveredSection = None
            if   self.settingsSubPage_Opened and ssps[ssp_current].isTouched(ex, ey): hoveredSection = 'SETTINGSSUBPAGE'
            elif auxBarPage.isTouched(ex, ey):                                        hoveredSection = 'AUXILLARYBAR'
            else:
                for dBoxName in self.hitBox:
                    if self.hitBox[dBoxName].isTouched(ex, ey): hoveredSection = dBoxName; break

            #Hovering Section Has Not Changed
            if hoveredSection == lastHovered:
                if   hoveredSection == 'SETTINGSSUBPAGE': ssps[ssp_current].handleMouseEvent(event)
                elif hoveredSection == 'AUXILLARYBAR':    auxBarPage.handleMouseEvent(event)

            #Hovering Section Changed
            else:
                #New Hovered Section
                if   hoveredSection == 'SETTINGSBUTTONFRAME':
                    self.frameSprites['SETTINGSBUTTONFRAME'].image = self.images['SETTINGSBUTTONFRAME_HOVERED'][0]
                    self.settingsButtonStatus = 'HOVERED'
                elif hoveredSection == 'SETTINGSSUBPAGE': ssps[ssp_current].handleMouseEvent({'eType': "HOVERENTERED", 'x': ex, 'y': ey})
                elif hoveredSection == 'AUXILLARYBAR':    auxBarPage.handleMouseEvent({'eType': "HOVERENTERED", 'x': ex, 'y': ey})
                elif hoveredSection is None:              self.__updatePosHighlight(ex, ey, None, updateType = 1)
                #Last Hovered Section
                if   lastHovered == 'SETTINGSBUTTONFRAME':
                    self.frameSprites['SETTINGSBUTTONFRAME'].image = self.images['SETTINGSBUTTONFRAME_DEFAULT'][0]
                    self.settingsButtonStatus = 'DEFAULT'
                elif lastHovered == 'SETTINGSSUBPAGE': ssps[ssp_current].handleMouseEvent({'eType': "HOVERESCAPED", 'x': ex, 'y': ey})
                elif lastHovered == 'AUXILLARYBAR':    auxBarPage.handleMouseEvent({'eType': "HOVERESCAPED", 'x': ex, 'y': ey})

            #POSHIGHLIGHT Control
            if hoveredSection and (hoveredSection == 'KLINESPRICE' or hoveredSection[:8] == 'SIVIEWER'):
                self.__updatePosHighlight(ex, ey, hoveredSection, updateType = 0)
            self.mouse_lastHoveredSection = hoveredSection

        #---[3-2]: PRESSED
        elif eType == "PRESSED":
            if lastHovered != lastSelected:
                if   lastSelected == 'SETTINGSSUBPAGE': ssps[ssp_current].handleMouseEvent({'eType': "SELECTIONESCAPED", 'x': ex, 'y': ey, 'button': event['button'], 'modifiers': event['modifiers']})
                elif lastSelected == 'AUXILLARYBAR':    auxBarPage.handleMouseEvent({'eType': "SELECTIONESCAPED", 'x': ex, 'y': ey, 'button': event['button'], 'modifiers': event['modifiers']})
            if   lastHovered == 'SETTINGSBUTTONFRAME':
                self.frameSprites['SETTINGSBUTTONFRAME'].image = self.images['SETTINGSBUTTONFRAME_PRESSED'][0]
                self.settingsButtonStatus = 'PRESSED'
            elif lastHovered == 'SETTINGSSUBPAGE': ssps[ssp_current].handleMouseEvent(event)
            elif lastHovered == 'AUXILLARYBAR':    auxBarPage.handleMouseEvent(event)
            #POSHIGHLIGHT Control
            if lastHovered and (lastHovered == 'KLINESPRICE' or lastHovered[:8] == 'SIVIEWER'):
                self.__updatePosHighlight(ex, ey, lastHovered, updateType = 1)
            self.mouse_lastSelectedSection = lastHovered
            self.mouse_Event_lastPressed   = event

        #---[3-3]: RELEASED
        elif eType == "RELEASED":
            if lastSelected == lastHovered:
                if   lastHovered == 'SETTINGSBUTTONFRAME':
                    self.frameSprites['SETTINGSBUTTONFRAME'].image = self.images['SETTINGSBUTTONFRAME_HOVERED'][0]
                    self.settingsButtonStatus = 'HOVERED'
                    self.__onSettingsButtonClick()
                elif lastHovered == 'SETTINGSSUBPAGE': ssps[ssp_current].handleMouseEvent(event)
                elif lastHovered == 'AUXILLARYBAR':    auxBarPage.handleMouseEvent(event)
            else:
                if   lastSelected == 'SETTINGSBUTTONFRAME':
                    self.frameSprites['SETTINGSBUTTONFRAME'].image = self.images['SETTINGSBUTTONFRAME_DEFAULT'][0]
                    self.settingsButtonStatus = 'DEFAULT'
                elif lastSelected == 'SETTINGSSUBPAGE': ssps[ssp_current].handleMouseEvent({'eType': "HOVERESCAPED", 'x': ex, 'y': ey})
                elif lastSelected == 'AUXILLARYBAR':    auxBarPage.handleMouseEvent({'eType': "HOVERESCAPED", 'x': ex, 'y': ey})
                if   lastHovered == 'SETTINGSBUTTONFRAME':
                    self.frameSprites['SETTINGSBUTTONFRAME'].image = self.images['SETTINGSBUTTONFRAME_HOVERED'][0]
                    self.settingsButtonStatus = 'HOVERED'
                elif lastHovered == 'SETTINGSSUBPAGE': ssps[ssp_current].handleMouseEvent({'eType': "HOVEREENTERED", 'x': ex, 'y': ey})
                elif lastHovered == 'AUXILLARYBAR':    auxBarPage.handleMouseEvent({'eType': "HOVEREENTERED", 'x': ex, 'y': ey})
            #POSHIGHLIGHT Control
            if lastHovered and (lastHovered == 'KLINESPRICE' or lastHovered[:8] == 'SIVIEWER'):
                self.__updatePosHighlight(ex, ey, lastHovered, updateType = 0)
                lastPressed = self.mouse_Event_lastPressed
                if lastPressed and lastPressed['x'] == ex and lastPressed['y'] == ey:
                    if   event['button'] == 1: self.__updatePosSelection(updateType = 0)
                    elif event['button'] == 4:
                        if lastHovered == 'KLINESPRICE': self._editVVR_toExtremaCenter(displayBoxName = lastHovered)
                        else:
                            siAlloc = self.objectConfig[f'SIVIEWER{int(lastHovered[8:]):d}SIAlloc']
                            if   siAlloc == 'VOL':   self._editVVR_toExtremaCenter(displayBoxName = lastHovered, extension_b = 0.0, extension_t = 0.2)
                            elif siAlloc == 'MMACD': self._editVVR_toExtremaCenter(displayBoxName = lastHovered, extension_b = 0.1, extension_t = 0.1)

        #---[3-4]: DRAGGED
        elif eType == "DRAGGED":
            #Find hovering section
            hoveredSection = None
            if   self.settingsSubPage_Opened and ssps[ssp_current].isTouched(ex, ey): hoveredSection = 'SETTINGSSUBPAGE'
            elif auxBarPage.isTouched(ex, ey):                                         hoveredSection = 'AUXILLARYBAR'
            else:
                for dBoxName in self.hitBox:
                    if self.hitBox[dBoxName].isTouched(ex, ey): hoveredSection = dBoxName; break
            #Drag Source
            if   lastSelected == 'SETTINGSSUBPAGE': ssps[ssp_current].handleMouseEvent(event)
            elif lastSelected == 'AUXILLARYBAR':    auxBarPage.handleMouseEvent(event)
            elif lastSelected and lastSelected != 'SETTINGSBUTTONFRAME':
                self.mouse_DragDX[lastSelected] += event['dx']
                self.mouse_DragDY[lastSelected] += event['dy']
                self.mouse_Dragged        = True
                self.mouse_lastDragged_ns = time.perf_counter_ns()
            self.mouse_lastHoveredSection = hoveredSection

        #---[3-5]: SCROLLED
        elif eType == "SCROLLED":
            if   lastSelected == 'SETTINGSSUBPAGE': ssps[ssp_current].handleMouseEvent(event)
            elif lastSelected == 'AUXILLARYBAR':    auxBarPage.handleMouseEvent(event)
            elif lastSelected:
                self.mouse_ScrollDX[lastSelected] += event['scroll_x']
                self.mouse_ScrollDY[lastSelected] += event['scroll_y']
                self.mouse_Scrolled        = True
                self.mouse_lastScrolled_ns = time.perf_counter_ns()

        #---[3-6]: SELECTIONESCAPED
        elif eType == "SELECTIONESCAPED":
            if   lastSelected == 'SETTINGSSUBPAGE': ssps[ssp_current].handleMouseEvent(event)
            elif lastSelected == 'AUXILLARYBAR':    auxBarPage.handleMouseEvent(event)
            self.mouse_lastSelectedSection = None

        #---[3-7]: HOVERESCAPED
        elif eType == "HOVERESCAPED":
            self.__updatePosHighlight(ex, ey, None, updateType = 1)
            if lastHovered == 'AUXILLARYBAR': auxBarPage.handleMouseEvent(event)
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
                tsHovered = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = xValHovered, nTicks = 0)

                #If there exist no previous hoveredPosition
                if (self.posHighlight_hoveredPos[2] == None): 
                    self.posHighlight_updatedPositions = [True, True]
                    self.posHighlight_hoveredPos = (tsHovered, yValHovered, hoveredSection, None)
                #If there exist a previous hoveredPoisiton
                else:
                    if (self.posHighlight_hoveredPos[0] != tsHovered):      self.posHighlight_updatedPositions[0] = True
                    if (self.posHighlight_hoveredPos[1] != yValHovered):    self.posHighlight_updatedPositions[1] = True
                    if (self.posHighlight_hoveredPos[2] != hoveredSection): self.posHighlight_hoveredPos = (tsHovered, yValHovered, hoveredSection, self.posHighlight_hoveredPos[2])
                    else:                                                   self.posHighlight_hoveredPos = (tsHovered, yValHovered, hoveredSection, hoveredSection)
            except Exception as e:
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
                ts_rightEnd = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = tsHovered, nTicks = 1)
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
                dBox_g_current['HORIZONTALGUIDETEXT'].setText(auxiliaries.simpleValueFormatter(value = yHovered, precision = 3))
        
        #[4]: Reset Update Flag
        self.posHighlight_updatedPositions = [False, False]

    def __onPHU_KLINE(self):
        #[1]: Instances
        oc     = self.objectConfig
        klines = self._data_agg[self.intervalID]['kline']
        cInfo  = self.currencyInfo
        tsHovered     = self.posHighlight_hoveredPos[0]
        func_fts      = auxiliaries.floatToString
        dBox_g_kl_dt1 = self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT1']

        #[2]: If Hovering Over A Kline Data
        if tsHovered in klines:
            kline = klines[tsHovered]
            p_open  = kline[KLINDEX_OPENPRICE]
            p_high  = kline[KLINDEX_HIGHPRICE]
            p_low   = kline[KLINDEX_LOWPRICE]
            p_close = kline[KLINDEX_CLOSEPRICE]
            kcType = oc['KlineColorType']
            if   p_open is None or p_close is None: klineColor = f'CONTENT_NEUTRAL_{kcType}'
            elif p_open < p_close:                  klineColor = f'CONTENT_POSITIVE_{kcType}'
            elif p_open > p_close:                  klineColor = f'CONTENT_NEGATIVE_{kcType}'
            else:                                   klineColor = f'CONTENT_NEUTRAL_{kcType}'
            displayText_time = datetime.fromtimestamp(tsHovered+self.timezoneDelta, tz = timezone.utc).strftime(" %Y/%m/%d %H:%M"); tp1 = len(displayText_time)
            pPrecision = cInfo['precisions']['price']
            p_open_str  = "-" if p_open  is None else func_fts(number = p_open,  precision = pPrecision)
            p_high_str  = "-" if p_high  is None else func_fts(number = p_high,  precision = pPrecision)
            p_low_str   = "-" if p_low   is None else func_fts(number = p_low,   precision = pPrecision)
            p_close_str = "-" if p_close is None else func_fts(number = p_close, precision = pPrecision)
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
        dAgg      = self._data_agg[self.intervalID]
        dBox_g_kp_dt2 = self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2']
        
        #[2]: Existence & Display Check
        if 'IVP' not in dAgg:            return False
        if tsHovered not in dAgg['IVP']: return False
        if not oc['IVP_Master']:         return False

        #[3]: Base Text & Styles
        text_display = f" [IVP]"

        #[4]: Displaying Text & Style Construction
        ivp = dAgg['IVP'][tsHovered]
        ivpr_vplp    = ivp['volumePriceLevelProfile']
        ivpr_gFactor = ivp['gammaFactor']
        ivpr_bFactor = ivp['betaFactor']
        if ivpr_vplp is None: textBlock  = " nDivisions: NONE, Gamma Factor: NONE"
        else:                 textBlock  = f" nDivisions: {len(ivpr_vplp):,}, Gamma Factor: {ivpr_gFactor*100:.2f} % [{ivpr_bFactor}]"
        text_display += textBlock

        #[5]: Update Text Element
        dBox_g_kp_dt2.setText(text_display, 'DEFAULT')

        #[6]: Return Result
        return True
    
    def __onPHU_TRADELOG(self):
        #[1]: Instances
        oc         = self.objectConfig
        tradeLogs  = self._data_raw.get('tradeLog', None)
        tsHovered     = self.posHighlight_hoveredPos[0]
        func_fts      = auxiliaries.floatToString
        dBox_g_kp_dt2 = self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2']

        #[2]: Existence & Display Check
        if tradeLogs is None:          return False
        if tsHovered not in tradeLogs: return False
        if not oc['TRADELOG_Display']: return False

        #[3]: Base Text & Styles
        text_display = f" [TRADELOG]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[4]: Displaying Text & Style Construction
        #---[4-1]: Contents Values
        tradeLog = tradeLogs[tsHovered]
        entryPrice = tradeLog['entryPrice']
        quantity   = tradeLog['totalQuantity']
        logs       = [l for ts in auxiliaries.getTimestampList_byRange(intervalID        = KLINTERVAL,
                                                                              timestamp_beg     = tsHovered,
                                                                              timestamp_end     = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = tsHovered, nTicks = 1)-1,
                                                                              lastTickInclusive = True)
                      if ts in tradeLogs
                      for l in tradeLogs[ts]['logs']]
        logsSumm = None
        if logs:
            quantity_sum   = 0
            profit_sum     = 0
            tradingFee_sum = 0
            for l in logs:
                quantity_sum   += l['quantity']
                profit_sum     += l['profit']
                tradingFee_sum += l['tradingFee']
            logsSumm = {'quantity':   quantity_sum,
                        'profit':     profit_sum,
                        'tradingFee': tradingFee_sum}
        tBlocks = []
        #---[4-2]: Contents Text
        precisions = self.currencyInfo['precisions']
        #------[4-2-1]: Entry Price
        if entryPrice is None: tBlock_str = "N/A"
        else:                  tBlock_str = func_fts(number = entryPrice, precision = precisions['price'])
        tBlock_col = 'DEFAULT'
        tBlocks.append((' Entry: ', 'DEFAULT'))
        tBlocks.append((tBlock_str, 'DEFAULT'))
        #------[4-2-2]: Entry Price
        if quantity is None: tBlock_str = "N/A"
        else:                tBlock_str = func_fts(number = quantity, precision = precisions['quantity'])
        if   quantity is None or quantity == 0.0: tBlock_col = 'DEFAULT'
        elif quantity < 0:                        tBlock_col = 'RED_LIGHT'
        elif 0 < quantity:                        tBlock_col = 'GREEN_LIGHT'
        tBlocks.append((' Quantity: ', 'DEFAULT'))
        tBlocks.append((tBlock_str, tBlock_col))
        #------[4-2-3]: Number Of Trades & Logs Summary
        if logsSumm:
            #[4-2-3-1]: Number Of Trades
            tBlock_str = f"{len(logs):d}"
            tBlocks.append((' Trades: ', 'DEFAULT'))
            tBlocks.append((tBlock_str,  'DEFAULT'))
            #[4-2-3-2]: Quantity Sum
            tBlock_str = func_fts(number = logsSumm['quantity'], precision = precisions['quantity'])
            tBlocks.append((' Trade Quantity: ', 'DEFAULT'))
            tBlocks.append((tBlock_str,  'DEFAULT'))
            #[4-2-3-3]: Profit Sum
            tBlock_str = func_fts(number = logsSumm['profit'], precision = precisions['quote'])
            if   logsSumm['profit'] < 0: tBlock_col = 'RED_LIGHT'
            elif 0 < logsSumm['profit']: tBlock_col = 'GREEN_LIGHT'
            else:                        tBlock_col = 'DEFAULT'
            tBlocks.append((' Profit: ', 'DEFAULT'))
            tBlocks.append((tBlock_str,  'DEFAULT'))
            #[4-2-3-4]: Trading Fee
            tBlock_str = func_fts(number = logsSumm['tradingFee'], precision = precisions['quote'])
            tBlocks.append((' Trading Fee: ', 'DEFAULT'))
            tBlocks.append((tBlock_str,  'DEFAULT'))
        #---[4-3]: Contents Concatenation
        for tb_display, tb_style in tBlocks:
            current_len = len(text_display)
            block_len   = len(tb_display)
            text_styles.append(((current_len, current_len+block_len-1), tb_style))
            text_display += tb_display

        #[5]: Update Text Element
        dBox_g_kp_dt2.setText(text_display, text_styles)

        #[6]: Return Result
        return True
    
    def __onPHU_VOL(self):
        #[1]: Instances
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID]
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        dAgg_iID  = self._data_agg[self.intervalID]
        klines    = dAgg_iID['kline']
        cInfo     = self.currencyInfo
        siViewerIndex   = self.siTypes_siViewerAlloc['VOL']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']

        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - VOL]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        if tsHovered in klines and oc['VOL_Master']:
            kline = klines[tsHovered]
            #[3-1]: Volume Raw
            volType = oc['VOL_VolumeType']
            if   volType == 'BASE':    value = kline[KLINDEX_VOLBASE];          unit = cInfo['info_server']['baseAsset']
            elif volType == 'QUOTE':   value = kline[KLINDEX_VOLQUOTE];         unit = cInfo['info_server']['quoteAsset']
            elif volType == 'BASETB':  value = kline[KLINDEX_VOLBASETAKERBUY];  unit = cInfo['info_server']['baseAsset']
            elif volType == 'QUOTETB': value = kline[KLINDEX_VOLQUOTETAKERBUY]; unit = cInfo['info_server']['quoteAsset']
            kcType = oc['KlineColorType']
            p_open  = kline[KLINDEX_OPENPRICE]
            p_close = kline[KLINDEX_CLOSEPRICE]
            if   p_open is None:   klineColor = f'CONTENT_NEUTRAL_{kcType}'
            elif p_open < p_close: klineColor = f'CONTENT_POSITIVE_{kcType}'
            elif p_open > p_close: klineColor = f'CONTENT_NEGATIVE_{kcType}'
            else:                  klineColor = f'CONTENT_NEUTRAL_{kcType}'
            textBlock_front = f" VOL_{volType}: "
            textBlock = "-" if value is None else f"{textBlock_front}{auxiliaries.simpleValueFormatter(value = value, precision = 3)} {unit}"
            text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(textBlock_front)), 'DEFAULT'))
            text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1),     klineColor))
            text_display += textBlock
            #[3-2]: Volume Analysis
            for aCode in self.siTypes_analysisCodes['VOL']:
                #[3-2-1]: Existence Check
                dAgg_aCode = dAgg_iID[aCode]
                if tsHovered not in dAgg_aCode: continue

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
                value_MA = dAgg_aCode[tsHovered][f'MA_{volType}']
                if value_MA is None: textBlock = f" {aCode}: NONE"
                else:                textBlock = f" {aCode}: {auxiliaries.simpleValueFormatter(value = value_MA, precision = 3)} {unit}"
                text_display += textBlock
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(aCode)+3),     'DEFAULT'))
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1), lineIndex_str))

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)

    def __onPHU_DEPTH(self):
        #[1]: Instances
        oc  = self.objectConfig
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        depths    = self._data_agg[self.intervalID]['depth']
        cInfo     = self.currencyInfo
        siViewerIndex   = self.siTypes_siViewerAlloc['DEPTH']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']

        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - DEPTH]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        if tsHovered in depths and oc['DEPTH_Master']:
            #[3-1]: Instances
            depth = depths[tsHovered]
            unit  = cInfo['info_server']['quoteAsset']

            #[3-2]: Text & TextStyle
            for line in ('BIDS', 'ASKS'):
                #[3-2-1]: Color & TextStyle Check
                currentLine_style = dBox_g_this_dt1.getTextStyle(line)
                color = (oc[f'DEPTH_{line}_ColorR%{cgt}'],
                         oc[f'DEPTH_{line}_ColorG%{cgt}'],
                         oc[f'DEPTH_{line}_ColorB%{cgt}'],
                         oc[f'DEPTH_{line}_ColorA%{cgt}'])
                if (currentLine_style is None) or (currentLine_style['color'] != color):
                    newLine_style = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                    newLine_style['color'] = color
                    dBox_g_this_dt1.addTextStyle(line, newLine_style)

                #[3-2-2]: Text & Format Array Construction
                if line == 'BIDS': 
                    values = (depth[DEPTHINDEX_BIDS0], depth[DEPTHINDEX_BIDS1], depth[DEPTHINDEX_BIDS2], depth[DEPTHINDEX_BIDS3], depth[DEPTHINDEX_BIDS4], depth[DEPTHINDEX_BIDS5])
                    value  = sum(values) if all(val is not None for val in values) else None
                elif line == 'ASKS':
                    values = (depth[DEPTHINDEX_ASKS0], depth[DEPTHINDEX_ASKS1], depth[DEPTHINDEX_ASKS2], depth[DEPTHINDEX_ASKS3], depth[DEPTHINDEX_ASKS4], depth[DEPTHINDEX_ASKS5])
                    value  = sum(values) if all(val is not None for val in values) else None
                tb_value = "-" if value is None else f"{auxiliaries.simpleValueFormatter(value = value, precision = 3)} {unit}"
                for tb, tColor in ((f" {line}: ", 'DEFAULT'),
                                    (tb_value,    line)):
                    text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(tb)), tColor))
                    text_display += tb

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)

    def __onPHU_AGGTRADE(self):
        #[1]: Instances
        oc  = self.objectConfig
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        aggTrades = self._data_agg[self.intervalID]['aggTrade']
        cInfo     = self.currencyInfo
        siViewerIndex   = self.siTypes_siViewerAlloc['AGGTRADE']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']

        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - AGGTRADE]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        if tsHovered in aggTrades and oc['AGGTRADE_Master']:
            #[3-1]: Instances
            aggTrade    = aggTrades[tsHovered]
            displayType = oc['AGGTRADE_DisplayType']
            if displayType == 'QUANTITY':
                dIdx = {'BUY': ATINDEX_QUANTITYBUY, 'SELL': ATINDEX_QUANTITYSELL}
                unit = cInfo['info_server']['baseAsset']
            elif displayType == 'NTRADES':
                dIdx = {'BUY': ATINDEX_NTRADESBUY, 'SELL': ATINDEX_NTRADESSELL}
                unit = ""
            elif displayType == 'NOTIONAL':
                dIdx = {'BUY': ATINDEX_NOTIONALBUY, 'SELL': ATINDEX_NOTIONALSELL}
                unit = cInfo['info_server']['quoteAsset']

            #[3-2]: Text & TextStyle
            for line in ('BUY', 'SELL'):
                #[3-2-1]: Color & TextStyle Check
                currentLine_style = dBox_g_this_dt1.getTextStyle(line)
                color = (oc[f'AGGTRADE_{line}_ColorR%{cgt}'],
                         oc[f'AGGTRADE_{line}_ColorG%{cgt}'],
                         oc[f'AGGTRADE_{line}_ColorB%{cgt}'],
                         oc[f'AGGTRADE_{line}_ColorA%{cgt}'])
                if (currentLine_style is None) or (currentLine_style['color'] != color):
                    newLine_style = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                    newLine_style['color'] = color
                    dBox_g_this_dt1.addTextStyle(line, newLine_style)

                #[3-2-2]: Text & Format Array Construction
                value    = aggTrade[dIdx[line]]
                tb_value = "-" if value is None else f"{auxiliaries.simpleValueFormatter(value = value, precision = 3)} {unit}"
                for tb, tColor in ((f" {line}: ", 'DEFAULT'),
                                   (tb_value,     line)):
                    text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(tb)), tColor))
                    text_display += tb

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)

    def __onPHU_NNA(self):
        #[1]: Instances
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID]
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        dAgg      = self._data_agg[self.intervalID]
        siViewerIndex   = self.siTypes_siViewerAlloc['NNA']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']


        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - NNA]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        if oc['NNA_Master']:
            for aCode in self.siTypes_analysisCodes['NNA']:
                #[3-1]: Existence Check
                if tsHovered not in dAgg[aCode]: continue

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
                value_nna = dAgg[aCode][tsHovered]['NNA']
                if value_nna is None: textBlock = f" {aCode}: NONE"
                else:                 textBlock = f" {aCode}: {value_nna:.2f}"
                text_display += textBlock
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(aCode)+3),     'DEFAULT'))
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1), lineIndex_str))

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)

    def __onPHU_MMACD(self):
        #[1]: Instances
        oc  = self.objectConfig
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        dAgg      = self._data_agg[self.intervalID]
        siViewerIndex   = self.siTypes_siViewerAlloc['MMACD']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']

        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - MMACD]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        aCode = 'MMACD'
        if oc['MMACD_Master'] and aCode in dAgg and tsHovered in dAgg[aCode]:
            for line, valCode in (('MMACD',     'MMACD'), 
                                  ('SIGNAL',    'SIGNAL'), 
                                  ('HISTOGRAM', oc['MMACD_HISTOGRAM_Type'])
                                  ):
                #[3-1]: Display Check
                if not oc[f'MMACD_{line}_Display']: continue

                #[3-2]: Display Value
                value_display = dAgg[aCode][tsHovered][valCode]

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
                    newLine_color = (oc[f'MMACD_{newLine_colType}_ColorR%{cgt}'],
                                     oc[f'MMACD_{newLine_colType}_ColorG%{cgt}'],
                                     oc[f'MMACD_{newLine_colType}_ColorB%{cgt}'],
                                     oc[f'MMACD_{newLine_colType}_ColorA%{cgt}'])
                    if (currentLine_style is None) or (currentLine_style['color'] != newLine_color):
                        newLine_style = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                        newLine_style['color'] = newLine_color
                        dBox_g_this_dt1.addTextStyle(newLine_colType, newLine_style)
                #[3-3]: Text & Format Array Construction
                if value_display is None: textBlock = f" {line}: NONE"
                else:                     textBlock = f" {line}: {auxiliaries.simpleValueFormatter(value = value_display, precision = 3)}"
                text_display += textBlock
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(line)+3),      'DEFAULT'))
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1), newLine_colType))

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)

    def __onPHU_DMIxADX(self):
        #[1]: Instances
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID]
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        dAgg      = self._data_agg[self.intervalID]
        siViewerIndex   = self.siTypes_siViewerAlloc['DMIxADX']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']


        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - DMIxADX]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        if oc['DMIxADX_Master']:
            for aCode in self.siTypes_analysisCodes['DMIxADX']:
                #[3-1]: Existence Check
                if tsHovered not in dAgg[aCode]: continue

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
                value_dmixadx_absAthRel = dAgg[aCode][tsHovered]['DMIxADX_ABSATHREL']
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
        ap  = self.analysisParams[self.intervalID]
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        dAgg      = self._data_agg[self.intervalID]
        siViewerIndex   = self.siTypes_siViewerAlloc['MFI']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']


        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - MFI]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        if oc['MFI_Master']:
            for aCode in self.siTypes_analysisCodes['MFI']:
                #[3-1]: Existence Check
                if tsHovered not in dAgg[aCode]: continue

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
                value_mfiAbsAthDevRel = dAgg[aCode][tsHovered]['MFI_ABSATHDEVREL']
                if value_mfiAbsAthDevRel is None: textBlock = f" {aCode}: NONE"
                else:                             textBlock = f" {aCode}: {value_mfiAbsAthDevRel:.2f}"
                text_display += textBlock
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(aCode)+3),     'DEFAULT'))
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1), lineIndex_str))

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)

    def __onPHU_TPD(self):
        #[1]: Instances
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID]
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        dAgg      = self._data_agg[self.intervalID]
        siViewerIndex   = self.siTypes_siViewerAlloc['TPD']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']


        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - TPD]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        if oc['TPD_Master']:
            for aCode in self.siTypes_analysisCodes['TPD']:
                #[3-1]: Existence Check
                if tsHovered not in dAgg[aCode]: continue

                #[3-2]: Display Check
                lineIndex     = ap[aCode]['lineIndex']
                lineIndex_str = f"{lineIndex}"
                if not oc[f'TPD_{lineIndex}_Display']: continue

                #[3-3]: TextStyle Check
                currentLine_style = dBox_g_this_dt1.getTextStyle(lineIndex_str)
                newLine_color = (oc[f'TPD_{lineIndex}_ColorR%{cgt}'],
                                 oc[f'TPD_{lineIndex}_ColorG%{cgt}'],
                                 oc[f'TPD_{lineIndex}_ColorB%{cgt}'],
                                 oc[f'TPD_{lineIndex}_ColorA%{cgt}'])
                if (currentLine_style is None) or (currentLine_style['color'] != newLine_color):
                    newLine_style = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                    newLine_style['color'] = newLine_color
                    dBox_g_this_dt1.addTextStyle(lineIndex_str, newLine_style)

                #[3-4]: Text & Format Array Construction
                value_biasMA = dAgg[aCode][tsHovered]['TPD_BIASMA']
                if value_biasMA is None: textBlock = f" {aCode}: NONE"
                else:                    textBlock = f" {aCode}: {value_biasMA:.2f}"
                text_display += textBlock
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(aCode)+3),     'DEFAULT'))
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1), lineIndex_str))

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)

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
            tsPosEnd = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = self.posHighlight_selectedPos, nTicks = 1)
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
        dAgg      = self._data_agg[self.intervalID]
        aParams   = self.analysisParams[self.intervalID]
        dQueue    = self.__drawQueue
        #IVP Update
        if 'IVP' in aParams:
            if   ph_selPos is None: self._drawer_RemoveDrawings(analysisCode = 'IVP', gRemovalSignal = 0b01)
            elif ph_selPos in dAgg['IVP']: 
                if ph_selPos in dQueue: 
                    if 'IVP' in dQueue[ph_selPos]: 
                        if dQueue[ph_selPos]['IVP'] is not None: dQueue[ph_selPos]['IVP'] |= 0b01
                    else:                                        dQueue[ph_selPos]['IVP'] = 0b01
                else:                                            dQueue[ph_selPos] = {'IVP': 0b01}
        #SWING Update
        for lineIndex in range (_NMAXLINES['SWING']):
            aCode = f'SWING_{lineIndex}'
            if aCode in aParams:
                if ph_selPos is None: self._drawer_RemoveDrawings(analysisCode = aCode, gRemovalSignal = 0b1)
                elif ph_selPos in dAgg[aCode]:
                    if ph_selPos in dQueue: 
                        if aCode in dQueue[ph_selPos]: 
                            if dQueue[ph_selPos][aCode] is not None: dQueue[ph_selPos][aCode] |= 0b1
                        else:                                        dQueue[ph_selPos][aCode] = 0b1
                    else:                                            dQueue[ph_selPos] = {aCode: 0b1}

    def handleKeyEvent(self, event):
        if not self.hidden:
            if self.mouse_lastSelectedSection == 'SETTINGSSUBPAGE': 
                self.settingsSubPages[self.settingsSubPage_Current].handleKeyEvent(event)
    
    def _clearHighlightsAndDescriptors(self):
        self.posHighlight_hoveredPos       = (None, None, None, None)
        self.posHighlight_updatedPositions = [False, False]
        self.posHighlight_selectedPos      = None
        self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_HOVERED'].visible  = False
        self.displayBox_graphics['KLINESPRICE']['POSHIGHLIGHT_SELECTED'].visible = False
        self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT1'].setText("")
        self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2'].setText("")
        for siViewerName in self.displayBox_graphics_visibleSIViewers:
            self.displayBox_graphics[siViewerName]['POSHIGHLIGHT_HOVERED'].visible  = False 
            self.displayBox_graphics[siViewerName]['POSHIGHLIGHT_SELECTED'].visible = False
            self.displayBox_graphics[siViewerName]['DESCRIPTIONTEXT1'].setText("")
    #User Interaction Control END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Basic Object Control -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def show(self):
        self.hidden = False

        for dBoxName in self.frameSprites: 
            self.frameSprites[dBoxName].visible = True

            if dBoxName == 'MAINGRID_TEMPORAL':
                self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'].visible = True

            elif dBoxName == 'KLINESPRICE':
                self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].visible    = True
                self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'].visible      = True
                self.displayBox_graphics[dBoxName]['DESCRIPTORDISPLAY_CAMGROUP'].visible = True
                self.displayBox_graphics[dBoxName]['RCLCG'].show()
                self.displayBox_graphics[dBoxName]['RCLCG_XFIXED'].show()
                self.displayBox_graphics[dBoxName]['RCLCG_YFIXED'].show()
                self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT1'].show()
                self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT2'].show()
                self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT3'].show()

            elif dBoxName == 'MAINGRID_KLINESPRICE':
                self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].visible = True

            elif dBoxName.startswith('SIVIEWER'):
                sivIdx = int(dBoxName[8:])
                if self.objectConfig[f'SIVIEWER{sivIdx}Display']:
                    self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].visible    = True
                    self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'].visible      = True
                    self.displayBox_graphics[dBoxName]['DESCRIPTORDISPLAY_CAMGROUP'].visible = True
                    self.displayBox_graphics[dBoxName]['RCLCG'].show()
                    self.displayBox_graphics[dBoxName]['RCLCG_XFIXED'].show()
                    self.displayBox_graphics[dBoxName]['RCLCG_YFIXED'].show()
                    self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT1'].show()

            elif (dBoxName.startswith('MAINGRID_SIVIEWER')):
                sivIdx = int(dBoxName[17:])
                if self.objectConfig[f'SIVIEWER{sivIdx}Display']: 
                    self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].visible = True

        self.auxBarPage.show()
        if self.settingsSubPage_Opened: 
            self.settingsSubPages[self.settingsSubPage_Current].show()

        if self.__loading:
            self.frameSprites['KLINELOADINGCOVER'].visible = True
            self.loadingGaugeBar.show()
            self.loadingTextBox.show()
            self.loadingTextBox_perc.show()
        else:
            self.frameSprites['KLINELOADINGCOVER'].visible = False
            self.loadingGaugeBar.hide()
            self.loadingTextBox.hide()
            self.loadingTextBox_perc.hide()

    def hide(self):
        self.hidden = True

        for dBoxName in self.frameSprites: 
            self.frameSprites[dBoxName].visible = False

            if dBoxName == 'MAINGRID_TEMPORAL':
                self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'].visible = False

            elif dBoxName == 'KLINESPRICE':
                self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].visible    = False
                self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'].visible      = False
                self.displayBox_graphics[dBoxName]['DESCRIPTORDISPLAY_CAMGROUP'].visible = False
                self.displayBox_graphics[dBoxName]['RCLCG'].hide()
                self.displayBox_graphics[dBoxName]['RCLCG_XFIXED'].hide()
                self.displayBox_graphics[dBoxName]['RCLCG_YFIXED'].hide()
                self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT1'].hide()
                self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT2'].hide()
                self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT3'].hide()

            elif dBoxName == 'MAINGRID_KLINESPRICE':
                self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].visible = False

            elif dBoxName.startswith('SIVIEWER'):
                self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].visible    = False
                self.displayBox_graphics[dBoxName]['VERTICALGRID_CAMGROUP'].visible      = False
                self.displayBox_graphics[dBoxName]['DESCRIPTORDISPLAY_CAMGROUP'].visible = False
                self.displayBox_graphics[dBoxName]['RCLCG'].hide()
                self.displayBox_graphics[dBoxName]['RCLCG_XFIXED'].hide()
                self.displayBox_graphics[dBoxName]['RCLCG_YFIXED'].hide()
                self.displayBox_graphics[dBoxName]['DESCRIPTIONTEXT1'].hide()

            elif dBoxName.startswith('MAINGRID_SIVIEWER'):
                self.displayBox_graphics[dBoxName]['HORIZONTALGRID_CAMGROUP'].visible = False

        self.auxBarPage.hide()
        self.settingsSubPages[self.settingsSubPage_Current].hide()
        self.frameSprites['KLINELOADINGCOVER'].visible = False
        self.loadingGaugeBar.hide()
        self.loadingTextBox.hide()
        self.loadingTextBox_perc.hide()

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
        #[1]: Instances
        im   = self.imageManager
        vm   = self.visualManager
        oc = self.objectConfig
        images   = self.images
        fSprites = self.frameSprites
        ssps     = self.settingsSubPages
        dBox_g   = self.displayBox_graphics

        #[2]: Load Text Styles and Colors
        gColor_prev       = self.gridColor
        gColor_Heavy_prev = self.gridColor_Heavy
        cgt = vm.getGUITheme()
        self.currentGUITheme = cgt
        self.gridColor                  = vm.getFromColorTable('CHARTDRAWER_GRID')
        self.gridColor_Heavy            = vm.getFromColorTable('CHARTDRAWER_GRIDHEAVY')
        self.guideColor                 = vm.getFromColorTable('CHARTDRAWER_GUIDECONTENT')
        self.posHighlightColor_hovered  = vm.getFromColorTable('CHARTDRAWER_POSHOVERED')
        self.posHighlightColor_selected = vm.getFromColorTable('CHARTDRAWER_POSSELECTED')
        tStyle_eff_new = vm.getTextStyle('chartDrawer_'+self.textStyle)
        for style_name, style in tStyle_eff_new.items():
            style['font_size'] = self.effectiveTextStyle[style_name]['font_size']
        self.effectiveTextStyle = tStyle_eff_new
        effTStyle = self.effectiveTextStyle

        #[3]: Object Image Update
        for dBoxName in self.displayBox:
            if self.displayBox[dBoxName] is None: continue
            if dBoxName == 'SETTINGSBUTTONFRAME':
                images['SETTINGSBUTTONFRAME_DEFAULT'] = im.getImageByLoadIndex(images['SETTINGSBUTTONFRAME_DEFAULT'][1])
                images['SETTINGSBUTTONFRAME_HOVERED'] = im.getImageByLoadIndex(images['SETTINGSBUTTONFRAME_HOVERED'][1])
                images['SETTINGSBUTTONFRAME_PRESSED'] = im.getImageByLoadIndex(images['SETTINGSBUTTONFRAME_PRESSED'][1])
                iconColoring = self.visualManager.getFromColorTable('ICON_COLORING')
                fSprites[dBoxName].image = images['SETTINGSBUTTONFRAME_'+self.settingsButtonStatus][0]
                fSprites['SETTINGSBUTTONFRAME_ICON'].color = (iconColoring[0], iconColoring[1], iconColoring[2]); fSprites['SETTINGSBUTTONFRAME'+'_ICON'].opacity = iconColoring[3]
            else:
                images[dBoxName] = im.getImageByLoadIndex(images[dBoxName][1])
                fSprites[dBoxName].image = images[dBoxName][0]
                    
        #[4]: Grid and Guide Lines & Text Update
        for dBoxName in self.displayBox:
            if dBoxName == 'KLINESPRICE':
                dBox_g_this_main = dBox_g['KLINESPRICE']
                dBox_g_this_grid = dBox_g['MAINGRID_KLINESPRICE']
                dBox_g_this_main['DESCRIPTIONTEXT1'].on_GUIThemeUpdate(newDefaultTextStyle = effTStyle['CONTENT_DEFAULT'], auxillaryTextStyles = effTStyle)
                dBox_g_this_main['DESCRIPTIONTEXT2'].on_GUIThemeUpdate(newDefaultTextStyle = effTStyle['CONTENT_DEFAULT'], auxillaryTextStyles = effTStyle)
                dBox_g_this_main['DESCRIPTIONTEXT3'].on_GUIThemeUpdate(newDefaultTextStyle = effTStyle['CONTENT_DEFAULT'], auxillaryTextStyles = effTStyle)

                dBox_g_this_main['POSHIGHLIGHT_HOVERED'].color  = self.posHighlightColor_hovered
                dBox_g_this_main['POSHIGHLIGHT_SELECTED'].color = self.posHighlightColor_selected
                dBox_g_this_main['HORIZONTALGUIDELINE'].color   = self.guideColor
                dBox_g_this_main['HORIZONTALGUIDETEXT'].on_GUIThemeUpdate(newDefaultTextStyle = effTStyle['GUIDECONTENT'])

                for gridLineShape in dBox_g_this_main['HORIZONTALGRID_LINES']: 
                    gls_col_prev = gridLineShape.color
                    if   gls_col_prev == gColor_prev:       gridLineShape.color = self.gridColor
                    elif gls_col_prev == gColor_Heavy_prev: gridLineShape.color = self.gridColor_Heavy
                for gridLineShape in dBox_g_this_main['VERTICALGRID_LINES']:
                    gls_col_prev = gridLineShape.color
                    if   gls_col_prev == gColor_prev:       gridLineShape.color = self.gridColor
                    elif gls_col_prev == gColor_Heavy_prev: gridLineShape.color = self.gridColor_Heavy
                for gridLineShape in dBox_g_this_grid['HORIZONTALGRID_LINES']:
                    gls_col_prev = gridLineShape.color
                    if   gls_col_prev == gColor_prev:       gridLineShape.color = self.gridColor
                    elif gls_col_prev == gColor_Heavy_prev: gridLineShape.color = self.gridColor_Heavy
                for gridLineText  in dBox_g_this_grid['HORIZONTALGRID_TEXTS']: gridLineText.on_GUIThemeUpdate(newDefaultTextStyle = effTStyle['GRID'])

            elif dBoxName.startswith('SIVIEWER'):
                siIndex = int(dBoxName[8:])
                dBoxName          = f'SIVIEWER{siIndex}'
                dBoxName_MAINGRID = f'MAINGRID_SIVIEWER{siIndex}'
                dBox_g_this_main = dBox_g[dBoxName]
                dBox_g_this_grid = dBox_g[dBoxName_MAINGRID]

                dBox_g_this_main['DESCRIPTIONTEXT1'].on_GUIThemeUpdate(newDefaultTextStyle = effTStyle['CONTENT_DEFAULT'], auxillaryTextStyles = effTStyle)
                dBox_g_this_main['POSHIGHLIGHT_HOVERED'].color  = self.posHighlightColor_hovered
                dBox_g_this_main['POSHIGHLIGHT_SELECTED'].color = self.posHighlightColor_selected
                dBox_g_this_main['HORIZONTALGUIDELINE'].color   = self.guideColor
                dBox_g_this_main['HORIZONTALGUIDETEXT'].on_GUIThemeUpdate(newDefaultTextStyle = effTStyle['GUIDECONTENT'])

                for gridLineShape in dBox_g_this_main['HORIZONTALGRID_LINES']:
                    gls_col_prev = gridLineShape.color
                    if   gls_col_prev == gColor_prev:       gridLineShape.color = self.gridColor
                    elif gls_col_prev == gColor_Heavy_prev: gridLineShape.color = self.gridColor_Heavy
                for gridLineShape in dBox_g_this_main['VERTICALGRID_LINES']:
                    gls_col_prev = gridLineShape.color
                    if   gls_col_prev == gColor_prev:       gridLineShape.color = self.gridColor
                    elif gls_col_prev == gColor_Heavy_prev: gridLineShape.color = self.gridColor_Heavy
                for gridLineShape in dBox_g_this_grid['HORIZONTALGRID_LINES']:
                    gls_col_prev = gridLineShape.color
                    if   gls_col_prev == gColor_prev:       gridLineShape.color = self.gridColor
                    elif gls_col_prev == gColor_Heavy_prev: gridLineShape.color = self.gridColor_Heavy
                for gridLineText  in dBox_g_this_grid['HORIZONTALGRID_TEXTS']: gridLineText.on_GUIThemeUpdate(newDefaultTextStyle = effTStyle['GRID'])

            elif (dBoxName == 'MAINGRID_TEMPORAL'):
                dBox_g_this = dBox_g['MAINGRID_TEMPORAL']
                for gridLineShape in dBox_g_this['VERTICALGRID_LINES']:
                    gls_col_prev = gridLineShape.color
                    if   gls_col_prev == gColor_prev:       gridLineShape.color = self.gridColor
                    elif gls_col_prev == gColor_Heavy_prev: gridLineShape.color = self.gridColor_Heavy
                for gridLineText  in dBox_g_this['VERTICALGRID_TEXTS']: gridLineText.on_GUIThemeUpdate(newDefaultTextStyle = effTStyle['GRID'])
        
        #[5]: Klines Loading GaugeBar Related
        images['KLINELOADINGCOVER']             = im.getImageByLoadIndex(images['KLINELOADINGCOVER'][1])
        fSprites['KLINELOADINGCOVER'].image = images['KLINELOADINGCOVER'][0]
        self.loadingGaugeBar.on_GUIThemeUpdate(**kwargs)
        self.loadingTextBox_perc.on_GUIThemeUpdate(**kwargs)
        self.loadingTextBox.on_GUIThemeUpdate(**kwargs)

        #[6]: Auxillary Bar Objects
        abp = self.auxBarPage
        aux = auxiliaries
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
                    aux.KLINE_INTERVAL_ID_1M):
            abp.GUIOs[f'AGGINTERVAL_{iID}'].on_GUIThemeUpdate(**kwargs)
        abp.GUIOs['TARGETTEXT'].on_GUIThemeUpdate(**kwargs)

        #[7]: Update Settings Subpages
        for ssp in ssps.values(): 
            ssp.on_GUIThemeUpdate(**kwargs)
        
        #[8]: Update Configuration Objects Color
        #---[8-1]: TRADELOG
        ssps['MAIN'].GUIOs["TRADELOGCOLOR_BUY_LED"].updateColor(oc[f'TRADELOG_BUY_ColorR%{cgt}'], 
                                                                oc[f'TRADELOG_BUY_ColorG%{cgt}'], 
                                                                oc[f'TRADELOG_BUY_ColorB%{cgt}'], 
                                                                oc[f'TRADELOG_BUY_ColorA%{cgt}'])
        ssps['MAIN'].GUIOs["TRADELOGCOLOR_SELL_LED"].updateColor(oc[f'TRADELOG_SELL_ColorR%{cgt}'], 
                                                                 oc[f'TRADELOG_SELL_ColorG%{cgt}'], 
                                                                 oc[f'TRADELOG_SELL_ColorB%{cgt}'], 
                                                                 oc[f'TRADELOG_SELL_ColorA%{cgt}'])
        self.__onSettingsContentUpdate(ssps['MAIN'].GUIOs["TRADELOGCOLOR_TARGETSELECTION"])
        #---[8-2]: BIDS AND ASKS
        ssps['MAIN'].GUIOs["DEPTHOVERLAYCOLOR_BIDS_LED"].updateColor(oc[f'DEPTHOVERLAY_BIDS_ColorR%{cgt}'], 
                                                                     oc[f'DEPTHOVERLAY_BIDS_ColorG%{cgt}'], 
                                                                     oc[f'DEPTHOVERLAY_BIDS_ColorB%{cgt}'], 
                                                                     oc[f'DEPTHOVERLAY_BIDS_ColorA%{cgt}'])
        ssps['MAIN'].GUIOs["DEPTHOVERLAYCOLOR_ASKS_LED"].updateColor(oc[f'DEPTHOVERLAY_ASKS_ColorR%{cgt}'], 
                                                                     oc[f'DEPTHOVERLAY_ASKS_ColorG%{cgt}'], 
                                                                     oc[f'DEPTHOVERLAY_ASKS_ColorB%{cgt}'], 
                                                                     oc[f'DEPTHOVERLAY_ASKS_ColorA%{cgt}'])
        self.__onSettingsContentUpdate(ssps['MAIN'].GUIOs["DEPTHOVERLAYCOLOR_TARGETSELECTION"])
        #---[8-3]: MAs
        for miType in ('SMA','WMA','EMA'):
            for lineIndex in range (_NMAXLINES[miType]):
                ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}_LINECOLOR"].updateColor(oc[f'{miType}_{lineIndex}_ColorR%{cgt}'], 
                                                                                           oc[f'{miType}_{lineIndex}_ColorG%{cgt}'], 
                                                                                           oc[f'{miType}_{lineIndex}_ColorB%{cgt}'], 
                                                                                           oc[f'{miType}_{lineIndex}_ColorA%{cgt}'])
            self.__onSettingsContentUpdate(ssps[miType].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
        #---[8-4]: PSAR
        for lineIndex in range (_NMAXLINES['PSAR']):
            ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}_LINECOLOR"].updateColor(oc[f'PSAR_{lineIndex}_ColorR%{cgt}'], 
                                                                                   oc[f'PSAR_{lineIndex}_ColorG%{cgt}'], 
                                                                                   oc[f'PSAR_{lineIndex}_ColorB%{cgt}'], 
                                                                                   oc[f'PSAR_{lineIndex}_ColorA%{cgt}'])
        self.__onSettingsContentUpdate(ssps['PSAR'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
        #---[8-5]: BOL
        for lineIndex in range (_NMAXLINES['BOL']):
            ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineIndex}_LINECOLOR"].updateColor(oc[f'BOL_{lineIndex}_ColorR%{cgt}'], 
                                                                                 oc[f'BOL_{lineIndex}_ColorG%{cgt}'], 
                                                                                 oc[f'BOL_{lineIndex}_ColorB%{cgt}'], 
                                                                                 oc[f'BOL_{lineIndex}_ColorA%{cgt}'])
        self.__onSettingsContentUpdate(ssps['BOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
        #---[8-6]: IVP
        ssps['IVP'].GUIOs["INDICATOR_VPLP_COLOR"].updateColor(oc[f'IVP_VPLP_ColorR%{cgt}'],
                                                              oc[f'IVP_VPLP_ColorG%{cgt}'],
                                                              oc[f'IVP_VPLP_ColorB%{cgt}'],
                                                              oc[f'IVP_VPLP_ColorA%{cgt}'])
        ssps['IVP'].GUIOs["INDICATOR_VPLPB_COLOR"].updateColor(oc[f'IVP_VPLPB_ColorR%{cgt}'],
                                                               oc[f'IVP_VPLPB_ColorG%{cgt}'],
                                                               oc[f'IVP_VPLPB_ColorB%{cgt}'],
                                                               oc[f'IVP_VPLPB_ColorA%{cgt}'])
        self.__onSettingsContentUpdate(ssps['IVP'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
        #---[8-7]: VOL
        for lineIndex in range (_NMAXLINES['VOL']):
            ssps['VOL'].GUIOs[f"INDICATOR_VOL{lineIndex}_LINECOLOR"].updateColor(oc[f'VOL_{lineIndex}_ColorR%{cgt}'], 
                                                                                 oc[f'VOL_{lineIndex}_ColorG%{cgt}'], 
                                                                                 oc[f'VOL_{lineIndex}_ColorB%{cgt}'], 
                                                                                 oc[f'VOL_{lineIndex}_ColorA%{cgt}'])
        self.__onSettingsContentUpdate(ssps['VOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
        #---[8-8]: MMACD
        for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM+', 'HISTOGRAM-'):
            ssps['MMACD'].GUIOs[f"INDICATOR_{targetLine}_COLOR"].updateColor(oc[f'MMACD_{targetLine}_ColorR%{cgt}'], 
                                                                             oc[f'MMACD_{targetLine}_ColorG%{cgt}'], 
                                                                             oc[f'MMACD_{targetLine}_ColorB%{cgt}'], 
                                                                             oc[f'MMACD_{targetLine}_ColorA%{cgt}'])
        self.__onSettingsContentUpdate(ssps['MMACD'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
        #---[8-9]: DMIxADX
        for lineIndex in range (_NMAXLINES['DMIxADX']):
            ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}_LINECOLOR"].updateColor(oc[f'DMIxADX_{lineIndex}_ColorR%{cgt}'], 
                                                                                         oc[f'DMIxADX_{lineIndex}_ColorG%{cgt}'], 
                                                                                         oc[f'DMIxADX_{lineIndex}_ColorB%{cgt}'], 
                                                                                         oc[f'DMIxADX_{lineIndex}_ColorA%{cgt}'])
        self.__onSettingsContentUpdate(ssps['DMIxADX'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
        #---[8-10]: MFI
        for lineIndex in range (_NMAXLINES['MFI']):
            ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}_LINECOLOR"].updateColor(oc[f'MFI_{lineIndex}_ColorR%{cgt}'], 
                                                                                 oc[f'MFI_{lineIndex}_ColorG%{cgt}'], 
                                                                                 oc[f'MFI_{lineIndex}_ColorB%{cgt}'], 
                                                                                 oc[f'MFI_{lineIndex}_ColorA%{cgt}'])
        self.__onSettingsContentUpdate(ssps['MFI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
        #---[8-11]: TPD
        for lineIndex in range (_NMAXLINES['TPD']):
            ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_LINECOLOR"].updateColor(oc[f'TPD_{lineIndex}_ColorR%{cgt}'], 
                                                                                 oc[f'TPD_{lineIndex}_ColorG%{cgt}'], 
                                                                                 oc[f'TPD_{lineIndex}_ColorB%{cgt}'], 
                                                                                 oc[f'TPD_{lineIndex}_ColorA%{cgt}'])
        self.__onSettingsContentUpdate(ssps['TPD'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])

        #[9]: Register Redraw Queues
        for ts in self.__drawn:
            for dType in self.__drawn[ts]: 
                self.__drawer_sendDrawSignals(timestamp = ts, analysisCode = dType, redraw = True)

    def on_LanguageUpdate(self, **kwargs):
        #[1]: Instances
        dBox_g       = self.displayBox_graphics
        dBox_g_vSIVs = self.displayBox_graphics_visibleSIViewers

        #[2]: Load Updated TextStyle
        tStyle_eff_new = self.visualManager.getTextStyle('chartDrawer_'+self.textStyle)
        for style_name, style in tStyle_eff_new.items():
            style['font_size'] = self.effectiveTextStyle[style_name]['font_size']
        self.effectiveTextStyle = tStyle_eff_new
        
        #[3]: Grid and Guide Lines & Text Update
        for dBoxName in self.displayBox:
            if dBoxName == 'KLINESPRICE':
                dBox_g['KLINESPRICE']['DESCRIPTIONTEXT1'].on_LanguageUpdate(**kwargs)
                dBox_g['KLINESPRICE']['DESCRIPTIONTEXT2'].on_LanguageUpdate(**kwargs)
                dBox_g['KLINESPRICE']['DESCRIPTIONTEXT3'].on_LanguageUpdate(**kwargs)
                dBox_g['KLINESPRICE']['HORIZONTALGUIDETEXT'].on_LanguageUpdate(**kwargs)
                for gridLineText in dBox_g['MAINGRID_KLINESPRICE']['HORIZONTALGRID_TEXTS']: gridLineText.on_LanguageUpdate(**kwargs)

            elif dBoxName.startswith('SIVIEWER') and (dBoxName in dBox_g_vSIVs):
                siIndex = int(dBoxName[8:])
                dBoxName          = f'SIVIEWER{siIndex}'
                dBoxName_MAINGRID = f'MAINGRID_SIVIEWER{siIndex}'
                dBox_g[dBoxName]['DESCRIPTIONTEXT1'].on_LanguageUpdate(**kwargs)
                dBox_g[dBoxName]['HORIZONTALGUIDETEXT'].on_LanguageUpdate(**kwargs)
                for gridLineText in dBox_g[dBoxName_MAINGRID]['HORIZONTALGRID_TEXTS']: gridLineText.on_LanguageUpdate(**kwargs)

            elif dBoxName == 'MAINGRID_TEMPORAL':
                for gridLineText  in dBox_g['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS']: gridLineText.on_LanguageUpdate(**kwargs)

        #[4]: Klines Loading GaugeBar Related
        self.loadingTextBox_perc.on_LanguageUpdate(**kwargs)
        self.loadingTextBox.on_LanguageUpdate(**kwargs)

        #[5]: Auxiliary Bar Objects
        abp = self.auxBarPage
        aux = auxiliaries
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
                    aux.KLINE_INTERVAL_ID_1M):
            abp.GUIOs[f'AGGINTERVAL_{iID}'].on_LanguageUpdate(**kwargs)
        abp.GUIOs['TARGETTEXT'].on_LanguageUpdate(**kwargs)

        #[6]: Update Settings Subpages
        for ssp in self.settingsSubPages.values(): 
            ssp.on_LanguageUpdate(**kwargs)
    #Basic Object Control END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Auxilliary Bar Control -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __onAggIntervalButtonClick(self, objectInstance):
        #[1]: New Interval
        iID_prev = self.intervalID
        self.intervalID = objectInstance.name

        #[2]: Remove Drawings
        drawn  = self.__drawn
        dQueue = self.__drawQueue
        for key in ('KLINE', 'VOL', 'DEPTH', 'AGGTRADE'):
            for ts in drawn:
                if key not in drawn[ts]: continue
                if ts in dQueue: dQueue[ts][key] = None
                else:            dQueue[ts] = {key: None}

        #[3]: Clear Graphics
        self._clearDrawers()
        self._initializeRCLCGs('KLINESPRICE')
        for sivCode in self.displayBox_graphics_visibleSIViewers: self._initializeSIViewer(sivCode)

        #[4]: Switches Update
        abp_GUIOs = self.auxBarPage.GUIOs
        aux       = auxiliaries
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
            if iID == self.intervalID: continue
            abp_GUIOs[f'AGGINTERVAL_{iID}'].setStatus(status = False, callStatusUpdateFunction = False)

        #[5]: Aggregation
        self._onAggregationIntervalUpdate(previousIntervalID = iID_prev)

        #[6]: View Range Control
        self._setHVRParams()
        self.horizontalViewRange_magnification = 80
        hvr_new_end = self.horizontalViewRange[1]
        hvr_new_beg = round(hvr_new_end-(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
        hvr_new = [hvr_new_beg, hvr_new_end]
        tz_rev  = -self.timezoneDelta
        if hvr_new[0] < tz_rev: hvr_new = [tz_rev, hvr_new[1]-hvr_new[0]+tz_rev]
        self.horizontalViewRange = hvr_new
        self._onHViewRangeUpdate(1)
        self._editVVR_toExtremaCenter('KLINESPRICE')
        for siViewerCode in self.displayBox_graphics_visibleSIViewers: self._editVVR_toExtremaCenter(siViewerCode)

    def _updateTargetText(self, text, textStyle = 'DEFAULT'):
        self.auxBarPage.GUIOs['TARGETTEXT'].updateText(text = text, textStyle = textStyle)
    #Auxilliary Bar Control END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





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
                self._onAnalysisConfigurationUpdate()
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
                self._onAnalysisRangeUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'STARTANALYSIS'):
                self._onStartAnalysis()
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
                    self._drawer_RemoveDrawings(analysisCode = 'TRADELOG', gRemovalSignal = _FULLDRAWSIGNALS['TRADELOG']) #Remove previous graphics
                    self.__addBufferZone_toDrawQueue(analysisCode  = 'TRADELOG', drawSignal     = _FULLDRAWSIGNALS['TRADELOG']) #Update draw queue
                #Control Buttons Handling
                ssps['MAIN'].GUIOs["TRADELOG_APPLYNEWSETTINGS"].deactivate()
                activateSaveConfigButton = True
        #---Bids and Asks
        if indicatorType == 'DEPTHOVERLAY':
            setterType = guioName_split[1]
            if (setterType == 'LineSelectionBox'):
                lineSelected = ssps['MAIN'].GUIOs["DEPTHOVERLAYCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps['MAIN'].GUIOs[f"DEPTHOVERLAYCOLOR_{lineSelected}_LED"].getColor()
                ssps['MAIN'].GUIOs['DEPTHOVERLAYCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps['MAIN'].GUIOs["DEPTHOVERLAYCOLOR_R_VALUE"].updateText(text = f"{color_r}")
                ssps['MAIN'].GUIOs["DEPTHOVERLAYCOLOR_G_VALUE"].updateText(text = f"{color_g}")
                ssps['MAIN'].GUIOs["DEPTHOVERLAYCOLOR_B_VALUE"].updateText(text = f"{color_b}")
                ssps['MAIN'].GUIOs["DEPTHOVERLAYCOLOR_A_VALUE"].updateText(text = f"{color_a}")
                ssps['MAIN'].GUIOs['DEPTHOVERLAYCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps['MAIN'].GUIOs['DEPTHOVERLAYCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps['MAIN'].GUIOs['DEPTHOVERLAYCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps['MAIN'].GUIOs['DEPTHOVERLAYCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps['MAIN'].GUIOs['DEPTHOVERLAYCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):
                cType = guioName_split[2]
                ssps['MAIN'].GUIOs['DEPTHOVERLAYCOLOR_LED'].updateColor(rValue = int(ssps['MAIN'].GUIOs['DEPTHOVERLAYCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                       gValue = int(ssps['MAIN'].GUIOs['DEPTHOVERLAYCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                       bValue = int(ssps['MAIN'].GUIOs['DEPTHOVERLAYCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                       aValue = int(ssps['MAIN'].GUIOs['DEPTHOVERLAYCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps['MAIN'].GUIOs[f'DEPTHOVERLAYCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps['MAIN'].GUIOs[f"DEPTHOVERLAYCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps['MAIN'].GUIOs['DEPTHOVERLAYCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):
                lineSelected = ssps['MAIN'].GUIOs["DEPTHOVERLAYCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps['MAIN'].GUIOs['DEPTHOVERLAYCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps['MAIN'].GUIOs['DEPTHOVERLAYCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps['MAIN'].GUIOs['DEPTHOVERLAYCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps['MAIN'].GUIOs['DEPTHOVERLAYCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps['MAIN'].GUIOs[f"DEPTHOVERLAYCOLOR_{lineSelected}_LED"].updateColor(color_r, color_g, color_b, color_a)
                ssps['MAIN'].GUIOs['DEPTHOVERLAYCOLOR_APPLYCOLOR'].deactivate()
                ssps['MAIN'].GUIOs["DEPTHOVERLAY_APPLYNEWSETTINGS"].activate()
            elif (setterType == 'DisplaySwitch'):
                ssps['MAIN'].GUIOs["DEPTHOVERLAY_APPLYNEWSETTINGS"].activate()
            elif (setterType == 'ApplySettings'):
                #UpdateTracker Initialization
                updateTracker = [False, False]
                #Check for any changes in the configuration
                #---Bids Color
                bidsColor_previous = (oc[f'DEPTHOVERLAY_BIDS_ColorR%{cgt}'], 
                                      oc[f'DEPTHOVERLAY_BIDS_ColorG%{cgt}'], 
                                      oc[f'DEPTHOVERLAY_BIDS_ColorB%{cgt}'], 
                                      oc[f'DEPTHOVERLAY_BIDS_ColorA%{cgt}'])
                color_r, color_g, color_b, color_a = ssps['MAIN'].GUIOs["DEPTHOVERLAYCOLOR_BIDS_LED"].getColor()
                oc[f'DEPTHOVERLAY_BIDS_ColorR%{cgt}'] = color_r
                oc[f'DEPTHOVERLAY_BIDS_ColorG%{cgt}'] = color_g
                oc[f'DEPTHOVERLAY_BIDS_ColorB%{cgt}'] = color_b
                oc[f'DEPTHOVERLAY_BIDS_ColorA%{cgt}'] = color_a
                if (bidsColor_previous != (color_r, color_g, color_b, color_a)): updateTracker[0] = True
                #---Asks Color
                asksColor_previous = (oc[f'DEPTHOVERLAY_ASKS_ColorR%{cgt}'], 
                                      oc[f'DEPTHOVERLAY_ASKS_ColorG%{cgt}'], 
                                      oc[f'DEPTHOVERLAY_ASKS_ColorB%{cgt}'], 
                                      oc[f'DEPTHOVERLAY_ASKS_ColorA%{cgt}'])
                color_r, color_g, color_b, color_a = ssps['MAIN'].GUIOs["DEPTHOVERLAYCOLOR_ASKS_LED"].getColor()
                oc[f'DEPTHOVERLAY_ASKS_ColorR%{cgt}'] = color_r
                oc[f'DEPTHOVERLAY_ASKS_ColorG%{cgt}'] = color_g
                oc[f'DEPTHOVERLAY_ASKS_ColorB%{cgt}'] = color_b
                oc[f'DEPTHOVERLAY_ASKS_ColorA%{cgt}'] = color_a
                if asksColor_previous != (color_r, color_g, color_b, color_a): updateTracker[1] = True
                #---Display
                display_previous = oc['DEPTHOVERLAY_Display']
                oc['DEPTHOVERLAY_Display'] = ssps['MAIN'].GUIOs["DEPTHOVERLAYDISPLAY_SWITCH"].getStatus()
                if display_previous != oc['DEPTHOVERLAY_Display']: 
                    updateTracker[0] = True
                    updateTracker[1] = True
                #Queue Update
                drawSignal = 0
                drawSignal += 0b01*updateTracker[0] #Bids
                drawSignal += 0b10*updateTracker[1] #Asks
                if drawSignal:
                    self._drawer_RemoveDrawings(analysisCode     = 'DEPTHOVERLAY', gRemovalSignal = drawSignal)
                    self.__addBufferZone_toDrawQueue(analysisCode = 'DEPTHOVERLAY', drawSignal     = drawSignal)
                #Control Buttons Handling
                ssps['MAIN'].GUIOs["DEPTHOVERLAY_APPLYNEWSETTINGS"].deactivate()
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
                ap_iID        = self.analysisParams[self.intervalID]
                configuredMAs = set([aCode for aCode in ap_iID if aCode.startswith(miType)])
                for configuredMA in configuredMAs:
                    lineIndex = ap_iID[configuredMA]['lineIndex']
                    if not updateTracker[lineIndex]: continue
                    self._drawer_RemoveDrawings(analysisCode = configuredMA, gRemovalSignal = _FULLDRAWSIGNALS[miType]) #Remove previous graphics
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
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'): 
                lineIndex = int(guioName_split[2])
                #Get new nSamples
                try:    _nSamples = int(ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}_INTERVALINPUT"].getText())
                except: _nSamples = None
                #Save the new value to the object config dictionary
                oc[f'{miType}_{lineIndex}_NSamples'] = _nSamples
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
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
                ap_iID          = self.analysisParams[self.intervalID]
                configuredPSARs = set(aCode for aCode in ap_iID if aCode.startswith('PSAR'))
                for configuredPSAR in configuredPSARs:
                    lineIndex = ap_iID[configuredPSAR]['lineIndex']
                    if updateTracker[lineIndex]:
                        self._drawer_RemoveDrawings(analysisCode = configuredPSAR, gRemovalSignal = _FULLDRAWSIGNALS['PSAR']) #Remove previous graphics
                        self.__addBufferZone_toDrawQueue(analysisCode = configuredPSAR, drawSignal = _FULLDRAWSIGNALS['PSAR']) #Update draw queue
                #Control Buttons Handling
                ssps['PSAR'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'): 
                lineIndex = int(guioName_split[2])
                #Get new switch status
                _newStatus = ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}"].getStatus()
                oc[f'PSAR_{lineIndex}_LineActive'] = _newStatus
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'AF0TextInputBox'):      
                lineIndex = int(guioName_split[2])
                #Get new AF0
                try:    _af0 = round(float(ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}_AF0INPUT"].getText()), 3)
                except: _af0 = None
                #Save the new value to the object config dictionary
                oc[f'PSAR_{lineIndex}_AF0'] = _af0
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'AF+TextInputBox'):      
                lineIndex = int(guioName_split[2])
                #Get new AF+
                try:    _afAccel = round(float(ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}_AF+INPUT"].getText()), 3)
                except: _afAccel = None
                #Save the new value to the object config dictionary
                oc[f'PSAR_{lineIndex}_AF+'] = _afAccel
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'AFMaxTextInputBox'):    
                lineIndex = int(guioName_split[2])
                #Get new AFMax
                try:    _afMax = round(float(ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}_AFMAXINPUT"].getText()), 3)
                except: _afMax = None
                #Save the new value to the object config dictionary
                oc[f'PSAR_{lineIndex}_AFMAX'] = _afMax
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
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
                ap_iID = self.analysisParams[self.intervalID]
                for configuredBOL in (aCode for aCode in ap_iID if aCode.startswith('BOL')):
                    lineIndex = ap_iID[configuredBOL]['lineIndex']
                    drawSignal = 0
                    drawSignal += 0b01*updateTracker[lineIndex][0] #CenterLine
                    drawSignal += 0b10*updateTracker[lineIndex][1] #Band
                    if drawSignal:
                        self._drawer_RemoveDrawings(analysisCode = configuredBOL, gRemovalSignal = drawSignal) #Remove previous graphics
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
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'):  
                lineIndex = int(guioName_split[2])
                #Get new nSamples
                try:    nSamples = int(ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineIndex}_INTERVALINPUT"].getText())
                except: nSamples = None
                #Save the new value to the object config dictionary
                oc[f'BOL_{lineIndex}_NSamples'] = nSamples
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'BandWidthTextInputBox'): 
                lineIndex = int(guioName_split[2])
                #Get new bandwidth
                try:    bandWidth = int(ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineIndex}_BANDWIDTHINPUT"].getText())
                except: bandWidth = None
                #Save the new value to the object config dictionary
                oc[f'BOL_{lineIndex}_BandWidth'] = bandWidth
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'MATypeSelection'): 
                #Get new MAType
                maType = ssps['BOL'].GUIOs["INDICATOR_MATYPESELECTION"].getSelected()
                #Save the new value to the object config dictionary
                oc['BOL_MAType'] = maType
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
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
                    self._drawer_RemoveDrawings(analysisCode = 'IVP', gRemovalSignal = drawSignal) #Remove previous graphics
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
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'GammaFactor'):
                #Get new Gamma Factor
                gammaFactor = round(ssps['IVP'].GUIOs["INDICATOR_GAMMAFACTOR_SLIDER"].getSliderValue()/100*0.095+0.005, 3)
                ssps['IVP'].GUIOs["INDICATOR_GAMMAFACTOR_VALUETEXT"].updateText(f"{gammaFactor*100:.1f} %")
                oc['IVP_GammaFactor'] = gammaFactor
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'DeltaFactor'):
                #Get new Delta Factor
                deltaFactor = round(ssps['IVP'].GUIOs["INDICATOR_DELTAFACTOR_SLIDER"].getSliderValue()/100*9.9+0.1, 1)
                ssps['IVP'].GUIOs["INDICATOR_DELTAFACTOR_VALUETEXT"].updateText(f"{int(deltaFactor*100)} %")
                oc['IVP_DeltaFactor'] = deltaFactor
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
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
                ap_iID = self.analysisParams[self.intervalID]
                for configuredSWING in (aCode for aCode in ap_iID if aCode.startswith('SWING')):
                    lineIndex = ap_iID[configuredSWING]['lineIndex']
                    if updateTracker[lineIndex]:
                        self._drawer_RemoveDrawings(analysisCode = configuredSWING, gRemovalSignal = _FULLDRAWSIGNALS['SWING']) #Remove previous graphics
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
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'SwingRangeTextInputBox'):
                lineIndex = int(guioName_split[2])
                #Get new Swing Range
                try:    swingRange = round(float(ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT"].getText()), 4)
                except: swingRange = None
                #Save the new value to the object config dictionary
                oc[f'SWING_{lineIndex}_SwingRange'] = swingRange
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
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
            elif (setterType == 'VolTypeSelection'):
                ssps['VOL'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):     
                #UpdateTracker Initialization
                updateTracker = {'VOL': False}
                #Check for any changes in the configuration
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
                volMaster_updated = (volMaster_previous != oc['VOL_Master'])
                if volMaster_updated:
                    for targetLine in updateTracker: updateTracker[targetLine] = True
                #---VOL Type
                volType_previous = oc['VOL_VolumeType']
                oc['VOL_VolumeType'] = ssps['VOL'].GUIOs["INDICATOR_VOLTYPESELECTION"].getSelected()
                volumeType_updated = (volType_previous != oc['VOL_VolumeType'])
                if volumeType_updated:
                    for targetLine in updateTracker: updateTracker[targetLine] = True
                #Extrema Recomputation
                if any(updateTracker[lIndex] for lIndex in updateTracker):
                    siViewerIndex = self.siTypes_siViewerAlloc['VOL']
                    siViewerCode  = f"SIVIEWER{siViewerIndex}"
                    if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                        if self.checkVerticalExtremas_SIs['VOL'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.0, extension_t = 0.2)
                #Queue Update
                if updateTracker['VOL']:
                    self._drawer_RemoveDrawings(analysisCode = 'VOL', gRemovalSignal = _FULLDRAWSIGNALS['VOL']) #Remove previous graphics
                    self.__addBufferZone_toDrawQueue(analysisCode  = 'VOL', drawSignal     = _FULLDRAWSIGNALS['VOL']) #Update draw queue
                ap_iID = self.analysisParams[self.intervalID]
                for configuredVOL in (aCode for aCode in ap_iID if aCode.startswith('VOL')):
                    lineIndex = ap_iID[configuredVOL]['lineIndex']
                    if updateTracker[lineIndex]:
                        self._drawer_RemoveDrawings(analysisCode = configuredVOL, gRemovalSignal = _FULLDRAWSIGNALS['VOL']) #Remove previous graphics
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
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'): 
                lineIndex = int(guioName_split[2])
                #Get new nSamples
                try:    _nSamples = int(ssps['VOL'].GUIOs[f"INDICATOR_VOL{lineIndex}_INTERVALINPUT"].getText())
                except: _nSamples = None
                #Save the new value to the object config dictionary
                oc[f'VOL_{lineIndex}_NSamples'] = _nSamples
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'MATypeSelection'): 
                #Get new MAType
                maType = ssps['VOL'].GUIOs["INDICATOR_MATYPESELECTION"].getSelected()
                #Save the new value to the object config dictionary
                oc['VOL_MAType'] = maType
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True

        #Subpage 'DEPTH'
        elif indicatorType == 'DEPTH':
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):    
                lineSelected = ssps['DEPTH'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps['DEPTH'].GUIOs[f"INDICATOR_{lineSelected}_LINECOLOR"].getColor()
                ssps['DEPTH'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps['DEPTH'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                ssps['DEPTH'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                ssps['DEPTH'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                ssps['DEPTH'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                ssps['DEPTH'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps['DEPTH'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps['DEPTH'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps['DEPTH'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps['DEPTH'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):             
                cType = guioName_split[2]
                ssps['DEPTH'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['DEPTH'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                      gValue = int(ssps['DEPTH'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                      bValue = int(ssps['DEPTH'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                      aValue = int(ssps['DEPTH'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps['DEPTH'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps['DEPTH'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps['DEPTH'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):        
                lineSelected = ssps['DEPTH'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps['DEPTH'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps['DEPTH'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps['DEPTH'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps['DEPTH'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps['DEPTH'].GUIOs[f"INDICATOR_{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
                ssps['DEPTH'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                ssps['DEPTH'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):     
                #UpdateTracker Initialization
                updateTracker = [False, False]
                #Check for any changes in the configuration siTypes_analysisCodes
                #---Bids Color
                bidsColor_previous = (oc[f'DEPTH_BIDS_ColorR%{cgt}'], 
                                      oc[f'DEPTH_BIDS_ColorG%{cgt}'], 
                                      oc[f'DEPTH_BIDS_ColorB%{cgt}'], 
                                      oc[f'DEPTH_BIDS_ColorA%{cgt}'])
                color_r, color_g, color_b, color_a = ssps['DEPTH'].GUIOs["INDICATOR_BIDS_LINECOLOR"].getColor()
                oc[f'DEPTH_BIDS_ColorR%{cgt}'] = color_r
                oc[f'DEPTH_BIDS_ColorG%{cgt}'] = color_g
                oc[f'DEPTH_BIDS_ColorB%{cgt}'] = color_b
                oc[f'DEPTH_BIDS_ColorA%{cgt}'] = color_a
                if bidsColor_previous != (color_r, color_g, color_b, color_a): updateTracker[0] = True
                #---Asks Color
                asksColor_previous = (oc[f'DEPTH_ASKS_ColorR%{cgt}'], 
                                      oc[f'DEPTH_ASKS_ColorG%{cgt}'], 
                                      oc[f'DEPTH_ASKS_ColorB%{cgt}'], 
                                      oc[f'DEPTH_ASKS_ColorA%{cgt}'])
                color_r, color_g, color_b, color_a = ssps['DEPTH'].GUIOs["INDICATOR_ASKS_LINECOLOR"].getColor()
                oc[f'DEPTH_ASKS_ColorR%{cgt}'] = color_r
                oc[f'DEPTH_ASKS_ColorG%{cgt}'] = color_g
                oc[f'DEPTH_ASKS_ColorB%{cgt}'] = color_b
                oc[f'DEPTH_ASKS_ColorA%{cgt}'] = color_a
                if asksColor_previous != (color_r, color_g, color_b, color_a): updateTracker[1] = True
                #---Display
                depthMaster_previous = oc['DEPTH_Master']
                oc['DEPTH_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_DEPTH"].getStatus()
                depthMaster_updated = (depthMaster_previous != oc['DEPTH_Master'])
                if depthMaster_updated:
                    updateTracker[0] = True
                    updateTracker[1] = True
                #Extrema Recomputation
                if any(updateTracker):
                    sivIdx  = self.siTypes_siViewerAlloc['DEPTH']
                    sivCode = f"SIVIEWER{sivIdx}"
                    if sivCode in self.displayBox_graphics_visibleSIViewers:
                        if self.checkVerticalExtremas_SIs['DEPTH'](): self._editVVR_toExtremaCenter(displayBoxName = sivCode, extension_b = 0.1, extension_t = 0.1)
                #Queue Update
                drawSignal = 0
                drawSignal += 0b01*updateTracker[0] #Bids
                drawSignal += 0b10*updateTracker[1] #Asks
                if drawSignal:
                    self._drawer_RemoveDrawings(analysisCode     = 'DEPTH', gRemovalSignal = drawSignal)
                    self.__addBufferZone_toDrawQueue(analysisCode = 'DEPTH', drawSignal     = drawSignal)
                #Control Buttons Handling
                ssps['DEPTH'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True

        #Subpage 'AGGTRADE'
        elif indicatorType == 'AGGTRADE':
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):    
                lineSelected = ssps['AGGTRADE'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps['AGGTRADE'].GUIOs[f"INDICATOR_{lineSelected}_LINECOLOR"].getColor()
                ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps['AGGTRADE'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                ssps['AGGTRADE'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                ssps['AGGTRADE'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                ssps['AGGTRADE'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):             
                cType = guioName_split[2]
                ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                         gValue = int(ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                         bValue = int(ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                         aValue = int(ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps['AGGTRADE'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps['AGGTRADE'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):        
                lineSelected = ssps['AGGTRADE'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps['AGGTRADE'].GUIOs[f"INDICATOR_{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
                ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                ssps['AGGTRADE'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplayTypeSelection'):
                ssps['AGGTRADE'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):     
                #UpdateTracker Initialization
                updateTracker = [False, False]
                #Check for any changes in the configuration siTypes_analysisCodes
                #---Buy Color
                buyColor_previous = (oc[f'AGGTRADE_BUY_ColorR%{cgt}'], 
                                     oc[f'AGGTRADE_BUY_ColorG%{cgt}'], 
                                     oc[f'AGGTRADE_BUY_ColorB%{cgt}'], 
                                     oc[f'AGGTRADE_BUY_ColorA%{cgt}'])
                color_r, color_g, color_b, color_a = ssps['AGGTRADE'].GUIOs["INDICATOR_BUY_LINECOLOR"].getColor()
                oc[f'AGGTRADE_BUY_ColorR%{cgt}'] = color_r
                oc[f'AGGTRADE_BUY_ColorG%{cgt}'] = color_g
                oc[f'AGGTRADE_BUY_ColorB%{cgt}'] = color_b
                oc[f'AGGTRADE_BUY_ColorA%{cgt}'] = color_a
                if buyColor_previous != (color_r, color_g, color_b, color_a): updateTracker[0] = True
                #---Sell Color
                sellColor_previous = (oc[f'AGGTRADE_SELL_ColorR%{cgt}'], 
                                      oc[f'AGGTRADE_SELL_ColorG%{cgt}'], 
                                      oc[f'AGGTRADE_SELL_ColorB%{cgt}'], 
                                      oc[f'AGGTRADE_SELL_ColorA%{cgt}'])
                color_r, color_g, color_b, color_a = ssps['AGGTRADE'].GUIOs["INDICATOR_SELL_LINECOLOR"].getColor()
                oc[f'AGGTRADE_SELL_ColorR%{cgt}'] = color_r
                oc[f'AGGTRADE_SELL_ColorG%{cgt}'] = color_g
                oc[f'AGGTRADE_SELL_ColorB%{cgt}'] = color_b
                oc[f'AGGTRADE_SELL_ColorA%{cgt}'] = color_a
                if sellColor_previous != (color_r, color_g, color_b, color_a): updateTracker[1] = True
                #---Display Type
                displayType_previous = oc['AGGTRADE_DisplayType']
                oc['AGGTRADE_DisplayType'] = ssps['AGGTRADE'].GUIOs["INDICATOR_DISPLAYTYPESELECTION"].getSelected()
                displayType_updated = (displayType_previous != oc['AGGTRADE_DisplayType'])
                if displayType_updated:
                    updateTracker[0] = True
                    updateTracker[1] = True
                #---Display
                aggTradeMaster_previous = oc['AGGTRADE_Master']
                oc['AGGTRADE_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_AGGTRADE"].getStatus()
                aggTradeMaster_updated = (aggTradeMaster_previous != oc['AGGTRADE_Master'])
                if aggTradeMaster_updated:
                    updateTracker[0] = True
                    updateTracker[1] = True
                #Extrema Recomputation
                if any(updateTracker):
                    sivIdx  = self.siTypes_siViewerAlloc['AGGTRADE']
                    sivCode = f"SIVIEWER{sivIdx}"
                    if sivCode in self.displayBox_graphics_visibleSIViewers:
                        if self.checkVerticalExtremas_SIs['AGGTRADE'](): self._editVVR_toExtremaCenter(displayBoxName = sivCode, extension_b = 0.1, extension_t = 0.1)
                #Queue Update
                drawSignal = 0
                drawSignal += 0b01*updateTracker[0] #Buy
                drawSignal += 0b10*updateTracker[1] #Sell
                if drawSignal:
                    self._drawer_RemoveDrawings(analysisCode     = 'AGGTRADE', gRemovalSignal = drawSignal)
                    self.__addBufferZone_toDrawQueue(analysisCode = 'AGGTRADE', drawSignal     = drawSignal)
                #Control Buttons Handling
                ssps['AGGTRADE'].GUIOs['APPLYNEWSETTINGS'].deactivate()
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
                #Extrema Recomputation
                if any(updateTracker[lIndex] for lIndex in updateTracker):
                    siViewerIndex = self.siTypes_siViewerAlloc['NNA']
                    siViewerCode  = f"SIVIEWER{siViewerIndex}"
                    if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                        if self.checkVerticalExtremas_SIs['NNA'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                #Queue Update
                ap_iID = self.analysisParams[self.intervalID]
                for configuredNNA in (aCode for aCode in ap_iID if aCode.startswith('NNA')):
                    lineIndex = ap_iID[configuredNNA]['lineIndex']
                    if updateTracker[lineIndex]:
                        self._drawer_RemoveDrawings(analysisCode = configuredNNA, gRemovalSignal = _FULLDRAWSIGNALS['NNA']) #Remove previous graphics
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
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'NNCodeTextInputBox'): 
                lineIndex = int(guioName_split[2])
                #Get new Neural Network Code
                try:    nnCode = ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_NNCODEINPUT"].getText()
                except: nnCode = None
                #Save the new value to the object config dictionary
                oc[f'NNA_{lineIndex}_NeuralNetworkCode'] = nnCode
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'AlphaTextInputBox'): 
                lineIndex = int(guioName_split[2])
                #Get new Alpha
                try:    alpha = round(float(ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_ALPHAINPUT"].getText()), 2)
                except: alpha = None
                #Save the new value to the object config dictionary
                oc[f'NNA_{lineIndex}_Alpha'] = alpha
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'BetaTextInputBox'): 
                lineIndex = int(guioName_split[2])
                #Get new Beta
                try:    beta = int(ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_BETAINPUT"].getText())
                except: beta = None
                #Save the new value to the object config dictionary
                oc[f'NNA_{lineIndex}_Beta'] = beta
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True

        #Subpage 'MMACD'
        elif indicatorType == 'MMACD':
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'): 
                lineSelected = ssps['MMACD'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps['MMACD'].GUIOs[f"INDICATOR_{lineSelected}_COLOR"].getColor()
                ssps['MMACD'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps['MMACD'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                ssps['MMACD'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                ssps['MMACD'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                ssps['MMACD'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                ssps['MMACD'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps['MMACD'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps['MMACD'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps['MMACD'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps['MMACD'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):          
                cType = guioName_split[2]
                ssps['MMACD'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                      gValue = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                      bValue = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                      aValue = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps['MMACD'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps['MMACD'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps['MMACD'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):     
                lineSelected = ssps['MMACD'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps['MMACD'].GUIOs[f"INDICATOR_{lineSelected}_COLOR"].updateColor(color_r, color_g, color_b, color_a)
                ssps['MMACD'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                ssps['MMACD'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):  
                ssps['MMACD'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'HistrogramTypeSelectionBox'):
                ssps['MMACD'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):  
                #UpdateTracker Initialization
                updateTracker = [False, False, False] #[0]: Draw MMACD, [1]: Draw SIGNAL, [2]: Draw HISTOGRAM
                #Check for any changes in the configuration
                #---MMACD Master
                mmacdMaster_previous = oc['MMACD_Master']
                oc['MMACD_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_MMACD"].getStatus()
                if mmacdMaster_previous != oc['MMACD_Master']: 
                    updateTracker[0] = True
                    updateTracker[1] = True
                    updateTracker[2] = True
                #---Colors
                for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM+', 'HISTOGRAM-'):
                    color_previous = (oc[f'MMACD_{targetLine}_ColorR%{cgt}'],
                                      oc[f'MMACD_{targetLine}_ColorG%{cgt}'],
                                      oc[f'MMACD_{targetLine}_ColorB%{cgt}'],
                                      oc[f'MMACD_{targetLine}_ColorA%{cgt}'])
                    color_r, color_g, color_b, color_a = ssps['MMACD'].GUIOs[f"INDICATOR_{targetLine}_COLOR"].getColor()
                    oc[f'MMACD_{targetLine}_ColorR%{cgt}'] = color_r
                    oc[f'MMACD_{targetLine}_ColorG%{cgt}'] = color_g
                    oc[f'MMACD_{targetLine}_ColorB%{cgt}'] = color_b
                    oc[f'MMACD_{targetLine}_ColorA%{cgt}'] = color_a
                    if (color_previous != (color_r, color_g, color_b, color_a)): 
                        if   (targetLine == 'MMACD'):      updateTracker[0] = True
                        elif (targetLine == 'SIGNAL'):     updateTracker[1] = True
                        elif (targetLine == 'HISTOGRAM+'): updateTracker[2] = True
                        elif (targetLine == 'HISTOGRAM-'): updateTracker[2] = True
                #---Line Display
                for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM'):
                    displayStatus_prev = oc[f'MMACD_{targetLine}_Display']
                    oc[f'MMACD_{targetLine}_Display'] = ssps['MMACD'].GUIOs[f"INDICATOR_{targetLine}_DISPLAYSWITCH"].getStatus()
                    if displayStatus_prev != oc[f'MMACD_{targetLine}_Display']:
                        if   targetLine == 'MMACD':     updateTracker[0] = True
                        elif targetLine == 'SIGNAL':    updateTracker[1] = True
                        elif targetLine == 'HISTOGRAM': updateTracker[2] = True
                #---Histogram Type
                histogramType_prev = oc['MMACD_HISTOGRAM_Type']
                oc['MMACD_HISTOGRAM_Type'] = ssps['MMACD'].GUIOs["INDICATOR_HISTOGRAMTYPE_SELECTION"].getSelected()
                if histogramType_prev != oc['MMACD_HISTOGRAM_Type']:
                    updateTracker[2] = True
                #Extrema Recomputation
                if any(updateTracker):
                    siViewerIndex = self.siTypes_siViewerAlloc['MMACD']
                    siViewerCode  = f"SIVIEWER{siViewerIndex}"
                    if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                        if self.checkVerticalExtremas_SIs['MMACD'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                #Queue Update
                drawSignal = 0
                drawSignal += 0b001*updateTracker[0] #MMACD
                drawSignal += 0b010*updateTracker[1] #SIGNAL
                drawSignal += 0b100*updateTracker[2] #HISTOGRAM
                if drawSignal:
                    self._drawer_RemoveDrawings(analysisCode = 'MMACD', gRemovalSignal = drawSignal) #Remove previous graphics
                    self.__addBufferZone_toDrawQueue(analysisCode  = 'MMACD', drawSignal     = drawSignal) #Update draw queue
                #Control Buttons Handling
                ssps['MMACD'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'):          
                lineIndex = int(guioName_split[2])
                #Get new switch status
                newStatus = ssps['MMACD'].GUIOs[f"INDICATOR_MMACDMA{lineIndex}"].getStatus()
                oc[f'MMACD_MA{lineIndex}_LineActive'] = newStatus
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'):          
                lineIndex = int(guioName_split[2])
                #Get new nSamples
                try:    nSamples = int(ssps['MMACD'].GUIOs[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].getText())
                except: nSamples = None
                #Save the new value to the object config dictionary
                oc[f'MMACD_MA{lineIndex}_NSamples'] = nSamples
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'SignalIntervalTextInputBox'):    
                #Get new nSamples
                try:    nSamples = int(ssps['MMACD'].GUIOs["INDICATOR_SIGNALINTERVALTEXTINPUT"].getText())
                except: nSamples = None
                #Save the new value to the object config dictionary
                oc['MMACD_SignalNSamples'] = nSamples
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
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
                #Extrema Recomputation
                if any(updateTracker[lIndex] for lIndex in updateTracker):
                    siViewerIndex = self.siTypes_siViewerAlloc['DMIxADX']
                    siViewerCode  = f"SIVIEWER{siViewerIndex}"
                    if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                        if self.checkVerticalExtremas_SIs['DMIxADX'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                #Queue Update
                ap_iID = self.analysisParams[self.intervalID]
                for configuredDMIxADX in (aCode for aCode in ap_iID if aCode.startswith('DMIxADX')):
                    lineIndex = ap_iID[configuredDMIxADX]['lineIndex']
                    if updateTracker[lineIndex]:
                        self._drawer_RemoveDrawings(analysisCode = configuredDMIxADX, gRemovalSignal = _FULLDRAWSIGNALS['DMIxADX']) #Remove previous graphics
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
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'): 
                lineIndex = int(guioName_split[2])
                #Get new nSamples
                try:    nSamples = int(ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT"].getText())
                except: nSamples = None
                #Save the new value to the object config dictionary
                oc[f'DMIxADX_{lineIndex}_NSamples'] = nSamples
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
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
                #Extrema Recomputation
                if any(updateTracker[lIndex] for lIndex in updateTracker):
                    siViewerIndex = self.siTypes_siViewerAlloc['MFI']
                    siViewerCode  = f"SIVIEWER{siViewerIndex}"
                    if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                        if self.checkVerticalExtremas_SIs['MFI'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                #Queue Update
                ap_iID = self.analysisParams[self.intervalID]
                for configuredMFI in (aCode for aCode in ap_iID if aCode.startswith('MFI')):
                    lineIndex = ap_iID[configuredMFI]['lineIndex']
                    if updateTracker[lineIndex]:
                        self._drawer_RemoveDrawings(analysisCode = configuredMFI, gRemovalSignal = _FULLDRAWSIGNALS['MFI']) #Remove previous graphics
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
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'): 
                lineIndex = int(guioName_split[2])
                #Get new nSamples
                try:    nSamples = int(ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}_INTERVALINPUT"].getText())
                except: nSamples = None
                #Save the new value to the object config dictionary
                oc[f'MFI_{lineIndex}_NSamples'] = nSamples
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True

        #Subpage 'TPD'
        elif indicatorType == 'TPD':
            setterType = guioName_split[1]
            #Graphics Related
            if (setterType == 'LineSelectionBox'):    
                lineSelected = ssps['TPD'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r, color_g, color_b, color_a = ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineSelected}_LINECOLOR"].getColor()
                ssps['TPD'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
                ssps['TPD'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
                ssps['TPD'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
                ssps['TPD'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
                ssps['TPD'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
                ssps['TPD'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
                ssps['TPD'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
                ssps['TPD'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
                ssps['TPD'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
                ssps['TPD'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
            elif (setterType == 'Color'):             
                cType = guioName_split[2]
                ssps['TPD'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['TPD'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                    gValue = int(ssps['TPD'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                    bValue = int(ssps['TPD'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                    aValue = int(ssps['TPD'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
                color_target_new = int(ssps['TPD'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
                ssps['TPD'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
                ssps['TPD'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
            elif (setterType == 'ApplyColor'):        
                lineSelected = ssps['TPD'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
                color_r = int(ssps['TPD'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
                color_g = int(ssps['TPD'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
                color_b = int(ssps['TPD'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
                color_a = int(ssps['TPD'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
                ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
                ssps['TPD'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
                ssps['TPD'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'WidthTextInputBox'): 
                ssps['TPD'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'DisplaySwitch'):     
                ssps['TPD'].GUIOs['APPLYNEWSETTINGS'].activate()
            elif (setterType == 'ApplySettings'):     
                #UpdateTracker Initialization
                updateTracker = dict()
                #Check for any changes in the configuration
                for lineIndex in range (_NMAXLINES['TPD']):
                    updateTracker[lineIndex] = False
                    #Width
                    width_previous = oc[f'TPD_{lineIndex}_Width']
                    reset = False
                    try:
                        width = int(ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].getText())
                        if 0 < width: oc[f'TPD_{lineIndex}_Width'] = width
                        else: reset = True
                    except: reset = True
                    if reset:
                        oc[f'TPD_{lineIndex}_Width'] = 1
                        ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'TPD_{lineIndex}_Width']))
                    if width_previous != oc[f'TPD_{lineIndex}_Width']: updateTracker[lineIndex] = True
                    #Color
                    color_previous = (oc[f'TPD_{lineIndex}_ColorR%{cgt}'], 
                                      oc[f'TPD_{lineIndex}_ColorG%{cgt}'], 
                                      oc[f'TPD_{lineIndex}_ColorB%{cgt}'], 
                                      oc[f'TPD_{lineIndex}_ColorA%{cgt}'])
                    color_r, color_g, color_b, color_a = ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_LINECOLOR"].getColor()
                    oc[f'TPD_{lineIndex}_ColorR%{cgt}'] = color_r
                    oc[f'TPD_{lineIndex}_ColorG%{cgt}'] = color_g
                    oc[f'TPD_{lineIndex}_ColorB%{cgt}'] = color_b
                    oc[f'TPD_{lineIndex}_ColorA%{cgt}'] = color_a
                    if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
                    #Line Display
                    display_previous = oc[f'TPD_{lineIndex}_Display']
                    oc[f'TPD_{lineIndex}_Display'] = ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_DISPLAY"].getStatus()
                    if display_previous != oc[f'TPD_{lineIndex}_Display']: updateTracker[lineIndex] = True
                #---TPD Master
                tpdMaster_previous = oc['TPD_Master']
                oc['TPD_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_TPD"].getStatus()
                if tpdMaster_previous != oc['TPD_Master']:
                    for lineIndex in updateTracker: updateTracker[lineIndex] = True
                #Extrema Recomputation
                if any(updateTracker[lIndex] for lIndex in updateTracker):
                    siViewerIndex = self.siTypes_siViewerAlloc['TPD']
                    siViewerCode  = f"SIVIEWER{siViewerIndex}"
                    if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                        if self.checkVerticalExtremas_SIs['TPD'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                #Queue Update
                ap_iID = self.analysisParams[self.intervalID]
                for configuredTPD in (aCode for aCode in ap_iID if aCode.startswith('TPD')):
                    lineIndex = ap_iID[configuredTPD]['lineIndex']
                    if updateTracker[lineIndex]:
                        self._drawer_RemoveDrawings(analysisCode = configuredTPD, gRemovalSignal = _FULLDRAWSIGNALS['TPD']) #Remove previous graphics
                        self.__addBufferZone_toDrawQueue(analysisCode  = configuredTPD, drawSignal     = _FULLDRAWSIGNALS['TPD']) #Update draw queue
                #Control Buttons Handling
                ssps['TPD'].GUIOs['APPLYNEWSETTINGS'].deactivate()
                activateSaveConfigButton = True
            #Analysis Related
            elif (setterType == 'LineActivationSwitch'): 
                lineIndex = int(guioName_split[2])
                #Get new switch status
                newStatus = ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}"].getStatus()
                oc[f'TPD_{lineIndex}_LineActive'] = newStatus
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'ViewLengthTextInputBox'): 
                lineIndex = int(guioName_split[2])
                #Get new nSamples
                try:    viewLength = int(ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT"].getText())
                except: viewLength = None
                #Save the new value to the object config dictionary
                oc[f'TPD_{lineIndex}_ViewLength'] = viewLength
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'IntervalTextInputBox'): 
                lineIndex = int(guioName_split[2])
                #Get new nSamples
                try:    nSamples = int(ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_INTERVALINPUT"].getText())
                except: nSamples = None
                #Save the new value to the object config dictionary
                oc[f'TPD_{lineIndex}_NSamples'] = nSamples
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True
            elif (setterType == 'MAIntervalTextInputBox'): 
                lineIndex = int(guioName_split[2])
                #Get new nSamples
                try:    nSamplesMA = int(ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT"].getText())
                except: nSamplesMA = None
                #Save the new value to the object config dictionary
                oc[f'TPD_{lineIndex}_NSamplesMA'] = nSamplesMA
                #Analysis Configuration Update Response
                self._onAnalysisConfigurationUpdate()
                activateSaveConfigButton = True

        if activateSaveConfigButton and ssps['MAIN'].GUIOs["AUX_SAVECONFIGURATION"].deactivated: ssps['MAIN'].GUIOs["AUX_SAVECONFIGURATION"].activate()

    def updateKlineColors(self, newType):
        if newType not in (1, 2): return False
        self.objectConfig['KlineColorType'] = newType
        self.settingsSubPages['MAIN'].GUIOs["AUX_KLINECOLORTYPE_SELECTIONBOX"].setSelected(newType, callSelectionUpdateFunction = False)
        drawn  = self.__drawn
        dQueue = self.__drawQueue
        for key in ('KLINE', 'VOL'):
            for ts in drawn:
                if key not in drawn[ts]: continue
                if ts in dQueue: dQueue[ts][key] = None
                else:            dQueue[ts] = {key: None}
        return True
        
    def updateTimeZone(self, newTimeZone):
        #[1]: Object Configuration Update
        self.objectConfig['TimeZone'] = newTimeZone

        #[2]: TimeZone Delta Update
        if   newTimeZone == 'LOCAL':        self.timezoneDelta = -time.timezone
        elif newTimeZone.startswith('UTC'): self.timezoneDelta = int(newTimeZone.split("+")[1])*3600

        #[3]: Update Vertical Grids
        if self.horizontalViewRange[0] is not None:
            tz_rev           = -self.timezoneDelta
            hvr_beg, hvr_end = self.horizontalViewRange
            if hvr_beg < tz_rev:
                self.horizontalViewRange = [tz_rev, hvr_end-hvr_beg+tz_rev]
            self._onHViewRangeUpdate(updateType = 1)
    #Configuration Update Control END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Drawing --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __addBufferZone_toDrawQueue(self, analysisCode, drawSignal):
        #[1]: Instances
        dRaw   = self._data_raw
        dAgg   = self._data_agg[self.intervalID]
        dQueue = self.__drawQueue
        
        #[2]: Data
        if   analysisCode == 'VOL':          aData = dAgg['kline']
        elif analysisCode == 'DEPTH':        aData = dAgg['depth']
        elif analysisCode == 'DEPTHOVERLAY': aData = dAgg['depth']
        elif analysisCode == 'AGGTRADE':     aData = dAgg['aggTrade']
        elif analysisCode in dAgg:           aData = dAgg[analysisCode]
        elif analysisCode == 'TRADELOG':     aData = dRaw['tradeLog']
        else: return

        #[3]: Draw Queue Update
        for ts in itertools.chain(self.horizontalViewRange_timestampsInViewRange, self.horizontalViewRange_timestampsInBufferZone):
            if ts not in aData: continue
            dQueue_ts = dQueue.get(ts, None)
            if dQueue_ts is None:
                dQueue[ts] = {analysisCode: drawSignal}
            else:
                if analysisCode in dQueue_ts and dQueue_ts[analysisCode] is not None: dQueue_ts[analysisCode] |= drawSignal
                else:                                                                 dQueue_ts[analysisCode]  = drawSignal

    def _addDrawQueue(self, targetCodes, timestamp):
        #[1]: Instances
        dQueue           = self.__drawQueue
        hvr_beg, hvr_end = self.horizontalViewRange

        #[2]: Classification
        ts_open  = timestamp
        ts_close = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = ts_open, nTicks = 1)-1
        classification = 0
        classification += 0b1000*(0 <= ts_open -hvr_beg)
        classification += 0b0100*(0 <= ts_open -hvr_end)
        classification += 0b0010*(0 <  ts_close-hvr_beg)
        classification += 0b0001*(0 <  ts_close-hvr_end)
        if classification not in (0b0010, 0b1010, 0b1011, 0b0011):
            return

        #[3]: Queue Update
        for tCode in targetCodes:
            if ts_open in dQueue: dQueue[ts_open][tCode] = None
            else:                 dQueue[ts_open] = {tCode: None}

    def _clearDrawers(self):
        self.__drawQueue        = dict()
        self.__drawn            = dict()
        self.__drawRemovalQueue = set()
    
    def __drawer_sendDrawSignals(self, timestamp, analysisCode, redraw = False):
        try:
            if redraw: drawSignal = None
            else:      drawSignal = self.__drawQueue[timestamp][analysisCode]
            drawn = self.__drawerFunctions[analysisCode.split("_")[0]](drawSignal = drawSignal, timestamp = timestamp, analysisCode = analysisCode)
            if not drawn: return
            if timestamp in self.__drawn:
                if analysisCode in self.__drawn[timestamp]: self.__drawn[timestamp][analysisCode] |= drawn
                else:                                       self.__drawn[timestamp][analysisCode] = drawn
            else:                                           self.__drawn[timestamp] = {analysisCode: drawn}
        except Exception as e: print(termcolor.colored(f"An unexpected error occured while attempting to draw {analysisCode} at {timestamp}\n *", 'light_yellow'), termcolor.colored(e, 'light_yellow'))

    def __drawer_KLINE(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        kline = self._data_agg[self.intervalID]['kline'][timestamp]

        #[2]: Dummy Check
        if kline[KLINDEX_SOURCE] in (FORMATTEDDATATYPE_EMPTY, FORMATTEDDATATYPE_DUMMY):
            return 0b1

        ts_open  = kline[KLINDEX_OPENTIME]
        ts_close = kline[KLINDEX_CLOSETIME]
        p_open   = kline[KLINDEX_OPENPRICE]
        p_high   = kline[KLINDEX_HIGHPRICE]
        p_low    = kline[KLINDEX_LOWPRICE]
        p_close  = kline[KLINDEX_CLOSEPRICE]

        #[3]: Width determination
        tsWidth = ts_close-ts_open+1
        body_width = round(tsWidth*0.9, 1)
        body_xPos  = round(ts_open+(tsWidth-body_width)/2, 1)
        tail_width = round(tsWidth/5, 1)
        tail_xPos  = round(ts_open+(tsWidth-tail_width)/2, 1)

        #[4]: Color & Height determination
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

        #[5]: Drawing
        if (0 < body_height): 
            self.displayBox_graphics['KLINESPRICE']['RCLCG'].addShape_Rectangle(x      = body_xPos, 
                                                                                y      = body_bottom, 
                                                                                width  = body_width, 
                                                                                height = body_height, 
                                                                                color = candleColor, 
                                                                                shapeName = ts_open, shapeGroupName = 'KLINEBODIES', layerNumber = 12)
        else:                 
            self.displayBox_graphics['KLINESPRICE']['RCLCG'].addShape_Line(x  = body_xPos, 
                                                                           y  = body_bottom, 
                                                                           x2 = body_xPos+body_width, 
                                                                           y2 = body_bottom, 
                                                                           width_y = 1, 
                                                                           color = candleColor, 
                                                                           shapeName = ts_open, shapeGroupName = 'KLINEBODIES', layerNumber = 12)
        self.displayBox_graphics['KLINESPRICE']['RCLCG'].addShape_Rectangle(x = tail_xPos, 
                                                                            y = tail_bottom, 
                                                                            width = tail_width, 
                                                                            height = tail_height, 
                                                                            color = candleColor, 
                                                                            shapeName = ts_open, shapeGroupName = 'KLINETAILS', layerNumber = 12)
        
        #[6]: Return Drawn Flag
        return 0b1

    def __drawer_DEPTHOVERLAY(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc    = self.objectConfig
        cgt   = self.currentGUITheme
        rclcg = self.displayBox_graphics['KLINESPRICE']['RCLCG']

        #[2]: Master & Display Status
        if not oc['DEPTHOVERLAY_Display']: return 0b00

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b11
        if not drawSignal:     return 0b00

        #[4]: Data Check
        dAgg  = self._data_agg[self.intervalID]
        kline = dAgg['kline'].get(timestamp, None)
        depth = dAgg['depth'][timestamp]
        if kline is None:                                                                  return 0b00
        if depth[DEPTHINDEX_SOURCE] in (FORMATTEDDATATYPE_EMPTY, FORMATTEDDATATYPE_DUMMY): return 0b11
        if kline[KLINDEX_SOURCE]    in (FORMATTEDDATATYPE_EMPTY, FORMATTEDDATATYPE_DUMMY): return 0b11
        kline_closePrice  = kline[KLINDEX_CLOSEPRICE]
        depth_maxNotional = max(depth[DEPTHINDEX_BIDS5:DEPTHINDEX_ASKS5+1])
        ts_open  = depth[DEPTHINDEX_OPENTIME]
        ts_close = depth[DEPTHINDEX_CLOSETIME]
        tsWidth  = ts_close-ts_open+1

        #[5]: Drawing
        drawn = 0b00
        #---[5-1]: Bids
        if drawSignal&0b01:
            #[5-1-1]: Previous Drawing Removal
            sgName = f'DEPTHOL_BIDS_{timestamp}'
            rclcg.removeGroup(groupName = sgName)
            #[5-1-2]: Drawing
            #---Common Coordinate
            tsWidth    = ts_close-ts_open+1
            width = round(tsWidth*0.9, 1)
            xPos  = round(ts_open+(tsWidth-width)/2, 1)
            #---Color
            color_RGB = (oc[f'DEPTHOVERLAY_BIDS_ColorR%{cgt}'],
                         oc[f'DEPTHOVERLAY_BIDS_ColorG%{cgt}'],
                         oc[f'DEPTHOVERLAY_BIDS_ColorB%{cgt}'])
            color_A = oc[f'DEPTHOVERLAY_BIDS_ColorA%{cgt}']
            #---Shapes
            for bIdx, dIdx in enumerate((DEPTHINDEX_BIDS0, DEPTHINDEX_BIDS1, DEPTHINDEX_BIDS2, DEPTHINDEX_BIDS3, DEPTHINDEX_BIDS4, DEPTHINDEX_BIDS5)):
                binBeg, binEnd = _DEPTHBINS[dIdx]
                y0 = kline_closePrice*(1+binBeg/100)
                y1 = kline_closePrice*(1+binEnd/100)
                yPos   = y0
                height = y1-y0
                rclcg.addShape_Rectangle(x = xPos, y = yPos, 
                                         width = width, height = height, 
                                         color = color_RGB+(int(color_A*depth[dIdx]/depth_maxNotional),), 
                                         shapeName = bIdx, shapeGroupName = sgName, layerNumber = 11)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b01

        #---[5-2]: Asks
        if drawSignal&0b10:
            #[5-2-1]: Previous Drawing Removal
            sgName = f'DEPTHOL_ASKS_{timestamp}'
            rclcg.removeGroup(groupName = sgName)
            #[5-2-2]: Drawing
            #---Common Coordinate
            tsWidth    = ts_close-ts_open+1
            width = round(tsWidth*0.9, 1)
            xPos  = round(ts_open+(tsWidth-width)/2, 1)
            #---Color
            color_RGB = (oc[f'DEPTHOVERLAY_ASKS_ColorR%{cgt}'],
                         oc[f'DEPTHOVERLAY_ASKS_ColorG%{cgt}'],
                         oc[f'DEPTHOVERLAY_ASKS_ColorB%{cgt}'])
            color_A = oc[f'DEPTHOVERLAY_ASKS_ColorA%{cgt}']
            #---Shapes
            for bIdx, dIdx in enumerate((DEPTHINDEX_ASKS0, DEPTHINDEX_ASKS1, DEPTHINDEX_ASKS2, DEPTHINDEX_ASKS3, DEPTHINDEX_ASKS4, DEPTHINDEX_ASKS5)):
                binBeg, binEnd = _DEPTHBINS[dIdx]
                y0 = kline_closePrice*(1+binBeg/100)
                y1 = kline_closePrice*(1+binEnd/100)
                yPos   = y0
                height = y1-y0
                rclcg.addShape_Rectangle(x = xPos, y = yPos, 
                                         width = width, height = height, 
                                         color = color_RGB+(int(color_A*depth[dIdx]/depth_maxNotional),), 
                                         shapeName = bIdx, shapeGroupName = sgName, layerNumber = 11)
            #[5-2-3]: Drawn Flag Update
            drawn += 0b10

        #[6]: Return Drawn Flag
        return drawn

    def __drawer_SMA(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc    = self.objectConfig
        ap    = self.analysisParams[self.intervalID][analysisCode]
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
        smas = self._data_agg[self.intervalID][analysisCode]
        timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, nTicks = -1)
        smaResult_prev = smas.get(timestamp_prev, None)
        smaResult      = smas[timestamp]

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
                                    shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = 13+lineIndex)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1
            
        #[6]: Return Drawn Flag
        return drawn

    def __drawer_WMA(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc    = self.objectConfig
        ap    = self.analysisParams[self.intervalID][analysisCode]
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
        wmas = self._data_agg[self.intervalID][analysisCode]
        timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, nTicks = -1)
        wmaResult_prev = wmas.get(timestamp_prev, None)
        wmaResult      = wmas[timestamp]
        
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
                                    shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = 13+lineIndex)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1
            
        #[6]: Return Drawn Flag
        return drawn

    def __drawer_EMA(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc    = self.objectConfig
        ap    = self.analysisParams[self.intervalID][analysisCode]
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
        emas = self._data_agg[self.intervalID][analysisCode]
        timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, nTicks = -1)
        emaResult_prev = emas.get(timestamp_prev, None)
        emaResult      = emas[timestamp]
        
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
                                    shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = 13+lineIndex)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1
            
        #[6]: Return Drawn Flag
        return drawn

    def __drawer_PSAR(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc    = self.objectConfig
        ap    = self.analysisParams[self.intervalID][analysisCode]
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
        dAgg = self._data_agg[self.intervalID]
        kline = dAgg['kline'][timestamp]
        psar  = dAgg[analysisCode][timestamp]

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: PSAR
        if drawSignal&0b1:
            #[5-1-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[5-1-2]: Drawing
            if psar['PSAR'] is not None:
                #Shape Object Params
                ts_open  = kline[KLINDEX_OPENTIME]
                ts_close = kline[KLINDEX_CLOSETIME]
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
                                    shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = 13+lineIndex)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1

        #[6]: Return Drawn Flag
        return drawn

    def __drawer_BOL(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc    = self.objectConfig
        ap    = self.analysisParams[self.intervalID][analysisCode]
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
        bols = self._data_agg[self.intervalID][analysisCode]
        timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, nTicks = -1)
        bolResult_prev = bols.get(timestamp_prev, None)
        bolResult      = bols[timestamp]

        #[5]: Drawing
        drawn = 0b00
        #---[5-1]: Center Line
        if drawSignal&0b01 and oc['BOL_DisplayCenterLine']:
            #[5-1-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode+'_LINE')
            #[5-1-2]: Drawing
            if (bolResult_prev is not None) and (bolResult_prev['MA'] is not None):
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
                                    shapeName = timestamp, shapeGroupName = f"{analysisCode}_LINE", layerNumber = 13+lineIndex)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b01
        #---[5-2]: Band
        if drawSignal&0b10 and oc['BOL_DisplayBand']:
            #[5-2-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode+'_BAND')
            #[5-2-2]: Drawing
            if (bolResult_prev is not None) and (bolResult_prev['BOL'] is not None):
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
                                       shapeName = timestamp, shapeGroupName = f"{analysisCode}_BAND", layerNumber = 0+lineIndex)
            #[5-2-3]: Drawn Flag Update
            drawn += 0b10

        #[6]: Return Drawn Flag
        return drawn

    def __drawer_IVP(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        cgt = self.currentGUITheme
        rclcg        = self.displayBox_graphics['KLINESPRICE']['RCLCG']
        rclcg_xFixed = self.displayBox_graphics['KLINESPRICE']['RCLCG_XFIXED']

        #[2]: Master & Display Status
        if not oc['IVP_Master']: return 0b00

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b11
        if not drawSignal:     return 0b00

        #[4]: Data Acquisition
        dAgg = self._data_agg[self.intervalID]
        kline = dAgg['kline'][timestamp]
        ivp   = dAgg[analysisCode][timestamp]

        #[5]: Drawing
        drawn = 0b00
        #---[5-1]: Volume Price Level Profile
        if drawSignal&0b01 and oc['IVP_VPLP_Display'] and timestamp == self.posHighlight_selectedPos:
            #[5-1-1]: Previous Drawing Removal
            rclcg_xFixed.removeGroup(groupName = 'IVP_VPLP')
            #[5-1-2]: Drawing
            vplp_f    = ivp['volumePriceLevelProfile_Filtered']
            vplp_fMax = ivp['volumePriceLevelProfile_Filtered_Max']
            if vplp_fMax is not None:
                dHeight  = ivp['divisionHeight']
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
                                                    shapeName = dIndex, shapeGroupName = 'IVP_VPLP', layerNumber = 10)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b01
        #---[5-2]: Volume Price Level Profile Boundaries
        if drawSignal&0b10 and oc['IVP_VPLPB_Display']:
            #[5-2-1]: Previous Drawing Removal
            rclcg.removeGroup(groupName = f'IVP_VPLPB_{timestamp}')
            #[5-2-2]: Drawing
            vplp_b = ivp['volumePriceLevelProfile_Boundaries']
            if vplp_b is not None:
                ts_open  = kline[KLINDEX_OPENTIME]
                ts_close = kline[KLINDEX_CLOSETIME]
                tsWidth  = ts_close-ts_open+1
                dr       = oc['IVP_VPLPB_DisplayRegion']
                lcp      = ivp['lastClosePrice']
                dHeight  = ivp['divisionHeight']
                pb_dr_beg = lcp*(1-dr)
                pb_dr_end = lcp*(1+dr)
                dIdx_bdr_beg = max(int(pb_dr_beg/dHeight), 0)
                dIdx_bdr_end = min(int(pb_dr_end/dHeight), len(ivp['volumePriceLevelProfile'])-1)
                color_rgb = (oc[f'IVP_VPLPB_ColorR%{cgt}'],
                             oc[f'IVP_VPLPB_ColorG%{cgt}'],
                             oc[f'IVP_VPLPB_ColorB%{cgt}'])
                color_a   = oc[f'IVP_VPLPB_ColorA%{cgt}']
                vplp_f    = ivp['volumePriceLevelProfile_Filtered']
                vplp_fMax = ivp['volumePriceLevelProfile_Filtered_Max']
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
                                             shapeName = bIndex, shapeGroupName = f'IVP_VPLPB_{timestamp}', layerNumber = 10)
            #[5-2-3]: Drawn Flag Update
            drawn += 0b10
        #[6]: Return Drawn Flag
        return drawn

    def __drawer_SWING(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc    = self.objectConfig
        ap    = self.analysisParams[self.intervalID][analysisCode]
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
        swing = self._data_agg[self.intervalID][analysisCode][timestamp]

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: SWINGS
        if drawSignal&0b1:
            if timestamp == self.posHighlight_selectedPos:
                #[5-1]: Previous Drawing Removal
                rclcg.removeGroup(groupName = f'{analysisCode}_SWINGS')
                #[5-1-2]: Drawing
                swing_swings = swing['SWINGS']
                timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, nTicks = -1)
                timestampWidth = timestamp-timestamp_prev
                color = (oc[f'SWING_{lineIndex}_ColorR%{cgt}'], 
                         oc[f'SWING_{lineIndex}_ColorG%{cgt}'], 
                         oc[f'SWING_{lineIndex}_ColorB%{cgt}'], 
                         oc[f'SWING_{lineIndex}_ColorA%{cgt}'])
                width_y = oc[f'SWING_{lineIndex}_Width']*2
                for sIndex in range (1, len(swing_swings)):
                    swing_prev    = swing_swings[sIndex-1]
                    swing_current = swing_swings[sIndex]
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
                                        shapeName = sIndex, shapeGroupName = f'{analysisCode}_SWINGS', layerNumber = 13+lineIndex)
                #[5-1-3]: Drawn Flag Update
                drawn += 0b1
        
        #[6]: Return Drawn Flag
        return drawn

    def __drawer_VOL(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID].get(analysisCode, None)
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

        #[4]: Drawing
        drawn = 0b0
        #---[4-1]: Volume
        if drawSignal&0b1 and analysisCode == 'VOL':
            #[4-1-1]: Kline
            kline = self._data_agg[self.intervalID]['kline'][timestamp]
            #[4-1-2]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = 'VOL')
            #[4-1-3]: Drawing
            if kline[KLINDEX_SOURCE] not in (FORMATTEDDATATYPE_EMPTY, FORMATTEDDATATYPE_DUMMY):
                #---Shape Object Params
                vType = oc['VOL_VolumeType']
                if   vType == 'BASE':    vaIdx = KLINDEX_VOLBASE
                elif vType == 'QUOTE':   vaIdx = KLINDEX_VOLQUOTE
                elif vType == 'BASETB':  vaIdx = KLINDEX_VOLBASETAKERBUY
                elif vType == 'QUOTETB': vaIdx = KLINDEX_VOLQUOTETAKERBUY
                kl_closeTime  = kline[KLINDEX_CLOSETIME]
                kl_openPrice  = kline[KLINDEX_OPENPRICE]
                kl_closePrice = kline[KLINDEX_CLOSEPRICE]
                tsWidth = kl_closeTime-timestamp+1
                shape_width  = round(tsWidth*0.9, 1)
                shape_xPos   = round(timestamp+(tsWidth-shape_width)/2, 1)
                shape_yPos   = 0
                shape_height = kline[vaIdx]
                kcType = oc['KlineColorType']
                if   kl_openPrice < kl_closePrice: color = self.visualManager.getFromColorTable(f'CHARTDRAWER_KLINECOLOR_TYPE{kcType}_INCREMENTAL') #Incremental
                elif kl_openPrice > kl_closePrice: color = self.visualManager.getFromColorTable(f'CHARTDRAWER_KLINECOLOR_TYPE{kcType}_DECREMENTAL') #Decremental
                else:                              color = self.visualManager.getFromColorTable(f'CHARTDRAWER_KLINECOLOR_TYPE{kcType}_NEUTRAL')     #Neutral
                #---Shape Adding
                rclcg.addShape_Rectangle(x = shape_xPos, y = shape_yPos, 
                                        width = shape_width, height = shape_height, 
                                        color = color, 
                                        shapeName = timestamp, shapeGroupName = 'VOL', layerNumber = 0)
            #[4-1-4]: Drawn Flag Update
            drawn += 0b1
        #---[4-2]: Volume MA
        if drawSignal&0b1 and analysisCode != 'VOL':
            #[4-2-1]: Analysis Data
            dAgg_ac   = self._data_agg[self.intervalID][analysisCode]
            lineIndex = ap['lineIndex']
            vType     = oc['VOL_VolumeType']
            maCode    = f'MA_{vType}'
            #[4-2-2]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[4-2-3]: Drawing
            timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, nTicks = -1)
            volResult_prev = dAgg_ac.get(timestamp_prev, None)
            volResult      = dAgg_ac[timestamp]
            if (volResult_prev is not None) and (volResult_prev[maCode] is not None):
                #Shape Object Params
                tsWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+tsWidth/2, 1)
                shape_x2 = round(timestamp     +tsWidth/2, 1)
                shape_y1 = volResult_prev[maCode]
                shape_y2 = volResult[maCode]
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
                                    shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = 1+lineIndex)
            #[4-2-4]: Drawn Flag Update
            drawn += 0b1

        #[5]: Return Drawn Flag
        return drawn

    def __drawer_DEPTH(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        cgt = self.currentGUITheme
        siViewerIndex = self.siTypes_siViewerAlloc['DEPTH']
        siViewerCode  = f'SIVIEWER{siViewerIndex}'
        rclcg = self.displayBox_graphics[siViewerCode]['RCLCG']

        #[2]: Master & Display Status
        if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b00
        if not oc['DEPTH_Master']:                    return 0b00

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b11
        if not drawSignal:     return 0b00

        #[4]: Data Check
        dAgg  = self._data_agg[self.intervalID]
        depth = dAgg['depth'][timestamp]
        if depth[DEPTHINDEX_SOURCE] in (FORMATTEDDATATYPE_EMPTY, FORMATTEDDATATYPE_DUMMY): return 0b11
        depth_maxNotional = max(depth[DEPTHINDEX_BIDS5:DEPTHINDEX_ASKS5+1])
        ts_open  = depth[DEPTHINDEX_OPENTIME]
        ts_close = depth[DEPTHINDEX_CLOSETIME]
        tsWidth  = ts_close-ts_open+1

        #[5]: Drawing
        drawn = 0b00
        #---[5-1]: Bids
        if drawSignal&0b01:
            #[5-1-1]: Previous Drawing Removal
            sgName = f'DEPTH_BIDS_{timestamp}'
            rclcg.removeGroup(groupName = sgName)
            #[5-1-2]: Drawing
            #---Common Coordinate
            width = round(tsWidth*0.9, 1)
            xPos  = round(ts_open+(tsWidth-width)/2, 1)
            #---Color
            color_RGB = (oc[f'DEPTH_BIDS_ColorR%{cgt}'],
                         oc[f'DEPTH_BIDS_ColorG%{cgt}'],
                         oc[f'DEPTH_BIDS_ColorB%{cgt}'])
            color_A = oc[f'DEPTH_BIDS_ColorA%{cgt}']
            #---Shapes
            for bIdx, dIdx in enumerate((DEPTHINDEX_BIDS0, DEPTHINDEX_BIDS1, DEPTHINDEX_BIDS2, DEPTHINDEX_BIDS3, DEPTHINDEX_BIDS4, DEPTHINDEX_BIDS5)):
                binBeg, binEnd = _DEPTHBINS[dIdx]
                y0 = binBeg
                y1 = binEnd
                yPos   = y0
                height = y1-y0
                rclcg.addShape_Rectangle(x = xPos, y = yPos, 
                                         width = width, height = height, 
                                         color = color_RGB+(int(color_A*depth[dIdx]/depth_maxNotional),), 
                                         shapeName = bIdx, shapeGroupName = sgName, layerNumber = 0)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b01
        #---[5-2]: Asks
        if drawSignal&0b10:
            #[5-2-1]: Previous Drawing Removal
            sgName = f'DEPTH_ASKS_{timestamp}'
            rclcg.removeGroup(groupName = sgName)
            #[5-2-2]: Drawing
            #---Common Coordinate
            width = round(tsWidth*0.9, 1)
            xPos  = round(ts_open+(tsWidth-width)/2, 1)
            #---Color
            color_RGB = (oc[f'DEPTH_ASKS_ColorR%{cgt}'],
                         oc[f'DEPTH_ASKS_ColorG%{cgt}'],
                         oc[f'DEPTH_ASKS_ColorB%{cgt}'])
            color_A = oc[f'DEPTH_ASKS_ColorA%{cgt}']
            #---Shapes
            for bIdx, dIdx in enumerate((DEPTHINDEX_ASKS0, DEPTHINDEX_ASKS1, DEPTHINDEX_ASKS2, DEPTHINDEX_ASKS3, DEPTHINDEX_ASKS4, DEPTHINDEX_ASKS5)):
                binBeg, binEnd = _DEPTHBINS[dIdx]
                y0 = binBeg
                y1 = binEnd
                yPos   = y0
                height = y1-y0
                rclcg.addShape_Rectangle(x = xPos, y = yPos, 
                                         width = width, height = height, 
                                         color = color_RGB+(int(color_A*depth[dIdx]/depth_maxNotional),), 
                                         shapeName = bIdx, shapeGroupName = sgName, layerNumber = 0)
            #[5-2-3]: Drawn Flag Update
            drawn += 0b10

        #[6]: Return Drawn Flag
        return drawn

    def __drawer_AGGTRADE(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        cgt = self.currentGUITheme
        siViewerIndex = self.siTypes_siViewerAlloc['AGGTRADE']
        siViewerCode  = f'SIVIEWER{siViewerIndex}'
        rclcg = self.displayBox_graphics[siViewerCode]['RCLCG']

        #[2]: Master & Display Status
        if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b00
        if not oc['AGGTRADE_Master']:                 return 0b00

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b11
        if not drawSignal:     return 0b00

        #[4]: Data Check
        dAgg     = self._data_agg[self.intervalID]
        aggTrade = dAgg['aggTrade'][timestamp]
        if aggTrade[ATINDEX_SOURCE] in (FORMATTEDDATATYPE_EMPTY, FORMATTEDDATATYPE_DUMMY): return 0b11
        ts_open  = aggTrade[DEPTHINDEX_OPENTIME]
        ts_close = aggTrade[DEPTHINDEX_CLOSETIME]
        tsWidth  = ts_close-ts_open+1
        displayType = oc['AGGTRADE_DisplayType']
        if displayType == 'QUANTITY':
            dIdx_buy  = ATINDEX_QUANTITYBUY
            dIdx_sell = ATINDEX_QUANTITYSELL
        elif displayType == 'NTRADES':
            dIdx_buy  = ATINDEX_NTRADESBUY
            dIdx_sell = ATINDEX_NTRADESSELL
        elif displayType == 'NOTIONAL':
            dIdx_buy  = ATINDEX_NOTIONALBUY
            dIdx_sell = ATINDEX_NOTIONALSELL

        #[5]: Drawing
        drawn = 0b00
        #---[5-1]: Buy
        if drawSignal&0b01:
            #[5-1-1]: Previous Drawing Removal
            sgName = 'AGGTRADE_BUY'
            rclcg.removeShape(shapeName = timestamp, groupName = sgName)
            #[5-1-2]: Drawing
            #---Common Coordinate
            width = round(tsWidth*0.9, 1)
            xPos  = round(ts_open+(tsWidth-width)/2, 1)
            #---Color
            color = (oc[f'AGGTRADE_BUY_ColorR%{cgt}'],
                     oc[f'AGGTRADE_BUY_ColorG%{cgt}'],
                     oc[f'AGGTRADE_BUY_ColorB%{cgt}'],
                     oc[f'AGGTRADE_BUY_ColorA%{cgt}'])
            #---Shapes
            yPos   = 0
            height = aggTrade[dIdx_buy]
            rclcg.addShape_Rectangle(x = xPos, y = yPos, 
                                     width = width, height = height, 
                                     color = color,
                                     shapeName = timestamp, shapeGroupName = sgName, layerNumber = 0)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b01
        #---[5-2]: Sell
        if drawSignal&0b10:
            #[5-2-1]: Previous Drawing Removal
            sgName = 'AGGTRADE_SELL'
            rclcg.removeShape(shapeName = timestamp, groupName = sgName)
            #[5-2-2]: Drawing
            #---Common Coordinate
            width = round(tsWidth*0.9, 1)
            xPos  = round(ts_open+(tsWidth-width)/2, 1)
            #---Color
            color = (oc[f'AGGTRADE_SELL_ColorR%{cgt}'],
                     oc[f'AGGTRADE_SELL_ColorG%{cgt}'],
                     oc[f'AGGTRADE_SELL_ColorB%{cgt}'],
                     oc[f'AGGTRADE_SELL_ColorA%{cgt}'])
            #---Shapes
            yPos   = 0
            height = aggTrade[dIdx_sell]
            rclcg.addShape_Rectangle(x = xPos, y = yPos, 
                                     width = width, height = -height, 
                                     color = color,
                                     shapeName = timestamp, shapeGroupName = sgName, layerNumber = 0)
            #[5-2-3]: Drawn Flag Update
            drawn += 0b10

        #[5]: Return Drawn Flag
        return drawn
    
    def __drawer_NNA(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID][analysisCode]
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
        nnas = self._data_agg[self.intervalID][analysisCode]
        timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, nTicks = -1)
        nna_prev = nnas.get(timestamp_prev, None)
        nna      = nnas[timestamp]

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: ABSATHREL
        if drawSignal&0b1:
            #[5-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[5-1-2]: Drawing
            if (nna_prev is not None) and (nna_prev['NNA'] is not None):
                #Shape Object Params
                timestampWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                shape_x2 = round(timestamp     +timestampWidth/2, 1)
                shape_y1 = nna_prev['NNA']
                shape_y2 = nna['NNA']
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

    def __drawer_MMACD(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        cgt = self.currentGUITheme
        siViewerIndex = self.siTypes_siViewerAlloc['MMACD']
        siViewerCode  = f'SIVIEWER{siViewerIndex}'
        rclcg = self.displayBox_graphics[siViewerCode]['RCLCG']

        #[2]: Master & Display Status
        if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b000
        if not oc['MMACD_Master']:                    return 0b000

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b111
        if not drawSignal:     return 0b000

        #[4]: Data Acquisition
        mmacds = self._data_agg[self.intervalID][analysisCode]
        timestamp_prev   = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, nTicks = -1)
        mmacd_prev = mmacds.get(timestamp_prev, None)
        mmacd      = mmacds[timestamp]

        #[5]: Common Coordinates
        tsWidth = timestamp-timestamp_prev
        shape_x1 = round(timestamp_prev+tsWidth/2, 1)
        shape_x2 = round(timestamp     +tsWidth/2, 1)

        #[6]: Drawing
        drawn = 0b000
        #---[6-1]: MMACD
        if drawSignal&0b001 and oc['MMACD_MMACD_Display']:
            #[6-1-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = 'MMACD_MMACD')
            #[6-1-2]: Drawing
            if (mmacd_prev is not None) and (mmacd_prev['MMACD'] is not None):
                #Shape Object Params
                shape_y       = mmacd_prev['MMACD']
                shape_y2      = mmacd['MMACD']
                shape_width_y = 5
                color = (oc[f'MMACD_MMACD_ColorR%{cgt}'],
                         oc[f'MMACD_MMACD_ColorG%{cgt}'],
                         oc[f'MMACD_MMACD_ColorB%{cgt}'],
                         oc[f'MMACD_MMACD_ColorA%{cgt}'])
                #Shape Adding
                rclcg.addShape_Line(x = shape_x1, x2 = shape_x2, 
                                    y = shape_y,  y2 = shape_y2, 
                                    width_y = shape_width_y, 
                                    color = color, 
                                    shapeName = timestamp, shapeGroupName = 'MMACD_MMACD', layerNumber = 1)
            #[6-1-3]: Drawn Flag Update
            drawn += 0b001
        #---[6-2]: SIGNAL
        if drawSignal&0b010 and oc['MMACD_SIGNAL_Display']:
            #[6-2-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = 'MMACD_SIGNAL')
            #[6-2-2]: Drawing
            if (mmacd_prev is not None) and (mmacd_prev['SIGNAL'] is not None):
                #Shape Object Params
                shape_y       = mmacd_prev['SIGNAL']
                shape_y2      = mmacd['SIGNAL']
                shape_width_y = 5
                color = (oc[f'MMACD_SIGNAL_ColorR%{cgt}'],
                         oc[f'MMACD_SIGNAL_ColorG%{cgt}'],
                         oc[f'MMACD_SIGNAL_ColorB%{cgt}'],
                         oc[f'MMACD_SIGNAL_ColorA%{cgt}'])
                #Shape Adding
                rclcg.addShape_Line(x = shape_x1, x2 = shape_x2,
                                    y = shape_y,  y2 = shape_y2,
                                    width_y = shape_width_y,
                                    color = color,
                                    shapeName = timestamp, shapeGroupName = 'MMACD_SIGNAL', layerNumber = 1)
            #[6-2-3]: Drawn Flag Update
            drawn += 0b010
        #---[6-3]: HISTOGRAM
        if drawSignal&0b100 and oc['MMACD_HISTOGRAM_Display']:
            #[6-3-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = 'MMACD_HISTOGRAM')
            #[6-3-2]: Drawing
            mr_mmacd     = mmacd['MMACD']
            mr_histogram = mmacd[oc['MMACD_HISTOGRAM_Type']]
            if mr_histogram is not None:
                #Shape Object Params
                shape_width = round(tsWidth*0.9, 1)
                shape_xPos  = round(timestamp+(tsWidth-shape_width)/2, 1)
                if 0 <= mr_histogram:
                    if 0 <= mr_mmacd:
                        color = (oc[f'MMACD_HISTOGRAM+_ColorR%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM+_ColorG%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM+_ColorB%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM+_ColorA%{cgt}'])
                    else:
                        color = (oc[f'MMACD_HISTOGRAM+_ColorR%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM+_ColorG%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM+_ColorB%{cgt}'],
                                 int(oc[f'MMACD_HISTOGRAM+_ColorA%{cgt}']/2))
                else:
                    if 0 <= mr_mmacd:
                        color = (oc[f'MMACD_HISTOGRAM-_ColorR%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM-_ColorG%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM-_ColorB%{cgt}'],
                                 int(oc[f'MMACD_HISTOGRAM-_ColorA%{cgt}']/2))
                    else:
                        color = (oc[f'MMACD_HISTOGRAM-_ColorR%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM-_ColorG%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM-_ColorB%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM-_ColorA%{cgt}'])
                body_y      = 0
                body_height = mr_histogram
                #Shape Adding
                rclcg.addShape_Rectangle(x = shape_xPos, y = body_y, 
                                         width = shape_width, height = body_height, 
                                         color = color, 
                                         shapeName = timestamp, shapeGroupName = 'MMACD_HISTOGRAM', layerNumber = 0)
            #[6-3-3]: Drawn Flag Update
            drawn += 0b100

        #[7]: Return Drawn Flag
        return drawn

    def __drawer_DMIxADX(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID][analysisCode]
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
        dmixadxs = self._data_agg[self.intervalID][analysisCode]
        timestamp_prev     = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, nTicks = -1)
        dmixadx_prev = dmixadxs.get(timestamp_prev, None)
        dmixadx      = dmixadxs[timestamp]

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: ABSATHREL
        if drawSignal&0b1:
            #[5-1-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[5-1-2]: Drawing
            if (dmixadx_prev is not None) and (dmixadx_prev['DMIxADX_ABSATHREL'] is not None):
                #Shape Object Params
                timestampWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                shape_x2 = round(timestamp     +timestampWidth/2, 1)
                shape_y1 = dmixadx_prev['DMIxADX_ABSATHREL']
                shape_y2 = dmixadx['DMIxADX_ABSATHREL']
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

    def __drawer_MFI(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID][analysisCode]
        cgt = self.currentGUITheme
        lineIndex = ap['lineIndex']
        siViewerIndex = self.siTypes_siViewerAlloc['MFI']
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
        mfis = self._data_agg[self.intervalID][analysisCode]
        timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, nTicks = -1)
        mfi_prev = mfis.get(timestamp_prev, None)
        mfi      = mfis[timestamp]

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: ABSATHREL
        if drawSignal&0b1:
            #[5-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[5-1-2]: Drawing
            if (mfi_prev is not None) and (mfi_prev['MFI_ABSATHDEVREL'] is not None):
                #Shape Object Params
                timestampWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                shape_x2 = round(timestamp     +timestampWidth/2, 1)
                shape_y1 = mfi_prev['MFI_ABSATHDEVREL']
                shape_y2 = mfi['MFI_ABSATHDEVREL']
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

    def __drawer_TPD(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID][analysisCode]
        cgt = self.currentGUITheme
        lineIndex = ap['lineIndex']
        siViewerIndex = self.siTypes_siViewerAlloc['TPD']
        siViewerCode  = f'SIVIEWER{siViewerIndex}'
        rclcg         = self.displayBox_graphics[siViewerCode]['RCLCG']

        #[2]: Master & Display Status
        if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b0
        if not oc['TPD_Master']:                      return 0b0
        if not oc[f'TPD_{lineIndex}_Display']:        return 0b0
        
        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b1
        if not drawSignal:     return 0b0

        #[4]: Data Acquisition
        tpds = self._data_agg[self.intervalID][analysisCode]
        timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, nTicks = -1)
        tpd_prev = tpds.get(timestamp_prev, None)
        tpd      = tpds[timestamp]

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: ABSATHREL
        if drawSignal&0b1:
            #[5-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[5-1-2]: Drawing
            if (tpd_prev is not None) and (tpd_prev['TPD_BIASMA'] is not None):
                #Shape Object Params
                timestampWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                shape_x2 = round(timestamp     +timestampWidth/2, 1)
                shape_y1 = tpd_prev['TPD_BIASMA']
                shape_y2 = tpd['TPD_BIASMA']
                width_y  = oc[f'TPD_{lineIndex}_Width']*5
                lineColor = (oc[f'TPD_{lineIndex}_ColorR%{cgt}'],
                             oc[f'TPD_{lineIndex}_ColorG%{cgt}'],
                             oc[f'TPD_{lineIndex}_ColorB%{cgt}'],
                             oc[f'TPD_{lineIndex}_ColorA%{cgt}'])
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

    def __drawer_TRADELOG(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc    = self.objectConfig
        cgt   = self.currentGUITheme
        rclcg = self.displayBox_graphics['KLINESPRICE']['RCLCG']

        #[2]: Master & Display Status
        if not oc['TRADELOG_Display']: return 0b0

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b1
        if not drawSignal:     return 0b0

        #[4]: Trade Log and Kline & Dummy Check
        tls      = self._data_raw['tradeLog']
        tradeLog = tls[timestamp]
        kline    = self._data_agg[self.intervalID]['kline'][timestamp]
        if kline[KLINDEX_SOURCE] in (FORMATTEDDATATYPE_EMPTY, FORMATTEDDATATYPE_DUMMY):
            return 0b1

        #[5]: Drawing
        drawn = 0b0
        if drawSignal&0b1:
            #[5-1-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = 'TRADELOG_BODY')
            rclcg.removeGroup(groupName = f'TRADELOG_LOGS_{timestamp}')
            #[5-1-2]: Drawing
            if tradeLog['totalQuantity']:
                func_gnitt = auxiliaries.getNextIntervalTickTimestamp
                #[5-1-2-1]: Position
                timestamp_next = func_gnitt(intervalID = self.intervalID, timestamp = timestamp, nTicks = 1)
                shape_x     = timestamp
                shape_x2    = timestamp_next
                shape_width = shape_x2-shape_x
                kl_cp = kline[KLINDEX_CLOSEPRICE]
                if 0 < tradeLog['totalQuantity']:
                    if tradeLog['entryPrice'] <= kl_cp: cType = 'BUY'
                    else:                               cType = 'SELL'
                elif tradeLog['totalQuantity'] < 0:
                    if tradeLog['entryPrice'] <= kl_cp: cType = 'SELL'
                    else:                               cType = 'BUY'
                color = (oc[f'TRADELOG_{cType}_ColorR%{cgt}'],
                         oc[f'TRADELOG_{cType}_ColorG%{cgt}'],
                         oc[f'TRADELOG_{cType}_ColorB%{cgt}'],
                         int(oc[f'TRADELOG_{cType}_ColorA%{cgt}']/5))
                shape_y      = tradeLog['entryPrice']
                shape_height = kl_cp-tradeLog['entryPrice']
                rclcg.addShape_Rectangle(x = shape_x, y = shape_y, 
                                         width = shape_width, height = shape_height, 
                                         color = color, 
                                         shapeName = timestamp, shapeGroupName = 'TRADELOG_BODY', layerNumber = 23)
                #[5-1-2-2]: Trades
                for lIdx, l in enumerate(l for ts in auxiliaries.getTimestampList_byRange(intervalID        = KLINTERVAL,
                                                                                                 timestamp_beg     = timestamp,
                                                                                                 timestamp_end     = timestamp_next-1,
                                                                                                 lastTickInclusive = True)
                                         if ts in tls
                                         for l in tls[ts]['logs']):
                    ts    = l['timestamp']
                    side  = l['side']
                    price = l['price']
                    color = (oc[f'TRADELOG_{side}_ColorR%{cgt}'],
                             oc[f'TRADELOG_{side}_ColorG%{cgt}'],
                             oc[f'TRADELOG_{side}_ColorB%{cgt}'],
                             oc[f'TRADELOG_{side}_ColorA%{cgt}'])
                    shape_y  = price
                    shape_y2 = price
                    width_y  = 3
                    rclcg.addShape_Line(x = ts+1, x2 = func_gnitt(intervalID = KLINTERVAL, timestamp = ts, nTicks = 1)-1, 
                                        y = shape_y, y2 = shape_y2, 
                                        color = color, width_y = width_y, 
                                        shapeName = lIdx, shapeGroupName = f'TRADELOG_LOGS_{timestamp}', layerNumber = 24)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1

        #[6]: Return Drawn Flag
        return drawn

    def _drawer_RemoveExpiredDrawings(self, timestamp):
        #[1]: Instances & Timestamp Check
        drawn = self.__drawn
        if timestamp not in drawn:
            return

        #[2]: Removal
        for aCode in drawn[timestamp]:
            targetType = aCode.split("_")[0]
            if targetType == 'KLINE':
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = 'KLINEBODIES')
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = 'KLINETAILS')

            elif targetType == 'DEPTHOVERLAY':
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = f'DEPTHOL_BIDS_{timestamp}')
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = f'DEPTHOL_ASKS_{timestamp}')

            elif targetType == 'SMA':
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = aCode)

            elif targetType == 'WMA':
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = aCode)

            elif targetType == 'EMA':
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = aCode)

            elif targetType == 'PSAR':
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = aCode)

            elif targetType == 'BOL':
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = f"{aCode}_LINE")
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = f"{aCode}_BAND")

            elif targetType == 'IVP':
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = f'IVP_VPLPB_{timestamp}')

            elif targetType == 'SWING':
                pass

            elif targetType == 'VOL': 
                sivIdx = self.siTypes_siViewerAlloc['VOL']
                if sivIdx is not None: 
                    sivCode = f"SIVIEWER{sivIdx}"
                    self.displayBox_graphics[f"SIVIEWER{sivIdx}"]['RCLCG'].removeShape(shapeName = timestamp, groupName = aCode)

            elif targetType == 'DEPTH': 
                sivIdx = self.siTypes_siViewerAlloc['DEPTH']
                if sivIdx is not None: 
                    sivCode = f"SIVIEWER{sivIdx}"
                    self.displayBox_graphics[f"SIVIEWER{sivIdx}"]['RCLCG'].removeGroup(groupName = f'DEPTH_BIDS_{timestamp}')
                    self.displayBox_graphics[f"SIVIEWER{sivIdx}"]['RCLCG'].removeGroup(groupName = f'DEPTH_ASKS_{timestamp}')

            elif targetType == 'AGGTRADE': 
                sivIdx = self.siTypes_siViewerAlloc['AGGTRADE']
                if sivIdx is not None: 
                    sivCode = f"SIVIEWER{sivIdx}"
                    self.displayBox_graphics[f"SIVIEWER{sivIdx}"]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'AGGTRADE_BUY')
                    self.displayBox_graphics[f"SIVIEWER{sivIdx}"]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'AGGTRADE_SELL')

            elif targetType == 'NNA':
                sivIdx = self.siTypes_siViewerAlloc['NNA']
                if sivIdx is not None: 
                    sivCode = f"SIVIEWER{sivIdx}"
                    self.displayBox_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = aCode)

            elif targetType == 'MMACD':
                sivIdx = self.siTypes_siViewerAlloc['MMACD']
                if sivIdx is not None: 
                    sivCode = f"SIVIEWER{sivIdx}"
                    self.displayBox_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACD_MMACD')
                    self.displayBox_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACD_SIGNAL')
                    self.displayBox_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACD_HISTOGRAM')

            elif targetType == 'DMIxADX':
                sivIdx = self.siTypes_siViewerAlloc['DMIxADX']
                if sivIdx is not None: 
                    sivCode = f"SIVIEWER{sivIdx}"
                    self.displayBox_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = aCode)

            elif targetType == 'MFI':
                sivIdx = self.siTypes_siViewerAlloc['MFI']
                if sivIdx is not None: 
                    sivCode = f"SIVIEWER{sivIdx}"
                    self.displayBox_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = aCode)

            elif targetType == 'TPD':
                sivIdx = self.siTypes_siViewerAlloc['TPD']
                if sivIdx is not None: 
                    sivCode = f"SIVIEWER{sivIdx}"
                    self.displayBox_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = aCode)

            elif targetType == 'TRADELOG':
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = 'TRADELOG_BODY')
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = f'TRADELOG_LOGS_{timestamp}')
        del drawn[timestamp]
        
    def _drawer_RemoveDrawings(self, analysisCode, gRemovalSignal = None):
        #[1]: Instances
        dBox_g = self.displayBox_graphics
        drawn  = self.__drawn
        dQueue = self.__drawQueue

        #[2]: Type
        if analysisCode in ('KLINE', 'DEPTHOVERLAY', 'DEPTH', 'AGGTRADE'):
            analysisType = analysisCode
        else:
            analysisType = analysisCode.split("_")[0]
        if gRemovalSignal is None: gRemovalSignal = _FULLDRAWSIGNALS[analysisType]
        else:                      gRemovalSignal = gRemovalSignal
        
        #[3]: Drawing Removal
        #---[3-1]: KLINE
        if analysisCode == 'KLINE':
            if gRemovalSignal&0b1: dBox_g['KLINESPRICE']['RCLCG'].removeGroup(groupName = analysisCode)

        #---[3-2]: DEPTHOVERLAY
        elif analysisCode == 'DEPTHOVERLAY':
            rclcg = dBox_g['KLINESPRICE']['RCLCG']
            for ts in drawn:
                if 'DEPTHOVERLAY' not in drawn[ts]: continue
                if gRemovalSignal&0b01: rclcg.removeGroup(groupName = f'DEPTHOL_BIDS_{ts}')
                if gRemovalSignal&0b10: rclcg.removeGroup(groupName = f'DEPTHOL_ASKS_{ts}')
        
        #---[3-3]: SMA
        elif analysisType == 'SMA':
            if gRemovalSignal&0b1: dBox_g['KLINESPRICE']['RCLCG'].removeGroup(groupName = analysisCode)

        #---[3-4]: WMA
        elif analysisType == 'WMA':
            if gRemovalSignal&0b1: dBox_g['KLINESPRICE']['RCLCG'].removeGroup(groupName = analysisCode)

        #---[3-5]: EMA
        elif analysisType == 'EMA':
            if gRemovalSignal&0b1: dBox_g['KLINESPRICE']['RCLCG'].removeGroup(groupName = analysisCode)

        #---[3-6]: PSAR
        elif analysisType == 'PSAR':
            if gRemovalSignal&0b1: dBox_g['KLINESPRICE']['RCLCG'].removeGroup(groupName = analysisCode)

        #---[3-7]: BOL
        elif analysisType == 'BOL':
            if gRemovalSignal&0b01: dBox_g['KLINESPRICE']['RCLCG'].removeGroup(groupName = f"{analysisCode}_LINE")
            if gRemovalSignal&0b10: dBox_g['KLINESPRICE']['RCLCG'].removeGroup(groupName = f"{analysisCode}_BAND")

        #---[3-8]: IVP
        elif analysisType == 'IVP':
            if gRemovalSignal&0b01: dBox_g['KLINESPRICE']['RCLCG_XFIXED'].removeGroup(groupName = 'IVP_VPLP')
            rclcg = dBox_g['KLINESPRICE']['RCLCG']
            for ts in drawn:
                if 'IVP' not in drawn[ts]: continue
                if gRemovalSignal&0b10: rclcg.removeGroup(groupName = f'IVP_VPLPB_{ts}')

        #---[3-9]: SWING
        elif analysisType == 'SWING':
            if gRemovalSignal&0b1: dBox_g['KLINESPRICE']['RCLCG'].removeGroup(groupName = f"{analysisCode}_SWINGS")

        #---[3-10]: VOL
        elif analysisType == 'VOL':
            sivIdx = self.siTypes_siViewerAlloc['VOL']
            if sivIdx is not None:
                sivCode = f"SIVIEWER{sivIdx}"
                if gRemovalSignal&0b1: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = analysisCode)

        #---[3-11]: DEPTH
        elif analysisCode == 'DEPTH':
            sivIdx = self.siTypes_siViewerAlloc['DEPTH']
            if sivIdx is not None:
                sivCode = f"SIVIEWER{sivIdx}"
                rclcg   = dBox_g[sivCode]['RCLCG']
                for ts in drawn:
                    if 'DEPTH' not in drawn[ts]: continue
                    if gRemovalSignal&0b01: rclcg.removeGroup(groupName = f'DEPTH_BIDS_{ts}')
                    if gRemovalSignal&0b10: rclcg.removeGroup(groupName = f'DEPTH_ASKS_{ts}')

        #---[3-12]: AGGTRADE
        elif analysisCode == 'AGGTRADE':
            sivIdx = self.siTypes_siViewerAlloc['AGGTRADE']
            if sivIdx is not None:
                sivCode = f"SIVIEWER{sivIdx}"
                if gRemovalSignal&0b01: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = 'AGGTRADE_BUY')
                if gRemovalSignal&0b10: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = 'AGGTRADE_SELL')

        #---[3-13]: NNA
        elif analysisType == 'NNA':
            sivIdx = self.siTypes_siViewerAlloc['NNA']
            if sivIdx is not None:
                sivCode = f"SIVIEWER{sivIdx}"
                if gRemovalSignal&0b1: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = analysisCode)

        #---[3-14]: MMACD
        elif analysisType == 'MMACD':
            sivIdx = self.siTypes_siViewerAlloc['MMACD']
            if sivIdx is not None:
                sivCode = f"SIVIEWER{sivIdx}"
                if gRemovalSignal&0b001: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = 'MMACD_MMACD')
                if gRemovalSignal&0b010: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = 'MMACD_SIGNAL')
                if gRemovalSignal&0b100: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = 'MMACD_HISTOGRAM')

        #---[3-15]: DMIxADX
        elif analysisType == 'DMIxADX':
            sivIdx = self.siTypes_siViewerAlloc['DMIxADX']
            if sivIdx is not None:
                sivCode = f"SIVIEWER{sivIdx}"
                if gRemovalSignal&0b1: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = analysisCode)

        #---[3-16]: MFI
        elif analysisType == 'MFI':
            sivIdx = self.siTypes_siViewerAlloc['MFI']
            if sivIdx is not None:
                sivCode = f"SIVIEWER{sivIdx}"
                if gRemovalSignal&0b1: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = analysisCode)

        #---[3-17]: TPD
        elif analysisType == 'TPD':
            sivIdx = self.siTypes_siViewerAlloc['TPD']
            if sivIdx is not None:
                sivCode = f"SIVIEWER{sivIdx}"
                if gRemovalSignal&0b1: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = analysisCode)

        #---[3-18]: TRADELOG
        elif analysisType == 'TRADELOG':
            if gRemovalSignal&0b1:
                rclcg = dBox_g['KLINESPRICE']['RCLCG']
                rclcg.removeGroup(groupName = 'TRADELOG_BODY')
                for ts in drawn:
                    if 'TRADELOG' not in drawn[ts]: continue
                    rclcg.removeGroup(groupName = f'TRADELOG_LOGS_{ts}')

        #[4]: Draw Trackers Reset
        for ts in drawn:
            if analysisCode not in drawn[ts]: 
                continue
            drawn[ts][analysisCode] &= ~gRemovalSignal
            if not drawn[ts][analysisCode]: del drawn[ts][analysisCode]
        for ts in dQueue:
            if analysisCode not in dQueue[ts]: 
                continue
            if dQueue[ts][analysisCode] is None: dQueue[ts][analysisCode] = _FULLDRAWSIGNALS[analysisType]&~gRemovalSignal
            else:                                dQueue[ts][analysisCode] &= ~gRemovalSignal
            if not dQueue[ts][analysisCode]: del dQueue[ts][analysisCode]
    #Kline Drawing End ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #View Control ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #[1]: Horizontal Position and Magnification
    #---ViewRange Control Params
    def _setHVRParams(self):
        self.expectedKlineTemporalWidth = _EXPECTEDTEMPORALWIDTHS[self.intervalID]
        nKlinesDisplayable_min = self.displayBox['KLINESPRICE'][2]*self.scaler / _GD_DISPLAYBOX_KLINESPRICE_MAXPIXELWIDTH
        nKlinesDisplayable_max = self.displayBox['KLINESPRICE'][2]*self.scaler / _GD_DISPLAYBOX_KLINESPRICE_MINPIXELWIDTH
        self.horizontalViewRangeWidth_min = nKlinesDisplayable_min * self.expectedKlineTemporalWidth
        self.horizontalViewRangeWidth_max = nKlinesDisplayable_max * self.expectedKlineTemporalWidth
        self.horizontalViewRangeWidth_m = (self.horizontalViewRangeWidth_min-self.horizontalViewRangeWidth_max)/(_GD_DISPLAYBOX_KLINESPRICE_HVR_MAXMAGNITUDE-_GD_DISPLAYBOX_KLINESPRICE_HVR_MINMAGNITUDE)
        self.horizontalViewRangeWidth_b = (self.horizontalViewRangeWidth_min*_GD_DISPLAYBOX_KLINESPRICE_HVR_MINMAGNITUDE-self.horizontalViewRangeWidth_max*_GD_DISPLAYBOX_KLINESPRICE_HVR_MAXMAGNITUDE)/(_GD_DISPLAYBOX_KLINESPRICE_HVR_MINMAGNITUDE-_GD_DISPLAYBOX_KLINESPRICE_HVR_MAXMAGNITUDE)

    #---Horizontal Position
    def __editHPosition(self, delta_drag = None, delta_scroll = None):
        #[1]: New Position Calculation
        hvr_beg, hvr_end = self.horizontalViewRange
        if   delta_drag   is not None: effectiveDelta = -delta_drag*(hvr_end-hvr_beg)/self.displayBox_graphics['KLINESPRICE']['DRAWBOX'][2]
        elif delta_scroll is not None: effectiveDelta = -delta_scroll*self.expectedKlineTemporalWidth
        else: return
        hvr_new = [round(hvr_beg+effectiveDelta), 
                   round(hvr_end+effectiveDelta)]
        
        #[2]: Range Control
        tz_rev  = -self.timezoneDelta
        if hvr_new[0] < tz_rev: hvr_new = [tz_rev, hvr_new[1]-hvr_new[0]+tz_rev]

        #[3]: View Range Update
        self.horizontalViewRange = hvr_new
        self._onHViewRangeUpdate(0)
        
    #---Horizontal Magnification
    def __editHMagFactor(self, delta_drag = None, delta_scroll = None):
        #[1]: New Magnification Calculation
        hvr_mag = self.horizontalViewRange_magnification
        if   delta_drag   is not None: hvr_mag_new = hvr_mag - delta_drag*200/self.displayBox_graphics['KLINESPRICE']['DRAWBOX'][2]
        elif delta_scroll is not None: hvr_mag_new = hvr_mag + delta_scroll
        else: return

        #[2]: Rounding & Range Control
        hvr_mag_new = round(hvr_mag_new, 1)
        if   hvr_mag_new < _GD_DISPLAYBOX_KLINESPRICE_HVR_MINMAGNITUDE: hvr_mag_new = _GD_DISPLAYBOX_KLINESPRICE_HVR_MINMAGNITUDE
        elif _GD_DISPLAYBOX_KLINESPRICE_HVR_MAXMAGNITUDE < hvr_mag_new: hvr_mag_new = _GD_DISPLAYBOX_KLINESPRICE_HVR_MAXMAGNITUDE

        #[3]: Variation Check
        if hvr_mag_new == hvr_mag: return

        #[4]: Horizontal View Range Update
        self.horizontalViewRange_magnification = hvr_mag_new
        hvr_new = (round(self.horizontalViewRange[1]-(hvr_mag_new*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b)), self.horizontalViewRange[1])
        tz_rev  = -self.timezoneDelta
        if hvr_new[0] < tz_rev: hvr_new = [tz_rev, hvr_new[1]-hvr_new[0]+tz_rev]
        self.horizontalViewRange = hvr_new
        self._onHViewRangeUpdate(1)
            
    #---Post Horizontal View-Range Update
    def _onHViewRangeUpdate(self, updateType):
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
                    if   siAlloc == 'VOL':      self._editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.0, extension_t = 0.2)
                    elif siAlloc == 'DEPTH':    self._editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                    elif siAlloc == 'AGGTRADE': self._editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                    elif siAlloc == 'MMACD':    self._editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                    elif siAlloc == 'DMIxADX':  self._editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                    elif siAlloc == 'MFI':      self._editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
                    elif siAlloc == 'TPD':      self._editVVR_toExtremaCenter(displayBoxName = siViewerCode, extension_b = 0.1, extension_t = 0.1)
        #[5]: Update PosSelection
        self.__updatePosSelection(updateType = 1)
        
    def __onHViewRangeUpdate_UpdateProcessQueue(self):
        #[1]: Instances
        iID              = self.intervalID
        klines_TSs       = self._data_timestamps[iID]['kline']
        hvr_beg, hvr_end = self.horizontalViewRange
        drawn  = self.__drawn
        dQueue = self.__drawQueue
        dRaw   = self._data_raw
        dAgg   = self._data_agg[iID]

        #[2]: If No Timestamp Target Exists, Return
        if not klines_TSs: 
            self.horizontalViewRange_timestampsInViewRange  = []
            self.horizontalViewRange_timestampsInBufferZone = []
            return

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
        self.__drawRemovalQueue = set(drawn)-br_TSs_set

        #[8]: Draw Queue Update
        dQueue_TSs = set(dQueue)
        for ts in (dQueue_TSs - br_TSs_set):
            del dQueue[ts]
            
        #[9]: Draw Targets Determination
        drawTargets = [('KLINE',        _FULLDRAWSIGNALS['KLINE'],        dAgg['kline']), 
                       ('DEPTHOVERLAY', _FULLDRAWSIGNALS['DEPTHOVERLAY'], dAgg['depth']),
                       ('VOL',          _FULLDRAWSIGNALS['VOL'],          dAgg['kline']),
                       ('DEPTH',        _FULLDRAWSIGNALS['DEPTH'],        dAgg['depth']),
                       ('AGGTRADE',     _FULLDRAWSIGNALS['AGGTRADE'],     dAgg['aggTrade'])]
        if 'tradeLog' in dRaw: 
            drawTargets.append(('TRADELOG', _FULLDRAWSIGNALS['TRADELOG'], dRaw['tradeLog']))
        drawTargets.extend((dType, _FULLDRAWSIGNALS[dType.split("_")[0]], dAgg[dType]) 
                           for dType in dAgg if dType not in _DRAWTARGETRAWNAMEEXCEPTION)
        
        #[10]: Draw Queue Update
        for ts in br_TSs_list:
            #[10-1]: If Drawing Exists Already
            if ts in drawn:
                drawn_ts   = drawn[ts]
                draw_delta = {}
                for dType, fds, data_dict in drawTargets:
                    if ts not in data_dict: continue
                    current_sig = drawn_ts.get(dType, 0)
                    if current_sig != fds:
                        draw_delta[dType] = fds & ~current_sig
                if draw_delta:
                    if ts not in dQueue: dQueue[ts] = {}
                    dQueue[ts].update(draw_delta)
            #[10-2]: If Drawing Does Not Exist
            else:
                dQueue[ts] = {dType: None for dType, fds, data_dict in drawTargets if ts in data_dict}

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
        hvr_beg, hvr_end        = self.horizontalViewRange
        hvr_tz_beg = hvr_beg+self.timezoneDelta
        hvr_tz_end = hvr_end+self.timezoneDelta

        #[2]: Determine Vertical Grid Intervals
        updateGridContents = False
        if updateType == 1:
            for giID in auxiliaries.GRID_INTERVAL_IDs[self.intervalID:]:
                rightEnd       = auxiliaries.getNextIntervalTickTimestamp_GRID(giID, hvr_tz_end, nTicks = 1)
                vGridIntervals = auxiliaries.getTimestampList_byRange_GRID(giID,     hvr_tz_beg, rightEnd, lastTickInclusive = True)
                if len(vGridIntervals)+1 < self.nMaxVerticalGridLines: 
                    break
            self.verticalGrid_intervalID = giID
            self.verticalGrid_intervals  = vGridIntervals
            updateGridContents = True
        elif updateType == 0:
            rightEnd       = auxiliaries.getNextIntervalTickTimestamp_GRID(vGridIntervalID_current, hvr_tz_end, nTicks = 1)
            vGridIntervals = auxiliaries.getTimestampList_byRange_GRID(vGridIntervalID_current,     hvr_tz_beg, rightEnd, lastTickInclusive = True)
            if (vGridIntervals_current[0] != vGridIntervals[0]) or (vGridIntervals_current[-1] != vGridIntervals[-1]): 
                self.verticalGrid_intervals = vGridIntervals
                updateGridContents = True

        #[3]: Update Grid Position & Text
        vGridIntervalID_current = self.verticalGrid_intervalID
        vGridIntervals_current  = self.verticalGrid_intervals
        pixelPerTS = dBox_g['MAINGRID_TEMPORAL']['DRAWBOX'][2]*self.scaler / (hvr_end-hvr_beg)
        if updateGridContents:
            #[3-1]: Instances
            dBox_g_kp_vgLines  = dBox_g['KLINESPRICE']['VERTICALGRID_LINES']
            dBox_g_mgT_vgLines = dBox_g['MAINGRID_TEMPORAL']['VERTICALGRID_LINES']
            dBox_g_mgT_vgTexts = dBox_g['MAINGRID_TEMPORAL']['VERTICALGRID_TEXTS']
            #[3-2]: Grid Loop
            for index in range (self.nMaxVerticalGridLines):
                #[3-2-1]: Active Grid
                if index < len(vGridIntervals_current) and 0 <= vGridIntervals_current[index]:
                    #[3-2-1-1]: TimeZone Timestamp
                    timestamp_tz = vGridIntervals_current[index]
                    #[3-2-1-2]: Coordinate
                    xPos = round((timestamp_tz-self.timezoneDelta-vGridIntervals_current[0])*pixelPerTS, 1)
                    #[3-2-1-3]: Lines Update - MAIN
                    dBox_g_kp_vgLines[index].x  = xPos
                    dBox_g_kp_vgLines[index].x2 = xPos
                    if not dBox_g_kp_vgLines[index].visible: dBox_g_kp_vgLines[index].visible = True
                    dBox_g_mgT_vgLines[index].x  = xPos
                    dBox_g_mgT_vgLines[index].x2 = xPos
                    if not dBox_g_mgT_vgLines[index].visible: dBox_g_mgT_vgLines[index].visible = True
                    #[3-2-1-4]: Texts Update
                    if self.verticalGrid_intervalID <= 11: #Maximum 12 Hours Interval
                        if timestamp_tz % 86400 == 0: dateStrFormat = "%m/%d"
                        else:                         dateStrFormat = "%H:%M"
                    elif self.verticalGrid_intervalID <= 14: #Maximum 1 Week Interval
                        if auxiliaries.isNewMonth(timestamp_tz): dateStrFormat = "%Y/%m"
                        else:                                           dateStrFormat = "%m/%d"
                    elif self.verticalGrid_intervalID <= 17: #Maximum 6 Months Interval
                        if auxiliaries.isNewYear(timestamp_tz): dateStrFormat = "%Y"
                        else:                                          dateStrFormat = "%Y/%m"
                    else:
                        dateStrFormat = "%Y"
                    dBox_g_mgT_vgTexts[index].setText(datetime.fromtimestamp(timestamp_tz, tz = timezone.utc).strftime(dateStrFormat))
                    dBox_g_mgT_vgTexts[index].moveTo(x = round(xPos/self.scaler-_GD_DISPLAYBOX_GRID_VERTICALTEXTWIDTH/2))
                    if dBox_g_mgT_vgTexts[index].hidden: dBox_g_mgT_vgTexts[index].show()
                    #[3-2-1-5]: Lines Update - SI Viwers
                    for siIndex in range (len(_SITYPES)):
                        siCode = f'SIVIEWER{siIndex}'
                        if not oc[f'{siCode}Display']: continue
                        dBox_g_siv_vgLines = dBox_g[siCode]['VERTICALGRID_LINES'][index]
                        dBox_g_siv_vgLines.x  = xPos
                        dBox_g_siv_vgLines.x2 = xPos
                        if not dBox_g_siv_vgLines.visible: 
                            dBox_g_siv_vgLines.visible = True
                #[3-2-2]: Inactive Grid
                else:
                    if dBox_g_kp_vgLines[index].visible:     dBox_g_kp_vgLines[index].visible = False
                    if dBox_g_mgT_vgLines[index].visible:    dBox_g_mgT_vgLines[index].visible = False
                    if not dBox_g_mgT_vgTexts[index].hidden: dBox_g_mgT_vgTexts[index].hide()
                    for siIndex in range (len(_SITYPES)):
                        siCode = f'SIVIEWER{siIndex}'
                        if not oc[f'{siCode}Display']: continue
                        dBox_g_siv_vgLines = dBox_g[siCode]['VERTICALGRID_LINES'][index]
                        if dBox_g_siv_vgLines.visible: dBox_g_siv_vgLines.visible = False

        #[4]: Update Grid CamGroup Projections
        proj_x0 = (hvr_beg-vGridIntervals_current[0])*pixelPerTS
        proj_x1 = proj_x0+dBox_g['MAINGRID_TEMPORAL']['DRAWBOX'][2]*self.scaler
        dBox_g['KLINESPRICE']['VERTICALGRID_CAMGROUP'].updateProjection(projection_x0=proj_x0, projection_x1=proj_x1)
        for dBoxName in self.displayBox_graphics_visibleSIViewers: 
            dBox_g[dBoxName]['VERTICALGRID_CAMGROUP'].updateProjection(projection_x0=proj_x0, projection_x1=proj_x1)
        dBox_g['MAINGRID_TEMPORAL']['VERTICALGRID_CAMGROUP'].updateProjection(projection_x0=proj_x0, projection_x1=proj_x1)

    def __checkVerticalExtremas_KLINES(self):
        #[1]: Instances
        klines      = self._data_agg[self.intervalID]['kline']
        hvr_tssInVR = self.horizontalViewRange_timestampsInViewRange

        #[2]: Timestamps Check
        if not hvr_tssInVR: return False

        #[3]: Extremas Search
        #---Initial Extrema
        valMin = float('inf')
        valMax = float('-inf')
        #---Search Loop
        for ts in hvr_tssInVR:
            kline = klines[ts]
            kl_lp = kline[KLINDEX_LOWPRICE]
            kl_hp = kline[KLINDEX_HIGHPRICE]
            if kl_lp is None or kl_hp is None:
                continue
            if kl_lp < valMin: valMin = kl_lp
            if valMax < kl_hp: valMax = kl_hp
        #---Extrema Check
        if math.isinf(valMin): return False
        if math.isinf(valMax): return False
        #---Extremas Filtering
        if valMin == valMax:
            valMin = valMin-1
            valMax = valMax+1

        #[4]: Change Check & Result Return
        vv_min        = self.verticalValue_min
        vv_max        = self.verticalValue_max
        vvr_precision = self.verticalViewRange_precision
        dBox_g_kp     = self.displayBox_graphics['KLINESPRICE']
        if (vv_min['KLINESPRICE'] != valMin) or (vv_max['KLINESPRICE'] != valMax):
            #[4-1]: Vertical View Range Update
            vv_min['KLINESPRICE'] = valMin
            vv_max['KLINESPRICE'] = valMax

            #[4-2]: Y Precision & RCLCG Precision Update (If Needed)
            vvrWidth_new    = vv_max['KLINESPRICE']-vv_min['KLINESPRICE']
            precision_y_new = math.floor(math.log10(10 / vvrWidth_new))+_VVR_PRECISIONCOMPENSATOR['KLINESPRICE']
            if _VVR_PRECISIONUPDATETHRESHOLD <= abs(vvr_precision['KLINESPRICE']-precision_y_new):
                vvr_precision['KLINESPRICE'] = precision_y_new
                dBox_g_kp['RCLCG'].setPrecision(precision_x        = None, precision_y = precision_y_new, transferObjects = True)
                dBox_g_kp['RCLCG_XFIXED'].setPrecision(precision_x = None, precision_y = precision_y_new, transferObjects = True)

            #[4-3]: Return Result
            return True
        return False
            
    def __checkVerticalExtremas_VOL(self):
        #[1]: References
        oc          = self.objectConfig
        ap          = self.analysisParams[self.intervalID]
        dAgg        = self._data_agg[self.intervalID]
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
        searchTargets = [('kline', aIndex)]
        searchTargets.extend((dType, f'MA_{volType}') 
                             for dType in self.siTypes_analysisCodes['VOL'] 
                             if ((dType != 'VOL') and 
                                 (dType in dAgg)  and 
                                 oc[f"VOL_{ap[dType]['lineIndex']}_Display"]))
        #---Initial Extrema
        valMax = 0
        #---Search Loop
        for dType, valCode in searchTargets:
            tData = dAgg[dType]
            for ts in hvr_tssInVR:
                if ts not in tData: continue
                value = tData[ts][valCode]
                if value is None: continue
                if valMax < value: valMax = value
        #---Extremas Filtering
        if valMax == 0: valMax = 1

        #[4]: Change Check & Result Return
        vv_min        = self.verticalValue_min
        vv_max        = self.verticalValue_max
        vvr_precision = self.verticalViewRange_precision
        dBox_g_this   = self.displayBox_graphics[siViewerCode]
        if vv_max[siViewerCode] != valMax:
            #[4-1]: Vertical View Range Update
            vv_min[siViewerCode] = 0
            vv_max[siViewerCode] = valMax

            #[4-2]: Y Precision & RCLCG Precision Update (If Needed)
            vvrWidth_new    = vv_max[siViewerCode]-vv_min[siViewerCode]
            precision_y_new = math.floor(math.log10(10 / vvrWidth_new))+_VVR_PRECISIONCOMPENSATOR['VOL']
            if _VVR_PRECISIONUPDATETHRESHOLD <= abs(vvr_precision[siViewerCode]-precision_y_new):
                vvr_precision[siViewerCode] = precision_y_new
                dBox_g_this['RCLCG'].setPrecision(precision_x        = None, precision_y = precision_y_new, transferObjects = True)
                dBox_g_this['RCLCG_XFIXED'].setPrecision(precision_x = None, precision_y = precision_y_new, transferObjects = True)

            #[4-3]: Return Result
            return True
        else: return False

    def __checkVerticalExtremas_DEPTH(self):
        #[1]: References
        hvr_tssInVR = self.horizontalViewRange_timestampsInViewRange
        siViewerIndex = self.siTypes_siViewerAlloc['DEPTH']
        siViewerCode  = f"SIVIEWER{siViewerIndex}"

        #[2]: Timestamps Check
        if not hvr_tssInVR: return False

        #[3]: Extremas Search
        valMin = _DEPTHBINS_MIN
        valMax = _DEPTHBINS_MAX
        #---Extremas Filtering
        maxExtrema = max(abs(valMin), abs(valMax))
        if maxExtrema == 0: maxExtrema = 1
        valMin = -maxExtrema
        valMax =  maxExtrema

        #[4]: Change Check & Result Return
        vv_min        = self.verticalValue_min
        vv_max        = self.verticalValue_max
        vvr_precision = self.verticalViewRange_precision
        dBox_g_this   = self.displayBox_graphics[siViewerCode]
        if (vv_min[siViewerCode] != valMin) or (vv_max[siViewerCode] != valMax):
            #[4-1]: Vertical View Range Update
            vv_min[siViewerCode] = valMin
            vv_max[siViewerCode] = valMax

            #[4-2]: Y Precision & RCLCG Precision Update (If Needed)
            vvrWidth_new    = vv_max[siViewerCode]-vv_min[siViewerCode]
            precision_y_new = math.floor(math.log10(10 / vvrWidth_new))+_VVR_PRECISIONCOMPENSATOR['DEPTH']
            if _VVR_PRECISIONUPDATETHRESHOLD <= abs(vvr_precision[siViewerCode]-precision_y_new):
                vvr_precision[siViewerCode] = precision_y_new
                dBox_g_this['RCLCG'].setPrecision(precision_x        = None, precision_y = precision_y_new, transferObjects = True)
                dBox_g_this['RCLCG_XFIXED'].setPrecision(precision_x = None, precision_y = precision_y_new, transferObjects = True)

            #[4-3]: Return Result
            return True
        else: return False
    
    def __checkVerticalExtremas_AGGTRADE(self):
        #[1]: References
        oc          = self.objectConfig
        aggTrades   = self._data_agg[self.intervalID]['aggTrade']
        hvr_tssInVR = self.horizontalViewRange_timestampsInViewRange
        siViewerIndex = self.siTypes_siViewerAlloc['AGGTRADE']
        siViewerCode  = f"SIVIEWER{siViewerIndex}"

        #[2]: Timestamps Check
        if not hvr_tssInVR: return False

        #[3]: Extremas Search
        #---Initial Extrema
        valMin = float('inf')
        valMax = float('-inf')
        #---Search Loop
        displayType = oc['AGGTRADE_DisplayType']
        if displayType == 'QUANTITY':
            dIdx_buy  = ATINDEX_QUANTITYBUY
            dIdx_sell = ATINDEX_QUANTITYSELL
        elif displayType == 'NTRADES':
            dIdx_buy  = ATINDEX_NTRADESBUY
            dIdx_sell = ATINDEX_NTRADESSELL
        elif displayType == 'NOTIONAL':
            dIdx_buy  = ATINDEX_NOTIONALBUY
            dIdx_sell = ATINDEX_NOTIONALSELL
        for ts in hvr_tssInVR:
            aggTrade = aggTrades.get(ts, None)
            if aggTrade is None: 
                continue
            val_buy  = aggTrade[dIdx_buy]
            val_sell = aggTrade[dIdx_sell]
            if val_buy is None or val_sell is None: 
                continue
            if -val_sell < valMin: valMin = -val_sell
            if valMax < val_buy:   valMax =  val_buy
        #---Extrema Check
        if math.isinf(valMin): return False
        if math.isinf(valMax): return False
        #---Extremas Filtering
        maxExtrema = max(abs(valMin), abs(valMax))
        if maxExtrema == 0: maxExtrema = 1
        valMin = -maxExtrema
        valMax =  maxExtrema

        #[4]: Change Check & Result Return
        vv_min        = self.verticalValue_min
        vv_max        = self.verticalValue_max
        vvr_precision = self.verticalViewRange_precision
        dBox_g_this   = self.displayBox_graphics[siViewerCode]
        if (vv_min[siViewerCode] != valMin) or (vv_max[siViewerCode] != valMax):
            #[4-1]: Vertical View Range Update
            vv_min[siViewerCode] = valMin
            vv_max[siViewerCode] = valMax

            #[4-2]: Y Precision & RCLCG Precision Update (If Needed)
            vvrWidth_new    = vv_max[siViewerCode]-vv_min[siViewerCode]
            precision_y_new = math.floor(math.log10(10 / vvrWidth_new))+_VVR_PRECISIONCOMPENSATOR['AGGTRADE']
            if _VVR_PRECISIONUPDATETHRESHOLD <= abs(vvr_precision[siViewerCode]-precision_y_new):
                vvr_precision[siViewerCode] = precision_y_new
                dBox_g_this['RCLCG'].setPrecision(precision_x        = None, precision_y = precision_y_new, transferObjects = True)
                dBox_g_this['RCLCG_XFIXED'].setPrecision(precision_x = None, precision_y = precision_y_new, transferObjects = True)

            #[4-3]: Return Result
            return True
        else: return False

    def __checkVerticalExtremas_NNA(self):
        #[1]: References
        oc          = self.objectConfig
        ap          = self.analysisParams[self.intervalID]
        dAgg        = self._data_agg[self.intervalID]
        hvr_tssInVR = self.horizontalViewRange_timestampsInViewRange
        siViewerIndex = self.siTypes_siViewerAlloc['NNA']
        siViewerCode  = f"SIVIEWER{siViewerIndex}"

        #[2]: Timestamps Check
        if not hvr_tssInVR: return False

        #[3]: Extremas Search
        #---Analysis Codes To Consider
        searchTargets = [(dType, 'NNA') 
                        for dType in self.siTypes_analysisCodes['NNA'] 
                        if ((dType in dAgg) and 
                            oc[f"NNA_{ap[dType]['lineIndex']}_Display"])]
        #---Initial Extrema
        valMin = float('inf')
        valMax = float('-inf')
        #---Search Loop
        for dType, valCode in searchTargets:
            tData = dAgg[dType]
            for ts in hvr_tssInVR:
                if ts not in tData: continue
                value = tData[ts][valCode]
                if value is None: continue
                if value < valMin: valMin = value
                if valMax < value: valMax = value
        #---Extrema Check
        if math.isinf(valMin): return False
        if math.isinf(valMax): return False
        #---Extremas Filtering
        maxExtrema = max(abs(valMin), abs(valMax))
        if maxExtrema == 0: maxExtrema = 1
        valMin = -maxExtrema
        valMax =  maxExtrema

        #[4]: Change Check & Result Return
        vv_min        = self.verticalValue_min
        vv_max        = self.verticalValue_max
        vvr_precision = self.verticalViewRange_precision
        dBox_g_this   = self.displayBox_graphics[siViewerCode]
        if (vv_min[siViewerCode] != valMin) or (vv_max[siViewerCode] != valMax):
            #[4-1]: Vertical View Range Update
            vv_min[siViewerCode] = valMin
            vv_max[siViewerCode] = valMax

            #[4-2]: Y Precision & RCLCG Precision Update (If Needed)
            vvrWidth_new    = vv_max[siViewerCode]-vv_min[siViewerCode]
            precision_y_new = math.floor(math.log10(10 / vvrWidth_new))+_VVR_PRECISIONCOMPENSATOR['NNA']
            if _VVR_PRECISIONUPDATETHRESHOLD <= abs(vvr_precision[siViewerCode]-precision_y_new):
                vvr_precision[siViewerCode] = precision_y_new
                dBox_g_this['RCLCG'].setPrecision(precision_x        = None, precision_y = precision_y_new, transferObjects = True)
                dBox_g_this['RCLCG_XFIXED'].setPrecision(precision_x = None, precision_y = precision_y_new, transferObjects = True)

            #[4-3]: Return Result
            return True
        else: return False

    def __checkVerticalExtremas_MMACD(self):
        #[1]: References
        oc          = self.objectConfig
        dAgg        = self._data_agg[self.intervalID]
        hvr_tssInVR = self.horizontalViewRange_timestampsInViewRange
        siViewerIndex = self.siTypes_siViewerAlloc['MMACD']
        siViewerCode  = f"SIVIEWER{siViewerIndex}"

        #[2]: Timestamps Check
        if not hvr_tssInVR: return False

        #[3]: Data Check
        if "MMACD" not in dAgg: return False

        #[4]: Extremas Search
        #---Analysis Codes To Consider
        searchTargets = [valCode
                         for valCode, lineCode in (('MMACD', 'MMACD'), ('SIGNAL', 'SIGNAL'), (oc['MMACD_HISTOGRAM_Type'], 'HISTOGRAM'))
                         if oc[f"MMACD_{lineCode}_Display"]]
        #---Initial Extrema
        valMin = float('inf')
        valMax = float('-inf')
        #---Search Loop
        tData = dAgg["MMACD"]
        for valCode in searchTargets:
            for ts in hvr_tssInVR:
                if ts not in tData: continue
                value = tData[ts][valCode]
                if value is None: continue
                if value < valMin: valMin = value
                if valMax < value: valMax = value
        #---Extrema Check
        if math.isinf(valMin): return False
        if math.isinf(valMax): return False
        #---Extremas Filtering
        maxExtrema = max(abs(valMin), abs(valMax))
        if maxExtrema == 0: maxExtrema = 1
        valMin = -maxExtrema
        valMax =  maxExtrema

        #[5]: Change Check & Result Return
        vv_min        = self.verticalValue_min
        vv_max        = self.verticalValue_max
        vvr_precision = self.verticalViewRange_precision
        dBox_g_this   = self.displayBox_graphics[siViewerCode]
        if (vv_min[siViewerCode] != valMin) or (vv_max[siViewerCode] != valMax):
            #[5-1]: Vertical View Range Update
            vv_min[siViewerCode] = valMin
            vv_max[siViewerCode] = valMax

            #[5-2]: Y Precision & RCLCG Precision Update (If Needed)
            vvrWidth_new    = vv_max[siViewerCode]-vv_min[siViewerCode]
            precision_y_new = math.floor(math.log10(10 / vvrWidth_new))+_VVR_PRECISIONCOMPENSATOR['MMACD']
            if _VVR_PRECISIONUPDATETHRESHOLD <= abs(vvr_precision[siViewerCode]-precision_y_new):
                vvr_precision[siViewerCode] = precision_y_new
                dBox_g_this['RCLCG'].setPrecision(precision_x        = None, precision_y = precision_y_new, transferObjects = True)
                dBox_g_this['RCLCG_XFIXED'].setPrecision(precision_x = None, precision_y = precision_y_new, transferObjects = True)

            #[5-3]: Return Result
            return True
        else: return False

    def __checkVerticalExtremas_DMIxADX(self):
        #[1]: References
        oc          = self.objectConfig
        ap          = self.analysisParams[self.intervalID]
        dAgg        = self._data_agg[self.intervalID]
        hvr_tssInVR = self.horizontalViewRange_timestampsInViewRange
        siViewerIndex = self.siTypes_siViewerAlloc['DMIxADX']
        siViewerCode  = f"SIVIEWER{siViewerIndex}"

        #[2]: Timestamps Check
        if not hvr_tssInVR: return False

        #[3]: Extremas Search
        #---Analysis Codes To Consider
        searchTargets = [(dType, 'DMIxADX_ABSATHREL') 
                        for dType in self.siTypes_analysisCodes['DMIxADX'] 
                        if ((dType in dAgg) and 
                            oc[f"DMIxADX_{ap[dType]['lineIndex']}_Display"])]
        #---Initial Extrema
        valMin = float('inf')
        valMax = float('-inf')
        #---Search Loop
        for dType, valCode in searchTargets:
            tData = dAgg[dType]
            for ts in hvr_tssInVR:
                if ts not in tData: continue
                value = tData[ts][valCode]
                if value is None: continue
                if value < valMin: valMin = value
                if valMax < value: valMax = value
        #---Extrema Check
        if math.isinf(valMin): return False
        if math.isinf(valMax): return False
        #---Extremas Filtering
        maxExtrema = max(abs(valMin), abs(valMax))
        if maxExtrema == 0: maxExtrema = 1
        valMin = -maxExtrema
        valMax =  maxExtrema

        #[4]: Change Check & Result Return
        vv_min        = self.verticalValue_min
        vv_max        = self.verticalValue_max
        vvr_precision = self.verticalViewRange_precision
        dBox_g_this   = self.displayBox_graphics[siViewerCode]
        if (vv_min[siViewerCode] != valMin) or (vv_max[siViewerCode] != valMax):
            #[4-1]: Vertical View Range Update
            vv_min[siViewerCode] = valMin
            vv_max[siViewerCode] = valMax

            #[4-2]: Y Precision & RCLCG Precision Update (If Needed)
            vvrWidth_new    = vv_max[siViewerCode]-vv_min[siViewerCode]
            precision_y_new = math.floor(math.log10(10 / vvrWidth_new))+_VVR_PRECISIONCOMPENSATOR['DMIxADX']
            if _VVR_PRECISIONUPDATETHRESHOLD <= abs(vvr_precision[siViewerCode]-precision_y_new):
                vvr_precision[siViewerCode] = precision_y_new
                dBox_g_this['RCLCG'].setPrecision(precision_x        = None, precision_y = precision_y_new, transferObjects = True)
                dBox_g_this['RCLCG_XFIXED'].setPrecision(precision_x = None, precision_y = precision_y_new, transferObjects = True)

            #[4-3]: Return Result
            return True
        else: return False

    def __checkVerticalExtremas_MFI(self):
        #[1]: References
        oc          = self.objectConfig
        ap          = self.analysisParams[self.intervalID]
        dAgg        = self._data_agg[self.intervalID]
        hvr_tssInVR = self.horizontalViewRange_timestampsInViewRange
        siViewerIndex = self.siTypes_siViewerAlloc['MFI']
        siViewerCode  = f"SIVIEWER{siViewerIndex}"

        #[2]: Timestamps Check
        if not hvr_tssInVR: return False

        #[3]: Extremas Search
        #---Analysis Codes To Consider
        searchTargets = [(dType, 'MFI_ABSATHDEVREL') 
                        for dType in self.siTypes_analysisCodes['MFI'] 
                        if ((dType in dAgg) and 
                            oc[f"MFI_{ap[dType]['lineIndex']}_Display"])]
        #---Initial Extrema
        valMin = float('inf')
        valMax = float('-inf')
        #---Search Loop
        for dType, valCode in searchTargets:
            tData = dAgg[dType]
            for ts in hvr_tssInVR:
                if ts not in tData: continue
                value = tData[ts][valCode]
                if value is None: continue
                if value < valMin: valMin = value
                if valMax < value: valMax = value
        #---Extrema Check
        if math.isinf(valMin): return False
        if math.isinf(valMax): return False
        #---Extremas Filtering
        delta         = 0.5
        fromDelta_min = valMin-delta
        fromDelta_max = valMax-delta
        fromDelta_maxExtrema = max(abs(fromDelta_min), abs(fromDelta_max))
        if fromDelta_maxExtrema == 0: fromDelta_maxExtrema = 1
        valMin = -fromDelta_maxExtrema+delta
        valMax =  fromDelta_maxExtrema+delta

        #[4]: Change Check & Result Return
        vv_min        = self.verticalValue_min
        vv_max        = self.verticalValue_max
        vvr_precision = self.verticalViewRange_precision
        dBox_g_this   = self.displayBox_graphics[siViewerCode]
        if (vv_min[siViewerCode] != valMin) or (vv_max[siViewerCode] != valMax):
            #[4-1]: Vertical View Range Update
            vv_min[siViewerCode] = valMin
            vv_max[siViewerCode] = valMax

            #[4-2]: Y Precision & RCLCG Precision Update (If Needed)
            vvrWidth_new    = vv_max[siViewerCode]-vv_min[siViewerCode]
            precision_y_new = math.floor(math.log10(10 / vvrWidth_new))+_VVR_PRECISIONCOMPENSATOR['MFI']
            if _VVR_PRECISIONUPDATETHRESHOLD <= abs(vvr_precision[siViewerCode]-precision_y_new):
                vvr_precision[siViewerCode] = precision_y_new
                dBox_g_this['RCLCG'].setPrecision(precision_x        = None, precision_y = precision_y_new, transferObjects = True)
                dBox_g_this['RCLCG_XFIXED'].setPrecision(precision_x = None, precision_y = precision_y_new, transferObjects = True)

            #[4-3]: Return Result
            return True
        else: return False

    def __checkVerticalExtremas_TPD(self):
        #[1]: References
        oc          = self.objectConfig
        ap          = self.analysisParams[self.intervalID]
        dAgg        = self._data_agg[self.intervalID]
        hvr_tssInVR = self.horizontalViewRange_timestampsInViewRange
        siViewerIndex = self.siTypes_siViewerAlloc['TPD']
        siViewerCode  = f"SIVIEWER{siViewerIndex}"

        #[2]: Timestamps Check
        if not hvr_tssInVR: return False

        #[3]: Extremas Search
        #---Analysis Codes To Consider
        searchTargets = [(dType, 'TPD_BIASMA') 
                        for dType in self.siTypes_analysisCodes['TPD'] 
                        if ((dType in dAgg) and 
                            oc[f"TPD_{ap[dType]['lineIndex']}_Display"])]
        #---Initial Extrema
        valMin = float('inf')
        valMax = float('-inf')
        #---Search Loop
        for dType, valCode in searchTargets:
            tData = dAgg[dType]
            for ts in hvr_tssInVR:
                if ts not in tData: continue
                value = tData[ts][valCode]
                if value is None: continue
                if value < valMin: valMin = value
                if valMax < value: valMax = value
        #---Extrema Check
        if math.isinf(valMin): return False
        if math.isinf(valMax): return False
        #---Extremas Filtering
        maxExtrema = max(abs(valMin), abs(valMax))
        if maxExtrema == 0: maxExtrema = 1
        valMin = -maxExtrema
        valMax =  maxExtrema

        #[4]: Change Check & Result Return
        vv_min        = self.verticalValue_min
        vv_max        = self.verticalValue_max
        vvr_precision = self.verticalViewRange_precision
        dBox_g_this   = self.displayBox_graphics[siViewerCode]
        if (vv_min[siViewerCode] != valMin) or (vv_max[siViewerCode] != valMax):
            #[4-1]: Vertical View Range Update
            vv_min[siViewerCode] = valMin
            vv_max[siViewerCode] = valMax

            #[4-2]: Y Precision & RCLCG Precision Update (If Needed)
            vvrWidth_new    = vv_max[siViewerCode]-vv_min[siViewerCode]
            precision_y_new = math.floor(math.log10(10 / vvrWidth_new))+_VVR_PRECISIONCOMPENSATOR['TPD']
            if _VVR_PRECISIONUPDATETHRESHOLD <= abs(vvr_precision[siViewerCode]-precision_y_new):
                vvr_precision[siViewerCode] = precision_y_new
                dBox_g_this['RCLCG'].setPrecision(precision_x        = None, precision_y = precision_y_new, transferObjects = True)
                dBox_g_this['RCLCG_XFIXED'].setPrecision(precision_x = None, precision_y = precision_y_new, transferObjects = True)

            #[4-3]: Return Result
            return True
        else: return False

    def __onVerticalExtremaUpdate(self, displayBoxName, updateType = 0):
        #[1]: Instances
        dBox    = displayBoxName
        vv_min  = self.verticalValue_min
        vv_max  = self.verticalValue_max
        vvr     = self.verticalViewRange
        vvr_mag = self.verticalViewRange_magnification

        #[2]: View Range Delta & Limits
        veDelta = vv_max[dBox]-vv_min[dBox]
        vrHeight_new_min = veDelta*100/_GD_DISPLAYBOX_VVR_MAGNITUDE_MAX[dBox]
        vrHeight_new_max = veDelta*100/_GD_DISPLAYBOX_VVR_MAGNITUDE_MIN[dBox]

        #[3]: View Range Computation
        #---[3-1]: Updating By Drag
        if updateType == 0:
            vvrCenter_prev = (vvr[dBox][0]+vvr[dBox][1])/2
            vvrHeight_prev = vvr[dBox][1]-vvr[dBox][0]
            if vvrHeight_prev < vrHeight_new_min: 
                vvr[dBox]     = [vvrCenter_prev-vrHeight_new_min*0.5, vvrCenter_prev+vrHeight_new_min*0.5]
                vvr_mag[dBox] = _GD_DISPLAYBOX_VVR_MAGNITUDE_MAX[dBox]
            elif vrHeight_new_max < vvrHeight_prev: 
                vvr[dBox]     = [vvrCenter_prev-vrHeight_new_max*0.5, vvrCenter_prev+vrHeight_new_max*0.5]
                vvr_mag[dBox] = _GD_DISPLAYBOX_VVR_MAGNITUDE_MIN[dBox]
            else:
                vvr_mag[dBox] = round(veDelta/vvrHeight_prev*100, 1)
            if vvrHeight_prev == vvr[dBox][1]-vvr[dBox][0]: self.__onVViewRangeUpdate(dBox, 0)
            else:                                           self.__onVViewRangeUpdate(dBox, 1)
        #---[3-2]: Updating By Jump
        elif updateType == 1:
            extremaCenter = (vv_min[dBox]+vv_max[dBox])/2
            vvr_mag[dBox] = _GD_DISPLAYBOX_VVR_MAGNITUDE_MAX[dBox]
            vvr[dBox]     = [extremaCenter-vrHeight_new_min*0.5, extremaCenter+vrHeight_new_min*0.5]
            self.__onVViewRangeUpdate(dBox, 1)
        
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
        #[1]: Instances
        dBoxName     = displayBoxName
        vvr_0, vvr_1 = self.verticalViewRange[dBoxName]
        vvr_mag      = self.verticalViewRange_magnification[dBoxName]

        #[2]: New Magnification Factor
        if   delta_drag   is not None: mag_new = vvr_mag + delta_drag*200/self.displayBox_graphics[displayBoxName]['DRAWBOX'][3]
        elif delta_scroll is not None: mag_new = vvr_mag + delta_scroll
        else: return
        mag_new = round(mag_new, 1)

        #[3]: Boundary Control
        if   mag_new < _GD_DISPLAYBOX_VVR_MAGNITUDE_MIN[dBoxName]: mag_new = _GD_DISPLAYBOX_VVR_MAGNITUDE_MIN[dBoxName]
        elif _GD_DISPLAYBOX_VVR_MAGNITUDE_MAX[dBoxName] < mag_new: mag_new = _GD_DISPLAYBOX_VVR_MAGNITUDE_MAX[dBoxName]

        #[4]: Change Check
        if mag_new == vvr_mag: return

        #[5]: Determine New View Range
        self.verticalViewRange_magnification[dBoxName] = mag_new
        veWidth     = self.verticalValue_max[dBoxName]-self.verticalValue_min[dBoxName]
        veWidth_mag = veWidth*100/mag_new
        if anchor == 'CENTER':
            vVRCenter = (vvr_0+vvr_1)/2
            vVR_effective = [vVRCenter-veWidth_mag*0.5, vVRCenter+veWidth_mag*0.5]
        elif anchor == 'BOTTOM': 
            vVR_effective = [vvr_0, vvr_0+veWidth_mag]
        elif anchor == 'TOP':    
            vVR_effective = [vvr_1-veWidth_mag, vvr_1]
        self.verticalViewRange[dBoxName] = vVR_effective

        #[6]: Update Handler
        self.__onVViewRangeUpdate(dBoxName, 1)
            
    #---Reset vVR_price
    def _editVVR_toExtremaCenter(self, displayBoxName, extension_b = 0.1, extension_t = 0.1):
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
        #[1]: Instances
        dBoxName     = displayBoxName
        dBox         = self.displayBox_graphics
        dBox_g_main  = dBox[dBoxName]
        dBox_g_grid  = dBox[f'MAINGRID_{dBoxName}']
        vvr_0, vvr_1 = self.verticalViewRange[dBoxName]
        hgis         = self.horizontalGridIntervals
        hgiHeight    = self.horizontalGridIntervalHeight
        nMaxHGLs     = self.nMaxHorizontalGridLines[dBoxName]
        scaler       = self.scaler
        if displayBoxName == 'KLINESPRICE': hglCenter = _VVR_HGLCENTERS[displayBoxName]
        else:                               hglCenter = _VVR_HGLCENTERS[self.objectConfig[f'{displayBoxName}SIAlloc']]
        func_svf = auxiliaries.simpleValueFormatter

        #[2]: Update RCLCGs Projections
        dBox_g_main['RCLCG'].updateProjection(projection_y0        = vvr_0, projection_y1 = vvr_1)
        dBox_g_main['RCLCG_XFIXED'].updateProjection(projection_y0 = vvr_0, projection_y1 = vvr_1)

        #[3]: Compute New Horizontal Grid Lines
        hgIntervals = None
        #---[3-1]: Non-Continuous Type
        if updateType == 1:
            #[3-1-1]: View Range Height Order Of Magnitude
            viewRangeHeight_OOM = math.floor(math.log((vvr_1-vvr_0), 10))
            #[3-1-2]: Most Appropriate Interval Factor Search
            for intervalFactor in (0.1, 0.25, 0.5, 0.75, 1, 2.5, 5, 7.5):
                #[3-1-2-1]: Interval Height Calculation & Check
                intervalHeight = intervalFactor*pow(10, viewRangeHeight_OOM)
                if intervalHeight == 0: continue
                #[3-1-2-2]: Grid Interval Lines Range
                idx_beg = math.floor((vvr_0-hglCenter)/intervalHeight)
                idx_end = math.ceil((vvr_1 -hglCenter)/intervalHeight)
                if nMaxHGLs < (idx_end - idx_beg + 1): continue
                #[3-1-2-3]: Horizontal Grid Line Intervals Determination
                hgIntervals         = [hglCenter+(intervalHeight*glIdx) for glIdx in range(idx_beg, idx_end+1)]
                hgiHeight[dBoxName] = intervalHeight
                break

        #---[3-2]: Continuous Type
        elif updateType == 0:
            #[3-2-1]: Current Horizontal Grid Intervals and Height
            hgis_current      = hgis[dBoxName]
            hgiHeight_current = hgiHeight[dBoxName]
            #[3-2-2]: Current Horizontal Grid Intervals and Height
            idx_beg = math.floor((vvr_0-hglCenter)/hgiHeight_current)
            idx_end = math.ceil((vvr_1 -hglCenter)/hgiHeight_current)
            hgis_new_beg = hglCenter + (idx_beg*hgiHeight_current)
            hgis_new_end = hglCenter + (idx_end*hgiHeight_current)
            #[3-2-3]: Horizontal Grid Line Intervals Update Check & Determination
            if not hgis_current or (hgis_current[0] != hgis_new_beg) or (hgis_current[-1] != hgis_new_end):
                hgIntervals = [hglCenter+(hgiHeight_current*glIdx) for glIdx in range(idx_beg, idx_end+1)]

        #[4]: Unit Pixel Per Height
        ppuh = dBox_g_main['DRAWBOX'][3]*scaler / (vvr_1-vvr_0)

        #[5]: Update Grid Contents
        if hgIntervals is not None:
            #[5-1]: Update Graphics
            for glIndex in range (nMaxHGLs):
                #[5-1-1]: Instances
                dBox_g_main_hg_lines = dBox_g_main['HORIZONTALGRID_LINES'][glIndex]
                dBox_g_grid_hg_lines = dBox_g_grid['HORIZONTALGRID_LINES'][glIndex]
                dBox_g_grid_hg_texts = dBox_g_grid['HORIZONTALGRID_TEXTS'][glIndex]
                #[5-2]: Active Intervals
                if (glIndex < len(hgIntervals)) and (vvr_0 <= hgIntervals[glIndex] <= vvr_1):
                    #[5-2-1]: Position
                    verticalValue = hgIntervals[glIndex]
                    yPos_Line     = round((verticalValue-hgIntervals[0])*ppuh, 1)
                    #[5-2-2]: Grid Lines Update
                    dBox_g_main_hg_lines.y  = yPos_Line
                    dBox_g_main_hg_lines.y2 = yPos_Line
                    dBox_g_grid_hg_lines.y  = yPos_Line
                    dBox_g_grid_hg_lines.y2 = yPos_Line
                    if not dBox_g_main_hg_lines.visible: dBox_g_main_hg_lines.visible = True
                    if not dBox_g_grid_hg_lines.visible: dBox_g_grid_hg_lines.visible = True
                    if abs(verticalValue - hglCenter) < 1e-9:
                        dBox_g_main_hg_lines.color = self.gridColor_Heavy
                        dBox_g_main_hg_lines.width = 1.5
                    else:
                        dBox_g_main_hg_lines.color = self.gridColor
                        dBox_g_main_hg_lines.width = 1
                    #[5-2-3]: Grid Text Update
                    if verticalValue == 0: vv_str = "0"
                    else:                  vv_str = func_svf(value = verticalValue, precision = 3)
                    dBox_g_grid_hg_texts.setText(vv_str)
                    dBox_g_grid_hg_texts.moveTo(y = round((yPos_Line)/scaler-_GD_DISPLAYBOX_GRID_HORIZONTALTEXTHEIGHT/2))
                    if dBox_g_grid_hg_texts.hidden: dBox_g_grid_hg_texts.show()
                #[5-3]: Inactive Intervals
                else:
                    if dBox_g_main_hg_lines.visible:    dBox_g_main_hg_lines.visible = False
                    if dBox_g_grid_hg_lines.visible:    dBox_g_grid_hg_lines.visible = False
                    if not dBox_g_grid_hg_texts.hidden: dBox_g_grid_hg_texts.hide()

            #[5-3]: Update Horizontal Grid Intervals
            hgis[dBoxName] = hgIntervals

        #[6]: Update Grid Camera Groups Projections
        if hgis[dBoxName]:
            proj_y0 = (vvr_0-hgis[dBoxName][0])*ppuh
            proj_y1 = proj_y0+dBox_g_main['DRAWBOX'][3]*scaler
            dBox_g_main['HORIZONTALGRID_CAMGROUP'].updateProjection(projection_y0    = proj_y0, projection_y1 = proj_y1)
            dBox_g_main['DESCRIPTORDISPLAY_CAMGROUP'].updateProjection(projection_y0 = proj_y0, projection_y1 = proj_y1)
            dBox_g_grid['HORIZONTALGRID_CAMGROUP'].updateProjection(projection_y0    = proj_y0, projection_y1 = proj_y1)
    #View Control END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    


    #Data Control -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def setTarget(self, target):
        pass
   
    def _clearData(self):
        self._data_raw        = {target: dict() for target in ('kline', 'depth', 'aggTrade')}                    #self._data_raw[dataType][timestamp]
        self._data_agg        = {self.intervalID: {target: dict() for target in ('kline', 'depth', 'aggTrade')}} #self._data_agg[intervalID][dataType][timestamp]
        self._data_timestamps = {self.intervalID: {target: list() for target in ('kline', 'depth', 'aggTrade')}} #self._data_timestamps[intervalID][dataType]

    def _setLoadingCover(self, show, text, gaugeValue):
        self.__loading = show
        if show:
            self.frameSprites['KLINELOADINGCOVER'].visible = True
            self.loadingGaugeBar.show()
            self.loadingTextBox.show()
            self.loadingTextBox_perc.show()
            self.loadingTextBox.updateText(text = text)
            if gaugeValue is None:
                self.loadingGaugeBar.updateGaugeValue(gaugeValue = 0)
                self.loadingTextBox_perc.updateText(text = "-")
            else:
                self.loadingGaugeBar.updateGaugeValue(gaugeValue = gaugeValue)
                if gaugeValue == 100.0: gaugeValue_text = f"100 %"
                else:                   gaugeValue_text = f"{gaugeValue:.3f} %"
                self.loadingTextBox_perc.updateText(text = gaugeValue_text)
        else:
            self.frameSprites['KLINELOADINGCOVER'].visible = False
            self.loadingGaugeBar.hide()
            self.loadingTextBox.hide()
            self.loadingTextBox_perc.hide()
        self.window.dispatch_events()
        self.window.dispatch_event('on_draw')
        self.window.flip()

    def _readCurrencyAnalysisConfiguration(self, currencyAnalysisConfiguration):
        oc  = self.objectConfig
        cac = currencyAnalysisConfiguration
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
                    guios_SWING[f"INDICATOR_SWING{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_SWING[f"INDICATOR_SWING{lineIndex}_DISPLAY"].deactivate()
        else:
            guios_MAIN["MAININDICATOR_SWING"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MAIN["MAININDICATOR_SWING"].deactivate()
            guios_MAIN["MAININDICATORSETUP_SWING"].deactivate()
        #VOL
        if cac['VOL_Master']:
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
            guios_VOL["INDICATOR_VOLTYPESELECTION"].setSelected(itemKey = oc['VOL_VolumeType'], callSelectionUpdateFunction = False)
            guios_VOL["INDICATOR_MATYPESELECTION"].setSelected(itemKey  = cac['VOL_MAType'],    callSelectionUpdateFunction = False)
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
        #MMACD
        if cac['MMACD_Master']:
            guios_MAIN["SUBINDICATOR_MMACD"].activate()
            guios_MAIN["SUBINDICATORSETUP_MMACD"].activate()
            for lineIndex in range (_NMAXLINES['MMACD']):
                if cac[f'MMACD_MA{lineIndex}_LineActive']:
                    nSamples = cac[f'MMACD_MA{lineIndex}_NSamples']
                    guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
                    guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
                else:
                    guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].updateText("-")
            signalNSamples = cac['MMACD_SignalNSamples']
            guios_MMACD["INDICATOR_SIGNALINTERVALTEXTINPUT"].updateText(f"{signalNSamples}")
        else:
            guios_MAIN["SUBINDICATOR_MMACD"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MAIN["SUBINDICATOR_MMACD"].deactivate()
            guios_MAIN["SUBINDICATORSETUP_MMACD"].deactivate()
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
        #TPD
        if cac['TPD_Master']:
            guios_MAIN["SUBINDICATOR_TPD"].activate()
            guios_MAIN["SUBINDICATORSETUP_TPD"].activate()
            for lineIndex in range (_NMAXLINES['TPD']):
                if cac[f'TPD_{lineIndex}_LineActive']:
                    viewLength = cac[f'TPD_{lineIndex}_ViewLength']
                    nSamples   = cac[f'TPD_{lineIndex}_NSamples']
                    nSamplesMA = cac[f'TPD_{lineIndex}_NSamplesMA']
                    width      = oc[f'TPD_{lineIndex}_Width']
                    display    = oc[f'TPD_{lineIndex}_Display']
                    guios_TPD[f"INDICATOR_TPD{lineIndex}"].setStatus(status = True)
                    guios_TPD[f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT"].updateText(f"{viewLength}")
                    guios_TPD[f"INDICATOR_TPD{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
                    guios_TPD[f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT"].updateText(f"{nSamplesMA}")
                    guios_TPD[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].activate()
                    guios_TPD[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
                    guios_TPD[f"INDICATOR_TPD{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                    guios_TPD[f"INDICATOR_TPD{lineIndex}_DISPLAY"].activate()
                else:
                    guios_TPD[f"INDICATOR_TPD{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_TPD[f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT"].updateText("-")
                    guios_TPD[f"INDICATOR_TPD{lineIndex}_INTERVALINPUT"].updateText("-")
                    guios_TPD[f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT"].updateText("-")
                    guios_TPD[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].deactivate()
                    guios_TPD[f"INDICATOR_TPD{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
                    guios_TPD[f"INDICATOR_TPD{lineIndex}_DISPLAY"].deactivate()
        else:
            guios_MAIN["SUBINDICATOR_TPD"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MAIN["SUBINDICATOR_TPD"].deactivate()
            guios_MAIN["SUBINDICATORSETUP_TPD"].deactivate()
        #SI Viewers
        for siViewerIndex in range (len(_SITYPES)):
            if siViewerIndex < self.usableSIViewers:
                guios_MAIN[f"SUBINDICATOR_DISPLAYSWITCH{siViewerIndex}"].activate()
                guios_MAIN[f"SUBINDICATOR_DISPLAYSELECTION{siViewerIndex}"].activate()
            else:
                guios_MAIN[f"SUBINDICATOR_DISPLAYSWITCH{siViewerIndex}"].deactivate()
                guios_MAIN[f"SUBINDICATOR_DISPLAYSELECTION{siViewerIndex}"].deactivate()
        self.objectConfig['VOL_MAType'] = cac['VOL_MAType']
    
    def _onAggregationIntervalUpdate(self, previousIntervalID):
        pass
    
    def _onAnalysisRangeUpdate(self):
        pass

    def _onStartAnalysis(self):
        pass

    def _onAnalysisConfigurationUpdate(self):
        pass
    
    def _updateSITypeAnalysisCodes(self):
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
    #Data Control END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def getGroupRequirement():
        return 50
#'chartDrawer' END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------