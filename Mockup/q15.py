import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
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
    fig = px.area(
        genre_data,
        x="decennie",
        y="percentage",
        color="playlist_genre",
        line_group="playlist_genre",
        hover_data=["playlist_genre"],
        custom_data=["playlist_genre"]  # Include custom_data here
    )

    fig.update_layout(height=500)
    fig.update_traces(hovertemplate=get_hover_template("Genre"))
    fig.update_yaxes(title_text='Pourcentage (%)')
    fig.update_layout(legend_title_text="Genre")

    return fig


app = dash.Dash(__name__)

# Add the new graph to the layout
app.layout = html.Div([
    dcc.Store(id='selected_genre', storage_type='memory'),
    html.H4("Évolution de la proportion de genres et sous-genres musicaux par décennie", style={"fontWeight": "bold", "fontSize": "30px"}),
    html.H4("Évolution de la proportion des genres", style={"fontWeight": "bold", "fontSize": "20px"}),
    dcc.Graph(id="graph", figure=get_figure_genre()),
    html.H4("Évolution de la proportion des sous genres du genre choisi", style={"fontWeight": "bold", "fontSize": "20px"}),
    dcc.Graph(id="subgenre_graph"),
    html.H4("Proportion des sous-genres parmi les artistes populaires", style={"fontWeight": "bold", "fontSize": "20px"}),
    dcc.Graph(id="popular_artist_graph"),
])

@app.callback(
    Output('selected_genre', 'data'),
    Input('graph', 'clickData')
)
def update_selected_genre(clickData):
    if clickData is None:
        return None
    return clickData["points"][0]["customdata"][0]

@app.callback(
    Output('subgenre_graph', 'figure'),
    Input('selected_genre', 'data')
)
def display_area(selected_genre):
    if selected_genre is None:
        fig = px.area()
        fig.add_annotation(dict(xref="paper", yref="paper", x=0.5, y=0.5),
                           text="Aucune donnée pour le moment, cliquez sur une des lignes.",
                           showarrow=False)
        return fig

    genre_data = data_preprocess("./dataset/spotify_songs_clean.csv", selected_genre)
    fig = px.area(
        genre_data,
        x="decennie",
        y="percentage",
        color="playlist_subgenre",
        line_group="playlist_subgenre",
        hover_data=["playlist_subgenre"],
        custom_data=["playlist_subgenre"]  # Include custom_data here
    )
    fig.update_traces(hovertemplate=get_hover_template(selected_genre))
    fig.update_yaxes(title_text='Pourcentage (%)')
    fig.update_layout(legend_title_text="Sous genre de " + selected_genre)
    return fig

def data_preprocess_popular_artists(path, genre, popularity_threshold=90):
    data = get_dataframe(path)
    data = data[data["playlist_genre"] == genre]  # Filter by genre
    data["year"] = data["track_album_release_date"].dt.year
    data["decennie"] = (data["year"] // 10) * 10

    # Filter popular artists
    popular_data = data[data["track_popularity"] >= popularity_threshold]
    popular_data = popular_data.groupby(["decennie", "playlist_subgenre"]).size().reset_index(name="count")

    # Normalize
    nb_songs_by_decade = popular_data.groupby("decennie")["count"].sum()
    popular_data["percentage"] = popular_data["count"] / popular_data["decennie"].map(nb_songs_by_decade) * 100

    return popular_data


def get_figure_popular_artists(selected_genre):
    if selected_genre is None:
        fig = px.area()
        fig.add_annotation(dict(xref="paper", yref="paper", x=0.5, y=0.5),
                           text="Aucune donnée pour le moment, cliquez sur une des lignes.",
                           showarrow=False)
        return fig

    genre_data = data_preprocess("./dataset/spotify_songs_clean.csv", selected_genre)
    popular_data = data_preprocess_popular_artists("./dataset/spotify_songs_clean.csv", selected_genre)

    fig = px.area(
        genre_data,
        x="decennie",
        y="percentage",
        color="playlist_subgenre",
        line_group="playlist_subgenre",
        hover_data=["playlist_subgenre"],
        custom_data=["playlist_subgenre"]
    )

    fig.add_traces(
        px.line(
            popular_data,
            x="decennie",
            y="percentage",
            color="playlist_subgenre",
            line_dash_sequence=["dot"],  # Dashed lines for popular artists
        ).data
    )

    fig.update_traces(hovertemplate=get_hover_template(selected_genre))
    fig.update_yaxes(title_text='Pourcentage (%)')
    fig.update_layout(legend_title_text="Sous genre de " + selected_genre)
    return fig

@app.callback(
    Output('popular_artist_graph', 'figure'),
    Input('selected_genre', 'data')
)
def display_popular_artists(selected_genre):
    return get_figure_popular_artists(selected_genre)



app.run_server(debug=False)