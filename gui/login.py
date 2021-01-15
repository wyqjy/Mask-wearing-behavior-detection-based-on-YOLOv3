# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(834, 693)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("C:/Users/WYQ/.designer/backup/icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(260, 190, 225, 92))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.id = QtWidgets.QLineEdit(self.layoutWidget)
        self.id.setObjectName("id")
        self.gridLayout.addWidget(self.id, 0, 1, 1, 2)
        self.password = QtWidgets.QLineEdit(self.layoutWidget)
        self.password.setObjectName("password")
        self.gridLayout.addWidget(self.password, 1, 1, 1, 2)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.Button_exit = QtWidgets.QPushButton(self.centralwidget)
        self.Button_exit.setGeometry(QtCore.QRect(590, 440, 93, 28))
        self.Button_exit.setObjectName("Button_exit")
        self.Button_affirm = QtWidgets.QPushButton(self.centralwidget)
        self.Button_affirm.setGeometry(QtCore.QRect(400, 320, 93, 28))
        self.Button_affirm.setObjectName("Button_affirm")
        self.Button_login = QtWidgets.QPushButton(self.centralwidget)
        self.Button_login.setGeometry(QtCore.QRect(250, 320, 91, 28))
        self.Button_login.setObjectName("Button_login")
        self.label_tip = QtWidgets.QLabel(self.centralwidget)
        self.label_tip.setGeometry(QtCore.QRect(500, 250, 141, 16))
        self.label_tip.setObjectName("label_tip")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(500, 210, 161, 16))
        self.label_3.setObjectName("label_3")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 834, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionFile = QtWidgets.QAction(MainWindow)
        self.actionFile.setObjectName("actionFile")
        self.actionexit = QtWidgets.QAction(MainWindow)
        self.actionexit.setObjectName("actionexit")

        self.retranslateUi(MainWindow)
        self.Button_exit.clicked['bool'].connect(MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "login"))
        self.label.setText(_translate("MainWindow", "账户:"))
        self.label_2.setText(_translate("MainWindow", "密码："))
        self.Button_exit.setText(_translate("MainWindow", "退出"))
        self.Button_affirm.setText(_translate("MainWindow", "确定"))
        self.Button_login.setText(_translate("MainWindow", "注册"))
        self.label_tip.setText(_translate("MainWindow", "密码错误，重新输入"))
        self.label_3.setText(_translate("MainWindow", "账号不存在，重新输入"))
        self.actionFile.setText(_translate("MainWindow", "File"))
        self.actionexit.setText(_translate("MainWindow", "exit"))

        self.label_tip.setVisible(False)
        self.label_3.setVisible(False)