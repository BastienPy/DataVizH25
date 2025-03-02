import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

def get_dataframe(path):
    data = pd.read_csv(path)
    data["track_album_release_date"] = pd.to_datetime(data["track_album_release_date"])
    data = data[data["track_album_release_date"].dt.year >= 1970] # On ne garde que les musiques après 1970, car il n'y a pas assez d'échantillons avant
    return data


def data_preprocess(path,type):
    data = get_dataframe(path)
    data["track_album_release_date"] = pd.to_datetime(data["track_album_release_date"])
    data["year"] = data["track_album_release_date"].dt.year
    data["decennie"] = (data["year"] // 10) * 10  # Obtention de la décennie

    if type != "playlist_genre":
        data = data[data["playlist_genre"] == type]
        type = "playlist_subgenre"
    genre_data = data.groupby(["decennie", type]).size().reset_index(name="count")
    genre_data = genre_data.pivot(index="decennie", columns=type, values="count")

    nb_songs_by_decade = genre_data.sum(axis=1)
    genre_data = (genre_data.div(nb_songs_by_decade, axis=0)*100).reset_index()
    genre_data = genre_data.melt(id_vars="decennie", var_name=type, value_name="percentage")

    return genre_data


def get_hover_template(type_name):

    return (
        f"<b>{type_name}:</b></span>" 
        " %{customdata[0]} <br /></span>"
        "<b>Decennie:</b></span>"
        " %{x}<br /></span>"
        "<b>Pourcentage:</b></span>"
        " %{y:.3f} %</span>"
        "<extra></extra>" # Pour enlever le "trace 0" qui apparait automatiquement sinon
    )

def get_figure_genre():
    genre_data = data_preprocess("./dataset/spotify_songs_clean.csv", "playlist_genre")
    fig = px.area(genre_data, x="decennie", y="percentage", color="playlist_genre", line_group="playlist_genre", hover_data=["playlist_genre"])

    fig.update_layout(height=500)
    fig.update_traces(hovertemplate=get_hover_template("Genre"))
    fig.update_yaxes(title_text='Pourcentage (%)')
    fig.update_layout(legend_title_text="Genre")

    return fig

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H4("Évolution de la proportion de genres et sous-genres musicaux par décennie", style={"fontWeight": "bold", "fontSize": "30px"}),
    html.H4("Évolution de la proportion des genres", style={"fontWeight": "bold", "fontSize": "20px"}),
    dcc.Graph(id="graph", figure = get_figure_genre()),
    html.H4("Évolution de la proportion des sous genres du genre choisi", style={"fontWeight": "bold", "fontSize": "20px"}),
    dcc.Graph(id="subgenre_graph"),
])


@app.callback(
    Output('subgenre_graph', 'figure'),
    [Input('graph', 'clickData')])
def display_area(clickData):
    if clickData == None :
        fig = px.area()
        fig.add_annotation(dict(xref="paper", yref="paper", x=0.5, y=0.5), text="Aucune donnée pour le moment, cliquez sur une des lignes.", showarrow=False)

        return fig
    
    type_name = clickData["points"][0]["customdata"][0]
    genre_data = data_preprocess("./dataset/spotify_songs_clean.csv", type_name)
    fig = px.area(genre_data, x="decennie", y="percentage", color="playlist_subgenre", line_group="playlist_subgenre", hover_data=["playlist_subgenre"])


    fig.update_traces(hovertemplate=get_hover_template(type_name))
    fig.update_yaxes(title_text='Pourcentage (%)')
    fig.update_layout(legend_title_text="Sous genre de "+type_name)

    return fig


app.run_server(debug=False)