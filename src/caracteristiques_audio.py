import dash
from dash import dcc, html, Input, Output

# Updated explanation structure with audio example names
explanations = {
    'danceability': {
        'description': "Danceability (dansant) décrit dans quelle mesure un morceau est adapté à la danse, en se basant sur des éléments comme le tempo, la stabilité du rythme, la force de la pulsation et la régularité globale. Une valeur de 0.0 signifie que le morceau est peu dansant, tandis que 1.0 indique un morceau très dansant.",
        'high_example_name': "Ice Ice Baby",
        'low_example_name': "Bridge Over Troubled Water"
    },
    'energy': {
        'description': "Energy (énergie) est une mesure de l'intensité et de l'activité ressenties dans un morceau, sur une échelle de 0.0 à 1.0. Des morceaux à haute énergie paraissent rapides, forts et parfois agressifs.",
        'high_example_name': "Harder Better Faster Stronger",
        'low_example_name': "Someone Like You"
    },
    'acousticness': {
        'description': "Acousticness (acousticité) est une mesure de confiance (de 0.0 à 1.0) indiquant si le morceau est acoustique. Une valeur de 1.0 signifie que le morceau est très probablement acoustique.",
        'high_example_name': "Blackbird",
        'low_example_name': "Sandstorm"
    },
    'instrumentalness': {
        'description': "Instrumentalness (instrumentalité) prédit l'absence de voix dans un morceau. Plus la valeur se rapproche de 1.0, plus le morceau est susceptible d'être instrumental.",
        'high_example_name': "Canon in D",
        'low_example_name': "Bohemian Rhapsody"
    },
    'liveness': {
        'description': "Liveness (en direct) détecte la présence d'un public dans l'enregistrement. Des valeurs élevées, notamment au-dessus de 0.8, suggèrent fortement que le morceau a été joué en live.",
        'high_example_name': "Hotel California (Live)",
        'low_example_name': "Blinding Lights"
    },
    'loudness': {
        'description': "Loudness (intensité) mesure l'intensité sonore globale d'un morceau en décibels (dB). Les valeurs, généralement comprises entre -60 et 0 dB, permettent de comparer le volume relatif des morceaux.",
        'high_example_name': "Smells Like Teen Spirit",
        'low_example_name': "Clair de Lune"
    },
    'speechiness': {
        'description': "Speechiness (le parlé) détecte la présence de paroles parlées dans un morceau. Des valeurs proches de 1.0 suggèrent un contenu fortement parlé (comme dans un podcast ou un spoken word), tandis que des valeurs faibles indiquent principalement de la musique.",
        'high_example_name': "TED Talk Sample",
        'low_example_name': "Instrumental Ambient"
    },
    'valence': {
        'description': "Valence mesure le caractère émotionnel positif ou négatif d'un morceau sur une échelle de 0.0 à 1.0. Des valeurs élevées indiquent un ton joyeux et positif, tandis que des valeurs faibles évoquent un ton plus triste ou mélancolique.",
        'high_example_name': "Happy",
        'low_example_name': "Mad World"
    },
    'tempo': {
        'description': "Tempo correspond à la vitesse du morceau, exprimée en battements par minute (BPM), et détermine le rythme global du morceau.",
        'high_example_name': "Don't Stop Me Now",
        'low_example_name': "Adagio for Strings"
    },
    'key': {
        'description': "Key (tonalité) indique la tonalité musicale du morceau, représentée par un nombre de 0 à 11, correspondant aux notes de la gamme chromatique.",
        'high_example_name': "Clair de Lune",
        'low_example_name': "Fur Elise"
    },
    'duration_ms': {
        'description': "Duration (durée) mesure la longueur du morceau en millisecondes.",
        'high_example_name': "Bohemian Rhapsody",
        'low_example_name': "Shortest Song Ever"
    },
}

layout = html.Div([
    html.Div(
        id='feature-tabs',
        children=[
            html.Span(feature.capitalize(), id={'type': 'feature-tab', 'index': feature}, n_clicks=0,
                      style={'marginRight': '15px', 'cursor': 'pointer'})
            for feature in explanations
        ],
        style={'marginBottom': '20px', 'color': '#1DB954', 'fontWeight': 'bold', 'fontSize': '16px'}
    ),
    html.Div(id='feature-explanation', style={
        'backgroundColor': '#1e1e1e',
        'padding': '15px',
        'borderRadius': '8px',
        'color': 'white',
        'fontSize': '16px',
        'lineHeight': '1.6'
    }, children="Click on a feature above to see the explanation."),
], style={'padding': '30px', 'backgroundColor': '#1e1e1e', 'minHeight': '100vh', 'fontFamily': 'Arial, sans-serif'})

def register_callbacks(app):
    @app.callback(
        Output('feature-explanation', 'children'),
        Output({'type': 'feature-tab', 'index': dash.dependencies.ALL}, 'style'),
        Input({'type': 'feature-tab', 'index': dash.dependencies.ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def update_feature(n_clicks_list):
        if not any(n_clicks_list):
            return dash.no_update

        selected_idx = n_clicks_list.index(max(n_clicks_list))
        selected_key = list(explanations.keys())[selected_idx]
        feature_data = explanations[selected_key]

        explanation_block = html.Div([
            html.P(html.B(selected_key.capitalize() + ":"), style={'marginBottom': '10px'}),
            html.P(feature_data['description']),
            html.Br(),
            html.P(html.B("High Example:"), style={'color': '#1DB954'}),
            html.P(feature_data['high_example_name']),
            html.Audio(src=f"/assets/audio/{selected_key}_high.mp3", controls=True,
                       style={'width': '100%', 'marginBottom': '20px'}),
            html.P(html.B("Low Example:"), style={'color': '#1DB954'}),
            html.P(feature_data['low_example_name']),
            html.Audio(src=f"/assets/audio/{selected_key}_low.mp3", controls=True, style={'width': '100%'})
        ])

        styles = []
        for i, key in enumerate(explanations.keys()):
            if i == selected_idx:
                styles.append({
                    'color': '#1e1e1e',
                    'backgroundColor': '#1DB954',
                    'padding': '3px 8px',
                    'borderRadius': '4px',
                    'marginRight': '15px',
                    'cursor': 'pointer'
                })
            else:
                styles.append({
                    'marginRight': '15px',
                    'cursor': 'pointer',
                    'color': '#1DB954'
                })

        return explanation_block, styles
