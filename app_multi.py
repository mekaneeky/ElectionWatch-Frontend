# Import required libraries
import pathlib
import dash
import math
import requests
from datetime import date
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash import dcc
from dash import html
from furl import furl
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


from settings import *
from utils import get_url
from datetime import datetime, timedelta

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()


app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=100%"}],
#    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

app.title = "Election Watch"
server = app.server


layout = dict(
    #autosize=True,
    #automargin=True,
    #margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    legend=dict(font=dict(size=10), orientation="h"),
    title="",
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
app.layout = html.Span(
    [
        dcc.Location(id='url', refresh=False),
        dcc.Graph(id="main_graph", style={'width': '105%', 'height': '350px', 'margin-left': -8, 'margin-top':-33})
    ],
            id="main_dashboard"    
)


def get_sentiment_scatter(period,data_type, candidate_name, begin_date, end_date):
   
    request_url = BASE_URL + PORT + f"/{data_type}/{period}/" +  begin_date.strftime("%Y-%m-%d %H:%M") + "/"  + end_date.strftime("%Y-%m-%d %H:%M") + "/"  + candidate_name  
    #import pdb;pdb.set_trace()
    data_dict = get_url(request_url)
    fig = go.Figure(data=go.Scatter(
        x = data_dict["timestamps"],
        y = data_dict["values"],
        mode='markers',
        marker=dict(
            size=10,
            #color=np.random.randn(500), #set color equal to a variable
            colorscale='Viridis', # one of plotly colorscales
            showscale=False
        )
    ))

    fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    )

    return fig




def get_image(url_to_get):
    return html.Img(
        src=app.get_asset_url(url_to_get),
        className="control_label",
        style={"height":"80%", "width":"80%", "margin":"auto"}
                )

def get_sentiment_pie(count_label, count_value, sum_label, sum_value ):

    fig = go.Figure(data=[go.Bar(
            x=[count_label, sum_label], y=[count_value, sum_value],
            text=[count_label, sum_label],
            textposition='auto',
        )])

    fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    xaxis=dict(
        autorange=True,
        showgrid=False,
        ticks='',
        showticklabels=False
    )

    )



    return fig





#
# http://127.0.0.1:8051/random?chart_type=cat&candidate_name=dog&data_type=bot_value&chart_duration=test
# data_type=candidate,candidate_bot
# chart_duration=hourly, daily, now
# candidate_name = 
# chart_type = pie, scatter
@app.callback(Output('main_graph', 'figure'),
              [Input('url', 'href')])
def conditional_load(href: str):
    f = furl(href)
    chart_type= f.args['chart_type']
    candidate_name= f.args['candidate_name']
    data_type= f.args['data_type']
    chart_duration= f.args['chart_duration']

    html_candidates = []
    
    if chart_type == "pie":
        request_url = BASE_URL + PORT + f"/{data_type}/now/" + candidate_name
        count_val, sum_val = get_url(request_url)
        if data_type == "sentiment":
            return get_sentiment_pie( "Posts Analyzed",count_val, "Total Sentiment" ,sum_val)
        else:
            return get_sentiment_pie( "Total Users Analyzed",count_val, "Total Bots Suspected" ,sum_val)

    if chart_type == "scatter":
        #period,data_type, candidate_name, begin_date, end_date
        if chart_duration == "daily":
           delta = timedelta(days=30)
        else:
           delta = timedelta(hours=24)

        
        now = datetime.now()
        prev_datetime = now - delta
        #import pdb;pdb.set_trace()
        
        return get_sentiment_scatter(chart_duration,data_type , candidate_name, prev_datetime, now )



# Main
if __name__ == "__main__":
    app.run_server(host="0.0.0.0",debug=True)

