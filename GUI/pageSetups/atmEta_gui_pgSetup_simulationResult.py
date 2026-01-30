#ATM Modules
import atmEta_IPC
import atmEta_Auxillaries
import atmEta_RQPMFunctions
import atmEta_Constants
from GUI import atmEta_gui_AdvancedPygletGroups
from GUI.atmEta_gui_TextControl import textObject_SL, textObject_SL_I, textObject_SL_IE
from GUI.atmEta_gui_Generals import passiveGraphics_typeA,\
                                    passiveGraphics_wrapperTypeA,\
                                    passiveGraphics_wrapperTypeB,\
                                    passiveGraphics_wrapperTypeC,\
                                    textBox_typeA,\
                                    imageBox_typeA,\
                                    button_typeA,\
                                    button_typeB,\
                                    switch_typeA,\
                                    switch_typeB,\
                                    switch_typeC,\
                                    slider_typeA,\
                                    scrollBar_typeA,\
                                    textInputBox_typeA,\
                                    LED_typeA,\
                                    gaugeBar_typeA,\
                                    selectionBox_typeA,\
                                    selectionBox_typeB,\
                                    selectionBox_typeC,\
                                    subPageBox_typeA
from GUI.atmEta_gui_ChartDrawer         import chartDrawer
from GUI.atmEta_gui_DailyReportViewer   import dailyReportViewer
from GUI.atmEta_gui_HourlyReportViewer  import hourlyReportViewer
from GUI.atmEta_gui_NeuralNetworkViewer import neuralNetworkViewer

#Python Modules
import pyglet
import pprint
import termcolor
import time
import random
import math
from datetime import datetime, timezone, tzinfo

#Constants
_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT

_ASSETPRECISIONS    = {'USDT': 8, 'USDC': 8, 'BTC': 6}
_ASSETPRECISIONS_S  = {'USDT': 4, 'USDC': 4, 'BTC': 4}
_ASSETPRECISIONS_XS = {'USDT': 2, 'USDC': 2, 'BTC': 2}

_POSITIONDATA_SELECTIONBOXCOLUMNINDEX = {'currencyAnalysisConfigurationCode': 2,
                                         'tradeConfigurationCode':            3,
                                         'isolated':                          4,
                                         'leverage':                          5,
                                         'priority':                          6,
                                         'assumedRatio':                      7,
                                         'weightedAssumedRatio':              8,
                                         'allocatedBalance':                  9,
                                         'maxAllocatedBalance':               10}

#SETUP PAGE <MAIN> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def setupPage(self):
    #Set page unique variables
    self.puVar['simulations']         = dict()
    self.puVar['simulation_selected'] = None
    self.puVar['simulation_selected_tradeLogs']    = None
    self.puVar['simulation_selected_dailyRecords'] = None
    self.puVar['simulation_toLoad']   = None
    self.puVar['simulationDetailView_selected']  = 'ASSETPOSITIONSETUP'
    self.puVar['simulationDetailView_firstLoad'] = {'ASSETPOSITIONSETUP': True,
                                                    'CONFIGURATIONS':     True,
                                                    'TRADELOGS':          True,
                                                    'DAILYREPORTS':       True,
                                                    'POSITIONCHART':      True}
    self.puVar['simulationDetailView_selectionPair'] = {'ASSETPOSITIONSETUP': [None,    None],
                                                        'CONFIGURATIONS':     ['#ALL#', '#ALL#'],
                                                        'TRADELOGS':          ['#ALL#', '#ALL#'],
                                                        'DAILYREPORTS':       [None,    None],
                                                        'POSITIONCHART':      ['#ALL#', None]}
    self.puVar['simulationDetailView_Configurations_CurrentCACConfigSubPage'] = 'MAIN'

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
        self.GUIOs["TITLETEXT_SIMULATIONRESULT"] = textBox_typeA(**inst, groupOrder=1, xPos= 6500, yPos=8550, width=3000, height=400, style=None, text=self.visualManager.getTextPack('SIMULATIONRESULT:TITLE'), fontSize = 220, textInteractable = False)

        self.GUIOs["BUTTON_MOVETO_DASHBOARD"] = button_typeB(**inst,  groupOrder=2, xPos=  50, yPos=8650, width= 300, height=300, style="styleB", releaseFunction=self.pageObjectFunctions['PAGEMOVE_DASHBOARD'], image = 'dashboardIcon_512x512.png', imageSize = (225, 225), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))

        #<SIMULATIONS>
        self.GUIOs["SIMULATIONS_BLOCKTITLE"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=8350, width=5000, height=200, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKTITLE_SIMULATIONS'), fontSize=80)
        self.GUIOs["SIMULATIONS_SEARCHTITLETEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=8000, width= 700, height= 250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONS_SEARCH'), fontSize=80, textInteractable=False)
        self.GUIOs["SIMULATIONS_SEARCHTEXTINPUTBOX"]       = textInputBox_typeA(**inst, groupOrder=1, xPos= 900, yPos=8000, width=1700, height= 250, style="styleA", text="",                                                                    fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_SIMULATIONS_SEARCHTEXT'])
        self.GUIOs["SIMULATIONS_SORTBYTITLETEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos=2700, yPos=8000, width= 800, height= 250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONS_SORTBY'), fontSize=80, textInteractable=False)
        self.GUIOs["SIMULATIONS_SORTBYSELECTIONBOX"]       = selectionBox_typeB(**inst, groupOrder=2, xPos=3600, yPos=8000, width=1500, height= 250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_SIMULATIONS_SORTTYPESELECTION'])
        simulationSortTypes = {'INDEX':           {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONS_SORTBY_INDEX')},
                               'SIMULATIONCODE':  {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONS_SORTBY_SIMULATIONCODE')},
                               'SIMULATIONRANGE': {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONS_SORTBY_SIMULATIONRANGE')},
                               'CREATIONTIME':    {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONS_SORTBY_CREATIONTIME')}}
        self.GUIOs["SIMULATIONS_SORTBYSELECTIONBOX"].setSelectionList(selectionList = simulationSortTypes, displayTargets = 'all')
        self.GUIOs["SIMULATIONS_SORTBYSELECTIONBOX"].setSelected(itemKey = 'CREATIONTIME', callSelectionUpdateFunction = False)
        self.GUIOs["SIMULATIONS_SELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=2, xPos= 100, yPos=3900, width=5000, height=4000, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_SIMULATIONS_SIMULATION'], 
                                                                    elementWidths = (500, 1650, 1600, 1000)) #4750
        self.GUIOs["SIMULATIONS_SELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONS_ST_INDEX')},           # 500
                                                                                {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONS_ST_SIMULATIONCODE')},  #1650
                                                                                {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONS_ST_SIMULATIONRANGE')}, #1600
                                                                                {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONS_ST_CREATIONTIME')}])   #1000
        self.GUIOs["SIMULATIONS_SIMULATIONCODETITLETEXT"]     = textBox_typeA(**inst,  groupOrder=1, xPos= 100, yPos=3550, width=1300, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONS_SIMULATIONCODE'),  fontSize=80, textInteractable=False)
        self.GUIOs["SIMULATIONS_SIMULATIONCODEDISPLAYTEXT"]   = textBox_typeA(**inst,  groupOrder=1, xPos=1500, yPos=3550, width=3600, height=250, style="styleA", text="-",                                                                            fontSize=80, textInteractable=True)
        self.GUIOs["SIMULATIONS_SIMULATIONRANGETITLETEXT"]    = textBox_typeA(**inst,  groupOrder=1, xPos= 100, yPos=3200, width=1300, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONS_SIMULATIONRANGE'), fontSize=80, textInteractable=False)
        self.GUIOs["SIMULATIONS_SIMULATIONRANGEDISPLAYTEXT1"] = textBox_typeA(**inst,  groupOrder=1, xPos=1500, yPos=3200, width=1750, height=250, style="styleA", text="-",                                                                            fontSize=80, textInteractable=True)
        self.GUIOs["SIMULATIONS_SIMULATIONRANGEDISPLAYTEXT2"] = textBox_typeA(**inst,  groupOrder=1, xPos=3350, yPos=3200, width=1750, height=250, style="styleA", text="-",                                                                            fontSize=80, textInteractable=True)

        #<SIMULATION SUMMARY>
        self.GUIOs["RESULTSUMMARY_BLOCKTITLE"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=2900, width=5000, height=200, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKTITLE_SIMULATIONSUMMARY'), fontSize=80)
        self.GUIOs["RESULTSUMMARY_ASSETTITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=2550, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:RESULTSUMMARY_ASSET'), fontSize=80, textInteractable=False)
        self.GUIOs["RESULTSUMMARY_ASSETSELECTIONBOX"] = selectionBox_typeB(**inst, groupOrder=2, xPos=2200, yPos=2550, width=2550, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_RESULTSUMMARY_ASSET'])
        assetsToDisplay = {'total': {'text': self.visualManager.getTextPack('SIMULATIONRESULT:RESULTSUMMARY_ASSETSELECTION_TOTAL')},
                           'USDT':  {'text': 'USDT'},
                           'USDC':  {'text': 'USDC'}}
        self.GUIOs["RESULTSUMMARY_ASSETSELECTIONBOX"].setSelectionList(selectionList = assetsToDisplay, displayTargets = 'all')
        self.GUIOs["RESULTSUMMARY_ASSETSELECTIONBOX"].setSelected(itemKey = 'total', callSelectionUpdateFunction = False)
        self.GUIOs["RESULTSUMMARY_SELECTEDASSETIMAGEBOX"] = imageBox_typeA(**inst, groupOrder=1, xPos=4850, yPos=2550, width= 250, height=250, style=None, image="assetTotalIcon_512x512.png")
        self.GUIOs["RESULTSUMMARY_NTRADEDAYSTITLETEXT"]                = textBox_typeA(**inst,  groupOrder=1, xPos= 100, yPos=2200, width= 900, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:RESULTSUMMARY_NTRADEDAYS'),       fontSize=80, textInteractable=False)
        self.GUIOs["RESULTSUMMARY_NTRADEDAYSDISPLAYTEXT"]              = textBox_typeA(**inst,  groupOrder=1, xPos=1100, yPos=2200, width=1450, height=250, style="styleA", text="-",                                                                               fontSize=80, textInteractable=True)
        self.GUIOs["RESULTSUMMARY_NTRADESTITLETEXT"]                   = textBox_typeA(**inst,  groupOrder=1, xPos=2650, yPos=2200, width= 900, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:RESULTSUMMARY_NTRADES_TOTAL'),    fontSize=80, textInteractable=False)
        self.GUIOs["RESULTSUMMARY_NTRADESDISPLAYTEXT"]                 = textBox_typeA(**inst,  groupOrder=1, xPos=3650, yPos=2200, width=1450, height=250, style="styleA", text="-",                                                                               fontSize=80, textInteractable=True)
        self.GUIOs["RESULTSUMMARY_NETPROFITTITLETEXT"]                 = textBox_typeA(**inst,  groupOrder=1, xPos= 100, yPos=1850, width= 900, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:RESULTSUMMARY_NETPROFIT'),        fontSize=80, textInteractable=False)
        self.GUIOs["RESULTSUMMARY_NETPROFITDISPLAYTEXT"]               = textBox_typeA(**inst,  groupOrder=1, xPos=1100, yPos=1850, width=1450, height=250, style="styleA", text="-",                                                                               fontSize=80, textInteractable=True)
        self.GUIOs["RESULTSUMMARY_GAINSTITLETEXT"]                     = textBox_typeA(**inst,  groupOrder=1, xPos=2650, yPos=1850, width= 900, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:RESULTSUMMARY_GAINS'),            fontSize=80, textInteractable=False)
        self.GUIOs["RESULTSUMMARY_GAINSDISPLAYTEXT"]                   = textBox_typeA(**inst,  groupOrder=1, xPos=3650, yPos=1850, width=1450, height=250, style="styleA", text="-",                                                                               fontSize=80, textInteractable=True)
        self.GUIOs["RESULTSUMMARY_LOSSESTITLETEXT"]                    = textBox_typeA(**inst,  groupOrder=1, xPos= 100, yPos=1500, width= 900, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:RESULTSUMMARY_LOSSES'),           fontSize=80, textInteractable=False)
        self.GUIOs["RESULTSUMMARY_LOSSESDISPLAYTEXT"]                  = textBox_typeA(**inst,  groupOrder=1, xPos=1100, yPos=1500, width=1450, height=250, style="styleA", text="-",                                                                               fontSize=80, textInteractable=True)
        self.GUIOs["RESULTSUMMARY_FEESTITLETEXT"]                      = textBox_typeA(**inst,  groupOrder=1, xPos=2650, yPos=1500, width= 900, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:RESULTSUMMARY_FEES'),             fontSize=80, textInteractable=False)
        self.GUIOs["RESULTSUMMARY_FEESDISPLAYTEXT"]                    = textBox_typeA(**inst,  groupOrder=1, xPos=3650, yPos=1500, width=1450, height=250, style="styleA", text="-",                                                                               fontSize=80, textInteractable=True)
        self.GUIOs["RESULTSUMMARY_WALLETBALANCE1TITLETEXT"]            = textBox_typeA(**inst,  groupOrder=1, xPos= 100, yPos=1150, width=1700, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:RESULTSUMMARY_WALLETBALANCE1'),   fontSize=80, textInteractable=False)
        self.GUIOs["RESULTSUMMARY_WALLETBALANCE1DISPLAYTEXT"]          = textBox_typeA(**inst,  groupOrder=1, xPos=1900, yPos=1150, width=3200, height=250, style="styleA", text="- / -",                                                                           fontSize=80, textInteractable=True)
        self.GUIOs["RESULTSUMMARY_WALLETBALANCE2TITLETEXT"]            = textBox_typeA(**inst,  groupOrder=1, xPos= 100, yPos= 800, width=1700, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:RESULTSUMMARY_WALLETBALANCE2'),   fontSize=80, textInteractable=False)
        self.GUIOs["RESULTSUMMARY_WALLETBALANCE2DISPLAYTEXT"]          = textBox_typeA(**inst,  groupOrder=1, xPos=1900, yPos= 800, width=3200, height=250, style="styleA", text="- / -",                                                                           fontSize=80, textInteractable=True)
        self.GUIOs["RESULTSUMMARY_WALLETBALANCEGROWTHRATETITLETEXT"]   = textBox_typeA(**inst,  groupOrder=1, xPos= 100, yPos= 450, width=1700, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:RESULTSUMMARY_WALLETBALANCEGROWTHRATE'), fontSize=80, textInteractable=False)
        self.GUIOs["RESULTSUMMARY_WALLETBALANCEGROWTHRATEDISPLAYTEXT"] = textBox_typeA(**inst,  groupOrder=1, xPos=1900, yPos= 450, width=3200, height=250, style="styleA", text="-",                                                                                      fontSize=80, textInteractable=True)
        self.GUIOs["RESULTSUMMARY_WALLETBALANCEVOLATILITYTITLETEXT"]   = textBox_typeA(**inst,  groupOrder=1, xPos= 100, yPos= 100, width=1700, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:RESULTSUMMARY_WALLETBALANCEVOLATILITY'), fontSize=80, textInteractable=False)
        self.GUIOs["RESULTSUMMARY_WALLETBALANCEVOLATILITYDISPLAYTEXT"] = textBox_typeA(**inst,  groupOrder=1, xPos=1900, yPos= 100, width=3200, height=250, style="styleA", text="-",                                                                                      fontSize=80, textInteractable=True)

        #<SIMULATION DETAIL>
        self.GUIOs["SIMULATIONDETAIL_BLOCKTITLE"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=5200, yPos=8350, width=10700, height=200, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKTITLE_SIMULATIONDETAIL'), fontSize=80)
        self.GUIOs["SIMULATIONDETAIL_VIEWTITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos=5200, yPos=8000, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_VIEWTYPE'), fontSize=80, textInteractable=False)
        self.GUIOs["SIMULATIONDETAIL_VIEWSELECTIONBOX"] = selectionBox_typeB(**inst, groupOrder=2, xPos=6500, yPos=8000, width=2300, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_VIEW'])
        _viewTypes = {'ASSETPOSITIONSETUP': {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_VIEWTYPE_ASSETPOSITIONSETUP')},
                      'CONFIGURATIONS':     {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_VIEWTYPE_CONFIGURATIONS')},
                      'TRADELOGS':          {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_VIEWTYPE_TRADELOGS')},
                      'DAILYREPORTS':       {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_VIEWTYPE_DAILYREPORTS')},
                      'POSITIONCHART':      {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_VIEWTYPE_POSITIONCHART')}}
        self.GUIOs["SIMULATIONDETAIL_VIEWSELECTIONBOX"].setSelectionList(selectionList = _viewTypes, displayTargets = 'all')
        self.GUIOs["SIMULATIONDETAIL_VIEWSELECTIONBOX"].setSelected(itemKey = 'ASSETPOSITIONSETUP', callSelectionUpdateFunction = False)
        self.GUIOs["SIMULATIONDETAIL_ASSETTITLETEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos= 8900, yPos=8000, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSET'), fontSize=80, textInteractable=False)
        self.GUIOs["SIMULATIONDETAIL_ASSETSELECTIONBOX"]    = selectionBox_typeB(**inst, groupOrder=2, xPos=10000, yPos=8000, width=1500, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_ASSET'])
        self.GUIOs["SIMULATIONDETAIL_ASSETIMAGEBOX"]        = imageBox_typeA(**inst,     groupOrder=1, xPos=11600, yPos=8000, width= 250, height=250, style=None, image="assetEmptyIcon_512x512.png")
        self.GUIOs["SIMULATIONDETAIL_POSITIONTITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos=11950, yPos=8000, width=1250, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_POSITION'), fontSize=80, textInteractable=False)
        self.GUIOs["SIMULATIONDETAIL_POSITIONSELECTIONBOX"] = selectionBox_typeB(**inst, groupOrder=2, xPos=13300, yPos=8000, width=2600, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_POSITION'])
        self.GUIOs["SIMULATIONDETAIL_ASSETSELECTIONBOX"].deactivate()
        self.GUIOs["SIMULATIONDETAIL_POSITIONSELECTIONBOX"].deactivate()
        self.puVar['GUIOGROUPS'] = dict()
        #---Asset & Position Setup
        if (True):
            #Positions
            self.GUIOs["BLOCKTITLE_SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSTIONS"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=5200, yPos=7700, width=10700, height=200, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKTITLE_SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS'),  fontSize=80)
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCHTITLETEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos= 5200, yPos=7350, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCH'),     fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCHTEXTINPUTBOX"]     = textInputBox_typeA(**inst, groupOrder=1, xPos= 6300, yPos=7350, width=3700, height=250, style="styleA", text="",                                                                fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCHTEXT'])
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCHTYPESELECTIONBOX"] = selectionBox_typeB(**inst, groupOrder=2, xPos=10100, yPos=7350, width=2000, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCHTYPE'])
            positionSearchTypes = {'SYMBOL':  {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCH_SYMBOL')},
                                   'CACCODE': {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCH_CACCODE')},
                                   'TCCODE':  {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCH_TCCODE')}}
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCHTYPESELECTIONBOX"].setSelectionList(selectionList = positionSearchTypes, displayTargets = 'all')
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCHTYPESELECTIONBOX"].setSelected(itemKey = 'SYMBOL', callSelectionUpdateFunction = False)
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBYTITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos=12200, yPos=7350, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY'),     fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBYSELECTIONBOX"] = selectionBox_typeB(**inst, groupOrder=2, xPos=13300, yPos=7350, width=2600, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTTYPE'])
            positionsSortTypes = {'INDEX':                {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_INDEX')},
                                  'SYMBOL':               {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_SYMBOL')},
                                  'CACCODE':              {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_CACCODE')},
                                  'TCCODE':               {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_TCCODE')},
                                  'MARGINMODE':           {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_MARGINMODE')},
                                  'LEVERAGE':             {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_LEVERAGE')},
                                  'PRIORITY':             {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_PRIORITY')},
                                  'ASSUMEDRATIO':         {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_ASSUMEDRATIO')},
                                  'WEIGHTEDASSUMEDRATIO': {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_WEIGHTEDASSUMEDRATIO')},
                                  'ALLOCATEDBALANCE':     {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_ALLOCATEDBALANCE')},
                                  'MAXALLOCATEDBALANCE':  {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_MAXALLOCATEDBALANCE')},
                                  'FIRSTKLINE':           {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_FIRSTKLINE')}}
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBYSELECTIONBOX"].setSelectionList(selectionList = positionsSortTypes, displayTargets = 'all')
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBYSELECTIONBOX"].setSelected(itemKey = 'INDEX', callSelectionUpdateFunction = False)
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=2, xPos=5200, yPos=1100, width=10700, height=6150, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = None, 
                                                                                                      elementWidths = (600, 1200, 1200, 1200, 700, 500, 500, 600, 600, 1100, 1100, 1150)) #10450
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_INDEX')},                             # 600
                                                                                                                      {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_SYMBOL')},                            #1200
                                                                                                                      {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_CURRENCYANALYSISCONFIGURATIONCODE')}, #1200
                                                                                                                      {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_TRADECONFIGURATIONCODE')},            #1200
                                                                                                                      {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_MARGINMODE')},                        # 700
                                                                                                                      {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_LEVERAGE')},                          # 500
                                                                                                                      {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_PRIORITY')},                          # 500
                                                                                                                      {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_ASSUMEDRATIO')},                      # 600
                                                                                                                      {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_WEIGHTEDASSUMEDRATIO')},              # 600
                                                                                                                      {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_ALLOCATEDBALANCE')},                  #1100
                                                                                                                      {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_MAXALLOCATEDBALANCE')},               #1100
                                                                                                                      {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_FIRSTKLINE')}])                       #1150
            #Assets
            self.GUIOs["BLOCKTITLE_SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=5200, yPos=800, width=10700, height=200, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKTITLE_SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS'), fontSize=80)
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSETTITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos= 5200, yPos=450, width=1400, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSET'),                fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSETSELECTIONBOX"] = selectionBox_typeB(**inst, groupOrder=2, xPos= 6700, yPos=450, width=1700, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 1, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSET'])
            assetsToDisplay = {'USDT': {'text': 'USDT'},
                               'USDC': {'text': 'USDC'}}
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSETSELECTIONBOX"].setSelectionList(selectionList = assetsToDisplay, displayTargets = 'all')
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSETSELECTIONBOX"].setSelected(itemKey = 'USDT', callSelectionUpdateFunction = False)
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_INITIALWALLETBALANCETITLETEXT"]    = textBox_typeA(**inst,  groupOrder=1, xPos= 8500, yPos=450, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_INITIALWALLETBALANCE'), fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_INITIALWALLETBALANCEDISPLAYTEXT"]  = textBox_typeA(**inst,  groupOrder=1, xPos=10600, yPos=450, width=2200, height=250, style="styleA", text="-",                                                                                                                fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ALLOCATIONRATIOTITLETEXT"]         = textBox_typeA(**inst,  groupOrder=1, xPos=12900, yPos=450, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ALLOCATIONRATIO'),      fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ALLOCATIONRATIODISPLAYTEXT"]       = textBox_typeA(**inst,  groupOrder=1, xPos=14500, yPos=450, width=1050, height=250, style="styleA", text="-",                                                                                                                fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_SELECTEDASSETIMAGEBOX"]            = imageBox_typeA(**inst, groupOrder=1, xPos=15650, yPos=450, width= 250, height=250, style=None, image="usdtIcon_512x512.png")
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSUMEDRATIOTITLETEXT"]            = textBox_typeA(**inst,  groupOrder=1, xPos= 5200, yPos=100, width=1350, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSUMEDRATIO'),         fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSUMEDRATIODISPLAYTEXT"]          = textBox_typeA(**inst,  groupOrder=1, xPos= 6650, yPos=100, width=1000, height=250, style="styleA", text="-",                                                                                                                fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_WEIGHTEDASSUMEDRATIOTITLETEXT"]    = textBox_typeA(**inst,  groupOrder=1, xPos= 7750, yPos=100, width=1350, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_WEIGHTEDASSUMEDRATIO'), fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_WEIGHTEDASSUMEDRATIODISPLAYTEXT"]  = textBox_typeA(**inst,  groupOrder=1, xPos= 9200, yPos=100, width=1000, height=250, style="styleA", text="-",                                                                                                                fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ALLOCATEDBALANCETITLETEXT"]        = textBox_typeA(**inst,  groupOrder=1, xPos=10300, yPos=100, width=1450, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ALLOCATEDBALANCE'),     fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ALLOCATEDBALANCEDISPLAYTEXT"]      = textBox_typeA(**inst,  groupOrder=1, xPos=11850, yPos=100, width=1100, height=250, style="styleA", text="-",                                                                                                                fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_MAXALLOCATEDBALANCETITLETEXT"]     = textBox_typeA(**inst,  groupOrder=1, xPos=13050, yPos=100, width=1650, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_MAXALLOCATEDBALANCE'),  fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_MAXALLOCATEDBALANCEDISPLAYTEXT"]   = textBox_typeA(**inst,  groupOrder=1, xPos=14800, yPos=100, width=1100, height=250, style="styleA", text="-",                                                                                                                fontSize=80, textInteractable=True)
            #Grouping
            self.puVar['GUIOGROUPS']['ASSETPOSITIONSETUP'] = ["BLOCKTITLE_SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSTIONS",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCHTITLETEXT",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCHTEXTINPUTBOX",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCHTYPESELECTIONBOX",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBYTITLETEXT",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBYSELECTIONBOX",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SELECTIONBOX",
                                                              "BLOCKTITLE_SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSETTITLETEXT",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSETSELECTIONBOX",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_INITIALWALLETBALANCETITLETEXT",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_INITIALWALLETBALANCEDISPLAYTEXT",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ALLOCATIONRATIOTITLETEXT",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ALLOCATIONRATIODISPLAYTEXT",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_SELECTEDASSETIMAGEBOX",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSUMEDRATIOTITLETEXT",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSUMEDRATIODISPLAYTEXT",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_WEIGHTEDASSUMEDRATIOTITLETEXT",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_WEIGHTEDASSUMEDRATIODISPLAYTEXT",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ALLOCATEDBALANCETITLETEXT",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ALLOCATEDBALANCEDISPLAYTEXT",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_MAXALLOCATEDBALANCETITLETEXT",
                                                              "SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_MAXALLOCATEDBALANCEDISPLAYTEXT",
                                                              ]
        for _guioName in self.puVar['GUIOGROUPS']['ASSETPOSITIONSETUP']: self.GUIOs[_guioName].show()
        #---Configurations
        if (True):
            #Currency Analysis Configurations
            self.GUIOs["BLOCKTITLE_SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONS"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos= 5200, yPos=7700, width=5300, height=200, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKTITLE_SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONS'), fontSize=80)
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIURATIONTITLETEXT"]     = textBox_typeA(**inst,      groupOrder=1, xPos=5200, yPos=7350, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONCODE'), fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIURATIONSELECTIONBOX"]  = selectionBox_typeB(**inst, groupOrder=2, xPos=6300, yPos=7350, width=3300, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATION'])
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_NCURRENCYANALYSISCONFIURATIONSDISPLAYTEXT"] = textBox_typeA(**inst,      groupOrder=1, xPos=9700, yPos=7350, width= 800, height=250, style="styleA", text="-", fontSize=80, textInteractable=False)
            _MITypes = ('SMA', 'WMA', 'EMA', 'PSAR', 'BOL', 'IVP', 'SWING')
            _SITypes = ('VOL', 'NNA', 'MMACDSHORT', 'MMACDLONG', 'DMIxADX', 'MFI')
            _currenyAnalysisConfigurationSubPageNames = ('MAIN',)+_MITypes+_SITypes
            for _configSubPageName in _currenyAnalysisConfigurationSubPageNames: self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_{:s}".format(_configSubPageName)] = subPageBox_typeA(**inst, groupOrder=1, xPos=5200, yPos=100, width=5300, height=7150, style=None, useScrollBar_V=True, useScrollBar_H=False)
            if (True):
                _yPos_beg = 20000
                _subPageViewSpaceWidth = self.GUIOs["BLOCKTITLE_SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONS"].width-150
                if (True): #Configuration/MAIN
                    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MAIN"]
                    yPosPoint0 = _yPos_beg
                    spo.addGUIO("TITLE_MAININDICATORS", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_MAININDICATORS'), 'fontSize': 80})
                    for i, miType in enumerate(_MITypes):
                        spo.addGUIO(f"INDICATORMASTERSWITCH_{miType}", switch_typeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-350-350*i, 'width': 4250, 'height': 250, 'style': 'styleB', 'text': miType, 'fontSize': 80})
                        spo.GUIOs[f"INDICATORMASTERSWITCH_{miType}"].deactivate()
                        spo.addGUIO(f"TOCONFIGSUBPAGE_{miType}",       button_typeA, {'groupOrder': 0, 'xPos': 4350, 'yPos': yPosPoint0-350-350*i, 'width':  800, 'height': 250, 'style': 'styleA', 'text': ">", 'fontSize': 80, 'name': f'navButton_{miType}', 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
                    yPosPoint1 = yPosPoint0-300-350*len(_MITypes)
                    spo.addGUIO("TITLE_SUBINDICATORS", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_SUBINDICATORS'), 'fontSize': 80})
                    for i, siType in enumerate(_SITypes):
                        spo.addGUIO(f"INDICATORMASTERSWITCH_{siType}", switch_typeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350-350*i, 'width': 4250, 'height': 250, 'style': 'styleB', 'text': siType, 'fontSize': 80})
                        spo.GUIOs[f"INDICATORMASTERSWITCH_{siType}"].deactivate()
                        spo.addGUIO(f"TOCONFIGSUBPAGE_{siType}",       button_typeA, {'groupOrder': 0, 'xPos': 4350, 'yPos': yPosPoint1-350-350*i, 'width':  800, 'height': 250, 'style': 'styleA', 'text': ">", 'fontSize': 80, 'name': f'navButton_{siType}', 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
                    yPosPoint2 = yPosPoint1-300-350*len(_SITypes)
                    spo.addGUIO("TITLE_OTHERS", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_OTHERS'), 'fontSize': 80})
                    spo.addGUIO("MINCOMPLETEANALYSISTITLETEXT",   textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint2-350, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_MINCOMPLETEANALYSIS'), 'fontSize': 80, 'textInteractable': False})
                    spo.addGUIO("MINCOMPLETEANALYSISDISPLAYTEXT", textBox_typeA, {'groupOrder': 0, 'xPos': 3150, 'yPos': yPosPoint2-350, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': "-",                                                                                                    'fontSize': 80})
                    spo.addGUIO("NANALYSISDISPLAYTITLETEXT",      textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint2-700, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NANALYSISDISPLAY'),    'fontSize': 80, 'textInteractable': False})
                    spo.addGUIO("NANALYSISDISPLAYDISPLAYTEXT",    textBox_typeA, {'groupOrder': 0, 'xPos': 3150, 'yPos': yPosPoint2-700, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': "-",                                                                                                    'fontSize': 80})
                if (True): #Configuration/SMA
                    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_SMA"]
                    _yPosPoint0 = _yPos_beg-200
                    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0,     'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_SMASETUP'), 'fontSize': 80})
                    spo.addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
                    _yPosPoint1 = _yPosPoint0-650
                    for lineIndex in range (atmEta_Constants.NLINES_SMA):
                        spo.addGUIO(f"SMA_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'SMA {lineIndex}', 'fontSize': 80})
                        spo.GUIOs[f"SMA_{lineIndex}_LINE"].deactivate()
                        spo.addGUIO(f"SMA_{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                  'fontSize': 80})
                    _yPosPoint2 = _yPosPoint1-350*atmEta_Constants.NLINES_SMA
                    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
                if (True): #Configuration/WMA
                    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_WMA"]
                    _yPosPoint0 = _yPos_beg-200
                    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0,     'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_WMASETUP'), 'fontSize': 80})
                    spo.addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
                    _yPosPoint1 = _yPosPoint0-650
                    for lineIndex in range (atmEta_Constants.NLINES_WMA):
                        spo.addGUIO(f"WMA_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'WMA {lineIndex}', 'fontSize': 80})
                        spo.GUIOs[f"WMA_{lineIndex}_LINE"].deactivate()
                        spo.addGUIO(f"WMA_{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                  'fontSize': 80})
                    _yPosPoint2 = _yPosPoint1-350*atmEta_Constants.NLINES_WMA
                    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
                if (True): #Configuration/EMA
                    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_EMA"]
                    _yPosPoint0 = _yPos_beg-200
                    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0,     'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_EMASETUP'), 'fontSize': 80})
                    spo.addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
                    _yPosPoint1 = _yPosPoint0-650
                    for lineIndex in range (atmEta_Constants.NLINES_EMA):
                        spo.addGUIO(f"EMA_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'EMA {lineIndex}', 'fontSize': 80})
                        spo.GUIOs[f"EMA_{lineIndex}_LINE"].deactivate()
                        spo.addGUIO(f"EMA_{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                  'fontSize': 80})
                    _yPosPoint2 = _yPosPoint1-350*atmEta_Constants.NLINES_EMA
                    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
                if (True): #Configuration/PSAR
                    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_PSAR"]
                    _yPosPoint0 = _yPos_beg-200
                    spo.addGUIO("CONFIGPAGETITLE",   passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0,     'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_PSARSETUP'), 'fontSize': 80})
                    spo.addGUIO("COLUMNTITLE_INDEX", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'), 'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("COLUMNTITLE_AF0",   passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1350, 'yPos': _yPosPoint0-300, 'width': 1200, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_AF0'),   'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("COLUMNTITLE_AF+",   passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2650, 'yPos': _yPosPoint0-300, 'width': 1200, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_AF+'),   'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("COLUMNTITLE_AFMAX", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3950, 'yPos': _yPosPoint0-300, 'width': 1200, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_AFMAX'), 'fontSize': 80, 'anchor': 'SW'})
                    _yPosPoint1 = _yPosPoint0-650
                    for lineIndex in range (atmEta_Constants.NLINES_PSAR):
                        spo.addGUIO(f"PSAR_{lineIndex}_LINE",  switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': f'PSAR {lineIndex}', 'fontSize': 80})
                        spo.GUIOs[f"PSAR_{lineIndex}_LINE"].deactivate()
                        spo.addGUIO(f"PSAR_{lineIndex}_AF0",   textBox_typeA, {'groupOrder': 0, 'xPos': 1350, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': "-",                   'fontSize': 80})
                        spo.addGUIO(f"PSAR_{lineIndex}_AF+",   textBox_typeA, {'groupOrder': 0, 'xPos': 2650, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': "-",                   'fontSize': 80})
                        spo.addGUIO(f"PSAR_{lineIndex}_AFMAX", textBox_typeA, {'groupOrder': 0, 'xPos': 3950, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': "-",                   'fontSize': 80})
                    _yPosPoint2 = _yPosPoint1-350*atmEta_Constants.NLINES_PSAR
                    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
                if (True): #Configuration/BOL
                    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_BOL"]
                    _yPosPoint0 = _yPos_beg-200
                    spo.addGUIO("CONFIGPAGETITLE",       passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0,     'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_BOLSETUP'), 'fontSize': 80})
                    spo.addGUIO("BOLMATYPETITLETEXT",    textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-350, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_BOLMATYPE'), 'fontSize': 80})
                    spo.addGUIO("BOLMATYPEDISPLAYTEXT",  textBox_typeA,                {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-350, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                                                                                          'fontSize': 80})
                    spo.addGUIO("COLUMNTITLE_INDEX",     passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-650, 'width': 1650, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),     'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("COLUMNTITLE_NSAMPLES",  passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1750, 'yPos': _yPosPoint0-650, 'width': 1650, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'),  'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("COLUMNTITLE_BANDWIDTH", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': _yPosPoint0-650, 'width': 1650, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_BANDWIDTH'), 'fontSize': 80, 'anchor': 'SW'})
                    _yPosPoint1 = _yPosPoint0-1000
                    for lineIndex in range (atmEta_Constants.NLINES_BOL):
                        spo.addGUIO(f"BOL_{lineIndex}_LINE",      switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1650, 'height': 250, 'style': 'styleB', 'text': f'BOL {lineIndex}', 'fontSize': 80})
                        spo.GUIOs[f"BOL_{lineIndex}_LINE"].deactivate()
                        spo.addGUIO(f"BOL_{lineIndex}_NSAMPLES",  textBox_typeA, {'groupOrder': 0, 'xPos': 1750, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1650, 'height': 250, 'style': 'styleA', 'text': "-",                  'fontSize': 80})
                        spo.addGUIO(f"BOL_{lineIndex}_BANDWIDTH", textBox_typeA, {'groupOrder': 0, 'xPos': 3500, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1650, 'height': 250, 'style': 'styleA', 'text': "-",                  'fontSize': 80})
                    _yPosPoint2 = _yPosPoint1-350*atmEta_Constants.NLINES_BOL
                    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
                if (True): #Configuration/IVP
                    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_IVP"]
                    _yPosPoint0 = _yPos_beg-200
                    spo.addGUIO("CONFIGPAGETITLE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_IVPSETUP'), 'fontSize': 80})
                    spo.addGUIO("NSAMPLESTITLETEXT",      textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0- 350, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80})
                    spo.addGUIO("NSAMPLESDISPLAYTEXT",    textBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': _yPosPoint0- 350, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
                    spo.addGUIO("GAMMAFACTORTITLETEXT",   textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0- 700, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_GAMMAFACTOR'), 'fontSize': 80})
                    spo.addGUIO("GAMMAFACTORDISPLAYTEXT", textBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': _yPosPoint0- 700, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
                    spo.addGUIO("DELTAFACTORTITLETEXT",   textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-1050, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_DELTAFACTOR'), 'fontSize': 80})
                    spo.addGUIO("DELTAFACTORDISPLAYTEXT", textBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': _yPosPoint0-1050, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
                    _yPosPoint1 = _yPosPoint0-1400
                    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint1, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
                if (True): #Configuration/SWING
                    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_SWING"]
                    _yPosPoint0 = _yPos_beg-200
                    spo.addGUIO("CONFIGPAGETITLE",        passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0,     'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_SWINGSETUP'), 'fontSize': 80})
                    spo.addGUIO("COLUMNTITLE_INDEX",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),      'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("COLUMNTITLE_SWINGRANGE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1350, 'yPos': _yPosPoint0-300, 'width': 3800, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_SWINGRANGE'), 'fontSize': 80, 'anchor': 'SW'})
                    _yPosPoint1 = _yPosPoint0-650
                    for lineIndex in range (atmEta_Constants.NLINES_SWING):
                        spo.addGUIO(f"SWING_{lineIndex}_LINE",       switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': f'SWING {lineIndex}', 'fontSize': 80})
                        spo.GUIOs[f"SWING_{lineIndex}_LINE"].deactivate()
                        spo.addGUIO(f"SWING_{lineIndex}_SWINGRANGE", textBox_typeA, {'groupOrder': 0, 'xPos': 1350, 'yPos': _yPosPoint1-350*lineIndex, 'width': 3800, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
                    _yPosPoint2 = _yPosPoint1-350*atmEta_Constants.NLINES_SWING
                    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
                if (True): #Configuration/VOL
                    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_VOL"]
                    _yPosPoint0 = _yPos_beg-200
                    spo.addGUIO("CONFIGPAGETITLE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_VOLSETUP'), 'fontSize': 80})
                    spo.addGUIO("MATYPETITLETEXT",      textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-350, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_VOLMATYPE'),  'fontSize': 80})
                    spo.addGUIO("MATYPEDISPLAYTEXT",    textBox_typeA,                {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-350, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                                                                                           'fontSize': 80})
                    spo.addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-650, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),      'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-650, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'),   'fontSize': 80, 'anchor': 'SW'})
                    _yPosPoint1 = _yPosPoint0-1000
                    for lineIndex in range (atmEta_Constants.NLINES_VOL):
                        spo.addGUIO(f"VOL_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'VOL {lineIndex}', 'fontSize': 80})
                        spo.GUIOs[f"VOL_{lineIndex}_LINE"].deactivate()
                        spo.addGUIO(f"VOL_{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                  'fontSize': 80})
                    _yPosPoint2 = _yPosPoint1-350*atmEta_Constants.NLINES_VOL
                    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
                if (True): #Configuration/NNA
                    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_NNA"]
                    _yPosPoint0 = _yPos_beg-200
                    spo.addGUIO("CONFIGPAGETITLE",        passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_NNASETUP'), 'fontSize': 80})
                    spo.addGUIO("COLUMNTITLE_INDEX",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),             'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("COLUMNTITLE_SWINGRANGE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1350, 'yPos': _yPosPoint0-300, 'width': 2600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NEURALNETWORKCODE'), 'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("COLUMNTITLE_ALPHA",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 4050, 'yPos': _yPosPoint0-300, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_ALPHA'),             'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("COLUMNTITLE_BETA",       passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 4650, 'yPos': _yPosPoint0-300, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_BETA'),              'fontSize': 80, 'anchor': 'SW'})
                    _yPosPoint1 = _yPosPoint0-650
                    for lineIndex in range (atmEta_Constants.NLINES_NNA):
                        spo.addGUIO(f"NNA_{lineIndex}_LINE",   switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': f'NNA {lineIndex}', 'fontSize': 80})
                        spo.GUIOs[f"NNA_{lineIndex}_LINE"].deactivate()
                        spo.addGUIO(f"NNA_{lineIndex}_NNCODE", textBox_typeA, {'groupOrder': 0, 'xPos': 1350, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2600, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
                        spo.addGUIO(f"NNA_{lineIndex}_ALPHA",  textBox_typeA, {'groupOrder': 0, 'xPos': 4050, 'yPos': _yPosPoint1-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
                        spo.addGUIO(f"NNA_{lineIndex}_BETA",   textBox_typeA, {'groupOrder': 0, 'xPos': 4650, 'yPos': _yPosPoint1-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
                    _yPosPoint2 = _yPosPoint1-350*atmEta_Constants.NLINES_NNA
                    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
                if (True): #Configuration/MMACDSHORT
                    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MMACDSHORT"]
                    _yPosPoint0 = _yPos_beg-200
                    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_MMACDSHORTSETUP'), 'fontSize': 80})
                    spo.addGUIO("MMACDSIGNALINTERVALTITLETEXT",   textBox_typeA,       {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0- 350, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_MMACDSIGNALINTERVAL'), 'fontSize': 80})
                    spo.addGUIO("MMACDSIGNALINTERVALDISPLAYTEXT", textBox_typeA,       {'groupOrder': 0, 'xPos': 3150, 'yPos': _yPosPoint0- 350, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': "-",                                                                                                    'fontSize': 80})
                    spo.addGUIO("MULTIPLIERTITLETEXT",            textBox_typeA,       {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0- 700, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_MULTIPLIER'),          'fontSize': 80})
                    spo.addGUIO("MULTIPLIERDISPLAYTEXT",          textBox_typeA,       {'groupOrder': 0, 'xPos': 3150, 'yPos': _yPosPoint0- 700, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': "-",                                                                                                    'fontSize': 80})
                    spo.addGUIO("INDEX_COLUMNTITLE1",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-1000, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("NSAMPLES_COLUMNTITLE1", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1200, 'yPos': _yPosPoint0-1000, 'width': 1325, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("INDEX_COLUMNTITLE2",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-1000, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("NSAMPLES_COLUMNTITLE2", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3825, 'yPos': _yPosPoint0-1000, 'width': 1325, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
                    _nMaxLines = atmEta_Constants.NLINES_MMACDSHORT
                    for lineIndex in range (_nMaxLines):
                        rowNumber = math.ceil((lineIndex+1)/2)
                        if (lineIndex%2 == 0): coordX = 0
                        else:                  coordX = 2625
                        spo.addGUIO(f"MA{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos': coordX,      'yPos': _yPosPoint0-1000-rowNumber*350, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': f'MA {lineIndex}', 'fontSize': 80})
                        spo.GUIOs[f"MA{lineIndex}_LINE"].deactivate()
                        spo.addGUIO(f"MA{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': coordX+1200, 'yPos': _yPosPoint0-1000-rowNumber*350, 'width': 1325, 'height': 250, 'style': 'styleA', 'text': "-",                 'fontSize': 80})
                    _yPosPoint1 = _yPosPoint0-1000-math.ceil(_nMaxLines/2)*350
                    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint1-350, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
                if (True): #Configuration/MMACDLONG
                    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MMACDLONG"]
                    _yPosPoint0 = _yPos_beg-200
                    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_MMACDLONGSETUP'), 'fontSize': 80})
                    spo.addGUIO("MMACDSIGNALINTERVALTITLETEXT",   textBox_typeA,       {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0- 350, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_MMACDSIGNALINTERVAL'), 'fontSize': 80})
                    spo.addGUIO("MMACDSIGNALINTERVALDISPLAYTEXT", textBox_typeA,       {'groupOrder': 0, 'xPos': 3150, 'yPos': _yPosPoint0- 350, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': "-",                                                                                                    'fontSize': 80})
                    spo.addGUIO("MULTIPLIERTITLETEXT",            textBox_typeA,       {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0- 700, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_MULTIPLIER'),          'fontSize': 80})
                    spo.addGUIO("MULTIPLIERDISPLAYTEXT",          textBox_typeA,       {'groupOrder': 0, 'xPos': 3150, 'yPos': _yPosPoint0- 700, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': "-",                                                                                                    'fontSize': 80})
                    spo.addGUIO("INDEX_COLUMNTITLE1",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-1000, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("NSAMPLES_COLUMNTITLE1", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1200, 'yPos': _yPosPoint0-1000, 'width': 1325, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("INDEX_COLUMNTITLE2",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-1000, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("NSAMPLES_COLUMNTITLE2", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3825, 'yPos': _yPosPoint0-1000, 'width': 1325, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
                    _nMaxLines = atmEta_Constants.NLINES_MMACDLONG
                    for lineIndex in range (_nMaxLines):
                        rowNumber = math.ceil((lineIndex+1)/2)
                        if (lineIndex%2 == 0): coordX = 0
                        else:                  coordX = 2625
                        spo.addGUIO(f"MA{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos': coordX,      'yPos': _yPosPoint0-1000-rowNumber*350, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': f'MA {lineIndex}', 'fontSize': 80})
                        spo.GUIOs[f"MA{lineIndex}_LINE"].deactivate()
                        spo.addGUIO(f"MA{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': coordX+1200, 'yPos': _yPosPoint0-1000-rowNumber*350, 'width': 1325, 'height': 250, 'style': 'styleA', 'text': "-",                 'fontSize': 80})
                    _yPosPoint1 = _yPosPoint0-1000-math.ceil(_nMaxLines/2)*350
                    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint1-350, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
                if (True): #Configuration/DMIxADX
                    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_DMIxADX"]
                    _yPosPoint0 = _yPos_beg-200
                    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_DMIxADXSETUP'), 'fontSize': 80})
                    spo.addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
                    _yPosPoint1 = _yPosPoint0-650
                    for lineIndex in range (atmEta_Constants.NLINES_DMIxADX):
                        spo.addGUIO(f"DMIxADX_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'DMIxADX {lineIndex}', 'fontSize': 80})
                        spo.GUIOs[f"DMIxADX_{lineIndex}_LINE"].deactivate()
                        spo.addGUIO(f"DMIxADX_{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                      'fontSize': 80})
                    _yPosPoint2 = _yPosPoint1-350*atmEta_Constants.NLINES_DMIxADX
                    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
                if (True): #Configuration/MFI
                    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MFI"]
                    _yPosPoint0 = _yPos_beg-200
                    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_MFISETUP'), 'fontSize': 80})
                    spo.addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
                    spo.addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
                    _yPosPoint1 = _yPosPoint0-650
                    for lineIndex in range (atmEta_Constants.NLINES_MFI):
                        spo.addGUIO(f"MFI_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'MFI {lineIndex}', 'fontSize': 80})
                        spo.GUIOs[f"MFI_{lineIndex}_LINE"].deactivate()
                        spo.addGUIO(f"MFI_{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                  'fontSize': 80})
                    _yPosPoint2 = _yPosPoint1-350*atmEta_Constants.NLINES_MFI
                    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
            #Trade Configurations
            self.GUIOs["BLOCKTITLE_SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIGURATIONS"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=10600, yPos=7700, width=5300, height=200, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKTITLE_SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIGURATIONS'), fontSize=80)
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIURATIONTITLETEXT"]     = textBox_typeA(**inst,      groupOrder=1, xPos=10600, yPos=7350, width=1000, height= 250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIGURATIONCODE'), fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIURATIONSELECTIONBOX"]  = selectionBox_typeB(**inst, groupOrder=2, xPos=11700, yPos=7350, width=3300, height= 250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIGURATION'])
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_NTRADECONFIURATIONSDISPLAYTEXT"] = textBox_typeA(**inst,      groupOrder=1, xPos=15100, yPos=7350, width= 800, height= 250, style="styleA", text="-", fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIGURATIONSUBPAGE"]      = subPageBox_typeA(**inst,   groupOrder=1, xPos=10600, yPos= 100, width=5300, height=7150, style=None, useScrollBar_V=True, useScrollBar_H=False)
            if (True):
                _yPos_beg = 20000
                _subPageViewSpaceWidth = self.GUIOs["BLOCKTITLE_SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIGURATIONS"].width-150
                spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIGURATIONSUBPAGE"]
                #Base
                spo.addGUIO("LEVERAGETITLETEXT",                textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPos_beg- 250, 'width': 3950, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_LEVERAGE'),              'fontSize': 80, 'textInteractable': False})
                spo.addGUIO("LEVERAGEDISPLAYTEXT",              textBox_typeA, {'groupOrder': 0, 'xPos': 4050, 'yPos': _yPos_beg- 250, 'width': 1100, 'height': 250, 'style': 'styleA', 'text': "-",                                                                                                      'fontSize': 80, 'textInteractable': False})
                spo.addGUIO("MARGINTYPETITLETEXT",              textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPos_beg- 600, 'width': 3950, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_MARGINTYPE'),            'fontSize': 80, 'textInteractable': False})
                spo.addGUIO("MARGINTYPEDISPLAYTEXT",            textBox_typeA, {'groupOrder': 0, 'xPos': 4050, 'yPos': _yPos_beg- 600, 'width': 1100, 'height': 250, 'style': 'styleA', 'text': "-",                                                                                                      'fontSize': 80, 'textInteractable': False})
                spo.addGUIO("DIRECTIONTITLETEXT",               textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPos_beg- 950, 'width': 3950, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_DIRECTION'),             'fontSize': 80, 'textInteractable': False})
                spo.addGUIO("DIRECTIONDISPLAYTEXT",             textBox_typeA, {'groupOrder': 0, 'xPos': 4050, 'yPos': _yPos_beg- 950, 'width': 1100, 'height': 250, 'style': 'styleA', 'text': "-",                                                                                                      'fontSize': 80, 'textInteractable': False})
                spo.addGUIO("FULLSTOPLOSSIMMEDIATETITLETEXT",   textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPos_beg-1300, 'width': 1325, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_FULLSTOPLOSSIMMEDIATE'), 'fontSize': 80, 'textInteractable': False})
                spo.addGUIO("FULLSTOPLOSSIMMEDIATEDISPLAYTEXT", textBox_typeA, {'groupOrder': 0, 'xPos': 1425, 'yPos': _yPos_beg-1300, 'width': 1100, 'height': 250, 'style': 'styleA', 'text': "-",                                                                                                      'fontSize': 80, 'textInteractable': False})
                spo.addGUIO("FULLSTOPLOSSCLOSETITLETEXT",       textBox_typeA, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPos_beg-1300, 'width': 1325, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_FULLSTOPLOSSIMMEDIATE'), 'fontSize': 80, 'textInteractable': False})
                spo.addGUIO("FULLSTOPLOSSCLOSEDISPLAYTEXT",     textBox_typeA, {'groupOrder': 0, 'xPos': 4050, 'yPos': _yPos_beg-1300, 'width': 1100, 'height': 250, 'style': 'styleA', 'text': "-",                                                                                                      'fontSize': 80, 'textInteractable': False})
                spo.addGUIO("POSTSTOPLOSSREENTRYTITLETEXT",     textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPos_beg-1650, 'width': 4550, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_POSTSTOPLOSSREENTRY'),   'fontSize': 80, 'textInteractable': False})
                spo.addGUIO("POSTSTOPLOSSREENTRYSWITCH",        switch_typeB,  {'groupOrder': 0, 'xPos': 4650, 'yPos': _yPos_beg-1650, 'width':  500, 'height': 250, 'style': 'styleA', 'align': 'horizontal'})
                #RQPM
                spo.addGUIO("RQPM_FUNCTIONTYPETITLETEXT",       textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPos_beg-2000, 'width': 1425, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_RQPM_FUNCTIONTYPE'),     'fontSize': 80, 'textInteractable': False})
                spo.addGUIO("RQPM_FUNCTIONTYPEDISPLAYTEXT",     textBox_typeA, {'groupOrder': 0, 'xPos': 1525, 'yPos': _yPos_beg-2000, 'width': 3625, 'height': 250, 'style': 'styleA', 'text': "-",                                                                                                      'fontSize': 80, 'textInteractable': False})
                spo.addGUIO("RQPM_PARAMETERSSELECTIONBOX", selectionBox_typeC, {'groupOrder': 2, 'xPos':    0, 'yPos': _yPos_beg-7150, 'width': _subPageViewSpaceWidth, 'height': 5050, 'style': 'styleA', 'fontSize': 80, 'elementHeight': 250, 'multiSelect': False, 'singularSelect_allowRelease': True,
                                                                                                 'elementWidths': (1000, 1950, 1950)})
                spo.GUIOs["RQPM_PARAMETERSSELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_RQPM_PARAMETER_INDEX')},
                                                                                          {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_RQPM_PARAMETER_NAME')},
                                                                                          {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_RQPM_PARAMETER_VALUE')}])
            self.puVar['GUIOGROUPS']['CONFIGURATIONS'] = ["BLOCKTITLE_SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONS",
                                                          "SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIURATIONTITLETEXT",
                                                          "SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIURATIONSELECTIONBOX",
                                                          "SIMULATIONDETAIL_CONFIGURATIONS_NCURRENCYANALYSISCONFIURATIONSDISPLAYTEXT",
                                                          "BLOCKTITLE_SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIGURATIONS",
                                                          "SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIURATIONTITLETEXT",
                                                          "SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIURATIONSELECTIONBOX",
                                                          "SIMULATIONDETAIL_CONFIGURATIONS_NTRADECONFIURATIONSDISPLAYTEXT",
                                                          "SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIGURATIONSUBPAGE"]
            for _cacSubPageName in _currenyAnalysisConfigurationSubPageNames: self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_{:s}".format(_cacSubPageName)].hide()
        for _guioName in self.puVar['GUIOGROUPS']['CONFIGURATIONS']: self.GUIOs[_guioName].hide()
        #---Trade Logs
        if (True):
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NETPROFITTITLETEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos= 5200, yPos=7650, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_NETPROFIT'),   fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NETPROFITDISPLAYTEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos= 6300, yPos=7650, width=1500, height=250, style="styleA", text="-",                                                                                       fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_GAINTITLETEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos= 7900, yPos=7650, width= 800, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_GAIN'),        fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_GAINDISPLAYTEXT"]           = textBox_typeA(**inst,      groupOrder=1, xPos= 8800, yPos=7650, width=1700, height=250, style="styleA", text="-",                                                                                       fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_LOSSTITLETEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos=10600, yPos=7650, width= 800, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_LOSS'),        fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_LOSSDISPLAYTEXT"]           = textBox_typeA(**inst,      groupOrder=1, xPos=11500, yPos=7650, width=1700, height=250, style="styleA", text="-",                                                                                       fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TRADINGFEETITLETEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos=13300, yPos=7650, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_TRADINGFEE'),  fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TRADINGFEEDISPLAYTEXT"]     = textBox_typeA(**inst,      groupOrder=1, xPos=14400, yPos=7650, width=1500, height=250, style="styleA", text="-",                                                                                       fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NTOTALLOGSTITLETEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos= 5200, yPos=7300, width=1400, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_TOTAL'),       fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NTOTALLOGSDISPLAYTEXT"]     = textBox_typeA(**inst,      groupOrder=1, xPos= 6700, yPos=7300, width=2000, height=250, style="styleA", text="- / -",                                                                                   fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NASSETLOGSTITLETEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos= 8800, yPos=7300, width=1400, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ASSET'),       fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NASSETLOGSDISPLAYTEXT"]     = textBox_typeA(**inst,      groupOrder=1, xPos=10300, yPos=7300, width=2000, height=250, style="styleA", text="- / -",                                                                                   fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NPOSITIONLOGSTITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos=12400, yPos=7300, width=1400, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_POSITION'),    fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NPOSITIONLOGSDISPLAYTEXT"]  = textBox_typeA(**inst,      groupOrder=1, xPos=13900, yPos=7300, width=2000, height=250, style="styleA", text="- / -",                                                                                   fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TIMEFILTERTITLETEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos= 5200, yPos=6950, width=1400, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_TIMEUTC'),     fontSize=80, textInteractable=False)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TIMEFILTERINPUTTEXT1"]      = textInputBox_typeA(**inst, groupOrder=1, xPos= 6700, yPos=6950, width=2750, height=250, style="styleA", text="",                                                                                        fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_SIMULATIONDETAIL_TRADELOGS_TIMEFILTER'])
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TIMEFILTERINPUTTEXT2"]      = textInputBox_typeA(**inst, groupOrder=1, xPos= 9550, yPos=6950, width=2750, height=250, style="styleA", text="",                                                                                        fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_SIMULATIONDETAIL_TRADELOGS_TIMEFILTER'])
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TIMEFILTERAPPLYBUTTON"]     = button_typeA(**inst,       groupOrder=1, xPos=12400, yPos=6950, width=1400, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_SEARCH'),      fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_TRADELOGS_TIMEFILTER'])
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TIMEFILTERAPPLYBUTTON"].deactivate()
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NTIMELOGSDISPLAYTEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos=13900, yPos=6950, width=2000, height=250, style="styleA", text="- / -",                                                                                   fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_SIDEFILTERBUY"]             = switch_typeC(**inst,       groupOrder=1, xPos= 5200, yPos=6600, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_BUY'),         switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_SIMULATIONDETAIL_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NBUYDISPLAYTEXT"]           = textBox_typeA(**inst,      groupOrder=1, xPos= 6300, yPos=6600, width=1500, height=250, style="styleA", text="- / -",                                                                                   fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_SIDEFILTERSELL"]            = switch_typeC(**inst,       groupOrder=1, xPos= 7900, yPos=6600, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_SELL'),        switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_SIMULATIONDETAIL_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NSELLDISPLAYTEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos= 9000, yPos=6600, width=1500, height=250, style="styleA", text="- / -",                                                                                   fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_LOGICSOURCEFILTERFSLIMMED"] = switch_typeC(**inst,       groupOrder=1, xPos=10600, yPos=6600, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_FSLIMMED'),    switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_SIMULATIONDETAIL_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NFSLIMMEDDISPLAYTEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos=11700, yPos=6600, width=1500, height=250, style="styleA", text="- / -",                                                                                   fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_LOGICSOURCEFILTERFSLCLOSE"] = switch_typeC(**inst,       groupOrder=1, xPos=13300, yPos=6600, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_FSLCLOSE'),    switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_SIMULATIONDETAIL_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NFSLCLOSEDISPLAYTEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos=14400, yPos=6600, width=1500, height=250, style="styleA", text="- / -",                                                                                   fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_LOGICSOURCEFILTERENTRY"]    = switch_typeC(**inst,       groupOrder=1, xPos= 5200, yPos=6250, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ENTRY'),       switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_SIMULATIONDETAIL_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NENTRYDISPLAYTEXT"]         = textBox_typeA(**inst,      groupOrder=1, xPos= 6300, yPos=6250, width=1500, height=250, style="styleA", text="- / -",                                                                                   fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_LOGICSOURCEFILTERCLEAR"]    = switch_typeC(**inst,       groupOrder=1, xPos= 7900, yPos=6250, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_CLEAR'),       switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_SIMULATIONDETAIL_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NCLEARDISPLAYTEXT"]         = textBox_typeA(**inst,      groupOrder=1, xPos= 9000, yPos=6250, width=1500, height=250, style="styleA", text="- / -",                                                                                   fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_LOGICSOURCEFILTEREXIT"]     = switch_typeC(**inst,       groupOrder=1, xPos=10600, yPos=6250, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_EXIT'),        switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_SIMULATIONDETAIL_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NEXITDISPLAYTEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos=11700, yPos=6250, width=1500, height=250, style="styleA", text="- / -",                                                                                   fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_SIDEFILTERLIQUIDATION"]     = switch_typeC(**inst,       groupOrder=1, xPos=13300, yPos=6250, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_LIQUIDATION'), switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_SIMULATIONDETAIL_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NLIQUIDATIONDISPLAYTEXT"]   = textBox_typeA(**inst,      groupOrder=1, xPos=14400, yPos=6250, width=1500, height=250, style="styleA", text="- / -",                                                                                   fontSize=80, textInteractable=True)
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TRADELOGSELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=2, xPos=5200, yPos=100, width=10700, height=6050, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_TRADELOGS_TRADELOG'], 
                                                                                               elementWidths = (900, 1000, 1200, 700, 700, 750, 800, 850, 850, 750, 800, 1150)) #10450
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TRADELOGSELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_INDEX')},          # 900
                                                                                                           {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_TIME')},           #1000
                                                                                                           {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_SYMBOL')},         #1200
                                                                                                           {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_LOGICSOURCE')},    # 700
                                                                                                           {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_SIDE')},           # 700
                                                                                                           {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_QUANTITY')},       # 750
                                                                                                           {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_PRICE')},          # 800
                                                                                                           {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_PROFIT')},         # 850
                                                                                                           {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_TRADINGFEE')},     # 850
                                                                                                           {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_TOTALQUANTITY')},  # 750
                                                                                                           {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_ENTRYPRICE')},     # 800
                                                                                                           {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_WALLETBALANCE')}]) #1150
            #Grouping
            self.puVar['GUIOGROUPS']['TRADELOGS'] = ["SIMULATIONDETAIL_TRADELOGS_NETPROFITTITLETEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_NETPROFITDISPLAYTEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_GAINTITLETEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_GAINDISPLAYTEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_LOSSTITLETEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_LOSSDISPLAYTEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_TRADINGFEETITLETEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_TRADINGFEEDISPLAYTEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_NTOTALLOGSTITLETEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_NTOTALLOGSDISPLAYTEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_NASSETLOGSTITLETEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_NASSETLOGSDISPLAYTEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_NPOSITIONLOGSTITLETEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_NPOSITIONLOGSDISPLAYTEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_TIMEFILTERTITLETEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_TIMEFILTERINPUTTEXT1",
                                                     "SIMULATIONDETAIL_TRADELOGS_TIMEFILTERINPUTTEXT2",
                                                     "SIMULATIONDETAIL_TRADELOGS_TIMEFILTERAPPLYBUTTON",
                                                     "SIMULATIONDETAIL_TRADELOGS_NTIMELOGSDISPLAYTEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_SIDEFILTERBUY",
                                                     "SIMULATIONDETAIL_TRADELOGS_NBUYDISPLAYTEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_SIDEFILTERSELL",
                                                     "SIMULATIONDETAIL_TRADELOGS_NSELLDISPLAYTEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_SIDEFILTERLIQUIDATION",
                                                     "SIMULATIONDETAIL_TRADELOGS_NLIQUIDATIONDISPLAYTEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_LOGICSOURCEFILTERFSLIMMED",
                                                     "SIMULATIONDETAIL_TRADELOGS_NFSLIMMEDDISPLAYTEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_LOGICSOURCEFILTERFSLCLOSE",
                                                     "SIMULATIONDETAIL_TRADELOGS_NFSLCLOSEDISPLAYTEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_LOGICSOURCEFILTERENTRY",
                                                     "SIMULATIONDETAIL_TRADELOGS_NENTRYDISPLAYTEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_LOGICSOURCEFILTERCLEAR",
                                                     "SIMULATIONDETAIL_TRADELOGS_NCLEARDISPLAYTEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_LOGICSOURCEFILTEREXIT",
                                                     "SIMULATIONDETAIL_TRADELOGS_NEXITDISPLAYTEXT",
                                                     "SIMULATIONDETAIL_TRADELOGS_TRADELOGSELECTIONBOX"]
        for _guioName in self.puVar['GUIOGROUPS']['TRADELOGS']: self.GUIOs[_guioName].hide()
        #---Daily Reports
        if (True):
            self.GUIOs["SIMULATIONDETAIL_DAILYREPORT_DAILYREPORTVIEWER"] = dailyReportViewer(**inst, groupOrder=1, xPos=5200, yPos=100, width=10700, height=7800, style="styleA", name = 'SIMULATIONRESULT_SIMULATIONDETAIL_POSITIONCHART_DAILYREPORTVIEWER')
            #Grouping
            self.puVar['GUIOGROUPS']['DAILYREPORTS'] = ["SIMULATIONDETAIL_DAILYREPORT_DAILYREPORTVIEWER",]
        for _guioName in self.puVar['GUIOGROUPS']['DAILYREPORTS']: self.GUIOs[_guioName].hide()
        #---Position Chart
        if (True):
            self.GUIOs["SIMULATIONDETAIL_POSITIONCHART_CHARTDRAWER"] = chartDrawer(**inst, groupOrder=1, xPos=5200, yPos=100, width=10700, height=7800, style="styleA", name = 'SIMULATIONRESULT_SIMULATIONDETAIL_POSITIONCHART_CHARTDRAWER', chartDrawerType = 'TLVIEWER')
            #Grouping
            self.puVar['GUIOGROUPS']['POSITIONCHART'] = ["SIMULATIONDETAIL_POSITIONCHART_CHARTDRAWER",]
        for _guioName in self.puVar['GUIOGROUPS']['POSITIONCHART']: self.GUIOs[_guioName].hide()
    elif (self.displaySpaceDefiner['ratio'] == '21:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 21000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
    elif (self.displaySpaceDefiner['ratio'] == '32:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 32000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
#SETUP PAGE <MAIN> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <LOAD> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageLoadFunction(self):
    #FAR Registration
    #---SIMULATIONMANAGER
    self.ipcA.addFARHandler('onSimulationUpdate', self.pageAuxillaryFunctions['_FAR_ONSIMULATIONUPDATE'], executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)

    #Get data via PRD
    _simulations_PAGE = self.puVar['simulations']
    _simulations_PRD  = self.ipcA.getPRD(processName = 'SIMULATIONMANAGER', prdAddress = 'SIMULATIONS')
    _simulationListUpdated      = False
    _simulationSelectionUpdated = False
    for _simCode in _simulations_PRD:
        _simulation_PRD = _simulations_PRD[_simCode]
        if (_simulation_PRD['_status'] == 'COMPLETED'):
            if (_simCode in _simulations_PAGE):
                if (_simulation_PRD['creationTime'] != _simulations_PAGE[_simCode]['creationTime']): 
                    _simulations_PAGE[_simCode] = _simulation_PRD.copy()
                    _simulationListUpdated = True
                    if (self.puVar['simulation_selected'] == _simCode): _simulationSelectionUpdated = True
            else: 
                _simulations_PAGE[_simCode] = _simulation_PRD.copy()
                _simulationListUpdated = True
        else:
            if (_simCode in _simulations_PAGE): 
                del _simulations_PAGE[_simCode]
                _simulationListUpdated = True
                if (self.puVar['simulation_selected'] == _simCode): _simulationSelectionUpdated = True
    _simCodesToRemove = [_simCode for _simCode in _simulations_PAGE if (_simCode not in _simulations_PRD)]
    for _simCode in _simCodesToRemove:
        del _simulations_PAGE[_simCode]
        _simulationListUpdated = True
        if (self.puVar['simulation_selected'] == _simCode): _simulationSelectionUpdated = True
    if (_simulationListUpdated == True): self.pageAuxillaryFunctions['SETSIMULATIONSLIST']()
    if (_simulationSelectionUpdated == True):
        if (self.puVar['simulation_selected'] not in _simulations_PAGE): self.puVar['simulation_selected'] = None
        self.pageAuxillaryFunctions['ONSIMULATIONSELECTIONUPDATE']()

    #Simulation Result Load
    if (self.puVar['simulation_toLoad'] != None):
        if ((self.puVar['simulation_toLoad'] in self.puVar['simulations']) and (self.puVar['simulation_toLoad'] != self.puVar['simulation_selected'])):
            self.GUIOs["SIMULATIONS_SELECTIONBOX"].clearSelected()
            self.GUIOs["SIMULATIONS_SELECTIONBOX"].addSelected(itemKey = self.puVar['simulation_toLoad'], callSelectionUpdateFunction = True)
        self.puVar['simulation_toLoad'] = None
#SETUP PAGE <LOAD> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <ESCAPE> --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageEscapeFunction(self):
    self.ipcA.removeFARHandler('onSimulationUpdate')
#SETUP PAGE <ESCAPE> END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <PROCESS> -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageProcessFunction(self, t_elapsed_ns, onLoad = False):
    pass
#SETUP PAGE <PROCESS> END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#OBJECT FUNCTIONS -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateObjectFunctions(self):
    objFunctions = dict()

    #<Page Navigation>
    def __pageMove_DASHBOARD(objInstance, **kwargs): 
        self.sysFunctions['LOADPAGE']('DASHBOARD')
    objFunctions['PAGEMOVE_DASHBOARD'] = __pageMove_DASHBOARD

    #<Simulations>
    def __onTextUpdate_Simulations_SearchText(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONSIMULATIONSFILTERUPDATE']()
    def __onSelectionUpdate_Simulations_SortTypeSelection(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONSIMULATIONSFILTERUPDATE']()
    def __onSelectionUpdate_Simulations_Simulation(objInstance, **kwargs):
        try:    self.puVar['simulation_selected'] = self.GUIOs["SIMULATIONS_SELECTIONBOX"].getSelected()[0]
        except: self.puVar['simulation_selected'] = None
        self.pageAuxillaryFunctions['ONSIMULATIONSELECTIONUPDATE']()
    objFunctions['ONTEXTUPDATE_SIMULATIONS_SEARCHTEXT']             = __onTextUpdate_Simulations_SearchText
    objFunctions['ONSELECTIONUPDATE_SIMULATIONS_SORTTYPESELECTION'] = __onSelectionUpdate_Simulations_SortTypeSelection
    objFunctions['ONSELECTIONUPDATE_SIMULATIONS_SIMULATION']        = __onSelectionUpdate_Simulations_Simulation

    #<Result Summary>
    def __onSelectionUpdate_ResultSummary_Asset(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONASSETSELECTIONUPDATE_RESULTSUMMARY']()
    objFunctions['ONSELECTIONUPDATE_RESULTSUMMARY_ASSET'] = __onSelectionUpdate_ResultSummary_Asset

    #<Simulation Detail>
    def __onSelectionUpdate_SimulationDetail_View(objInstance, **kwargs):
        _view_prev = self.puVar['simulationDetailView_selected']
        self.puVar['simulationDetailView_selected'] = self.GUIOs["SIMULATIONDETAIL_VIEWSELECTIONBOX"].getSelected()
        self.pageAuxillaryFunctions['ONSIMULATIONVIEWUPDATE'](view_prev = _view_prev)
    def __onSelectionUpdate_SimulationDetail_Asset(objInstance, **kwargs):
        _assetName_selected = self.GUIOs["SIMULATIONDETAIL_ASSETSELECTIONBOX"].getSelected()
        _view_selected = self.GUIOs["SIMULATIONDETAIL_VIEWSELECTIONBOX"].getSelected()
        self.puVar['simulationDetailView_selectionPair'][_view_selected][0] = _assetName_selected
        if   (_assetName_selected == '#ALL#'): self.GUIOs["SIMULATIONDETAIL_ASSETIMAGEBOX"].updateImage(image = "assetTotalIcon_512x512.png")
        elif (_assetName_selected == 'USDT'):  self.GUIOs["SIMULATIONDETAIL_ASSETIMAGEBOX"].updateImage(image = "usdtIcon_512x512.png")
        elif (_assetName_selected == 'USDC'):  self.GUIOs["SIMULATIONDETAIL_ASSETIMAGEBOX"].updateImage(image = "usdcIcon_512x512.png")
        self.pageAuxillaryFunctions['SETPOSITIONSLIST']()
        self.pageAuxillaryFunctions['ONASSETPOSITIONUPDATE_SIMULATIONDETAIL']()
    def __onSelectionUpdate_SimulationDetail_Position(objInstance, **kwargs):
        _positionSymbol_selected = self.GUIOs["SIMULATIONDETAIL_POSITIONSELECTIONBOX"].getSelected()
        _view_selected = self.GUIOs["SIMULATIONDETAIL_VIEWSELECTIONBOX"].getSelected()
        self.puVar['simulationDetailView_selectionPair'][_view_selected][1] = _positionSymbol_selected
        self.pageAuxillaryFunctions['ONASSETPOSITIONUPDATE_SIMULATIONDETAIL']()
    objFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_VIEW']     = __onSelectionUpdate_SimulationDetail_View
    objFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_ASSET']    = __onSelectionUpdate_SimulationDetail_Asset
    objFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_POSITION'] = __onSelectionUpdate_SimulationDetail_Position
    #---Asset & Position Setup
    #------Positions
    def __onTextUpdate_SimulationDetail_AssetPositionSetup_Positions_SearchText(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONPOSITIONSFILTERUPDATE_ASSETPOSITIONSETUP']()
    def __onSelectionUpdate_SimulationDetail_AssetPositionSetup_Positions_SearchType(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONPOSITIONSFILTERUPDATE_ASSETPOSITIONSETUP']()
    def __onSelectionUpdate_SimulationDetail_AssetPositionSetup_Positions_SortType(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONPOSITIONSFILTERUPDATE_ASSETPOSITIONSETUP']()
    def __onSelectionUpdate_SimulationDetail_AssetPositionSetup_Positions_TradableFilter(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONPOSITIONSFILTERUPDATE_ASSETPOSITIONSETUP']()
    objFunctions['ONTEXTUPDATE_SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCHTEXT']          = __onTextUpdate_SimulationDetail_AssetPositionSetup_Positions_SearchText
    objFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCHTYPE']     = __onSelectionUpdate_SimulationDetail_AssetPositionSetup_Positions_SearchType
    objFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTTYPE']       = __onSelectionUpdate_SimulationDetail_AssetPositionSetup_Positions_SortType
    objFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_TRADABLEFILTER'] = __onSelectionUpdate_SimulationDetail_AssetPositionSetup_Positions_TradableFilter
    #------Assets
    def __onSelectionUpdate_SimulationDetail_AssetPositionSetup_Assets_Asset(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONASSETSELECTIONUPDATE_ASSETPOSITIONSETUP']()
    objFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSET'] = __onSelectionUpdate_SimulationDetail_AssetPositionSetup_Assets_Asset
    #---Configurations
    def __onSelectionUpdate_SimulationDetail_Configurations_CurrencyAnalysisConfiguration(objInstance, **kwargs):
        self.pageAuxillaryFunctions['LOADCURRENCYANALYSISCONFIGURATION_CONFIGURATIONS']()
    def __onSelectionUpdate_SimulationDetail_Configurations_TradeConfiguration(objInstance, **kwargs):
        self.pageAuxillaryFunctions['LOADTRADECONFIGURATION_CONFIGURATIONS']()
    def __onButtonRelease_SimulationDetail_Configurations_MoveToSubpage(objInstance, **kwargs):
        pageNameTo = objInstance.name.split("_")[1]
        self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_{:s}".format(self.puVar['simulationDetailView_Configurations_CurrentCACConfigSubPage'])].hide()
        self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_{:s}".format(pageNameTo)].show()
        self.puVar['simulationDetailView_Configurations_CurrentCACConfigSubPage'] = pageNameTo
    def __onSelectionUpdate_SimulationDetail_Configurations_TradeScenarioType(objInstance, **kwargs):
        self.pageAuxillaryFunctions['SETTRADESCENARIOLIST_CONFIGURATIONS']()
    def __onSelectionUpdate_SimulationDetail_Configurations_RQPMFunctionSide(objInstance, **kwargs):
        self.pageAuxillaryFunctions['SETRQPMFUNCTINOPARAMETERS_CONFIGURATIONS']()
    objFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATION'] = __onSelectionUpdate_SimulationDetail_Configurations_CurrencyAnalysisConfiguration
    objFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIGURATION']            = __onSelectionUpdate_SimulationDetail_Configurations_TradeConfiguration
    objFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']                   = __onButtonRelease_SimulationDetail_Configurations_MoveToSubpage
    objFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_CONFIGURATIONS_TRADESCENARIOTYPE']             = __onSelectionUpdate_SimulationDetail_Configurations_TradeScenarioType
    objFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_CONFIGURATIONS_RQPMFUNCTIONSIDE']              = __onSelectionUpdate_SimulationDetail_Configurations_RQPMFunctionSide
    #---Trade Logs
    def __onTextUpdate_SimulationDetail_TradeLogs_TimeFilter(objInstance, **kwargs):
        rangeBeg_str = self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TIMEFILTERINPUTTEXT1"].getText()
        rangeEnd_str = self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TIMEFILTERINPUTTEXT2"].getText()
        if (rangeBeg_str == ""): rangeBeg = float('-inf')
        else:
            try:    rangeBeg = datetime.strptime(rangeBeg_str, "%Y/%m/%d %H:%M").timestamp()-time.timezone
            except: rangeBeg = None
        if (rangeEnd_str == ""): rangeEnd = float('inf')
        else:
            try:    rangeEnd = datetime.strptime(rangeEnd_str, "%Y/%m/%d %H:%M").timestamp()-time.timezone
            except: rangeEnd = None
        if ((rangeBeg is not None) and (rangeEnd is not None) and (rangeBeg <= rangeEnd)): self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TIMEFILTERAPPLYBUTTON"].activate()
        else:                                                                              self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TIMEFILTERAPPLYBUTTON"].deactivate()
    def __onButtonRelease_SimulationDetail_TradeLogs_TimeFilter(objInstance, **kwargs):
        self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TIMEFILTERAPPLYBUTTON"].deactivate()
        self.pageAuxillaryFunctions['ONTRADELOGSFILTERUPDATE_TRADELOGS']()
    def __onStatusUpdate_TradeLogs_SwitchFilter(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONTRADELOGSFILTERUPDATE_TRADELOGS']()
    def __onSelectionUpdate_SimulationDetail_TradeLogs_TradeLog(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONTRADELOGSELECTIONUPDATE_TRADELOGS']()
    objFunctions['ONTEXTUPDATE_SIMULATIONDETAIL_TRADELOGS_TIMEFILTER']     = __onTextUpdate_SimulationDetail_TradeLogs_TimeFilter
    objFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_TRADELOGS_TIMEFILTER']  = __onButtonRelease_SimulationDetail_TradeLogs_TimeFilter
    objFunctions['ONSTATUSUPDATE_SIMULATIONDETAIL_TRADELOGS_SWITCHFILTER'] = __onStatusUpdate_TradeLogs_SwitchFilter
    objFunctions['ONSELECTIONUPDATE_SIMULATIONDETAIL_TRADELOGS_TRADELOG']  = __onSelectionUpdate_SimulationDetail_TradeLogs_TradeLog
    #---Daily Reports
    #---Position Chart

    #Return the generated functions
    return objFunctions
#OBJECT FUNCTIONS END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUXILALRY FUNCTIONS --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateAuxillaryFunctions(self):
    auxFunctions = dict()

    #<_PAGELOAD>
    def __far_onSimulationUpdate(requester, updateType, simulationCode):
        if (requester == 'SIMULATIONMANAGER'):
            if (updateType == 'ADDED'):
                if (self.puVar['simulations']['_status'] == 'COMPLETED'):
                    self.puVar['simulations'][simulationCode] = self.ipcA.getPRD(processName = 'SIMULATIONMANAGER', prdAddress = ('SIMULATIONS', simulationCode))
                    self.pageAuxillaryFunctions['SETSIMULATIONSLIST']()
            elif (updateType == 'REMOVED'):
                if (simulationCode in self.puVar['simulations']):
                    del self.puVar['simulations'][simulationCode]
                    self.pageAuxillaryFunctions['SETSIMULATIONSLIST']()
                    if (simulationCode == self.puVar['simulation_selected']): 
                        self.puVar['simulation_selected'] = None
                        self.pageAuxillaryFunctions['ONSIMULATIONSELECTIONUPDATE']()
            elif (updateType == 'COMPLETED'):
                _simulation = self.ipcA.getPRD(processName = 'SIMULATIONMANAGER', prdAddress = ('SIMULATIONS', simulationCode))
                self.puVar['simulations'][simulationCode] = _simulation
                self.pageAuxillaryFunctions['SETSIMULATIONSLIST']()
    auxFunctions['_FAR_ONSIMULATIONUPDATE'] = __far_onSimulationUpdate

    #<Simulations>
    def __onSimulationsFilterUpdate():
        _simulations = self.puVar['simulations']
        #Filter Parameters
        searchText = self.GUIOs["SIMULATIONS_SEARCHTEXTINPUTBOX"].getText()
        sortType   = self.GUIOs["SIMULATIONS_SORTBYSELECTIONBOX"].getSelected()
        #Filtering
        _filtered = list(_simulations.keys())
        #---[1]: Text Filtering
        if (searchText != ""): _filtered = [_simulationCode for _simulationCode in _filtered if (searchText in _simulationCode)]
        #---[3]: Sorting
        if   (sortType == 'INDEX'): pass
        elif (sortType == 'SIMULATIONCODE'): _filtered.sort()
        elif (sortType == 'SIMULATIONRANGE'): 
            _forSort = dict()
            for _simCode in _filtered:
                _sim = _simulations[_simCode]
                _sim_simRangeBeg = _sim['simulationRange'][0]
                _sim_simRangeEnd = _sim['simulationRange'][0]
                if (_sim_simRangeBeg not in _forSort): _forSort[_sim_simRangeBeg] = list()
                _forSort[_sim_simRangeBeg].append((_simCode, _sim_simRangeEnd))
            for _simRangeBeg in _forSort: _forSort[_simRangeBeg].sort(key = lambda x: x[1])
            _forSort_forSimRangeBegSort = list(_forSort.keys())
            _forSort_forSimRangeBegSort.sort()
            _forSort_final = list()
            for _simRangeBeg in _forSort_forSimRangeBegSort: _forSort_final += _forSort[_simRangeBeg]
            _filtered = [_sortPair[0] for _sortPair in _forSort_final]
        elif (sortType == 'CREATIONTIME'):
            _forSort = [[_simulationCode, _simulations[_simulationCode]['creationTime']] for _simulationCode in _filtered]
            _forSort.sort(key = lambda x: x[1], reverse = True)
            _filtered = [_sortPair[0] for _sortPair in _forSort]
        #Finally
        self.GUIOs["SIMULATIONS_SELECTIONBOX"].setDisplayTargets(displayTargets = _filtered)
    def __setSimulationsList():
        nSimulations = len(self.puVar['simulations'])
        simulations_selectionList = dict()
        for simulationIndex, simulationCode in enumerate(self.puVar['simulations']):
            _simulation = self.puVar['simulations'][simulationCode]
            #[0]:  Index
            _index_str = "{:d} / {:d}".format(simulationIndex+1, nSimulations)
            #[1]:  Simulation Code
            _simulationCode_str = simulationCode
            #[2]:  Simulation Range
            _simRange_str1 = datetime.fromtimestamp(_simulation['simulationRange'][0], tz=timezone.utc).strftime("%Y/%m/%d")
            _simRange_str2 = datetime.fromtimestamp(_simulation['simulationRange'][1], tz=timezone.utc).strftime("%Y/%m/%d")
            _simRange_str = "{:s} ~ {:s}".format(_simRange_str1, _simRange_str2)
            #[3]:  Creation Time
            _creationTime_str = datetime.fromtimestamp(_simulation['creationTime']).strftime("%Y/%m/%d %H:%M")
            #Finally
            simulations_selectionList[simulationCode] = [{'text': _index_str},
                                                         {'text': _simulationCode_str},
                                                         {'text': _simRange_str},
                                                         {'text': _creationTime_str}]
        self.GUIOs["SIMULATIONS_SELECTIONBOX"].setSelectionList(selectionList = simulations_selectionList, keepSelected = True, displayTargets = 'all', callSelectionUpdateFunction = False)
        self.pageAuxillaryFunctions['ONSIMULATIONSFILTERUPDATE']()
    def __onSimulationSelectionUpdate():
        simulation_selected = self.puVar['simulation_selected']
        if (simulation_selected != None): _simulation = self.puVar['simulations'][simulation_selected]
        else:                             _simulation = None
        #[1]: Simulation Code
        if (simulation_selected != None):
            self.GUIOs["SIMULATIONS_SIMULATIONCODEDISPLAYTEXT"].updateText(text = simulation_selected)
            self.GUIOs["SIMULATIONS_SIMULATIONRANGEDISPLAYTEXT1"].updateText(text = datetime.fromtimestamp(_simulation['simulationRange'][0], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
            self.GUIOs["SIMULATIONS_SIMULATIONRANGEDISPLAYTEXT2"].updateText(text = datetime.fromtimestamp(_simulation['simulationRange'][1], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
        else:
            self.GUIOs["SIMULATIONS_SIMULATIONCODEDISPLAYTEXT"].updateText(text   = "-")
            self.GUIOs["SIMULATIONS_SIMULATIONRANGEDISPLAYTEXT1"].updateText(text = "-")
            self.GUIOs["SIMULATIONS_SIMULATIONRANGEDISPLAYTEXT2"].updateText(text = "-")
        #[2]: Simulation Summary
        if (simulation_selected != None):
            _simulation_summary = _simulation['_simulationSummary']
            asset_selected = self.GUIOs["RESULTSUMMARY_ASSETSELECTIONBOX"].getSelected()
            if (asset_selected not in _simulation_summary):
                _summaryKeys = [_summaryKey for _summaryKey in _simulation_summary]
                if (0 < len(_summaryKeys)): self.GUIOs["RESULTSUMMARY_ASSETSELECTIONBOX"].setSelected(itemKey = _summaryKeys[0], callSelectionUpdateFunction = False)
            self.pageAuxillaryFunctions['ONASSETSELECTIONUPDATE_RESULTSUMMARY']()
        else: self.pageAuxillaryFunctions['UPDATESIMULATIONSUMMARYASSET']()
        #[3]: Result Detail
        self.puVar['simulationDetailView_firstLoad'] = {'ASSETPOSITIONSETUP': True,
                                                        'CONFIGURATIONS':     True,
                                                        'DAILYREPORTS':       True,
                                                        'POSITIONCHART':      True,
                                                        'TRADELOGS':          True}
        self.puVar['simulationDetailView_selectionPair'] = {'ASSETPOSITIONSETUP': [None,    None],
                                                            'CONFIGURATIONS':     ['#ALL#', '#ALL#'],
                                                            'TRADELOGS':          ['#ALL#', '#ALL#'],
                                                            'DAILYREPORTS':       [None,    None],
                                                            'POSITIONCHART':      ['#ALL#', None]}
        self.puVar['simulation_selected_tradeLogs']                 = None
        self.puVar['simulation_selected_dailyRecords']              = None
        if (simulation_selected != None): self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'fetchSimulationTradeLogs', functionParams = {'simulationCode': simulation_selected}, farrHandler = self.pageAuxillaryFunctions['FARR_ONTRADELOGSFETCHRESPONSE_TRADELOGS'])
        self.pageAuxillaryFunctions['ONSIMULATIONVIEWUPDATE'](view_prev = None)
    auxFunctions['ONSIMULATIONSFILTERUPDATE']   = __onSimulationsFilterUpdate
    auxFunctions['SETSIMULATIONSLIST']          = __setSimulationsList
    auxFunctions['ONSIMULATIONSELECTIONUPDATE'] = __onSimulationSelectionUpdate

    #<Result Summary>
    def __onAssetSelectionUpdate_ResultSummary():
        _assetName_selected = self.GUIOs["RESULTSUMMARY_ASSETSELECTIONBOX"].getSelected()
        if   (_assetName_selected == 'total'): self.GUIOs["RESULTSUMMARY_SELECTEDASSETIMAGEBOX"].updateImage(image = "assetTotalIcon_512x512.png")
        elif (_assetName_selected == 'USDT'):  self.GUIOs["RESULTSUMMARY_SELECTEDASSETIMAGEBOX"].updateImage(image = "usdtIcon_512x512.png")
        elif (_assetName_selected == 'USDC'):  self.GUIOs["RESULTSUMMARY_SELECTEDASSETIMAGEBOX"].updateImage(image = "usdcIcon_512x512.png")
        self.pageAuxillaryFunctions['UPDATESIMULATIONSUMMARYASSET']()
    def __updateSimulationSummaryAsset():
        simulation_selected = self.puVar['simulation_selected']
        asset_selected      = self.GUIOs["RESULTSUMMARY_ASSETSELECTIONBOX"].getSelected()
        if (simulation_selected != None):
            _simulation_summary = self.puVar['simulations'][simulation_selected]['_simulationSummary']
            if (asset_selected in _simulation_summary): _simulation_summary_asset = _simulation_summary[asset_selected]
            else:                                       _simulation_summary_asset = None
        else: _simulation_summary_asset = None
        if (_simulation_summary_asset != None):
            _nTradeDays = _simulation_summary_asset['nTradeDays']
            self.GUIOs["RESULTSUMMARY_NTRADEDAYSDISPLAYTEXT"].updateText(text = "{:d}".format(_nTradeDays))
            self.GUIOs["RESULTSUMMARY_NTRADESDISPLAYTEXT"].updateText(text    = "{:d}".format(_simulation_summary_asset['nTrades_total']))
            if (asset_selected == 'total'):
                self.GUIOs["RESULTSUMMARY_NETPROFITDISPLAYTEXT"].updateText(text               = "-")
                self.GUIOs["RESULTSUMMARY_GAINSDISPLAYTEXT"].updateText(text                   = "-")
                self.GUIOs["RESULTSUMMARY_LOSSESDISPLAYTEXT"].updateText(text                  = "-")
                self.GUIOs["RESULTSUMMARY_FEESDISPLAYTEXT"].updateText(text                    = "-")
                self.GUIOs["RESULTSUMMARY_WALLETBALANCE1DISPLAYTEXT"].updateText(text          = "- / -")
                self.GUIOs["RESULTSUMMARY_WALLETBALANCE2DISPLAYTEXT"].updateText(text          = "- / -")
                self.GUIOs["RESULTSUMMARY_WALLETBALANCEGROWTHRATEDISPLAYTEXT"].updateText(text = "-")
                self.GUIOs["RESULTSUMMARY_WALLETBALANCEVOLATILITYDISPLAYTEXT"].updateText(text = "-")
            else:
                #Gains, Losses, Trading Fee
                _gains      = _simulation_summary_asset['gains']
                _losses     = _simulation_summary_asset['losses']
                _tradingFee = _simulation_summary_asset['tradingFee']
                self.GUIOs["RESULTSUMMARY_GAINSDISPLAYTEXT"].updateText(text  = f"{atmEta_Auxillaries.floatToString(number = _gains,      precision = _ASSETPRECISIONS_XS[asset_selected])} {asset_selected}")
                self.GUIOs["RESULTSUMMARY_LOSSESDISPLAYTEXT"].updateText(text = f"{atmEta_Auxillaries.floatToString(number = _losses,     precision = _ASSETPRECISIONS_XS[asset_selected])} {asset_selected}")
                self.GUIOs["RESULTSUMMARY_FEESDISPLAYTEXT"].updateText(text   = f"{atmEta_Auxillaries.floatToString(number = _tradingFee, precision = _ASSETPRECISIONS_XS[asset_selected])} {asset_selected}")
                #Net Profit
                _netProfit = round(_gains-_losses-_tradingFee, _ASSETPRECISIONS[asset_selected])
                if   (_netProfit < 0):  str = f"{atmEta_Auxillaries.floatToString(number  = _netProfit, precision = _ASSETPRECISIONS_XS[asset_selected])}"; strCol = 'RED_LIGHT'
                elif (_netProfit == 0): str = f"{atmEta_Auxillaries.floatToString(number  = _netProfit, precision = _ASSETPRECISIONS_XS[asset_selected])}"; strCol = 'DEFAULT'
                else:                   str = f"+{atmEta_Auxillaries.floatToString(number = _netProfit, precision = _ASSETPRECISIONS_XS[asset_selected])}"; strCol = 'GREEN_LIGHT'
                _netProfit_text = ""; _netProfit_textStyle = list()
                for _newTextString, _newTextStyle in ((str,                  strCol), 
                                                      (f" {asset_selected}", 'DEFAULT')):
                    _netProfit_textStyle.append(((len(_netProfit_text), len(_netProfit_text)+len(_newTextString)-1), _newTextStyle))
                    _netProfit_text += _newTextString
                self.GUIOs["RESULTSUMMARY_NETPROFITDISPLAYTEXT"].updateText(text = _netProfit_text, textStyle = _netProfit_textStyle)
                #Wallet Balance (Initial / Final)
                _wb_initial = _simulation_summary_asset['walletBalance_initial']
                _wb_final   = _simulation_summary_asset['walletBalance_final']
                if (_wb_initial == 0): _wb_ifRatio = None
                else:                  _wb_ifRatio = round(_wb_final/_wb_initial*100, 3)
                _wb_initial_str = atmEta_Auxillaries.floatToString(number = _simulation_summary_asset['walletBalance_initial'], precision = _ASSETPRECISIONS_XS[asset_selected])
                _wb_final_str   = atmEta_Auxillaries.floatToString(number = _simulation_summary_asset['walletBalance_final'],   precision = _ASSETPRECISIONS_XS[asset_selected])
                if   (_wb_ifRatio is None): _wb_ifRatio_str = f"[N/A]";                  _wb_final_str_color = 'DEFAULT'
                elif (_wb_ifRatio == 100):  _wb_ifRatio_str = f"[{_wb_ifRatio:,.3f} %]"; _wb_final_str_color = 'DEFAULT'
                elif (_wb_ifRatio <  100):  _wb_ifRatio_str = f"[{_wb_ifRatio:,.3f} %]"; _wb_final_str_color = 'RED_LIGHT'
                else:                       _wb_ifRatio_str = f"[{_wb_ifRatio:,.3f} %]"; _wb_final_str_color = 'GREEN_LIGHT'
                _textString = ""; _textStyle = list()
                for _newTextString, _newTextStyle in ((f"{_wb_initial_str} {asset_selected}", 'DEFAULT'), 
                                                      (" / ",                                 'DEFAULT'), 
                                                      (_wb_final_str,                         _wb_final_str_color), 
                                                      (f" {asset_selected} ",                 'DEFAULT'), 
                                                      (_wb_ifRatio_str,                       _wb_final_str_color)):
                    _textStyle.append(((len(_textString), len(_textString)+len(_newTextString)-1), _newTextStyle))
                    _textString += _newTextString
                self.GUIOs["RESULTSUMMARY_WALLETBALANCE1DISPLAYTEXT"].updateText(text = _textString, textStyle = _textStyle)
                #Wallet Balance (Minimum, Maximum)
                _wb_min_str = atmEta_Auxillaries.floatToString(number = _simulation_summary_asset['walletBalance_min'], precision = _ASSETPRECISIONS_XS[asset_selected])
                _wb_max_str = atmEta_Auxillaries.floatToString(number = _simulation_summary_asset['walletBalance_max'], precision = _ASSETPRECISIONS_XS[asset_selected])
                self.GUIOs["RESULTSUMMARY_WALLETBALANCE2DISPLAYTEXT"].updateText(text = f"{_wb_min_str} {asset_selected} / {_wb_max_str} {asset_selected}")
                #Wallet Balance Growth Rate
                _wbta_growthRate_daily = _simulation_summary_asset['wbta_growthRate_daily']
                if (_wbta_growthRate_daily is None): _wbta_growthRate_text = "N/A"; _wbta_growthRate_textStyle = 'DEFAULT'
                else:
                    _wbta_growthRate_monthly = math.exp(_wbta_growthRate_daily*30.4167)-1
                    _wbta_growthRate_text = ""; _wbta_growthRate_textStyle = list()
                    if   (_wbta_growthRate_daily < 0):  _str0 = f"{_wbta_growthRate_daily*100:.3f} %";  _str1 = f"{_wbta_growthRate_monthly*100:.3f} %";  strCol = "RED_LIGHT"
                    elif (_wbta_growthRate_daily == 0): _str0 = f"{_wbta_growthRate_daily*100:.3f} %";  _str1 = f"{_wbta_growthRate_monthly*100:.3f} %";  strCol = "DEFAULT"
                    else:                               _str0 = f"+{_wbta_growthRate_daily*100:.3f} %"; _str1 = f"+{_wbta_growthRate_monthly*100:.3f} %"; strCol = "GREEN_LIGHT"
                    for _newTextString, _newTextStyle in ((_str0,         strCol), 
                                                          (" [Daily] / ", 'DEFAULT'),
                                                          (_str1,         strCol), 
                                                          (" [Monthly]",  'DEFAULT')):
                        _wbta_growthRate_textStyle.append(((len(_wbta_growthRate_text), len(_wbta_growthRate_text)+len(_newTextString)-1), _newTextStyle))
                        _wbta_growthRate_text += _newTextString
                self.GUIOs["RESULTSUMMARY_WALLETBALANCEGROWTHRATEDISPLAYTEXT"].updateText(text = _wbta_growthRate_text, textStyle = _wbta_growthRate_textStyle)
                #Wallet Balance Volatility
                _wbta_volatility = _simulation_summary_asset['wbta_volatility']
                if (_wbta_growthRate_daily is None): _textString = "N/A"; _textStyle = "DEFAULT"
                else:
                    _wbta_tMin = math.exp(-_wbta_volatility*3)-1
                    _wbta_tMax = math.exp( _wbta_volatility*3)-1
                    _textString = ""; _textStyle = list()
                    for _newTextString, _newTextStyle in ((f" {_wbta_tMin*100:.3f} %", 'ORANGE_LIGHT'), 
                                                          (" / ",                      'DEFAULT'),
                                                          (f"+{_wbta_tMax*100:.3f} %", 'BLUE_LIGHT')):
                        _textStyle.append(((len(_textString), len(_textString)+len(_newTextString)-1), _newTextStyle))
                        _textString += _newTextString
                self.GUIOs["RESULTSUMMARY_WALLETBALANCEVOLATILITYDISPLAYTEXT"].updateText(text = _textString, textStyle = _textStyle)
        else:
            self.GUIOs["RESULTSUMMARY_NTRADEDAYSDISPLAYTEXT"].updateText(text              = "-")
            self.GUIOs["RESULTSUMMARY_NTRADESDISPLAYTEXT"].updateText(text                 = "-")
            self.GUIOs["RESULTSUMMARY_NETPROFITDISPLAYTEXT"].updateText(text               = "-")
            self.GUIOs["RESULTSUMMARY_GAINSDISPLAYTEXT"].updateText(text                   = "-")
            self.GUIOs["RESULTSUMMARY_LOSSESDISPLAYTEXT"].updateText(text                  = "-")
            self.GUIOs["RESULTSUMMARY_FEESDISPLAYTEXT"].updateText(text                    = "-")
            self.GUIOs["RESULTSUMMARY_WALLETBALANCE1DISPLAYTEXT"].updateText(text          = "- / -")
            self.GUIOs["RESULTSUMMARY_WALLETBALANCE2DISPLAYTEXT"].updateText(text          = "- / -")
            self.GUIOs["RESULTSUMMARY_WALLETBALANCEGROWTHRATEDISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["RESULTSUMMARY_WALLETBALANCEVOLATILITYDISPLAYTEXT"].updateText(text = "-")
    auxFunctions['ONASSETSELECTIONUPDATE_RESULTSUMMARY'] = __onAssetSelectionUpdate_ResultSummary
    auxFunctions['UPDATESIMULATIONSUMMARYASSET'] = __updateSimulationSummaryAsset

    #<Simulation Detail>
    def __onSimulationViewUpdate(view_prev = None):
        _view_selected = self.puVar['simulationDetailView_selected']
        if (view_prev != None):
            for _guioName in self.puVar['GUIOGROUPS'][view_prev]: self.GUIOs[_guioName].hide()
            if (view_prev == 'CONFIGURATIONS'): self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_{:s}".format(self.puVar['simulationDetailView_Configurations_CurrentCACConfigSubPage'])].hide()
            for _guioName in self.puVar['GUIOGROUPS'][_view_selected]: self.GUIOs[_guioName].show()
            if (_view_selected == 'CONFIGURATIONS'): self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_{:s}".format(self.puVar['simulationDetailView_Configurations_CurrentCACConfigSubPage'])].show()
        #Asset & Position Selection GUIOs Control & Post Update Handling
        self.pageAuxillaryFunctions['SETASSETSLIST']()
        self.pageAuxillaryFunctions['SETPOSITIONSLIST']()
        #View-Dependent Handling
        if (self.puVar['simulationDetailView_firstLoad'][_view_selected] == True):
            self.puVar['simulationDetailView_firstLoad'][_view_selected] = False
            if (_view_selected == 'ASSETPOSITIONSETUP'):
                self.pageAuxillaryFunctions['SETPOSITIONSLIST_ASSETPOSITIONSETUP']()
                self.pageAuxillaryFunctions['ONASSETSELECTIONUPDATE_ASSETPOSITIONSETUP']()
            elif (_view_selected == 'CONFIGURATIONS'):
                self.pageAuxillaryFunctions['SETCONFIGURATIONSLIST_CONFIGURATIONS']()
                self.pageAuxillaryFunctions['LOADCURRENCYANALYSISCONFIGURATION_CONFIGURATIONS']()
                self.pageAuxillaryFunctions['LOADTRADECONFIGURATION_CONFIGURATIONS']()
            elif (_view_selected == 'TRADELOGS'):
                self.pageAuxillaryFunctions['SETTRADELOGSLIST_TRADELOGS']()
            elif (_view_selected == 'DAILYREPORTS'):
                self.pageAuxillaryFunctions['SETDAILYREPORTSTARGET_DAILYREPORTS']()
            elif (_view_selected == 'POSITIONCHART'):
                self.pageAuxillaryFunctions['SETCHARTDRAWERTARGET_POSITIONCHART']()
    def __setAssetsList():
        _simulation_selected = self.puVar['simulation_selected']
        if (_simulation_selected != None):
            _simulation    = self.puVar['simulations'][_simulation_selected]
            _view_selected = self.puVar['simulationDetailView_selected']
            #Selection List
            if ((_view_selected == 'CONFIGURATIONS') or (_view_selected == 'TRADELOGS') or (_view_selected == 'DAILYREPORTS') or (_view_selected == 'POSITIONCHART')):
                _asset_selected = self.puVar['simulationDetailView_selectionPair'][_view_selected][0]
                if   ((_view_selected == 'CONFIGURATIONS') or (_view_selected == 'TRADELOGS') or (_view_selected == 'POSITIONCHART')): _assetsList = {'#ALL#': {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_SELECTIONBOX_ALL')}}
                elif (_view_selected == 'DAILYREPORTS'):                                                                               _assetsList = dict()
                for _assetName in _simulation['assets']: _assetsList[_assetName] = {'text': _assetName}
                self.GUIOs["SIMULATIONDETAIL_ASSETSELECTIONBOX"].setSelectionList(selectionList = _assetsList, displayTargets = 'all', keepSelected = True, callSelectionUpdateFunction = False)
                self.GUIOs["SIMULATIONDETAIL_ASSETSELECTIONBOX"].setSelected(itemKey = _asset_selected, callSelectionUpdateFunction = False)
                if   (_asset_selected == None):    self.GUIOs["SIMULATIONDETAIL_ASSETIMAGEBOX"].updateImage(image = "assetEmptyIcon_512x512.png")
                elif (_asset_selected == '#ALL#'): self.GUIOs["SIMULATIONDETAIL_ASSETIMAGEBOX"].updateImage(image = "assetTotalIcon_512x512.png")
                elif (_asset_selected == 'USDT'):  self.GUIOs["SIMULATIONDETAIL_ASSETIMAGEBOX"].updateImage(image = "usdtIcon_512x512.png")
                elif (_asset_selected == 'USDC'):  self.GUIOs["SIMULATIONDETAIL_ASSETIMAGEBOX"].updateImage(image = "usdcIcon_512x512.png")
            elif (_view_selected == 'ASSETPOSITIONSETUP'):
                self.GUIOs["SIMULATIONDETAIL_ASSETSELECTIONBOX"].clearSelectionList()
                self.GUIOs["SIMULATIONDETAIL_ASSETSELECTIONBOX"].setSelected(itemKey = None, callSelectionUpdateFunction = False)
                self.GUIOs["SIMULATIONDETAIL_ASSETIMAGEBOX"].updateImage(image = "assetEmptyIcon_512x512.png")
            #Activation
            if   ((_view_selected == 'CONFIGURATIONS') or (_view_selected == 'TRADELOGS') or (_view_selected == 'DAILYREPORTS') or (_view_selected == 'POSITIONCHART')): self.GUIOs["SIMULATIONDETAIL_ASSETSELECTIONBOX"].activate()
            elif (_view_selected == 'ASSETPOSITIONSETUP'):                                                                                                               self.GUIOs["SIMULATIONDETAIL_ASSETSELECTIONBOX"].deactivate()
        else:
            self.GUIOs["SIMULATIONDETAIL_ASSETSELECTIONBOX"].clearSelectionList()
            self.GUIOs["SIMULATIONDETAIL_ASSETSELECTIONBOX"].setSelected(itemKey = None, callSelectionUpdateFunction = False)
            self.GUIOs["SIMULATIONDETAIL_ASSETIMAGEBOX"].updateImage(image = "assetEmptyIcon_512x512.png")
            self.GUIOs["SIMULATIONDETAIL_ASSETSELECTIONBOX"].deactivate()
    def __setPositionsList():
        _simulation_selected     = self.puVar['simulation_selected']
        if (_simulation_selected != None):
            _simulation    = self.puVar['simulations'][_simulation_selected]
            _view_selected = self.puVar['simulationDetailView_selected']
            #Selection List
            if ((_view_selected == 'CONFIGURATIONS') or (_view_selected == 'TRADELOGS') or (_view_selected == 'POSITIONCHART')):
                _asset_selected    = self.puVar['simulationDetailView_selectionPair'][_view_selected][0]
                _position_selected = self.puVar['simulationDetailView_selectionPair'][_view_selected][1]
                _positions = _simulation['positions']
                if (_asset_selected == '#ALL#'): _pSymbols_thisAsset = list(_positions.keys())
                else:                            _pSymbols_thisAsset = [_pSymbol for _pSymbol in _positions if _positions[_pSymbol]['quoteAsset'] == _asset_selected]
                if   ((_view_selected == 'CONFIGURATIONS') or (_view_selected == 'TRADELOGS')):     _positionsList = {'#ALL#': {'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_SELECTIONBOX_ALL'), 'textAnchor': 'W'}}
                elif ((_view_selected == 'DAILYREPORTS')   or (_view_selected == 'POSITIONCHART')): _positionsList = dict()
                for _pSymbol in _pSymbols_thisAsset: _positionsList[_pSymbol] = {'text': _pSymbol, 'textAnchor': 'W'}
                self.GUIOs["SIMULATIONDETAIL_POSITIONSELECTIONBOX"].setSelectionList(selectionList = _positionsList, displayTargets = 'all', keepSelected = True, callSelectionUpdateFunction = False)
                if (_position_selected not in _pSymbols_thisAsset): self.puVar['simulationDetailView_selectionPair'][_view_selected][1] = "#ALL#"; _position_selected = "#ALL#"
                self.GUIOs["SIMULATIONDETAIL_POSITIONSELECTIONBOX"].setSelected(itemKey = self.puVar['simulationDetailView_selectionPair'][_view_selected][1], callSelectionUpdateFunction = False)
            elif (_view_selected == 'ASSETPOSITIONSETUP') or (_view_selected == 'DAILYREPORTS'):
                self.GUIOs["SIMULATIONDETAIL_POSITIONSELECTIONBOX"].clearSelectionList()
                self.GUIOs["SIMULATIONDETAIL_POSITIONSELECTIONBOX"].setSelected(itemKey = None, callSelectionUpdateFunction = False)
            #Activation
            if   ((_view_selected == 'CONFIGURATIONS') or (_view_selected == 'TRADELOGS') or (_view_selected == 'POSITIONCHART')): self.GUIOs["SIMULATIONDETAIL_POSITIONSELECTIONBOX"].activate()
            elif ((_view_selected == 'ASSETPOSITIONSETUP') or (_view_selected == 'DAILYREPORTS')):                                 self.GUIOs["SIMULATIONDETAIL_POSITIONSELECTIONBOX"].deactivate()
        else:
            self.GUIOs["SIMULATIONDETAIL_POSITIONSELECTIONBOX"].clearSelectionList()
            self.GUIOs["SIMULATIONDETAIL_POSITIONSELECTIONBOX"].setSelected(itemKey = None, callSelectionUpdateFunction = False)
            self.GUIOs["SIMULATIONDETAIL_POSITIONSELECTIONBOX"].deactivate()
    def __onAssetPositionUpdate_SimulationDetail():
        _view_selected = self.GUIOs["SIMULATIONDETAIL_VIEWSELECTIONBOX"].getSelected()
        if   (_view_selected == 'CONFIGURATIONS'): self.pageAuxillaryFunctions['SETCONFIGURATIONSLIST_CONFIGURATIONS']()
        elif (_view_selected == 'TRADELOGS'):      self.pageAuxillaryFunctions['ONTRADELOGSFILTERUPDATE_TRADELOGS']()
        elif (_view_selected == 'DAILYREPORTS'):   self.pageAuxillaryFunctions['SETDAILYREPORTSTARGET_DAILYREPORTS']()
        elif (_view_selected == 'POSITIONCHART'):  self.pageAuxillaryFunctions['SETCHARTDRAWERTARGET_POSITIONCHART']()
    auxFunctions['ONSIMULATIONVIEWUPDATE']                      = __onSimulationViewUpdate
    auxFunctions['SETASSETSLIST']                               = __setAssetsList
    auxFunctions['SETPOSITIONSLIST']                            = __setPositionsList
    auxFunctions['ONASSETPOSITIONUPDATE_SIMULATIONDETAIL']      = __onAssetPositionUpdate_SimulationDetail
    #---Asset & Position Setup
    #------Positions
    def __setPositionsList_AssetPositionSetup():
        if (self.puVar['simulation_selected'] == None): self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SELECTIONBOX"].clearSelectionList()
        else:
            positions = self.puVar['simulations'][self.puVar['simulation_selected']]['positions']
            nPositions = len(positions)
            positions_selectionList = dict()
            for positionIndex, symbol in enumerate(positions):
                _position = positions[symbol]
                #[0]:  Index
                _index_str = "{:d} / {:d}".format(positionIndex+1, nPositions)
                #[1]:  Symbol
                _symbol_str = symbol
                #[2]:  Currency Analysis Code
                if (_position['currencyAnalysisConfigurationCode'] == None): _currencyAnalysisConfigurationCode_str = "-"
                else:                                                        _currencyAnalysisConfigurationCode_str = _position['currencyAnalysisConfigurationCode']
                #[3]:  Trade Configuration Code
                if (_position['tradeConfigurationCode'] == None): _tradeConfigurationCode_str = "-"
                else:                                             _tradeConfigurationCode_str = _position['tradeConfigurationCode']
                #[4]:  Margin Mode
                if   (_position['isolated'] == True):  _marginMode_str = 'ISOLATED'
                elif (_position['isolated'] == False): _marginMode_str = 'CROSSED'
                elif (_position['isolated'] == None):  _marginMode_str = '-'
                #[5]:  Leverage
                if (_position['leverage'] == None): _leverage_str = "-"
                else:                               _leverage_str = str(_position['leverage'])
                #[6]:  Priority
                _priority_str = str(_position['priority'])
                #[7]:  Assumed Ratio
                _assumedRatio_str = "{:.3f} %".format(_position['assumedRatio']*100)
                #[8]:  Weighted Assumed Ratio
                if (_position['weightedAssumedRatio'] == None): _weightedAssumedRatio_str = "-"
                else:                                           _weightedAssumedRatio_str = "{:.3f} %".format(_position['weightedAssumedRatio']*100)
                #[9]:  Allocated Balance
                _allocatedBalance_str = atmEta_Auxillaries.floatToString(number = _position['allocatedBalance'], precision = _ASSETPRECISIONS_S[_position['quoteAsset']])
                #[10]: Max Allocated Balance
                if (_position['maxAllocatedBalance'] == float('inf')): _maxAllocatedBalance_str = "INF"
                else:                                                  _maxAllocatedBalance_str = atmEta_Auxillaries.floatToString(number = _position['maxAllocatedBalance'], precision = _ASSETPRECISIONS_S[_position['quoteAsset']])
                #[11]: First Kline
                if (_position['firstKline'] == None): _firstKline_str = "-"
                else:                                 _firstKline_str = datetime.fromtimestamp(_position['firstKline'], tz=timezone.utc).strftime("%Y/%m/%d %H:%M")
                #Finally
                positions_selectionList[symbol] = [{'text': _index_str},
                                                   {'text': _symbol_str},
                                                   {'text': _currencyAnalysisConfigurationCode_str},
                                                   {'text': _tradeConfigurationCode_str},
                                                   {'text': _marginMode_str},
                                                   {'text': _leverage_str,},
                                                   {'text': _priority_str},
                                                   {'text': _assumedRatio_str},
                                                   {'text': _weightedAssumedRatio_str},
                                                   {'text': _allocatedBalance_str},
                                                   {'text': _maxAllocatedBalance_str},
                                                   {'text': _firstKline_str}]
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SELECTIONBOX"].setSelectionList(selectionList = positions_selectionList, displayTargets = 'all', callSelectionUpdateFunction = True)
            self.pageAuxillaryFunctions['ONPOSITIONSFILTERUPDATE_ASSETPOSITIONSETUP']()
    def __onPositionsFilterUpdate_AssetPositionSetup():
        if (self.puVar['simulation_selected'] != None):
            _positions = self.puVar['simulations'][self.puVar['simulation_selected']]['positions']
            #Filter Parameters
            searchText = self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCHTEXTINPUTBOX"].getText()
            searchType = self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCHTYPESELECTIONBOX"].getSelected()
            sortType   = self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBYSELECTIONBOX"].getSelected()
            #Filtering
            _filtered = list(_positions.keys())
            #---[1]: Text Filtering
            if (searchText != ""): 
                if (searchType == 'SYMBOL'):  _filtered = [_symbol for _symbol in _filtered if (searchText in _symbol)]
                if (searchType == 'TCCODE'):  _filtered = [_symbol for _symbol in _filtered if ((_positions[_symbol]['tradeConfigurationCode']            != None) and (searchText in _positions[_symbol]['tradeConfigurationCode']))]
                if (searchType == 'CACCODE'): _filtered = [_symbol for _symbol in _filtered if ((_positions[_symbol]['currencyAnalysisConfigurationCode'] != None) and (searchText in _positions[_symbol]['currencyAnalysisConfigurationCode']))]
            #---[2]: Sorting
            if   (sortType == 'INDEX'): pass
            elif (sortType == 'SYMBOL'): _filtered.sort()
            elif (sortType == 'CACCODE'): 
                _forSort = [[_symbol, _positions[_symbol]['currencyAnalysisConfigurationCode']] for _symbol in _filtered]
                for i in range (len(_forSort)): 
                    if (_forSort[i][1] == None): _forSort[i][1] = ""
                _forSort.sort(key = lambda x: x[1])
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            elif (sortType == 'TCCODE'):
                _forSort = [[_symbol, _positions[_symbol]['tradeConfigurationCode']] for _symbol in _filtered]
                for i in range (len(_forSort)): 
                    if (_forSort[i][1] == None): _forSort[i][1] = ""
                _forSort.sort(key = lambda x: x[1])
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            elif (sortType == 'MARGINMODE'):
                _forSort = [[_symbol, _positions[_symbol]['isolated']] for _symbol in _filtered]
                for i in range (len(_forSort)): 
                    if   (_forSort[i][1] == True):  _forSort[i][1] = 0
                    elif (_forSort[i][1] == False): _forSort[i][1] = 1
                    elif (_forSort[i][1] == None):  _forSort[i][1] = 2
                _forSort.sort(key = lambda x: x[1])
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            elif (sortType == 'LEVERAGE'):
                _forSort = [[_symbol, _positions[_symbol]['leverage']] for _symbol in _filtered]
                for i in range (len(_forSort)): 
                    if (_forSort[i][1] == None): _forSort[i][1] = 0
                _forSort.sort(key = lambda x: x[1], reverse = True)
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            elif (sortType == 'PRIORITY'): 
                _forSort = [[_symbol, _positions[_symbol]['priority']] for _symbol in _filtered]
                _forSort.sort(key = lambda x: x[1])
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            elif (sortType == 'ASSUMEDRATIO'): 
                _forSort = [[_symbol, _positions[_symbol]['assumedRatio']] for _symbol in _filtered]
                _forSort.sort(key = lambda x: x[1], reverse = True)
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            elif (sortType == 'WEIGHTEDASSUMEDRATIO'):
                _forSort = [[_symbol, _positions[_symbol]['weightedAssumedRatio']] for _symbol in _filtered]
                for i in range (len(_forSort)): 
                    if (_forSort[i][1] == None): _forSort[i][1] = 0
                _forSort.sort(key = lambda x: x[1], reverse = True)
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            elif (sortType == 'ALLOCATEDBALANCE'): 
                _forSort = [[_symbol, _positions[_symbol]['allocatedBalance']] for _symbol in _filtered]
                _forSort.sort(key = lambda x: x[1], reverse = True)
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            elif (sortType == 'MAXALLOCATEDBALANCE'): 
                _forSort = [[_symbol, _positions[_symbol]['maxAllocatedBalance']] for _symbol in _filtered]
                for i in range (len(_forSort)): 
                    if (_forSort[i][1] == None): _forSort[i][1] = -1
                _forSort.sort(key = lambda x: x[1])
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            elif (sortType == 'FIRSTKLINE'): 
                _forSort = [[_symbol, _positions[_symbol]['firstKline']] for _symbol in _filtered]
                for i in range (len(_forSort)): 
                    if (_forSort[i][1] == None): _forSort[i][1] = float('inf')
                _forSort.sort(key = lambda x: x[1])
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            #Finally
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SELECTIONBOX"].setDisplayTargets(displayTargets = _filtered)
    def __updatePositionsGraphics_AssetPositionSetup(positionsPrev):
        #Update Graphics
        for _pSymbol in positionsPrev:
            _position      = self.puVar['simulationSetup_positions'][_pSymbol]
            _position_prev = positionsPrev[_pSymbol]
            for _dataName in _POSITIONDATA_SELECTIONBOXCOLUMNINDEX:
                _cIndex = _POSITIONDATA_SELECTIONBOXCOLUMNINDEX[_dataName]
                if (_position_prev[_dataName] != _position[_dataName]):
                    if (_dataName == 'currencyAnalysisConfigurationCode'):
                        if (_position['currencyAnalysisConfigurationCode'] == None): _text = "-"
                        else:                                                        _text = _position['currencyAnalysisConfigurationCode']
                        _newSelectionBoxItem = {'text': _text}
                    elif (_dataName == 'tradeConfigurationCode'):
                        if (_position['tradeConfigurationCode'] == None): _text = "-"
                        else:                                             _text = _position['tradeConfigurationCode']
                        _newSelectionBoxItem = {'text': _text}
                    elif (_dataName == 'isolated'):
                        if   (_position['isolated'] == None):  _text = "-"
                        elif (_position['isolated'] == True):  _text = 'ISOLATED'
                        elif (_position['isolated'] == False): _text = 'CROSSED'
                        _newSelectionBoxItem = {'text': _text}
                    elif (_dataName == 'leverage'):
                        if (_position['leverage'] == None): _text = "-"
                        else:                               _text = "{:d}".format(_position['leverage'])
                        _newSelectionBoxItem = {'text': _text}
                    elif (_dataName == 'priority'):
                        if (_position['priority'] == None): _text = "-"
                        else:                               _text = "{:d}".format(_position['priority'])
                        _newSelectionBoxItem = {'text': _text}
                    elif (_dataName == 'assumedRatio'):
                        _text = "{:.3f} %".format(_position['assumedRatio']*100)
                        _newSelectionBoxItem = {'text': _text}
                    elif (_dataName == 'weightedAssumedRatio'):
                        if (_position['weightedAssumedRatio'] == None): _text = "-"
                        else:                                           _text = "{:.3f} %".format(_position['weightedAssumedRatio']*100)
                        _newSelectionBoxItem = {'text': _text}
                    elif (_dataName == 'allocatedBalance'):
                        _text = atmEta_Auxillaries.floatToString(number = _position['allocatedBalance'], precision = _ASSETPRECISIONS_S[_position['quoteAsset']])
                        _newSelectionBoxItem = {'text': _text}
                    elif (_dataName == 'maxAllocatedBalance'):
                        if (_position['maxAllocatedBalance'] == float('inf')): _text = "INF"
                        else:                                                  _text = atmEta_Auxillaries.floatToString(number = _position['maxAllocatedBalance'], precision = _ASSETPRECISIONS_S[_position['quoteAsset']])
                        _newSelectionBoxItem = {'text': _text}
                    elif (_dataName == 'tradable'):
                        if (_position['tradable'] == True): _text = 'TRUE';  _textColor = 'GREEN_LIGHT'
                        else:                               _text = 'FALSE'; _textColor = 'RED_LIGHT'
                        _newSelectionBoxItem = {'text': _text, 'textStyles': [('all', _textColor),]}
                    self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SELECTIONBOX"].editSelectionListItem(itemKey = _pSymbol, item = _newSelectionBoxItem, columnIndex = _cIndex)
    auxFunctions['SETPOSITIONSLIST_ASSETPOSITIONSETUP']        = __setPositionsList_AssetPositionSetup
    auxFunctions['ONPOSITIONSFILTERUPDATE_ASSETPOSITIONSETUP'] = __onPositionsFilterUpdate_AssetPositionSetup
    auxFunctions['UPDATEPOSITIONSGRAPHICS_ASSETPOSITIONSETUP'] = __updatePositionsGraphics_AssetPositionSetup
    #------Assets
    def __onAssetSelectionUpdate_AssetPositionSetup():
        _assetName_selected = self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSETSELECTIONBOX"].getSelected()
        if   (_assetName_selected == 'USDT'): self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_SELECTEDASSETIMAGEBOX"].updateImage(image = "usdtIcon_512x512.png")
        elif (_assetName_selected == 'USDC'): self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_SELECTEDASSETIMAGEBOX"].updateImage(image = "usdcIcon_512x512.png")
        self.pageAuxillaryFunctions['UPDATEASSETDATADISPLAY_ASSETPOSITIONSETUP']()
    def __updateAssetDataDisplay_AssetPositionSetup():
        if (self.puVar['simulation_selected'] != None):
            _assetName_selected = self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSETSELECTIONBOX"].getSelected()
            _asset = self.puVar['simulations'][self.puVar['simulation_selected']]['assets'][_assetName_selected]
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_INITIALWALLETBALANCEDISPLAYTEXT"].updateText(text = atmEta_Auxillaries.floatToString(number = _asset['initialWalletBalance'], precision = _ASSETPRECISIONS[_assetName_selected]))
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ALLOCATIONRATIODISPLAYTEXT"].updateText(text = "{:.1f} %".format(_asset['allocationRatio']*100))
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ALLOCATEDBALANCEDISPLAYTEXT"].updateText(text = atmEta_Auxillaries.floatToString(number = _asset['allocatedBalance'], precision = _ASSETPRECISIONS_S[_assetName_selected]))
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSUMEDRATIODISPLAYTEXT"].updateText(text = "{:.3f} %".format(_asset['assumedRatio']*100))
            if (_asset['weightedAssumedRatio'] == None): self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_WEIGHTEDASSUMEDRATIODISPLAYTEXT"].updateText(text = "-")
            else:                                        self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_WEIGHTEDASSUMEDRATIODISPLAYTEXT"].updateText(text = "{:.3f} %".format(_asset['weightedAssumedRatio']*100))
            if   (_asset['maxAllocatedBalance'] == None):         self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_MAXALLOCATEDBALANCEDISPLAYTEXT"].updateText(text = "-")
            elif (_asset['maxAllocatedBalance'] == float('inf')): self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_MAXALLOCATEDBALANCEDISPLAYTEXT"].updateText(text = "INF")
            else:                                                 self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_MAXALLOCATEDBALANCEDISPLAYTEXT"].updateText(text = atmEta_Auxillaries.floatToString(number = _asset['maxAllocatedBalance'], precision = _ASSETPRECISIONS_S[_assetName_selected]))
        else:
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_INITIALWALLETBALANCEDISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ALLOCATIONRATIODISPLAYTEXT"].updateText(text      = "-")
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ALLOCATEDBALANCEDISPLAYTEXT"].updateText(text     = "-")
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSUMEDRATIODISPLAYTEXT"].updateText(text         = "-")
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_WEIGHTEDASSUMEDRATIODISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_MAXALLOCATEDBALANCEDISPLAYTEXT"].updateText(text  = "-")
    auxFunctions['ONASSETSELECTIONUPDATE_ASSETPOSITIONSETUP'] = __onAssetSelectionUpdate_AssetPositionSetup
    auxFunctions['UPDATEASSETDATADISPLAY_ASSETPOSITIONSETUP'] = __updateAssetDataDisplay_AssetPositionSetup
    #---Configurations
    def __setConfigurationsList_Configurations():
        _simulation_selected = self.puVar['simulation_selected']
        if (_simulation_selected != None):
            _simulation = self.puVar['simulations'][_simulation_selected]
            _positions  = _simulation['positions']
            _assetName_selected      = self.GUIOs["SIMULATIONDETAIL_ASSETSELECTIONBOX"].getSelected()
            _positionSymbol_selected = self.GUIOs["SIMULATIONDETAIL_POSITIONSELECTIONBOX"].getSelected()
            if (_positionSymbol_selected == '#ALL#'):
                if (_assetName_selected == '#ALL#'): _pSymbols_selected = list(_positions.keys())
                else:                                _pSymbols_selected = [_pSymbol for _pSymbol in _positions if (_positions[_pSymbol]['quoteAsset'] == _assetName_selected)]
            else: _pSymbols_selected = [_positionSymbol_selected,]
            _currencyAnalysisConfigurations_selected = set()
            _tradeConfigurations_selected            = set()
            for _pSymbol in _pSymbols_selected:
                _currencyAnalysisConfigurations_selected.add(_positions[_pSymbol]['currencyAnalysisConfigurationCode'])
                _tradeConfigurations_selected.add(_positions[_pSymbol]['tradeConfigurationCode'])
            _currencyAnalysisConfigurations_selectionList = dict()
            _tradeConfigurations_selectionList            = dict()
            for _cacCode in _currencyAnalysisConfigurations_selected: _currencyAnalysisConfigurations_selectionList[_cacCode] = {'text': _cacCode, 'textAnchor': 'W'}
            for _tcCode in _tradeConfigurations_selected:             _tradeConfigurations_selectionList[_tcCode]             = {'text': _tcCode,  'textAnchor': 'W'}
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIURATIONSELECTIONBOX"].setSelectionList(selectionList = _currencyAnalysisConfigurations_selectionList, keepSelected = True, displayTargets = 'all', callSelectionUpdateFunction = True)
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIURATIONSELECTIONBOX"].setSelectionList(selectionList            = _tradeConfigurations_selectionList,            keepSelected = True, displayTargets = 'all', callSelectionUpdateFunction = True)
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIURATIONSELECTIONBOX"].activate()
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIURATIONSELECTIONBOX"].activate()
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_NCURRENCYANALYSISCONFIURATIONSDISPLAYTEXT"].updateText(text = "{:d} / {:d}".format(len(_currencyAnalysisConfigurations_selectionList), len(_simulation['currencyAnalysisConfigurations'])))
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_NTRADECONFIURATIONSDISPLAYTEXT"].updateText(text            = "{:d} / {:d}".format(len(_tradeConfigurations_selectionList),            len(_simulation['tradeConfigurations'])))
        else:
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIURATIONSELECTIONBOX"].clearSelectionList()
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIURATIONSELECTIONBOX"].clearSelectionList()
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIURATIONSELECTIONBOX"].setSelected(itemKey = None, callSelectionUpdateFunction = False)
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIURATIONSELECTIONBOX"].setSelected(itemKey = None, callSelectionUpdateFunction = False)
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIURATIONSELECTIONBOX"].deactivate()
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIURATIONSELECTIONBOX"].deactivate()
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_NCURRENCYANALYSISCONFIURATIONSDISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_NTRADECONFIURATIONSDISPLAYTEXT"].updateText(text            = "-")
    def __loadCurrencyAnalysisConfiguration_Configurations():
        _cacCode_selected = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIURATIONSELECTIONBOX"].getSelected()
        if (_cacCode_selected is not None):
            _cac = self.puVar['simulations'][self.puVar['simulation_selected']]['currencyAnalysisConfigurations'][_cacCode_selected]
            #MAIN
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MAIN"]
            _subPage.GUIOs["INDICATORMASTERSWITCH_SMA"].setStatus(status        = _cac['SMA_Master'],        callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_EMA"].setStatus(status        = _cac['EMA_Master'],        callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_WMA"].setStatus(status        = _cac['WMA_Master'],        callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_PSAR"].setStatus(status       = _cac['PSAR_Master'],       callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_BOL"].setStatus(status        = _cac['BOL_Master'],        callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_IVP"].setStatus(status        = _cac['IVP_Master'],        callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_SWING"].setStatus(status      = _cac['SWING_Master'],      callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_VOL"].setStatus(status        = _cac['VOL_Master'],        callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_NNA"].setStatus(status        = _cac['NNA_Master'],        callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_MMACDSHORT"].setStatus(status = _cac['MMACDSHORT_Master'], callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_MMACDLONG"].setStatus(status  = _cac['MMACDLONG_Master'],  callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_DMIxADX"].setStatus(status    = _cac['DMIxADX_Master'],    callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_MFI"].setStatus(status        = _cac['MFI_Master'],        callStatusUpdateFunction = False)
            _subPage.GUIOs["MINCOMPLETEANALYSISDISPLAYTEXT"].updateText(text    = str(_cac['NI_MinCompleteAnalysis']))
            _subPage.GUIOs["NANALYSISDISPLAYDISPLAYTEXT"].updateText(text       = str(_cac['NI_NAnalysisToDisplay']))
            #SMA
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_SMA"]
            for lineIndex in range (atmEta_Constants.NLINES_SMA):
                lineActive = _cac.get(f'SMA_{lineIndex}_LineActive', False)
                if lineActive: nSamples_str = f"{_cac[f'SMA_{lineIndex}_NSamples']}"
                else:          nSamples_str = "-"
                _subPage.GUIOs[f"SMA_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"SMA_{lineIndex}_NSAMPLES"].updateText(text = nSamples_str)
            #WMA
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_WMA"]
            for lineIndex in range (atmEta_Constants.NLINES_WMA):
                lineActive = _cac.get(f'WMA_{lineIndex}_LineActive', False)
                if lineActive: nSamples_str = f"{_cac[f'WMA_{lineIndex}_NSamples']}"
                else:          nSamples_str = "-"
                _subPage.GUIOs[f"WMA_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"WMA_{lineIndex}_NSAMPLES"].updateText(text = nSamples_str)
            #EMA
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_EMA"]
            for lineIndex in range (atmEta_Constants.NLINES_EMA):
                lineActive = _cac.get(f'EMA_{lineIndex}_LineActive', False)
                if lineActive: nSamples_str = f"{_cac[f'EMA_{lineIndex}_NSamples']}"
                else:          nSamples_str = "-"
                _subPage.GUIOs[f"EMA_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"EMA_{lineIndex}_NSAMPLES"].updateText(text = nSamples_str)
            #PSAR
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_PSAR"]
            for lineIndex in range (atmEta_Constants.NLINES_PSAR):
                lineActive = _cac.get(f'PSAR_{lineIndex}_LineActive', False)
                if lineActive: 
                    af0_str    = f"{_cac[f'PSAR_{lineIndex}_AF0']:.3f}"
                    afPlus_str = f"{_cac[f'PSAR_{lineIndex}_AF+']:.3f}"
                    afMax_str  = f"{_cac[f'PSAR_{lineIndex}_AFMax']:.3f}"
                else:          
                    af0_str    = "-"
                    afPlus_str = "-"
                    afMax_str  = "-"
                _subPage.GUIOs[f"PSAR_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"PSAR_{lineIndex}_AF0"].updateText(text   = af0_str)
                _subPage.GUIOs[f"PSAR_{lineIndex}_AF+"].updateText(text   = afPlus_str)
                _subPage.GUIOs[f"PSAR_{lineIndex}_AFMAX"].updateText(text = afMax_str)
            #BOL
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_BOL"]
            _subPage.GUIOs["BOLMATYPEDISPLAYTEXT"].updateText(text = self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_{:s}'.format(_cac['BOL_MAType'])))
            for lineIndex in range (atmEta_Constants.NLINES_BOL):

                lineActive = _cac.get(f'BOL_{lineIndex}_LineActive', False)
                if lineActive: 
                    nSamples_str  = f"{_cac[f'BOL_{lineIndex}_NSamples']}"
                    bandWidth_str = f"{_cac[f'BOL_{lineIndex}_BandWidth']:.1f}"
                else:          
                    nSamples_str  = "-"
                    bandWidth_str = "-"
                _subPage.GUIOs[f"BOL_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"BOL_{lineIndex}_NSAMPLES"].updateText(text  = nSamples_str)
                _subPage.GUIOs[f"BOL_{lineIndex}_BANDWIDTH"].updateText(text = bandWidth_str)
            #IVP
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_IVP"]
            _subPage.GUIOs["NSAMPLESDISPLAYTEXT"].updateText(text = f"{_cac['IVP_NSamples']}")
            _subPage.GUIOs["GAMMAFACTORDISPLAYTEXT"].updateText(text = f"{_cac['IVP_GammaFactor']*100:.1f} %")
            _subPage.GUIOs["DELTAFACTORDISPLAYTEXT"].updateText(text = f"{_cac['IVP_DeltaFactor']*100:.0f} %")
            #SWING
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_SWING"]
            for lineIndex in range (atmEta_Constants.NLINES_SWING):
                lineActive = _cac.get(f'SWING_{lineIndex}_LineActive', False)
                if lineActive: 
                    swingRange_str = f"{_cac[f'SWING_{lineIndex}_SwingRange']:.4f}"
                else:          
                    swingRange_str = "-"
                _subPage.GUIOs[f"SWING_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"SWING_{lineIndex}_SWINGRANGE"].updateText(text = swingRange_str)
            #VOL
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_VOL"]
            maType = _cac['VOL_MAType']
            _subPage.GUIOs["MATYPEDISPLAYTEXT"].updateText(text = self.visualManager.getTextPack(f'SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_{maType}'))
            for lineIndex in range (atmEta_Constants.NLINES_VOL):
                lineActive = _cac.get(f'VOL_{lineIndex}_LineActive', False)
                if lineActive: nSamples_str = f"{_cac[f'VOL_{lineIndex}_NSamples']}"
                else:          nSamples_str = "-"
                _subPage.GUIOs[f"VOL_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"VOL_{lineIndex}_NSAMPLES"].updateText(text = nSamples_str)
            #NNA
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_NNA"]
            for lineIndex in range (atmEta_Constants.NLINES_NNA):
                lineActive = _cac.get(f'NNA_{lineIndex}_LineActive', False)
                if lineActive: 
                    nnCode = _cac[f'NNA_{lineIndex}_NeuralNetworkCode']
                    nnCode_str = "" if nnCode is None else f"{nnCode}"
                    alpha_str  = f"{_cac[f'NNA_{lineIndex}_Alpha']:.2f}"
                    beta_str   = f"{_cac[f'NNA_{lineIndex}_Beta']}"
                else:          
                    nnCode_str = "-"
                    alpha_str  = "-"
                    beta_str   = "-"
                _subPage.GUIOs[f"NNA_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"NNA_{lineIndex}_NNCODE"].updateText(text = nnCode_str)
                _subPage.GUIOs[f"NNA_{lineIndex}_ALPHA"].updateText(text  = alpha_str)
                _subPage.GUIOs[f"NNA_{lineIndex}_BETA"].updateText(text   = beta_str)
            #MMACDSHORT
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MMACDSHORT"]
            signalNSamples = _cac['MMACDSHORT_SignalNSamples']
            multiplier     = _cac['MMACDSHORT_Multiplier']
            _subPage.GUIOs["MMACDSIGNALINTERVALDISPLAYTEXT"].updateText(text = f"{signalNSamples}")
            _subPage.GUIOs["MULTIPLIERDISPLAYTEXT"].updateText(text          = f"{multiplier}")
            for lineIndex in range (atmEta_Constants.NLINES_MMACDSHORT):
                lineActive = _cac.get(f'MMACDSHORT_MA{lineIndex}_LineActive', False)
                if lineActive: nSamples_str = f"{_cac[f'MMACDSHORT_MA{lineIndex}_NSamples']}"
                else:          nSamples_str = "-"
                _subPage.GUIOs[f"MA{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"MA{lineIndex}_NSAMPLES"].updateText(text = nSamples_str)
            #MMACDLONG
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MMACDLONG"]
            signalNSamples = _cac['MMACDLONG_SignalNSamples']
            multiplier     = _cac['MMACDLONG_Multiplier']
            _subPage.GUIOs["MMACDSIGNALINTERVALDISPLAYTEXT"].updateText(text = f"{signalNSamples}")
            _subPage.GUIOs["MULTIPLIERDISPLAYTEXT"].updateText(text          = f"{multiplier}")
            for lineIndex in range (atmEta_Constants.NLINES_MMACDLONG):
                lineActive = _cac.get(f'MMACDLONG_MA{lineIndex}_LineActive', False)
                if lineActive: nSamples_str = f"{_cac[f'MMACDLONG_MA{lineIndex}_NSamples']}"
                else:          nSamples_str = "-"
                _subPage.GUIOs[f"MA{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"MA{lineIndex}_NSAMPLES"].updateText(text = nSamples_str)
            #DMIxADX
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_DMIxADX"]
            for lineIndex in range (atmEta_Constants.NLINES_DMIxADX):
                lineActive = _cac.get(f'DMIxADX_{lineIndex}_LineActive', False)
                if lineActive: nSamples_str = f"{_cac[f'DMIxADX_{lineIndex}_NSamples']}"
                else:          nSamples_str = "-"
                _subPage.GUIOs[f"DMIxADX_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"DMIxADX_{lineIndex}_NSAMPLES"].updateText(text = nSamples_str)
            #MFI
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MFI"]
            for lineIndex in range (atmEta_Constants.NLINES_MFI):
                lineActive = _cac.get(f'MFI_{lineIndex}_LineActive', False)
                if lineActive: nSamples_str = f"{_cac[f'MFI_{lineIndex}_NSamples']}"
                else:          nSamples_str = "-"
                _subPage.GUIOs[f"MFI_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"MFI_{lineIndex}_NSAMPLES"].updateText(text = nSamples_str)
        else:
            #MAIN
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MAIN"]
            _subPage.GUIOs["INDICATORMASTERSWITCH_SMA"].setStatus(status        = False, callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_EMA"].setStatus(status        = False, callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_WMA"].setStatus(status        = False, callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_PSAR"].setStatus(status       = False, callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_BOL"].setStatus(status        = False, callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_IVP"].setStatus(status        = False, callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_SWING"].setStatus(status      = False, callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_VOL"].setStatus(status        = False, callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_NNA"].setStatus(status        = False, callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_MMACDSHORT"].setStatus(status = False, callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_MMACDLONG"].setStatus(status  = False, callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_DMIxADX"].setStatus(status    = False, callStatusUpdateFunction = False)
            _subPage.GUIOs["INDICATORMASTERSWITCH_MFI"].setStatus(status        = False, callStatusUpdateFunction = False)
            _subPage.GUIOs["MINCOMPLETEANALYSISDISPLAYTEXT"].updateText(text = "-")
            _subPage.GUIOs["NANALYSISDISPLAYDISPLAYTEXT"].updateText(text    = "-")
            #SMA
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_SMA"]
            for lineIndex in range (atmEta_Constants.NLINES_SMA):
                _subPage.GUIOs[f"SMA_{lineIndex}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"SMA_{lineIndex}_NSAMPLES"].updateText(text = "-")
            #WMA
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_WMA"]
            for lineIndex in range (atmEta_Constants.NLINES_WMA):
                _subPage.GUIOs[f"WMA_{lineIndex}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"WMA_{lineIndex}_NSAMPLES"].updateText(text = "-")
            #EMA
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_EMA"]
            for lineIndex in range (atmEta_Constants.NLINES_EMA):
                _subPage.GUIOs[f"EMA_{lineIndex}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"EMA_{lineIndex}_NSAMPLES"].updateText(text = "-")
            #PSAR
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_PSAR"]
            for lineIndex in range (atmEta_Constants.NLINES_PSAR):
                _subPage.GUIOs[f"PSAR_{lineIndex}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"PSAR_{lineIndex}_AF0"].updateText(text   = "-")
                _subPage.GUIOs[f"PSAR_{lineIndex}_AF+"].updateText(text   = "-")
                _subPage.GUIOs[f"PSAR_{lineIndex}_AFMAX"].updateText(text = "-")
            #BOL
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_BOL"]
            _subPage.GUIOs["BOLMATYPEDISPLAYTEXT"].updateText(text = "-")
            for lineIndex in range (atmEta_Constants.NLINES_BOL):
                _subPage.GUIOs[f"BOL_{lineIndex}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"BOL_{lineIndex}_NSAMPLES"].updateText(text  = "-")
                _subPage.GUIOs[f"BOL_{lineIndex}_BANDWIDTH"].updateText(text = "-")
            #IVP
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_IVP"]
            _subPage.GUIOs["NSAMPLESDISPLAYTEXT"].updateText(text    = "-")
            _subPage.GUIOs["GAMMAFACTORDISPLAYTEXT"].updateText(text = "-")
            _subPage.GUIOs["DELTAFACTORDISPLAYTEXT"].updateText(text = "-")
            #SWING
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_SWING"]
            for lineIndex in range (atmEta_Constants.NLINES_SWING):
                _subPage.GUIOs[f"SWING_{lineIndex}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"SWING_{lineIndex}_SWINGRANGE"].updateText(text = "-")
            #VOL
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_VOL"]
            _subPage.GUIOs["MATYPEDISPLAYTEXT"].updateText(text = "-")
            for lineIndex in range (atmEta_Constants.NLINES_VOL):
                _subPage.GUIOs[f"VOL_{lineIndex}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"VOL_{lineIndex}_NSAMPLES"].updateText(text = "-")
            #NNA
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_NNA"]
            for lineIndex in range (atmEta_Constants.NLINES_NNA):
                _subPage.GUIOs[f"NNA_{lineIndex}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"NNA_{lineIndex}_NNCODE"].updateText(text = "-")
                _subPage.GUIOs[f"NNA_{lineIndex}_ALPHA"].updateText(text  = "-")
                _subPage.GUIOs[f"NNA_{lineIndex}_BETA"].updateText(text   = "-")
            #MMACDSHORT
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MMACDSHORT"]
            _subPage.GUIOs["MMACDSIGNALINTERVALDISPLAYTEXT"].updateText(text = "-")
            _subPage.GUIOs["MULTIPLIERDISPLAYTEXT"].updateText(text          = "-")
            for lineIndex in range (atmEta_Constants.NLINES_MMACDSHORT):
                _subPage.GUIOs[f"MA{lineIndex}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"MA{lineIndex}_NSAMPLES"].updateText(text = "-")
            #MMACDLONG
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MMACDLONG"]
            _subPage.GUIOs["MMACDSIGNALINTERVALDISPLAYTEXT"].updateText(text = "-")
            _subPage.GUIOs["MULTIPLIERDISPLAYTEXT"].updateText(text          = "-")
            for lineIndex in range (atmEta_Constants.NLINES_MMACDLONG):
                _subPage.GUIOs[f"MA{lineIndex}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"MA{lineIndex}_NSAMPLES"].updateText(text = "-")
            #DMIxADX
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_DMIxADX"]
            for lineIndex in range (atmEta_Constants.NLINES_DMIxADX):
                _subPage.GUIOs[f"DMIxADX_{lineIndex}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"DMIxADX_{lineIndex}_NSAMPLES"].updateText(text = "-")
            #MFI
            _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MFI"]
            for lineIndex in range (atmEta_Constants.NLINES_MFI):
                _subPage.GUIOs[f"MFI_{lineIndex}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
                _subPage.GUIOs[f"MFI_{lineIndex}_NSAMPLES"].updateText(text = "-")
    def __loadTradeConfiguration_Configurations():
        _tcCode_selected = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIURATIONSELECTIONBOX"].getSelected()
        _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIGURATIONSUBPAGE"]
        if (_tcCode_selected is None):
            #Base
            _subPage.GUIOs["LEVERAGEDISPLAYTEXT"].updateText(text               = "-")
            _subPage.GUIOs["MARGINTYPEDISPLAYTEXT"].updateText(text             = "-")
            _subPage.GUIOs["DIRECTIONDISPLAYTEXT"].updateText(text              = "-")
            _subPage.GUIOs["FULLSTOPLOSSIMMEDIATEDISPLAYTEXT"].updateText(text  = "-")
            _subPage.GUIOs["FULLSTOPLOSSCLOSEDISPLAYTEXT"].updateText(text      = "-")
            _subPage.GUIOs["POSTSTOPLOSSREENTRYSWITCH"].setStatus(status        = False)
            #RQPM
            _subPage.GUIOs["RQPM_FUNCTIONTYPEDISPLAYTEXT"].updateText(text      = "-")
            self.pageAuxillaryFunctions['SETRQPMFUNCTINOPARAMETERS_CONFIGURATIONS']()
        else:
            #Base
            _tc = self.puVar['simulations'][self.puVar['simulation_selected']]['tradeConfigurations'][_tcCode_selected]
            _subPage.GUIOs["LEVERAGEDISPLAYTEXT"].updateText(text   = "X {:d}".format(_tc['leverage']))
            if (_tc['isolated'] == False): _subPage.GUIOs["MARGINTYPEDISPLAYTEXT"].updateText(text = self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_MARGINTYPE_CROSSED'))
            else:                          _subPage.GUIOs["MARGINTYPEDISPLAYTEXT"].updateText(text = self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_MARGINTYPE_ISOLATED'))
            _subPage.GUIOs["DIRECTIONDISPLAYTEXT"].updateText(text = _tc['direction'])
            if (_tc['fullStopLossImmediate'] is None): _subPage.GUIOs["FULLSTOPLOSSIMMEDIATEDISPLAYTEXT"].updateText(text = "-")
            else:                                      _subPage.GUIOs["FULLSTOPLOSSIMMEDIATEDISPLAYTEXT"].updateText(text = "{:.2f} %".format(_tc['fullStopLossImmediate']*100))
            if (_tc['fullStopLossClose'] is None):     _subPage.GUIOs["FULLSTOPLOSSCLOSEDISPLAYTEXT"].updateText(text = "-")
            else:                                      _subPage.GUIOs["FULLSTOPLOSSCLOSEDISPLAYTEXT"].updateText(text = "{:.2f} %".format(_tc['fullStopLossClose']*100))
            _subPage.GUIOs["POSTSTOPLOSSREENTRYSWITCH"].setStatus(status = _tc['postStopLossReentry'])
            #RQPM
            if (_tc['rqpm_functionType'] == None): _subPage.GUIOs["RQPM_FUNCTIONTYPEDISPLAYTEXT"].updateText(text = "-")
            else:                                  _subPage.GUIOs["RQPM_FUNCTIONTYPEDISPLAYTEXT"].updateText(text = "{:s}".format(_tc['rqpm_functionType']))
            self.pageAuxillaryFunctions['SETRQPMFUNCTINOPARAMETERS_CONFIGURATIONS']()
    def __setRQPMFunctionParameters_Configurations():
        _tcCode_selected = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIURATIONSELECTIONBOX"].getSelected()
        _subPage = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIGURATIONSUBPAGE"]
        #TC Code Check
        if (_tcCode_selected is None): 
            _subPage.GUIOs["RQPM_PARAMETERSSELECTIONBOX"].clearSelectionList()
            return
        #TC
        _tc = self.puVar['simulations'][self.puVar['simulation_selected']]['tradeConfigurations'][_tcCode_selected]
        _functionType = _tc['rqpm_functionType']
        #Function Type Check
        if (_functionType is None): 
            _subPage.GUIOs["RQPM_PARAMETERSSELECTIONBOX"].clearSelectionList()
            return
        #Parameters Update
        _functionDescriptor = atmEta_RQPMFunctions.RQPMFUNCTIONS_DESCRIPTORS[_functionType]
        _rqpmParams_selectionList = dict()
        _nParams = len(_functionDescriptor)
        for _paramIndex, _paramDescriptor in enumerate(_functionDescriptor):
            _index_str = f"{_paramIndex+1:d} / {_nParams:d}"                                              #[0]: Index
            _name_str  = f"{_paramDescriptor['name']}"                                                    #[1]: Name
            _value_str = f"{_paramDescriptor['val_to_str'](x = _tc['rqpm_functionParams'][_paramIndex])}" #[2]: Value
            #Finally
            _rqpmParams_selectionList[_paramIndex] = [{'text': _index_str},
                                                      {'text': _name_str},
                                                      {'text': _value_str}]
        _subPage.GUIOs["RQPM_PARAMETERSSELECTIONBOX"].setSelectionList(selectionList = _rqpmParams_selectionList, keepSelected = False, displayTargets = 'all', callSelectionUpdateFunction = False)
    auxFunctions['SETCONFIGURATIONSLIST_CONFIGURATIONS']             = __setConfigurationsList_Configurations
    auxFunctions['LOADCURRENCYANALYSISCONFIGURATION_CONFIGURATIONS'] = __loadCurrencyAnalysisConfiguration_Configurations
    auxFunctions['LOADTRADECONFIGURATION_CONFIGURATIONS']            = __loadTradeConfiguration_Configurations
    auxFunctions['SETRQPMFUNCTINOPARAMETERS_CONFIGURATIONS']         = __setRQPMFunctionParameters_Configurations
    #---Trade Logs
    def __farr_onTradeLogsFetchResponse_TradeLogs(responder, requestID, functionResult):
        if (functionResult['simulationCode'] == self.puVar['simulation_selected']):
            if (functionResult['result'] == True):
                self.puVar['simulation_selected_tradeLogs'] = functionResult['tradeLogs']
                if (self.puVar['simulationDetailView_selected'] == 'TRADELOGS'): 
                    self.puVar['simulationDetailView_firstLoad']['TRADELOGS'] = True
                    self.pageAuxillaryFunctions['ONSIMULATIONVIEWUPDATE']()
            else: print(termcolor.colored("[GUI] Simulation {:s} Daily Reports Fetch Failed: {:s}".format(functionResult['simulationCode'], functionResult['failureType']), 'light_red'))
    def __setTradeLogsList_TradeLogs():
        if (self.puVar['simulation_selected_tradeLogs'] is None):
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TRADELOGSELECTIONBOX"].clearSelectionList()
            self.pageAuxillaryFunctions['ONTRADELOGSFILTERUPDATE_TRADELOGS']()
            return
        _positions = self.puVar['simulations'][self.puVar['simulation_selected']]['positions']
        _nTradeLogs = len(self.puVar['simulation_selected_tradeLogs'])
        tradeLogs_selectionList = dict()
        for _tradeLog in self.puVar['simulation_selected_tradeLogs']:
            _positionSymbol = _tradeLog['positionSymbol']
            _position = _positions[_positionSymbol]
            _position_quoteAsset = _position['quoteAsset']
            _position_precisions = _position['precisions']
            #[0]: Index
            _index_str = f"{_tradeLog['logIndex']+1:,d} / {_nTradeLogs:,d}"
            #[1]: Time
            _time_str = datetime.fromtimestamp(_tradeLog['timestamp'], tz=timezone.utc).strftime("%Y/%m/%d %H:%M")
            #[2]: Symbol
            _symbol_str = _positionSymbol
            #[3]: Logic Source
            _logicSource_str = _tradeLog['logicSource']
            #[4]: Side
            if   (_tradeLog['side'] == 'BUY'):         _side_str = self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_TRADELOG_SIDE_BUY');         _side_str_color = 'GREEN_LIGHT'
            elif (_tradeLog['side'] == 'SELL'):        _side_str = self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_TRADELOG_SIDE_SELL');        _side_str_color = 'RED_LIGHT'
            elif (_tradeLog['side'] == 'LIQUIDATION'): _side_str = self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_TRADELOG_SIDE_LIQUIDATION'); _side_str_color = 'VIOLET_LIGHT'
            #[5]: Quantity
            _quantity_str = atmEta_Auxillaries.floatToString(number = _tradeLog['quantity'], precision = _position_precisions['quantity'])
            #[6]: Price
            _price_str = atmEta_Auxillaries.floatToString(number = _tradeLog['price'], precision = _position_precisions['price'])
            #[7]: Profit
            if   (0 < _tradeLog['profit']):  _profit_str = "+"+atmEta_Auxillaries.floatToString(number = _tradeLog['profit'], precision = _ASSETPRECISIONS_XS[_position_quoteAsset]); _profit_str_color = 'GREEN_LIGHT'
            elif (_tradeLog['profit'] == 0): _profit_str =     atmEta_Auxillaries.floatToString(number = _tradeLog['profit'], precision = _ASSETPRECISIONS_XS[_position_quoteAsset]); _profit_str_color = 'DEFAULT'
            elif (_tradeLog['profit'] < 0):  _profit_str =     atmEta_Auxillaries.floatToString(number = _tradeLog['profit'], precision = _ASSETPRECISIONS_XS[_position_quoteAsset]); _profit_str_color = 'RED_LIGHT'
            #[8]: Trading Fee
            _tradingFee_str = atmEta_Auxillaries.floatToString(number = _tradeLog['tradingFee'], precision = _ASSETPRECISIONS_XS[_position_quoteAsset])
            #[9]: Total Quantity
            _totalQuantity_str = atmEta_Auxillaries.floatToString(number = _tradeLog['totalQuantity'], precision = _position_precisions['quantity'])
            #[10]: Entry Price
            if (_tradeLog['entryPrice'] is None): _entryPrice_str = "-"
            else:                                 _entryPrice_str = atmEta_Auxillaries.floatToString(number = _tradeLog['entryPrice'], precision = _position_precisions['price'])
            #[11]: Wallet Balance
            _walletBalance_str = atmEta_Auxillaries.floatToString(number = _tradeLog['walletBalance'], precision = _ASSETPRECISIONS_XS[_position_quoteAsset])
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
        self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TRADELOGSELECTIONBOX"].setSelectionList(selectionList = tradeLogs_selectionList, keepSelected = False, displayTargets = 'all', callSelectionUpdateFunction = False)
        self.pageAuxillaryFunctions['ONTRADELOGSFILTERUPDATE_TRADELOGS']()
    def __onTradeLogsFilterUpdate_TradeLogs():
        simulation_selected = self.puVar['simulation_selected']

        #[1]: No Simulation Selected
        if (simulation_selected is None):
            #[1-1]: Net Proft, Gain, Loss, Trading Fee Display Update
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NETPROFITDISPLAYTEXT"].updateText(text  = "-", textStyle = 'DEFAULT')
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_GAINDISPLAYTEXT"].updateText(text       = "-")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_LOSSDISPLAYTEXT"].updateText(text       = "-")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TRADINGFEEDISPLAYTEXT"].updateText(text = "-")
            #[1-2]: Logs Counter Display Update
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NTOTALLOGSDISPLAYTEXT"].updateText(text    = "- / -")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NASSETLOGSDISPLAYTEXT"].updateText(text    = "- / -")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NPOSITIONLOGSDISPLAYTEXT"].updateText(text = "- / -")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NTIMELOGSDISPLAYTEXT"].updateText(text     = "- / -")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NBUYDISPLAYTEXT"].updateText(text          = "- / -")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NSELLDISPLAYTEXT"].updateText(text         = "- / -")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NFSLIMMEDDISPLAYTEXT"].updateText(text     = "- / -")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NFSLCLOSEDISPLAYTEXT"].updateText(text     = "- / -")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NENTRYDISPLAYTEXT"].updateText(text        = "- / -")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NLIQUIDATIONDISPLAYTEXT"].updateText(text  = "- / -")
            #[1-3]: Finally
            return

        #[2]: Simulation Data
        simulation_positions      = self.puVar['simulations'][simulation_selected]['positions']
        asset_selected            = self.GUIOs["SIMULATIONDETAIL_ASSETSELECTIONBOX"].getSelected()
        position_selected         = self.GUIOs["SIMULATIONDETAIL_POSITIONSELECTIONBOX"].getSelected()
        tradeLogs                 = self.puVar['simulation_selected_tradeLogs'] if (self.puVar['simulation_selected_tradeLogs'] is not None) else list()
        tradeLogs_filteredIndexes = set()

        #[3]: Filter Params
        if (True):
            _filter_time_beg_str = self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TIMEFILTERINPUTTEXT1"].getText()
            _filter_time_end_str = self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TIMEFILTERINPUTTEXT2"].getText()
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
            _filter_side_buy         = self.GUIOs["SIMULATIONDETAIL_TRADELOGS_SIDEFILTERBUY"].getStatus()
            _filter_side_sell        = self.GUIOs["SIMULATIONDETAIL_TRADELOGS_SIDEFILTERSELL"].getStatus()
            _filter_side_liquidation = self.GUIOs["SIMULATIONDETAIL_TRADELOGS_SIDEFILTERLIQUIDATION"].getStatus()
            _filter_logicSource_fslImmed = self.GUIOs["SIMULATIONDETAIL_TRADELOGS_LOGICSOURCEFILTERFSLIMMED"].getStatus()
            _filter_logicSource_fslClose = self.GUIOs["SIMULATIONDETAIL_TRADELOGS_LOGICSOURCEFILTERFSLCLOSE"].getStatus()
            _filter_logicSource_entry    = self.GUIOs["SIMULATIONDETAIL_TRADELOGS_LOGICSOURCEFILTERENTRY"].getStatus()
            _filter_logicSource_clear    = self.GUIOs["SIMULATIONDETAIL_TRADELOGS_LOGICSOURCEFILTERCLEAR"].getStatus()
            _filter_logicSource_exit     = self.GUIOs["SIMULATIONDETAIL_TRADELOGS_LOGICSOURCEFILTEREXIT"].getStatus()
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
        #[4]: Filtering
        if (True):
            for _logIndex, _log in enumerate(tradeLogs):
                _test_asset       = False
                _test_symbol      = False
                _test_time        = False
                _test_side        = False
                _test_logicSource = False
                #Asset
                if   (_filter['asset'] == '#ALL#'):                                                    _test_asset = True
                elif (_filter['asset'] == simulation_positions[_log['positionSymbol']]['quoteAsset']): _test_asset = True
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
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TRADELOGSELECTIONBOX"].setDisplayTargets(displayTargets = list(tradeLogs_filteredIndexes))
        #[5]: Net Proft, Gain, Loss, Trading Fee Display Update
        if (True):
            if (asset_selected == '#ALL#'):
                self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NETPROFITDISPLAYTEXT"].updateText(text  = "N/A", textStyle = 'DEFAULT')
                self.GUIOs["SIMULATIONDETAIL_TRADELOGS_GAINDISPLAYTEXT"].updateText(text       = "N/A")
                self.GUIOs["SIMULATIONDETAIL_TRADELOGS_LOSSDISPLAYTEXT"].updateText(text       = "N/A")
                self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TRADINGFEEDISPLAYTEXT"].updateText(text = "N/A")
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
                self.GUIOs["SIMULATIONDETAIL_TRADELOGS_GAINDISPLAYTEXT"].updateText(text       = f"{atmEta_Auxillaries.floatToString(number = _gain,       precision = _ASSETPRECISIONS_XS[asset_selected])} {asset_selected}")
                self.GUIOs["SIMULATIONDETAIL_TRADELOGS_LOSSDISPLAYTEXT"].updateText(text       = f"{atmEta_Auxillaries.floatToString(number = _loss,       precision = _ASSETPRECISIONS_XS[asset_selected])} {asset_selected}")
                self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TRADINGFEEDISPLAYTEXT"].updateText(text = f"{atmEta_Auxillaries.floatToString(number = _tradingFee, precision = _ASSETPRECISIONS_XS[asset_selected])} {asset_selected}")
                _netProfit = round(_gain-_loss-_tradingFee, _ASSETPRECISIONS[asset_selected])
                if   (_netProfit < 0):  str = f"{atmEta_Auxillaries.floatToString(number  = _netProfit, precision = _ASSETPRECISIONS_XS[asset_selected])}"; strCol = 'RED_LIGHT'
                elif (_netProfit == 0): str = f"{atmEta_Auxillaries.floatToString(number  = _netProfit, precision = _ASSETPRECISIONS_XS[asset_selected])}"; strCol = 'DEFAULT'
                else:                   str = f"+{atmEta_Auxillaries.floatToString(number = _netProfit, precision = _ASSETPRECISIONS_XS[asset_selected])}"; strCol = 'GREEN_LIGHT'
                _netProfit_text = ""; _netProfit_textStyle = list()
                for _newTextString, _newTextStyle in ((str,                  strCol), 
                                                      (f" {asset_selected}", 'DEFAULT')):
                    _netProfit_textStyle.append(((len(_netProfit_text), len(_netProfit_text)+len(_newTextString)-1), _newTextStyle))
                    _netProfit_text += _newTextString
                self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NETPROFITDISPLAYTEXT"].updateText(text = _netProfit_text, textStyle = _netProfit_textStyle)
        #[6]: Logs Counter Display Update
        if (True):
            #Setup
            #---[6-1]: Total
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
            #Counting
            for _logIndex, _log in enumerate(tradeLogs):
                _isViewing = (_logIndex in tradeLogs_filteredIndexes)
                #Main
                _test_asset    = ((_filter['asset'] == '#ALL#') or (_filter['asset'] == simulation_positions[_log['positionSymbol']]['quoteAsset']))
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
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NTOTALLOGSDISPLAYTEXT"].updateText(text    = f"{_nLogs_total_viewing:,d} / {_nLogs_total_total:,d}")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NASSETLOGSDISPLAYTEXT"].updateText(text    = f"{_nLogs_asset_viewing:,d} / {_nLogs_asset_total:,d}")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NPOSITIONLOGSDISPLAYTEXT"].updateText(text = f"{_nLogs_position_viewing:,d} / {_nLogs_position_total:,d}")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NTIMELOGSDISPLAYTEXT"].updateText(text     = f"{_nLogs_time_viewing:,d} / {_nLogs_time_total:,d}")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NBUYDISPLAYTEXT"].updateText(text          = f"{_nLogs_buy_viewing:,d} / {_nLogs_buy_total:,d}")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NSELLDISPLAYTEXT"].updateText(text         = f"{_nLogs_sell_viewing:,d} / {_nLogs_sell_total:,d}")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NFSLIMMEDDISPLAYTEXT"].updateText(text     = f"{_nLogs_fslImmed_viewing:,d} / {_nLogs_fslImmed_total:,d}")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NFSLCLOSEDISPLAYTEXT"].updateText(text     = f"{_nLogs_fslClose_viewing:,d} / {_nLogs_fslClose_total:,d}")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NENTRYDISPLAYTEXT"].updateText(text        = f"{_nLogs_entry_viewing:,d} / {_nLogs_entry_total:,d}")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NCLEARDISPLAYTEXT"].updateText(text        = f"{_nLogs_clear_viewing:,d} / {_nLogs_clear_total:,d}")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NEXITDISPLAYTEXT"].updateText(text         = f"{_nLogs_exit_viewing:,d} / {_nLogs_exit_total:,d}")
            self.GUIOs["SIMULATIONDETAIL_TRADELOGS_NLIQUIDATIONDISPLAYTEXT"].updateText(text  = f"{_nLogs_liquidation_viewing:,d} / {_nLogs_liquidation_total:,d}")
        #[7]: Time Filter Search Button Deactivation
        self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TIMEFILTERAPPLYBUTTON"].deactivate()
    def __onTradeLogSelectionUpdate_TradeLogs():
        if (self.puVar['simulation_selected'] != None): _positions = self.puVar['simulations'][self.puVar['simulation_selected']]['positions']
        else:                                           _positions = None
        try:    _logIndex_selected = self.GUIOs["SIMULATIONDETAIL_TRADELOGS_TRADELOGSELECTIONBOX"].getSelected()[0]
        except: _logIndex_selected = None
        if (_logIndex_selected != None):
            _tradeLog = self.puVar['simulation_selected_tradeLogs'][_logIndex_selected]
            _positionSymbol = _tradeLog['positionSymbol']
            _precisions = _positions[_positionSymbol]['precisions']
        else: pass
    auxFunctions['FARR_ONTRADELOGSFETCHRESPONSE_TRADELOGS'] = __farr_onTradeLogsFetchResponse_TradeLogs
    auxFunctions['SETTRADELOGSLIST_TRADELOGS']              = __setTradeLogsList_TradeLogs
    auxFunctions['ONTRADELOGSFILTERUPDATE_TRADELOGS']       = __onTradeLogsFilterUpdate_TradeLogs
    auxFunctions['ONTRADELOGSELECTIONUPDATE_TRADELOGS']     = __onTradeLogSelectionUpdate_TradeLogs
    #---Daily Reports
    def __setDailyReportsTarget_DailyReports():
        _simulation_selected = self.puVar['simulation_selected']
        if (_simulation_selected != None):
            _assetName_selected = self.GUIOs["SIMULATIONDETAIL_ASSETSELECTIONBOX"].getSelected()
            if (_assetName_selected != None): self.GUIOs["SIMULATIONDETAIL_DAILYREPORT_DAILYREPORTVIEWER"].setTarget(target = (_simulation_selected, _assetName_selected))
            else:                             self.GUIOs["SIMULATIONDETAIL_DAILYREPORT_DAILYREPORTVIEWER"].setTarget(target = None)
        else: self.GUIOs["SIMULATIONDETAIL_DAILYREPORT_DAILYREPORTVIEWER"].setTarget(target = None)
    auxFunctions['SETDAILYREPORTSTARGET_DAILYREPORTS'] = __setDailyReportsTarget_DailyReports
    #---Position Chart
    def __setChartDrawerTarget_PositionChart():
        _simulation_selected = self.puVar['simulation_selected']
        if (_simulation_selected != None):
            _positionSymbol_selected = self.GUIOs["SIMULATIONDETAIL_POSITIONSELECTIONBOX"].getSelected()
            if (_positionSymbol_selected != None): self.GUIOs["SIMULATIONDETAIL_POSITIONCHART_CHARTDRAWER"].setTarget(target = (_simulation_selected, _positionSymbol_selected))
            else:                                  self.GUIOs["SIMULATIONDETAIL_POSITIONCHART_CHARTDRAWER"].setTarget(target = None)
        else: self.GUIOs["SIMULATIONDETAIL_POSITIONCHART_CHARTDRAWER"].setTarget(target = None)
    auxFunctions['SETCHARTDRAWERTARGET_POSITIONCHART'] = __setChartDrawerTarget_PositionChart

    #Return the generated functions
    return auxFunctions
#AUXILALRY FUNCTIONS END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------