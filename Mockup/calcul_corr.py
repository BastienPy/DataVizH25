import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np

def get_dataframe(path):
    data = pd.read_csv(path)
    data["track_album_release_date"] = pd.to_datetime(data["track_album_release_date"])
    data = data.groupby("playlist_genre").apply(lambda x: x.nlargest(1000, "track_popularity")).reset_index(drop=True)
    excluded_artists = [
        "The Sleep Specialist", "Nature Sounds", "Natural Sound Makers", "Mother Nature Sound FX",
        "Rain Recordings", "Pinetree Way", "Aquagirl", "Rain Sounds FX", "Relax Meditate Sleep",
        "Life Sounds Nature"
    ]
    data = data[~data["track_artist"].isin(excluded_artists)]
    data = data[data["track_album_release_date"].dt.year >= 1970]
    return data

def get_figure(genre=None):
    data = get_dataframe("./dataset/spotify_songs_clean.csv")
    if genre:
        data = data[data['playlist_genre'] == genre]
    numeric_data = data.select_dtypes(include=['number']).drop(columns=['key', 'track_popularity', 'mode'])
    corr_matrix = numeric_data.corr()
    corr_matrix = corr_matrix.applymap(lambda x: round(x, 2))
    
    # Masquer les valeurs inférieures à 0.1
    corr_matrix = corr_matrix.where(abs(corr_matrix) > 0.1, np.nan)
    
    fig = px.imshow(
        corr_matrix,
        aspect="auto",
        title=f"Correlation Matrix for {genre}" if genre else "Correlation Matrix",
        labels=dict(x="Features", y="Features", color="Correlation"),
        x=corr_matrix.columns,
        y=corr_matrix.index,
        zmin=-1,
        zmax=1
    )
    fig.update_layout(width=600, height=500)
    return fig

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H4("Corrélation entre les caractéristiques audio", style={"fontWeight": "bold", "fontSize": "30px"}),
    html.Div([
        dcc.Graph(id="graph-all", figure=get_figure()),
        dcc.Graph(id="graph-pop", figure=get_figure("pop")),
        dcc.Graph(id="graph-rap", figure=get_figure("rap")),
        dcc.Graph(id="graph-rock", figure=get_figure("rock")),
        dcc.Graph(id="graph-latin", figure=get_figure("latin")),
        dcc.Graph(id="graph-rnb", figure=get_figure("r&b")),
        dcc.Graph(id="graph-edm", figure=get_figure("edm")),
    ], style={"display": "flex", "flex-wrap": "wrap", "gap": "20px"}),
    dcc.Graph(id="scatter-plot")
])

@app.callback(
    Output("scatter-plot", "figure"),
    [Input("graph-all", "clickData"),
     Input("graph-pop", "clickData"),
     Input("graph-rap", "clickData"),
     Input("graph-rock", "clickData"),
     Input("graph-latin", "clickData"),
     Input("graph-rnb", "clickData"),
     Input("graph-edm", "clickData")]
)
def update_scatter_plot(all_clickData, pop_clickData, rap_clickData, rock_clickData, latin_clickData, rnb_clickData, edm_clickData):
    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update
    
    click_data = ctx.triggered[0]['value']
    
    if click_data is None:
        return dash.no_update
    
    x_feature = click_data['points'][0]['x']
    y_feature = click_data['points'][0]['y']

    if x_feature == y_feature:
        return dash.no_update

    data = get_dataframe("./dataset/spotify_songs_clean.csv")
    
    scatter_fig = px.scatter(data, x=x_feature, y=y_feature, title=f"Scatter plot of {x_feature} vs {y_feature}")
    scatter_fig.update_layout(width=800, height=600)
    
    return scatter_fig

if __name__ == '__main__':
    app.run_server(debug=True)