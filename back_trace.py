import sys
import mysql.connector
import json
import os
import getpass
import socket
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QScrollArea, QMessageBox

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

def run_query(default_config):
    username = username_input.text().strip() or default_config["username"]
    password = password_input.text().strip() or default_config["password"]
    host = host_input.text().strip() or default_config["host"]
    port = port_input.text().strip() or default_config["port"]
    query_user = query_username_input.text().strip() or default_config["query_username"]
    query_host = query_host_input.text().strip() or default_config["query_host"]
    user_host = f"{query_user}[{query_user}] @  [{query_host}]"
    event_time = event_time_input.text().strip()

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
            "ORDER BY event_time"
        )

        cursor.execute(query, (event_time, user_host))
        results = cursor.fetchall()
        output_text.clear()

        last_time = None
        for row in results:
            event_time = row[0]
            sql_text = row[1] # it is a byte now convert it to string
            if isinstance(sql_text, bytes):
                sql_text = sql_text.decode('utf-8')
            output_text.append(f"{event_time}\n{sql_text}\n\n")
            last_time = row[0]

        if last_time:
            save_last_event_time(last_time.strftime("%Y-%m-%d %H:%M:%S"))

        if not results:
            output_text.append("No results found.\n")

        cursor.close()
        conn.close()

    except Exception as e:
        QMessageBox.critical(window, "Error", str(e))




default_config = get_default_config()


# UI Setup
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("BackTrace - MySQL Query Log Viewer")

layout = QVBoxLayout()

form_layout = QFormLayout()

username_input = QLineEdit()
username_input.setText(default_config["username"])
form_layout.addRow(QLabel("MySQL Username:"), username_input)

password_input = QLineEdit()
password_input.setText(default_config["password"])
password_input.setEchoMode(QLineEdit.Password)
form_layout.addRow(QLabel("MySQL Password:"), password_input)

host_input = QLineEdit()
host_input.setText(default_config["host"])
form_layout.addRow(QLabel("Host IP:"), host_input)

port_input = QLineEdit()
port_input.setText(default_config["port"])
form_layout.addRow(QLabel("Port:"), port_input)

query_username_input = QLineEdit()
query_username_input.setText(default_config["query_username"])
form_layout.addRow(QLabel("Query Username:"), query_username_input)
query_host_input = QLineEdit()
query_host_input.setText(default_config["query_host"])
form_layout.addRow(QLabel("Query Host:"), query_host_input)

event_time_input = QLineEdit()
event_time_input.setText(default_config["event_time"])
form_layout.addRow(QLabel("Event Time:"), event_time_input)



layout.addLayout(form_layout)

run_button = QPushButton("Run Query")
run_button.clicked.connect(lambda: run_query(get_default_config()))
layout.addWidget(run_button)

output_text = QTextEdit()
output_text.setReadOnly(True)
scroll_area = QScrollArea()
scroll_area.setWidget(output_text)
scroll_area.setWidgetResizable(True)
layout.addWidget(scroll_area)

window.setLayout(layout)
window.show()

sys.exit(app.exec_())