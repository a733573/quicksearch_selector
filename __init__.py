from aqt import mw
from .settings import on_config_action
from .popup import setup_shortcut, setup_auto_popup

# Register the add-on's configuration action
mw.addonManager.setConfigAction(__name__, on_config_action)

# Set up the shortcut for the popup
setup_shortcut()

# Set up the auto-popup feature
setup_auto_popup()
