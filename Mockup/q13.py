import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

file_path = "./dataset/spotify_songs_clean.csv"
data = pd.read_csv(file_path)

data["track_album_release_date"] = pd.to_datetime(data["track_album_release_date"], errors='coerce')
data["year"] = data["track_album_release_date"].dt.year
data["decade"] = (data["year"] // 10) * 10

div_pop_df = data.groupby("track_artist").agg(nb_decennie=("decade", "nunique")).query("nb_decennie >= 3").reset_index()

features = ["track_popularity", "danceability", "energy", "valence", "tempo"]

def generate_line_chart(selected_feature):
    # Filtrer les données pour ne conserver que celles dont l'année est >= 1970
    data_filtered = data[data["year"] >= 1970]
    
    all_artists_data = data_filtered.groupby("year")[selected_feature].mean().reset_index()
    long_career_data = data_filtered[data_filtered["track_artist"].isin(div_pop_df["track_artist"])].groupby("year")[selected_feature].mean().reset_index()

    all_artists_track_count = data_filtered.groupby("year").size().reset_index(name='track_count')
    long_career_track_count = data_filtered[data_filtered["track_artist"].isin(div_pop_df["track_artist"])].groupby("year").size().reset_index(name='track_count')

    fig = px.line()
    fig.add_scatter(x=all_artists_data["year"], y=all_artists_data[selected_feature], mode='lines+markers', 
                    name="Tous les artistes", line=dict(color='blue'), 
                    text=all_artists_track_count['track_count'])  
    fig.add_scatter(x=long_career_data["year"], y=long_career_data[selected_feature], mode='lines+markers', 
                    name="Artistes (+3 décennies)", line=dict(color='green'),
                    text=long_career_track_count['track_count'])  

    fig.update_traces(hovertemplate=(
        '<b>Année: </b>%{x}<br>' +
        '<b>Valeur moyenne: </b>%{y:.2f}<br>' +  
        '<b>Nombre de morceaux: </b>%{text}<br>' +   
        '<extra></extra>'
    ))

    fig.update_layout(title=f"Évolution de {selected_feature} au fil du temps (après 1970)",
                      xaxis_title="Année",
                      yaxis_title=selected_feature,
                      template="plotly_white")
    
    return fig

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("Évolution des caractéristiques musicales des artistes", style={"textAlign": "center"}),
    
    html.Label("Sélectionnez une caractéristique musicale:"),
    dcc.Dropdown(
        id='feature-dropdown',
        options=[{'label': feature.capitalize(), 'value': feature} for feature in features],
        value='track_popularity',
        clearable=False
    ),
    
    dcc.Graph(id='line_chart')
])


@app.callback(
    Output('line_chart', 'figure'),
    [Input('feature-dropdown', 'value')]
)
def update_chart(selected_feature):
    return generate_line_chart(selected_feature)

if __name__ == '__main__':
    app.run_server(debug=True)
