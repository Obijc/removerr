import requests, os, time

from datetime import datetime
from webhook_discord import *

def tvdbId_to_serieId_sonarr(api_key_sonarr, tvdbId, discord_webhook_error):
    headers = {'X-Api-Key': api_key_sonarr}
    urlserie = 'http://192.168.1.15:8989/api/v3/series?tvdbId={TVDBID}&includeSeasonImages=false'
    urlserie = urlserie.replace('{TVDBID}', str(tvdbId))

    response = requests.get(urlserie, headers=headers)

    if response.status_code != 200:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('log/api_error.log', 'a') as f:
            f.write(date + " - Get serie status code in Sonarr: " + str(response.status_code) + "\n")
        webhook_discord_error(discord_webhook_error, "Get serie status code in Sonarr", str(response.status_code), date)
        return None, None, None

    data = response.json()

    if len(data) == 0:
        return None, None, None

    seriename = data[0]['title']
    serieid = data[0]['id']
    seriefolder = data[0]['path']

    return serieid, seriename, seriefolder

def queue_sonarr(api_key_sonarr, discord_webhook_error):
    #regturn true or false if queue is empty or not
    url_queue = 'http://192.168.1.15:8989/api/v3/queue/'

    headers = {'X-Api-Key': api_key_sonarr}
    response = requests.get(url_queue, headers=headers)

    if response.status_code != 200:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('log/api_error.log', 'a') as f:
            f.write(date + " - Get queue status code in Sonarr: " + str(response.status_code) + "\n")
        webhook_discord_error(discord_webhook_error, "Get queue status code in Sonarr", str(response.status_code), date)
        return True
    else:
        data = response.json()
        if len(data["records"]) == 0:
            return False
        else:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open('log/data.log', 'a') as f:
                f.write(date + " - Queue is not empty in Sonarr - " + str(data) + "\n")
            webhook_discord_error(discord_webhook_error, "Queue is not empty in Sonarr", str(data), date)
            return True

def restart_sonarr(api_key_sonarr, discord_webhook_error):
    url_restart = 'http://192.168.1.15:8989/api/v3/system/restart'

    time.sleep(5)

    if queue_sonarr(api_key_sonarr ,discord_webhook_error):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('log/queue_error.log', 'a') as f:
            f.write(date + " - Queue is not empty in Sonarr\n")
        webhook_discord_error(discord_webhook_error, "Queue is not empty in Sonarr", "", date)
        return

    headers = {'X-Api-Key': api_key_sonarr}
    response = requests.post(url_restart, headers=headers)

    #print("Restarting Sonarr status code: " + str(response.status_code))
    if response.status_code != 200:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('log/api_error.log', 'a') as f:
            f.write(date + " - Restarting Sonarr status code: " + str(response.status_code) + "\n")
        webhook_discord_error(discord_webhook_error, "Restarting Sonarr status code", str(response.status_code), date)

def sonarr_delete(api_key_sonarr, tvdbId, discord_webhook_error):

    serieid, seriename, seriefolder = tvdbId_to_serieId_sonarr(api_key_sonarr, tvdbId, discord_webhook_error)

    if serieid is None or seriename is None or seriefolder is None:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('log/error.log', 'a') as f:
            f.write(date + " - Value is None in Sonarr: " + str(serieid) + " " + str(seriename) + " " + str(seriefolder) + "\n")
        webhook_discord_error(discord_webhook_error, "Value is None in Sonarr", str(serieid) + " " + str(seriename) + " " + str(seriefolder), date)
    else:
        # Delete the folder with all the files in it
        seriefolderSys = seriefolder.replace('\\', '/')
        
        if os.path.exists(seriefolderSys):
            #print("Deleting folder: " + seriefolder)
            os.system('rmdir /S /Q "{}"'.format(seriefolderSys))
            time.sleep(5)
            if os.path.exists(seriefolderSys):
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open('log/error.log', 'a') as f:
                    f.write(date + " - Folder not deleted because users are connected: " + seriefolderSys + "\n")
                webhook_discord_error(discord_webhook_error, "Folder not deleted because users are connected", seriefolderSys, date)
                return False
        else:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open('log/error.log', 'a') as f:
                f.write(date + " - Folder not found: " + seriefolderSys + "\n")
            webhook_discord_error(discord_webhook_error, "Folder not found in Sonarr", seriefolderSys, date)
            return
        
        url_delete = 'http://192.168.1.15:8989/api/v3/series/{NUMBER}?deleteFiles=false&addImportListExclusion=false'
        url_delete = url_delete.replace('{NUMBER}', str(serieid))

        headers = {'X-Api-Key': api_key_sonarr}
        response = requests.delete(url_delete, headers=headers)

        #print("Deleting serie status code: " + str(response.status_code))
        if response.status_code != 200:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open('log/api_error.log', 'a') as f:
                f.write(date + " - Deleting serie status code in Sonarr: " + str(response.status_code) + "\n")
            webhook_discord_error(discord_webhook_error, "Deleting serie status code in Sonarr", str(response.status_code), date)