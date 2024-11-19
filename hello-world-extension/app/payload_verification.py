
import base64
import os
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature
from .github_api import fetch_copilot_public_key

class VerificationRequestError(Exception):
    pass

def verify_request(request, github_token):
    """
    Verifies the integrity and authenticity of a GitHub webhook request.

    Skips verification if SKIP_PAYLOAD_VERIFICATION env variable is defined (for local debugging).

    Args:
        request (Request): The incoming request object containing headers and data.
        github_token (str): The GitHub token used to fetch the public key.
    Returns:
        bool: True if the request is verified successfully, False otherwise.
    Raises:
        VerificationRequestError: If no public key is found matching the key identifier.
    The function performs the following checks:
    1. Ensures the request body is not empty.
    2. Retrieves the 'Github-Public-Key-Identifier' and 'Github-Public-Key-Signature' from the request headers.
    3. Fetches the public key using the provided GitHub token and key identifier.
    4. Loads the public key and verifies the signature against the request data using ECDSA with SHA-256.

    See https://docs.github.com/en/copilot/building-copilot-extensions/building-a-copilot-agent-for-your-copilot-extension/configuring-your-copilot-agent-to-communicate-with-github#verifying-that-payloads-are-coming-from-github for more information.
    """
    
    if os.getenv('SKIP_PAYLOAD_VERIFICATION'):
        return True
        
    if not request.data:
        return False
    
    key_identifier = request.headers.get('Github-Public-Key-Identifier')
    signature = request.headers.get('Github-Public-Key-Signature')
    if not key_identifier or not signature:
        return False

    public_key = fetch_copilot_public_key(github_token, key_identifier)
    if not public_key:
        raise VerificationRequestError(f"No public key found matching key identifier: {key_identifier}")  
   
    # Load the public key
    public_key_obj = serialization.load_pem_public_key(public_key.encode())
   
    try:
        public_key_obj.verify(
            base64.b64decode(signature),
            request.data,
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except InvalidSignature:
        return False