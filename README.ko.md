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

[![english-readme](https://img.shields.io/badge/Language-English-yellow.svg)](./README.md)



---



### 📖 프로젝트 소개 ###
**Auto Trade Machine Eta (ATM-Eta)** 는 다중 시간대 시장 분석과 실시간 자동 매매를 하나의 애플리케이션에서 통합적으로 제공하는 암호화폐 거래 플랫폼입니다. 전략 연구와 실거래 사이의 간극을 좁히는 것을 목표로 설계되었으며, 사용자는 별도의 도구나 환경 전환 없이 트레이딩 전략을 개발하고, 검증하고, 운용할 수 있습니다.

#### 핵심 기능
* **실시간 시장 데이터 파이프라인** — 애플리케이션 실행 시 Binance Futures 거래소에 자동으로 연결되어 klines, 호가창 스냅샷, 체결 데이터를 지속적으로 수집합니다. 수집된 데이터는 로컬 TimescaleDB 기반의 PostgreSQL 서버에 집계 및 저장되며, 실시간 분석과 백테스팅 모두에 낮은 지연으로 접근할 수 있습니다.
* **커스텀 분석 도구 모음** — 표준 보조지표(MA, PSAR, Bollinger Bands) 외에도 ATM-Eta는 자체 개발한 7개의 하이브리드 분석 도구 — **IVP**, **MMACD**, **DMIxADX**, **MFI**, **TPD**, **WOI**, **NES** — 를 제공합니다. 각 도구는 가격, 거래량, 호가창, 체결 데이터를 통합하여 트레이드 컨트롤러가 활용할 수 있는 일관된 신호 집합을 생성합니다.
* **TEF 기반 전략 정형화** — 트레이딩 전략은 **TEF (Target Exposure Factor)** 라는 하나의 정규화된 스칼라 값(`-1.0` ~ `+1.0`)으로 표현됩니다. 부호는 방향(음수 = SHORT, 양수 = LONG)을, 절대값의 크기는 할당된 자본 대비 목표 포지션 크기를 나타냅니다. 방향과 크기를 단일 유계 값으로 압축함으로써, 임의의 복잡한 분석 로직을 깔끔하고 표준화된 전략 인터페이스로 패키징할 수 있습니다.
* **외부 GPU 가속 최적화** — ATM-Eta에서 추출한 분석 데이터는 별도의 확장 애플리케이션인 **TEFFP Seeker** 에 입력될 수 있습니다. TEFFP Seeker는 GPU 가속 백테스팅 엔진으로, 사용자 정의 전략에 대한 대규모 파라미터 스윕을 병렬로 실행하여, CPU만으로는 현실적으로 탐색이 불가능한 영역에서 최적 파라미터 조합을 찾아낼 수 있도록 지원합니다.
* **신경망 통합 (실험적 기능)** — 사용자는 과거 시장 데이터를 기반으로 커스텀 **MLP (Multi-Layer Perceptron)** 모델을 직접 설계, 학습, 배포할 수 있습니다. 학습된 모델은 Analyzer 또는 Simulator에 보조 신호 소스로 연결할 수 있습니다. 현재는 MLP 구조만 지원합니다.
* **프로세스 격리 아키텍처** — 애플리케이션은 9개 이상의 독립된 프로세스(Main, GUI, BinanceAPI, DataManager, TradeManager, SimulationManager, Analyzer, Simulator, NeuralNetwork)로 구성되어, 자체 IPC 레이어를 통해 통신합니다. GUI 렌더링, 데이터 수집, 분석, 시뮬레이션, 실거래 실행이 서로 독립적으로 동작하며 어느 한 작업도 다른 작업을 블로킹하지 않습니다.

본 플랫폼은 **'Build → Test → Execute'** 워크플로우를 중심으로 설계되어 있으며, 하나의 전략을 코드 재작성이나 환경 변경 없이 백테스트 검증에서 실거래 운용까지 그대로 이어갈 수 있습니다.



---



### 🔬 실거래 안정성 테스트 ###

전체 시스템을 장기간에 걸쳐 검증하기 위해, 본인의 Binance Futures 계정에서 약 4개월간 애플리케이션을 실제로 운용해 보았습니다. 아래 차트는 해당 기간 동안의 실제 잔고 변동 기록입니다.

<img src="./docs/balancehistory_myaccount.png" width="800">

| 항목 | 내용 |
| :--- | :--- |
| **운용 기간** | 2025년 8월 24일 ~ 2025년 12월 20일 (약 118일) |
| **거래 종목** | Binance Futures의 `BTCUSDT`, `ETHUSDT`, `XRPUSDT` |
| **전략 출처** | 배포 전 5년치 과거 데이터로 파라미터 튜닝 |
| **백테스트 예측치** | 약 150배 성장, 최대 낙폭(MDD) 약 35% |
| **초기 잔고** | $4,718.55 |
| **최저 잔고** | $4,022.05 (−14.76%) |
| **최고 잔고** | $6,603.11 (+39.94%) |
| **최종 잔고** | $5,640.23 (+19.53%) |

**백테스트 예측치에 대해서.** 150배라는 수치는 과거 데이터에 대한 파라미터 과적합(overfitting)으로 인한 과장된 결과일 가능성이 매우 높으며, 본인 또한 이를 실제 운용 시 기대 수익으로 예상하지 않았습니다. 그럼에도 해당 전략을 배포한 이유는, 이번 운용의 목적이 **수익 창출이 아니라 전체 파이프라인이 실거래 환경에서 지속적이고 정상적으로 동작하는지 검증하는 것**이었기 때문입니다.

**실제로 검증된 부분.** 118일간의 운용 기간 동안 시스템은 모든 주문 체결을 안정적으로 처리하였고, 거래소와의 포지션 및 잔고 동기화를 유지하였으며, 네트워크 단절, API rate limit 도달, 데이터 스트림 끊김 등의 상황에서 수동 개입 없이 자동으로 복구되었습니다. 이는 수익 시연이 아닌 안정성 검증 목적의 운용으로서 충분한 결과라고 판단했습니다. 실제 최대 낙폭은 백테스트 예측치(약 35%)보다 양호한 수준에서 머물렀고, 동일 기간 기준 수익률 또한 백테스트의 동기간 예측치를 상회하였습니다. 다만 이는 운용 시점의 시장 상황이 우호적으로 맞물린 결과일 가능성이 크며, 전략 자체의 우수성으로 보기에는 어렵다고 판단됩니다.

> ⚠️ **유의사항** — 본 애플리케이션은 **수익을 보장하지 않습니다**. 사용자가 직접 자신의 전략을 구축하고 운용할 수 있는 플랫폼을 제공할 뿐입니다. 백테스트 결과든 실거래 결과든 과거의 성과는 미래의 성과를 보장하지 않으며, 암호화폐 파생상품 거래는 상당한 손실 위험을 동반합니다.



---



### ▶️ 실행 방법 ###
애플리케이션을 실행하기 전에 **Docker** 가 시스템에 설치되어 있고 실행 중인 상태여야 합니다. 최초 실행 시 PostgreSQL (TimescaleDB) 서버 컨테이너가 자동으로 구성됩니다.

#### Windows 🪟
1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) 을 설치하고 실행 상태인지 확인합니다.
2. 루트 디렉토리에서 `setup.bat` 을 실행합니다. `.venv` 가 생성되고 필요한 라이브러리가 설치됩니다.
3. 루트 디렉토리에서 `run.bat` 을 실행합니다. 애플리케이션이 시작됩니다.

#### Linux 🐧
1. [Docker Engine](https://docs.docker.com/engine/install/) 을 설치하고 Docker 데몬이 활성화되어 있는지 확인합니다 (`sudo systemctl start docker`).
2. 터미널에서 `chmod +x setup.sh run.sh` 명령을 실행합니다.
3. 루트 디렉토리에서 `setup.sh` 를 실행합니다. `.venv` 가 생성되고 필요한 라이브러리가 설치됩니다.
4. 루트 디렉토리에서 `run.sh` 를 실행합니다. 애플리케이션이 시작됩니다.



---



### ✅ 요구 사양 ###
* **운영체제**: Windows 10/11 또는 Linux
* **Python**: `3.11` 이상
* **CPU**:    8코어 이상
* **RAM**:    16GB 이상
* **저장공간**: 10GB 이상



---



### 🧱 시스템 아키텍처 ###
ATM-Eta는 각 핵심 책임이 독립된 프로세스로 분리되어 동작하는 멀티프로세스 시스템으로 설계되었습니다. 실시간 시장 데이터 수집, GUI 렌더링, 분석, 시뮬레이션, 실거래 실행이 모두 동시에 동작하며, 어느 작업도 다른 작업을 블로킹하지 않습니다. 아래 다이어그램은 외부 입력, 내부 프로세스, 영속 저장소, 그리고 확장 애플리케이션인 **TEFFP Seeker** 와의 연결까지 포함한 전체 구조를 나타냅니다.

<img src="./docs/applicationArchitecture.png" width="1200">

모든 프로세스는 `atmEta_IPC.py` 모듈에 정의된 `IPCAssistant` 클래스를 통해 서로 통신하며, 이 클래스는 애플리케이션 전반에 걸쳐 통합된 메시지 전달 인터페이스를 제공합니다.

> **다이어그램에 대한 참고 사항:** 최상위 **Main 프로세스** 는 애플리케이션 생명주기를 관리합니다 — 모든 매니저 프로세스를 spawn하고, 시스템 리소스를 평가하며, 정상적인 종료(graceful shutdown)를 조율합니다. 다이어그램에서는 런타임 데이터 흐름에 집중하기 위해 Main 프로세스를 생략했습니다.

#### 프로세스별 역할

| 프로세스                | 역할 |
| :---:                   | :--- |
| **Main**                    | 애플리케이션 초기화, 시스템 리소스 평가, 워커 프로세스(Analyzer/Simulator) 수 결정, 시작 시퀀스 조율 |
| **GUI Manager**             | 그래픽, 오디오 리소스, 사용자 상호작용 객체를 관리. 사용자 인터페이스와 백엔드 로직을 잇는 중앙 허브 역할 수행 |
| **Binance API Manager**     | 거래소와의 모든 상호작용을 담당하는 게이트웨이. 실시간 시장 데이터 수집, API rate limit 관리, 주문 체결 처리 |
| **Data Manager**            | 로컬 시장 데이터, 계정 정보, 시뮬레이션 기록을 통합 관리하는 저장 엔진. 다른 매니저 프로세스에게 일관된 CRUD 인터페이스 제공 |
| **Trade Manager**           | 트레이딩 운용의 중심 오케스트레이션 단위. 계정 연결, 전략 설정, 로직 결정, Analyzer로의 작업 위임 담당 |
| **Analyzer**                | **Trade Manager** 가 할당한 실시간 시장 분석 작업을 수행 |
| **Simulation Manager**      | 시뮬레이션 세션의 생명주기 관리 및 과거 시뮬레이션 데이터 관리 |
| **Simulator**               | **Simulation Manager** 가 할당한 시뮬레이션 (백테스팅) 작업 수행 |
| **Neural Network Manager**  | 사용자가 과거 데이터를 기반으로 모델을 설계, 학습, 배포할 수 있도록 지원. 학습된 모델은 **Analyzer** 또는 **Simulator** 에 import되어 보조 신호 생성에 활용 |

#### 워커 프로세스 할당

**Analyzer** 와 **Simulator** 워커 프로세스의 수는 `programConfig.config` 파일의 `nAnalyzers`, `nSimulators` 파라미터를 통해 사용자가 직접 설정합니다. 다만 애플리케이션은 런타임에 사용 가능한 CPU 코어 수를 기준으로 이 값들을 제한하여, 설정된 워커 수가 호스트 머신이 감당할 수 있는 범위를 절대 초과하지 않도록 보장합니다.

실제로 spawn되는 워커 수는 다음 로직에 따라 결정됩니다.

$$n_{rem} = \max(N_{CPU} - N_{managers} - 2,\ 0)$$

$$n_{Analyzers} = 1 + \min(n_{rem},\ \texttt{nAnalyzers} - 1)$$

$$n_{Simulators} = 1 + \min(n_{rem} - (n_{Analyzers} - 1),\ \texttt{nSimulators} - 1)$$

여기서 $N_{CPU}$ 는 호스트 머신이 보유한 CPU 코어 수, $N_{managers}$ 는 매니저 프로세스의 수를 의미합니다. `-2` 는 Main 프로세스와 OS 레벨 작업을 위한 여유 코어를 확보하기 위함입니다.

이 할당 정책은 **설정값과 무관하게 최소 1개의 Analyzer와 1개의 Simulator 가 항상 spawn 됨을 보장** 하며, 동시에 리소스가 제한된 환경에서 코어 oversubscription이 발생하지 않도록 합니다. CPU 자원이 부족할 경우에는 Simulator 보다 Analyzer 에 우선 할당되는데, 이는 실시간 분석이 실거래 운용에서 핵심적인 반면 시뮬레이션은 오프라인 작업이기 때문입니다.

> **참고:** Neural Network 모듈은 머신러닝 기반 시장 분석의 가능성을 탐구하기 위한 실험적 기능입니다. 현재는 MLP 구조만 지원합니다.



---



### 📥 시장 데이터 파이프라인 ###



---



### 🛡️ 시스템 복구 ###



---



### 📊 다중 시간대 분석 ###



---



### 🎯 트레이드 로직 파이프라인 ###



---



### 👀 애플리케이션 프리뷰 & 사용법 ###
* 시장
  * ㅇㅁㄴㅇ  
  * <img src="./docs/test.png" width="600" height="400">
* 실시간 분석
  * ㅇㅁㄴㅇ  
* 투자 전략
  * ㅇㅁㄴㅇ  
* 시뮬레이션 (백테스팅)
  * ㅇㅁㄴㅇ  
* 바이낸스 계정 연결
  * ㅇㅁㄴㅇ  
* 트레이딩
  * ㅇㅁㄴㅇ  
* 뉴럴 네트워크 (재미로만 봐주세요)
  * ㅇㅁㄴㅇ  

---



### 🤝 크레딧
* **[python-binance](https://github.com/sammchardy/python-binance)** by *sammchardy* (MIT License)  
  - This project includes a modified version of `python-binance`. An option to disable the first kline search within the `futures_historical_klines` function in `client.py` module was added. 



---



### 🗓️ 프로젝트 기간
* 2024년 9월 - 2026년 5월



---



### 📄 문서 정보
* **마지막 업데이트:** 2026년 5월 6일
* **작성자:** 김범수
* **이메일:** kimlvis31@gmail.com
