import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go

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
    features = ["danceability", "energy", "speechiness", "liveness", "valence", "loudness"]

    df["year_month"] = pd.to_datetime(df["year_month"])
    df["year"] = df["year_month"].dt.year
    df["year_group"] = (df["year"] // 3) * 3
    
    df_popular = df[df["track_popularity"] > popularity_threshold].groupby(["year_group", "playlist_genre"])[features].mean().reset_index()
    df_popular["year_group"] = pd.to_datetime(df_popular["year_group"], format='%Y')
    return df_popular.sort_values("year_group")

def calculate_index(df_popular, base_year=1998):
    features = ["danceability", "energy", "speechiness", "liveness", "valence", "loudness"]
    base_values = df_popular[df_popular["year_group"].dt.year == base_year]
    for feature in features:
        for genre in df_popular["playlist_genre"].unique():
            base_value = base_values[base_values["playlist_genre"] == genre][feature].values[0]
            df_popular.loc[(df_popular["playlist_genre"] == genre), f"{feature}_index"] = df_popular[feature] / base_value * 100
    return df_popular

def create_dashboard(df):
    app = dash.Dash(__name__)
    features = ["danceability", "energy", "speechiness", "liveness", "valence", "loudness"]
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
        
        # Créer une figure avec subplots
        fig = make_subplots(
            rows=2, 
            cols=3,
            subplot_titles=[f"Évolution de l'index de {feature.capitalize()}" for feature in features],
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )
        
        # Ajouter les traces pour chaque feature et genre
        for i, feature in enumerate(features):
            row = (i // 3) + 1
            col = (i % 3) + 1
            
            for genre in df_popular_updated["playlist_genre"].unique():
                genre_df = df_popular_updated[df_popular_updated["playlist_genre"] == genre]
                
                fig.add_trace(
                    go.Scatter(
                        x=genre_df["year_group"],
                        y=genre_df[f"{feature}_index"],
                        name=genre,
                        legendgroup=genre,  # Même groupe pour toutes les traces du même genre
                        showlegend=True if i == 0 else False,  # Afficher la légende seulement pour le premier subplot
                        hovertemplate=f"<b>Genre:</b> {genre}<br><b>Index:</b> %{{y:.2f}}<extra></extra>",
                        line=dict(width=2)
                    ),
                    row=row,
                    col=col
                )
        
        # Mise en forme de la légende et du layout
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                title_text="Genres:"
            ),
            height=800,
            margin=dict(t=50, b=50),
            hovermode="x unified"
        )
        
        # Mise à jour des axes et titres
        for i in range(1, 7):
            fig.update_yaxes(title_text="Index", row=(i-1)//3 + 1, col=(i-1)%3 + 1)
            fig.update_xaxes(title_text="Année", row=(i-1)//3 + 1, col=(i-1)%3 + 1)
        
        return html.Div([
            dcc.Graph(
                figure=fig,
                style={'width': '100%', 'height': '800px'}
            )
        ])

    return app

if __name__ == "__main__":
    df = load_and_clean_data("./dataset/spotify_songs_clean.csv")
    app = create_dashboard(df)
    app.run_server(debug=True)