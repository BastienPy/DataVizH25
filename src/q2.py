from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import numpy as np
import pandas as pd

# Load dataset
def get_dataframe(path):
    """Load and preprocess the Spotify dataset."""
    data = pd.read_csv(path)
    data["track_album_release_date"] = pd.to_datetime(data["track_album_release_date"])
    # data = data.groupby("playlist_genre").apply(lambda x: x.nlargest("track_popularity")).reset_index(drop=True)
    # excluded_artists = [
    #     "The Sleep Specialist", "Nature Sounds", "Natural Sound Makers", "Mother Nature Sound FX",
    #     "Rain Recordings", "Pinetree Way", "Aquagirl", "Rain Sounds FX", "Relax Meditate Sleep",
    #     "Life Sounds Nature"
    # ]
    # data = data[~data["track_artist"].isin(excluded_artists)]
    data = data[data["track_album_release_date"].dt.year >= 1970]
    return data

# Load data
data = get_dataframe("dataset/spotify_songs_clean.csv")

# Define matrix size
x_size = 10
y_size = 6

# Labels for axes (Inverted Y-axis)
y_labels = ["Pop", "Latin", "R&B", "Rap", "EDM", "Rock"][::-1]
x_labels = ["loudness", "energy", "acousticness", "valence", "danceability", 
            "tempo", "instrumentalness", "duration_ms", "speechiness", "liveness"]

# Default color mapping (white for 0, green for 1)
color_map = {0: "white", 1: "#008000"}  # Green for 1, white for 0

# Data matrix (Green = 1, White = 0)
arr = np.array([[1,1,1,1,1,1,0,0,0,0],
                [1,1,1,1,1,1,0,0,0,0],
                [1,1,1,1,1,1,0,0,0,0],
                [1,1,1,1,0,0,1,0,0,0],
                [1,1,1,1,1,1,1,1,0,1],
                [1,1,1,1,1,1,0,1,1,0]])[::-1].copy()

# Convert matrix values to colors
colors = np.vectorize(color_map.get)(arr)

def create_figure(colors):
    """Creates a new figure based on the color matrix."""
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
                'tickangle': -45,
                'color': 'white'  # Set x-axis labels color to white
            },
            'yaxis': {
                'showgrid': False,
                'zeroline': False,
                'tickmode': 'array',
                'tickvals': np.arange(y_size),
                'ticktext': y_labels,
                'color': 'white'  # Set y-axis labels color to white
            },
            'plot_bgcolor': '#121212',  # Set plot background color to black
            'paper_bgcolor': '#121212'  # Set paper background color to black
        }
    )

    # Add scatter points for each column
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

# Dash layout
layout = html.Div([
    html.H2("Corrélations internes au sein de chaque genre", style={'textAlign': 'center'}),

    dcc.Store(id="color-store", data=colors.tolist()),
    dcc.Store(id="selected-column", data=None),

    # Centered heatmap and bar chart side by side
    html.Div(
        style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'gap': '30px'},
        children=[
            dcc.Graph(
                id="music-matrix",
                figure=create_figure(colors),
                config={'staticPlot': False}
            )
            # dcc.Graph(id="bar-chart")
        ]
    ),

    # Centered legend
    html.Div([
        html.Div(style={'display': 'flex', 'alignItems': 'right'}, children=[
            html.Div(style={'width': '20px', 'height': '20px', 'backgroundColor': '#008000', 'marginRight': '10px'}),
            html.Span("Caractéristique importante")
        ]),

        html.Div(style={'display': 'flex', 'alignItems': 'right'}, children=[
            html.Div(style={'width': '20px', 'height': '20px', 'backgroundColor': '#90EE90', 'marginRight': '10px'}),
            html.Span("Caractéristique sélectionnée")
        ]),
        html.Div(style={'display': 'flex', 'alignItems': 'right'}, children=[
            html.Div(style={'width': '20px', 'height': '20px', 'backgroundColor': 'red', 'marginRight': '10px'}),
            html.Span("Corrélation négative")
        ]),
        html.Div(style={'display': 'flex', 'alignItems': 'right'}, children=[
            html.Div(style={'width': '20px', 'height': '20px', 'backgroundColor': 'yellow', 'marginRight': '10px'}),
            html.Span("Corrélation positive")
        ])
    ], style={'display': 'flex', 'justifyContent': 'center', 'gap': '20px', 'marginTop': '20px'})
])

def register_callbacks(app):
    @app.callback(
        Output("music-matrix", "figure"),
        #Output("bar-chart", "figure"),
        Input("music-matrix", "clickData"),
        State("color-store", "data"),
    )
    def update_on_click(clickData, stored_colors):
        """Changes clicked column to light green, and updates the bar chart."""
        stored_colors = np.array(stored_colors)  # Convert back to array

        if clickData is None:
            # return create_figure(stored_colors), go.Figure()  # No click, keep default
            return create_figure(stored_colors)
        # Get clicked point index
        point = clickData["points"][0]
        x = int(point["x"])  # Only track the column (x-axis)
        selected_characteristic = x_labels[x]

        # Make a temporary copy of colors for click effect
        temp_colors = stored_colors.copy()

        rock_idx = 0
        edm_idx = 1
        rap_idx = 2
        rb_idx = 3
        latin_idx = 4
        pop_idx = 5

        loudness_idx = x_labels.index("loudness")
        energy_idx = x_labels.index("energy")
        acousticness_idx = x_labels.index("acousticness")
        valence_idx = x_labels.index("valence")
        danceability_idx = x_labels.index("danceability")
        tempo_idx = x_labels.index("tempo")
        instrumentalness_idx = x_labels.index("instrumentalness")
        duration_idx = x_labels.index("duration_ms")
        speechiness_idx = x_labels.index("speechiness")
        liveness_idx = x_labels.index("liveness")

        correlations = {
            pop_idx: {
                (loudness_idx, energy_idx): 0.67,
                (acousticness_idx, energy_idx): -0.53,
                (acousticness_idx, loudness_idx): -0.36,
                (valence_idx, energy_idx): 0.36,
                (valence_idx, danceability_idx): 0.34,
                (valence_idx, loudness_idx): 0.28,
                (tempo_idx, danceability_idx): -0.24
            },
            rap_idx: {
                (loudness_idx, energy_idx): 0.69,
                (instrumentalness_idx, loudness_idx): -0.42,
                (instrumentalness_idx, energy_idx): -0.36,
                (valence_idx, energy_idx): 0.35,
                (instrumentalness_idx, acousticness_idx): 0.31,
                (acousticness_idx, energy_idx): -0.3,
                (acousticness_idx, loudness_idx): -0.26
            },
            rock_idx: {
                (loudness_idx, energy_idx): 0.76,
                (acousticness_idx, energy_idx): -0.62,
                (valence_idx, danceability_idx): 0.53,
                (acousticness_idx, loudness_idx): -0.49,
                (energy_idx, speechiness_idx): 0.29,
                (tempo_idx, danceability_idx): -0.25,
                (speechiness_idx, loudness_idx): 0.22,
                (duration_idx, valence_idx): -0.22,
                (tempo_idx, speechiness_idx): 0.21
            },
            latin_idx: {
                (loudness_idx, energy_idx): 0.7,
                (acousticness_idx, energy_idx): -0.45,
                (valence_idx, energy_idx): 0.4,
                (acousticness_idx, loudness_idx): -0.33,
                (valence_idx, danceability_idx): 0.32,
                (valence_idx, loudness_idx): 0.29,
                (tempo_idx, danceability_idx): -0.22
            },
            rb_idx: {
                (loudness_idx, energy_idx): 0.68,
                (acousticness_idx, energy_idx): -0.57,
                (valence_idx, energy_idx): 0.43,
                (valence_idx, danceability_idx): 0.42,
                (acousticness_idx, loudness_idx): -0.4,
                (acousticness_idx, danceability_idx): -0.37,
                (valence_idx, loudness_idx): 0.24,
                (energy_idx, danceability_idx): 0.23,
                (tempo_idx, acousticness_idx): -0.22,
                (loudness_idx, danceability_idx): 0.21
            },
            edm_idx: {
                (loudness_idx, energy_idx): 0.66,
                (acousticness_idx, energy_idx): -0.42,
                (valence_idx, danceability_idx): 0.38,
                (duration_idx, loudness_idx): -0.3,
                (duration_idx, instrumentalness_idx): 0.28,
                (acousticness_idx, loudness_idx): -0.25,
                (instrumentalness_idx, loudness_idx): -0.21,
                (tempo_idx, energy_idx): 0.19,
                (liveness_idx, energy_idx): 0.19,
                (loudness_idx, liveness_idx): 0.18
            }
        }

        def update_colors(selected_characteristic, temp_colors):
            selected_idx = x_labels.index(selected_characteristic)
            
            for genre, correlations_dict in correlations.items():
                for (feature1, feature2), value in correlations_dict.items():
                    if selected_idx in (feature1, feature2):
                        target_feature = feature2 if feature1 == selected_idx else feature1 
                        if temp_colors[genre, target_feature] != "white":
                            temp_colors[genre, target_feature] = "red" if value < 0 else "yellow"

        if selected_characteristic in x_labels:
            update_colors(selected_characteristic, temp_colors)

        # Change the entire column to light green (except white cases)
        for y in range(y_size):
            if temp_colors[y, x] != "white":
                temp_colors[y, x] = "#90EE90"  # Light green

        # return create_figure(temp_colors), fig
        return create_figure(temp_colors)