import os
import json
import base64
import gzip
import boto3
import inspect
from discord_webhook import DiscordWebhook, DiscordEmbed

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
FAILED_ATTEMPT_THRESHOLD = 2
TIME_WINDOW_SECONDS = 120  # 2 minutes


# Initialize Bedrock client
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")


"""Send the detected threat to Bedrock for AI analysis."""
def analyze_with_bedrock(log_message, threat_type, severity):
    
    prompt = f"""You are a cybersecurity AI agent analyzing Linux auth logs.
        A {severity} severity threat was detected: {threat_type}

        Log entry:
        {log_message}

        Respond ONLY in this JSON format, nothing else (do not wrap its response in markdown code fences):
        {{
        "summary": "one sentence explaining what happened",
        "likely_attack": "e.g. brute force, credential stuffing, etc.",
        "recommended_action": "e.g. block IP, monitor, investigate",
        "ip_address": "extract IP from log or null if not found"
        }}"""

    response = bedrock.invoke_model(
        modelId="us.anthropic.claude-sonnet-4-6",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": inspect.cleandoc(prompt)}]
        })
    )

    result = json.loads(response["body"].read())
    raw_text = result["content"][0]["text"]

    # Safely parse the JSON response from Bedrock
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "summary": raw_text,
            "likely_attack": "Unknown",
            "recommended_action": "Manual review needed",
            "ip_address": None
        }


def webhook_embed(title, message_description, color=None):
    webhook = DiscordWebhook(url=WEBHOOK_URL)
    embed = DiscordEmbed(
        title=title,
        description=message_description,
        color='03b2f8')
    webhook.add_embed(embed)
    webhook.execute()


def analyze_auth_log(log_message):
    message = log_message.lower()

    threat = {
        'failed_login': {
            'keywords': ['failed password', 'authentication failure'],
            'color': 'orange',
            'severity': 'MEDIUM'
        }
    }

    for threat_type, threat_info in threat.items():
        if any(keyword in message for keyword in threat_info['keywords']):
            return {
                'is_threat': True,
                'type': threat_type,
                'detection': threat_info['keywords'],
                'color': threat_info['color'],
                'severity': threat_info['severity']
            }

    return {'is_threat': False}

def check_threshold_in_window(events, threshold, window_seconds):
    """
    Returns (triggered, matching_events) if `threshold` events occur
    within `window_seconds` of each other using a sliding window.
    """
    if len(events) < threshold:
        return False, []

    # Events from CloudWatch are in milliseconds
    sorted_events = sorted(events, key=lambda e: e['timestamp'])

    for i in range(len(sorted_events) - threshold + 1):
        window_start = sorted_events[i]['timestamp']
        window_end = sorted_events[i + threshold - 1]['timestamp']

        elapsed_seconds = (window_end - window_start) / 1000  # ms → seconds

        if elapsed_seconds <= window_seconds:
            # Return the events that triggered the alert
            return True, sorted_events[i:i + threshold]

    return False, []

def lambda_handler(event, context):
    print("Running...")

    try:
        compressed_data = base64.b64decode(event['awslogs']['data'])
        log_data = json.loads(gzip.decompress(compressed_data))

        log_events = log_data['logEvents']
        log_group = log_data['logGroup']

        suspicious_events = []

        for log_event in log_events:
            message = log_event['message']
            threat_analysis = analyze_auth_log(message)

            if threat_analysis['is_threat']:
                suspicious_events.append({
                    'timestamp': log_event['timestamp'],
                    'message': message,
                    'threat_type': threat_analysis['type'],
                    'detection': threat_analysis['detection'],
                    'severity': threat_analysis['severity'],
                    'color': threat_analysis['color'],
                })

        # Group by threat type
        from collections import defaultdict
        threat_groups = defaultdict(list)
        for evt in suspicious_events:
            threat_groups[evt['threat_type']].append(evt)

        alerts_sent = 0
        for threat_type, events in threat_groups.items():

            triggered, window_events = check_threshold_in_window(
                events,
                threshold=FAILED_ATTEMPT_THRESHOLD,
                window_seconds=TIME_WINDOW_SECONDS
            )

            if triggered:
                latest = window_events[-1]
                first = window_events[0]
                elapsed = (latest['timestamp'] - first['timestamp']) / 1000

                ai_analysis = analyze_with_bedrock(
                    log_message=latest['message'],
                    threat_type=latest['threat_type'],
                    severity=latest['severity']
                )

                title = f"🚨 {latest['severity']} ALERT: {latest['threat_type'].upper()} ({len(window_events)} attempts in {int(elapsed)}s)"
                description = inspect.cleandoc(f"""
                **Threat Type:** {latest['threat_type']}
                **Attempts Detected:** {len(window_events)} in {int(elapsed)} seconds
                **Detection:** {', '.join(latest['detection'])}

                **__AI Analysis__**
                **Summary:** \n{ai_analysis.get('summary', 'N/A')}\n
                **Attack Type:** \n{ai_analysis.get('likely_attack', 'N/A')}\n
                **Recommended Action:** \n{ai_analysis.get('recommended_action', 'N/A')}\n
                **IP Address:** \n{ai_analysis.get('ip_address') or 'Not found'}
                """)

                webhook_embed(title=title, message_description=description, color=latest['color'])
                alerts_sent += 1

        return {
            'statusCode': 200,
            'body': json.dumps(f'Sent {alerts_sent} alerts' if alerts_sent else 'No threshold breaches detected')
        }

    except Exception as e:
        print(f"Error: {e}")
        webhook_embed(title="Lambda Error", message_description=f"Error analyzing logs: {str(e)}", color='ff0000')
        return {'statusCode': 500, 'body': json.dumps(f'Error: {str(e)}')}