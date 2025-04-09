import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def load_and_clean_data(filepath="./dataset/spotify_songs_clean.csv"):
    df = pd.read_csv(filepath)
    df = preprocess_dates(df)
    return df

def preprocess_dates(df):
    df["track_album_release_date"] = pd.to_datetime(df["track_album_release_date"], errors='coerce') #conversion en datetime
    df = df[df["track_album_release_date"].notna() & (df["track_album_release_date"].dt.month.notna())] 
    df["year_month"] = df["track_album_release_date"].dt.to_period('M')
    df = df[df["year_month"] > '2000-01'] #filtre pour ne garder que les dates après 2000
    df["year_month"] = df["year_month"].astype(str)
    return df

def filter_popular_songs(df):
    popularity_threshold = 50
    features = ["danceability", "energy", "speechiness", "liveness", "valence", "loudness"]

    df["year_month"] = pd.to_datetime(df["year_month"])
    df["year"] = df["year_month"].dt.year
    df["year_group"] = (df["year"] // 3) * 3
    
    df_popular = df[df["track_popularity"] > popularity_threshold].groupby(["year_group", "playlist_genre"])[features].mean().reset_index()
    df_popular["year_group"] = pd.to_datetime(df_popular["year_group"], format='%Y')
    return df_popular.sort_values("year_group")

def calculate_index(df_popular, base_year=1998):
    features = ["danceability", "energy", "speechiness", "liveness", "valence", "loudness"]
    base_values = df_popular[df_popular["year_group"].dt.year == base_year]
    for feature in features:
        for genre in df_popular["playlist_genre"].unique():
            base_value = base_values[base_values["playlist_genre"] == genre][feature].values[0]
            df_popular.loc[(df_popular["playlist_genre"] == genre), f"{feature}_index"] = (
                (df_popular[feature] / base_value) * 100
            )  # Start at 100% instead of 0%
    return df_popular

# data
df = load_and_clean_data("./dataset/spotify_songs_clean.csv")
df_popular = filter_popular_songs(df)
    
min_year = df_popular["year_group"].dt.year.min()
max_year = df_popular["year_group"].dt.year.max()

#layout
layout = html.Div([
    html.H1("Évolution des caractéristiques musicales pour tous les genres"),
    html.Div(
        dcc.Slider(
            id='base-year-slider',
            min=min_year,
            max=max_year,
            value=min_year,
            marks={str(year): str(year) for year in range(min_year, max_year + 1, 3)},
            step=3
        ),
        style={'width': '60%', 'margin': '0 auto'}  
    ),
        html.Div(
    [
        html.Label("Sélectionne un genre :", style={'color': 'white'}),
        dcc.RadioItems(
            id='genre-selector',
            options=[{'label': 'Tous', 'value': 'all'}] + [{'label': genre.capitalize(), 'value': genre} for genre in df_popular['playlist_genre'].unique()],
            value='all',  # Set "Tous" as the default selection
            labelStyle={'display': 'inline-block', 'margin-right': '10px', 'color': 'white'}
        )
    ],
    style={'textAlign': 'center', 'marginTop': '20px'}
),

    html.Div(id='graphs-container'),
])


def register_callbacks(app):
    analyses = {
    "tous" : "Sélectionnez un genre pour voir l'analyse.",
    "edm": "L'EDM a évolué vers une complexité émotionnelle et sonore. La baisse de la 'valence' traduit une préférence pour des ambiances plus mélancoliques, tandis que la chute de la 'speechiness' montre un éloignement des éléments vocaux au profit de l'instrumentation. L'augmentation de la 'liveness' suggère une intégration croissante d'enregistrements live, c'est le seul à avoir cette caractéristique en augmentation notable, et la baisse du 'loudness' reflète une recherche de subtilité sonore.",
    "latin": "Le genre latin a montré une évolution marquée vers des sonorités plus dynamiques et émotionnelles. La 'danceability', en constante augmentation, reflète une adaptation aux pistes de danse et une popularité croissante. L'énergie, également en hausse, traduit une intensité accrue dans les productions, tandis que la 'speechiness', en progression, indique une place importante des éléments vocaux dans ce genre. La 'valence', bien que légèrement en baisse, conserve des tonalités majoritairement positives, et la 'loudness', en baisse puis se stabilisant par la suite, montre son adaptation aux goûts actuels.",
    "pop": "La pop a évolué vers une production plus calibrée et émotionnellement diversifiée. La 'danceability' s’est maintenue à un niveau élevé, confirmant son orientation grand public et adaptée aux pistes de danse. L'énergie, bien qu'en légère baisse, reflète un équilibre entre intensité et accessibilité. La 'speechiness', en hausse, traduit une intégration croissante de paroles narratives ou chantées. La 'valence' en déclin révèle une transition vers des tonalités plus introspectives, tandis que la 'loudness' reste stable, témoignant d’une recherche de constance dans l’impact sonore.",
    "r&b": "Le R&B a vu une transformation notable depuis 1998 avec des fluctuations de la 'valence', traduisant une recherche de tonalités variées. L'augmentation de l' 'energy' avec une diminution de la 'loudness' montre une évolution vers des productions plus intenses mais moins bruyantes. L’augmentation modérée de la 'speechiness' reflète l’importance continue des paroles narratives dans ce style.",
    "rap": "Le rap a connu, depuis 1998, une stabilité de la 'speechiness', soulignant son ancrage dans le récit et les paroles dominantes. La baisse progressive de la 'valence' indique un virage vers des thèmes plus sérieux ou sombres. Malgré cela, la 'loudness' élevée combinée à une 'energy' en déclin traduit l’intensité caractéristique du genre, montrant que le rap conserve son impact sonore puissant tout en s’adaptant aux nouvelles tendances moins énergétiques.",
    "rock": "Depuis 1998, le rock a vu sa 'valence' diminuer progressivement, reflétant un virage vers des tonalités plus sombres ou introspectives. La 'loudness' ainsi que la 'danceability' restent relativement stables mais légèrement inférieures à ses sommets passés, suggérant un adoucissement global du genre. L'augmentation de la 'speechiness' pourrait indiquer un retour à des productions avec une plus grande présence d'éléments vocaux."
    }



    @app.callback(
        Output('graphs-container', 'children'),
        Input('base-year-slider', 'value'),
        Input('genre-selector', 'value')
    )
    def update_graphs(base_year, selected_genre):

        df_popular_updated = calculate_index(df_popular, base_year=base_year)
        features = ["danceability", "energy", "speechiness", "liveness", "valence", "loudness"]
        genres_couleurs = {
            "rock": "#FF0000",       # Rouge
            "latin": "#FFA500",      # Orange
            "edm": "#f542f5",        # Rose
            "rap": "#800080",        # Violet
            "r&b": "#008000",        # Vert
            "pop": "#ADD8E6"         # Bleu clair
        }
        
        feature_emojis = {
            "danceability": "💃",
            "energy": "⚡",
            "speechiness": "🗣️",
            "liveness": "🎤",
            "valence": "😊",
            "loudness": "🔊"
        }
        
        #subplots
        fig = make_subplots(
            rows=2, 
            cols=3,
            subplot_titles=[
                f"{feature_emojis[feature]} Évolution de l'index de {feature.capitalize()}" 
                for feature in features
            ],
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )
        
        #traces
        for i, feature in enumerate(features):
            row = (i // 3) + 1
            col = (i % 3) + 1
            
            for genre in df_popular_updated["playlist_genre"].unique():
                genre_df = df_popular_updated[df_popular_updated["playlist_genre"] == genre]
                
                opacity = 1.0 if selected_genre == 'all' or genre == selected_genre else 0.2

                fig.add_trace(
                    go.Scatter(
                        x=genre_df["year_group"],
                        y=genre_df[f"{feature}_index"],
                        name=genre,
                        legendgroup=genre,
                        showlegend=True if i == 0 else False,
                        hovertemplate=f"<b>Genre:</b> {genre}<br><b>Index:</b> %{{y:.2f}}<extra></extra>",
                        line=dict(width=2, color=genres_couleurs.get(genre, "#FFFFFF")),
                        opacity=opacity
                    ),
                    row=row,
                    col=col
                )

        
        
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                title_text="Genres:",
                font=dict(color="white") 
            ),
            height=800,
            margin=dict(t=50, b=50),
            hovermode="x unified",
            plot_bgcolor='#121212',  
            paper_bgcolor='#121212',  
            font=dict(color="white") 
        )
        
        for i, feature in enumerate(features):
            row = (i // 3) + 1
            col = (i % 3) + 1
            fig.update_yaxes(
                title_text=f"Index de {feature.capitalize()}", 
                title_font=dict(color="white"),  
                tickfont=dict(color="white"), 
                showgrid=False, 
                row=row, 
                col=col
            )
            fig.update_xaxes(
                title_text="Année", 
                title_font=dict(color="white"), 
                tickfont=dict(color="white"),  
                showgrid=False,  
                tickmode="array", 
                tickvals=df_popular_updated["year_group"].dt.year.unique(),  
                ticktext=[str(year) for year in df_popular_updated["year_group"].dt.year.unique()], 
                row=row, 
                col=col
            )
            
        return html.Div([dcc.Graph(figure=fig,style={'width': '100%', 'height': '800px'})])