import shutil
import threading
import time
import tkinter as tk
from tkinter import Label, Button, Menu, messagebox, StringVar, Entry, X, BOTTOM, SUNKEN, W, E
import os
import webbrowser
import pyrebase
import requests


class FirebaseConfig:
    def __init__(self):

        # MAKE SURE YOU ADD YOUR OWN API KEYS FROM YOUR FIREBASE PROJECT

        self.firebaseConfig = {
            "apiKey": "AIzaSyAk0xzpUuH0LYXihigz3OXentCn1T8YC3Q",
            "authDomain": "global-testing-env.firebaseapp.com",
            "databaseURL": "https://global-testing-env-default-rtdb.firebaseio.com",
            "projectId": "global-testing-env",
            "storageBucket": "global-testing-env.appspot.com",
            "messagingSenderId": "403456253125",
            "appId": "1:403456253125:web:129423ef3a31c45a5a24ac"
        }

        self.firebase = pyrebase.initialize_app(self.firebaseConfig)
        self.auth = self.firebase.auth()
        self.storage = self.firebase.storage()

    def register(self, username, password):
        try:
            user = self.auth.create_user_with_email_and_password(username, password)
            self.auth.send_email_verification(user['idToken'])
            return True
        except:
            return False

    def login_user(self, username, password):
        try:
            login = self.auth.sign_in_with_email_and_password(username, password)
            return login
        except:
            return False

    def reset_password(self, username):
        try:
            self.auth.send_password_reset_email(username)
            return
        except:
            return False

    # def resend_verification_email(self):
    #     try:
    #         with open('session', 'r') as user_cred:
    #             cred = json.load(user_cred)
    #             self.auth.send_email_verification(cred['idToken'])
    #     except:
    #         return False


class FirebaseTkinterApp(tk.Tk):

    # __init__ function for class FirebaseTkinterApp
    def __init__(self, *args, **kwargs):
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)

        # App version number
        self.current_version = '1.0'

        self.title(f"FirebaseTkinterApp_v{self.current_version}")
        self.iconbitmap(r'logo.ico')

        self.defaultbg = self.cget('bg')
        # this data is shared among all the classes
        self.app_login_cred = {'email': StringVar(), 'idToken': StringVar()}

        self.status_label = Label(self, text="", font=('ariel', 10, 'italic bold'), bd=1, relief=SUNKEN, anchor=W)
        self.status_label.pack(fill=X, side=BOTTOM, ipady=1)

        # creating a container
        container = tk.Frame(self)
        self.geometry('{}x{}'.format(600, 600))
        container.pack(side="top", fill="both", expand=True)

        self.defaultbg = self.cget('bg')

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # initializing frames to an empty array
        self.frames = {}

        # iterating through a tuple consisting
        # of the different page layouts
        for F in (Disclaimer, LoginPage, About, DonatePage, UserHomepage, StartFrame):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Disclaimer)

        def callback(self, url):
            webbrowser.open_new(url)

        '''
        
        In order to get the UPDATE function working, create a file with name as 'version' without any extension within your Firebase Storage Bucket and add your version number as mentioned below.
        
        {"version" : "1.0"}
        
        '''
        def check_update():
            time.sleep(4)
            z = FirebaseConfig()
            u = z.storage.child('version').get_url(None)
            b = requests.get(u).json()

            if b['version'] == self.current_version:
                pass
            else:
                ans = messagebox.askquestion("Alert!", "A new update is available, would you like to download it now?")
                if ans == 'yes':
                    callback(self, 'https://github.com/fortysev-en/FirebaseTkinterApp')
                else:
                    pass

        threading.Thread(target=check_update, daemon=True).start()

        menubar = Menu()

        # Adding File Menu and commands
        file = Menu(menubar, tearoff=0)
        # Adding Help Menu
        help_ = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Help', menu=help_)
        help_.add_command(label='Quickstart Guide...', command=lambda: callback(self, "https://thefortyseven.dev/firebase-tkinter-login-signup-app-template"))
        help_.add_separator()
        help_.add_command(label='Report a Bug...', command=lambda: callback(self, "https://thefortyseven.dev/contact"))
        help_.add_separator()
        help_.add_command(label='Support the Project...', command=lambda: callback(self,
                                                                                   "https://thefortyseven.dev/donatePage"))
        help_.add_separator()
        help_.add_command(label='Contact',
                          command=lambda: callback(self, "https://thefortyseven.dev/contact"))

        # display Menu
        self.config(menu=menubar)

        status_label_top_left = Label(self, text="", font=('ariel', 10, 'bold'), bd=1, relief=SUNKEN, anchor=W)
        status_label_top_left.place(x=0, y=0, width=400, height=20)

        status_label_top_right = Label(self, text="", font=('ariel', 10, 'bold'), bd=1, relief=SUNKEN, anchor=E)
        status_label_top_right.place(x=400, y=0, width=200, height=20)

        # A single Firebase session is valid for 60 mins / 1 hour hence the countdown to display the time remaining, user after this will have to login again
        def update_statusbar():
            if '@' not in (self.app_login_cred['email'].get()):
                time.sleep(2)
                update_statusbar()
            else:
                status_label_top_left.config(text=f"{self.app_login_cred['email'].get()}")
                def countdown(time_sec):
                    while time_sec:
                        mins, secs = divmod(time_sec, 60)
                        timeformat = '{:02d}:{:02d}'.format(mins, secs)
                        if timeformat == '15:00':
                            status_label_top_right.config(fg='orange')
                        elif timeformat == '05:00':
                            status_label_top_right.config(fg='red')
                        status_label_top_right.config(text=f"{timeformat} ")
                        time.sleep(1)
                        time_sec -= 1
                    status_label_top_right.config(text=f"SESSION TIMEOUT, please relogin!", fg="#c00000")

                threading.Thread(target=lambda: countdown(3600), daemon=True).start()

        threading.Thread(target=update_statusbar, daemon=True).start()

    if os.path.exists('output/temp'):
        shutil.rmtree('output/temp', ignore_errors=True)

    def distroy_window(self):
        app.destroy()

    def show_frame_head(self):
        def callback(self, url):
            webbrowser.open_new(url)

        def on_enter(event):
            auth_name.config(fg='green', cursor="question_arrow")

        def on_leave(enter):
            auth_name.config(fg='#c00000')

        Label(self, text="FirebaseTkinterApp", fg="#c00000", font=('ariel', 20, 'bold')).place(x=170, y=40)
        auth_name = Label(self, text='========================== by fortyseven ==========================', fg="#c00000", font=('ariel', 8, 'italic'))
        auth_name.place(x=110, y=80)
        auth_name.bind("<Button-1>", lambda e: callback(self, "https://thefortyseven.dev"))
        auth_name.bind("<Enter>", on_enter)
        auth_name.bind("<Leave>", on_leave)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class Disclaimer(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        #         # controller.show_frame_head()

        Label(self, text="DISCLAIMER", fg="#282828", font=('ariel', 20, 'bold')).place(x=210, y=150)
        Label(self,
              text="This tool is meant for EDUCATION PURPOSE ONLY. I personally DO NOT support or promote any unethical practices, as said, it is solely meant for education purpose only. Any misuse of this tool will be completely at your OWN risks.",
              fg="#282828", font=('ariel', 10, 'bold'), wraplength=450).place(x=85, y=250)

        Button(self, text="About", font=('ariel', 10, 'bold'),
               command=lambda: controller.show_frame(About)).place(x=50, y=520, width=110)

        ## button to show frame 2 with text layout2
        Button(self, text="Accept and Next", font=('ariel', 10, 'bold'), fg="white", bg="green",
               command=lambda: controller.show_frame(LoginPage)).place(x=270, y=520, width=150)
        # exit button for checking connection window
        Button(self, text="Exit", font=('ariel', 10, 'bold'), fg="white", bg="#c00000",
               command=lambda: controller.distroy_window()).place(
            x=440, y=520, width=110)


class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        img_logo = tk.PhotoImage(file='merces_logos.png')
        img_logo_label = tk.Label(self, image=img_logo)
        img_logo_label.place(x=220, y=50)
        img_logo_label.image = img_logo

        Label(self, text='FirebaseTkinterApp', fg="#c00000", font=('ariel', 15, 'bold')).place(x=200, y=200)

        def pass_focus(event):
            passwordEntry.delete('0', 'end')
            passwordEntry.config(show='*')

        def raise_login_frame(event):
            login_frame.tkraise()

        a = FirebaseConfig()

        def sign_up_frame(event):
            signup_frame = tk.Frame(self)

            Label(signup_frame, text="SIGN UP", fg="#282828", font=('ariel', 10, 'bold')).place(x=185, y=0)

            def reg_user(controller):
                if (usernameEntry.get() == '') or (passwordEntry.get() == ''):
                    controller.status_label.config(text="Error! email/password cannot be empty!", fg="#c00000")
                else:
                    signup_btn.config(state="disabled")
                    controller.status_label.config(text="Please wait, signing you up...")
                    response = a.register(usernameEntry.get(), passwordEntry.get())
                    if response:
                        signup_btn.config(state="normal")
                        controller.status_label.config(
                            text="Account successfully registered, please verify your email before using the app!",
                            fg="green")
                    else:
                        signup_btn.config(state="normal")
                        controller.status_label.config(text="Error! email already exist!")

            usernameEntry = Entry(signup_frame, textvariable=username)
            usernameEntry.place(x=125, y=70, width=180)
            usernameEntry.delete('0', 'end')
            usernameEntry.insert(0, 'Email Address')
            usernameEntry.bind("<FocusIn>", lambda args: usernameEntry.delete('0', 'end'))

            passwordEntry = Entry(signup_frame, textvariable=password)
            passwordEntry.place(x=125, y=100, width=180)
            passwordEntry.delete('0', 'end')
            passwordEntry.insert(0, 'Password')
            passwordEntry.bind("<FocusIn>", pass_focus)

            signup_btn = Button(signup_frame, text="Sign Up", font=('ariel', 10, 'bold'),
                                command=lambda: threading.Thread(target=lambda: reg_user(controller)).start())
            signup_btn.place(x=165, y=140, width=100)

            login_label = Label(signup_frame, text="Already a user? Click here to Login!", fg="blue", cursor="hand2")
            login_label.place(x=115, y=190)
            login_label.bind("<Button-1>", raise_login_frame)

            reset_pwd_label = Label(signup_frame, text="Forgot Password?", fg="blue", cursor="hand2")
            reset_pwd_label.place(x=165, y=220)
            reset_pwd_label.bind("<Button-1>", pwd_reset_frame)

            signup_frame.place(x=85, y=260, height=240, width=430)

        def pwd_reset_frame(event):
            pass_reset_frame = tk.Frame(self)

            Label(pass_reset_frame, text="PASSWORD RESET", fg="#282828", font=('ariel', 10, 'bold')).place(x=150, y=0)

            def call_reset_pwd():
                response = a.reset_password(usernameEntry.get())
                if response is None:
                    controller.status_label.config(text="Password reset email sent successfully!", fg="green")
                else:
                    controller.status_label.config(text="Invalid email, please try again!", fg="#c00000")

            usernameEntry = Entry(pass_reset_frame, textvariable=username)
            usernameEntry.place(x=125, y=70, width=180)
            usernameEntry.delete('0', 'end')
            usernameEntry.insert(0, 'Email Address')
            usernameEntry.bind("<FocusIn>", lambda args: usernameEntry.delete('0', 'end'))

            signup_btn = Button(pass_reset_frame, text="Reset", font=('ariel', 10, 'bold'),
                                command=lambda: threading.Thread(target=lambda: call_reset_pwd()).start())
            signup_btn.place(x=165, y=140, width=100)

            login_label = Label(pass_reset_frame, text="Click here to Login!", fg="blue", cursor="hand2")
            login_label.place(x=160, y=190)
            login_label.bind("<Button-1>", raise_login_frame)

            pass_reset_frame.place(x=85, y=260, height=240, width=430)

        def log_user(controller):
            if (usernameEntry.get() == '') or (passwordEntry.get() == ''):
                controller.status_label.config(text="Error! email/password cannot be empty!", fg="#c00000")
            else:
                login_btn.config(state="disabled")
                controller.status_label.config(text="Please wait, logging you in...", fg="black")
                response = a.login_user(usernameEntry.get(), passwordEntry.get())
                if response:
                    tok = response['idToken']
                    complete_account_info = a.auth.get_account_info(tok)
                    email_verified = complete_account_info['users'][0]['emailVerified']
                    if email_verified:
                        controller.app_login_cred['email'].set(response['email'])
                        controller.app_login_cred['idToken'].set(response['idToken'])
                        controller.status_label.config(text="Logged-in successfully!", fg="green")
                        controller.show_frame_head()
                        controller.show_frame(UserHomepage)
                    else:
                        login_btn.config(state="normal")
                        controller.status_label.config(text="Please verify your email address before logging in!",
                                                       fg="#c00000")
                else:
                    login_btn.config(state="normal")
                    controller.status_label.config(text="Invalid email or password! Please try again!", fg="#c00000")

        login_frame = tk.Frame(self)

        Label(login_frame, text="LOGIN", fg="#282828", font=('ariel', 10, 'bold')).place(x=190, y=0)

        username = StringVar()
        password = StringVar()

        usernameEntry = Entry(login_frame, textvariable=username)
        usernameEntry.place(x=125, y=70, width=180)
        usernameEntry.delete('0', 'end')
        usernameEntry.insert(0, 'Email Address')
        usernameEntry.bind("<FocusIn>", lambda args: usernameEntry.delete('0', 'end'))

        passwordEntry = Entry(login_frame, textvariable=password)
        passwordEntry.place(x=125, y=100, width=180)
        passwordEntry.delete('0', 'end')
        passwordEntry.insert(0, 'Password')
        passwordEntry.bind("<FocusIn>", pass_focus)

        login_btn = Button(login_frame, text="Login", font=('ariel', 10, 'bold'),
                           command=lambda: threading.Thread(target=lambda: log_user(controller)).start())
        login_btn.place(x=165, y=140, width=100)

        signup_label = Label(login_frame, text="New user? Click here to Sign-up!", fg="blue", cursor="hand2")
        signup_label.place(x=125, y=190)
        signup_label.bind("<Button-1>", sign_up_frame)

        reset_pwd_label = Label(login_frame, text="Forgot Password?", fg="blue", cursor="hand2")
        reset_pwd_label.place(x=165, y=220)
        reset_pwd_label.bind("<Button-1>", pwd_reset_frame)

        login_frame.place(x=85, y=260, height=240, width=430)

        # def call_email_verify(self):
        #     a.resend_verification_email()

        # resend_verify_label = Label(self, text="Resend Verification Email", fg="blue", cursor="hand2")
        # resend_verify_label.place(x=310,y=480)
        # resend_verify_label.bind("<Button-1>", call_email_verify)

        Button(self, text="Exit", font=('ariel', 10, 'bold'), fg="white", bg="#c00000",
               command=lambda: controller.distroy_window()).place(
            x=440, y=520, width=110)


class UserHomepage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        Label(self, text="Welcome!", fg="#282828", font=('ariel', 20, 'bold')).place(x=235, y=150)

        Label(self, text="Thank you for downloading FirebaseTkinterApp!", font=('ariel', 13, 'bold'), fg='green').place(x=120,
                                                                                                              y=290)

        Label(self,
              text="Just a headsup, in case you find any bugs, please make sure you report those so that I can fix it, click on Help > Report a Bug. I'm also open for suggestions, you can post your suggestions in the same form! Happy Hacking Comrades!",
              font=('ariel', 10, 'bold'), wraplength=350, justify='center').place(x=120, y=350)

        Button(self, text="About", font=('ariel', 10, 'bold'),
               command=lambda: controller.show_frame(About)).place(x=50, y=520, width=110)
        Button(self, text="Next", font=('ariel', 10, 'bold'),
               command=lambda: controller.show_frame(StartFrame)).place(x=310, y=520, width=110)
        Button(self, text="Exit", font=('ariel', 10, 'bold'), fg="white", bg="#c00000",
               command=lambda: controller.distroy_window()).place(
            x=440, y=520, width=110)


class About(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        def back_method(self, controller):
            if not controller.app_login_cred['idToken'].get() == '':
                controller.show_frame(UserHomepage)
            else:
                controller.show_frame(Disclaimer)

        def callback(self, url):
            webbrowser.open_new(url)

        def on_donate_enter(event):
            donate_link.config(cursor="question_arrow")
            donate_link.config(fg='green', cursor="heart")

        def on_donate_leave(event):
            donate_link.config(fg='blue')

        def on_more_info_enter(event):
            more_info_link.config(cursor="question_arrow")
            more_info_link.config(fg='green', cursor="shuttle")

        def on_more_info_leave(event):
            more_info_link.config(fg='blue')

        Label(self, text="ABOUT", fg="#282828", font=('ariel', 20, 'bold')).place(x=245, y=100)

        Label(self, text=f"FirebaseTkinterApp\nversion_number: v{controller.current_version}", font=('ariel', 12, 'bold'),
              justify="center").place(x=210, y=160)
        Label(self,
              text="FirebaseTkinterApp is an open source tool which is used to generate Windows Exploitation Packages. This tool is capable of generating Windows Executables consisting of a malware. It could be used to study the vulnerabilities, and ultimately help us prevent them.\n\n\nThe application has an unique feature to fetch new available exploits developed by the author (me) from a cloud database and make them available for users (like you) to generate an exploit.\n\n\nIf you like my work, please consider to donate, it will not only encourage me but will keep this project live long.",
              fg="#282828", font=('ariel', 10, 'bold'), wraplength=450).place(x=75, y=230)

        donate_link = Label(self, text='donate', font=('ariel', 8, 'bold'), fg='blue')
        donate_link.place(x=220, y=470)
        donate_link.bind("<Button-1>", lambda e: controller.show_frame(DonatePage))
        donate_link.bind("<Enter>", on_donate_enter)
        donate_link.bind("<Leave>", on_donate_leave)

        more_info_link = Label(self, text='more info', font=('ariel', 8, 'bold'), fg='blue')
        more_info_link.place(x=310, y=470)
        more_info_link.bind("<Button-1>", lambda e: callback(self, "https://thefortyseven.dev/firebase-tkinter-login-signup-app-template"))
        more_info_link.bind("<Enter>", on_more_info_enter)
        more_info_link.bind("<Leave>", on_more_info_leave)

        ## button to show frame 2 with text layout2
        Button(self, text="Back", font=('ariel', 10, 'bold'),
               command=lambda: back_method(self, controller)).place(x=310, y=520, width=110)
        # exit button for checking connection window
        Button(self, text="Exit", font=('ariel', 10, 'bold'), fg="white", bg="#c00000",
               command=lambda: controller.distroy_window()).place(
            x=440, y=520, width=110)


class DonatePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        Label(self, text="DONATE", fg="#282828", font=('ariel', 20, 'bold')).place(x=230, y=100)
        Label(self,
              text="Since you're already here, I Thank You for your support. You're one of those people who encourage me to work harder and keep going in the right direction. Your donation will not only boost me but also help this project live.",
              fg="#282828", font=('ariel', 10, 'bold'), wraplength=450).place(x=75, y=150)

        def btc_master():
            def btc_btc():
                btc_btc_frame = tk.Frame(self)
                btc_btc_img = tk.PhotoImage(file='wallets/btc-btc.png')
                btc_btc_img_label = tk.Label(btc_btc_frame, image=btc_btc_img)
                btc_btc_img_label.place(x=0, y=20)
                btc_btc_img_label.image = btc_btc_img
                btc_btc_id_display = Entry(btc_btc_frame)
                btc_btc_id_display.place(x=0, y=220, width=300)
                btc_btc_id_display.insert(0, "17FhPFfDExrh3JNWhQJgTesE8NGphJH8ci")
                btc_btc_id_display.config(state="readonly")
                Button(btc_btc_frame, text="BTC - BEP20", font=('ariel', 10, 'bold'), command=btc_bep).place(x=250,
                                                                                                             y=30,
                                                                                                             width=150)
                Label(btc_btc_frame, text="BTC\nBTC NETWORK", font=('ariel', 12, 'bold')).place(x=250, y=150, width=150)
                btc_btc_frame.place(x=85, y=270, height=240, width=430)

            def btc_bep():
                btc_bep_frame = tk.Frame(self)
                btc_bep_img = tk.PhotoImage(file='wallets/eth.png')
                btc_bep_img_label = tk.Label(btc_bep_frame, image=btc_bep_img)
                btc_bep_img_label.place(x=0, y=20)
                btc_bep_img_label.image = btc_bep_img
                btc_bep_id_display = Entry(btc_bep_frame)
                btc_bep_id_display.place(x=0, y=220, width=300)
                btc_bep_id_display.insert(0, "0x6e6a5aad65fa35638f5f65dba0fa34d5e13490d0")
                btc_bep_id_display.config(state="readonly")
                Button(btc_bep_frame, text="BTC - BTC NETWORK", font=('ariel', 10, 'bold'), command=btc_btc).place(
                    x=250, y=30, width=150)
                Label(btc_bep_frame, text="BTC\nBEP NETWORK", font=('ariel', 12, 'bold')).place(x=250, y=150, width=150)
                btc_bep_frame.place(x=85, y=270, height=240, width=430)

            btc_btc()

        def eth_erc20():
            eth_erc20_frame = tk.Frame(self)
            eth_erc20_img = tk.PhotoImage(file='wallets/eth.png')
            eth_erc20_img_label = tk.Label(eth_erc20_frame, image=eth_erc20_img)
            eth_erc20_img_label.place(x=0, y=20)
            eth_erc20_img_label.image = eth_erc20_img
            eth_erc20_id_display = Entry(eth_erc20_frame)
            eth_erc20_id_display.place(x=0, y=220, width=300)
            eth_erc20_id_display.insert(0, "0x6e6a5aad65fa35638f5f65dba0fa34d5e13490d0")
            eth_erc20_id_display.config(state="readonly")
            Label(eth_erc20_frame, text="ETH\nERC20 NETWORK", font=('ariel', 12, 'bold')).place(x=250, y=150, width=150)
            eth_erc20_frame.place(x=85, y=270, height=240, width=430)

        def ada_master():
            def ada_ada():
                ada_ada_frame = tk.Frame(self)
                ada_ada_img = tk.PhotoImage(file='wallets/ada-ada.png')
                ada_ada_img_label = tk.Label(ada_ada_frame, image=ada_ada_img)
                ada_ada_img_label.place(x=0, y=20)
                ada_ada_img_label.image = ada_ada_img
                ada_ada_id_display = Entry(ada_ada_frame)
                ada_ada_id_display.place(x=0, y=220, width=300)
                ada_ada_id_display.insert(0,
                                          "DdzFFzCqrhspxEA9ykiLwrC77RKbgdvrLsbbbbrDoJAzNXCLfk6jTgbUnWnEgQdnETxdLV2nyW5srKunRdowhpYL8igCXpPED9JPZitx")
                ada_ada_id_display.config(state="readonly")
                Button(ada_ada_frame, text="ADA - BEP20", font=('ariel', 10, 'bold'), command=ada_bep).place(x=250,
                                                                                                             y=30,
                                                                                                             width=150)
                Label(ada_ada_frame, text="ADA\nADA NETWORK", font=('ariel', 12, 'bold')).place(x=250, y=150, width=150)
                ada_ada_frame.place(x=85, y=270, height=240, width=430)

            def ada_bep():
                ada_bep_frame = tk.Frame(self)
                ada_bep_img = tk.PhotoImage(file='wallets/btc-bep.png')
                ada_bep_img_label = tk.Label(ada_bep_frame, image=ada_bep_img)
                ada_bep_img_label.place(x=0, y=20)
                ada_bep_img_label.image = ada_bep_img
                ada_bep_id_display = Entry(ada_bep_frame)
                ada_bep_id_display.place(x=0, y=220, width=300)
                ada_bep_id_display.insert(0, "0x6e6a5aad65fa35638f5f65dba0fa34d5e13490d0")
                ada_bep_id_display.config(state="readonly")
                Button(ada_bep_frame, text="ADA - ADA NETWORK", font=('ariel', 10, 'bold'), command=ada_ada).place(
                    x=250, y=30, width=150)
                Label(ada_bep_frame, text="ADA\nBEP NETWORK", font=('ariel', 12, 'bold')).place(x=250, y=150, width=150)
                ada_bep_frame.place(x=85, y=270, height=240, width=430)

            ada_ada()

        def usdt_erc20():
            usdt_erc20_frame = tk.Frame(self)
            usdt_erc20_img = tk.PhotoImage(file='wallets/eth.png')
            usdt_erc20_img_label = tk.Label(usdt_erc20_frame, image=usdt_erc20_img)
            usdt_erc20_img_label.place(x=0, y=20)
            usdt_erc20_img_label.image = usdt_erc20_img
            usdt_erc20_id_display = Entry(usdt_erc20_frame)
            usdt_erc20_id_display.place(x=0, y=220, width=300)
            usdt_erc20_id_display.insert(0, "0x6e6a5aad65fa35638f5f65dba0fa34d5e13490d0")
            usdt_erc20_id_display.config(state="readonly")
            Label(usdt_erc20_frame, text="USDT\nERC20 NETWORK", font=('ariel', 12, 'bold')).place(x=250, y=150,
                                                                                                  width=150)
            usdt_erc20_frame.place(x=85, y=270, height=240, width=430)

        Button(self, text="BTC", font=('ariel', 10, 'bold'), command=btc_master).place(x=100, y=240, width=85)
        Button(self, text="ETH", font=('ariel', 10, 'bold'), command=eth_erc20).place(x=205, y=240, width=85)
        Button(self, text="ADA", font=('ariel', 10, 'bold'), command=ada_master).place(x=310, y=240, width=85)
        Button(self, text="USDT", font=('ariel', 10, 'bold'), command=usdt_erc20).place(x=415, y=240, width=85)

        ## button to show frame 2 with text layout2
        Button(self, text="Back", font=('ariel', 10, 'bold'),
               command=lambda: controller.show_frame(About)).place(x=310, y=520, width=110)
        # exit button for checking connection window
        Button(self, text="Exit", font=('ariel', 10, 'bold'), fg="white", bg="#c00000",
               command=lambda: controller.distroy_window()).place(
            x=440, y=520, width=110)


class StartFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        Label(self, text="START FRAME", fg="#282828", font=('ariel', 20, 'bold')).place(x=200, y=150)
        Label(self,
              text="You can now start working on your App from here. Create class frames inherited from the main app and continue. Feel free to add your own App Logo and Name and all the redirects to your website if available. Also, make sure you add your own wallet addresses from the donate page. Hope this project helps you in kickstarting your app.",
              fg="#282828", font=('ariel', 10, 'bold'), wraplength=450).place(x=85, y=250)


        # exit button for checking connection window
        Button(self, text="Exit", font=('ariel', 10, 'bold'), fg="white", bg="#c00000",
               command=lambda: controller.distroy_window()).place(
            x=440, y=520, width=110)


if __name__ == "__main__":
    app = FirebaseTkinterApp()
    app.mainloop()
