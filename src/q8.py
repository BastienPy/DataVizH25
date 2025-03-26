import pandas as pd
import dash
from dash import dcc, html, Input, Output, callback_context
import plotly.express as px


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

subgenre_cache = {
    "edm": px.area(data_preprocess("./dataset/spotify_songs_clean.csv", "edm"), x="decennie", y="percentage", color="playlist_subgenre", line_group="playlist_subgenre", hover_data=["playlist_subgenre"]),
    "latin": px.area(data_preprocess("./dataset/spotify_songs_clean.csv", "latin"), x="decennie", y="percentage", color="playlist_subgenre", line_group="playlist_subgenre", hover_data=["playlist_subgenre"]),
    "pop":   px.area(data_preprocess("./dataset/spotify_songs_clean.csv", "pop"), x="decennie", y="percentage", color="playlist_subgenre", line_group="playlist_subgenre", hover_data=["playlist_subgenre"]),
    "r&b":   px.area(data_preprocess("./dataset/spotify_songs_clean.csv", "r&b"), x="decennie", y="percentage", color="playlist_subgenre", line_group="playlist_subgenre", hover_data=["playlist_subgenre"]),
    "rap":   px.area(data_preprocess("./dataset/spotify_songs_clean.csv", "rap"), x="decennie", y="percentage", color="playlist_subgenre", line_group="playlist_subgenre", hover_data=["playlist_subgenre"]),
    "rock":  px.area(data_preprocess("./dataset/spotify_songs_clean.csv", "rock"), x="decennie", y="percentage", color="playlist_subgenre", line_group="playlist_subgenre", hover_data=["playlist_subgenre"])
}


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
    fig = px.area(genre_data, x="decennie", y="percentage", color="playlist_genre", line_group="playlist_genre", hover_data=["playlist_genre"],
                  color_discrete_sequence=px.colors.qualitative.Dark2)

    fig.update_layout(height=500)
    fig.update_traces(hovertemplate=get_hover_template("Genre"))
    fig.update_yaxes(title_text='Pourcentage (%)')
    fig.update_layout(legend_title_text="Genre")


    return fig

layout = html.Div([
    html.H4("Évolution de la proportion de genres et sous-genres musicaux par décennie", style={"fontWeight": "bold", "fontSize": "30px"}),
    html.Div([
        html.Div([
            html.H4("Évolution de la proportion des genres", style={"fontWeight": "bold", "fontSize": "20px"}),
            dcc.Graph(id="graph-q8", figure=get_figure_genre())
        ], style={"width": "50%", "display": "inline-block"}),
        html.Div([
            html.H4("Évolution de la proportion des sous genres du genre choisi", style={"fontWeight": "bold", "fontSize": "20px"}),
            html.Div([
                html.Button("EDM", id="edm-button", n_clicks=0),
                html.Button("Latin", id="latin-button", n_clicks=0),
                html.Button("Pop", id="pop-button", n_clicks=0),
                html.Button("R&B", id="r&b-button", n_clicks=0),
                html.Button("Rap", id="rap-button", n_clicks=0),
                html.Button("Rock", id="rock-button", n_clicks=0)
            ], style={"display": "flex", "gap": "5px", "margin-top": "20px"}),
            dcc.Graph(id="subgenre_graph"),
        ], style={"width": "50%", "display": "inline-block", "verticalAlign": "top"})
    ], style={"display": "flex"})
])


def register_callbacks(app):
    @app.callback(
        Output("subgenre_graph", "figure"),
        [Input("pop-button", "n_clicks"),
        Input("rap-button", "n_clicks"),
        Input("rock-button", "n_clicks"),
        Input("edm-button", "n_clicks"),
        Input("r&b-button", "n_clicks"),
        Input("latin-button", "n_clicks")])
    def update_graph(pop_clicks, rap_clicks, rock_clicks, edm_clicks, rnb_clicks, latin_clicks):
        ctx = dash.callback_context
        if not ctx.triggered:
            fig = px.area()
            fig.add_annotation(dict(xref="paper", yref="paper", x=0.5, y=0.5), text="Aucune donnée pour le moment, cliquez sur une des lignes.", showarrow=False)
            return fig
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        genre = button_id.split("-")[0]

        fig = subgenre_cache[genre]

        fig.update_traces(hovertemplate=get_hover_template(genre))
        fig.update_yaxes(title_text='Pourcentage (%)')
        fig.update_layout(legend_title_text="Sous genre de "+genre)

        return fig