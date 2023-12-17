import requests, time, json, sys

from datetime import datetime, timedelta
from overseerr_request_remove import *
from radarr_movie_remove import *
from sonarr_serie_remove import *
from webhook_discord import *

def get_movie_info(api_key_overseerr, tmdb_id):
    url = 'http://192.168.1.28:5055/api/v1/movie/{TMDBID}'
    url = url.replace('{TMDBID}', str(tmdb_id))

    headers = {'X-Api-Key': api_key_overseerr}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('log/api_error.log', 'a') as f:
            f.write(date + " - Get movie info status code: " + str(response.status_code) + "\n")
        webhook_discord_error(discord_webhook_error, "Get movie info status code", str(response.status_code), date)

    data = response.json()
    return data['title']

def get_serie_info(api_key_overseerr, tvdb_id):
    url = 'http://192.168.1.28:5055/api/v1/tv/{TVDBID}'
    url = url.replace('{TVDBID}', str(tvdb_id))

    headers = {'X-Api-Key': api_key_overseerr}
    
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('log/api_error.log', 'a') as f:
            f.write(date + " - Get serie info status code: " + str(response.status_code) + "\n")
        webhook_discord_error(discord_webhook_error, "Get serie info status code", str(response.status_code), date)

    response = requests.get(url, headers=headers)

    data = response.json()
    return data['originalName']

def setup(api_key_overseerr):

    url = 'http://192.168.1.28:5055/api/v1/request?take=10000&skip=0&filter=all&sort=added'
    headers = {'X-Api-Key': api_key_overseerr}

    response = requests.get(url, headers=headers)
    data = response.json()
    
    #print("Get all requests status code: " + str(response.status_code))
    if response.status_code != 200:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('log/api_error.log', 'a') as f:
            f.write(date + " - Get all requests status code: " + str(response.status_code) + "\n")
        webhook_discord_error(discord_webhook_error, "Get all requests status code", str(response.status_code), date)

    return data, api_key_overseerr

def save_requests(data, api_key_overseerr):
    thirty_days_ago_movie = datetime.now() - timedelta(days=number_movie)
    thirty_days_ago_serie = datetime.now() - timedelta(days=number_serie)

    element = []

    for request in data['results']:

        if 'mediaAddedAt' in request['media']:
            if request['media']['mediaAddedAt'] == None:
                continue
            updated_at = datetime.strptime(request['media']['mediaAddedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
        elif 'mediaAddedAt' in request:
            if request['mediaAddedAt'] == None:
                continue
            updated_at = datetime.strptime(request['mediaAddedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")

        if (updated_at <= thirty_days_ago_movie and request['type'] == 'movie') or (updated_at <= thirty_days_ago_serie and request['type'] == 'tv'):
            request_id = request['id']
            tmdb_id = request['media']['tmdbId']
            tvdb_id = request['media']['tvdbId']
            media_id = request['media']['id']
            modification_date = updated_at.strftime("%Y-%m-%d %H:%M:%S")
            typeElement = request['type']
            statusElement = request['media']['status']
            Element4k = request['is4k']

            if request['media']['status'] not in [5,4]:
                continue

            if request['type'] == 'movie':
                if url_radarr != False:
                    if request['rootFolder'] != None and url_radarr.lower() not in request['rootFolder'].lower():
                        continue
                name = get_movie_info(api_key_overseerr, tmdb_id)
            if request['type'] == 'tv':
                if url_sonarr != False:
                    if request['rootFolder'] != None and url_sonarr.lower() not in request['rootFolder'].lower():
                        continue
                #name = get_serie_info(api_key_overseerr, tvdb_id)
                name = request['media']['externalServiceSlug']

            webhook_discord_remove(discord_webhook_info, name, typeElement, modification_date)
            
            element.append([request_id, tmdb_id, modification_date, typeElement, media_id, statusElement, tvdb_id, Element4k, name])
    
    return element

# Importation des données depuis le fichier JSON
with open('settings.json', 'r') as json_file:
    variables = json.load(json_file)

# Accès aux variables importées
api_key_radarr = variables['api_key_radarr']
api_key_overseerr = variables['api_key_overseerr']
api_key_sonarr = variables['api_key_sonarr']

number_movie = variables['days_max_movie']
number_serie = variables['days_max_serie']
waiting_time = variables['waiting_time']
start_in = variables['start_in']
is4k_movie = variables['is4k_movie']
is4k_serie = variables['is4k_serie']

discord_webhook_info = variables['discord_webhook_info']
discord_webhook_error = variables['discord_webhook_error']

start_all_day = variables['start_all_day']

url_sonarr = variables['url_sonarr']
url_radarr = variables['url_radarr']

if start_all_day == False:
    ActualTime = datetime.now() + timedelta(hours=start_in)
    print("Start in: " + ActualTime.strftime("%Y-%m-%d %H:%M:%S"))
    time.sleep(start_in * 3600)
else:
    try:
        scanTime = datetime.strptime(start_all_day, "%H:%M")
    except:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('log/fatal_error.log', 'a') as f:
            f.write(date + " - " + "Error in start_all_day variable" + "\n")
    
    ActualTime = datetime.now()
    ActualTime = ActualTime.replace(hour=scanTime.hour, minute=scanTime.minute, second=0, microsecond=0)
    if ActualTime < datetime.now():
        ActualTime = ActualTime + timedelta(days=1)
    print("Start in: " + ActualTime.strftime("%Y-%m-%d %H:%M:%S"))
    time.sleep((ActualTime - datetime.now()).seconds)


while True:
    try:
        data, api_key_overseerr = setup(api_key_overseerr)
        remove_element_count_movie = 0
        remove_element_count_serie = 0

        element = save_requests(data, api_key_overseerr)
            
        #print(save_requests(data))
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('log/delete_movie.log', 'a') as f:
            f.write(date + " - Movie to delete: " + str(element) + "\n")

        for elt in element:
            if elt[3] == 'movie':
                if is4k_movie == True and elt[7] == False:
                    continue
                remove_element_count_movie += 1
                if radarr_delete(api_key_radarr, elt[1], discord_webhook_error) == False:
                    remove_element_count_movie -= 1
                    continue
                overseerr_delete(api_key_overseerr, elt[1], elt[4], discord_webhook_error)
            if elt[3] == 'tv':
                if is4k_movie == True and elt[7] == False:
                    continue
                remove_element_count_serie += 1
                if sonarr_delete(api_key_sonarr, elt[6], discord_webhook_error) == False:
                    remove_element_count_serie -= 1
                    continue
                overseerr_delete(api_key_overseerr, elt[1], elt[4], discord_webhook_error)

        if remove_element_count_movie > 0:
            restart_radarr(api_key_radarr, discord_webhook_error)
        
        if remove_element_count_serie > 0:
            restart_sonarr(api_key_sonarr, discord_webhook_error)
        
        if start_all_day == False:
            ActualTime = datetime.now() + timedelta(hours=waiting_time)
            print("Restart in: " + ActualTime.strftime("%Y-%m-%d %H:%M:%S"))
            time.sleep(waiting_time * 3600)
        else:
            ActualTime = datetime.now()
            ActualTime = ActualTime.replace(hour=scanTime.hour, minute=scanTime.minute, second=0, microsecond=0)
            if ActualTime < datetime.now():
                ActualTime = ActualTime + timedelta(days=1)
            print("Restart in: " + ActualTime.strftime("%Y-%m-%d %H:%M:%S"))
            time.sleep((ActualTime - datetime.now()).seconds)

    except Exception as e:

        error_line = "Error line: {}".format(sys.exc_info()[-1].tb_lineno)

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('log/fatal_error.log', 'a') as f:
            f.write(date + " - " + str(e) + "\n")
            f.write(date + " - " + error_line + "\n")

        #Start discord webhook
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        webhook_discord_error(discord_webhook_error, "Error", str(e) + "\n" + error_line, date)

        if start_all_day == False:
            ActualTime = datetime.now() + timedelta(hours=waiting_time)
            print("Restart in: " + ActualTime.strftime("%Y-%m-%d %H:%M:%S"))
            time.sleep(waiting_time * 3600)
        else:
            ActualTime = datetime.now()
            ActualTime = ActualTime.replace(hour=scanTime.hour, minute=scanTime.minute, second=0, microsecond=0)
            if ActualTime < datetime.now():
                ActualTime = ActualTime + timedelta(days=1)
            print("Restart in: " + ActualTime.strftime("%Y-%m-%d %H:%M:%S"))
            time.sleep((ActualTime - datetime.now()).seconds)

