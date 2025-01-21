from aqt import mw
from .settings import on_config_action
from .popup import setup_shortcut, setup_auto_popup

# アドオンの設定アクションを登録
mw.addonManager.setConfigAction(__name__, on_config_action)

# ショートカットを設定
setup_shortcut()

# 自動ポップアップを設定
setup_auto_popup()
