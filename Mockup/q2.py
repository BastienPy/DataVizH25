import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np
import plotly.colors as pc

def get_dataframe(path):
    data = pd.read_csv(path)
    data["track_album_release_date"] = pd.to_datetime(data["track_album_release_date"])
    data = data.groupby("playlist_genre").apply(lambda x: x.nlargest(500, "track_popularity")).reset_index(drop=True)
    excluded_artists = [
        "The Sleep Specialist", "Nature Sounds", "Natural Sound Makers", "Mother Nature Sound FX",
        "Rain Recordings", "Pinetree Way", "Aquagirl", "Rain Sounds FX", "Relax Meditate Sleep",
        "Life Sounds Nature"
    ]
    data = data[~data["track_artist"].isin(excluded_artists)]
    data = data[data["track_album_release_date"].dt.year >= 1970]
    return data

def get_figure():
    data = get_dataframe("./dataset/spotify_songs_clean.csv")
    numeric_data = data.select_dtypes(include=['number']).drop(columns=['key', 'track_popularity', 'mode'])
    corr_matrix = numeric_data.corr()
    corr_matrix[:] = 0  
    mask = np.triu(np.ones(corr_matrix.shape), k=0)
    masked_corr_matrix = corr_matrix.where(mask == 0, np.nan)
    masked_corr_matrix = masked_corr_matrix.iloc[1:, :-1]  
    norm_values = np.zeros(masked_corr_matrix.shape)
    custom_colorscale = [
        [0.0, "lightgray"],
        [0.1, "darkblue"],
        [0.2, "purple"],
        [0.4, "red"],
        [0.6, "cyan"],
        [0.8, "orange"],
        [1.0, "green"]
    ]
    color_mappings = {
        1.0: [("loudness", "energy"), ("acousticness", "energy"), ("acousticness", "loudness"), 
              ("valence", "danceability"), ("valence", "energy")],
        0.8: [("instrumentalness", "energy"), ("instrumentalness", "loudness"), ("instrumentalness", "acousticness")],
        0.6: [("speechiness", "energy"), ("speechiness", "loudness"), ("tempo", "speechiness")],
        0.4: [("valence", "loudness")],
        0.2: [("energy", "danceability"), ("loudness", "danceability"), ("valence", "acousticness")],
        0.1: [("duration_ms", "instrumentalness"), ("duration_ms", "loudness"), 
              ("liveness", "energy"), ("liveness", "loudness"), ("tempo", "energy")]
    }
    for value, label_pairs in color_mappings.items():
        for row_label, col_label in label_pairs:
            if row_label in masked_corr_matrix.index and col_label in masked_corr_matrix.columns:
                row_idx = masked_corr_matrix.index.get_loc(row_label)
                col_idx = masked_corr_matrix.columns.get_loc(col_label)
                norm_values[row_idx, col_idx] = value  
    norm_values = np.where(np.tril(np.ones(norm_values.shape)), norm_values, np.nan)
    fig = px.imshow(norm_values,
                    aspect="auto",
                    title=f"Corrélations importantes",
                    labels=dict(x="", y=""),
                    x=masked_corr_matrix.columns,
                    y=masked_corr_matrix.index,
                    color_continuous_scale=custom_colorscale
                    )
    fig.update_traces(z=norm_values, colorscale=custom_colorscale)
    fig.update_coloraxes(showscale=False)
    legend_items = [
        ("All Genres", "green"),
        ("EDM", "darkblue"),
        ("Latin", "red"),   
        ("R&B", "purple"),
        ("Rap", "orange"),
        ("Rock", "cyan"),
        ("No Correlation", "lightgray")
    ]
    annotations = []
    shapes = []
    x_offset = 1.05
    y_offset = 1.2
    spacing = -0.08
    box_size = 0.05
    for i, (label, color) in enumerate(legend_items):
        shapes.append(
            dict(
                type="rect",
                x0=x_offset - box_size + 0.07, y0=y_offset + i * spacing - box_size / 2 - 0.04,
                x1=x_offset + 0.07, y1=y_offset + i * spacing + box_size / 2 - 0.04,
                xref="paper", yref="paper",
                fillcolor=color,
                line=dict(width=0)
            )
        )
        annotations.append(
            dict(
                x=x_offset, y=y_offset + i * spacing,
                xref="paper", yref="paper",
                text=f"<b>{label}</b>",
                showarrow=False,
                font=dict(size=14, color="black"),
                align="left"
            )
        )
    
    # Ajouter une note indiquant que la pop n’a pas de corrélations détectées
    annotations.append(
        dict(
            x=0, y=y_offset + (len(legend_items) * spacing) - 0.89,
            xref="paper", yref="paper",
            text="<i>Aucune relation particulière pour la pop</i>",
            showarrow=False,
            font=dict(size=12, color="gray"),
            align="left"
        )
    )

    fig.update_layout(annotations=annotations, shapes=shapes)
    fig.update_layout(
        width=600,
        height=500,
        plot_bgcolor="white",  
        paper_bgcolor="white",
        xaxis=dict(showgrid=False, zeroline=False),  
        yaxis=dict(showgrid=False, zeroline=False)  
    )
    return fig

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H4("Corrélation entre les caractéristiques audio", style={"fontWeight": "bold", "fontSize": "30px"}),
    html.Div([
        dcc.Graph(id="graph-all", figure=get_figure()),
        dcc.Graph(id="scatter-plot")
    ], style={"display": "flex", "flex-wrap": "wrap", "gap": "20px"})
])

@app.callback(
    Output("scatter-plot", "figure"),
    [Input("graph-all", "clickData")]
)
def update_plot(all_clickData):
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
    selected = click_data['points'][0]['z']

    if selected == 1.0:
        selected_genre = 'all'
    elif selected == 0.8:
        selected_genre = 'rap'
    elif selected == 0.6:
        selected_genre = 'rock'
    elif selected == 0.4:
        selected_genre = 'latin'
    elif selected == 0.2:
        selected_genre = 'r&b'
    elif selected == 0.1:
        selected_genre = 'edm'

    if selected_genre == 'all':
        scatter_fig = px.scatter(data, x=x_feature, y=y_feature, hover_data=['track_name', 'track_artist'], color='playlist_genre', title=f"Scatter plot of {x_feature} vs {y_feature}")
        scatter_fig = px.parallel_coordinates(data, dimensions=['loudness', 'acousticness', 'energy', 'valence', 'danceability'], color='track_popularity', title=f"Parallel coordinates plot for {selected_genre}")
    if selected_genre == 'rap':
        genre_data = data[data['playlist_genre'] == selected_genre]
        scatter_fig = px.parallel_coordinates(genre_data, dimensions=['energy', 'instrumentalness','loudness', 'acousticness'], color='track_popularity', title=f"Parallel coordinates plot for {selected_genre}")
    if selected_genre == 'rock':
        genre_data = data[data['playlist_genre'] == selected_genre]
        scatter_fig = px.parallel_coordinates(genre_data, dimensions=['loudness', 'speechiness','energy', 'tempo'], color='track_popularity', title=f"Parallel coordinates plot for {selected_genre}")
    if selected_genre == 'latin':
        genre_data = data[data['playlist_genre'] == selected_genre]
        scatter_fig = px.parallel_coordinates(genre_data, dimensions=['valence', 'loudness'], color='track_popularity', title=f"Parallel coordinates plot for {selected_genre}")
    if selected_genre == 'r&b':
        genre_data = data[data['playlist_genre'] == selected_genre]
        scatter_fig = px.parallel_coordinates(genre_data, dimensions=['energy', 'danceability', 'loudness', 'valence', 'acousticness'], color='track_popularity', title=f"Parallel coordinates plot for {selected_genre}")
    if selected_genre == 'edm':
        genre_data = data[data['playlist_genre'] == selected_genre]
        scatter_fig = px.parallel_coordinates(genre_data, dimensions=['tempo', 'energy', 'duration_ms', 'liveness', 'loudness', 'instrumentalness'], color='track_popularity', title=f"Parallel coordinates plot for {selected_genre}")
    
    scatter_fig.update_layout(width=600, height=600)

    return scatter_fig

if __name__ == '__main__':
    app.run_server(debug=True)