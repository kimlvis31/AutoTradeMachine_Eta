LANGUAGES = ('ENG', 'KOR')
TEXTPACK = dict()

#PAGE 'DASHBOARD' -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
if (True):
    TEXTPACK['DASHBOARD:TITLE'] = {'ENG': "DASHBOARD",
                                   'KOR': "대시보드"}
#PAGE 'DASHBOARD' END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#PAGE 'ACCOUNTS' ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
if (True):
    TEXTPACK['ACCOUNTS:TITLE'] = {'ENG': "ACCOUNTS",
                                  'KOR': "계정"}
    #<Accounts List>
    TEXTPACK['ACCOUNTS:BLOCKTITLE_ACCOUNTSLIST'] = {'ENG': "ACCOUNTS LIST",
                                                    'KOR': "계정 리스트"}
    TEXTPACK['ACCOUNTS:ACCOUNTLIST_VIRTUAL'] = {'ENG': "VIRTUAL ONLY",
                                                'KOR': "가상계정만 표시"}
    TEXTPACK['ACCOUNTS:ACCOUNTLIST_ACTUAL'] = {'ENG': "ACTUAL ONLY",
                                               'KOR': "실제계정만 표시"}
    TEXTPACK['ACCOUNTS:ACCOUNTLIST_INDEX'] = {'ENG': "INDEX",
                                              'KOR': "인덱스"}
    TEXTPACK['ACCOUNTS:ACCOUNTLIST_LOCALID'] = {'ENG': "LOCAL ID",
                                                'KOR': "로컬 ID"}
    TEXTPACK['ACCOUNTS:ACCOUNTLIST_TYPE'] = {'ENG': "TYPE",
                                             'KOR': "타입"}
    TEXTPACK['ACCOUNTS:ACCOUNTLIST_STATUS'] = {'ENG': "STATUS",
                                               'KOR': "상태"}
    TEXTPACK['ACCOUNTS:ACCOUNTLIST_TRADESTATUS'] = {'ENG': "TRADE STATUS",
                                                    'KOR': "거래 상태"}
    #<Acounts Information & Control>
    TEXTPACK['ACCOUNTS:BLOCKTITLE_ACCOUNTSINFORMATION&CONTROL'] = {'ENG': "ACCOUNTS INFORMATION & CONTROL",
                                                                   'KOR': "계정 정보 & 관리"}
    TEXTPACK['ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_LOCALID'] = {'ENG': "LOCAL ID",
                                                                'KOR': "로컬 ID"}
    TEXTPACK['ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_BINANCEUID'] = {'ENG': "BINANCE UID",
                                                                   'KOR': "바이낸스 UID"}
    TEXTPACK['ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_ACCOUNTTYPE'] = {'ENG': "ACCOUNT TYPE",
                                                                    'KOR': "계정 타입"}
    TEXTPACK['ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_STATUS'] = {'ENG': "ACCOUNT STATUS",
                                                               'KOR': "계정 상태"}
    TEXTPACK['ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_TRADESTATUS'] = {'ENG': "TRADE STATUS",
                                                                    'KOR': "거래 상태"}
    TEXTPACK['ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_APIKEY'] = {'ENG': "API KEY",
                                                               'KOR': "API 키"}
    TEXTPACK['ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_SECRETKEY'] = {'ENG': "SECRET KEY",
                                                                  'KOR': "시크릿 키"}
    TEXTPACK['ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_PASSWORD'] = {'ENG': "PASSWORD",
                                                                 'KOR': "비밀번호"}
    TEXTPACK['ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_HOLDPASSWORD'] = {'ENG': "HOLD PW",
                                                                     'KOR': "임시저장"}
    TEXTPACK['ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYENTEREDKEYS'] = {'ENG': "ACTIVATE WITH ENTERED KEYS",
                                                                              'KOR': "입력된 키로 활성화"}
    TEXTPACK['ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_DEACTIVATE'] = {'ENG': "DEACTIVATE",
                                                                   'KOR': "비활성화"}
    TEXTPACK['ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYAAF'] = {'ENG': "ACTIVATE WITH AAF",
                                                                      'KOR': "AAF로 활성화"}
    TEXTPACK['ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_GENERATEAAF'] = {'ENG': "GENERATE AAF",
                                                                    'KOR': "AAF 생성"}
    TEXTPACK['ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_ADDACCOUNT'] = {'ENG': "ADD ACCOUNT",
                                                                   'KOR': "계정 추가"}
    TEXTPACK['ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNT'] = {'ENG': "REMOVE ACCOUNT",
                                                                      'KOR': "계정 삭제"}
    #<Assets>
    TEXTPACK['ACCOUNTS:BLOCKTITLE_ASSETS'] = {'ENG': "ASSETS",
                                              'KOR': "자산"}
    TEXTPACK['ACCOUNTS:ASSETS_MARGINBALANCE'] = {'ENG': "MARGIN BALANCE",
                                                 'KOR': "마진 잔고"}
    TEXTPACK['ACCOUNTS:ASSETS_WALLETBALANCE'] = {'ENG': "WALLET BALANCE (TOTAL / CROSS / ISOLATED)",
                                                 'KOR': "지갑 잔고 (전체 / 교차 / 격리)"}
    TEXTPACK['ACCOUNTS:ASSETS_AVAILABLEBALANCE'] = {'ENG': "AVAILABLE BALANCE",
                                                    'KOR': "가용잔액"}
    TEXTPACK['ACCOUNTS:ASSETS_MARGIN'] = {'ENG': "MARGIN (POSINIT / OOINIT / MAINT_CROSS)",
                                          'KOR': "증거금 (포지션개시 / 주문개시 / 교차유지)"}
    TEXTPACK['ACCOUNTS:ASSETS_ALLOCATABLEBALANCE'] = {'ENG': "ALLOCATABLE BALANCE",
                                                      'KOR': "할당가능액"}
    TEXTPACK['ACCOUNTS:ASSETS_POSITIONINITIALMARGIN'] = {'ENG': "POSITION INITIAL MARGIN (CROSS / ISOLATED)",
                                                         'KOR': "포지션 개시 증거금 (교차 / 격리)"}
    TEXTPACK['ACCOUNTS:ASSETS_ALLOCATEDBALANCE'] = {'ENG': "ALLOCATED BALANCE",
                                                    'KOR': "할당액"}
    TEXTPACK['ACCOUNTS:ASSETS_UNREALIZEDPNL'] = {'ENG': "UNREALIZED PNL (TOTAL / CROSS / ISOLATED)",
                                                 'KOR': "미실현 손익 (전체 / 교차 / 격리)"}
    TEXTPACK['ACCOUNTS:ASSETS_BASEASSUMEDRATIO'] = {'ENG': "BASE ASSUMED RATIO",
                                                    'KOR': "기본가정율"}
    TEXTPACK['ACCOUNTS:ASSETS_WEIGHTEDASSUMEDRATIO'] = {'ENG': "WEIGHTED ASSUMED RATIO",
                                                        'KOR': "가중가정율"}
    TEXTPACK['ACCOUNTS:ASSETS_COMMITMENTRATE'] = {'ENG': "COMMITMENT RATE",
                                                  'KOR': "자금투입율"}
    TEXTPACK['ACCOUNTS:ASSETS_RISKLEVEL'] = {'ENG': "RISK LEVEL",
                                             'KOR': "위험도"}
    TEXTPACK['ACCOUNTS:ASSETS_ASSUMPTIONRATE'] = {'ENG': "ASSUMPTION RATE",
                                                  'KOR': "가정비율"}
    TEXTPACK['ACCOUNTS:ASSETS_ASSET'] = {'ENG': "ASSET",
                                         'KOR': "자산"}
    TEXTPACK['ACCOUNTS:ASSETS_TRANSFERBALANCE'] = {'ENG': "TRANSFER BALANCE",
                                                   'KOR': "자금 이동"}
    TEXTPACK['ACCOUNTS:ASSETS_DEPOSIT'] = {'ENG': "DEPOSIT",
                                           'KOR': "송금"}
    TEXTPACK['ACCOUNTS:ASSETS_WITHDRAW'] = {'ENG': "WITHDRAW",
                                            'KOR': "출금"}
    TEXTPACK['ACCOUNTS:ASSETS_ALLOCATIONRATIO'] = {'ENG': "ALLOCATION RATIO",
                                                   'KOR': "할당비율"}
    TEXTPACK['ACCOUNTS:ASSETS_APPLY'] = {'ENG': "APPLY",
                                         'KOR': "적용"}
    #<Positions>
    TEXTPACK['ACCOUNTS:BLOCKTITLE_POSITIONS'] = {'ENG': "POSITIONS",
                                                 'KOR': "포지션"}
    TEXTPACK['ACCOUNTS:POSITIONS_DISPLAYMODE'] = {'ENG': "DISPLAY MODE",
                                                  'KOR': "디스플레이 모드"}
    TEXTPACK['ACCOUNTS:POSITIONS_DISPLAYMODE_BASIC'] = {'ENG': "BASIC",
                                                        'KOR': "기본"}
    TEXTPACK['ACCOUNTS:POSITIONS_DISPLAYMODE_TRADER'] = {'ENG': "TRADER",
                                                         'KOR': "트레이더"}
    TEXTPACK['ACCOUNTS:POSITIONS_DISPLAYMODE_DETAIL'] = {'ENG': "DETAIL",
                                                         'KOR': "디테일"}
    TEXTPACK['ACCOUNTS:POSITIONS_SEARCH'] = {'ENG': "SEARCH",
                                             'KOR': "검색"}
    TEXTPACK['ACCOUNTS:POSITIONS_SEARCH_SYMBOL'] = {'ENG': "SYMBOL",
                                                    'KOR': "심볼"}
    TEXTPACK['ACCOUNTS:POSITIONS_SEARCH_CACODE'] = {'ENG': "CA CODE",
                                                    'KOR': "CA 코드"}
    TEXTPACK['ACCOUNTS:POSITIONS_SEARCH_TCCODE'] = {'ENG': "TC CODE",
                                                    'KOR': "TC 코드"}
    TEXTPACK['ACCOUNTS:POSITIONS_SORTBY'] = {'ENG': "SORT BY",
                                             'KOR': "정렬 기준"}
    TEXTPACK['ACCOUNTS:POSITIONS_SORTBY_INDEX'] = {'ENG': "INDEX",
                                                   'KOR': "인덱스"}
    TEXTPACK['ACCOUNTS:POSITIONS_SORTBY_SYMBOL'] = {'ENG': "SYMBOL",
                                                    'KOR': "심볼"}
    TEXTPACK['ACCOUNTS:POSITIONS_SORTBY_LEVERAGE'] = {'ENG': "LEVERAGE",
                                                      'KOR': "레버리지"}
    TEXTPACK['ACCOUNTS:POSITIONS_SORTBY_UNREALIZEDPNL'] = {'ENG': "Un.PNL",
                                                           'KOR': "미실현손익"}
    TEXTPACK['ACCOUNTS:POSITIONS_SORTBY_ASSUMEDRATIO'] = {'ENG': "ASMD%",
                                                          'KOR': "가정율"}
    TEXTPACK['ACCOUNTS:POSITIONS_SORTBY_WEIGHTEDASSUMEDRATIO'] = {'ENG': "ASMD%[W]",
                                                                  'KOR': "가중가정율"}
    TEXTPACK['ACCOUNTS:POSITIONS_SORTBY_ALLOCATEDBALANCE'] = {'ENG': "ALLC. BAL.",
                                                              'KOR': "할당액"}
    TEXTPACK['ACCOUNTS:POSITIONS_SORTBY_COMMITMENTRATE'] = {'ENG': "C.R.",
                                                            'KOR': "자금투입률"}
    TEXTPACK['ACCOUNTS:POSITIONS_SORTBY_RISKLEVEL'] = {'ENG': "RISK LEVEL",
                                                       'KOR': "위험도"}
    TEXTPACK['ACCOUNTS:POSITIONS_SORTBY_CACODE'] = {'ENG': "CA CODE",
                                                    'KOR': "CA 코드"}
    TEXTPACK['ACCOUNTS:POSITIONS_SORTBY_TCCODE'] = {'ENG': "TC CODE",
                                                    'KOR': "TC 코드"}
    TEXTPACK['ACCOUNTS:POSITIONS_SORTBY_PRIORITY'] = {'ENG': "PRIORITY",
                                                      'KOR': "우선순위"}
    TEXTPACK['ACCOUNTS:POSITIONS_TRADESTATUSFILTER'] = {'ENG': "TRADE STATUS",
                                                        'KOR': "거래 상태"}
    TEXTPACK['ACCOUNTS:POSITIONS_TRADABLEFILTER'] = {'ENG': "TRADABLE",
                                                     'KOR': "거래 가능"}
    TEXTPACK['ACCOUNTS:POSITIONS_QUANTITYFILTER'] = {'ENG': "QUANTITY",
                                                     'KOR': "보유수"}
    TEXTPACK['ACCOUNTS:POSITIONS_ASSUMEDRATIOFILTER'] = {'ENG': "ASSUMED BALANCE",
                                                         'KOR': "가정액"}
    TEXTPACK['ACCOUNTS:POSITIONS_ALLOCATIONBALANCEFILTER'] = {'ENG': "ALLOCATION BALANCE",
                                                              'KOR': "할당액"}
    TEXTPACK['ACCOUNTS:POSITIONS_CURRENCYANALYSISCODEFILTER'] = {'ENG': "CURRENCY ANALYSIS CODE",
                                                                 'KOR': "종목 분석 코드"}
    TEXTPACK['ACCOUNTS:POSITIONS_FILTER_ALL'] = {'ENG': "ALL",
                                                 'KOR': "전체"}
    TEXTPACK['ACCOUNTS:POSITIONS_FILTER_TRUE'] = {'ENG': "TRUE",
                                                  'KOR': "참"}
    TEXTPACK['ACCOUNTS:POSITIONS_FILTER_FALSE'] = {'ENG': "FALSE",
                                                   'KOR': "거짓"}
    TEXTPACK['ACCOUNTS:POSITIONS_FILTER_NONZERO'] = {'ENG': "GREATER THAN ZERO",
                                                     'KOR': "1 이상"}
    TEXTPACK['ACCOUNTS:POSITIONS_FILTER_ZERO'] = {'ENG': "EQUAL TO ZERO",
                                                  'KOR': "없음 (혹은 == 0)"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_INDEX'] = {'ENG': "INDEX",
                                                'KOR': "인덱스"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_SYMBOL'] = {'ENG': "SYMBOL",
                                                'KOR': "심볼"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_TRADING'] = {'ENG': "TRADING",
                                                 'KOR': "거래중"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_TRADABLE'] = {'ENG': "TRADABLE",
                                                  'KOR': "거래가능"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_REDUCEONLY'] = {'ENG': "RDC-ONLY",
                                                    'KOR': "진입금지"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_CURRENCYANALYSISCODE'] = {'ENG': "CA CODE",
                                                              'KOR': "CA 코드"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_TRADECONFIGURATIONCODE'] = {'ENG': "TC CODE",
                                                                'KOR': "TC 코드"}

    TEXTPACK['ACCOUNTS:POSITIONS_ST_TRADECONTROL'] = {'ENG': "TRADE CONTROL",
                                                      'KOR': "트레이드 컨트롤"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_ABRUPTCLEARINGRECORDS'] = {'ENG': "ACR",
                                                               'KOR': "ACR"}

    TEXTPACK['ACCOUNTS:POSITIONS_ST_QUANTITY'] = {'ENG': "QUANTITY",
                                                  'KOR': "보유수"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_ENTRYPRICE'] = {'ENG': "ENTRY",
                                                    'KOR': "진입가"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_LEVERAGE'] = {'ENG': "LEVERAGE",
                                                  'KOR': "레버리지"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_MARGINMODE'] = {'ENG': "MARGIN MODE",
                                                    'KOR': "마진 모드"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_ISOLATEDWALLETBALANCE'] = {'ENG': "IWB",
                                                               'KOR': "IWB"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_POSITIONINITIALMARGIN'] = {'ENG': "PIM",
                                                               'KOR': "PIM"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_OPENORDERINITIALMARGIN'] = {'ENG': "OOIM",
                                                                'KOR': "OOIM"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_MAINTENANCEMARGIN'] = {'ENG': "MM",
                                                           'KOR': "MM"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_CURRENTPRICE'] = {'ENG': "CURRENT",
                                                      'KOR': "현재가"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_UNREALIZEDPNL'] = {'ENG': "Un.PNL",
                                                       'KOR': "미실현 손익"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_LIQUIDATIONPRICE'] = {'ENG': "LIQ.PRICE",
                                                          'KOR': "청산가"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_ASSUMEDRATIO'] = {'ENG': "ASMD%",
                                                      'KOR': "가정율"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_PRIORITY'] = {'ENG': "PRIORITY",
                                                  'KOR': "우선순위"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_ALLOCATEDBALANCE'] = {'ENG': "ALLC.BAL.",
                                                          'KOR': "할당액"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_MAXALLOCATEDBALANCE'] = {'ENG': "MAX ALLC.BAL.",
                                                             'KOR': "최대할당액"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_WEIGHTEDASSUMEDRATIO'] = {'ENG': "ASMD%[W]",
                                                              'KOR': "가중가정율"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_COMMITMENTRATE'] = {'ENG': "CMT RATE",
                                                        'KOR': "자금투입율"}
    TEXTPACK['ACCOUNTS:POSITIONS_ST_RISKLEVEL'] = {'ENG': "R.L",
                                                   'KOR': "위험도"}
    TEXTPACK['ACCOUNTS:POSITIONS_FORCECLEARPOSITION'] = {'ENG': "FORCE CLEAR POSITION",
                                                         'KOR': "포지션 강제 종료"}
    TEXTPACK['ACCOUNTS:POSITIONS_CURRENCYANALYSISCODE'] = {'ENG': "CURRENCY ANALYSIS CODE",
                                                           'KOR': "종목 분석 코드"}
    TEXTPACK['ACCOUNTS:POSITIONS_TRADECONFIGURATIONCODE'] = {'ENG': "TRADE CONFIGURATION CODE",
                                                             'KOR': "트레이드 설정 코드"}
    TEXTPACK['ACCOUNTS:POSITIONS_PRIORITY'] = {'ENG': "PRIORITY",
                                               'KOR': "우선순위"}
    TEXTPACK['ACCOUNTS:POSITIONS_ASSUMEDRATIO'] = {'ENG': "ASSUMED RATIO",
                                                   'KOR': "가정율"}
    TEXTPACK['ACCOUNTS:POSITIONS_MAXALLOCATEDBALANCE'] = {'ENG': "MAX ALLC.BAL.",
                                                          'KOR': "최대할당액"}
    TEXTPACK['ACCOUNTS:POSITIONS_TRADESTATUS'] = {'ENG': "TRADE STATUS",
                                                  'KOR': "거래 상태"}
    TEXTPACK['ACCOUNTS:POSITIONS_REDUCEONLY'] = {'ENG': "REDUCE ONLY",
                                                 'KOR': "진입 금지"}
    TEXTPACK['ACCOUNTS:POSITIONS_APPLY'] = {'ENG': "APPLY",
                                            'KOR': "적용"}
    TEXTPACK['ACCOUNTS:POSITIONS_RESETTRADECONTROLTRACKER'] = {'ENG': "RESET TC TRACKER",
                                                               'KOR': "TC TRACKER 초기화"}
    #<Information>
    TEXTPACK['ACCOUNTS:BLOCKTITLE_INFORMATION'] = {'ENG': "INFORMATION",
                                                   'KOR': "정보"}
    TEXTPACK['ACCOUNTS:INFORMATION_LOCALID'] = {'ENG': "LOCAL ID",
                                                'KOR': "로컬 ID"}
    TEXTPACK['ACCOUNTS:INFORMATION_BINANCEUID'] = {'ENG': "BINANCE UID",
                                                   'KOR': "바이낸스 UID"}
    TEXTPACK['ACCOUNTS:INFORMATION_TYPE'] = {'ENG': "ACCOUNT TYPE",
                                             'KOR': "계정 타입"}
    TEXTPACK['ACCOUNTS:INFORMATION_STATUS'] = {'ENG': "ACCOUNT STATUS",
                                               'KOR': "계정 상태"}
    TEXTPACK['ACCOUNTS:INFORMATION_TRADESTATUS'] = {'ENG': "TRADE STATUS",
                                                    'KOR': "거래 상태"}
    #<Control>
    TEXTPACK['ACCOUNTS:BLOCKTITLE_CONTROL'] = {'ENG': "CONTROL",
                                               'KOR': "관리"}
    TEXTPACK['ACCOUNTS:CONTROL_LOCALID'] = {'ENG': "LOCAL ID",
                                            'KOR': "로컬 ID"}
    TEXTPACK['ACCOUNTS:CONTROL_BINANCEUID'] = {'ENG': "BINANCE UID",
                                               'KOR': "바이낸스 UID"}
    TEXTPACK['ACCOUNTS:CONTROL_TYPE'] = {'ENG': "ACCOUNT TYPE",
                                         'KOR': "계정 타입"}
    TEXTPACK['ACCOUNTS:CONTROL_ADD'] = {'ENG': "ADD ACCOUNT",
                                        'KOR': "계정 추가"}
    TEXTPACK['ACCOUNTS:CONTROL_REMOVE'] = {'ENG': "REMOVE ACCOUNT",
                                           'KOR': "계정 삭제"}
    TEXTPACK['ACCOUNTS:CONTROL_APIKEY'] = {'ENG': "API KEY",
                                           'KOR': "API 키"}
    TEXTPACK['ACCOUNTS:CONTROL_SECRETKEY'] = {'ENG': "SECRET KEY",
                                              'KOR': "시크릿 키"}
    TEXTPACK['ACCOUNTS:CONTROL_ACTIVATEBYENTEREDKEYS'] = {'ENG': "ACTIVATE USING THE ENTERED KEYS",
                                                          'KOR': "입력 키로 활성화"}
    TEXTPACK['ACCOUNTS:CONTROL_ACTIVATEBYFLASHDRIVE'] = {'ENG': "ACTIVATE USING A FLASH DRIVE",
                                                         'KOR': "이동식 디스크로 활성화"}
    #<Trader Sets>
    TEXTPACK['ACCOUNTS:BLOCKTITLE_TRADERSETS'] = {'ENG': "TRADER SETS",
                                                  'KOR': "트레이더 세트"}
    TEXTPACK['ACCOUNTS:TRADERSETS_FILTER_SEARCH'] = {'ENG': "SEARCH",
                                                     'KOR': "검색"}
    TEXTPACK['ACCOUNTS:TRADERSETS_FILTER_CAEXISTINGONLY'] = {'ENG': "AT LEAST ONE CURRENCY ANALYSIS ONLY",
                                                             'KOR': "최소 1개 이상의 종목분석만 표시"}
    TEXTPACK['ACCOUNTS:TRADERSETS_FILTER_TRADINGONLY'] = {'ENG': "TRADING ONLY",
                                                          'KOR': "거래중만 표시"}
    TEXTPACK['ACCOUNTS:TRADERSETS_FILTER_NOTTRADINGONLY'] = {'ENG': "NOT TRADING ONLY",
                                                             'KOR': "비거래중만 표시"}
    TEXTPACK['ACCOUNTS:TRADERSETS_FILTER_CONFIGUREDONLY'] = {'ENG': "CONFIGURED ONLY",
                                                             'KOR': "구성완료만 표시"}
    TEXTPACK['ACCOUNTS:TRADERSETS_FILTER_NOTCONFIGUREDONLY'] = {'ENG': "NOT CONFIGURED ONLY",
                                                                'KOR': "미구성만 표시"}
    TEXTPACK['ACCOUNTS:TRADERSETS_CURRENCYANALYSISCODE'] = {'ENG': "CURRENCY ANALYSIS CODE",
                                                            'KOR': "종목 분석 코드"}
    TEXTPACK['ACCOUNTS:TRADERSETS_TRADECONFIGURATIONCODE'] = {'ENG': "TRADE CONFIG CODE",
                                                              'KOR': "트레이드 설정 코드"}
    TEXTPACK['ACCOUNTS:TRADERSETS_PRIORITY'] = {'ENG': "PRIORITY",
                                                'KOR': "우선순위"}
    TEXTPACK['ACCOUNTS:TRADERSETS_TRADINGSTATUS'] = {'ENG': "TRADING STATUS",
                                                     'KOR': "거래 상태"}
    #<Currency Analysis>
    TEXTPACK['ACCOUNTS:BLOCKTITLE_CURRENCYANALYSIS'] = {'ENG': "CURRENCY ANALYSIS",
                                                        'KOR': "종목 분석"}
    #<Trade Configurations>
    TEXTPACK['ACCOUNTS:BLOCKTITLE_TRADECONFIGURATIONS'] = {'ENG': "TRADE CONFIGURATIONS",
                                                           'KOR': "트레이드 설정"}
    #<Apply Trader Sets Config>
    TEXTPACK['ACCOUNTS:BLOCKTITLE_APPLYTRADERSETSCONFIG'] = {'ENG': "APPLY TRADER SETS CONFIG",
                                                             'KOR': "트레이더 세트 설정 적용"}
    TEXTPACK['ACCOUNTS:APPLYTRADERSETSCONFIG_CURRENCYANALYSISCODE'] = {'ENG': "CURRENCY ANALYSIS CODE",
                                                                       'KOR': "종목 분석 코드"}
    TEXTPACK['ACCOUNTS:APPLYTRADERSETSCONFIG_TRADECONFIGURATIONCODE'] = {'ENG': "TRADE CONFIG CODE",
                                                                         'KOR': "트레이드 설정 코드"}
    TEXTPACK['ACCOUNTS:APPLYTRADERSETSCONFIG_APPLYTRADERSETCONFIG'] = {'ENG': "APPLY TRADER SET CONFIGURATION",
                                                                       'KOR': "트레이더 세트 설정 적용"}
    #<Position>
    TEXTPACK['ACCOUNTS:BLOCKTITLE_POSITION'] = {'ENG': "POSITION",
                                                 'KOR': "포지션"}
    TEXTPACK['ACCOUNTS:POSITION_ALLOCATEDBALANCE'] = {'ENG': "ALLOCATED BALANCE",
                                                      'KOR': "할당액"}
    TEXTPACK['ACCOUNTS:POSITION_AVAILABLEBALANCE'] = {'ENG': "AVAILABLE BALANCE",
                                                      'KOR': "사용 가능 잔액"}
    TEXTPACK['ACCOUNTS:POSITION_ENTRYPRICE'] = {'ENG': "ENTRY PRICE",
                                                'KOR': "진입가"}
    TEXTPACK['ACCOUNTS:POSITION_QUANTITY'] = {'ENG': "QUANTITY",
                                              'KOR': "보유수"}
    TEXTPACK['ACCOUNTS:POSITION_CURRENTPRICE'] = {'ENG': "CURRENT PRICE",
                                                  'KOR': "현재가"}
    TEXTPACK['ACCOUNTS:POSITION_LIQUIDATIONPRICE'] = {'ENG': "LIQUIDATION PRICE",
                                                      'KOR': "청산가"}
    TEXTPACK['ACCOUNTS:POSITION_UNREALIZEDPNL'] = {'ENG': "UNREALIZED PNL",
                                                   'KOR': "미실현 손익"}
#PAGE 'ACCOUNTS' END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#PAGE 'AUTOTRADE' -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
if (True):
    #<Market>
    TEXTPACK['AUTOTRADE:TITLE'] = {'ENG': "AUTOTRADE",
                                   'KOR': "오토트레이드"}
    TEXTPACK['AUTOTRADE:BLOCKTITLE_MARKET'] = {'ENG': "MARKET",
                                               'KOR': "마켓"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_CURRENCIES'] = {'ENG': "CURRENCY LIST",
                                                      'KOR': "종목 리스트"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_FILTER'] = {'ENG': "FILTER",
                                                  'KOR': "필터"}
    TEXTPACK['AUTOTRADE:MARKET&FILTER_SEARCH'] = {'ENG': "SEARCH",
                                                  'KOR': "검색"}
    TEXTPACK['AUTOTRADE:MARKET&FILTER_TRADINGTRUE'] = {'ENG': "TRADING O",
                                                       'KOR': "거래중 O"}
    TEXTPACK['AUTOTRADE:MARKET&FILTER_TRADINGFALSE'] = {'ENG': "TRADING X",
                                                        'KOR': "거래중 X"}
    TEXTPACK['AUTOTRADE:MARKET&FILTER_MINNUMBEROFKLINES'] = {'ENG': "MIN. # OF KLINES",
                                                             'KOR': "최소 KLINE 갯수"}
    TEXTPACK['AUTOTRADE:MARKET&FILTER_SORTBY'] = {'ENG': "SORT BY",
                                                  'KOR': "정렬 기준"}
    TEXTPACK['AUTOTRADE:MARKET&FILTER_ID'] = {'ENG': "ID",
                                              'KOR': "ID"}
    TEXTPACK['AUTOTRADE:MARKET&FILTER_SYMBOL'] = {'ENG': "SYMBOL",
                                                  'KOR': "심볼"}
    TEXTPACK['AUTOTRADE:MARKET&FILTER_FIRSTKLINE'] = {'ENG': "FIRST KLINE",
                                                      'KOR': "최초 KLINE"}
    TEXTPACK['AUTOTRADE:MARKET&CURRENCIES_NCURRENCIES'] = {'ENG': "N SYMBOLS",
                                                           'KOR': "종목 수"}
    TEXTPACK['AUTOTRADE:MARKET&CURRENCIES_INDEX'] = {'ENG': "INDEX",
                                                      'KOR': "인덱스"}
    TEXTPACK['AUTOTRADE:MARKET&CURRENCIES_SYMBOL'] = {'ENG': "SYMBOL",
                                                      'KOR': "심볼"}
    TEXTPACK['AUTOTRADE:MARKET&CURRENCIES_STATUS'] = {'ENG': "STATUS",
                                                      'KOR': "상태"}
    TEXTPACK['AUTOTRADE:MARKET&CURRENCIES_FIRSTKLINE'] = {'ENG': "FIRST KLINE",
                                                          'KOR': "최초 KLINE"}
    TEXTPACK['AUTOTRADE:MARKET&CURRENCIES_STATUS_TRADING'] = {'ENG': "TRADING",
                                                              'KOR': "거래중"}
    TEXTPACK['AUTOTRADE:MARKET&CURRENCIES_STATUS_SETTLING'] = {'ENG': "SETTLING",
                                                               'KOR': "정산중"}
    TEXTPACK['AUTOTRADE:MARKET&CURRENCIES_STATUS_REMOVED'] = {'ENG': "REMOVED",
                                                              'KOR': "폐지"}
    TEXTPACK['AUTOTRADE:MARKET&INFORMATION_CURRENCYID'] = {'ENG': "CURRENCY ID",
                                                           'KOR': "화폐 ID"}
    TEXTPACK['AUTOTRADE:MARKET&INFORMATION_DATARANGE'] = {'ENG': "DATA RANGE",
                                                          'KOR': "데이터 범위"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_TOANALYSISLIST'] = {'ENG': "ADD TO ANALYSIS LIST", 
                                                          'KOR': "분석 리스트에 추가"}
    TEXTPACK['AUTOTRADE:MARKET&TOANALYSISLIST_CACLIST'] = {'ENG': "CAC LIST",
                                                           'KOR': "CAC 리스트"}
    TEXTPACK['AUTOTRADE:MARKET&TOANALYSISLIST_ANALYSISCODE'] = {'ENG': "CA CODE",
                                                                'KOR': "CA 코드"}
    TEXTPACK['AUTOTRADE:MARKET&TOANALYSISLIST_ADD'] = {'ENG': "ADD",
                                                       'KOR': "추가"}
    #<Trade Manager>
    TEXTPACK['AUTOTRADE:BLOCKTITLE_TRADEMANAGER'] = {'ENG': "TRADE MANAGER",
                                                     'KOR': "트레이드 매니저"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_ANALYZERS'] = {'ENG': "ANALYZERS",
                                                     'KOR': "분석기"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFANALYZERS'] = {'ENG': "# OF ANALYZERS",
                                                                       'KOR': "분석기 수"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCAUNALLOCATED'] = {'ENG': "[UNALLOCATED]",
                                                                           'KOR': "[비할당]"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCAALLOCATED'] = {'ENG': "[ALLOCATED]",
                                                                         'KOR': "[할당]"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCACONFIGNOTFOUND'] = {'ENG': "[CONFIGNOTFOUND]",
                                                                              'KOR': "[분석설정없음]"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCACURRENCYNOTFOUND'] = {'ENG': "[CURRENCYNOTFOUND]",
                                                                                'KOR': "[종목없음]"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCAWAITINGTRADING'] = {'ENG': "[WAITINGTRADING]",
                                                                              'KOR': "[거래대기중]"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&NANALYZERS_AVERAGEANALYSISGENERATIONTIME'] = {'ENG': "AVG ANALYSIS TIME",
                                                                                   'KOR': "평균 분석 시간"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&NANALYZERS_ANALYZER'] = {'ENG': "ANALYZER",
                                                              'KOR': "분석기"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCATOTAL'] = {'ENG': "[TOTAL]",
                                                                     'KOR': "[전체]"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCAWAITINGSTREAM'] = {'ENG': "[WAITINGSTREAM]",
                                                                             'KOR': "[스트림대기중]"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCAWAITINGDATAAVAILABLE'] = {'ENG': "[WAITINGDA]",
                                                                                    'KOR': "[데이터대기중]"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCAPREPARING'] = {'ENG': "[PREPARING]",
                                                                         'KOR': "[준비중]"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCAANALYZINGREALTIME'] = {'ENG': "[ANALYZINGRT]",
                                                                                 'KOR': "[실시간분석중]"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCAERROR'] = {'ENG': "[ERROR]",
                                                                     'KOR': "[에러]"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCURRENCYANALYSIS'] = {'ENG': "# OF CURRENCY ANALYSIS",
                                                                              'KOR': "총 종목 분석 수"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_CONFIGURATIONCONTROL'] = {'ENG': "ANALYSIS CONFIGURATION CONTROL",
                                                                'KOR': "분석 설정 관리"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATIONCONTROL_CACLIST'] = {'ENG': "CAC LIST",
                                                                       'KOR': "CAC 리스트"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATIONCONTROL_CACCODE'] = {'ENG': "CAC CODE",
                                                                       'KOR': "CAC 코드"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATIONCONTROL_ADD'] = {'ENG': "ADD",
                                                                   'KOR': "추가"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATIONCONTROL_REMOVE'] = {'ENG': "REMOVE",
                                                                      'KOR': "삭제"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_CONFIGURATION'] = {'ENG': "ANALYSIS CONFIGURATION",
                                                         'KOR': "분석 설정"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_MAININDICATORS'] = {'ENG': "MAIN INDICATORS",
                                                          'KOR': "주요지표"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_SUBINDICATORS'] = {'ENG': "SUB INDICATORS",
                                                         'KOR': "보조지표"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_OTHERS'] = {'ENG': "OTHERS",
                                                  'KOR': "기타"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_MINCOMPLETEANALYSIS'] = {'ENG': "MIN # OF COMPLETE ANALYSIS",
                                                                            'KOR': "최소 완전분석 수"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_NANALYSISDISPLAY'] = {'ENG': "# OF ANALYSIS TO DISPLAY",
                                                                         'KOR': "디스플레이 분석 수"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'] = {'ENG': "TO CONFIGURATION MAIN",
                                                               'KOR': "설정 메인으로"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_SMASETUP'] = {'ENG': "MAIN INDICATOR SETUP - SMA",
                                                    'KOR': "주요지표 설정 - SMA"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_WMASETUP'] = {'ENG': "MAIN INDICATOR SETUP - WMA",
                                                    'KOR': "주요지표 설정 - WMA"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_EMASETUP'] = {'ENG': "MAIN INDICATOR SETUP - EMA",
                                                    'KOR': "주요지표 설정 - EMA"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_PSARSETUP'] = {'ENG': "MAIN INDICATOR SETUP - PSAR",
                                                     'KOR': "주요지표 설정 - PSAR"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_BOLSETUP'] = {'ENG': "MAIN INDICATOR SETUP - BOL",
                                                    'KOR': "주요지표 설정 - BOL"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_IVPSETUP'] = {'ENG': "MAIN INDICATOR SETUP - IVP",
                                                    'KOR': "주요지표 설정 - IVP"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_SWINGSETUP'] = {'ENG': "SUB INDICATOR SETUP - SWING",
                                                      'KOR': "보조지표 설정 - SWING"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_VOLSETUP'] = {'ENG': "SUB INDICATOR SETUP - VOL",
                                                    'KOR': "보조지표 설정 - VOL"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_NNASETUP'] = {'ENG': "SUB INDICATOR SETUP - NNA",
                                                    'KOR': "보조지표 설정 - NNA"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_MMACDSHORTSETUP'] = {'ENG': "SUB INDICATOR SETUP - MMACDSHORT",
                                                           'KOR': "보조지표 설정 - MMACDSHORT"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_MMACDLONGSETUP'] = {'ENG': "SUB INDICATOR SETUP - MMACDLONG",
                                                          'KOR': "보조지표 설정 - MMACDLONG"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_DMIxADXSETUP'] = {'ENG': "SUB INDICATOR SETUP - DMIxADX",
                                                        'KOR': "보조지표 설정 - DMIxADX"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_MFISETUP'] = {'ENG': "SUB INDICATOR SETUP - MFI",
                                                    'KOR': "보조지표 설정 - MFI"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_WOISETUP'] = {'ENG': "SUB INDICATOR SETUP - WOI",
                                                    'KOR': "보조지표 설정 - WOI"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_NESSETUP'] = {'ENG': "SUB INDICATOR SETUP - NES",
                                                    'KOR': "보조지표 설정 - NES"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'] = {'ENG': "INDEX",
                                                              'KOR': "인덱스"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'] = {'ENG': "NUMBER OF SAMPLES",
                                                                 'KOR': "샘플 수"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_SIGMA'] = {'ENG': "SIGMA",
                                                              'KOR': "시그마"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_AF0'] = {'ENG': "AF0",
                                                            'KOR': "AF0"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_AF+'] = {'ENG': "AF+",
                                                            'KOR': "AF+"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_AFMAX'] = {'ENG': "AFMax",
                                                              'KOR': "AFMax"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_BANDWIDTH'] = {'ENG': "BW",
                                                                  'KOR': "BW"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_BOLMATYPE'] = {'ENG': "BOL MA TYPE",
                                                                  'KOR': "BOL 이동평균 타입"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_GAMMAFACTOR'] = {'ENG': "GAMMA FACTOR",
                                                                    'KOR': "감마 인수"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_DELTAFACTOR'] = {'ENG': "DELTA FACTOR",
                                                                    'KOR': "델타 인수"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_SWINGRANGE'] = {'ENG': "SWING ANGE",
                                                                   'KOR': "스윙 범위"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_SMA'] = {'ENG': "SMA",
                                                            'KOR': "단순이동평균"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_EMA'] = {'ENG': "EMA",
                                                            'KOR': "지수이동평균"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_WMA'] = {'ENG': "WMA",
                                                            'KOR': "가중이동평균"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_VOLTYPE_BASE'] = {'ENG': "BASE",
                                                                     'KOR': "BASE"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_VOLTYPE_QUOTE'] = {'ENG': "QUOTE",
                                                                      'KOR': "QUOTE"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_VOLTYPE_BASETB'] = {'ENG': "BASE TAKER BUY",
                                                                       'KOR': "BASE TAKER BUY"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_VOLTYPE_QUOTETB'] = {'ENG': "QUOTE TAKER BUY",
                                                                        'KOR': "QUOTE TAKER BUY"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_VOLUMETYPE'] = {'ENG': "VOLUME TYPE",
                                                                   'KOR': "거래량 타입"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_VOLMATYPE'] = {'ENG': "VOL MA TYPE",
                                                                  'KOR': "거래량 이동평균 타입"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_NEURALNETWORKCODE'] = {'ENG': "NN CODE",
                                                                          'KOR': "신경망 코드"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_ALPHA'] = {'ENG': "ALPHA",
                                                              'KOR': "알파"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_BETA'] = {'ENG': "BETA",
                                                             'KOR': "베타"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_MMACDSIGNALINTERVAL'] = {'ENG': "MMACD SIGNAL INTERVAL",
                                                                            'KOR': "MMACD 시그널 기간"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CONFIGURATION_MULTIPLIER'] = {'ENG': "MULTIPLIER",
                                                                   'KOR': "멀티플라이어"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_CURRENCYANALYSISLIST'] = {'ENG': "CURRENCY ANALYSIS LIST",
                                                                'KOR': "종목 분석 리스트"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISFILTER_SEARCH'] = {'ENG': "SEARCH",
                                                                        'KOR': "검색"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISFILTER_SORTBY'] = {'ENG': "SORT BY",
                                                                        'KOR': "정렬 기준"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISFILTER_ID'] = {'ENG': "ID",
                                                                    'KOR': "ID"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISFILTER_ANALYZER'] = {'ENG': "ANALYZER",
                                                                          'KOR': "분석기"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISFILTER_ANALYSISCODE'] = {'ENG': "ANALYSIS CODE",
                                                                            'KOR': "분석 코드"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISFILTER_SYMBOL'] = {'ENG': "SYMBOL",
                                                                        'KOR': "종목 심볼"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISFILTER_CACCODE'] = {'ENG': "CAC CODE",
                                                                         'KOR': "CAC 코드"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISFILTER_FIRSTKLINE'] = {'ENG': "FIRST KLINE",
                                                                            'KOR': "종목 최초 KLINE"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_INDEX'] = {'ENG': "INDEX",
                                                                     'KOR': "인덱스"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_CACODE'] = {'ENG': "CA CODE",
                                                                      'KOR': "CA 코드"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_SYMBOL'] = {'ENG': "SYMBOL",
                                                                      'KOR': "심볼"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS'] = {'ENG': "STATUS",
                                                                      'KOR': "상태"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_CURRENCYNOTFOUND'] = {'ENG': "NO CURRENCY",
                                                                                       'KOR': "종목 없음"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_CONFIGNOTFOUND'] = {'ENG': "NO CAC",
                                                                                     'KOR': "CAC 없음"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_WAITINGTRADING'] = {'ENG': "W.TRADING",
                                                                                     'KOR': "거래 대기중"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_WAITINGNNCDATA'] = {'ENG': "W.NNCDATA",
                                                                                     'KOR': "NNCDATA 대기중"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_WAITINGSTREAM'] = {'ENG': "W.STREAM",
                                                                                    'KOR': "스트리밍 대기중"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_WAITINGDATAAVAILABLE'] = {'ENG': "W.DATA",
                                                                                           'KOR': "데이터수집중"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_PREP_QUEUED'] = {'ENG': "QUEUED",
                                                                                  'KOR': "대기중"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_PREP_ANALYZINGKLINES'] = {'ENG': "I.ANALYZING",
                                                                                           'KOR': "초기분석중"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_ANALYZINGREALTIME'] = {'ENG': "ANALYZING",
                                                                                        'KOR': "분석중"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_ERROR'] = {'ENG': "ERROR",
                                                                            'KOR': "에러"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISINFORMATION_CONFIGURATIONCODE'] = {'ENG': "CAC CODE",
                                                                                        'KOR': "CAC 코드"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISINFORMATION_ALLOCATEDANALYZER'] = {'ENG': "ALLOCATED ANALYZER",
                                                                                        'KOR': "할당 분석기"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISINFORMATION_VIEWCURRENCYANALYSISCHART'] = {'ENG': "VIEW CURRENCY ANALYSIS CHART",
                                                                                                'KOR': "종목 분석 차트 보기"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISCONTROL_REMOVEANALYSIS'] = {'ENG': "REMOVE ANALYSIS",
                                                                                 'KOR': "종목 분석 삭제"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_TRADECONFIGURATION'] = {'ENG': "TRADE CONFIGURATION",
                                                              'KOR': "트레이드 설정"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_LEVERAGE'] = {'ENG': "LEVERAGE",
                                                                      'KOR': "레버리지"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_MARGINTYPE'] = {'ENG': "MARGIN TYPE",
                                                                        'KOR': "마진 타입"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_MARGINTYPE_CROSSED'] = {'ENG': "CROSSED",
                                                                                'KOR': "교차"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_MARGINTYPE_ISOLATED'] = {'ENG': "ISOLATED",
                                                                                 'KOR': "격리"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TCMODE'] = {'ENG': "TC MODE",
                                                                    'KOR': "TC 모드"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TCMODE_TS'] = {'ENG': "TRADE SCENARIO",
                                                                       'KOR': "트레이드 시나리오"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TCMODE_RQPM'] = {'ENG': "RQPM",
                                                                         'KOR': "RQPM"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_DIRECTION'] = {'ENG': "DIRECTION",
                                                                       'KOR': "방향"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_FULLSTOPLOSSIMMEDIATE'] = {'ENG': "FSL (IMMED)",
                                                                                   'KOR': "FSL (IMMED)"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_FULLSTOPLOSSCLOSE'] = {'ENG': "FSL (CLOSE)",
                                                                               'KOR': "FSL (CLOSE)"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_POSTSTOPLOSSREENTRY'] = {'ENG': "POST-STOPLOSS REENTRY",
                                                                                 'KOR': "STOPLOSS 이후 재진입"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_WEIGHTREDUCE'] = {'ENG': "WR (ACT / AMT)",
                                                                          'KOR': "WR (ACT / AMT)"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_REACHANDFALL'] = {'ENG': "RAF",
                                                                          'KOR': "RAF"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO'] = {'ENG': "TRADE SCENARIO",
                                                                           'KOR': "트레이드 시나리오"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_ENTRY'] = {'ENG': "ENTRY",
                                                                                 'KOR': "진입"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_EXIT'] = {'ENG': "EXIT",
                                                                                'KOR': "회수"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_PSL'] = {'ENG': "PARTIAL STOP-LOSS",
                                                                               'KOR': "부분적 스탑로스"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_ST_INDEX'] = {'ENG': "INDEX",
                                                                                    'KOR': "인덱스"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_ST_PD'] = {'ENG': "PD",
                                                                                 'KOR': "PD"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_ST_QD'] = {'ENG': "QD",
                                                                                 'KOR': "QD"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_PD'] = {'ENG': "PRICE DIFFERENCE",
                                                                              'KOR': "가격 차이"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_QD'] = {'ENG': "QUANTITY DETERMINATION",
                                                                              'KOR': "물량 결정"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_ADD'] = {'ENG': "ADD",
                                                                               'KOR': "추가"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_EDIT'] = {'ENG': "EDIT",
                                                                                'KOR': "수정"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_REMOVE'] = {'ENG': "REMOVE",
                                                                                  'KOR': "삭제"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_FUNCTIONTYPE'] = {'ENG': "FUNCTION TYPE",
                                                                          'KOR': "함수 타입"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_FUNCTIONSIDE'] = {'ENG': "FUNCTION SIDE",
                                                                          'KOR': "함수 방향"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_PARAMETER_INDEX'] = {'ENG': "INDEX",
                                                                             'KOR': "인덱스"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_PARAMETER_NAME'] = {'ENG': "NAME",
                                                                            'KOR': "변수명"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_PARAMETER_VALUE'] = {'ENG': "VALUE",
                                                                             'KOR': "변수값"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_PARAMETER'] = {'ENG': "PARAMETER",
                                                                       'KOR': "변수"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_SET'] = {'ENG': "SET",
                                                                 'KOR': "설정"}
    TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_TRADECONFIGURATIONCONTROL'] = {'ENG': "TRADE CONFIGURATIONS CONTROL",
                                                                     'KOR': "트레이드 설정 관리"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONS'] = {'ENG': "TC LIST",
                                                                                   'KOR': "TC 리스트"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONCODE'] = {'ENG': "TC CODE",
                                                                                      'KOR': "TC 코드"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATIONCONTROL_ADD'] = {'ENG': "ADD",
                                                                        'KOR': "추가"}
    TEXTPACK['AUTOTRADE:TRADEMANAGER&TRADECONFIGURATIONCONTROL_REMOVE'] = {'ENG': "REMOVE",
                                                                           'KOR': "삭제"}
#PAGE 'AUTOTRADE' END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#PAGE 'CURRENCYANALYSIS' ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
if (True):
    TEXTPACK['CURRENCYANALYSIS:TITLE'] = {'ENG': "CURRENCY ANALYSIS",
                                          'KOR': "종목 분석"}
    #<Currency Analysis List>
    TEXTPACK['CURRENCYANALYSIS:BLOCKTITLE_CURRENCYANALYSISLIST'] = {'ENG': "CURRENCY ANALYSIS LIST",
                                                                    'KOR': "종목 분석 리스트"}
    #---Filter
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_SEARCH'] = {'ENG': "SEARCH",
                                                                'KOR': "검색"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_SORTBY'] = {'ENG': "SORT BY",
                                                                'KOR': "정렬 기준"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_ID'] = {'ENG': "ID",
                                                            'KOR': "ID"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_ANALYZER'] = {'ENG': "ANALYZER",
                                                                  'KOR': "분석기"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_CACODE'] = {'ENG': "CA CODE",
                                                                'KOR': "CA 코드"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_SYMBOL'] = {'ENG': "SYMBOL",
                                                                'KOR': "종목 심볼"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_CACCODE'] = {'ENG': "CAC CODE",
                                                                 'KOR': "CAC 코드"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_STATUS'] = {'ENG': "STATUS",
                                                                'KOR': "상태"}
    #---List & Information
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_INDEX'] = {'ENG': "INDEX",
                                                               'KOR': "인덱스"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_CURRENCYANALYSISCODE'] = {'ENG': "CA CODE",
                                                                              'KOR': "CA 코드"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_CURRENCYSYMBOL'] = {'ENG': "SYMBOL",
                                                                        'KOR': "심볼"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_STATUS_CURRENCYNOTFOUND'] = {'ENG': "NO CURRENCY",
                                                                                 'KOR': "종목 없음"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_STATUS_CONFIGNOTFOUND'] = {'ENG': "NO CAC",
                                                                               'KOR': "CAC 없음"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_STATUS_WAITINGTRADING'] = {'ENG': "W.TRADING",
                                                                               'KOR': "거래 대기중"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_STATUS_WAITINGNNCDATA'] = {'ENG': "W.NNCDATA",
                                                                               'KOR': "NNCDATA 대기중"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_STATUS_WAITINGSTREAM'] = {'ENG': "W.STREAM",
                                                                              'KOR': "스트리밍 대기중"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_STATUS_WAITINGDATAAVAILABLE'] = {'ENG': "W.DATA",
                                                                                     'KOR': "데이터수집중"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_STATUS_PREP_QUEUED'] = {'ENG': "A.QUEUED",
                                                                            'KOR': "분석 대기열"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_STATUS_PREP_ANALYZINGKLINES'] = {'ENG': "I.ANALYZING",
                                                                                     'KOR': "초기분석중"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_STATUS_ANALYZINGREALTIME'] = {'ENG': "ANALYZING",
                                                                                  'KOR': "분석중"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_STATUS_ERROR'] = {'ENG': "ERROR",
                                                                      'KOR': "에러 발생"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_CONFIGURATIONCODE'] = {'ENG': "CAC CODE",
                                                                           'KOR': "CAC 코드"}
    TEXTPACK['CURRENCYANALYSIS:CURRENCYANALYSISLIST_ALLOCATEDANALYZER'] = {'ENG': "ALLOCATED ANALYZER",
                                                                           'KOR': "할당 분석기"}
    #<Chart>
    TEXTPACK['CURRENCYANALYSIS:BLOCKTITLE_CHART'] = {'ENG': "CURRENCY ANALYSIS CHART",
                                                     'KOR': "종목 분석 차트"}
#PAGE 'CURRENCYANALYSIS' END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#PAGE 'ACCOUNTHISTORY' --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
if (True):
    TEXTPACK['ACCOUNTHISTORY:TITLE'] = {'ENG': "ACCOUNT HISTORY",
                                        'KOR': "계정 기록"}
    #<Accounts List>
    TEXTPACK['ACCOUNTHISTORY:BLOCKTITLE_ACCOUNTSLIST'] = {'ENG': "ACCOUNTS LIST",
                                                        'KOR': "계정 리스트"}
    TEXTPACK['ACCOUNTHISTORY:ACCOUNTLIST_VIRTUAL'] = {'ENG': "VIRTUAL ONLY",
                                                    'KOR': "가상계정만 표시"}
    TEXTPACK['ACCOUNTHISTORY:ACCOUNTLIST_ACTUAL'] = {'ENG': "ACTUAL ONLY",
                                                   'KOR': "실제계정만 표시"}
    TEXTPACK['ACCOUNTHISTORY:ACCOUNTLIST_INDEX'] = {'ENG': "INDEX",
                                                  'KOR': "인덱스"}
    TEXTPACK['ACCOUNTHISTORY:ACCOUNTLIST_LOCALID'] = {'ENG': "LOCAL ID",
                                                    'KOR': "로컬 ID"}
    TEXTPACK['ACCOUNTHISTORY:ACCOUNTLIST_TYPE'] = {'ENG': "TYPE",
                                                 'KOR': "타입"}
    TEXTPACK['ACCOUNTHISTORY:ACCOUNTLIST_STATUS'] = {'ENG': "STATUS",
                                                   'KOR': "상태"}
    TEXTPACK['ACCOUNTHISTORY:ACCOUNTLIST_TRADESTATUS'] = {'ENG': "TRADE STATUS",
                                                        'KOR': "거래 상태"}
    #<Acounts Information>
    TEXTPACK['ACCOUNTHISTORY:BLOCKTITLE_ACCOUNTSINFORMATION'] = {'ENG': "ACCOUNTS INFORMATION",
                                                               'KOR': "계정 정보"}
    TEXTPACK['ACCOUNTHISTORY:ACCOUNTSINFORMATION_LOCALID'] = {'ENG': "LOCAL ID",
                                                            'KOR': "로컬 ID"}
    TEXTPACK['ACCOUNTHISTORY:ACCOUNTSINFORMATION_BINANCEUID'] = {'ENG': "BINANCE UID",
                                                               'KOR': "바이낸스 UID"}
    TEXTPACK['ACCOUNTHISTORY:ACCOUNTSINFORMATION_ACCOUNTTYPE'] = {'ENG': "ACCOUNT TYPE",
                                                                'KOR': "계정 타입"}
    TEXTPACK['ACCOUNTHISTORY:ACCOUNTSINFORMATION_STATUS'] = {'ENG': "ACCOUNT STATUS",
                                                           'KOR': "계정 상태"}
    TEXTPACK['ACCOUNTHISTORY:ACCOUNTSINFORMATION_TRADESTATUS'] = {'ENG': "TRADE STATUS",
                                                                'KOR': "거래 상태"}
    #<History>
    TEXTPACK['ACCOUNTHISTORY:BLOCKTITLE_HISTORY'] = {'ENG': "HISTORY",
                                                     'KOR': "기록"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_VIEWTYPE'] = {'ENG': "VIEWER TYPE",
                                                   'KOR': "뷰어 타입"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_VIEWTYPE_HOURLYREPORTS'] = {'ENG': "HOURLY REPORTS",
                                                                 'KOR': "시간별 리포트"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_VIEWTYPE_TRADELOGS'] = {'ENG': "TRADE LOGS",
                                                             'KOR': "트레이드 기록"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_ASSET'] = {'ENG': "ASSET",
                                                'KOR': "자산"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_POSITION'] = {'ENG': "POSITION",
                                                   'KOR': "포지션"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_SELECTIONBOX_ALL'] = {'ENG': "ALL",
                                                           'KOR': "전체"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_LOAD'] = {'ENG': "LOAD",
                                               'KOR': "불러오기"}
    #<Balance>

    #<Trade Logs>
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_NETPROFIT'] = {'ENG': "NET PROFIT",
                                                              'KOR': "순이익"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_GAIN'] = {'ENG': "GAIN",
                                                         'KOR': "수익"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_LOSS'] = {'ENG': "LOSS",
                                                         'KOR': "손실"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_TRADINGFEE'] = {'ENG': "TRADING FEE",
                                                               'KOR': "수수료"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_TOTAL'] = {'ENG': "TOTAL",
                                                          'KOR': "전체"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_ASSET'] = {'ENG': "ASSET",
                                                          'KOR': "자산"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_POSITION'] = {'ENG': "POSITION",
                                                             'KOR': "포지션"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_TIMEUTC'] = {'ENG': "TIME (UTC)",
                                                            'KOR': "시간 (UTC)"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_SEARCH'] = {'ENG': "SEARCH",
                                                           'KOR': "검색"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_BUY'] = {'ENG': "BUY",
                                                        'KOR': "매수"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_SELL'] = {'ENG': "SELL",
                                                         'KOR': "매도"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_LIQUIDATION'] = {'ENG': "LIQUIDATION",
                                                                'KOR': "강제 청산"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_FSLIMMED'] = {'ENG': "FSLIMMED",
                                                             'KOR': "FSLIMMED"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_FSLCLOSE'] = {'ENG': "FSLCLOSE",
                                                             'KOR': "FSLCLOSE"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_ENTRY'] = {'ENG': "ENTRY",
                                                          'KOR': "진입"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_CLEAR'] = {'ENG': "CLEAR",
                                                          'KOR': "종료"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_EXIT'] = {'ENG': "EXIT",
                                                         'KOR': "회수"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_FORCECLEAR'] = {'ENG': "FORCE CLEAR",
                                                               'KOR': "강제 종료"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_UNKNOWN'] = {'ENG': "UNKNOWN",
                                                            'KOR': "미확인"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_INDEX'] = {'ENG': "INDEX",
                                                             'KOR': "인덱스"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_TIME'] = {'ENG': "TIME (UTC)",
                                                            'KOR': "시간 (UTC)"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_SYMBOL'] = {'ENG': "SYMBOL",
                                                              'KOR': "심볼"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_LOGICSOURCE'] = {'ENG': "LOGIC SOURCE",
                                                                   'KOR': "로직 소스"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_SIDE'] = {'ENG': "SIDE",
                                                            'KOR': "방향"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_QUANTITY'] = {'ENG': "QUANTITY",
                                                                'KOR': "거래수"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_PRICE'] = {'ENG': "PRICE",
                                                             'KOR': "거래가"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_PROFIT'] = {'ENG': "PROFIT",
                                                              'KOR': "이익"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_TRADINGFEE'] = {'ENG': "TRADING FEE",
                                                                  'KOR': "수수료"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_TOTALQUANTITY'] = {'ENG': "QUANTITY [T]",
                                                                     'KOR': "총 보유수"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_ENTRYPRICE'] = {'ENG': "ENTRY PRICE",
                                                                  'KOR': "진입가"}
    TEXTPACK['ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_WALLETBALANCE'] = {'ENG': "WALLET BALANCE",
                                                                     'KOR': "지갑 잔고"}
#PAGE 'ACCOUNTHISTORY' END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#PAGE 'MARKET' --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
if (True):
    TEXTPACK['MARKET:TITLE'] = {'ENG': "MARKET",
                                'KOR': "마켓"}
    #<Currency List>
    TEXTPACK['MARKET:BLOCKTITLE_CURRENCYLIST'] = {'ENG': "CURRENCY LIST",
                                                  'KOR': "종목 리스트"}
    #---Filter
    TEXTPACK['MARKET:CURRENCYLIST_SEARCH'] = {'ENG': "SEARCH",
                                              'KOR': "검색"}
    TEXTPACK['MARKET:CURRENCYLIST_TRADINGTRUE'] = {'ENG': "TRADING O",
                                                   'KOR': "거래중 O"}
    TEXTPACK['MARKET:CURRENCYLIST_TRADINGFALSE'] = {'ENG': "TRADING X",
                                                    'KOR': "거래중 X"}
    TEXTPACK['MARKET:CURRENCYLIST_MINNUMBEROFKLINES'] = {'ENG': "MIN. # OF KLINES",
                                                         'KOR': "최소 KLINE 갯수"}
    TEXTPACK['MARKET:CURRENCYLIST_SORTBY'] = {'ENG': "SORT BY",
                                              'KOR': "정렬 기준"}
    TEXTPACK['MARKET:CURRENCYLIST_ID'] = {'ENG': "ID",
                                          'KOR': "ID"}
    TEXTPACK['MARKET:CURRENCYLIST_SYMBOL'] = {'ENG': "SYMBOL",
                                              'KOR': "심볼"}
    TEXTPACK['MARKET:CURRENCYLIST_FIRSTKLINE'] = {'ENG': "FIRST KLINE",
                                                  'KOR': "최초 KLINE"}
    #---List & Information
    TEXTPACK['MARKET:CURRENCYLIST_INDEX'] = {'ENG': "INDEX",
                                             'KOR': "인덱스"}
    TEXTPACK['MARKET:CURRENCYLIST_STATUS_TRADING'] = {'ENG': "TRADING",
                                                      'KOR': "거래중"}
    TEXTPACK['MARKET:CURRENCYLIST_STATUS_SETTLING'] = {'ENG': "SETTLING",
                                                      'KOR': "정산중"}
    TEXTPACK['MARKET:CURRENCYLIST_STATUS_REMOVED'] = {'ENG': "REMOVED",
                                                      'KOR': "폐지"}
    TEXTPACK['MARKET:CURRENCYLIST_STATUS'] = {'ENG': "STATUS",
                                              'KOR': "상태"}
    TEXTPACK['MARKET:CURRENCYLIST_STATUS'] = {'ENG': "STATUS",
                                              'KOR': "상태"}
    TEXTPACK['MARKET:CURRENCYLIST_STATUS'] = {'ENG': "STATUS",
                                              'KOR': "상태"}
    TEXTPACK['MARKET:CURRENCYLIST_CURRENCYID'] = {'ENG': "CURRENCY ID",
                                                  'KOR': "화폐 ID"}
    TEXTPACK['MARKET:CURRENCYLIST_DATARANGE'] = {'ENG': "DATA RANGE",
                                                 'KOR': "데이터 범위"}
    #<Chart>
    TEXTPACK['MARKET:BLOCKTITLE_CHART'] = {'ENG': "CHART",
                                           'KOR': "차트"}
#PAGE 'MARKET' END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#PAGE 'SIMULATION' ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
if (True):
    TEXTPACK['SIMULATION:TITLE'] = {'ENG': "SIMULATION",
                                    'KOR': "시뮬레이션"}
    #<Simulators>
    TEXTPACK['SIMULATION:BLOCKTITLE_SIMULATORS'] = {'ENG': "SIMULATORS",
                                                    'KOR': "시뮬레이터"}
    TEXTPACK['SIMULATION:SIMULATORS_NUMBEROFSIMULATORS'] = {'ENG': "# OF SIMULATORS",
                                                            'KOR': "시뮬레이터 수"}
    TEXTPACK['SIMULATION:SIMULATORS_SIMULATIONSCOMPLETED'] = {'ENG': "[COMPLETED]",
                                                              'KOR': "[완료]"}
    TEXTPACK['SIMULATION:SIMULATORS_SIMULATOR'] = {'ENG': "SIMULATOR",
                                                   'KOR': "시뮬레이터"}
    TEXTPACK['SIMULATION:SIMULATORS_SIMULATIONSTOTAL'] = {'ENG': "[TOTAL]",
                                                          'KOR': "[전체]"}
    TEXTPACK['SIMULATION:SIMULATORS_SIMULATIONSQUEUED'] = {'ENG': "[QUEUED]",
                                                           'KOR': "[대기열]"}
    TEXTPACK['SIMULATION:SIMULATORS_SIMULATIONSPROCESSING'] = {'ENG': "[PROCESSING]",
                                                               'KOR': "[처리중]"}
    TEXTPACK['SIMULATION:SIMULATORS_SIMULATIONSPAUSED'] = {'ENG': "[PAUSED]",
                                                           'KOR': "[중지됨]"}
    TEXTPACK['SIMULATION:SIMULATORS_SIMULATIONSERROR'] = {'ENG': "[ERROR]",
                                                          'KOR': "[에러발생]"}
    TEXTPACK['SIMULATION:SIMULATORS_ACTIVATION'] = {'ENG': "ACTIVAITON",
                                                    'KOR': "활성화"}
    #<Simulations>
    TEXTPACK['SIMULATION:BLOCKTITLE_SIMULATIONS'] = {'ENG': "SIMULATIONS",
                                                     'KOR': "시뮬레이션"}
    TEXTPACK['SIMULATION:SIMULATIONS_SEARCH'] = {'ENG': "SEARCH",
                                                 'KOR': "검색"}
    TEXTPACK['SIMULATION:SIMULATIONS_SORTBY'] = {'ENG': "SORT BY",
                                                 'KOR': "정렬 기준"}
    TEXTPACK['SIMULATION:SIMULATIONS_SORTBY_INDEX'] = {'ENG': "INDEX",
                                                       'KOR': "인덱스"}
    TEXTPACK['SIMULATION:SIMULATIONS_SORTBY_SIMULATIONCODE'] = {'ENG': "SIMULATION CODE",
                                                                'KOR': "시뮬레이션 코드"}
    TEXTPACK['SIMULATION:SIMULATIONS_SORTBY_SIMULATIONRANGE'] = {'ENG': "SIMULATION RANGE",
                                                                 'KOR': "시뮬레이션 범위"}
    TEXTPACK['SIMULATION:SIMULATIONS_SORTBY_CREATIONTIME'] = {'ENG': "CREATION TIME",
                                                              'KOR': "생성 시간"}
    TEXTPACK['SIMULATION:SIMULATIONS_SORTBY_STATUS'] = {'ENG': "STATUS",
                                                        'KOR': "상태"}
    TEXTPACK['SIMULATION:SIMULATIONS_SORTBY_COMPLETION'] = {'ENG': "COMPLETION",
                                                            'KOR': "진행률"}
    TEXTPACK['SIMULATION:SIMULATIONS_ST_INDEX'] = {'ENG': "INDEX",
                                                   'KOR': "인덱스"}
    TEXTPACK['SIMULATION:SIMULATIONS_ST_SIMULATIONCODE'] = {'ENG': "SIMULATION CODE",
                                                            'KOR': "시뮬레이션 코드"}
    TEXTPACK['SIMULATION:SIMULATIONS_ST_SIMULATIONRANGE'] = {'ENG': "SIMULATION RANGE",
                                                             'KOR': "시뮬레이션 범위"}
    TEXTPACK['SIMULATION:SIMULATIONS_ST_CREATIONTIME'] = {'ENG': "CREATION TIME",
                                                          'KOR': "생성 시간"}
    TEXTPACK['SIMULATION:SIMULATIONS_ST_STATUS'] = {'ENG': "STATUS",
                                                    'KOR': "상태"}
    TEXTPACK['SIMULATION:SIMULATIONS_ST_COMPLETION'] = {'ENG': "COMPLETION",
                                                        'KOR': "진행률"}
    #<General>
    TEXTPACK['SIMULATION:BLOCKTITLE_GENERAL'] = {'ENG': "GENERAL",
                                                 'KOR': "일반"}
    TEXTPACK['SIMULATION:GENERAL_SIMULATIONCODE'] = {'ENG': "SIMULATION CODE",
                                                     'KOR': "시뮬레이션 코드"}
    TEXTPACK['SIMULATION:GENERAL_SIMULATIONRANGE'] = {'ENG': "SIMULATION RANGE",
                                                      'KOR': "시뮬레이션 범위"}
    TEXTPACK['SIMULATION:GENERAL_CREATIONTIME'] = {'ENG': "CREATION TIME",
                                                   'KOR': "생성 시간"}
    TEXTPACK['SIMULATION:GENERAL_ANALYSISEXPORT'] = {'ENG': "ANALYSIS EXPORT",
                                                     'KOR': "분석 내보내기"}
    TEXTPACK['SIMULATION:GENERAL_ANALYSISEXPORTPLOT'] = {'ENG': "ANALYSIS PLOT EXPORT",
                                                         'KOR': "분석 그래프 내보내기"}
    TEXTPACK['SIMULATION:GENERAL_ALLOCATEDSIMUALTOR'] = {'ENG': "ALLOCATED SIMULATOR",
                                                         'KOR': "할당 시뮬레이터"}
    TEXTPACK['SIMULATION:GENERAL_STATUS'] = {'ENG': "STATUS",
                                             'KOR': "상태"}
    TEXTPACK['SIMULATION:GENERAL_STATUS_COMPLETED'] = {'ENG': "COMPLETED",
                                                       'KOR': "완료"}
    TEXTPACK['SIMULATION:GENERAL_STATUS_QUEUED'] = {'ENG': "QUEUED",
                                                    'KOR': "대기중"}
    TEXTPACK['SIMULATION:GENERAL_STATUS_PROCESSING'] = {'ENG': "PROCESSING",
                                                        'KOR': "처리중"}
    TEXTPACK['SIMULATION:GENERAL_STATUS_PAUSED'] = {'ENG': "PAUSED",
                                                    'KOR': "정지중"}
    TEXTPACK['SIMULATION:GENERAL_STATUS_ERROR'] = {'ENG': "ERROR",
                                                   'KOR': "에러"}
    TEXTPACK['SIMULATION:GENERAL_ADD'] = {'ENG': "ADD",
                                          'KOR': "추가"}
    TEXTPACK['SIMULATION:GENERAL_REMOVE'] = {'ENG': "REMOVE",
                                             'KOR': "삭제"}
    TEXTPACK['SIMULATION:GENERAL_REPLICATECONFIGURATION'] = {'ENG': "REPLICATE CONFIGURATION",
                                                             'KOR': "시뮬레이션 설정 복사"}
    TEXTPACK['SIMULATION:GENERAL_VIEWRESULT'] = {'ENG': "VIEW RESULT",
                                                 'KOR': "결과 보기"}
    #<Positions>
    TEXTPACK['SIMULATION:BLOCKTITLE_POSITIONS'] = {'ENG': "POSITIONS",
                                                   'KOR': "포지션"}
    TEXTPACK['SIMULATION:POSITIONS_SEARCH'] = {'ENG': "SEARCH",
                                               'KOR': "검색"}
    TEXTPACK['SIMULATION:POSITIONS_SEARCH_SYMBOL'] = {'ENG': "SYMBOL",
                                                      'KOR': "심볼"}
    TEXTPACK['SIMULATION:POSITIONS_SEARCH_TCCODE'] = {'ENG': "TC CODE",
                                                      'KOR': "TC 코드"}
    TEXTPACK['SIMULATION:POSITIONS_SEARCH_CACCODE'] = {'ENG': "CAC CODE",
                                                       'KOR': "CAC 코드"}
    TEXTPACK['SIMULATION:POSITIONS_SORTBY'] = {'ENG': "SORT BY",
                                               'KOR': "정렬 기준"}
    TEXTPACK['SIMULATION:POSITIONS_SORTBY_INDEX'] = {'ENG': "INDEX",
                                                     'KOR': "인덱스"}
    TEXTPACK['SIMULATION:POSITIONS_SORTBY_SYMBOL'] = {'ENG': "SYMBOL",
                                                      'KOR': "심볼"}
    TEXTPACK['SIMULATION:POSITIONS_SORTBY_CACCODE'] = {'ENG': "CAC CODE",
                                                       'KOR': "CAC 코드"}
    TEXTPACK['SIMULATION:POSITIONS_SORTBY_TCCODE'] = {'ENG': "TC CODE",
                                                      'KOR': "TC 코드"}
    TEXTPACK['SIMULATION:POSITIONS_SORTBY_MARGINMODE'] = {'ENG': "MARGIN MODE",
                                                          'KOR': "마진 모드"}
    TEXTPACK['SIMULATION:POSITIONS_SORTBY_LEVERAGE'] = {'ENG': "LEVERAGE",
                                                        'KOR': "레버리지"}
    TEXTPACK['SIMULATION:POSITIONS_SORTBY_PRIORITY'] = {'ENG': "PRIORITY",
                                                        'KOR': "우선순위"}
    TEXTPACK['SIMULATION:POSITIONS_SORTBY_ASSUMEDRATIO'] = {'ENG': "ASSUMED RATIO",
                                                            'KOR': "가정율"}
    TEXTPACK['SIMULATION:POSITIONS_SORTBY_WEIGHTEDASSUMEDRATIO'] = {'ENG': "WEIGHTED ASSUMED RATIO",
                                                                    'KOR': "가중가정율"}
    TEXTPACK['SIMULATION:POSITIONS_SORTBY_ALLOCATEDBALANCE'] = {'ENG': "ALLOCATED BALANCE",
                                                                'KOR': "할당액"}
    TEXTPACK['SIMULATION:POSITIONS_SORTBY_MAXALLOCATEDBALANCE'] = {'ENG': "MAX ALLOCATED BALANCE",
                                                                   'KOR': "최대 할당액"}
    TEXTPACK['SIMULATION:POSITIONS_SORTBY_FIRSTKLINE'] = {'ENG': "FIRST KLINE",
                                                          'KOR': "최초 KLINE"}
    TEXTPACK['SIMULATION:POSITIONS_TRADABLEFILTER'] = {'ENG': "TRADABLE",
                                                       'KOR': "거래 가능"}
    TEXTPACK['SIMULATION:POSITIONS_FILTER_ALL'] = {'ENG': "ALL",
                                                   'KOR': "전체"}
    TEXTPACK['SIMULATION:POSITIONS_FILTER_TRUE'] = {'ENG': "TRUE",
                                                    'KOR': "참"}
    TEXTPACK['SIMULATION:POSITIONS_FILTER_FALSE'] = {'ENG': "FALSE",
                                                     'KOR': "거짓"}
    TEXTPACK['SIMULATION:POSITIONS_INITIALIZESETUP'] = {'ENG': "INITIALIZE SETUP",
                                                        'KOR': "설정 초기화"}
    TEXTPACK['SIMULATION:POSITIONS_SELECTEDPOSITIONS'] = {'ENG': "SELECTED POSITIONS",
                                                          'KOR': "선택된 포지션"}
    TEXTPACK['SIMULATION:POSITIONS_RELEASEALL'] = {'ENG': "RELEASE ALL",
                                                   'KOR': "전체 선택 해제"}
    TEXTPACK['SIMULATION:POSITIONS_ST_INDEX'] = {'ENG': "INDEX",
                                                 'KOR': "인덱스"}
    TEXTPACK['SIMULATION:POSITIONS_ST_SYMBOL'] = {'ENG': "SYMBOL",
                                                  'KOR': "심볼"}
    TEXTPACK['SIMULATION:POSITIONS_ST_CURRENCYANALYSISCONFIGURATIONCODE'] = {'ENG': "CAC CODE",
                                                                             'KOR': "CAC 코드"}
    TEXTPACK['SIMULATION:POSITIONS_ST_TRADECONFIGURATIONCODE'] = {'ENG': "TC CODE",
                                                                  'KOR': "TC 코드"}
    TEXTPACK['SIMULATION:POSITIONS_ST_MARGINMODE'] = {'ENG': "MARGIN MODE",
                                                      'KOR': "마진 모드"}
    TEXTPACK['SIMULATION:POSITIONS_ST_LEVERAGE'] = {'ENG': "LEVERAGE",
                                                    'KOR': "레버리지"}
    TEXTPACK['SIMULATION:POSITIONS_ST_PRIORITY'] = {'ENG': "PRIORITY",
                                                    'KOR': "우선순위"}
    TEXTPACK['SIMULATION:POSITIONS_ST_ASSUMEDRATIO'] = {'ENG': "ASMD%",
                                                        'KOR': "가정율"}
    TEXTPACK['SIMULATION:POSITIONS_ST_WEIGHTEDASSUMEDRATIO'] = {'ENG': "ASMD%[W]",
                                                                'KOR': "가중가정율"}
    TEXTPACK['SIMULATION:POSITIONS_ST_ALLOCATEDBALANCE'] = {'ENG': "ALLC.BAL.",
                                                            'KOR': "할당액"}
    TEXTPACK['SIMULATION:POSITIONS_ST_MAXALLOCATEDBALANCE'] = {'ENG': "MAX ALLC.BAL.",
                                                               'KOR': "최대 할당액"}
    TEXTPACK['SIMULATION:POSITIONS_ST_FIRSTKLINE'] = {'ENG': "FIRST KLINE",
                                                      'KOR': "최초 KLINE"}
    TEXTPACK['SIMULATION:POSITIONS_ST_TRADABLE'] = {'ENG': "TRADABLE",
                                                    'KOR': "거래 가능"}
    TEXTPACK['SIMULATION:POSITIONS_ST_MARKETSTATUS'] = {'ENG': "MARKET STATUS",
                                                        'KOR': "마켓 상태"}
    TEXTPACK['SIMULATION:POSITIONS_ST_MINNOTIONAL'] = {'ENG': "MIN NOTIONAL",
                                                       'KOR': "최소 가치"}
    TEXTPACK['SIMULATION:POSITIONS_MARKETSTATUS_TRADING'] = {'ENG': "TRADING",
                                                             'KOR': "거래중"}
    TEXTPACK['SIMULATION:POSITIONS_MARKETSTATUS_SETTLING'] = {'ENG': "SETTLING",
                                                              'KOR': "정산중"}
    TEXTPACK['SIMULATION:POSITIONS_MARKETSTATUS_REMOVED'] = {'ENG': "REMOVED",
                                                             'KOR': "폐지"}
    TEXTPACK['SIMULATION:POSITIONS_CURRENCYANALYSISCONFIGURATIONCODE'] = {'ENG': "CAC CODE",
                                                                          'KOR': "CAC 코드"}
    TEXTPACK['SIMULATION:POSITIONS_TRADECONFIGURATIONCODE'] = {'ENG': "TC CODE",
                                                               'KOR': "TC 코드"}
    TEXTPACK['SIMULATION:POSITIONS_RESET'] = {'ENG': "RESET",
                                              'KOR': "초기화"}
    TEXTPACK['SIMULATION:POSITIONS_ASSUMEDRATIO'] = {'ENG': "ASSUMED RATIO",
                                                     'KOR': "가정율"}
    TEXTPACK['SIMULATION:POSITIONS_PRIORITY'] = {'ENG': "PRIORITY",
                                                 'KOR': "우선순위"}
    TEXTPACK['SIMULATION:POSITIONS_MAXALLOCATEDBALANCE'] = {'ENG': "MAX ALLOCATED BALANCE",
                                                            'KOR': "최대 할당액"}
    TEXTPACK['SIMULATION:POSITIONS_APPLY'] = {'ENG': "APPLY",
                                              'KOR': "적용"}
    #<Assets>
    TEXTPACK['SIMULATION:BLOCKTITLE_ASSETS'] = {'ENG': "ASSETS",
                                                'KOR': "자산"}
    TEXTPACK['SIMULATION:ASSETS_ASSET'] = {'ENG': "ASSET",
                                           'KOR': "자산"}
    TEXTPACK['SIMULATION:ASSETS_INITIALWALLETBALANCE'] = {'ENG': "INITIAL WALLET BALANCE",
                                                          'KOR': "최초 지갑 잔고"}
    TEXTPACK['SIMULATION:ASSETS_ALLOCATIONRATIO'] = {'ENG': "ALLOCATION RATIO",
                                                     'KOR': "할당율"}
    TEXTPACK['SIMULATION:ASSETS_ALLOCATABLEBALANCE'] = {'ENG': "ALLOCATABLE BALANCE",
                                                        'KOR': "할당가능액"}
    TEXTPACK['SIMULATION:ASSETS_APPLY'] = {'ENG': "APPLY",
                                           'KOR': "적용"}
    TEXTPACK['SIMULATION:ASSETS_ASSUMEDRATIO'] = {'ENG': "ASSUMED RATIO",
                                                  'KOR': "가정율"}
    TEXTPACK['SIMULATION:ASSETS_WEIGHTEDASSUMEDRATIO'] = {'ENG': "ASSUMED RATIO [W]",
                                                          'KOR': "가중가정율"}
    TEXTPACK['SIMULATION:ASSETS_ALLOCATEDBALANCE'] = {'ENG': "ALLOCATED BALANCE",
                                                      'KOR': "할당액"}
    TEXTPACK['SIMULATION:ASSETS_MAXALLOCATEDBALANCE'] = {'ENG': "MAX ALLOCATED BALANCE",
                                                         'KOR': "최대 할당액"}
#PAGE 'SIMULATION' END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#PAGE 'SIMULATIONRESULT' ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
if (True):
    TEXTPACK['SIMULATIONRESULT:TITLE'] = {'ENG': "SIMULATION RESULT",
                                          'KOR': "시뮬레이션 결과"}
    #<Simulations>
    TEXTPACK['SIMULATIONRESULT:BLOCKTITLE_SIMULATIONS'] = {'ENG': "SIMULATIONS",
                                                           'KOR': "시뮬레이션"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONS_SEARCH'] = {'ENG': "SEARCH",
                                                       'KOR': "검색"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONS_SORTBY'] = {'ENG': "SORT BY",
                                                       'KOR': "정렬 기준"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONS_SORTBY_INDEX'] = {'ENG': "INDEX",
                                                             'KOR': "인덱스"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONS_SORTBY_SIMULATIONCODE'] = {'ENG': "SIMULATION CODE",
                                                                      'KOR': "시뮬레이션 코드"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONS_SORTBY_SIMULATIONRANGE'] = {'ENG': "SIMULATION RANGE",
                                                                       'KOR': "시뮬레이션 범위"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONS_SORTBY_CREATIONTIME'] = {'ENG': "CREATION TIME",
                                                                    'KOR': "생성 시간"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONS_ST_INDEX'] = {'ENG': "INDEX",
                                                         'KOR': "인덱스"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONS_ST_SIMULATIONCODE'] = {'ENG': "SIMULATION CODE",
                                                                  'KOR': "시뮬레이션 코드"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONS_ST_SIMULATIONRANGE'] = {'ENG': "SIMULATION RANGE",
                                                                   'KOR': "시뮬레이션 범위"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONS_ST_CREATIONTIME'] = {'ENG': "CREATION TIME",
                                                                'KOR': "생성 시간"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONS_SIMULATIONCODE'] = {'ENG': "SIMULATION CODE",
                                                               'KOR': "시뮬레이션 코드"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONS_SIMULATIONRANGE'] = {'ENG': "SIMULATION RANGE",
                                                                'KOR': "시뮬레이션 범위"}
    #<Simulation Summary>
    TEXTPACK['SIMULATIONRESULT:BLOCKTITLE_SIMULATIONSUMMARY'] = {'ENG': "RESULT SUMMARY",
                                                                 'KOR': "결과 요약"}
    TEXTPACK['SIMULATIONRESULT:RESULTSUMMARY_ASSET'] = {'ENG': "ASSET",
                                                        'KOR': "자산"}
    TEXTPACK['SIMULATIONRESULT:RESULTSUMMARY_ASSETSELECTION_TOTAL'] = {'ENG': "TOTAL",
                                                                       'KOR': "전체"}
    TEXTPACK['SIMULATIONRESULT:RESULTSUMMARY_NTRADEDAYS'] = {'ENG': "TRADE DAYS",
                                                             'KOR': "거래일"}
    TEXTPACK['SIMULATIONRESULT:RESULTSUMMARY_NTRADES_TOTAL'] = {'ENG': "N TRADES",
                                                                'KOR': "거래 수"}
    TEXTPACK['SIMULATIONRESULT:RESULTSUMMARY_NETPROFIT'] = {'ENG': "NET PROFIT",
                                                            'KOR': "순이익"}
    TEXTPACK['SIMULATIONRESULT:RESULTSUMMARY_GAINS'] = {'ENG': "GAINS",
                                                        'KOR': "수익"}
    TEXTPACK['SIMULATIONRESULT:RESULTSUMMARY_LOSSES'] = {'ENG': "LOSSES",
                                                         'KOR': "손실"}
    TEXTPACK['SIMULATIONRESULT:RESULTSUMMARY_FEES'] = {'ENG': "FEES",
                                                       'KOR': "수수료"}
    TEXTPACK['SIMULATIONRESULT:RESULTSUMMARY_WALLETBALANCE1'] = {'ENG': "WB (INITIAL / FINAL)",
                                                                 'KOR': "지갑 잔고 (최초 / 최종)"}
    TEXTPACK['SIMULATIONRESULT:RESULTSUMMARY_WALLETBALANCE2'] = {'ENG': "WB (MIN / MAX)",
                                                                 'KOR': "지갑 잔고 (최소 / 최대)"}
    TEXTPACK['SIMULATIONRESULT:RESULTSUMMARY_WALLETBALANCEGROWTHRATE'] = {'ENG': "WB GROWTH RATE",
                                                                          'KOR': "지갑 잔고 성장률"}
    TEXTPACK['SIMULATIONRESULT:RESULTSUMMARY_WALLETBALANCEVOLATILITY'] = {'ENG': "WB VOLATILITY [99.7 %]",
                                                                          'KOR': "지갑 잔고 변동성 [99.7 %]"}
    #<Result Detail>
    TEXTPACK['SIMULATIONRESULT:BLOCKTITLE_SIMULATIONDETAIL'] = {'ENG': "SIMULATION DETAIL",
                                                                'KOR': "시뮬레이션 상세정보"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_VIEWTYPE'] = {'ENG': "VIEWER TYPE",
                                                              'KOR': "뷰어 타입"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_VIEWTYPE_ASSETPOSITIONSETUP'] = {'ENG': "ASSET & POSITION SETUP",
                                                                                 'KOR': "자산 & 포지션 설정"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_VIEWTYPE_CONFIGURATIONS'] = {'ENG': "CA & TRADE CONFIGURATIONS",
                                                                             'KOR': "종목분석 & 트레이드 설정"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_VIEWTYPE_DAILYREPORTS'] = {'ENG': "DAILY REPORTS",
                                                                           'KOR': "일일 리포트"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_VIEWTYPE_TRADELOGS'] = {'ENG': "TRADE LOGS",
                                                                        'KOR': "트레이드 기록"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_VIEWTYPE_POSITIONCHART'] = {'ENG': "POSITION CHART",
                                                                            'KOR': "포지션 차트"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSET'] = {'ENG': "ASSET",
                                                           'KOR': "자산"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_POSITION'] = {'ENG': "POSITION",
                                                              'KOR': "포지션"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_SELECTIONBOX_ALL'] = {'ENG': "ALL",
                                                                      'KOR': "전체"}
    #---Asset & Position Setup
    #------Positions
    TEXTPACK['SIMULATIONRESULT:BLOCKTITLE_SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS'] = {'ENG': "POSITIONS",
                                                                                             'KOR': "포지션"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCH'] = {'ENG': "SEARCH",
                                                                                         'KOR': "검색"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCH_SYMBOL'] = {'ENG': "SYMBOL",
                                                                                                'KOR': "심볼"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCH_TCCODE'] = {'ENG': "TC CODE",
                                                                                                'KOR': "TC 코드"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SEARCH_CACCODE'] = {'ENG': "CAC CODE",
                                                                                                 'KOR': "CAC 코드"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY'] = {'ENG': "SORT BY",
                                                                                         'KOR': "정렬 기준"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_INDEX'] = {'ENG': "INDEX",
                                                                                               'KOR': "인덱스"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_SYMBOL'] = {'ENG': "SYMBOL",
                                                                                                'KOR': "심볼"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_CACCODE'] = {'ENG': "CAC CODE",
                                                                                                 'KOR': "CAC 코드"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_TCCODE'] = {'ENG': "TC CODE",
                                                                                                'KOR': "TC 코드"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_MARGINMODE'] = {'ENG': "MARGIN MODE",
                                                                                                    'KOR': "마진 모드"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_LEVERAGE'] = {'ENG': "LEVERAGE",
                                                                                                  'KOR': "레버리지"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_PRIORITY'] = {'ENG': "PRIORITY",
                                                                                                  'KOR': "우선순위"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_ASSUMEDRATIO'] = {'ENG': "ASSUMED RATIO",
                                                                                                      'KOR': "가정율"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_WEIGHTEDASSUMEDRATIO'] = {'ENG': "WEIGHTED ASSUMED RATIO",
                                                                                                              'KOR': "가중가정율"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_ALLOCATEDBALANCE'] = {'ENG': "ALLOCATED BALANCE",
                                                                                                          'KOR': "할당액"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_MAXALLOCATEDBALANCE'] = {'ENG': "MAX ALLOCATED BALANCE",
                                                                                                             'KOR': "최대 할당액"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_SORTBY_FIRSTKLINE'] = {'ENG': "FIRST KLINE",
                                                                                                    'KOR': "최초 KLINE"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_INITIALIZESETUP'] = {'ENG': "INITIALIZE SETUP",
                                                                                                  'KOR': "설정 초기화"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_INDEX'] = {'ENG': "INDEX",
                                                                                           'KOR': "인덱스"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_SYMBOL'] = {'ENG': "SYMBOL",
                                                                                            'KOR': "심볼"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_CURRENCYANALYSISCONFIGURATIONCODE'] = {'ENG': "CAC CODE",
                                                                                                                       'KOR': "CAC 코드"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_TRADECONFIGURATIONCODE'] = {'ENG': "TC CODE",
                                                                                                            'KOR': "TC 코드"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_MARGINMODE'] = {'ENG': "MARGIN MODE",
                                                                                                'KOR': "마진 모드"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_LEVERAGE'] = {'ENG': "LEVERAGE",
                                                                                              'KOR': "레버리지"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_PRIORITY'] = {'ENG': "PRIORITY",
                                                                                              'KOR': "우선순위"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_ASSUMEDRATIO'] = {'ENG': "ASMD%",
                                                                                                  'KOR': "가정율"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_WEIGHTEDASSUMEDRATIO'] = {'ENG': "ASMD%[W]",
                                                                                                          'KOR': "가중가정율"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_ALLOCATEDBALANCE'] = {'ENG': "ALLC.BAL.",
                                                                                                      'KOR': "할당액"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_MAXALLOCATEDBALANCE'] = {'ENG': "MAX ALLC.BAL.",
                                                                                                         'KOR': "최대 할당액"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_FIRSTKLINE'] = {'ENG': "FIRST KLINE",
                                                                                                'KOR': "최초 KLINE"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_POSITIONS_ST_TRADABLE'] = {'ENG': "TRADABLE",
                                                                                              'KOR': "거래 가능"}
    #------Assets
    TEXTPACK['SIMULATIONRESULT:BLOCKTITLE_SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS'] = {'ENG': "ASSETS",
                                                                                          'KOR': "자산"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSET'] = {'ENG': "ASSET",
                                                                                     'KOR': "자산"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_INITIALWALLETBALANCE'] = {'ENG': "INITIAL WALLET BALANCE",
                                                                                                    'KOR': "최초 지갑 잔고"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ALLOCATIONRATIO'] = {'ENG': "ALLOCATION RATIO",
                                                                                               'KOR': "할당율"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ALLOCATABLEBALANCE'] = {'ENG': "ALLOCATABLE BALANCE",
                                                                                                  'KOR': "할당가능액"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_APPLY'] = {'ENG': "APPLY",
                                                                                     'KOR': "적용"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ASSUMEDRATIO'] = {'ENG': "ASSUMED RATIO",
                                                                                            'KOR': "가정율"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_WEIGHTEDASSUMEDRATIO'] = {'ENG': "ASSUMED RATIO [W]",
                                                                                                    'KOR': "가중가정율"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_ALLOCATEDBALANCE'] = {'ENG': "ALLOCATED BALANCE",
                                                                                                'KOR': "할당액"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_ASSETPOSITIONSETUP_ASSETS_MAXALLOCATEDBALANCE'] = {'ENG': "MAX ALLOCATED BALANCE",
                                                                                                   'KOR': "최대 할당액"}
    #---Configurations
    #------Currency Analysis Configurations
    TEXTPACK['SIMULATIONRESULT:BLOCKTITLE_SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONS'] = {'ENG': "CURRENCY ANALYSIS CONFIGURATIONS",
                                                                                                              'KOR': "종목분석 설정"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONCODE'] = {'ENG': "CAC CODE",
                                                                                                      'KOR': "CAC 코드"}
    TEXTPACK['SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_MAININDICATORS'] = {'ENG': "MAIN INDICATORS",
                                                                                                 'KOR': "주요지표"}
    TEXTPACK['SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_SUBINDICATORS'] = {'ENG': "SUB INDICATORS",
                                                                                                'KOR': "보조지표"}
    TEXTPACK['SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_OTHERS'] = {'ENG': "OTHERS",
                                                                                         'KOR': "기타"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_MINCOMPLETEANALYSIS'] = {'ENG': "MIN # OF COMPLETE ANALYSIS",
                                                                                        'KOR': "최소 완전분석 수"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NANALYSISDISPLAY'] = {'ENG': "# OF ANALYSIS TO DISPLAY",
                                                                                     'KOR': "디스플레이 분석 수"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'] = {'ENG': "TO CONFIGURATION MAIN",
                                                                           'KOR': "설정 메인으로"}
    TEXTPACK['SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_SMASETUP'] = {'ENG': "MAIN INDICATOR SETUP - SMA",
                                                                                           'KOR': "주요지표 설정 - SMA"}
    TEXTPACK['SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_WMASETUP'] = {'ENG': "MAIN INDICATOR SETUP - WMA",
                                                                                           'KOR': "주요지표 설정 - WMA"}
    TEXTPACK['SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_EMASETUP'] = {'ENG': "MAIN INDICATOR SETUP - EMA",
                                                                                           'KOR': "주요지표 설정 - EMA"}
    TEXTPACK['SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_PSARSETUP'] = {'ENG': "MAIN INDICATOR SETUP - PSAR",
                                                                                            'KOR': "주요지표 설정 - PSAR"}
    TEXTPACK['SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_BOLSETUP'] = {'ENG': "MAIN INDICATOR SETUP - BOL",
                                                                                           'KOR': "주요지표 설정 - BOL"}
    TEXTPACK['SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_IVPSETUP'] = {'ENG': "MAIN INDICATOR SETUP - IVP",
                                                                                           'KOR': "주요지표 설정 - IVP"}
    TEXTPACK['SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_SWINGSETUP'] = {'ENG': "MAIN INDICATOR SETUP - SWING",
                                                                                           'KOR': "주요지표 설정 - SWING"}
    TEXTPACK['SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_VOLSETUP'] = {'ENG': "SUB INDICATOR SETUP - VOL",
                                                                                           'KOR': "보조지표 설정 - VOL"}
    TEXTPACK['SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_NNASETUP'] = {'ENG': "SUB INDICATOR SETUP - NNA",
                                                                                           'KOR': "보조지표 설정 - NNA"}
    TEXTPACK['SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_MMACDSHORTSETUP'] = {'ENG': "SUB INDICATOR SETUP - MMACDSHORT",
                                                                                                  'KOR': "보조지표 설정 - MMACDSHORT"}
    TEXTPACK['SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_MMACDLONGSETUP'] = {'ENG': "SUB INDICATOR SETUP - MMACDLONG",
                                                                                                 'KOR': "보조지표 설정 - MMACDLONG"}
    TEXTPACK['SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_DMIxADXSETUP'] = {'ENG': "SUB INDICATOR SETUP - DMIxADX",
                                                                                               'KOR': "보조지표 설정 - DMIxADX"}
    TEXTPACK['SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_MFISETUP'] = {'ENG': "SUB INDICATOR SETUP - MFI",
                                                                                           'KOR': "보조지표 설정 - MFI"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'] = {'ENG': "INDEX",
                                                                          'KOR': "인덱스"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'] = {'ENG': "NUMBER OF SAMPLES",
                                                                             'KOR': "샘플 수"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_AF0'] = {'ENG': "AF0",
                                                                        'KOR': "AF0"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_AF+'] = {'ENG': "AF+",
                                                                        'KOR': "AF+"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_AFMAX'] = {'ENG': "AFMax",
                                                                          'KOR': "AFMax"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_BANDWIDTH'] = {'ENG': "BW",
                                                                              'KOR': "BW"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_BOLMATYPE'] = {'ENG': "BOL MA TYPE",
                                                                              'KOR': "BOL 이동평균 타입"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_GAMMAFACTOR'] = {'ENG': "GAMMA FACTOR",
                                                                                'KOR': "감마 인수"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_DELTAFACTOR'] = {'ENG': "DELTA FACTOR",
                                                                                'KOR': "델타 인수"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_SWINGRANGE'] = {'ENG': "SWING RANGE",
                                                                               'KOR': "스윙 범위"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_SMA'] = {'ENG': "SMA",
                                                                        'KOR': "단순이동평균"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_EMA'] = {'ENG': "EMA",
                                                                        'KOR': "지수이동평균"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_WMA'] = {'ENG': "WMA",
                                                                        'KOR': "가중이동평균"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NEURALNETWORKCODE'] = {'ENG': "NN CODE",
                                                                                      'KOR': "신경망 코드"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_ALPHA'] = {'ENG': "ALPHA",
                                                                          'KOR': "알파"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_BETA'] = {'ENG': "BETA",
                                                                         'KOR': "베타"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_VOLTYPE_BASE'] = {'ENG': "BASE",
                                                                                 'KOR': "BASE"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_VOLTYPE_QUOTE'] = {'ENG': "QUOTE",
                                                                                  'KOR': "QUOTE"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_VOLTYPE_BASETB'] = {'ENG': "BASE TAKER BUY",
                                                                                   'KOR': "BASE TAKER BUY"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_VOLTYPE_QUOTETB'] = {'ENG': "QUOTE TAKER BUY",
                                                                                    'KOR': "QUOTE TAKER BUY"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_VOLUMETYPE'] = {'ENG': "VOLUME TYPE",
                                                                               'KOR': "거래량 타입"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_VOLMATYPE'] = {'ENG': "VOL MA TYPE",
                                                                              'KOR': "거래량 이동평균 타입"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_DECISIONMAKERREGION'] = {'ENG': "DM REGION SIZE",
                                                                                        'KOR': "DM 구역 크기"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_DIRECTIVITYFLIPTHRESHOLD'] = {'ENG': "DF THRESHOLD",
                                                                                             'KOR': "DF 한계점"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_MINCLUSTERRANGERATIO'] = {'ENG': "MIN CRR",
                                                                                         'KOR': "최소 CRR"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_CONTRIBUTIONFACTORPSAR'] = {'ENG': "PSAR CF",
                                                                                           'KOR': "PSAR 기여도"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_CONTRIBUTIONFACTORIVP'] = {'ENG': "IVP CF",
                                                                                          'KOR': "IVP 기여도"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_CONTRIBUTIONFACTORMMACD'] = {'ENG': "MMACD CF",
                                                                                            'KOR': "MMACD 기여도"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_CONTRIBUTIONFACTORDMIxADX'] = {'ENG': "DMIxADX CF",
                                                                                              'KOR': "DMIxADX 기여도"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_CONTRIBUTIONFACTORMFI'] = {'ENG': "MFI CF",
                                                                                          'KOR': "MFI 기여도"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_MMACDSIGNALINTERVAL'] = {'ENG': "MMACD SIGNAL INTERVAL",
                                                                                        'KOR': "MMACD 시그널 기간"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_MULTIPLIER'] = {'ENG': "MULTIPLIER",
                                                                               'KOR': "멀티플라이어"}
    #------Trade Configurations
    TEXTPACK['SIMULATIONRESULT:BLOCKTITLE_SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIGURATIONS'] = {'ENG': "TRADE CONFIGURATIONS",
                                                                                                   'KOR': "트레이드 설정"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TRADECONFIGURATIONCODE'] = {'ENG': "TC CODE",
                                                                                           'KOR': "TC 코드"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_LEVERAGE'] = {'ENG': "LEVERAGE",
                                                                             'KOR': "레버리지"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_MARGINTYPE'] = {'ENG': "MARGIN TYPE",
                                                                               'KOR': "마진 타입"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_MARGINTYPE_CROSSED'] = {'ENG': "CROSSED",
                                                                                        'KOR': "교차"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_MARGINTYPE_ISOLATED'] = {'ENG': "ISOLATED",
                                                                                        'KOR': "격리"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_DIRECTION'] = {'ENG': "DIRECTION",
                                                                              'KOR': "방향"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_FULLSTOPLOSSIMMEDIATE'] = {'ENG': "FSL (IMMED)",
                                                                                          'KOR': "FSL (IMMED)"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_FULLSTOPLOSSIMMEDIATE'] = {'ENG': "FSL (CLOSE)",
                                                                                          'KOR': "FSL (CLOSE)"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_POSTSTOPLOSSREENTRY'] = {'ENG': "POST-STOPLOSS REENTRY",
                                                                                        'KOR': "STOPLOSS 이후 재진입"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_RQPM_FUNCTIONTYPE'] = {'ENG': "FUNCTION TYPE",
                                                                                      'KOR': "함수 타입"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_RQPM_PARAMETER_INDEX'] = {'ENG': "INDEX",
                                                                                         'KOR': "인덱스"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_RQPM_PARAMETER_NAME'] = {'ENG': "NAME",
                                                                                        'KOR': "변수명"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_RQPM_PARAMETER_VALUE'] = {'ENG': "VALUE",
                                                                                         'KOR': "변수값"}

    #---Trade Logs
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_NETPROFIT'] = {'ENG': "NET PROFIT",
                                                                         'KOR': "순이익"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_GAIN'] = {'ENG': "GAIN",
                                                                    'KOR': "수익"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_LOSS'] = {'ENG': "LOSS",
                                                                    'KOR': "손실"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_TRADINGFEE'] = {'ENG': "TRADING FEE",
                                                                          'KOR': "수수료"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_TOTAL'] = {'ENG': "TOTAL",
                                                                     'KOR': "전체"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ASSET'] = {'ENG': "ASSET",
                                                                     'KOR': "자산"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_POSITION'] = {'ENG': "POSITION",
                                                                        'KOR': "포지션"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_TIMEUTC'] = {'ENG': "TIME (UTC)",
                                                                       'KOR': "시간 (UTC)"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_SEARCH'] = {'ENG': "SEARCH",
                                                                      'KOR': "검색"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_BUY'] = {'ENG': "BUY",
                                                                   'KOR': "매수"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_SELL'] = {'ENG': "SELL",
                                                                    'KOR': "매도"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_LIQUIDATION'] = {'ENG': "LIQUIDATION",
                                                                           'KOR': "강제 청산"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_FSLIMMED'] = {'ENG': "FSLIMMED",
                                                                        'KOR': "FSLIMMED"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_FSLCLOSE'] = {'ENG': "FSLCLOSE",
                                                                        'KOR': "FSLCLOSE"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ENTRY'] = {'ENG': "ENTRY",
                                                                     'KOR': "진입"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_CLEAR'] = {'ENG': "CLEAR",
                                                                     'KOR': "종료"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_EXIT'] = {'ENG': "EXIT",
                                                                    'KOR': "회수"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_INDEX'] = {'ENG': "INDEX",
                                                                        'KOR': "인덱스"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_TIME'] = {'ENG': "TIME (UTC)",
                                                                       'KOR': "시간 (UTC)"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_SYMBOL'] = {'ENG': "SYMBOL",
                                                                         'KOR': "심볼"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_LOGICSOURCE'] = {'ENG': "LOGIC SOURCE",
                                                                              'KOR': "로직 소스"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_SIDE'] = {'ENG': "SIDE",
                                                                       'KOR': "방향"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_QUANTITY'] = {'ENG': "QUANTITY",
                                                                           'KOR': "거래수"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_PRICE'] = {'ENG': "PRICE",
                                                                        'KOR': "거래가"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_PROFIT'] = {'ENG': "PROFIT",
                                                                         'KOR': "이익"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_TRADINGFEE'] = {'ENG': "TRADING FEE",
                                                                             'KOR': "수수료"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_TOTALQUANTITY'] = {'ENG': "QUANTITY [T]",
                                                                                'KOR': "총 보유수"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_ENTRYPRICE'] = {'ENG': "ENTRY PRICE",
                                                                             'KOR': "진입가"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_ST_WALLETBALANCE'] = {'ENG': "WALLET BALANCE",
                                                                                'KOR': "지갑 잔고"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_TRADELOG_SIDE_BUY'] = {'ENG': "BUY",
                                                                                 'KOR': "매수"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_TRADELOG_SIDE_SELL'] = {'ENG': "SELL",
                                                                                  'KOR': "매도"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_TRADELOG_SIDE_LIQUIDATION'] = {'ENG': "LIQUIDATION",
                                                                                         'KOR': "청산"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_NTRADELOGSTOTAL'] = {'ENG': "TOTAL LOGS",
                                                                               'KOR': "전체 로그"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_NTRADELOGSASSET'] = {'ENG': "ASSET LOGS",
                                                                               'KOR': "자산 로그"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_NTRADELOGSPOSITION'] = {'ENG': "POSITION LOGS",
                                                                                  'KOR': "포지션 로그"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_NBUYS'] = {'ENG': "BUY",
                                                                     'KOR': "매매"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_NSELLS'] = {'ENG': "SELL",
                                                                      'KOR': "매도"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_NPSLS'] = {'ENG': "PSL",
                                                                     'KOR': "PSL"}
    TEXTPACK['SIMULATIONRESULT:SIMULATIONDETAIL_TRADELOGS_NLIQUIDATIONS'] = {'ENG': "LIQUIDATION",
                                                                             'KOR': "청산"}
    #---Daily Report

    #---Position Chart

    #---Detailed Evaluation
#PAGE 'SIMULATIONRESULT' END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#PAGE 'NEURALNETWORK' ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
if (True):
    TEXTPACK['NEURALNETWORK:TITLE'] = {'ENG': "NEURAL NETWORK",
                                       'KOR': "뉴럴 네트워크"}
    #<Neural Network Manager>
    TEXTPACK['NEURALNETWORK:BLOCKTITLE_NEURALNETWORKMANAGER'] = {'ENG': "NEURAL NETWORK MANAGER",
                                                                 'KOR': "뉴럴 네트워크 매니저"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS'] = {'ENG': "NEURAL NETWORKS",
                                                                     'KOR': "뉴럴 네트워크"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES'] = {'ENG': "PROCESSES",
                                                                'KOR': "프로세스"}
    #---Neural Networks
    TEXTPACK['NEURALNETWORK:BLOCKSUBTITLE_NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKS'] = {'ENG': "NEURAL NETWORKS",
                                                                                                  'KOR': "뉴럴 네트워크"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_ST_INDEX'] = {'ENG': "INDEX",
                                                                              'KOR': "인덱스"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_ST_NETWORKCODE'] = {'ENG': "NETWORK CODE",
                                                                                    'KOR': "네트워크 코드"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_ST_STATUS'] = {'ENG': "STATUS",
                                                                               'KOR': "상태"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAME'] = {'ENG': "NETWORK CODE",
                                                                                       'KOR': "네트워크 코드"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPE'] = {'ENG': "NETWORK TYPE",
                                                                                       'KOR': "네트워크 타입"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEY'] = {'ENG': "CONTROL KEY",
                                                                                'KOR': "관리 키"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_HOLDCONTROLKEY'] = {'ENG': "HOLD CK",
                                                                                    'KOR': "임시저장"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATIONTIME'] = {'ENG': "GENERATION TIME",
                                                                                    'KOR': "생성 시간"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS'] = {'ENG': "STATUS",
                                                                            'KOR': "상태"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_STANDBY'] = {'ENG': "STANDBY",
                                                                                    'KOR': "대기중"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_QUEUED'] = {'ENG': "QUEUED",
                                                                                   'KOR': "대기열"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_TRAINING'] = {'ENG': "TRAINING",
                                                                                     'KOR': "학습중"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_TESTING'] = {'ENG': "TESTING",
                                                                                    'KOR': "테스트중"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_TESTINGPERFORMANCE'] = {'ENG': "TESTING PERFORMANCE",
                                                                                               'KOR': "성능 테스트중"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONSETUP'] = {'ENG': "INIT. PARAMS",
                                                                                         'KOR': "초기화 변수"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZE'] = {'ENG': "INITIALIZE",
                                                                                'KOR': "초기화"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATE'] = {'ENG': "GENERATE",
                                                                              'KOR': "생성"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_REMOVE'] = {'ENG': "REMOVE",
                                                                            'KOR': "삭제"}
    #---Processes
    TEXTPACK['NEURALNETWORK:BLOCKSUBTITLE_NEURALNETWORKMANAGER_PROCESSES_PROCESSES'] = {'ENG': "PROCESSES",
                                                                                        'KOR': "프로세스"}

    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_INDEX'] = {'ENG': "INDEX",
                                                                              'KOR': "인덱스"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_NETWORKCODE'] = {'ENG': "NETWORK CODE",
                                                                               'KOR': "네트워크 코드"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_TYPE'] = {'ENG': "TYPE",
                                                                        'KOR': "타입"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_STATUS'] = {'ENG': "STATUS",
                                                                          'KOR': "상태"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_COMPLETION'] = {'ENG': "COMPLETION",
                                                                              'KOR': "진행률"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_ETC'] = {'ENG': "ETC",
                                                                       'KOR': "ETC"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_TARGET'] = {'ENG': "TARGET",
                                                                          'KOR': "타겟"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_TARGETRANGE'] = {'ENG': "TARGET RANGE",
                                                                               'KOR': "타겟 범위"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_NEPOCHS'] = {'ENG': "EPOCHS",
                                                                           'KOR': "EPOCH"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_BATCHSIZE'] = {'ENG': "BATCH",
                                                                             'KOR': "BATCH"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_LEARNINGRATE'] = {'ENG': "LR",
                                                                                'KOR': "LR"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_SWINGRANGE'] = {'ENG': "SR",
                                                                              'KOR': "SR"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS'] = {'ENG': "STATUS",
                                                                       'KOR': "상태"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_QUEUED'] = {'ENG': "QUEUED",
                                                                              'KOR': "대기중"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_PREPARING'] = {'ENG': "PREPARING",
                                                                                 'KOR': "준비중"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_PREPROCESSING'] = {'ENG': "PREPROCESSING",
                                                                                     'KOR': "전처리중"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_PROCESSING'] = {'ENG': "PROCESSING",
                                                                                  'KOR': "처리중"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_TYPE_TRAINING'] = {'ENG': "TRAINING",
                                                                              'KOR': "학습"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_TYPE_PERFORMANCETEST'] = {'ENG': "TESTING",
                                                                                     'KOR': "테스트"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_CONTROLKEY'] = {'ENG': "CONTROL KEY",
                                                                           'KOR': "관리 키"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_HOLDCONTROLKEY'] = {'ENG': "HOLD CK",
                                                                               'KOR': "임시저장"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_REMOVE'] = {'ENG': "REMOVE",
                                                                       'KOR': "삭제"}
    #<Neural Network Detail>
    TEXTPACK['NEURALNETWORK:BLOCKTITLE_NEURALNETWORKCONTROL&DETAIL'] = {'ENG': "NEURAL NETWORK CONTROL & DETAIL",
                                                                        'KOR': "뉴럴 네트워크 관리 & 상세정보"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE'] = {'ENG': "NETWORK STRUCTURE",
                                                                              'KOR': "네트워크 구조"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP'] = {'ENG': "TRAINING & PERFORMANCE",
                                                                 'KOR': "학습 & 성능"}
    #---Network Structure
    TEXTPACK['NEURALNETWORK:BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_STRUCTUREPARAMETERS'] = {'ENG': "STRUCTURE PARAMETERS",
                                                                                                                'KOR': "구조 변수"}
    TEXTPACK['NEURALNETWORK:BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_STRUCTUREDETAIL'] = {'ENG': "STRUCTURE DETAIL",
                                                                                                            'KOR': "상세 구조"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINES'] = {'ENG': "N KLINES",
                                                                                      'KOR': "KLINE 수"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYER'] = {'ENG': "OUTPUT LAYER",
                                                                                          'KOR': "출력층"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERS'] = {'ENG': "HIDDEN LAYERS",
                                                                                           'KOR': "은닉층"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_ANALYSISREF'] = {'ENG': "ANALYSIS REF",
                                                                                          'KOR': "분석 참조"}
    #---TAP
    TEXTPACK['NEURALNETWORK:BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCIES'] = {'ENG': "CURRENCIES",
                                                                                          'KOR': "종목"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_SEARCH'] = {'ENG': "SEARCH",
                                                                        'KOR': "검색"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_SORTBY'] = {'ENG': "SORT BY",
                                                                        'KOR': "정렬"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_SORTBY_INDEX'] = {'ENG': "INDEX",
                                                                              'KOR': "인덱스"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_SORTBY_SYMBOL'] = {'ENG': "SYMBOL",
                                                                               'KOR': "심볼"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_SORTBY_STATUS'] = {'ENG': "STATUS",
                                                                               'KOR': "상태"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_SORTBY_FIRSTKLINE'] = {'ENG': "FIRST KLINE",
                                                                                   'KOR': "최초 KLINE"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_INDEX'] = {'ENG': "INDEX",
                                                                          'KOR': "인덱스"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_SYMBOL'] = {'ENG': "SYMBOL",
                                                                           'KOR': "심볼"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_STATUS'] = {'ENG': "STATUS",
                                                                           'KOR': "상태"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_FIRSTKLINE'] = {'ENG': "FIRST KLINE",
                                                                               'KOR': "최초 KLINE"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_STATUS_TRADING'] = {'ENG': "TRADING",
                                                                                'KOR': "거래중"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_STATUS_SETTLING'] = {'ENG': "SETTLIN",
                                                                                 'KOR': "정산중"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_STATUS_REMOVED'] = {'ENG': "REMOVED",
                                                                                'KOR': "폐지"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_SYMBOL'] = {'ENG': "SYMBOL",
                                                                        'KOR': "심볼"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_DATARANGES'] = {'ENG': "DATA RANGES",
                                                                            'KOR': "데이터 범위"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_TARGETDATARANGE'] = {'ENG': "TARGET D.R.",
                                                                                 'KOR': "타겟 데이터 범위"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_OPTIMIZER'] = {'ENG': "OPTIMIZER",
                                                                           'KOR': "옵티마이저"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTION'] = {'ENG': "LOSS FN",
                                                                              'KOR': "손실 함수"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_CACCODE'] = {'ENG': "CAC CODE",
                                                                         'KOR': "CAC 코드"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_NEPOCHS'] = {'ENG': "EPOCH",
                                                                         'KOR': "EPOCH"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_BATCHSIZE'] = {'ENG': "BATCH",
                                                                           'KOR': "BATCH"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_LEARNINGRATE'] = {'ENG': "LR",
                                                                              'KOR': "학습율"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_SWINGRANGE'] = {'ENG': "SWING RANGE",
                                                                            'KOR': "SWING 범위"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_RUNTRAINING'] = {'ENG': "RUN TRAINING",
                                                                             'KOR': "학습 시작"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_RUNPERFORMANCETEST'] = {'ENG': "RUN PERFORMANCE TEST",
                                                                                    'KOR': "성능 테스트 시작"}
    TEXTPACK['NEURALNETWORK:BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_TAP_TRAININGLOG'] = {'ENG': "TRAINING LOG",
                                                                                           'KOR': "학습 로그"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_TIME'] = {'ENG': "TIME",
                                                                         'KOR': "시간"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_TARGET'] = {'ENG': "TARGET",
                                                                           'KOR': "타겟"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_TARGETRANGE'] = {'ENG': "TARGET RANGE",
                                                                                'KOR': "타겟 범위"}
    TEXTPACK['NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_LOSSVALUE'] = {'ENG': "LOSS VALUE",
                                                                              'KOR': "로스 값"}
    TEXTPACK['NEURALNETWORK:BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_TAP_PERFORMANCETESTLOG'] = {'ENG': "PERFORMANCE TEST LOG",
                                                                                                  'KOR': "성능 테스트 로그"}
#PAGE 'NEURALNETWORK' END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#PAGE 'SETTINGS' ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
if (True):
    TEXTPACK['SETTINGS:TITLE'] = {'ENG': "SETTINGS",
                                  'KOR': "설정"}
    TEXTPACK['SETTINGS:AUDIOWRAPPERTITLE'] = {'ENG': "AUDIO",
                                              'KOR': "오디오"}
    TEXTPACK['SETTINGS:PLAYSOUND'] = {'ENG': "PLAY SOUND",
                                      'KOR': "소리 재생"}
    TEXTPACK['SETTINGS:MAINVOLUME'] = {'ENG': "MAIN VOLUME",
                                       'KOR': "메인 볼륨"}
    TEXTPACK['SETTINGS:GRAPHICSWRAPPERTITLE'] = {'ENG': "GRAPHICS",
                                                 'KOR': "그래픽"}
    TEXTPACK['SETTINGS:FULLSCREEN'] = {'ENG': "FULLSCREEN",
                                       'KOR': "전체화면"}
    TEXTPACK['SETTINGS:GUITHEME'] = {'ENG': "GUI THEME",
                                     'KOR': "GUI 테마"}
    TEXTPACK['SETTINGS:LIGHTMODE'] = {'ENG': "LIGHT MODE",
                                      'KOR': "라이트 모드"}
    TEXTPACK['SETTINGS:DARKMODE'] = {'ENG': "DARK MODE",
                                     'KOR': "다크 모드"}
    TEXTPACK['SETTINGS:LANGUAGE'] = {'ENG': "LANGUAGE",
                                     'KOR': "언어"}
    TEXTPACK['SETTINGS:KOR'] = {'ENG': "KOREAN",
                                'KOR': "한국어"}
    TEXTPACK['SETTINGS:ENG'] = {'ENG': "ENGLISH",
                                'KOR': "영어"}
    TEXTPACK['SETTINGS:SYSTEM_PRINTUPDATE'] = {'ENG': "PRINT UPDATE",
                                               'KOR': "업데이트 출력"}
    TEXTPACK['SETTINGS:SYSTEM_PRINTWARNING'] = {'ENG': "PRINT WARNING",
                                                'KOR': "경고 출력"}
    TEXTPACK['SETTINGS:SYSTEM_PRINTERROR'] = {'ENG': "PRINT ERROR",
                                              'KOR': "에러 출력"}
    TEXTPACK['SETTINGS:SYSTEM_BINANCEAPI_WRAPPERTITLE'] = {'ENG': "SYSTEM - BINANCE API",
                                                           'KOR': "시스템 - 바이낸스 API"}
    TEXTPACK['SETTINGS:SYSTEM_BINANCEAPI_RATELIMITIPSHARINGNUMBER'] = {'ENG': "RATE LIMIT IP SHARING NUMBER",
                                                                       'KOR': "RATE LIMIT IP 공유 수"}
    TEXTPACK['SETTINGS:SYSTEM_DATAMANAGER_WRAPPERTITLE'] = {'ENG': "SYSTEM - DATA MANAGER",
                                                            'KOR': "시스템 - 데이터 매니저"}
    TEXTPACK['SETTINGS:SYSTEM_TRADEMANAGER_WRAPPERTITLE'] = {'ENG': "SYSTEM - TRADE MANAGER",
                                                             'KOR': "시스템 - 트레이드 매니저"}
    TEXTPACK['SETTINGS:CONFIGURATIONANDMESSAGEWRAPPERTITLE'] = {'ENG': "CONFIGURATION & MESSAGE",
                                                                'KOR': "설정 & 메세지"}
    TEXTPACK['SETTINGS:SAVECHANGES'] = {'ENG': "SAVE CHANGES",
                                        'KOR': "변경사항 저장"}
#PAGE 'SETTINGS' END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO 'CHARTDRAWER' ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
if (True):
    TEXTPACK['GUIO_CHARTDRAWER:WAITINGFIRSTSTREAM'] = {'ENG': "Waiting First Streamed Kline...",
                                                       'KOR': "최초 KLINE 스트림 대기중..."}
    TEXTPACK['GUIO_CHARTDRAWER:WAITINGDATAAVAILABLE'] = {'ENG': "Waiting Data Available...",
                                                         'KOR': "데이터 수집 대기중..."}
    TEXTPACK['GUIO_CHARTDRAWER:WAITINGANALYZERALLOCATION'] = {'ENG': "Waiting Analyzer Allocation...",
                                                              'KOR': "분석기 할당 대기중..."}
    TEXTPACK['GUIO_CHARTDRAWER:REQUESTINGCADATASUBSCRIPTIONREGISTRATION'] = {'ENG': "REQUESTING CURRENCY ANALYSIS DATA SUBSCRIPTION REGISTRATION...",
                                                                             'KOR': "종목 분석 데이터 구독 등록 요청중..."}
    TEXTPACK['GUIO_CHARTDRAWER:NOTARGETDATARANGEINTERSECTION'] = {'ENG': "NO TARGET DATA RANGE INTERSECTION",
                                                                  'KOR': "타켓 데이터 범위 교차 없음"}
    TEXTPACK['GUIO_CHARTDRAWER:FETCHINGTRADELOGDATA'] = {'ENG': "FETCHING TRADE LOG DATA",
                                                         'KOR': "트레이드 기록을 불러오는중"}
    TEXTPACK['GUIO_CHARTDRAWER:TRADELOGDATAFETCHFAILED'] = {'ENG': "TRADE LOG DATA FETCH FAILED",
                                                            'KOR': "트레이드 기록 불러오기 실패"}
    TEXTPACK['GUIO_CHARTDRAWER:LOADINGNEURALNETWORKCONNECTIONSDATA'] = {'ENG': "LOADING NEURAL NETWORK CONNECTIONS DATA",
                                                                        'KOR': "뉴럴 네트워크 연결 데이터 요청중"}
    TEXTPACK['GUIO_CHARTDRAWER:NEURALNETWORKCONNECTIONSDATAREQUESTFAILED'] = {'ENG': "NEURAL NETWORK CONNECTIONS DATA REQUEST FAILED",
                                                                              'KOR': "뉴럴 네트워크 연결 데이터 요청 실패"}
    TEXTPACK['GUIO_CHARTDRAWER:LOADINGKLINES'] = {'ENG': "Loading Klines...",
                                                  'KOR': "데이터를 불러오는중..."}
    TEXTPACK['GUIO_CHARTDRAWER:REGENERATINGANALYSISDATA'] = {'ENG': "REGENERATING ANALYSIS DATA",
                                                             'KOR': "분석 데이터 재생성중"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_CHARTSETTINGS'] = {'ENG': "CHART SETTINGS",
                                                        'KOR': "차트 설정"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_MAININDICATORS'] = {'ENG': "MAIN INDICATORS",
                                                         'KOR': "주요지표"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_SUBINDICATORS'] = {'ENG': "SUB INDICATORS",
                                                        'KOR': "보조지표"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_SUBINDICATORDISPLAY'] = {'ENG': "SUB INDICATORS DISPLAY",
                                                              'KOR': "보조지표 디스플레이"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_ANALYZER'] = {'ENG': "ANALYZER",
                                                   'KOR': "분석기"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_TRADELOG'] = {'ENG': "TRADE LOG",
                                                   'KOR': "트레이드 로그"}
    TEXTPACK['GUIO_CHARTDRAWER:DISPLAYTRADELOG'] = {'ENG': "DISPLAY TRADE LOG",
                                                    'KOR': "트레이드 로그 표시"}
    TEXTPACK['GUIO_CHARTDRAWER:TRADELOG_BUY'] = {'ENG': "BUY LOG",
                                                 'KOR': "매수 기록"}
    TEXTPACK['GUIO_CHARTDRAWER:TRADELOG_SELL'] = {'ENG': "SELL LOG",
                                                  'KOR': "매도 기록"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_BIDSANDASKS'] = {'ENG': "BIDS AND ASKS",
                                                      'KOR': "호가"}
    TEXTPACK['GUIO_CHARTDRAWER:DISPLAYBIDSANDASKS'] = {'ENG': "DISPLAY BIDS AND ASKS",
                                                       'KOR': "호가 표시"}
    TEXTPACK['GUIO_CHARTDRAWER:BIDSANDASKS_BIDS'] = {'ENG': "BIDS",
                                                     'KOR': "매수 호가"}
    TEXTPACK['GUIO_CHARTDRAWER:BIDSANDASKS_ASKS'] = {'ENG': "ASKS",
                                                     'KOR': "매도 호가"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_AUX'] = {'ENG': "AUXILLARIES",
                                              'KOR': "기타"}
    TEXTPACK['GUIO_CHARTDRAWER:INDICATOR0'] = {'ENG': "INDICATOR 0",
                                               'KOR': "지표 0"}
    TEXTPACK['GUIO_CHARTDRAWER:INDICATOR1'] = {'ENG': "INDICATOR 1",
                                               'KOR': "지표 1"}
    TEXTPACK['GUIO_CHARTDRAWER:INDICATOR2'] = {'ENG': "INDICATOR 2",
                                               'KOR': "지표 2"}
    TEXTPACK['GUIO_CHARTDRAWER:INDICATOR3'] = {'ENG': "INDICATOR 3",
                                               'KOR': "지표 3"}
    TEXTPACK['GUIO_CHARTDRAWER:INDICATOR4'] = {'ENG': "INDICATOR 4",
                                               'KOR': "지표 4"}
    TEXTPACK['GUIO_CHARTDRAWER:INDICATOR5'] = {'ENG': "INDICATOR 5",
                                               'KOR': "지표 5"}
    TEXTPACK['GUIO_CHARTDRAWER:INDICATOR6'] = {'ENG': "INDICATOR 6",
                                               'KOR': "지표 6"}
    TEXTPACK['GUIO_CHARTDRAWER:INDICATOR7'] = {'ENG': "INDICATOR 7",
                                               'KOR': "지표 7"}
    TEXTPACK['GUIO_CHARTDRAWER:INDICATOR8'] = {'ENG': "INDICATOR 8",
                                               'KOR': "지표 8"}
    TEXTPACK['GUIO_CHARTDRAWER:INDICATOR9'] = {'ENG': "INDICATOR 9",
                                               'KOR': "지표 9"}
    TEXTPACK['GUIO_CHARTDRAWER:ANALYSISRANGEBEG'] = {'ENG': "ANALYSIS RANGE BEGIN (UTC)",
                                                     'KOR': "분석 범위 시작 (UTC)"}
    TEXTPACK['GUIO_CHARTDRAWER:ANALYSISRANGEEND'] = {'ENG': "ANALYSIS RANGE END (UTC)",
                                                     'KOR': "분석 범위 끝 (UTC)"}
    TEXTPACK['GUIO_CHARTDRAWER:STARTANALYSIS'] = {'ENG': "START ANALYSIS",
                                                  'KOR': "분석 시작"}
    TEXTPACK['GUIO_CHARTDRAWER:KLINECOLORTYPE'] = {'ENG': "KLINE COLOR TYPE",
                                                   'KOR': "KLINE 색상 타입"}
    TEXTPACK['GUIO_CHARTDRAWER:TIMEZONE'] = {'ENG': "TIMEZONE",
                                             'KOR': "시간대"}
    TEXTPACK['GUIO_CHARTDRAWER:SAVECONFIG'] = {'ENG': "SAVE CONFIGURATION",
                                               'KOR': "설정 저장"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_MI_SMA'] = {'ENG': "MAIN INDICATOR SETUP - SMA",
                                                 'KOR': "주요지표 설정 - SMA"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_MI_WMA'] = {'ENG': "MAIN INDICATOR SETUP - WMA",
                                                 'KOR': "주요지표 설정 - WMA"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_MI_EMA'] = {'ENG': "MAIN INDICATOR SETUP - EMA",
                                                 'KOR': "주요지표 설정 - EMA"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_MI_BOL'] = {'ENG': "MAIN INDICATOR SETUP - BOL",
                                                 'KOR': "주요지표 설정 - BOL"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_MI_PSAR'] = {'ENG': "MAIN INDICATOR SETUP - PSAR",
                                                  'KOR': "주요지표 설정 - PSAR"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_MI_IVP'] = {'ENG': "MAIN INDICATOR SETUP - IVP",
                                                 'KOR': "주요지표 설정 - IVP"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_MI_SWING'] = {'ENG': "MAIN INDICATOR SETUP - SWING",
                                                   'KOR': "주요지표 설정 - SWING"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_SI_VOL'] = {'ENG': "SUB INDICATOR SETUP - VOL",
                                                 'KOR': "보조지표 설정 - VOL"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_SI_NNA'] = {'ENG': "SUB INDICATOR SETUP - NNA",
                                                 'KOR': "보조지표 설정 - NNA"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_SI_MMACDSHORT'] = {'ENG': "SUB INDICATOR SETUP - MMACDSHORT",
                                                        'KOR': "보조지표 설정 - MMACDSHORT"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_SI_MMACDLONG'] = {'ENG': "SUB INDICATOR SETUP - MMACDLONG",
                                                       'KOR': "보조지표 설정 - MMACDLONG"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_SI_DMIxADX'] = {'ENG': "SUB INDICATOR SETUP - DMIxADX",
                                                     'KOR': "보조지표 설정 - DMIxADX"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_SI_MFI'] = {'ENG': "SUB INDICATOR SETUP - MFI",
                                                 'KOR': "보조지표 설정 - MFI"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_SI_WOI'] = {'ENG': "SUB INDICATOR SETUP - WOI",
                                                 'KOR': "보조지표 설정 - WOI"}
    TEXTPACK['GUIO_CHARTDRAWER:TITLE_SI_NES'] = {'ENG': "SUB INDICATOR SETUP - NES",
                                                 'KOR': "보조지표 설정 - NES"}
    TEXTPACK['GUIO_CHARTDRAWER:LINECOLOR'] = {'ENG': "LINE COLOR",
                                              'KOR': "지표 색상"}
    TEXTPACK['GUIO_CHARTDRAWER:LINETARGET'] = {'ENG': "TARGET",
                                               'KOR': "대상"}
    TEXTPACK['GUIO_CHARTDRAWER:APPLYCOLOR'] = {'ENG': "APPLY",
                                               'KOR': "적용"}
    TEXTPACK['GUIO_CHARTDRAWER:INDEX'] = {'ENG': "INDEX",
                                          'KOR': "인덱스"}
    TEXTPACK['GUIO_CHARTDRAWER:INTERVAL'] = {'ENG': "INTERVAL",
                                             'KOR': "기간"}
    TEXTPACK['GUIO_CHARTDRAWER:INTERVALSHORT'] = {'ENG': "INT.",
                                                  'KOR': "기간"}
    TEXTPACK['GUIO_CHARTDRAWER:BANDWIDTH'] = {'ENG': "B.W.",
                                              'KOR': "대역폭"}
    TEXTPACK['GUIO_CHARTDRAWER:MATYPE'] = {'ENG': "MOVING AVERAGE TYPE",
                                           'KOR': "이동평균 타입"}
    TEXTPACK['GUIO_CHARTDRAWER:MATYPE_SMA'] = {'ENG': "SIMPLE",
                                               'KOR': "단순이동평균"}
    TEXTPACK['GUIO_CHARTDRAWER:MATYPE_WMA'] = {'ENG': "WEIGHTED",
                                               'KOR': "가중이동평균"}
    TEXTPACK['GUIO_CHARTDRAWER:MATYPE_EMA'] = {'ENG': "EXPONENTIAL",
                                               'KOR': "지수이동평균"}
    TEXTPACK['GUIO_CHARTDRAWER:MATYPE_SMA_ABBR'] = {'ENG': "SMA",
                                                    'KOR': "SMA"}
    TEXTPACK['GUIO_CHARTDRAWER:MATYPE_WMA_ABBR'] = {'ENG': "WMA",
                                                    'KOR': "WMA"}
    TEXTPACK['GUIO_CHARTDRAWER:MATYPE_EMA_ABBR'] = {'ENG': "EMA",
                                                    'KOR': "EMA"}
    TEXTPACK['GUIO_CHARTDRAWER:PSARSTART'] = {'ENG': "AF0",
                                              'KOR': "AF0"}
    TEXTPACK['GUIO_CHARTDRAWER:PSARACCELERATION'] = {'ENG': "AF+",
                                                     'KOR': "AF+"}
    TEXTPACK['GUIO_CHARTDRAWER:PSARMAXIMUM'] = {'ENG': "AFmax",
                                                'KOR': "AFmax"}
    TEXTPACK['GUIO_CHARTDRAWER:SIZE'] = {'ENG': "SIZE",
                                         'KOR': "크기"}
    TEXTPACK['GUIO_CHARTDRAWER:WIDTH'] = {'ENG': "WIDTH",
                                          'KOR': "두께"}
    TEXTPACK['GUIO_CHARTDRAWER:COLOR'] = {'ENG': "COLOR",
                                          'KOR': "색상"}
    TEXTPACK['GUIO_CHARTDRAWER:DISPLAY'] = {'ENG': "DISPLAY",
                                            'KOR': "표시"}
    TEXTPACK['GUIO_CHARTDRAWER:DISPLAYCONTENTS'] = {'ENG': "DISPLAY CONTENTS",
                                                    'KOR': "표시 내용"}
    TEXTPACK['GUIO_CHARTDRAWER:DISPLAYBOLCENTER'] = {'ENG': "DISPLAY BOLLINGER CENTER",
                                                     'KOR': "볼린저 중앙값 표시"}
    TEXTPACK['GUIO_CHARTDRAWER:DISPLAYBOLBAND'] = {'ENG': "DISPLAY BOLLINGER BAND",
                                                   'KOR': "볼린저 밴드 표시"}
    TEXTPACK['GUIO_CHARTDRAWER:APPLYSETTINGS'] = {'ENG': "APPLY SETTINGS",
                                                  'KOR': "설정 적용"}
    TEXTPACK['GUIO_CHARTDRAWER:IVPDISPLAY'] = {'ENG': "IVP DISPLAY",
                                               'KOR': "IVP 디스플레이"}
    TEXTPACK['GUIO_CHARTDRAWER:VPLP'] = {'ENG': "VPLP",
                                         'KOR': "VPLP"}
    TEXTPACK['GUIO_CHARTDRAWER:VPLPB'] = {'ENG': "VPLPB",
                                          'KOR': "VPLPB"}
    TEXTPACK['GUIO_CHARTDRAWER:VPLPDISPLAY'] = {'ENG': "VPLP DISPLAY",
                                                'KOR': "VPLP 표시"}
    TEXTPACK['GUIO_CHARTDRAWER:DISPLAYWIDTH'] = {'ENG': "DISPLAY WIDTH",
                                                 'KOR': "디스플레이 길이"}
    TEXTPACK['GUIO_CHARTDRAWER:VPLPBDISPLAY'] = {'ENG': "VPLPB DISPLAY",
                                                 'KOR': "VPLPB 표시"}
    TEXTPACK['GUIO_CHARTDRAWER:DISPLAYREGION'] = {'ENG': "DISPLAY REGION",
                                                  'KOR': "표시 영역"}
    TEXTPACK['GUIO_CHARTDRAWER:IVPPARAMS'] = {'ENG': "IVP PARAMETERS",
                                              'KOR': "IVP 변수"}
    TEXTPACK['GUIO_CHARTDRAWER:IVPGAMMAFACTOR'] = {'ENG': "GAMMA FACTOR",
                                                   'KOR': "감마 인수"}
    TEXTPACK['GUIO_CHARTDRAWER:IVPDELTAFACTOR'] = {'ENG': "DELTA FACTOR",
                                                   'KOR': "델타 인수"}
    TEXTPACK['GUIO_CHARTDRAWER:SWINGRANGE'] = {'ENG': "SWING RANGE",
                                               'KOR': "스윙 범위"}
    TEXTPACK['GUIO_CHARTDRAWER:VOLSETTINGS'] = {'ENG': "VOLUME SETTINGS",
                                                'KOR': "거래량 설정"}
    TEXTPACK['GUIO_CHARTDRAWER:VOLTYPE'] = {'ENG': "VOLUME TYPE",
                                            'KOR': "거래량 타입"}
    TEXTPACK['GUIO_CHARTDRAWER:VOLTYPE_BASE'] = {'ENG': "BASE",
                                                 'KOR': "BASE"}
    TEXTPACK['GUIO_CHARTDRAWER:VOLTYPE_QUOTE'] = {'ENG': "QUOTE",
                                                  'KOR': "QUOTE"}
    TEXTPACK['GUIO_CHARTDRAWER:VOLTYPE_BASETB'] = {'ENG': "BASE TAKER BUY",
                                                   'KOR': "BASE TAKER BUY"}
    TEXTPACK['GUIO_CHARTDRAWER:VOLTYPE_QUOTETB'] = {'ENG': "QUOTE TAKER BUY",
                                                    'KOR': "QUOTE TAKER BUY"}
    TEXTPACK['GUIO_CHARTDRAWER:MATYPE'] = {'ENG': "MA TYPE",
                                           'KOR': "이동평균 타입"}
    TEXTPACK['GUIO_CHARTDRAWER:MATYPE_SMA'] = {'ENG': "SIMPLE",
                                               'KOR': "단순형"}
    TEXTPACK['GUIO_CHARTDRAWER:MATYPE_WMA'] = {'ENG': "WEIGHTED",
                                               'KOR': "가중형"}
    TEXTPACK['GUIO_CHARTDRAWER:MATYPE_EMA'] = {'ENG': "EXPONENTIAL",
                                               'KOR': "지수형"}
    TEXTPACK['GUIO_CHARTDRAWER:NEURALNETWORKCODE'] = {'ENG': "NN CODE",
                                                      'KOR': "신경망 코드"}
    TEXTPACK['GUIO_CHARTDRAWER:ALPHA'] = {'ENG': "ALPHA",
                                          'KOR': "알파"}
    TEXTPACK['GUIO_CHARTDRAWER:BETA'] = {'ENG': "BETA",
                                         'KOR': "베타"}
    TEXTPACK['GUIO_CHARTDRAWER:MMACDMMACD'] = {'ENG': "MMACD",
                                               'KOR': "MMACD"}
    TEXTPACK['GUIO_CHARTDRAWER:MMACDSIGNAL'] = {'ENG': "SIGNAL",
                                                'KOR': "시그널"}
    TEXTPACK['GUIO_CHARTDRAWER:MMACDHISTOGRAM+'] = {'ENG': "HISTOGRAM+",
                                                    'KOR': "히스토그램+"}
    TEXTPACK['GUIO_CHARTDRAWER:MMACDHISTOGRAM-'] = {'ENG': "HISTOGRAM-",
                                                    'KOR': "히스토그램-"}
    TEXTPACK['GUIO_CHARTDRAWER:MMACDDISPLAY'] = {'ENG': "MMACD DISPLAY",
                                                 'KOR': "MMACD 디스플레이"}
    TEXTPACK['GUIO_CHARTDRAWER:MMACDMMACDDISPLAY'] = {'ENG': "DISPLAY MMACD",
                                                      'KOR': "MMACD 표시"}
    TEXTPACK['GUIO_CHARTDRAWER:MMACDSIGNALDISPLAY'] = {'ENG': "DISPLAY SIGNAL",
                                                       'KOR': "시그널 표시"}
    TEXTPACK['GUIO_CHARTDRAWER:MMACDHISTOGRAMDISPLAY'] = {'ENG': "DISPLAY HISTOGRAM",
                                                          'KOR': "히스토그램 표시"}
    TEXTPACK['GUIO_CHARTDRAWER:MMACDSETTINGS'] = {'ENG': "MMACD SETTINGS",
                                                  'KOR': "MMACD 설정"}
    TEXTPACK['GUIO_CHARTDRAWER:MMACDSIGNALINTERVAL'] = {'ENG': "MMACD SIGNAL INTERVAL",
                                                        'KOR': "MMACD 시그널 기간"}
    TEXTPACK['GUIO_CHARTDRAWER:MULTIPLIER'] = {'ENG': "MULTIPLIER",
                                               'KOR': "멀티플라이어"}
    TEXTPACK['GUIO_CHARTDRAWER:DMIINTERVAL'] = {'ENG': "DMI INTERVAL",
                                                'KOR': "DMI 기간"}
    TEXTPACK['GUIO_CHARTDRAWER:ADXINTERVAL'] = {'ENG': "ADX INTERVAL",
                                                'KOR': "ADX 기간"}
    TEXTPACK['GUIO_CHARTDRAWER:WOISETTINGS'] = {'ENG': "WOI SETTINGS",
                                                'KOR': "WOI 설정"}
    TEXTPACK['GUIO_CHARTDRAWER:BASE+'] = {'ENG': "BASE+",
                                          'KOR': "기본값+"}
    TEXTPACK['GUIO_CHARTDRAWER:BASE-'] = {'ENG': "BASE-",
                                          'KOR': "기본값-"}
    TEXTPACK['GUIO_CHARTDRAWER:SIGMA'] = {'ENG': "SIGMA",
                                          'KOR': "시그마"}
    TEXTPACK['GUIO_CHARTDRAWER:WOIBASE'] = {'ENG': "WOI BASE",
                                            'KOR': "WOI 기본"}
    TEXTPACK['GUIO_CHARTDRAWER:WOIBASEDISPLAY'] = {'ENG': "WOI BASE DISPLAY",
                                                   'KOR': "WOI 기본값 디스플레이"}
    TEXTPACK['GUIO_CHARTDRAWER:WOIGAUSSIANDELTA'] = {'ENG': "WOI GAUSSIAN DELTA",
                                                     'KOR': "WOI 가우시안 델타"}
    TEXTPACK['GUIO_CHARTDRAWER:NESBASE'] = {'ENG': "NES BASE",
                                            'KOR': "NES 기본"}
    TEXTPACK['GUIO_CHARTDRAWER:NESBASEDISPLAY'] = {'ENG': "NES BASE DISPLAY",
                                                   'KOR': "NES 기본값 디스플레이"}
    TEXTPACK['GUIO_CHARTDRAWER:NESGAUSSIANDELTA'] = {'ENG': "NES GAUSSIAN DELTA",
                                                     'KOR': "NES 가우시안 델타"}
#GUIO 'CHARTDRAWER' END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO 'DAILYREPORTVIEWER' ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
if (True):
    TEXTPACK['GUIO_DAILYREPORTVIEWER:TITLE_VIEWERSETTINGS'] = {'ENG': "VIEWER SETTINGS",
                                                               'KOR': "뷰어 설정"}
    TEXTPACK['GUIO_DAILYREPORTVIEWER:DISPLAYMODE'] = {'ENG': "DISPLAY MODE",
                                                      'KOR': "디스플레이 모드"}
    TEXTPACK['GUIO_DAILYREPORTVIEWER:BALANCE'] = {'ENG': "BALANCE",
                                                  'KOR': "잔고"}
    TEXTPACK['GUIO_DAILYREPORTVIEWER:COMMITMENTRATE'] = {'ENG': "COMMITMENT RATE",
                                                         'KOR': "자금투입률"}
    TEXTPACK['GUIO_DAILYREPORTVIEWER:RISKLEVEL'] = {'ENG': "RISK LEVEL",
                                                    'KOR': "위험도"}
    TEXTPACK['GUIO_DAILYREPORTVIEWER:NTRADES_TOTAL'] = {'ENG': "TRADE",
                                                        'KOR': "거래수"}
    TEXTPACK['GUIO_DAILYREPORTVIEWER:NTRADES_BUY'] = {'ENG': "BUY",
                                                      'KOR': "매수"}
    TEXTPACK['GUIO_DAILYREPORTVIEWER:NTRADES_SELL'] = {'ENG': "SELL",
                                                       'KOR': "매도"}
    TEXTPACK['GUIO_DAILYREPORTVIEWER:NTRADES_PSL'] = {'ENG': "PSL",
                                                      'KOR': "PSL"}
    TEXTPACK['GUIO_DAILYREPORTVIEWER:NLIQUIDATIONS'] = {'ENG': "LIQUIDATION",
                                                        'KOR': "청산"}
    TEXTPACK['GUIO_DAILYREPORTVIEWER:TIMEZONE'] = {'ENG': "TIMEZONE",
                                                   'KOR': "시간대"}
    TEXTPACK['GUIO_DAILYREPORTVIEWER:LINE'] = {'ENG': "LINE",
                                               'KOR': "지표"}
    TEXTPACK['GUIO_DAILYREPORTVIEWER:WIDTH'] = {'ENG': "WIDTH",
                                                'KOR': "두께"}
    TEXTPACK['GUIO_DAILYREPORTVIEWER:COLOR'] = {'ENG': "COLOR",
                                                'KOR': "색상"}
    TEXTPACK['GUIO_DAILYREPORTVIEWER:DISPLAY'] = {'ENG': "DISPLAY",
                                                  'KOR': "표시"}
    TEXTPACK['GUIO_DAILYREPORTVIEWER:APPLYSETTINGS'] = {'ENG': "APPLY SETTINGS",
                                                        'KOR': "설정 적용"}
    TEXTPACK['GUIO_DAILYREPORTVIEWER:SAVECONFIG'] = {'ENG': "SAVE CONFIGURATION",
                                                     'KOR': "설정 저장"}
    TEXTPACK['GUIO_DAILYREPORTVIEWER:FETCHINGDAILYREPORTS'] = {'ENG': "FETCHING DAILY REPORTS DATA...",
                                                               'KOR': "일일 리포트를 불러오는중..."}
#GUIO 'DAILYREPORTVIEWER' END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO 'HOURLYREPORTVIEWER' ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
if (True):
    TEXTPACK['GUIO_HOURLYREPORTVIEWER:TITLE_VIEWERSETTINGS'] = {'ENG': "VIEWER SETTINGS",
                                                                'KOR': "뷰어 설정"}
    TEXTPACK['GUIO_HOURLYREPORTVIEWER:DISPLAYMODE'] = {'ENG': "DISPLAY MODE",
                                                       'KOR': "디스플레이 모드"}
    TEXTPACK['GUIO_HOURLYREPORTVIEWER:BALANCE'] = {'ENG': "BALANCE",
                                                   'KOR': "잔고"}
    TEXTPACK['GUIO_HOURLYREPORTVIEWER:COMMITMENTRATE'] = {'ENG': "COMMITMENT RATE",
                                                          'KOR': "자금투입률"}
    TEXTPACK['GUIO_HOURLYREPORTVIEWER:RISKLEVEL'] = {'ENG': "RISK LEVEL",
                                                     'KOR': "위험도"}
    TEXTPACK['GUIO_HOURLYREPORTVIEWER:NTRADES_TOTAL'] = {'ENG': "TRADE",
                                                         'KOR': "거래수"}
    TEXTPACK['GUIO_HOURLYREPORTVIEWER:NTRADES_BUY'] = {'ENG': "BUY",
                                                       'KOR': "매수"}
    TEXTPACK['GUIO_HOURLYREPORTVIEWER:NTRADES_SELL'] = {'ENG': "SELL",
                                                        'KOR': "매도"}
    TEXTPACK['GUIO_HOURLYREPORTVIEWER:NTRADES_PSL'] = {'ENG': "PSL",
                                                       'KOR': "PSL"}
    TEXTPACK['GUIO_HOURLYREPORTVIEWER:NLIQUIDATIONS'] = {'ENG': "LIQUIDATION",
                                                         'KOR': "청산"}
    TEXTPACK['GUIO_HOURLYREPORTVIEWER:TIMEZONE'] = {'ENG': "TIMEZONE",
                                                    'KOR': "시간대"}
    TEXTPACK['GUIO_HOURLYREPORTVIEWER:LINE'] = {'ENG': "LINE",
                                                'KOR': "지표"}
    TEXTPACK['GUIO_HOURLYREPORTVIEWER:WIDTH'] = {'ENG': "WIDTH",
                                                 'KOR': "두께"}
    TEXTPACK['GUIO_HOURLYREPORTVIEWER:COLOR'] = {'ENG': "COLOR",
                                                 'KOR': "색상"}
    TEXTPACK['GUIO_HOURLYREPORTVIEWER:DISPLAY'] = {'ENG': "DISPLAY",
                                                   'KOR': "표시"}
    TEXTPACK['GUIO_HOURLYREPORTVIEWER:APPLYSETTINGS'] = {'ENG': "APPLY SETTINGS",
                                                         'KOR': "설정 적용"}
    TEXTPACK['GUIO_HOURLYREPORTVIEWER:SAVECONFIG'] = {'ENG': "SAVE CONFIGURATION",
                                                      'KOR': "설정 저장"}
    TEXTPACK['GUIO_HOURLYREPORTVIEWER:FETCHINGHOURLYREPORTS'] = {'ENG': "FETCHING HOURLY REPORTS DATA...",
                                                                 'KOR': "시간별 리포트를 불러오는중..."}
#GUIO 'DAILYREPORTVIEWER' END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO 'NEURALNETWORKVIEWER' ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
if (True):
    TEXTPACK['GUIO_NEURALNETWORKVIEWER:TITLE_VIEWERSETTINGS'] = {'ENG': "VIEWER SETTINGS",
                                                                 'KOR': "뷰어 설정"}
    TEXTPACK['GUIO_NEURALNETWORKVIEWER:LINE'] = {'ENG': "LINE",
                                                 'KOR': "지표"}
    TEXTPACK['GUIO_NEURALNETWORKVIEWER:LINEPOSITIVE'] = {'ENG': "POSITIVE",
                                                         'KOR': "양성"}
    TEXTPACK['GUIO_NEURALNETWORKVIEWER:LINENEGATIVE'] = {'ENG': "NEGATIVE",
                                                         'KOR': "음성"}
    TEXTPACK['GUIO_NEURALNETWORKVIEWER:LINENEUTRAL'] = {'ENG': "NEUTRAL",
                                                        'KOR': "중성"}
    TEXTPACK['GUIO_NEURALNETWORKVIEWER:INPUTLAYER'] = {'ENG': "INPUT LAYER",
                                                       'KOR': "입력층"}
    TEXTPACK['GUIO_NEURALNETWORKVIEWER:LINEWIDTH'] = {'ENG': "WIDTH",
                                                      'KOR': "두께"}
    TEXTPACK['GUIO_NEURALNETWORKVIEWER:COLOR'] = {'ENG': "COLOR",
                                                  'KOR': "색상"}
    TEXTPACK['GUIO_NEURALNETWORKVIEWER:DISPLAY'] = {'ENG': "DISPLAY",
                                                    'KOR': "표시"}
    TEXTPACK['GUIO_NEURALNETWORKVIEWER:APPLYSETTINGS'] = {'ENG': "APPLY SETTINGS",
                                                          'KOR': "설정 적용"}
    TEXTPACK['GUIO_NEURALNETWORKVIEWER:SAVECONFIG'] = {'ENG': "SAVE CONFIGURATION",
                                                       'KOR': "설정 저장"}
    TEXTPACK['GUIO_NEURALNETWORKVIEWER:REQUESTINGCONNECTIONSDATA'] = {'ENG': "REQUESTING NEURAL NETWORK CONNECTIONS DATA...",
                                                                      'KOR': "뉴럴 네트워크 연결 데이터 요청중..."}
    TEXTPACK['GUIO_NEURALNETWORKVIEWER:NEURALNETWORKCONNECTIONSDATAREQUESTFAILED'] = {'ENG': "NEURAL NETWORK CONNECTIONS DATA REQUEST FAILED",
                                                                                      'KOR': "뉴럴 네트워크 연결 데이터 요청 실패"}
#GUIO 'DAILYREPORTVIEWER' END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


