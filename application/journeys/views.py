from flask import (
    Blueprint,
    render_template
)

journeys = Blueprint('journeys', __name__, template_folder='templates')

@journeys.route('/journeys')
def journeys_home():
    return render_template('journeys/home.html')

@journeys.route('/journeys/viewer')
def journeys_viewer():
    return render_template('journeys/viewer.html')