import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

def load_and_clean_data(filepath="./dataset/spotify_songs_clean.csv"):
    """Charge et nettoie les données du dataset Spotify."""
    df = pd.read_csv(filepath)
    df = preprocess_dates(df)
    return df

def preprocess_dates(df):
    """Convertit les dates et filtre les valeurs invalides."""
    df["track_album_release_date"] = pd.to_datetime(df["track_album_release_date"], errors='coerce')
    df = df[df["track_album_release_date"].notna() & (df["track_album_release_date"].dt.month.notna())]
    df["year_month"] = df["track_album_release_date"].dt.to_period('M')
    df = df[df["year_month"] > '2000-01']
    df["year_month"] = df["year_month"].astype(str)
    return df

def smooth_data(df, window=3):
    """Lisse les courbes en appliquant une moyenne mobile."""
    features = ["danceability", "energy", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "loudness"]
    df[features] = df[features].rolling(window=window, min_periods=3).mean()
    return df

def split_data(df, popularity_threshold):
    """Sépare les données en fonction du seuil de popularité et applique un lissage."""
    features = ["danceability", "energy", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "loudness"]
    df_low = df[df["track_popularity"] <= popularity_threshold].groupby(["year_month", "playlist_genre"])[features].mean().reset_index()
    df_high = df[df["track_popularity"] > popularity_threshold].groupby(["year_month", "playlist_genre"])[features].mean().reset_index()
    df_low["year_month"] = pd.to_datetime(df_low["year_month"])
    df_high["year_month"] = pd.to_datetime(df_high["year_month"])
    df_low = smooth_data(df_low)
    df_high = smooth_data(df_high)
    return df_low.sort_values("year_month"), df_high.sort_values("year_month")

def create_dashboard(df):
    """Crée l'application Dash pour afficher les courbes par genre et popularité."""
    app = dash.Dash(__name__)
    genres = sorted(df["playlist_genre"].unique())
    features = ["danceability", "energy", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "loudness"]

    app.layout = html.Div([
        html.H1("Évolution des caractéristiques musicales par genre et popularité"),

        html.Label("Choisissez un genre:"),
        dcc.Dropdown(
            id="genre-dropdown",
            options=[{"label": genre, "value": genre} for genre in genres],
            value=genres[0]
        ),

        html.Label("Choisissez un seuil de popularité:"),
        dcc.Slider(
            id="popularity-slider",
            min=0,
            max=100,
            step=1,
            value=40,
            marks={i: f"{i}" for i in range(0, 101, 10)},
            tooltip={"placement": "bottom", "always_visible": True}
        ),

        *[dcc.Graph(id=f"feature-graph-{feature}") for feature in features]
    ])

    @app.callback(
        [Output(f"feature-graph-{feature}", "figure") for feature in features],
        [Input("genre-dropdown", "value"),
         Input("popularity-slider", "value")]
    )
    def update_graph(selected_genre, popularity_threshold):
        # Filtrer les données par genre et popularité
        df_low, df_high = split_data(df, popularity_threshold)

        df_low_filtered = df_low[df_low["playlist_genre"] == selected_genre]
        df_high_filtered = df_high[df_high["playlist_genre"] == selected_genre]

        graphs = []
        for feature in features:
            fig = px.line(x=df_low_filtered["year_month"], y=df_low_filtered[feature],labels={"x": "Année", "y": f"{feature.capitalize()} Moyenne"},
                    title=f"Évolution de {feature.capitalize()}"
            )
            fig.add_scatter(x=df_high_filtered["year_month"], y=df_high_filtered[feature], mode='lines', name=f"Popularité > {popularity_threshold}")
            fig.add_scatter(x=df_low_filtered["year_month"], y=df_low_filtered[feature], mode='lines', name=f"Popularité <= {popularity_threshold}")
            
            fig.update_xaxes(tickformat="%Y", nticks=10)
            graphs.append(fig)

        return graphs

    return app

if __name__ == "__main__":
    df = load_and_clean_data("./dataset/spotify_songs_clean.csv")
    app = create_dashboard(df)
    app.run_server(debug=True)
