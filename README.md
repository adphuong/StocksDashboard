# A Simple Stocks Dashboard
A single-page web app, built with <a href="https://dash.plotly.com/introduction">Dash</a>, that retrieves stock information by calling Yahoo Finance's
API based on the given ticker. It displays the company information, current stock price, and creates a chart of its historical prices.


<img src='walkthrough.gif' title='Video Walkthrough' width='' alt='Video Walkthrough'/>  


## Setup
### 1. Clone repo
```
git clone https://github.com/adphuong/StocksDashboard.git  
cd StocksDashboard
```

### 2. Setup virtual environment (optional)  
  Create a new environment  
  ```
  virtualenv <my_env_name> -p /usr/bin/python3.8
  ```

  Activate the new environment  
  ```
  source <my_env_name>/bin/activate
  ```
  
### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Run app
In a terminal, run the main app
```
python3 app.py
```
In another terminal, run the microservice
```
python3 historicalPricesRetrieval.py
```
