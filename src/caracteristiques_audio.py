import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Dictionnaire des explications pour chaque caractéristique audio.
explanations = {
    'danceability': "Danceability (dansant) décrit dans quelle mesure un morceau est adapté à la danse, en se basant sur des éléments comme le tempo, la stabilité du rythme, la force de la pulsation et la régularité globale. Une valeur de 0.0 signifie que le morceau est peu dansant, tandis que 1.0 indique un morceau très dansant.",
    'energy': "Energy (énergie) est une mesure de l'intensité et de l'activité ressenties dans un morceau, sur une échelle de 0.0 à 1.0. Des morceaux à haute énergie paraissent rapides, forts et parfois agressifs.",
    'key': "Key (clef) correspond à la tonalité estimée du morceau. Les entiers représentent les notes selon la notation standard (ex : 0 = C, 1 = C♯/D♭, 2 = D, etc.). Si aucune tonalité n’est détectée, la valeur est -1.",
    'loudness': "Loudness (intensité) mesure l'intensité sonore globale d'un morceau en décibels (dB). Les valeurs, généralement comprises entre -60 et 0 dB, permettent de comparer le volume relatif des morceaux.",
    'mode': "Mode (tonalité) indique si le morceau est en tonalité majeure (1) ou mineure (0), ce qui influence la perception émotionnelle de la musique.",
    'speechiness': "Speechiness (le parlé) détecte la présence de paroles parlées dans un morceau. Des valeurs proches de 1.0 suggèrent un contenu fortement parlé (comme dans un podcast ou un spoken word), tandis que des valeurs faibles indiquent principalement de la musique.",
    'acousticness': "Acousticness (acousticité) est une mesure de confiance (de 0.0 à 1.0) indiquant si le morceau est acoustique. Une valeur de 1.0 signifie que le morceau est très probablement acoustique.",
    'instrumentalness': "Instrumentalness (instrumentalité) prédit l'absence de voix dans un morceau. Plus la valeur se rapproche de 1.0, plus le morceau est susceptible d'être instrumental.",
    'liveness': "Liveness (en direct) détecte la présence d'un public dans l'enregistrement. Des valeurs élevées, notamment au-dessus de 0.8, suggèrent fortement que le morceau a été joué en live.",
    'valence': "Valence mesure le caractère émotionnel positif ou négatif d'un morceau sur une échelle de 0.0 à 1.0. Des valeurs élevées indiquent un ton joyeux et positif, tandis que des valeurs faibles évoquent un ton plus triste ou mélancolique.",
    'tempo': "Tempo correspond à la vitesse du morceau, exprimée en battements par minute (BPM), et détermine le rythme global du morceau.",
    'duration_ms': "Duration_ms (durée en ms) indique la durée du morceau en millisecondes."
}

# Création de la liste d'options pour le menu déroulant.
options = [{'label': feature.capitalize(), 'value': feature} for feature in explanations.keys()]

# Définition de la mise en page pour la page "Caractéristiques Audio".
layout = html.Div([
    html.H1("Caractéristiques Audio", style={'color': '#1DB954'}),
    dcc.Dropdown(
        id='audio-feature-dropdown',
        options=options,
        placeholder="Choisissez une caractéristique audio",
        style={'width': '50%', 'margin': '20px 0'},
        className='custom-dropdown'
    ),
    html.Div(
        id='audio-feature-explanation',
        style={'marginTop': '20px'}
    )
], style={'padding': '20px'})

# Callback pour mettre à jour l'explication en fonction de la sélection.
def register_callbacks(app):
    @app.callback(
        Output('audio-feature-explanation', 'children'),
        Input('audio-feature-dropdown', 'value')
    )
    def update_explanation(selected_feature):
        if selected_feature is None:
            return "Veuillez sélectionner une caractéristique pour obtenir son explication."
        return explanations.get(selected_feature, "Caractéristique inconnue.")
