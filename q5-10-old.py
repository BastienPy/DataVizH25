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

def filter_popular_songs(df):
    """Filtre les chansons avec une popularité supérieure à 40 et applique un lissage."""
    popularity_threshold = 40
    features = ["danceability", "energy", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "loudness"]

    # Convertir 'year_month' en datetime pour le regroupement
    df["year_month"] = pd.to_datetime(df["year_month"])

    # Ajouter une colonne pour l'année
    df["year"] = df["year_month"].dt.year

    # Regrouper par périodes de 3 ans
    df["year_group"] = (df["year"] //3) * 3

    # Calculer la moyenne des caractéristiques pour chaque période de 3 ans
    df_popular = df[df["track_popularity"] > popularity_threshold].groupby(["year_group", "playlist_genre"])[features].mean().reset_index()

    # Convertir 'year_group' en datetime pour l'affichage
    df_popular["year_group"] = pd.to_datetime(df_popular["year_group"], format='%Y')

    return df_popular.sort_values("year_group")

def create_dashboard(df):
    """Crée l'application Dash pour afficher les courbes par caractéristique pour tous les genres."""
    app = dash.Dash(__name__)
    genres = sorted(df["playlist_genre"].unique())
    features = ["danceability", "energy", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "loudness"]

    # Palette de couleurs pour les graphiques
    color_palette = px.colors.qualitative.Plotly

    app.layout = html.Div([
        html.H1("Évolution des caractéristiques musicales par caractéristique pour tous les genres"),

        html.Label("Choisissez une caractéristique:"),
        dcc.Dropdown(
            id="feature-dropdown",
            options=[{"label": feature.capitalize(), "value": feature} for feature in features],
            value=features[0]
        ),

        html.Div([
            html.Div([dcc.Graph(id=f"genre-graph-{genre}") for genre in genres[i:i+3]], style={'display': 'flex'})
            for i in range(0, len(genres), 3)
        ])
    ])

    @app.callback(
        [Output(f"genre-graph-{genre}", "figure") for genre in genres],
        [Input("feature-dropdown", "value")]
    )
    def update_graph(selected_feature):
        # Filtrer les données par caractéristique
        df_popular = filter_popular_songs(df)

        # Calculer le nombre de chansons par période de 3 ans et genre
        song_counts = df.groupby(["year_group", "playlist_genre"]).size().reset_index(name='song_count')
        song_counts["year_group"] = pd.to_datetime(song_counts["year_group"], format='%Y')

        # Déterminer les limites de l'axe y
        y_min = df_popular[selected_feature].min()
        y_max = df_popular[selected_feature].max()

        graphs = []
        for idx, genre in enumerate(genres):
            df_popular_filtered = df_popular[df_popular["playlist_genre"] == genre]
            df_song_counts_filtered = song_counts[song_counts["playlist_genre"] == genre]

            fig = px.line(x=df_popular_filtered["year_group"], y=df_popular_filtered[selected_feature], labels={"x": "Année", "y": f"{selected_feature.capitalize()} Moyenne"},
                          title=f"Évolution de {selected_feature.capitalize()} pour {genre.capitalize()}"
            )
            fig.update_traces(hovertemplate='<b>%{x}</b><br>Moyenne: %{y}<br>Nombre de chansons: %{customdata[0]}',
                              line=dict(color=color_palette[idx % len(color_palette)]))  # Attribuer une couleur unique
            fig.update_xaxes(tickformat="%Y", nticks=10)
            fig.update_layout(height=400, width=600, yaxis_range=[y_min, y_max])  # Ajuste la taille des graphiques et fixe l'échelle y
            fig.update_traces(customdata=df_song_counts_filtered[['song_count']])

            graphs.append(fig)

        return graphs

    return app

if __name__ == "__main__":
    df = load_and_clean_data("./dataset/spotify_songs_clean.csv")
    app = create_dashboard(df)
    app.run_server(debug=True)
