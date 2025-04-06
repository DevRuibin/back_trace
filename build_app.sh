python setup.py py2app

hdiutil create -volname "MySQL Log Viewer" \
                -srcfolder dist/ \
                -ov -format UDZO \
                MySQL_Log_Viewer.dmg


pkgbuild \
    --component "dist/MySQL Log Viewer.app" \
    --install-location "/Applications" \
    --identifier "zhangruibin" \
    --version "1.0" \
    "MySQL Log Viewer.pkg"