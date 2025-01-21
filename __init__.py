from aqt import mw
from .settings import on_config_action
from .popup import setup_shortcut

# アドオンの設定アクションを登録
mw.addonManager.setConfigAction(__name__, on_config_action)

# ショートカットを設定
setup_shortcut()
