# AutoTradeMachine_Eta

[![korean-readme](https://img.shields.io/badge/lang-한국어-blue.svg)](./README.ko.md)

This is the seventh version of the **Auto Trade Machine** project.  


---

### 🧱 System Architecture ###

---

### ▶️ How To Run ###
* ***Windows*** 🪟
1. run this file or `./setup.bat`
2. run this file or `./run.bat`

* ***Linux*** 🐧 ***/*** ***MacOS*** 🍎
1. enter this command `chmod +x setup.sh run.sh`
2. run this file or `./setup.sh`
3. run this file or `./run.sh`

---

### 👀 Application Preview & How To Use ###
* Market View
* Real-Time Analysis
* Trading Strategy
* Simulation (Backtesting)
* Binance Account Connection
* Trading
* Neural Network (Just for fun for now)


---

### 🚫 Warning (VERY IMPORTANT)
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
* **Last Updated:** November 24th, 2025  
* **Author:** Bumsu Kim
* **Email:**  kimlvis31@gmail.com
