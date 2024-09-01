import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import sqlite3
import uuid
from datetime import datetime

conn = sqlite3.connect('FragranceShop.db')
cursor = conn.cursor()



def show_frame(frame):
    frame.tkraise()


def submit_customer():
    name = customer_name_entry.get()
    mobile = customer_mobile_entry.get()
    age = customer_age_entry.get()
    customer_id = str(uuid.uuid4())

    cursor.execute("INSERT INTO Customers (CustomerID, CustomerName, MobileNumber, Age) VALUES (?, ?, ?, ?)", (customer_id, name, mobile, age))
    conn.commit()

    names.append(name)
    customer_name["values"] = names

    # Clear the fields after submission
    customer_name_entry.delete(0, tk.END)
    customer_mobile_entry.delete(0, tk.END)
    customer_age_entry.delete(0, tk.END)


    tk.messagebox.showinfo("Success","Customer Added Successfully!")
    show_frame(main_page)


def get_fragrances():
    cursor.execute("SELECT FragranceName FROM Fragrances")
    fragrances = cursor.fetchall()
    return sorted([fragrance[0] for fragrance in fragrances])


def get_names():
    cursor.execute("SELECT CustomerName FROM Customers")
    names = cursor.fetchall()
    return sorted([name[0] for name in names])


def update_combobox(event, combobox, values):
    typed = combobox.get()
    if typed == '':
        combobox['values'] = values
    else:
        combobox['values'] = [item for item in values if item.lower().startswith(typed.lower())]


def submit_purchase():

    selected_customer_name = customer_name.get()
    selected_fragrance = fragrance_choice.get()

    if not selected_customer_name or not selected_fragrance:
        tk.messagebox.showerror("Error","Please select both customer and fragrance.")
        return


    # Get customer ID and fragrance ID from the database
    cursor.execute("SELECT CustomerID FROM Customers WHERE CustomerName = ?",(selected_customer_name,))
    customer_id_result = cursor.fetchone()
    if not customer_id_result:
        tk.messagebox.showerror("Error","Customer not found.")
        return
    customer_id = customer_id_result[0]

    # Get Fragrance Data
    cursor.execute("SELECT FragranceID, Price, Stock FROM Fragrances WHERE FragranceName = ?",(selected_fragrance,))
    fragrance_result = cursor.fetchone()
    if not fragrance_result:
        tk.messagebox.showerror("Error","Fragrance not found.")
        return
    fragrance_id, price, current_stock = fragrance_result


    if current_stock == 0:
        tk.messagebox.showerror("Warning","Stock is Zero. Unable to Complete The Process")
        return

    elif current_stock <= 5:
        tk.messagebox.showwarning("Warning",f"There is {current_stock} Left in Stock !")

    # Genreate an ID for the Sale
    sale_id = str(uuid.uuid4())
    sale_date = datetime.now().strftime("%Y-%m-%d %H:%M")



    # Insert into Sales table
    cursor.execute("""
        INSERT INTO Sales (SaleID, CustomerID, FragranceID, SaleDate)
        VALUES (?, ?, ?, ?)
    """,(sale_id, customer_id, fragrance_id, sale_date))


    # Update Stock
    cursor.execute("""
        UPDATE Fragrances
        SET Stock = Stock - 1
        WHERE FragranceID = ?
    """,(fragrance_id,))

    conn.commit()


    # Clear the fields after submission
    customer_name.set('')
    fragrance_choice.set('')


    tk.messagebox.showinfo("Success","Purchase Recorded Successfully!")




root = tk.Tk()
root.title("Fragrance Shop")
root.geometry("400x300")
root.config(bg="#e6e6fa")
root.resizable(False, False)
root.iconbitmap('Perfume.ico')


main_page = tk.Frame(root, bg="#e6e6fa")
customer_page = tk.Frame(root, bg="#e6e6fa")

for frame in (main_page, customer_page):
    frame.grid(row=0, column=0, sticky='nsew')



# Get data for comboboxes
names = get_names()
fragrances = get_fragrances()


ttk.Label(main_page, text="Customer Name:", background="#e6e6fa").grid(row=0, column=0, padx=10, pady=10, sticky="w")
customer_name = ttk.Combobox(main_page, values=names)
customer_name.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
customer_name.bind("<KeyRelease>", lambda event: update_combobox(event, customer_name, names))

ttk.Label(main_page, text="Fragrance:", background="#e6e6fa").grid(row=1, column=0, padx=10, pady=10, sticky="w")
fragrance_choice = ttk.Combobox(main_page, values=fragrances)
fragrance_choice.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
fragrance_choice.bind("<KeyRelease>", lambda event: update_combobox(event, fragrance_choice, fragrances))

submit_button = tk.Button(main_page, text="Submit Purchase", command=submit_purchase, bg="#4b0082", fg="white", font=('Verdana', 12, 'bold'))
submit_button.grid(row=2, column=1, padx=10, pady=10, sticky="e")




new_customer_button = tk.Button(main_page, text="New Customer", command=lambda: show_frame(customer_page), bg="#4b0082", fg="white", font=('Verdana', 12, 'bold'))
new_customer_button.grid(row=3, column=1, padx=10, pady=10, sticky="e")


ttk.Label(customer_page, text="New Customer", font=('Verdana', 14, 'bold'), background="#e6e6fa").grid(row=0, columnspan=2, pady=15)

ttk.Label(customer_page, text="Customer Name:", font=('Verdana', 12), background="#e6e6fa").grid(row=1, column=0, padx=10, pady=10, sticky="w")
customer_name_entry = ttk.Entry(customer_page)
customer_name_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

ttk.Label(customer_page, text="Mobile Number:", font=('Verdana', 12), background="#e6e6fa").grid(row=2, column=0, padx=10, pady=10, sticky="w")
customer_mobile_entry = ttk.Entry(customer_page)
customer_mobile_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

ttk.Label(customer_page, text="Age:", font=('Verdana', 12), background="#e6e6fa").grid(row=3, column=0, padx=10, pady=10, sticky="w")
customer_age_entry = ttk.Entry(customer_page)
customer_age_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

submit_customer_button = tk.Button(customer_page, text="Submit Customer", command=submit_customer, bg="#4b0082", fg="white", font=('Verdana', 12, 'bold'))
submit_customer_button.grid(row=4, column=1, padx=10, pady=10, sticky="e")

back_button = tk.Button(customer_page, text="Back", command=lambda: show_frame(main_page), bg="#4b0082", fg="white", font=('Verdana', 12, 'bold'))
back_button.grid(row=5, column=1, padx=10, pady=10, sticky="e")




# Configure row and column weights to expand properly
main_page.columnconfigure(1, weight=1)
customer_page.columnconfigure(1, weight=1)

# Show the main page initially
show_frame(main_page)

root.mainloop()