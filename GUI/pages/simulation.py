#ATM Modules
from re import L
import ipc
import auxiliaries
from GUI.generals import passiveGraphics_wrapperTypeC,\
                         textBox_typeA,\
                         imageBox_typeA,\
                         button_typeA,\
                         button_typeB,\
                         switch_typeB,\
                         slider_typeA,\
                         textInputBox_typeA,\
                         gaugeBar_typeA,\
                         selectionBox_typeB,\
                         selectionBox_typeC

#Python Modules
import pyglet
import time
from datetime import datetime, timezone

#Constants
_IPC_THREADTYPE_MT = ipc._THREADTYPE_MT
_IPC_THREADTYPE_AT = ipc._THREADTYPE_AT
_IPC_PRD_INVALIDADDRESS    = ipc._PRD_INVALIDADDRESS
_IPC_FAR_INVALIDFUNCTIONID = ipc._FAR_INVALIDFUNCTIONID

_SIMULATIONLISTUPDATEINTERVAL_NS = 500e6

_READABLEASSETS = ('USDT', 'USDC')
_ASSETPRECISIONS = {'USDT': 8,
                    'USDC': 8}

_ASSETPRECISIONS    = {'USDT': 8, 'USDC': 8, 'BTC': 6}
_ASSETPRECISIONS_S  = {'USDT': 4, 'USDC': 4, 'BTC': 4}
_ASSETPRECISIONS_XS = {'USDT': 2, 'USDC': 2, 'BTC': 2}

_ACCOUNT_BASEASSETALLOCATABLERATIO = 0.95

_POSITIONDATA_SELECTIONBOXCOLUMNINDEX = {'currencyAnalysisConfigurationCode': 2,
                                         'tradeConfigurationCode':            3,
                                         'isolated':                          4,
                                         'leverage':                          5,
                                         'priority':                          6,
                                         'assumedRatio':                      7,
                                         'weightedAssumedRatio':              8,
                                         'allocatedBalance':                  9,
                                         'maxAllocatedBalance':               10,
                                         'tradable':                          12}
_POSITIONDATA_SELECTIONBOXCOLUMNINDEX_AUX = {'marketStatus': 13,
                                             'minNotional':  14}

_MAXDISPLAYABLESELECTEDPOSITIONSYMBOLS = 8

#SETUP PAGE <MAIN> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def setupPage(self):
    #Set page unique variables
    self.puVar['simulatorCentral'] = dict()
    self.puVar['simulatorCentral_nSimulatorsIdentified'] = False
    self.puVar['simulatorCentral_selectedSimulator']     = None
    self.puVar['simulations']         = dict()
    self.puVar['simulation_selected'] = None
    self.puVar['simulationSetup_analysisExport'] = True
    self.puVar['currencies']                = dict()
    self.puVar['simulationSetup_positions'] = dict()
    self.puVar['simulationSetup_assets']    = dict()
    self.puVar['currencyAnalysisConfigurations'] = dict()
    self.puVar['tradeConfigurations']            = dict()

    self.puVar['simulationListUpdate_ItemsToUpdate']  = list()
    self.puVar['simulationListUpdate_LastUpdated_ns'] = 0

    for _assetName in ('USDT', 'USDC'):
        self.puVar['simulationSetup_assets'][_assetName] = {'initialWalletBalance': 0,
                                                            'allocatableBalance':   0,
                                                            'allocatedBalance':     0,
                                                            'allocationRatio':      0.500,
                                                            'assumedRatio':         0,
                                                            'weightedAssumedRatio': None,
                                                            'maxAllocatedBalance':  None,
                                                            '_positionSymbols':                set(),
                                                            '_positionSymbols_crossed':        set(),
                                                            '_positionSymbols_isolated':       set(),
                                                            '_positionSymbols_prioritySorted': list()}

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
        self.GUIOs["TITLETEXT_SIMULATION"] = textBox_typeA(**inst, groupOrder=1, xPos= 7000, yPos=8550, width=2000, height=400, style=None, text=self.visualManager.getTextPack('SIMULATION:TITLE'), fontSize = 220, textInteractable = False)

        self.GUIOs["BUTTON_MOVETO_DASHBOARD"] = button_typeB(**inst,  groupOrder=2, xPos=  50, yPos=8650, width= 300, height=300, style="styleB", releaseFunction=self.pageObjectFunctions['PAGEMOVE_DASHBOARD'], image = 'dashboardIcon_512x512.png', imageSize = (225, 225), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))
        
        #Simulators
        self.GUIOs["BLOCKTITLE_SIMULATORS"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=8350, width=5600, height=200, style="styleA", text=self.visualManager.getTextPack('SIMULATION:BLOCKTITLE_SIMULATORS'), fontSize=80)
        self.GUIOs["SIMULATORS_NUMBEROFSIMULATORSTITLETEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=8000, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:SIMULATORS_NUMBEROFSIMULATORS'),    fontSize=80, textInteractable=False)
        self.GUIOs["SIMULATORS_NUMBEROFSIMULATORSDISPLAYTEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos=1400, yPos=8000, width= 400, height=250, style="styleA", text="-",                                                                           fontSize=80, textInteractable=True)
        self.GUIOs["SIMULATORS_SIMULATORTITLETEXT"]               = textBox_typeA(**inst,      groupOrder=1, xPos=1900, yPos=8000, width= 900, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:SIMULATORS_SIMULATOR'),             fontSize=80, textInteractable=False)
        self.GUIOs["SIMULATORS_SIMULATORSELECTIONBOX"]            = selectionBox_typeB(**inst, groupOrder=2, xPos=2900, yPos=8000, width=1200, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_SIMULATORS_SIMULATORSELECTION'])
        self.GUIOs["SIMULATORS_ACTIVATIONTITLETEXT"]              = textBox_typeA(**inst,      groupOrder=1, xPos=4200, yPos=8000, width= 900, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:SIMULATORS_ACTIVATION'),            fontSize=80, textInteractable=False)
        self.GUIOs["SIMULATORS_ACTIVATIONSWITCH"]                 = switch_typeB(**inst,       groupOrder=2, xPos=5200, yPos=8000, width= 500, height=250, style="styleA", align='horizontal', switchStatus=False, statusUpdateFunction = self.pageObjectFunctions['ONSTATUSUPDATED_SIMULATORS_ACTIVATIONSWITCH'])
        self.GUIOs["SIMULATORS_SIMULATIONSCOMPLETEDTITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=7650, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:SIMULATORS_SIMULATIONSCOMPLETED'),  fontSize=80, textInteractable=False)
        self.GUIOs["SIMULATORS_SIMULATIONSCOMPLETEDDISPLAYTEXT"]  = textBox_typeA(**inst,      groupOrder=1, xPos=1200, yPos=7650, width= 700, height=250, style="styleA", text="-",                                                                           fontSize=80, textInteractable=True)
        self.GUIOs["SIMULATORS_SIMULATIONSTOTALTITLETEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos=2000, yPos=7650, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:SIMULATORS_SIMULATIONSTOTAL'),      fontSize=80, textInteractable=False)
        self.GUIOs["SIMULATORS_SIMULATIONSTOTALDISPLAYTEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos=3100, yPos=7650, width= 700, height=250, style="styleA", text="-",                                                                           fontSize=80, textInteractable=True)
        self.GUIOs["SIMULATORS_SIMULATIONSQUEUEDTITLETEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos=3900, yPos=7650, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:SIMULATORS_SIMULATIONSQUEUED'),     fontSize=80, textInteractable=False)
        self.GUIOs["SIMULATORS_SIMULATIONSQUEUEDDISPLAYTEXT"]     = textBox_typeA(**inst,      groupOrder=1, xPos=5000, yPos=7650, width= 700, height=250, style="styleA", text="-",                                                                           fontSize=80, textInteractable=True)
        self.GUIOs["SIMULATORS_SIMULATIONSPROCESSINGTITLETEXT"]   = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=7300, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:SIMULATORS_SIMULATIONSPROCESSING'), fontSize=80, textInteractable=False)
        self.GUIOs["SIMULATORS_SIMULATIONSPROCESSINGDISPLAYTEXT"] = textBox_typeA(**inst,      groupOrder=1, xPos=1200, yPos=7300, width= 700, height=250, style="styleA", text="-",                                                                           fontSize=80, textInteractable=True)
        self.GUIOs["SIMULATORS_SIMULATIONSPAUSEDTITLETEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos=2000, yPos=7300, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:SIMULATORS_SIMULATIONSPAUSED'),     fontSize=80, textInteractable=False)
        self.GUIOs["SIMULATORS_SIMULATIONSPAUSEDDISPLAYTEXT"]     = textBox_typeA(**inst,      groupOrder=1, xPos=3100, yPos=7300, width= 700, height=250, style="styleA", text="-",                                                                           fontSize=80, textInteractable=True)
        self.GUIOs["SIMULATORS_SIMULATIONSERRORTITLETEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos=3900, yPos=7300, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:SIMULATORS_SIMULATIONSERROR'),      fontSize=80, textInteractable=False)
        self.GUIOs["SIMULATORS_SIMULATIONSERRORDISPLAYTEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos=5000, yPos=7300, width= 700, height=250, style="styleA", text="-",                                                                           fontSize=80, textInteractable=True)

        #Simulations
        self.GUIOs["BLOCKTITLE_SIMULATIONS"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=7000, width=5600, height=200, style="styleA", text=self.visualManager.getTextPack('SIMULATION:BLOCKTITLE_SIMULATIONS'), fontSize=80)
        self.GUIOs["SIMULATIONS_SEARCHTITLETEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=6650, width= 700, height= 250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:SIMULATIONS_SEARCH'),       fontSize=80, textInteractable=False)
        self.GUIOs["SIMULATIONS_SEARCHTEXTINPUTBOX"]       = textInputBox_typeA(**inst, groupOrder=1, xPos= 900, yPos=6650, width=2300, height= 250, style="styleA", text="",                                                                    fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_SIMULATIONS_SEARCHTEXT'])
        self.GUIOs["SIMULATIONS_SORTBYTITLETEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos=3300, yPos=6650, width= 800, height= 250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:SIMULATIONS_SORTBY'),       fontSize=80, textInteractable=False)
        self.GUIOs["SIMULATIONS_SORTBYSELECTIONBOX"]       = selectionBox_typeB(**inst, groupOrder=2, xPos=4200, yPos=6650, width=1500, height= 250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_SIMULATIONS_SORTTYPE'])
        simulationSortTypes = {'INDEX':           {'text': self.visualManager.getTextPack('SIMULATION:SIMULATIONS_SORTBY_INDEX')},
                               'SIMULATIONCODE':  {'text': self.visualManager.getTextPack('SIMULATION:SIMULATIONS_SORTBY_SIMULATIONCODE')},
                               'SIMULATIONRANGE': {'text': self.visualManager.getTextPack('SIMULATION:SIMULATIONS_SORTBY_SIMULATIONRANGE')},
                               'CREATIONTIME':    {'text': self.visualManager.getTextPack('SIMULATION:SIMULATIONS_SORTBY_CREATIONTIME')},
                               'STATUS':          {'text': self.visualManager.getTextPack('SIMULATION:SIMULATIONS_SORTBY_STATUS')},
                               'COMPLETION':      {'text': self.visualManager.getTextPack('SIMULATION:SIMULATIONS_SORTBY_COMPLETION')}}
        self.GUIOs["SIMULATIONS_SORTBYSELECTIONBOX"].setSelectionList(selectionList = simulationSortTypes, displayTargets = 'all')
        self.GUIOs["SIMULATIONS_SORTBYSELECTIONBOX"].setSelected(itemKey = 'CREATIONTIME', callSelectionUpdateFunction = False)
        self.GUIOs["SIMULATIONS_SELECTIONBOX"]             = selectionBox_typeC(**inst, groupOrder=2, xPos= 100, yPos=2850, width=5600, height=3700, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_SIMULATIONS_SIMULATIONSELECTION'], 
                                                                                elementWidths = (500, 1000, 1600, 1000, 600, 650)) #5350
        self.GUIOs["SIMULATIONS_SELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('SIMULATION:SIMULATIONS_ST_INDEX')},           # 500
                                                                                {'text': self.visualManager.getTextPack('SIMULATION:SIMULATIONS_ST_SIMULATIONCODE')},  #1000
                                                                                {'text': self.visualManager.getTextPack('SIMULATION:SIMULATIONS_ST_SIMULATIONRANGE')}, #1600
                                                                                {'text': self.visualManager.getTextPack('SIMULATION:SIMULATIONS_ST_CREATIONTIME')},    #1000
                                                                                {'text': self.visualManager.getTextPack('SIMULATION:SIMULATIONS_ST_STATUS')},          # 600
                                                                                {'text': self.visualManager.getTextPack('SIMULATION:SIMULATIONS_ST_COMPLETION')}])     # 650

        #Generals
        self.GUIOs["BLOCKTITLE_GENERAL"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=2550, width=5600, height=200, style="styleA", text=self.visualManager.getTextPack('SIMULATION:BLOCKTITLE_GENERAL'), fontSize=80)
        self.GUIOs["GENERAL_SIMULATIONCODETITLETEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=2200, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:GENERAL_SIMULATIONCODE'),         fontSize=80, textInteractable=False)
        self.GUIOs["GENERAL_SIMULATIONCODETEXTINPUTBOX"]    = textInputBox_typeA(**inst, groupOrder=1, xPos=1700, yPos=2200, width=4000, height=250, style="styleA", text="",                                                                          fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_GENERAL_SIMULATIONCODE'])
        self.GUIOs["GENERAL_SIMULATIONCODEDISPLAYTEXT"]     = textBox_typeA(**inst,      groupOrder=1, xPos=1700, yPos=2200, width=4000, height=250, style="styleA", text="",                                                                          fontSize=80, textInteractable=True)
        self.GUIOs["GENERAL_SIMULATIONCODEDISPLAYTEXT"].hide()
        self.GUIOs["GENERAL_SIMULATIONRANGETITLETEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=1850, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:GENERAL_SIMULATIONRANGE'),        fontSize=80, textInteractable=False)
        self.GUIOs["GENERAL_SIMULATIONRANGETEXTINPUTBOX1"]  = textInputBox_typeA(**inst, groupOrder=1, xPos=1700, yPos=1850, width=1950, height=250, style="styleA", text="",                                                                          fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_GENERAL_SIMULATIONRANGE'])
        self.GUIOs["GENERAL_SIMULATIONRANGETEXTINPUTBOX2"]  = textInputBox_typeA(**inst, groupOrder=1, xPos=3750, yPos=1850, width=1950, height=250, style="styleA", text="",                                                                          fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_GENERAL_SIMULATIONRANGE'])
        self.GUIOs["GENERAL_SIMULATIONRANGEDISPLAYTEXT1"]   = textBox_typeA(**inst,      groupOrder=1, xPos=1700, yPos=1850, width=1950, height=250, style="styleA", text="",                                                                          fontSize=80, textInteractable=True)
        self.GUIOs["GENERAL_SIMULATIONRANGEDISPLAYTEXT2"]   = textBox_typeA(**inst,      groupOrder=1, xPos=3750, yPos=1850, width=1950, height=250, style="styleA", text="",                                                                          fontSize=80, textInteractable=True)
        self.GUIOs["GENERAL_SIMULATIONRANGEDISPLAYTEXT1"].hide()
        self.GUIOs["GENERAL_SIMULATIONRANGEDISPLAYTEXT2"].hide()
        self.GUIOs["GENERAL_CREATIONTIMETITLETEXT"]         = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=1500, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:GENERAL_CREATIONTIME'),            fontSize=80, textInteractable=False)
        self.GUIOs["GENERAL_CREATIONTIMEDISPLAYTEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos=1400, yPos=1500, width=1400, height=250, style="styleA", text="-",                                                                          fontSize=80, textInteractable=True)
        self.GUIOs["GENERAL_ALLOCATEDSIMUALTORTITLETEXT"]   = textBox_typeA(**inst,      groupOrder=1, xPos=2900, yPos=1500, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:GENERAL_ALLOCATEDSIMUALTOR'),      fontSize=80, textInteractable=False)
        self.GUIOs["GENERAL_ALLOCATEDSIMUALTORDISPLAYTEXT"] = textBox_typeA(**inst,      groupOrder=1, xPos=4500, yPos=1500, width=1200, height=250, style="styleA", text="-",                                                                          fontSize=80, textInteractable=True)
        self.GUIOs["GENERAL_STATUSTITLETEXT"]               = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=1150, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:GENERAL_STATUS'),                 fontSize=80, textInteractable=False)
        self.GUIOs["GENERAL_STATUSDISPLAYTEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos=1400, yPos=1150, width=1400, height=250, style="styleA", text="-",                                                                         fontSize=80, textInteractable=True)
        self.GUIOs["GENERAL_COMPLETIONGAUGEBAR"]            = gaugeBar_typeA(**inst,     groupOrder=1, xPos=2900, yPos=1150, width=2800, height=250, style="styleB", align='horizontal', gaugeColor = (0, 0, 0, 255))
        self.GUIOs["GENERAL_COMPLETIONGAUGEBAR"].updateGaugeValue(gaugeValue = 0)
        self.GUIOs["GENERAL_COMPLETIONDISPLAYTEXT"]         = textBox_typeA(**inst,      groupOrder=1, xPos=2900, yPos=1150, width=2800, height=250, style=None, text="-", fontSize=80, textInteractable=False)
        self.GUIOs["GENERAL_ANALYSISEXPORTTITLETEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos= 800, width=2100, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:GENERAL_ANALYSISEXPORT'),     fontSize=80, textInteractable=True)
        self.GUIOs["GENERAL_ANALYSISEXPORTSWITCH"]          = switch_typeB(**inst,       groupOrder=2, xPos=2300, yPos= 800, width= 500, height=250, style="styleA", align='horizontal', switchStatus=False, statusUpdateFunction = self.pageObjectFunctions['ONSWITCHUPDATE_GENERAL_ANALYSISEXPORT'])
        self.GUIOs["GENERAL_ANALYSISEXPORTSWITCH"].setStatus(status = self.puVar['simulationSetup_analysisExport'], animate = False, callStatusUpdateFunction = False)
        self.GUIOs["GENERAL_REPLICATECONFIGURATIONBUTTON"]  = button_typeA(**inst,       groupOrder=1, xPos=2900, yPos= 800, width=2800, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:GENERAL_REPLICATECONFIGURATION'), fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_GENERAL_REPLICATECONFIGURATION'])
        self.GUIOs["GENERAL_ADDSIMULATIONBUTTON"]           = button_typeA(**inst,       groupOrder=1, xPos= 100, yPos= 450, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:GENERAL_ADD'),                    fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_GENERAL_ADDSIMULATION'])
        self.GUIOs["GENERAL_REMOVESIMULATIONBUTTON"]        = button_typeA(**inst,       groupOrder=1, xPos=1200, yPos= 450, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:GENERAL_REMOVE'),                 fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_GENERAL_REMOVESIMULATION'])
        self.GUIOs["GENERAL_VIEWRESULTBUTTON"]              = button_typeA(**inst,       groupOrder=1, xPos=2300, yPos= 450, width=3400, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:GENERAL_VIEWRESULT'),             fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_GENERAL_VIEWRESULT'])
        self.GUIOs["GENERAL_ADDSIMULATIONBUTTON"].deactivate()
        self.GUIOs["GENERAL_REMOVESIMULATIONBUTTON"].deactivate()
        self.GUIOs["GENERAL_REPLICATECONFIGURATIONBUTTON"].deactivate()
        self.GUIOs["GENERAL_VIEWRESULTBUTTON"].deactivate()

        #Positions
        self.GUIOs["BLOCKTITLE_POSITIONS"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=5800, yPos=8350, width=10100, height=200, style="styleA", text=self.visualManager.getTextPack('SIMULATION:BLOCKTITLE_POSITIONS'),  fontSize=80)
        self.GUIOs["POSITIONS_SEARCHTITLETEXT"]               = textBox_typeA(**inst,      groupOrder=1, xPos= 5800, yPos=8000, width= 700, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:POSITIONS_SEARCH'),     fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_SEARCHTEXTINPUTBOX"]            = textInputBox_typeA(**inst, groupOrder=1, xPos= 6600, yPos=8000, width=1700, height=250, style="styleA", text="",                                                                fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_POSITIONS_SEARCHTEXT'])
        self.GUIOs["POSITIONS_SEARCHTYPESELECTIONBOX"]        = selectionBox_typeB(**inst, groupOrder=2, xPos= 8400, yPos=8000, width=1100, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_POSITIONS_SEARCHTYPE'])
        positionSearchTypes = {'SYMBOL':  {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_SEARCH_SYMBOL')},
                               'CACCODE': {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_SEARCH_CACCODE')},
                               'TCCODE':  {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_SEARCH_TCCODE')}}
        self.GUIOs["POSITIONS_SEARCHTYPESELECTIONBOX"].setSelectionList(selectionList = positionSearchTypes, displayTargets = 'all')
        self.GUIOs["POSITIONS_SEARCHTYPESELECTIONBOX"].setSelected(itemKey = 'SYMBOL', callSelectionUpdateFunction = False)
        self.GUIOs["POSITIONS_SORTBYTITLETEXT"]               = textBox_typeA(**inst,      groupOrder=1, xPos= 9600, yPos=8000, width= 800, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:POSITIONS_SORTBY'),     fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_SORTBYSELECTIONBOX"]            = selectionBox_typeB(**inst, groupOrder=2, xPos=10500, yPos=8000, width=1800, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_POSITIONS_SORTTYPE'])
        positionsSortTypes = {'INDEX':                {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_SORTBY_INDEX')},
                              'SYMBOL':               {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_SORTBY_SYMBOL')},
                              'CACCODE':              {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_SORTBY_CACCODE')},
                              'TCCODE':               {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_SORTBY_TCCODE')},
                              'MARGINMODE':           {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_SORTBY_MARGINMODE')},
                              'LEVERAGE':             {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_SORTBY_LEVERAGE')},
                              'PRIORITY':             {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_SORTBY_PRIORITY')},
                              'ASSUMEDRATIO':         {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_SORTBY_ASSUMEDRATIO')},
                              'WEIGHTEDASSUMEDRATIO': {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_SORTBY_WEIGHTEDASSUMEDRATIO')},
                              'ALLOCATEDBALANCE':     {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_SORTBY_ALLOCATEDBALANCE')},
                              'MAXALLOCATEDBALANCE':  {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_SORTBY_MAXALLOCATEDBALANCE')},
                              'FIRSTKLINE':           {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_SORTBY_FIRSTKLINE')}}
        self.GUIOs["POSITIONS_SORTBYSELECTIONBOX"].setSelectionList(selectionList = positionsSortTypes, displayTargets = 'all')
        self.GUIOs["POSITIONS_SORTBYSELECTIONBOX"].setSelected(itemKey = 'INDEX', callSelectionUpdateFunction = False)
        self.GUIOs["POSITIONS_TRADABLEFILTERTITLETEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos=12400, yPos=8000, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:POSITIONS_TRADABLEFILTER'), fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_TRADABLEFILTERSELECTIONBOX"]    = selectionBox_typeB(**inst, groupOrder=2, xPos=13500, yPos=8000, width=1000, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_POSITIONS_TRADABLEFILTER'])
        tradabilityFilterTypes = {'ALL':   {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_FILTER_ALL')},
                                  'TRUE':  {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_FILTER_TRUE')},
                                  'FALSE': {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_FILTER_FALSE')}}
        self.GUIOs["POSITIONS_TRADABLEFILTERSELECTIONBOX"].setSelectionList(selectionList = tradabilityFilterTypes, displayTargets = 'all')
        self.GUIOs["POSITIONS_TRADABLEFILTERSELECTIONBOX"].setSelected(itemKey = 'ALL', callSelectionUpdateFunction = False)
        self.GUIOs["POSITIONS_INITIALIZATIONBUTTON"]          = button_typeA(**inst,  groupOrder=1, xPos=14600, yPos=8000, width=1300, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:POSITIONS_INITIALIZESETUP'), fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_POSITIONS_INITIALIZE'])
        self.GUIOs["POSITIONS_INITIALIZATIONBUTTON"].deactivate()
        self.GUIOs["POSITIONS_SELECTEDPOSITIONSTITLETEXT"]    = textBox_typeA(**inst, groupOrder=1, xPos= 5800, yPos=7650, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:POSITIONS_SELECTEDPOSITIONS'), fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_SELECTEDPOSITIONSDISPLAYTEXT"]  = textBox_typeA(**inst, groupOrder=1, xPos= 7400, yPos=7650, width=6100, height=250, style="styleA", text="-",                                                                      fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_NSELECTEDPOSITIONSDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=13600, yPos=7650, width=1000, height=250, style="styleA", text="- / -", fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_RELEASEALLBUTTON"]              = button_typeA(**inst,  groupOrder=1, xPos=14700, yPos=7650, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:POSITIONS_RELEASEALL'), fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_POSITIONS_RELEASEALL'])
        self.GUIOs["POSITIONS_RELEASEALLBUTTON"].deactivate()
        self.GUIOs["POSITIONS_SETUPSELECTIONBOX"]             = selectionBox_typeC(**inst, groupOrder=2, xPos=5800, yPos=2500, width=10100, height=5050, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_POSITIONS_POSITION'], 
                                                                                   elementWidths = (600, 1200, 950, 950, 700, 500, 500, 600, 600, 800, 800, 1000, 650, 800, 800), name = "SETUP") #9850+1600
        self.GUIOs["POSITIONS_SELECTEDSIMSELECTIONBOX"]       = selectionBox_typeC(**inst, groupOrder=2, xPos=5800, yPos=2500, width=10100, height=5400, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_POSITIONS_POSITION'], 
                                                                                   elementWidths = (600, 1200, 950, 950, 700, 500, 500, 600, 600, 800, 800, 1000, 650), name = "SIM") #9850
        self.GUIOs["POSITIONS_SETUPSELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_INDEX')},                             # 600
                                                                                   {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_SYMBOL')},                            #1200
                                                                                   {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_CURRENCYANALYSISCONFIGURATIONCODE')}, # 950
                                                                                   {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_TRADECONFIGURATIONCODE')},            # 950
                                                                                   {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_MARGINMODE')},                        # 700
                                                                                   {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_LEVERAGE')},                          # 500
                                                                                   {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_PRIORITY')},                          # 500
                                                                                   {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_ASSUMEDRATIO')},                      # 600
                                                                                   {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_WEIGHTEDASSUMEDRATIO')},              # 600
                                                                                   {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_ALLOCATEDBALANCE')},                  # 800
                                                                                   {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_MAXALLOCATEDBALANCE')},               # 800
                                                                                   {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_FIRSTKLINE')},                        #1000
                                                                                   {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_TRADABLE')},                          # 650
                                                                                   {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_MARKETSTATUS')},                      # 800
                                                                                   {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_MINNOTIONAL')}])                      # 800
        self.GUIOs["POSITIONS_SELECTEDSIMSELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_INDEX')},                             # 600
                                                                                         {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_SYMBOL')},                            #1200
                                                                                         {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_CURRENCYANALYSISCONFIGURATIONCODE')}, # 950
                                                                                         {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_TRADECONFIGURATIONCODE')},            # 950
                                                                                         {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_MARGINMODE')},                        # 700
                                                                                         {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_LEVERAGE')},                          # 500
                                                                                         {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_PRIORITY')},                          # 500
                                                                                         {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_ASSUMEDRATIO')},                      # 600
                                                                                         {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_WEIGHTEDASSUMEDRATIO')},              # 600
                                                                                         {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_ALLOCATEDBALANCE')},                  # 800
                                                                                         {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_MAXALLOCATEDBALANCE')},               # 800
                                                                                         {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_FIRSTKLINE')},                        #1000
                                                                                         {'text': self.visualManager.getTextPack('SIMULATION:POSITIONS_ST_TRADABLE')}])                         # 650
        self.GUIOs["POSITIONS_SELECTEDSIMSELECTIONBOX"].hide()
        self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODETITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos= 5800, yPos=2150, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:POSITIONS_CURRENCYANALYSISCONFIGURATIONCODE'), fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODESELECTIONBOX"] = selectionBox_typeB(**inst, groupOrder=2, xPos= 6900, yPos=2150, width=3000, height=250, style="styleA", nDisplay = 8, fontSize = 80, expansionDir = 0, showIndex = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_POSITIONS_CURRENCYANALYSISCONFIGURATIONCODE'])
        self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODEDISPLAYTEXT"]  = textBox_typeA(**inst,      groupOrder=1, xPos= 6900, yPos=2150, width=3000, height=250, style="styleA", text="-",                                                                                      fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODERESETBUTTON"]  = button_typeA(**inst,       groupOrder=1, xPos=10000, yPos=2150, width= 800, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:POSITIONS_RESET'),                             fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_POSITIONS_RESETCURRENCYANALYSISCONFIURATIONCODE'])
        self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODESELECTIONBOX"].deactivate()
        self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODEDISPLAYTEXT"].hide()
        self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODERESETBUTTON"].deactivate()
        self.GUIOs["POSITIONS_TRADECONFIGURATIONCODETITLETEXT"]               = textBox_typeA(**inst,      groupOrder=1, xPos=10900, yPos=2150, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:POSITIONS_TRADECONFIGURATIONCODE'),            fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_TRADECONFIGURATIONCODESELECTIONBOX"]            = selectionBox_typeB(**inst, groupOrder=2, xPos=12000, yPos=2150, width=3000, height=250, style="styleA", nDisplay = 8, fontSize = 80, expansionDir = 0, showIndex = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_POSITIONS_TRADECONFIGURATIONCODE'])
        self.GUIOs["POSITIONS_TRADECONFIGURATIONCODEDISPLAYTEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos=12000, yPos=2150, width=3000, height=250, style="styleA", text="-",                                                                                      fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_TRADECONFIGURATIONCODERESETBUTTON"]             = button_typeA(**inst,       groupOrder=1, xPos=15100, yPos=2150, width= 800, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:POSITIONS_RESET'),                             fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_POSITIONS_RESETTRADECONFIGURATIONCODE'])
        self.GUIOs["POSITIONS_TRADECONFIGURATIONCODESELECTIONBOX"].deactivate()
        self.GUIOs["POSITIONS_TRADECONFIGURATIONCODEDISPLAYTEXT"].hide()
        self.GUIOs["POSITIONS_TRADECONFIGURATIONCODERESETBUTTON"].deactivate()
        self.GUIOs["POSITIONS_ASSUMEDRATIOTITLETEXT"]                         = textBox_typeA(**inst,      groupOrder=1, xPos= 5800, yPos=1800, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:POSITIONS_ASSUMEDRATIO'),                      fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_ASSUMEDRATIOTEXTINPUTBOX"]                      = textInputBox_typeA(**inst, groupOrder=1, xPos= 7100, yPos=1800, width=1000, height=250, style="styleA", text="",                                                                                       fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_POSITIONS_ASSUMEDRATIO'])
        self.GUIOs["POSITIONS_ASSUMEDRATIODISPLAYTEXT"]                       = textBox_typeA(**inst,      groupOrder=1, xPos= 7100, yPos=1800, width=1000, height=250, style="styleA", text="-",                                                                                      fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_ASSUMEDRATIOTEXTINPUTBOX"].deactivate()
        self.GUIOs["POSITIONS_ASSUMEDRATIODISPLAYTEXT"].hide()
        self.GUIOs["POSITIONS_ASSUMEDRATIOUNITTEXT"]                          = textBox_typeA(**inst,      groupOrder=1, xPos= 8200, yPos=1800, width= 400, height=250, style="styleA", text="%",                                                                                      fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_PRIORITYTITLETEXT"]                             = textBox_typeA(**inst,      groupOrder=1, xPos= 8700, yPos=1800, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:POSITIONS_PRIORITY'),                          fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_PRIORITYTEXTINPUTBOX"]                          = textInputBox_typeA(**inst, groupOrder=1, xPos= 9800, yPos=1800, width= 700, height=250, style="styleA", text="",                                                                                       fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_POSITIONS_PRIORITY'])
        self.GUIOs["POSITIONS_PRIORITYDISPLAYTEXT"]                           = textBox_typeA(**inst,      groupOrder=1, xPos= 9800, yPos=1800, width= 700, height=250, style="styleA", text="-",                                                                                      fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_PRIORITYTEXTINPUTBOX"].deactivate()
        self.GUIOs["POSITIONS_PRIORITYDISPLAYTEXT"].hide()
        self.GUIOs["POSITIONS_MAXALLOCATEDBALANCETITLETEXT"]                  = textBox_typeA(**inst,      groupOrder=1, xPos=10600, yPos=1800, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:POSITIONS_MAXALLOCATEDBALANCE'),               fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_MAXALLOCATEDBALANCETEXTINPUTBOX"]               = textInputBox_typeA(**inst, groupOrder=1, xPos=12700, yPos=1800, width=1700, height=250, style="styleA", text="",                                                                                       fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_POSITIONS_MAXALLOCATEDBALANCE'])
        self.GUIOs["POSITIONS_MAXALLOCATEDBALANCEDISPLAYTEXT"]                = textBox_typeA(**inst,      groupOrder=1, xPos=12700, yPos=1800, width=1700, height=250, style="styleA", text="-",                                                                                      fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_MAXALLOCATEDBALANCETEXTINPUTBOX"].deactivate()
        self.GUIOs["POSITIONS_MAXALLOCATEDBALANCEDISPLAYTEXT"].hide()
        self.GUIOs["POSITIONS_MAXALLOCATEDBALANCEUNITTEXT"]                   = textBox_typeA(**inst,      groupOrder=1, xPos=14500, yPos=1800, width= 600, height=250, style="styleA", text="-",                                                                                      fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_POSITIONAPPLYBUTTON"]                           = button_typeA(**inst,       groupOrder=1, xPos=15200, yPos=1800, width= 700, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:POSITIONS_APPLY'),                             fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_POSITIONS_EDITPOSITIONPARAMS'])
        self.GUIOs["POSITIONS_POSITIONAPPLYBUTTON"].deactivate()

        #Assets
        self.GUIOs["BLOCKTITLE_ASSETS"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=5800, yPos=1500, width=10100, height=200, style="styleA", text=self.visualManager.getTextPack('SIMULATION:BLOCKTITLE_ASSETS'), fontSize=80)
        self.GUIOs["ASSETS_ASSETTITLETEXT"]                   = textBox_typeA(**inst,      groupOrder=1, xPos= 5800, yPos=1150, width=1300, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:ASSETS_ASSET'),                fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_ASSETSELECTIONBOX"]                = selectionBox_typeB(**inst, groupOrder=2, xPos= 7200, yPos=1150, width=1500, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_ASSETS_ASSETSELECTION'])
        assetsToDisplay = {'USDT': {'text': 'USDT'},
                           'USDC': {'text': 'USDC'}}
        self.GUIOs["ASSETS_ASSETSELECTIONBOX"].setSelectionList(selectionList = assetsToDisplay, displayTargets = 'all')
        self.GUIOs["ASSETS_ASSETSELECTIONBOX"].setSelected(itemKey = 'USDT', callSelectionUpdateFunction = False)
        self.GUIOs["ASSETS_INITIALWALLETBALANCETITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos= 8800, yPos=1150, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:ASSETS_INITIALWALLETBALANCE'), fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_INITIALWALLETBALANCEDISPLAYTEXT"]  = textBox_typeA(**inst,      groupOrder=1, xPos=10900, yPos=1150, width=1800, height=250, style="styleA", text="-",                                                                      fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_INITIALWALLETBALANCETEXTINPUTBOX"] = textInputBox_typeA(**inst, groupOrder=1, xPos=12800, yPos=1150, width=1800, height=250, style="styleA", text="",                                                                       fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_ASSETS_INITIALWALLETBALANCE'])
        self.GUIOs["ASSETS_ASSETAPPLYBUTTON"]                 = button_typeA(**inst,       groupOrder=1, xPos=14700, yPos=1150, width= 850, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:ASSETS_APPLY'),                fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_ASSETS_EDITASSETPARAMS'])
        self.GUIOs["ASSETS_ASSETAPPLYBUTTON"].deactivate()
        self.GUIOs["ASSETS_SELECTEDASSETIMAGEBOX"]            = imageBox_typeA(**inst,     groupOrder=1, xPos=15650, yPos=1150, width= 250, height=250, style=None, image="usdtIcon_512x512.png")
        self.GUIOs["ASSETS_ALLOCATIONRATIOTITLETEXT"]         = textBox_typeA(**inst,      groupOrder=1, xPos= 5800, yPos= 800, width=1300, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:ASSETS_ALLOCATIONRATIO'),      fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_ALLOCATIONRATIOSLIDER"]            = slider_typeA(**inst,       groupOrder=1, xPos= 7200, yPos= 850, width=4400, height=150, style="styleA", valueUpdateFunction=self.pageObjectFunctions['ONVALUEUPDATE_ASSETS_ALLOCATIONRATIOSLIDER'])
        self.GUIOs["ASSETS_ALLOCATIONRATIODISPLAYTEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos=11700, yPos= 800, width= 900, height=250, style="styleA", text="-",                                                                      fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_ALLOCATABLEBALANCETITLETEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos=12700, yPos= 800, width=1600, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:ASSETS_ALLOCATABLEBALANCE'),   fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_ALLOCATABLEBALANCEDISPLAYTEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos=14400, yPos= 800, width=1500, height=250, style="styleA", text="-",                                                                      fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_ASSUMEDRATIOTITLETEXT"]            = textBox_typeA(**inst,      groupOrder=1, xPos= 5800, yPos= 450, width=1300, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:ASSETS_ASSUMEDRATIO'),         fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_ASSUMEDRATIODISPLAYTEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos= 7200, yPos= 450, width= 900, height=250, style="styleA", text="-",                                                                      fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_WEIGHTEDASSUMEDRATIOTITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos= 8200, yPos= 450, width=1300, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:ASSETS_WEIGHTEDASSUMEDRATIO'), fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_WEIGHTEDASSUMEDRATIODISPLAYTEXT"]  = textBox_typeA(**inst,      groupOrder=1, xPos= 9600, yPos= 450, width= 900, height=250, style="styleA", text="-",                                                                      fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_ALLOCATEDBALANCETITLETEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos=10600, yPos= 450, width=1400, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:ASSETS_ALLOCATEDBALANCE'),     fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_ALLOCATEDBALANCEDISPLAYTEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos=12100, yPos= 450, width=1000, height=250, style="styleA", text="-",                                                                      fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_MAXALLOCATEDBALANCETITLETEXT"]     = textBox_typeA(**inst,      groupOrder=1, xPos=13200, yPos= 450, width=1600, height=250, style="styleA", text=self.visualManager.getTextPack('SIMULATION:ASSETS_MAXALLOCATEDBALANCE'),  fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_MAXALLOCATEDBALANCEDISPLAYTEXT"]   = textBox_typeA(**inst,      groupOrder=1, xPos=14900, yPos= 450, width=1000, height=250, style="styleA", text="-",                                                                      fontSize=80, textInteractable=False)
        self.pageAuxillaryFunctions['UPDATEASSETDATADISPLAY']()

        #<Message>
        self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=  100, yPos=100, width=15800, height=250, style="styleA", text="-", fontSize=80, textInteractable=False)

    elif (self.displaySpaceDefiner['ratio'] == '21:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 21000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
    elif (self.displaySpaceDefiner['ratio'] == '32:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 32000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
#SETUP PAGE <MAIN> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <LOAD> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageLoadFunction(self):
    #[1]: Instances
    puVar              = self.puVar
    pafs               = self.pageAuxillaryFunctions
    func_getPRD        = self.ipcA.getPRD
    func_addFARHandler = self.ipcA.addFARHandler

    #[2]: FAR Handlers Registration
    func_addFARHandler('onCurrenciesUpdate',            pafs['_FAR_ONCURRENCIESUPDATE'],            executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #DATAMANAGER
    func_addFARHandler('onAnalysisConfigurationUpdate', pafs['_FAR_ONANALYSISCONFIGURATIONUPDATE'], executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #TRADEMANAGER
    func_addFARHandler('onTradeConfigurationUpdate',    pafs['_FAR_ONTRADECONFIGURATIONUPDATE'],    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #TRADEMANAGER
    func_addFARHandler('onSimulatorCentralUpdate',      pafs['_FAR_ONSIMULATORCENTRALUPDATE'],      executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #SIMULATIONMANAGER
    func_addFARHandler('onSimulationUpdate',            pafs['_FAR_ONSIMULATIONUPDATE'],            executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #SIMULATIONMANAGER

    #[3]: Get data via PRD
    puVar['currencies']                     = func_getPRD(processName = 'DATAMANAGER',       prdAddress = 'CURRENCIES').copy()
    puVar['currencyAnalysisConfigurations'] = func_getPRD(processName = 'TRADEMANAGER',      prdAddress = 'CURRENCYANALYSISCONFIGURATIONS').copy()
    puVar['tradeConfigurations']            = func_getPRD(processName = 'TRADEMANAGER',      prdAddress = 'TRADECONFIGURATIONS').copy()
    puVar['simulatorCentral']               = func_getPRD(processName = 'SIMULATIONMANAGER', prdAddress = 'SIMULATORCENTRAL').copy()
    puVar['simulations']                    = func_getPRD(processName = 'SIMULATIONMANAGER', prdAddress = 'SIMULATIONS').copy()

    #[4]: Update Simulation Setup Positions List Data
    currencies = puVar['currencies']
    cacs          = puVar['currencyAnalysisConfigurations']
    tcs           = puVar['tradeConfigurations']
    ss_positions  = puVar['simulationSetup_positions']
    ss_assets     = puVar['simulationSetup_assets']
    assets_resort = set()
    for symbol, currency in currencies.items():
        #[4-1]: Quote Asset Check
        qAsset = currency['quoteAsset']
        if qAsset not in _READABLEASSETS:
            continue

        #[4-2]: Existing Symbol
        if symbol in ss_positions:
            ss_position = ss_positions[symbol]
            cacCode = ss_position['currencyAnalysisConfigurationCode']
            tcCode  = ss_position['tradeConfigurationCode']

            #[4-2-1]: Currency Analysis Configuration
            if cacCode not in cacs:
                cacCode = None
            ss_position['currencyAnalysisConfigurationCode'] = cacCode

            #[4-2-2]: Trade Configuration
            if tcCode not in tcs:
                tcCode = None
            ss_position['tradeConfigurationCode'] = tcCode
            if tcCode is None:
                ss_position['isolated']             = None
                ss_position['leverage']             = None
                ss_position['weightedAssumedRatio'] = None
            else:
                tc = tcs[tcCode]
                ss_position['isolated'] = tc['isolated']
                ss_position['leverage'] = tc['leverage']
                ss_position['weightedAssumedRatio'] = ss_position['assumedRatio']*tcs[tcCode]['leverage']

            #[4-2-3]: First Open Timestamps & Available Ranges
            drs   = dict()
            foTSs = dict()
            for t in ('kline', 'depth', 'aggTrade'):
                if currency[f'{t}s_availableRanges']: drs[t] = currency[f'{t}s_availableRanges'].copy()
                else:                                 drs[t] = None
                foTSs[t] = currency[f'{t}_firstOpenTS']
            ss_position['dataRanges']   = drs
            ss_position['firstOpenTSs'] = foTSs

            #[4-2-4]: Tradable Update
            ss_position['tradable'] = (cacCode is not None and tcCode is not None)
        
        #[4-3]: New Symbol
        else:
            drs   = dict()
            foTSs = dict()
            for t in ('kline', 'depth', 'aggTrade'):
                if currency[f'{t}s_availableRanges']: drs[t] = currency[f'{t}s_availableRanges'].copy()
                else:                                 drs[t] = None
                foTSs[t] = currency[f'{t}_firstOpenTS']
            ss_positions[symbol] = {'quoteAsset':                        currency['quoteAsset'],
                                    'precisions':                        currency['precisions'].copy(),
                                    'dataRanges':                        drs,
                                    'currencyAnalysisConfigurationCode': None,
                                    'tradeConfigurationCode':            None,
                                    'isolated':                          None,
                                    'leverage':                          None,
                                    'priority':                          len(puVar['simulationSetup_positions'])+1,
                                    'assumedRatio':                      0,
                                    'weightedAssumedRatio':              None,
                                    'allocatedBalance':                  0,
                                    'maxAllocatedBalance':               float('inf'),
                                    'firstOpenTSs':                      foTSs,
                                    'tradable':                          False}
            ss_asset = ss_assets[qAsset]
            ss_asset['_positionSymbols'].add(symbol)
            ss_asset['_positionSymbols_prioritySorted'].append(symbol)
            assets_resort.add(qAsset)

    #[5]: Assets Resort
    for assetName in assets_resort:
        pafs['SORTPOSITIONSYMBOLSBYPRIORITY'](assetName = assetName)
        pafs['ALLOCATEWALLETBALANCE'](assetName         = assetName)
        pafs['COMPUTEPOSITIONSUMS'](assetName           = assetName)

    #[6]: GUIOs Update
    if puVar['simulation_selected'] not in puVar['simulations']:
        puVar['simulation_selected'] = None
    pafs['SETSETUPPOSITIONSLIST']()
    pafs['SETSIMULATIONSLIST']()
    pafs['UPDATESIMULATIONDATA']()
    pafs['UPDATESIMULATORSDATA'](updateAll = True)
    pafs['SETCURRENCYANALYSISCONFIGURATIONLIST']()
    pafs['SETTRADECONFIGURATIONLIST']()
    pafs['ONSIMULATIONSELECTIONUPDATE']()
#SETUP PAGE <LOAD> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <ESCAPE> --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageEscapeFunction(self):
    #[1]: Instances
    func_removeFARHandler   = self.ipcA.removeFARHandler
    func_addDummyFARHandler = self.ipcA.addDummyFARHandler

    #[2]: FAR Handlers Update
    for fID in ('onCurrenciesUpdate',
                'onCurrencyAnalysisConfigurationUpdate',
                'onTradeConfigurationUpdate',
                'onSimulatorCentralUpdate',
                'onSimulationUpdate',):
        func_removeFARHandler(functionID   = fID)
        func_addDummyFARHandler(functionID = fID)
#SETUP PAGE <ESCAPE> END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <PROCESS> -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageProcessFunction(self, t_elapsed_ns, onLoad = False):
    #[1]: Instances
    puVar  = self.puVar
    guios  = self.GUIOs
    pafs   = self.pageAuxillaryFunctions
    vm_gtp = self.visualManager.getTextPack
    sims    = puVar['simulations']
    slu_itu = puVar['simulationListUpdate_ItemsToUpdate']

    #[2]: Simulations List
    t_current_ns = time.perf_counter_ns()
    if slu_itu and _SIMULATIONLISTUPDATEINTERVAL_NS <= t_current_ns-puVar['simulationListUpdate_LastUpdated_ns']:
        for itu in puVar['simulationListUpdate_ItemsToUpdate']:
            #[2-1]: Instances
            simCode = itu[0]
            dName   = itu[1]
            sim = sims.get(simCode, None)
            if sim is None:
                continue

            #[2-2]: Update Handling
            #---[2-2-1]: Status
            if dName == 'status':
                status = sim['_status']
                if   status == 'COMPLETED':  text = vm_gtp('SIMULATION:GENERAL_STATUS_COMPLETED');  textColor = 'GREEN'
                elif status == 'QUEUED':     text = vm_gtp('SIMULATION:GENERAL_STATUS_QUEUED');     textColor = 'BLUE'
                elif status == 'PROCESSING': text = vm_gtp('SIMULATION:GENERAL_STATUS_PROCESSING'); textColor = 'GREEN_LIGHT'
                elif status == 'PAUSED':     text = vm_gtp('SIMULATION:GENERAL_STATUS_PAUSED');     textColor = 'YELLOW'
                elif status == 'ERROR':      text = vm_gtp('SIMULATION:GENERAL_STATUS_ERROR');      textColor = 'RED_LIGHT'
                nsbi = {'text': text, 'textStyles': [('all', textColor),]}
                guios["SIMULATIONS_SELECTIONBOX"].editSelectionListItem(itemKey = simCode, item = nsbi, columnIndex = 4)

            #---[2-2-2]: Completion
            elif dName == 'completion':
                completion = sim['_completion']
                if completion is None: 
                    text      = "-"
                    textColor = 'DEFAULT'
                else:                                    
                    completion_perc = completion*100
                    text            = f"{completion_perc:.2f} %"
                    if   0 <= completion_perc and completion_perc <=  33: textColor = 'ORANGE_LIGHT'
                    elif 33 < completion_perc and completion_perc <=  66: textColor = 'BLUE_LIGHT'
                    elif 66 < completion_perc and completion_perc <= 100: textColor = 'GREEN_LIGHT'
                nsbi = {'text': text, 'textStyles': [('all', textColor),]}
                guios["SIMULATIONS_SELECTIONBOX"].editSelectionListItem(itemKey = simCode, item = nsbi, columnIndex = 5)

        pafs['ONSIMULATIONSFILTERUPDATE']()
        puVar['simulationListUpdate_ItemsToUpdate'].clear()
        puVar['simulationListUpdate_LastUpdated_ns'] = t_current_ns
#SETUP PAGE <PROCESS> END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#OBJECT FUNCTIONS -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateObjectFunctions(self):
    objFunctions = dict()

    #<Page Navigation>
    def __pageMove_DASHBOARD(objInstance, **kwargs): 
        self.sysFunctions['LOADPAGE']('DASHBOARD')
    objFunctions['PAGEMOVE_DASHBOARD'] = __pageMove_DASHBOARD

    #<Simulators>
    def __onSelectionUpdate_Simulators_SimulatorSelection(objInstance, **kwargs):
        self.puVar['simulatorCentral_selectedSimulator'] = self.GUIOs["SIMULATORS_SIMULATORSELECTIONBOX"].getSelected()
        if (self.puVar['simulatorCentral_selectedSimulator'] == 'total'):
            allSimulatorsActive = True
            for simulatorIndex in range (self.puVar['simulatorCentral']['nSimulators']):
                if (self.puVar['simulatorCentral']['simulatorActivation'][simulatorIndex] == False): allSimulatorsActive = False; break
            self.GUIOs["SIMULATORS_ACTIVATIONSWITCH"].setStatus(status = allSimulatorsActive, animate = False, callStatusUpdateFunction = False)
        else:
            simulatorActive = self.puVar['simulatorCentral']['simulatorActivation'][self.puVar['simulatorCentral_selectedSimulator']]
            self.GUIOs["SIMULATORS_ACTIVATIONSWITCH"].setStatus(status = simulatorActive, animate = False, callStatusUpdateFunction = False)
        self.pageAuxillaryFunctions['UPDATESIMULATORSDATA'](updateAll = False)
    def __onStatusUpdate_Simulators_ActivationSwitch(objInstance, **kwargs):
        switchStatus = self.GUIOs["SIMULATORS_ACTIVATIONSWITCH"].getStatus()
        if (self.puVar['simulatorCentral_selectedSimulator'] == 'total'): targetSimulatorIndex = 'all'
        else:                                                             targetSimulatorIndex = self.puVar['simulatorCentral_selectedSimulator']
        self.ipcA.sendFAR(targetProcess = 'SIMULATIONMANAGER', functionID = 'setSimulatorActivation', functionParams = {'targetSimulatorIndex': targetSimulatorIndex, 'activation': switchStatus}, farrHandler = self.pageAuxillaryFunctions['_FARR_ONSIMULATIONCONTROLREQUESTRESPONSE'])
    objFunctions['ONSELECTIONUPDATE_SIMULATORS_SIMULATORSELECTION'] = __onSelectionUpdate_Simulators_SimulatorSelection
    objFunctions['ONSTATUSUPDATED_SIMULATORS_ACTIVATIONSWITCH']     = __onStatusUpdate_Simulators_ActivationSwitch
    
    #<Simulations>
    def __onTextUpdate_Simulations_SearchText(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONSIMULATIONSFILTERUPDATE']()
    def __onSelectionUpdate_Simulations_SortType(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONSIMULATIONSFILTERUPDATE']()
    def __onSelectionUpdate_Simulations_SimulationSelection(objInstance, **kwargs):
        try:    _simulation_selected = self.GUIOs["SIMULATIONS_SELECTIONBOX"].getSelected()[0]
        except: _simulation_selected = None
        self.puVar['simulation_selected'] = _simulation_selected
        self.pageAuxillaryFunctions['ONSIMULATIONSELECTIONUPDATE']()
    objFunctions['ONTEXTUPDATE_SIMULATIONS_SEARCHTEXT']               = __onTextUpdate_Simulations_SearchText
    objFunctions['ONSELECTIONUPDATE_SIMULATIONS_SORTTYPE']            = __onSelectionUpdate_Simulations_SortType
    objFunctions['ONSELECTIONUPDATE_SIMULATIONS_SIMULATIONSELECTION'] = __onSelectionUpdate_Simulations_SimulationSelection

    #<General>
    def __onTextUpdate_General_SimulationCode(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANADDSIMULATION']()
    def __onTextUpdate_General_SimulationRange(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANADDSIMULATION']()
    def __onSwitchUpdate_General_AnalysisExport(objInstance, **kwargs):
        _switchStatus = self.GUIOs["GENERAL_ANALYSISEXPORTSWITCH"].getStatus()
        self.puVar['simulationSetup_analysisExport'] = _switchStatus
    def __onButtonRelease_General_AddSimulation(objInstance, **kwarg):
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        pafs  = self.pageAuxillaryFunctions
        ss_positions = puVar['simulationSetup_positions']
        cacs         = puVar['currencyAnalysisConfigurations']
        tcs          = puVar['tradeConfigurations']
        func_sendFAR = self.ipcA.sendFAR

        #[2]: Collect Simulation Parameters
        positions_tradable = set(symbol for symbol, position in ss_positions.items() if position['tradable'])

        #---[2-1]: Simulation code
        simCode = guios["GENERAL_SIMULATIONCODETEXTINPUTBOX"].getText()
        if simCode == "": simCode = None

        #---[2-2]: Simulation Range
        simulationRange = (int(datetime.strptime(guios["GENERAL_SIMULATIONRANGETEXTINPUTBOX1"].getText(), "%Y/%m/%d %H:%M").timestamp()-time.timezone), 
                           int(datetime.strptime(guios["GENERAL_SIMULATIONRANGETEXTINPUTBOX2"].getText(), "%Y/%m/%d %H:%M").timestamp()-time.timezone))
        
        #---[2-3]: Assets
        assets = dict()
        for assetName in puVar['simulationSetup_assets']:
            positions_tradable_asset = [symbol for symbol in positions_tradable if ss_positions[symbol]['quoteAsset'] == assetName]
            ss_asset                 = puVar['simulationSetup_assets'][assetName]
            assets[assetName] = {'initialWalletBalance': ss_asset['initialWalletBalance'],
                                 'allocatableBalance':   ss_asset['allocatableBalance'],
                                 'allocatedBalance':     ss_asset['allocatedBalance'],
                                 'allocationRatio':      ss_asset['allocationRatio'],
                                 'assumedRatio':         ss_asset['assumedRatio'],
                                 'weightedAssumedRatio': ss_asset['weightedAssumedRatio'],
                                 'maxAllocatedBalance':  ss_asset['maxAllocatedBalance'],
                                 '_positionSymbols':                set(symbol for symbol in ss_asset['_positionSymbols'] if symbol in positions_tradable),
                                 '_positionSymbols_crossed':        set(symbol for symbol in positions_tradable_asset     if not ss_positions[symbol]['isolated']),
                                 '_positionSymbols_isolated':       set(symbol for symbol in positions_tradable_asset     if     ss_positions[symbol]['isolated']),
                                 '_positionSymbols_prioritySorted': [symbol for symbol in ss_asset['_positionSymbols_prioritySorted'] if symbol in positions_tradable]}
            
        #---[2-4]: Positions
        positions = dict()
        for symbol in positions_tradable:
            ss_position = puVar['simulationSetup_positions'][symbol]
            positions[symbol] = {'quoteAsset':                        ss_position['quoteAsset'],
                                 'precisions':                        ss_position['precisions'].copy(),
                                 'dataRanges':                        {t: drs.copy() if drs is not None else None for t, drs in ss_position['dataRanges'].items()},
                                 'currencyAnalysisConfigurationCode': ss_position['currencyAnalysisConfigurationCode'],
                                 'tradeConfigurationCode':            ss_position['tradeConfigurationCode'],
                                 'isolated':                          ss_position['isolated'],
                                 'leverage':                          ss_position['leverage'],
                                 'priority':                          ss_position['priority'],
                                 'assumedRatio':                      ss_position['assumedRatio'],
                                 'weightedAssumedRatio':              ss_position['weightedAssumedRatio'],
                                 'allocatedBalance':                  ss_position['allocatedBalance'],
                                 'maxAllocatedBalance':               ss_position['maxAllocatedBalance'],
                                 'firstOpenTSs':                      ss_position['firstOpenTSs'].copy(),
                                 'tradable':                          True}
            
        #---[2-5]: Currency Analysis Configurations
        sim_cacs = {cacCode: {iID: cac_iID.copy() for iID, cac_iID in cacs[cacCode].items()} 
                    for cacCode in [ss_positions[symbol]['currencyAnalysisConfigurationCode'] for symbol in positions_tradable]
                    if cacCode in cacs}

        #---[2-6]: Trade Configurations
        sim_tcs = {tcCode: tcs[tcCode].copy() 
                   for tcCode in [ss_positions[symbol]['tradeConfigurationCode'] for symbol in positions_tradable] 
                   if tcCode in tcs}

        #[3]: Request Dispatch
        func_sendFAR(targetProcess  = 'SIMULATIONMANAGER', 
                     functionID     = 'addSimulation', 
                     functionParams = {'simulationCode':                  simCode, 
                                        'simulationRange':                simulationRange,
                                        'analysisExport':                 puVar['simulationSetup_analysisExport'],
                                        'assets':                         assets,
                                        'positions':                      positions,
                                        'currencyAnalysisConfigurations': sim_cacs,
                                        'tradeConfigurations':            sim_tcs},
                     farrHandler = pafs['_FARR_ONSIMULATIONCONTROLREQUESTRESPONSE'])
        
        #[4]: Button Deactivation
        guios["GENERAL_ADDSIMULATIONBUTTON"].deactivate()
    def __onButtonRelease_General_RemoveSimulation(objInstance, **kwarg):
        self.ipcA.sendFAR(targetProcess = 'SIMULATIONMANAGER', functionID = 'removeSimulation', functionParams = {'simulationCode': self.puVar['simulation_selected']}, farrHandler = self.pageAuxillaryFunctions['_FARR_ONSIMULATIONCONTROLREQUESTRESPONSE'])
        self.GUIOs["GENERAL_REMOVESIMULATIONBUTTON"].deactivate()
    def __onButtonRelease_General_ReplicateConfiguration(objInstance, **kwarg):
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        pafs  = self.pageAuxillaryFunctions
        sims         = puVar['simulations']
        simCode_sel  = puVar['simulation_selected']
        ss_positions = puVar['simulationSetup_positions']
        ss_assets    = puVar['simulationSetup_assets']
        cacs         = puVar['currencyAnalysisConfigurations']
        tcs          = puVar['tradeConfigurations']

        #[2]: Replicate Button Deactivation
        guios["GENERAL_REPLICATECONFIGURATIONBUTTON"].deactivate()

        #[3]: Copy Previous Data
        positions_prev = {symbol: ss_position.copy() for symbol, ss_position in ss_positions.items()}

        #[4]: Replication
        sim_toCopy           = sims[simCode_sel]
        sim_toCopy_positions = sim_toCopy['positions']
        sim_toCopy_assets    = sim_toCopy['assets']

        #---[4-1]: Assets
        for assetName, ss_asset in ss_assets.items():
            if assetName in sim_toCopy_assets:
                asset_toCopy = sim_toCopy_assets[assetName]
                ss_asset['initialWalletBalance'] = asset_toCopy['initialWalletBalance']
                ss_asset['allocationRatio']      = asset_toCopy['allocationRatio']
                ss_asset['allocatableBalance']   = round(ss_asset['initialWalletBalance']*ss_asset['allocationRatio']*_ACCOUNT_BASEASSETALLOCATABLERATIO, _ASSETPRECISIONS[assetName])
            else:
                ss_asset['initialWalletBalance'] = 0
                ss_asset['allocationRatio']      = 0.500
                ss_asset['allocatableBalance']   = 0

        #---[4-2]: Positions
        for symbol, ss_position in ss_positions.items():
            if symbol in sim_toCopy_positions:
                position_toCopy = sim_toCopy_positions[symbol]
                ss_position['assumedRatio']        = position_toCopy['assumedRatio']
                ss_position['maxAllocatedBalance'] = position_toCopy['maxAllocatedBalance']
                cacCode_toCopy = position_toCopy['currencyAnalysisConfigurationCode']
                tcCode_toCopy  = position_toCopy['tradeConfigurationCode']
                ss_position['currencyAnalysisConfigurationCode'] = cacCode_toCopy if cacCode_toCopy in cacs else None
                ss_position['tradeConfigurationCode']            = tcCode_toCopy  if tcCode_toCopy  in tcs  else None
                if ss_position['tradeConfigurationCode'] is None:
                    ss_position['isolated']             = None
                    ss_position['leverage']             = None
                    ss_position['weightedAssumedRatio'] = None
                else:
                    tc = tcs[ss_position['tradeConfigurationCode']]
                    ss_position['isolated']             = tc['isolated']
                    ss_position['leverage']             = tc['leverage']
                    ss_position['weightedAssumedRatio'] = ss_position['assumedRatio']*tc['leverage']
                pafs['UPDATEPOSITIONPRIORITY'](positionSymbol = symbol, newPriority = position_toCopy['priority'])
                #Tradability
                ss_position['tradable'] = (ss_position['currencyAnalysisConfigurationCode'] is not None and ss_position['tradeConfigurationCode'] is not None)
            else:
                ss_position['currencyAnalysisConfigurationCode'] = None
                ss_position['tradeConfigurationCode']            = None
                ss_position['isolated']                          = None
                ss_position['leverage']                          = None
                ss_position['assumedRatio']                      = 0
                ss_position['weightedAssumedRatio']              = None
                ss_position['maxAllocatedBalance']               = float('inf')
                ss_position['tradable']                          = False

        #---[4-3]: Position Dependent Assets
        for assetName in sim_toCopy_assets:
            pafs['SORTPOSITIONSYMBOLSBYPRIORITY'](assetName = assetName)
            pafs['ALLOCATEWALLETBALANCE'](assetName         = assetName)
            pafs['COMPUTEPOSITIONSUMS'](assetName           = assetName)

        #---[4-4]: Simulation Range
        guios["GENERAL_SIMULATIONCODETEXTINPUTBOX"].updateText(text   = simCode_sel)
        guios["GENERAL_SIMULATIONRANGETEXTINPUTBOX1"].updateText(text = datetime.fromtimestamp(sim_toCopy['simulationRange'][0], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
        guios["GENERAL_SIMULATIONRANGETEXTINPUTBOX2"].updateText(text = datetime.fromtimestamp(sim_toCopy['simulationRange'][1], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))

        #[5]: Graphics Update
        pafs['UPDATEPOSITIONSGRAPHICS'](positionsPrev = positions_prev)
        guios["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text      = f"Assets and Positions Configuration Successfully Copied From '{simCode_sel}'", 
                                                       textStyle = "GREEN_LIGHT")
    def __onButtonRelease_General_ViewResult(objInstance, **kwarg):
        puVar_SimulationResult = self.sysFunctions['GETPAGEPUVAR']('SIMULATIONRESULT')
        puVar_SimulationResult['simulation_toLoad'] = self.puVar['simulation_selected']
        self.sysFunctions['LOADPAGE']('SIMULATIONRESULT')
    objFunctions['ONTEXTUPDATE_GENERAL_SIMULATIONCODE']            = __onTextUpdate_General_SimulationCode
    objFunctions['ONTEXTUPDATE_GENERAL_SIMULATIONRANGE']           = __onTextUpdate_General_SimulationRange
    objFunctions['ONSWITCHUPDATE_GENERAL_ANALYSISEXPORT']          = __onSwitchUpdate_General_AnalysisExport
    objFunctions['ONBUTTONRELEASE_GENERAL_ADDSIMULATION']          = __onButtonRelease_General_AddSimulation
    objFunctions['ONBUTTONRELEASE_GENERAL_REMOVESIMULATION']       = __onButtonRelease_General_RemoveSimulation
    objFunctions['ONBUTTONRELEASE_GENERAL_REPLICATECONFIGURATION'] = __onButtonRelease_General_ReplicateConfiguration
    objFunctions['ONBUTTONRELEASE_GENERAL_VIEWRESULT']             = __onButtonRelease_General_ViewResult

    #<Positions>
    def __onTextUpdate_Positions_SearchText(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONPOSITIONSFILTERUPDATE']()
    def __onSelectionUpdate_Positions_SearchType(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONPOSITIONSFILTERUPDATE']()
    def __onSelectionUpdate_Positions_SortType(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONPOSITIONSFILTERUPDATE']()
    def __onSelectionUpdate_Positions_TradableFilter(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONPOSITIONSFILTERUPDATE']()
    def __onButtonRelease_Positions_Initialization(objInstance, **kwargs):
        self.GUIOs["POSITIONS_INITIALIZATIONBUTTON"].deactivate()
        self.pageAuxillaryFunctions['INITIALIZEPOSITIONS']()
    def __onButtonRelease_Positions_ReleaseAll(objInstance, **kwargs):
        self.GUIOs["POSITIONS_SETUPSELECTIONBOX"].clearSelected()
        self.pageAuxillaryFunctions['ONPOSITIONSELECTIONUPDATE']()
    def __onSelectionUpdate_Positions_Position(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONPOSITIONSELECTIONUPDATE']()
    def __onSelectionUpdate_Positions_CurrencyAnalysisConfigurationCode(objInstance, **kwargs):
        self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODERESETBUTTON"].activate()
        self.pageAuxillaryFunctions['CHECKIFCANEDITPOSITIONPARAMS']()
    def __onSelectionUpdate_Positions_TradeConfigurationCode(objInstance, **kwargs):
        self.GUIOs["POSITIONS_TRADECONFIGURATIONCODERESETBUTTON"].activate()
        self.pageAuxillaryFunctions['CHECKIFCANEDITPOSITIONPARAMS']()
    def __onButtonRelease_Positions_ResetCurrencyAnalysisConfigurationCode(objInstance, **kwargs):
        self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODERESETBUTTON"].deactivate()
        self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODESELECTIONBOX"].setSelected(itemKey = None, callSelectionUpdateFunction = False)
        self.pageAuxillaryFunctions['CHECKIFCANEDITPOSITIONPARAMS']()
    def __onButtonRelease_Positions_ResetTradeConfigurationCode(objInstance, **kwargs):
        self.GUIOs["POSITIONS_TRADECONFIGURATIONCODERESETBUTTON"].deactivate()
        self.GUIOs["POSITIONS_TRADECONFIGURATIONCODESELECTIONBOX"].setSelected(itemKey = None, callSelectionUpdateFunction = False)
        self.pageAuxillaryFunctions['CHECKIFCANEDITPOSITIONPARAMS']()
    def __onTextUpdate_Positions_AssumedRatio(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANEDITPOSITIONPARAMS']()
    def __onTextUpdate_Positions_Priority(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANEDITPOSITIONPARAMS']()
    def __onTextUpdate_Positions_MaxAllocatedBalance(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANEDITPOSITIONPARAMS']()
    def __onButtonRelease_Positions_EditPositionParams(objInstance, **kwargs):
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        pafs  = self.pageAuxillaryFunctions
        ss_positions = puVar['simulationSetup_positions']
        tcs          = puVar['tradeConfigurations']

        #[2]: Position Apply Button Deactivation
        guios["POSITIONS_POSITIONAPPLYBUTTON"].deactivate()

        #[3]: Copy Previous Data
        positions_prev = {symbol: ss_position.copy() for symbol, ss_position in ss_positions.items()}

        #[4]: Position Params
        cacCode      = guios["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODESELECTIONBOX"].getSelected()
        tcCode       = guios["POSITIONS_TRADECONFIGURATIONCODESELECTIONBOX"].getSelected()
        assumedRatio = round(float(guios["POSITIONS_ASSUMEDRATIOTEXTINPUTBOX"].getText())/100, 5)
        try:    priority = int(guios["POSITIONS_PRIORITYTEXTINPUTBOX"].getText())
        except: priority = None
        maxAllocatedBalance_str = guios["POSITIONS_MAXALLOCATEDBALANCETEXTINPUTBOX"].getText()
        if maxAllocatedBalance_str == "": maxAllocatedBalance = float('inf')
        else:                             maxAllocatedBalance = float(maxAllocatedBalance_str)

        #[5]: Position Update
        symbols_sel   = guios["POSITIONS_SETUPSELECTIONBOX"].getSelected()
        nSymbols_sel  = len(symbols_sel)
        assets_update = set()
        for symbol in symbols_sel:
            position = ss_positions[symbol]
            #[5-1]: Currency Analysis Configuration Code
            position['currencyAnalysisConfigurationCode'] = cacCode
            #[5-2]: Trade Configuration Code
            position['tradeConfigurationCode'] = tcCode
            if tcCode is None:
                position['isolated'] = None
                position['leverage'] = None
            else:
                tc = tcs[tcCode]
                position['isolated'] = tc['isolated']
                position['leverage'] = tc['leverage']
            #[5-3]: Assumed Ratio
            position['assumedRatio'] = assumedRatio
            if tcCode is None: position['weightedAssumedRatio'] = None
            else:              position['weightedAssumedRatio'] = assumedRatio*tcs[tcCode]['leverage']
            #[5-4]: Priority
            if nSymbols_sel == 1: pafs['UPDATEPOSITIONPRIORITY'](positionSymbol = symbol, newPriority = priority)
            #[5-5]: Maximum Allocated Balance
            position['maxAllocatedBalance'] = maxAllocatedBalance if maxAllocatedBalance == float('inf') else round(maxAllocatedBalance, position['precisions']['quote'])
            #[5-6]: Tradability
            position['tradable'] = (cacCode is not None and tcCode is not None)
            #[5-7]: Asset To Update
            assets_update.add(position['quoteAsset'])

        #[6]: Reallocate balance and recompute position sums
        for assetName in assets_update:
            pafs['SORTPOSITIONSYMBOLSBYPRIORITY'](assetName = assetName)
            pafs['ALLOCATEWALLETBALANCE'](assetName         = assetName)
            pafs['COMPUTEPOSITIONSUMS'](assetName           = assetName)

        #[7]: Update Graphics
        pafs['UPDATEPOSITIONSGRAPHICS'](positionsPrev = positions_prev)
        pafs['UPDATEASSETDATADISPLAY']()

        #[8]: Positions Initialization Button Activation
        guios["POSITIONS_INITIALIZATIONBUTTON"].activate()
    objFunctions['ONTEXTUPDATE_POSITIONS_SEARCHTEXT']                               = __onTextUpdate_Positions_SearchText
    objFunctions['ONSELECTIONUPDATE_POSITIONS_SEARCHTYPE']                          = __onSelectionUpdate_Positions_SearchType
    objFunctions['ONSELECTIONUPDATE_POSITIONS_SORTTYPE']                            = __onSelectionUpdate_Positions_SortType
    objFunctions['ONSELECTIONUPDATE_POSITIONS_TRADABLEFILTER']                      = __onSelectionUpdate_Positions_TradableFilter
    objFunctions['ONBUTTONRELEASE_POSITIONS_INITIALIZE']                            = __onButtonRelease_Positions_Initialization
    objFunctions['ONBUTTONRELEASE_POSITIONS_RELEASEALL']                            = __onButtonRelease_Positions_ReleaseAll
    objFunctions['ONSELECTIONUPDATE_POSITIONS_POSITION']                            = __onSelectionUpdate_Positions_Position
    objFunctions['ONSELECTIONUPDATE_POSITIONS_CURRENCYANALYSISCONFIGURATIONCODE']   = __onSelectionUpdate_Positions_CurrencyAnalysisConfigurationCode
    objFunctions['ONSELECTIONUPDATE_POSITIONS_TRADECONFIGURATIONCODE']              = __onSelectionUpdate_Positions_TradeConfigurationCode
    objFunctions['ONBUTTONRELEASE_POSITIONS_RESETCURRENCYANALYSISCONFIURATIONCODE'] = __onButtonRelease_Positions_ResetCurrencyAnalysisConfigurationCode
    objFunctions['ONBUTTONRELEASE_POSITIONS_RESETTRADECONFIGURATIONCODE']           = __onButtonRelease_Positions_ResetTradeConfigurationCode
    objFunctions['ONTEXTUPDATE_POSITIONS_ASSUMEDRATIO']                             = __onTextUpdate_Positions_AssumedRatio
    objFunctions['ONTEXTUPDATE_POSITIONS_PRIORITY']                                 = __onTextUpdate_Positions_Priority
    objFunctions['ONTEXTUPDATE_POSITIONS_MAXALLOCATEDBALANCE']                      = __onTextUpdate_Positions_MaxAllocatedBalance
    objFunctions['ONBUTTONRELEASE_POSITIONS_EDITPOSITIONPARAMS']                    = __onButtonRelease_Positions_EditPositionParams

    #<Assets>
    def __onSelectionUpdate_Assets_AssetSelection(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONASSETSELECTIONUPDATE']()
    def __onTextUpdate_Assets_InitialWalletBalance(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANEDITASSETPARAMS']()
    def __onValueUpdate_Assets_AllocationRatioSlider(objInstance, **kwargs):
        _sliderVal = self.GUIOs["ASSETS_ALLOCATIONRATIOSLIDER"].getSliderValue()
        self.GUIOs["ASSETS_ALLOCATIONRATIODISPLAYTEXT"].updateText("{:.1f} %".format(_sliderVal))
        self.pageAuxillaryFunctions['CHECKIFCANEDITASSETPARAMS']()
    def __onButtonRelease_Assets_EditAssetParams(objInstance, **kwargs):
        self.GUIOs["ASSETS_ASSETAPPLYBUTTON"].deactivate()
        _assetName_selected = self.GUIOs["ASSETS_ASSETSELECTIONBOX"].getSelected()
        #Copy Previous Positions Data
        _positions_prev = dict()
        for _pSymbol in self.puVar['simulationSetup_positions']: _positions_prev[_pSymbol] = self.puVar['simulationSetup_positions'][_pSymbol].copy()
        #Get Entered Values
        _initialWalletBalance = round(float(self.GUIOs["ASSETS_INITIALWALLETBALANCETEXTINPUTBOX"].getText()), _ASSETPRECISIONS[_assetName_selected])
        _allocationRatio      = round(self.GUIOs["ASSETS_ALLOCATIONRATIOSLIDER"].getSliderValue()/100, 3)
        #Update Current Values
        _asset = self.puVar['simulationSetup_assets'][_assetName_selected]
        _asset['initialWalletBalance'] = _initialWalletBalance
        _asset['allocationRatio']      = _allocationRatio
        _asset['allocatableBalance']   = round(_asset['initialWalletBalance']*_asset['allocationRatio']*_ACCOUNT_BASEASSETALLOCATABLERATIO, _ASSETPRECISIONS[_assetName_selected])
        #Reallocate wallet balance and recompute position sums
        self.pageAuxillaryFunctions['ALLOCATEWALLETBALANCE'](assetName = _assetName_selected)
        self.pageAuxillaryFunctions['COMPUTEPOSITIONSUMS'](assetName = _assetName_selected)
        #Update Graphics
        self.pageAuxillaryFunctions['UPDATEPOSITIONSGRAPHICS'](positionsPrev = _positions_prev)
        self.pageAuxillaryFunctions['UPDATEASSETDATADISPLAY']()
    objFunctions['ONSELECTIONUPDATE_ASSETS_ASSETSELECTION']    = __onSelectionUpdate_Assets_AssetSelection
    objFunctions['ONTEXTUPDATE_ASSETS_INITIALWALLETBALANCE']   = __onTextUpdate_Assets_InitialWalletBalance
    objFunctions['ONVALUEUPDATE_ASSETS_ALLOCATIONRATIOSLIDER'] = __onValueUpdate_Assets_AllocationRatioSlider
    objFunctions['ONBUTTONRELEASE_ASSETS_EDITASSETPARAMS']     = __onButtonRelease_Assets_EditAssetParams

    #Return the generated functions
    return objFunctions
#OBJECT FUNCTIONS END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUXILALRY FUNCTIONS --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateAuxillaryFunctions(self):
    auxFunctions = dict()

    #<_PAGELOAD>
    def __far_onCurrenciesUpdate(requester, updatedContents):
        #[1]: Source Check
        if requester != 'DATAMANAGER':
            return
        
        #[2]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        pafs  = self.pageAuxillaryFunctions
        currencies   = puVar['currencies']
        simCode_sel  = puVar['simulation_selected']
        ss_positions = puVar['simulationSetup_positions']
        func_getPRD = self.ipcA.getPRD
        vm_gtp      = self.visualManager.getTextPack
        
        #[3]: Updates Read
        for uContent in updatedContents:
            #[3-1]: Instances
            symbol    = uContent['symbol']
            contentID = uContent['id']

            #[3-2]: New Currency
            if contentID == '_ADDED':
                #[3-2-1]: New Currency Data
                currency = func_getPRD(processName = 'DATAMANAGER', 
                                       prdAddress = ('CURRENCIES', symbol))
                currencies[symbol] = currency

                #[3-2-2]: Data Ranges & First Open Timestamps
                drs   = dict()
                foTSs = dict()
                for t in ('kline', 'depth', 'aggTrade'):
                    if currency[f'{t}s_availableRanges']: drs[t] = currency[f'{t}s_availableRanges'].copy()
                    else:                                 drs[t] = None
                    foTSs[t] = currency[f'{t}_firstOpenTS']

                #[3-2-3]: New Setup Position
                ss_positions[symbol] = {'quoteAsset':                        currency['quoteAsset'],
                                        'precisions':                        currency['precisions'].copy(),
                                        'dataRanges':                        drs,
                                        'currencyAnalysisConfigurationCode': None,
                                        'tradeConfigurationCode':            None,
                                        'isolated':                          None,
                                        'leverage':                          None,
                                        'priority':                          len(self.puVar['simulationSetup_positions'])+1,
                                        'assumedRatio':                      0,
                                        'weightedAssumedRatio':              None,
                                        'allocatedBalance':                  0,
                                        'maxAllocatedBalance':               float('inf'),
                                        'firstOpenTSs':                      foTSs,
                                        'tradable':                          False}
                
                #[3-2-4]: Setup Positions List Update
                if simCode_sel is None:
                    pafs['SETSETUPPOSITIONSLIST']()

            #[3-3]: Currency Update
            else:
                #[3-3-1]: Currency Server Information Updated
                if contentID[0] == 'info_server': 
                    #[3-3-1-1]: Instances
                    try:    contentID_1 = contentID[1]
                    except: contentID_1 = None
                    currency = currencies[symbol]

                    #[3-3-1-2]: Updates Check
                    update_status      = False
                    update_minNotional = False
                    #---[3-3-1-2-1]: Entire Server Information Updated
                    if contentID_1 is None:
                        currency['info_server'] = func_getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'info_server'))
                        update_status      = True
                        update_minNotional = True
                    #---[3-3-1-2-2]: Currency Status Updated
                    else:
                        if contentID_1 == 'status':
                            currency['info_server']['status'] = func_getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'info_server', 'status'))
                            update_status = True

                    #[3-3-1-3]: Updates Handling
                    sInfo = currency['info_server']
                    #---[3-3-1-3-1]: Status Updated
                    if update_status:
                        status = None if sInfo is None else sInfo['status']
                        if   status == 'TRADING':  text = vm_gtp('SIMULATION:POSITIONS_MARKETSTATUS_TRADING');  textColor = 'GREEN_LIGHT'
                        elif status == 'SETTLING': text = vm_gtp('SIMULATION:POSITIONS_MARKETSTATUS_SETTLING'); textColor = 'RED_LIGHT'
                        elif status == 'REMOVED':  text = vm_gtp('SIMULATION:POSITIONS_MARKETSTATUS_REMOVED');  textColor = 'RED_DARK'
                        elif status is None:       text = '-';                                                  textColor = 'BLUE_DARK'
                        else:                      text = status;                                               textColor = 'VIOLET'
                        nsbi = {'text': text, 'textStyles': [('all', textColor),]}
                        guios["POSITIONS_SETUPSELECTIONBOX"].editSelectionListItem(itemKey = symbol, item = nsbi, columnIndex = _POSITIONDATA_SELECTIONBOXCOLUMNINDEX_AUX['marketStatus'])

                    #---[3-3-1-3-2]: Min Notional Update
                    if update_minNotional:
                        if sInfo is None: 
                            text = 'N/A'
                        else:
                            minNotional = None
                            for flt in sInfo['filters']:
                                if flt['filterType'] != 'MIN_NOTIONAL':
                                    continue
                                minNotional = flt['notional']
                                break
                            if minNotional is None: text = "-"
                            else:                   text = minNotional
                        nsbi = {'text': text}
                        guios["POSITIONS_SETUPSELECTIONBOX"].editSelectionListItem(itemKey = symbol, item = nsbi, columnIndex = _POSITIONDATA_SELECTIONBOXCOLUMNINDEX_AUX['minNotional'])

                #[3-3-2]: klineFirstOpenTS Updated
                elif contentID[0] == 'kline_firstOpenTS':
                    foTS_new = func_getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'kline_firstOpenTS'))
                    currencies[symbol]['kline_firstOpenTS']       = foTS_new
                    ss_positions[symbol]['firstOpenTSs']['kline'] = foTS_new
                    if simCode_sel is None:
                        if foTS_new is None: foTS_str = "-"
                        else:                foTS_str = datetime.fromtimestamp(foTS_new, tz=timezone.utc).strftime("%Y/%m/%d %H:%M")
                        nsbi = {'text': foTS_str}
                        guios["POSITIONS_SETUPSELECTIONBOX"].editSelectionListItem(itemKey     = symbol, 
                                                                                   item        = nsbi, 
                                                                                   columnIndex = 11)

                #[3-3-3]: depthFirstOpenTS Updated
                elif contentID[0] == 'depth_firstOpenTS':
                    foTS_new = func_getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'depth_firstOpenTS'))
                    currencies[symbol]['depth_firstOpenTS']       = foTS_new
                    ss_positions[symbol]['firstOpenTSs']['depth'] = foTS_new

                #[3-3-4]: aggTradeFirstOpenTS Updated
                elif contentID[0] == 'aggTrade_firstOpenTS':
                    foTS_new = func_getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'aggTrade_firstOpenTS'))
                    currencies[symbol]['aggTrade_firstOpenTS']       = foTS_new
                    ss_positions[symbol]['firstOpenTSs']['aggTrade'] = foTS_new

                #[3-3-5]: klineAvailableRanges Updated
                elif contentID[0] == 'klines_availableRanges':
                    aRanges_new = func_getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'klines_availableRanges'))
                    currencies[symbol]['klines_availableRanges'] = aRanges_new
                    ss_positions[symbol]['dataRanges']['kline']  = aRanges_new.copy() if aRanges_new else None

                #[3-3-6]: depthsAvailableRanges Updated
                elif contentID[0] == 'depths_availableRanges':
                    aRanges_new = func_getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'depths_availableRanges'))
                    currencies[symbol]['depths_availableRanges'] = aRanges_new
                    ss_positions[symbol]['dataRanges']['depth']  = aRanges_new.copy() if aRanges_new else None

                #[3-3-7]: aggTradesAvailableRanges Updated
                elif contentID[0] == 'aggTrades_availableRanges':
                    aRanges_new = func_getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'aggTrades_availableRanges'))
                    currencies[symbol]['aggTrades_availableRanges'] = aRanges_new
                    ss_positions[symbol]['dataRanges']['aggTrade']  = aRanges_new.copy() if aRanges_new else None
    def __far_onAnalysisConfigurationUpdate(requester, updateType, currencyAnalysisConfigurationCode):
        #[1]: Source Check
        if requester != 'TRADEMANAGER':
            return

        #[2]: Instances
        puVar = self.puVar
        pafs  = self.pageAuxillaryFunctions
        func_getPRD = self.ipcA.getPRD
        cacCode = currencyAnalysisConfigurationCode

        #[3]: Update Handling
        #---[3-1]: Added
        if updateType == 'ADDED':
            puVar['currencyAnalysisConfigurations'][cacCode] = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSISCONFIGURATIONS', cacCode))
            pafs['SETCURRENCYANALYSISCONFIGURATIONLIST']()

        #---[3-2]: Removed
        elif updateType == 'REMOVED':
            puVar['currencyAnalysisConfigurations'].pop(cacCode, None)
            pafs['SETCURRENCYANALYSISCONFIGURATIONLIST']()
    def __far_onTradeConfigurationUpdate(requester, updateType, tradeConfigurationCode):
        if (requester == 'TRADEMANAGER'):
            if (updateType == 'ADDED'):
                self.puVar['tradeConfigurations'][tradeConfigurationCode] = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('TRADECONFIGURATIONS', tradeConfigurationCode))
                self.pageAuxillaryFunctions['SETTRADECONFIGURATIONLIST']()
            elif (updateType == 'REMOVED'):
                self.pageAuxillaryFunctions['SETTRADECONFIGURATIONLIST']()
                if (tradeConfigurationCode == self.puVar['tradeConfiguration_selected']): 
                    self.puVar['tradeConfiguration_selected'] = None
                    self.GUIOs["ADDSIMULATION&SIMULATIONPARAMETERS_TRADECONFIGURATIONCODEDISPLAYTEXT"].updateText("-")
                    self.pageAuxillaryFunctions['CHECKIFCANADDSIMULATION']()
    def __far_onSimulatorCentralUpdate(requester, updatedContents):
        if (requester == 'SIMULATIONMANAGER'):
            for updatedContent in updatedContents:
                updatedContent_type = type(updatedContent)
                if (updatedContent_type == str):
                    if (updatedContent == 'nSimulations_COMPLETED'):
                        nSimulations = self.ipcA.getPRD(processName = 'SIMULATIONMANAGER', prdAddress = ('SIMULATORCENTRAL', 'nSimulations_COMPLETED'))
                        self.puVar['simulatorCentral']['nSimulations_COMPLETED'] = nSimulations
                        self.GUIOs["SIMULATORS_SIMULATIONSCOMPLETEDDISPLAYTEXT"].updateText(text = str(nSimulations))
                elif (updatedContent_type == tuple):
                    if (updatedContent[0] == 'nSimulations_total'):
                        updatedSimulator = updatedContent[1]
                        nSimulations = self.ipcA.getPRD(processName = 'SIMULATIONMANAGER', prdAddress = ('SIMULATORCENTRAL', 'nSimulations_total', updatedSimulator))
                        self.puVar['simulatorCentral']['nSimulations_total'][updatedSimulator] = nSimulations
                        if (updatedSimulator == self.puVar['simulatorCentral_selectedSimulator']): self.GUIOs["SIMULATORS_SIMULATIONSTOTALDISPLAYTEXT"].updateText(text = str(nSimulations))
                    elif (updatedContent[0] == 'nSimulations_QUEUED'):
                        updatedSimulator = updatedContent[1]
                        nSimulations = self.ipcA.getPRD(processName = 'SIMULATIONMANAGER', prdAddress = ('SIMULATORCENTRAL', 'nSimulations_QUEUED', updatedSimulator))
                        self.puVar['simulatorCentral']['nSimulations_QUEUED'][updatedSimulator] = nSimulations
                        if (updatedSimulator == self.puVar['simulatorCentral_selectedSimulator']): self.GUIOs["SIMULATORS_SIMULATIONSQUEUEDDISPLAYTEXT"].updateText(text = str(nSimulations))
                    elif (updatedContent[0] == 'nSimulations_PROCESSING'):
                        updatedSimulator = updatedContent[1]
                        nSimulations = self.ipcA.getPRD(processName = 'SIMULATIONMANAGER', prdAddress = ('SIMULATORCENTRAL', 'nSimulations_PROCESSING', updatedSimulator))
                        self.puVar['simulatorCentral']['nSimulations_PROCESSING'][updatedSimulator] = nSimulations
                        if (updatedSimulator == self.puVar['simulatorCentral_selectedSimulator']): self.GUIOs["SIMULATORS_SIMULATIONSPROCESSINGDISPLAYTEXT"].updateText(text = str(nSimulations))
                    elif (updatedContent[0] == 'nSimulations_PAUSED'):
                        updatedSimulator = updatedContent[1]
                        nSimulations = self.ipcA.getPRD(processName = 'SIMULATIONMANAGER', prdAddress = ('SIMULATORCENTRAL', 'nSimulations_PAUSED', updatedSimulator))
                        self.puVar['simulatorCentral']['nSimulations_PAUSED'][updatedSimulator] = nSimulations
                        if (updatedSimulator == self.puVar['simulatorCentral_selectedSimulator']): self.GUIOs["SIMULATORS_SIMULATIONSPAUSEDDISPLAYTEXT"].updateText(text = str(nSimulations))
                    elif (updatedContent[0] == 'nSimulations_ERROR'):
                        updatedSimulator = updatedContent[1]
                        nSimulations = self.ipcA.getPRD(processName = 'SIMULATIONMANAGER', prdAddress = ('SIMULATORCENTRAL', 'nSimulations_ERROR', updatedSimulator))
                        self.puVar['simulatorCentral']['nSimulations_ERROR'][updatedSimulator] = nSimulations
                        if (updatedSimulator == self.puVar['simulatorCentral_selectedSimulator']): self.GUIOs["SIMULATORS_SIMULATIONSERRORDISPLAYTEXT"].updateText(text = str(nSimulations))
                    elif (updatedContent[0] == 'simulatorActivation'):
                        updatedSimulator = updatedContent[1]
                        self.puVar['simulatorCentral']['simulatorActivation'][updatedSimulator] = self.ipcA.getPRD(processName = 'SIMULATIONMANAGER', prdAddress = ('SIMULATORCENTRAL', 'simulatorActivation', updatedSimulator))
    def __far_onSimulationUpdate(requester, updateType, simulationCode):
        #[1]: Source Check
        if requester != 'SIMULATIONMANAGER':
            return
        
        #[2]: Instances
        puVar  = self.puVar
        guios  = self.GUIOs
        pafs   = self.pageAuxillaryFunctions
        vm_gtp = self.visualManager.getTextPack
        sims        = puVar['simulations']
        simCode_sel = puVar['simulation_selected']
        func_getPRD = self.ipcA.getPRD

        #[3]: Update Handling
        #---[3-1]: Simulation Added
        if updateType == 'ADDED':
            sims[simulationCode] = func_getPRD(processName = 'SIMULATIONMANAGER', prdAddress = ('SIMULATIONS', simulationCode))
            pafs['SETSIMULATIONSLIST']()

        #---[3-2]: Simulation Removed
        elif updateType == 'REMOVED':
            del sims[simulationCode]
            pafs['SETSIMULATIONSLIST']()
            if simulationCode == simCode_sel: 
                puVar['simulation_selected'] = None
                pafs['ONSIMULATIONSELECTIONUPDATE']()
                pafs['CHECKIFCANADDSIMULATION']()

        #---[3-3]: Simulation Status Updated
        elif updateType == 'UPDATED_STATUS':
            status = func_getPRD(processName = 'SIMULATIONMANAGER', prdAddress = ('SIMULATIONS', simulationCode, '_status'))
            sims[simulationCode]['_status'] = status
            if simulationCode == simCode_sel:
                if   status == 'COMPLETED':  guios["GENERAL_STATUSDISPLAYTEXT"].updateText(text = vm_gtp('SIMULATION:GENERAL_STATUS_COMPLETED'),  textStyle = 'GREEN')
                elif status == 'QUEUED':     guios["GENERAL_STATUSDISPLAYTEXT"].updateText(text = vm_gtp('SIMULATION:GENERAL_STATUS_QUEUED'),     textStyle = 'BLUE')
                elif status == 'PROCESSING': guios["GENERAL_STATUSDISPLAYTEXT"].updateText(text = vm_gtp('SIMULATION:GENERAL_STATUS_PROCESSING'), textStyle = 'GREEN_LIGHT'); guios["GENERAL_COMPLETIONGAUGEBAR"].updateGaugeColor(rValue =   0, gValue = 200, bValue = 100)
                elif status == 'PAUSED':     guios["GENERAL_STATUSDISPLAYTEXT"].updateText(text = vm_gtp('SIMULATION:GENERAL_STATUS_PAUSED'),     textStyle = 'YELLOW');      guios["GENERAL_COMPLETIONGAUGEBAR"].updateGaugeColor(rValue = 250, gValue = 190, bValue =  10)
                elif status == 'ERROR':      guios["GENERAL_STATUSDISPLAYTEXT"].updateText(text = vm_gtp('SIMULATION:GENERAL_STATUS_ERROR'),      textStyle = 'RED_LIGHT')
            puVar['simulationListUpdate_ItemsToUpdate'].append((simulationCode, 'status'))

        #---[3-4]: Simulation Completion Updated
        elif updateType == 'UPDATED_COMPLETION':
            completion = func_getPRD(processName = 'SIMULATIONMANAGER', prdAddress = ('SIMULATIONS', simulationCode, '_completion'))
            sims[simulationCode]['_completion'] = completion
            if simulationCode == simCode_sel:
                if completion is None or completion == _IPC_PRD_INVALIDADDRESS: 
                    guios["GENERAL_COMPLETIONDISPLAYTEXT"].updateText(text = "-")
                    guios["GENERAL_COMPLETIONGAUGEBAR"].updateGaugeValue(gaugeValue = 0)
                else:
                    guios["GENERAL_COMPLETIONDISPLAYTEXT"].updateText(text = f"{completion*100:.3f} %")
                    guios["GENERAL_COMPLETIONGAUGEBAR"].updateGaugeValue(gaugeValue = completion*100)
            puVar['simulationListUpdate_ItemsToUpdate'].append((simulationCode, 'completion'))

        #---[3-5]: Simulation Completed
        elif updateType == 'COMPLETED':
            sim = func_getPRD(processName = 'SIMULATIONMANAGER', prdAddress = ('SIMULATIONS', simulationCode))
            sims[simulationCode] = sim
            if simulationCode == simCode_sel:
                guios["GENERAL_STATUSDISPLAYTEXT"].updateText(text = vm_gtp('SIMULATION:GENERAL_STATUS_COMPLETED'), textStyle = 'GREEN')
                guios["GENERAL_COMPLETIONDISPLAYTEXT"].updateText(text = "-")
                guios["GENERAL_COMPLETIONGAUGEBAR"].updateGaugeValue(gaugeValue = 0)
                guios["GENERAL_ALLOCATEDSIMUALTORDISPLAYTEXT"].updateText(text = "-")
                guios["GENERAL_VIEWRESULTBUTTON"].activate()
            puVar['simulationListUpdate_ItemsToUpdate'].append((simulationCode, 'status'))
            puVar['simulationListUpdate_ItemsToUpdate'].append((simulationCode, 'completion'))
    auxFunctions['_FAR_ONCURRENCIESUPDATE']            = __far_onCurrenciesUpdate
    auxFunctions['_FAR_ONANALYSISCONFIGURATIONUPDATE'] = __far_onAnalysisConfigurationUpdate
    auxFunctions['_FAR_ONTRADECONFIGURATIONUPDATE']    = __far_onTradeConfigurationUpdate
    auxFunctions['_FAR_ONSIMULATORCENTRALUPDATE']      = __far_onSimulatorCentralUpdate
    auxFunctions['_FAR_ONSIMULATIONUPDATE']            = __far_onSimulationUpdate

    #<Simulators>
    def __updateSimulatorsData(updateAll):
        if (self.puVar['simulatorCentral'] != _IPC_PRD_INVALIDADDRESS):
            if (updateAll == True):
                if (self.puVar['simulatorCentral_nSimulatorsIdentified'] == False):
                    nSimulators = self.puVar['simulatorCentral']['nSimulators']
                    self.GUIOs["SIMULATORS_NUMBEROFSIMULATORSDISPLAYTEXT"].updateText(text = str(nSimulators))
                    simulatorList_formatted = {'total': {'text': 'TOTAL'}}
                    for simulatorIndex in range (nSimulators): simulatorList_formatted[simulatorIndex] = {'text': 'SIMULATOR {:d}'.format(simulatorIndex)}
                    self.GUIOs["SIMULATORS_SIMULATORSELECTIONBOX"].setSelectionList(selectionList = simulatorList_formatted, displayTargets = 'all', keepSelected = True, callSelectionUpdateFunction = False)
                    self.GUIOs["SIMULATORS_SIMULATORSELECTIONBOX"].setSelected(itemKey = 'total', callSelectionUpdateFunction = False)
                    self.puVar['simulatorCentral_selectedSimulator']     = 'total'
                    self.puVar['simulatorCentral_nSimulatorsIdentified'] = True
                self.GUIOs["SIMULATORS_SIMULATIONSCOMPLETEDDISPLAYTEXT"].updateText(text  = str(self.puVar['simulatorCentral']['nSimulations_COMPLETED']))
            selectedSimulator = self.puVar['simulatorCentral_selectedSimulator']
            if (selectedSimulator != None):
                self.GUIOs["SIMULATORS_SIMULATIONSTOTALDISPLAYTEXT"].updateText(text      = str(self.puVar['simulatorCentral']['nSimulations_total'][selectedSimulator]))
                self.GUIOs["SIMULATORS_SIMULATIONSQUEUEDDISPLAYTEXT"].updateText(text     = str(self.puVar['simulatorCentral']['nSimulations_QUEUED'][selectedSimulator]))
                self.GUIOs["SIMULATORS_SIMULATIONSPROCESSINGDISPLAYTEXT"].updateText(text = str(self.puVar['simulatorCentral']['nSimulations_PROCESSING'][selectedSimulator]))
                self.GUIOs["SIMULATORS_SIMULATIONSPAUSEDDISPLAYTEXT"].updateText(text     = str(self.puVar['simulatorCentral']['nSimulations_PAUSED'][selectedSimulator]))
                self.GUIOs["SIMULATORS_SIMULATIONSERRORDISPLAYTEXT"].updateText(text      = str(self.puVar['simulatorCentral']['nSimulations_ERROR'][selectedSimulator]))
        else:
            if (updateAll == True): self.GUIOs["SIMULATORS_SIMULATIONSCOMPLETEDDISPLAYTEXT"].updateText(text  = "-")
            self.GUIOs["SIMULATORS_SIMULATIONSTOTALDISPLAYTEXT"].updateText(text      = "-")
            self.GUIOs["SIMULATORS_SIMULATIONSQUEUEDDISPLAYTEXT"].updateText(text     = "-")
            self.GUIOs["SIMULATORS_SIMULATIONSPROCESSINGDISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["SIMULATORS_SIMULATIONSPAUSEDDISPLAYTEXT"].updateText(text     = "-")
            self.GUIOs["SIMULATORS_SIMULATIONSERRORDISPLAYTEXT"].updateText(text      = "-")
    def __farr_onSimulationControlRequestResponse(responder, requestID, functionResult):
        responseOn               = functionResult['responseOn']
        requestResult            = functionResult['result']
        simulationManagerMessage = functionResult['message']
        if (responseOn == 'ADDREQUEST'):
            self.pageAuxillaryFunctions['CHECKIFCANADDSIMULATION']()
            if (requestResult == True): self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = simulationManagerMessage, textStyle = 'GREEN_LIGHT')
            else:                       self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = simulationManagerMessage, textStyle = 'RED_LIGHT')
        elif (responseOn == 'REMOVALREQUEST'):
            if (requestResult == True): self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = simulationManagerMessage, textStyle = 'ORANGE_LIGHT')
            else:                       self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = simulationManagerMessage, textStyle = 'YELLOW')
        elif (responseOn == 'SIMULATORACTIVATION'):
            if (requestResult == True): self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = simulationManagerMessage, textStyle = 'GREEN_LIGHT')
            else:                       self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = simulationManagerMessage, textStyle = 'YELLOW')
    auxFunctions['UPDATESIMULATORSDATA']                     = __updateSimulatorsData
    auxFunctions['_FARR_ONSIMULATIONCONTROLREQUESTRESPONSE'] = __farr_onSimulationControlRequestResponse

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
        elif (sortType == 'STATUS'):
            _forSort = list()
            for _simCode in _filtered:
                _sim        = _simulations[_simCode]
                _sim_status = _sim['_status']
                if   (_sim_status == 'COMPLETED'):  _forSort.append((_simCode, 0))
                elif (_sim_status == 'QUEUED'):     _forSort.append((_simCode, 3))
                elif (_sim_status == 'PROCESSING'): _forSort.append((_simCode, 1))
                elif (_sim_status == 'PAUSED'):     _forSort.append((_simCode, 2))
                elif (_sim_status == 'ERROR'):      _forSort.append((_simCode, 4))
            _forSort.sort(key = lambda x: x[1])
            _filtered = [_sortPair[0] for _sortPair in _forSort]
        elif (sortType == 'COMPLETION'):
            _forSort_completed  = list()
            _forSort_queued     = list()
            _forSort_processing = list()
            _forSort_paused     = list()
            _forSort_error      = list()
            for _simCode in _filtered:
                _sim        = _simulations[_simCode]
                _sim_status = _sim['_status']
                if (_sim_status == 'COMPLETED'): _forSort_completed.append(_simCode)
                elif (_sim_status == 'QUEUED'):  _forSort_queued.append(_simCode)
                elif (_sim_status == 'PROCESSING'):
                    _sim_completion = _sim['_completion']
                    if (_sim_completion == None): _forSort_processing.append((_simCode, 0))
                    else:                         _forSort_processing.append((_simCode, _sim_completion))
                elif (_sim_status == 'PAUSED'):
                    _sim_completion = _sim['_completion']
                    if (_sim_completion == None): _forSort_paused.append((_simCode, 0))
                    else:                         _forSort_paused.append((_simCode, _sim_completion))
                elif (_sim_status == 'ERROR'): _forSort_error.append(_simCode)
            _forSort_completed.sort()
            _forSort_queued.sort()
            _forSort_processing.sort(key = lambda x: x[0], reverse = True)
            _forSort_paused.sort(key = lambda x: x[0], reverse = True)
            _forSort_error.sort()
            _filtered = _forSort_completed+[_sortPair[0] for _sortPair in _forSort_processing]+[_sortPair[0] for _sortPair in _forSort_paused]+_forSort_queued+_forSort_error
        #Finally
        self.GUIOs["SIMULATIONS_SELECTIONBOX"].setDisplayTargets(displayTargets = _filtered, resetViewPosition = False)
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
            #[4]:  Status
            _status = _simulation['_status']
            _status_str = _simulation['_status']
            if   (_status == 'COMPLETED'):  _status_str = self.visualManager.getTextPack('SIMULATION:GENERAL_STATUS_COMPLETED');  _status_str_color = 'GREEN'
            elif (_status == 'QUEUED'):     _status_str = self.visualManager.getTextPack('SIMULATION:GENERAL_STATUS_QUEUED');     _status_str_color = 'BLUE'
            elif (_status == 'PROCESSING'): _status_str = self.visualManager.getTextPack('SIMULATION:GENERAL_STATUS_PROCESSING'); _status_str_color = 'GREEN_LIGHT'
            elif (_status == 'PAUSED'):     _status_str = self.visualManager.getTextPack('SIMULATION:GENERAL_STATUS_PAUSED');     _status_str_color = 'YELLOW'
            elif (_status == 'ERROR'):      _status_str = self.visualManager.getTextPack('SIMULATION:GENERAL_STATUS_ERROR');      _status_str_color = 'RED_LIGHT'
            #[5]:  Completion
            _completion = _simulation['_completion']
            if (_simulation['_completion'] == None): _completion_str = "-"; _completion_str_color = 'DEFAULT'
            else:                                    
                _completion_str = "{:.2f} %".format(_simulation['_completion']*100)
                _completion_perc = _completion*100
                if   ((0 <= _completion_perc) and (_completion_perc <=  33)): _completion_str_color = 'ORANGE_LIGHT'
                elif ((33 < _completion_perc) and (_completion_perc <=  66)): _completion_str_color = 'BLUE_LIGHT'
                elif ((66 < _completion_perc) and (_completion_perc <= 100)): _completion_str_color = 'GREEN_LIGHT'
            #Finally
            simulations_selectionList[simulationCode] = [{'text': _index_str},
                                                         {'text': _simulationCode_str},
                                                         {'text': _simRange_str},
                                                         {'text': _creationTime_str},
                                                         {'text': _status_str, 'textStyles': [('all', _status_str_color)]},
                                                         {'text': _completion_str, 'textStyles': [('all', _completion_str_color)]}]
        self.GUIOs["SIMULATIONS_SELECTIONBOX"].setSelectionList(selectionList = simulations_selectionList, keepSelected = True, displayTargets = 'all', callSelectionUpdateFunction = False)
        self.pageAuxillaryFunctions['ONSIMULATIONSFILTERUPDATE']()
    def __onSimulationSelectionUpdate():
        _simulation_selected = self.puVar['simulation_selected']
        if (_simulation_selected == None):
            self.GUIOs["GENERAL_SIMULATIONCODETEXTINPUTBOX"].show()
            self.GUIOs["GENERAL_SIMULATIONCODEDISPLAYTEXT"].hide()
            self.GUIOs["GENERAL_SIMULATIONRANGETEXTINPUTBOX1"].show()
            self.GUIOs["GENERAL_SIMULATIONRANGETEXTINPUTBOX2"].show()
            self.GUIOs["GENERAL_SIMULATIONRANGEDISPLAYTEXT1"].hide()
            self.GUIOs["GENERAL_SIMULATIONRANGEDISPLAYTEXT2"].hide()
            self.GUIOs["GENERAL_ANALYSISEXPORTSWITCH"].activate()
            self.GUIOs["GENERAL_ADDSIMULATIONBUTTON"].deactivate()
            self.GUIOs["GENERAL_REMOVESIMULATIONBUTTON"].deactivate()
            self.GUIOs["GENERAL_REPLICATECONFIGURATIONBUTTON"].deactivate()
            self.GUIOs["GENERAL_VIEWRESULTBUTTON"].deactivate()
            #Positions
            self.GUIOs["POSITIONS_SETUPSELECTIONBOX"].show()
            self.GUIOs["POSITIONS_SELECTEDSIMSELECTIONBOX"].hide()
            self.GUIOs["POSITIONS_INITIALIZATIONBUTTON"].deactivate()
            self.GUIOs["POSITIONS_SELECTEDPOSITIONSTITLETEXT"].show()
            self.GUIOs["POSITIONS_SELECTEDPOSITIONSDISPLAYTEXT"].show()
            self.GUIOs["POSITIONS_NSELECTEDPOSITIONSDISPLAYTEXT"].show()
            self.GUIOs["POSITIONS_RELEASEALLBUTTON"].show()
            self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODESELECTIONBOX"].show()
            self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODEDISPLAYTEXT"].hide()
            self.GUIOs["POSITIONS_TRADECONFIGURATIONCODESELECTIONBOX"].show()
            self.GUIOs["POSITIONS_TRADECONFIGURATIONCODEDISPLAYTEXT"].hide()
            self.GUIOs["POSITIONS_ASSUMEDRATIOTEXTINPUTBOX"].show()
            self.GUIOs["POSITIONS_ASSUMEDRATIODISPLAYTEXT"].hide()
            self.GUIOs["POSITIONS_PRIORITYTEXTINPUTBOX"].show()
            self.GUIOs["POSITIONS_PRIORITYDISPLAYTEXT"].hide()
            self.GUIOs["POSITIONS_MAXALLOCATEDBALANCETEXTINPUTBOX"].show()
            self.GUIOs["POSITIONS_MAXALLOCATEDBALANCEDISPLAYTEXT"].hide()
            #Assets
            self.GUIOs["ASSETS_INITIALWALLETBALANCETEXTINPUTBOX"].activate()
            self.GUIOs["ASSETS_ALLOCATIONRATIOSLIDER"].activate()
        else:
            _simulation = self.puVar['simulations'][_simulation_selected]
            self.GUIOs["GENERAL_SIMULATIONCODETEXTINPUTBOX"].hide()
            self.GUIOs["GENERAL_SIMULATIONCODEDISPLAYTEXT"].show()
            self.GUIOs["GENERAL_SIMULATIONRANGETEXTINPUTBOX1"].hide()
            self.GUIOs["GENERAL_SIMULATIONRANGETEXTINPUTBOX2"].hide()
            self.GUIOs["GENERAL_SIMULATIONRANGEDISPLAYTEXT1"].show()
            self.GUIOs["GENERAL_SIMULATIONRANGEDISPLAYTEXT2"].show()
            self.GUIOs["GENERAL_ANALYSISEXPORTSWITCH"].deactivate()
            self.GUIOs["GENERAL_ADDSIMULATIONBUTTON"].deactivate()
            self.GUIOs["GENERAL_REMOVESIMULATIONBUTTON"].activate()
            self.GUIOs["GENERAL_REPLICATECONFIGURATIONBUTTON"].activate()
            if (_simulation['_status'] == 'COMPLETED'): self.GUIOs["GENERAL_VIEWRESULTBUTTON"].activate()
            else:                                       self.GUIOs["GENERAL_VIEWRESULTBUTTON"].deactivate()
            #Positions
            self.GUIOs["POSITIONS_SETUPSELECTIONBOX"].hide()
            self.GUIOs["POSITIONS_SELECTEDSIMSELECTIONBOX"].show()
            self.GUIOs["POSITIONS_INITIALIZATIONBUTTON"].deactivate()
            self.GUIOs["POSITIONS_SELECTEDPOSITIONSTITLETEXT"].hide()
            self.GUIOs["POSITIONS_SELECTEDPOSITIONSDISPLAYTEXT"].hide()
            self.GUIOs["POSITIONS_NSELECTEDPOSITIONSDISPLAYTEXT"].hide()
            self.GUIOs["POSITIONS_RELEASEALLBUTTON"].hide()
            self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODESELECTIONBOX"].hide()
            self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODEDISPLAYTEXT"].show()
            self.GUIOs["POSITIONS_TRADECONFIGURATIONCODESELECTIONBOX"].hide()
            self.GUIOs["POSITIONS_TRADECONFIGURATIONCODEDISPLAYTEXT"].show()
            self.GUIOs["POSITIONS_ASSUMEDRATIOTEXTINPUTBOX"].hide()
            self.GUIOs["POSITIONS_ASSUMEDRATIODISPLAYTEXT"].show()
            self.GUIOs["POSITIONS_PRIORITYTEXTINPUTBOX"].hide()
            self.GUIOs["POSITIONS_PRIORITYDISPLAYTEXT"].show()
            self.GUIOs["POSITIONS_MAXALLOCATEDBALANCETEXTINPUTBOX"].hide()
            self.GUIOs["POSITIONS_MAXALLOCATEDBALANCEDISPLAYTEXT"].show()
            #Assets
            self.GUIOs["ASSETS_INITIALWALLETBALANCETEXTINPUTBOX"].updateText(text = "")
            self.GUIOs["ASSETS_INITIALWALLETBALANCETEXTINPUTBOX"].deactivate()
            self.GUIOs["ASSETS_ALLOCATIONRATIOSLIDER"].deactivate()
            #Finally
            self.pageAuxillaryFunctions['SETSELECTEDSIMPOSITIONSLIST']()
        self.pageAuxillaryFunctions['UPDATESIMULATIONDATA']()
        self.pageAuxillaryFunctions['UPDATEASSETDATADISPLAY']()
        self.pageAuxillaryFunctions['ONPOSITIONSFILTERUPDATE']()
    def __updateSimulationData():
        if (self.puVar['simulation_selected'] == None):
            self.GUIOs["GENERAL_CREATIONTIMEDISPLAYTEXT"].updateText(text       = "-")
            self.GUIOs["GENERAL_ALLOCATEDSIMUALTORDISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["GENERAL_STATUSDISPLAYTEXT"].updateText(text             = "-", textStyle = 'DEFAULT')
            self.GUIOs["GENERAL_COMPLETIONGAUGEBAR"].updateGaugeValue(gaugeValue = 0)
            self.GUIOs["GENERAL_COMPLETIONDISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["GENERAL_ANALYSISEXPORTSWITCH"].setStatus(status = self.puVar['simulationSetup_analysisExport'], animate = False, callStatusUpdateFunction = True)
        else:
            _simulation = self.puVar['simulations'][self.puVar['simulation_selected']]
            self.GUIOs["GENERAL_SIMULATIONCODEDISPLAYTEXT"].updateText(text = self.puVar['simulation_selected'])
            self.GUIOs["GENERAL_SIMULATIONRANGEDISPLAYTEXT1"].updateText(text = datetime.fromtimestamp(_simulation['simulationRange'][0], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
            self.GUIOs["GENERAL_SIMULATIONRANGEDISPLAYTEXT2"].updateText(text = datetime.fromtimestamp(_simulation['simulationRange'][1], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
            self.GUIOs["GENERAL_CREATIONTIMEDISPLAYTEXT"].updateText(text = datetime.fromtimestamp(_simulation['creationTime']).strftime("%Y/%m/%d %H:%M"))
            if (_simulation['_allocatedSimulator'] == None): self.GUIOs["GENERAL_ALLOCATEDSIMUALTORDISPLAYTEXT"].updateText(text = "-")
            else:                                            self.GUIOs["GENERAL_ALLOCATEDSIMUALTORDISPLAYTEXT"].updateText(text = _simulation['_allocatedSimulator'])
            _status = _simulation['_status']
            if   (_status == 'COMPLETED'):  self.GUIOs["GENERAL_STATUSDISPLAYTEXT"].updateText(text = self.visualManager.getTextPack('SIMULATION:GENERAL_STATUS_COMPLETED'),  textStyle = 'GREEN')
            elif (_status == 'QUEUED'):     self.GUIOs["GENERAL_STATUSDISPLAYTEXT"].updateText(text = self.visualManager.getTextPack('SIMULATION:GENERAL_STATUS_QUEUED'),     textStyle = 'BLUE')
            elif (_status == 'PROCESSING'): self.GUIOs["GENERAL_STATUSDISPLAYTEXT"].updateText(text = self.visualManager.getTextPack('SIMULATION:GENERAL_STATUS_PROCESSING'), textStyle = 'GREEN_LIGHT'); self.GUIOs["GENERAL_COMPLETIONGAUGEBAR"].updateGaugeColor(rValue =   0, gValue = 200, bValue = 100)
            elif (_status == 'PAUSED'):     self.GUIOs["GENERAL_STATUSDISPLAYTEXT"].updateText(text = self.visualManager.getTextPack('SIMULATION:GENERAL_STATUS_PAUSED'),     textStyle = 'YELLOW');      self.GUIOs["GENERAL_COMPLETIONGAUGEBAR"].updateGaugeColor(rValue = 250, gValue = 190, bValue =  10)
            elif (_status == 'ERROR'):      self.GUIOs["GENERAL_STATUSDISPLAYTEXT"].updateText(text = self.visualManager.getTextPack('SIMULATION:GENERAL_STATUS_ERROR'),      textStyle = 'RED_LIGHT')
            if (_simulation['_completion'] == None):
                self.GUIOs["GENERAL_COMPLETIONGAUGEBAR"].updateGaugeValue(gaugeValue = 0)
                self.GUIOs["GENERAL_COMPLETIONDISPLAYTEXT"].updateText(text = "-")
            else:
                self.GUIOs["GENERAL_COMPLETIONGAUGEBAR"].updateGaugeValue(gaugeValue = _simulation['_completion']*100)
                self.GUIOs["GENERAL_COMPLETIONDISPLAYTEXT"].updateText(text = "{:.3f} %".format(_simulation['_completion']*100))
            self.GUIOs["GENERAL_ANALYSISEXPORTSWITCH"].setStatus(status = _simulation['analysisExport'], animate = False, callStatusUpdateFunction = False)
    auxFunctions['ONSIMULATIONSFILTERUPDATE']   = __onSimulationsFilterUpdate
    auxFunctions['SETSIMULATIONSLIST']          = __setSimulationsList
    auxFunctions['ONSIMULATIONSELECTIONUPDATE'] = __onSimulationSelectionUpdate
    auxFunctions['UPDATESIMULATIONDATA']        = __updateSimulationData

    #<General>
    def __checkIfCanAddSimulation():
        #Read Params
        #---Simulation Code
        _simulationCode = self.GUIOs["GENERAL_SIMULATIONCODETEXTINPUTBOX"].getText()
        if (_simulationCode == ""): _simulationCode = None
        #---Simulation Range
        rangeBeg_str = self.GUIOs["GENERAL_SIMULATIONRANGETEXTINPUTBOX1"].getText()
        rangeEnd_str = self.GUIOs["GENERAL_SIMULATIONRANGETEXTINPUTBOX2"].getText()
        try:
            rangeBeg = datetime.strptime(rangeBeg_str, "%Y/%m/%d %H:%M").timestamp()-time.timezone
            rangeEnd = datetime.strptime(rangeEnd_str, "%Y/%m/%d %H:%M").timestamp()-time.timezone
        except: rangeBeg = None; rangeEnd = None
        #Tests
        _testPassed = True
        if not((_simulationCode == None) or (_simulationCode not in self.puVar['simulations'])): _testPassed = False
        if not((rangeBeg != None) and (rangeEnd != None) and (rangeBeg < rangeEnd)):             _testPassed = False
        #Finally
        if (_testPassed == True): self.GUIOs["GENERAL_ADDSIMULATIONBUTTON"].activate()
        else:                     self.GUIOs["GENERAL_ADDSIMULATIONBUTTON"].deactivate()
    auxFunctions['CHECKIFCANADDSIMULATION']   = __checkIfCanAddSimulation

    #<Positions>
    def __setSetupPositionsList():
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        pafs  = self.pageAuxillaryFunctions
        currencies   = puVar['currencies']
        ss_positions = puVar['simulationSetup_positions']
        vm_gtp   = self.visualManager.getTextPack
        func_fts = auxiliaries.floatToString

        #[2]: Positions Selection Box
        nPositions = len(ss_positions)
        sList      = dict()
        for pIndex, symbol in enumerate(ss_positions):
            #[2-1]: Instances
            ss_position = ss_positions[symbol]
            sInfo       = currencies[symbol]['info_server']

            #[2-2]: Display Texts
            #---[2-2-1]:  Index
            index_str = f"{pIndex+1} / {nPositions}"
            #---[2-2-2]:  Symbol
            symbol_str = symbol
            #---[2-2-3]:  Currency Analysis Code
            if ss_position['currencyAnalysisConfigurationCode'] is None: cacCode_str = "-"
            else:                                                        cacCode_str = ss_position['currencyAnalysisConfigurationCode']
            #---[2-2-4]:  Trade Configuration Code
            if ss_position['tradeConfigurationCode'] is None: tcCode_str = "-"
            else:                                             tcCode_str = ss_position['tradeConfigurationCode']
            #---[2-2-5]:  Margin Mode
            isolated = ss_position['isolated']
            if   isolated is None: marginMode_str = '-'
            elif isolated:         marginMode_str = 'ISOLATED'
            else:                  marginMode_str = 'CROSSED'
            #---[2-2-6]:  Leverage
            if ss_position['leverage'] is None: leverage_str = "-"
            else:                               leverage_str = f"{ss_position['leverage']:d}"
            #---[2-2-7]:  Priority
            priority_str = f"{ss_position['priority']:d}"
            #---[2-2-8]:  Assumed Ratio
            assumedRatio_str = f"{ss_position['assumedRatio']*100:.3f} %"
            #---[2-2-9]:  Weighted Assumed Ratio
            waRatio = ss_position['weightedAssumedRatio']
            if waRatio is None: weightedAssumedRatio_str = "-"
            else:               weightedAssumedRatio_str = f"{waRatio*100:.3f} %"
            #---[2-2-10]:  Allocated Balance
            allocatedBalance_str = func_fts(number = ss_position['allocatedBalance'], precision = _ASSETPRECISIONS_S[ss_position['quoteAsset']])
            #---[2-2-11]: Max Allocated Balance
            maxAllocBal = ss_position['maxAllocatedBalance']
            if maxAllocBal == float('inf'): maxAllocatedBalance_str = "INF"
            else:                           maxAllocatedBalance_str = func_fts(number = ss_position['maxAllocatedBalance'], precision = _ASSETPRECISIONS_S[ss_position['quoteAsset']])
            #---[2-2-12]: First Kline Open Timestamp
            foTS_kline = ss_position['firstOpenTSs']['kline']
            if foTS_kline is None: firstKline_str = "-"
            else:                  firstKline_str = datetime.fromtimestamp(foTS_kline, tz=timezone.utc).strftime("%Y/%m/%d %H:%M")
            #---[2-2-13]: Tradable
            if ss_position['tradable']: tradable_str = 'TRUE';  tradable_str_color = 'GREEN_LIGHT'
            else:                       tradable_str = 'FALSE'; tradable_str_color = 'RED_LIGHT'
            #---[2-2-14]: Market Status
            status = None if sInfo is None else sInfo['status']
            if   status == 'TRADING':  status_str = vm_gtp('SIMULATION:POSITIONS_MARKETSTATUS_TRADING');  status_str_color = 'GREEN_LIGHT'
            elif status == 'SETTLING': status_str = vm_gtp('SIMULATION:POSITIONS_MARKETSTATUS_SETTLING'); status_str_color = 'RED_LIGHT'
            elif status == 'REMOVED':  status_str = vm_gtp('SIMULATION:POSITIONS_MARKETSTATUS_REMOVED');  status_str_color = 'RED_DARK'
            elif status is None:       status_str = '-';                                                  status_str_color = 'BLUE_DARK'
            else:                      status_str = status;                                               status_str_color = 'VIOLET'
            #---[2-2-15]: Min Notional
            if sInfo is None: 
                minNotional_str = 'N/A'
            else:
                minNotional = None
                for flt in sInfo['filters']:
                    if flt['filterType'] != 'MIN_NOTIONAL': 
                        continue
                    minNotional = flt['notional']
                    break
                if minNotional is None: minNotional_str = "-"
                else:                   minNotional_str = minNotional

            #[2-3]: Selection Box Item
            sList[symbol] = [{'text': index_str},
                             {'text': symbol_str},
                             {'text': cacCode_str},
                             {'text': tcCode_str},
                             {'text': marginMode_str},
                             {'text': leverage_str,},
                             {'text': priority_str},
                             {'text': assumedRatio_str},
                             {'text': weightedAssumedRatio_str},
                             {'text': allocatedBalance_str},
                             {'text': maxAllocatedBalance_str},
                             {'text': firstKline_str},
                             {'text': tradable_str, 'textStyles': [('all', tradable_str_color),]},
                             {'text': status_str,   'textStyles': [('all', status_str_color),]},
                             {'text': minNotional_str}]
        guios["POSITIONS_SETUPSELECTIONBOX"].setSelectionList(selectionList               = sList, 
                                                              displayTargets              = 'all', 
                                                              callSelectionUpdateFunction = True)

        #[3]: Apply Filter
        pafs['ONPOSITIONSFILTERUPDATE']()
    def __setSelectedSimPositionsList():
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        pafs  = self.pageAuxillaryFunctions
        sim_positions = puVar['simulations'][puVar['simulation_selected']]['positions']
        func_fts = auxiliaries.floatToString

        #[2]: Positions Selection Box
        nPositions = len(sim_positions)
        sList      = dict()
        for pIndex, symbol in enumerate(sim_positions):
            #[2-1]: Instances
            sim_position = sim_positions[symbol]

            #[2-2]: Display Texts
            #---[2-2-1]:  Index
            index_str = f"{pIndex+1} / {nPositions}"
            #---[2-2-2]:  Symbol
            symbol_str = symbol
            #---[2-2-3]:  Currency Analysis Code
            if sim_position['currencyAnalysisConfigurationCode'] is None: cacCode_str = "-"
            else:                                                         cacCode_str = sim_position['currencyAnalysisConfigurationCode']
            #---[2-2-4]:  Trade Configuration Code
            if sim_position['tradeConfigurationCode'] is None: tcCode_str = "-"
            else:                                              tcCode_str = sim_position['tradeConfigurationCode']
            #---[2-2-5]:  Margin Mode
            isolated = sim_position['isolated']
            if   isolated is None: marginMode_str = '-'
            elif isolated:         marginMode_str = 'ISOLATED'
            else:                  marginMode_str = 'CROSSED'
            #---[2-2-6]:  Leverage
            if sim_position['leverage'] is None: leverage_str = "-"
            else:                                leverage_str = str(sim_position['leverage'])
            #---[2-2-7]:  Priority
            priority_str = f"{sim_position['priority']:d}"
            #---[2-2-8]:  Assumed Ratio
            assumedRatio_str = f"{sim_position['assumedRatio']*100:.3f} %"
            #---[2-2-9]:  Weighted Assumed Ratio
            waRatio = sim_position['weightedAssumedRatio']
            if waRatio is None: weightedAssumedRatio_str = "-"
            else:               weightedAssumedRatio_str = f"{waRatio*100:.3f} %"
            #---[2-2-10]:  Allocated Balance
            allocatedBalance_str = func_fts(number = sim_position['allocatedBalance'], precision = _ASSETPRECISIONS_S[sim_position['quoteAsset']])
            #---[2-2-11]: Max Allocated Balance
            maxAllocBal = sim_position['maxAllocatedBalance']
            if maxAllocBal == float('inf'): maxAllocatedBalance_str = "INF"
            else:                           maxAllocatedBalance_str = func_fts(number = sim_position['maxAllocatedBalance'], precision = _ASSETPRECISIONS_S[sim_position['quoteAsset']])
            #---[2-2-12]: First Kline
            foTS_kline = sim_position['firstOpenTSs']['kline']
            if foTS_kline is None: firstKline_str = "-"
            else:                  firstKline_str = datetime.fromtimestamp(foTS_kline, tz=timezone.utc).strftime("%Y/%m/%d %H:%M")
            #---[2-2-13]: Tradable
            if sim_position['tradable']: tradable_str = 'TRUE';  tradable_str_color = 'GREEN_LIGHT'
            else:                        tradable_str = 'FALSE'; tradable_str_color = 'RED_LIGHT'

            #[2-3]: Selection Box Item
            sList[symbol] = [{'text': index_str},
                             {'text': symbol_str},
                             {'text': cacCode_str},
                             {'text': tcCode_str},
                             {'text': marginMode_str},
                             {'text': leverage_str,},
                             {'text': priority_str},
                             {'text': assumedRatio_str},
                             {'text': weightedAssumedRatio_str},
                             {'text': allocatedBalance_str},
                             {'text': maxAllocatedBalance_str},
                             {'text': firstKline_str},
                             {'text': tradable_str, 'textStyles': [('all', tradable_str_color),]}]
        guios["POSITIONS_SELECTEDSIMSELECTIONBOX"].setSelectionList(selectionList               = sList, 
                                                                    displayTargets              = 'all', 
                                                                    callSelectionUpdateFunction = True)

        #[3]: Apply Filter
        pafs['ONPOSITIONSFILTERUPDATE']()
    def __onPositionsFilterUpdate():
        if (self.puVar['simulation_selected'] == None): _positions = self.puVar['simulationSetup_positions']
        else:                                           _positions = self.puVar['simulations'][self.puVar['simulation_selected']]['positions']
        #Filter Parameters
        searchText             = self.GUIOs["POSITIONS_SEARCHTEXTINPUTBOX"].getText()
        searchType             = self.GUIOs["POSITIONS_SEARCHTYPESELECTIONBOX"].getSelected()
        sortType               = self.GUIOs["POSITIONS_SORTBYSELECTIONBOX"].getSelected()
        conditionType_tradable = self.GUIOs["POSITIONS_TRADABLEFILTERSELECTIONBOX"].getSelected()
        #Filtering
        _filtered = list(_positions.keys())
        #---[1]: Condition Filtering - Trade Status
        if   (conditionType_tradable == 'ALL'):   pass
        elif (conditionType_tradable == 'TRUE'):  _filtered = [_symbol for _symbol in _filtered if (_positions[_symbol]['tradable'] == True)]
        elif (conditionType_tradable == 'FALSE'): _filtered = [_symbol for _symbol in _filtered if (_positions[_symbol]['tradable'] == False)]
        #---[2]: Text Filtering
        if (searchText != ""): 
            if (searchType == 'SYMBOL'):  _filtered = [_symbol for _symbol in _filtered if (searchText in _symbol)]
            if (searchType == 'TCCODE'):  _filtered = [_symbol for _symbol in _filtered if ((_positions[_symbol]['tradeConfigurationCode']            != None) and (searchText in _positions[_symbol]['tradeConfigurationCode']))]
            if (searchType == 'CACCODE'): _filtered = [_symbol for _symbol in _filtered if ((_positions[_symbol]['currencyAnalysisConfigurationCode'] != None) and (searchText in _positions[_symbol]['currencyAnalysisConfigurationCode']))]
        #---[3]: Sorting
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
        if (self.puVar['simulation_selected'] is None): self.GUIOs["POSITIONS_SETUPSELECTIONBOX"].setDisplayTargets(displayTargets       = _filtered, resetViewPosition = False)
        else:                                           self.GUIOs["POSITIONS_SELECTEDSIMSELECTIONBOX"].setDisplayTargets(displayTargets = _filtered, resetViewPosition = False)
    def __updateSelectedPositionsDisplay():
        _positionSymbols_selected = self.GUIOs["POSITIONS_SETUPSELECTIONBOX"].getSelected()
        _nPositionSymbols_selected = len(_positionSymbols_selected)
        _positionSymbols_selected_str = ""
        if (_nPositionSymbols_selected == 0): 
            _positionSymbols_selected_str = "-"
            self.GUIOs["POSITIONS_RELEASEALLBUTTON"].deactivate()
        else:
            _positionSymbols_selected_str = ""
            if (8 < _nPositionSymbols_selected):
                for i in range (0, _MAXDISPLAYABLESELECTEDPOSITIONSYMBOLS):
                    if (i < _MAXDISPLAYABLESELECTEDPOSITIONSYMBOLS-1): _positionSymbols_selected_str += "{:s}, ".format(_positionSymbols_selected[i])
                    else:                                              _positionSymbols_selected_str += "{:s} (+ {:d})".format(_positionSymbols_selected[i], _nPositionSymbols_selected-_MAXDISPLAYABLESELECTEDPOSITIONSYMBOLS)
            else:
                for i in range (0, _nPositionSymbols_selected):
                    if (i < _nPositionSymbols_selected-1): _positionSymbols_selected_str += "{:s}, ".format(_positionSymbols_selected[i])
                    else:                                  _positionSymbols_selected_str += _positionSymbols_selected[i]
            self.GUIOs["POSITIONS_RELEASEALLBUTTON"].activate()
        self.GUIOs["POSITIONS_SELECTEDPOSITIONSDISPLAYTEXT"].updateText(text = _positionSymbols_selected_str)
        self.GUIOs["POSITIONS_NSELECTEDPOSITIONSDISPLAYTEXT"].updateText(text = "{:d} / {:d}".format(_nPositionSymbols_selected, len(self.puVar['simulationSetup_positions'])))
    def __onPositionSelectionUpdate():
        if (self.puVar['simulation_selected'] == None):
            _positionSymbols_selected = self.GUIOs["POSITIONS_SETUPSELECTIONBOX"].getSelected()
            _nSelected = len(_positionSymbols_selected)
            if (_nSelected == 0):
                self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODESELECTIONBOX"].deactivate()
                self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODERESETBUTTON"].deactivate()
                self.GUIOs["POSITIONS_TRADECONFIGURATIONCODESELECTIONBOX"].deactivate()
                self.GUIOs["POSITIONS_TRADECONFIGURATIONCODERESETBUTTON"].deactivate()
                self.GUIOs["POSITIONS_ASSUMEDRATIOTEXTINPUTBOX"].deactivate()
                self.GUIOs["POSITIONS_PRIORITYTEXTINPUTBOX"].deactivate()
                self.GUIOs["POSITIONS_MAXALLOCATEDBALANCETEXTINPUTBOX"].deactivate()
                self.GUIOs["POSITIONS_POSITIONAPPLYBUTTON"].deactivate()
                self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODESELECTIONBOX"].setSelected(itemKey = None, callSelectionUpdateFunction = False)
                self.GUIOs["POSITIONS_TRADECONFIGURATIONCODESELECTIONBOX"].setSelected(itemKey = None, callSelectionUpdateFunction = False)
                self.GUIOs["POSITIONS_ASSUMEDRATIOTEXTINPUTBOX"].updateText(text        = "")
                self.GUIOs["POSITIONS_PRIORITYTEXTINPUTBOX"].updateText(text            = "")
                self.GUIOs["POSITIONS_MAXALLOCATEDBALANCETEXTINPUTBOX"].updateText(text = "")
                self.GUIOs["POSITIONS_MAXALLOCATEDBALANCEUNITTEXT"].updateText(text     = "-")
            elif (_nSelected == 1):
                _position = self.puVar['simulationSetup_positions'][_positionSymbols_selected[0]]
                self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODESELECTIONBOX"].activate()
                if (_position['currencyAnalysisConfigurationCode'] != None): self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODERESETBUTTON"].activate()
                else:                                                        self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODERESETBUTTON"].deactivate()
                self.GUIOs["POSITIONS_TRADECONFIGURATIONCODESELECTIONBOX"].activate()
                if (_position['tradeConfigurationCode'] != None): self.GUIOs["POSITIONS_TRADECONFIGURATIONCODERESETBUTTON"].activate()
                else:                                             self.GUIOs["POSITIONS_TRADECONFIGURATIONCODERESETBUTTON"].deactivate()
                self.GUIOs["POSITIONS_ASSUMEDRATIOTEXTINPUTBOX"].activate()
                self.GUIOs["POSITIONS_PRIORITYTEXTINPUTBOX"].activate()
                self.GUIOs["POSITIONS_MAXALLOCATEDBALANCETEXTINPUTBOX"].activate()
                if (_position['currencyAnalysisConfigurationCode'] != None) and (_position['currencyAnalysisConfigurationCode'] in self.puVar['currencyAnalysisConfigurations']): self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODESELECTIONBOX"].setSelected(itemKey = _position['currencyAnalysisConfigurationCode'], callSelectionUpdateFunction = False)
                else:                                                                                                                                                             self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODESELECTIONBOX"].setSelected(itemKey = None,                                           callSelectionUpdateFunction = False)
                if (_position['tradeConfigurationCode'] != None) and (_position['tradeConfigurationCode'] in self.puVar['tradeConfigurations']): self.GUIOs["POSITIONS_TRADECONFIGURATIONCODESELECTIONBOX"].setSelected(itemKey = _position['tradeConfigurationCode'], callSelectionUpdateFunction = False)
                else:                                                                                                                            self.GUIOs["POSITIONS_TRADECONFIGURATIONCODESELECTIONBOX"].setSelected(itemKey = None,                                callSelectionUpdateFunction = False)
                if (_position['assumedRatio'] == None): self.GUIOs["POSITIONS_ASSUMEDRATIOTEXTINPUTBOX"].updateText("")
                else:                                   self.GUIOs["POSITIONS_ASSUMEDRATIOTEXTINPUTBOX"].updateText("{:.3f}".format(_position['assumedRatio']*100))
                self.GUIOs["POSITIONS_PRIORITYTEXTINPUTBOX"].updateText("{:d}".format(_position['priority']))
                if (_position['maxAllocatedBalance'] == float('inf')): self.GUIOs["POSITIONS_MAXALLOCATEDBALANCETEXTINPUTBOX"].updateText("")
                else:                                                  self.GUIOs["POSITIONS_MAXALLOCATEDBALANCETEXTINPUTBOX"].updateText(auxiliaries.floatToString(number = _position['maxAllocatedBalance'], precision = _ASSETPRECISIONS_S[_position['quoteAsset']], comma = False))
                self.GUIOs["POSITIONS_MAXALLOCATEDBALANCEUNITTEXT"].updateText(text = _position['quoteAsset'])
            else:
                self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODESELECTIONBOX"].activate()
                self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODERESETBUTTON"].deactivate()
                self.GUIOs["POSITIONS_TRADECONFIGURATIONCODESELECTIONBOX"].activate()
                self.GUIOs["POSITIONS_TRADECONFIGURATIONCODERESETBUTTON"].deactivate()
                self.GUIOs["POSITIONS_ASSUMEDRATIOTEXTINPUTBOX"].activate()
                self.GUIOs["POSITIONS_PRIORITYTEXTINPUTBOX"].deactivate()
                self.GUIOs["POSITIONS_MAXALLOCATEDBALANCETEXTINPUTBOX"].activate()
                self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODESELECTIONBOX"].setSelected(itemKey = None, callSelectionUpdateFunction = False)
                self.GUIOs["POSITIONS_TRADECONFIGURATIONCODESELECTIONBOX"].setSelected(itemKey = None, callSelectionUpdateFunction = False)
                self.GUIOs["POSITIONS_ASSUMEDRATIOTEXTINPUTBOX"].updateText("")
                self.GUIOs["POSITIONS_PRIORITYTEXTINPUTBOX"].updateText("")
                self.GUIOs["POSITIONS_MAXALLOCATEDBALANCETEXTINPUTBOX"].updateText("")
                self.GUIOs["POSITIONS_MAXALLOCATEDBALANCEUNITTEXT"].updateText(text = "-")
                _positions  = self.puVar['simulationSetup_positions']
                _assetNames = set()
                for _pSymbol in _positionSymbols_selected: _assetNames.add(_positions[_pSymbol]['quoteAsset'])
                if (len(_assetNames) == 1): self.GUIOs["POSITIONS_MAXALLOCATEDBALANCEUNITTEXT"].updateText(text = list(_assetNames)[0])
                else:                       self.GUIOs["POSITIONS_MAXALLOCATEDBALANCEUNITTEXT"].updateText(text = "-")
            self.pageAuxillaryFunctions['UPDATESELECTEDPOSITIONSDISPLAY']()
        else:
            try:    _positionSymbol_selected = self.GUIOs["POSITIONS_SELECTEDSIMSELECTIONBOX"].getSelected()[0]
            except: _positionSymbol_selected = None
            if (_positionSymbol_selected == None):
                self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODEDISPLAYTEXT"].updateText(text = "-")
                self.GUIOs["POSITIONS_TRADECONFIGURATIONCODEDISPLAYTEXT"].updateText(text            = "-")
                self.GUIOs["POSITIONS_ASSUMEDRATIODISPLAYTEXT"].updateText(text                      = "-")
                self.GUIOs["POSITIONS_PRIORITYDISPLAYTEXT"].updateText(text                          = "-")
                self.GUIOs["POSITIONS_MAXALLOCATEDBALANCEDISPLAYTEXT"].updateText(text               = "-")
                self.GUIOs["POSITIONS_MAXALLOCATEDBALANCEUNITTEXT"].updateText(text                  = "-")
            else:
                _position = self.puVar['simulations'][self.puVar['simulation_selected']]['positions'][_positionSymbol_selected]
                self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODEDISPLAYTEXT"].updateText(text = _position['currencyAnalysisConfigurationCode'])
                self.GUIOs["POSITIONS_TRADECONFIGURATIONCODEDISPLAYTEXT"].updateText(text            = _position['tradeConfigurationCode'])
                self.GUIOs["POSITIONS_ASSUMEDRATIODISPLAYTEXT"].updateText(text                      = "{:.3f} %".format(_position['assumedRatio']*100))
                self.GUIOs["POSITIONS_PRIORITYDISPLAYTEXT"].updateText(text                          = "{:d}".format(_position['priority']))
                if (_position['maxAllocatedBalance'] == float('inf')): self.GUIOs["POSITIONS_MAXALLOCATEDBALANCEDISPLAYTEXT"].updateText("INF")
                else:                                                  self.GUIOs["POSITIONS_MAXALLOCATEDBALANCEDISPLAYTEXT"].updateText(auxiliaries.floatToString(number = _position['maxAllocatedBalance'], precision = _ASSETPRECISIONS_S[_position['quoteAsset']]))
                self.GUIOs["POSITIONS_MAXALLOCATEDBALANCEUNITTEXT"].updateText(text = _position['quoteAsset'])
    def __setCurrencyAnalysisConfigurationList():
        currencyAnalysisConfigurations_selectionList = dict()
        for currencyAnalysisConfigurationCode in self.puVar['currencyAnalysisConfigurations']: currencyAnalysisConfigurations_selectionList[currencyAnalysisConfigurationCode] = {'text': currencyAnalysisConfigurationCode, 'textAnchor': 'W'}
        self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODESELECTIONBOX"].setSelectionList(selectionList = currencyAnalysisConfigurations_selectionList, displayTargets = 'all', keepSelected = True, callSelectionUpdateFunction = False)
    def __setTradeConfigurationList():
        tradeConfigurations_selectionList = dict()
        for tradeConfigurationCode in self.puVar['tradeConfigurations']: tradeConfigurations_selectionList[tradeConfigurationCode] = {'text': tradeConfigurationCode, 'textAnchor': 'W'}
        self.GUIOs["POSITIONS_TRADECONFIGURATIONCODESELECTIONBOX"].setSelectionList(selectionList = tradeConfigurations_selectionList, displayTargets = 'all', keepSelected = True, callSelectionUpdateFunction = False)
    def __checkIfCanEditPositionParams():
        _positionSymbols_selected = self.GUIOs["POSITIONS_SETUPSELECTIONBOX"].getSelected()
        _nSelected = len(_positionSymbols_selected)
        if (_nSelected == 1):
            #Position
            _position = self.puVar['simulationSetup_positions'][_positionSymbols_selected[0]]
            #Entered Values
            _cacCode = self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODESELECTIONBOX"].getSelected()
            _tcCode  = self.GUIOs["POSITIONS_TRADECONFIGURATIONCODESELECTIONBOX"].getSelected()
            try:    _assumedRatio = round(float(self.GUIOs["POSITIONS_ASSUMEDRATIOTEXTINPUTBOX"].getText())/100, 5)
            except: _assumedRatio = None
            try:    _priority = int(self.GUIOs["POSITIONS_PRIORITYTEXTINPUTBOX"].getText())
            except: _priority = None
            try:    
                _maxAllocatedBalance_str = self.GUIOs["POSITIONS_MAXALLOCATEDBALANCETEXTINPUTBOX"].getText()
                if (_maxAllocatedBalance_str == ""): _maxAllocatedBalance = float('inf')
                else:                                _maxAllocatedBalance = round(float(_maxAllocatedBalance_str), _position['precisions']['quote'])
            except: _maxAllocatedBalance = None
            #Tests
            _testPassed = True
            if not((_assumedRatio != None) and (0 <= _assumedRatio) and (_assumedRatio <= 1)):                                _testPassed = False
            if not((_priority != None) and (1 <= _priority) and (_priority <= len(self.puVar['simulationSetup_positions']))): _testPassed = False
            if not((_maxAllocatedBalance != None) and (0 < _maxAllocatedBalance)):                                            _testPassed = False
            if not(   (_cacCode             != _position['currencyAnalysisConfigurationCode'])
                   or (_tcCode              != _position['tradeConfigurationCode']) 
                   or (_assumedRatio        != _position['assumedRatio']) 
                   or (_priority            != _position['priority'])
                   or (_maxAllocatedBalance != _position['maxAllocatedBalance'])):
                _testPassed = False
            #Finally
            if (_testPassed == True): self.GUIOs["POSITIONS_POSITIONAPPLYBUTTON"].activate()
            else:                     self.GUIOs["POSITIONS_POSITIONAPPLYBUTTON"].deactivate()
        elif (0 < _nSelected):
            _positions = self.puVar['simulationSetup_positions']
            #Entered Values
            _cacCode = self.GUIOs["POSITIONS_CURRENCYANALYSISCONFIGURATIONCODESELECTIONBOX"].getSelected()
            _tcCode  = self.GUIOs["POSITIONS_TRADECONFIGURATIONCODESELECTIONBOX"].getSelected()
            try:    _assumedRatio = round(float(self.GUIOs["POSITIONS_ASSUMEDRATIOTEXTINPUTBOX"].getText())/100, 5)
            except: _assumedRatio = None
            try:    
                _maxAllocatedBalance_str = self.GUIOs["POSITIONS_MAXALLOCATEDBALANCETEXTINPUTBOX"].getText()
                if (_maxAllocatedBalance_str == ""): _maxAllocatedBalance = float('inf')
                else:                                _maxAllocatedBalance = float(_maxAllocatedBalance_str)
            except: _maxAllocatedBalance = None
            #Tests
            _testPassed = True
            if not((_assumedRatio != None) and (0 <= _assumedRatio) and (_assumedRatio <= 1)): _testPassed = False
            if not((_maxAllocatedBalance != None) and (0 < _maxAllocatedBalance)):             _testPassed = False
            for _pSymbol in _positionSymbols_selected:
                _position = _positions[_pSymbol]
                if not(   (_cacCode             != _position['currencyAnalysisConfigurationCode'])
                       or (_tcCode              != _position['tradeConfigurationCode'])
                       or (_assumedRatio        != _position['assumedRatio'])
                       or (_maxAllocatedBalance != _position['maxAllocatedBalance'])): 
                    _testPassed = False; break
            #Finally
            if (_testPassed == True): self.GUIOs["POSITIONS_POSITIONAPPLYBUTTON"].activate()
            else:                     self.GUIOs["POSITIONS_POSITIONAPPLYBUTTON"].deactivate()
    def __updatePositionPriority(positionSymbol, newPriority):
        _position = self.puVar['simulationSetup_positions'][positionSymbol]
        if (_position['priority'] < newPriority): 
            _target = (_position['priority']+1, newPriority)
            for _pSymbol in self.puVar['simulationSetup_positions']:
                __position = self.puVar['simulationSetup_positions'][_pSymbol]
                if ((_target[0] <= __position['priority']) and (__position['priority'] <= _target[1])): __position['priority'] -= 1
        elif (newPriority < _position['priority']): 
            _target = (newPriority, _position['priority']-1)
            for _pSymbol in self.puVar['simulationSetup_positions']:
                __position = self.puVar['simulationSetup_positions'][_pSymbol]
                if ((_target[0] <= __position['priority']) and (__position['priority'] <= _target[1])): __position['priority'] += 1
        _position['priority'] = newPriority
    def __sortPositionSymbolsByPriority(assetName):
        _asset     = self.puVar['simulationSetup_assets'][assetName]
        _positions = self.puVar['simulationSetup_positions']
        _positionSymbols_forSort = [(_pSymbol, _positions[_pSymbol]['priority']) for _pSymbol in _asset['_positionSymbols']]
        _positionSymbols_forSort.sort(key = lambda x: x[1])
        _asset['_positionSymbols_prioritySorted'] = [_sortPair[0] for _sortPair in _positionSymbols_forSort]
    def __allocateWalletBalance(assetName):
        _asset     = self.puVar['simulationSetup_assets'][assetName]
        _positions = self.puVar['simulationSetup_positions']
        #Initialize the allocated balance
        for _positionSymbol in _asset['_positionSymbols']: _positions[_positionSymbol]['allocatedBalance'] = 0
        #Allocate balance
        if (0 < _asset['allocatableBalance']):
            allocatedAssumedRatio = 0
            for _positionSymbol in _asset['_positionSymbols_prioritySorted']:
                _position = _positions[_positionSymbol]
                _allocatedBalance = round(_asset['allocatableBalance']*_position['assumedRatio'], _ASSETPRECISIONS[assetName])
                if (_position['maxAllocatedBalance'] < _allocatedBalance): _allocatedBalance = _position['maxAllocatedBalance']
                _assumedRatio_effective = round(_allocatedBalance/_asset['allocatableBalance'], 3)
                if (allocatedAssumedRatio+_assumedRatio_effective <= 1):
                    allocatedAssumedRatio += _assumedRatio_effective
                    _position['allocatedBalance'] = _allocatedBalance
                else: break
    def __computePositionSums(assetName):
        _asset     = self.puVar['simulationSetup_assets'][assetName]
        _positions = self.puVar['simulationSetup_positions']
        _positions_tradable = [_pSymbol for _pSymbol in _asset['_positionSymbols'] if (_positions[_pSymbol]['tradable'] == True)]
        if (len(_positions_tradable) == 0):
            _asset['allocatedBalance']     = 0
            _asset['assumedRatio']         = 0
            _asset['weightedAssumedRatio'] = None
            _asset['maxAllocatedBalance']  = None
        else:
            _asset['allocatedBalance']     = sum([_positions[_pSymbol]['allocatedBalance']                                        for _pSymbol in _positions_tradable])
            _asset['assumedRatio']         = sum([_positions[_pSymbol]['assumedRatio']                                            for _pSymbol in _positions_tradable])
            _asset['weightedAssumedRatio'] = sum([round(_positions[_pSymbol]['assumedRatio']*_positions[_pSymbol]['leverage'], 3) for _pSymbol in _positions_tradable])
            _asset['maxAllocatedBalance']  = sum([_positions[_pSymbol]['maxAllocatedBalance']                                     for _pSymbol in _positions_tradable])
    def __updatePositionsGraphics(positionsPrev):
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
                        _text = auxiliaries.floatToString(number = _position['allocatedBalance'], precision = _ASSETPRECISIONS_S[_position['quoteAsset']])
                        _newSelectionBoxItem = {'text': _text}
                    elif (_dataName == 'maxAllocatedBalance'):
                        if (_position['maxAllocatedBalance'] == float('inf')): _text = "INF"
                        else:                                                  _text = auxiliaries.floatToString(number = _position['maxAllocatedBalance'], precision = _ASSETPRECISIONS_S[_position['quoteAsset']])
                        _newSelectionBoxItem = {'text': _text}
                    elif (_dataName == 'tradable'):
                        if (_position['tradable'] == True): _text = 'TRUE';  _textColor = 'GREEN_LIGHT'
                        else:                               _text = 'FALSE'; _textColor = 'RED_LIGHT'
                        _newSelectionBoxItem = {'text': _text, 'textStyles': [('all', _textColor),]}
                    self.GUIOs["POSITIONS_SETUPSELECTIONBOX"].editSelectionListItem(itemKey = _pSymbol, item = _newSelectionBoxItem, columnIndex = _cIndex)
    def __initializePositions():
        #Copy Previous Data
        _positions_prev = dict()
        for _pSymbol in self.puVar['simulationSetup_positions']: _positions_prev[_pSymbol] = self.puVar['simulationSetup_positions'][_pSymbol].copy()
        #Initialize Positions Setup Variables
        for _index, _pSymbol in enumerate(self.puVar['simulationSetup_positions']):
            _position = self.puVar['simulationSetup_positions'][_pSymbol]
            _position['currencyAnalysisConfigurationCode'] = None
            _position['tradeConfigurationCode']            = None
            _position['isolated']                          = None
            _position['leverage']                          = None
            _position['priority']                          = _index+1
            _position['assumedRatio']                      = 0
            _position['weightedAssumedRatio']              = None
            _position['allocatedBalance']                  = 0
            _position['maxAllocatedBalance']               = float('inf')
            _position['tradable']                          = False
        #Reallocate balance and recompute position sums
        for _assetName in self.puVar['simulationSetup_assets']:
            self.pageAuxillaryFunctions['SORTPOSITIONSYMBOLSBYPRIORITY'](assetName = _assetName)
            self.pageAuxillaryFunctions['ALLOCATEWALLETBALANCE'](assetName = _assetName)
            self.pageAuxillaryFunctions['COMPUTEPOSITIONSUMS'](assetName = _assetName)
        #Update Graphics
        self.pageAuxillaryFunctions['UPDATEPOSITIONSGRAPHICS'](positionsPrev = _positions_prev)
        self.pageAuxillaryFunctions['UPDATEASSETDATADISPLAY']()
    auxFunctions['SETSETUPPOSITIONSLIST']                = __setSetupPositionsList
    auxFunctions['SETSELECTEDSIMPOSITIONSLIST']          = __setSelectedSimPositionsList
    auxFunctions['ONPOSITIONSFILTERUPDATE']              = __onPositionsFilterUpdate
    auxFunctions['UPDATESELECTEDPOSITIONSDISPLAY']       = __updateSelectedPositionsDisplay
    auxFunctions['ONPOSITIONSELECTIONUPDATE']            = __onPositionSelectionUpdate
    auxFunctions['SETCURRENCYANALYSISCONFIGURATIONLIST'] = __setCurrencyAnalysisConfigurationList
    auxFunctions['SETTRADECONFIGURATIONLIST']            = __setTradeConfigurationList
    auxFunctions['CHECKIFCANEDITPOSITIONPARAMS']         = __checkIfCanEditPositionParams
    auxFunctions['UPDATEPOSITIONPRIORITY']               = __updatePositionPriority
    auxFunctions['SORTPOSITIONSYMBOLSBYPRIORITY']        = __sortPositionSymbolsByPriority
    auxFunctions['ALLOCATEWALLETBALANCE']                = __allocateWalletBalance
    auxFunctions['COMPUTEPOSITIONSUMS']                  = __computePositionSums
    auxFunctions['UPDATEPOSITIONSGRAPHICS']              = __updatePositionsGraphics
    auxFunctions['INITIALIZEPOSITIONS']                  = __initializePositions

    #<Assets>
    def __onAssetSelectionUpdate():
        _assetName_selected = self.GUIOs["ASSETS_ASSETSELECTIONBOX"].getSelected()
        if   (_assetName_selected == 'USDT'): self.GUIOs["ASSETS_SELECTEDASSETIMAGEBOX"].updateImage(image = "usdtIcon_512x512.png")
        elif (_assetName_selected == 'USDC'): self.GUIOs["ASSETS_SELECTEDASSETIMAGEBOX"].updateImage(image = "usdcIcon_512x512.png")
        self.pageAuxillaryFunctions['UPDATEASSETDATADISPLAY']()
        self.GUIOs["ASSETS_ASSETAPPLYBUTTON"].deactivate()
    def __updateAssetDataDisplay():
        _assetName_selected = self.GUIOs["ASSETS_ASSETSELECTIONBOX"].getSelected()
        if (self.puVar['simulation_selected'] == None): _asset = self.puVar['simulationSetup_assets'][_assetName_selected]
        else:                                           _asset = self.puVar['simulations'][self.puVar['simulation_selected']]['assets'][_assetName_selected]
        self.GUIOs["ASSETS_INITIALWALLETBALANCEDISPLAYTEXT"].updateText(text = auxiliaries.floatToString(number = _asset['initialWalletBalance'], precision = _ASSETPRECISIONS[_assetName_selected]))
        if (self.puVar['simulation_selected'] == None): self.GUIOs["ASSETS_INITIALWALLETBALANCETEXTINPUTBOX"].updateText(text = auxiliaries.floatToString(number = _asset['initialWalletBalance'], precision = _ASSETPRECISIONS[_assetName_selected], comma = False))
        self.GUIOs["ASSETS_ALLOCATABLEBALANCEDISPLAYTEXT"].updateText(text = auxiliaries.floatToString(number = _asset['allocatableBalance'], precision = _ASSETPRECISIONS_S[_assetName_selected]))
        self.GUIOs["ASSETS_ALLOCATEDBALANCEDISPLAYTEXT"].updateText(text = auxiliaries.floatToString(number = _asset['allocatedBalance'], precision = _ASSETPRECISIONS_S[_assetName_selected]))
        self.GUIOs["ASSETS_ALLOCATIONRATIOSLIDER"].setSliderValue(newValue = _asset['allocationRatio']*100, callValueUpdateFunction = False)
        self.GUIOs["ASSETS_ALLOCATIONRATIODISPLAYTEXT"].updateText(text = "{:.1f} %".format(_asset['allocationRatio']*100))
        self.GUIOs["ASSETS_ASSUMEDRATIODISPLAYTEXT"].updateText(text = "{:.3f} %".format(_asset['assumedRatio']*100))
        if (_asset['weightedAssumedRatio'] == None): self.GUIOs["ASSETS_WEIGHTEDASSUMEDRATIODISPLAYTEXT"].updateText(text = "-")
        else:                                        self.GUIOs["ASSETS_WEIGHTEDASSUMEDRATIODISPLAYTEXT"].updateText(text = "{:.3f} %".format(_asset['weightedAssumedRatio']*100))
        if   (_asset['maxAllocatedBalance'] == None):         self.GUIOs["ASSETS_MAXALLOCATEDBALANCEDISPLAYTEXT"].updateText(text = "-")
        elif (_asset['maxAllocatedBalance'] == float('inf')): self.GUIOs["ASSETS_MAXALLOCATEDBALANCEDISPLAYTEXT"].updateText(text = "INF")
        else:                                                 self.GUIOs["ASSETS_MAXALLOCATEDBALANCEDISPLAYTEXT"].updateText(text = auxiliaries.floatToString(number = _asset['maxAllocatedBalance'], precision = _ASSETPRECISIONS_S[_assetName_selected]))
    def __checkIfCanEditAssetParams():
        _assetName_selected = self.GUIOs["ASSETS_ASSETSELECTIONBOX"].getSelected()
        #Get Entered Values
        try:    _initialWalletBalance = round(float(self.GUIOs["ASSETS_INITIALWALLETBALANCETEXTINPUTBOX"].getText()), _ASSETPRECISIONS[_assetName_selected])
        except: _initialWalletBalance = None
        _allocationRatio = round(self.GUIOs["ASSETS_ALLOCATIONRATIOSLIDER"].getSliderValue()/100, 3)
        #Get Current Values
        _asset = self.puVar['simulationSetup_assets'][_assetName_selected]
        _initialWalletBalance_current = _asset['initialWalletBalance']
        _allocationRatio_current      = _asset['allocationRatio']
        #Tests
        _testPassed = True
        if not((_initialWalletBalance != None) and (0 <= _initialWalletBalance)):                                           _testPassed = False
        if not((_initialWalletBalance != _initialWalletBalance_current) or (_allocationRatio != _allocationRatio_current)): _testPassed = False
        #Finally
        if (_testPassed == True): self.GUIOs["ASSETS_ASSETAPPLYBUTTON"].activate()
        else:                     self.GUIOs["ASSETS_ASSETAPPLYBUTTON"].deactivate()
    auxFunctions['ONASSETSELECTIONUPDATE']    = __onAssetSelectionUpdate
    auxFunctions['UPDATEASSETDATADISPLAY']    = __updateAssetDataDisplay
    auxFunctions['CHECKIFCANEDITASSETPARAMS'] = __checkIfCanEditAssetParams

    #Return the generated functions
    return auxFunctions
#AUXILALRY FUNCTIONS END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------