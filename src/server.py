'''
    Contains the server to run our application.
'''
from flask_failsafe import failsafe
import sys
import os

# Add the parent directory of 'src' to the Python module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@failsafe
def create_app():
    '''
        Gets the underlying Flask server from our Dash app.

        Returns:
            The server to be run
    '''
    # the import is intentionally inside to work with the server failsafe
    from src.app import app  # pylint: disable=import-outside-toplevel
    return app.server


if __name__ == "__main__":
    create_app().run(port="8050", debug=True)