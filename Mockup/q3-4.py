import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

def get_dataframe(path):
    data = pd.read_csv(path)
    data["duration_min"] = data["duration_ms"] / 60000 
    return data

def get_scatter_plot():
    data = get_dataframe("./dataset/spotify_songs_clean.csv")
    fig = px.scatter(
        data, x="duration_min", y="track_popularity",
        title="Relation entre la durée d'un morceau et sa popularité",
        labels={"duration_min": "Durée (minutes)", "track_popularity": "Popularité"},
        opacity=0.6,
        hover_data=["track_name"]  
    )
    fig.update_traces(marker=dict(size=5, line=dict(width=0)))
    return fig

def get_boxplot():
    data = get_dataframe("./dataset/spotify_songs_clean.csv")
    fig = px.box(
        data, x="playlist_genre", y="track_popularity",
        title="Influence du genre musical sur la popularité",
        labels={"playlist_genre": "Genre musical", "track_popularity": "Popularité"},
        points=False  
    )
    return fig

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H4("Impact de la durée sur la popularité des morceaux", style={"fontWeight": "bold", "fontSize": "20px"}),
    dcc.Graph(id="scatter_graph", figure=get_scatter_plot()),
    html.H4("Influence du genre musical sur la popularité", style={"fontWeight": "bold", "fontSize": "20px"}),
    dcc.Graph(id="boxplot_graph", figure=get_boxplot()),
])

app.run_server(debug=False)