import re
from aqt import mw
from urllib.parse import urlparse
from aqt.utils import showWarning
from aqt.qt import QShortcut, QAction

# Default settings for the add-on
DEFAULT_SETTINGS = {
    "buttons": [
        {"label": "Google", "url": "https://www.google.com/search?q=%s", "enabled": True},
        {"label": "Wiktionary", "url": "https://en.wiktionary.org/wiki/%s", "enabled": True},
        {"label": "Oxford", "url": "https://www.oxfordlearnersdictionaries.com/us/search/english/?q=%s", "enabled": True},
        {"label": "YouGlish",
            "url": "https://youglish.com/pronounce/%s/english/us?", "enabled": True},
        {"label": "Google Images",
            "url": "https://www.google.com/search?tbm=isch&q=%s", "enabled": True},
        {"label": "DeepL(en-ja)",
         "url": "https://www.deepl.com/en/translator#en/ja/%s", "enabled": True},
    ],
    "shortcut": "Ctrl+Shift+S",
    "auto_popup_enabled": True,  # Enable/disable auto-popup
    "auto_popup_delay": 1000  # Delay in milliseconds for the auto-popup
}


def get_existing_shortcuts():
    """
    Retrieve existing shortcut keys registered by Anki or other add-ons.
    Excludes the shortcut key used by this add-on.
    """
    existing_shortcuts = set()

    # Get default shortcut keys from Anki
    for action in mw.findChildren(QAction):
        if action.shortcut():
            shortcut = action.shortcut().toString()
            existing_shortcuts.add(shortcut)

    # Get shortcut keys registered by other add-ons
    for child in mw.findChildren(QShortcut):
        if child.key().toString():
            # Exclude this add-on's shortcut
            if not hasattr(child, "objectName") or child.objectName() != "search_selected_text_shortcut":
                shortcut = child.key().toString()
                existing_shortcuts.add(shortcut)

    return existing_shortcuts


def check_shortcut_conflict(new_shortcut):
    """
    Check if the new shortcut key conflicts with existing shortcut keys.
    """
    existing_shortcuts = get_existing_shortcuts()
    if new_shortcut in existing_shortcuts:
        showWarning(
            f"The shortcut '{new_shortcut}' is already in use. "
            "Please choose a different shortcut."
        )
        return True
    return False


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
