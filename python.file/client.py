import socket
import pickle
from flask import Flask, render_template, request, url_for, redirect, session, jsonify, flash

import struct
import threading



host = '127.0.0.1'
port = 2021
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Broadcast_Data = {"Type": "No_New_Notification"}
Broadcast_Sub_Data = {"Type": "No_New_Notification"}


sock = socket.socket()

sock.connect((host, port))
app.config['SECRET_KEY'] = '74849hfjkL34352678GHHFe'
broadcast_ip = '227.4.56.7'


def multicasting():
    MCAST_GRP = broadcast_ip
    MCAST_PORT = 2022
    IS_ALL_GROUPS = True

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if IS_ALL_GROUPS:
        s.bind(('', MCAST_PORT))
    else:
        s.bind((MCAST_GRP, MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    while True:
        multicast_raw_data = s.recv(4096)
        print("raw:- ", multicast_raw_data)
        multicast_data = pickle.loads(multicast_raw_data)
        print("loads:- ", multicast_data)

        Multi_Type = multicast_data["Type"]
        print("Multi_Type", Multi_Type)

        if Multi_Type == "Broadcast":
            #Image = multicast_data["Response"]["image"]
            #Title = multicast_data["Response"]["name"]
            #Base_Price = multicast_data["Response"]["base_price"]
            #Expiry_Date = multicast_data["Response"]["expiry_date"]
            #print(Image, Title, Base_Price, Expiry_Date)
            global Broadcast_Data
            Broadcast_Data = multicast_data["Response"]
            print("Broadcast_Data", Broadcast_Data)




        if Multi_Type == "sub_broad":

           #Title = multicast_data["Response"]["Title"]
           #Base_Price = multicast_data["Response"]["Base_Price"]
           #Max_bid = multicast_data["Response"]["Max_bid"]
           #print("Title", Title,
           #      "Base_Price", Base_Price,
           #      "Max_bid", Max_bid)
            global Broadcast_Sub_Data
            Broadcast_Sub_Data = multicast_data["Response"]
            print("Broadcast_Sub_Data = ", Broadcast_Sub_Data)


mu = threading.Thread(target=multicasting)
mu.start()




while True:

    @app.route("/log_in", methods=['GET', 'POST'])
    def log_in():
        print(request.method)
        if request.method == 'POST':
            print("new_jj")
            if request.form.get('Sign_Up') == 'Sign_Up':
                Name = request.form.get('Name')
                Email = request.form.get('Email')
                Address = request.form.get('Address')
                Phone = request.form.get('Phone')
                Password = request.form.get('Password')

                print(Name, Email, Address, Phone, Password)

                User_SignUp_arr = {"type": "Sign_Up", 'Name': Name, 'Email': Email, 'Address': Address, 'Phone': Phone,
                                   'Password': Password}
                User_SignUp_Dump = pickle.dumps(User_SignUp_arr)
                sock.send(User_SignUp_Dump)

                recv_data = sock.recv(1024)
                recv_data_item = pickle.loads(recv_data)
                print(recv_data_item)
                flash(recv_data_item["data"])

                return redirect("/")
            if request.form.get('Sign_In') == 'Sign_In':
                Ename = request.form.get('Ename')
                password = request.form.get('password')

                print(Ename, password)
                SignIn_arr = {"type": "Sign_In", 'Ename': Ename, 'password': password, 'broadcast': broadcast_ip}
                SignIn_Dump = pickle.dumps(SignIn_arr)
                sock.send(SignIn_Dump)
                print("SignIn_Dump", SignIn_Dump)

                User_details_recv = sock.recv(1024)
                User_Data = pickle.loads(User_details_recv)
                print(User_Data)

                type = User_Data["Type"]
                if type == "User":
                    session['user_id'] = User_Data["Data"][0][0]
                    session['user_Name'] = User_Data["Data"][0][1]
                    session['user_Phone_Number'] = User_Data["Data"][0][2]
                    session['user_Email'] = User_Data["Data"][0][3]
                    session['User_Address'] = User_Data["Data"][0][4]
                    print("User_Data", User_Data)
                    flash("Login successful")

                    return redirect("/")

                if type == "Error":
                    session['user_id'] = None
                    session['user_Name'] = None
                    session['user_Phone_Number'] = None
                    session['user_Email'] = None
                    session['User_Address'] = None
                    flash("Login unsuccessful.Try Again")

                    return redirect("/")

        if request.method == 'GET':
            return render_template("form.html")
        # print(Username, Password)


    @app.route("/", methods=['GET', 'POST'])
    def index():
        print(request.method)
        #print("new_jdnfg")
        if request.method == 'GET':
            user_id = session.get('user_id')
            home_details_arr={"type":"F_page"}
            home_details_Dump = pickle.dumps(home_details_arr)
            sock.send(home_details_Dump)

            while True:
                recv_data = sock.recv(4048)
                if not recv_data:
                    break
                print(recv_data)
                recv_data_string = pickle.loads(recv_data)
                print("Received", recv_data_string)

                return render_template("index.html",co_data=recv_data_string, user_id=user_id)

        if request.method == 'POST':
            if request.form.get('fp_sub_bt') == 'fp_sub_bt':
                #print("FP")
                item_id = request.form.get('hide_id')
                print(item_id)
                session['hide_id'] = item_id
                return redirect('/item')

            else:
                return redirect('/item')




    @app.route("/item", methods=['GET', 'POST'])
    def item():
        if request.method == 'GET':
            item_id = session.get('hide_id')

            user_id = session.get('user_id')

            item_details_arr = {"type": "fp_sub_bt", "item_id":item_id}
            item_details_Dump = pickle.dumps(item_details_arr)
            sock.send(item_details_Dump)

            while True:
                recv_data = sock.recv(4048)
                if not recv_data:
                    break
                print(recv_data)
                recv_data_item = pickle.loads(recv_data)
                print("Received", recv_data_item)
                item_page_result=recv_data_item["item_page_result"]
                maxbid_result = recv_data_item["maxbid_result"]

                print(item_page_result, maxbid_result)

                return render_template("item.html",co_data=item_page_result, user_id=user_id,maxbid_result=maxbid_result )

        if request.method == 'POST':
            if request.form.get('Sub_button') == 'Sub_button':

                bid_user_id = request.form.get('bid_user_id')
                item_id = request.form.get('item_id')

                print(bid_user_id, item_id )

                bid_item_id_arr = {"type": "sub_item", "bid_user_id": bid_user_id, "item_id": item_id}
                bid_item_id_Dump = pickle.dumps(bid_item_id_arr)
                sock.send(bid_item_id_Dump)



                recv_data = sock.recv(4048)
                print(recv_data)
                recv_data_sub_item = pickle.loads(recv_data)
                flash(recv_data_sub_item["data"])

                return redirect('/item')



            if request.form.get('bid_button') == 'bid_button':
                # print("FP")
                bid_user_id = request.form.get('bid_user_id')
                item_id = request.form.get('item_id')
                bid_price = request.form.get('bid_price')
                expiry_date= request.form.get('expiry_date')
                time_extd = request.form.get('time_extd')
                print(bid_user_id, item_id,bid_price,time_extd)

                bid_item_id_arr={"type":"new_bid" ,"bid_user_id": bid_user_id, "item_id": item_id, "bid_price": bid_price, "expiry_date":expiry_date, "time_extd":time_extd }
                bid_item_id_Dump = pickle.dumps(bid_item_id_arr)
                sock.send(bid_item_id_Dump)

                return redirect('/item')
            else:
                return redirect('/item')
        return redirect('/item')

    @app.route("/user", methods=['GET', 'POST'])
    def user():
        if request.method == 'GET':

            user_id = session.get('user_id')

            user_details_arr = {"type": "user_profile", "user_id": user_id}
            user_details_Dump = pickle.dumps(user_details_arr)
            sock.send(user_details_Dump)


            while True:
                recv_data = sock.recv(6048)
                if not recv_data:
                    break
                print(recv_data)
                recv_data_item = pickle.loads(recv_data)
                print(recv_data_item)

                user_details=recv_data_item["user_detail"]
                print("user_detail", user_details)

                user_Name = recv_data_item["user_detail"][0][1]
                user_Phone_Number = recv_data_item["user_detail"][0][2]
                user_Email = recv_data_item["user_detail"][0][3]
                User_Address = recv_data_item["user_detail"][0][4]
                print(user_id, user_Name, user_Phone_Number, user_Email, User_Address)

                print("Received", recv_data_item)
                get_bid_items_result=recv_data_item["get_bid_items"]
                input_bid_items_result = recv_data_item["input_bid_items"]

                print(get_bid_items_result, input_bid_items_result)

                return render_template("user.html", user_id= user_id, user_Name=user_Name, user_Phone_Number=user_Phone_Number,user_Email=user_Email,User_Address=User_Address, get_bid_items_result=get_bid_items_result, input_bid_items_result=input_bid_items_result)


        #return render_template("user.html")
    @app.route("/sup", methods=['GET', 'POST'])
    def sup():
        if request.method == 'POST':
            print("new")
            if request.form.get('New_item') == 'New_item':
                owner_id = request.form.get("hide_id")
                image = request.form.get('image')
                name = request.form.get('name')
                base_price = request.form.get('base_price')
                expiry_date = request.form.get('expiry_date')
                item_description = request.form.get('item_description')
                #status = request.form.get('status')
                item_category = request.form.get('item_category')


                print(image, name, base_price, expiry_date, item_description,  item_category)

                #print(Name, Email, Address, Phone, Password)

                New_item_arr = {"type": "New_item", 'owner_id':owner_id, 'image': image, 'name': name, 'base_price': base_price,'expiry_date': expiry_date, 'item_category': item_category,'item_description': item_description}
                New_item_Dump = pickle.dumps(New_item_arr)
                sock.send(New_item_Dump)
                flash("Added New Item")

                return redirect("/user")
            #return redirect("/user")
        #return redirect("/user")



            if request.form.get('User_edit') == 'User_edit':
                E_user_id = request.form.get("hide_edit_id")
                Name = request.form.get('Full_name')
                #Email = request.form.get('Email')
                Address = request.form.get('Address')
                #Phone = request.form.get('Phone-number')


                print(Name, Address )

                User_edit_arr = {"type":"U_edit",'hide_edit_id': E_user_id, 'Name':Name,'Address':Address }
                User_edit_Dump = pickle.dumps(User_edit_arr)
                sock.send(User_edit_Dump)
                flash("Edit success")

                return redirect("/user")
            return redirect("/user")
        return redirect("/user")


    @app.route('/notification', methods=['POST'])
    def notification():

        global Broadcast_Data, Broadcast_Sub_Data
        #print("Broadcast_Data",Broadcast_Data)
        #print("Broadcast_Sub_Data", Broadcast_Sub_Data)

        name = request.form['name']
        print("Request", name)
        if name == "Notification":

           Type_01 = Broadcast_Sub_Data["Type"]
           if Type_01 == "New_Bid":
               print("IN_New_BID", Broadcast_Sub_Data)
               Title = Broadcast_Sub_Data["name"]
               Base_Price = Broadcast_Sub_Data["Base_Price"]
               Max_bid = Broadcast_Sub_Data["Max_bid"]
               return jsonify({"Type":"new_bid",'Title': Title, 'Base_Price': Base_Price, "Max_bid": Max_bid})

           Type_02 = Broadcast_Data["Type"]
           if Type_02 == "New_Item":
               Title = Broadcast_Data["name"]
               Base_Price = Broadcast_Data["base_price"]
               Expiry_Date = Broadcast_Data["expiry_date"]
               return jsonify({"Type":"new_item", 'Title': Title, 'Base_Price': Base_Price, "Expiry_Date": Expiry_Date})
           else:
               return jsonify({'error': 'Missing data!'})

        if name == "Notification_OFF":
            Broadcast_Data = {"Type": "No_New_Notification"}
            Broadcast_Sub_Data = {"Type": "No_New_Notification"}
            return jsonify({'error': 'Missing data!'})





    @app.route("/logout" )
    def logout():

        user_id = session.get('user_id')
        logout_arr = {"type": "logout", 'user_id': user_id,"broadcast_ip":broadcast_ip }
        logout_Dump = pickle.dumps(logout_arr )
        sock.send(logout_Dump)
        recv_data = sock.recv(4048)
        recv_data_string = pickle.loads(recv_data)
        print("Received", recv_data_string )

        if recv_data_string["data"] == 'logout':
            session['user_id'] = None
            session['user_Name'] = None
            session['user_Phone_Number'] = None
            session['user_Email'] = None
            session['User_Address'] = None
            flash("Logout successful")

            return redirect("/")
        return redirect("/")



            #print(item_id)
            #return render_template("item.html",)




 #      return render_template("Register.html")

    if __name__ == "__main__":
            app.run(debug=True, host="127.0.0.2", port=1235)


