# AutoTradeMachine_Eta

[![korean-readme](https://img.shields.io/badge/Language-한국어-blue.svg)](./README.ko.md)

---
### 📖 Project Introduction ###
This is the seventh version of the **Auto Trade Machine** project. I am very excited to finally upload this version on GitHub, as this is the first operational version of the ATM project. Unlike the previous versions, application structure and features will be described in details and how to use the application to automate trading for anyone interested.

#### ***What Is This?***  
When I started learning programming back in Summer 2023, I thought the best way would be to start one big project and absorb as much as I can from the experience. At the time I was also very interested in learning various trading strategies and heard about other people making automated trading programs using the APIs the trading platforms like Binance provide. It was also something that wouldn't be heavily limited by the choice of programming langauge or really anything. The degree of freedom this project could provide seemed like a great learning playground. So the ATM project began, with a goal of building an application on which users can customize and backtest their trading strategies, connect their market accounts, and automate trading 24/7.

#### ***Does It Actually Work?***  
First it must be defined what we mean by ***"it works"***. If we limit the scope of its definition to the capability of analyzing and executing real-time trades, almost yes. Does it make meaningful and stable profit? Depends on the strategy being used. It is hard to give a straight answer, and I will describe the reasons in more detail in the section below.  

I think sharing my own experience would give a more straight answer. I have been running the application 24/7 since August 24th, 2025. It has been about three months, and I traded three cryptocurrencies - `BTCUSDT`, `ETHUSDT`, and `XRPUSDT` on **Binance Futures**.   

Beforehand, I first backtested my trade strategy and confirmed relatively stable growth in the total account balance. Over the span of 5 years, the final balance grew to over ~150 times that of the initial, and the maximum droppage was around ~35% of the previous peak. It must be noted, however, that this was an optimized result on a historical data. This result does not mean that the similar pattern will appear in the future.

I have been lucky during the last three months though. Starting from 4,700 USDT, reached 4,000 USDT in October, and am now sitting at 5,660 USDT with unrealized PNL of 400 USDT at this very moment. The number can vary day to day, but that is roughly 7~8% monthly profit. But as the backtest result showed, my balance could go down directly to around 3,700 USDT or lower in the near future. So the risk always exists. The screenshot below is the total balance history of my actual Binance account.

<img src="./docs/balancehistory_myaccount.png" width="1100" height="300">

So I am confident to say, despite it still has some technical limitations, the application does what it should do. It serves as a platform on which trading strategies can be customized, tested, and be used to execute automated trades. How well it generates profit? It depends completely on the strategy the user configures and decides to use.

#### ***Performances***  
ATM-Eta is a multiprocessing program. Each of the managers, analyzers, and simulators is an independent process, and the numbers of analyzer and simulator processes are dynamically determined upon program initialization based on the number of CPU cores of the user's computer. This allows a simultaneous execution of automated trade schemes and backtestings with minimal bottle-neck. 

Currency analysis tasks are also dynamically allocated to each analyzer process during run-time, which allows efficient utilization of the hardware resources. The details on how this is done will be explained in the `System Architecture` section.

While the exact number varies depending on the configuration, average backtesting takes around 2~5 minutes per currency over a historical currency data of 5 years. It may seem slow but this is because not only does the simulator perform currency analysis, but also handles sequential trade execution, account data updates, SL (Stop-Loss) triggering, liquidation detection, etc. to simulate realistic trading environment.

#### ***Limitations***  
There still are problems that need to be addressed for the application to prove itself more useful and reliable. Some of them are closely related to each other, as will be described below.

* **Unstable Data Stream Connection During Highly Volatile Market**  
  This is the most significant problem this applciation has. There are a few reasons why this happens.

  During highly volatile market, Binance can disconnect some of the stream connections with its clients to its server load. This cannot be anticipated because the client-side has no way of knowing its position in the server's disconnection priority list or the logic behind it. Currently when such case occurs, the program automatically requests websocket stream connection with seconds of delay, fetch the entire orderbook (which again, costs API rate-limit), and update the local orderbook profile. This operation, especially considering that it needs to be done on hundreds of assets in a temporal window of only seconds, can easily create delays in generating trade logics. API rate-limit posed by the server is also a problem, because it takes only about 100 assets to reach the upper limit when requesting full orderbook profile data fetch.

  The second scenario is when the stream data floods in too fast to the point where the client's computer cannot handle. As a form of handling the backpressure, the `python-binance` module automatically disconnects the websocket stream raising `'queue overflow'` exception. This application already has adjusted the maximum queue size so this case does not happen as often, it still appears to be almost impossible to avoid this issue completely.

* **Limited Flexibility In Trade Strategy Customization**  
  The only means of trade strategy customization is adjusting the predetermined set of variables of existing functions that ar hard-coded in the source code. This means whenever there needs to be a change in the trade logic, the program itself needs to be updated. This structure has an advantage of being more crash-proof and reliable. However, the fact that it is hard to expand the scope of customization is directly against the very purpose of this application.

* **High-Resource Usage**  
  All of the features - data collection, database management, simulation and automated trading management are all included in a single program. The current multiprocessing structure requiring a minimum of one process for each of these tasks make the application very resource-heavy, and the current inefficient IPC module makes it even worse. Once you start the application, you will be able to see that this application takes up 5~10 Gb of RAM (Depending on the number of analyzers+simulators initialized), even during an idle state. The reasons are as below.

   * Large IPC message queue buffer size. Originally was determined to be so to relieve queue back-pressure.
   * Always-alive process structure. Instead of being dynamically generated and terminated once a task is completed, each of the processes of this application are initialized upon program launch, as stay alive until the main process determines to terminate the entire program.

#### ***Future Plans***  
Since a major system restructuring is anticipated to be needed in order to address the current limitations, I decided to wrap up this version here and move on to the next. The successor will have the major roles - data collection, automated trading, and simulation be completely separated. Comprehensive redesign of IPC module and server connection handler will be made, and more flexible and detailed trade strategy customization and visualization methods will be introduced.

---

### 🧱 System Architecture ###
The image below shows a simplified diagram of the multiprocessing structure of ATM-Eta.
  
<img src="./docs/processHierarchy.png" width="600" height="400">
  
Each of the processes communicate with each other via `IPCAssistant` class defined in the `atmEta_IPC.py` module. Described below is the task and characterstic of each process.

* **Main**  
Upon the application launch, identifies the system requirements, determine number of simulators and analyzers to generate, configure IPCs, and generate and start processes.

* **GUI Manager**  
Manages graphics and audio resources, interaction objects, and display objects to serve as a hub connecting the user and teh manage processes.

* **Binance API Manager**  
Responsible for market data fetch, stream connection, order placement, API rate-limit management, etc. It is one of the most vital parts of this application.

* **Data Manager**  
Keeps track of local market, account, simulation, and neural network data. Enables other managers to easily perform CRUD operations with the local DB.

* **Trade Manager**  
Manages all the tasks related to trading. These tasks include account connection (through the Binance API Manager), currency analysis and trade configuration management, trade logic determination, analyzer allocation, etc.

* **Analyzer**  
The number of analyzers are determined by the **main process** depending on the number of CPU cores and by the `ASRatio` in the `programConfig.config` file.  
`number of analyzers = (number of CPU cores - 8) * ASRatio`  
When the user adds a currency analysis, the analysis task is allocated to the most relevant or free analyzer process by the **Trade Manager**. The analyzer then request market data from the **Binance API Manager** and **Data Manager**, perform analysis, and dispatch generated `PIP (Potential Investment Plan)` signals to the **Trade Manager**.

* **Simulation Manager**  
Manages all the simulation processes and history. When the user configures a simulation setup and sends a queue append request, **simulation manager** reformats the configuration, allocate the task to the most appropriate simulator process, and keeps track of the task process until complete.

* **Simulator**  
The number of simulators are determined by the **main process** depending on the number of CPU cores and by the `ASRatio` in the `programConfig.config` file (same as with analyzers, but inversly proportional).  
`number of simulators = (number of CPU cores - 8) * (1 - ASRatio)`   
dsad

* **Neural Network Manager**  
This is an experimental neural network module to examine any possible effectiveness of neural network models in trading. It enables users to configure, initialize, and train models on historical market data which can later be imported by `Analyzers` or `Simulators` to provide an additional reference of market analysis.

---

### ▶️ How To Run ###
* ***Windows*** 🪟
1. Run `setup.bat` in the root directory. This will setup .venv to install any necessary libraries for this application.
2. Run `run.bat` in the root directory. This will start the application.

* ***Linux*** 🐧 ***/*** ***MacOS*** 🍎
1. Enter the command `chmod +x setup.sh run.sh`
2. Run `setup.sh` in the root directory. This will setup .venv to install any necessary libraries for this application.
3. Run `run.sh` in the root directory. This will start the application.

---

### 👀 Application Preview & How To Use ###
Once the program starts, a GUI window will open up letting the user to nagivate through different pages for each different tasks.

* <Details>
  <Summary><b><i> Pages </b></i></Summary>

  * <Details> 
      <Summary><b><i> Dashboard </b></i></Summary>
      <img src="./docs/dashboard_0.png" width="960" height="540">
      This is the *Dashboard* page. In this page, the user can

      1. Navigate to other pages  
      2. Terminate the application  
    </Details>

  * <Details> 
      <Summary><b><i> Accounts </b></i></Summary>
      <img src="./docs/accounts_0.png" width="960" height="540">
      This is the *Accounts* page. In this page, the user can  

      1. Create a local virtual account instance
      2. Create a local actual account instance / link to Binance account  
      3. View account asset / position data
      4. Determine the trade configurations of assets / positions.
      5. View position-wise trade control variable details.
    </Details>

  * <Details> 
      <Summary><b><i> AutoTrade </b></i></Summary>
      <img src="./docs/autotrade_0.png" width="960" height="540">
      This is the *AutoTrade* page. In this page, the user can  
      
      1. View Analyzers status.
      2. Create a currency analysis configuration (CAC)
      3. Add a currency analysis by choosing a CAC and a symbol to analyze.
      4. View currency analysis list and status
      5. Create a trade configuration (TC)
    </Details>

  * <Details> 
      <Summary><b><i> Currency Analysis </b></i></Summary>
      <img src="./docs/currencyanalysis_0.png" width="960" height="540">
      This is the *Currency Analysis* page. In this page, the user can  

      1. Choose a currency analysis and view its chart.
      2. View the CAC applied to the currently chosen currency analysis
    </Details>

  * <Details> 
      <Summary><b><i> Account History </b></i></Summary>
      <img src="./docs/accounthistory_0.png" width="960" height="540">
      This is the *Account History* page. In this page, the user can  

      1. View actual/virtual account trade logs and balance history.
    </Details>

  * <Details> 
      <Summary><b><i> Market </b></i></Summary>
      <img src="./docs/market_0.png" width="960" height="540">
      This is the *Market* page. In this page, the user can  

      1. View current market positions list
      2. View a position chart
      3. Configure a temporary currency analysis, and analyze on the determined temporal window.
    </Details>

  * <Details> 
      <Summary><b><i> Simulation </b></i></Summary>
      <img src="./docs/simulation_0.png" width="960" height="540">

      This is the *Simulation* page. In this page, the user can  
      1. View completed/processing simulation lists
      2. Copy trade configurations from the chosen simulation
      3. Backtest the configured target positions, trade strategies, initial variables, and simulation range.
    </Details>

  * <Details> 
      <Summary><b><i> Simulation Result </b></i></Summary>
      <img src="./docs/simulationresult_0.png" width="960" height="540">

      This is the *Simulation Result* page. In this page, the user can  
      1. View the completed simulations and their result summary.
      2. View account balance history.
      3. View simulation position setups, currency analysis configurations and trade configurations.
      4. View trade logs.
      4. Reconstruct currency analysis and view chart.
    </Details>

  * <Details> 
      <Summary><b><i> Database (Not Implemented) </b></i></Summary>
      This is the *Database* page. This page is not implemented.
    </Details>

  * <Details> 
      <Summary><b><i> Neural Network </b></i></Summary>
      <img src="./docs/neuralnetwork_0.png" width="960" height="540">

      This is the *Neural Network* page. In this page, the user can  

      1. Create a custom designed MLP (Multi-Layer Perceptron) model.
      2. Train the models using the chosen historical market data.
      3. View training results
    </Details>

  * <Details> 
      <Summary><b><i> Settings </b></i></Summary>
      <img src="./docs/settings_0.png" width="960" height="540">
      
      This is the *Settings* page. In this page, the user can  
      1. Change the langauge
      2. Change the GUI theme (Light Mode or Dark Mode)
      3. Toggle fullscreen mode
      4. Toggle or adjust audio
      5. Determine log display level on terminal
    </Details>
  </Details>

* <Details>
  <Summary><b><i> Features </b></i></Summary>
  This section describes the key features of this application step-by-step guide on how to use those features.

  * <Details>
    <Summary><b><i> Viewing Market & Perform Temporary Currency Analysis </b></i></Summary>
      By navigating to the Market page, the user can view the charts of the trading positions on Binance Futures and run temporary currency analysis.

      1. Navigate to Market page.
      2. Select a position.
      3. Click on settings button on the chart drawer.
      4. Configure currency analysis.
      5. Determine analysis range.
      6. Run.
      7. View analysis result.

    </Details>

  * <Details>
    <Summary><b><i> Adding a Currency Analysis Configuration </b></i></Summary>
      Currency Analysis Configuration, is just a predetermined configuration of a currency analysis.

      1. Navigate to AutoTrade page.
      2. Configure currency analysis in the highlighted section.
      3. Name the configuration and add
      4. Confirm

    </Details>

  * <Details>
    <Summary><b><i> Adding & Viewing Currency Analysis </b></i></Summary>
      Adding a currency analysis requires a CAC and a target position.

      1. Navigate to AutoTrade page.
      2. Select a position.
      3. Select a currency analysis configuration to apply.
      4. Add.
      5. Confirm and view

    </Details>

  * <Details>
    <Summary><b><i> Adding a Trade Configuration </b></i></Summary>
      Adding a trade configuration is very similar to adding a currency analysis configuration.

      1. Navigate to AutoTrade page.
      2. Configure trade control variables in the highlighted section.
      3. Name the configuration and add.
      4. Confirm.

    </Details>

  * <Details>
    <Summary><b><i> Backtesting & Results </b></i></Summary>
      Backtesting a configured trading strategy and evaluating the result is crucial for an automated trading system.

      1. Navigate to Simulation page.
      2. Configure simulation variables, positions, currency analysis, trade control, and account control.
      3. Start simulation
      4. View simulation result


    </Details>

  * <Details>
    <Summary><b><i> Adding Accounts & Automate Trading </b></i></Summary>
      In this application, the user can either create a virtual account to perform a real-time virtual trading, or a local instance of an actual Binance account to perform an actual trading.

      1. Navigate to Accounts page.
      2. Fill in accounts information and create
      3. [ACTUAL Only] Activate the account by entering the API and Secret key
      4. [ACTUAL Only - Optional] Activate the account using a flash drive.
      5. Configure positions, currency analysis, trade control, and account control.
      6. Start automated trading

    </Details>

  * <Details>
    <Summary><b><i> View Account History </b></i></Summary>
      Similary to viewing the simulation result, the user can view the account trade logs and balance history.

      1. Navigate to Account History page.
      2. Select trade logs tab to view trade logs.
      3. Select balance history tab to view account balance history.

    </Details>

  * <Details>
    <Summary><b><i> Creating and Training a Neural Network Model </b></i></Summary>
      While it remains at a very fundamental level, this application provides users to experiment with MLP in automated trading.

      1. Navigate to Neural Network page.
      2. Configure neural network model and create.
      3. Select a neural network model and historical market data to train on.
      4. Start training and view result.

    </Details>

  </Details>
  
---

### 🧠 Trading Strategy ### 
A trade strategy of this application consists of three configurations - Currency Analysis, Trade Control, and Account Control

<img src="./docs/tradestrategy_0.png" width="750" height="440">

* <Details>
  <Summary><b><i> Currency Analysis Configuration </b></i></Summary>
    
  Aside from the 7 custom-developed currency analysis methods (two of them being technical experiments) shown below, there are also the very well-known analysis methods such as SMA, EMA, WMA, PSAR, and BOLs. The ones described below are also a fusioned or modified versions of other *classical* analysis methods, so I imagine they would feel very familiar to anyone with some experience in trading.

  * <Details> 
    <Summary><b><i> IVP (Integrated Volume Profile) </b></i></Summary>
    <img src="./docs/ivp0.png" width="750" height="440">
    <img src="./docs/ivp1.png" width="750" height="440">

    This analysis method is fundamentally the same as what is famously known as VPVR (Volume Profile Visible Range). 
    </Details>

  * <Details> 
    <Summary><b><i> MMACD (Multi Moving Average Convergence and Divergence) </b></i></Summary>
    <img src="./docs/mmacd0.png" width="750" height="440">
    <img src="./docs/mmacd1.png" width="750" height="440">

    As its name suggests, this is a modified version of the technical analysis method MACD (Moving Average Convergence and Divergence). 
    </Details>

  * <Details> 
    <Summary><b><i> DMIxADX (Directional Movement Index and Average Directional Index) </b></i></Summary>
    <img src="./docs/dmixadx0.png" width="750" height="440">
    <img src="./docs/dmixadx1.png" width="750" height="440">

    This is a combined indicator of DMI (Directional Movement Index) and ADX (Average Directional Index)
    </Details>

  * <Details> 
    <Summary><b><i> MFI (Money Flow Index) </b></i></Summary>
    <img src="./docs/mfi0.png" width="750" height="440">
    <img src="./docs/mfi1.png" width="750" height="440">

    There has not been a significant change to MFI, except that is provided in a dynamically normalized version.
    </Details>

  * <Details> 
    <Summary><b><i> WOI (Weighted Order Imbalance) </b></i></Summary>
    This is an technical experiment
    </Details>

  * <Details> 
    <Summary><b><i> NES (Net Execution Strength) </b></i></Summary>
    This is an technical experiment
    </Details>

  * <Details> 
    <Summary><b><i> PIP (Potential Investment Plan) </b></i></Summary>
    <img src="./docs/pip0.png" width="750" height="440">
    <img src="./docs/pip1.png" width="750" height="440">

    This is the central hub of all the indicators in which the currency analysis finally generates any interpretable output.
    </Details>

  </Defails>

* <Details>
  <Summary><b><i> Trade Control Configuration </b></i></Summary>
  <img src="./docs/tradecontrol.png" width="750" height="440">

  Trade Control is a process in which generated analysis outputs from the currency analysis are converted into trade orders under a pre-defined scenarios and rules.


  * <Details> 
    <Summary><b><i> TS (Trading Scenario) </b></i></Summary>

    This is a very primitive type of trade control method. Its idea is extremely simple. The user configures each step of a trade cycle (from position enterance to exit). 
    </Details>

  * <Details> 
    <Summary><b><i> RQPM (Remaining Quantity Percentage Map) </b></i></Summary>
    
    This is a more advanced model of Trading Scenario. Its fundamental idea is the same. 


    </Details>

  </Defails>

* <Details>
  <Summary><b><i> Account Control Configuration </b></i></Summary>
  <img src="./docs/accountcontrol.png" width="750" height="440">

  By setting the four major parameters below, the user can proportionalize their investment portfolio.
  * [Asset] Allocation Ratio - This variable determines the amount of asset balance to use for trading.
  * [Position] Assumed Ratio - This variable determines the amount of asset balance to use for the specific position.
  * [Position] Priority - This variable determines which position to prioritize, when the amount of remaining asset balance is not enough to provide for all of the positions. (This occurs when the sum of Assumed Ratio exceeds 100%).
  * [Position] Maximum Allocated Balance - This variable determines the maximum amount of asset balance to allocate for a specific position.

  </Defails>

---

### ⚠️ Warning (VERY IMPORTANT)



* Even though real Binance account connection and trading is possible, this application **DOES NOT** guarantee profits. 
* WebSocket connection can be unstable during highly volatile market. 
* Occasional PIP (Potential Investment Plan) signal loss may be found in real-time trading. When that happens on the symbol that is being traded, I highly recommend re-starting the application.
* The trading strategy `Trade Scenario (TS)` is incomplete. The developer sadly could not find any way to use this strategy to generate stable profit and decided to leave it there for now and move on 😢 for now. Trying to use it **WILL** crash the application. **DO NOT USE IT**.

I myself have been running the application 24/7 with occasional application restarts for about three months since August 24th, and have not experienced any major issues trading with the trading strategy `Remaining Quantity Percentage Map (RQPM)`. If you ever happen to be interesed to try, you could configure a strategy and invest just a **TINY** bit amount of money for fun.

---

### 🤝 Credits
* **[python-binance](https://github.com/sammchardy/python-binance)** by *sammchardy* (MIT License)  
  - This project includes a modified version of `python-binance`. An option to disable the first kline search within the `futures_historical_klines` function in `client.py` module was added. 

---

### 🗓️ Project Duration
* September 2024 – November 2025

---

### 📄 Document Info
* **Last Updated:** December 16th, 2025  
* **Author:** Bumsu Kim
* **Email:**  kimlvis31@gmail.com
