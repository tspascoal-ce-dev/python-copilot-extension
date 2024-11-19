import os
from flask import Blueprint, request, jsonify, Response, current_app as App
from ..github_api import get_github_user_login
from ..payload_verification import verify_request

agent_bp = Blueprint('agent', __name__)

@agent_bp.route('/agent', methods=['POST'])
def handle_agent():
    """
    Handle POST requests to the /agent endpoint.
    This function performs the following steps:
    1. Logs the incoming request data.
    2. Retrieves the GitHub token from the request headers.
    3. Validates the presence of the GitHub token.
    4. Validates the request body signature using the GitHub token.
    5. Extracts and validates the agent name from the request body.
    6. Retrieves the GitHub user login associated with the token.
    7. Generates a server-sent event (SSE) response with a greeting message.
    Returns:
        Response: A server-sent event (SSE) response containing a greeting message
    
    We do not process any received SSE, we basically ignore it. But if we wanted to,
    here is the reference to the docs https://docs.github.com/en/copilot/building-copilot-extensions/building-a-copilot-agent-for-your-copilot-extension/configuring-your-copilot-agent-to-communicate-with-the-copilot-platform#receiving-server-sent-events
    """

    data = request.get_json()

    App.logger.debug(request.data)

    App.logger.info('Getting Token')
    github_token = request.headers.get('X-Github-Token')
    
    # fail if there is no token
    if not github_token:
        return jsonify({'error': 'No GitHub token provided'}), 401
    
    App.logger.info('Validating Message')

    # Validate if the body is signed with a GitHub public key
    if not verify_request(request, github_token):
        return jsonify({'error': 'Invalid signature'}), 401

    agent_name = data['agent']

    App.logger.info('Validating Agent Name')

    if not validate_agent_name(agent_name):
        return jsonify({'error': 'Invalid agent'}), 400
    
    App.logger.info('Getting GitHub Login')

    github_login = get_github_user_login(github_token)  

    App.logger.info(f'Responding to user [{github_login}] from agent [{agent_name}]')  

    # Generate a server-sent event (SSE) response is hardcoded. In case you want to send other events or events, these
    # are the docs to follow:
    # https://docs.github.com/en/copilot/building-copilot-extensions/building-a-copilot-agent-for-your-copilot-extension/configuring-your-copilot-agent-to-communicate-with-the-copilot-platform#sending-server-sent-events
    # if the response takes time to generate and initial empty message to show user progress and then stream the responses
    def generate():
        yield f'data: {{"choices":[{{"index":0,"delta":{{"content":"Hello {github_login} from {agent_name}","role":"assistant"}}}}]}}\n\n'
        yield 'data: {"choices":[{"index":0,"finish_reason":"stop","delta":{"content":null}}]}\n'
        yield 'data: [DONE]\n'

    return Response(generate(), content_type='text/event-stream')

def validate_agent_name(agent_name):
    """
    Validates the provided agent name against the environment variable 'COPILOT_AGENT_NAME'.

    If no variable is set (not recommeded), no validation is performed.
    Args:
        agent_name (str): The name of the agent to validate.
    Returns:
        bool: True if the agent name matches the environment variable or if the environment variable is not set.
    """
    copilot_agent_name = os.getenv('COPILOT_AGENT_NAME')
    # As a best practice we should really NOT skip the validation of the agent name
    if not copilot_agent_name:
        return True
    
    if agent_name == copilot_agent_name:
        return True
    
    return False

