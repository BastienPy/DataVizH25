import dash
from dash import dcc, html, Input, Output

# Create the main Dash app instance.
# Using suppress_callback_exceptions is useful in multipage apps.
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = 'Spotify Songs Analysis'

# Import your page modules.
import q1
import q2

# Register the page-specific callbacks.
q1.register_callbacks(app)
q2.register_callbacks(app)

# Define a sidebar with links to each page.
sidebar = html.Div(
    [
        html.H2("Navigation", style={'textAlign': 'center'}),
        html.Hr(),
        dcc.Link("Page Q1", href="/q1"),
        html.Br(),
        dcc.Link("Page Q2", href="/q2"),
    ],
    style={'padding': '20px', 'width': '20%', 'display': 'inline-block', 'verticalAlign': 'top'}
)

# Content container: page layouts will be rendered here.
content = html.Div(id="page-content", style={'padding': '20px', 'width': '75%', 'display': 'inline-block'})

# Define the overall app layout with a Location component.
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    sidebar,
    content
])

# Callback to update the content based on the URL.
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/q1":
        return q1.layout
    elif pathname == "/q2":
        return q2.layout
    else:
        return html.Div([
            html.H1("Welcome to Spotify Songs Analysis"),
            html.P("Select a page from the sidebar.")
        ])

if __name__ == '__main__':
    app.run_server(debug=True)
