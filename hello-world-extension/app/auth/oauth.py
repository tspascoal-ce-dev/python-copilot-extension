from flask import Blueprint, redirect, request, url_for

oauth_bp = Blueprint('oauth', __name__)

@oauth_bp.route('/callback-no-oauth')
def callback_no_oauth():
    """
    Handles the callback for a scenario where OAuth is not used.

    This is the URL you configure in the Github App "Callback URL" under the section  "Identifying and authorizing users"

    Returns:
        str: A message indicating that the user is logged in and can close the window.
    """

    return "You are now logged in. You can close this window and start using the extension"

