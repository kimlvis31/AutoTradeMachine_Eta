# AutoTradeMachine_Eta



![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-blue?style=flat-square)
![LOC](https://img.shields.io/badge/LOC-~73K-success?style=flat-square)
![Modules](https://img.shields.io/badge/Modules-59-success?style=flat-square)
![Processes](https://img.shields.io/badge/Processes-9_concurrent-blueviolet?style=flat-square)
![TimescaleDB](https://img.shields.io/badge/TimescaleDB-FDB515?style=flat-square&logo=timescale&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![SQLite3](https://img.shields.io/badge/SQLite3-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Pyglet](https://img.shields.io/badge/GUI-Pyglet-FF6F00?style=flat-square&logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![Binance](https://img.shields.io/badge/API-Binance_Futures-FCD535?style=flat-square&logo=binance&logoColor=white)

[![korean-readme](https://img.shields.io/badge/Language-한국어-blue.svg)](./README.ko.md)



---



### 📖 Project Introduction ###

**Auto Trade Machine Eta (ATM-Eta)** is an end-to-end cryptocurrency trading platform that unifies multi-timeframe market analysis and live trade automation in a single application. It is designed to close the gap between strategy research and live deployment — users can develop, validate, and operate trading strategies without leaving the application or switching environments.

#### **Core Capabilities**
* **Real-time Market Data Pipeline** — Upon launch, the system automatically connects to the Binance Futures exchange and continuously ingests klines, orderbook snapshots, trade executions, and derivatives metrics (Open Interest, Long/Short Ratio). The collected data is aggregated and persisted into a local TimescaleDB-backed PostgreSQL server, providing low-latency access for both online analysis and offline backtesting.
* **Custom Analysis Toolkit** — Beyond standard indicators (MA, PSAR, Bollinger Bands), ATM-Eta provides a set of hybrid analysis modules that integrate price, volume, orderbook, and trade execution data into a unified set of signals consumable by TEF functions.
* **TEF-Based Strategy Formalization** — Trade strategies are expressed through a **TEF (Target Exposure Factor)**: a target direction (`LONG` / `SHORT` / none) paired with a bounded value in `[-1.0, +1.0]`, whose magnitude sets the target position size relative to the allocated balance. By collapsing a strategy's decision into a single normalized target, TEF allows arbitrarily complex analytical logic to be packaged into a clean, standardized strategy interface.
* **External GPU-Accelerated Optimization** — Analysis data exported from ATM-Eta can be fed into the companion application **TEFFP Seeker**, a GPU-accelerated backtesting engine that runs massive parameter sweeps against user-defined trade strategies in parallel, helping users converge on optimal parameter sets that would be impractical to search on CPU.
* **Neural Network Integration (Experimental)** — Users can design, train, and deploy custom **MLP (Multi-Layer Perceptron)** models against historical market data. Trained models can be plugged into analyzers or simulators as auxiliary signal sources. Currently only MLP architectures are supported.
* **Process-Isolated Architecture** — The application consists of 9+ processes (Main, GUI, BinanceAPI, DataManager, TradeManager, SimulationManager, Analyzers, Simulators, NeuralNetwork) connected via a custom IPC module. GUI rendering, data ingestion, analysis, simulation, and live execution operate independently and never block each other.

The platform is built around a **'Build → Test → Execute'** workflow, allowing a strategy to move from backtest validation to live deployment without code rewrites or environment changes.

---



### ▶️ How To Run ###
Before running the application, **Docker** must be installed and running on your system. The application will automatically pull and configure a PostgreSQL (TimescaleDB) server container on first launch.

#### **Windows** 🪟
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and ensure it is running.
2. Run `setup.bat` in the root directory. This will setup `.venv` and install any necessary libraries for this application.
3. Run `run.bat` in the root directory. This will start the application.

#### **Linux** 🐧
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

All processes communicate with each other via the `IPCAssistant` class defined in the `ipc.py` module, which provides a unified message-passing interface across the application.

> **Note on the diagram:** A top-level **Main Process** orchestrates the application lifecycle — spawning all manager processes, assessing system resources, and coordinating graceful shutdown. It is omitted from the diagram above to keep the focus on runtime data flow.

#### **Process Responsibilities**

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

#### **Worker Process Allocation**

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

<img src="./docs/marketdatapipeline.png" width="1200">

The pipeline is structured around several design decisions made specifically to minimize network footprint, storage cost, and downstream complexity, while preserving the flexibility required for both live trading and backtesting.
  
<br>
   
#### **Single Base Interval, On-Demand Aggregation**

Across the entire pipeline, all market data is collected, processed, and persisted at a **1-minute base interval**. Higher timeframes (5m, 15m, 1h, 4h, ..., up to 1M) are **not stored separately**; instead, they are derived **on-demand** by the Secondary Aggregator inside each Data Requester whenever a task actually needs them.

This approach offers two key advantages:

* **Network Footprint** — Each data type requires only a single 1m stream per symbol, regardless of how many timeframes downstream tasks demand. A naive design subscribing to each timeframe independently would multiply WebSocket load by the number of active timeframes.
* **Storage Efficiency & DB Simplicity** — Storing only the 1m base data minimizes the physical storage footprint. More importantly, this drastically simplifies the database architecture and ingestion logic. The system only needs to maintain a single dataset per symbol, eliminating the complexity and overhead of synchronizing inserts across multiple timeframe-specific tables.



<br>



#### **Heterogeneous Stream Unification**

ATM-Eta collects four types of market data, each with its own structure and delivery mechanism:

| Data Type | Source | Native Resolution |
| :--- | :--- | :--- |
| `kline` | WebSocket | Fixed 1m boundaries |
| `aggTrade` | WebSocket | Event-driven (per trade) |
| `depth` | WebSocket | Event-driven (orderbook diffs) |
| `metric` (Open Interest, Long/Short Ratio) | REST only | 5m |

To unify these under the same 1m-base structure, every non-kline type is converted inside the **Primary Aggregator** before it leaves the Binance API Manager:

* `aggTrade` events within the same 1m window are accumulated into buy/sell quantity, trade count, and notional summaries.
* `depth` diffs are applied to a locally maintained orderbook, which is sampled at most once per second into 12 notional bands: 6 bid and 6 ask bands at fixed distances from the mid price (0.2%, 1%, 2%, 3%, 4%, 5%). The last sample of each minute becomes that minute's record.
* `metric` values are polled via REST shortly after each 5m boundary and expanded into an internally generated 1m stream, so they flow through the same stream handling path as the WebSocket data.

This produces two compounding benefits. First, the data volume reduction is substantial — multiple orders of magnitude in the case of `aggTrade` and `depth`. Second, all four data types can be processed using structurally identical stream and fetch handling methods, minimizing the need for type-specific branching.



<br>



#### **Historical Backfill Sources**

Historical data is collected from two sources. **Binance Vision** daily archives are preferred for their volume, and the **REST API** covers the ranges not yet archived.

| Data Type | Binance Vision | REST | Otherwise |
| :--- | :--- | :--- | :--- |
| `kline` | ✅ | ✅ Any range | — |
| `depth` | ✅ (re-binned into the same 12 bands) | Current snapshot only | Dummy |
| `aggTrade` | ✅ | Live stream gaps only | Dummy |
| `metric` | ✅ | ✅ Last 28 days | Dummy |

Archive files are downloaded in parallel and verified against their SHA-256 checksums before use. Ranges that cannot be recovered from either source are recorded as dummy ranges and can be recovered later (see [Integrity & Recovery](#️-integrity--recovery)).



<br>



#### **Stream Continuity Guarantee**

The Stream Receiver continuously monitors incoming WebSocket data for temporal gaps caused by network disconnects, rate-limit throttling, or exchange-side stream interruptions. When a gap is detected, the missing range is fetched and merged back into the stream in order, and only ranges that cannot be recovered are filled with dummy data. From the perspective of downstream consumers, this removes the need for complex gap-recovery logic; they simply need to handle the injected dummy data entries appropriately.

> Detailed recovery schemes are described in the [Integrity & Recovery](#️-integrity--recovery) section.



<br>



#### **Distributed Sub-Pipelines per Data Requester**

Each Data Requester (Analyzer, Simulator, GUI, Trade Manager) maintains its **own self-contained sub-pipeline** —  an Aggregated Base Stream Receiver, an Internal Fetch Request Generator, a Secondary Aggregator, and a Task Handler — rather than depending on a centralized aggregation service inside the Data Manager. This decision is intentional and addresses three concerns:

* **Heterogeneous Timeframe Needs** — Different requesters need different timeframes simultaneously. An Analyzer monitoring 5m may run concurrently with a Simulator backtesting on 4h. Centralized aggregation would force the Data Manager to maintain N parallel timeframe pipelines per symbol per consumer, with significant coordination overhead.
* **Minimal Data Manager Responsibility** — By keeping aggregation on the consumer side, the Data Manager's responsibility stays focused on three things: persistence, range comparison, and fetch coordination. Task-specific timeframe logic lives where it belongs — next to the task itself.
* **Independent lifecycle** — A failing or restarting Data Requester does not affect any other Requester's pipeline, since each maintains its own state.



<br>



#### **Buffered Persistence and TimescaleDB**

The Data Manager accumulates incoming data in memory and flushes it to the database in batches: streamed data every 5 seconds, and fetched historical data in chunks of up to 10,000 rows. This approach reduces per-transaction overhead and smooths out sudden bursts of data.

For persistent storage, the system utilizes **TimescaleDB**, a time-series extension for PostgreSQL. The primary advantage of this choice is its native time-based compression, which substantially reduces storage costs. In my live deployment, ~98 GB of raw market data was compressed down to ~21 GB (a ~78% reduction).



<br>



#### ⚠️ **A Note on Storage Hardware**

Selecting **TimescaleDB** is not the end of the storage decision. The **physical drive that hosts the PostgreSQL data directory** also matters, and this point is worth flagging because it is easy to overlook until things start failing in subtle ways.

Database workloads — and PostgreSQL in particular — generate sustained random I/O patterns from B-tree index updates and concurrent transactions. Modern consumer HDDs increasingly ship as **SMR (Shingled Magnetic Recording)** drives, whose track layout is fundamentally optimized for sequential writes. On SMR drives, random writes trigger expensive read-modify-write cycles inside the firmware. Under sustained database load, this typically manifests as a deferred failure: the system operates normally during initial data accumulation, but once the drive's cache is exhausted, I/O processing speeds drop drastically. This extreme latency causes internal data queues to bottleneck and skip, ultimately throwing index corruption errors — symptoms that look like application-side bugs but are actually rooted in the physical storage layer.

For ATM-Eta deployments handling continuous market data ingestion, I strongly recommend hosting the PostgreSQL data directory on either a **CMR (Conventional Magnetic Recording) HDD** or, preferably, an **SSD**.

The Data Manager includes mitigations for this failure mode — it defers writes while the database is waiting on I/O and attempts an automatic `REINDEX` when index corruption is detected — but these only soften the symptoms. They do not replace appropriate storage hardware.

---



### 🛡️ Integrity & Recovery ###

#### **1. AAF (Account Activation File) System**

Activating an **ACTUAL** account requires a Binance API Key and Secret Key. Typing them in on every launch is tedious and error-prone, while keeping them in a plaintext config file exposes credentials that can place live orders. The **AAF (Account Activation File)** system resolves this trade-off: the keys are encrypted with a key derived from the account password and stored as a portable file, so an account can be reactivated with just the file and the password.

<br>

 🔹 **Generation**

1. The user enters the API Key, Secret Key, and account password on the **Accounts** page.
2. The password is first verified against the account's stored **bcrypt** hash by the Trade Manager. AAF generation proceeds only if verification succeeds.
3. A random 16-byte salt is generated, and a 32-byte encryption key is derived from the password using **scrypt** (`n = 2^17`, `r = 8`, `p = 1`).
4. Both keys are encrypted with **Fernet** (AES-128-CBC + HMAC-SHA256) and written to `data/{localID}.aaf` along with the KDF parameters. The key input fields are cleared immediately afterward.

```json
{
    "localID":              "<account local ID>",
    "generationTime_ns":    1758585600000000000,
    "scrypt_n":             131072,
    "scrypt_r":             8,
    "scrypt_p":             1,
    "salt_b64":             "<base64 salt>",
    "api_key_encrypted":    "<Fernet token>",
    "secret_key_encrypted": "<Fernet token>"
}
```

<br>

 🔹 **Activation**

1. When **ACTIVATE BY AAF** is pressed, the GUI scans the root directory of every mounted drive, as well as the project's `data/` folder, for `.aaf` files. Because removable drives are included in the scan, an AAF can be kept on a USB drive and plugged in only when activation is needed.
2. If multiple AAFs exist for the same account, the most recently generated one (by `generationTime_ns`) is selected.
3. The encrypted keys and KDF parameters are sent to the Trade Manager, which re-verifies the password, re-derives the key with the stored parameters, and decrypts the credentials **in memory only**.
4. The decrypted keys are passed to the Binance API Manager, which validates them against the exchange (Futures permission, Binance UID match) before the account is marked `ACTIVE`.

<br>

 🔹 **Security Properties**

* **No plaintext at rest** — API credentials are never written to disk unencrypted. They exist in plaintext only in process memory during activation.
* **Brute-force resistance** — scrypt's memory-hard key derivation (~128 MB per attempt at the configured parameters) makes offline password guessing against a leaked AAF expensive.
* **Tamper detection** — Fernet authenticates every token, so a modified or corrupted AAF fails decryption instead of producing garbage credentials.
* **Credential–account binding** — Even with a valid AAF, activation fails if the keys belong to a different Binance account than the one registered (`UIDMISMATCH`).



<br><br><br>



#### **2. Account Exchange State Reconciliation**

The account model held by the Trade Manager and the actual account state on Binance can drift apart for several reasons: orders left over from a previous session, fills that show up before their order responses arrive, trades placed manually by the user, or requests whose outcome is lost to a network error. ATM-Eta treats the exchange as the single source of truth and reconciles against it at three points: on activation, on every account snapshot, and per order.

<br>

 🔹 **On Activation**

* Before an account is marked `ACTIVE`, the Binance API Manager fetches all open orders and cancels those whose `clientOrderId` starts with `ATMETA`, the prefix carried by every order ATM-Eta places. Orders from a previous session are no longer tracked, so leaving them on the book risks fills the system cannot account for. Orders placed manually by the user are left untouched.
* An order that is already gone (`-2011`) counts as cleared. Any other cancellation failure aborts the activation (`OPENORDERCLEARFAILED`) rather than starting from an unknown state.
* Tracking state from the previous session is discarded on both sides: the Binance API Manager drops its order trackers, and the Trade Manager clears in-flight order requests and pending trade handlers.
* The same cleanup runs on deactivation on a best-effort basis. If it fails, it is retried at the next activation.

<br>

 🔹 **Snapshot Synchronization**

* Account snapshots are read via REST at an adaptive interval (see [API Rate-Limit Handling](#api-rate-limit-handling)), with an immediate read right after activation.
* Margin, unrealized PNL, leverage, and margin type are always overwritten with exchange values. Position quantity and entry price are overwritten only when no order is in flight. Otherwise, the quantity change must be explained first:
  * A change matching the in-flight order's reported fills is recorded as that order's trade.
  * A change that fits within a live order's outstanding quantity, but whose order response has not yet arrived, is held and attributed once the response arrives.
  * Anything left over is treated as an **Unknown Trade**. It is logged as `UNKNOWN`, the trade control state is reset, and, if *Stop Trade On Unknown Trade* is enabled (default), trading on the position is halted (manual intervention or liquidation is assumed).
* Other forms of drift make a position non-tradable until resolved:
  * Open-order margin that persists for more than 20 seconds with no ATM-Eta order in flight indicates an externally placed order.
  * Leverage or margin type that differs from the trade configuration. A correction request is sent automatically once the position is flat with no open orders.
* After a restart, allocated balances are restored for open positions and scaled down proportionally if their total exceeds the allocatable balance.

<br>

 🔹 **Order State Verification**

| Situation | Handling |
| :--- | :--- |
| Definite rejection | Reported as a failure. The Trade Manager may regenerate the order (up to 5 attempts) |
| Ambiguous result (timeout, network error, server-side errors `-1000`/`-1001`/`-1006`/`-1007`/`-1008`, unparseable response) | Registered as *unconfirmed* and queried by `clientOrderId` every second. No blind retry |
| Unconfirmed order found on the server | Confirmed and tracked normally |
| Unconfirmed order never found (600 consecutive checks, ~10 minutes) | Reported as `NOTPLACED`. Safe to regenerate |
| Previously confirmed order vanishes, or checks keep failing | Reported as `ORDERSTATEUNKNOWN`. Terminated **without** regeneration, manual check advised |
| Cancellation rejected because the order is no longer on the book (`-2011`) | Final order state is fetched, so fills that happened just before cancellation are still recorded |

Resting orders are polled for progress, and updates are forwarded to the Trade Manager only when the executed quantity increases or the order reaches a terminal state.



<br><br><br>



#### **3. API Rate-Limit Handling**

Binance enforces request-weight and order-count limits per IP, and exceeding them leads to rejected requests and eventually temporary IP bans. Because market data backfill, account polling, and order execution all share the same IP, ATM-Eta tracks usage locally and distributes the budget by priority.

<br>

 🔹 **Local Limit Tracking**

* Limits are read from the exchange info at runtime rather than hardcoded, covering every `REQUEST_WEIGHT` and `ORDERS` window the exchange reports.
* Every request declares its weight before it is sent and is checked against all windows of its limit type. If any window would be exceeded, the request is not sent. Counters reset at window boundaries.
* **Conservative startup** — Usage from before launch is unknown, so each window's tracker starts as fully consumed. The budget opens at the next window boundary.
* **IP sharing** — `rateLimitIPSharingNumber` (1–5) divides the budget when multiple instances run behind the same IP.

<br>

 🔹 **Priority-Based Budget Reservation**

* Market data fetches are bulk, deferrable work, so they may only use the budget left after reserving headroom for time-critical work:
  * 1 weight per second as a baseline margin
  * 5 weight per second per activated account (account polling)
  * 1 weight per second per tracked order (order verification)
* When a fetch is refused or fails, a fetch block halts all market data fetching until the next window reset, instead of retrying on every loop.
* Order creation and cancellation draw from the `ORDERS` limit. If it is exhausted, the request is rejected immediately (`APIRATELIMITREACHED`) rather than queued, leaving the retry decision to the Trade Manager.

<br>

 🔹 **Adaptive Account Polling**

* The account polling interval scales with the number of activated accounts, so that polling consumes at most ~50% of the weight budget (with a 10% margin). It is never faster than once per second.
* The number of accounts that can be activated is capped so that polling stays within that 50% even at the slowest interval (10 seconds). For example, the current 2,400/min weight limit allows up to 36 accounts.



<br><br><br>



#### **4. Server Disconnection Recovery**

 🔹 **Connection Monitoring**

* Every second, the Binance API Manager checks network reachability and the Binance system status (normal / maintenance). All exchange-dependent tasks run only while both checks pass.
* Requests from the Trade Manager that arrive while the server is unavailable are rejected immediately (`SERVERUNAVAILABLE`) instead of hanging.

<br>

 🔹 **On Disconnect**

* Everything that may have gone stale is discarded: the API client, cached exchange info, the rate-limit table, all WebSocket connections, and per-symbol stream state.
* Stream subscriptions (which process listens to which symbol) are backed up per symbol.
* Activated accounts and order trackers are kept, and order verification resumes after reconnection.

<br>

 🔹 **On Reconnect**

* Exchange info is re-read. Since the symbol cache was cleared, every symbol is treated as newly listed, re-registered, and queued for streaming.
* Stream state is rebuilt from scratch, and subscriptions are restored from the backup so subscribers do not need to re-register.
* The first message of each stream triggers resynchronization: a fresh orderbook snapshot for `depth`, a backfill from the start of the current interval for `aggTrade`, and a restart of metrics polling.
* Gaps spanning the outage are detected by the Data Manager, whose continuity state is not reset on disconnect, and are backfilled automatically (see [Market Data Gap Detection](#market-data-gap-detection)).
* The rate-limit table is re-initialized with the same conservative startup policy.

<br>

 🔹 **WebSocket Connection Lifecycle**

* Symbols are grouped 50 per connection, with 3 streams per symbol, which uses 75% of Binance's recommended 200 streams per connection.
* **Make-before-break renewal** — Every 15 minutes, each connection is marked expired and its symbols are queued for a new connection. The old connection is closed only after the new one has delivered `kline`, `depth`, and `aggTrade` messages for every symbol. Duplicate messages received during the overlap are dropped by the stream continuity checks.
* Connection creation is retried up to 3 times. If it still fails, the symbols are re-queued.
* A message queue overflow or an unexpected WebSocket error tears down and regenerates all connections.
* Binance Vision downloads retry on 5xx errors with exponential backoff (up to 5 retries).



<br><br><br>



#### **5. Market Data Gap Detection**

Gap detection operates at two layers. The Stream Receiver in the Binance API Manager validates message-level continuity in real time, while the Data Manager validates interval-level continuity of what is actually persisted. Because the Data Manager's state survives stream resets, gaps that the first layer cannot see — such as those spanning a server outage — are still caught.

 🔹 **Layer 1: Stream Receiver (Message Level)**

| Stream | Continuity Check | On Gap |
| :--- | :--- | :--- |
| `kline` | Event time must increase, and each new kline must open exactly one interval after the previous closed one | Missing range is fetched (Binance Vision archive if available, REST otherwise) |
| `depth` | Each diff's `pu` must equal the previous diff's `u` | A REST orderbook snapshot (1000 levels) is fetched and buffered diffs after its `lastUpdateId` are replayed. Re-fetched if the buffer is still discontinuous |
| `aggTrade` | Aggregate trade ID must increase by exactly 1 | Missing ID range is fetched via REST. On the first message, trades are backfilled from the start of the current interval |
| `metric` | Open time continuity of the internally generated 1m stream | Missing range is fetched via REST (limited to the last 28 days) |

While a gap fetch is in progress, live messages are buffered rather than dropped. Fetched data is merged into the buffer in order, so downstream consumers receive a continuous, ordered stream.

<br>

 🔹 **Layer 2: Data Manager (Interval Level)**

* The Data Manager receives only closed intervals and tracks the last open time per symbol and data type. If the next interval does not open exactly one interval later, a fetch request for the missing range is dispatched. Older or duplicate intervals are discarded.
* Stored coverage is tracked per symbol and data type as two range sets in the `descriptors` table: **available ranges** (intervals that have been processed) and **dummy ranges** (intervals whose data could not be recovered).
* When historical collection is enabled, the backfill target is the range from the symbol's first listing time to its first streamed interval, minus the available ranges.
* Fetched results that overlap stored or buffered ranges are rejected, and the fetch targets are recomputed.

<br>

 🔹 **Explicit Data Provenance**

Every interval is tagged with its origin, and the tag determines how it is persisted:

| Tag | Meaning | Persisted |
| :--- | :--- | :--- |
| `FETCHED` | Retrieved via REST or Binance Vision | Yes |
| `STREAMED` | Received via WebSocket | Yes |
| `EMPTY` | Expected but not returned by the exchange | Yes (as a null-valued row) |
| `DUMMY` | Unrecoverable gap filled with a placeholder | No, recorded in dummy ranges |
| `INCOMPLETE` | Interval cut short by a resynchronization | No, recorded in dummy ranges |

When a consumer reads a range from the database, any timestamps without stored rows are returned as `DUMMY` placeholders, so consumers always receive a complete, evenly spaced series.

<br>

 🔹 **Dummy Range Recovery**

Dummy ranges are not permanent. They can be recovered in two ways:

* **Refetch** — Dummy ranges are requested again from Binance, which is useful once Binance Vision has published the daily archives covering them. Only real data replaces dummy ranges.
* **LAN import** — Data can be imported from another ATM-Eta instance's database on the local network. The import target is the local dummy ranges that the remote instance has actually stored (remote available ranges minus remote dummy ranges).

Refetch and import results exclude each other's ranges to prevent double insertion.

<br>

 🔹 **Archive Integrity**

Every Binance Vision file is verified against its SHA-256 `.CHECKSUM` before use. Mismatched files are discarded and downloaded again.



<br><br><br>



#### **6. Database Write Integrity**

* **Batched, transactional writes** — Streamed data is flushed every 5 seconds, and fetched data in chunks of up to 10,000 rows. Data rows and the corresponding range updates in the `descriptors` table are committed in the same transaction, so coverage metadata and stored rows change together.
* **Overlap guard** — Streamed data that overlaps already stored ranges is discarded before insertion.
* **Backpressure** — When the fetched-data buffer reaches 14,400 rows (10 days of 1m data), the Binance API Manager is asked to pause fetching and resumes once the buffer drains below the threshold.
* **I/O-aware scheduling** — A write cycle is skipped while any database backend is waiting on I/O, deferring writes instead of piling them onto a saturated drive.
* **Writing into compressed history** — TimescaleDB chunks are compressed after 7 days. Backfilled data targeting compressed chunks triggers decompression of only the affected chunks, the insert, and recompression. A recompression failure is non-fatal, since the compression policy picks the chunks up later.
* **Automatic index repair** — On an index corruption error, the transaction is rolled back, the corrupted index is identified from the error message and rebuilt with `REINDEX`, and the fetched data still in the buffer is written on the next cycle.

---



### 📊 Multi-timeframe Analysis ###

The diagram below illustrates how ATM-Eta transforms base-aggregated 1m market data into a single actionable trading signal through a multi-timeframe analysis pipeline. The flow is split across two cooperating modules — the **Analyzer**, responsible for extracting structured signals across multiple timeframes, and the **Trade Manager**, responsible for translating those signals into a concrete position target through a user-defined strategy.

The design reflects a core premise: rather than committing the system to a single timeframe, the pipeline runs the same analyses independently across every active timeframe and exposes the full set to the user's strategy — leaving it to the strategy to decide which timeframes matter and how to combine them.

<img src="./docs/mtfanalysis.png" width="800">

#### **Per-Timeframe Analysis**

The Secondary Aggregator expands the base-aggregated 1m market data across the active set of timeframes — 1m, 3m, 5m, 15m, ..., up to 1M — and each timeframe carries its own independent analysis track. Each track runs against its own **Currency Analysis Configuration** — a declarative specification of which analyses to apply (SMA, PSAR, MMACD, IVP, WOI, NES, etc.) and with what parameters — and produces its own **Analysis Results** bundle.
The same indicator can be configured differently across timeframes, giving the strategy access to both fast and slow variants of any signal it cares about.

<br>

#### **Analysis Linearization**

The analysis bundles are then collapsed by the **Analysis Linearizer** into a single flat dictionary — the **Linearized Analysis** — where every (timeframe, analysis code, sub-field) combination is mapped to a unique top-level key.

This step exists for one reason: **strategy ergonomics**. A nested `{interval: {analysisCode: {...}}}` structure forces user-defined strategy code to know the internal layout of the analyzer and walk it manually, coupling every strategy to the analyzer's internal representation. A flat dictionary, by contrast, lets the strategy reference any signal it needs with a single dictionary lookup, treating the entire multi-timeframe analysis surface as a uniform key-value namespace. As a side benefit, this flat form is trivially serializable for offline analysis export — every column in a dataset consumed by TEFFP Seeker is exactly one key from the linearized dictionary, minimizing schema translation between ATM-Eta (CPU) and TEFFP Seeker (GPU-accelerated).

<br>

#### **TEF-Based Strategy Decoupling**

The boundary between the Analyzer and the Trade Manager is the most deliberate piece of this architecture. The Analyzer's responsibility ends at producing a Linearized Analysis. The Trade Manager then invokes a **user-defined TEF Function**, imported from a user-customized Python module, which consumes the Linearized Analysis and returns the target exposure: a direction (`LONG` / `SHORT` / none) and a TEF value in `[-1.0, +1.0]` whose magnitude sets the relative position size. **Trade handlers** then keep the position's **commitment rate** in sync with this target, issuing orders only when the two diverge (see *Trade Configuration*).

This separation produces three concrete benefits:

* **Strategy interchangeability** — Switching strategies is as simple as pointing to a different TEF function file. The Analyzer, the data pipeline, and the order execution path remain untouched.
* **Portable across CPU and GPU** — TEFFP Seeker requires the strategy to be rewritten as a Triton kernel for GPU acceleration, but the TEF interface contract (Linearized Analysis in, target exposure out) stays the same on both sides.
* **Bounded, normalized strategy interface** — Because every strategy is contractually required to output a value in `[-1.0, +1.0]`, downstream position sizing, leverage allocation, and risk-control logic can be written once and reused across every strategy, regardless of how complex the strategy's internal logic is.

---



### 🧠 Trade Logic Pipeline ### 
<img src="./docs/tradestrategy_0.png" width="1000">

A trade strategy in ATM-Eta is defined by three configurations: a **Currency Analysis Configuration** (what to analyze), a **Trade Configuration** (how TEF decisions become orders), and **Account Control** settings (how much capital each position may use). Starting from raw market data, these configurations together determine the order requests that are sent to the exchange.

* <Details>
  <Summary><b><i> Currency Analysis Configuration </b></i></Summary>

  Beyond standard technical analysis tools such as MAs, PSAR, and Bollinger Bands, ATM-Eta ships with a set of built-in hybrid analysis modules. Four of them, **IVP**, **MMACD**, **DMIxADX**, and **MFI**, are described below as representative examples.

  The analysis results are linearized and passed to the TEF function of the position's Trade Configuration (see *Multi-timeframe Analysis*).

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

  
  </Details>

* <Details>
  <Summary><b><i> Trade Configuration </b></i></Summary>
  <img src="./docs/tradecontrol.png" width="750" height="440">

  A **Trade Configuration (TC)** defines how a position turns TEF decisions into orders: which strategy to run, how to size and place orders, and when to cut losses. Each position is attached to one TC.

  | Parameter | Description |
  | :--- | :--- |
  | TEF Function | The strategy function type and its parameters. Returns a direction (`LONG` / `SHORT` / none) and a TEF value in `[-1.0, +1.0]` |
  | Leverage | Leverage applied to the position |
  | Margin Type | `ISOLATED` or `CROSSED` |
  | Direction | Allowed entry directions: `BOTH`, `LONG`, or `SHORT` |
  | Order Type | `MARKET`, `LIMIT` (post-only, filled at the maker fee rate), or `ADAPTIVE` (post-only limits by default, switching to market orders whenever the position must be cleared) |
  | Order Offset | For `LIMIT` and `ADAPTIVE` orders, the price offset from the current price, placed away from the market and aligned to the symbol's tick size |
  | Full Stop Loss (Immediate) | Closes the position as soon as the price touches this distance from the entry price within a kline |
  | Full Stop Loss (Close) | Closes the position when a kline closes beyond this distance from the entry price |
  | Post-Stop-Loss Re-entry | Whether re-entry in the same direction is allowed after a stop loss, before the TEF direction changes |
  <br>

  **Position-Level Controls**

  In addition to the TC, each position has its own trading controls:

  | Parameter | Default | Description |
  | :--- | :---: | :--- |
  | Reduce Only | Off | Blocks entry orders, so the position can only be reduced |
  | Stop Trade On FSL | On | Halts trading on the position after a full stop loss |
  | Stop Trade On Unknown Trade | On | Halts trading on the position after an externally caused position change |
  <br>

  **From TEF to Trade Handlers**

  Each new analysis result is passed through the TEF function, and the resulting target is compared with the current position to generate up to three **trade handlers**, processed in order:

  | Handler | Condition | Action |
  | :--- | :--- | :--- |
  | `CLEAR` | The position is not in the TEF direction (opposite, or TEF has no direction) | Close the entire position |
  | `EXIT` | The committed balance exceeds the target | Reduce the position toward the target (fully, if the TEF value is `0`) |
  | `ENTRY` | The committed balance is below the target, the direction is allowed by the TC, and the position is not reduce-only | Increase the position toward the target |

  The target is `Position Allocated Balance × |TEF|` (see *Account Control Configuration*). Every order passes quantity precision, exchange filter, and side checks before dispatch.

  **Safeguards**

  * **Stale analysis rejection** — An analysis result is ignored if it does not belong to the previous, current, or next interval, or if the price has moved 0.5% or more since it was computed.
  * **Handler expiration** — A trade handler that cannot be executed within one fifth of the base interval is discarded, so outdated decisions never reach the exchange. Time spent waiting for an order cancellation is excluded.
  * **Order replacement** — A resting limit order is cancelled and replaced when a newer TEF decision or a stop loss arrives.
  * **Stop loss precedence** — Stop loss orders are always market orders, regardless of the TC's order type, and discard any pending trade handlers generated before them.
  * **Tradability check** — A position trades only while its currency analysis and TC are attached, its leverage and margin type match the TC, and no external open order is detected.
  * **Automatic halt** — Full stop losses and unknown trades are recorded as abrupt clearing events and retained for 30 days. Depending on the position-level controls, trading on the position is halted when either occurs.

  </Details>

* <Details>
  <Summary><b><i> Account Control Configuration </b></i></Summary>
  <img src="./docs/accountcontrol.png" width="750" height="440">

  Account Control distributes capital across positions and bounds each position's exposure through the three parameters below.

  | Parameter                 | Target   | Description |
  | :---:                     | :---:    | :--- |
  | Allocation Ratio          | Asset    | The fraction of the asset's wallet balance made available for trading |
  | Assumed Ratio             | Position | The fraction of the asset's allocatable balance assigned to a specific position |
  | Maximum Allocated Balance | Position | A hard cap on the balance a single position can be allocated (unlimited by default) |
  <br>

  $$\text{Allocatable Balance} = \max(\text{Wallet Balance},\ 0) \times 0.95 \times \color{orange}{\text{Allocation Ratio}}$$
  $$\text{Position Allocated Balance} = \max\left(0,\ \min\left(\text{Allocatable Balance} \times \color{orange}{\text{Assumed Ratio}},\ \color{orange}{\text{Maximum Allocated Balance}},\ \text{Remaining Allocatable Balance}\right)\right)$$
  <br>

  The `0.95` factor reserves a 5% buffer of the wallet balance for fees and margin fluctuations.

  **Allocation Lifecycle**

  * Balance is allocated to a position when it first enters, and released back to the asset once the position is fully closed.
  * There is no priority ordering. If the Assumed Ratios of all positions sum to more than 100%, positions are funded in the order they enter, and later entries receive only the remaining allocatable balance.
  * If the allocatable balance shrinks below the total already allocated (e.g., after a loss), every position's allocation is scaled down proportionally.
  * After a restart, open positions have their allocations restored automatically.

  **Connection to TEF**

  The allocated balance is the base the TEF value acts on. The target committed balance of a position is:

  $$\text{Target Committed Balance} = \text{Position Allocated Balance} \times |\text{TEF}|$$

  Entry orders are generated when the committed balance falls below this target, and exit orders when it exceeds it. Entries are additionally bounded by the account's available balance.

  **Derived Risk Metrics**

  | Metric | Definition |
  | :--- | :--- |
  | Weighted Assumed Ratio | Assumed Ratio × leverage. The effective exposure the position can reach relative to the allocatable balance |
  | Commitment Rate | Margin in use (quantity × entry price ÷ leverage) ÷ allocated balance |
  | Risk Level | Commitment Rate × how far the current price has moved from the entry price toward the liquidation price |
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
      Manage the local market database.

      1\. Monitor database and drive usage, including compression statistics.  
      2\. Configure stream and historical data collection per symbol.  
      3\. Compress the database, or reset market data for selected symbols.  
      4\. Recover dummy ranges by refetching from Binance or importing from another ATM-Eta instance on the local network.  
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

      2\. Select a target symbol.  
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
      3\. Name the configuration (auto-generated if left blank) and click **ADD**.
      <img src="./docs/feat2_2.png">
      <br>

      4\. Select a target symbol from the market list.  
      5\. Select a CAC to apply, name the analysis instance (auto-generated if left blank) and click **ADD**.  
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
    <Summary><b><i> Adding a Trade Configuration </b></i></Summary>

      1\. Navigate to the **AutoTrade** page.  
      <img src="./docs/feat3_1.png">
      <br>

      2\. Configure trade configuration parameters.  
      3\. Name the configuration (auto-generated if left blank) and click **ADD**.  
      <img src="./docs/feat3_2.png">
      <br>

    </Details>

  * <Details>
    <Summary><b><i> Backtesting & Results </b></i></Summary>

      1\. Navigate to the **Simulation** page.  
      <img src="./docs/feat4_1.png">
      <br>

      2\. Set the simulation name (auto-generated if left blank) and range.  
      3\. Configure position-specific strategies (Currency Analysis, Trade Configuration, Account Control).  
      4\. Determine account-level parameters.  
      5\. Click **ADD** to start the simulation. Once it is completed, move to the **SIMULATION RESULT** page either by clicking **VIEW RESULT** or navigating from the **DASHBOARD**.  
      <img src="./docs/feat4_2.png">
      <br>

      6\. Select a simulation.  
      7\. View the simulation result summary.  
      8\. Inspect the simulation result details.  
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
      &nbsp; [ACTUAL ONLY] Activate the account by entering your Binance API Key and Secret Key, or by using an **AAF** (see *Integrity & Recovery*). This will synchronize the local account instance with the real account in Binance.  
      4\. Monitor asset information and position status.  
      5\. For each position to trade, assign a Currency Analysis, a Trade Configuration, and an Assumed Ratio, then enable the position's trade status. Automated trading runs only while both the account's and the position's trade status are enabled.
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

**What the run actually validated.** Over the 118-day period, the system handled all order executions reliably, maintained position and balance synchronization with the exchange, and recovered automatically from network disconnects, API rate limit events, and data stream interruptions without manual intervention. I considered this a sufficient outcome for a stability validation run rather than a profit demonstration. The realized maximum drawdown stayed well within the backtest's projected level (~35%), and the realized return likewise exceeded what the backtest projected for the same deployment window. That said, this is more likely attributable to favorable market conditions during the deployment window than to any inherent strength of the strategy itself.

> ⚠️ **Disclaimer** — This application **does not guarantee profit**. It only serves as a platform on which users can build and operate their own strategies. Past performance, whether from backtests or live runs, is not indicative of future results. Cryptocurrency derivatives trading carries substantial risk of loss.



---



### 🤝 Credits
* **[python-binance](https://github.com/sammchardy/python-binance)** by *sammchardy* (MIT License)  
  - This project includes a modified version of `python-binance`. An option to disable the first kline search within the `futures_historical_klines` function in `client.py` module was added. 

---



### 🗓️ Project Duration
* September 2024 – May 2026 (Updates + Maintenance Continued)



---



### 🚀 Project Updates
**Version 1.1.0 Update [2026/09/22]**
 - **New Features**

   * **Metrics Market Data Fetching:** 
   Added a data pipeline that collects 5m interval Open Interest and global Long/Short Ratio data via the Binance REST API, with Binance Vision archives used for historical backfill. Since Binance provides no streaming support for these metrics, an internal stream generation logic produces 1m interval data from the 5m source, allowing the metrics to flow through the same pipeline as kline, depth, and aggTrade data with minimal changes to the existing architecture. Only endpoints that require no API key were selected, so metrics collection runs independently of account activation.

   * **Limit Price Trading:** 
   Integrated with the existing TEF function to automatically execute limit orders. Orders are placed as post-only (GTX) at a configurable offset from the current price, aligned to each symbol's tick size in the direction away from the market, so every fill is executed at the maker fee rate. A redesigned order lifecycle (DISPATCHED → RESTING → CANCELING → SETTLED/CANCELLED) tracks resting orders across partial fills using cumulative executed quantity, and resting orders are automatically cancelled and replaced when a newer TEF decision or a stop-loss is triggered. Stop-loss and force-clear orders remain market orders to guarantee immediate execution. The virtual trading server was extended to simulate post-only rejections, partial fills, and price-movement-based limit execution, enabling full lifecycle testing before live deployment.

 - **Improvements & Fixes**

   * **Analysis System Modularization:** 
   Restructured the monolithic analysis logic so that each indicator lives in its own self-contained module file. This establishes a consistent structure for expanding the analysis system: new indicators plug in as standalone modules rather than extending a single growing codebase, keeping the analysis layer scalable as the number of supported indicators increases.

   * **Improved Order Tracking Logic:**
   Order handling now distinguishes between definite rejections and ambiguous failures (timeouts, network errors, unexpected response formats). Ambiguous orders are no longer retried blindly; instead, they are registered for status verification and resolved by querying the exchange, preventing duplicate orders. Orders confirmed absent are safely regenerated, while orders whose state cannot be determined are terminated without regeneration. Cancellation requests rejected because the order already closed now fetch the order's final state, correctly recording fills that occur just before cancellation. Response parsing was hardened against API changes, including the removal of `avgPrice` from order creation responses, which is now retrieved via order queries.

   * **Position Direction Display In Chart Drawer Object:**
   Added a position strip along the bottom of the chart that visualizes, based on trade log data, the final long or short position held at the end of each interval. This makes it easy to read the position state across the chart at a glance, alongside the existing trade record markers.



<br>



**Version 1.2.0 Update [2026/09/23]**
 - **New Features**

   * **Position-Level Trading Control Parameters:**
   Reduce-only mode, previously stored but never enforced, now blocks entry orders so a position can only be reduced. Two new per-position parameters were added alongside it: stop-trade-on-FSL and stop-trade-on-unknown-trade, which control whether trading is halted after a full stop loss or an externally-caused position change. Full stop losses are now recorded as abrupt clearing events, which were previously only logged for unknown trades, and these records are retained for 30 days rather than cleared on each halt.
   
   * **Adaptive Order Type:**
     A new `ADAPTIVE` order type places post-only limit orders by default, but switches to market orders when the target exposure factor reverses direction and the position must be cleared. This keeps the maker fee advantage of limit orders for routine entries and partial exits, while ensuring that reversals — where execution speed matters most — are not left resting in the order book.

 - **Improvements & Fixes**

   * **False Unknown Trade Detection Fix:**
   Account data and order responses arrive through separate paths, so a fill could appear in the account snapshot before its order response was received. The system previously treated this as external intervention, halting trading on the position. Quantity changes that fall within a live order's outstanding quantity are now attributed to that order and resolved once its response arrives, while genuine external changes are still detected.

   * **Average Fill Price Retrieval:**
   Binance removed `avgPrice` from order creation responses following the CM migration. The system now falls back to computing a volume-weighted average from the order's trade history whenever the field is absent, and order response parsing is guarded so that a missing or changed field can no longer leave a placed order untracked.

   * **Account Data Read Rate Limit Calculation Fix:**
   The IP sharing factor was applied as a multiplier instead of a divisor when computing the account data read interval, causing the polling interval to shorten rather than lengthen as the rate limit budget was split across more clients. The interval is now clamped to its configured bounds, and the maximum activation count accounts for the same safety margin used in the interval calculation, so the margin is never truncated at the upper bound.
   
   * **AAF Scan Robustness:**
   The AAF scan now validates each `.aaf` file's contents before use. Previously, a file that parsed as JSON but lacked the expected fields could raise an exception and interrupt the scan. Since the scan covers the root directory of every mounted drive, unrelated files sharing the extension could trigger this. Malformed files are now skipped.



---



### 📄 Document Info
* **Last Updated:** September 25th, 2026  
* **Author:** Bumsu Kim
* **Email:**  kimlvis31@gmail.com
