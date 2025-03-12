import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

def convert_date(date):
    try:
        # Format complet "%Y-%m-%d"
        return pd.to_datetime(date, format="%Y-%m-%d")
    except ValueError:
        try:
            # Format année seule "%Y", compléter par "-01-01"
            return pd.to_datetime(date, format="%Y") + pd.offsets.DateOffset(months=0, days=0)
        except ValueError:
            return pd.NaT


def get_dataframe(path):
    data = pd.read_csv(path)
    data["track_album_release_date"] = data["track_album_release_date"].apply(convert_date)
    data = data[data["track_album_release_date"].dt.year >= 1970] # On ne garde que les musiques après 1970, car il n'y a pas assez d'échantillons avant
    return data

def get_hover_template():
    return (
        "<b>Nombre d'artistes:</b></span>" 
        " %{customdata} <br /></span>"
        "<b>Nombre de sous-genres:</b></span>"
        " %{x}<br /></span>"
        "<b>Popularité:</b></span>"
        " %{y:.3f} %</span>"
        "<extra></extra>" # Pour enlever le "trace 0" qui apparait automatiquement sinon
    )

def get_figure():
    data = get_dataframe("./dataset/spotify_songs_clean.csv")
    div_pop_df = data.groupby("track_artist").agg(nb_subgenres=("playlist_subgenre", "nunique"), mean_popularity=("track_popularity", "mean")).reset_index()
    div_pop_df = div_pop_df.groupby("nb_subgenres").agg(mean_popularity=("mean_popularity", "mean"), nb_artist=("track_artist", "count")).reset_index()
    div_pop_df = div_pop_df[div_pop_df["nb_artist"] > 4]

    size = div_pop_df["nb_artist"]

    fig = go.Figure(data=[go.Scatter(
        x=div_pop_df["nb_subgenres"],
        y=div_pop_df["mean_popularity"],
        name="Nombre d'artistes",
        mode='markers',
        marker=dict(size=size, sizemode='area', sizeref=2, sizemin=4, color='#62d089'),
        customdata=size,
    )])

    fig.update_traces(hovertemplate=get_hover_template())

    fig.update_layout(
        title=dict(text="<b>Popularité moyenne des artistes en fonction du nombre de sous-genres<b>", font=dict(size=25)),
        xaxis_title="Nombre de sous-genres", xaxis=dict(showgrid=True),
        yaxis_title="Popularité moyenne", yaxis=dict(showgrid=True),
        showlegend=True,
        plot_bgcolor='#f5f6f7',
        height=600,
    )
    return fig



app = dash.Dash(__name__)

app.layout = html.Div([
    html.H4("Étude de la popularité des artistes en fonction de leur diversité musicale", style={"fontWeight": "bold", "fontSize": "30px"}),
    dcc.Graph(id="graph", figure = get_figure()),
])



app.run_server(debug=False)
