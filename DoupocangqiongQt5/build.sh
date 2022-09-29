source activate python3.7
pyrcc5 res.qrc -o res_rc.py
pyuic5 Contents.ui -o Contents.py
pyuic5 TextContent.ui -o TextContent.py
pyinstaller -w app.py --name="斗破苍穹" --icon=icon.ico --add-data="doupocangqiong.db;./" -y
rm -rf dist/斗破苍穹/Qt5DBus.dll
rm -rf dist/斗破苍穹/Qt5Network.dll
rm -rf dist/斗破苍穹/Qt5Qml.dll
rm -rf dist/斗破苍穹/Qt5QmlModels.dll
rm -rf dist/斗破苍穹/Qt5Quick.dll
rm -rf dist/斗破苍穹/Qt5Svg.dll
rm -rf dist/斗破苍穹/Qt5WebSockets.dll