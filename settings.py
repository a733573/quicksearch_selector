from aqt.qt import *
from aqt import mw
from .utils import load_settings, save_settings, validate_url, DEFAULT_SETTINGS


def open_settings():
    # 設定を読み込む
    settings = load_settings()

    dialog = QDialog(mw)
    dialog.setWindowTitle("Popup Search Settings")
    dialog.resize(600, 400)
    layout = QVBoxLayout()

    # ショートカットキーの入力欄
    shortcut_layout = QHBoxLayout()
    shortcut_label = QLabel("Shortcut Key:")
    shortcut_edit = QKeySequenceEdit(QKeySequence(
        settings.get("shortcut", DEFAULT_SETTINGS["shortcut"])))
    shortcut_layout.addWidget(shortcut_label)
    shortcut_layout.addWidget(shortcut_edit)
    layout.addLayout(shortcut_layout)

    # テーブルの作成
    table = QTableWidget()
    table.setColumnCount(4)  # 列数を4に変更 (Delete, Enabled, Label, URL)
    table.setHorizontalHeaderLabels(
        ["Delete", "Enabled", "Label", "URL (must contain %s, which will be replaced by the selected text)"])
    table.setRowCount(len(settings["buttons"]))
    table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.verticalHeader().setVisible(False)

    # テーブルに行を追加
    for i, button_info in enumerate(settings["buttons"]):
        # Delete ボタン
        delete_button = QPushButton("×")
        delete_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 5px;
                background-color: transparent;
                color: red;
                border: none;
            }
            QPushButton:hover {
                color: darkred;
            }
        """)
        delete_button.clicked.connect(lambda _, row=i: table.removeRow(row))
        table.setCellWidget(i, 0, delete_button)

        # Enabled チェックボックス
        enabled_checkbox = QCheckBox()
        enabled_checkbox.setChecked(button_info.get("enabled", True))
        table.setCellWidget(i, 1, enabled_checkbox)

        # Label と URL
        table.setItem(i, 2, QTableWidgetItem(button_info["label"]))
        table.setItem(i, 3, QTableWidgetItem(button_info["url"]))

    # テーブルの列幅を調整
    table.horizontalHeader().setSectionResizeMode(
        0, QHeaderView.ResizeMode.ResizeToContents)
    table.horizontalHeader().setSectionResizeMode(
        1, QHeaderView.ResizeMode.ResizeToContents)
    table.horizontalHeader().setSectionResizeMode(
        2, QHeaderView.ResizeMode.ResizeToContents)
    table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

    # Move Up と Move Down ボタン
    move_up_button = QPushButton("Move Up")
    move_down_button = QPushButton("Move Down")

    # Move Up ボタンの動作
    def move_up():
        current_row = table.currentRow()
        if current_row > 0:
            # セルウィジェット（×ボタンとチェックボックス）を取得
            delete_button = table.cellWidget(current_row, 0)
            enabled_checkbox = table.cellWidget(current_row, 1)
            # 行を移動
            table.insertRow(current_row - 1)
            for col in range(table.columnCount()):
                table.setItem(current_row - 1, col,
                              table.takeItem(current_row + 1, col))
                # セルウィジェットを移動
                if col == 0:
                    table.setCellWidget(current_row - 1, col, delete_button)
                elif col == 1:
                    table.setCellWidget(current_row - 1, col, enabled_checkbox)
            table.removeRow(current_row + 1)
            table.setCurrentCell(current_row - 1, 0)

    # Move Down ボタンの動作
    def move_down():
        current_row = table.currentRow()
        if current_row < table.rowCount() - 1:
            # セルウィジェット（×ボタンとチェックボックス）を取得
            delete_button = table.cellWidget(current_row, 0)
            enabled_checkbox = table.cellWidget(current_row, 1)
            # 行を移動
            table.insertRow(current_row + 2)
            for col in range(table.columnCount()):
                table.setItem(current_row + 2, col,
                              table.takeItem(current_row, col))
                # セルウィジェットを移動
                if col == 0:
                    table.setCellWidget(current_row + 2, col, delete_button)
                elif col == 1:
                    table.setCellWidget(current_row + 2, col, enabled_checkbox)
            table.removeRow(current_row)
            table.setCurrentCell(current_row + 1, 0)

    # ボタンに動作を接続
    move_up_button.clicked.connect(move_up)
    move_down_button.clicked.connect(move_down)

    # Add Button と Save Settings ボタン
    add_button = QPushButton("Add")
    save_button = QPushButton("Save")
    add_button.clicked.connect(lambda: add_new_row(table))
    save_button.clicked.connect(
        lambda: save_settings_from_table(table, dialog, shortcut_edit))

    # ボタンを配置するレイアウト
    button_layout = QGridLayout()
    button_layout.addWidget(move_up_button, 0, 0)
    button_layout.addWidget(move_down_button, 1, 0)
    button_layout.addWidget(add_button, 0, 1)
    button_layout.addWidget(save_button, 1, 1)

    # レイアウトにテーブルとボタンを追加
    layout.addWidget(table)
    layout.addLayout(button_layout)

    dialog.setLayout(layout)
    dialog.closeEvent = lambda event: confirm_close(
        event, table, dialog, shortcut_edit)
    dialog.exec()


def add_new_row(table):
    row = table.rowCount()
    table.insertRow(row)
    delete_button = QPushButton("×")
    delete_button.setStyleSheet("""
        QPushButton {
            font-size: 14px;
            padding: 5px;
            background-color: transparent;
            color: red;
            border: none;
        }
        QPushButton:hover {
            color: darkred;
        }
    """)
    delete_button.clicked.connect(lambda _, row=row: table.removeRow(row))
    table.setCellWidget(row, 0, delete_button)

    # Enabled チェックボックス
    enabled_checkbox = QCheckBox()
    enabled_checkbox.setChecked(True)
    table.setCellWidget(row, 1, enabled_checkbox)

    # Label と URL
    table.setItem(row, 2, QTableWidgetItem(""))
    table.setItem(row, 3, QTableWidgetItem(""))


def save_settings_from_table(table, dialog, shortcut_edit):
    settings = {"buttons": []}
    labels = set()
    for row in range(table.rowCount()):
        label_item = table.item(row, 2)
        url_item = table.item(row, 3)
        enabled_checkbox = table.cellWidget(row, 1)

        if label_item and url_item and enabled_checkbox:
            label = label_item.text()
            url = url_item.text()
            enabled = enabled_checkbox.isChecked()

            if not label or not url:
                QMessageBox.warning(mw, "Empty Field",
                                    "Label and URL cannot be empty.")
                return
            if label in labels:
                QMessageBox.warning(
                    mw, "Duplicate Label", f"The label '{label}' already exists. Please use a unique label.")
                return
            labels.add(label)
            error_message = validate_url(url)
            if error_message:
                QMessageBox.warning(mw, "Invalid URL", error_message)
                return
            settings["buttons"].append(
                {"label": label, "url": url, "enabled": enabled})

    # ショートカットキーの保存
    shortcut = shortcut_edit.keySequence().toString()
    if not shortcut:
        QMessageBox.warning(
            mw, "Invalid Shortcut", "Shortcut key cannot be empty. Using default shortcut.")
        shortcut = DEFAULT_SETTINGS["shortcut"]
    settings["shortcut"] = shortcut

    # 設定を保存
    save_settings(settings)
    dialog.accept()


def confirm_close(event, table, dialog, shortcut_edit):
    # 現在の設定を取得
    current_settings = {"buttons": []}
    for row in range(table.rowCount()):
        label_item = table.item(row, 2)
        url_item = table.item(row, 3)
        enabled_checkbox = table.cellWidget(row, 1)

        if label_item and url_item and enabled_checkbox:
            label = label_item.text()
            url = url_item.text()
            enabled = enabled_checkbox.isChecked()
            if label and url:
                current_settings["buttons"].append(
                    {"label": label, "url": url, "enabled": enabled})

    # 設定を比較
    saved_settings = load_settings()
    if current_settings["buttons"] != saved_settings["buttons"] or shortcut_edit.keySequence().toString() != saved_settings.get("shortcut", DEFAULT_SETTINGS["shortcut"]):
        confirm_dialog = QMessageBox(mw)
        confirm_dialog.setWindowTitle("Unsaved Changes")
        confirm_dialog.setText(
            "You have unsaved changes. Do you want to save them?")
        confirm_dialog.setIcon(QMessageBox.Icon.Warning)
        confirm_dialog.setStandardButtons(
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
        confirm_dialog.setDefaultButton(QMessageBox.StandardButton.Save)

        result = confirm_dialog.exec()
        if result == QMessageBox.StandardButton.Save:
            save_settings_from_table(table, dialog, shortcut_edit)
        elif result == QMessageBox.StandardButton.Discard:
            event.accept()
        elif result == QMessageBox.StandardButton.Cancel:
            event.ignore()
    else:
        event.accept()


def on_config_action():
    open_settings()


# Add-ons の Config に設定画面を追加
mw.addonManager.setConfigAction(__name__, on_config_action)
