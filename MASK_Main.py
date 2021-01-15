# -*- coding: utf-8 -*-
# @Time : 2020/4/8 23:00
# @Author : Wangyuqi
# @FileName: MASK_Main.py
# @Email : www2048g@126.com

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication
from functools import partial
from PyQt5 import QtCore, QtGui, QtWidgets

import pymysql

import gui.login as login
import gui.Register as Register
import gui.Main as Main
import gui.query as query
import gui.show_personal as show_personal

import people_counting

conn = pymysql.connect(host='127.0.0.1',user='root',passwd='123456',db='mask',port=3306,charset='utf8')
cur = conn.cursor()



def set_P(MainWindow):  # 设置背景
    palette = QtGui.QPalette()
    pix = QtGui.QPixmap("./pictures/white.jpg")
    pix = pix.scaled(MainWindow.width(), MainWindow.height())
    palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pix))
    MainWindow.setPalette(palette)

def login_success(ui):               #登陆判断
    input_id=ui.id.text()
    input_pas=ui.password.text()
    sql = 'select * from accounts where id=' + input_id
    cur.execute(sql)
    account = cur.fetchone()
    if account == None:
        #print('账号不存在')
        ui.label_3.setVisible(True)
        ui.id.clear()
        ui.password.clear()
    else:
        if account[1] != input_pas:
            #print("密码错误")
            ui.label_3.setVisible(False)
            ui.label_tip.setVisible(True)
            ui.password.clear()
        else:
            acc_id = input_id
            print(acc_id+'登陆成功')
            show_Main(acc_id)


def save_people(regui,input_id):    #保存个人信息
    name1 = regui.name.text()
    tel = regui.tel.text()
    notes = regui.textEdit.toPlainText()
    if regui.radioM.isChecked():
        sex = '男'
    if regui.radioW.isChecked():
        sex = '女'
    #print(name, ' ', sex, ' ', tel, ' ', notes)
    sql2 = "insert into people(id,name,sex,tel,notes)values('" +input_id+ "','" +name1+ "','" +sex+ "','" +tel+ "','" +notes+ "')"
    #print(sql2)
    cur.execute(sql2)
    conn.commit()

def register_success(regui):            #注册判断

    input_id=regui.register_id.text()
    input_pas=regui.register_password.text()
    input_confim=regui.confirm_pas.text()

    sql = 'select * from accounts where id=' + input_id
    cur.execute(sql)
    account = cur.fetchone()

    #print(account)
    if account == None:
        if input_pas != input_confim:  # 密码不一致
            regui.label_10.setVisible(True)
            regui.label_11.setVisible(False)
            regui.register_password.clear()  # 清除输入
            regui.confirm_pas.clear()
        else:
            sql1 = "insert into accounts(id,password)values('" +input_id+ "','" +input_pas+ "')"
            #print(sql1)
            cur.execute(sql1)
            conn.commit()
            save_people(regui,input_id)
            show_login()
            print("注册成功")
    else:
        print('账号已存在！')
        regui.label_11.setVisible(True)
        regui.register_id.clear()
        regui.register_password.clear()
        regui.confirm_pas.clear()


def show_register():
    reg_ui=Register.Ui_register_2()
    reg_ui.setupUi(MainWindow)
    set_P(MainWindow)
    MainWindow.show()
    reg_ui.Button_register.clicked.connect(partial(register_success,reg_ui))
    reg_ui.Button_returnlogin.clicked.connect(show_login)

def show_login():
    ui = login.Ui_MainWindow()
    # 向主窗口上添加控件
    ui.setupUi(MainWindow)
    set_P(MainWindow)
    MainWindow.show()
    ui.Button_affirm.clicked.connect(partial(login_success, ui))
    ui.Button_login.clicked.connect(show_register)

def modify(acc_id, perui):          #修改个人信息
    name = perui.lineEdit.text()
    sex = perui.lineEdit_2.text()
    tel = perui.lineEdit_3.text()
    note = perui.lineEdit_4.text()
    sql = "update people set name='"+name+"',sex='"+sex+"',tel='"+tel+"',notes='"+note+"' where id="+acc_id
    #print(sql)
    cur.execute(sql)
    conn.commit()
    print('修改成功')
    show_person(acc_id)

def delete(acc_id):                #删除账号
    sql = "delete from people where id="+acc_id
    sql1 = "delete from accounts where id="+acc_id
    cur.execute(sql)
    cur.execute(sql1)
    conn.commit()
    print("删除成功")
    show_login()

def show_person(acc_id):          #显示个人信息

    perui = show_personal.Ui_MainWindow()
    perui.setupUi(MainWindow)
    set_P(MainWindow)
    sql = "select * from people where id =" + acc_id
    cur.execute(sql)
    data = cur.fetchone()
    #print(data)
    perui.lineEdit.setText(data[1])
    perui.lineEdit_2.setText(data[2])
    perui.lineEdit_3.setText(data[3])
    perui.lineEdit_4.setText(data[4])

    MainWindow.show()
    perui.pushButton_3.clicked.connect(partial(show_Main, acc_id))
    perui.pushButton.clicked.connect(partial(modify, acc_id, perui ))
    perui.pushButton_2.clicked.connect(partial(delete,acc_id))

def show_query_res(queryui):            #显示查询结果
    start_date = queryui.lineEdit.text()
    end_date = queryui.lineEdit_2.text()
    sql1 = "select people from day_statistics where date1='" + start_date + "'"
    sql2 = "select people from day_statistics where date1='" + end_date +"'"
    cur.execute(sql1)
    s1 = cur.fetchone()
    cur.execute(sql2)
    s2 = cur.fetchone()
    #print(type(s1))
    #print(s1,s2)
    if s1 == None or s2 == None:
        queryui.label_7.setVisible(True)
        queryui.lineEdit.clear()
        queryui.lineEdit_2.clear()
    else:
        queryui.label_7.setVisible(False)
        queryui.label_5.setVisible(True)
        queryui.label_4.setVisible(True)
        queryui.label_6.setVisible(True)
        res = int(s2[0])-int(s1[0])
        #print(res)
        queryui.label_6.setText(str(res))


def show_query(acc_id):                #显示查询界面

    queryui = query.Ui_Query()
    queryui.setupUi(MainWindow)
    set_P(MainWindow)
    MainWindow.show()
    queryui.pushButton_2.clicked.connect(partial(show_Main, acc_id))
    queryui.pushButton.clicked.connect(partial(show_query_res, queryui))


def show_Main(acc_id):     #显示主界面
    mainui = Main.Ui_MainWindow()
    mainui.setupUi(MainWindow)
    set_P(MainWindow)
    # MainWindow.setStyleSheet("border-image: url(./pictures/main2.jpg);")
    MainWindow.show()
    mainui.pushButton_3.clicked.connect(partial(show_person, acc_id))
    mainui.pushButton_2.clicked.connect(partial(show_query, acc_id))
    mainui.pushButton.clicked.connect(people_counting.Main)

if __name__ == '__main__':

    app = QApplication(sys.argv)

    global MainWindow
    global acc_id

    MainWindow = QMainWindow()
    show_login()


    sys.exit(app.exec_())
