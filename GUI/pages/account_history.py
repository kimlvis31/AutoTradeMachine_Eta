#ATM Modules
import ipc
import auxiliaries
from GUI.generals import passiveGraphics_wrapperTypeC,\
                         textBox_typeA,\
                         imageBox_typeA,\
                         button_typeA,\
                         button_typeB,\
                         switch_typeC,\
                         textInputBox_typeA,\
                         selectionBox_typeB,\
                         selectionBox_typeC
from GUI.chart_drawer_account_viewer import chartDrawer_accountViewer
from GUI.periodic_report_viewer      import periodicReportViewer

#Python Modules
import pyglet
import termcolor
import time
from datetime import datetime, timezone

#Constants
_IPC_THREADTYPE_MT = ipc._THREADTYPE_MT
_IPC_THREADTYPE_AT = ipc._THREADTYPE_AT

_ASSETPRECISIONS    = {'USDT': 8, 'USDC': 8, 'BTC': 6}
_ASSETPRECISIONS_S  = {'USDT': 4, 'USDC': 4, 'BTC': 4}
_ASSETPRECISIONS_XS = {'USDT': 2, 'USDC': 2, 'BTC': 2}

_CLOCK_UPDATE_INTERVAL_NS = 100e6

#SETUP PAGE <MAIN> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def setupPage(self):
    #Set page unique variables
    self.puVar['accounts']                                 = dict()
    self.puVar['accounts_selected']                        = None
    self.puVar['currencyAnalysis']                         = dict()
    self.puVar['currencyAnalysis_selected']                = None
    self.puVar['historyView_selected']                     = 'POSITIONCHART'
    self.puVar['historyView_tradeLogsFetchRID']            = None
    self.puVar['historyView_tradeLogs']                    = None
    self.puVar['historyView_tradeLogs_availableAssets']    = None
    self.puVar['historyView_tradeLogs_availablePositions'] = None
    self.puVar['clock_lastUpdated_ns']                     = 0

    #Setup Functions
    self.pageAuxillaryFunctions = __generateAuxillaryFunctions(self) #Generate auxillary functions
    self.pageLoadFunction       = __pageLoadFunction                 #Set page load function
    self.pageEscapeFunction     = __pageEscapeFunction               #Set page escape function
    self.pageProcessFunction    = __pageProcessFunction              #Set page process function
    self.pageObjectFunctions    = __generateObjectFunctions(self)    #Generate object functions

    #Setup a pyglet group for background
    self.groups['BACKGROUND'] = pyglet.graphics.Group(order = 0)

    #Generate guioInitialization base instances
    inst = {'windowInstance':      self.windowInstance,
            'displaySpaceDefiner': self.displaySpaceDefiner,
            'guioConfig':          self.guioConfig,
            'batch':               self.batch,
            'scaler':              self.displaySpaceDefiner['scaler'],
            'imageManager':        self.imageManager,
            'audioManager':        self.audioManager,
            'visualManager':       self.visualManager,
            'sysFunctions':        self.sysFunctions,
            'ipcA':                self.ipcA}

    #GUIO Initializations
    if (self.displaySpaceDefiner['ratio'] == '16:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 16000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
        self.GUIOs["TITLETEXT_ACCOUNTHISTORY"] = textBox_typeA(**inst, groupOrder=1, xPos= 5000, yPos=8550, width=6000, height=400, style=None, text=self.visualManager.getTextPack('ACCOUNTHISTORY:TITLE'), fontSize = 220, textInteractable = False)

        self.GUIOs["BUTTON_MOVETO_DASHBOARD"] = button_typeB(**inst, groupOrder=2, xPos=50, yPos=8650, width= 300, height=300, style="styleB", releaseFunction=self.pageObjectFunctions['PAGEMOVE_DASHBOARD'], image = 'dashboardIcon_512x512.png', imageSize = (225, 225), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))

        #[1]: Accounts
        #[1-1]: Accounts List
        if (True):
            self.GUIOs["BLOCKTITLE_ACCOUNTSLIST"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=8350, width=4900, height=200, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:BLOCKTITLE_ACCOUNTSLIST'), fontSize = 80)
            self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_VIRTUAL"] = switch_typeC(**inst,       groupOrder=1, xPos= 100, yPos=8000, width=2400, height= 250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTLIST_VIRTUAL'), fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_ACCOUNTLIST_FILTERSWITCH_VIRTUAL'])
            self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_ACTUAL"]  = switch_typeC(**inst,       groupOrder=1, xPos=2600, yPos=8000, width=2400, height= 250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTLIST_ACTUAL'),  fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_ACCOUNTLIST_FILTERSWITCH_ACTUAL'])
            self.GUIOs["ACCOUNTSLIST_SELECTIONBOX"]         = selectionBox_typeC(**inst, groupOrder=1, xPos= 100, yPos=2150, width=4900, height=5750, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_LIST_ACCOUNT'], elementWidths = (600, 1600, 800, 800, 850))
            self.GUIOs["ACCOUNTSLIST_SELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTLIST_INDEX')},
                                                                                     {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTLIST_LOCALID')},
                                                                                     {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTLIST_TYPE')},
                                                                                     {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTLIST_STATUS')},
                                                                                     {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTLIST_TRADESTATUS')}])
        #[1-2}: Accounts Information & Control
        if (True):
            self.GUIOs["BLOCKTITLE_ACCOUNTSINFORMATION"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=1850, width=4900, height=200, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:BLOCKTITLE_ACCOUNTSINFORMATION'), fontSize = 80)
            #---Local ID
            self.GUIOs["ACCOUNTSINFORMATION_LOCALIDTITLETEXT"]       = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=1500, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTSINFORMATION_LOCALID'),      fontSize=80, textInteractable=False)
            self.GUIOs["ACCOUNTSINFORMATION_LOCALIDDISPLAYTEXT"]     = textBox_typeA(**inst, groupOrder=1, xPos=1700, yPos=1500, width=3300, height=250, style="styleA", text="-",                                                                             fontSize=80, textInteractable=False)
            #---Binance UserID
            self.GUIOs["ACCOUNTSINFORMATION_BINANCEUIDTITLETEXT"]    = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=1150, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTSINFORMATION_BINANCEUID'),   fontSize=80, textInteractable=False)
            self.GUIOs["ACCOUNTSINFORMATION_BINANCEUIDDISPLAYTEXT"]  = textBox_typeA(**inst, groupOrder=1, xPos=1700, yPos=1150, width=3300, height=250, style="styleA", text="-",                                                                             fontSize=80, textInteractable=False)
            #---Account Type
            self.GUIOs["ACCOUNTSINFORMATION_ACCOUNTTYPETITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos= 800, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTSINFORMATION_ACCOUNTTYPE'),  fontSize=80, textInteractable=False)
            self.GUIOs["ACCOUNTSINFORMATION_ACCOUNTTYPEDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=1700, yPos= 800, width=3300, height=250, style="styleA", text="-",                                                                             fontSize=80, textInteractable=False)
            #---Status
            self.GUIOs["ACCOUNTSINFORMATION_STATUSTITLETEXT"]        = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos= 450, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTSINFORMATION_STATUS'),       fontSize=80, textInteractable=False)
            self.GUIOs["ACCOUNTSINFORMATION_STATUSDISPLAYTEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos=1700, yPos= 450, width=3300, height=250, style="styleA", text="-",                                                                             fontSize=80, textInteractable=False)
            #---Trade Status
            self.GUIOs["ACCOUNTSINFORMATION_TRADESTATUSTITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos= 100, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTSINFORMATION_TRADESTATUS'),  fontSize=80, textInteractable=False)
            self.GUIOs["ACCOUNTSINFORMATION_TRADESTATUSDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=1700, yPos= 100, width=3300, height=250, style="styleA", text="-",                                                                             fontSize=80, textInteractable=False) 
        
        #[2]: History
        if (True):
            self.GUIOs["BLOCKTITLE_HISTORY"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=5100, yPos=8350, width=10800, height=200, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:BLOCKTITLE_HISTORY'), fontSize = 80)
            self.GUIOs["HISTORY_VIEWTITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos=5100, yPos=8000, width=1300, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_VIEWTYPE'), fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_VIEWSELECTIONBOX"] = selectionBox_typeB(**inst, groupOrder=51, xPos=6500, yPos=8000, width=2300, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_HISTORY_VIEW'])
            _viewTypes = {'POSITIONCHART':   {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_VIEWTYPE_POSITIONCHART')},
                          'PERIODICREPORTS': {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_VIEWTYPE_PERIODICREPORTS')},
                          'TRADELOGS':       {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_VIEWTYPE_TRADELOGS')}}
            self.GUIOs["HISTORY_VIEWSELECTIONBOX"].setSelectionList(selectionList = _viewTypes, displayTargets = 'all')
            self.GUIOs["HISTORY_VIEWSELECTIONBOX"].setSelected(itemKey = 'POSITIONCHART', callSelectionUpdateFunction = False)
            self.GUIOs["HISTORY_ASSETTITLETEXT"]       = textBox_typeA(**inst,      groupOrder=1,  xPos= 8900, yPos=8000, width= 800, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_ASSET'), fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_ASSETSELECTIONBOX"]    = selectionBox_typeB(**inst, groupOrder=51, xPos= 9800, yPos=8000, width=1200, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_HISTORY_ASSET'])
            _assetSelections = {'#ALL#': {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_SELECTIONBOX_ALL')}}
            self.GUIOs["HISTORY_ASSETSELECTIONBOX"].setSelectionList(selectionList = _assetSelections, displayTargets = 'all')
            self.GUIOs["HISTORY_ASSETSELECTIONBOX"].setSelected(itemKey = '#ALL#', callSelectionUpdateFunction = False)
            self.GUIOs["HISTORY_ASSETSELECTIONBOX"].deactivate()
            self.GUIOs["HISTORY_ASSETIMAGEBOX"]        = imageBox_typeA(**inst,     groupOrder=1,  xPos=11100, yPos=8000, width= 250, height=250, style=None, image="assetTotalIcon_512x512.png")
            self.GUIOs["HISTORY_POSITIONTITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1,  xPos=11450, yPos=8000, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_POSITION'), fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_POSITIONSELECTIONBOX"] = selectionBox_typeB(**inst, groupOrder=51, xPos=12550, yPos=8000, width=2000, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_HISTORY_POSITION'])
            _positionSelections = {'#ALL#': {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_SELECTIONBOX_ALL'), 'textAnchor': 'W'}}
            self.GUIOs["HISTORY_POSITIONSELECTIONBOX"].setSelectionList(selectionList = _positionSelections, displayTargets = 'all')
            self.GUIOs["HISTORY_POSITIONSELECTIONBOX"].setSelected(itemKey = '#ALL#', callSelectionUpdateFunction = False)
            self.GUIOs["HISTORY_POSITIONSELECTIONBOX"].deactivate()
            self.GUIOs["HISTORY_LOADBUTTON"] = button_typeA(**inst, groupOrder=1, xPos=14650, yPos=8000, width=1250, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_LOAD'), fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_HISTORY_LOAD'])
            self.GUIOs["HISTORY_LOADBUTTON"].deactivate()
            self.puVar['GUIOGROUPS'] = dict()
        #[2-1]: Position Chart
        if (True):
            #---CA Viewer
            self.GUIOs["HISTORY_POSITIONCHART_CHARTDRAWER"] = chartDrawer_accountViewer(**inst, groupOrder=1, xPos=5100, yPos=100, width=10800, height=7800, style="styleA", name = 'ACCOUNTHISTORY_HISTORY_POSITIONCHART_CHARTDRAWER')
            #---%GUIOGROUPS%
            self.puVar['GUIOGROUPS']['POSITIONCHART'] = ["HISTORY_POSITIONCHART_CHARTDRAWER",]
            for _guioName in self.puVar['GUIOGROUPS']['POSITIONCHART']: self.GUIOs[_guioName].show()
        #[2-2]: Periodic Report
        if (True):
            #---Daily Report Viewer
            self.GUIOs["HISTORY_PERIODICREPORT_PERIODICREPORTVIEWER"] = periodicReportViewer(**inst, groupOrder=1, xPos=5100, yPos=100, width=10800, height=7800, style="styleA", name = 'ACCOUNTHISTORY_HISTORY_PERIODICREPORT_PERIODICREPORTVIEWER')
            #---%GUIOGROUPS%
            self.puVar['GUIOGROUPS']['PERIODICREPORTS'] = ["HISTORY_PERIODICREPORT_PERIODICREPORTVIEWER",]
            for _guioName in self.puVar['GUIOGROUPS']['PERIODICREPORTS']: self.GUIOs[_guioName].hide()
        #[2-3]: Trade Logs
        if (True):
            #---Filters & Summary
            self.GUIOs["HISTORY_TRADELOGS_NETPROFITTITLETEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos= 5100, yPos=7650, width=1100, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_NETPROFIT'),   fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_TRADELOGS_NETPROFITDISPLAYTEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos= 6300, yPos=7650, width=1425, height=250, style="styleA", text="-",                                                                            fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_GAINTITLETEXT"]               = textBox_typeA(**inst,      groupOrder=1, xPos= 7825, yPos=7650, width= 700, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_GAIN'),        fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_TRADELOGS_GAINDISPLAYTEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos= 8625, yPos=7650, width=1825, height=250, style="styleA", text="-",                                                                            fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_LOSSTITLETEXT"]               = textBox_typeA(**inst,      groupOrder=1, xPos=10550, yPos=7650, width= 700, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_LOSS'),        fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_TRADELOGS_LOSSDISPLAYTEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos=11350, yPos=7650, width=1825, height=250, style="styleA", text="-",                                                                            fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_TRADINGFEETITLETEXT"]         = textBox_typeA(**inst,      groupOrder=1, xPos=13275, yPos=7650, width=1100, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_TRADINGFEE'),  fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_TRADELOGS_TRADINGFEEDISPLAYTEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos=14475, yPos=7650, width=1425, height=250, style="styleA", text="-",                                                                            fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_NTOTALLOGSTITLETEXT"]         = textBox_typeA(**inst,      groupOrder=1, xPos= 5100, yPos=7300, width=1700, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_TOTAL'),       fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_TRADELOGS_NTOTALLOGSDISPLAYTEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos= 6900, yPos=7300, width=2000, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_NASSETLOGSTITLETEXT"]         = textBox_typeA(**inst,      groupOrder=1, xPos= 9000, yPos=7300, width=1300, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ASSET'),       fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_TRADELOGS_NASSETLOGSDISPLAYTEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos=10400, yPos=7300, width=2000, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_NPOSITIONLOGSTITLETEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos=12500, yPos=7300, width=1300, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_POSITION'),    fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_TRADELOGS_NPOSITIONLOGSDISPLAYTEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos=13900, yPos=7300, width=2000, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERTITLETEXT"]         = textBox_typeA(**inst,      groupOrder=1, xPos= 5100, yPos=6950, width=2080, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_TIMEUTC'),     fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERINPUTTEXT1"]        = textInputBox_typeA(**inst, groupOrder=1, xPos= 7280, yPos=6950, width=2080, height=250, style="styleA", text="",                                                                             fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_TRADELOGS_TIMEFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERINPUTTEXT2"]        = textInputBox_typeA(**inst, groupOrder=1, xPos= 9460, yPos=6950, width=2080, height=250, style="styleA", text="",                                                                             fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_TRADELOGS_TIMEFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERAPPLYBUTTON"]       = button_typeA(**inst,       groupOrder=1, xPos=11640, yPos=6950, width=2080, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_SEARCH'),      fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_TRADELOGS_TIMEFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERAPPLYBUTTON"].deactivate()
            self.GUIOs["HISTORY_TRADELOGS_NTIMELOGSDISPLAYTEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos=13820, yPos=6950, width=2080, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_SIDEFILTERBUY"]               = switch_typeC(**inst,       groupOrder=1, xPos= 5100, yPos=6600, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_BUY'),         switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NBUYDISPLAYTEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos= 6200, yPos=6600, width= 980, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_SIDEFILTERSELL"]              = switch_typeC(**inst,       groupOrder=1, xPos= 7280, yPos=6600, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_SELL'),        switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NSELLDISPLAYTEXT"]            = textBox_typeA(**inst,      groupOrder=1, xPos= 8380, yPos=6600, width= 980, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_SIDEFILTERLIQUIDATION"]       = switch_typeC(**inst,       groupOrder=1, xPos= 9460, yPos=6600, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_LIQUIDATION'), switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NLIQUIDATIONDISPLAYTEXT"]     = textBox_typeA(**inst,      groupOrder=1, xPos=10560, yPos=6600, width= 980, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTERFSLIMMED"]   = switch_typeC(**inst,       groupOrder=1, xPos=11640, yPos=6600, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_FSLIMMED'),    switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NFSLIMMEDDISPLAYTEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos=12740, yPos=6600, width= 980, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTERFSLCLOSE"]   = switch_typeC(**inst,       groupOrder=1, xPos=13820, yPos=6600, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_FSLCLOSE'),    switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NFSLCLOSEDISPLAYTEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos=14920, yPos=6600, width= 980, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTERENTRY"]      = switch_typeC(**inst,       groupOrder=1, xPos= 5100, yPos=6250, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ENTRY'),       switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NENTRYDISPLAYTEXT"]           = textBox_typeA(**inst,      groupOrder=1, xPos= 6200, yPos=6250, width= 980, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTERCLEAR"]      = switch_typeC(**inst,       groupOrder=1, xPos= 7280, yPos=6250, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_CLEAR'),       switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NCLEARDISPLAYTEXT"]           = textBox_typeA(**inst,      groupOrder=1, xPos= 8380, yPos=6250, width= 980, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTEREXIT"]       = switch_typeC(**inst,       groupOrder=1, xPos= 9460, yPos=6250, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_EXIT'),        switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NEXITDISPLAYTEXT"]            = textBox_typeA(**inst,      groupOrder=1, xPos=10560, yPos=6250, width= 980, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTERFORCECLEAR"] = switch_typeC(**inst,       groupOrder=1, xPos=11640, yPos=6250, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_FORCECLEAR'),  switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NFORCECLEARDISPLAYTEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos=12740, yPos=6250, width= 980, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTERUNKNOWN"]    = switch_typeC(**inst,       groupOrder=1, xPos=13820, yPos=6250, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_UNKNOWN'),     switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NUNKNOWNDISPLAYTEXT"]         = textBox_typeA(**inst,      groupOrder=1, xPos=14920, yPos=6250, width= 980, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            #---Selection Box
            self.GUIOs["HISTORY_TRADELOGS_TRADELOGSELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=2, xPos=5100, yPos=100, width=10800, height=6050, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_TRADELOGS_TRADELOG'], 
                                                                                      elementWidths = (900, 1000, 1200, 700, 700, 750, 800, 850, 850, 750, 800, 1250)) #10800
            self.GUIOs["HISTORY_TRADELOGS_TRADELOGSELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_INDEX')},          # 900
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_TIME')},           #1000
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_SYMBOL')},         #1200
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_LOGICSOURCE')},    # 700
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_SIDE')},           # 700
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_QUANTITY')},       # 750
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_PRICE')},          # 800
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_PROFIT')},         # 850
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_TRADINGFEE')},     # 850
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_TOTALQUANTITY')},  # 750
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_ENTRYPRICE')},     # 800
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_WALLETBALANCE')}]) #1250
            #---%GUIOGROUPS%
            self.puVar['GUIOGROUPS']['TRADELOGS'] = ["HISTORY_TRADELOGS_NETPROFITTITLETEXT",
                                                     "HISTORY_TRADELOGS_NETPROFITDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_GAINTITLETEXT",
                                                     "HISTORY_TRADELOGS_GAINDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_LOSSTITLETEXT",
                                                     "HISTORY_TRADELOGS_LOSSDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_TRADINGFEETITLETEXT",
                                                     "HISTORY_TRADELOGS_TRADINGFEEDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_NTOTALLOGSTITLETEXT",
                                                     "HISTORY_TRADELOGS_NTOTALLOGSDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_NASSETLOGSTITLETEXT",
                                                     "HISTORY_TRADELOGS_NASSETLOGSDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_NPOSITIONLOGSTITLETEXT",
                                                     "HISTORY_TRADELOGS_NPOSITIONLOGSDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_TIMEFILTERTITLETEXT",
                                                     "HISTORY_TRADELOGS_TIMEFILTERINPUTTEXT1",
                                                     "HISTORY_TRADELOGS_TIMEFILTERINPUTTEXT2",
                                                     "HISTORY_TRADELOGS_TIMEFILTERAPPLYBUTTON",
                                                     "HISTORY_TRADELOGS_NTIMELOGSDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_SIDEFILTERBUY",
                                                     "HISTORY_TRADELOGS_NBUYDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_SIDEFILTERSELL",
                                                     "HISTORY_TRADELOGS_NSELLDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_SIDEFILTERLIQUIDATION",
                                                     "HISTORY_TRADELOGS_NLIQUIDATIONDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_LOGICSOURCEFILTERFSLIMMED",
                                                     "HISTORY_TRADELOGS_NFSLIMMEDDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_LOGICSOURCEFILTERFSLCLOSE",
                                                     "HISTORY_TRADELOGS_NFSLCLOSEDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_LOGICSOURCEFILTERENTRY",
                                                     "HISTORY_TRADELOGS_NENTRYDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_LOGICSOURCEFILTERCLEAR",
                                                     "HISTORY_TRADELOGS_NCLEARDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_LOGICSOURCEFILTEREXIT",
                                                     "HISTORY_TRADELOGS_NEXITDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_LOGICSOURCEFILTERFORCECLEAR",
                                                     "HISTORY_TRADELOGS_NFORCECLEARDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_LOGICSOURCEFILTERUNKNOWN",
                                                     "HISTORY_TRADELOGS_NUNKNOWNDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_TRADELOGSELECTIONBOX"]
            for _guioName in self.puVar['GUIOGROUPS']['TRADELOGS']: self.GUIOs[_guioName].hide()

        #[3]: Clock
        self.GUIOs["CLOCK_LOCAL"] = textBox_typeA(**inst, groupOrder=1, xPos= 14000, yPos=8800, width=1950, height=150, style=None, text="", anchor = 'E', fontSize = 80, textInteractable = False)
        self.GUIOs["CLOCK_UTC"]   = textBox_typeA(**inst, groupOrder=1, xPos= 14000, yPos=8650, width=1950, height=150, style=None, text="", anchor = 'E', fontSize = 80, textInteractable = False)

    elif (self.displaySpaceDefiner['ratio'] == '21:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 21000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
    elif (self.displaySpaceDefiner['ratio'] == '32:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 32000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
#SETUP PAGE <MAIN> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <LOAD> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageLoadFunction(self):
    #[1]: Instances
    puVar = self.puVar
    guios = self.GUIOs
    pafs  = self.pageAuxillaryFunctions
    func_addFARHandler = self.ipcA.addFARHandler
    func_getPRD        = self.ipcA.getPRD

    #[2]: FAR Registration
    func_addFARHandler('onAccountUpdate',          pafs['_FAR_ONACCOUNTUPDATE'],          executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #TRADEMANAGER
    func_addFARHandler('onCurrencyAnalysisUpdate', pafs['_FAR_ONCURRENCYANALYSISUPDATE'], executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #TRADEMANAGER
    
    #[3]: Get data via PRD
    puVar['accounts']         = func_getPRD(processName = 'TRADEMANAGER', prdAddress = 'ACCOUNTS')
    puVar['currencyAnalysis'] = func_getPRD(processName = 'TRADEMANAGER', prdAddress = 'CURRENCYANALYSIS')

    #[4]: Display Data Update
    #---[4-1]: Accounts
    pafs['SETACCOUNTSLIST']() #Set Account List
    if puVar['accounts_selected'] not in puVar['accounts']:
        puVar['accounts_selected'] = None
        pafs['SETASSETSLIST']()
        pafs['SETPOSITIONSLIST']()
        pafs['SETTRADELOGSLIST']()

    #---[4-2]: Currency Analysis

#SETUP PAGE <LOAD> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <ESCAPE> --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageEscapeFunction(self):
    for fID in ('onAccountUpdate', 'onCurrencyAnalysisUpdate'):
        self.ipcA.removeFARHandler(functionID   = fID)
        self.ipcA.addDummyFARHandler(functionID = fID)
#SETUP PAGE <ESCAPE> END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <PROCESS> -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageProcessFunction(self, t_elapsed_ns, onLoad = False):
    #[1]: Instances
    puVar = self.puVar
    guios = self.GUIOs
    t_current_ns = time.perf_counter_ns()

    #[2]: Clock Update
    if _CLOCK_UPDATE_INTERVAL_NS <= t_current_ns-puVar['clock_lastUpdated_ns']:
        t_current_s = time.time()
        guios["CLOCK_LOCAL"].updateText(text = datetime.fromtimestamp(timestamp = t_current_s).strftime("[LOCAL] %Y/%m/%d %H:%M:%S.%f")[:-5])
        guios["CLOCK_UTC"].updateText(text   = datetime.fromtimestamp(timestamp = t_current_s, tz=timezone.utc).strftime("[UTC] %Y/%m/%d %H:%M:%S.%f")[:-5])
        puVar['clock_lastUpdated_ns'] = t_current_ns
#SETUP PAGE <PROCESS> END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#OBJECT FUNCTIONS -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateObjectFunctions(self):
    objFunctions = dict()

    #<Page Navigation>
    def __pageMove_DASHBOARD(objInstance, **kwargs): 
        self.sysFunctions['LOADPAGE']['function']('DASHBOARD')
    objFunctions['PAGEMOVE_DASHBOARD'] = __pageMove_DASHBOARD

    #<AccountsList>
    def __onStatusUpdate_AccountList_FilterSwitch_Virtual(objInstance, **kwargs):
        if (self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_ACTUAL"].getStatus() == True): self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_ACTUAL"].setStatus(status = False, callStatusUpdateFunction = False)
        self.pageAuxillaryFunctions['ONACCOUNTSLISTFILTERUPDATE']()
    def __onStatusUpdate_AccountList_FilterSwitch_Actual(objInstance, **kwargs):
        if (self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_VIRTUAL"].getStatus() == True): self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_VIRTUAL"].setStatus(status = False, callStatusUpdateFunction = False)
        self.pageAuxillaryFunctions['ONACCOUNTSLISTFILTERUPDATE']()
    def __onSelectionUpdate_List_Account(objInstance, **kwargs):
        try:    localID = objInstance.getSelected()[0]
        except: localID = None
        self.puVar['accounts_selected'] = localID
        self.pageAuxillaryFunctions['ONACCOUNTSELECTIONUPDATE']()
    objFunctions['ONSTATUSUPDATE_ACCOUNTLIST_FILTERSWITCH_VIRTUAL'] = __onStatusUpdate_AccountList_FilterSwitch_Virtual
    objFunctions['ONSTATUSUPDATE_ACCOUNTLIST_FILTERSWITCH_ACTUAL']  = __onStatusUpdate_AccountList_FilterSwitch_Actual
    objFunctions['ONSELECTIONUPDATE_LIST_ACCOUNT']                  = __onSelectionUpdate_List_Account

    #<History>
    def __onSelectionUpdate_History_View(objInstance, **kwargs): 
        _view_prev = self.puVar['historyView_selected']
        self.puVar['historyView_selected'] = self.GUIOs["HISTORY_VIEWSELECTIONBOX"].getSelected()
        self.pageAuxillaryFunctions['ONHISTORYVIEWUPDATE'](view_prev = _view_prev)
    def __onSelectionUpdate_History_Asset(objInstance, **kwargs): 
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        pafs  = self.pageAuxillaryFunctions
        assetName = guios["HISTORY_ASSETSELECTIONBOX"].getSelected()
        aImgBox   = guios["HISTORY_ASSETIMAGEBOX"]
        hv_sel    = puVar['historyView_selected']

        #[2]: Image Box Update
        if   assetName == '#ALL#': aImgBox.updateImage(image = "assetTotalIcon_512x512.png")
        elif assetName == 'USDT':  aImgBox.updateImage(image = "usdtIcon_512x512.png")
        elif assetName == 'USDC':  aImgBox.updateImage(image = "usdcIcon_512x512.png")

        #[3]: View-Dependent Responses
        if hv_sel == 'POSITIONCHART': 
            pafs['SETPOSITIONSLIST']()
            pafs['SETCHARTDRAWERTARGET']()
        if hv_sel == 'PERIODICREPORTS': 
            pafs['SETPERIODICREPORTSVIEWERTARGET']()
        elif hv_sel == 'TRADELOGS':
            pafs['SETPOSITIONSLIST']()
            pafs['ONTRADELOGSFILTERUPDATE']()
    def __onSelectionUpdate_History_Position(objInstance, **kwargs):
        #[1]: Instances
        puVar = self.puVar
        pafs  = self.pageAuxillaryFunctions
        hv_sel = puVar['historyView_selected']

        #[2]: View-Dependent Responses
        if hv_sel == 'POSITIONCHART':
            pafs['SETCHARTDRAWERTARGET']()
        if hv_sel == 'PERIODICREPORTS':
            pass
        elif hv_sel == 'TRADELOGS':
            pafs['ONTRADELOGSFILTERUPDATE']()
    def __onButtonRelease_History_Load(objInstance, **kwargs):
        self.GUIOs["HISTORY_LOADBUTTON"].deactivate()
        self.puVar['historyView_tradeLogsFetchRID'] = self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'fetchAccountTradeLog', functionParams = {'localID': self.puVar['accounts_selected']}, farrHandler = self.pageAuxillaryFunctions['_FARR_ONTRADELOGSREQUESTRESPONSE'])
    objFunctions['ONSELECTIONUPDATE_HISTORY_VIEW']     = __onSelectionUpdate_History_View
    objFunctions['ONSELECTIONUPDATE_HISTORY_ASSET']    = __onSelectionUpdate_History_Asset
    objFunctions['ONSELECTIONUPDATE_HISTORY_POSITION'] = __onSelectionUpdate_History_Position
    objFunctions['ONBUTTONRELEASE_HISTORY_LOAD']       = __onButtonRelease_History_Load

    #<Trade Logs>
    def __onTextUpdate_TradeLogs_TimeFilter(objInstance, **kwargs):
        rangeBeg_str = self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERINPUTTEXT1"].getText()
        rangeEnd_str = self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERINPUTTEXT2"].getText()
        if (rangeBeg_str == ""): rangeBeg = float('-inf')
        else:
            try:    rangeBeg = datetime.strptime(rangeBeg_str, "%Y/%m/%d %H:%M").timestamp()-time.timezone
            except: rangeBeg = None
        if (rangeEnd_str == ""): rangeEnd = float('inf')
        else:
            try:    rangeEnd = datetime.strptime(rangeEnd_str, "%Y/%m/%d %H:%M").timestamp()-time.timezone
            except: rangeEnd = None
        if ((rangeBeg is not None) and (rangeEnd is not None) and (rangeBeg <= rangeEnd)): self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERAPPLYBUTTON"].activate()
        else:                                                                              self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERAPPLYBUTTON"].deactivate()
    def __onButtonRelease_TradeLogs_TimeFilter(objInstance, **kwargs):
        self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERAPPLYBUTTON"].deactivate()
        self.pageAuxillaryFunctions['ONTRADELOGSFILTERUPDATE']()
    def __onStatusUpdate_TradeLogs_SwitchFilter(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONTRADELOGSFILTERUPDATE']()
    def __onSelectionUpdate_TradeLogs_TradeLog(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONTRADELOGSELECTIONUPDATE']()
    objFunctions['ONTEXTUPDATE_TRADELOGS_TIMEFILTER']     = __onTextUpdate_TradeLogs_TimeFilter
    objFunctions['ONBUTTONRELEASE_TRADELOGS_TIMEFILTER']  = __onButtonRelease_TradeLogs_TimeFilter
    objFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'] = __onStatusUpdate_TradeLogs_SwitchFilter
    objFunctions['ONSELECTIONUPDATE_TRADELOGS_TRADELOG']  = __onSelectionUpdate_TradeLogs_TradeLog

    #Return the generated functions
    return objFunctions
#OBJECT FUNCTIONS END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUXILALRY FUNCTIONS --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateAuxillaryFunctions(self):
    auxFunctions = dict()
    
    #<_PAGELOAD>
    def __far_onAccountUpdate(requester, updateType, updatedContent):
        if (requester == 'TRADEMANAGER'):
            if (updateType == 'ADDED'):
                localID = updatedContent
                self.puVar['accounts'][localID] = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ACCOUNTS', localID))
                self.pageAuxillaryFunctions['SETACCOUNTSLIST']()
            elif (updateType == 'REMOVED'):
                localID = updatedContent
                self.pageAuxillaryFunctions['SETACCOUNTSLIST']()
                if (localID == self.puVar['accounts_selected']):
                    #[1]: Account Information & Control
                    self.puVar['accounts_selected'] = None
                    self.pageAuxillaryFunctions['ONACCOUNTSELECTIONUPDATE']()
            elif (updateType == 'UPDATED_STATUS'):
                localID = updatedContent
                newStatus = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ACCOUNTS', localID, 'status'))
                self.puVar['accounts'][localID]['status'] = newStatus
                #SelectionBox Update
                if   (newStatus == 'INACTIVE'): _text = 'INACTIVE'; _textColor = 'RED_LIGHT'
                elif (newStatus == 'ACTIVE'):   _text = 'ACTIVE';   _textColor = 'GREEN_LIGHT'
                _newSelectionBoxItem = {'text': _text, 'textStyles': [('all', _textColor),], 'textAnchor': 'CENTER'}
                self.GUIOs["ACCOUNTSLIST_SELECTIONBOX"].editSelectionListItem(itemKey = localID, item = _newSelectionBoxItem, columnIndex = 3)
                #Account Information Update
                if (localID == self.puVar['accounts_selected']):
                    if   (newStatus == 'ACTIVE'):   self.GUIOs["ACCOUNTSINFORMATION_STATUSDISPLAYTEXT"].updateText(text = newStatus, textStyle = 'GREEN_LIGHT')
                    elif (newStatus == 'INACTIVE'): self.GUIOs["ACCOUNTSINFORMATION_STATUSDISPLAYTEXT"].updateText(text = newStatus, textStyle = 'RED_LIGHT')
            elif (updateType == 'UPDATED_TRADESTATUS'):
                localID = updatedContent
                newTradeStatus = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ACCOUNTS', localID, 'tradeStatus'))
                self.puVar['accounts'][localID]['tradeStatus'] = newTradeStatus
                #SelectionBox Update
                if (newTradeStatus == False): _text = 'FALSE'; _textColor = 'RED_LIGHT'
                else:                         _text = 'TRUE';  _textColor = 'GREEN_LIGHT'
                _newSelectionBoxItem = {'text': _text, 'textStyles': [('all', _textColor),], 'textAnchor': 'CENTER'}
                self.GUIOs["ACCOUNTSLIST_SELECTIONBOX"].editSelectionListItem(itemKey = localID, item = _newSelectionBoxItem, columnIndex = 4)
                #Account Information Update
                if (localID == self.puVar['accounts_selected']):
                    if   (newTradeStatus == True):  self.GUIOs["ACCOUNTSINFORMATION_TRADESTATUSDISPLAYTEXT"].updateText(text = 'TRUE',  textStyle = 'GREEN_LIGHT')
                    elif (newTradeStatus == False): self.GUIOs["ACCOUNTSINFORMATION_TRADESTATUSDISPLAYTEXT"].updateText(text = 'FALSE', textStyle = 'RED_LIGHT')
    auxFunctions['_FAR_ONACCOUNTUPDATE'] = __far_onAccountUpdate

    def __far_onCurrencyAnalysisUpdate(requester, updateType, currencyAnalysisCode):
        #[1]: Source Check
        if requester != 'TRADEMANAGER':
            return
        
        #[2]: Instances
        puVar  = self.puVar
        guios  = self.GUIOs
        pafs   = self.pageAuxillaryFunctions
        caCode = currencyAnalysisCode
        func_getPRD = self.ipcA.getPRD

        #[3]: Update Response
        #---[3-1]: Status Updated
        if updateType == 'UPDATE_STATUS':
            status = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', caCode, 'status'))
            puVar['currencyAnalysis'][caCode]['status'] = status

        #---[3-2]: Analyzer Updated
        elif updateType == 'UPDATE_ANALYZER':
            allocatedAnalyzer = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', caCode, 'allocatedAnalyzer'))
            puVar['currencyAnalysis'][caCode]['allocatedAnalyzer'] = allocatedAnalyzer

        #---[3-3]: Added
        elif updateType == 'ADDED':
            puVar['currencyAnalysis'][caCode] = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', caCode))

        #---[3-4]: Removed
        elif updateType == 'REMOVED':
            del puVar['currencyAnalysis'][caCode]

        #Send the update to the chart drawer if this is for the selected currency analysis
        if caCode == puVar['currencyAnalysis_selected']: 
            guios["CHART_CHARTDRAWER"].onCurrencyAnalysisUpdate(updateType = updateType, currencyAnalysisCode = caCode)
    auxFunctions['_FAR_ONCURRENCYANALYSISUPDATE'] = __far_onCurrencyAnalysisUpdate





    #<Accounts List>
    def __setAccountsList():
        accounts_selectionList = dict()
        for accountIndex, localID in enumerate(self.puVar['accounts']):
            _account = self.puVar['accounts'][localID]
            #Display Table Formatting
            _status = _account['status']
            if   (_status == 'INACTIVE'): _text_status = 'INACTIVE'; _textColor_status = 'RED_LIGHT'
            elif (_status == 'ACTIVE'):   _text_status = 'ACTIVE';   _textColor_status = 'GREEN_LIGHT'
            _tradeStatus = _account['tradeStatus']
            if (_tradeStatus == False): _text_tradeStatus = 'FALSE'; _textColor_tradeStatus = 'RED_LIGHT'
            else:                       _text_tradeStatus = 'TRUE';  _textColor_tradeStatus = 'GREEN_LIGHT'
            accounts_selectionList[localID] = [{'text': str(accountIndex),       'textStyles': [('all', 'DEFAULT'),],              'textAnchor': 'CENTER'},
                                               {'text': localID,                 'textStyles': [('all', 'DEFAULT'),],              'textAnchor': 'CENTER'},
                                               {'text': _account['accountType'], 'textStyles': [('all', 'DEFAULT'),],              'textAnchor': 'CENTER'},
                                               {'text': _text_status,            'textStyles': [('all', _textColor_status),],      'textAnchor': 'CENTER'},
                                               {'text': _text_tradeStatus,       'textStyles': [('all', _textColor_tradeStatus),], 'textAnchor': 'CENTER'}]
        self.GUIOs["ACCOUNTSLIST_SELECTIONBOX"].setSelectionList(selectionList = accounts_selectionList, keepSelected = True, displayTargets = 'all', callSelectionUpdateFunction = False)
        #self.pageAuxillaryFunctions['ONACCOUNTSLISTFILTERUPDATE']()
    def __onAccountsListFilterUpdate():
        if   (self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_VIRTUAL"].getStatus() == True): localIDs_filtered = [localID for localID in self.puVar['accounts'] if (self.puVar['accounts'][localID]['accountType'] == 'VIRTUAL')]
        elif (self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_ACTUAL"].getStatus()  == True): localIDs_filtered = [localID for localID in self.puVar['accounts'] if (self.puVar['accounts'][localID]['accountType'] == 'ACTUAL')]
        else:                                                                       localIDs_filtered = 'all'
        self.GUIOs["ACCOUNTSLIST_SELECTIONBOX"].setDisplayTargets(displayTargets = localIDs_filtered)
    auxFunctions['SETACCOUNTSLIST']            = __setAccountsList
    auxFunctions['ONACCOUNTSLISTFILTERUPDATE'] = __onAccountsListFilterUpdate

    #<Accounts Information & Control>
    def __farr_onTradeLogsRequestResponse(responder, requestID, functionResult):
        if (responder == 'DATAMANAGER'):
            _result      = functionResult['result']
            _localID     = functionResult['localID']
            _tradeLogs   = functionResult['tradeLogs']
            _failureType = functionResult['failureType']
            if ((_localID == self.puVar['accounts_selected']) and (requestID == self.puVar['historyView_tradeLogsFetchRID'])):
                if (_result == True):
                    #Save trade logs
                    self.puVar['historyView_tradeLogs'] = _tradeLogs
                    #Find available assets and positions
                    _assets_avail    = set()
                    _positions_avail = {'#ALL#': set()}
                    _account_positions = self.puVar['accounts'][self.puVar['accounts_selected']]['positions']
                    #---Asssets
                    for _tLog in _tradeLogs: _assets_avail.add(_account_positions[_tLog['positionSymbol']]['quoteAsset'])
                    #---Positions
                    for _assetName in _assets_avail: _positions_avail[_assetName] = set()
                    for _tLog in _tradeLogs: 
                        _pSymbol = _tLog['positionSymbol']
                        _positions_avail['#ALL#'].add(_pSymbol)
                        _positions_avail[_account_positions[_pSymbol]['quoteAsset']].add(_pSymbol)
                    #---Finally
                    self.puVar['historyView_tradeLogs_availableAssets']    = _assets_avail
                    self.puVar['historyView_tradeLogs_availablePositions'] = _positions_avail
                    #If this is the current view
                    if (self.puVar['historyView_selected'] == 'TRADELOGS'):
                        self.pageAuxillaryFunctions['SETASSETSLIST']()
                        self.pageAuxillaryFunctions['SETPOSITIONSLIST']()
                        self.pageAuxillaryFunctions['SETTRADELOGSLIST']()
                else: print(termcolor.colored("[GUI-PAGE:ACCOUNTHISTORY] A failure returned from DATAMANAGER while attempting to fetch tradeLogs for account '{:s}'.\n *".format(_localID), 'light_red'), termcolor.colored(_failureType, 'light_red'))
                self.puVar['historyView_tradeLogsFetchRID'] = None
    def __onAccountSelectionUpdate():
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        pafs  = self.pageAuxillaryFunctions

        #[2]: Account Information Display Update
        localID = puVar['accounts_selected']
        account = puVar['accounts'].get(localID, None)
        if account is None: 
            #Account Information
            guios["ACCOUNTSINFORMATION_LOCALIDDISPLAYTEXT"].updateText(text     = "-") #Local ID
            guios["ACCOUNTSINFORMATION_BINANCEUIDDISPLAYTEXT"].updateText(text  = "-") #BUID
            guios["ACCOUNTSINFORMATION_ACCOUNTTYPEDISPLAYTEXT"].updateText(text = "-") #Account Type
            guios["ACCOUNTSINFORMATION_STATUSDISPLAYTEXT"].updateText(text      = "-") #Status
            guios["ACCOUNTSINFORMATION_TRADESTATUSDISPLAYTEXT"].updateText(text = "-") #Trade Status
            #Trade Logs
            puVar['historyView_tradeLogsFetchRID'] = None
            puVar['historyView_tradeLogs']         = None
            puVar['historyView_tradeLogs_availableAssets']    = None
            puVar['historyView_tradeLogs_availablePositions'] = None
            #Load Button
            guios["HISTORY_LOADBUTTON"].deactivate()
        else:
            #Account Information
            #---Local ID
            guios["ACCOUNTSINFORMATION_LOCALIDDISPLAYTEXT"].updateText(text = localID)
            #---BUID
            buid = account['buid']
            if buid is None: guios["ACCOUNTSINFORMATION_BINANCEUIDDISPLAYTEXT"].updateText(text = "-")
            else:            guios["ACCOUNTSINFORMATION_BINANCEUIDDISPLAYTEXT"].updateText(text = f"{buid}")
            #---Account Type
            guios["ACCOUNTSINFORMATION_ACCOUNTTYPEDISPLAYTEXT"].updateText(text = account['accountType'])
            #---Status
            status = account['status']
            if   status == 'INACTIVE': guios["ACCOUNTSINFORMATION_STATUSDISPLAYTEXT"].updateText(text = status, textStyle = 'RED_LIGHT')
            elif status == 'ACTIVE':   guios["ACCOUNTSINFORMATION_STATUSDISPLAYTEXT"].updateText(text = status, textStyle = 'GREEN_LIGHT')
            #---Trade Status
            tradeStatus = account['tradeStatus']
            if tradeStatus: guios["ACCOUNTSINFORMATION_TRADESTATUSDISPLAYTEXT"].updateText(text = "TRUE",  textStyle = 'GREEN_LIGHT')
            else:           guios["ACCOUNTSINFORMATION_TRADESTATUSDISPLAYTEXT"].updateText(text = "FALSE", textStyle = 'RED_LIGHT')
            #Trade Logs
            puVar['historyView_tradeLogsFetchRID'] = self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'fetchAccountTradeLog', functionParams = {'localID': localID}, farrHandler = __farr_onTradeLogsRequestResponse)
            puVar['historyView_tradeLogs']         = None
            puVar['historyView_tradeLogs_availableAssets']    = None
            puVar['historyView_tradeLogs_availablePositions'] = None
            #Load Button
            guios["HISTORY_LOADBUTTON"].activate()

        #[3]: Assets & Positions List Update
        pafs['SETASSETSLIST']()
        pafs['SETPOSITIONSLIST']()

        #[4]: View-Dependent Response
        hv_sel = puVar['historyView_selected']
        if   hv_sel == 'POSITIONCHART':   pafs['SETCHARTDRAWERTARGET']()
        elif hv_sel == 'PERIODICREPORTS': pafs['SETPERIODICREPORTSVIEWERTARGET']()
        elif hv_sel == 'TRADELOGS':       pafs['SETTRADELOGSLIST']()
    auxFunctions['_FARR_ONTRADELOGSREQUESTRESPONSE'] = __farr_onTradeLogsRequestResponse
    auxFunctions['ONACCOUNTSELECTIONUPDATE']         = __onAccountSelectionUpdate

    #<History>
    def __onHistoryViewUpdate(view_prev = None):
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        pafs  = self.pageAuxillaryFunctions

        #[2]: GUIOs Hide & Show
        view_sel = puVar['historyView_selected']
        if view_prev is not None:
            for gName in puVar['GUIOGROUPS'][view_prev]: guios[gName].hide()
            for gName in puVar['GUIOGROUPS'][view_sel]:  guios[gName].show()

        #[3]: Assets & Positions List Update
        pafs['SETASSETSLIST']()
        pafs['SETPOSITIONSLIST']()

        #[4]: View-Dependent Response
        if   view_sel == 'POSITIONCHART':   pafs['SETCHARTDRAWERTARGET']()
        elif view_sel == 'PERIODICREPORTS': pafs['SETPERIODICREPORTSVIEWERTARGET']()
        elif view_sel == 'TRADELOGS':       pafs['SETTRADELOGSLIST']()
    def __setAssetsList():
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        vm_gtp = self.visualManager.getTextPack

        #[2]: No Account Selected
        localID = puVar['accounts_selected']
        account = puVar['accounts'].get(localID, None)
        if account is None:
            guios["HISTORY_ASSETSELECTIONBOX"].setSelectionList(selectionList = dict(), keepSelected = False, displayTargets = 'all')
            guios["HISTORY_ASSETSELECTIONBOX"].deactivate()

        #[3]: Account Selected
        else:
            #[3-1]: Instances
            hv_sel = puVar['historyView_selected']
            aSelBox = guios["HISTORY_ASSETSELECTIONBOX"]
            aImgBox = guios["HISTORY_ASSETIMAGEBOX"]

            #[3-2]: Position Chart
            if hv_sel == 'POSITIONCHART':
                assetSels = {'#ALL#': {'text': vm_gtp('ACCOUNTHISTORY:HISTORY_SELECTIONBOX_ALL')}}
                for assetName in set(position['quoteAsset'] for position in account['positions'].values() if position['currencyAnalysisCode'] in puVar['currencyAnalysis']):
                    assetSels[assetName] = {'text': assetName} 
                aSelBox.setSelectionList(selectionList = assetSels, keepSelected = True, displayTargets = 'all')
                aSelBox.setSelected(itemKey = '#ALL#', callSelectionUpdateFunction = False)
                aImgBox.updateImage(image = "assetTotalIcon_512x512.png")

            #[3-3]: Periodic Reports
            if hv_sel == 'PERIODICREPORTS':
                assetSels = {assetName: {'text': assetName} for assetName in ('USDT', 'USDC')}
                aSelBox.setSelectionList(selectionList = assetSels, keepSelected = True, displayTargets = 'all')
                aSelBox.setSelected(itemKey = 'USDT',  callSelectionUpdateFunction = False)
                aImgBox.updateImage(image = "usdtIcon_512x512.png")

            #[3-4]: Trade Logs
            elif hv_sel == 'TRADELOGS':
                tls_aas = puVar['historyView_tradeLogs_availableAssets']
                assetSels = {'#ALL#': {'text': vm_gtp('ACCOUNTHISTORY:HISTORY_SELECTIONBOX_ALL')}}
                if tls_aas is not None:
                    for assetName in tls_aas: 
                        assetSels[assetName] = {'text': assetName}
                aSelBox.setSelectionList(selectionList = assetSels, keepSelected = True, displayTargets = 'all')
                aSelBox.setSelected(itemKey = '#ALL#', callSelectionUpdateFunction = False)
                aImgBox.updateImage(image = "assetTotalIcon_512x512.png")

            #[3-5]: Asset Selection Box Activation
            aSelBox.activate()

    def __setPositionsList():
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        vm_gtp = self.visualManager.getTextPack

        #[2]: No Account Selected
        localID = puVar['accounts_selected']
        account = puVar['accounts'].get(localID, None)
        if account is None:
            guios["HISTORY_POSITIONSELECTIONBOX"].setSelectionList(selectionList = dict(), keepSelected = False, displayTargets = 'all')
            guios["HISTORY_POSITIONSELECTIONBOX"].deactivate()

        #[3]: Account Selected
        else:
            #[3-1]: Instances
            hv_sel    = puVar['historyView_selected']
            pSelBox   = guios["HISTORY_POSITIONSELECTIONBOX"]
            assetName = guios["HISTORY_ASSETSELECTIONBOX"].getSelected()

            #[3-2]: Periodic Reports
            if hv_sel == 'POSITIONCHART': 
                symbols = [symbol for symbol, position in account['positions'].items() 
                           if position['currencyAnalysisCode'] in puVar['currencyAnalysis'] and (assetName == '#ALL#' or assetName == position['quoteAsset'])]
                positionSels = {symbol: {'text': symbol, 'textAnchor': 'W'} for symbol in symbols}
                pSelBox.setSelectionList(selectionList = positionSels, keepSelected = True, displayTargets = 'all')
                symbol = symbols[0] if symbols else None
                pSelBox.setSelected(itemKey = symbol, callSelectionUpdateFunction = False)
                puVar['currencyAnalysis_selected'] = symbol
                pSelBox.activate()

            #[3-3]: Periodic Reports
            elif hv_sel == 'PERIODICREPORTS': 
                pSelBox.setSelectionList(selectionList = dict(), keepSelected = False, displayTargets = 'all')
                pSelBox.deactivate()

            #[3-4]: Trade Logs
            elif hv_sel == 'TRADELOGS':
                tls_aas = puVar['historyView_tradeLogs_availableAssets']
                tls_aps = puVar['historyView_tradeLogs_availablePositions']
                positionSels = {'#ALL#': {'text': vm_gtp('ACCOUNTHISTORY:HISTORY_SELECTIONBOX_ALL'), 'textAnchor': 'W'}}
                if tls_aas is not None:
                    for symbol in tls_aps[assetName]: 
                        positionSels[symbol] = {'text': symbol, 'textAnchor': 'W'}
                pSelBox.setSelectionList(selectionList = positionSels, keepSelected = True, displayTargets = 'all')
                pSelBox.setSelected(itemKey = '#ALL#', callSelectionUpdateFunction = False)
                pSelBox.activate()

    auxFunctions['ONHISTORYVIEWUPDATE'] = __onHistoryViewUpdate
    auxFunctions['SETASSETSLIST']       = __setAssetsList
    auxFunctions['SETPOSITIONSLIST']    = __setPositionsList

    #<Chart Drawer>
    def __setChartDrawerTarget():

        sels       = objInstance.getSelected()
        caCode_sel = sels[0] if sels else None
        self.puVar['currencyAnalysis_selected'] = caCode_sel


        self.GUIOs["CHART_CHARTDRAWER"].setTarget(target = caCode_sel)
    auxFunctions['SETCHARTDRAWERTARGET'] = __setChartDrawerTarget

    #<Balances>
    def __setPeriodicReportsViewerTarget():
        localID_selected   = self.puVar['accounts_selected']
        assetName_selected = self.GUIOs["HISTORY_ASSETSELECTIONBOX"].getSelected()
        if (localID_selected is not None) and (assetName_selected is not None): self.GUIOs["HISTORY_PERIODICREPORT_PERIODICREPORTVIEWER"].setTarget(target = (localID_selected, assetName_selected, 'ACCOUNT'))
        else:                                                                   self.GUIOs["HISTORY_PERIODICREPORT_PERIODICREPORTVIEWER"].setTarget(target = None)
    auxFunctions['SETPERIODICREPORTSVIEWERTARGET'] = __setPeriodicReportsViewerTarget

    #<Trade Logs>
    def __setTradeLogsList():
        if (self.puVar['historyView_tradeLogs'] != None):
            _positions  = self.puVar['accounts'][self.puVar['accounts_selected']]['positions']
            _nTradeLogs = len(self.puVar['historyView_tradeLogs'])
            tradeLogs_selectionList = dict()
            for _tradeLog in self.puVar['historyView_tradeLogs']:
                _positionSymbol = _tradeLog['positionSymbol']
                _position = _positions[_positionSymbol]
                _position_precisions = _position['precisions']
                _position_quoteAsset = _position['quoteAsset']
                #[0]: Index
                _index_str = f"{_tradeLog['logIndex']+1:,d} / {_nTradeLogs:,d}"
                #[1]: Time
                _time_str = datetime.fromtimestamp(_tradeLog['timestamp'], tz=timezone.utc).strftime("%Y/%m/%d %H:%M")
                #[2]: Symbol
                _symbol_str = _positionSymbol
                #[3]: Logic Source
                _logicSource_str = _tradeLog['logicSource']
                #[4]: Side
                _side_str = _tradeLog['side']
                if   (_tradeLog['side'] == 'BUY'):         _side_str_color = 'GREEN_LIGHT'
                elif (_tradeLog['side'] == 'SELL'):        _side_str_color = 'RED_LIGHT'
                elif (_tradeLog['side'] == 'LIQUIDATION'): _side_str_color = 'VIOLET_LIGHT'
                #[5]: Quantity
                _quantity_str = auxiliaries.floatToString(number = _tradeLog['quantity'], precision = _position_precisions['quantity'])
                #[6]: Price
                if (_tradeLog['price'] is None): _price_str = "N/A"
                else:                            _price_str = auxiliaries.floatToString(number = _tradeLog['price'], precision = _position_precisions['price'])
                #[7]: Profit
                if   (_tradeLog['profit'] is None): _profit_str = "N/A";                                                                                                                     _profit_str_color = 'DEFAULT'
                elif (0 < _tradeLog['profit']):     _profit_str = "+"+auxiliaries.floatToString(number = _tradeLog['profit'], precision = _ASSETPRECISIONS_XS[_position_quoteAsset]); _profit_str_color = 'GREEN_LIGHT'
                elif (_tradeLog['profit'] == 0):    _profit_str =     auxiliaries.floatToString(number = _tradeLog['profit'], precision = _ASSETPRECISIONS_XS[_position_quoteAsset]); _profit_str_color = 'DEFAULT'
                elif (_tradeLog['profit'] < 0):     _profit_str =     auxiliaries.floatToString(number = _tradeLog['profit'], precision = _ASSETPRECISIONS_XS[_position_quoteAsset]); _profit_str_color = 'RED_LIGHT'
                #[8]: Trading Fee
                if (_tradeLog['tradingFee'] is None): _tradingFee_str = "N/A"
                else:                                 _tradingFee_str = auxiliaries.floatToString(number = _tradeLog['tradingFee'], precision = _ASSETPRECISIONS_XS[_position_quoteAsset])
                #[9]: Total Quantity
                _totalQuantity_str = auxiliaries.floatToString(number = _tradeLog['totalQuantity'], precision = _position_precisions['quantity'])
                #[10]: Entry Price
                if (_tradeLog['entryPrice'] is None): _entryPrice_str = "-"
                else:                                 _entryPrice_str = auxiliaries.floatToString(number = _tradeLog['entryPrice'], precision = _position_precisions['price'])
                #[11]: Wallet Balance
                if (_tradeLog['walletBalance'] is None): _walletBalance_str = "N/A"
                else:                                    _walletBalance_str = auxiliaries.floatToString(number = _tradeLog['walletBalance'], precision = _ASSETPRECISIONS_XS[_position_quoteAsset])
                #Finally
                tradeLogs_selectionList[_tradeLog['logIndex']] = [{'text': _index_str},
                                                                  {'text': _time_str},
                                                                  {'text': _symbol_str},
                                                                  {'text': _logicSource_str},
                                                                  {'text': _side_str, 'textStyles': [('all', _side_str_color)]},
                                                                  {'text': _quantity_str},
                                                                  {'text': _price_str},
                                                                  {'text': _profit_str, 'textStyles': [('all', _profit_str_color)]},
                                                                  {'text': _tradingFee_str},
                                                                  {'text': _totalQuantity_str},
                                                                  {'text': _entryPrice_str},
                                                                  {'text': _walletBalance_str}]
            self.GUIOs["HISTORY_TRADELOGS_TRADELOGSELECTIONBOX"].setSelectionList(selectionList = tradeLogs_selectionList, keepSelected = False, displayTargets = 'all', callSelectionUpdateFunction = False)
        else: self.GUIOs["HISTORY_TRADELOGS_TRADELOGSELECTIONBOX"].clearSelectionList()
        self.pageAuxillaryFunctions['ONTRADELOGSFILTERUPDATE']()
    def __onTradeLogsFilterUpdate():
        account_selected = self.puVar['accounts_selected']

        #[1]: No Account Selected
        if (account_selected is None):
            #[1-1]: Net Proft, Gain, Loss, Trading Fee Display Update
            self.GUIOs["HISTORY_TRADELOGS_NETPROFITDISPLAYTEXT"].updateText(text  = "-", textStyle = 'DEFAULT')
            self.GUIOs["HISTORY_TRADELOGS_GAINDISPLAYTEXT"].updateText(text       = "-")
            self.GUIOs["HISTORY_TRADELOGS_LOSSDISPLAYTEXT"].updateText(text       = "-")
            self.GUIOs["HISTORY_TRADELOGS_TRADINGFEEDISPLAYTEXT"].updateText(text = "-")
            #[1-2]: Logs Counter Display Update
            self.GUIOs["HISTORY_TRADELOGS_NTOTALLOGSDISPLAYTEXT"].updateText(text    = "- / -")
            self.GUIOs["HISTORY_TRADELOGS_NASSETLOGSDISPLAYTEXT"].updateText(text    = "- / -")
            self.GUIOs["HISTORY_TRADELOGS_NPOSITIONLOGSDISPLAYTEXT"].updateText(text = "- / -")
            self.GUIOs["HISTORY_TRADELOGS_NTIMELOGSDISPLAYTEXT"].updateText(text     = "- / -")
            self.GUIOs["HISTORY_TRADELOGS_NBUYDISPLAYTEXT"].updateText(text          = "- / -")
            self.GUIOs["HISTORY_TRADELOGS_NSELLDISPLAYTEXT"].updateText(text         = "- / -")
            self.GUIOs["HISTORY_TRADELOGS_NLIQUIDATIONDISPLAYTEXT"].updateText(text  = "- / -")
            self.GUIOs["HISTORY_TRADELOGS_NFSLIMMEDDISPLAYTEXT"].updateText(text     = "- / -")
            self.GUIOs["HISTORY_TRADELOGS_NFSLCLOSEDISPLAYTEXT"].updateText(text     = "- / -")
            self.GUIOs["HISTORY_TRADELOGS_NENTRYDISPLAYTEXT"].updateText(text        = "- / -")
            self.GUIOs["HISTORY_TRADELOGS_NCLEARDISPLAYTEXT"].updateText(text        = "- / -")
            self.GUIOs["HISTORY_TRADELOGS_NEXITDISPLAYTEXT"].updateText(text         = "- / -")
            self.GUIOs["HISTORY_TRADELOGS_NFORCECLEARDISPLAYTEXT"].updateText(text   = "- / -")
            self.GUIOs["HISTORY_TRADELOGS_NUNKNOWNDISPLAYTEXT"].updateText(text      = "- / -")
            #[1-3]: Finally
            return
        
        #[2]: Account Data
        account_positions         = self.puVar['accounts'][account_selected]['positions']
        asset_selected            = self.GUIOs["HISTORY_ASSETSELECTIONBOX"].getSelected()
        position_selected         = self.GUIOs["HISTORY_POSITIONSELECTIONBOX"].getSelected()
        tradeLogs                 = self.puVar['historyView_tradeLogs'] if (self.puVar['historyView_tradeLogs'] is not None) else list()
        tradeLogs_filteredIndexes = set()

        #[3]: Filter Params
        if (True):
            _filter_time_beg_str = self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERINPUTTEXT1"].getText()
            _filter_time_end_str = self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERINPUTTEXT2"].getText()
            if (_filter_time_beg_str == ""): rangeBeg = float('-inf')
            else:
                try:    rangeBeg = datetime.strptime(_filter_time_beg_str, "%Y/%m/%d %H:%M").timestamp()-time.timezone
                except: rangeBeg = None
            if (_filter_time_end_str == ""): rangeEnd = float('inf')
            else:
                try:    rangeEnd = datetime.strptime(_filter_time_end_str, "%Y/%m/%d %H:%M").timestamp()-time.timezone
                except: rangeEnd = None
            if ((rangeBeg is not None) and (rangeEnd is not None) and (rangeBeg <= rangeEnd)): _filter_time = (rangeBeg, rangeEnd)
            else:                                                                              _filter_time = None
            _filter_side_buy         = self.GUIOs["HISTORY_TRADELOGS_SIDEFILTERBUY"].getStatus()
            _filter_side_sell        = self.GUIOs["HISTORY_TRADELOGS_SIDEFILTERSELL"].getStatus()
            _filter_side_liquidation = self.GUIOs["HISTORY_TRADELOGS_SIDEFILTERLIQUIDATION"].getStatus()
            _filter_logicSource_fslImmed   = self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTERFSLIMMED"].getStatus()
            _filter_logicSource_fslClose   = self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTERFSLCLOSE"].getStatus()
            _filter_logicSource_entry      = self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTERENTRY"].getStatus()
            _filter_logicSource_clear      = self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTERCLEAR"].getStatus()
            _filter_logicSource_exit       = self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTEREXIT"].getStatus()
            _filter_logicSource_forceClear = self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTERFORCECLEAR"].getStatus()
            _filter_logicSource_unknown    = self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTERUNKNOWN"].getStatus()
            _filter = {'asset':        asset_selected,
                       'symbol':       position_selected,
                       'time':         _filter_time,
                       'side':         set(),
                       'logicSource':  set()}
            if (_filter_side_buy         == True): _filter['side'].add('BUY')
            if (_filter_side_sell        == True): _filter['side'].add('SELL')
            if (_filter_side_liquidation == True): _filter['side'].add('LIQUIDATION')
            if (_filter_logicSource_fslImmed   == True): _filter['logicSource'].add('FSLIMMED')
            if (_filter_logicSource_fslClose   == True): _filter['logicSource'].add('FSLCLOSE')
            if (_filter_logicSource_entry      == True): _filter['logicSource'].add('ENTRY')
            if (_filter_logicSource_clear      == True): _filter['logicSource'].add('CLEAR')
            if (_filter_logicSource_exit       == True): _filter['logicSource'].add('EXIT')
            if (_filter_logicSource_forceClear == True): _filter['logicSource'].add('FORCECLEAR')
            if (_filter_logicSource_unknown    == True): _filter['logicSource'].add('UNKNOWN')
        #[4]: Filtering
        if (True):
            for _logIndex, _log in enumerate(tradeLogs):
                _test_asset       = False
                _test_symbol      = False
                _test_time        = False
                _test_side        = False
                _test_logicSource = False
                #Asset
                if   (_filter['asset'] == '#ALL#'):                                                 _test_asset = True
                elif (_filter['asset'] == account_positions[_log['positionSymbol']]['quoteAsset']): _test_asset = True
                #Symbol
                if   (_filter['symbol'] == '#ALL#'):                _test_symbol = True
                elif (_filter['symbol'] == _log['positionSymbol']): _test_symbol = True
                #Time
                if   (_filter['time'] == None):                                                                 _test_time = True
                elif ((_filter['time'][0] <= _log['timestamp']) and (_log['timestamp'] <= _filter['time'][1])): _test_time = True
                #Side
                if (_log['side'] in _filter['side']): _test_side = True
                #Logic Source
                if (_log['logicSource'] in _filter['logicSource']): _test_logicSource = True
                #FINALLY
                if ((_test_asset == True) and (_test_symbol == True) and (_test_time == True) and (_test_side == True) and (_test_logicSource == True)): tradeLogs_filteredIndexes.add(_logIndex)
            self.GUIOs["HISTORY_TRADELOGS_TRADELOGSELECTIONBOX"].setDisplayTargets(displayTargets = list(tradeLogs_filteredIndexes))
        #[5]: Net Proft, Gain, Loss, Trading Fee Display Update
        if (True):
            if (asset_selected == '#ALL#'):
                self.GUIOs["HISTORY_TRADELOGS_NETPROFITDISPLAYTEXT"].updateText(text  = "N/A", textStyle = 'DEFAULT')
                self.GUIOs["HISTORY_TRADELOGS_GAINDISPLAYTEXT"].updateText(text       = "N/A")
                self.GUIOs["HISTORY_TRADELOGS_LOSSDISPLAYTEXT"].updateText(text       = "N/A")
                self.GUIOs["HISTORY_TRADELOGS_TRADINGFEEDISPLAYTEXT"].updateText(text = "N/A")
            else:
                _gain       = 0
                _loss       = 0
                _tradingFee = 0
                for _logIndex in tradeLogs_filteredIndexes:
                    _log = tradeLogs[_logIndex]
                    if (_log['profit'] != None):
                        if   (0 < _log['profit']): _gain +=  _log['profit']
                        elif (_log['profit'] < 0): _loss += -_log['profit']
                    if (_log['tradingFee'] != None): _tradingFee += _log['tradingFee']
                self.GUIOs["HISTORY_TRADELOGS_GAINDISPLAYTEXT"].updateText(text       = f"{auxiliaries.floatToString(number = _gain,       precision = _ASSETPRECISIONS_XS[asset_selected])} {asset_selected}")
                self.GUIOs["HISTORY_TRADELOGS_LOSSDISPLAYTEXT"].updateText(text       = f"{auxiliaries.floatToString(number = _loss,       precision = _ASSETPRECISIONS_XS[asset_selected])} {asset_selected}")
                self.GUIOs["HISTORY_TRADELOGS_TRADINGFEEDISPLAYTEXT"].updateText(text = f"{auxiliaries.floatToString(number = _tradingFee, precision = _ASSETPRECISIONS_XS[asset_selected])} {asset_selected}")
                _netProfit = round(_gain-_loss-_tradingFee, _ASSETPRECISIONS[asset_selected])
                if   (_netProfit < 0):  str = f"{auxiliaries.floatToString(number  = _netProfit, precision = _ASSETPRECISIONS_XS[asset_selected])}"; strCol = 'RED_LIGHT'
                elif (_netProfit == 0): str = f"{auxiliaries.floatToString(number  = _netProfit, precision = _ASSETPRECISIONS_XS[asset_selected])}"; strCol = 'DEFAULT'
                else:                   str = f"+{auxiliaries.floatToString(number = _netProfit, precision = _ASSETPRECISIONS_XS[asset_selected])}"; strCol = 'GREEN_LIGHT'
                _netProfit_text = ""; _netProfit_textStyle = list()
                for _newTextString, _newTextStyle in ((str,                  strCol), 
                                                      (f" {asset_selected}", 'DEFAULT')):
                    _netProfit_textStyle.append(((len(_netProfit_text), len(_netProfit_text)+len(_newTextString)-1), _newTextStyle))
                    _netProfit_text += _newTextString
                self.GUIOs["HISTORY_TRADELOGS_NETPROFITDISPLAYTEXT"].updateText(text = _netProfit_text, textStyle = _netProfit_textStyle)
        #[6]: Logs Counter Display Update
        if (True):
            #Setup
            _nLogs_total_total,       _nLogs_total_viewing       = 0,0
            _nLogs_asset_total,       _nLogs_asset_viewing       = 0,0
            _nLogs_position_total,    _nLogs_position_viewing    = 0,0
            _nLogs_time_total,        _nLogs_time_viewing        = 0,0
            _nLogs_buy_total,         _nLogs_buy_viewing         = 0,0
            _nLogs_sell_total,        _nLogs_sell_viewing        = 0,0
            _nLogs_liquidation_total, _nLogs_liquidation_viewing = 0,0
            _nLogs_fslImmed_total,    _nLogs_fslImmed_viewing    = 0,0
            _nLogs_fslClose_total,    _nLogs_fslClose_viewing    = 0,0
            _nLogs_entry_total,       _nLogs_entry_viewing       = 0,0
            _nLogs_clear_total,       _nLogs_clear_viewing       = 0,0
            _nLogs_exit_total,        _nLogs_exit_viewing        = 0,0
            _nLogs_forceClear_total,  _nLogs_forceClear_viewing  = 0,0
            _nLogs_unknown_total,     _nLogs_unknown_viewing     = 0,0
            #Counting
            for _logIndex, _log in enumerate(tradeLogs):
                _isViewing = (_logIndex in tradeLogs_filteredIndexes)
                #Main
                _test_asset    = ((_filter['asset'] == '#ALL#') or (_filter['asset'] == account_positions[_log['positionSymbol']]['quoteAsset']))
                _test_position = (((_filter['symbol'] == '#ALL#') and (_test_asset == True)) or (_filter['symbol'] == _log['positionSymbol']))
                _test_time     = (_filter['time'] is None) or ((_filter['time'][0] <= _log['timestamp']) and (_log['timestamp'] <= _filter['time'][1]))
                #---[1]: Total
                _nLogs_total_total += 1
                if (_isViewing == True): _nLogs_total_viewing += 1
                #---[2]: Asset
                if (_test_asset == True):
                    _nLogs_asset_total += 1
                    if (_isViewing == True): _nLogs_asset_viewing += 1
                #---[3]: Position
                if (_test_position == True):
                    _nLogs_position_total += 1
                    if (_isViewing == True): _nLogs_position_viewing += 1
                #---[4]: Time
                if (_test_time == True):
                    if (_test_position == True): _nLogs_time_total   += 1
                    if (_isViewing == True):     _nLogs_time_viewing += 1
                #Side
                _log_side = _log['side']
                #---[5]: Buy
                if (_log_side == 'BUY'):
                    if ((_test_position == True) and (_test_time == True)): _nLogs_buy_total   += 1
                    if (_isViewing == True):                                _nLogs_buy_viewing += 1
                #---[6]: Sell
                elif (_log_side == 'SELL'):
                    if ((_test_position == True) and (_test_time == True)): _nLogs_sell_total   += 1
                    if (_isViewing == True):                                _nLogs_sell_viewing += 1
                #---[7]: Liquidation
                elif (_log_side == 'LIQUIDATION'):
                    if ((_test_position == True) and (_test_time == True)): _nLogs_liquidation_total   += 1
                    if (_isViewing == True):                                _nLogs_liquidation_viewing += 1
                #Logic Source
                _log_logicSource = _log['logicSource']
                #---[8]: FSLIMMED
                if (_log_logicSource == 'FSLIMMED'):
                    if ((_test_position == True) and (_test_time == True)): _nLogs_fslImmed_total   += 1
                    if (_isViewing == True):                                _nLogs_fslImmed_viewing += 1
                #---[9]: FSLCLOSE
                elif (_log_logicSource == 'FSLCLOSE'):
                    if ((_test_position == True) and (_test_time == True)): _nLogs_fslClose_total   += 1
                    if (_isViewing == True):                                _nLogs_fslClose_viewing += 1
                #---[10]: Entry
                elif (_log_logicSource == 'ENTRY'):
                    if ((_test_position == True) and (_test_time == True)): _nLogs_entry_total   += 1
                    if (_isViewing == True):                                _nLogs_entry_viewing += 1
                #---[11]: Clear
                elif (_log_logicSource == 'CLEAR'):
                    if ((_test_position == True) and (_test_time == True)): _nLogs_clear_total   += 1
                    if (_isViewing == True):                                _nLogs_clear_viewing += 1
                #---[12]: Exit
                elif (_log_logicSource == 'EXIT'):
                    if ((_test_position == True) and (_test_time == True)): _nLogs_exit_total   += 1
                    if (_isViewing == True):                                _nLogs_exit_viewing += 1
            #Text Update
            self.GUIOs["HISTORY_TRADELOGS_NTOTALLOGSDISPLAYTEXT"].updateText(text    = f"{_nLogs_total_viewing:,d} / {_nLogs_total_total:,d}")
            self.GUIOs["HISTORY_TRADELOGS_NASSETLOGSDISPLAYTEXT"].updateText(text    = f"{_nLogs_asset_viewing:,d} / {_nLogs_asset_total:,d}")
            self.GUIOs["HISTORY_TRADELOGS_NPOSITIONLOGSDISPLAYTEXT"].updateText(text = f"{_nLogs_position_viewing:,d} / {_nLogs_position_total:,d}")
            self.GUIOs["HISTORY_TRADELOGS_NTIMELOGSDISPLAYTEXT"].updateText(text     = f"{_nLogs_time_viewing:,d} / {_nLogs_time_total:,d}")
            self.GUIOs["HISTORY_TRADELOGS_NBUYDISPLAYTEXT"].updateText(text          = f"{_nLogs_buy_viewing:,d} / {_nLogs_buy_total:,d}")
            self.GUIOs["HISTORY_TRADELOGS_NSELLDISPLAYTEXT"].updateText(text         = f"{_nLogs_sell_viewing:,d} / {_nLogs_sell_total:,d}")
            self.GUIOs["HISTORY_TRADELOGS_NLIQUIDATIONDISPLAYTEXT"].updateText(text  = f"{_nLogs_liquidation_viewing:,d} / {_nLogs_liquidation_total:,d}")
            self.GUIOs["HISTORY_TRADELOGS_NFSLIMMEDDISPLAYTEXT"].updateText(text     = f"{_nLogs_fslImmed_viewing:,d} / {_nLogs_fslImmed_total:,d}")
            self.GUIOs["HISTORY_TRADELOGS_NFSLCLOSEDISPLAYTEXT"].updateText(text     = f"{_nLogs_fslClose_viewing:,d} / {_nLogs_fslClose_total:,d}")
            self.GUIOs["HISTORY_TRADELOGS_NENTRYDISPLAYTEXT"].updateText(text        = f"{_nLogs_entry_viewing:,d} / {_nLogs_entry_total:,d}")
            self.GUIOs["HISTORY_TRADELOGS_NCLEARDISPLAYTEXT"].updateText(text        = f"{_nLogs_clear_viewing:,d} / {_nLogs_clear_total:,d}")
            self.GUIOs["HISTORY_TRADELOGS_NEXITDISPLAYTEXT"].updateText(text         = f"{_nLogs_exit_viewing:,d} / {_nLogs_exit_total:,d}")
            self.GUIOs["HISTORY_TRADELOGS_NFORCECLEARDISPLAYTEXT"].updateText(text   = f"{_nLogs_forceClear_viewing:,d} / {_nLogs_forceClear_total:,d}")
            self.GUIOs["HISTORY_TRADELOGS_NUNKNOWNDISPLAYTEXT"].updateText(text      = f"{_nLogs_unknown_viewing:,d} / {_nLogs_unknown_total:,d}")
    def __onTradeLogSelectionUpdate():
        if (self.puVar['accounts_selected'] != None): _positions = self.puVar['accounts'][self.puVar['accounts_selected']]['positions']
        else:                                         _positions = None
        try:    _logIndex_selected = self.GUIOs["HISTORY_TRADELOGS_TRADELOGSELECTIONBOX"].getSelected()[0]
        except: _logIndex_selected = None
        if (_logIndex_selected != None):
            _tradeLog = self.puVar['historyView_tradeLogs'][_logIndex_selected]
            _positionSymbol = _tradeLog['positionSymbol']
            _precisions = _positions[_positionSymbol]['precisions']
        else: pass
    auxFunctions['SETTRADELOGSLIST']          = __setTradeLogsList
    auxFunctions['ONTRADELOGSFILTERUPDATE']   = __onTradeLogsFilterUpdate
    auxFunctions['ONTRADELOGSELECTIONUPDATE'] = __onTradeLogSelectionUpdate

    #Return the generated functions
    return auxFunctions
#AUXILALRY FUNCTIONS END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------