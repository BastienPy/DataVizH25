import dash
from dash import dcc, html, Input, Output

# Create the main Dash app instance.
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = 'Spotify Songs Analysis'

# Import page sections.
import q1
import q2

# Register callbacks for both sections.
q1.register_callbacks(app)
q2.register_callbacks(app)

# Create a sidebar with anchor links for scrolling.
sidebar = html.Div(
    [
        html.H2("Navigation", style={'textAlign': 'center'}),
        html.Hr(),
        # The href targets the div id on the page
        html.A("Go to Q1 Section", href="#q1-section", style={'display': 'block', 'margin-bottom': '10px'}),
        html.A("Go to Q2 Section", href="#q2-section", style={'display': 'block'})
    ],
    style={'padding': '20px', 'width': '20%', 'position': 'fixed', 'height': '100%', 'overflowY': 'auto'}
)

# Main content that includes both q1 and q2 sections.
content = html.Div(
    [
        # Q1 Section with an id for the anchor link.
        html.Div(
            q1.layout,
            id="q1-section",
            style={"padding-top": "60px", "margin-top": "-60px"}
        ),
        html.Hr(),
        # Q2 Section with an id for the anchor link.
        html.Div(
            q2.layout,
            id="q2-section",
            style={"padding-top": "60px", "margin-top": "-60px"}
        )
    ],
    style={'margin-left': '22%', 'padding': '20px'}
)

# Overall layout.
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

if __name__ == '__main__':
    app.run_server(debug=True)
