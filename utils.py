import re
from aqt import mw
from urllib.parse import urlparse

# Default settings for the add-on
DEFAULT_SETTINGS = {
    "buttons": [
        {"label": "Google", "url": "https://www.google.com/search?q=%s", "enabled": True},
        {"label": "Wiktionary", "url": "https://en.wiktionary.org/wiki/%s", "enabled": True}
    ],
    "shortcut": "Ctrl+Shift+S",
    "auto_popup_enabled": True,  # Enable/disable auto-popup
    "auto_popup_delay": 1000  # Delay in milliseconds for the auto-popup
}


def load_settings():
    """
    Load the settings for the add-on. If no settings are found, initialize with default settings.
    """
    settings = mw.addonManager.getConfig(__name__)
    if settings is None:
        settings = DEFAULT_SETTINGS
        mw.addonManager.writeConfig(__name__, settings)
    return settings


def save_settings(settings):
    """
    Save the settings for the add-on.
    """
    mw.addonManager.writeConfig(__name__, settings)


def validate_url(url):
    """
    Validate the URL format. Ensure it starts with 'http://' or 'https://' and contains exactly one '%s' placeholder.
    """
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return "Invalid URL format. Please enter a valid URL starting with 'http://' or 'https://'."
        if url.count("%s") != 1:
            return "The URL must contain exactly one '%s' placeholder."
        return None
    except Exception as e:
        return f"Invalid URL format: {str(e)}"
