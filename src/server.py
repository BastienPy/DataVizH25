"""
Contains the server to run our application.
"""
from flask_failsafe import failsafe
import os

@failsafe
def create_app():
    """
    Gets the underlying Flask server from our Dash app.

    Returns:
        The server to be run.
    """
    # the import is intentionally inside to work with the server failsafe
    from src.app import app  # pylint: disable=import-outside-toplevel
    return app.server

# Create the WSGI callable that Gunicorn expects.
server = create_app()

if __name__ == "__main__":
    # Récupère le port défini dans la variable d'environnement PORT ou par défaut 8050.
    port = int(os.environ.get("PORT", 8050))
    # Utilise 0.0.0.0 pour écouter sur toutes les interfaces.
    server.run(port=port, debug=True, host='0.0.0.0')
