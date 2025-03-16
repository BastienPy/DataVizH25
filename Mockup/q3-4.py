import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from statsmodels.nonparametric.smoothers_lowess import lowess
def get_dataframe(path):
    data = pd.read_csv(path)
    data["duration_min"] = data["duration_ms"] / 60000
    data["duration_formatted"] = data["duration_min"].apply(lambda x: f"{int(x)}:{int((x % 1) * 60):02d}")
    return data

def get_scatter_plot():
    data = get_dataframe("./dataset/spotify_songs_clean.csv")
    
    data["duration_bin"] = (data["duration_min"] * 4).round() / 4
    
    grouped_data = data.groupby("duration_bin", as_index=False).agg({
        "track_popularity": "mean", 
        "track_id": "count"
    }).rename(columns={"track_id": "count"})
    

    grouped_data["duration_bin"] = grouped_data["duration_bin"].round(2)
    grouped_data["track_popularity"] = grouped_data["track_popularity"].round(2)
    
    grouped_data["Legend"] = "Nombre de morceaux"
    grouped_data["size_scaled"] = np.sqrt(grouped_data["count"]) * 10
    grouped_data["count_original"] = grouped_data["count"]
    
    fig = px.scatter(
        grouped_data,
        x="duration_bin",
        y="track_popularity",
        size="size_scaled",
        color="Legend",
        title="Influence de la durée d'un morceau sur sa popularité",
        labels={
            "duration_bin": "Durée (min)",
            "track_popularity": "Popularité moyenne",
            "count": "Nombre de morceaux"
        },
        opacity=0.7,
        hover_data={
            "duration_bin": True,
            "track_popularity": True,
            "count_original": True
        },
        color_discrete_map={"Nombre de morceaux": "#2ca02c"}
    )
    
    grouped_data_sorted = grouped_data.sort_values(by="duration_bin")
    
    lowess_results = lowess(
        endog=grouped_data_sorted["track_popularity"],  
        exog=grouped_data_sorted["duration_bin"],      
        frac=0.3
    )

    lowess_trace = go.Scatter(
        x=lowess_results[:, 0],
        y=lowess_results[:, 1],
        mode='lines',
        line=dict(dash='dot', color='blue'),
        name='Tendance'
    )
    
    fig.add_trace(lowess_trace)
    
    fig.update_traces(
        marker=dict(line=dict(width=0)),
        hovertemplate=(
            "<b>Durée:</b> %{x} min<br>"
            "<b>Popularité moyenne:</b> %{y:.2f}<br>"
            "<b>Nombre de morceaux:</b> %{customdata:.0f} morceaux<extra></extra>"
        ),
        customdata=grouped_data["count_original"]
    )
    
    fig.update_layout(
        legend_title_text="Légende"
    )
    
    return fig

def get_boxplot():
    data = get_dataframe("./dataset/spotify_songs_clean.csv")
    color_map = {
        "pop": "#ff7f0e",
        "rap": "#d62728",
        "rock": "#1f77b4",
        "latin": "#9467bd",
        "r&b": "#8c564b",
        "edm": "#17becf"
    }

    summary_stats = data.groupby("playlist_genre")["track_popularity"].describe()[['min', '25%', '50%', '75%', 'max']]
    summary_stats = summary_stats.rename(columns={'25%': 'Q1', '50%': 'Median', '75%': 'Q3'})
    data = data.merge(summary_stats, left_on="playlist_genre", right_index=True)


    mean_pop_by_genre = data.groupby("playlist_genre")["track_popularity"].mean().sort_values()
    genre_order = mean_pop_by_genre.index.tolist()


    fig = px.box(
        data,
        x="playlist_genre",
        y="track_popularity",
        title="Influence du genre musical sur la popularité",
        labels={"playlist_genre": "Genre musical", "track_popularity": "Popularité"},
        points=False,
        color="playlist_genre",
        color_discrete_map=color_map,
        custom_data=["min", "Q1", "Median", "Q3", "max"],
        category_orders={"playlist_genre": genre_order}
    )

    return fig


app = dash.Dash(__name__)

app.layout = html.Div([
    html.H4("Influence de la durée d'un morceau sur sa popularité", style={"fontWeight": "bold", "fontSize": "20px"}),
    dcc.Graph(id="scatter_graph", figure=get_scatter_plot()),
    html.H4("Influence du genre musical sur la popularité", style={"fontWeight": "bold", "fontSize": "20px"}),
    dcc.Graph(id="boxplot_graph", figure=get_boxplot()),
])

app.run_server(debug=False)
