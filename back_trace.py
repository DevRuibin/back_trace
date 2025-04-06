import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QGridLayout, QVBoxLayout, QScrollArea, QSizePolicy, QMessageBox
)

import mysql.connector
import json
import os
import getpass
import socket
from datetime import datetime, timedelta
import sqlparse
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import SqlLexer



CONFIG_FILE = "config.json"

def load_last_event_time():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("last_event_time")
    return None

def save_last_event_time(event_time):
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
        config["last_event_time"] = event_time
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def get_default_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            default_config = json.load(f)
    else:
        default_config = {
            "username": getpass.getuser(),
            "password": "",
            "host": socket.gethostbyname(socket.gethostname()),
            "port": "3306",
            "query_username": getpass.getuser(),
            "query_host": socket.gethostbyname(socket.gethostname()),
            "event_time": (datetime.now() - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        }
    return default_config

def get_default_event_time():
    return (datetime.now() - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")

def format_and_highlight_sql(query: str) -> str:
    # Format SQL
    formatted_sql = sqlparse.format(query, reindent=True, keyword_case='upper').strip()
    
    # Highlight SQL
    highlighted_sql = highlight(formatted_sql, SqlLexer(), HtmlFormatter())
    print(highlighted_sql)
    
    return highlighted_sql


def get_pygments_styles():
    return HtmlFormatter().get_style_defs('.highlight')
    


class ResponsiveForm(QWidget):
    def __init__(self, default_config, output_text):
        super().__init__()
        self.default_config = default_config
        self.output_text = output_text
        self.inputs = []
        self.fields = []
        self.keys_map = {
            "username": 0,
            "password": 1,
            "host": 2,
            "port": 3,
            "query_username": 4,
            "query_host": 5,    
            "event_time": 6
        }
        self.init_ui()
        

    def init_ui(self):
        self.setWindowTitle("Responsive MySQL Log Viewer")
        self.resize(800, 600)

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(8)

        # Scrollable input form
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.scroll_area.setMaximumHeight(300)  # Limit height to keep output visible

        self.form_widget = QWidget()
        self.grid_layout = QGridLayout(self.form_widget)
        self.grid_layout.setSpacing(4)

        self.scroll_area.setWidget(self.form_widget)
        self.main_layout.addWidget(self.scroll_area)

        # Define fields
        self.fields = [
            ("MySQL Username:", QLineEdit()),
            ("MySQL Password:", QLineEdit()),
            ("Host IP:", QLineEdit()),
            ("Port:", QLineEdit()),
            ("Query Username:", QLineEdit()),
            ("Query Host:", QLineEdit()),
            ("Event Time:", QLineEdit())
        ]

        keys = self.keys_map.keys()
        
        for (label, input_field), key in zip(self.fields,keys):
            input_field.setText(self.default_config[key])
            input_field.setMinimumHeight(25)
            if "password" in label.lower():
                input_field.setEchoMode(QLineEdit.Password)
            self.inputs.append((label, input_field))

        self.update_layout()
        self.installEventFilter(self)

        # Run Button
        run_button = QPushButton("Run Query")
        run_button.setFixedHeight(30)
        run_button.clicked.connect(self.on_run_query)
        self.main_layout.addWidget(run_button)

        # Output Area
        self.output_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.main_layout.addWidget(self.output_text, stretch=1)

    def on_run_query(self):
        config = get_default_config()
        self.output_text.setText(f"Running query with config:\n{config}")
        username = self.inputs[self.keys_map["username"]][1].text().strip() or default_config["username"]
        password = self.inputs[self.keys_map["password"]][1].text().strip() or default_config["password"]
        host = self.inputs[self.keys_map["host"]][1].text().strip() or default_config["host"]
        port = self.inputs[self.keys_map["port"]][1].text().strip() or default_config["port"]
        query_user = self.inputs[self.keys_map["query_username"]][1].text().strip() or default_config["query_username"]
        query_host = self.inputs[self.keys_map["query_host"]][1].text().strip() or default_config["query_host"]
        user_host = f"{query_user}[{query_user}] @  [{query_host}]"
        event_time = self.inputs[self.keys_map["event_time"]][1].text().strip() or default_config["event_time"]

        #  save the config to the file
        config = {
            "username": username,
            "password": password,
            "host": host,
            "port": port,
            "query_username": query_user,
            "query_host": query_host,
            "event_time": event_time
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)


        if not event_time:
            event_time = load_last_event_time() or get_default_event_time()
        

        try:
            conn = mysql.connector.connect(
                host=host,
                port=port,
                user=username,
                password=password,
                database="mysql"
            )

            cursor = conn.cursor()
            query = (
                "SELECT event_time, argument AS sql_text FROM mysql.general_log "
                "WHERE event_time > %s "
                "AND user_host = %s "
                "ORDER BY event_time desc"
            )

            cursor.execute(query, (event_time, user_host))
            results = cursor.fetchall()
            output_text.clear()

            css_styles = get_pygments_styles()
            html_output = f"<style>{css_styles}</style>"

            last_time = None
            for row in results:
                event_time = row[0]
                sql_text = row[1] # it is a byte now convert it to string
                if isinstance(sql_text, bytes):
                    sql_text = sql_text.decode('utf-8')
                if sql_text == "" or sql_text is None:
                    sql_text = "<p style='color:red;'>Empty SQL statement</p>"
                else:
                    if len(sql_text) > 1000:
                        sql_text = sql_text[:1000] + "..."
                    formatted_highlighted_sql = format_and_highlight_sql(sql_text)
                    print(formatted_highlighted_sql)
                    html_output += f"<b>{event_time}</b>{formatted_highlighted_sql}<br/>"
                    
            last_time = results[0][0] if results else None
            if last_time and last_time != '':
                save_last_event_time(last_time.strftime("%Y-%m-%d %H:%M:%S.%f"))
                self.inputs[self.keys_map["event_time"]][1].setText(last_time.strftime("%Y-%m-%d %H:%M:%S.%f"))

            if not results:
                # the css style is red
                html_output += "<p style='color:red;'>No results found.</p>"

            cursor.close()
            conn.close()
            self.output_text.setHtml(html_output)
        except Exception as e:
            QMessageBox.critical(window, "Error", str(e))
        

    def eventFilter(self, source, event):
        if event.type() == event.Resize:
            self.update_layout()
        return super().eventFilter(source, event)

    def update_layout(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        width = self.width()
        # Calculate the number of columns based on the width
        columns = max(1, width // 400)

        for index, (label_text, input_field) in enumerate(self.inputs):
            row = index // columns
            col = (index % columns) * 2
            label = QLabel(label_text)
            label.setMinimumHeight(20)
            self.grid_layout.addWidget(label, row, col)
            self.grid_layout.addWidget(input_field, row, col + 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    default_config = get_default_config()

    output_text = QTextEdit()
    output_text.setReadOnly(True)
    output_text.setAcceptRichText(True)

    window = ResponsiveForm(default_config, output_text)
    window.show()

    sys.exit(app.exec_())