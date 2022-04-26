from dash import Dash
from dash import dcc
from dash import html
from datetime import date
from dash import Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
import matplotlib.pyplot as plt
import yfinance as yf
from dash.exceptions import PreventUpdate
from plotly.graph_objects import Layout
from plotly.validator_cache import ValidatorCache
import dash_bootstrap_components as dbc
import time
from googlesearch import search


def name_convert(self):

    searchval = 'yahoo finance '+self
    link = []
    #limits to the first link
    for url in search(searchval, tld='es', lang='es', stop=1):
        link.append(url)

    link = str(link[0])
    link=link.split("/")
    if link[-1]=='':
        ticker=link[-2]
    else:
        x=link[-1].split('=')
        ticker=x[-1]

    return(ticker)

# Create dash instance and store in app variable
# 2. Create a Dash app instance
app = Dash(external_stylesheets=[dbc.themes.CYBORG])
# app = dash.Dash()
app.config.suppress_callback_exceptions=True

# Store application's server property in variable
server = app.server




placeholder_data = dbc.Row([
    dbc.Row([
        dbc.Col([
            html.H2("About Netflix"),
            html.Br(),
            html.P("\
                    Netflix, Inc. is an American subscription streaming service and production company. \
                    Launched on August 29, 1997, it offers a film and television series library through \
                    distribution deals as well as its own productions, known as Netflix Originals.                                                                        \
                "),
            html.P("\
                    As of December 31, 2021, Netflix had over 221.8 million subscribers worldwide, \
                    including 75.2 million in the United States and Canada, 74.0 million in Europe, the \
                    Middle East and Africa, 39.9 million in Latin America and 32.7 million in Asia-Pacific. \
                    It is available worldwide aside from Mainland China (due to local restrictions), Syria, North \
                    Korea, Kosovo, Russia (due to the 2022 Russian invasion of Ukraine) and Crimea (due to US sanctions). \
                    Netflix has played a prominent role in independent film distribution, and is a member of the Motion Picture Association (MPA).                                                                      \
                "),
            html.P("\
                    Netflix can be accessed via internet browser on computers, or via application \
                    software installed on smart TVs, set-top boxes connected to televisions, tablet \
                    computers, smartphones, digital media players, Blu-ray Disc players, video game \
                    consoles and virtual reality headsets on the list of Netflix-compatible devices.\
                    It is available in 4K resolution.[16] In the United States, the company provides DVD \
                    and Blu-ray rentals delivered individually via the United States Postal Service from regional warehouses.                                                                    \
                "),
        ]),
    ])
])
graph_content = dbc.Col([
    dbc.Row([
        dbc.Col([
            html.H2("Trend History")
        ], className="col-12"),
        dbc.Col([
            html.H5("Enter a start and end date to view the stock’s trend", className="mt-3")
        ], className="col-12"),  
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dcc.DatePickerRange(
                        id='my-date-picker-range',
                        min_date_allowed=date(1995, 8, 5),
                        max_date_allowed=date.today(),
                        initial_visible_month=date(2022, 4, 22),
                        end_date=date.today(),
                        className="mb-2"
                    ),
                    html.Div(id='output-container-date-picker-range')
                ], className="col-12"),
                dbc.Col([
                    dbc.Button("VIEW TREND",
                    color="primary",
                    id="view-trend-button",
                    size="md",
                    n_clicks=0), 

                ], className="col-12, mt-3")
            ]),
        ], className="col-12, mt-2"),
    ], className="mb-3"),
], className="col-12"),
dbc.Col([
    dbc.Row([
        dbc.Col([
            html.H2("Forecaster")
        ], className="col-12"),
        dbc.Col([
            html.H5("Enter a number of days from today to get stock price prediction", className="mb-3"),
        ], className="col-12, mb-2"),
        dbc.Col([
            dbc.Input(placeholder="5", type="number", min=0, max=100, step=1, size="lg", className="mb-3"),
            html.P(id="forecast-output"),
        ], className="mt-1, col-9", id="forecast-input"),
        dbc.Col([
            dbc.Button("VIEW FORECAST",
            color="primary",
            id="button",
            style={"height":"50px"})
        ],className="mb-3, col-3")
    ])
])



trends_date_input = dbc.Col([
    dbc.Row([
        dbc.Col([
            html.H3("Trend History", className="mb-3")
        ], className="col-12, mt-5"),
        dbc.Col([
            html.H6("Enter a start and end date to view the stock’s trend")
        ], className="col-12"),  
        dbc.Col([ 
            html.Div([
                dcc.DatePickerRange(
                    id='my-date-picker-range',
                    min_date_allowed=date(1995, 8, 5),
                    max_date_allowed=date.today(),
                    initial_visible_month=date(2022, 4, 22),
                    end_date=date.today(),
                    className="mb-2"
                )
            ], style= {"width":"100% !important", "height":"50px !important"}),
            dbc.Row([
                dbc.Col(id='output-container-date-picker-range')
            ], className="mt-2"),
        ], className="col-10, mt-2"),
        dbc.Col([
            dbc.Button("VIEW TREND",
            color="primary",
            id="button",
            size="md",
            style={"height":"50px"})
        ],className="col-12, mt-3")
    ], className="mb-3"),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="graph")
        ])
    ], className="mt-4")
])

forecast_input = dbc.Col([
    dbc.Row([
        dbc.Col([
            html.H3("Forecast", className="mb-3")
        ], className="col-12, mt-5"),
        dbc.Col([
            html.H6("Enter a number of days from today to get stock price prediction", className="mb-3"),
        ], className="col-12"),
        dbc.Col([
            dbc.Input(placeholder="5", type="number", min=0, max=100, step=1, size="lg", className="mb-3", style={"height":"50px"}),
            html.P(id="forecast-output"),
        ], className="mt-1, col-6", id="forecast-input"),
        dbc.Col([
            dbc.Button("VIEW FORECAST",
            color="primary",
            id="button",
            style={"height":"50px"})
        ],className="mb-3, col-3")
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="graph")
        ])
    ], className="mt-4")
])



# This is the layout of the webpage
app.layout = dbc.Container(
    [
        dcc.Store(id="stocks"),
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
                        html.H5("Please enter a legitimate stock code to get its company information and stock details"),
                    ], className="mb-2")
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Input(id="stock-input", placeholder="i.e. NFLX", type="text", size="lg", className="mb-3", style={"height":"50px"}),
                        html.P(id="output"),
                    ], className="col-6"),
                    dbc.Col([
                        dbc.Button("SEARCH STOCK",
                        color="primary",
                        id="search-button",
                        n_clicks=0,
                        className="mb-3",
                        style={"height":"50px"})
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
                        # html.Img(src="assets/netflix.png", id="logo", style={"width":"75%"})
                    ], className="col-2"),
                    dbc.Col([
                        dbc.Row([
                            # html.H1("Netflix")
                            html.H1(id="name")
                        ], className=""),
                        dbc.Row([
                            # html.H4("NFLX")
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
                    dbc.Col([
                        html.H2(id="company-overview", className="mt-5")
                    ], className="col-12"),
                    dbc.Col([
                        html.P(id="description", style={"font-size":"16px"})
                    ], className="mt-3")
                ], className="mb-5"),
                dbc.Row([
            
                ], id="trends-content"),
                dbc.Row([
                    # dcc.Graph(id="graph")
                ], id="graph"),
                dbc.Row([
            
                ], id="forecast-content", className="mt-5"),
                
                    # dbc.Col([
                    #     dbc.Row([
                    #         html.H1("$340.00")
                    #     ], className="mb-2"),
                    #     dbc.Row([
                    #         dbc.Col([
                    #             html.H6("-$3.27 (-0.96%) Today", className="text-danger")
                    #         ], className="col-5"),
                    #         dbc.Col([
                    #             html.H6("+2.14 (-0.63%) After Hours", className="text-success")
                    #         ], className="col-5"),
                    #     ])
                    # ], className="col-9, mt-5"),
                
                html.Div(id="netflix-placeholder-data", className="p-5"),
                html.Hr(),
                
                # USES THE TAB LAYOUT
                # dbc.Tabs(
                #     [
                #         dbc.Tab(label="Company Overview", tab_id="company-overview"),
                #         dbc.Tab(label="Trends", tab_id="scatter"),
                #         dbc.Tab(label="Forecast", tab_id="forecast")
                #     ],
                #     id="tabs",
                #     active_tab="company-overview",
                # ),
                # dbc.Row([
                # ], id="tab-content", className="p-5"),
            ]
        )
    ],
    fluid=True
)




# @app.callback([
#     Output("graph", "figure"), 
#     Input('my-date-picker-range', 'start_date'),
#     Input('my-date-picker-range', 'end_date'),
#     State('stock-input', 'value')])

# def update_line_chart(n, start_date, end_date, val):
#     if n == None:
#         return [""]
#         #raise PreventUpdate
#     if val == None:
#         raise PreventUpdate
#     else:
#         if start_date != None:
#           df = yf.download(val,str( start_date) ,str( end_date ))
#         else:
#           df = yf.download(val)  
#     df.reset_index(inplace=True)
#     fig = get_stock_price_fig(df)


@app.callback([
    Output("stocks", "data"),
    Input('search-button', 'n_clicks'),
    State('stock-input', 'value')
    ])
def update_line_chart(n, code):
    start = date(2022, 4, 1)
    end = date(2022, 4, 24)

    # df = yf.download(code)
    # df.reset_index(inplace=True)
    

    # fig = px.line(df,x= "Date" ,y= ["Close","Open"], title="Closing and Opening Price vs Date",markers=True)
    # fig.update_layout(title_x=0.5)

    df = px.data.stocks()
    fig = px.line(df, x='date', y="NFLX")

    # return fig
    return [dcc.Graph(figure=fig)]





@app.callback([
    Output('error_msg','children'),
    Output("loading-output-2", "children"),
    Output('logo','src'),
    Output('name','children'),
    Output('stock_code','children'),
    Output('price', 'children'),
    Output('difference', 'children'),
    Output('company-overview','children'),
    Output('description', 'children'),
    Output('trends-content', 'children'),
    Output('forecast-content', 'children'),
    Input('search-button', 'n_clicks'),
    State('stock-input', 'value')])


def update_company_data(n, val):
    # graph = dbc.Col([
    #     dcc.Graph(figure=data["scatter"])
    # ], className="col-12")

    if n and val == None:
        error_msg = "Hey there! Please enter a legitimate stock code to get details."
        return error_msg, None, None, None, None, None, None, None, None, None, None
        # raise PreventUpdate

    else:
        company = name_convert(val)
        ticker = yf.Ticker(company)
        info = ticker.info

        if info == None:
            return f"Oops, looks like that stock doesn't exist. Please enter a valid stock", None, None, None, None, None, None, None, None, None, None

        else:
            df = pd.DataFrame().from_dict(info, orient="index").T    
            df[['logo_url', 'shortName', 'longBusinessSummary', 'regularMarketPrice', 'previousClose']]
            prev_price = df['previousClose'].values[0]
            curr_price = df['regularMarketPrice'].values[0]
            space = "   "

            if curr_price < prev_price:
                change = prev_price - curr_price
                change_formatted = "{:.2f}".format(change)
                change_str = "Price down: -$"+ str(change_formatted)
            elif curr_price > prev_price:
                change = curr_price - prev_price
                change_formatted = "{:.2f}".format(change)
                change_str = "Price up: -$" + str(change_formatted)


            name = df['shortName'].values[0]
            company_overview = "About " + name
            price_to_str = str(curr_price)
            stock_price_str = "$" + price_to_str
            return None, None, df['logo_url'].values[0], df['shortName'].values[0], company, stock_price_str, change_str, company_overview, df['longBusinessSummary'].values[0], trends_date_input, forecast_input


# @app.callback([Output("tab-content", "children")], [Input("tabs", "active_tab"), Input("stocks", "data")],)
# def render_tab_content(active_tab, data):
#     """
#     This callback takes the 'active_tab' property as input, as well as the
#     stored graphs, and renders the tab content depending on what the value of
#     'active_tab' is.
#     """
#     if active_tab is not None:
#         if active_tab == "company-overview":
#             return dbc.Row([
#                 dbc.Col([
#                         html.H2("About Netflix", id="name"),
#                         html.Br(),
#                         html.P(id="description")
#                     ])
#                 ])
#         elif active_tab == "scatter":
#             return dbc.Row(
#                 [
#                     trends_date_input,
#                     dbc.Row([
#                         dbc.Col([
#                             html.H5("NFLX opening and closing price from 03/01/2022 - 04/22/2022", className="mb-4")
#                         ], className="col-12"),
#                         dbc.Col([
#                             dcc.Graph(figure=data["scatter"])
#                         ], className="col-12")
#                     ], className="mt-5")
#                 ]
#             )
#         elif active_tab == "forecast":
#             return dbc.Row(
#                 [
#                     forecast_input,
#                     dbc.Row([
#                         dbc.Col([
#                             html.H5("Predicted close price of NFLX in the next 5 days", className="mb-4")
#                         ], className="col-12"),
#                         dbc.Col([
#                             dcc.Graph(figure=data["scatter"])
#                         ], className="col-12")
#                     ], className="mt-5")
#                 ]
#             )
#     return html.P("Please enter a legitimate stock to view information")



# @app.callback(Output("stocks", "data"), [Input("view-trend-button", "n_clicks")])
# def generate_graphs(n):
#     """
#     This callback generates three simple graphs from random data.
#     """
#     if not n:
#         # generate empty graphs when app loads
#         return {k: go.Figure(data=[]) for k in ["scatter", "hist_1", "hist_2"]}

#     # simulate expensive graph generation process
#     time.sleep(2)

#     # generate 100 multivariate normal samples
#     data = np.random.multivariate_normal([0, 0], [[1, 0.5], [0.5, 1]], 100)

#     scatter = go.Figure(
#         data=[go.Scatter(x=data[:, 0], y=data[:, 1], mode="markers")]
#     )
#     hist_1 = go.Figure(data=[go.Histogram(x=data[:, 0])])
#     hist_2 = go.Figure(data=[go.Histogram(x=data[:, 1])])

#     # save figures in a dictionary for sending to the dcc.Store
#     return {"scatter": scatter, "hist_1": hist_1, "hist_2": hist_2}


#     # # save figures in a dictionary for sending to the dcc.Store
#     # return {"trends": scatter, "forecast": scatter}


@app.callback(
    Output('output-container-date-picker-range', 'children'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))
def update_output(start_date, end_date):
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





if __name__ == '__main__':
    app.run_server(debug=False, dev_tools_props_check=False )


