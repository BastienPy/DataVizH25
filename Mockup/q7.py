import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

def load_and_clean_data(filepath="./dataset/spotify_songs_clean.csv"):
    """Charge et nettoie les données du dataset Spotify."""
    df = pd.read_csv(filepath)
    df["track_album_release_date"] = pd.to_datetime(df["track_album_release_date"], errors='coerce')
    df = df[df["track_album_release_date"].notna() & df["track_album_release_date"].dt.month.notna()]
    df["year_month"] = df["track_album_release_date"].dt.to_period("M").astype(str)
    return df

def create_dashboard(df):
    """Crée l'application Dash pour visualiser l'influence de la date de sortie sur la popularité."""
    app = dash.Dash(__name__)
    
    app.layout = html.Div([
        html.H1("Influence de la date de sortie sur la popularité des musiques"),
        dcc.Graph(id="popularity-trend")
    ])

    @app.callback(
        Output("popularity-trend", "figure"),
        Input("popularity-trend", "id")
    )
    def update_graph(_):
        df_grouped = df.groupby("year_month")["track_popularity"].mean().reset_index()
        fig = px.line(df_grouped, x="year_month", y="track_popularity",
                      labels={"year_month": "Date de sortie (Année-Mois)", "track_popularity": "Popularité moyenne"},
                      title="Évolution de la popularité moyenne des musiques selon la date de sortie")
        return fig
    
    return app

if __name__ == "__main__":
    df = load_and_clean_data("./dataset/spotify_songs_clean.csv")
    app = create_dashboard(df)
    app.run_server(debug=True)
