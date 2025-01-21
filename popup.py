from aqt.qt import *
from aqt import mw
import webbrowser
from .utils import load_settings, DEFAULT_SETTINGS

# Global variable for the popup timer
popup_timer = None


def show_popup(text, pos):
    """
    Display a popup menu with buttons for searching the selected text.
    """
    settings = load_settings()
    dialog = QDialog(mw)
    dialog.setWindowTitle("")
    dialog.setWindowFlags(
        Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
    layout.setSpacing(0)  # Remove spacing between buttons

    # Add buttons for each enabled search option
    for button_info in settings["buttons"]:
        if not button_info.get("enabled", True):  # Skip disabled buttons
            continue
        button = QPushButton(button_info["label"])
        button.setFixedHeight(35)  # Set button height
        button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-weight: 500;
                padding: 5px;
                border: 1px solid #555;
                border-radius: 0;
                background-color: #444;
                color: white;
                text-align: left;
                text-overflow: ellipsis;
                overflow: hidden;
                max-width: 150px;
                margin: 0;
            }
            QPushButton:hover {
                background-color: #666;
                border: 1px solid #777;
                color: #fff;
            }
        """)
        button.clicked.connect(
            lambda _, url=button_info["url"]: open_browser(url, text, dialog))
        layout.addWidget(button)

    dialog.setLayout(layout)
    dialog.setFixedWidth(150)  # Set popup width
    dialog.adjustSize()
    dialog.setStyleSheet("""
        QDialog {
            border: 2px solid #666;
            border-radius: 0;
            background-color: #333;
            padding: 0;
        }
    """)

    # Adjust popup position to fit within the screen
    screen_geometry = QApplication.primaryScreen().geometry()
    popup_width = dialog.width()
    popup_height = dialog.height()
    popup_x = pos.x()
    popup_y = pos.y()

    if popup_x + popup_width > screen_geometry.width():
        popup_x = pos.x() - popup_width
    if popup_y + popup_height > screen_geometry.height():
        popup_y = pos.y() - popup_height

    dialog.move(popup_x, popup_y)
    dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
    dialog.installEventFilter(CloseOnClickOutsideFilter(dialog))
    dialog.exec()


class CloseOnClickOutsideFilter(QObject):
    """
    Event filter to close the popup when clicking outside of it.
    """

    def __init__(self, dialog):
        super().__init__()
        self.dialog = dialog

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if not self.dialog.geometry().contains(event.globalPosition().toPoint()):
                self.dialog.close()
        return super().eventFilter(obj, event)


def open_browser(base_url, text, dialog):
    """
    Open the selected text in the browser using the provided URL template.
    """
    url = base_url.replace("%s", text)
    webbrowser.open(url)
    dialog.close()


# JavaScript code to get the position of the selected text
js_code = """
(function() {
    const selection = window.getSelection();
    if (selection.rangeCount === 0) return null;
    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();
    return { x: rect.right, y: rect.bottom };
})();
"""


def on_shortcut_triggered():
    """
    Triggered when the shortcut key is pressed. Gets the selected text and its position.
    """
    webview = mw.web
    webview.page().runJavaScript(js_code, lambda result: handle_js_result(result, webview))


def handle_js_result(result, webview):
    """
    Handle the result of the JavaScript execution and show the popup.
    """
    if result:
        text = webview.selectedText()
        if text:
            x = result["x"]
            y = result["y"]
            pos = webview.mapToGlobal(QPoint(int(x), int(y)))
            show_popup(text, pos)


def setup_shortcut():
    """
    Set up the shortcut key for triggering the popup.
    """
    shortcut = QShortcut(QKeySequence("Alt+A"), mw)
    shortcut.activated.connect(on_shortcut_triggered)


def on_selection_changed():
    """
    Triggered when the text selection changes. Starts a timer to show the popup automatically.
    """
    global popup_timer
    settings = load_settings()
    if not settings.get("auto_popup_enabled", DEFAULT_SETTINGS["auto_popup_enabled"]):
        return

    webview = mw.web
    text = webview.selectedText().strip()

    # Check if text is selected and the left mouse button is not pressed
    if text:
        if popup_timer:
            popup_timer.stop()
        popup_timer = QTimer()
        popup_timer.setSingleShot(True)
        popup_timer.timeout.connect(lambda: handle_selection_timeout(webview))
        popup_timer.start(settings.get("auto_popup_delay",
                          DEFAULT_SETTINGS["auto_popup_delay"]))


def handle_selection_timeout(webview):
    """
    Handle the timeout event for the auto-popup timer.
    """
    webview.page().runJavaScript(js_code, lambda result: handle_js_result(result, webview))


def setup_auto_popup():
    """
    Set up the auto-popup feature by connecting to the selectionChanged signal.
    """
    webview = mw.web
    webview.page().selectionChanged.connect(on_selection_changed)
