import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Create the main Dash app instance.
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = 'Spotify Songs Analysis'

# Import your sections (q1 and q2 must export a "layout" variable)
import q1
import q2
import q8
import q5
import q11

# Register callbacks for both sections.
q1.register_callbacks(app)
q2.register_callbacks(app)
q5.register_callbacks(app)
q8.register_callbacks(app)

# Top navigation bar with anchor links for scrolling
navbar = html.Div(
    [
        html.A("Q1 Analysis", href="#q1-section"),
        html.A("Q2 Analysis", href="#q2-section"),
        html.A("Q5 Analysis", href="#q5-section"),
        html.A("Q8 Analysis", href="#q8-section"), # TODO : renommer les analyses
        html.A("Q11 Analysis", href="#q11-section")
    ],
    className="navbar"
)

# Main content area that includes both sections
content = html.Div(
    [
        # Q1 Section with an id for anchor scrolling
        html.Div(
            q1.layout,
            id="q1-section",
            style={"padding-top": "60px", "margin-top": "-60px"}
        ),
        html.Hr(style={"border-color": "#1DB954"}),
        # Q2 Section with an id for anchor scrolling
        html.Div(
            q2.layout,
            id="q2-section",
            style={"padding-top": "60px", "margin-top": "-60px"}
        ),
        html.Hr(style={"border-color": "#1DB954"}),
        # Q5 Section with an id for anchor scrolling
        html.Div(
            q5.layout,
            id="q5-section",
            style={"padding-top": "60px", "margin-top": "-60px"}
        ),
        html.Hr(style={"border-color": "#1DB954"}),
        # Q8 Section with an id for anchor scrolling
        html.Div(
            q8.layout,
            id="q8-section",
            style={"padding-top": "60px", "margin-top": "-60px"}
        ),
        html.Hr(style={"border-color": "#1DB954"}),
        # Q11 Section with an id for anchor scrolling
        html.Div(
            q11.layout,
            id="q11-section",
            style={"padding-top": "60px", "margin-top": "-60px"}
        )
    ],
    className="content"
)

# Overall app layout
app.layout = html.Div([dcc.Location(id="url"), navbar, content])

if __name__ == '__main__':
    app.run_server(debug=True)
