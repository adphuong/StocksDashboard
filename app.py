from dash import Dash, dash_table
from dash import dcc
from dash import html
from datetime import datetime as date
from dash import Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
import plotly.io as pio
import matplotlib.pyplot as plt
import yfinance as yf
from dash.exceptions import PreventUpdate
from plotly.graph_objects import Layout
from plotly.validator_cache import ValidatorCache
import dash_bootstrap_components as dbc
import requests
import json
from googlesearch import search    # Used to convert company name to stock ticker


# Theme for plotly graph
pio.templates.default = "plotly_dark"

# Create dash instance and store in app variable
app = Dash(external_stylesheets=[dbc.themes.CYBORG])
app.config.suppress_callback_exceptions=True

# Store application's server property in variable
server = app.server

# ============================================================================= #
#                                WEBPAGE LAYOUT                                 #
# ============================================================================= #
app.layout = dbc.Container(
    [
        # dcc.Store(id="stocks"),
        html.Br(),
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Login/Create Account", href="#")),
            ],
            brand="All about Stocks",
            brand_href="#",
            color="none",
            dark=True,
            fluid=True
        ),
        html.Hr(),
        html.Hr(),
        dbc.Container(
            [
                dbc.Row([
                    dbc.Col([html.H1("Search stocks")])
                ], className="mt-5"),
                html.Hr(),
                dbc.Row([
                    dbc.Col([
                        html.H5("Please enter a stock ticker to get its company information and stock data"),
                    ], className="mb-2")
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Input(id="stock-input", placeholder="i.e. NFLX", type="text", \
                                  size="lg", className="mb-3", style={"height":"50px"}),
                        html.P(id="output"),
                    ], className="col-6"),
                    dbc.Col([
                        dbc.Button("SEARCH STOCK",
                        color="primary",
                        id="search-button",
                        n_clicks=0,
                        className="mb-3",
                        style={"height":"50px", "font-weight":"bold"})
                    ], className="col-3")
                ]),
                dbc.Row([
                    dbc.Col([
                        html.H5(id="error_msg", className="text-danger")
                    ])
                ], className="mt-3"),
                html.Div([
                    dcc.Loading(
                        children=[html.Div([html.Div(id="loading-output-2")])],
                        type="circle",
                    )
                ], id="loading", className="mt-5"),
                dbc.Row([
                    dbc.Col([
                        html.Img(id="logo", style={"width":"75%"})
                    ], className="col-2"),
                    dbc.Col([
                        dbc.Row([
                            html.H1(id="name")
                        ], className=""),
                        dbc.Row([
                            html.H4(id="stock_code")
                        ])
                    ], className="col-6"),
                    dbc.Col([
                        dbc.Row([
                            html.H1(id="price")
                        ], className="mb-2"),
                        dbc.Row([
                            html.H5(id="difference", className="")
                        ])
                    ], className="col-3"),
                ], className="mt-5"),
                html.Br(),
                html.Br(),
                dbc.Row([

                ], id="key-stats"),

                dbc.Row([
            
                ], id="trends-content"),
                dbc.Row([
                    dbc.Col([
                        html.Div([], 
                            id="graph-content"),
                    ])
                ], className="mt-4"),
                dbc.Row([
                    dbc.Col([
                        html.Div([], 
                            id="trend-table"),
                    ])
                ], className="mt-4"),
                html.Div([], className="mt-5"),
                dbc.Row([
                    dbc.Col([
                        html.H2(id="company-overview", className="mt-5")
                    ], className="col-12"),
                    dbc.Col([
                        html.P(id="description", style={"font-size":"16px"})
                    ], className="mt-3")
                ], className="mb-5"),
                
                html.Hr(),
            ]
        )
    ],
    fluid=True
)

# Layout for historical prices section
historical_prices_section = dbc.Col([
    dbc.Row([
        dbc.Col([
            html.H2("Historical Prices", className="mb-3")
        ], className="col-12, mt-5"),
        dbc.Col([
            html.H6("Currently showing closing and opening prices of this year to date"),
            html.H6("Enter a start and end date to view the stock’s trend during a specified time")
        ], className="col-12"),
    ], className="mb-3"),  
    dbc.Row([
        dbc.Col([ 
            html.Div([
                dcc.DatePickerRange(
                    id='my-date-picker-range',
                    min_date_allowed=date(1995, 8, 5),
                    max_date_allowed=date.now(),
                    initial_visible_month=date.now(),
                    end_date=date.now().date(),
                    className="mb-2"                 
                )
            ], style={"width":"100%"}),
            dbc.Row([
                dbc.Col(id='output-container-date-picker-range')
            ], className="mt-2"),
        ], width=5, className=""),
        dbc.Col([
            html.Div([
                dbc.Button("VIEW HISTORICAL PRICES",
                color="primary",
                id="trend-button",
                size="md",
                n_clicks=0,
                style={"height":"50px", "font-weight":"bold"})
            ], className="")
        ], width=3, )
    ], className="mt-3")
])
# ============================================================================= #
#                            END OF LAYOUT SECTION                              #
# ============================================================================= #


# ============================================================================= #
#                                   FUNCTIONS                                   #
# ============================================================================= #
# Yahoo finance only searches information using stock tickers. If user
# enters company name in search field, this will convert it into its 
# stock ticker using Google's search API
def convert_to_ticker(self):
    if self == None:
        return self
    else:
        link = []

        # Used in Google's search to look up company name on Yahoo Finance
        searchval = 'yahoo finance ' + self

        # Grabs just the first link in the Google search
        for url in search(searchval, tld='es', lang='es', stop=1):
            link.append(url)

        # Convert link to string and split it at every '/'
        link = str(link[0])
        link = link.split("/")

        if link[-1] == '':
            # Last item in the link is empty, so ticker is 
            # the second to last item
            # ex - https://finance.yahoo.com/quote/NFLX/
            ticker = link[-2]
        else:
            # Start splitting link after last item in link
            x = link[-1].split('=')
            ticker = x[-1]

        return(ticker)


# Calculates the difference from today's stock prices with
# the previous closing price
def calculate_prev_close(curr_price, prev_price):
    if curr_price < prev_price:
        # Stock price is down from previous closing
        # Calculate difference
        change = prev_price - curr_price
        change_formatted = "{:.2f}".format(change)
        change_str = "Price down: -$"+ str(change_formatted)
    elif curr_price > prev_price:
        # Stock price is up from previous closing
        # Calculate price increase
        change = curr_price - prev_price
        change_formatted = "{:.2f}".format(change)
        change_str = "Price up: +$" + str(change_formatted)

    return change_str


# Takes in dataframe and generates stock closing and 
# opening prices for each date
def get_stock_price_graph(df):
    fig = px.line(df,
                  x = "Date",
                  y = ["Close", "Open"],
                  labels = dict(value="Price", variable="Price Category"),
                  title="Opening and Closing Price vs Date")
    fig.update_layout(title_x=0.5)
    fig.data[0].line.color = "#00FFFF"

    return fig


# Takes in the data retrieved from microservice and generates a table with
# the stock's closing and opening prices for the requested time frame
def get_stock_price_table(dict_data):
    # Store data (from microservice) into a Dataframe to use for data
    # and reverse col and rows
    table_data = pd.DataFrame.from_dict(dict_data)
    reverse = table_data.transpose()

    # Rename columns for table
    reverse.columns = ['Date', 'Opening', 'Closing']

    # Create table layout of stock's opening and closing prices
    table = dash_table.DataTable(
            data = reverse.to_dict('rows'),
            columns =[
                {'id': i, 'name': i} for i in reverse.columns
            ],
            style_table={'height': '400px', 'overflowY': 'auto'},
            style_cell_conditional= [
                {
                    'if': {'column_id': 'Date'},
                    'textAlign':'left'
                }
            ],
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#202020',
                }
            ],   
            sort_action="native",
            style_data = {'backgroundColor':'black', 'color':'white'},
            style_header = {'backgroundColor':'#111111', 'color':'white'},
            style_header_conditional = [
                {
                    'if': {'column_id': 'Date'},
                    'textAlign':'left'
                }
            ]
        )

    return table
# ============================================================================= #
#                                END OF FUNCTIONS                               #
# ============================================================================= #


# ============================================================================= #
#                               CALLBACK FUNCTIONS                              #
# ============================================================================= #
@app.callback([
    Output('error_msg','children'),
    Output("loading-output-2", "children"),
    Output('logo','src'),
    Output('name','children'),
    Output('stock_code','children'),
    Output('price', 'children'),
    Output('difference', 'children'),
    Output('trends-content', 'children'),
    Output('company-overview','children'),
    Output('description', 'children'),
    Input('search-button', 'n_clicks'),
    State('stock-input', 'value')])

# Retrieves company data from Yahoo Finance and displays it on the webpage
def update_company_data(n, val):
    if n and val == None:
        # No stock ticker entered - error message displays
        error_msg = "Hey there! Please enter a legitimate stock code to get details."

        return error_msg, None, None, None, None, None, None, None, None, None
    else:
        stock_ticker = convert_to_ticker(val)     # Converts company name to its stock ticker
        ticker = yf.Ticker(stock_ticker)          # Retrieves stock data from Yahoo Finance
        info = ticker.info

        if info == None:
            # Stock does not exist
            return f"Oops, looks like that stock doesn't exist. Please enter a valid stock", \
            None, None, None, None, None, None, None, None, None
        else:
            # Create dataframe of the stock's info
            df = pd.DataFrame().from_dict(info, orient="index").T    

            # Grab logo, company's short name, business summary, stock price, and previous close price
            df[['logo_url', 'shortName', 'longBusinessSummary', 'regularMarketPrice', 'previousClose']]
            prev_price = df['previousClose'].values[0]
            curr_price = df['regularMarketPrice'].values[0]
            space = "   "

            # Calculates the diff between today's price and previous closing price
            prev_close_diff = calculate_prev_close(curr_price, prev_price)

            company_name = df['shortName'].values[0]
            company_overview = "About " + company_name          # Section title - "About [company_name]"     
            
            # Get stock price string to print in Stock Overview section
            price_to_str = str(curr_price)
            stock_price_str = "$" + price_to_str

            return None, None, df['logo_url'].values[0], company_name, stock_ticker, stock_price_str, \
                    prev_close_diff, historical_prices_section, company_overview, \
                    df['longBusinessSummary'].values[0]


@app.callback([
    Output("graph-content", "children"), 
    Output("trend-table", "children"),
    Input('trend-button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    State('stock-input', 'value')])

# Retrieves stock's opening and closing prices with requested
# dates from user, and displays the data in a graph and a table
def update_graph_and_table(n, start_date, end_date, val):
    if n == None:
        return [""]
    if val == None:
        raise PreventUpdate
    else:
        # Call microservice to retrieve data
        ticker = convert_to_ticker(val)        # Convert company name to stock ticker
        url = 'http://localhost:3500'          # Address that microservice is running on 

        if start_date == None:
            # Start date is not entered by user, so it defaults to beginning of the year
            year = 2022
            start_date = "2022-1-1"        

        # MICROSERVICE CALLED HERE - passing in stock ticker, start, and
        # end date to retrieve open and closing prices for that stock
        data = {'stock':ticker, 'start':start_date, 'end':end_date}
        req_data = requests.get(url, params = data)
        df = yf.download(ticker, str(start_date) ,str(end_date))

    df.reset_index(inplace=True)                # Reset the index of the DataFrame
    graph_fig = get_stock_price_graph(df)       # Generate graph with dataframe

    # Grab data retrieved from microservice
    dict_data = req_data.json()
    dict_data_norm = pd.json_normalize(dict_data)

    # Generate table with the stock's opening and closing prices
    table = get_stock_price_table(dict_data)

    return [dcc.Graph(figure=graph_fig)], table


@app.callback(
    Output('output-container-date-picker-range', 'children'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))

# Takes in the start and end dates entered by the user and 
# displays the string notifying the user which dates 
# were entered
def update_date_selection(start_date, end_date):
    string_prefix = 'You have selected: '
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'End Date: ' + end_date_string
    if len(string_prefix) == len('You have selected: '):
        return 'Select a date to see it displayed here'
    else:
        return string_prefix

# ============================================================================= #
#                           END OF CALLBACK FUNCTIONS                           #
# ============================================================================= #


if __name__ == '__main__':
    app.run_server(debug=False, dev_tools_props_check=False)