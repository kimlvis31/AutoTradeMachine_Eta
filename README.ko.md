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

[![english-readme](https://img.shields.io/badge/Language-English-yellow.svg)](./README.md)



---



### 📖 프로젝트 소개 ###

**Auto Trade Machine Eta (ATM-Eta)** 는 다중 시간대 시장 분석과 실시간 자동 매매를 하나의 애플리케이션에서 통합적으로 제공하는 암호화폐 거래 플랫폼입니다. 전략 연구와 실거래 사이의 간극을 좁히는 것을 목표로 설계되었으며, 사용자는 별도의 도구나 환경 전환 없이 트레이딩 전략을 개발하고, 검증하고, 운용할 수 있습니다.

#### **핵심 기능**
* **실시간 시장 데이터 파이프라인** — 애플리케이션 실행 시 Binance Futures 거래소에 자동으로 연결되어 kline, 호가창 스냅샷, 체결 데이터, 파생 지표(미결제약정, 롱/숏 비율)를 지속적으로 수집합니다. 수집된 데이터는 로컬 TimescaleDB 기반의 PostgreSQL 서버에 집계 및 저장되며, 실시간 분석과 백테스팅 모두에 낮은 지연으로 접근할 수 있습니다.
* **커스텀 분석 도구 모음** — 표준 보조지표(MA, PSAR, Bollinger Bands) 외에도, ATM-Eta는 가격, 거래량, 호가창, 체결 데이터를 통합하여 TEF 함수가 활용할 수 있는 일관된 신호 집합을 생성하는 하이브리드 분석 모듈들을 제공합니다.
* **TEF 기반 전략 정형화** — 트레이딩 전략은 **TEF (Target Exposure Factor)** 로 표현됩니다. TEF는 목표 방향(`LONG` / `SHORT` / 없음)과 `[-1.0, +1.0]` 범위의 유계 값으로 구성되며, 값의 크기는 할당된 자본 대비 목표 포지션 크기를 나타냅니다. 전략의 판단을 하나의 정규화된 목표로 압축함으로써, 임의의 복잡한 분석 로직을 깔끔하고 표준화된 전략 인터페이스로 패키징할 수 있습니다.
* **외부 GPU 가속 최적화** — ATM-Eta에서 추출한 분석 데이터는 별도의 확장 애플리케이션인 **TEFFP Seeker** 에 입력될 수 있습니다. TEFFP Seeker는 GPU 가속 백테스팅 엔진으로, 사용자 정의 전략에 대한 대규모 파라미터 스윕을 병렬로 실행하여, CPU만으로는 현실적으로 탐색이 불가능한 영역에서 최적 파라미터 조합을 찾아낼 수 있도록 지원합니다.
* **신경망 통합 (실험적 기능)** — 사용자는 과거 시장 데이터를 기반으로 커스텀 **MLP (Multi-Layer Perceptron)** 모델을 직접 설계, 학습, 배포할 수 있습니다. 학습된 모델은 Analyzer 또는 Simulator에 보조 신호 소스로 연결할 수 있습니다. 현재는 MLP 구조만 지원합니다.
* **프로세스 격리 아키텍처** — 애플리케이션은 9개 이상의 독립된 프로세스(Main, GUI, BinanceAPI, DataManager, TradeManager, SimulationManager, Analyzer, Simulator, NeuralNetwork)로 구성되어, 자체 IPC 모듈을 통해 통신합니다. GUI 렌더링, 데이터 수집, 분석, 시뮬레이션, 실거래 실행이 서로 독립적으로 동작하며 어느 한 작업도 다른 작업을 블로킹하지 않습니다.

본 플랫폼은 **'Build → Test → Execute'** 워크플로우를 중심으로 설계되어 있으며, 하나의 전략을 코드 재작성이나 환경 변경 없이 백테스트 검증에서 실거래 운용까지 그대로 이어갈 수 있습니다.

---



### ▶️ 실행 방법 ###
애플리케이션을 실행하기 전에 **Docker** 가 시스템에 설치되어 있고 실행 중인 상태여야 합니다. 최초 실행 시 PostgreSQL (TimescaleDB) 서버 컨테이너가 자동으로 내려받아지고 구성됩니다.

#### **Windows** 🪟
1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) 을 설치하고 실행 상태인지 확인합니다.
2. 루트 디렉토리에서 `setup.bat` 을 실행합니다. `.venv` 가 생성되고 필요한 라이브러리가 설치됩니다.
3. 루트 디렉토리에서 `run.bat` 을 실행합니다. 애플리케이션이 시작됩니다.

#### **Linux** 🐧
1. [Docker Engine](https://docs.docker.com/engine/install/) 을 설치하고 Docker 데몬이 활성화되어 있는지 확인합니다 (`sudo systemctl start docker`).
2. 터미널에서 `chmod +x setup.sh run.sh` 명령을 실행합니다.
3. 루트 디렉토리에서 `setup.sh` 를 실행합니다. `.venv` 가 생성되고 필요한 라이브러리가 설치됩니다.
4. 루트 디렉토리에서 `run.sh` 를 실행합니다. 애플리케이션이 시작됩니다.



---



### ✅ 요구 사양 ###
* **운영체제**: Windows 10/11 또는 Linux
* **Python**:   `3.11` 이상
* **CPU**:      8코어 이상
* **RAM**:      16GB 이상
* **저장공간**: 10GB 이상



---



### 🧱 시스템 아키텍처 ###
ATM-Eta는 각 핵심 책임이 독립된 프로세스로 분리되어 동작하는 멀티프로세스 시스템으로 설계되었습니다. 실시간 시장 데이터 수집, GUI 렌더링, 분석, 시뮬레이션, 실거래 실행이 모두 동시에 동작하며, 어느 작업도 다른 작업을 블로킹하지 않습니다. 아래 다이어그램은 외부 입력, 내부 프로세스, 영속 저장소, 그리고 확장 애플리케이션인 **TEFFP Seeker** 와의 연결까지 포함한 전체 구조를 나타냅니다.

<img src="./docs/applicationArchitecture.png" width="1200">

모든 프로세스는 `ipc.py` 모듈에 정의된 `IPCAssistant` 클래스를 통해 서로 통신하며, 이 클래스는 애플리케이션 전반에 걸쳐 통합된 메시지 전달 인터페이스를 제공합니다.

> **다이어그램에 대한 참고 사항:** 최상위 **Main 프로세스** 는 애플리케이션 생명주기를 관리합니다 — 모든 매니저 프로세스를 생성하고, 시스템 리소스를 평가하며, 정상적인 종료(graceful shutdown)를 조율합니다. 다이어그램에서는 런타임 데이터 흐름에 집중하기 위해 Main 프로세스를 생략했습니다.

#### **프로세스별 역할**

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

#### **워커 프로세스 할당**

**Analyzer** 와 **Simulator** 워커 프로세스의 수는 `programConfig.config` 파일의 `nAnalyzers`, `nSimulators` 파라미터를 통해 사용자가 직접 설정합니다. 다만 애플리케이션은 런타임에 사용 가능한 CPU 코어 수를 기준으로 이 값들을 제한하여, 설정된 워커 수가 호스트 머신이 감당할 수 있는 범위를 초과하지 않도록 보장합니다.

실제로 생성되는 워커 수는 다음 로직에 따라 결정됩니다.

$$n_{rem} = \max(N_{CPU} - N_{managers} - 2,\ 0)$$

$$n_{Analyzers} = 1 + \min(n_{rem},\ \texttt{nAnalyzers} - 1)$$

$$n_{Simulators} = 1 + \min(n_{rem} - (n_{Analyzers} - 1),\ \texttt{nSimulators} - 1)$$

여기서 $N_{CPU}$ 는 호스트 머신이 보유한 CPU 코어 수, $N_{managers}$ 는 매니저 프로세스의 수를 의미합니다. `-2` 는 Main 프로세스와 OS 레벨 작업을 위한 여유 코어를 확보하기 위함입니다.

이 할당 정책은 **설정값과 무관하게 최소 1개의 Analyzer와 1개의 Simulator가 항상 생성됨을 보장** 하며, 동시에 리소스가 제한된 환경에서 코어 oversubscription이 발생하지 않도록 합니다. CPU 자원이 부족할 경우에는 Simulator보다 Analyzer에 우선 할당되는데, 이는 실시간 분석이 실거래 운용에서 핵심적인 반면 시뮬레이션은 오프라인 작업이기 때문입니다.

> **참고:** Neural Network 모듈은 머신러닝 기반 시장 분석의 가능성을 탐구하기 위한 실험적 기능입니다. 현재는 MLP 구조만 지원합니다.



---



### 📥 시장 데이터 파이프라인 ###

아래 다이어그램은 외부 Binance 서비스로부터 Binance API Manager와 Data Manager, 데이터베이스 서버를 거쳐 최종적으로 데이터 소비자(Data Consumers)에게 전달되는 데이터 흐름을 보여주는 간소화된 시장 데이터 파이프라인입니다. 전체 구현에는 상태 관리(bookkeeping) 및 오류 처리 경로가 추가로 포함되어 있으나, 구조적 의도를 명확히 전달하기 위해 본 다이어그램에서는 의도적으로 생략했습니다.

<img src="./docs/marketdatapipeline.png" width="1200">

이 파이프라인은 실시간 거래와 백테스트 모두에 필요한 유연성을 유지하면서, 네트워크 부하, 스토리지 비용, 하위 컴포넌트의 복잡성을 최소화하기 위한 몇 가지 핵심적인 설계 결정을 바탕으로 구축되었습니다.
  
<br>
   
#### **단일 베이스 인터벌, 온디맨드 집계**

파이프라인 전반에 걸쳐 모든 시장 데이터는 **1분 베이스 인터벌** 을 기준으로 수집, 처리, 저장됩니다. 상위 타임프레임(5m, 15m, 1h, 4h, ..., 1M)은 **별도로 저장되지 않으며**, 실제로 해당 데이터가 필요한 시점에 각 Data Requester 내부의 Secondary Aggregator에 의해 **온디맨드 방식으로 생성** 됩니다.

이 방식은 두 가지 핵심적인 이점을 제공합니다.

* **네트워크 부하 감소** — 하위 작업이 얼마나 많은 타임프레임을 요구하든, 각 데이터 타입은 심볼당 단 하나의 1분 스트림만 필요합니다. 타임프레임마다 개별적으로 구독하는 단순한 설계라면, 활성화된 타임프레임 수만큼 WebSocket 부하가 배로 늘어나게 됩니다.
* **스토리지 효율성 및 DB 구조 단순화** — 1분 베이스 데이터만 저장함으로써 물리적인 스토리지 용량을 최소화합니다. 더 중요한 점은 데이터베이스 구조와 수집 로직이 획기적으로 단순해진다는 것입니다. 시스템은 심볼당 단일 데이터셋만 유지하면 되므로, 여러 타임프레임 테이블에 걸쳐 삽입을 동기화해야 하는 복잡성과 오버헤드가 사라집니다.



<br>



#### **이기종 스트림 통합**

ATM-Eta는 각기 다른 구조와 전달 방식을 가진 네 가지 타입의 시장 데이터를 수집합니다.

| 데이터 타입 | 소스 | 원본 해상도 |
| :--- | :--- | :--- |
| `kline` | WebSocket | 고정된 1분 경계 |
| `aggTrade` | WebSocket | 이벤트 기반 (체결 단위) |
| `depth` | WebSocket | 이벤트 기반 (호가창 변경분) |
| `metric` (미결제약정, 롱/숏 비율) | REST 전용 | 5분 |

이들을 동일한 1분 베이스 구조로 통합하기 위해, kline을 제외한 모든 타입은 Binance API Manager를 벗어나기 전 **Primary Aggregator** 내부에서 변환됩니다.

* `aggTrade` 이벤트는 동일한 1분 구간 내에서 매수/매도 수량, 체결 횟수, 거래대금 요약으로 누적됩니다.
* `depth` 변경분은 로컬에서 유지되는 호가창에 적용되며, 이 호가창은 최대 초당 1회 12개의 거래대금 구간으로 샘플링됩니다. 12개 구간은 중간가 기준 고정 거리(0.2%, 1%, 2%, 3%, 4%, 5%)에 위치한 매수 6개, 매도 6개 구간으로 구성되며, 각 분의 마지막 샘플이 해당 분의 기록이 됩니다.
* `metric` 값은 매 5분 경계 직후 REST로 조회되어 내부적으로 생성되는 1분 스트림으로 확장되므로, WebSocket 데이터와 동일한 스트림 처리 경로를 따릅니다.

이를 통해 두 가지 연쇄적인 이점을 얻을 수 있습니다. 첫째, 데이터 볼륨이 크게 감소합니다. `aggTrade` 와 `depth` 의 경우 수 자릿수 규모로 줄어듭니다. 둘째, 네 가지 데이터 타입 모두 구조적으로 동일한 스트림 및 fetch 처리 메서드로 다룰 수 있어, 타입별 분기 처리의 필요성이 최소화됩니다.



<br>



#### **과거 데이터 백필 소스**

과거 데이터는 두 가지 소스에서 수집됩니다. 대용량 처리에 유리한 **Binance Vision** 일별 아카이브를 우선 사용하고, 아직 아카이브되지 않은 구간은 **REST API** 로 보완합니다.

| 데이터 타입 | Binance Vision | REST | 그 외 |
| :--- | :--- | :--- | :--- |
| `kline` | ✅ | ✅ 모든 구간 | — |
| `depth` | ✅ (동일한 12개 구간으로 재분배) | 현재 스냅샷만 | 더미 |
| `aggTrade` | ✅ | 실시간 스트림 공백만 | 더미 |
| `metric` | ✅ | ✅ 최근 28일 | 더미 |

아카이브 파일은 병렬로 내려받으며, 사용 전에 SHA-256 체크섬으로 검증됩니다. 두 소스 모두에서 복구할 수 없는 구간은 더미 구간으로 기록되며, 이후에 복구할 수 있습니다 ([무결성 및 복구](#integrity-and-recovery) 참고).



<br>



#### **스트림 연속성 보장**

Stream Receiver는 네트워크 연결 끊김, API rate limit, 거래소 측 스트림 중단 등으로 인해 발생하는 WebSocket 데이터의 시간적 공백을 지속적으로 감시합니다. 공백이 감지되면 누락된 구간을 fetch하여 순서대로 스트림에 다시 병합하며, 복구할 수 없는 구간만 더미 데이터로 채웁니다. 하위 데이터 소비자 입장에서는 복잡한 공백 복구 로직을 구현할 필요 없이, 삽입된 더미 데이터 항목만 적절히 처리하면 됩니다.

> 상세한 복구 체계는 [무결성 및 복구](#integrity-and-recovery) 섹션에서 다룹니다.



<br>



#### **Data Requester별 분산 서브 파이프라인**

각 Data Requester(Analyzer, Simulator, GUI, Trade Manager)는 Data Manager 내부의 중앙 집중식 집계 서비스에 의존하지 않고, **독립적인 자체 서브 파이프라인** — Aggregated Base Stream Receiver, Internal Fetch Request Generator, Secondary Aggregator, Task Handler — 을 유지합니다. 이는 다음 세 가지 문제를 해결하기 위한 의도적인 설계입니다.

* **다양한 타임프레임 동시 요구** — 요청자마다 동시에 필요로 하는 타임프레임이 다릅니다. 예를 들어 5분봉을 모니터링하는 Analyzer와 4시간봉으로 백테스트하는 Simulator가 동시에 실행될 수 있습니다. 중앙 집중식 집계를 사용하면 Data Manager가 심볼 및 소비자별로 N개의 타임프레임 파이프라인을 병렬로 유지해야 하므로, 상당한 조정 오버헤드가 발생합니다.
* **Data Manager의 책임 최소화** — 집계를 소비자 측에 둠으로써, Data Manager의 책임은 영구 저장, 구간 비교, fetch 조정이라는 세 가지에 집중됩니다. 태스크별 타임프레임 로직은 있어야 할 곳, 즉 태스크 바로 옆에 위치하게 됩니다.
* **독립적인 생명주기** — 각 요청자가 자체 상태를 유지하므로, 특정 Data Requester가 실패하거나 재시작하더라도 다른 요청자의 파이프라인에는 영향을 주지 않습니다.



<br>



#### **버퍼 기반 영구 저장과 TimescaleDB**

Data Manager는 수신 데이터를 메모리에 누적한 뒤 배치 단위로 데이터베이스에 기록합니다. 스트림 데이터는 5초마다, fetch한 과거 데이터는 최대 10,000행 단위로 기록됩니다. 이 방식은 트랜잭션당 오버헤드를 줄이고, 갑작스러운 데이터 유입 급증을 완화합니다.

영구 저장소로는 PostgreSQL의 시계열 확장인 **TimescaleDB** 를 사용합니다. 이 선택의 가장 큰 이점은 시간 기반 네이티브 압축으로 스토리지 비용을 크게 줄일 수 있다는 점입니다. 실제 운용 환경에서는 약 98GB의 원본 시장 데이터가 약 21GB로 압축되었습니다 (약 78% 절감).



<br>



#### ⚠️ **저장장치에 대한 참고 사항**

**TimescaleDB** 를 선택하는 것으로 스토리지에 대한 결정이 끝나는 것은 아닙니다. **PostgreSQL 데이터 디렉토리를 호스팅하는 물리적 드라이브** 도 중요하며, 겉으로 잘 드러나지 않는 방식으로 문제가 생기기 전까지 간과하기 쉬운 부분이라 특별히 짚고 넘어갈 필요가 있습니다.

데이터베이스 워크로드, 특히 PostgreSQL은 B-tree 인덱스 갱신과 동시 트랜잭션으로 인해 지속적인 랜덤 I/O 패턴을 만들어냅니다. 반면 최근 소비자용 HDD는 순차 쓰기에 최적화된 트랙 구조를 가진 **SMR (Shingled Magnetic Recording)** 방식으로 출하되는 경우가 늘고 있습니다. SMR 드라이브에서 랜덤 쓰기가 발생하면 펌웨어 내부에서 비용이 큰 read-modify-write 사이클이 실행됩니다. 지속적인 데이터베이스 부하가 걸리면 이는 지연된 장애 형태로 나타납니다. 초기 데이터 누적 단계에서는 정상적으로 동작하지만, 드라이브 캐시가 소진되는 순간 I/O 처리 속도가 급격히 떨어집니다. 이 극단적인 지연은 내부 데이터 큐의 병목과 누락을 일으키고, 결국 인덱스 손상 에러로 이어집니다. 애플리케이션 버그처럼 보이지만, 실제 원인은 물리적 스토리지 계층에 있습니다.

지속적인 시장 데이터 수집을 수행하는 ATM-Eta 환경에서는 PostgreSQL 데이터 디렉토리를 **CMR (Conventional Magnetic Recording) HDD**, 가급적이면 **SSD** 에 두는 것을 강력히 권장합니다.

Data Manager에는 이 장애 유형에 대한 완화 장치가 포함되어 있습니다. 데이터베이스가 I/O 대기 중일 때는 쓰기를 미루고, 인덱스 손상이 감지되면 자동으로 `REINDEX` 를 시도합니다. 다만 이는 증상을 완화할 뿐이며, 적절한 저장장치를 대체하지는 못합니다.

---



<a name="integrity-and-recovery"></a>
### 🛡️ 무결성 및 복구 ###

#### **1. AAF (Account Activation File) 시스템**

**ACTUAL** 계정을 활성화하려면 Binance API Key와 Secret Key가 필요합니다. 매 실행마다 이를 직접 입력하는 것은 번거롭고 실수하기 쉬우며, 평문 설정 파일에 저장하면 실제 주문을 넣을 수 있는 자격 증명이 노출됩니다. **AAF (Account Activation File)** 시스템은 이 트레이드오프를 해결합니다. 키를 계정 비밀번호에서 유도한 키로 암호화하여 이동 가능한 파일로 저장하므로, 파일과 비밀번호만으로 계정을 다시 활성화할 수 있습니다.

<br>

 🔹 **생성**

1. 사용자가 **Accounts** 페이지에서 API Key, Secret Key, 계정 비밀번호를 입력합니다.
2. Trade Manager가 먼저 저장된 **bcrypt** 해시로 비밀번호를 검증합니다. 검증에 성공한 경우에만 AAF 생성이 진행됩니다.
3. 16바이트 랜덤 salt를 생성하고, **scrypt** (`n = 2^17`, `r = 8`, `p = 1`)로 비밀번호에서 32바이트 암호화 키를 유도합니다.
4. 두 키를 **Fernet** (AES-128-CBC + HMAC-SHA256)으로 암호화하여 KDF 파라미터와 함께 `data/{localID}.aaf` 에 저장합니다. 키 입력란은 저장 직후 비워집니다.

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

 🔹 **활성화**

1. **ACTIVATE BY AAF** 를 누르면, GUI가 마운트된 모든 드라이브의 루트 디렉토리와 프로젝트의 `data/` 폴더에서 `.aaf` 파일을 탐색합니다. 이동식 드라이브도 탐색 대상에 포함되므로, AAF를 USB 드라이브에 보관하다가 활성화가 필요할 때만 연결해서 쓸 수 있습니다.
2. 같은 계정의 AAF가 여러 개 있으면, 가장 최근에 생성된 파일(`generationTime_ns` 기준)이 선택됩니다.
3. 암호화된 키와 KDF 파라미터는 Trade Manager로 전달되며, Trade Manager는 비밀번호를 다시 검증하고 저장된 파라미터로 키를 재유도한 뒤 자격 증명을 **메모리 안에서만** 복호화합니다.
4. 복호화된 키는 Binance API Manager로 전달되며, 거래소를 통해 검증(Futures 권한, Binance UID 일치)을 거친 뒤에야 계정이 `ACTIVE` 로 전환됩니다.

<br>

 🔹 **보안 특성**

* **디스크에 평문 없음** — API 자격 증명은 암호화되지 않은 상태로 디스크에 기록되지 않습니다. 평문은 활성화 과정 중 프로세스 메모리 안에만 존재합니다.
* **무차별 대입 공격 저항성** — scrypt의 메모리 집약적 키 유도(현재 파라미터 기준 시도당 약 128MB)로 인해, 유출된 AAF에 대한 오프라인 비밀번호 추측 비용이 매우 커집니다.
* **변조 감지** — Fernet은 모든 토큰을 인증하므로, 변조되거나 손상된 AAF는 엉뚱한 자격 증명을 만들어내는 대신 복호화에 실패합니다.
* **자격 증명-계정 결합** — 유효한 AAF라도, 키가 등록된 계정과 다른 Binance 계정의 것이라면 활성화에 실패합니다 (`UIDMISMATCH`).



<br><br><br>



#### **2. 계정-거래소 상태 대조**

Trade Manager가 보유한 계정 모델과 Binance의 실제 계정 상태는 여러 이유로 어긋날 수 있습니다. 이전 세션에서 남은 주문, 주문 응답보다 먼저 나타나는 체결, 사용자가 직접 넣은 거래, 네트워크 오류로 결과를 알 수 없게 된 요청 등이 그 예입니다. ATM-Eta는 거래소를 단일 진실 공급원(single source of truth)으로 삼아, 활성화 시점, 모든 계정 스냅샷, 개별 주문이라는 세 지점에서 대조를 수행합니다.

<br>

 🔹 **활성화 시**

* 계정이 `ACTIVE` 로 전환되기 전에, Binance API Manager는 모든 미체결 주문을 조회하여 `clientOrderId` 가 `ATMETA` 로 시작하는 주문을 취소합니다. `ATMETA` 는 ATM-Eta가 넣는 모든 주문에 붙는 접두사입니다. 이전 세션의 주문은 더 이상 추적되지 않기 때문에, 그대로 두면 시스템이 파악할 수 없는 체결이 발생할 위험이 있습니다. 사용자가 직접 넣은 주문은 건드리지 않습니다.
* 이미 사라진 주문(`-2011`)은 정리된 것으로 간주합니다. 그 외의 취소 실패가 발생하면, 알 수 없는 상태에서 시작하는 대신 활성화를 중단합니다 (`OPENORDERCLEARFAILED`).
* 이전 세션의 추적 상태는 양쪽 모두에서 폐기됩니다. Binance API Manager는 주문 추적기를 비우고, Trade Manager는 진행 중인 주문 요청과 대기 중인 trade handler를 정리합니다.
* 비활성화 시에도 같은 정리가 최선의 노력(best-effort) 방식으로 실행됩니다. 실패하면 다음 활성화 때 다시 시도됩니다.

<br>

 🔹 **스냅샷 동기화**

* 계정 스냅샷은 적응형 주기로 REST를 통해 조회되며 ([API Rate Limit 처리](#api-rate-limit-handling) 참고), 활성화 직후에는 즉시 한 번 조회됩니다.
* 마진, 미실현 손익, 레버리지, 마진 타입은 항상 거래소 값으로 덮어씁니다. 포지션 수량과 진입가는 진행 중인 주문이 없을 때만 덮어쓰며, 그렇지 않으면 먼저 수량 변화의 원인을 설명해야 합니다.
  * 진행 중인 주문이 보고한 체결량과 일치하는 변화는 해당 주문의 거래로 기록됩니다.
  * 활성 주문의 미체결 수량 범위 안에 들어오지만 주문 응답이 아직 도착하지 않은 변화는 보류되었다가, 응답이 도착하면 해당 주문에 귀속됩니다.
  * 그 외의 나머지 변화는 **Unknown Trade** 로 처리됩니다. `UNKNOWN` 으로 기록되고 trade control 상태가 초기화되며, *Stop Trade On Unknown Trade* 가 켜져 있으면(기본값) 해당 포지션의 거래가 중단됩니다 (사용자 개입이나 청산이 발생한 것으로 간주).
* 다른 형태의 불일치는 해소될 때까지 포지션을 거래 불가 상태로 만듭니다.
  * ATM-Eta 주문이 없는데 미체결 주문 마진이 20초 이상 유지되면, 외부에서 넣은 주문으로 판단합니다.
  * 레버리지나 마진 타입이 Trade Configuration과 다른 경우입니다. 포지션이 비어 있고 미체결 주문이 없으면 수정 요청이 자동으로 전송됩니다.
* 재시작 후에는 열린 포지션의 할당 잔고가 복원되며, 총합이 할당 가능 잔고를 초과하면 비례적으로 축소됩니다.

<br>

 🔹 **주문 상태 검증**

| 상황 | 처리 |
| :--- | :--- |
| 명확한 거절 | 실패로 보고됩니다. Trade Manager가 주문을 재생성할 수 있습니다 (최대 5회) |
| 모호한 결과 (타임아웃, 네트워크 오류, 서버 측 에러 `-1000`/`-1001`/`-1006`/`-1007`/`-1008`, 파싱 불가능한 응답) | *미확인* 상태로 등록되고 `clientOrderId` 로 매초 조회합니다. 무작정 재시도하지 않습니다 |
| 미확인 주문이 서버에서 발견됨 | 확인 처리 후 정상적으로 추적합니다 |
| 미확인 주문이 끝내 발견되지 않음 (연속 600회 확인, 약 10분) | `NOTPLACED` 로 보고됩니다. 안전하게 재생성할 수 있습니다 |
| 이전에 확인된 주문이 사라졌거나, 확인이 계속 실패함 | `ORDERSTATEUNKNOWN` 으로 보고됩니다. 재생성 **없이** 종료되며, 수동 확인이 권장됩니다 |
| 주문이 이미 호가창에 없어서 취소가 거절됨 (`-2011`) | 주문의 최종 상태를 조회하여, 취소 직전에 발생한 체결도 기록합니다 |

대기 중인 주문은 진행 상황을 주기적으로 조회하며, 체결 수량이 늘어나거나 주문이 최종 상태에 도달했을 때만 Trade Manager에 업데이트를 전달합니다.



<br><br><br>



<a name="api-rate-limit-handling"></a>
#### **3. API Rate Limit 처리**

Binance는 IP 단위로 요청 가중치(request weight)와 주문 횟수에 제한을 두며, 이를 초과하면 요청이 거절되고 결국 일시적인 IP 차단으로 이어집니다. 시장 데이터 백필, 계정 조회, 주문 실행이 모두 같은 IP를 공유하기 때문에, ATM-Eta는 사용량을 로컬에서 추적하고 우선순위에 따라 예산을 분배합니다.

<br>

 🔹 **로컬 사용량 추적**

* 제한값은 하드코딩하지 않고 런타임에 거래소 정보에서 읽어오며, 거래소가 보고하는 모든 `REQUEST_WEIGHT` 및 `ORDERS` 윈도우를 반영합니다.
* 모든 요청은 전송 전에 자신의 가중치를 선언하고, 해당 제한 타입의 모든 윈도우와 비교됩니다. 하나라도 초과하게 되면 요청을 보내지 않습니다. 카운터는 윈도우 경계에서 초기화됩니다.
* **보수적인 시작** — 실행 전의 사용량은 알 수 없으므로, 각 윈도우의 추적값은 모두 소진된 상태로 시작합니다. 예산은 다음 윈도우 경계에서 열립니다.
* **IP 공유** — 여러 인스턴스가 같은 IP를 사용하는 경우, `rateLimitIPSharingNumber` (1–5)로 예산을 나눕니다.

<br>

 🔹 **우선순위 기반 예산 예약**

* 시장 데이터 fetch는 대량이면서 미룰 수 있는 작업이므로, 시간에 민감한 작업을 위한 여유분을 먼저 예약한 뒤 남은 예산만 사용할 수 있습니다.
  * 기본 여유분으로 초당 가중치 1
  * 활성화된 계정당 초당 가중치 5 (계정 조회)
  * 추적 중인 주문당 초당 가중치 1 (주문 검증)
* fetch가 거절되거나 실패하면, 매 루프마다 재시도하는 대신 다음 윈도우 초기화 시점까지 모든 시장 데이터 fetch를 중단합니다.
* 주문 생성과 취소는 `ORDERS` 제한을 사용합니다. 제한에 도달하면 요청을 대기열에 넣지 않고 즉시 거절하며 (`APIRATELIMITREACHED`), 재시도 판단은 Trade Manager에 맡깁니다.

<br>

 🔹 **적응형 계정 조회**

* 계정 조회 주기는 활성화된 계정 수에 따라 조정되어, 조회가 가중치 예산의 최대 약 50%만 사용하도록 합니다 (10% 여유 포함). 조회 주기는 1초보다 짧아지지 않습니다.
* 활성화할 수 있는 계정 수는 가장 느린 조회 주기(10초)에서도 조회가 50% 안에 머물도록 제한됩니다. 예를 들어 현재 분당 2,400의 가중치 제한에서는 최대 36개 계정까지 활성화할 수 있습니다.



<br><br><br>



#### **4. 서버 연결 끊김 복구**

 🔹 **연결 모니터링**

* Binance API Manager는 매초 네트워크 연결 가능 여부와 Binance 시스템 상태(정상 / 점검)를 확인합니다. 거래소에 의존하는 모든 작업은 두 확인이 모두 통과한 동안에만 실행됩니다.
* 서버를 사용할 수 없는 동안 Trade Manager로부터 도착한 요청은 대기시키지 않고 즉시 거절합니다 (`SERVERUNAVAILABLE`).

<br>

 🔹 **연결이 끊겼을 때**

* 오래된 상태가 되었을 수 있는 모든 것을 폐기합니다. API 클라이언트, 캐시된 거래소 정보, rate limit 테이블, 모든 WebSocket 연결, 심볼별 스트림 상태가 여기에 해당합니다.
* 스트림 구독 정보(어떤 프로세스가 어떤 심볼을 구독하는지)는 심볼별로 백업됩니다.
* 활성화된 계정과 주문 추적기는 유지되며, 재연결 후 주문 검증이 재개됩니다.

<br>

 🔹 **재연결되었을 때**

* 거래소 정보를 다시 읽어옵니다. 심볼 캐시가 비워진 상태이므로, 모든 심볼이 새로 상장된 것으로 간주되어 다시 등록되고 스트리밍 대기열에 들어갑니다.
* 스트림 상태는 처음부터 다시 구성되며, 구독 정보는 백업에서 복원되므로 구독자가 다시 등록할 필요가 없습니다.
* 각 스트림의 첫 메시지가 재동기화를 트리거합니다. `depth` 는 새 호가창 스냅샷을 받고, `aggTrade` 는 현재 인터벌의 시작부터 백필하며, metric 조회가 다시 시작됩니다.
* 끊겨 있던 기간의 공백은, 연결이 끊겨도 연속성 상태가 초기화되지 않는 Data Manager가 감지하여 자동으로 백필합니다 ([시장 데이터 공백 감지](#market-data-gap-detection) 참고).
* rate limit 테이블은 동일한 보수적 시작 정책으로 다시 초기화됩니다.

<br>

 🔹 **WebSocket 연결 생명주기**

* 심볼은 연결당 50개씩 묶이며, 심볼당 3개의 스트림을 사용하므로 Binance가 권장하는 연결당 200개 스트림의 75%를 사용합니다.
* **Make-before-break 갱신** — 4시간마다 각 연결은 만료 처리되고, 해당 심볼들은 새 연결 대기열에 들어갑니다. 기존 연결은 새 연결이 모든 심볼에 대해 `kline`, `depth`, `aggTrade` 메시지를 전달한 뒤에야 종료됩니다. 겹치는 기간에 받은 중복 메시지는 스트림 연속성 검사에서 걸러집니다.
* 연결 생성은 최대 3회까지 재시도되며, 그래도 실패하면 심볼들을 다시 대기열에 넣습니다.
* 메시지 큐 오버플로나 예상치 못한 WebSocket 오류가 발생하면 모든 연결을 종료하고 다시 생성합니다.
* Binance Vision 다운로드는 5xx 오류 시 지수 백오프로 재시도합니다 (최대 5회).



<br><br><br>



<a name="market-data-gap-detection"></a>
#### **5. 시장 데이터 공백 감지**

공백 감지는 두 계층에서 동작합니다. Binance API Manager의 Stream Receiver는 메시지 수준의 연속성을 실시간으로 검증하고, Data Manager는 실제로 저장되는 데이터의 인터벌 수준 연속성을 검증합니다. Data Manager의 상태는 스트림이 재설정되어도 유지되므로, 서버 장애 기간처럼 첫 번째 계층이 볼 수 없는 공백도 감지할 수 있습니다.

 🔹 **계층 1: Stream Receiver (메시지 수준)**

| 스트림 | 연속성 검사 | 공백 발생 시 |
| :--- | :--- | :--- |
| `kline` | 이벤트 시간이 증가해야 하며, 새 kline은 직전에 마감된 kline으로부터 정확히 한 인터벌 뒤에 시작해야 합니다 | 누락 구간을 fetch합니다 (가능하면 Binance Vision 아카이브, 그 외에는 REST) |
| `depth` | 각 변경분의 `pu` 가 직전 변경분의 `u` 와 같아야 합니다 | REST 호가창 스냅샷(1000단계)을 받고, 스냅샷의 `lastUpdateId` 이후 버퍼에 쌓인 변경분을 재적용합니다. 버퍼가 여전히 불연속이면 다시 받습니다 |
| `aggTrade` | 집계 체결 ID가 정확히 1씩 증가해야 합니다 | 누락된 ID 구간을 REST로 fetch합니다. 첫 메시지에서는 현재 인터벌 시작부터 체결을 백필합니다 |
| `metric` | 내부적으로 생성된 1분 스트림의 시작 시간 연속성 | 누락 구간을 REST로 fetch합니다 (최근 28일 이내) |

공백 fetch가 진행되는 동안 실시간 메시지는 버리지 않고 버퍼에 보관합니다. fetch한 데이터는 버퍼에 순서대로 병합되므로, 하위 소비자는 연속적이고 순서가 보장된 스트림을 받게 됩니다.

<br>

 🔹 **계층 2: Data Manager (인터벌 수준)**

* Data Manager는 마감된 인터벌만 받으며, 심볼과 데이터 타입별로 마지막 시작 시간을 추적합니다. 다음 인터벌이 정확히 한 인터벌 뒤에 시작하지 않으면, 누락 구간에 대한 fetch 요청을 보냅니다. 오래되었거나 중복된 인터벌은 폐기합니다.
* 저장 범위는 심볼과 데이터 타입별로 `descriptors` 테이블에 두 개의 구간 집합으로 관리됩니다. **available ranges** (처리된 인터벌)와 **dummy ranges** (데이터를 복구할 수 없었던 인터벌)입니다.
* 과거 데이터 수집이 켜져 있으면, 백필 대상은 심볼의 최초 상장 시점부터 첫 스트림 인터벌까지의 구간에서 available ranges를 뺀 범위입니다.
* 저장되었거나 버퍼에 있는 구간과 겹치는 fetch 결과는 거절되며, fetch 대상이 다시 계산됩니다.

<br>

 🔹 **명시적 데이터 출처 표기**

모든 인터벌에는 출처 태그가 붙으며, 태그에 따라 저장 방식이 결정됩니다.

| 태그 | 의미 | 저장 여부 |
| :--- | :--- | :--- |
| `FETCHED` | REST 또는 Binance Vision에서 가져온 데이터 | 저장 |
| `STREAMED` | WebSocket으로 수신한 데이터 | 저장 |
| `EMPTY` | 존재해야 하지만 거래소가 반환하지 않은 데이터 | 저장 (null 값 행으로) |
| `DUMMY` | 복구할 수 없는 공백을 채운 자리표시자 | 저장하지 않음, dummy ranges에 기록 |
| `INCOMPLETE` | 재동기화로 인해 중간에 끊긴 인터벌 | 저장하지 않음, dummy ranges에 기록 |

소비자가 데이터베이스에서 구간을 읽을 때, 저장된 행이 없는 시점은 `DUMMY` 자리표시자로 반환되므로 소비자는 항상 빈틈없이 균등한 간격의 시계열을 받게 됩니다.

<br>

 🔹 **더미 구간 복구**

더미 구간은 영구적이지 않으며, 두 가지 방법으로 복구할 수 있습니다.

* **재요청 (Refetch)** — 더미 구간을 Binance에 다시 요청합니다. 해당 구간을 포함하는 Binance Vision 일별 아카이브가 공개된 이후에 유용합니다. 실제 데이터만 더미 구간을 대체합니다.
* **로컬 네트워크 가져오기** — 로컬 네트워크에 있는 다른 ATM-Eta 인스턴스의 데이터베이스에서 데이터를 가져올 수 있습니다. 가져오기 대상은 로컬 더미 구간 중 원격 인스턴스가 실제로 저장하고 있는 구간(원격 available ranges에서 원격 dummy ranges를 뺀 범위)입니다.

재요청과 가져오기 결과는 서로의 구간을 제외하므로, 같은 데이터가 두 번 삽입되지 않습니다.

<br>

 🔹 **아카이브 무결성**

모든 Binance Vision 파일은 사용 전에 SHA-256 `.CHECKSUM` 으로 검증됩니다. 일치하지 않는 파일은 폐기되고 다시 내려받습니다.



<br><br><br>



#### **6. 데이터베이스 쓰기 무결성**

* **배치 단위 트랜잭션 쓰기** — 스트림 데이터는 5초마다, fetch한 데이터는 최대 10,000행 단위로 기록됩니다. 데이터 행과 이에 대응하는 `descriptors` 테이블의 구간 갱신은 같은 트랜잭션으로 커밋되므로, 저장 범위 메타데이터와 실제 저장된 행이 항상 함께 변경됩니다.
* **중복 방지** — 이미 저장된 구간과 겹치는 스트림 데이터는 삽입 전에 폐기됩니다.
* **역압 (Backpressure)** — fetch한 데이터 버퍼가 14,400행(1분 데이터 10일치)에 도달하면 Binance API Manager에 fetch 일시 중지를 요청하고, 버퍼가 기준 아래로 줄어들면 재개합니다.
* **I/O 인지 스케줄링** — 데이터베이스 백엔드 중 하나라도 I/O 대기 중이면 해당 쓰기 주기를 건너뛰어, 이미 포화된 드라이브에 쓰기를 쌓지 않고 미룹니다.
* **압축된 과거 데이터에 쓰기** — TimescaleDB 청크는 7일이 지나면 압축됩니다. 압축된 청크를 대상으로 하는 백필 데이터는 영향받는 청크만 압축을 풀고, 삽입한 뒤, 다시 압축합니다. 재압축 실패는 치명적이지 않으며, 이후 압축 정책이 해당 청크를 다시 처리합니다.
* **자동 인덱스 복구** — 인덱스 손상 에러가 발생하면 트랜잭션을 롤백하고, 에러 메시지에서 손상된 인덱스를 찾아 `REINDEX` 로 재구성하며, 버퍼에 남아 있는 fetch 데이터는 다음 주기에 기록합니다.

---



### 📊 다중 시간대 분석 ###

아래 다이어그램은 ATM-Eta가 베이스 집계된 1분 시장 데이터를 다중 시간대 분석 파이프라인을 거쳐 하나의 실행 가능한 트레이딩 신호로 변환하는 과정을 나타냅니다. 전체 흐름은 두 개의 협력 모듈로 나뉩니다. 여러 타임프레임에 걸쳐 정형화된 신호를 추출하는 **Analyzer**, 그리고 추출된 신호를 사용자 정의 전략을 통해 구체적인 포지션 목표로 변환하는 **Trade Manager** 입니다.

이 설계의 핵심 전제는 다음과 같습니다. 시스템을 특정 타임프레임 하나에 고정하는 대신, 활성화된 모든 타임프레임에 대해 동일한 분석을 독립적으로 수행하고 그 결과 전체를 사용자 전략에 노출합니다. 어떤 타임프레임이 중요한지, 그리고 이를 어떻게 조합할지는 전략이 직접 결정합니다.

<img src="./docs/mtfanalysis.png" width="800">

#### **타임프레임별 분석**

Secondary Aggregator는 베이스 집계된 1분 시장 데이터를 활성화된 타임프레임 전체(1m, 3m, 5m, 15m, ..., 1M)로 확장하며, 각 타임프레임은 독립적인 분석 트랙을 가집니다. 각 트랙은 자신의 **Currency Analysis Configuration** — 어떤 분석(SMA, PSAR, MMACD, IVP, WOI, NES 등)을 어떤 파라미터로 적용할지에 대한 선언적 명세 — 에 따라 동작하며, 자신만의 **Analysis Results** 번들을 생성합니다.
같은 지표를 타임프레임마다 다르게 설정할 수 있어, 전략은 관심 있는 신호의 빠른 버전과 느린 버전 모두에 접근할 수 있습니다.

<br>

#### **분석 평탄화 (Analysis Linearization)**

이후 분석 번들들은 **Analysis Linearizer** 를 거쳐 하나의 평탄한 딕셔너리인 **Linearized Analysis** 로 합쳐지며, 이 과정에서 (타임프레임, 분석 코드, 하위 필드) 조합 각각이 고유한 최상위 키로 매핑됩니다.

이 단계가 존재하는 이유는 하나입니다. **전략 작성 편의성** 입니다. `{interval: {analysisCode: {...}}}` 형태의 중첩 구조는 사용자 전략 코드가 분석기의 내부 구조를 알고 직접 순회하도록 강제하며, 모든 전략을 분석기의 내부 표현에 결합시킵니다. 반면 평탄한 딕셔너리는 전략이 필요한 신호를 딕셔너리 조회 한 번으로 참조할 수 있게 하여, 다중 시간대 분석 전체를 균일한 키-값 네임스페이스로 다룰 수 있게 합니다. 부수적인 이점으로, 이 평탄한 형태는 오프라인 분석 export를 위해 그대로 직렬화할 수 있습니다. TEFFP Seeker가 사용하는 데이터셋의 모든 컬럼은 평탄화된 딕셔너리의 키 하나에 정확히 대응하므로, ATM-Eta(CPU)와 TEFFP Seeker(GPU 가속) 사이의 스키마 변환이 최소화됩니다.

<br>

#### **TEF 기반 전략 분리**

Analyzer와 Trade Manager 사이의 경계는 이 아키텍처에서 가장 의도적으로 설계된 부분입니다. Analyzer의 책임은 Linearized Analysis를 산출하는 데서 끝납니다. 이후 Trade Manager는 사용자가 작성한 Python 모듈에서 가져온 **사용자 정의 TEF 함수** 를 호출하며, 이 함수는 Linearized Analysis를 입력받아 목표 노출도를 반환합니다. 목표 노출도는 방향(`LONG` / `SHORT` / 없음)과 `[-1.0, +1.0]` 범위의 TEF 값으로 구성되며, 값의 크기가 상대적 포지션 크기를 결정합니다. 이후 **trade handler** 가 포지션의 **commitment rate** 를 이 목표에 맞춰 유지하며, 둘 사이에 차이가 생길 때만 주문을 실행합니다 (*Trade Configuration* 참고).

이러한 분리는 세 가지 구체적인 이점을 제공합니다.

* **전략 교체 용이성** — 전략을 바꾸려면 다른 TEF 함수 파일을 지정하기만 하면 됩니다. Analyzer, 데이터 파이프라인, 주문 실행 경로는 그대로 유지됩니다.
* **CPU와 GPU 간 이식성** — TEFFP Seeker는 GPU 가속을 위해 전략을 Triton 커널로 다시 작성해야 하지만, TEF 인터페이스 계약(Linearized Analysis 입력, 목표 노출도 출력)은 양쪽에서 동일하게 유지됩니다.
* **유계의 정규화된 전략 인터페이스** — 모든 전략이 `[-1.0, +1.0]` 범위의 값을 출력하도록 계약상 강제되므로, 하위의 포지션 사이징, 레버리지 할당, 리스크 관리 로직은 한 번만 작성하면 전략 내부 로직의 복잡도와 무관하게 모든 전략에서 재사용할 수 있습니다.

---



### 🧠 트레이드 로직 파이프라인 ### 
<img src="./docs/tradestrategy_0.png" width="1000">

ATM-Eta의 트레이딩 전략은 세 가지 설정으로 정의됩니다. 무엇을 분석할지 정하는 **Currency Analysis Configuration**, TEF 결정을 어떻게 주문으로 바꿀지 정하는 **Trade Configuration**, 그리고 각 포지션이 얼마의 자본을 쓸 수 있는지 정하는 **Account Control** 설정입니다. 원본 시장 데이터에서 출발하여, 이 설정들이 함께 거래소로 전송될 주문 요청을 결정합니다.

* <Details>
  <Summary><b><i> Currency Analysis Configuration </b></i></Summary>

  MA, PSAR, Bollinger Bands 같은 표준 기술적 분석 도구 외에도, ATM-Eta에는 여러 하이브리드 분석 모듈이 기본으로 포함되어 있습니다. 그중 대표 예시로 **IVP**, **MMACD**, **DMIxADX**, **MFI** 네 가지를 아래에서 소개합니다.

  분석 결과는 평탄화된 뒤, 포지션에 지정된 Trade Configuration의 TEF 함수로 전달됩니다 (*다중 시간대 분석* 참고).

  * <Details> 
    <Summary><b><i> IVP (Interpreted Volume Profile) </b></i></Summary>

    **IVP** 모듈은 널리 사용되는 **VPVR (Volume Profile Visible Range)** 지표를 개념적 기반으로 합니다. 특정 가격대별 거래량을 집계하여 볼륨 프로파일을 구성한 뒤, 필터링 알고리즘으로 노이즈를 제거하고 핵심적인 구조적 가격대를 찾아냅니다.

    <img src="./docs/ivp0.png" width="750">

    아래 표는 IVP의 설정 파라미터입니다.  
    | 파라미터    | 설명 |
    | :--- | :---  |
    | Interval     | 초기 볼륨 프로파일을 구성하는 데 필요한 최소 샘플 수를 정의합니다. 이보다 오래된 데이터도 **제외되지 않고 유지** 되어, 누적 프로파일이 만들어집니다 |
    | Gamma Factor | 볼륨 프로파일 버킷의 세밀도(세로 분할 높이)를 조절합니다 |
    | Delta Factor | 노이즈 필터링의 강도를 결정합니다 |
    <br>

    <img src="./docs/ivp1.png" width="750">

    위 이미지는 오른쪽의 필터링된 볼륨 프로파일(**VPLP**)과, 이를 통해 식별된 주요 지지/저항선(**VPLPB**)을 보여줍니다.

    </Details>

  * <Details> 
    <Summary><b><i> MMACD (Multi Moving Average Convergence and Divergence) </b></i></Summary>
    
    이름에서 알 수 있듯이 **MMACD** 는 표준 MACD (Moving Average Convergence Divergence) 지표를 확장한 것입니다. 두 개의 이동평균만 비교하는 기존 MACD와 달리, MMACD는 최대 6개의 서로 다른 이동평균 간의 관계를 추적합니다.

    또한 MMACD에는 **Kline Interval Multiplication** 이라는 실험적 기능이 있습니다. 기반 데이터 스트림을 바꾸지 않고 상위 타임프레임 분석을 흉내 낼 수 있는 기능으로, 예를 들어 `15m` 도메인에서 배수를 `4` 로 설정하면 사실상 `1h` (15m × 4) 타임프레임 분석과 같은 효과를 냅니다. 이 다중 시간대 기능을 활용하기 위해 **MMACDSHORT** 와 **MMACDLONG** 두 개의 인스턴스를 사용합니다.

    <img src="./docs/mmacd0.png" width="750">

    아래 표는 MMACD의 설정 파라미터입니다.  
    | 파라미터       | 설명 |
    | :---            | :--- |
    | Signal Interval | 시그널 라인 계산에 사용하는 샘플링 기간 |
    | Multiplier      | 시간 도메인 배수. 상위 타임프레임 분석을 흉내 내는 데 사용됩니다 (예: 15m 데이터에 배수 4 ≈ 1h 데이터) |
    | MA Interval     | 이동평균의 기본 기간 |
    <br>

    <img src="./docs/mmacd1.png" width="750">

    위 이미지는 MMACD 분석의 실제 차트 데이터를 보여줍니다.

    </Details>

  * <Details> 
    <Summary><b><i> DMIxADX (Directional Movement Index and Average Directional Index) </b></i></Summary>
    
    이 하이브리드 지표는 두 가지 표준 기술적 분석 도구를 결합합니다.  
    **DMI (Directional Movement Index):** 시장 추세의 방향(상승/하락)을 식별합니다.  
    **ADX (Average Directional Index):** 방향과 무관하게 추세의 강도를 식별합니다.  
    두 지표를 결합함으로써 시장 움직임의 방향과 강도를 함께 평가할 수 있습니다.
    
    **ATH (All-Time-High) 상대 표현**  
    이 지표들의 원시 값은 편차가 커서 자동화 시스템이 해석하기 모호할 수 있습니다. 이를 해결하기 위해 본 애플리케이션은 **ATH 상대 표현** 을 사용합니다. 출력을 과거 최댓값 기준으로 정규화하여, 자산과 타임프레임에 관계없이 일관된 표준화된 강도 지표를 제공합니다.

    <img src="./docs/dmixadx0.png" width="750">

    아래 표는 DMIxADX의 설정 파라미터입니다.  
    | 파라미터 | 설명 |
    | :---      | :--- |
    | Interval  | 신호 계산에 사용하는 샘플 수 |
    <br>

    <img src="./docs/dmixadx1.png" width="750">

    위 이미지는 DMIxADX 분석의 실제 차트 데이터를 보여줍니다.

    </Details>

  * <Details> 
    <Summary><b><i> MFI (Money Flow Index) </b></i></Summary>

    **MFI (Money Flow Index)** 는 가격과 거래량 데이터를 결합하여 매수·매도 압력을 측정하는 모멘텀 오실레이터입니다. **DMIxADX** 모듈과 마찬가지로 **ATH (All-Time-High) 상대 표현** 을 사용하여, 과거 최댓값 기준으로 출력을 정규화함으로써 자동화 시스템이 해석하기 쉬운 표준화된 지표를 제공합니다.

    <img src="./docs/mfi0.png" width="750">

    아래 표는 MFI의 설정 파라미터입니다.  
    | 파라미터 | 설명 |
    | :---:     | :--- |
    | Interval  | 신호 계산에 사용하는 샘플 수 |
    <br>

    <img src="./docs/mfi1.png" width="750">

    위 이미지는 MFI 분석의 실제 차트 데이터를 보여줍니다.

    </Details>

  
  </Details>

* <Details>
  <Summary><b><i> Trade Configuration </b></i></Summary>
  <img src="./docs/tradecontrol.png" width="750" height="440">

  **Trade Configuration (TC)** 은 포지션이 TEF 결정을 주문으로 바꾸는 방식을 정의합니다. 어떤 전략을 실행할지, 주문 크기와 방식을 어떻게 정할지, 언제 손절할지가 여기에 포함됩니다. 각 포지션에는 하나의 TC가 지정됩니다.

  | 파라미터 | 설명 |
  | :--- | :--- |
  | TEF Function | 전략 함수의 종류와 파라미터. 방향(`LONG` / `SHORT` / 없음)과 `[-1.0, +1.0]` 범위의 TEF 값을 반환합니다 |
  | Leverage | 포지션에 적용할 레버리지 |
  | Margin Type | `ISOLATED` 또는 `CROSSED` |
  | Direction | 허용할 진입 방향: `BOTH`, `LONG`, `SHORT` |
  | Order Type | `MARKET`, `LIMIT` (post-only, maker 수수료율로 체결), 또는 `ADAPTIVE` (기본적으로 post-only 지정가를 사용하되, 포지션을 청산해야 할 때는 시장가로 전환) |
  | Order Offset | `LIMIT` 및 `ADAPTIVE` 주문에서 현재가 대비 주문 가격 오프셋. 시장 반대 방향으로, 심볼의 tick size에 맞춰 배치됩니다 |
  | Full Stop Loss (Immediate) | kline 진행 중 가격이 진입가로부터 이 거리에 닿는 즉시 포지션을 청산합니다 |
  | Full Stop Loss (Close) | kline이 진입가로부터 이 거리를 넘어선 상태로 마감되면 포지션을 청산합니다 |
  | Post-Stop-Loss Re-entry | 손절 이후 TEF 방향이 바뀌기 전에 같은 방향으로 재진입을 허용할지 여부 |
  <br>

  **포지션 단위 설정**

  TC와 별도로, 각 포지션은 자체적인 거래 설정을 가집니다.

  | 파라미터 | 기본값 | 설명 |
  | :--- | :---: | :--- |
  | Reduce Only | Off | 진입 주문을 막아, 포지션을 줄이는 방향으로만 거래합니다 |
  | Stop Trade On FSL | On | Full Stop Loss 발생 후 해당 포지션의 거래를 중단합니다 |
  | Stop Trade On Unknown Trade | On | 외부 요인으로 포지션이 변경된 후 해당 포지션의 거래를 중단합니다 |
  <br>

  **TEF에서 Trade Handler로**

  새 분석 결과가 나올 때마다 TEF 함수를 통과시키고, 그 결과로 얻은 목표를 현재 포지션과 비교하여 최대 세 개의 **trade handler** 를 생성하며, 다음 순서로 처리합니다.

  | Handler | 조건 | 동작 |
  | :--- | :--- | :--- |
  | `CLEAR` | 포지션이 TEF 방향과 다름 (반대이거나, TEF에 방향이 없음) | 포지션 전체를 청산 |
  | `EXIT` | 투입된 잔고가 목표를 초과함 | 목표를 향해 포지션을 축소 (TEF 값이 `0` 이면 전량) |
  | `ENTRY` | 투입된 잔고가 목표에 미달하고, TC가 해당 방향을 허용하며, 포지션이 reduce-only가 아님 | 목표를 향해 포지션을 확대 |

  목표는 `Position Allocated Balance × |TEF|` 입니다 (*Account Control Configuration* 참고). 모든 주문은 전송 전에 수량 정밀도, 거래소 필터, 방향 검사를 거칩니다.

  **안전장치**

  * **오래된 분석 결과 거부** — 분석 결과가 이전, 현재, 다음 인터벌 중 어디에도 속하지 않거나, 계산된 이후 가격이 0.5% 이상 움직였다면 무시합니다.
  * **Handler 만료** — 베이스 인터벌의 5분의 1 안에 실행되지 못한 trade handler는 폐기되므로, 오래된 결정이 거래소에 도달하지 않습니다. 주문 취소를 기다린 시간은 제외됩니다.
  * **주문 교체** — 대기 중인 지정가 주문은 더 새로운 TEF 결정이나 손절이 발생하면 취소되고 교체됩니다.
  * **손절 우선** — 손절 주문은 TC의 주문 타입과 관계없이 항상 시장가로 실행되며, 그보다 먼저 생성된 대기 중인 trade handler를 모두 폐기합니다.
  * **거래 가능 여부 검사** — 포지션은 currency analysis와 TC가 연결되어 있고, 레버리지와 마진 타입이 TC와 일치하며, 외부 미체결 주문이 감지되지 않는 동안에만 거래합니다.
  * **자동 중단** — Full Stop Loss와 Unknown Trade는 abrupt clearing 이벤트로 기록되어 30일간 보관됩니다. 포지션 단위 설정에 따라, 둘 중 하나가 발생하면 해당 포지션의 거래가 중단됩니다.

  </Details>

* <Details>
  <Summary><b><i> Account Control Configuration </b></i></Summary>
  <img src="./docs/accountcontrol.png" width="750" height="440">

  Account Control은 아래 세 가지 파라미터를 통해 자본을 포지션들에 분배하고, 각 포지션의 노출 한도를 정합니다.

  | 파라미터                 | 대상   | 설명 |
  | :---:                     | :---:    | :--- |
  | Allocation Ratio          | 자산    | 해당 자산의 지갑 잔고 중 거래에 사용할 비율 |
  | Assumed Ratio             | 포지션 | 자산의 할당 가능 잔고 중 특정 포지션에 배정할 비율 |
  | Maximum Allocated Balance | 포지션 | 단일 포지션에 할당할 수 있는 잔고의 상한 (기본값: 무제한) |
  <br>

  $$\text{Allocatable Balance} = \max(\text{Wallet Balance},\ 0) \times 0.95 \times \color{orange}{\text{Allocation Ratio}}$$
  $$\text{Position Allocated Balance} = \max\left(0,\ \min\left(\text{Allocatable Balance} \times \color{orange}{\text{Assumed Ratio}},\ \color{orange}{\text{Maximum Allocated Balance}},\ \text{Remaining Allocatable Balance}\right)\right)$$
  <br>

  `0.95` 계수는 수수료와 마진 변동에 대비하여 지갑 잔고의 5%를 여유분으로 남겨두기 위한 것입니다.

  **할당 생명주기**

  * 잔고는 포지션이 처음 진입할 때 할당되고, 포지션이 완전히 청산되면 자산으로 반환됩니다.
  * 우선순위 개념은 없습니다. 모든 포지션의 Assumed Ratio 합이 100%를 넘으면, 먼저 진입하는 포지션부터 할당받고 나중에 진입하는 포지션은 남은 할당 가능 잔고만 받습니다.
  * 할당 가능 잔고가 이미 할당된 총액보다 줄어들면 (예: 손실 발생 후), 모든 포지션의 할당액이 비례적으로 축소됩니다.
  * 재시작 후에는 열린 포지션의 할당액이 자동으로 복원됩니다.

  **TEF와의 연결**

  할당 잔고는 TEF 값이 적용되는 기준입니다. 포지션의 목표 투입 잔고는 다음과 같습니다.

  $$\text{Target Committed Balance} = \text{Position Allocated Balance} \times |\text{TEF}|$$

  투입된 잔고가 이 목표보다 작으면 진입 주문이, 크면 청산 주문이 생성됩니다. 진입은 추가로 계정의 사용 가능 잔고에 의해 제한됩니다.

  **파생 리스크 지표**

  | 지표 | 정의 |
  | :--- | :--- |
  | Weighted Assumed Ratio | Assumed Ratio × 레버리지. 할당 가능 잔고 대비 포지션이 도달할 수 있는 실질 노출도 |
  | Commitment Rate | 사용 중인 마진 (수량 × 진입가 ÷ 레버리지) ÷ 할당 잔고 |
  | Risk Level | Commitment Rate × 현재가가 진입가에서 청산가 쪽으로 얼마나 이동했는지 |
  </Details>











---



### 👀 애플리케이션 프리뷰 & 사용법 ###
* <Details>
  <Summary><b><i> 페이지 </b></i></Summary>

  * <Details> 
      <Summary><b><i> Dashboard </b></i></Summary>
      <img src="./docs/dashboard_0.png" width="960" height="540">
      페이지 이동과 애플리케이션 제어를 위한 중앙 허브입니다.

      1\. 다른 페이지로 이동합니다.  
      2\. 애플리케이션을 종료합니다.  
    </Details>

  * <Details> 
      <Summary><b><i> Accounts </b></i></Summary>
      <img src="./docs/accounts_0.png" width="960" height="540">
      가상 계정과 실제 계정을 관리합니다.

      1\. 로컬 가상 계정 인스턴스를 생성합니다.  
      2\. 로컬 실제 계정 인스턴스를 생성하고 Binance와 동기화합니다.  
      3\. 자산과 포지션 상태를 모니터링합니다.  
      4\. 자산과 포지션의 거래 설정을 구성합니다.  
    </Details>

  * <Details> 
      <Summary><b><i> AutoTrade </b></i></Summary>
      <img src="./docs/autotrade_0.png" width="960" height="540">
      자동 분석 및 트레이딩 전략을 구성합니다.
      
      1\. Analyzer 상태를 모니터링합니다.  
      2\. Currency Analysis Configuration (CAC)을 생성합니다.  
      3\. CAC와 대상 종목을 선택하여 currency analysis를 시작합니다.  
      4\. 활성화된 currency analysis 목록과 상태를 확인합니다.  
      5\. Trade Configuration (TC)을 생성합니다.  
    </Details>

  * <Details> 
      <Summary><b><i> Currency Analysis </b></i></Summary>
      <img src="./docs/currencyanalysis_0.png" width="960" height="540">
        
      등록된 Currency Analysis를 모니터링합니다.

      1\. currency analysis 인스턴스를 선택하여 차트를 확인합니다.  
      2\. 선택한 분석에 적용된 CAC를 확인합니다.  
    </Details>

  * <Details> 
      <Summary><b><i> Account History </b></i></Summary>
      <img src="./docs/accounthistory_0.png" width="960" height="540">
      과거 성과와 기록을 확인합니다.

      1\. 실제/가상 계정의 거래 기록과 잔고 변동 이력을 확인합니다.
    </Details>

  * <Details> 
      <Summary><b><i> Market </b></i></Summary>
      <img src="./docs/market_0.png" width="960" height="540">
      실시간 시장을 모니터링합니다.

      1\. 현재 시장 종목 목록을 확인합니다.  
      2\. 종목 차트에 접근합니다.  
      3\. 특정 시간 구간에 대해 임시 currency analysis를 수행합니다.  
    </Details>

  * <Details> 
      <Summary><b><i> Simulation </b></i></Summary>
      <img src="./docs/simulation_0.png" width="960" height="540">
      백테스트를 실행하여 사용자 정의 트레이딩 전략의 성능을 검증합니다.

      1\. 완료되었거나 진행 중인 시뮬레이션 목록을 확인합니다.  
      2\. 기존 시뮬레이션에서 trade configuration을 가져옵니다.  
      3\. 대상 포지션에 대해 특정 전략, 변수, 기간으로 백테스트를 수행합니다.  
    </Details>

  * <Details> 
      <Summary><b><i> Simulation Result </b></i></Summary>
      <img src="./docs/simulationresult_0.png" width="960" height="540">
      시뮬레이션 결과를 분석합니다.
      
      1\. 완료된 시뮬레이션과 결과 요약을 확인합니다.  
      2\. 계정 잔고 변동 이력을 확인합니다.  
      3\. 시뮬레이션 설정(포지션, CAC, TC)을 확인합니다.  
      4\. 상세 거래 기록을 확인합니다.  
      5\. 상세 검토를 위해 currency analysis 차트를 재구성합니다.  
    </Details>

  * <Details> 
      <Summary><b><i> Database </b></i></Summary>
      <img src="./docs/database_0.png" width="960" height="540">
      로컬 시장 데이터베이스를 관리합니다.

      1\. 압축 통계를 포함한 데이터베이스 및 드라이브 사용량을 모니터링합니다.  
      2\. 심볼별 스트림 및 과거 데이터 수집을 설정합니다.  
      3\. 데이터베이스를 압축하거나, 선택한 심볼의 시장 데이터를 초기화합니다.  
      4\. Binance에 재요청하거나 로컬 네트워크의 다른 ATM-Eta 인스턴스에서 가져와 더미 구간을 복구합니다.  
    </Details>

  * <Details> 
      <Summary><b><i> Neural Network </b></i></Summary>
      <img src="./docs/neuralnetwork_0.png" width="960" height="540">
      머신러닝 모델을 설계하고 학습합니다.

      1\. 커스텀 MLP (Multi-Layer Perceptron) 모델을 설계합니다.  
      2\. 과거 시장 데이터로 모델을 학습합니다.  
      3\. 학습 성능과 결과를 분석합니다.  
    </Details>

  * <Details> 
      <Summary><b><i> Settings </b></i></Summary>
      <img src="./docs/settings_0.png" width="960" height="540">
      애플리케이션 환경을 설정합니다.

      1\. 언어를 변경합니다.  
      2\. GUI 테마(라이트/다크 모드)를 전환합니다.  
      3\. 전체 화면 모드를 켜고 끕니다.  
      4\. 오디오 설정을 관리합니다.  
      5\. 터미널 로그 표시 수준을 설정합니다.  
    </Details>
  </Details>

* <Details>
  <Summary><b><i> 기능 </b></i></Summary>

  * <Details>
    <Summary><b><i> 시장 확인 및 임시 Currency Analysis 수행 </b></i></Summary>

      1\. **Market** 페이지로 이동합니다.
      <img src="./docs/feat1_1.png">
      <br>

      2\. 대상 종목을 선택합니다.  
      3\. 차트 드로어의 설정 버튼을 클릭합니다.
      <img src="./docs/feat1_2.png"> 
      <br>

      4\. currency analysis 파라미터를 설정합니다.
      <img src="./docs/feat1_3.png"> 
      <br>

      5\. 분석 구간을 설정하고 분석을 시작합니다.
      <img src="./docs/feat1_4.png"> 
      <br>

      6\. 분석 결과를 확인합니다.
      <img src="./docs/feat1_5.png">

    </Details>

  * <Details>
    <Summary><b><i> Currency Analysis 추가 </b></i></Summary>

      1\. **AutoTrade** 페이지로 이동합니다.
      <img src="./docs/feat2_1.png">
      <br>

      2\. currency analysis 파라미터를 설정합니다.  
      3\. 설정 이름을 입력하고 (비워두면 자동 생성) **ADD** 를 클릭합니다.
      <img src="./docs/feat2_2.png">
      <br>

      4\. 시장 목록에서 대상 종목을 선택합니다.  
      5\. 적용할 CAC를 선택하고, 분석 인스턴스 이름을 입력한 뒤 (비워두면 자동 생성) **ADD** 를 클릭합니다.  
      <img src="./docs/feat2_3.png">
      <br>

      6\. 분석 인스턴스 목록을 확인합니다. **VIEW CURRENCY ANALYSIS CHART** 를 클릭하면 차트가 열립니다.  
      <img src="./docs/feat2_4.png">
      <br>

      7\. currency analysis를 모니터링합니다.  
      <img src="./docs/feat2_5.png">
      <br>

    </Details>

  * <Details>
    <Summary><b><i> Trade Configuration 추가 </b></i></Summary>

      1\. **AutoTrade** 페이지로 이동합니다.  
      <img src="./docs/feat3_1.png">
      <br>

      2\. trade configuration 파라미터를 설정합니다.  
      3\. 설정 이름을 입력하고 (비워두면 자동 생성) **ADD** 를 클릭합니다.  
      <img src="./docs/feat3_2.png">
      <br>

    </Details>

  * <Details>
    <Summary><b><i> 백테스트 및 결과 확인 </b></i></Summary>

      1\. **Simulation** 페이지로 이동합니다.  
      <img src="./docs/feat4_1.png">
      <br>

      2\. 시뮬레이션 이름(비워두면 자동 생성)과 기간을 설정합니다.  
      3\. 포지션별 전략(Currency Analysis, Trade Configuration, Account Control)을 구성합니다.  
      4\. 계정 단위 파라미터를 설정합니다.  
      5\. **ADD** 를 클릭하여 시뮬레이션을 시작합니다. 완료되면 **VIEW RESULT** 를 클릭하거나 **DASHBOARD** 를 통해 **SIMULATION RESULT** 페이지로 이동합니다.  
      <img src="./docs/feat4_2.png">
      <br>

      6\. 시뮬레이션을 선택합니다.  
      7\. 시뮬레이션 결과 요약을 확인합니다.  
      8\. 시뮬레이션 결과의 세부 내용을 확인합니다.  
      <img src="./docs/feat4_3.png">
      <br>

    </Details>

  * <Details>
    <Summary><b><i> 계정 추가 및 자동 매매 </b></i></Summary>

      1\. **Accounts** 페이지로 이동합니다.  
      <img src="./docs/feat5_1.png">
      <br>

      2\. 계정 정보를 입력하고 **ADD ACCOUNT** 를 클릭합니다.  
      &nbsp; [ACTUAL 전용] Binance User ID를 입력합니다.  
      <img src="./docs/feat5_2.png">
      <br>

      3\. 선택한 계정의 정보를 확인합니다.  
      &nbsp; [ACTUAL 전용] Binance API Key와 Secret Key를 입력하거나 **AAF** 를 사용하여 계정을 활성화합니다 (*무결성 및 복구* 참고). 로컬 계정 인스턴스가 Binance의 실제 계정과 동기화됩니다.  
      4\. 자산 정보와 포지션 상태를 모니터링합니다.  
      5\. 거래할 각 포지션에 Currency Analysis, Trade Configuration, Assumed Ratio를 지정한 뒤, 포지션의 trade status를 켭니다. 자동 매매는 계정과 포지션의 trade status가 모두 켜져 있는 동안에만 동작합니다.
      <img src="./docs/feat5_3.png">
      <br>

      6\. **Account History** 페이지로 이동합니다.  
      <img src="./docs/feat5_4.png">
      <br>

      7\. 목록에서 계정을 선택합니다.  
      8\. 보기 방식을 전환하여 잔고 변동 차트 또는 거래 기록을 확인합니다.  
      <img src="./docs/feat5_5.png">
      <br>

    </Details>

  * <Details>
    <Summary><b><i> 신경망 모델 생성 및 학습 </b></i></Summary>

      1\. **Neural Network** 페이지로 이동합니다.  
      <img src="./docs/feat6_1.png">
      <br>

      2\. 모델 파라미터(이름, 타입, Control Key, 초기화 방법)를 설정합니다.   
      3\. 신경망 구조(레이어/노드/분석 참조)를 정의합니다.  
      <img src="./docs/feat6_2.png">
      <br>

      4\. 목록에서 모델을 선택합니다.  
      5\. 네트워크 구조를 시각화합니다.  
      <img src="./docs/feat6_3.png">
      <br>

      6\. 학습에 사용할 과거 시장 데이터를 선택하고 학습 파라미터를 설정합니다.  
      <img src="./docs/feat6_4.png">
      <br>

      7\. 학습 과정을 모니터링합니다.  
      8\. 학습 결과와 성능 지표를 확인합니다.  
      <img src="./docs/feat6_5.png">
      <br>

    </Details>

  </Details>
  
---



### 🔬 실거래 안정성 테스트 ###

전체 시스템을 장기간에 걸쳐 검증하기 위해, 본인의 Binance Futures 계정에서 약 4개월간 애플리케이션을 실제로 운용했습니다. 아래 차트는 해당 기간의 실제 잔고 변동 기록입니다.

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

**백테스트 예측치에 대해서.** 150배라는 수치는 과거 데이터에 대한 파라미터 과적합으로 부풀려진 결과일 가능성이 매우 높으며, 이를 현실적인 기대 수익으로 보지 않았습니다. 그럼에도 해당 전략을 배포한 이유는, 이번 운용의 목적이 **수익 창출이 아니라 전체 파이프라인이 실거래 환경에서 지속적이고 정확하게 동작하는지 검증하는 것** 이었기 때문입니다.

**실제로 검증된 부분.** 118일간의 운용 기간 동안 시스템은 모든 주문 체결을 안정적으로 처리했고, 거래소와의 포지션 및 잔고 동기화를 유지했으며, 네트워크 단절, API rate limit 도달, 데이터 스트림 끊김 상황에서 수동 개입 없이 자동으로 복구되었습니다. 수익 시연이 아닌 안정성 검증 목적의 운용으로서 충분한 결과라고 판단했습니다. 실제 최대 낙폭은 백테스트 예측치(약 35%)보다 훨씬 양호한 수준에 머물렀고, 실제 수익률 또한 같은 운용 기간에 대한 백테스트 예측치를 상회했습니다. 다만 이는 전략 자체의 우수성보다는 운용 기간의 시장 상황이 우호적이었던 결과일 가능성이 크다고 판단합니다.

> ⚠️ **유의사항** — 본 애플리케이션은 **수익을 보장하지 않습니다**. 사용자가 직접 자신의 전략을 구축하고 운용할 수 있는 플랫폼을 제공할 뿐입니다. 백테스트 결과든 실거래 결과든 과거의 성과는 미래의 성과를 보장하지 않으며, 암호화폐 파생상품 거래는 상당한 손실 위험을 동반합니다.



---



### 🤝 크레딧
* **[python-binance](https://github.com/sammchardy/python-binance)** by *sammchardy* (MIT License)  
  - 본 프로젝트는 수정된 버전의 `python-binance` 를 포함합니다. `client.py` 모듈의 `futures_historical_klines` 함수에 첫 kline 탐색을 비활성화하는 옵션이 추가되었습니다. 

---



### 🗓️ 프로젝트 기간
* 2024년 9월 – 2026년 5월 (이후 업데이트 및 유지보수 지속)



---



### 🚀 프로젝트 업데이트
**버전 1.1.0 업데이트 [2026/09/22]**
 - **새 기능**

   * **Metric 시장 데이터 수집:** 
   Binance REST API로 5분 간격의 미결제약정(Open Interest)과 글로벌 롱/숏 비율 데이터를 수집하는 파이프라인을 추가했으며, 과거 데이터 백필에는 Binance Vision 아카이브를 사용합니다. Binance가 이 지표들에 대한 스트리밍을 제공하지 않기 때문에, 5분 원본으로부터 1분 간격 데이터를 만들어내는 내부 스트림 생성 로직을 구현하여, 기존 아키텍처를 거의 변경하지 않고도 kline, depth, aggTrade와 동일한 파이프라인으로 흐르도록 했습니다. API 키가 필요 없는 엔드포인트만 사용하므로, metric 수집은 계정 활성화와 무관하게 동작합니다.

   * **지정가 거래:** 
   기존 TEF 함수와 연동하여 지정가 주문을 자동으로 실행하도록 했습니다. 주문은 현재가 대비 설정 가능한 오프셋만큼 떨어진 가격에 post-only(GTX)로 제출되며, 각 심볼의 tick size에 맞춰 시장 반대 방향으로 정렬되므로 모든 체결이 maker 수수료율로 이루어집니다. 재설계된 주문 생명주기(DISPATCHED → RESTING → CANCELING → SETTLED/CANCELLED)는 누적 체결 수량을 이용해 부분 체결이 발생한 대기 주문을 추적하며, 더 새로운 TEF 결정이나 손절이 발생하면 대기 주문을 자동으로 취소하고 교체합니다. 손절 및 강제 청산 주문은 즉시 체결을 보장하기 위해 시장가 주문을 유지합니다. 가상 거래 서버도 post-only 거절, 부분 체결, 가격 움직임 기반 지정가 체결을 시뮬레이션하도록 확장하여, 실거래 배포 전에 전체 생명주기를 테스트할 수 있게 했습니다.

 - **개선 및 수정**

   * **분석 시스템 모듈화:** 
   하나로 뭉쳐 있던 분석 로직을 재구성하여, 각 지표가 독립된 모듈 파일에 위치하도록 했습니다. 이를 통해 분석 시스템을 확장하기 위한 일관된 구조가 마련되었습니다. 새 지표는 하나의 커지는 코드베이스를 확장하는 대신 독립 모듈로 추가되므로, 지원 지표가 늘어나도 분석 계층이 확장 가능하게 유지됩니다.

   * **주문 추적 로직 개선:**
   주문 처리에서 명확한 거절과 모호한 실패(타임아웃, 네트워크 오류, 예상치 못한 응답 형식)를 구분하도록 했습니다. 모호한 주문은 더 이상 무작정 재시도하지 않고, 상태 검증 대상으로 등록한 뒤 거래소 조회를 통해 확정하여 중복 주문을 방지합니다. 존재하지 않는 것으로 확인된 주문은 안전하게 재생성하고, 상태를 판단할 수 없는 주문은 재생성 없이 종료합니다. 주문이 이미 종료되어 취소가 거절된 경우에는 주문의 최종 상태를 조회하여, 취소 직전에 발생한 체결도 정확하게 기록합니다. 또한 주문 생성 응답에서 `avgPrice` 가 제거된 것을 포함한 API 변경에 대응하도록 응답 파싱을 강화했으며, 해당 값은 주문 조회를 통해 가져옵니다.

   * **차트 드로어 객체의 포지션 방향 표시:**
   거래 기록 데이터를 바탕으로, 각 인터벌 종료 시점에 보유한 최종 롱/숏 포지션을 시각화하는 포지션 스트립을 차트 하단에 추가했습니다. 기존 거래 기록 마커와 함께 차트 전반의 포지션 상태를 한눈에 파악할 수 있습니다.



<br>



**버전 1.2.0 업데이트 [2026/09/23]**
 - **새 기능**

   * **포지션 단위 거래 제어 파라미터:**
   저장만 되고 실제로 적용되지 않던 reduce-only 모드가 이제 진입 주문을 막아, 포지션을 줄이는 방향으로만 거래하도록 동작합니다. 이와 함께 두 개의 포지션 단위 파라미터인 stop-trade-on-FSL과 stop-trade-on-unknown-trade를 추가하여, Full Stop Loss나 외부 요인에 의한 포지션 변경 후 거래를 중단할지 여부를 제어할 수 있게 했습니다. 기존에는 unknown trade만 기록되던 abrupt clearing 이벤트에 Full Stop Loss도 기록되며, 이 기록은 거래가 중단될 때마다 지워지지 않고 30일간 보관됩니다.
   
   * **Adaptive 주문 타입:**
   새로운 `ADAPTIVE` 주문 타입은 기본적으로 post-only 지정가 주문을 사용하되, TEF 방향이 반전되어 포지션을 청산해야 할 때는 시장가 주문으로 전환합니다. 일반적인 진입과 부분 청산에서는 지정가 주문의 maker 수수료 이점을 유지하면서, 체결 속도가 가장 중요한 반전 상황에서는 주문이 호가창에 대기한 채로 남지 않도록 보장합니다.

 - **개선 및 수정**

   * **잘못된 Unknown Trade 감지 수정:**
   계정 데이터와 주문 응답은 서로 다른 경로로 도착하기 때문에, 주문 응답을 받기 전에 체결이 계정 스냅샷에 먼저 나타날 수 있었습니다. 기존에는 이를 외부 개입으로 판단하여 해당 포지션의 거래를 중단했습니다. 이제는 활성 주문의 미체결 수량 범위 안에 들어오는 수량 변화는 해당 주문에 귀속시키고 응답이 도착하면 확정하며, 실제 외부 변경은 여전히 감지합니다.

   * **평균 체결가 조회:**
   CM 마이그레이션 이후 Binance가 주문 생성 응답에서 `avgPrice` 를 제거했습니다. 이제 해당 필드가 없으면 주문의 체결 내역으로부터 거래량 가중 평균을 계산하여 대체하며, 주문 응답 파싱을 보호하여 필드가 없거나 바뀌더라도 이미 제출된 주문이 추적에서 누락되지 않도록 했습니다.

   * **계정 데이터 조회 Rate Limit 계산 수정:**
   계정 데이터 조회 주기를 계산할 때 IP 공유 계수가 나눗셈이 아닌 곱셈으로 적용되어, rate limit 예산을 더 많은 클라이언트가 나눠 쓸수록 조회 주기가 길어지는 대신 오히려 짧아지는 문제가 있었습니다. 이제 조회 주기는 설정된 범위 안으로 제한되며, 최대 활성화 계정 수도 조회 주기 계산과 동일한 안전 마진을 반영하여 상한에서 마진이 잘리지 않도록 했습니다.
   
   * **AAF 탐색 안정성 개선:**
   AAF 탐색 시 각 `.aaf` 파일의 내용을 사용 전에 검증하도록 했습니다. 기존에는 JSON으로는 파싱되지만 필요한 필드가 없는 파일이 예외를 일으켜 탐색을 중단시킬 수 있었습니다. 탐색 대상이 마운트된 모든 드라이브의 루트 디렉토리이기 때문에, 같은 확장자를 가진 무관한 파일로도 이 문제가 발생할 수 있었습니다. 이제 형식이 잘못된 파일은 건너뜁니다.



---



### 📄 문서 정보
* **마지막 업데이트:** 2026년 9월 25일  
* **작성자:** 김범수
* **이메일:**  kimlvis31@gmail.com
