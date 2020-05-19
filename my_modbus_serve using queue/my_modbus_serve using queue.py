import socket,sys,math,time,threading
from threading import Thread
from array import array
import firstMainWin as fm
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import queue

q = queue.Queue(maxsize=5)
class myserver():
   startflag = 0
   startedflag=0
   addr=''
   port=0
   sok=[]
   clientlist=[]
   clientcon=[]#客户端连接信息
   def setflag(self):
       self.startflag = 1
       return self.startflag

   def resetflag(self):
       self.startflag = 0
       return self.startflag

   def setadd(self):
       try:
        self.port=int(ui.port_edit.text())
        self.add=ui.add_edit.text()
       except Exception:
           showdialog()

def showflag():
    print("startflag:%d,startedflag:%d"%(d.startflag,d.startedflag))

Hold_register = array('B', [0] * 1000)
Hold_register[0]=0
Hold_register[1]=12
Hold_register[2]=0
Hold_register[3]=16
Hold_register[4]=00
Hold_register[5]=11

Coil_register = array('B', [0] * 200)
Coil_register[0]=110
Coil_register[1]=75
Coil_register[2]=156
Coil_register[3]=189

def get_bit_val(byte, index):
    """
    得到某个字节中某一位（Bit）的值
    :param byte: 待取值的字节值
    :param index: 待读取位的序号，从右向左0开始，0-7为一个完整字节的8个位
    :returns: 返回读取该位的值，0或1
    """
    if byte & (1 << index):
        return 1
    else:
        return 0
def set_bit_val(byte, index, val):
  """
  更改某个字节中某一位（Bit）的值
  :param byte: 准备更改的字节原值
  :param index: 待更改位的序号，从右向左0开始，0-7为一个完整字节的8个位
  :param val: 目标位预更改的值，0或1
  :returns: 返回更改后字节的值
  """
  if val:
    return byte | (1 << index)
  else:
    return byte & ~(1 << index)

def closesocket():
   d.startedflag = 0
   d.clientlist.clear()
   additem()
   q.empty()
   d.sok.close()

def showdialog():
    dialog=QDialog()
    dialog.resize(150,50)
    label1=QLabel("Not valid IP address or Port",dialog)
    label1.move(15,15)
    dialog.setWindowTitle("Error")
    dialog.setWindowModality(Qt.ApplicationModal)
    dialog.exec_()

def additem():
    listit = []
    i=0
    while i<len(d.clientlist):
        listit.append('IP:'+d.clientlist[i]+'   Port:'+d.clientlist[i+1])
        i=i+2
    ui.listWidget.clear()
    ui.listWidget.addItems(listit)

def TCP(conn, addr):
    buffer = array('B', [0] * 10000)
    d.clientlist.append((list(addr))[0])
    print(list(addr)[0])
    d.clientlist.append(str(list(addr)[1]))
    print('\n', list(addr)[1])
    additem()
    while True:
        if d.startflag==0:
            print("close_connection3", d.startflag)
            conn.close()
            break
        else:
         try:
           # print("close_connection4", d.startflag)
            conn.recv_into(buffer,1000)
            TID0 = buffer[0]   #Transaction ID  to sync
            TID1 = buffer[1]   #Transaction ID
            ID = buffer[6]     #Unit ID
            FC = buffer[7]     #Function Code
            mADR = buffer[8]   #Address MSB
            lADR = buffer[9]   #Address LSB
            ADR = mADR * 256 + lADR
            LEN = 1
            if FC==3:
                LEN = buffer[10] * 256 + buffer[11]
                BYT = LEN * 2
                #print('LEN:',BYT)
                DAT=Hold_register[(ADR*2):((ADR*2)+LEN*2)]
               # print('~~~~~~~~~~~~~~~')
               # for i in range(BYT):
               #     print(Hold_register[ADR*2+i])
                #print(DAT)
                conn.send(array('B', [TID0, TID1, 0, 0, 0, BYT + 3, ID, FC, BYT]) + DAT)
            elif FC==1:
                   LEN = math.ceil((buffer[10] * 256 + buffer[11])/8)
                   BYT = LEN * 2
                   ADR_COIL=ADR//8
                   DAT = Coil_register[ADR_COIL:ADR_COIL + LEN*2]
                   conn.send(array('B', [TID0, TID1, 0, 0, 0, BYT + 3, ID, FC, BYT]) + DAT)
            elif FC in [5, 6, 15, 16]:
                conn.send(array('B', [TID0, TID1, 0, 0, 0, 6, ID, FC, mADR, lADR, buffer[10], buffer[11]]))
                if FC==5:
                    coil_addr_byte=int((ADR/8))
                    coil_addr_bit = (ADR)%8
                    #print(buffer[10])
                    #time.sleep(2)
                    if buffer[10]!=0:
                        Coil_register[coil_addr_byte]=set_bit_val(Coil_register[coil_addr_byte], coil_addr_bit, 1)
                    else:
                        Coil_register[coil_addr_byte]=set_bit_val(Coil_register[coil_addr_byte], coil_addr_bit, 0)
                if FC==6:
                    print(ADR)
                    print(buffer[10])
                    print(buffer[11])
                    #time.sleep(1)
                    Hold_register[(ADR)*2]=buffer[10]
                    print(Hold_register[(ADR)*2])
                    Hold_register[(ADR)*2+1] = buffer[11]
                    print(Hold_register[(ADR) * 2+1])
                if FC == 16:
                    print(ADR)
                    print(buffer[10])
                    print(buffer[11])
                    LEN = buffer[10] * 256 + buffer[11]
                    for i in range(LEN):
                      Hold_register[(ADR+i) * 2] = buffer[13+i]
                      print('----------',i)
                      print(Hold_register[(ADR + i) * 2])
                      Hold_register[(ADR+i) * 2 + 1] = buffer[14+i]
                      print(Hold_register[(ADR+i) * 2 + 1])
            else:
                print("Function Code %d Not Supported" % FC)
                exit()
         except Exception as e:
            print(e, "\nConnection with Client terminated")
            d.clientlist.remove((list(addr))[0])
            d.clientlist.remove(str(list(addr)[1]))
            additem()
            q.get()
            conn.close()
            break

def accept_connection_forever(listener1):
    while True:
        print("accept_connection1",d.startflag)
        print("current thread:",threading.currentThread().ident)
        #time.sleep(0.5)
        d.startedflag=1
        clientlist=[]
        if (d.startflag == 1) and (d.startedflag == 1):
            try:
                 d.startedflag = 1
                 d.clientcon, clientaddr = listener1.accept()
                 clientlist=d.clientlist
                 print("accept_connection2", d.startflag)
                 TCP(d.clientcon, clientaddr)
            except Exception as accepterror:
                print(accepterror, "\nSocket has been closed!")
                q.get()
                break
        else:
            print("close_connection1", d.startflag,threading.currentThread().ident)
            if clientlist!=[]:
                  clientlist.close()
                  q.get()
            if (d.startedflag == 1):
                d.startedflag=0
            break

def mainnet():
     while True:
        time.sleep(0.5)#time delay to reduce CPU load
        d.sok = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #d.sok.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if (d.startflag == 1) and (d.startedflag == 0):
            try:
                d.sok.bind((d.addr, d.port))
            except Exception as binderror:#if the addr or port is not valid ,show error information
                d.startflag=0
                print(binderror, "\nbind socket error!")
                showdialog()
                continue
            print("create_srv_socket,d.startflag=", d.startflag)
            print("mainnet start---startflag:%d,startedflag:%d" % (d.startflag, d.startedflag))
            d.sok.listen(1)
            while True:
                time.sleep(0.5)#time delay to reduce CPU load
                print(q.qsize())
                t = (d.sok,)
                if q.full():
                    continue
                if d.startflag==0:
                    break
                Threadlist = Thread(target=accept_connection_forever, args=t)
                q.put(Threadlist, False)
                Threadlist.start()

if __name__=='__main__':
    d=myserver()
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = fm.Ui_MainWindow()
    ui.setupUi(MainWindow)

    ui.startButton.clicked.connect(d.setflag)
    ui.startButton.clicked.connect(d.setadd)
    ui.startButton.clicked.connect(showflag)

    ui.stopButton.clicked.connect(d.resetflag)
    ui.stopButton.clicked.connect(showflag)
    ui.stopButton.clicked.connect(closesocket)

    ui.freshbutton.clicked.connect(additem)
    MainWindow.show()
    Thread(target=mainnet).start()
    sys.exit(app.exec_())
