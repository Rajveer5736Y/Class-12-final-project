import os 
import mysql.connector 
import tkinter as tk 
from tkinter import messagebox, ttk, simpledialog 
import smtplib 
from email.mime.text import MIMEText 
import random 
 
 
# ------------------ CONFIG ------------------ 
DB_CONFIG = { 
    'host': 'localhost', 
    'user': 'root', 
    'password': '', 
    'database': 'food_ordering' 
} 
 
 
EMAIL_CONFIG = { 
    'sender': 'foodorderingsystem406@gmail.com',      # CHANGE THIS 
    'password': 'rhts fqsv wpms wsku'                 # CHANGE THIS (Gmail App Password) 
} 
 
 
current_user = None 
current_is_admin = False 
cart = [] 
order_summary = ""  # FIXED: Global variable 
 
 
# ------------------ DATABASE ------------------ 
def get_db_connection(): 
    try: 
        return mysql.connector.connect(**DB_CONFIG) 
    except: 
        return None 
 
 
BG = "#f8f9fa" 
PRIMARY = "#e74c3c" 
CARD = "#ffffff" 
FONT_TITLE = ("Segoe UI", 40, "bold") 
FONT_HEAD = ("Segoe UI", 28, "bold") 
FONT_TEXT = ("Segoe UI", 22) 
 
 
def init_db(): 
    conn = get_db_connection() 
    if not conn: return 
    cursor = conn.cursor() 
     
    cursor.execute("CREATE DATABASE IF NOT EXISTS food_ordering") 
    cursor.execute("USE food_ordering") 
     
    # Tables (unchanged) 
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS users ( 
        id INT AUTO_INCREMENT PRIMARY KEY, 
        username VARCHAR(100) UNIQUE NOT NULL, 
        password VARCHAR(255) NOT NULL, 
        email VARCHAR(255) NOT NULL 
    ) 
    """) 
     
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS admin ( 
        id INT AUTO_INCREMENT PRIMARY KEY, 
        username VARCHAR(100) UNIQUE NOT NULL, 
        password VARCHAR(255) NOT NULL 
    ) 
    """) 
     
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS menu ( 
        id INT AUTO_INCREMENT PRIMARY KEY, 
        item_name VARCHAR(255) NOT NULL, 
        price DECIMAL(10,2) NOT NULL 
    ) 
    """) 
     
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS orders ( 
        id INT AUTO_INCREMENT PRIMARY KEY, 
        customer_name VARCHAR(100), 
        item_name VARCHAR(255), 
        item_quantity INT, 
        total_price DECIMAL(10,2), 
        order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
    ) 
    """) 
 
    # Default admin 
    cursor.execute("SELECT COUNT(*) FROM admin") 
    if cursor.fetchone()[0] == 0: 
        cursor.execute("INSERT INTO admin (username,password) VALUES (%s,%s)", 
("admin","admin123")) 
     
    # 
✨
 BEAUTIFUL: Add sample menu items 
    cursor.execute("SELECT COUNT(*) FROM menu") 
    if cursor.fetchone()[0] == 0: 
        sample_menu = [ 
            ("
🍔
 Classic Burger", 150.00), 
            ("
🍕
 Margherita Pizza", 250.00), 
            ("
🍗
 Chicken Biryani", 200.00), 
            ("
🥗
 Caesar Salad", 120.00), 
            ("
🍝
 Pasta Alfredo", 180.00), 
            ("
🥙
 Chicken Wrap", 160.00), 
            ("
🍦
 Chocolate Cake", 90.00), 
            ("
☕
 Cappuccino", 80.00) 
        ] 
        cursor.executemany("INSERT INTO menu (item_name, price) VALUES (%s, %s)", 
sample_menu) 
        print("
✅
 Added 8 delicious menu items!") 
     
    conn.commit() 
    cursor.close() 
    conn.close() 
 
 
# ------------------ EMAIL (unchanged) ------------------ 
def send_otp(email, otp): 
    print(otp) 
    msg = MIMEText(f"Your OTP for Food Ordering App signup is: {otp}") 
    msg['Subject'] = 'OTP Verification' 
    msg['From'] = EMAIL_CONFIG['sender'] 
    msg['To'] = email 
    try: 
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server: 
            server.login(EMAIL_CONFIG['sender'], EMAIL_CONFIG['password']) 
            server.send_message(msg) 
    except Exception as e: 
        messagebox.showerror("Email Error", str(e)) 
 
 
def send_cancel_order_email(user_email, order_details): 
    html_body = f""" 
    <html> 
      <body> 
        <h3>Your order has been Canceled successfully! 
�
�
</h3> 
        <p><b>Order Details:</b></p> 
        <pre>{order_details}</pre> 
        <br> 
        <p> 
         
�
�
 <a 
href="mailto:{EMAIL_CONFIG['sender']}?subject=Food%20Order%20Feedback"> 
            Send Feedback 
         </a> 
        </p> 
        <br> 
        <p>Thank you for Ordering with us!</p> 
      </body> 
    </html> 
    """ 
    msg = MIMEText(html_body, "html") 
    msg['Subject'] = 'Food Order Cancel Confirmation' 
    msg['From'] = EMAIL_CONFIG['sender'] 
    msg['To'] = user_email 
    try: 
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server: 
            server.login(EMAIL_CONFIG['sender'], EMAIL_CONFIG['password']) 
            server.send_message(msg) 
    except Exception as e: 
        messagebox.showwarning("Email Warning", f"Order placed but failed to send 
email.\n{str(e)}") 
 
 
def send_order_email(user_email, order_details): 
    html_body = f""" 
    <html> 
      <body> 
        <h3>Your order has been placed successfully! 
�
�
</h3> 
        <p><b>Order Details:</b></p> 
        <pre>{order_details}</pre> 
        <br> 
        <p> 
         
�
�
 <a 
href="mailto:{EMAIL_CONFIG['sender']}?subject=Food%20Order%20Feedback"> 
            Send Feedback 
         </a> 
        </p> 
        <br> 
        <p>Thank you for ordering with us!</p> 
      </body> 
    </html> 
    """ 
    msg = MIMEText(html_body, "html") 
    msg['Subject'] = 'Food Order Confirmation' 
    msg['From'] = EMAIL_CONFIG['sender'] 
    msg['To'] = user_email 
    try: 
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server: 
            server.login(EMAIL_CONFIG['sender'], EMAIL_CONFIG['password']) 
            server.send_message(msg) 
    except Exception as e: 
        messagebox.showwarning("Email Warning", f"Order placed but failed to send 
email.\n{str(e)}") 
 
 
def create_scrollable_frame(parent): 
    canvas = tk.Canvas(parent, bg="#fffaf0", highlightthickness=0) 
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview) 
 
    scroll_frame = tk.Frame(canvas, bg="#fffaf0") 
 
    # Create window INSIDE canvas 
    canvas_window = canvas.create_window( 
        (0, 0), 
        window=scroll_frame, 
        anchor="nw" 
    ) 
 
    # Update scroll region when content changes 
    scroll_frame.bind( 
        "<Configure>", 
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")) 
    ) 
 
    # 
�
�
 THIS IS THE KEY LINE 
    # Make scroll_frame width = canvas width 
    canvas.bind( 
        "<Configure>", 
        lambda e: canvas.itemconfig(canvas_window, width=e.width) 
    ) 
 
    canvas.configure(yscrollcommand=scrollbar.set) 
 
    canvas.pack(side="left", fill="both", expand=True) 
    scrollbar.pack(side="right", fill="y") 
 
    return scroll_frame 
 
 
# ------------------ GUI ------------------ 
root = tk.Tk() 
root.title("
🍕
 Food Ordering System") 
root.geometry("1200x800") 
root.configure(bg="#f8f9fa") 
root.resizable(True, True) 
 
main_frame = tk.Frame(root, bg="#f8f9fa") 
main_frame.pack(fill="both", expand=True, padx=40, pady=40) 
 
LARGE_FONT = ("Segoe UI", 36, "bold") 
MED_FONT = ("Segoe UI", 24, "bold") 
SMALL_FONT = ("Segoe UI", 18) 
 
 
# ---------- Utility ---------- 
def clear_frame(): 
    for widget in main_frame.winfo_children(): 
        widget.destroy() 
 
 
def show_message(title, text): 
    top = tk.Toplevel() 
    top.title(title) 
    top.geometry("400x200") 
    top.configure(bg="#fffacd") 
    top.resizable(False, False) 
    tk.Label(top, text=text, font=("Segoe UI", 20), bg="#fffacd", fg="#2c3e50").pack(padx=30, 
pady=30) 
    tk.Button(top, text="✕ OK", font=("Segoe UI", 16, "bold"), bg="#e74c3c", fg="white", 
              bd=0, relief="flat", width=10, height=2, command=top.destroy).pack(pady=10) 
    top.grab_set() 
 
 
# ---------- Start Page ---------- 
def start_page(): 
    clear_frame() 
     
    # Beautiful header 
    header = tk.Frame(main_frame, bg="#2c3e50", relief="raised", bd=0, height=120) 
    header.pack(fill="x", pady=(0, 40)) 
    header.pack_propagate(False) 
     
    tk.Label(header, text="
🍕
 FOOD ORDERING SYSTEM", font=LARGE_FONT, 
            bg="#2c3e50", fg="white").pack(pady=30) 
     
    # Modern buttons 
    login_btn = tk.Button(main_frame, text="
🔐
 LOGIN", width=28, height=3, 
font=MED_FONT, 
                         bg="#3498db", fg="white", bd=0, relief="flat", 
                         activebackground="#2980b9", cursor="hand2", command=login_page) 
    login_btn.pack(pady=15) 
     
    signup_btn = tk.Button(main_frame, text="
📝
 SIGNUP", width=28, height=3, 
font=MED_FONT, 
                          bg="#e74c3c", fg="white", bd=0, relief="flat", 
                          activebackground="#c0392b", cursor="hand2", command=signup_page) 
    signup_btn.pack(pady=10) 
 
 
# ---------- Signup Page ---------- 
def signup_page(): 
    clear_frame() 
    tk.Label(main_frame, text="
📝
 SIGNUP", font=LARGE_FONT, bg="#f8f9fa", 
fg="#2c3e50").pack(pady=40) 
     
    # Beautiful form card 
    form_card = tk.Frame(main_frame, bg="white", relief="raised", bd=3, padx=60, pady=40) 
    form_card.pack(pady=30) 
     
    tk.Label(form_card, text="
👤
 Username", font=MED_FONT, bg="white", 
fg="#2c3e50").grid(row=0, column=0, pady=20, sticky="e") 
    username_entry = tk.Entry(form_card, font=SMALL_FONT, relief="solid", bd=2, width=25, 
bg="#f8f9fa") 
    username_entry.grid(row=0, column=1, padx=20, pady=20) 
     
    tk.Label(form_card, text="
📧
 Email", font=MED_FONT, bg="white", 
fg="#2c3e50").grid(row=1, column=0, pady=20, sticky="e") 
    email_entry = tk.Entry(form_card, font=SMALL_FONT, relief="solid", bd=2, width=25, 
bg="#f8f9fa") 
    email_entry.grid(row=1, column=1, padx=20, pady=20) 
     
    tk.Label(form_card, text="
🔒
 Password", font=MED_FONT, bg="white", 
fg="#2c3e50").grid(row=2, column=0, pady=20, sticky="e") 
    password_entry = tk.Entry(form_card, show="*", font=SMALL_FONT, relief="solid", bd=2, 
width=25, bg="#f8f9fa") 
    password_entry.grid(row=2, column=1, padx=20, pady=20) 
 
    def create_account(): 
        username = username_entry.get().strip() 
        email = email_entry.get().strip() 
        password = password_entry.get().strip() 
        if not username or not email or not password: 
            show_message("Error", "All fields required") 
            return 
        otp = random.randint(100000, 999999) 
        send_otp(email, otp) 
        user_otp = simpledialog.askstring("OTP Verification", f"OTP sent to {email}\nEnter 
OTP") 
        if not user_otp or int(user_otp) != otp: 
            show_message("Error", "Invalid OTP") 
            return 
        conn = get_db_connection() 
        cursor = conn.cursor() 
        try: 
            cursor.execute("INSERT INTO users (username, password, email) VALUES 
(%s,%s,%s)", (username, password, email)) 
            conn.commit() 
            show_message("Success", "Account created successfully!") 
            login_page() 
        except mysql.connector.IntegrityError: 
            show_message("Error", "Username already exists") 
        finally: 
            cursor.close() 
            conn.close() 
 
    btn_frame = tk.Frame(main_frame, bg="#f8f9fa") 
    btn_frame.pack(pady=20, fill="x") 
 
    tk.Button( 
    btn_frame, 
    text="
✅
 CREATE ACCOUNT", 
    font=MED_FONT, 
    bg="#27ae60", 
    fg="white", 
    bd=0, 
    relief="flat", 
    width=22, 
    height=3, 
    command=create_account 
).pack(side="left", padx=40) 
 
    tk.Button(btn_frame, 
    text="
🔙
 BACK", 
    font=MED_FONT, 
    bg="#95a5a6", 
    fg="white", 
    bd=0, 
    relief="flat", 
    width=15, 
    height=3, 
    command=start_page 
).pack(side="right", padx=40) 
 
 
# ---------- Login Page ---------- 
def login_page(): 
    clear_frame() 
    tk.Label(main_frame, text="
🔐
 LOGIN", font=LARGE_FONT, bg="#f8f9fa", 
fg="#2c3e50").pack(pady=40) 
     
    form_card = tk.Frame(main_frame, bg="white", relief="raised", bd=3, padx=60, pady=40) 
    form_card.pack(pady=30) 
     
    tk.Label(form_card, text="
👤
 Username", font=MED_FONT, bg="white", 
fg="#2c3e50").grid(row=0, column=0, pady=20, sticky="e") 
    username_entry = tk.Entry(form_card, font=SMALL_FONT, relief="solid", bd=2, width=25, 
bg="#f8f9fa") 
    username_entry.grid(row=0, column=1, padx=20, pady=20) 
     
    tk.Label(form_card, text="
🔒
 Password", font=MED_FONT, bg="white", 
fg="#2c3e50").grid(row=1, column=0, pady=20, sticky="e") 
    password_entry = tk.Entry(form_card, show="*", font=SMALL_FONT, relief="solid", bd=2, 
width=25, bg="#f8f9fa") 
    password_entry.grid(row=1, column=1, padx=20, pady=20) 
 
    def login(): 
        global current_user, current_is_admin 
        u = username_entry.get().strip() 
        p = password_entry.get().strip() 
        conn = get_db_connection() 
        if not conn: return 
        cursor = conn.cursor(dictionary=True) 
        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", 
(u,p)) 
        if cursor.fetchone(): 
            current_user = u 
            current_is_admin = True 
            cursor.close() 
            conn.close() 
            admin_dashboard() 
            return 
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", 
(u,p)) 
        row = cursor.fetchone() 
        if row: 
            current_user = u 
            current_is_admin = False 
            user_email = row['email'] 
            cursor.close() 
            conn.close() 
            user_dashboard(user_email) 
        else: 
            show_message("Error", "Invalid credentials\n
💡
 Try: admin / admin123") 
        cursor.close() 
        conn.close() 
 
    # Button container (fixes hidden Back button) 
    btn_frame = tk.Frame(main_frame, bg="#f8f9fa") 
    btn_frame.pack(pady=20, fill="x") 
 
    tk.Button( 
    btn_frame, 
    text="
🚀
 LOGIN", 
    font=MED_FONT, 
    bg="#3498db", 
    fg="white", 
    bd=0, 
    relief="flat", 
    width=20, 
    height=3, 
    command=login 
).pack(side="left", padx=40) 
 
    tk.Button( 
    btn_frame, 
    text="
🔙
 BACK", 
    font=MED_FONT, 
    bg="#95a5a6", 
    fg="white", 
    bd=0, 
    relief="flat", 
    width=15, 
    height=3, 
    command=start_page 
).pack(side="right", padx=40) 
 
 
# ---------- User Dashboard (MENU CARDS) ---------- 
def user_dashboard(user_email): 
    clear_frame() 
     
    # Beautiful header 
    header = tk.Frame(main_frame, bg="#27ae60", relief="raised", bd=0, height=100) 
    header.pack(fill="x", pady=(0, 30)) 
    header.pack_propagate(False) 
     
    tk.Label(header, text="
🍽
  RESTAURANT MENU", font=LARGE_FONT, 
            bg="#27ae60", fg="white").pack(pady=25) 
 
    # Search bar 
    search_frame = tk.Frame(main_frame, bg="white", relief="solid", bd=2) 
    search_frame.pack(fill="x", pady=(0, 25)) 
    tk.Label(search_frame, text="
🔍
 Search Food Items:", font=MED_FONT, bg="white", 
fg="#2c3e50").pack(side="left", padx=25, pady=18) 
    search_entry = tk.Entry(search_frame, font=SMALL_FONT, relief="solid", bd=2, width=35, 
bg="#f8f9fa") 
    search_entry.pack(side="left", padx=15, pady=18) 
 
    menu_container = tk.Frame(main_frame, bg="#fffaf0", relief="raised", bd=3) 
    menu_container.pack(fill="both", expand=True, pady=20) 
 
    menu_frame = create_scrollable_frame(menu_container) 
 
    def refresh_menu(search_text=""): 
        for widget in menu_frame.winfo_children(): 
            widget.destroy() 
        conn = get_db_connection() 
        if not conn: 
            tk.Label(menu_frame, text="
❌
 Database Error", font=MED_FONT, 
bg="#fffaf0").pack(pady=50) 
            return 
        cursor = conn.cursor() 
        if search_text: 
            cursor.execute("SELECT * FROM menu WHERE item_name LIKE %s", 
('%'+search_text+'%',)) 
        else: 
            cursor.execute("SELECT * FROM menu") 
        items = cursor.fetchall() 
        cursor.close() 
        conn.close() 
         
        if not items: 
            tk.Label(menu_frame, text="
🥺
 No food items available\nAsk admin to add some 
delicious food!",  
                    font=("Segoe UI", 22, "bold"), bg="#fffaf0", fg="#7f8c8d").pack(pady=80) 
            return 
         
        # 
✨
 BEAUTIFUL FULL WIDTH MENU CARDS 
        colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#f9ca24", "#f0932b", "#eb4d4b", "#6c5ce7", 
"#a29bfe"] 
        for idx, i in enumerate(items): 
            # BIG FULL WIDTH CARD 
            card = tk.Frame(menu_frame, bg=colors[idx%len(colors)], relief="raised", bd=5, 
height=140) 
            card.pack(fill="x", padx=25, pady=20) 
            card.pack_propagate(False) 
             
            # Food name (BIG FONT) 
            name_label = tk.Label(card, text=i[1], font=("Segoe UI", 28, "bold"),  
                                 bg=colors[idx%len(colors)], fg="white", anchor="w") 
            name_label.pack(side="left", padx=35, pady=25, fill="x", expand=True) 
             
            # Price (GOLDEN) 
            price_label = tk.Label(card, text=f"₹{i[2]:.0f}", font=("Segoe UI", 32, "bold"),  
                                  bg=colors[idx%len(colors)], fg="#f1c40f", padx=35) 
            price_label.pack(side="right", pady=25) 
             
            # Quantity selector 
            qty_frame = tk.Frame(card, bg=colors[idx%len(colors)], width=180) 
            qty_frame.pack(side="right", padx=30) 
            qty_frame.pack_propagate(False) 
             
            tk.Label(qty_frame, text="Qty:", font=("Segoe UI", 20, "bold"),  
                    bg=colors[idx%len(colors)], fg="white").pack(side="left", pady=20) 
            qty_entry = tk.Entry(qty_frame, width=6, font=("Segoe UI", 20, "bold"), 
justify="center", bg="white") 
            qty_entry.insert(0,"1") 
            qty_entry.pack(side="left", padx=(15,0), pady=20) 
             
            def add_to_cart_closure(item=i, entry=qty_entry): 
                try: 
                    qty = int(entry.get()) 
                    if qty<=0: 
                        show_message("Error","Quantity must be >0") 
                        return 
                    cart.append((item, qty)) 
                    show_message("
✅
 Added to Cart!", f"{item[1]}\n×{qty} = ₹{item[2]*qty:.0f}") 
                except: 
                    show_message("Error","Invalid quantity") 
 
            # Beautiful Add button 
            add_btn = tk.Button(card, text="
➕
 ADD TO CART", font=("Segoe UI", 16, "bold"),  
                               bg="#27ae60", fg="white", bd=0, relief="flat", 
                               padx=35, pady=15, cursor="hand2", command=add_to_cart_closure) 
            add_btn.pack(side="right", padx=40, pady=25) 
 
    refresh_menu() 
    search_entry.bind("<KeyRelease>", lambda e: refresh_menu(search_entry.get().strip())) 
 
    # Action buttons 
    btn_frame = tk.Frame(main_frame, bg="#f8f9fa") 
    btn_frame.pack(pady=30, fill="x") 
     
    tk.Button(btn_frame, text="
🛒
 VIEW CART / ORDER", font=MED_FONT, bg="#f39c12", 
fg="white", 
              bd=0, relief="flat", width=22, height=3, command=lambda: 
view_cart(user_email)).pack(side="left", padx=20) 
    tk.Button(btn_frame, text="
📋
 VIEW ORDERS", font=MED_FONT, bg="#3498db", 
fg="white", 
              bd=0, relief="flat", width=22, height=3, command=lambda: 
view_orders(user_email)).pack(side="left", padx=20) 
    tk.Button(btn_frame, text="
🚪
 LOGOUT", font=MED_FONT, bg="#e74c3c", fg="white", 
              bd=0, relief="flat", width=18, height=3, command=start_page).pack(side="right", 
padx=20) 
 
 
# ---------- View Cart ---------- 
# ONLY REPLACE the view_cart function in YOUR ORIGINAL CODE: 
 
def view_cart(user_email): 
    if not cart: 
        show_message("
🛒
 Cart Empty","Your cart is empty\nAdd some delicious items first!") 
        return 
     
    cart_window = tk.Toplevel() 
    cart_window.title("
🛒
 Shopping Cart") 
    cart_window.geometry("950x750") 
    cart_window.configure(bg="#fffacd") 
    cart_window.resizable(False, False) 
     
    tk.Label(cart_window, text="
🛒
 YOUR SHOPPING CART", font=("Segoe UI", 34, "bold"),  
            bg="#fffacd", fg="#e74c3c").pack(pady=30) 
 
    # 
✅
 FIXED: Scrollable cart with FIXED height 
    cart_container = tk.Frame(cart_window, bg="#fffacd") 
    cart_container.pack(fill="both", expand=True, padx=30, pady=(0,30)) 
     
    canvas = tk.Canvas(cart_container, bg="#fffacd", height=300, highlightthickness=0) 
    scrollbar = tk.Scrollbar(cart_container, orient="vertical", command=canvas.yview) 
    cart_scroll = tk.Frame(canvas, bg="#fffacd") 
 
    cart_scroll.bind("<Configure>", lambda e: 
canvas.configure(scrollregion=canvas.bbox("all"))) 
    canvas.create 
