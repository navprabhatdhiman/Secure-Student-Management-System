import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import datetime


def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def encrypt(text):
    return "".join(chr(ord(c)^7) for c in text)

def decrypt(text):
    return "".join(chr(ord(c)^7) for c in text)


conn = sqlite3.connect(".sms_secure.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
username TEXT PRIMARY KEY,
password TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS students(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
age TEXT,
course TEXT
)
""")

cur.execute("INSERT OR IGNORE INTO users VALUES(?,?)",
('admin', hash_password('1234')))

conn.commit()

attempts = 0


def login_screen():

    global login_win,user_var,pass_var

    login_win = tk.Tk()
    login_win.title("Secure Student Management System")
    login_win.geometry("400x300")

    frame = ttk.Frame(login_win,padding=20)
    frame.pack(expand=True)

    ttk.Label(frame,text="Secure Student Management System",
    font=("Arial",18,"bold")).pack(pady=10)

    user_var=tk.StringVar()
    pass_var=tk.StringVar()

    ttk.Label(frame,text="Username").pack(anchor="w")
    ttk.Entry(frame,textvariable=user_var,width=30).pack(pady=5)

    ttk.Label(frame,text="Password").pack(anchor="w")
    ttk.Entry(frame,textvariable=pass_var,show="*",width=30).pack(pady=5)

    ttk.Button(frame,text="Login",command=login).pack(pady=20)

    login_win.mainloop()


def login():

    global attempts

    u=user_var.get()
    p=pass_var.get()

    if u=="" or p=="":
        messagebox.showwarning("Warning","Fill all fields")
        return

    cur.execute("SELECT * FROM users WHERE username=? AND password=?",
    (u,hash_password(p)))

    if cur.fetchone():

        messagebox.showinfo("Success",
        f"Login Successful\nTime: {datetime.datetime.now()}")

        login_win.destroy()
        main_window()

    else:

        attempts+=1
        messagebox.showerror("Error","Invalid Login")

        if attempts>=3:
            messagebox.showerror("Blocked","Too many attempts")
            login_win.destroy()


def main_window():

    root=tk.Tk()
    root.title("Secure Student Management System")

    root.attributes("-fullscreen",True)
    root.bind("<Escape>",lambda e: root.attributes("-fullscreen",False))

    def logout():

        confirm=messagebox.askyesno("Logout","Logout now?")

        if confirm:
            root.destroy()
            login_screen()


    top=ttk.Frame(root)
    top.pack(fill="x")

    ttk.Label(top,
    text="Secure Student Management System",
    font=("Arial",20,"bold")).pack(side="left",padx=20,pady=10)

    tk.Button(top,
    text="Logout",
    bg="red",
    fg="white",
    command=logout).pack(side="right",padx=20)


    dash=ttk.Frame(root)
    dash.pack(pady=10)

    total_label=tk.Label(dash,
    text="Total Students : 0",
    font=("Arial",12,"bold"),
    fg="blue")

    total_label.pack()


    form=ttk.LabelFrame(root,text="Student Details",padding=20)
    form.pack(padx=20,pady=10,fill="x")

    name_var=tk.StringVar()
    age_var=tk.StringVar()
    course_var=tk.StringVar()
    search_var=tk.StringVar()

    ttk.Label(form,text="Name").grid(row=0,column=0,padx=10,pady=5)
    ttk.Entry(form,textvariable=name_var,width=25).grid(row=0,column=1)

    ttk.Label(form,text="Age").grid(row=0,column=2)
    ttk.Entry(form,textvariable=age_var,width=10).grid(row=0,column=3)

    ttk.Label(form,text="Course").grid(row=1,column=0)
    ttk.Entry(form,textvariable=course_var,width=25).grid(row=1,column=1)

    ttk.Label(form,text="Search Name").grid(row=1,column=2)
    ttk.Entry(form,textvariable=search_var,width=20).grid(row=1,column=3)


    def clear():
        name_var.set("")
        age_var.set("")
        course_var.set("")

    def update_dashboard():

        cur.execute("SELECT COUNT(*) FROM students")
        count=cur.fetchone()[0]

        total_label.config(text=f"Total Students : {count}")

    def add_student():

        if name_var.get()=="" or age_var.get()=="" or course_var.get()=="":
            messagebox.showwarning("Warning","Fill all fields")
            return

        cur.execute("INSERT INTO students(name,age,course) VALUES(?,?,?)",
        (encrypt(name_var.get()),
        encrypt(age_var.get()),
        encrypt(course_var.get())))

        conn.commit()

        show_students()
        update_dashboard()
        clear()

    def show_students():

        tree.delete(*tree.get_children())

        cur.execute("SELECT * FROM students")

        i=1

        for row in cur.fetchall():

            tree.insert("", "end",
            values=(i,
            row[0],
            decrypt(row[1]),
            decrypt(row[2]),
            decrypt(row[3])))

            i+=1

    def search_student():

        keyword=search_var.get().lower()

        tree.delete(*tree.get_children())

        cur.execute("SELECT * FROM students")

        i=1

        for row in cur.fetchall():

            name=decrypt(row[1])

            if keyword in name.lower():

                tree.insert("", "end",
                values=(i,
                row[0],
                name,
                decrypt(row[2]),
                decrypt(row[3])))

                i+=1

    def delete_student():

        selected=tree.selection()

        if not selected:
            messagebox.showwarning("Select","Select student")
            return

        item=tree.item(selected)

        cur.execute("DELETE FROM students WHERE id=?",
        (item['values'][1],))

        conn.commit()

        show_students()
        update_dashboard()

    def update_student():

        selected=tree.selection()

        if not selected:
            messagebox.showwarning("Select","Select student")
            return

        item=tree.item(selected)

        sid=item['values'][1]

        cur.execute("""UPDATE students
        SET name=?,age=?,course=?
        WHERE id=?""",
        (encrypt(name_var.get()),
        encrypt(age_var.get()),
        encrypt(course_var.get()),
        sid))

        conn.commit()

        show_students()
        clear()

    def select_student(event):

        selected=tree.selection()

        if selected:

            item=tree.item(selected)

            name_var.set(item['values'][2])
            age_var.set(item['values'][3])
            course_var.set(item['values'][4])


    btn=ttk.Frame(root)
    btn.pack(pady=10)

    ttk.Button(btn,text="Add",command=add_student).grid(row=0,column=0,padx=10)
    ttk.Button(btn,text="Update",command=update_student).grid(row=0,column=1,padx=10)
    ttk.Button(btn,text="Delete",command=delete_student).grid(row=0,column=2,padx=10)
    ttk.Button(btn,text="Show All",command=show_students).grid(row=0,column=3,padx=10)
    ttk.Button(btn,text="Search",command=search_student).grid(row=0,column=4,padx=10)


    table_frame=ttk.Frame(root)
    table_frame.pack(fill="both",expand=True,padx=20,pady=20)

    tree=ttk.Treeview(table_frame,
    columns=("SNo","ID","Name","Age","Course"),
    show="headings")

    tree.heading("SNo",text="S.No")
    tree.heading("ID",text="ID")
    tree.heading("Name",text="Name")
    tree.heading("Age",text="Age")
    tree.heading("Course",text="Course")

    tree.column("SNo",width=80,anchor="center")
    tree.column("ID",width=100,anchor="center")
    tree.column("Name",width=250,anchor="center")
    tree.column("Age",width=120,anchor="center")
    tree.column("Course",width=250,anchor="center")

    scrollbar=ttk.Scrollbar(table_frame,orient="vertical",command=tree.yview)
    tree.configure(yscroll=scrollbar.set)

    scrollbar.pack(side="right",fill="y")
    tree.pack(fill="both",expand=True)

    tree.bind("<<TreeviewSelect>>",select_student)

    show_students()
    update_dashboard()

    root.mainloop()


login_screen()
