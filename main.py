import tkinter as tk
from tkinter import messagebox, scrolledtext
import sqlite3
from fpdf import FPDF
import hashlib

# ---------- DATABASE SETUP ----------
conn = sqlite3.connect("issues.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS issues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        category TEXT,
        issue TEXT NOT NULL,
        solution TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
conn.commit()

# GUI setup
root = tk.Tk()
root.title("Issue Solution Tracker")
root.geometry("600x700")

user_id = None

def register_user():
    username = username_entry.get()
    password = password_entry.get()
    if username and password:
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
            conn.commit()
            messagebox.showinfo("Success", "User registered successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
    else:
        messagebox.showwarning("Input Error", "Please enter username and password.")

def login_user():
    global user_id
    username = username_entry.get()
    password = password_entry.get()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, hashed_pw))
    result = cursor.fetchone()
    if result:
        user_id = result[0]
        auth_frame.pack_forget()
        main_frame.pack()
        load_issues()
    else:
        messagebox.showerror("Login Failed", "Invalid credentials.")

def save_issue():
    category = category_entry.get()
    issue_text = issue_entry.get()
    solution_text = solution_textbox.get("1.0", tk.END)
    if issue_text and solution_text.strip():
        cursor.execute("INSERT INTO issues (user_id, category, issue, solution) VALUES (?, ?, ?, ?)", (user_id, category, issue_text, solution_text))
        conn.commit()
        messagebox.showinfo("Success", "Issue and solution saved successfully!")
        clear_fields()
        load_issues()
    else:
        messagebox.showwarning("Input Error", "Please provide category, issue and solution.")

def clear_fields():
    category_entry.delete(0, tk.END)
    issue_entry.delete(0, tk.END)
    solution_textbox.delete("1.0", tk.END)

def search_issue():
    keyword = search_entry.get()
    if not keyword:
        messagebox.showwarning("Input Error", "Please enter a keyword to search.")
        return
    cursor.execute("SELECT category, issue, solution FROM issues WHERE user_id=? AND issue LIKE ?", (user_id, f"%{keyword}%"))
    results = cursor.fetchall()
    result_textbox.delete("1.0", tk.END)
    for res in results:
        result_textbox.insert(tk.END, f"Category: {res[0]}\nIssue: {res[1]}\nSolution: {res[2]}\n{'-'*40}\n")

def load_issues():
    issue_listbox.delete(0, tk.END)
    cursor.execute("SELECT id, category, issue FROM issues WHERE user_id=?", (user_id,))
    for row in cursor.fetchall():
        issue_listbox.insert(tk.END, f"{row[0]} | {row[1]} | {row[2]}")

# Frames
auth_frame = tk.Frame(root)
auth_frame.pack()
tk.Label(auth_frame, text="Username").pack()
username_entry = tk.Entry(auth_frame)
username_entry.pack()
tk.Label(auth_frame, text="Password").pack()
password_entry = tk.Entry(auth_frame, show="*")
password_entry.pack()
tk.Button(auth_frame, text="Register", command=register_user).pack()
tk.Button(auth_frame, text="Login", command=login_user).pack()

main_frame = tk.Frame(root)

tk.Label(main_frame, text="Category").pack()
category_entry = tk.Entry(main_frame)
category_entry.pack()
tk.Label(main_frame, text="Issue").pack()
issue_entry = tk.Entry(main_frame)
issue_entry.pack()
tk.Label(main_frame, text="Solution").pack()
solution_textbox = scrolledtext.ScrolledText(main_frame, width=70, height=10)
solution_textbox.pack()
tk.Button(main_frame, text="Save Issue", command=save_issue).pack()

tk.Label(main_frame, text="Search Issue").pack()
search_entry = tk.Entry(main_frame)
search_entry.pack()
tk.Button(main_frame, text="Search", command=search_issue).pack()
result_textbox = scrolledtext.ScrolledText(main_frame, width=70, height=10)
result_textbox.pack()

tk.Label(main_frame, text="All Issues").pack()
issue_listbox = tk.Listbox(main_frame, width=70)
issue_listbox.pack()

root.mainloop()