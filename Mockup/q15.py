import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

def convert_date(date):
    try:
        #Complete format: "%Y-%m-%d"
        return pd.to_datetime(date, format="%Y-%m-%d")
    except ValueError:
        try:
            #Year only: "%Y", completed with "-01-01"
            return pd.to_datetime(date, format="%Y") + pd.offsets.DateOffset(months=0, days=0)
        except ValueError:
            return pd.NaT

def get_dataframe(path):
    data = pd.read_csv(path)
    data["track_album_release_date"] = data["track_album_release_date"].apply(convert_date)
    #Keep only songs released from 1970 onward
    data = data[data["track_album_release_date"].dt.year >= 1970]
    return data

def get_color_map():
    data = get_dataframe("./dataset/spotify_songs_clean.csv")
    unique_subgenres = sorted(data["playlist_subgenre"].unique())
    color_sequence = px.colors.qualitative.Dark2
    #Cycle through the colors if there are more subgenres than colors
    color_map = {subgenre: color_sequence[i % len(color_sequence)] 
                 for i, subgenre in enumerate(unique_subgenres)}
    return color_map

color_map = get_color_map()

# Original decade-based preprocessing function
def data_preprocess(path, filter_type, filter_value=None, genre_filter=None):
    data = get_dataframe(path)
    data["year"] = data["track_album_release_date"].dt.year
    data["decennie"] = (data["year"] // 10) * 10  #Calculate the decade

    if genre_filter:
        data = data[data["playlist_genre"] == genre_filter]

    if filter_type == "artist" and filter_value:
        data = data[data["track_artist"] == filter_value]
        group_by_column = "playlist_subgenre"
    elif filter_type in ["genre", "edm", "latin", "pop", "r&b", "rap", "rock"] and filter_value is None:
        data = data[data["playlist_genre"] == filter_type]
        group_by_column = "playlist_subgenre"
    elif filter_type == "genre" and filter_value:
        data = data[data["playlist_genre"] == filter_value]
        group_by_column = "playlist_subgenre"
    else:
        group_by_column = "playlist_genre"

    genre_data = data.groupby(["decennie", group_by_column]).size().reset_index(name="count")
    genre_data = genre_data.pivot(index="decennie", columns=group_by_column, values="count").fillna(0)
    total_songs_by_decennie = genre_data.sum(axis=1)
    genre_data = (genre_data.div(total_songs_by_decennie, axis=0) * 100).reset_index()
    genre_data = genre_data.melt(id_vars="decennie", var_name=group_by_column, value_name="percentage")
    return genre_data

def data_preprocess_artist_cumulative(path, artist, genre_filter):
    data = get_dataframe(path)
    # Filtrer pour l'artiste et le genre sélectionnés
    data = data[(data["track_artist"] == artist) & (data["playlist_genre"] == genre_filter)]
    # Formater la date
    data["formatted_date"] = pd.to_datetime(data["track_album_release_date"]).dt.strftime("%Y-%m-%d")
    
    # Grouper par date et sous-genre et compter le nombre de chansons
    grouped = data.groupby(["formatted_date", "playlist_subgenre"]).size().reset_index(name="count")
    # Pivot pour avoir une ligne par date et une colonne par sous-genre
    pivot = grouped.pivot(index="formatted_date", columns="playlist_subgenre", values="count").fillna(0)
    
    # S'assurer que l'index (date) est de type datetime et trié
    pivot.index = pd.to_datetime(pivot.index)
    pivot = pivot.sort_index()
    
    # Calcul de la somme cumulée par sous-genre sur le temps
    cum = pivot.cumsum()
    # Pour chaque date, calculer le total cumulé de toutes les chansons
    total_cum = cum.sum(axis=1)
    # Calculer le pourcentage cumulatif pour chaque sous-genre
    cum_percent = cum.div(total_cum, axis=0) * 100
    
    # Repasser en format "long" pour Plotly Express
    cum_percent = cum_percent.reset_index().melt(
        id_vars="formatted_date", var_name="playlist_subgenre", value_name="percentage"
    )
    cum_percent["formatted_date"] = pd.to_datetime(cum_percent["formatted_date"])
    cum_percent = cum_percent.sort_values("formatted_date")
    
    return cum_percent

#Custom binning preprocessing function with 10 bins over a dynamic time range
def data_preprocess_custom(path, filter_type, filter_value=None, genre_filter=None, bins=10, start_date=None, end_date=None):
    data = get_dataframe(path)
    
    #Filter by genre if provided
    if genre_filter:
        data = data[data["playlist_genre"] == genre_filter]
        
    if filter_type == "artist" and filter_value:
        data = data[data["track_artist"] == filter_value]
        group_by_column = "playlist_subgenre"
    elif filter_type in ["genre", "edm", "latin", "pop", "r&b", "rap", "rock"] and filter_value is None:
        data = data[data["playlist_genre"] == filter_type]
        group_by_column = "playlist_subgenre"
    elif filter_type == "genre" and filter_value:
        data = data[data["playlist_genre"] == filter_value]
        group_by_column = "playlist_subgenre"
    else:
        group_by_column = "playlist_genre"
    
    #Define start and end dates based on the data if not provided
    if start_date is None:
        min_date = data["track_album_release_date"].min()
    else:
        min_date = start_date
    if end_date is None:
        max_date = data["track_album_release_date"].max()
    else:
        max_date = end_date

    #If there's only one unique date, extend the range by one day
    if min_date == max_date:
        max_date = min_date + pd.Timedelta(days=1)
        
    #Create bin edges and compute midpoints for labeling
    bin_edges = pd.date_range(start=min_date, end=max_date, periods=bins+1)
    bin_midpoints = [bin_edges[i] + (bin_edges[i+1] - bin_edges[i]) / 2 for i in range(len(bin_edges)-1)]
    
    #Filter data to the chosen time range and assign each song to a bin
    data = data[(data["track_album_release_date"] >= min_date) & (data["track_album_release_date"] <= max_date)]
    data["time_bin"] = pd.cut(data["track_album_release_date"], bins=bin_edges, labels=bin_midpoints, include_lowest=True)
    
    #Group by the custom time_bin and the specified grouping column, then calculate percentages
    genre_data = data.groupby(["time_bin", group_by_column]).size().reset_index(name="count")
    genre_data = genre_data.pivot(index="time_bin", columns=group_by_column, values="count").fillna(0)
    total_songs_by_bin = genre_data.sum(axis=1)
    genre_data = (genre_data.div(total_songs_by_bin, axis=0) * 100).reset_index()
    genre_data = genre_data.melt(id_vars="time_bin", var_name=group_by_column, value_name="percentage")
    
    return genre_data, (min_date, max_date)

#Cached figures for decade-based graphs (used when no artist is selected)
subgenre_cache = {
    "edm": px.area(
        data_preprocess("./dataset/spotify_songs_clean.csv", "genre", "edm"),
        x="decennie", y="percentage", color="playlist_subgenre",
        line_group="playlist_subgenre", hover_data=["playlist_subgenre"],
        color_discrete_map=color_map
    ),
    "latin": px.area(
        data_preprocess("./dataset/spotify_songs_clean.csv", "genre", "latin"),
        x="decennie", y="percentage", color="playlist_subgenre",
        line_group="playlist_subgenre", hover_data=["playlist_subgenre"],
        color_discrete_map=color_map
    ),
    "pop": px.area(
        data_preprocess("./dataset/spotify_songs_clean.csv", "genre", "pop"),
        x="decennie", y="percentage", color="playlist_subgenre",
        line_group="playlist_subgenre", hover_data=["playlist_subgenre"],
        color_discrete_map=color_map
    ),
    "r&b": px.area(
        data_preprocess("./dataset/spotify_songs_clean.csv", "genre", "r&b"),
        x="decennie", y="percentage", color="playlist_subgenre",
        line_group="playlist_subgenre", hover_data=["playlist_subgenre"],
        color_discrete_map=color_map
    ),
    "rap": px.area(
        data_preprocess("./dataset/spotify_songs_clean.csv", "genre", "rap"),
        x="decennie", y="percentage", color="playlist_subgenre",
        line_group="playlist_subgenre", hover_data=["playlist_subgenre"],
        color_discrete_map=color_map
    ),
    "rock": px.area(
        data_preprocess("./dataset/spotify_songs_clean.csv", "genre", "rock"),
        x="decennie", y="percentage", color="playlist_subgenre",
        line_group="playlist_subgenre", hover_data=["playlist_subgenre"],
        color_discrete_map=color_map
    )
}

def get_hover_template(type_name):
    return (
        f"<b>{type_name}:</b></span>" 
        " %{customdata[0]} <br /></span>"
        "<b>Decennie:</b></span>"
        " %{x}<br /></span>"
        "<b>Pourcentage:</b></span>"
        " %{y:.3f} %</span>"
        "<extra></extra>" # Pour enlever le "trace 0" qui apparait automatiquement sinon
    )


#Hover template for the custom binned graphs with formatted dates
def get_hover_template_custom(type_name):
    return (
        f"<b>{type_name}:</b></span>" 
        " %{customdata[0]} <br /></span>"
        "<b>Date:</b></span>"
        " %{x|%Y/%m/%d}<br /></span>"
        "<b>Pourcentage:</b></span>"
        " %{y:.3f} %</span>"
        "<extra></extra>" # Pour enlever le "trace 0" qui apparait automatiquement sinon
    )


app = dash.Dash(__name__)

app.layout = html.Div([
    html.H4("Évolution de la proportion des sous-genres musicaux par genre et artiste",
            style={"fontWeight": "bold", "fontSize": "30px", "textAlign": "center"}),
    
    html.Div([
        # Left column: Genre selection and graph
        html.Div([
            html.Label("Sélectionnez un genre:"),
            dcc.Dropdown(
                id='genre_dropdown',
                options=[{'label': g.capitalize(), 'value': g} for g in ['edm', 'latin', 'pop', 'r&b', 'rap', 'rock']],
                placeholder="Sélectionnez un genre",
                style={"margin-bottom": "20px"}
            ),
            dcc.Graph(id='subgenre_graph')
        ], style={"width": "50%", "display": "inline-block", "verticalAlign": "top", "padding": "10px"}),

        # Right column: Artist selection and graph
        html.Div([
            html.Label("Sélectionnez un artiste:"),
            dcc.Dropdown(
                id='artist_dropdown',
                options=[],  # Options will be populated based on selected genre
                placeholder="Sélectionnez un artiste",
                style={"margin-bottom": "20px"}
            ),
            dcc.Graph(id='artist_subgenre_graph')
        ], style={"width": "50%", "display": "inline-block", "verticalAlign": "top", "padding": "10px"})
    ], style={"display": "flex", "flex-direction": "row"})
])

# Callback to update the artist dropdown based on the selected genre
@app.callback(
    [Output('artist_dropdown', 'options'),
     Output('artist_dropdown', 'value')],
    [Input('genre_dropdown', 'value')]
)
def update_artist_options(selected_genre):
    if not selected_genre:
        return [], None
    data = get_dataframe("./dataset/spotify_songs_clean.csv")
    # Filter data to only include songs from the selected genre
    data = data[data["playlist_genre"] == selected_genre]
    # Count unique songs per artist (assuming the CSV contains a 'track_name' column)
    artist_counts = data.groupby("track_artist")["track_name"].nunique().reset_index(name="song_count")
    # Sort artists by the number of unique songs in descending order
    artist_counts = artist_counts.sort_values("song_count", ascending=False)
    # Create the dropdown options list using the sorted order
    options = [{'label': artist, 'value': artist} for artist in artist_counts["track_artist"]]
    # Reset the selected artist value to None
    return options, None


# Updated callback for the genre/subgenre graph
@app.callback(
    Output('subgenre_graph', 'figure'),
    [Input('genre_dropdown', 'value'),
     Input('artist_dropdown', 'value')]
)
def update_subgenre_graph(selected_genre, selected_artist):
    if not selected_genre:
        fig = px.area()
        fig.add_annotation(dict(xref="paper", yref="paper", x=0.5, y=0.5),
                           text="Sélectionnez un genre pour voir les données.",
                           showarrow=False)
        return fig

    if selected_artist:
        # Determine the artist's time range within the selected genre
        data = get_dataframe("./dataset/spotify_songs_clean.csv")
        data_artist = data[(data["playlist_genre"] == selected_genre) &
                           (data["track_artist"] == selected_artist)]
        if data_artist.empty:
            # Fallback to cached genre figure if no artist data found
            fig = subgenre_cache[selected_genre]
        else:
            artist_min = data_artist["track_album_release_date"].min()
            artist_max = data_artist["track_album_release_date"].max()
            # Use custom binning with 10 bins over the artist's timeframe
            genre_data, _ = data_preprocess_custom(
                "./dataset/spotify_songs_clean.csv", 
                "genre", 
                selected_genre, 
                bins=10, 
                start_date=artist_min, 
                end_date=artist_max
            )
            # Convert time_bin values to datetime so that Plotly formats them correctly
            genre_data["time_bin"] = pd.to_datetime(genre_data["time_bin"])
            fig = px.area(
                genre_data, 
                x="time_bin", y="percentage", 
                color="playlist_subgenre",
                line_group="playlist_subgenre", 
                hover_data=["playlist_subgenre"],
                color_discrete_map=color_map
            )
            # Use the custom hover template for the custom binned data
            fig.update_traces(hovertemplate=get_hover_template_custom(selected_genre))
            fig.update_layout(legend_title_text="Sous-genre de " + selected_genre)
            fig.update_layout(legend=dict(traceorder='reversed'))
            # Update x-axis to show formatted dates instead of numeric timestamps
            fig.update_xaxes(title_text="Date", tickformat="%Y")
    else:
        # When only a genre is selected, use the cached (decade-based) figure
        fig = subgenre_cache[selected_genre]
        
    fig.update_yaxes(title_text='Pourcentage (%)')
    return fig


def data_preprocess_artist(path, artist, genre_filter):
    data = get_dataframe(path)
    # Filter for the selected artist and genre
    data = data[(data["track_artist"] == artist) & (data["playlist_genre"] == genre_filter)]
    # Create a formatted date column (or simply use the original date)
    data["formatted_date"] = data["track_album_release_date"].dt.strftime("%Y-%m-%d")
    
    # Group by the formatted date and subgenre, and count the number of songs
    grouped = data.groupby(["formatted_date", "playlist_subgenre"]).size().reset_index(name="count")
    
    # Pivot the table to have one row per date and one column per subgenre
    pivot = grouped.pivot(index="formatted_date", columns="playlist_subgenre", values="count").fillna(0)
    
    # Calculate percentages per date
    pivot_percent = pivot.div(pivot.sum(axis=1), axis=0) * 100
    pivot_percent = pivot_percent.reset_index()
    
    # Melt back to tidy format for Plotly Express
    melted = pivot_percent.melt(id_vars="formatted_date", var_name="playlist_subgenre", value_name="percentage")
    
    # Ensure dates are sorted correctly (convert back to datetime if needed)
    melted["formatted_date"] = pd.to_datetime(melted["formatted_date"])
    melted = melted.sort_values("formatted_date")
    
    return melted

@app.callback(
    Output('artist_subgenre_graph', 'figure'),
    [Input('genre_dropdown', 'value'),
     Input('artist_dropdown', 'value')]
)
def update_artist_subgenre_graph(selected_genre, selected_artist):
    if not selected_genre or not selected_artist:
        fig = px.area()
        fig.add_annotation(dict(xref="paper", yref="paper", x=0.5, y=0.5),
                           text="Sélectionnez un artiste pour voir les données.",
                           showarrow=False)
        return fig

    # Utiliser la nouvelle fonction qui calcule les proportions cumulées
    artist_data = data_preprocess_artist_cumulative("./dataset/spotify_songs_clean.csv", selected_artist, selected_genre)
    
    # Création du graphique en aires avec les dates formatées
    fig = px.area(artist_data, x="formatted_date", y="percentage", color="playlist_subgenre",
                  line_group="playlist_subgenre", hover_data=["playlist_subgenre"],
                  color_discrete_map=color_map)
    
    fig.update_layout(height=500, title=f"Évolution cumulée des sous-genres pour {selected_artist} ({selected_genre})")
    # Personnalisation du hover pour afficher la date au format souhaité
    fig.update_traces(hovertemplate=(
        "<b>Sous-genre:</b> %{customdata[0]}<br>"
        "<b>Date:</b> %{x|%Y-%m-%d}<br>"
        "<b>Pourcentage cumulatif:</b> %{y:.3f}%<extra></extra>"
    ))
    fig.update_yaxes(title_text='Pourcentage cumulatif (%)')
    fig.update_layout(legend_title_text="Sous-genre", legend=dict(traceorder='reversed'))
    
    return fig



if __name__ == '__main__':
    app.run_server(debug=False)