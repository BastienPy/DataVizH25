import pandas as pd
from dash import dcc, html, Input, Output
import plotly.express as px

# Path to dataset and audio features list.
dataset_path = "./dataset/spotify_songs_clean.csv"
carac_audio = [
    "danceability", "energy", "key", "loudness", "mode", 
    "speechiness", "acousticness", "instrumentalness", "liveness", "valence"
]

def preprocess_data():
    df = pd.read_csv(dataset_path)
    
    
    # release date -> datetime et extract year
    df["track_album_release_date"] = pd.to_datetime(df["track_album_release_date"], errors="coerce")
    df["year"] = df["track_album_release_date"].dt.year
    # print(df)
    
    
    # garder les données après 1970
    df = df[df["year"] >= 1970]
    # print(df)
    
    # moyenne de popularite par an pour chaque carcteristique audio
    grouped_df = df.groupby("year")[["track_popularity"] + carac_audio].mean().reset_index()
    #  print(grouped_df)
    return grouped_df

df = preprocess_data()

# Export the layout as a variable.
layout = html.Div([
    html.H1("Évolution des caractéristiques audio et leur impact sur la popularité"),
    html.Label("Sélectionnez l'intervalle de temps :"),
    dcc.RadioItems(
        id="time-interval",
        options=[
            {"label": "Décennie", "value": "decade"},
            {"label": "Année", "value": "year"}
        ],
        value="decade",
        inline=True
    ),
    dcc.RangeSlider(
        id="year-slider",
        min=df["year"].min(),
        max=df["year"].max(),
        value=[2010, 2020],
        marks={str(year): str(year) for year in range(df["year"].min(), df["year"].max()+1, 10)},
        step=10
    ),
    html.Div(id="charts-container", style={"display": "grid", "grid-template-columns": "repeat(3, 1fr)", "gap": "30px"})
])

# Register callbacks with the main app.
def register_callbacks(app):
    @app.callback(
        Output("year-slider", "step"),
        Output("year-slider", "marks"),
        Output("year-slider", "value"),
        [Input("time-interval", "value"),
         Input("year-slider", "value")]
    )
    def update_slider_mode(mode, current_range):
        start_year, end_year = current_range
        if mode == "year":
            step = 1
            marks = {str(year): str(year) for year in range(df["year"].min(), df["year"].max()+1, 5)}
            value = [max(df["year"].min(), start_year), min(df["year"].max(), end_year)]
        else:  # decade
            step = 10
            marks = {str(year): str(year) for year in range(df["year"].min(), df["year"].max()+1, 10)}
            value = [max(df["year"].min(), round(start_year / 10) * 10), min(df["year"].max(), round(end_year / 10) * 10)]
        return step, marks, value

    @app.callback(
        Output("charts-container", "children"),
        [Input("year-slider", "value")]
    )
    def update_charts(selected_years):
        start_year, end_year = selected_years
        filtered_df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]
        charts = []
        total_features = len(carac_audio)
        for i, feature in enumerate(carac_audio):
            filtered_df = df[(df["year"] >= start_year) & (df["year"] <= end_year)].copy()
            filtered_df["fixed_size"] = 20  # adding a dummy column to have a fixed size for bubbles
            
            fig = px.scatter(
                filtered_df, 
                x=feature,  
                y="track_popularity",  
                size='fixed_size', 
                color="year",
                color_continuous_scale="Viridis",  
                # color_continuous_scale=[
                #     [0.0, "#000000"],
                #     [0.1, "#121212"],
                #     [0.2, "#212121"],
                #     [0.4, "#535353"],
                #     [0.6, "#b3b3b3"],
                #     [0.8, "#70d97c"],
                #     [1.0, "#1db954"]
                # ],
                title=f"{feature.capitalize()} vs Popularité",
                labels={"track_popularity": "Popularité Moyenne", feature: feature.capitalize(), "year": "Année"},
            )
            fig.update_traces(
                marker=dict(opacity=0.7),
                hovertemplate=(
                    f"{feature.capitalize()}: %{{x:.6f}}<br>"
                    "Popularité Moyenne: %{y:.5f}<br>"
                    "Année: %{marker.color}"
                )
            )
            fig.update_layout(
                title_x=0.5,
                yaxis_title="Popularité", 
                xaxis_title=feature.capitalize(),
                height=350,
                showlegend=True  
            )
            # centering last row
            remaining = total_features % 3
            is_last = i == total_features - 1
            needs_centering = remaining == 1 and is_last
            style = {"width": "100%", "textAlign": "center"}
            if needs_centering:
                style["gridColumn"] = "2 / 3"  # center in the second column of 3
            charts.append(html.Div(dcc.Graph(figure=fig), style=style))

        return charts
