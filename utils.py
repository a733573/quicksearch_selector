import re
from aqt import mw

# 設定のデフォルト値
DEFAULT_SETTINGS = {
    "buttons": [
        {"label": "Google", "url": "https://www.google.com/search?q=%s", "enabled": True},
        {"label": "Cambridge",
            "url": "https://dictionary.cambridge.org/dictionary/english/%s", "enabled": True},
        {"label": "Oxford", "url": "https://www.oxfordlearnersdictionaries.com/definition/english/%s", "enabled": True},
        {"label": "DeepL", "url": "https://www.deepl.com/translator#en/ja/%s", "enabled": True}
    ]
}


def load_settings():
    settings = mw.addonManager.getConfig(__name__)
    if not settings:
        settings = DEFAULT_SETTINGS
        mw.addonManager.writeConfig(__name__, settings)
    return settings


def save_settings(settings):
    mw.addonManager.writeConfig(__name__, settings)


def validate_url(url):
    url_pattern = re.compile(r"https?://\S+")
    if not url_pattern.match(url):
        return "Invalid URL format. Please enter a valid URL starting with 'http://' or 'https://'."
    if url.count("%s") != 1:
        return "The URL must contain exactly one '%s' placeholder."
    return None
