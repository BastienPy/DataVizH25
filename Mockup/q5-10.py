import pandas as pd 
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

df = pd.read_csv("./dataset/spotify_songs_clean.csv")

import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

df["year"] = pd.to_datetime(df["track_album_release_date"], errors='coerce').dt.year
df = df[df["year"] > 1970]
df["year"] = (df["year"] // 1) * 1

# Filtrer
df = df[df["track_popularity"] > 50]

# caract
features = ["danceability", "energy", "speechiness", "acousticness", "instrumentalness", "liveness", "valence"]

# Agréger par année et genre
df_grouped = df.groupby(["year", "playlist_genre"])[features].mean().reset_index()


# Appliquer une moyenne mobile sur 5 ans
df_grouped[features] = df_grouped.groupby("playlist_genre")[features].transform(lambda x: x.rolling(window=5, min_periods=1).mean())


app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Évolution des caractéristiques musicales par genre"),
    dcc.Graph(
        id="small-multiple",
        figure=px.line(
            df_grouped.melt(id_vars=["year", "playlist_genre"], var_name="Feature", value_name="Value"),
            x="year", y="Value", color="playlist_genre",
            facet_col="Feature", facet_col_wrap=3,
            title="Évolution des caractéristiques musicales moyennes par genre",
            labels={"year": "Année", "Value": "Valeur Moyenne", "playlist_genre": "Genre"},
            height=900
        ).update_xaxes(tickvals=df_grouped["year"].unique())
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)
