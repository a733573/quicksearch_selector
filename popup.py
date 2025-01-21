from aqt.qt import *
from aqt import mw
import aqt.utils
import webbrowser
from .utils import load_settings, DEFAULT_SETTINGS  # DEFAULT_SETTINGS を追加
from aqt.utils import showInfo

# グローバル変数としてタイマーを定義
popup_timer = None


def show_popup(text, pos):
    settings = load_settings()
    dialog = QDialog(mw)
    dialog.setWindowTitle("")
    dialog.setWindowFlags(
        Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)  # 余白を完全になくす
    layout.setSpacing(0)  # ボタン間のスペースを完全になくす

    for button_info in settings["buttons"]:
        if not button_info.get("enabled", True):  # 休止状態のボタンをスキップ
            continue
        button = QPushButton(button_info["label"])
        button.setFixedHeight(35)  # ボタンの高さを 35px に調整
        button.setStyleSheet("""
            QPushButton {
                font-size: 16px;  /* 文字サイズを大きくする */
                font-family: 'Segoe UI', 'Arial', sans-serif;  /* モダンなフォント */
                font-weight: 500;  /* フォントの太さを Medium に */
                padding: 5px;  /* パディングを最小限に */
                border: 1px solid #555;
                border-radius: 0;  /* 角を丸くしない */
                background-color: #444;  /* ボタンの背景色 */
                color: white;
                text-align: left;
                text-overflow: ellipsis;  /* 長いテキストを省略表示 */
                overflow: hidden;  /* はみ出たテキストを非表示 */
                max-width: 150px;  /* 最大幅を設定 */
                margin: 0;  /* マージンをなくす */
            }
            QPushButton:hover {
                background-color: #666;  /* ホバー時の背景色 */
                border: 1px solid #777;  /* ホバー時のボーダー色 */
                color: #fff;  /* ホバー時のテキスト色 */
            }
        """)
        button.clicked.connect(
            lambda _, url=button_info["url"]: open_browser(url, text, dialog))
        layout.addWidget(button)

    dialog.setLayout(layout)
    dialog.setFixedWidth(150)  # ポップアップの横幅を 150px に固定
    dialog.adjustSize()
    dialog.setStyleSheet("""
        QDialog {
            border: 2px solid #666;  /* ポップアップのボーダー色 */
            border-radius: 0;  /* 角を丸くしない */
            background-color: #333;  /* ポップアップの背景色 */
            padding: 0;  /* パディングをなくす */
        }
    """)

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
    def __init__(self, dialog):
        super().__init__()
        self.dialog = dialog

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if not self.dialog.geometry().contains(event.globalPosition().toPoint()):
                self.dialog.close()
        return super().eventFilter(obj, event)


def open_browser(base_url, text, dialog):
    url = base_url.replace("%s", text)
    webbrowser.open(url)
    dialog.close()


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
    webview = mw.web
    webview.page().runJavaScript(js_code, lambda result: handle_js_result(result, webview))


def handle_js_result(result, webview):
    if result:
        text = webview.selectedText()
        if text:
            x = result["x"]
            y = result["y"]
            pos = webview.mapToGlobal(QPoint(int(x), int(y)))
            show_popup(text, pos)


def setup_shortcut():
    shortcut = QShortcut(QKeySequence("Alt+A"), mw)
    shortcut.activated.connect(on_shortcut_triggered)


def on_selection_changed():
    global popup_timer
    settings = load_settings()
    if not settings.get("auto_popup_enabled", DEFAULT_SETTINGS["auto_popup_enabled"]):
        return

    webview = mw.web
    text = webview.selectedText().strip()

    # マウスの左ボタンが離れていることと選択中のテキストが空でないことを確認
    if text:
        if popup_timer:
            popup_timer.stop()
        popup_timer = QTimer()
        popup_timer.setSingleShot(True)
        popup_timer.timeout.connect(lambda: handle_selection_timeout(webview))
        popup_timer.start(settings.get("auto_popup_delay",
                          DEFAULT_SETTINGS["auto_popup_delay"]))  # 設定された時間待機


def handle_selection_timeout(webview):
    webview.page().runJavaScript(js_code, lambda result: handle_js_result(result, webview))


def setup_auto_popup():
    webview = mw.web
    webview.page().selectionChanged.connect(on_selection_changed)
