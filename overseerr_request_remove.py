import requests

from datetime import datetime
from webhook_discord import *

def overseerr_delete(api_key_overseerr, tmdbId, media_id, discord_webhook_error, url_overseerr):

    url_delete = 'http://{url_overseerr}/api/v1/media/{id}'
    url_delete = url_delete.replace('{id}', str(media_id))
    url_delete = url_delete.replace('{url_overseerr}', url_overseerr)

    headers = {'X-Api-Key': api_key_overseerr}
    response = requests.delete(url_delete, headers=headers)

    # print("Deleting movie status code: " + str(response.status_code))
    if response.status_code != 204:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('api_error.log', 'a') as f:
            f.write(date + " - Deleting movie status code in overseerr: " + str(response.status_code) + "\n")
        webhook_discord_error(discord_webhook_error, "Deleting movie status code in overseerr", str(response.status_code), date)