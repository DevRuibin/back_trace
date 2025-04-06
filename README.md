# 📊 MySQL General Log Viewer (Desktop App)

A simple, responsive Python desktop application built with PyQt5 that allows you to query and visualize recent MySQL general_log entries with search, formatting, and highlighting features.

This tool is inspired by the need for understanding a complex backend systems. If the system is too complex, learning
and understnding it from the database level is a good start. This tool helps you to do that.

--- 

## 🚀 Features
* ✅ View recent SQL statements from the MySQL general_log table
* ✅ Automatically detects local IP and current system user for config defaults
* ✅ Search through results with Next and Previous buttons
* ✅ Responsive UI with scrollable inputs and highlighted SQL
* ✅ Smart defaults (e.g. event time defaults to 10 minutes ago)
* ✅ Saves config (like username/host/time) across runs
* ✅ Syntax highlighting for SQL using Pygments and sqlparse
* ✅ Handles large SQL logs with truncation and graceful fallbacks

--- 

## 🧰 Requirements

1. Python 3.6+
2. MySQL (with general_log enabled)
3. PyQt5
4. mysql-connector-python
5. sqlparse
6. pygments

--- 

## ⚙️ Setup
1.	Make sure your MySQL server has general_log enabled:
    ```
    SET GLOBAL general_log = 'ON';
    SET GLOBAL log_output = 'TABLE'; -- Ensure logs go to mysql.general_log
    ``` 
2. Run the app
    ```
    python3 mysql_log_viewer.py
    ```
3.	The app will attempt to use:
    1. Your current system username
    2. Your machine’s IP as the default MySQL host
    3. Event time defaults to 10 minutes ago

--- 

## 🔎 Search Feature

Use the search bar to search within the displayed SQL logs:
1. Next → Find next occurrence
2. Previous → Find previous one

It wraps around when you reach the end or beginning of the text.

--- 

## 📁 File Structure

```
.
├── config.json           # Stores your last used settings
├── back_trace.py         # Main PyQt5 application
├── requirements.txt      # Python dependencies
└── README.md             # You're reading this
```


--- 

## 🧠 Known Limitations
	Designed primarily for desktop usage on Mac/Linux (Windows not fully tested).
	Assumes MySQL general logs are stored in the mysql.general_log table.
	Limited error handling for incorrect credentials or log access permissions.

--- 

## 💡 Ideas for Future
	Export logs to .txt or .html
	Pagination for large result sets
	Advanced filtering (by command type, duration, etc.)
	Dark mode 🌙

--- 


## 🛠️ How to install it(Test only on mac)

```
python setup.py py2app

hdiutil create -volname "MySQL Log Viewer" \
                -srcfolder dist/ \
                -ov -format UDZO \
                MySQL_Log_Viewer.dmg
# Move the .dmg file to your Applications folder
```


## 🧑‍💻 Author

Built by a backend engineer passionate about database internals and tooling ✨
Feel free to contribute or open issues!