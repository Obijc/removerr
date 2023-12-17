import json

from radarr_movie_remove import *
from sonarr_serie_remove import *

with open('settings.json', 'r') as json_file:
    variables = json.load(json_file)

api_key_radarr = variables['api_key_radarr']
api_key_sonarr = variables['api_key_sonarr']

restart_radarr(api_key_radarr)
restart_sonarr(api_key_sonarr)

