import pandas as pd
from dash import dcc, html, Input, Output
import plotly.express as px

# Chargement et prétraitement des données
file_path = "./dataset/spotify_songs_clean.csv"
data = pd.read_csv(file_path)

data["track_album_release_date"] = pd.to_datetime(data["track_album_release_date"], errors='coerce')
data["year"] = data["track_album_release_date"].dt.year
data["decade"] = (data["year"] // 10) * 10

# On sélectionne les artistes ayant des sorties sur au moins 3 décennies
div_pop_df = data.groupby("track_artist").agg(nb_decennie=("decade", "nunique"))\
                 .query("nb_decennie >= 3").reset_index()

# Liste des caractéristiques musicales à analyser
features = ["track_popularity", "danceability", "energy", "valence", "tempo"]

def generate_line_chart(selected_feature):
    # Filtrer les données pour ne garder que celles de 1970 et après
    data_filtered = data[data["year"] >= 1970]
    
    all_artists_data = data_filtered.groupby("year")[selected_feature].mean().reset_index()
    long_career_data = data_filtered[data_filtered["track_artist"].isin(div_pop_df["track_artist"])]\
                        .groupby("year")[selected_feature].mean().reset_index()

    all_artists_track_count = data_filtered.groupby("year").size().reset_index(name='track_count')
    long_career_track_count = data_filtered[data_filtered["track_artist"].isin(div_pop_df["track_artist"])]\
                              .groupby("year").size().reset_index(name='track_count')

    fig = px.line()
    fig.add_scatter(
        x=all_artists_data["year"], 
        y=all_artists_data[selected_feature], 
        mode='lines+markers', 
        name="Tous les artistes", 
        line=dict(color='blue'),
        text=all_artists_track_count['track_count']
    )
    fig.add_scatter(
        x=long_career_data["year"], 
        y=long_career_data[selected_feature], 
        mode='lines+markers', 
        name="Artistes (+3 décennies)", 
        line=dict(color='green'),
        text=long_career_track_count['track_count']
    )

    fig.update_traces(hovertemplate=(
        '<b>Année: </b>%{x}<br>' +
        '<b>Valeur moyenne: </b>%{y:.2f}<br>' +
        '<b>Nombre de morceaux: </b>%{text}<br>' +
        '<extra></extra>'
    ))
    if selected_feature == "energy":
        title = f"Évolution de l'{selected_feature} au cours du temps"
    elif selected_feature == "tempo":
        title = f"Évolution du {selected_feature} au cours du temps"
    else : 
        title = f"Évolution de la {selected_feature} au cours du temps"

    fig.update_layout(
    title=dict(text=title, font=dict(size=20, color='white')),
    xaxis_title="Année",
    yaxis_title=selected_feature,
    xaxis=dict(showgrid=True, title_font=dict(color='white'), tickfont=dict(color='white')),
    yaxis=dict(showgrid=True, title_font=dict(color='white'), tickfont=dict(color='white')),
    legend=dict(font=dict(color='white')),
    legend_title=dict(font=dict(color='white')),
    plot_bgcolor='#121212',
    paper_bgcolor='#121212',
    height=600,
)

    
    return fig

# Layout pour l'intégration dans app.py

narrative_q13 = html.Div(
    [
        dcc.Markdown("""  
        
        Il est possible d'intéresser à la différence entre les artistes possédant une longue carrière (plus de 30 ans !) et les autres.
        Cela permet d'observer si ces artistes suivent des tendances similaires au reste, c'est-à-dire s'ils s'adaptent à l'évolution des goûts musicaux. 

        *Qu'observe-t-on alors ? Les deux courbes se suivent presque systématiquement !*
        
        Cela suggère que les artistes avec une grande longévité arrivent à **adapter leur musique aux tendances** sans forcément changer complètement leur style.  
        On peut donc dire que la **longévité artistique** permet de rester populaire tout en gardant une certaine **cohérence musicale**.  

        Cette analyse complète les observations précédentes en montrant que **l’expérience** et la capacité à évoluer sont aussi des facteurs importants dans le succès musical.
        
        
        De légères différences sont remarquables cependant, comme pour la **valence** au milieu des années 2010, où les artistes avec une longue carrière semblent créer des musiques bien plus joyeuses que les autres.
        """)
    ],
    style={'padding': '20px', 'backgroundColor': '#121212', 'borderRadius': '8px'}
)

layout = html.Div([
    html.H2("Évolution des caractéristiques musicales des artistes", style={"textAlign": "center"}),
    narrative_q13,
    html.Label("Sélectionnez une caractéristique musicale:"),
    dcc.Dropdown(
        id='feature-dropdown-q13',
        options=[{'label': feature.capitalize(), 'value': feature} for feature in features],
        value='track_popularity',
        className='custom-dropdown'
    ),
    dcc.Graph(id='line_chart-q13')
])

# Enregistrement des callbacks pour q13
def register_callbacks(app):
    @app.callback(
        Output('line_chart-q13', 'figure'),
        [Input('feature-dropdown-q13', 'value')]
    )
    def update_chart(selected_feature):
        return generate_line_chart(selected_feature)
