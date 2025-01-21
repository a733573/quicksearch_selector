from aqt import mw
from .settings import on_config_action
from .popup import setup_shortcut, setup_auto_popup
from aqt.utils import showWarning

# Register the add-on's configuration action
mw.addonManager.setConfigAction(__name__, on_config_action)

try:
    # Set up the shortcut for the popup
    setup_shortcut()
    # Set up the auto-popup feature
    setup_auto_popup()
except Exception as e:
    showWarning(f"An error occurred while setting up the add-on: {str(e)}")
