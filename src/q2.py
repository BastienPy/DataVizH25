from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import numpy as np
import pandas as pd

# Define matrix dimensions and labels.
x_size = 10
y_size = 6
y_labels = ["Pop", "Latin", "R&B", "Rap", "EDM", "Rock"][::-1]
x_labels = ["Loudness", "Energy", "Acousticness", "Valence", "Danceability", 
            "Tempo", "Instrumentalness", "Duration_ms", "Speechiness", "Liveness"]

# Default color mapping.
color_map = {0: "white", 1: "#008000"}
arr = np.array([[1,1,1,1,1,1,0,0,0,0],
                [1,1,1,1,1,1,0,0,0,0],
                [1,1,1,1,1,1,0,0,0,0],
                [1,1,1,1,0,0,1,0,0,0],
                [1,1,1,1,1,1,1,1,0,1],
                [1,1,1,1,1,1,0,1,1,0]])[::-1].copy()
colors = np.vectorize(color_map.get)(arr)

def create_figure(colors):
    fig = go.Figure(
        layout={
            'height': 500,
            'width': 700,
            'xaxis': {
                'showgrid': False,
                'zeroline': False,
                'tickmode': 'array',
                'tickvals': np.arange(x_size),
                'ticktext': x_labels,
                'tickangle': -45
            },
            'yaxis': {
                'showgrid': False,
                'zeroline': False,
                'tickmode': 'array',
                'tickvals': np.arange(y_size),
                'ticktext': y_labels
            },
            'plot_bgcolor': 'rgba(0,0,0,0)'
        }
    )
    for i in range(x_size):
        fig.add_scatter(
            x=np.ones(y_size) * i,
            y=np.arange(y_size),
            mode='markers',
            hoverinfo="none",
            marker={
                'symbol': 'square',
                'size': 40,
                'color': colors[:, i],
                'showscale': False
            },
            showlegend=False
        )
    return fig

# Export the layout.
layout = html.Div([
    html.H2("Music Genre vs Audio Features", style={'textAlign': 'center'}),
    dcc.Store(id="color-store", data=colors.tolist()),
    dcc.Store(id="selected-column", data=None),
    html.Div(
        dcc.Graph(
            id="music-matrix",
            figure=create_figure(colors),
            config={'staticPlot': False}
        ),
        style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}
    ),
    html.Div([
        html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
            html.Div(style={'width': '20px', 'height': '20px', 'backgroundColor': '#90EE90', 'marginRight': '10px'}),
            html.Span("Caractéristique sélectionnée")
        ]),
        html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
            html.Div(style={'width': '20px', 'height': '20px', 'backgroundColor': 'red', 'marginRight': '10px'}),
            html.Span("Corrélation négative")
        ]),
        html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
            html.Div(style={'width': '20px', 'height': '20px', 'backgroundColor': 'yellow', 'marginRight': '10px'}),
            html.Span("Corrélation positive")
        ])
    ], style={'display': 'flex', 'justifyContent': 'center', 'gap': '20px', 'marginTop': '20px'})
])

# (Optional) Functions for data manipulation in q2.
def get_dataframe(path):
    data = pd.read_csv(path)
    data["track_album_release_date"] = pd.to_datetime(data["track_album_release_date"])
    data = data.groupby("playlist_genre").apply(lambda x: x.nlargest(1000, "track_popularity")).reset_index(drop=True)
    excluded_artists = [
        "The Sleep Specialist", "Nature Sounds", "Natural Sound Makers", "Mother Nature Sound FX",
        "Rain Recordings", "Pinetree Way", "Aquagirl", "Rain Sounds FX", "Relax Meditate Sleep",
        "Life Sounds Nature"
    ]
    data = data[~data["track_artist"].isin(excluded_artists)]
    data = data[data["track_album_release_date"].dt.year >= 1970]
    return data

def calculate_average_instrumentalness(data):
    overall_avg = data["duration_ms"].mean()
    genre_avg = data.groupby("playlist_genre")["duration_ms"].mean()
    return overall_avg, genre_avg

# (For debugging or additional use.)
data = get_dataframe('dataset/spotify_songs_clean.csv')
a, b = calculate_average_instrumentalness(data)
print(a, b)

# Register callbacks with the main app.
def register_callbacks(app):
    @app.callback(
        Output("music-matrix", "figure"),
        Output("selected-column", "data"),
        Input("music-matrix", "clickData"),
        State("color-store", "data"),
        State("selected-column", "data")
    )
    def update_on_click(clickData, stored_colors, selected_column):
        stored_colors = np.array(stored_colors)
        if clickData is None:
            return create_figure(stored_colors), selected_column
        point = clickData["points"][0]
        x = int(point["x"])
        if selected_column == x:
            return create_figure(stored_colors), None
        temp_colors = stored_colors.copy()
        for y in range(y_size):
            if temp_colors[y, x] != "white":
                temp_colors[y, x] = "#90EE90"
        if x_labels[x] == "Instrumentalness":
            # Special color adjustments for the Instrumentalness column.
            rap_idx = 2
            edm_idx = 1
            acousticness_idx = x_labels.index("Acousticness")
            loudness_idx = x_labels.index("Loudness")
            energy_idx = x_labels.index("Energy")
            duration_ms_idx = x_labels.index("Duration_ms")
            if temp_colors[rap_idx, acousticness_idx] != "white":
                temp_colors[rap_idx, acousticness_idx] = "yellow"
            if temp_colors[rap_idx, loudness_idx] != "white":
                temp_colors[rap_idx, loudness_idx] = "red"
            if temp_colors[rap_idx, energy_idx] != "white":
                temp_colors[rap_idx, energy_idx] = "red"
            if temp_colors[edm_idx, loudness_idx] != "white":
                temp_colors[edm_idx, loudness_idx] = "red"
            if temp_colors[edm_idx, duration_ms_idx] != "white":
                temp_colors[edm_idx, duration_ms_idx] = "yellow"
        return create_figure(temp_colors), x
