from setuptools import setup
import pkg_resources


pkg_resources.require("setuptools==70.3.0")

APP = ['back_trace.py']  # Replace with your main script filename
DATA_FILES = ['config.json']
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'MyAppIcon.icns',  # Optional: path to your icon file
    'plist': {
        'CFBundleName': "MySQL Log Viewer",
        'CFBundleDisplayName': "MySQL Log Viewer",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHumanReadableCopyright': "Copyright © 2023, Zhang Ruibin",
        'PyRuntimeLocations': [
            '@executable_path/../Frameworks/Python.framework/Versions/Current/Python'
        ],
        'CFBundleIconFile': 'MyAppIcon',
    },
    'packages': ['PyQt5', 'mysql', 'sqlparse', 'pygments'],
    'includes': ['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
    
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app', 'setuptools==70.3.0'],
)