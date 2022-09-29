import sys, sqlite3
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import *
from PyQt5 import QtGui
from Contents import Ui_Contents
from TextContent import Ui_TextContent


class Contents(Ui_Contents, QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super(Contents, self).__init__(*args, **kwargs)
        self.setupUi(self)
        listModel = QStringListModel()
        self.list = [
            row[0]
            for row in cur.execute(
                "SELECT `title` FROM doupocangqiong ORDER BY `title_index` ASC;"
            )
        ]
        listModel.setStringList(self.list)
        self.listView.setModel(listModel)
        self.listView.doubleClicked.connect(self.doubleClicked)

    def doubleClicked(self):
        cur.execute(
            "SELECT `title_index`,`content` FROM doupocangqiong WHERE `title`=?",
            (self.listView.selectionModel().selectedIndexes()[0].data(),),
        )
        res = cur.fetchone()
        if res:
            subWindow.open(self.listView.selectionModel().selectedIndexes()[0].data())

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key.Key_Return or a0.key() == Qt.Key.Key_Enter:
            if self.listView.selectionModel().selectedIndexes():
                cur.execute(
                    "SELECT `title_index`,`content` FROM doupocangqiong WHERE `title`=?",
                    (self.listView.selectionModel().selectedIndexes()[0].data(),),
                )
                res = cur.fetchone()
                if res:
                    subWindow.open(
                        self.listView.selectionModel().selectedIndexes()[0].data()
                    )
        return super().keyPressEvent(a0)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        db.close()
        return super().closeEvent(a0)


class Dairy(Ui_TextContent, QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.textBrowser.clear()
        self.id = 0
        self.previousId = 0
        self.nextId = 0
        self.pushButton_Previous.clicked.connect(self.clicked_previous)
        self.pushButton_Next.clicked.connect(self.clicked_next)

    def open(self, title: str):
        self.show()
        mainWindow.hide()
        cur.execute(
            "SELECT `title_index`,`content` FROM doupocangqiong WHERE `title`=?",
            (title,),
        )
        res = cur.fetchone()
        if res:
            self.id = res[0]
            self.label.setText(title)
            self.textBrowser.setText(
                "\u3000\u3000" + res[1].replace("\n", "\n\n\u3000\u3000")
            )
            cur.execute(
                "SELECT `title_index` FROM doupocangqiong WHERE `title_index`<? ORDER BY `title_index` DESC LIMIT 1;",
                (self.id,),
            )
            previousId = cur.fetchone()
            self.previousId = previousId[0] if previousId else self.id
            cur.execute(
                "SELECT `title_index` FROM doupocangqiong WHERE `title_index`>? ORDER BY `title_index` ASC LIMIT 1;",
                (self.id,),
            )
            nextid = cur.fetchone()
            self.nextId = nextid[0] if nextid else self.id
            if self.id <= self.previousId:
                self.pushButton_Previous.setEnabled(False)
            else:
                self.pushButton_Previous.setEnabled(True)
            if self.id >= self.nextId:
                self.pushButton_Next.setEnabled(False)
            else:
                self.pushButton_Next.setEnabled(True)

    def clicked_previous(self):
        if self.id <= self.previousId:
            pass
        else:
            cur.execute(
                "SELECT `title`,`content` FROM doupocangqiong WHERE `title_index`=?",
                (self.previousId,),
            )
            res = cur.fetchone()
            if res:
                self.label.setText(res[0])
                self.textBrowser.setText(
                    "\u3000\u3000" + res[1].replace("\n", "\n\n\u3000\u3000")
                )
                self.id = self.previousId
                cur.execute(
                    "SELECT `title_index` FROM doupocangqiong WHERE `title_index`<? ORDER BY `title_index` DESC LIMIT 1;",
                    (self.id,),
                )
                previousId = cur.fetchone()
                self.previousId = previousId[0] if previousId else self.id
                cur.execute(
                    "SELECT `title_index` FROM doupocangqiong WHERE `title_index`>? ORDER BY `title_index` ASC LIMIT 1;",
                    (self.id,),
                )
                nextid = cur.fetchone()
                self.nextId = nextid[0] if nextid else self.id
                if self.id <= self.previousId:
                    self.pushButton_Previous.setEnabled(False)
                else:
                    self.pushButton_Previous.setEnabled(True)
                if self.id >= self.nextId:
                    self.pushButton_Next.setEnabled(False)
                else:
                    self.pushButton_Next.setEnabled(True)

    def clicked_next(self):
        if self.id >= self.nextId:
            pass
        else:
            cur.execute(
                "SELECT `title`,`content` FROM doupocangqiong WHERE `title_index`=?",
                (self.nextId,),
            )
            res = cur.fetchone()
            if res:
                self.label.setText(res[0])
                self.textBrowser.setText(
                    "\u3000\u3000" + res[1].replace("\n", "\n\n\u3000\u3000")
                )
                self.id = self.nextId
                cur.execute(
                    "SELECT `title_index` FROM doupocangqiong WHERE `title_index`<? ORDER BY `title_index` DESC LIMIT 1;",
                    (self.id,),
                )
                previousId = cur.fetchone()
                self.previousId = previousId[0] if previousId else self.id
                cur.execute(
                    "SELECT `title_index` FROM doupocangqiong WHERE `title_index`>? ORDER BY `title_index` ASC LIMIT 1;",
                    (self.id,),
                )
                nextid = cur.fetchone()
                self.nextId = nextid[0] if nextid else self.id
                if self.id <= self.previousId:
                    self.pushButton_Previous.setEnabled(False)
                else:
                    self.pushButton_Previous.setEnabled(True)
                if self.id >= self.nextId:
                    self.pushButton_Next.setEnabled(False)
                else:
                    self.pushButton_Next.setEnabled(True)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        mainWindow.show()
        return super().closeEvent(a0)


if __name__ == "__main__":
    db = sqlite3.connect("doupocangqiong.db")
    cur = db.cursor()
    db.execute(
        """CREATE TABLE IF NOT EXISTS doupocangqiong (
	uid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	title_index INTEGER NOT NULL,
	title TEXT(128),
	content TEXT
);
""",
    )
    db.execute(
        """CREATE INDEX IF NOT EXISTS doupocangqiong_title_index_IDX ON doupocangqiong (title_index);"""
    )
    db.execute(
        """CREATE INDEX IF NOT EXISTS doupocangqiong_title_IDX ON doupocangqiong (title);"""
    )
    app = QApplication(sys.argv)
    mainWindow = Contents()
    mainWindow.show()
    subWindow = Dairy()
    sys.exit(app.exec_())
