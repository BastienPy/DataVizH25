import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import webbrowser

# remplacer avec path local
dataset_path = "./dataset/spotify_songs_clean.csv"

# carcteristiques audio
carac_audio = [
    "danceability", "energy", "key", "loudness", "mode", 
    "speechiness", "acousticness", "instrumentalness", "liveness", "valence"
]

# pre-process
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

# load dataset
df = preprocess_data()

# dash app init
app = dash.Dash(__name__)
server = app.server  


# App layout
app.layout = html.Div([
    html.H1("Évolution des caractéristiques audio et leur impact sur la popularité"),
    
    html.Label("Sélectionnez l'intervalle de temps :"),
    
    # choisir entre year et décennie
    dcc.RadioItems(
        id="time-interval",
        options=[
            {"label": "Décennie", "value": "decade"},
            {"label": "Année", "value": "year"}
        ],
        value="decade",  # par default
        inline=True
    ),
    
    # sélectionner la plage temporelle
    dcc.RangeSlider(
        id="year-slider",
        min=df["year"].min(),
        max=df["year"].max(),
        value=[2010, 2020],  # Default selection (2010-2020)
        marks={str(year): str(year) for year in range(df["year"].min(), df["year"].max()+1, 10)},  # Default: decades
        step=10  # Default to decade selection
    ),

    # Small multiples 
    html.Div(id="charts-container", style={"display": "grid", "grid-template-columns": "repeat(5, 1fr)", "gap": "20px"})
])

# update le slider selon l'option du button-radio
@app.callback(
    Output("year-slider", "step"),
    Output("year-slider", "marks"),
    Output("year-slider", "value"),
    [Input("time-interval", "value"),
     Input("year-slider", "value")]
)
def update_slider_mode(mode, current_range):
    # extract user's current selection
    start_year, end_year = current_range

    if mode == "year":
        step = 1  # step par année
        marks = {str(year): str(year) for year in range(df["year"].min(), df["year"].max()+1, 5)}  # marquer pour chaque 5 anées
        # ajuster l'interval sans reset
        value = [
            max(df["year"].min(), start_year), 
            min(df["year"].max(), end_year)
        ]
    else:  # decade
        step = 10  # step par décennie
        marks = {str(year): str(year) for year in range(df["year"].min(), df["year"].max()+1, 10)}  # Show every decade
        
        # Arroundir à la plus proche décennie
        value = [
            max(df["year"].min(), round(start_year / 10) * 10), 
            min(df["year"].max(), round(end_year // 10) * 10)
        ]

    return step, marks, value



# update les graph selon les plages tempo
@app.callback(
    Output("charts-container", "children"),
    [Input("year-slider", "value")]
)
def update_charts(selected_years):
    start_year, end_year = selected_years
    filtered_df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]

    charts = []
    
    for feature in carac_audio:
        filtered_df["fixed_size"] = 20 # adding a dummy colon to have a fixed size for bubbles
        
        fig = px.scatter(
            filtered_df, 
            x=feature,  # x-axis: carac audio
            y="track_popularity",  # y-axis: popularité
            size='fixed_size', 
            color="year",  # couleur pour l'année
            title=f"{feature.capitalize()} vs Popularité",
            labels={"track_popularity": "Popularité Moyenne", feature: feature.capitalize(), "year": "Année"},
        )
        fig.update_traces(
            marker=dict(opacity=0.7), # pour visualiser overlap points
            hovertemplate=(
                f"{feature.capitalize()}: %{{x:.6f}}<br>"
                "Popularité Moyenne: %{y:.5f}<br>" # 5 chiffre apres la virgule
                "Année: %{marker.color}" 
            )
        )
        fig.update_layout(
            title_x=0.5,  # titre au centre
            yaxis_title="Popularité", 
            xaxis_title=feature.capitalize(),
            height=320,
            showlegend=True  
        )
        charts.append(html.Div(dcc.Graph(figure=fig), style={"width": "100%", "textAlign": "center"}))
    
    return charts

# ouvrir l'appli 
if __name__ == '__main__':
    app.run_server(debug=True)