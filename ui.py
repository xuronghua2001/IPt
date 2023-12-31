# -*- coding: utf-8 -*-
import ast
import struct
import datetime
import socket
import matplotlib
from matplotlib import pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

matplotlib.use('Qt5Agg')
# Form implementation generated from reading ui file '20230614.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtGui import QIcon, QMouseEvent, QFont
from PyQt5.QtWidgets import QComboBox, QFileDialog

IP_info = []

IP_s = set()
IP_d = set()


class Worker(QThread):
    signal_IP = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        # 设置工作状态与初始num数值
        self.working = True
        self.num = 0
        self.is_pause = False

    def __del__(self):
        # 线程状态改变与线程终止
        self.working = False
        self.wait()

    def run(self):
        raw_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
        for i in range(len(socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET))):
            print(socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)[i])
        ip_address = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)[1][4][0]
        print(ip_address)
        raw_sock.bind((ip_address, 0))


        if raw_sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON) != 0:
            print('打开混杂模式失败')
        else:
            print('打开混杂模式成功')

        while self.working:
            packet = raw_sock.recv(65536)

            if len(packet) < 35:

                continue

            ip_header = packet[0:20]

            # 解析 IP 头部字段
            version_ihl = ip_header[0]
            version = version_ihl >> 4  # 版本号
            ihl = (version_ihl & 0x0F) * 4  # 首部长度
            tos = ip_header[1]  # 服务类型
            total_length = socket.ntohs(struct.unpack('!H', ip_header[2:4])[0])  # 分组总长度
            identification = socket.ntohs(struct.unpack('!H', ip_header[4:6])[0])  # 分组标识
            flags_fragment_offset = socket.ntohs(struct.unpack('!H', ip_header[6:8])[0])  # 标志位和片偏移
            ttl = ip_header[8]  # 生存时间
            protocol = ip_header[9]  # 协议
            header_checksum = socket.ntohs(struct.unpack('!H', ip_header[10:12])[0])  # 校验和
            src_ip = socket.inet_ntoa(ip_header[12:16])  # 源 IP 地址
            dest_ip = socket.inet_ntoa(ip_header[16:20])  # 目的 IP 地址

            now = datetime.datetime.now()
            data = (now, src_ip, dest_ip, version, ihl, tos, total_length, identification, flags_fragment_offset,ttl, protocol, header_checksum)
            IP_info.append(data)
            self.signal_IP.emit(data)


class MyStaticMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=10, height=4, dpi=200):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        super(MyStaticMplCanvas, self).__init__(self.figure)
        self.setParent(parent)
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
        plt.rcParams['axes.unicode_minus'] = False
        self.ax = self.figure.add_subplot(111)
        self.plot()
    def plot(self):
        labels = ['流量统计']
        sizes = [100]
        self.ax.pie(sizes, labels=labels, autopct='%1.1f%%')

    def updatePieChart(self,labels,sizes):
        self.ax.clear()
        self.ax.set_title(labels[0]+'有'+str(sizes[0])+'个IP包')
        self.ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        self.ax.legend(loc='upper right')
        self.draw()

class myComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton or Qt.RightButton:
            com_set = set()
            for i in range(self.count()):
                com_set.add(self.itemText(i))
            self.addItems(list(IP_s - com_set))
        super().mousePressEvent(event)


class myComboBox_2(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton or Qt.RightButton:
            com_set = set()
            for i in range(self.count()):
                com_set.add(self.itemText(i))
            self.addItems(list(IP_d - com_set))
        # 调用父类的mousePressEvent处理其他事件
        super().mousePressEvent(event)


class Ui_MainWindow(QtWidgets.QMainWindow):
    thread = Worker()


    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.isStart = False

    def setupUi(self, MainWindow):
        MainWindow.setWindowIcon(QIcon("IPSta.png"))
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1300, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.comboBox = myComboBox(self.centralwidget)
        self.comboBox.setMinimumSize(QtCore.QSize(300, 0))
        self.comboBox.setObjectName("comboBox")
        self.gridLayout_2.addWidget(self.comboBox, 0, 1, 1, 1)
        self.comboBox.addItem('全部')
        self.comboBox.currentIndexChanged.connect(self.selectionchange)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_2.addWidget(self.pushButton, 0, 2, 2, 1)
        self.pushButton.clicked.connect(self.start)
        self.thread.signal_IP.connect(self.addList)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout_2.addWidget(self.pushButton_2, 0, 3, 2, 1)
        self.pushButton_2.clicked.connect(self.write)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout_2.addWidget(self.pushButton_3, 0, 4, 2, 1)
        self.pushButton_3.clicked.connect(self.read)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.comboBox_2 = myComboBox_2(self.centralwidget)
        self.comboBox_2.setMinimumSize(QtCore.QSize(300, 0))
        self.comboBox_2.setObjectName("comboBox_2")
        self.gridLayout_2.addWidget(self.comboBox_2, 1, 1, 1, 1)
        self.comboBox_2.addItem('全部')
        self.comboBox_2.currentIndexChanged.connect(self.selectionchange_2)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setMinimumSize(QtCore.QSize(400, 0))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout = QtWidgets.QGridLayout(self.tab)
        self.gridLayout.setObjectName("gridLayout")
        self.listWidget = QtWidgets.QListWidget(self.tab)
        self.listWidget.setObjectName("listWidget")
        self.listWidget.itemDoubleClicked.connect(self.doubcl)
        self.gridLayout.addWidget(self.listWidget, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.tab_2)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.plainTextEdit.setFont(QFont('SimHei', 10))
        self.gridLayout_3.addWidget(self.plainTextEdit, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout_2.addWidget(self.tabWidget, 2, 0, 1, 2)
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setMinimumSize(QtCore.QSize(0, 300))
        self.widget.setObjectName("widget")

        self.sc = MyStaticMplCanvas(self.widget, width=5, height=4, dpi=150)
        self.sc.plot()
        self.gridLayout_2.addWidget(self.widget, 2, 2, 1, 3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 722, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    def write(self):
        if len(IP_info)>0:
            s = ''
            for i in IP_info:
                s = s + f"{{'时间':'{i[0].strftime('%Y-%m-%d %H:%M:%S')}','源IP地址':'{str(i[1])}','目的IP地址':'{str(i[2])}','IP协议版本':'{str(i[3])}','IP头部长度':'{str(i[4])}','服务类型':'{str(i[5])}','分组总长度':'{str(i[6])}','唯一标识号':'{str(i[7])}','标识符':'{str(i[8])}','生存时间':'{str(i[9])}','IP数据包中协议':'{str(i[10])}','IP头部校验和':'{str(i[11])}'}}\n"
            with open(datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S_")+'cap.txt', 'w') as f:
                f.write(s)


    def draw_pie(self):
        h = 0
        v = 0
        for i in range(self.listWidget.count()):
            if self.listWidget.item(i).isHidden():
                h = h + 1
            else:
                v = v + 1
        self.sc.updatePieChart([self.comboBox.currentText() + '到' + self.comboBox_2.currentText(), '其他流量'], [v, h])



    def start(self):
        if self.isStart:
            self.pushButton.setText('开始')
            self.isStart = False
            self.thread.working = False
            self.thread.quit()
            self.thread.wait()
            self.draw_pie()


        else:
            self.pushButton.setText('结束')
            self.thread.working = True
            self.thread.start()
            self.isStart = True

    def addList(self,data):
        now, src_ip, dest_ip, version, ihl, tos, total_length, identification, flags_fragment_offset, ttl, protocol, header_checksum = data
        info_text = f"{now}\n  源IP地址: {src_ip}\n  目的IP地址: {dest_ip}"
        print(info_text)
        c1 = self.comboBox.currentText()
        c2 = self.comboBox_2.currentText()
        if c1 == src_ip and c2 == dest_ip or c1 == '全部' and c2 == '全部' or c1 == '全部' and c2 == dest_ip or c1 == src_ip and c2 == '全部':
            self.listWidget.addItem(info_text)
        else:
            self.listWidget.addItem(info_text)
            self.listWidget.item(self.listWidget.count()-1).setHidden(True)
        IP_s.add(src_ip)
        IP_d.add(dest_ip)

    def selectionchange(self, i):

        # print(self.comboBox.itemText(i))
        com_text = self.comboBox.itemText(i)


        for j in range(self.listWidget.count()):
            if com_text != '全部' and self.comboBox_2.currentText() != '全部':
                self.listWidget.item(j).setHidden(False)
            it = self.listWidget.item(j).text()
            s1 = it.split('\n')[1][9:]
            s2 = it.split('\n')[2][10:]
            # print((j, s1, com_text))

            if com_text == '全部' and self.comboBox.currentText() == '全部':
                self.listWidget.item(j).setHidden(False)
            elif com_text == '全部' and self.comboBox_2.currentText() == s2:
                self.listWidget.item(j).setHidden(False)
            elif com_text == s1 and self.comboBox_2.currentText() == '全部':
                self.listWidget.item(j).setHidden(False)
            elif com_text == s1 and self.comboBox_2.currentText() == s2:
                self.listWidget.item(j).setHidden(False)
            else:
                self.listWidget.item(j).setHidden(True)

        self.draw_pie()

    def selectionchange_2(self, i):

        # print(self.comboBox_2.itemText(i))
        com_text = self.comboBox_2.itemText(i)
        for j in range(self.listWidget.count()):
            if com_text != '全部' and self.comboBox.currentText() != '全部':
                self.listWidget.item(j).setHidden(False)
            it = self.listWidget.item(j).text()
            s1 = it.split('\n')[1][9:]
            s2 = it.split('\n')[2][10:]
            # print((j, s2, com_text))

            if com_text == '全部' and self.comboBox.currentText() == '全部':
                self.listWidget.item(j).setHidden(False)
            elif com_text == '全部' and self.comboBox.currentText() == s1:
                self.listWidget.item(j).setHidden(False)
            elif com_text == s2 and self.comboBox.currentText() == '全部':
                self.listWidget.item(j).setHidden(False)
            elif com_text == s2 and self.comboBox.currentText() == s1:
                self.listWidget.item(j).setHidden(False)
            else:
                self.listWidget.item(j).setHidden(True)
        self.draw_pie()


    def doubcl(self,item):
        i = self.listWidget.row(item)
        info_text = f"{str(IP_info[i][0])}\n  源IP地址: {str(IP_info[i][1])}\n  目的IP地址: {str(IP_info[i][2])}  IP协议版本: {str(IP_info[i][3])}\n  IP头部长度: {str(IP_info[i][4])}\n  服务类型: {str(IP_info[i][5])}\n  分组总长度: {str(IP_info[i][6])}\n  唯一标识号: {str(IP_info[i][7])}\n  标识符: {str(IP_info[i][8])}\n  生存时间: {str(IP_info[i][9])}\n  IP数据包中协议: {str(IP_info[i][10])}\n  IP头部校验和: {str(IP_info[i][11])}\n"
        self.plainTextEdit.setPlainText(str(info_text))
        self.tabWidget.setCurrentIndex(1)

    def read(self):
        fileName, filetype = QFileDialog.getOpenFileName(self,"读取日志","./","Text Files (*.txt)")
        if fileName != '':
            with open(fileName, 'r') as f:
                l = f.readlines()
                IP_info.clear()
                s_ip = set()
                d_ip = set()
                for content in l:
                    log_dict = ast.literal_eval(content)
                    data = (log_dict['时间'], log_dict['源IP地址'], log_dict['目的IP地址'], log_dict['IP协议版本'], log_dict['IP头部长度'], log_dict['服务类型'], log_dict['分组总长度'], log_dict['唯一标识号'], log_dict['标识符'], log_dict['生存时间'],log_dict['IP数据包中协议'], log_dict['IP头部校验和'])
                    IP_info.append(data)
                    s_ip.add(log_dict['源IP地址'])
                    d_ip.add(log_dict['目的IP地址'])
                    # print(log_dict)
                    info_text = f"{log_dict['时间']}\n  源IP地址: {log_dict['源IP地址']}\n  目的IP地址: {log_dict['目的IP地址']}"
                    self.listWidget.addItem(info_text)
                self.comboBox.addItems(list(s_ip))
                self.comboBox_2.addItems(list(d_ip))



    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "IPSta 20201527"))
        self.label.setText(_translate("MainWindow", "源IP："))
        self.pushButton.setText(_translate("MainWindow", "开始"))
        self.pushButton_2.setText(_translate("MainWindow", "写入日志"))
        self.pushButton_3.setText(_translate("MainWindow", "读入日志"))
        self.label_2.setText(_translate("MainWindow", "目的IP："))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "列表"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "详情"))
