import as608 as as608

def fp_test():
    session = as608.connect_serial_session("COM3")
    if session:
        as608.get_templates_list(session)
        as608.get_templates_count(session)
        as608.get_device_size(session)
        # as608.enroll_finger_to_device(session, as608)
        print(as608.search_fingerprint_on_device(session, as608))
    # as608.enroll_save_to_file(session, as608, "database", "templ1")
    # as608.enroll_save_to_file(session, as608, "database", "templ000000001")
    # as608.fingerprint_check_one_file(session, as608, "database", "templ1")
    # as608.fingerprint_check_one_file(session, as608, "database", "templ000000001")
    # print(as608.fingerprint_check_all_file(session, as608, "database"))
    else:
        print("EXIT")

    # import binascii
    # import serial
    # import serial.tools.list_ports
    # import time
    # # volatile unsigned char FPM10A_RECEICE_BUFFER[32];        //定义接收缓存区
    # # code unsigned char FPM10A_Pack_Head[6] = {0xEF,0x01,0xFF,0xFF,0xFF,0xFF};  //协议包头
    # # code unsigned char FPM10A_Get_Img[6] = {0x01,0x00,0x03,0x01,0x00,0x05};    //获得指纹图像
    # # code unsigned char FPM10A_Img_To_Buffer1[7]={0x01,0x00,0x04,0x02,0x01,0x00,0x08}; //将图像放入到BUFFER1
    # # code unsigned char FPM10A_Search[11]={0x01,0x00,0x08,0x04,0x01,0x00,0x00,0x00,0x64,0x00,0x72}; //搜索指纹搜索范围0 - 999,使用BUFFER1中的特征码搜索

    # def recv(serial):
    #     while True:
    #         data = serial.read_all()
    #         if data == '':
    #             continue
    #         else:
    #             break
    #     return data

    # if __name__ == '__main__':
    #     serial = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5)  #/dev/ttyUSB0
    #     if serial.isOpen() :
    #         print("open success")
    #     else :
    #         print("open failed")
    #     while True:
    #         a = 'EF 01 FF FF FF FF 01 00 03 01 00 05'
    #         d = bytes.fromhex(a)
    #         serial.write(d)
    #         time.sleep(1)
    #         data =recv(serial)
    #         if data != b'' :
    #             data_con = str(binascii.b2a_hex(data))[20:22]
    #             if(data_con == '02'):
    #                 print("请按下手指")
    #             elif(data_con == '00'):
    #                 print("载入成功")
    #                 buff = 'EF 01 FF FF FF FF 01 00 04 02 01 00 08'
    #                 buff = bytes.fromhex(buff)
    #                 serial.write(buff)
    #                 time.sleep(1)
    #                 buff_data = recv(serial)
    #                 buff_con = str(binascii.b2a_hex(buff_data))[20:22]
    #                 if(buff_con == '00'):
    #                     print("生成特征成功")
    #                     serch = 'EF 01 FF FF FF FF 01 00 08 04 01 00 00 00 64 00 72'
    #                     serch = bytes.fromhex(serch)
    #                     serial.write(serch)
    #                     time.sleep(1)
    #                     serch_data = recv(serial)
    #                     serch_con = str(binascii.b2a_hex(serch_data))[20:22]
    #                     if (serch_con == '09'):
    #                         print("指纹不匹配")
    #                     elif(serch_con == '00'):
    #                         print("指纹匹配成功")
    #                 serial.close()
    #                 exit()
    #             else:
    #                 print("不成功")
