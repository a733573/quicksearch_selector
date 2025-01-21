import re
from aqt import mw
from aqt.utils import showInfo

# 設定のデフォルト値
DEFAULT_SETTINGS = {
    "buttons": [
        {"label": "Google", "url": "https://www.google.com/search?q=%s", "enabled": True},
        {"label": "Wiktionary", "url": "https://en.wiktionary.org/wiki/%s", "enabled": True}
    ],
    "shortcut": "Ctrl+Shift+S",
    "auto_popup_enabled": True,  # 自動ポップアップのオンオフ
    "auto_popup_delay": 1000  # タイマーの時間（ミリ秒）
}


def load_settings():
    settings = mw.addonManager.getConfig(__name__)
    if settings is None:
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
