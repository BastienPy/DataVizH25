import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

def get_dataframe(path):
    data = pd.read_csv(path)
    data["track_album_release_date"] = pd.to_datetime(data["track_album_release_date"], format="mixed", errors="coerce")
    data = data[data["track_album_release_date"].dt.year >= 1970] # On ne garde que les musiques après 1970, car il n'y a pas assez d'échantillons avant
    return data


def get_figure(genre=None):
    data = get_dataframe("./dataset/spotify_songs_clean.csv")
    if genre:
        data = data[data['playlist_genre'] == genre]
    # Sélectionner uniquement les colonnes numériques
    numeric_data = data.select_dtypes(include=['number']).drop(columns=['key', 'track_popularity', 'mode'])
    # Calculer la matrice de corrélation
    corr_matrix = numeric_data.corr()
    corr_matrix = corr_matrix.applymap(lambda x: round(x, 2))  # Optional: round to 2 decimal places for readability
    corr_matrix = corr_matrix.clip(lower=-1, upper=1)  # Ensure the scale is between -1 and 1
    # Afficher la matrice avec plotly
    fig = px.imshow(corr_matrix,
                    text_auto=False,
                    aspect="auto",
                    title=f"Correlation Matrix for {genre}" if genre else "Correlation Matrix",
                    color_continuous_scale="Viridis",
                    zmin=-0.65,
                    zmax=0.8)
    fig.update_layout(width=800, height=600)
    return fig

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H4("Corrélation entre les caractéristiques audio", style={"fontWeight": "bold", "fontSize": "30px"}),
    dcc.Graph(id="graph", figure = get_figure()),
])

@app.callback(
    Output("scatter-plot", "figure"),
    [Input("graph", "clickData")]
)
def update_scatter_plot(clickData):
    if clickData is None:
        return dash.no_update
    
    data = get_dataframe("./dataset/spotify_songs_clean.csv")
    numeric_data = data.select_dtypes(include=['number'])
    corr_matrix = numeric_data.corr()

    x_feature = clickData['points'][0]['x']
    y_feature = clickData['points'][0]['y']

    if x_feature == y_feature:
        return dash.no_update

    scatter_fig = px.scatter(data, x=x_feature, y=y_feature, title=f"Scatter plot of {x_feature} vs {y_feature}")
    scatter_fig.update_layout(width=800, height=600)
    parallel_fig = px.parallel_coordinates(data, dimensions=[x_feature, y_feature], title=f"Parallel Coordinates of {x_feature} and {y_feature}")
    parallel_fig.update_layout(width=800, height=600)
    return scatter_fig

app.layout = html.Div([
    html.H4("Corrélation entre les caractéristiques audio", style={"fontWeight": "bold", "fontSize": "30px"}),
    html.Div([
        html.Button("All", id="all-button", n_clicks=0),
        html.Button("Pop", id="pop-button", n_clicks=0),
        html.Button("Rap", id="rap-button", n_clicks=0),
        html.Button("Rock", id="rock-button", n_clicks=0),
        html.Button("Latin", id="latin-button", n_clicks=0),
        html.Button("R&B", id="rnb-button", n_clicks=0),
        html.Button("EDM", id="edm-button", n_clicks=0),
    ], style={"display": "flex", "gap": "5px", "margin-bottom": "20px"}),
    html.Div([
        dcc.Graph(id="graph", figure=get_figure()),
        dcc.Graph(id="scatter-plot")
    ], style={"display": "flex"})
])

@app.callback(
    Output("graph", "figure"),
    [Input("all-button", "n_clicks"),
     Input("pop-button", "n_clicks"),
     Input("rap-button", "n_clicks"),
     Input("rock-button", "n_clicks"),
     Input("edm-button", "n_clicks"),
     Input("rnb-button", "n_clicks"),
     Input("latin-button", "n_clicks")]
)
def update_graph(all_clicks, pop_clicks, rock_clicks, hiphop_clicks, electronic_clicks, rnb_clicks, jazz_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        return get_figure()
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    genre = None
    if button_id == "pop-button":
        genre = "pop"
    elif button_id == "rap-button":
        genre = "rap"
    elif button_id == "rock-button":
        genre = "rock"
    elif button_id == "edm-button":
        genre = "edm"
    elif button_id == "rnb-button":
        genre = "r&b"
    elif button_id == "edm-button":
        genre = "edm"

    return get_figure(genre)


app.run_server(debug=False)