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
from GUI.pageSetups.atmEta_gui_pgSetup_dataBase         import setupPage as pSetup_dataBase
from GUI.pageSetups.atmEta_gui_pgSetup_neuralNetwork    import setupPage as pSetup_neuralNetwork

#Python Modules
import time
import pyglet
import os
import json
import traceback
import termcolor
import datetime

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
_PAGESTOINITIALIZE = ("DASHBOARD", "SETTINGS", "ACCOUNTS", "AUTOTRADE", "CURRENCYANALYSIS", "ACCOUNTHISTORY", "MARKET", "SIMULATION", "SIMULATIONRESULT", "DATABASE", "NEURALNETWORK")

#DEVELOPER CONSTANTS
_CONSOLEPRINT_FPS = False
_CONSOLEPRINT_PPS = False

class procManager_GUI:
    #Manager Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, path_project, ipcA):
        print(termcolor.colored("   Initializing", 'green'), termcolor.colored("GUI Manager", 'light_blue'), termcolor.colored("-----------------------------------------------------------------------------------------------------------------------", 'green'))
        #IPC Assistance
        self.ipcA = ipcA
        for fID in ('onAccountUpdate',
                    'onCurrencyAnalysisUpdate',
                    'onTradeConfigurationUpdate',
                    'onKlineStreamReceival',
                    'onCurrenciesUpdate',
                    'onAnalyzerCentralUpdate',
                    'onCurrencyAnalysisConfigurationUpdate',
                    'onNeuralNetworkUpdate',
                    'onProcessUpdate',
                    'onSimulatorCentralUpdate',
                    'onSimulationUpdate'):
            self.ipcA.addDummyFARHandler(functionID = fID)

        #Project Path
        self.path_project = path_project
        
        #Graphcis Control
        self.displaySpaceDefiner = None

        #GUI Configurations
        self.__config_GUI  = {"fullscreen": True,                      #Fullscreen
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
        self.__config_GUIOs = dict()
        #---Read GUI Configuration and print
        print("Reading GUI Configuration...")
        self.__readGUIConfig()
        print(" <GUI Configuration>\n"
             f" * windowSize:   {self.__config_GUI['windowSize']}\n"
             f" * resolution:   {self.__config_GUI['resolution']}\n"
             f" * windowTitle:  {self.__config_GUI['windowTitle']}\n"
             f" * windowIcon:   {self.__config_GUI['windowIcon']}\n"
             f" * maxFPS:       {self.__config_GUI['maxFPS']}\n"
             f" * maxPPS:       {self.__config_GUI['maxPPS']}\n"
             f" * MSAA:         {self.__config_GUI['MSAA']}\n"
             f" * VSync:        {self.__config_GUI['VSync']}\n"
             f" * Language:     {self.__config_GUI['Language']}\n"
             f" * ImageGenMSAA: {self.__config_GUI['ImageGenMSAA']}\n"
             f" * GUITheme:     {self.__config_GUI['GUITheme']}\n"
             f" * AudioMute:    {self.__config_GUI['AudioMute']}\n"
             f" * AudioVolume:  {self.__config_GUI['AudioVolume']}")
        print(f" * Using Display Space Definer for {self.__config_GUI['resolution'][0]}x{self.__config_GUI['resolution'][1]}: {self.displaySpaceDefiner}")
        print("GUI Configuration Read Complete!")
        #---Read GUIO Configurations and print
        print("\nReading GUIO Configurations...")
        self.__readGUIOConfigs()
        print(f" * {len(self.__config_GUIOs)} GUIO configurations imported")
        print("GUIO Configurations Read Complete!") #---Print configuration

        #Image & Audio Manager Initialization
        self.imageManager  = atmEta_gui_manager_image.imageManager(self.path_project,   self.__config_GUI)
        self.audioManager  = atmEta_gui_manager_audio.audioManager(self.path_project,   self.__config_GUI)
        self.visualManager = atmEta_gui_manager_visual.visualManager(self.path_project, self.__config_GUI)

        #Identify Monitor Information
        print("\nAnalyzing Monitor Information...")
        self.allowFullScreen = False
        display = pyglet.canvas.get_display(); screens = display.get_screens()
        print(" <Detected Monitors>")
        for index, screen in enumerate(screens): print(f"  [{index}]: {screen}")
        if (f"{screens[0].width}x{screens[0].height}" in _SCREENASPECTRATIOTABLE):
            print(" * Primary screen specification is supported by the program, fullscreen mode is", termcolor.colored("allowed", 'light_green'))
            self.allowFullscreen = True
        else: 
            print(" * Primary screen specification is not supported by the program, fullscreen mode is", termcolor.colored("disallowed", 'light_red'))
            self.allowFullscreen = False
        self.allowFullscreen = True

        print("Monitor Information Analysis Complete!")

        #Window Object Initialization
        config = pyglet.gl.Config(sample_buffers = 1, samples = self.__config_GUI["MSAA"])
        self.window = pyglet.window.Window(width   = self.__config_GUI["windowSize"][0], 
                                           height  = self.__config_GUI["windowSize"][1],
                                           caption = self.__config_GUI["windowTitle"],
                                           config  = config,
                                           vsync   = self.__config_GUI["VSync"])
        self.windowIcon = pyglet.image.load(os.path.join(self.path_project, 'GUI', 'imgs', self.__config_GUI["windowIcon"]))
        self.window.set_icon(self.windowIcon)
        if ((self.allowFullscreen == True) and (self.__config_GUI["fullscreen"] == True)): self.window.set_fullscreen(True); self.window.activate()
        else:                                                                              self.window.set_location(_WINDOWPOS_X_INITIAL, _WINDOWPOS_Y_INITIAL)

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
        pyglet.clock.schedule_interval(func = self.__process, interval = 1/self.__config_GUI['maxPPS'])
        pyglet.app.run(1/self.__config_GUI['maxFPS'])

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
        newPage = atmEta_gui_Generals.guiPage(self.window, self.GUIOCallSysFunc, self.displaySpaceDefiner, self.__config_GUIOs, self.imageManager, self.audioManager, self.visualManager, pageName, self.ipcA, self.path_project)
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
        elif (pageName == "DATABASE"):         pSetup_dataBase(newPage)
        elif (pageName == "NEURALNETWORK"):    pSetup_neuralNetwork(newPage)

    def __toggleFullscreen(self):
        if not self.allowFullscreen:
            return
        self.window.set_fullscreen(not(self.__config_GUI["fullscreen"]))
        self.__config_GUI["fullscreen"] = not(self.__config_GUI["fullscreen"])
    #Auxillary Functions END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Configuration ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __readGUIConfig(self):
        #[1]: Configuration File Read
        try:
            config_dir = os.path.join(self.path_project, 'configs', 'guiConfig.config')
            with open(config_dir, 'r') as f:
                config_loaded = json.load(f)
        except: 
            config_loaded = dict()

        #[2]: Contents Verification
        #---[2-1]: FullScreen
        fullscreen = config_loaded.get('fullscreen', True)
        if not isinstance(fullscreen, bool): fullscreen = True
        #---[2-2]: Window Size
        windowSize = config_loaded.get('windowSize', (1920, 1080))
        if not(isinstance(windowSize, list)) or len(windowSize) != 2: windowSize = (1920, 1080)
        windowSize     = tuple(windowSize)
        windowSize_str = f"{windowSize[0]}x{windowSize[1]}"
        if windowSize_str not in _SCREENASPECTRATIOTABLE:
            windowSize     = (1920, 1080)
            windowSize_str = f"{windowSize[0]}x{windowSize[1]}"
        #---[2-3]: Resolution
        resolution = config_loaded.get('resolution', (1920, 1080))
        if not(isinstance(resolution, list)) or len(resolution) != 2: resolution = (1920, 1080)
        resolution     = tuple(resolution)
        resolution_str = f"{resolution[0]}x{resolution[1]}"
        if resolution_str not in _SCREENASPECTRATIOTABLE:
            resolution     = (1920, 1080)
            resolution_str = f"{resolution[0]}x{resolution[1]}"
        #---[2-4]: Window Title 
        windowTitle = config_loaded.get('windowTitle', "AUTO TRADE MACHINE ETA")
        if not(isinstance(windowTitle, str)): windowTitle = "AUTO TRADE MACHINE ETA"
        #---[2-5]: Window Icon
        windowIcon = config_loaded.get('windowIcon', "windowIcon.png")
        if not(isinstance(windowIcon, str)): windowIcon = "windowIcon.png"
        #---[2-6]: maxFPS
        maxFPS = config_loaded.get('maxFPS', 60)
        if not isinstance(maxFPS, int): maxFPS = 60
        if not 10 <= maxFPS <= 300:     maxFPS = 60
        #---[2-7]: maxPPS
        maxPPS = config_loaded.get('maxPPS', 120)
        if not isinstance(maxPPS, int): maxPPS = 120
        if not 10 <= maxPPS <= 300:     maxPPS = 120
        #---[2-8]: MSAA
        msaa = config_loaded.get('MSAA', 2)
        if not isinstance(msaa, int):    msaa = 2
        if not 2 <= msaa <= 32:          msaa = 2
        if not (msaa & (msaa - 1)) == 0: msaa = 2
        #---[2-9]: VSync
        vSync = config_loaded.get('VSync', False)
        if not isinstance(vSync, bool): vSync = False
        #---[2-10]: Language
        language = config_loaded.get('Language', 'ENG')
        if language not in ('ENG', 'KOR'): language = 'ENG'
        #---[2-11]: ImageGenMSAA
        imageGenMSAA = config_loaded.get('ImageGenMSAA', 4)
        if not isinstance(imageGenMSAA, int):            imageGenMSAA = 4
        if not 2 <= imageGenMSAA <= 32:                  imageGenMSAA = 4
        if not (imageGenMSAA & (imageGenMSAA - 1)) == 0: imageGenMSAA = 4
        #---[2-12]: GUITheme
        guiTheme = config_loaded.get('GUITheme', 'LIGHT')
        if guiTheme not in ('DARK', 'LIGHT'): guiTheme = 'LIGHT'
        #---[2-13]: AudioMute
        audioMute = config_loaded.get('AudioMute', False)
        if not isinstance(audioMute, bool): audioMute = False
        #---[2-14]: AudioVolume
        audioVolume = config_loaded.get('AudioVolume', 100)
        if not isinstance(audioVolume, int): audioVolume = 100
        if not 0 <= audioVolume <= 100:      audioVolume = 100

        #[3]: Update and save the configuration
        self.__config_GUI = {'fullscreen':   fullscreen,
                             'windowSize':   windowSize,
                             'resolution':   resolution,
                             'windowTitle':  windowTitle,
                             'windowIcon':   windowIcon,
                             'maxFPS':       maxFPS,
                             'maxPPS':       maxPPS,
                             'MSAA':         msaa,
                             'VSync':        vSync,
                             'Language':     language,
                             'ImageGenMSAA': imageGenMSAA,
                             'GUITheme':     guiTheme,
                             'AudioMute':    audioMute,
                             'AudioVolume':  audioVolume}
        self.displaySpaceDefiner = _SCREENASPECTRATIOTABLE[resolution_str]
        self.__saveGUIConfig()

    def __saveGUIConfig(self):
        #[1]: Reformat config for save
        config = self.__config_GUI
        config_toSave = {"fullscreen":   config["fullscreen"],   #Fullscreen
                         "windowSize":   config["windowSize"],   #Window Size
                         "resolution":   config["resolution"],   #Resolution
                         "windowTitle":  config["windowTitle"],  #Window Title
                         "windowIcon":   config["windowIcon"],   #Window Icon
                         "maxFPS":       config["maxFPS"],       #Frames per second
                         "maxPPS":       config["maxPPS"],       #Processes per second
                         "MSAA":         config["MSAA"],         #Multisample Anti-Aliasing
                         "VSync":        config["VSync"],        #VSync
                         "Language":     config["Language"],     #Language
                         "ImageGenMSAA": config["ImageGenMSAA"], #Image Generation Multisample Anti-Aliasing
                         "GUITheme":     config["GUITheme"],     #GUI Theme
                         "AudioMute":    config["AudioMute"],    #Audio Mute
                         "AudioVolume":  config["AudioVolume"]}  #Audio Volume

        #[2]: Save the reformatted configuration file
        config_dir = os.path.join(self.path_project, 'configs', 'guiConfig.config')
        try:
            with open(config_dir, 'w') as f:
                json.dump(config_toSave, f, indent=4)
        except Exception as e:
            time_str = datetime.fromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M:%S")
            print(termcolor.colored(f"[GUIMANAGER-{time_str}] An Unexpected Error Occurred While Attempting to Save GUI Manager Configuration. User Attention Strongly Advised"
                                    f" * Error:          {e}\n"
                                    f" * Detailed Trace: {traceback.format_exc()}\n", 
                                    'light_red'))

    def __readGUIOConfigs(self, configName = None):
        if (configName is None): targets = [fileName for fileName in os.listdir(os.path.join(self.path_project, 'configs')) if fileName.startswith('guioConfig_')]; self.__config_GUIOs.clear()
        else:                    targets = [f'guioConfig_{configName}.config',]
        for fileName in targets:
            try:
                config_dir = os.path.join(self.path_project, 'configs', fileName)
                objectName = fileName.split(".")[0][11:]
                with open(config_dir, 'r') as f:
                    self.__config_GUIOs[objectName] = json.load(f)
            except Exception as e: print(termcolor.colored(f"[GUI] An unexpected error occurred while attempting to read GUIO config file '{fileName}'\n *", 'light_red'), termcolor.colored(e, 'light_red'))

    def __saveGUIOConfigs(self, configName = None):
        if (configName is None): configNamesToSave = self.__config_GUIOs.keys()
        else:                    configNamesToSave = [configName,]
        for cName in configNamesToSave:
            fileName = f'guioConfig_{cName}.config'
            try:
                config_dir = os.path.join(self.path_project, 'configs', fileName)
                with open(config_dir, 'w') as f:
                    json.dump(self.__config_GUIOs[cName], f, indent=4)
            except Exception as e: 
                time_str = datetime.fromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M:%S")
                print(termcolor.colored(f"[GUIMANAGER-{time_str}] An Unexpected Error Occurred While Attempting to Save GUIO Configuration '{cName}'. User Attention Strongly Advised"
                                        f" * Error:          {e}\n"
                                        f" * Detailed Trace: {traceback.format_exc()}\n", 
                                        'light_red'))
    #Configuration END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #System Functions -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __sysFunc_terminateProgram(self):
        self.ipcA.sendFAR(targetProcess = 'MAIN', functionID = 'TERMINATEPROGRAM', functionParams = None, farrHandler = None)

    def __sysFunc_toggleFullscreen(self): 
        self.__toggleFullscreen()

    def __sysFunc_isFullScreen(self): 
        return self.__config_GUI['fullscreen']

    def __sysFunc_loadPage(self, pageName):
        if (pageName in self.pages):
            if (self.currentPage != None): self.pages[self.currentPage].on_PageEscape()
            self.currentPage = pageName
            self.pages[self.currentPage].on_PageLoad()

    def __sysFunc_saveGUIConfig(self):
        self.__saveGUIConfig()

    def __sysFunc_changeGUITheme(self, guiTheme):
        if (((guiTheme == 'LIGHT') and (self.__config_GUI['GUITheme'] == 'DARK')) or ((guiTheme == 'DARK') and (self.__config_GUI['GUITheme'] == 'LIGHT'))): self.__config_GUI['GUITheme'] = guiTheme
        self.imageManager.on_GUIThemeUpdate()
        self.visualManager.on_GUIThemeUpdate()
        for pageName in self.pages.keys(): self.pages[pageName].on_GUIThemeUpdate()

    def __sysFunc_changeLanguage(self, language):
        if (language in self.visualManager.availableLanguages): self.__config_GUI['Language'] = language
        self.visualManager.on_LanguageUpdate()
        for pageName in self.pages.keys(): self.pages[pageName].on_LanguageUpdate()

    def __sysFunc_editGUIOConfig(self, configName, targetContent):
        self.__config_GUIOs[configName] = targetContent
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