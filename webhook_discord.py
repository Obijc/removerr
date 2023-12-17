import requests

from datetime import datetime

def webhook_discord_remove(discord_webhook, title_remove, type_remove, date_remove):
    url = discord_webhook
    data = {
        "embeds": [{
            "title": "Item Removal Notification",
            "description": "An item has been removed from the listing.",
            "color": 32776,
            "fields": [
                {
                    "name": "Type",
                    "value": type_remove,
                    "inline": True
                },
                {
                    "name": "Title",
                    "value": title_remove,
                    "inline": True
                },
                {
                    "name": "Date of Request",
                    "value": date_remove,
                    "inline": False
                }
            ],
            "footer": {
                "text": "Removal processed on " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }]
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 204:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('log/api_error_webhook.log', 'a') as f:
            f.write(date + " - Webhook Discord status code: " + str(response.status_code) + "\n")

def webhook_discord_error(discord_webhook, error_type, error_message, error_date):
    url = discord_webhook
    data = {
        "embeds": [{
            "title": "Error Notification",
            "description": "An error has been detected.",
            "color": 16711680,
            "fields": [
                {
                    "name": "Type",
                    "value": error_type,
                    "inline": True
                },
                {
                    "name": "Message",
                    "value": error_message,
                    "inline": True
                },
                {
                    "name": "Date of Removal",
                    "value": error_date,
                    "inline": False
                }
            ],
            "footer": {
                "text": "Error detected on " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }]
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 204:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('log/api_error_webhook.log', 'a') as f:
            f.write(date + " - Webhook Discord error status code: " + str(response.status_code) + "\n")