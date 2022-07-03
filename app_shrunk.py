# Import required libraries
import pathlib
import dash
import math
import requests
from datetime import date
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash import dcc
from dash import html
import plotly.graph_objects as go


from settings import *
from utils import get_url
from datetime import datetime, timedelta

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)

app.index_string = '''<!DOCTYPE html>
<html>
<head>
<title>ElectionWatchKe</title>
<link rel="manifest" href="./assets/manifest.json" />
{%metas%}
{%favicon%}
{%css%}
</head>
<script type="module">
   import 'https://cdn.jsdelivr.net/npm/@pwabuilder/pwaupdate';
   const el = document.createElement('pwa-update');
   document.body.appendChild(el);
</script>
<body>
<script>
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', ()=> {
      navigator
      .serviceWorker
      .register('/assets/sw.js')
      .then(()=>console.log("Ready."))
      .catch(()=>console.log("Err..."));
    });
  }
</script>
{%app_entry%}
<footer>
{%config%}
{%scripts%}
{%renderer%}
</footer>
</body>
</html>
'''

app.title = "Election Watch"
server = app.server
#cache = Cache(app.server, config={
#    # try 'filesystem' if you don't want to setup redis
#    'CACHE_TYPE': 'filesystem',
#    'CACHE_DIR': '.'
#})


layout = dict(
    #autosize=True,
    #automargin=True,
    #margin=dict(l=30, r=30, b=20, t=40),
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
                )
                
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            id="main_dashboard",
            style={"display": "flex", "flex-direction": "column"},
            className="row"
        )
    ]
)


def get_sentiment_data(period, candidate_name, begin_date, end_date):
    
    if period == "daily":
        request_url = "http://0.0.0.0:8080" + DAILY_URL +  begin_date.strftime("%Y-%m-%d %H:%M") + "/" \
            + end_date.strftime("%Y-%m-%d %H:%M") + "/" \
            + candidate_name
    elif period == "hourly":
        request_url = "http://0.0.0.0:8080" + HOURLY_URL +  begin_date.strftime("%Y-%m-%d %H:%M") + "/" \
            + end_date.strftime("%Y-%m-%d %H:%M") + "/" \
            + candidate_name
    else:
        raise ValueError

    data_dict = get_url(request_url)
    #import pdb;pdb.set_trace()
    fig = go.Figure(data=go.Scatter(
        x = data_dict["timestamps"],
        y = data_dict["sentiments"],
        mode='markers',
        marker=dict(
            size=16,
            #color=np.random.randn(500), #set color equal to a variable
            colorscale='Viridis', # one of plotly colorscales
            showscale=False
        )
    ))

    return fig




def get_image(url_to_get):
    return html.Img(
        src=app.get_asset_url(url_to_get),
        className="control_label",
                )

def get_sentiment_pie(sentiment_value):

    fig = go.Figure(data=[go.Pie(labels=["Sentiment: "+sentiment_value , ""], values=[int(sentiment_value), 1000-int(sentiment_value)], hole=.3)]) 
    fig.update_traces(showlegend=False, hoverinfo='label', textinfo='label', textfont_size=20,marker=dict(colors=["gold", "white"], line=dict(color='#000000', width=2)))
    #fig.update_layout(height=425)

    return fig


@app.callback(
    Output(component_id='main_dashboard',component_property="children" ),
     # Dummy input
    [Input(component_id="title", component_property="children")]
)
def generate_all_candidates(_):
    candidates = get_url('http://0.0.0.0:8080/candidate/now')
    html_candidates = []
    for candidate in candidates:
        candidate_div = generate_candidate(candidate["name"], candidate["sentiment"], candidate["party"], 0,candidate["image_path"])
        html_candidates.append (candidate_div)
    return html_candidates

def generate_candidate(candidate_name, candidate_sentiment, candidate_party, candidate_number,image_path):

    return html.Div(
            [
              

                    
                    html.Span(
                        [
                            get_image(image_path),
                            html.Div(
                                [
                                html.H3(
                                    candidate_name,
                                    #id="candidate-" + candidate_number + "-name"
                                )
                                ,
                                html.H4(candidate_party)#, id='begin-block-number' + candidate_number)
                                ]
                            )
                            
                        ],
                        className="pretty_container four columns",
                        #id="cross-filter-options",
                    ),
                    html.Div(
                        [dcc.Graph(figure=get_sentiment_pie(candidate_sentiment))],
                        className="pretty_container four columns",
                    ),
                    #html.Div(
                    #    #[dcc.Graph(figure=get_sentiment_pie(candidate_sentiment))],
                    #    className="two columns",
                    #),
            
                html.Div(
                    [html.H3("Hourly Candidate Sentiment"),
                        dcc.Graph(figure=get_sentiment_data("hourly", candidate_name, datetime.now()-timedelta(hours=24),datetime.now() ))],
                    className="pretty_container five columns",
                ),
                html.Div(
                    [html.H3("Monthly Candidate Sentiment"),
                    dcc.Graph(figure=get_sentiment_data("daily", candidate_name, datetime.now()-timedelta(days=30),datetime.now() ))],
                    className="pretty_container five columns",
                ),

            #className="row",
            ])
                
        

        
    

# Main
if __name__ == "__main__":
    app.run_server(debug=True)
