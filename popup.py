from aqt.qt import *
from aqt import mw
import webbrowser
from .utils import load_settings, DEFAULT_SETTINGS

popup_timer = None
current_shortcut = None  # Track the current shortcut


def show_popup(text, pos):
    """
    Display a popup with search buttons based on the selected text.
    """
    settings = load_settings()
    dialog = QDialog(mw)
    dialog.setWindowTitle("")
    dialog.setWindowFlags(
        Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    for button_info in settings["buttons"]:
        if not button_info.get("enabled", True):
            continue
        button = QPushButton(button_info["label"])
        button.setFixedHeight(35)
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
    dialog.setFixedWidth(150)
    dialog.adjustSize()
    dialog.setStyleSheet("""
        QDialog {
            border: 2px solid #666;
            border-radius: 0;
            background-color: #333;
            padding: 0;
        }
    """)

    screen_geometry = QApplication.primaryScreen().geometry()
    popup_width = dialog.width()
    popup_height = dialog.height()
    popup_x = pos.x()
    popup_y = pos.y()

    # Adjust the popup position to ensure it stays within the screen bounds
    if popup_x + popup_width > screen_geometry.width():
        popup_x = screen_geometry.width() - popup_width
    if popup_y + popup_height > screen_geometry.height():
        popup_y = screen_geometry.height() - popup_height

    dialog.move(popup_x, popup_y)
    dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
    dialog.installEventFilter(CloseOnClickOutsideFilter(dialog))
    dialog.exec()


class CloseOnClickOutsideFilter(QObject):
    """
    Close the popup when the user clicks outside of it.
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
    Open the selected URL in the default web browser.
    """
    url = base_url.replace("%s", text)
    webbrowser.open(url)
    dialog.close()


js_code = """
(function() {
    const selection = window.getSelection();
    if (selection.rangeCount === 0) return null;
    const range = selection.getRangeAt(0);
    const rects = range.getClientRects();
    if (rects.length === 0) return null;
    const lastRect = rects[rects.length - 1];
    return { x: lastRect.right, y: lastRect.bottom };
})();
"""


def on_shortcut_triggered():
    """
    Triggered when the shortcut key is pressed. Retrieves the selected text and its position.
    """
    webview = mw.web
    webview.page().runJavaScript(js_code, lambda result: handle_js_result(result, webview))


def handle_js_result(result, webview):
    """
    Handle the result of the JavaScript code execution.
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
    global current_shortcut
    settings = load_settings()
    shortcut_key = settings.get("shortcut", DEFAULT_SETTINGS["shortcut"])

    # Remove the existing shortcut if it exists
    if current_shortcut:
        current_shortcut.setEnabled(False)
        current_shortcut.deleteLater()
        current_shortcut = None

    # Set up the new shortcut
    current_shortcut = QShortcut(QKeySequence(shortcut_key), mw)
    current_shortcut.setObjectName(
        "search_selected_text_shortcut")  # Identify the shortcut
    current_shortcut.activated.connect(on_shortcut_triggered)


def on_selection_changed():
    """
    Triggered when the user selects text in the Anki browser.
    """
    global popup_timer
    settings = load_settings()
    if not settings.get("auto_popup_enabled", DEFAULT_SETTINGS["auto_popup_enabled"]):
        return

    webview = mw.web
    text = webview.selectedText().strip()

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
    Handle the timeout event for the auto-popup feature.
    """
    webview.page().runJavaScript(js_code, lambda result: handle_js_result(result, webview))


def setup_auto_popup():
    """
    Set up the auto-popup feature that triggers when text is selected.
    """
    webview = mw.web
    webview.page().selectionChanged.connect(on_selection_changed)
