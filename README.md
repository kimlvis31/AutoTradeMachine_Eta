# AutoTradeMachine_Eta



![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![TimescaleDB](https://img.shields.io/badge/Database-TimescaleDB-FDB515?style=flat-square&logo=timescale&logoColor=black)
![SQLite3](https://img.shields.io/badge/Database-SQLite3-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Pyglet](https://img.shields.io/badge/GUI-Pyglet-FF6F00?style=flat-square&logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/Numpy-013243?style=flat-square&logo=numpy&logoColor=white)
![Binance](https://img.shields.io/badge/API-Binance-FCD535?style=flat-square&logo=binance&logoColor=yellow)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-blue?style=flat-square)

[![korean-readme](https://img.shields.io/badge/Language-한국어-blue.svg)](./README.ko.md)



---



### 📖 Project Introduction ###

**Auto Trade Machine Eta (ATM-Eta)** is an end-to-end cryptocurrency trading platform that unifies multi-timeframe market analysis and live trade automation in a single application. It is designed to close the gap between strategy research and live deployment — users can develop, validate, and operate trading strategies without leaving the application or switching environments.

#### Core Capabilities
* **Real-time Market Data Pipeline** — Upon launch, the system automatically connects to the Binance Futures exchange and continuously ingests klines, orderbook snapshots, and trade executions. The collected data is aggregated and persisted into a local TimescaleDB-backed PostgreSQL server, providing low-latency access for both online analysis and offline backtesting.
* **Custom Analysis Toolkit** — Beyond standard indicators (MA, PSAR, Bollinger Bands), ATM-Eta provides 7 hybrid analysis tools — **IVP**, **MMACD**, **DMIxADX**, **MFI**, **TPD**, **WOI**, and **NES** — that integrate price, volume, orderbook, and trade execution data into a unified set of signals consumable by the trade controller.
* **TEF-Based Strategy Formalization** — Trade strategies are expressed through a single normalized scalar called **TEF (Target Exposure Factor)**, ranging from `-1.0` to `+1.0`. The sign indicates direction (negative = SHORT, positive = LONG) and the magnitude indicates target position size relative to the allocated balance. By collapsing direction and sizing into a single bounded value, TEF allows arbitrarily complex analytical logic to be packaged into a clean, standardized strategy interface.
* **External GPU-Accelerated Optimization** — Analysis data exported from ATM-Eta can be fed into the companion application **TEFFP Seeker**, a GPU-accelerated backtesting engine that runs massive parameter sweeps against user-defined trade strategies in parallel, helping users converge on optimal parameter sets that would be impractical to search on CPU.
* **Neural Network Integration (Experimental)** — Users can design, train, and deploy custom **MLP (Multi-Layer Perceptron)** models against historical market data. Trained models can be plugged into analyzers or simulators as auxiliary signal sources. Currently only MLP architectures are supported.
* **Process-Isolated Architecture** — The application consists of 9+ processes (Main, GUI, BinanceAPI, DataManager, TradeManager, SimulationManager, Analyzers, Simulators, NeuralNetwork) connected via a custom IPC module. GUI rendering, data ingestion, analysis, simulation, and live execution operate independently and never block each other.

The platform is built around a **'Build → Test → Execute'** workflow, allowing a strategy to move from backtest validation to live deployment without code rewrites or environment changes.

---



### 🔬 Live Stability Test ###

To validate the end-to-end system over an extended period, I deployed the application against my own Binance Futures account for approximately four months. The chart below shows the actual balance history:

<img src="./docs/balancehistory_myaccount.png" width="800">

| Item | Detail |
| :--- | :--- |
| **Trading Duration** | August 24, 2025 ~ December 20, 2025 (~118 days) |
| **Traded Pairs** | `BTCUSDT`, `ETHUSDT`, `XRPUSDT` on Binance Futures |
| **Strategy Origin** | Parameters tuned on 5 years of historical data prior to deployment |
| **Backtest Projection** | ~150x growth with ~35% maximum drawdown |
| **Initial Balance** | $4,718.55 |
| **Minimum Balance** | $4,022.05 (−14.76%) |
| **Maximum Balance** | $6,603.11 (+39.94%) |
| **Final Balance** | $5,640.23 (+19.53%) |

**On the backtest projection.** The 150x figure is almost certainly an inflated result of parameter overfitting against historical data, and I do not treat it as a realistic forward-looking expectation. I deployed the strategy regardless because the goal of this run was **not to generate profit, but to validate that the full pipeline could operate continuously and correctly against a live exchange**.

**What the run actually validated.** Over the 118-day period, the system handled all order executions reliably, maintained position and balance synchronization with the exchange, and recovered automatically from network disconnects, API rate limit events, and data stream interruptions without manual intervention. I considered this a sufficient outcome for a stability validation run rather than a profit demonstration. The realized maximum drawdown stayed well within the backtest's projected level (~35%), and the realized return likewise exceeded the backtest's projection. That said, this is more likely attributable to favorable market conditions during the deployment window than to any inherent strength of the strategy itself.

> ⚠️ **Disclaimer** — This application **does not guarantee profit**. It only serves as a platform on which users can build and operate their own strategies. Past performance, whether from backtests or live runs, is not indicative of future results. Cryptocurrency derivatives trading carries substantial risk of loss.



---



### ▶️ How To Run ###
Before running the application, **Docker** must be installed and running on your system. The application will automatically pull and configure a PostgreSQL (TimescaleDB) server container on first launch.

#### Windows 🪟
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and ensure it is running.
2. Run `setup.bat` in the root directory. This will setup `.venv` and install any necessary libraries for this application.
3. Run `run.bat` in the root directory. This will start the application.

#### Linux 🐧
1. Install [Docker Engine](https://docs.docker.com/engine/install/) and ensure the Docker daemon is active (`sudo systemctl start docker`).
2. Execute the command `chmod +x setup.sh run.sh` in the terminal.
3. Run `setup.sh` in the root directory. This will setup `.venv` and install any necessary libraries for this application.
4. Run `run.sh` in the root directory. This will start the application.



---



### ✅ Requirements ###
* **Operating System**: Windows 10/11 or Linux
* **Python**:           Version `3.11` or higher
* **CPU**:              Minimum 8-core CPU
* **RAM**:              16GB or more
* **Storage**:          10GB or more



---



### 🧱 System Architecture ###
ATM-Eta is built as a multi-process system in which each major responsibility runs in its own isolated process. Real-time market data ingestion, GUI rendering, analysis, simulation, and live trade execution all operate concurrently and never block each other. The diagram below illustrates the overall structure, including external inputs, internal processes, persistent storage, and the connection point to the companion application **TEFFP Seeker**.

<img src="./docs/applicationArchitecture.png" width="1200">

All processes communicate with each other via the `IPCAssistant` class defined in the `atmEta_IPC.py` module, which provides a unified message-passing interface across the application.

> **Note on the diagram:** A top-level **Main Process** orchestrates the application lifecycle — spawning all manager processes, assessing system resources, and coordinating graceful shutdown. It is omitted from the diagram above to keep the focus on runtime data flow.

#### Process Responsibilities

| Process                | Responsibilities |
| :---:                  | :--- |
| **Main**                   | Initializes the application, assesses system resources, determines the number of worker processes (Analyzers/Simulators), and orchestrates the startup sequence |
| **GUI Manager**            | Manages graphics, audio resources, and user interaction objects. Acts as the central hub bridging the user interface with the backend logic |
| **Binance API Manager**    | Serves as the gateway for exchange interactions, handling real-time market data ingestion, API rate-limit enforcement, and order execution |
| **Data Manager**           | Centralized storage engine for local market data, account info, and simulation records. Provides unified CRUD operations for other manager processes |
| **Trade Manager**          | The core orchestration unit for trading operations. Manages account connections, strategy configurations, logic determination, and delegates tasks to Analyzers |
| **Analyzer**               | Executes real-time market analysis tasks as assigned by the **Trade Manager** |
| **Simulation Manager**     | Oversees the lifecycle of simulation sessions and manages historical simulation data |
| **Simulator**              | Performs simulation (backtesting) tasks as assigned by the **Simulation Manager** |
| **Neural Network Manager** | Enables users to configure, train, and deploy models on historical data. Trained models can later be imported by **Analyzers** or **Simulators** to generate auxiliary reference signals |

#### Worker Process Allocation

The number of **Analyzer** and **Simulator** worker processes is configured by the user in the `programConfig.config` file via the `nAnalyzers` and `nSimulators` parameters. The application then bounds these values by the number of available CPU cores at runtime, ensuring that the configured worker count never exceeds what the host machine can sustain.

The actual number of workers spawned is determined by the following logic:

$$n_{rem} = \max(N_{CPU} - N_{managers} - 2,\ 0)$$

$$n_{Analyzers} = 1 + \min(n_{rem},\ \texttt{nAnalyzers} - 1)$$

$$n_{Simulators} = 1 + \min(n_{rem} - (n_{Analyzers} - 1),\ \texttt{nSimulators} - 1)$$

Where $N_{CPU}$ is the number of CPU cores available on the host machine, and $N_{managers}$ is the number of manager processes. The `-2` accounts for headroom reserved for the Main Process and OS-level operations.

This allocation policy guarantees that **at least one Analyzer and one Simulator are always spawned**, regardless of the configured values, while preventing oversubscription on resource-constrained systems. When CPU capacity is insufficient, Analyzers are prioritized over Simulators, since real-time analysis is critical for live trading whereas simulation is an offline activity.

> **Note:** The Neural Network module is experimental, designed to explore the potential of ML-based market analysis. Currently only MLP architectures are supported.



---



### 📥 Market Data Pipeline ###

The diagram below is a simplified view of ATM-Eta's market data pipeline, illustrating how data flows from external Binance services through the Binance API Manager and Data Manager, into the database server, and finally into the data consumers. The full implementation contains additional bookkeeping and error-handling paths that are intentionally abstracted out here to keep the structural intent visible.

<img src="./docs/marketDataPipeline.png" width="1200">

The pipeline is structured around several design decisions made specifically to minimize network footprint, storage cost, and downstream complexity, while preserving the flexibility required for both live trading and backtesting.
  
<br>
   
#### Single Base Interval, On-Demand Aggregation

Across the entire pipeline, all market data is collected, processed, and persisted at a **1-minute base interval**. Higher timeframes (5m, 15m, 1h, 4h, ..., up to 1M) are **not stored separately**; instead, they are derived **on-demand** by the Secondary Aggregator inside each Data Requester whenever a task actually needs them.

This approach offers two key advantages:

* **Network Footprint** — Only a single 1m stream subscription per symbol is required, regardless of how many timeframes downstream tasks demand. A naive design subscribing to each timeframe independently would multiply WebSocket load by the number of active timeframes.
* **Storage Efficiency & DB Simplicity** — Storing only the 1m base data minimizes the physical storage footprint. More importantly, this drastically simplifies the database architecture and ingestion logic. The system only needs to maintain a single dataset per symbol, eliminating the complexity and overhead of synchronizing inserts across multiple timeframe-specific tables

<br>

#### Heterogeneous Stream Unification

Binance Futures exposes three distinct market data streams — `kline`, `aggTrade`, and `depth` — each with their own unique data structure. While `kline` already arrives at fixed 1m boundaries, `aggTrade` and `depth` streams are event-driven, generating high-frequency data volumes that are impractical to persist as-is.

To unify these heterogeneous streams under the same 1m-base structure, both `aggTrade` and `depth` are **temporally aggregated within the Primary Aggregator** before they leave the Binance API Manager:

* `aggTrade` events within the same 1m window are accumulated into per-minute volume and directional pressure summaries.
* `depth` snapshots are processed by retaining only the final snapshot of the corresponding 1m interval.

This produces two compounding benefits. First, the data volume reduction is substantial — multiple orders of magnitude in the case of `aggTrade` and `depth`. Second, all three data types can be processed using structurally identical stream and fetch handling methods, minimizing the need for type-specific branching.

<br>

#### Stream Continuity Guarantee

The Stream Receiver continuously monitors incoming WebSocket data for temporal gaps caused by network disconnects, rate-limit throttling, or exchange-side stream interruptions. When a gap is detected, the missing temporal range is immediately filled with dummy data. From the perspective of downstream consumers, this removes the need for complex gap-recovery logic; they simply need to handle the injected dummy data entries appropriately.

> Detailed recovery schemes are described in the [Resilience & Recovery](#-resilience--recovery) section.

<br>

#### Distributed Sub-Pipelines per Data Requester

Each Data Requester (Analyzer, Simulator, GUI, Trade Manager) maintains its **own self-contained sub-pipeline** —  an Aggregated Base Stream Receiver, an Internal Fetch Request Generator, a Secondary Aggregator, and a Task Handler — rather than depending on a centralized aggregation service inside the Data Manager. This decision is intentional and addresses three concerns:

* **Heterogeneous Timeframe Needs** — Different requesters need different timeframes simultaneously. An Analyzer monitoring 5m may run concurrently with a Simulator backtesting on 4h. Centralized aggregation would force the Data Manager to maintain N parallel timeframe pipelines per symbol per consumer, with significant coordination overhead.
* **Minimal Data Manager Responsibility** — By keeping aggregation on the consumer side, the Data Manager's responsibility stays focused on three things: persistence, range comparison, and fetch coordination. Task-specific timeframe logic lives where it belongs — next to the task itself.
* **Independent lifecycle** — A failing or restarting Data Requester does not affect any other Requester's pipeline, since each maintains its own state.

<br>

#### Buffered Persistence and TimescaleDB

The Data Manager accumulates incoming data in memory and flushes it to the database in batches. This approach reduces per-transaction overhead and smooths out sudden bursts of data.

For persistent storage, the system utilizes **TimescaleDB**, a time-series extension for PostgreSQL. The primary advantage of this choice is its native time-based compression, which substantially reduces storage costs. In my live deployment, ~98 GB of raw market data was compressed down to ~21 GB (a ~78% reduction).

<br>

#### ⚠️ A Note on Storage Hardware

Selecting **TimescaleDB** is not the end of the storage decision. The **physical drive that hosts the PostgreSQL data directory** also matters, and this point is worth flagging because it is easy to overlook until things start failing in subtle ways.

Database workloads — and PostgreSQL in particular — generate sustained random I/O patterns from B-tree index updates and concurrent transactions. Modern consumer HDDs increasingly ship as **SMR (Shingled Magnetic Recording)** drives, whose track layout is fundamentally optimized for sequential writes. On SMR drives, random writes trigger expensive read-modify-write cycles inside the firmware. Under sustained database load, this typically manifests as a deferred failure: the system operates normally during initial data accumulation, but once the drive's cache is exhausted, I/O processing speeds drop drastically. This extreme latency causes internal data queues to bottleneck and skip, ultimately throwing index corruption errors — symptoms that look like application-side bugs but are actually rooted in the physical storage layer.

For ATM-Eta deployments handling continuous market data ingestion, I strongly recommend hosting the PostgreSQL data directory on either a **CMR (Conventional Magnetic Recording) HDD** or, preferably, an **SSD**.

---



### 🛡️ Resilience & Recovery ###



---



### 📊 Multi-timeframe Analysis ###



---



### 🧠 Trade Logic Pipeline ### 
<img src="./docs/tradestrategy_0.png">

A trade strategy in this application refers to a set of three processes - currency analysis, trade control, and account control. Starting from raw market data, each of these processes uses a pre-defined model and configuration to eventually generate order requests that are sent to the exchange server to be executed.

* <Details>
  <Summary><b><i> Currency Analysis Configuration </b></i></Summary>

  Beyond standard technical analysis tools such as MAs, PSAR, and Bollinger Bands, this module incorporates 6 hybrid analysis tools designed for enhanced signal clarity.  

  These individual signals are aggregated and interpreted by the PIP (Potential Investment Plan) tool. PIP acts as a high-level signal aggregator, uniquely designed to interpret and translate raw analytical data.  

  The resulting PIP signal is then captured by the **Trade Control** process to generate actionable execution signals.

  * <Details> 
    <Summary><b><i> IVP (Interpreted Volume Profile) </b></i></Summary>

    The **IVP** module is conceptually based on the widely used **VPVR (Volume Profile Visible Range)** indicator. It aggregates trading volumes across specific price levels to construct a comprehensive volume profile. This raw data is then processed through a filtering algorithm to eliminate noise and pinpoint key structural price levels.

    <img src="./docs/ivp0.png" width="750">

    The table below outlines the configuration parameters for IVP.  
    | Parameter    | Description |
    | :--- | :---  |
    | Interval     | Defines the minimum number of samples required to construct the initial volume profile. Note that data points older than this threshold are **retained** (not excluded), allowing for a cumulative profile |
    | Gamma Factor | Controls the granularity (vertical division height) of the volume profile buckets |
    | Delta Factor | Determines the intensity of the noise filtering |
    <br>

    <img src="./docs/ivp1.png" width="750">

    The image above illustrates the filtered volume profile (**VPLP**) on the right, alongside the identified major support and resistance lines (**VPLPB**).

    </Details>

  * <Details> 
    <Summary><b><i> MMACD (Multi Moving Average Convergence and Divergence) </b></i></Summary>
    
    As the name implies, **MMACD** is an expansion of the standard MACD (Moving Average Convergence Divergence) indicator. Unlike the traditional MACD, which tracks the relationship between just two moving averages, MMACD expands this capability to monitor relationships among up to 6 distinct moving averages.

    Furthermore, MMACD incorporates an experimental feature known as **Kline Interval Multiplication**. This allows the system to simulate analysis on higher timeframes without switching the underlying data stream. For example, setting the multiplier to `4` while running on a `15m` domain effectively simulates analysis on a `1h` (15m × 4) timeframe. To leverage this multi-timeframe capability, the system employs two distinct instances: **MMACDSHORT** and **MMACDLONG**.

    <img src="./docs/mmacd0.png" width="750">

    The table below outlines the configuration parameters for MMACD.  
    | Parameter       | Description |
    | :---            | :--- |
    | Signal Interval | The sampling period for the signal line calculation |
    | Multiplier      | The time-domain multiplication factor. Used to simulate higher timeframe analysis (e.g., 4x multiplier on 15m data ≈ 1h data) |
    | MA Interval     | The base interval for the moving averages |
    <br>

    <img src="./docs/mmacd1.png" width="750">

    The image above demonstrates the actual chart data of the MMACD analysis.

    </Details>

  * <Details> 
    <Summary><b><i> DMIxADX (Directional Movement Index and Average Directional Index) </b></i></Summary>
    
    This hybrid indicator integrates two standard technical analysis tools:  
    **DMI (Directional Movement Index):** Identifies the direction of the market trend (Bullish/Bearish).  
    **ADX (Average Directional Index):** Identifies the strength of the trend, regardless of its direction.  
    By combining these complementary indicators, the system can assess both the direction and the intensity of market movements.
    
    **ATH (All-Time-High) Relative Representation**  
    Raw values from these indicators can vary significantly, making them ambiguous for automated systems to interpret. To address this, this application adopts an **ATH Relative Representation**. By normalizing the output against its historical maximum value, the indicator provides a standardized and interpretable strength metric, ensuring consistency across different assets and timeframes.

    <img src="./docs/dmixadx0.png" width="750">

    The table below outlines the configuration parameters for DMIxADX.  
    | Parameter | Description |
    | :---      | :--- |
    | Interval  | The number of samples for the signal |
    <br>

    <img src="./docs/dmixadx1.png" width="750">

    The image above demonstrates the actual chart data of the DMIxADX analysis.

    </Details>

  * <Details> 
    <Summary><b><i> MFI (Money Flow Index) </b></i></Summary>

    The **MFI (Money Flow Index)** is a momentum oscillator designed to measure buying and selling pressure by integrating price and volume data. Similar to the **DMIxADX** module, this tool adopts the **ATH (All-Time-High) Relative Representation** technique. By normalizing the output against historical maximums, it provides a standardized metric that is easier for the automated system to interpret.

    <img src="./docs/mfi0.png" width="750">

    The table below outlines the configuration parameters for MFI.  
    | Parameter | Description |
    | :---:     | :--- |
    | Interval  | The number of samples for the signal |
    <br>

    <img src="./docs/mfi1.png" width="750">

    The image above demonstrates the actual chart data of the MFI analysis.

    </Details>

  * <Details> 
    <Summary><b><i> WOI (Weighted Order Imbalance) </b></i></Summary>
    
    The **WOI (Weighted Order Imbalance)** is an orderbook-based indicator, designed to quantify the disparity between average buying and selling pressure.

     **Gaussian Filtering**
    Since raw high-frequency orderbook data is inherently noise-heavy, the output is aggregated over the same **temporal interval** as the active candlestick. Then, **Gaussian Filtering** is applied to smooth out micro-fluctuations, generating a cleaner trend signal.
    
    
    The table below outlines the configuration parameters for WOI.  
    | Parameter | Description |
    | :---:     | :--- |
    | Interval  | Number of samples (interval block) for the Gaussian Filter |
    | Sigma     | Determines the standard deviation of the Gaussian Filter |
    <br>

    > **Note:** This analysis tool is an experimental approach to integrating Level 2 (Orderbook) data into the currency analysis process.

    </Details>

  * <Details> 
    <Summary><b><i> NES (Net Execution Strength) </b></i></Summary>
    
    The **NES (Net Execution Strength)** is a volume-based indicator derived from real-time trade execution data (`aggTrades`). Unlike orderbook metrics which represent intent, NES quantifies the **actual executed buying and selling momentum**.

    **Gaussian Filtering**
    Similar to the **WOI** indicator, raw execution data is aggregated and processed using **Gaussian Filtering**. This technique smoothens high-frequency trade noise to generate a coherent and interpretable trend signal.
    
    The table below outlines the configuration parameters for NES.  
    | Parameter | Description |
    | :---:     | :--- |
    | Interval  | Number of samples (interval block) for the Gaussian Filter |
    | Sigma     | Determines the standard deviation of the Gaussian Filter |
    <br>

    > **Note:** This analysis tool is an experimental approach to integrating trade execution data into the currency analysis process.

    </Details>

  

  </Details>

* <Details>
  <Summary><b><i> Trade Control Configuration </b></i></Summary>
  <img src="./docs/tradecontrol.png" width="750" height="440">

  The **Trade Control** process generates potential trade orders based on PIP signals derived from currency analysis. It operates by identifying the current position within the trade cycle and applying corresponding pre-determined reaction models.

  Currently, two trade control methods are implemented: **TS (Trading Scenario)** and **RQPM (Remaining Quantity Percentage Map)**.

  </Details>

* <Details>
  <Summary><b><i> Account Control Configuration </b></i></Summary>
  <img src="./docs/accountcontrol.png" width="750" height="440">

  Account Control achieves portfolio risk management and capital distribution by defining the four parameters below.

  | Parameter                 | Target   | Description |
  | :---:                     | :---:    | :--- |
  | Allocation Ratio          | Asset    | Determines the percentage of the total *Available Balance* to be utilized for trading activities |
  | Assumed Ratio             | Position | Determines the percentage of the *Asset Allocated Balance* assigned to a specific position |
  | Priority                  | Position | Defines the funding order. If the sum of all Assumed Ratios exceeds 100%, positions with higher priority (1 being the highest priority) are funded first |
  | Maximum Allocated Balance | Position | A hard cap limiting the maximum capital allocated to a specific position |
  <br>
  $$\text{Asset Allocated Balance} = \text{Available Balance} \times \color{orange}{\text{Allocation Ratio}}$$
  $$\text{Position Allocated Balance} = \min(\text{Asset Allocated Balance} \times \color{orange}{\text{Assumed Ratio}}, \color{orange}{\text{Maximum Allocated Balance}})$$
  <br>
  </Details>











---



### 👀 Application Preview & How To Use ###
* <Details>
  <Summary><b><i> Pages </b></i></Summary>

  * <Details> 
      <Summary><b><i> Dashboard </b></i></Summary>
      <img src="./docs/dashboard_0.png" width="960" height="540">
      The central hub for navigation and application control.

      1\. Navigate to other pages.  
      2\. Terminate the application.  
    </Details>

  * <Details> 
      <Summary><b><i> Accounts </b></i></Summary>
      <img src="./docs/accounts_0.png" width="960" height="540">
      Manage virtual and actual trading accounts.

      1\. Create local virtual account instances.  
      2\. Create local actual account instances and synchronize with Binance.  
      3\. Monitor assets and positions status.  
      4\. Configure trade settings for assets and positions.  
    </Details>

  * <Details> 
      <Summary><b><i> AutoTrade </b></i></Summary>
      <img src="./docs/autotrade_0.png" width="960" height="540">
      Configure automated analysis and trading strategies.
      
      1\. Monitor Analyzers status.  
      2\. Create Currency Analysis Configurations (CAC).  
      3\. Initialize currency analysis by selecting a CAC and a target currency.  
      4\. View the list and status of active currency analyses.  
      5\. Create Trade Configurations (TC).  
    </Details>

  * <Details> 
      <Summary><b><i> Currency Analysis </b></i></Summary>
      <img src="./docs/currencyanalysis_0.png" width="960" height="540">
        
      Monitor the registered Currency Analyses.

      1\. Select a currency analysis instance to view the chart.  
      2\. Inspect the CAC applied to the selected analysis.  
    </Details>

  * <Details> 
      <Summary><b><i> Account History </b></i></Summary>
      <img src="./docs/accounthistory_0.png" width="960" height="540">
      Review historical performance and logs.

      1\. View trade logs and balance history for actual/virtual accounts.
    </Details>

  * <Details> 
      <Summary><b><i> Market </b></i></Summary>
      <img src="./docs/market_0.png" width="960" height="540">
      Real-time market monitoring.

      1\. View the list of current market positions.  
      2\. Access position charts.  
      3\. Perform temporary currency analysis on a specific time window.  
    </Details>

  * <Details> 
      <Summary><b><i> Simulation </b></i></Summary>
      <img src="./docs/simulation_0.png" width="960" height="540">
      Run backtests to verify the performances of customized trade strategies.

      1\. View the list of completed and processing simulations.  
      2\. Import trade configurations from existing simulations.  
      3\. Backtest specific strategies, variables, and ranges on target positions.  
    </Details>

  * <Details> 
      <Summary><b><i> Simulation Result </b></i></Summary>
      <img src="./docs/simulationresult_0.png" width="960" height="540">
      Analyze simulation results.
      
      1\. View completed simulations and result summaries.  
      2\. Inspect account balance history.  
      3\. Review simulation setups (positions, CAC, TC).  
      4\. View detailed trade logs.  
      5\. Reconstruct currency analysis charts for a detailed inspection.  
    </Details>

  * <Details> 
      <Summary><b><i> Database </b></i></Summary>
      <img src="./docs/database_0.png" width="960" height="540">
      Run backtests to verify the performances of customized trade strategies.

      1\. View the list of completed and processing simulations.  
      2\. Import trade configurations from existing simulations.  
      3\. Backtest specific strategies, variables, and ranges on target positions.  
    </Details>

  * <Details> 
      <Summary><b><i> Neural Network </b></i></Summary>
      <img src="./docs/neuralnetwork_0.png" width="960" height="540">
      Design and train Machine Learning models.

      1\. Design custom Multi-Layer Perceptron (MLP) models.  
      2\. Train models using historical market data.  
      3\. Analyze training performance and results.  
    </Details>

  * <Details> 
      <Summary><b><i> Settings </b></i></Summary>
      <img src="./docs/settings_0.png" width="960" height="540">
      Configure application preferences.

      1\. Change language.  
      2\. Switch GUI theme (Light/Dark Mode).  
      3\. Toggle fullscreen mode.  
      4\. Manage audio settings.  
      5\. Set the terminal log display level.  
    </Details>
  </Details>

* <Details>
  <Summary><b><i> Features </b></i></Summary>

  * <Details>
    <Summary><b><i> Viewing Market & Performing Temporary Currency Analysis </b></i></Summary>

      1\. Navigate to the **Market** page.
      <img src="./docs/feat1_1.png">
      <br>

      2\. Select a target position.  
      3\. Click the settings button on the chart drawer.
      <img src="./docs/feat1_2.png"> 
      <br>

      4\. Configure currency analysis parameters.
      <img src="./docs/feat1_3.png"> 
      <br>

      5\. Set the analysis range and start the analysis.
      <img src="./docs/feat1_4.png"> 
      <br>

      6\. View the analysis results.
      <img src="./docs/feat1_5.png">

    </Details>

  * <Details>
    <Summary><b><i> Adding a Currency Analysis </b></i></Summary>

      1\. Navigate to the **AutoTrade** page.
      <img src="./docs/feat2_1.png">
      <br>

      2\. Configure currency analysis parameters.  
      3\. Name the configuration (auto-generated if left blank)and click **ADD**.
      <img src="./docs/feat2_2.png">
      <br>

      4\. Select a target position from the market list.  
      5\. Select a CAC to apply, name the analysis instance (auto-generated if left blank)and click **ADD**.  
      <img src="./docs/feat2_3.png">
      <br>

      6\. Review the list of analysis instances. Click **VIEW CURRENCY ANALYSIS CHART** to open the chart.  
      <img src="./docs/feat2_4.png">
      <br>

      7\. Monitor the currency analysis.  
      <img src="./docs/feat2_5.png">
      <br>

    </Details>

  * <Details>
    <Summary><b><i> Adding a Trade Control Configuration </b></i></Summary>

      1\. Navigate to the **AutoTrade** page.  
      <img src="./docs/feat3_1.png">
      <br>

      2\. Configure trade control parameters.  
      3\. Name the configuration (auto-generated if left blank)and click **ADD**.  
      <img src="./docs/feat3_2.png">
      <br>

    </Details>

  * <Details>
    <Summary><b><i> Backtesting & Results </b></i></Summary>

      1\. Navigate to the **Simulation** page.  
      <img src="./docs/feat4_1.png">
      <br>

      2\. Set the simulation name (auto-generated if left blank) and range.  
      &nbsp; Once all the configurations are completed, click **ADD** (Once step 3 and 4 are done).  
      &nbsp; Once the simulation is completed, move to **SIMULATION RESULT** page either by clicking **VIEW RESULT** or navigating from **DASHBOARD**.  
      3\. Configure position-specific strategies (Currency Analysis, Trade Control, Account Control)  
      4\. Determine account-level parameters.  
      <img src="./docs/feat4_2.png">
      <br>

      5\. Select a simulation.  
      6\. View the simulation result summary.  
      7\. Inspect the simulation result details.  
      <img src="./docs/feat4_3.png">
      <br>

    </Details>

  * <Details>
    <Summary><b><i> Adding Accounts & Automated Trading </b></i></Summary>

      1\. Navigate to the **Accounts** page.  
      <img src="./docs/feat5_1.png">
      <br>

      2\. Enter account details and click **ADD ACCOUNT**.  
      &nbsp; [ACTUAL ONLY] Enter Binance User ID.  
      <img src="./docs/feat5_2.png">
      <br>

      3\. View the selected account's information.  
      &nbsp; [ACTUAL ONLY] Activate the account by entering your Binance API Key and Secret Key. This will synchronize the local account instance with the real account in Binance.  
      4\. Monitor asset information and position status.  
      5\. Monitor and configure trade strategies for specific positions.
      <img src="./docs/feat5_3.png">
      <br>

      6\. Navigate to the **Account History** page.  
      <img src="./docs/feat5_4.png">
      <br>

      7\. Select an account from the list.  
      8\. Toggle the view type to check either the balance history chart or trade logs.  
      <img src="./docs/feat5_5.png">
      <br>

    </Details>

  * <Details>
    <Summary><b><i> Creating and Training a Neural Network Model </b></i></Summary>

      1\. Navigate to the **Neural Network** page.  
      <img src="./docs/feat6_1.png">
      <br>

      2\. Configure model parameters: Name, Type, Control Key, and Initialization Method.   
      3\. Define the neural network structure (Layers/Nodes/Analysis References).  
      <img src="./docs/feat6_2.png">
      <br>

      4\. Select a model from the list.  
      5\. Visualize the network structure.  
      <img src="./docs/feat6_3.png">
      <br>

      6\. Select historical market data to train the model on, and set training parameters.  
      <img src="./docs/feat6_4.png">
      <br>

      7\. Monitor the training process.  
      8\. Review training results and performance metrics.  
      <img src="./docs/feat6_5.png">
      <br>

    </Details>

  </Details>
  
---



### 🤝 Credits
* **[python-binance](https://github.com/sammchardy/python-binance)** by *sammchardy* (MIT License)  
  - This project includes a modified version of `python-binance`. An option to disable the first kline search within the `futures_historical_klines` function in `client.py` module was added. 

---



### 🗓️ Project Duration
* September 2024 – May 2026



---



### 📄 Document Info
* **Last Updated:** May 6th, 2026  
* **Author:** Bumsu Kim
* **Email:**  kimlvis31@gmail.com
