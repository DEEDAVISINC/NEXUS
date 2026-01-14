"""
Alexa Skill for NEXUS Government Contracting System
AWS Lambda function that handles Alexa voice commands
"""

import json
import requests
import os
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# NEXUS API configuration
NEXUS_API_URL = os.environ.get('NEXUS_API_URL', 'https://nexus-backend.onrender.com')
ALEXA_SKILL_ID = os.environ.get('ALEXA_SKILL_ID')

# JWT token for authentication (cached)
jwt_token = None

def get_jwt_token():
    """Get JWT token for NEXUS API authentication"""
    global jwt_token

    if jwt_token:
        return jwt_token

    try:
        headers = {'Alexa-Skill-Id': ALEXA_SKILL_ID}
        response = requests.post(f"{NEXUS_API_URL}/auth/alexa", headers=headers)

        if response.status_code == 200:
            data = response.json()
            jwt_token = data.get('token')
            return jwt_token
        else:
            logger.error(f"Failed to get JWT token: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error getting JWT token: {str(e)}")
        return None

def call_nexus_api(command):
    """Call NEXUS API with voice command"""
    token = get_jwt_token()
    if not token:
        return "Sorry, I couldn't authenticate with your NEXUS system."

    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        payload = {
            'command': command,
            'source': 'alexa'
        }

        response = requests.post(
            f"{NEXUS_API_URL}/alexa/command",
            json=payload,
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            return data.get('response', 'Command processed successfully.')
        else:
            logger.error(f"NEXUS API error: {response.status_code} - {response.text}")
            return "Sorry, I had trouble connecting to your NEXUS system."

    except requests.exceptions.Timeout:
        return "Sorry, the request timed out. Please try again."
    except Exception as e:
        logger.error(f"Error calling NEXUS API: {str(e)}")
        return "Sorry, I encountered an error. Please try again."

def lambda_handler(event, context):
    """Main Alexa skill handler"""
    try:
        logger.info(f"Received Alexa event: {json.dumps(event)}")

        # Extract intent information
        request_type = event['request']['type']

        if request_type == 'LaunchRequest':
            return build_response(
                "Welcome to ALEXIS NEXUS. I can help you manage opportunities, contacts, and more. What would you like to do?",
                should_end_session=False
            )

        elif request_type == 'IntentRequest':
            intent_name = event['request']['intent']['name']

            if intent_name == 'CreateOpportunityIntent':
                return handle_create_opportunity(event)
            elif intent_name == 'CreateContactIntent':
                return handle_create_contact(event)
            elif intent_name == 'GetStatusIntent':
                return handle_get_status(event)
            elif intent_name == 'AMAZON.HelpIntent':
                return handle_help()
            elif intent_name == 'AMAZON.StopIntent' or intent_name == 'AMAZON.CancelIntent':
                return build_response("Goodbye!")
            else:
                return build_response("I'm not sure how to help with that. Try asking about opportunities or contacts.")

        elif request_type == 'SessionEndedRequest':
            return build_response("Session ended.")

        else:
            return build_response("I didn't understand that request.")

    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return build_response("Sorry, I encountered an error. Please try again.")

def handle_create_opportunity(event):
    """Handle opportunity creation intent"""
    slots = event['request']['intent'].get('slots', {})

    # Extract slot values
    title = get_slot_value(slots, 'title')
    value = get_slot_value(slots, 'value')
    agency = get_slot_value(slots, 'agency')

    # Build command for NEXUS
    command = f"create opportunity"
    if title:
        command += f": {title}"
    if value:
        command += f" value: ${value}"
    if agency:
        command += f" agency: {agency}"

    response = call_nexus_api(command)

    if "successfully" in response.lower():
        return build_response(f"✅ {response}")
    else:
        return build_response(f"I tried to create an opportunity, but {response}")

def handle_create_contact(event):
    """Handle contact creation intent"""
    slots = event['request']['intent'].get('slots', {})

    # Extract slot values
    name = get_slot_value(slots, 'name')
    email = get_slot_value(slots, 'email')
    phone = get_slot_value(slots, 'phone')

    # Build command for NEXUS
    command = f"add contact"
    if name:
        command += f" {name}"
    if email:
        command += f" {email}"
    if phone:
        command += f" {phone}"

    response = call_nexus_api(command)

    if "successfully" in response.lower() or "added" in response.lower():
        return build_response(f"✅ {response}")
    else:
        return build_response(f"I tried to add a contact, but {response}")

def handle_get_status(event):
    """Handle status request intent"""
    response = call_nexus_api("status")
    return build_response(response)

def handle_help():
    """Handle help intent"""
    help_text = """
    I can help you manage your NEXUS government contracting system. Try saying:

    "Alexa, tell ALEXIS NEXUS to create opportunity for website redesign worth 50,000 dollars for GSA"
    "Alexa, ask ALEXIS NEXUS to add contact John Smith at john@gsa.gov"
    "Alexa, ask ALEXIS NEXUS what's my status"
    "Alexa, ask ALEXIS NEXUS how am I doing"

    What would you like to do?
    """

    return build_response(help_text, should_end_session=False)

def get_slot_value(slots, slot_name):
    """Extract value from Alexa slot"""
    slot = slots.get(slot_name)
    if slot and slot.get('value'):
        return slot['value']
    return None

def build_response(speech_text, should_end_session=True):
    """Build Alexa response"""
    return {
        'version': '1.0',
        'response': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': speech_text
            },
            'shouldEndSession': should_end_session
        }
    }