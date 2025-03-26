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
    
    #for each genre
    grouped_df_genre = df.groupby(["year", "playlist_genre"])[["track_popularity"] + carac_audio].mean().reset_index()

    # print("grouped df")
    # print(grouped_df)
    # print("grouped df for genre")
    # print(grouped_df_genre )
    return grouped_df,grouped_df_genre

grouped_df,grouped_df_genre = preprocess_data()
# print(df)

def filter_df(year_range, genre):
    start_year, end_year = year_range
    if genre == 'all':
        return grouped_df[(grouped_df["year"] >= start_year) & (grouped_df["year"] <= end_year)]
    else:
        return grouped_df_genre[
            (grouped_df_genre["year"] >= start_year) &
            (grouped_df_genre["year"] <= end_year) &
            (grouped_df_genre["playlist_genre"] == genre)
        ]

# Export the layout as a variable.
layout = html.Div([
    html.H1("Évolution des caractéristiques audio et leur impact sur la popularité"),
    html.Label("Sélectionnez un genre :"),
    dcc.Dropdown(
        id='genre-dropdown',
        options=[{'label': 'Tous les genres', 'value': 'all'}] + [
            {'label': genre, 'value': genre} for genre in sorted(grouped_df_genre['playlist_genre'].dropna().unique())
        ],
        value='all',
        
        clearable=False,
        style={"color":"black","width": "30%", "margin-bottom": "10px"}
    ),
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
        min=grouped_df["year"].min(),
        max=grouped_df["year"].max(),
        value=[1970, 2020],
        marks={str(year): str(year) for year in range(grouped_df["year"].min(), grouped_df["year"].max()+1, 10)},
        step=10
    ),
    html.Div(id="charts-container", style={"display": "grid", "grid-template-columns": "repeat(3, 1fr)", "gap": "20px"})
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
            marks = {str(year): str(year) for year in range(grouped_df["year"].min(), grouped_df["year"].max()+1, 5)}
            value = [max(grouped_df["year"].min(), start_year), min(grouped_df["year"].max(), end_year)]
        else:  # decade
            step = 10
            marks = {str(year): str(year) for year in range(grouped_df["year"].min(), grouped_df["year"].max()+1, 10)}
            value = [max(grouped_df["year"].min(), round(start_year / 10) * 10), min(grouped_df["year"].max(), round(end_year / 10) * 10)]
        return step, marks, value

    @app.callback(
        Output("charts-container", "children"),
        [Input("year-slider", "value"),
        Input("genre-dropdown", "value")]
    )
    def update_charts(selected_years, selected_genre):
        start_year, end_year = selected_years
        filtered_df = filter_df([start_year, end_year], selected_genre)
        if selected_genre != "all":
            filtered_df = filtered_df[filtered_df["playlist_genre"] == selected_genre]
        charts = []
        total_features = len(carac_audio)
        for i, feature in enumerate(carac_audio):
            filtered_df = filtered_df.copy()
            filtered_df["fixed_size"] = 20  # adding a dummy column to have a fixed size for bubbles
            
            # getting index of last subchart in row
            show_colorbar = ((i + 1) % 3 == 0) or (i == len(carac_audio) - 1)
            
            fig = px.scatter(
                filtered_df, 
                x=feature,  
                y="track_popularity",  
                size='fixed_size', 
                color="year",
                color_continuous_scale="Viridis",
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
            #showing year color only once per row 
            if not show_colorbar:
                fig.update_coloraxes(showscale=False)
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
