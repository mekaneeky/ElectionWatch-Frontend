# Import required libraries
import networkx as nx
import pickle
import copy
import pathlib
import dash
import math
from datetime import date
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html


from static import *
from graphing import build_block_tx_graph, _plot_graph
from utils import get_url
# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "Election Watch"
server = app.server
#cache = Cache(app.server, config={
#    # try 'filesystem' if you don't want to setup redis
#    'CACHE_TYPE': 'filesystem',
#    'CACHE_DIR': '.'
#})


layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Transaction Graph",
)

def days_to_election():
    
    f_date = date.today()
    l_date = date(2022, 8, 9)
    if l_date < f_date:
        return 0
    else:
        delta = l_date - f_date
        return delta.days

    

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        #html.Img(
                        #    src=app.get_asset_url("nau-logo.png"),
                        #    id="plotly-image",
                        #    style={
                        #        "height": "60px",
                        #        "width": "auto",
                        #        "margin-bottom": "25px",
                        #    },
                        #)
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Election Watch Kenya 2022",
                                    style={"margin-bottom": "0px"},
                                ),
                                #html.H5(
                                #    "PLD 450 Project", style={"margin-top": "0px"}
                                #),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(id="daysLeft"), html.P("Days Left Till Election")],
                                    id="price",
                                    className="mini_container",
                                    style ={
                                        #'margin':'auto'
                                    }
                                ),
                             
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                       
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("Uhuru_Kenyatta.jpg"),
                            className="control_label",
                        ),
                        html.Div(
                            [
                            html.H3(
                                "Uhuru Kenyatta",
                                id="begin-block-height"
                            )
                            ,
                            html.H4("Test Party", id='begin-block-number')
                            ]

                        )
                        


                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                
                
                html.Div(
                    [dcc.Graph(id="main_graph")],
                    className="pretty_container twelve columns",
                ),
                
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("Uhuru_Kenyatta.jpg"),
                            className="control_label",
                        ),
                        html.Div(
                            [
                            html.H3(
                                "Uhuru Kenyatta",
                                id="begin-block-height2"
                            )
                            ,
                            html.H4("Test Party", id='begin-block-number2')
                            ]

                        )


                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options2",
                ),
                
                
                html.Div(
                    [dcc.Graph(id="main_graph2")],
                    className="pretty_container twelve columns",
                ),
                
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("Uhuru_Kenyatta.jpg"),
                            className="control_label",
                        ),
                        html.Div(
                            [
                            html.H3(
                                "Uhuru Kenyatta",
                                id="begin-block-height3"
                            )
                            ,
                            html.H4("Test Party", id='begin-block-number3')
                            ]

                        )

                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options3",
                ),
                
                
                html.Div(
                    [dcc.Graph(id="main_graph3")],
                    className="pretty_container twelve columns",
                ),
                
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [html.H3("Hourly Candidate Sentiment"),
                        dcc.Graph(id="cap_graph")],
                    className="pretty_container six columns",
                ),
                html.Div(
                    [html.H3("Monthly Candidate Sentiment"),
                    dcc.Graph(id="volume_graph")],
                    className="pretty_container six columns",
                ),
            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)



# Create callbacks
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("title", "children")],
)


@app.callback(
    [
        Output("cap_graph", "figure"),
        Output("volume_graph", "figure"),
    ],
    # Dummy input
    [Input(component_id="title", component_property="children")],
)
def load_chart_data(_):
    x_price, y_price = [], []
    price = get_url(MARKET_PRICE)["values"]
    x_volume, y_volume = [], []
    volume = get_url(TRADE_VOLUME)["values"]

    for price_point in price:
        timestamp = int(price_point["x"])
        timestamp = datetime.utcfromtimestamp(timestamp)
        x_price.append(timestamp)
        y_price.append(price_point["y"])

    for volume_point in volume:
        timestamp = int(volume_point["x"])
        timestamp = datetime.utcfromtimestamp(timestamp)
        x_volume.append(timestamp)
        y_volume.append(volume_point["y"])

    price_fig = px.line( 
        x=x_price, y=y_price)
    cap_fig = px.line( 
        x=x_volume, y=y_volume)
    return cap_fig, price_fig


@app.callback(
    Output("daysLeft", "children")
    ,
    # Dummy input
    [Input(component_id="title", component_property="children")],
)
def load_days_left(_):
    return days_to_election()
    
@app.callback(
    Output('main_graph', 'figure'),
    [Input('graph-button', 'n_clicks')],
    [State('begin-block-height', 'value')]
)
def update_graph_output(_, begin_block):
    print("Begin Drawing")
    if not begin_block:
        print("Drawing Coinbase")
        graph = nx.MultiDiGraph()
        graph.add_node("Coinbase")
        graph = _plot_graph(graph)
        return graph

    begin_block = int(begin_block)

    figure = build_block_tx_graph(begin_block)
    print("Drawing Figure")
    return figure
           


# Main
if __name__ == "__main__":
    app.run_server(debug=True)
