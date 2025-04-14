import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import numpy as np
import pandas as pd

button_style = {
    'backgroundColor': '#222',
    'color': 'white',
    'border': '1px solid #555',
    'padding': '10px 20px',
    'fontSize': '16px',
    'borderRadius': '8px',
    'cursor': 'pointer',
    'transition': '0.3s',
    'boxShadow': '0 0 5px rgba(255,255,255,0.1)'
}


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
    dcc.Store(id="color-store", data=colors.tolist()),
    dcc.Store(id="selected-column", data=None),

    html.Div(  # Conteneur global
        style={'display': 'flex', 'justifyContent': 'center', 'gap': '10px'},
        children=[

            # Légende à gauche
            html.Div(
                style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'gap': '25px',
                    'color': 'white',
                    'marginTop': '200px'
                },
                children=[
                    html.Div([
                        html.Strong("Caractéristique", style={'marginBottom': '20px'}),
                        html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'}, children=[
                            html.Div(style={'width': '15px', 'height': '15px', 'backgroundColor': '#008000'}),
                            html.Span("Importante")
                        ]),
                        html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'}, children=[
                            html.Div(style={'width': '15px', 'height': '15px', 'backgroundColor': 'white'}),
                            html.Span("Insignifiante")
                        ])
                    ]),
                    html.Div([
                        html.Strong("Corrélation après sélection", style={'marginBottom': '40px'}),
                        html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'}, children=[
                            html.Div(style={'width': '15px', 'height': '15px', 'backgroundColor': '#90EE90'}),
                            html.Span("Caractéristique sélectionnée")
                        ]),
                        html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'}, children=[
                            html.Div(style={'width': '15px', 'height': '15px', 'backgroundColor': 'yellow'}),
                            html.Span("Corrélation positive")
                        ]),
                        html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'}, children=[
                            html.Div(style={'width': '15px', 'height': '15px', 'backgroundColor': 'red'}),
                            html.Span("Corrélation négative")
                        ])
                    ])
                ]
            ),

            # Colonne centrale (boutons + graphique)
            html.Div([
                # Boutons centrés au-dessus du graphique
                html.Div([
                    html.Button("← Précédent", id="prev-button", n_clicks=0, className='custom-button'),
                    html.Button("Suivant →", id="next-button", n_clicks=0, className='custom-button')
                ], style={
                    'display': 'flex',
                    'justifyContent': 'center',
                    'gap': '20px',
                    'marginBottom': '20px'
                }),

                # Graphique
                dcc.Graph(
                    id="music-matrix",
                    figure=create_figure(colors),   
                    config={'staticPlot': False}
                )
            ]),

            # Analyse à droite
            html.Div(
                id="analysis-text",
                style={
                    'width': '500px',
                    'color': 'white',
                    'fontSize': '16px',
                    'marginTop': '200px'
                },
                children="Les genres pop, latin et R&B partagent des caractéristiques communes, tandis que les autres genres se distinguent davantage par des particularités propres."
            )
        ]
    )
])


def register_callbacks(app):
    @app.callback(
        Output("music-matrix", "figure"),
        Output("selected-column", "data"),
        Output("analysis-text", "children"),
        Input("prev-button", "n_clicks"),
        Input("next-button", "n_clicks"),
        State("selected-column", "data"),
        State("color-store", "data")
    )
    def navigate_columns(prev_clicks, next_clicks, selected_column, stored_colors):
        stored_colors = np.array(stored_colors)

        all_columns = [None] + list(range(len(x_labels)))
        ctx = dash.callback_context
        button_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
        current_index = all_columns.index(selected_column)

        if button_id == "prev-button":
            new_index = (current_index - 1) % len(all_columns)
        elif button_id == "next-button":
            new_index = (current_index + 1) % len(all_columns)
        else:
            new_index = 0

        selected_column = all_columns[new_index]

        if selected_column is None:
            return create_figure(stored_colors), None, "La pop, latin et R&B partagent des caractéristiques communes, tandis que les autres genres se distinguent davantage par des particularités propres."

        selected_characteristic = x_labels[selected_column]
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

        update_colors(selected_characteristic, temp_colors)

        for y in range(y_size):
            if temp_colors[y, selected_column] != "white":
                temp_colors[y, selected_column] = "#90EE90"

        # Analyses par caractéristique
            analyses = {
                "loudness": "La loudness est un élément important pour tous les genres. Elle accompagne souvent l’énergie pour intensifier un morceau. Dans la Pop, le Latin ou le R&B, elle soutient des ambiances joyeuses, renforcées par une valence plus élevée. À l’inverse, la loudness s’atténue dans les morceaux plus acoustiques.",
                "energy": "L’énergie constitue une caractéristique clé, notamment dans la Pop, le Latin et le R&B, où elle va de pair avec une forte loudness. Elle est généralement opposée à l’acousticness, révélant un contraste entre sons produits et ambiances acoustiques.",
                "acousticness": "L’acousticness présente une corrélation négative avec l’énergie et le volume, traduisant une atmosphère plus douce et organique. Elle est peu présente dans les genres modernes et très produits comme l’EDM, la Pop ou le Rock.",
                "valence": "La valence, reflet de la positivité émotionnelle, est une variable influente dans tous les genres. Elle est souvent renforcée par l’énergie et la danceability, ce qui en fait un indicateur clé des morceaux joyeux et entraînants.",
                "danceability": "La danceability est largement valorisée dans la plupart des genres — sauf le Rap — pour générer une ambiance positive. En R&B, elle occupe une place centrale et dépend de multiples facteurs comme l’énergy ou la loudness, illustrant une richesse musicale.",
                "tempo": "Le tempo intervient comme un facteur structurant dans tous les styles, à l’exception du Rap. Un rythme trop rapide peut limiter la danceability dans certains genres (Pop, Latin, EDM), mais dans l’EDM, il soutient directement l’energy.",
                "instrumentalness": "L’instrumentalness se révèle importante dans l’EDM et le Rap, bien que de façon opposée : l’EDM favorise les sons artificiels puissants, tandis que le Rap alterne entre morceaux vocaux dominants et productions plus instrumentales.",
                "duration_ms": "La durée des morceaux joue un rôle secondaire, sauf en EDM et en Rock. Dans ces styles, des morceaux plus courts peuvent amplifier l’impact sonore et émotionnel, en accentuant la puissance ou la positivité du morceau.",
                "speechiness": "La speechiness est une dimension particulièrement marquée dans le Rock, où les passages parlés apportent intensité et énergie. Elle contribue à renforcer le lien avec l’auditeur.",
                "liveness": "L’EDM se distingue par sa liveness, suggérant une forte interaction avec le public. Cela renforce l’effet de loudness et d’énergy, en particulier lorsqu’une ambiance de concert est recréée à l’écoute."
            }

        analysis = analyses.get(selected_characteristic, "")

        return create_figure(temp_colors), selected_column, analysis
