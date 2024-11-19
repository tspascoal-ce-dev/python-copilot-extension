import requests

USER_AGENT = 'python-copilot-sample/1.0'

def build_headers(github_token):
    return {
        'Authorization': f'Bearer {github_token}',
        'User-Agent': USER_AGENT
    }

def get_github_user_login(github_token):
    headers = build_headers(github_token)
    response = requests.get('https://api.github.com/user', headers=headers)
    return response.json().get('login')

# TODO: this should be cached
def fetch_copilot_public_key(github_token, key_identifier):
    """
    Fetches the public key for GitHub Copilot API using the provided GitHub token and key identifier.
    Args:
        github_token (str): The GitHub token used for authentication.
        key_identifier (str): The identifier of the public key to fetch.
    Returns:
        str or None: The public key if found, otherwise None.
    """

    headers = build_headers(github_token)
    # Fetch public keys
    response = requests.get('https://api.github.com/meta/public_keys/copilot_api', headers=headers)
    public_keys = response.json().get('public_keys', [])
    
    # Find the correct public key
    for key in public_keys:
        if key['key_identifier'] == key_identifier:
            return key['key']
    return None