import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

# Create the main Dash app instance.
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = 'Spotify Songs Analysis'

# Import your sections (q1, q2, q8, q11 must export a "layout" variable)
import caracteristiques_audio
import q1
import q2
import q5
import q11
import q14
import q13

# Register callbacks for the sections.
caracteristiques_audio.register_callbacks(app)
q1.register_callbacks(app)
q2.register_callbacks(app)
q5.register_callbacks(app)
q14.register_callbacks(app)
q13.register_callbacks(app)

# Top navigation bar with anchor links for scrolling.
navbar = html.Div(
    [
        html.Img(src="/assets/spotify_icon.svg", style={'height': '40px', 'marginRight': '10px'}),
        html.A(
            [html.I(className="fa-brands fa-spotify", style={'marginRight': '8px'}), "Définitions"],
            href="#def-section"
        ),
        html.A(
            [html.I(className="fa-brands fa-spotify", style={'marginRight': '8px'}), "Q1 Analysis"],
            href="#q1-section"
        ),
        html.A(
            [html.I(className="fa-brands fa-spotify", style={'marginRight': '8px'}), "Q2 Analysis"],
            href="#q2-section"
        ),
        html.A(
            [html.I(className="fa-brands fa-spotify", style={'marginRight': '8px'}), "Q5 Analysis"],
            href="#q5-section"
        ),
        html.A(
            [html.I(className="fa-brands fa-spotify", style={'marginRight': '8px'}), "Q11 Analysis"],
            href="#q11-section"
        ),
        html.A(
            [html.I(className="fa-brands fa-spotify", style={'marginRight': '8px'}), "Q14 Analysis"],
            href="#q14-section"
        ),
        html.A(
            [html.I(className="fa-brands fa-spotify", style={'marginRight': '8px'}), "Q13 Analysis"],
            href="#q13-section"
        )
    ],
    className="navbar"
)

# Mascot element – the image that can be clicked to hide it.
mascot = html.Div(
    html.Img(src="/assets/mascot.png", style={'height': '150px'}),
    id='mascot',
    n_clicks=0,  # for toggling
    style={
        'position': 'fixed',
        'bottom': '20px',
        'left': '0px',
        'zIndex': '1001',
        'display': 'block'
    }
)

# Toggle button that appears when the mascot is hidden.
mascot_toggle_btn = html.Button(
    html.I(className="fa-solid fa-eye"),
    id='mascot-toggle-btn',
    n_clicks=0,
    style={
        'position': 'fixed',
        'bottom': '20px',
        'left': '0px',
        'zIndex': '1002',
        'display': 'none',
        'backgroundColor': '#1DB954',
        'border': 'none',
        'color': 'white',
        'padding': '10px',
        'borderRadius': '5px'
    }
)

# Speech bubble for the mascot.
mascot_speech = html.Div(
    id='mascot-speech',
    children="Welcome to Spotify Songs Analysis!",
    style={
        'position': 'fixed',
        'bottom': '180px',
        'left': '0px',
        'backgroundColor': '#1DB954',
        'padding': '10px',
        'borderRadius': '10px'
    }
)
narrative_q1 = html.Div(
    dcc.Markdown("""
    ### Story Time
    A REMPLIR
    """),
    style={'padding': '20px', 'backgroundColor': '#181818', 'borderRadius': '8px'}
)

narrative = html.Div(
    dcc.Markdown("""
    ### Story Time
    Saviez-vous que la pupularité d'une musique est influencé par ses caractéristiques audio ?
    """),
    style={'padding': '20px', 'backgroundColor': '#181818', 'borderRadius': '8px'}
)

narrative_q13 = html.Div(
    [
        dcc.Markdown("""  
        
        Cette visualisation compare l’évolution musicale générale avec celle des artistes ayant une longue carrière (plus de 30 ans).  
        On remarque que la tendance globale (courbe bleue) montre des changements progressifs dans les caractéristiques comme la **danceability**, l’**énergie** ou la **valence**.  
        En revanche, les artistes de longue carrière (courbe verte) conservent des valeurs plus stables dans le temps.  

        Cela suggère qu’ils arrivent à **adapter leur musique aux tendances** sans forcément changer complètement leur style.  
        On peut donc dire que la **longévité artistique** permet de rester populaire tout en gardant une certaine **cohérence musicale**.  

        Cette analyse complète les observations précédentes en montrant que **l’expérience** et la capacité à évoluer sont aussi des facteurs importants dans le succès musical.
        """)
    ],
    style={'padding': '20px', 'backgroundColor': '#121212', 'borderRadius': '8px'}
)

narrative_q14 = html.Div(
    [
        dcc.Markdown("""
        ### Analyse de l'évolution des genres des artistes
                     
        Il est maintenant possible de s'attarder non plus sur les caractéristiques des musiques elles-mêmes, mais sur l'évolution des artistes et des genres qu'ils créent.
                     
        On peut y apprendre de nombreux éléments sur l'évolution des goûts musicaux. 
        Par exemple, le rock semblait être le plus populaire dans les années 1970 (on peut alors penser à l'apparition de groupes comme les Rolling Stones, U2 ou Radiohead…)
        alors que l'EDM a lui émergé dans les années 2000.
        """),
        html.Br(),
        dcc.Markdown("""
        Vous pouvez **choisir un genre** en particulier pour observer les évolutions de ses sous-genres, ainsi que choisir un des artistes de ce genre pour observer l'évolution de sa discographie !
        
        *Il est ainsi possible de remarquer par exemple que pour le rap, le hip-hop qui représente aujourd'hui la majeure partie du genre, n'existait pas avant les années 1990 !*
        """)
    ],
    style={'padding': '20px', 'backgroundColor': '#121212', 'borderRadius': '8px'}
)


# Main content area that includes all sections.
content = html.Div(
    [
        # Q1 Section with an id for anchor scrolling.
        narrative_q1,
        html.Hr(style={"border-color": "#1DB954"}),
        html.Div(
            caracteristiques_audio.layout,
            id="def-section",
            style={"padding-top": "60px", "margin-top": "-60px"}
        ),
        html.Div(
            q1.layout,
            id="q1-section",
            style={"padding-top": "60px", "margin-top": "-60px"}
        ),
        narrative,
        html.Hr(style={"border-color": "#1DB954"}),
        # Q2 Section with an id for anchor scrolling.
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
        # Q11 Section with an id for anchor scrolling.
        html.Div(
            q11.layout,
            id="q11-section",
            style={"padding-top": "60px", "margin-top": "-60px"}
        ),
        html.Hr(style={"border-color": "#1DB954"}),
        # Q14 Section with an id for anchor scrolling.
        narrative_q14,
        html.Div(
            q14.layout,
            id="q14-section",
            style={"padding-top": "60px", "margin-top": "-60px"}
        ),
        html.Hr(style={"border-color": "#1DB954"}),
        html.Div(
            q13.layout,
            id="q13-section",
            style={"padding-top": "60px", "margin-top": "-60px"}
        )
    ],
    className="content"
)

# An Interval component that fires every 1000ms (adjust as needed).
interval = dcc.Interval(id="scroll-interval", interval=1000, n_intervals=0)

# A hidden Store to keep track of the current section.
current_section_store = dcc.Store(id="current-section", data="")

# A Store to keep track of the mascot's visibility (True = visible).
mascot_state = dcc.Store(id="mascot-state", data=True)

# Overall app layout (added Interval, Stores, and the toggle button).
app.layout = html.Div([
    dcc.Location(id="url"),
    interval,
    current_section_store,
    mascot_state,
    navbar,
    content,
    mascot,              # Mascot image.
    mascot_toggle_btn,   # Toggle button.
    mascot_speech        # Speech bubble.
])


# -----------------------------------------------------------------------------
# Callback 1: Toggle the mascot's visibility using clicks from either the mascot or toggle button.
# -----------------------------------------------------------------------------
@app.callback(
    Output('mascot-state', 'data'),
    [Input('mascot', 'n_clicks'),
     Input('mascot-toggle-btn', 'n_clicks')],
    State('mascot-state', 'data')
)
def toggle_mascot_state(mascot_clicks, toggle_btn_clicks, current_state):
    # Determine which input triggered the callback.
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_state
    # Toggle the state when either element is clicked.
    return not current_state


# -----------------------------------------------------------------------------
# Callback 2: Update the styles of the mascot and the toggle button based on visibility.
# -----------------------------------------------------------------------------
@app.callback(
    [Output('mascot', 'style'),
     Output('mascot-toggle-btn', 'style')],
    Input('mascot-state', 'data')
)
def update_mascot_styles(is_visible):
    base_mascot_style = {
        'position': 'fixed',
        'bottom': '20px',
        'left': '0px',
        'zIndex': '1001'
    }
    base_toggle_style = {
        'position': 'fixed',
        'bottom': '20px',
        'left': '0px',
        'zIndex': '1002',
        'backgroundColor': '#1DB954',
        'border': 'none',
        'color': 'white',
        'padding': '10px',
        'borderRadius': '5px'
    }
    if is_visible:
        base_mascot_style['display'] = 'block'
        base_toggle_style['display'] = 'none'
    else:
        base_mascot_style['display'] = 'none'
        base_toggle_style['display'] = 'block'
    return base_mascot_style, base_toggle_style


# -----------------------------------------------------------------------------
# Clientside callback: Detect the section currently in view.
# It measures the distance between each section's top and the vertical midpoint of the window.
# -----------------------------------------------------------------------------
app.clientside_callback(
    """
    function(n_intervals) {
        var sections = ['q1-section', 'q2-section', 'q8-section', 'q11-section'];
        var current = "";
        var minDistance = Infinity;
        var target = window.innerHeight / 2;  // Middle of the viewport.
        for (var i = 0; i < sections.length; i++){
            var el = document.getElementById(sections[i]);
            if (el){
                var rect = el.getBoundingClientRect();
                var distance = Math.abs(rect.top - target);
                if (distance < minDistance){
                    minDistance = distance;
                    current = sections[i];
                }
            }
        }
        return current;
    }
    """,
    Output('current-section', 'data'),
    Input('scroll-interval', 'n_intervals')
)


# -----------------------------------------------------------------------------
# Callback 3: Update the speech bubble text based on the current section.
# -----------------------------------------------------------------------------
@app.callback(
    Output('mascot-speech', 'children'),
    Input('current-section', 'data')
)
def update_speech(current):
    if current == "def-section":
        return "Définissions les termes"
    elif current == "q1-section":
        return "Comment évoluent les caractéristiques audio, et quel impact sur la popularité ?"
    elif current == "q2-section":
        return "Quelles corrélations entre les caractéristiques audio ?"
    elif current == "q5-section":
        return "Comment évoluent les caractéristiques audio selon le genre ?"
    elif current == "q11-section":
        return "Les artistes diversifiés sont-ils plus populaires ?"
    elif current == "q14-section":
        return "Les artistes à grande discographie s'adaptent-ils aux sous-genres populaires ?"
    elif current == "q13-section":
        return "Et les artistes s'adaptent-ils aux caractéristiques audio populaires ?"
    else:
        return "Welcome to Spotify Songs Analysis!"


if __name__ == '__main__':
    app.run_server(debug=True)
