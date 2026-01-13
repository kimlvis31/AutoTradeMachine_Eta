#ATM Modules
from atmEta_IPC import _THREADTYPE_MT as IPCTHREAD_MT, _THREADTYPE_AT as IPCTHREAD_AT
from GUI import atmEta_gui_Generals
from GUI.guiManagers import atmEta_gui_manager_image, atmEta_gui_manager_visual, atmEta_gui_manager_audio

from GUI.pageSetups.atmEta_gui_pgSetup_dashboard        import setupPage as pSetup_dashboard
from GUI.pageSetups.atmEta_gui_pgSetup_settings         import setupPage as pSetup_settings
from GUI.pageSetups.atmEta_gui_pgSetup_accounts         import setupPage as pSetup_accounts
from GUI.pageSetups.atmEta_gui_pgSetup_autotrade        import setupPage as pSetup_autotrade
from GUI.pageSetups.atmEta_gui_pgSetup_currencyAnalysis import setupPage as pSetup_currencyAnalysis
from GUI.pageSetups.atmEta_gui_pgSetup_accountHistory   import setupPage as pSetup_accountHistory
from GUI.pageSetups.atmEta_gui_pgSetup_market           import setupPage as pSetup_market
from GUI.pageSetups.atmEta_gui_pgSetup_simulation       import setupPage as pSetup_simulation
from GUI.pageSetups.atmEta_gui_pgSetup_simulationResult import setupPage as pSetup_simulationResult
from GUI.pageSetups.atmEta_gui_pgSetup_neuralNetwork    import setupPage as pSetup_neuralNetwork

#Python Modules
import time
import pyglet
import os
import json
import termcolor
import pprint

#INITIAL VALUE
_CONFIG_GUI_INITIAL = {"fullscreen": True,                      #Fullscreen
                       "windowSize": (1920, 1080),              #Window Size
                       "resolution": (1920, 1080),              #Resolution
                       "windowTitle": "AUTO TRADE MACHINE ETA", #Window Title
                       "windowIcon": "windowIcon.png",          #Window Icon
                       "maxFPS": 60,                            #Frames per second
                       "maxPPS": 120,                           #Processes per second
                       "MSAA": 2,                               #Multisample Anti-Aliasing
                       "VSync": False,                          #VSync
                       "Language": 'ENG',                       #Language
                       "ImageGenMSAA": 4,                       #Image Generation Multisample Anti-Aliasing
                       "GUITheme": 'DARK',                      #GUI Theme
                       "AudioMute": False,                      #Audio Mute
                       "AudioVolume": 100}                      #Audio Volume

#ATM GUI CONSTANTS
_WINDOWPOS_X_INITIAL = 100
_WINDOWPOS_Y_INITIAL = 100
#---Screen Aspect Ratio Table, only supports the resolutions listed below (16:9H, 21:9H, 32:9H)
_SCREENASPECTRATIOTABLE = {'1920x1080': {'resolutionX': 1920, 'resolutionY': 1080, 'ratio': '16:9H', 'scaler': 0.12}, # 16:9 FHD HORIZONTAL
                           '2560x1440': {'resolutionX': 2560, 'resolutionY': 1440, 'ratio': '16:9H', 'scaler': 0.16}, # 16:9 QHD HORIZONTAL
                           '3840x2160': {'resolutionX': 3840, 'resolutionY': 2160, 'ratio': '16:9H', 'scaler': 0.24}, # 16:9 UHD HORIZONTAL
                                  
                           '2520x1080': {'resolutionX': 2520, 'resolutionY': 1080, 'ratio': '21:9H', 'scaler': 0.12}, # 21:9 FHD HORIZONTAL
                           '3360x1440': {'resolutionX': 3360, 'resolutionY': 1440, 'ratio': '21:9H', 'scaler': 0.16}, # 21:9 QHD HORIZONTAL
                                 
                           '3840x1080': {'resolutionX': 3840, 'resolutionY': 1080, 'ratio': '32:9H', 'scaler': 0.12}, # 32:9 FHD HORIZONTAL
                           '5120x1440': {'resolutionX': 5120, 'resolutionY': 1440, 'ratio': '32:9H', 'scaler': 0.16}} # 32:9 QHD HORIZONTAL
#---Page Initialization List
_PAGESTOINITIALIZE = ("DASHBOARD", "SETTINGS", "ACCOUNTS", "AUTOTRADE", "CURRENCYANALYSIS", "ACCOUNTHISTORY", "MARKET", "SIMULATION", "SIMULATIONRESULT", "NEURALNETWORK")

#DEVELOPER CONSTANTS
_CONSOLEPRINT_FPS = False
_CONSOLEPRINT_PPS = False

class procManager_GUI:
    #Manager Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, path_project, ipcA):
        print(termcolor.colored("   Initializing", 'green'), termcolor.colored("GUI Manager", 'light_blue'), termcolor.colored("-----------------------------------------------------------------------------------------------------------------------", 'green'))
        #IPC Assistance
        self.ipcA = ipcA

        #Project Path
        self.path_project = path_project
        
        #Graphcis Control
        self.displaySpaceDefiner = None

        #GUI Configurations
        self.config_GUI   = _CONFIG_GUI_INITIAL.copy()
        self.config_GUIOs = dict()
        if (True):
            #---Read GUI Configuration and print
            print("Reading GUI Configuration...")
            self.__readGUIConfig()
            print(" <GUI Configuration>\n",
                  " * windowSize:  ", self.config_GUI['windowSize'], "\n",
                  " * resolution:  ", self.config_GUI['resolution'], "\n",
                  " * windowTitle: ", self.config_GUI['windowTitle'], "\n",
                  " * windowIcon:  ", self.config_GUI['windowIcon'], "\n",
                  " * maxFPS:      ", self.config_GUI['maxFPS'], "\n",
                  " * maxPPS:      ", self.config_GUI['maxPPS'], "\n",
                  " * MSAA:        ", self.config_GUI['MSAA'], "\n",
                  " * VSync:       ", self.config_GUI['VSync'], "\n",
                  " * Language:    ", self.config_GUI['Language'], "\n",
                  " * ImageGenMSAA:", self.config_GUI['ImageGenMSAA'], "\n",
                  " * GUITheme:    ", self.config_GUI['GUITheme'], "\n",
                  " * AudioMute:   ", self.config_GUI['AudioMute'], "\n",
                  " * AudioVolume: ", self.config_GUI['AudioVolume'])
            print(" * Using Display Space Definer for {:d}x{:d}: {:s}".format(self.config_GUI['resolution'][0], self.config_GUI['resolution'][1], str(self.displaySpaceDefiner)))
            print("GUI Configuration Read Complete!")
            #---Read GUIO Configurations and print
            print("\nReading GUIO Configurations...")
            self.__readGUIOConfigs()
            print(" * {:d} GUIO configurations imported".format(len(self.config_GUIOs)))
            print("GUIO Configurations Read Complete!") #---Print configuration

        #Image & Audio Manager Initialization
        self.imageManager  = atmEta_gui_manager_image.imageManager(self.path_project, self.config_GUI)
        self.audioManager  = atmEta_gui_manager_audio.audioManager(self.path_project, self.config_GUI)
        self.visualManager = atmEta_gui_manager_visual.visualManager(self.path_project, self.config_GUI)

        #Identify Monitor Information
        self.allowFullScreen = False
        if (True):
            print("\nAnalyzing Monitor Information...")
            display = pyglet.canvas.get_display(); screens = display.get_screens()
            print(" <Detected Monitors>")
            for index, screen in enumerate(screens): print("  [{:d}]: {:s}".format(index, str(screen)))
            if ("{:d}x{:d}".format(screens[0].width, screens[0].height) in _SCREENASPECTRATIOTABLE):
                print(" * Primary screen specification is supported by the program, fullscreen mode is", termcolor.colored("allowed", 'light_green'))
                self.allowFullscreen = True
            else: 
                print(" * Primary screen specification is not supported by the program, fullscreen mode is", termcolor.colored("disallowed", 'light_red'))
                self.allowFullscreen = False
            self.allowFullscreen = True

            print("Monitor Information Analysis Complete!")

        #Window Object Initialization
        if (True):
            config = pyglet.gl.Config(sample_buffers = 1, samples = self.config_GUI["MSAA"])
            self.window = pyglet.window.Window(width      = self.config_GUI["windowSize"][0], 
                                               height     = self.config_GUI["windowSize"][1],
                                               caption    = self.config_GUI["windowTitle"],
                                               config     = config,
                                               vsync      = self.config_GUI["VSync"])
            self.windowIcon = pyglet.image.load(os.path.join(self.path_project, 'GUI', 'imgs', self.config_GUI["windowIcon"]))
            self.window.set_icon(self.windowIcon)
            if ((self.allowFullscreen == True) and (self.config_GUI["fullscreen"] == True)): self.window.set_fullscreen(True); self.window.activate()
            else:                                                                            self.window.set_location(_WINDOWPOS_X_INITIAL, _WINDOWPOS_Y_INITIAL)

        #GUIO Callable System Functions
        self.GUIOCallSysFunc = {'TERMINATEPROGRAM':  self.__sysFunc_terminateProgram,
                                'TOGGLE_FULLSCREEN': self.__sysFunc_toggleFullscreen,
                                'ISFULLSCREEN':      self.__sysFunc_isFullScreen,
                                'LOADPAGE':          self.__sysFunc_loadPage,
                                'SAVEGUICONFIG':     self.__sysFunc_saveGUIConfig,
                                'CHANGEGUITHEME':    self.__sysFunc_changeGUITheme,
                                'CHANGELANGUAGE':    self.__sysFunc_changeLanguage,
                                'EDITGUIOCONFIG':    self.__sysFunc_editGUIOConfig,
                                'GETPAGEPUVAR':      self.__sysFunc_getPagePUVar}

        #Pages Initialization
        self.pages = dict()
        for pageName in _PAGESTOINITIALIZE: self.__addPage(pageName)
        self.currentPage = "DASHBOARD"

        #Window Events Handler Functions
        if (True):
            @self.window.event
            def on_draw(): self.__draw()
            @self.window.event
            def on_key_press(symbol, modifiers):
                self.__InputHandler_KeyPress(symbol, modifiers)
                if (symbol == 65307): return pyglet.event.EVENT_HANDLED
            @self.window.event
            def on_key_release(symbol, modifiers): self.__InputHandler_KeyRelease(symbol, modifiers)
            @self.window.event
            def on_mouse_motion(x, y, dx, dy): self.__InputHandler_MouseMotion(x, y, dx, dy)
            @self.window.event
            def on_mouse_press(x, y, button, modifiers): self.__InputHandler_MousePress(x, y, button, modifiers)
            @self.window.event
            def on_mouse_release(x, y, button, modifiers): self.__InputHandler_MouseRelease(x, y, button, modifiers)
            @self.window.event
            def on_mouse_drag(x, y, dx, dy, button, modifiers): self.__InputHandler_MouseDrag(x, y, dx, dy, button, modifiers)
            @self.window.event
            def on_mouse_scroll(x, y, scroll_x, scroll_y): self.__InputHandler_MouseScroll(x, y, scroll_x, scroll_y)

        #System Clock Variables
        self.nProcessesThisSecond = list()
        self.nFramesThisSecond    = list()
        self.lastProcessTime_ns = 0

        print(termcolor.colored("   GUI Manager", 'light_blue'), termcolor.colored("Initialization Complete! -----------------------------------------------------------------------------------------------------------", 'green'))
    #Manager Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Manager Process Functions ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def start(self):
        pyglet.clock.schedule_interval(func = self.__process, interval = 1/self.config_GUI['maxPPS'])
        pyglet.app.run(1/self.config_GUI['maxFPS'])

    def terminate(self, requester):
        pyglet.app.exit()
        self.window.close()

    def __process(self, functionCallInterval):
        currentTime_ns = time.perf_counter_ns()

        #Page Processing and Process Reports Analysis
        sinceLastProcess_ns = currentTime_ns - self.lastProcessTime_ns; self.lastProcessTime_ns = currentTime_ns
        self.pages[self.currentPage].process(sinceLastProcess_ns)

        #FAR/FARR Processing
        self.ipcA.processFARs()
        self.ipcA.processFARRs()

        #PPS Calculation & Print
        if (_CONSOLEPRINT_PPS == True): 
            self.nProcessesThisSecond.append(currentTime_ns)
            try:
                while (1e9 <= (currentTime_ns-self.nProcessesThisSecond[0])): self.nProcessesThisSecond.pop(0)
            except: pass
            print("{:d} PPS".format(len(self.nProcessesThisSecond)))

    def __draw(self):
        #Graphics Drawing
        self.window.clear()
        self.pages[self.currentPage].draw()

        #FPS Calculation & Print
        if (_CONSOLEPRINT_FPS == True):
            currentTime_ns = time.perf_counter_ns()
            self.nFramesThisSecond.append(currentTime_ns)
            try:
                while (1e9 <= (currentTime_ns-self.nFramesThisSecond[0])): self.nFramesThisSecond.pop(0)
            except: pass
            print("{:d} FPS".format(len(self.nFramesThisSecond)))
    #Manager Process Functions END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Auxillary Functions ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __addPage(self, pageName):
        newPage = atmEta_gui_Generals.guiPage(self.window, self.GUIOCallSysFunc, self.displaySpaceDefiner, self.config_GUIOs, self.imageManager, self.audioManager, self.visualManager, pageName, self.ipcA, self.path_project)
        self.pages[pageName] = newPage
        if   (pageName == "DASHBOARD"):        pSetup_dashboard(newPage)
        elif (pageName == "SETTINGS"):         pSetup_settings(newPage)
        elif (pageName == "ACCOUNTS"):         pSetup_accounts(newPage)
        elif (pageName == "AUTOTRADE"):        pSetup_autotrade(newPage)
        elif (pageName == "CURRENCYANALYSIS"): pSetup_currencyAnalysis(newPage)
        elif (pageName == "ACCOUNTHISTORY"):   pSetup_accountHistory(newPage)
        elif (pageName == "MARKET"):           pSetup_market(newPage)
        elif (pageName == "SIMULATION"):       pSetup_simulation(newPage)
        elif (pageName == "SIMULATIONRESULT"): pSetup_simulationResult(newPage)
        elif (pageName == "NEURALNETWORK"):    pSetup_neuralNetwork(newPage)

    def __toggleFullscreen(self):
        if (self.allowFullscreen == True):
            self.window.set_fullscreen(not(self.config_GUI["fullscreen"]))
            self.config_GUI["fullscreen"] = not(self.config_GUI["fullscreen"])
    #Auxillary Functions END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Configuration ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __readGUIConfig(self):
        #Configuration File Read
        try:
            configFile = open(os.path.join(self.path_project, 'configs', 'gui', 'guiConfig.config'), 'r')
            self.config_GUI = json.loads(configFile.read())
            configFile.close()
        except: self.__saveGUIConfig()
        #Contents Verification
        #---Display Space Definer
        resolution_str = str(self.config_GUI['resolution'][0]) + "x" + str(self.config_GUI['resolution'][1])
        if resolution_str in _SCREENASPECTRATIOTABLE.keys(): 
            self.displaySpaceDefiner = _SCREENASPECTRATIOTABLE[resolution_str]
            self.config_GUI['windowSize'] = self.config_GUI['resolution']
        else:                                                    
            self.config_GUI['resolution'] = (1920, 1080)
            self.displaySpaceDefiner = _SCREENASPECTRATIOTABLE['1920x1080']
        #---GUITheme Value
        if not(self.config_GUI['GUITheme'] in ('DARK', 'LIGHT')): self.config_GUI['GUITheme'] = 'DARK'

    def __saveGUIConfig(self):
        configFile = open(os.path.join(self.path_project, 'configs', 'gui', 'guiConfig.config'), 'w')
        configFile.write(json.dumps(self.config_GUI))
        configFile.close()

    def __readGUIOConfigs(self, configName = None):
        if (configName == None): targets = [fileName for fileName in os.listdir(os.path.join(self.path_project, 'configs', 'gui')) if fileName[:11] == 'guioConfig_']; self.config_GUIOs.clear()
        else:                    targets = ['guioConfig_{:s}.config'.format(configName)]
        for fileName in targets:
            try:
                configFile = open(os.path.join(self.path_project, 'configs', 'gui', fileName), 'r')
                self.config_GUIOs[fileName.split(".")[0][11:]] = json.loads(configFile.read())
                configFile.close()
            except Exception as e: print(termcolor.colored("[GUI] An unexpected error occurred while attempting to read GUIO config file '{:s}'\n *".format(fileName), 'light_red'), termcolor.colored(e, 'light_red'))

    def __saveGUIOConfigs(self, configName = None):
        if (configName == None): configNamesToSave = self.config_GUIOs.keys()
        else:                    configNamesToSave = [configName]
        for configName in configNamesToSave:
            fileName = 'guioConfig_{:s}.config'.format(configName)
            try:
                configFile = open(os.path.join(self.path_project, 'configs', 'gui', fileName), 'w')
                configFile.write(json.dumps(self.config_GUIOs[configName]))
                configFile.close()
            except Exception as e: print(termcolor.colored("[GUI] An unexpected error occurred while attempting to write GUIO config file '{:s}'\n *".format(fileName), 'light_red'), termcolor.colored(e, 'light_red'))
    #Configuration END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #System Functions -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __sysFunc_terminateProgram(self):
        self.ipcA.sendFAR(targetProcess = 'MAIN', functionID = 'TERMINATEPROGRAM', functionParams = None, farrHandler = None)

    def __sysFunc_toggleFullscreen(self): 
        self.__toggleFullscreen()

    def __sysFunc_isFullScreen(self): 
        return self.config_GUI['fullscreen']

    def __sysFunc_loadPage(self, pageName):
        if (pageName in self.pages):
            if (self.currentPage != None): self.pages[self.currentPage].on_PageEscape()
            self.currentPage = pageName
            self.pages[self.currentPage].on_PageLoad()

    def __sysFunc_saveGUIConfig(self):
        self.__saveGUIConfig()

    def __sysFunc_changeGUITheme(self, guiTheme):
        if (((guiTheme == 'LIGHT') and (self.config_GUI['GUITheme'] == 'DARK')) or ((guiTheme == 'DARK') and (self.config_GUI['GUITheme'] == 'LIGHT'))): self.config_GUI['GUITheme'] = guiTheme
        self.imageManager.on_GUIThemeUpdate()
        self.visualManager.on_GUIThemeUpdate()
        for pageName in self.pages.keys(): self.pages[pageName].on_GUIThemeUpdate()

    def __sysFunc_changeLanguage(self, language):
        if (language in self.visualManager.availableLanguages): self.config_GUI['Language'] = language
        self.visualManager.on_LanguageUpdate()
        for pageName in self.pages.keys(): self.pages[pageName].on_LanguageUpdate()

    def __sysFunc_editGUIOConfig(self, configName, targetContent):
        self.config_GUIOs[configName] = targetContent
        self.__saveGUIOConfigs(configName = configName)

    def __sysFunc_getPagePUVar(self, pageName):
        if (pageName in self.pages): return self.pages[pageName].puVar
    #System Functions END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Input Hanlder Functions ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __InputHandler_KeyPress(self, symbol, modifiers):
        if (symbol == 65480): self.__toggleFullscreen() #F11, no shift
        self.pages[self.currentPage].handleKeyEvent({'eType': "PRESSED", 'symbol': symbol, 'modifiers': modifiers})
    def __InputHandler_KeyRelease(self, symbol, modifiers):              self.pages[self.currentPage].handleKeyEvent({'eType': "RELEASED", 'symbol': symbol, 'modifiers': modifiers})
    def __InputHandler_MouseMotion(self, x, y, dx, dy):                  self.pages[self.currentPage].handleMouseEvent({'eType': "MOVED",    'x': x/self.displaySpaceDefiner['scaler'], 'y': y/self.displaySpaceDefiner['scaler'], 'dx': dx/self.displaySpaceDefiner['scaler'], 'dy': dy/self.displaySpaceDefiner['scaler']}) 
    def __InputHandler_MousePress(self, x, y, button, modifiers):        self.pages[self.currentPage].handleMouseEvent({'eType': "PRESSED",  'x': x/self.displaySpaceDefiner['scaler'], 'y': y/self.displaySpaceDefiner['scaler'], 'button': button, 'modifiers': modifiers})
    def __InputHandler_MouseRelease(self, x, y, button, modifiers):      self.pages[self.currentPage].handleMouseEvent({'eType': "RELEASED", 'x': x/self.displaySpaceDefiner['scaler'], 'y': y/self.displaySpaceDefiner['scaler'], 'button': button, 'modifiers': modifiers})
    def __InputHandler_MouseDrag(self, x, y, dx, dy, button, modifiers): self.pages[self.currentPage].handleMouseEvent({'eType': "DRAGGED",  'x': x/self.displaySpaceDefiner['scaler'], 'y': y/self.displaySpaceDefiner['scaler'], 'dx': dx/self.displaySpaceDefiner['scaler'], 'dy': dy/self.displaySpaceDefiner['scaler'], 'button': button, 'modifiers': modifiers})
    def __InputHandler_MouseScroll(self, x, y, scroll_x, scroll_y):      self.pages[self.currentPage].handleMouseEvent({'eType': "SCROLLED", 'x': x/self.displaySpaceDefiner['scaler'], 'y': y/self.displaySpaceDefiner['scaler'], 'scroll_x': scroll_x, 'scroll_y': scroll_y}) 
    #Input Hanlder Functions END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------