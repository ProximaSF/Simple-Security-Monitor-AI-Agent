import os
import json
import inspect
from discord_webhook import DiscordWebhook, DiscordEmbed

# Get webhook URL from Lambda environment variables instead of .env file
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
WEBHOOK_URL = "https://discord.com/api/webhooks/1479741984666157056/x9zkWqoZLMznkmVeEd4ssfr5eyC8sU0EutAr0MBMTWJqeG4gYYXHV2Wa-m4ERIGNUe8Q"
def webhook_embed(title, message_description, color=None):
    webhook = DiscordWebhook(url=WEBHOOK_URL)
    embed = DiscordEmbed(
        title=title, 
        description=message_description,
        color='03b2f8')
    webhook.add_embed(embed)
    webhook.execute()
    return

def analyze_auth_log(log_message):
    message = log_message.lower()

    # Detect threat patters
    threat = {
        'failed_login': {
            'keywords': ['Failed password', "authentication failure"],
            'color': "orange",
            'security level': 'MEDIUM'
    }}

    for threat_type, threat_info in threat.items():
        if any(keyword in log_message for keyword in threat_info['keywords']):
            return {
                'type': threat_type,
                'detection': threat_info['keywords'],
                'color': threat_info['color'],
                'security level': threat_info['security level'],
                'threat': True
                }
        
        return False

def read_log():
    file_path = "auth.log"
    with open(file_path, "r", encoding='utf-8') as f:
        log_content = f.read()
        return log_content
    
def main():
    log_message = read_log()
    threat_overview = analyze_auth_log(log_message)
    print(threat_overview)
    if threat_overview['threat']:
        title = "Threat Overview"
        message_description = inspect.cleandoc(f"""
                                               Threat Type: {threat_overview['type']}
                                               Threat Detection: {threat_overview['detection']}
                                               """)
        color = threat_overview['color']
        webhook_embed(title, message_description, color)
    else:
        title = "Threat Overview"
        message_description = f"No threat found"
        webhook_embed(title, message_description)



main()

"""REQUIRED FUNCTION TO RUN"""
def lambda_handler(event, context):
    try:
        title = "TESTING"
        message_description = "TESTING123"
        webhook_embed(title, message_description)
        
        return {
            'statusCode': 200,
            'body': json.dumps('Message sent successfully')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }