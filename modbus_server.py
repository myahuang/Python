#最原始的modbus_server框架
import socket
import math
import time
from threading import Thread
from array import array

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

def TCP(conn, addr):
    buffer = array('B', [0] * 100)
    cnt = 0
    while True:
        if cnt < 60000: cnt = cnt + 1
        else: cnt = 1
        try:
            conn.recv_into(buffer,12)
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
                DAT=Hold_register[ADR:(ADR+LEN*2)]
                #print(DAT)
                conn.send(array('B', [TID0, TID1, 0, 0, 0, BYT + 3, ID, FC, BYT]) + DAT)
            elif FC==1:
                   LEN = math.ceil((buffer[10] * 256 + buffer[11])/8)
                   BYT = LEN * 2
                   ADR_COIL=ADR//8
                   DAT = Coil_register[ADR_COIL:ADR_COIL + LEN*2]
                   conn.send(array('B', [TID0, TID1, 0, 0, 0, BYT + 3, ID, FC, BYT]) + DAT)

            elif (FC in [5, 6, 15, 16]):
                conn.send(array('B', [TID0, TID1, 0, 0, 0, 6, ID, FC, mADR, lADR, buffer[10], buffer[11]]))
                if FC==5:
                    coil_addr_byte=((ADR)/8)
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
                    Hold_register[(ADR)*2+1] = buffer[11]

            else:
                print("Funtion Code %d Not Supported" % FC)
                exit()
        except Exception as e:
            print(e, "\nConnection with Client terminated")
            conn.close()
            break

def create_srv_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 502))
    s.listen(4)
    return s

def accept_connection_forever(listener1):
    while True:
        conn,addr = listener1.accept()
        TCP(conn, addr)

if __name__=='__main__':
    listener = create_srv_socket()
    t=(listener,)
    for i in range(3):
        Thread(target=accept_connection_forever,args=t).start()

