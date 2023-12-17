import requests, os, time

from datetime import datetime
from webhook_discord import *

def tmdbId_to_movieId_radarr(api_key_radarr, tmdbId, discord_webhook_error):
    headers = {'X-Api-Key': api_key_radarr}
    urlmovie = 'http://192.168.1.15:7878/api/v3/movie?tmdbId={TMDBID}&excludeLocalCovers=false'
    urlmovie = urlmovie.replace('{TMDBID}', str(tmdbId))

    response = requests.get(urlmovie, headers=headers)

    if response.status_code != 200:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('log/api_error.log', 'a') as f:
            f.write(date + " - Get movie status code in Radarr: " + str(response.status_code) + "\n")
        webhook_discord_error(discord_webhook_error, "Get movie status code in Radarr", str(response.status_code), date)
        return None, None, None

    data = response.json()

    if len(data) == 0:
        return None, None, None

    moviename = data[0]['title']
    movieid = data[0]['id']
    moviefolder = data[0]['path']

    return movieid, moviename, moviefolder

def queue_radarr(api_key_radarr, discord_webhook_error):
    #regturn true or false if queue is empty or not
    url_queue = 'http://192.168.1.15:7878/api/v3/queue/'

    headers = {'X-Api-Key': api_key_radarr}
    response = requests.get(url_queue, headers=headers)

    if response.status_code != 200:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('log/api_error.log', 'a') as f:
            f.write(date + " - Get queue status code in Radarr: " + str(response.status_code) + "\n")
        webhook_discord_error(discord_webhook_error, "Get queue status code in Radarr", str(response.status_code), date)
        return True
    else:
        data = response.json()
        if len(data["records"]) == 0:
            return False
        else:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open('log/data.log', 'a') as f:
                f.write(date + " - Queue is not empty in Radarr - " + str(data) + "\n")
            webhook_discord_error(discord_webhook_error, "Queue is not empty in Radarr", str(data), date)
            return True

def restart_radarr(api_key_radarr, discord_webhook_error):
    url_restart = 'http://192.168.1.15:7878/api/v3/system/restart'

    time.sleep(5)

    if queue_radarr(api_key_radarr ,discord_webhook_error):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('log/queue_error.log', 'a') as f:
            f.write(date + " - Queue is not empty in Radarr\n")
        webhook_discord_error(discord_webhook_error, "Queue is not empty in Radarr", "", date)
        return

    headers = {'X-Api-Key': api_key_radarr}
    response = requests.post(url_restart, headers=headers)

    #print("Restarting Radarr status code: " + str(response.status_code))
    if response.status_code != 200:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('log/api_error.log', 'a') as f:
            f.write(date + " - Restarting Radarr status code: " + str(response.status_code) + "\n")
        webhook_discord_error(discord_webhook_error, "Restarting Radarr status code", str(response.status_code), date)

def radarr_delete(api_key_radarr, tmdbId, discord_webhook_error):

    movieid, moviename, moviefolder = tmdbId_to_movieId_radarr(api_key_radarr, tmdbId, discord_webhook_error)

    if movieid is None or moviename is None or moviefolder is None:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('log/error.log', 'a') as f:
            f.write(date + " - Value is None in radarr: " + str(movieid) + " " + str(moviename) + " " + str(moviefolder) + "\n")
        webhook_discord_error(discord_webhook_error, "Value is None in radarr", str(movieid) + " " + str(moviename) + " " + str(moviefolder), date)
    else:
        # Delete the folder with all the files in it
        moviefolderSys = moviefolder.replace('\\', '/')
        
        if os.path.exists(moviefolderSys):
            #print("Deleting folder: " + moviefolder)
            os.system('rmdir /S /Q "{}"'.format(moviefolderSys))
            time.sleep(5)
            if os.path.exists(moviefolderSys):
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open('log/error.log', 'a') as f:
                    f.write(date + " - Folder not deleted because users are connected: " + moviefolderSys + "\n")
                webhook_discord_error(discord_webhook_error, "Folder not deleted because users are connected", moviefolderSys, date)
                return False
        else:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open('log/error.log', 'a') as f:
                f.write(date + " - Folder not found: " + moviefolderSys + "\n")
            webhook_discord_error(discord_webhook_error, "Folder not found in radarr", moviefolderSys, date)
            return
        url_delete = 'http://192.168.1.15:7878/api/v3/movie/{NUMBER}?addImportExclusion=false&apikey={APIKEY}'
        url_delete = url_delete.replace('{APIKEY}', api_key_radarr)
        url_delete = url_delete.replace('{NUMBER}', str(movieid))

        headers = {'X-Api-Key': api_key_radarr}
        response = requests.delete(url_delete, headers=headers)

        #print("Deleting movie status code: " + str(response.status_code))
        if response.status_code != 200:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open('log/api_error.log', 'a') as f:
                f.write(date + " - Deleting movie status code in Radarr: " + str(response.status_code) + "\n")
            webhook_discord_error(discord_webhook_error, "Deleting movie status code in Radarr", str(response.status_code), date)