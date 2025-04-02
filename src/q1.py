import pandas as pd
from dash import dcc, html, Input, Output
import plotly.express as px
from dash import State
from dash import callback_context as ctx
from dash import ctx, no_update



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
    if genre == "all":
        return grouped_df[(grouped_df["year"] >= start_year) & (grouped_df["year"] <= end_year)]
    else:
        filtered = grouped_df_genre[(grouped_df_genre["playlist_genre"] == genre)]
        return filtered[(filtered["year"] >= start_year) & (filtered["year"] <= end_year)]

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
    # dcc.RadioItems(
    #     id="time-interval",
    #     options=[
    #         {"label": "Décennie", "value": "decade"},
    #         {"label": "Année", "value": "year"}
    #     ],
    #     value="decade",
    #     inline=True
    # ),
    dcc.RangeSlider(
        id="year-slider",
        min=grouped_df["year"].min(),
        max=grouped_df["year"].max(),
        value=[1970, 2020],
        marks={str(year): str(year) for year in range(grouped_df["year"].min(), grouped_df["year"].max()+1, 10)},
        step=10
    ),

                # Boutons centrés au-dessus du graphique
                html.Div([
                    html.Button("← Précédent", id="prev-button-q1", n_clicks=0, className='custom-button'),
                    html.Button("Suivant →", id="next-button-q1", n_clicks=0, className='custom-button'),
                    html.Div(id="page-indicator-q1", style={"padding": "0 20px", "color": "white"}),
                ], style={
                    'display': 'flex',
                    'justifyContent': 'center',
                    'gap': '20px',
                    'marginTop': '20px',
                    'marginBottom': '20px'
                }),
                            # Analyse à droite
            html.Div(
                id="analysis-text-q1",
                style={
                    # 'width': '800px',
                    'color': 'white',
                    'fontSize': '16px',
                    'marginTop': '20px',
                    'textAlign': 'center'
                },
                children="Pour certaines caractéristiques audio on remarque une très faible corrélation entre leur variations et celles de la popularité indiquant un rôle faible dans la popularité de la musique."
            ),
                
                
    html.Div(id="charts-container", style={"display": "grid", "grid-template-columns": "repeat(3, 1fr)", "gap": "20px"}),
    dcc.Store(id='story-page-q1', data=1),
    dcc.Store(id="features-store", data=carac_audio),

    
])

# Register callbacks with the main app.
def register_callbacks(app):
    @app.callback(
        Output("story-page-q1", "data"),
        Input("next-button-q1", "n_clicks"),
        Input("prev-button-q1", "n_clicks"),
        State("story-page-q1", "data"),
        prevent_initial_call=True
    )
    def update_story_page(n_next, n_prev, current):
        triggered = ctx.triggered_id
        if triggered == "next-button-q1":
            return 1 if current == 7 else current + 1
        elif triggered == "prev-button-q1":
            return 7 if current == 1 else current - 1
        return current

    @app.callback(
        Output("analysis-text-q1", "children"),
        Output("year-slider", "value"),
        Output("genre-dropdown", "value"),
        Output("page-indicator-q1", "children"),
        Output("features-store", "data"), 
        Input("story-page-q1", "data"),
    )
    def display_story(page):
        text = ""
        genre = "all"
        year_range = [1970, 2020]
        features = carac_audio.copy()

        if page == 1:
            text = "Pour certaines caractéristiques audio on remarque une très faible corrélation entre leur variations et celles de la popularité indiquant un rôle faible dans la popularité de la musique."
        elif page == 2:
            text = "Même pour un genre spécifique, on n’observe pas un impact important des caractéristique audio sur la popularité d’une musique. Vous pouvez aussi explorer les données pour un genre de votre choix en utilisant le filtre par genre."
            genre = "pop"
        elif page == 3:
            text = "Les musiques anciennes présentent un mode, valence et loudness faible."
            year_range = [1970, 2010]
        elif page == 4:
            text = "Les musique récentes présentent un mode, valence et loudness élevé"
            year_range = [2010, 2020]
        elif page == 5:
            text = "Nous pouvons ainsi conclure que les musiques récentes ont certaines caractéristiques audio différentes."
        elif page == 6:
            text = "Les caractéristiques exceptées key et liveness présentent des tendances et des évolutions notables au fil du temps"
            features = [f for f in carac_audio if f not in ["key", "liveness"]]
        elif page == 7:
            text = "Alors que les caractéristiques Key et Liveness reste relativement stable au fil du temps et donc intemporelles"
            features = ["key", "liveness"]

        return text, year_range, genre, f"{page}/7", features

    @app.callback(
        Output("charts-container", "children"),
        Input("year-slider", "value"),
        Input("genre-dropdown", "value"),
        Input("features-store", "data")
    )
    def update_charts(year_range, selected_genre, features):
        filtered_df = filter_df(year_range, selected_genre)
        charts = []
        for i, feature in enumerate(features):
            show_colorbar = ((i + 1) % 3 == 0) or (i == len(carac_audio) - 1)
            fig = px.scatter(
                filtered_df.copy(),
                x=feature,
                y="track_popularity",
                size=[20]*len(filtered_df),
                color="year",
                color_continuous_scale="Viridis",
                labels={"track_popularity": "Popularité Moyenne", feature: feature.capitalize(), "year": "Année"},
                title=f"{feature.capitalize()} vs Popularity"
            )
            fig.update_traces(
                marker=dict(opacity=0.95),
                hovertemplate=(
                    f"{feature.capitalize()}: %{{x:.6f}}<br>"
                    "Popularité Moyenne: %{y:.5f}<br>"
                    "Année: %{marker.color}"
                )
            )
            if not show_colorbar:
                fig.update_coloraxes(showscale=False)
            fig.update_layout(
                title_x=0.5, 
                yaxis_title="Popularity", 
                xaxis_title=feature.capitalize(),
                title_font_color='white',
                xaxis=dict(title_font=dict(color='white'), tickfont=dict(color='white')),
                yaxis=dict(title_font=dict(color='white'), tickfont=dict(color='white')),
                coloraxis_colorbar=dict(
                tickfont=dict(color='white'),
                title=dict(font=dict(color='white'))
                ),
                plot_bgcolor='#121212', 
                paper_bgcolor='#121212',
                height=350,
                showlegend=True  
                )
            
            
            charts.append(html.Div(dcc.Graph(figure=fig), style={"textAlign": "center"}))
        return charts






        

