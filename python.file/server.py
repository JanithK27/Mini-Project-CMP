import socket
import pickle
import time
from _thread import *
import threading
import mysql.connector
#import datetime
from datetime import datetime
import pandas
import schedule





data_base = mysql.connector.connect(
    host='127.0.0.3',
    user='root',
    passwd='mysql',
    database='cmp_new')

db_con = data_base.cursor()




host = '127.0.0.1'
port = 2021

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

soc.bind((host, port))

soc.listen()

all_conn=[]

def multi_threading(c):


    while True:
        recv_data = c.recv(4048)
        if not recv_data:
            break

        recv_data_string = pickle.loads(recv_data)
        print("Received", recv_data_string)
        print(recv_data)


        type = recv_data_string["type"]
        print(type)
        if type == "Sign_Up":

            Name = recv_data_string['Name']

            Phone_Number = recv_data_string['Phone']
            Email = recv_data_string['Email']
            Password = recv_data_string['Password']
            User_Address = recv_data_string['Address']

            print(Name, Phone_Number, Email, Password, User_Address)

            try:
                sql_q1 = ("INSERT INTO user (user_id, Name, Phone_Number, Email, Password, User_Address) VALUES (NULL, %s, %s, %s, %s,%s);")
                value = (Name, Phone_Number, Email, Password, User_Address)
                db_con.execute(sql_q1, value)
                data_base.commit()


                sql_uphone =  "SELECT user_id FROM user WHERE Phone_Number = %s;" % Phone_Number
                db_con.execute(sql_uphone)
                phoneuser_id_arr = db_con.fetchall()
                print("Sign_Up_User_ID: ", phoneuser_id_arr)
                user_id = phoneuser_id_arr[0][0]

                broadcast_sql = "INSERT INTO broadcast VALUES (Null, %s, NULL);" % user_id
                db_con.execute(broadcast_sql)
                data_base.commit()

                signup_response = {'Type': "Successful", 'data': 'Successfully! Signup'}
                signup_response_dump = pickle.dumps(signup_response)
                c.sendall(signup_response_dump)
            except:
                print("Invalid details. Please try again")
                response_error = {'Type': "Error", 'data': 'Invalid details. Please try again'}
                response_error_dum = pickle.dumps(response_error)
                c.sendall(response_error_dum)


        if type == "Sign_In":

            Ename = recv_data_string['Ename']
            password = recv_data_string['password']


            print(Ename, password)
            sql_q2 = """SELECT COUNT(email) FROM user WHERE email ='%s' AND password = '%s' """ % (Ename, password)
            db_con.execute(sql_q2)
            login_result = db_con.fetchall()

            print(login_result)
            print("Log count", login_result[0][0])


            if login_result[0][0] == 1:
                log_true ="SELECT user_id, Name,  Phone_Number, Email, User_Address FROM user WHERE email ='%s' AND password = '%s'" % (Ename, password)
                db_con.execute(log_true)
                user_detail = db_con.fetchall()
                print("user_log_details", user_detail)
                usr_arr = {"Type": "User", "Data": user_detail}
                usr_details = pickle.dumps(usr_arr)
                c.sendall(usr_details)
                broadcast = recv_data_string['broadcast']
                #if broadcast not in all_conn:
                all_conn.append(broadcast)


                User_ID=user_detail[0][0]
                multicast_sql = "UPDATE broadcast SET broadcast_IP= %s WHERE user_id = %s;"
                val = (broadcast, User_ID)
                db_con.execute(multicast_sql, val)
                data_base.commit()

            else:
                usr_arr = {"Type": "Error" }
                usr_details = pickle.dumps(usr_arr)
                c.sendall(usr_details)

        if type == "F_page":

            sql_q3 = """SELECT item_id, image, name, item_category, status ,base_price, expiry_date FROM item;"""
            db_con.execute(sql_q3)
            F_page_result = db_con.fetchall()

            print("F_page_details",F_page_result)
            F_page_details = pickle.dumps(F_page_result)
            print(F_page_details)
            c.send(F_page_details)



        if type == "fp_sub_bt":
            item_id = recv_data_string['item_id']
            print(item_id)
            sql_q4 = "SELECT item_id, image, name, item_category, status ,base_price, expiry_date,time_extd, item_description FROM item WHERE item_id = '%s';"% (item_id)
            db_con.execute(sql_q4)
            item_page_result = db_con.fetchall()
            print("item_page_details",item_page_result)


            Sql_q5 = "SELECT max(bid_price) FROM bid WHERE item_id = '%s';" % (item_id)
            db_con.execute(Sql_q5)
            maxbid_result = db_con.fetchall()
            print("maxbid_result", maxbid_result)


            bid_item_details ={"item_page_result":item_page_result,"maxbid_result":maxbid_result}
            ibid_item_arr = pickle.dumps(bid_item_details)
            c.sendall(ibid_item_arr)


            #print(item_page_details)
            #c.send(item_page_details)

        if type == "new_bid":



            bid_user_id = recv_data_string['bid_user_id']
            item_id = recv_data_string['item_id']
            bid_price = recv_data_string['bid_price']
            expiry_date = recv_data_string['expiry_date']
            time_extd = recv_data_string['time_extd']
            print(time_extd)

            if bid_end_check(expiry_date) > 60 or time_extd == "TRUE":

                print(bid_user_id, item_id, bid_price, expiry_date)
                sql_q5="INSERT INTO bid (bid_id, item_id, bid_user_id, bid_price) VALUES (NULL, %s, %s, %s);"
                value = (item_id, bid_user_id, bid_price)
                print(bid_price)
                db_con.execute(sql_q5, value)
                data_base.commit()

                bid_noti_sql = "SELECT name, base_price, max(bid_price) FROM item LEFT JOIN bid ON item.item_id = bid.item_id WHERE item.item_id = %s;" % item_id
                db_con.execute(bid_noti_sql)
                bid_noti_arr = db_con.fetchall()
                print(bid_noti_arr)

                Title = bid_noti_arr[0][0]
                Base_Price = bid_noti_arr[0][1]
                Max_bid = bid_noti_arr[0][2]

                new_bid_arr = {"Type": "New_Bid", "item_id": item_id, "name": Title, "Base_Price": Base_Price,
                               "Max_bid": Max_bid}
                Notification_Type = "New_Bid"
                mu = threading.Thread(target=new_item_noti, args=(Notification_Type, new_bid_arr))
                mu.start()

            if bid_end_check(expiry_date) <= 60 and time_extd != "TRUE":
                current_time = str(datetime.now())
                current_time_expand = current_time[:19]
                date_format_str = '%Y-%m-%d %H:%M:%S'
                time_convert = datetime.strptime(current_time_expand, date_format_str)
                print("time_convert", time_convert)
                extended_time = 60 + bid_end_check(expiry_date)
                final_time = time_convert + pandas.DateOffset(seconds=extended_time)
                final_time_str = final_time.strftime('%Y-%m-%d %H:%M:%S')
                print("final_time_str", final_time_str)

                print(bid_user_id, item_id, bid_price, expiry_date)
                sql_q5 = "INSERT INTO bid (bid_id, item_id, bid_user_id, bid_price) VALUES (NULL, %s, %s, %s);"
                value = (item_id, bid_user_id, bid_price)
                print(bid_price)
                db_con.execute(sql_q5, value)
                data_base.commit()

                DateTime_sql = "UPDATE item SET expiry_date = %s, time_extd = 'TRUE' WHERE item_id = %s;"
                val = (final_time_str, item_id,)
                db_con.execute(DateTime_sql, val)
                data_base.commit()

                bid_noti_sql = "SELECT name, base_price, max(bid_price) FROM item LEFT JOIN bid ON item.item_id = bid.item_id WHERE item.item_id = %s;" % item_id
                db_con.execute(bid_noti_sql)
                bid_noti_arr = db_con.fetchall()
                print(bid_noti_arr)

                Title = bid_noti_arr[0][0]
                Base_Price = bid_noti_arr[0][1]
                Max_bid = bid_noti_arr[0][2]

                new_bid_arr = {"Type": "New_Bid", "item_id": item_id, "name": Title, "Base_Price": Base_Price,
                               "Max_bid": Max_bid}
                Notification_Type = "New_Bid"
                mu = threading.Thread(target=new_item_noti, args=(Notification_Type, new_bid_arr))
                mu.start()



        if type == "user_profile":
            user_id = recv_data_string['user_id']
            print(user_id)

            log_true = "SELECT user_id, Name,  Phone_Number, Email, User_Address FROM user WHERE user_id = %s" % (user_id)
            db_con.execute(log_true)
            user_detail = db_con.fetchall()
            print("user_log_details", user_detail)

            sql_q6="SELECT item.name, base_price, bid_price  FROM item LEFT JOIN bid ON bid.item_id = item.item_id LEFT JOIN user ON bid.bid_user_id = user.user_id WHERE bid_user_id = '%s' and bid.bid_price <> 'NULL';" %(user_id)
            db_con.execute(sql_q6)
            get_bid_items = db_con.fetchall()
            print(get_bid_items)

            sql_q7="SELECT DISTINCT item.item_id, item.name,base_price FROM item LEFT JOIN bid ON bid.bid_id = item.item_id WHERE seller_id = %s;"%(user_id)
            db_con.execute(sql_q7)
            input_bid_items = db_con.fetchall()
            print(input_bid_items)

            get_bid_items_details = {"get_bid_items": get_bid_items, "input_bid_items":input_bid_items, "user_detail": user_detail}
            get_bid_items_details_arr = pickle.dumps(get_bid_items_details)
            c.sendall(get_bid_items_details_arr)

        if type == "New_item":
            owner_id = recv_data_string['owner_id']
            image  = recv_data_string['image']
            name  = recv_data_string['name']
            base_price  = recv_data_string['base_price']
            expiry_date  = recv_data_string['expiry_date']
            item_description  = recv_data_string['item_description']
            #status  = recv_data_string['status']
            item_category  = recv_data_string['item_category']

            #print(Name, Phone_Number, Email, Password, User_Address)


            sql_q1 = ("INSERT INTO item (item_id, seller_id, image, name, item_category, base_price, expiry_date, item_description, status,time_extd ) VALUES (NULL,%s,%s, %s, %s,%s,%s,%s,'Available','false');")
            value = (owner_id,image,name,item_category,base_price,expiry_date,item_description)
            db_con.execute(sql_q1, value)
            data_base.commit()

            new_item_arr = {"Type":"New_Item","image": image, "name": name, "base_price": base_price,
                            "expiry_date": expiry_date}
            Notification_Type = "New_Item"
            mu = threading.Thread(target=new_item_noti, args=(Notification_Type, new_item_arr))
            mu.start()

        if type == "U_edit":

            E_user_id = recv_data_string['hide_edit_id']
            Name = recv_data_string['Name']
            #Phone = recv_data_string['Phone']
            #Email = recv_data_string['Email']
            Address = recv_data_string['Address']


            print(E_user_id,Name, Address)



            sql_edit = "UPDATE user SET Name=%s,User_Address=%s  WHERE user_id=%s;"
            value = (Name, Address, E_user_id)
            db_con.execute(sql_edit,value)
            data_base.commit()

        if type == "sub_item":
            bid_user_id = recv_data_string['bid_user_id']
            item_id = recv_data_string['item_id']

            print(bid_user_id, item_id)
            sql_q5 = "INSERT INTO bid (bid_id, item_id, bid_user_id, bid_price,status) VALUES (NULL, %s, %s, NULL,'Subscribe');"
            value = (item_id, bid_user_id)
            db_con.execute(sql_q5, value)
            data_base.commit()

            response_sub = {'Type': "Response", 'data': 'Successfully! You have subscribed'}
            new_response_sub = pickle.dumps(response_sub)
            c.sendall(new_response_sub)

        if type == "logout":
            user_id = recv_data_string['user_id']
            broadcast_ip = recv_data_string['broadcast_ip']

            print( user_id, broadcast_ip)
            if broadcast_ip in all_conn:
                all_conn.remove(broadcast_ip)

            logout_sql = "UPDATE broadcast SET broadcast_IP= NULL  WHERE user_id = '%s';" % user_id
            db_con.execute(logout_sql)
            data_base.commit()

            response_logout = {'Type': "Response", 'data': 'logout'}
            new_response = pickle.dumps(response_logout)
            c.sendall(new_response)




def new_item_noti(Notification_Type, Data):
    #print("New_Item_Func")
    #print("Data: ", Data)
    new_item_arr = Data
    #print(all_conn)
    if Notification_Type == "New_Item":
        time.sleep(0.251)
        all_user_sql = "SELECT broadcast_IP FROM broadcast WHERE broadcast_IP IS NOT NULL;"
        db_con.execute(all_user_sql)
        all_conn = db_con.fetchall()
        print("all_user= ", all_conn)

        for m_ip in range(0,len(all_conn)):
            print("New_Item_Func_loop")
            MCAST_GRP = all_conn[m_ip][0]
            MCAST_PORT = 2022
            MULTICAST_TTL = 10
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
            multicasting_response = {'Type': 'Broadcast', 'Response': new_item_arr}
            multicasting_response_Dump = pickle.dumps(multicasting_response)
            sock.sendto(multicasting_response_Dump, (MCAST_GRP, MCAST_PORT))
            if m_ip == (len(all_conn)-1):
                m_ip=0
                break

    if Notification_Type == "New_Bid":
        print("bb")
        new_bid_arr = Data
        Item_ID = new_bid_arr["item_id"]
        print(Item_ID)
        time.sleep(0.5)
        sub_user_sql = "SELECT DISTINCT bid_user_id FROM bid WHERE item_id = %s;"% Item_ID

        db_con.execute(sub_user_sql)
        sub_user = db_con.fetchall()
        print("sub_user", sub_user)

        sub_user_arr = []
        for i in sub_user:
            print("sub_user", i[0])
            sub_user_arr.append(i[0])
        broadcast_ip_arr = []
        for i in sub_user_arr:
            sub_user_b_IP_sql = "SELECT broadcast_IP FROM broadcast WHERE user_id = %s;" % i
            db_con.execute(sub_user_b_IP_sql)
            broadcast_IP = db_con.fetchall()
            print("broadcast_IP[0][0]", broadcast_IP[0][0])

            if broadcast_IP[0][0] is None:
                pass

            if broadcast_IP[0][0] is not None:
                print("None")
                broadcast_ip_arr.append(broadcast_IP[0][0])
        #print( broadcast_ip_arr)


        for sub_ip in range(0,len(broadcast_ip_arr)):
            print("New_Item_Func_loop")
            MCAST_GRP = broadcast_ip_arr[sub_ip]
            MCAST_PORT = 2022
            MULTICAST_TTL = 10
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
            multicasting_response = {'Type': 'sub_broad', 'Response': new_bid_arr}
            multicasting_response_Dump = pickle.dumps(multicasting_response)
            sock.sendto(multicasting_response_Dump, (MCAST_GRP, MCAST_PORT))
            if sub_ip == (len(broadcast_ip_arr)-1):
                sub_ip=0
                break

def bid_end_check(Expiry_Date):
   while True:
       time_str = Expiry_Date
       date_format_str = '%Y-%m-%d %H:%M:%S'
       expiry_time = datetime.strptime(time_str, date_format_str)
       now_time = datetime.now()
       duration = expiry_time - now_time
       duration_in_sec = duration.total_seconds()
       print("bid_end_check", duration_in_sec)

       return duration_in_sec

def bid_end():
    item_sql = """SELECT item_id, expiry_date FROM item WHERE time_extd <> 'TRUE' AND status = "Available";"""
    db_con.execute(item_sql)
    item_result = db_con.fetchall()
    # print(home_result)
    bid_ended_items = []
    while True:
        for i in range(0, len(item_result)):
            arr = str(item_result[i][1])
            date_format_str = '%Y-%m-%d %H:%M:%S'
            expiry_time = datetime.strptime(arr, date_format_str)
            now_01 = str(datetime.now())
            now_02 = (now_01[:19])
            ex = datetime.strptime(now_02, date_format_str)
            duration = expiry_time - ex
            duration_in_s = duration.total_seconds()
            print("Final", duration_in_s)
            if duration_in_s < 3:
                item_id = item_result[i][0]
                print(item_id)
                max_bid_sql = "SELECT item_id, bid_user_id, max(bid_price) FROM bid WHERE item_id = %s;" % item_id
                db_con.execute(max_bid_sql)
                max_bid_result = db_con.fetchall()
                bid_ended_items.append(max_bid_result)
        # print(bid_ended_items)
        for update_item in bid_ended_items:
            print(update_item)
            bid_item_id = update_item[0][0]
            bid_buyer_id = update_item[0][1]
            sold_price = update_item[0][2]
            # print(bid_item_id,bid_buyer_id,sold_price)
            final_bid_sql = "UPDATE item SET buyer =%s, sold_price = %s , status='Sold' WHERE item_id = %s;"
            val = (bid_buyer_id, sold_price, bid_item_id)
            db_con.execute(final_bid_sql, val)
            data_base.commit()
        print("Final_Bid_Updated")
        break
    print("end")

def extended_bid_end():
    item_sql = """SELECT item_id, expiry_date FROM item WHERE time_extd = 'TRUE' AND status = "Available";"""
    db_con.execute(item_sql)
    item_result = db_con.fetchall()
    # print(home_result)
    bid_ended_items = []
    while True:
        for i in range(0, len(item_result)):
            item_id = item_result[i][0]
            max_bid_sql = "SELECT item_id, bid_user_id, max(bid_price) FROM bid WHERE item_id = %s;" % item_id
            db_con.execute(max_bid_sql)
            max_bid_result = db_con.fetchall()
            bid_ended_items.append(max_bid_result)
        # print(bid_ended_items)
        for update_item in bid_ended_items:
            # print(update_item)
            bid_item_id = update_item[0][0]
            bid_buyer_id = update_item[0][1]
            sold_price = update_item[0][2]
            # print(bid_item_id,bid_buyer_id,sold_price)
            final_bid_sql = "UPDATE item SET buyer =%s, sold_price = %s , status='Sold' WHERE item_id = %s;"
            val = (bid_buyer_id, sold_price, bid_item_id)
            db_con.execute(final_bid_sql, val)
            data_base.commit()
        print("Final_Bid_Updated")
        break
    print("end")

def force_end_bid():
    item_sql = """SELECT item_id, expiry_date FROM item WHERE time_extd <> 'TRUE' AND status = "Available";"""
    db_con.execute(item_sql)
    item_result = db_con.fetchall()
    # print(home_result)
    bid_ended_items = []
    while True:
        for i in range(0, len(item_result)):
            arr = str(item_result[i][1])
            date_format_str = '%Y-%m-%d %H:%M:%S'
            expiry_time = datetime.strptime(arr, date_format_str)
            now_01 = str(datetime.now())
            now_02 = (now_01[:19])
            ex = datetime.strptime(now_02, date_format_str)
            duration = expiry_time - ex
            duration_in_s = duration.total_seconds()
            print("Final", duration_in_s)
            if duration_in_s < 0:
                item_id = item_result[i][0]
                print(item_id)

                force_end_bid_sql = "UPDATE item SET status='Expired' WHERE item_id = %s;" % item_id
                db_con.execute(force_end_bid_sql)
                data_base.commit()

        break
    print("end")

    #if Notification_Type == "New_Bid":
    #    new_bid_arr = Data
    #    Item_ID = new_bid_arr["Item_ID"]
    #    sub_user_sql = "SELECT DISTINCT bid_buyer_id FROM bid_item WHERE bid_item_id = %s;" % Item_ID
    #    db_con.execute(sub_user_sql)
    #    sub_user = db_con.fetchall()
    #    print("sub_user", sub_user)
#
    #    sub_user_arr = []
    #    for i in sub_user:
    #        print("sub_user", i[0])
    #        sub_user_arr.append(i[0])
#
    #    broadcast_ip_arr = []
    #    for i in sub_user_arr:
    #        sub_user_broadcast_IP_sql = "SELECT broadcast_IP FROM multicast WHERE user_id = %s;" % i
    #        db_01.execute(sub_user_broadcast_IP_sql)
    #        broadcast_IP = db_01.fetchall()
    #        print("broadcast_IP[0][0]",broadcast_IP[0][0])
    #        if broadcast_IP[0][0] != None:
    #            print("None")
    #            broadcast_ip_arr.append(broadcast_IP[0][0])
    #    print("broadcast_ip_arr: ", broadcast_ip_arr)
    #    for m_ip in range(0,len(broadcast_ip_arr)):
    #        print("New_Bid_Func_loop")
    #        MCAST_GRP = broadcast_ip_arr[m_ip]
    #        MCAST_PORT = 2022
    #        MULTICAST_TTL = 10
    #        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    #        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
#
    #        multicasting_response = {'Type': 'Broadcast_Sub', 'Response': new_bid_arr}
    #        multicasting_response_Dump = pickle.dumps(multicasting_response)
    #        sock.sendto(multicasting_response_Dump, (MCAST_GRP, MCAST_PORT))
    #        if m_ip == (len(multicast_connections)-1):
    #            sub_user_arr = []
#
    #            break
#
    #    print("New_bid lawata goda")
#



schedule.every().day.at("23:59:57").do(bid_end)
schedule.every().day.at("00:01:02").do(extended_bid_end)
schedule.every().day.at("00:00:01").do(force_end_bid)




def clock():
    while True:
        schedule.run_pending()
        time.sleep(0.5)


time_run = threading.Thread(target=clock)
time_run.start()



while True:


    client, addr = soc.accept()
    print('Connected to: ' + addr[0] + ':' + str(addr[1]))
    cli = threading.Thread(target=multi_threading, args=(client,))
    cli.start()
#start_new_thread(multi_threading, (client,))


