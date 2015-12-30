from flask import (
    Blueprint,
    render_template
)

import json

journeys = Blueprint('journeys', __name__, template_folder='templates')

@journeys.route('/journeys')
def journeys_home():
    return render_template('journeys/home.html')

@journeys.route('/journeys/viewer')
def journeys_viewer():
    with open('application/data/csl.json') as data_file:
          journeys = json.load(data_file)
    return render_template('journeys/viewer.html', journeys=journeys)