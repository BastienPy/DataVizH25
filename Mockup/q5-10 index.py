import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

def load_and_clean_data(filepath="./dataset/spotify_songs_clean.csv"):
    df = pd.read_csv(filepath)
    df = preprocess_dates(df)
    return df

def preprocess_dates(df):
    df["track_album_release_date"] = pd.to_datetime(df["track_album_release_date"], errors='coerce')
    df = df[df["track_album_release_date"].notna() & (df["track_album_release_date"].dt.month.notna())]
    df["year_month"] = df["track_album_release_date"].dt.to_period('M')
    df = df[df["year_month"] > '2000-01']
    df["year_month"] = df["year_month"].astype(str)
    return df

def filter_popular_songs(df):
    popularity_threshold = 50
    features = ["danceability", "energy", "speechiness",   "liveness", "valence", "loudness"]

    df["year_month"] = pd.to_datetime(df["year_month"])
    df["year"] = df["year_month"].dt.year
    df["year_group"] = (df["year"] // 3) * 3
    
    df_popular = df[df["track_popularity"] > popularity_threshold].groupby(["year_group", "playlist_genre"])[features].mean().reset_index()
    df_popular["year_group"] = pd.to_datetime(df_popular["year_group"], format='%Y')
    return df_popular.sort_values("year_group")

def calculate_index(df_popular, base_year=1998):
    features = ["danceability", "energy", "speechiness",   "liveness", "valence", "loudness"]
    base_values = df_popular[df_popular["year_group"].dt.year == base_year]
    for feature in features:
        for genre in df_popular["playlist_genre"].unique():
            base_value = base_values[base_values["playlist_genre"] == genre][feature].values[0]
            df_popular.loc[(df_popular["playlist_genre"] == genre), f"{feature}_index"] = df_popular[feature] / base_value * 100
    return df_popular

def create_dashboard(df):
    app = dash.Dash(__name__)
    features = ["danceability", "energy", "speechiness",   "liveness", "valence", "loudness"]
    df_popular = filter_popular_songs(df)
    
    min_year = df_popular["year_group"].dt.year.min()
    max_year = df_popular["year_group"].dt.year.max()

    app.layout = html.Div([
        html.H1("Évolution des caractéristiques musicales pour tous les genres"),
        dcc.Slider(
            id='base-year-slider',
            min=min_year,
            max=max_year,
            value=min_year,
            marks={str(year): str(year) for year in range(min_year, max_year + 1, 3)},
            step=3
        ),
        html.Div(id='graphs-container')
    ])

    @app.callback(
        Output('graphs-container', 'children'),
        Input('base-year-slider', 'value')
    )
    def update_graphs(base_year):
        df_popular_updated = calculate_index(df_popular, base_year=base_year)
        return [
            dcc.Graph(
                figure=px.line(df_popular_updated, x="year_group", y=f"{feature}_index", color="playlist_genre",
                               labels={"year_group": "Année", f"{feature}_index": f"Index de {feature.capitalize()}"},
                               title=f"Évolution de l'index de {feature.capitalize()} pour tous les genres"
                               ),
                style={"width": "48%", "display": "inline-block"}
                
                
            ) for feature in features
        ]

    return app

if __name__ == "__main__":
    df = load_and_clean_data("./dataset/spotify_songs_clean.csv")
    app = create_dashboard(df)
    app.run_server(debug=True)