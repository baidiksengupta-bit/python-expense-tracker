import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import date

FILE_NAME = "expenses.csv"

# =====================================================================
# MEMBER 1: Database & File Initialization (CSV Storage)
# =====================================================================
def initialize_file():
    """Creates the CSV file with headers if it does not exist yet."""
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Category", "Description", "Amount"])


# =====================================================================
# MEMBER 2: Data Validation & Adding Expense Records
# =====================================================================
def add_expense():
    """Validates user input and appends a new expense row to the CSV."""
    category = category_var.get().strip()
    description = desc_entry.get().strip()
    amount_str = amount_entry.get().strip()

    if not category or not description or not amount_str:
        messagebox.showwarning("Input Error", "All fields are required!")
        return

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Amount", "Please enter a valid positive number for Amount.")
        return

    today = date.today().strftime("%Y-%m-%d")

    with open(FILE_NAME, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([today, category, description, f"{amount:.2f}"])

    # Clear input fields and refresh display
    desc_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    refresh_dashboard()
    messagebox.showinfo("Success", f"Added Rs. {amount:.2f} under {category}!")


# =====================================================================
# MEMBER 3: Reading Data & Populating the Table (Treeview)
# =====================================================================
def load_expenses_to_table(filter_category="All"):
    """Reads all records from CSV, applies category filter, and updates table."""
    for row in tree.get_children():
        tree.delete(row)

    records = []
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header row
            for idx, row in enumerate(reader):
                if len(row) == 4:
                    records.append(row)
                    if filter_category == "All" or row[1] == filter_category:
                        tree.insert("", tk.END, iid=str(idx), values=row)
    return records


# =====================================================================
# MEMBER 4: Deleting Records & Updating CSV
# =====================================================================
def delete_selected_expense():
    """Deletes the selected expense from the table and rewrites the CSV."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select Record", "Please click on a record in the table to delete it.")
        return

    selected_index = int(selected[0])
    all_rows = []

    with open(FILE_NAME, mode="r", newline="", encoding="utf-8") as file:
        reader = list(csv.reader(file))
        header = reader[0]
        data_rows = reader[1:]

    if 0 <= selected_index < len(data_rows):
        removed = data_rows.pop(selected_index)
        with open(FILE_NAME, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(data_rows)
        refresh_dashboard()
        messagebox.showinfo("Deleted", f"Removed '{removed[2]}' (Rs. {removed[3]})")


# =====================================================================
# MEMBER 5: Analytics & Summary Calculations (Dictionaries)
# =====================================================================
def calculate_analytics(records):
    """Calculates grand total and category-wise breakdown using a dictionary."""
    total_spent = 0.0
    category_totals = {}

    for row in records:
        cat = row[1]
        amt = float(row[3])
        total_spent += amt
        category_totals[cat] = category_totals.get(cat, 0.0) + amt

    total_label.config(text=f"Total Spend: Rs. {total_spent:,.2f}")
    return total_spent, category_totals


# =====================================================================
# MEMBER 6: Visual Chart Generator (Pure Tkinter Canvas Bar Chart)
# =====================================================================
def draw_chart(total_spent, category_totals):
    """Draws a colorful horizontal bar chart on the Tkinter Canvas."""
    chart_canvas.delete("all")

    if total_spent == 0:
        chart_canvas.create_text(
            180, 100, text="No expenses yet. Add an item to see the chart!",
            fill="#666666", font=("Arial", 10, "italic")
        )
        return

    colors = {
        "Food": "#FF6B6B",
        "Transport": "#4ECDC4",
        "Books & Study": "#45B7D1",
        "Entertainment": "#FFA07A",
        "Rent & Bills": "#98D8C8",
        "Other": "#C39BD3"
    }

    y_pos = 20
    max_bar_width = 210

    for cat, amt in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        pct = (amt / total_spent) * 100
        bar_width = max(int((amt / total_spent) * max_bar_width), 6)
        color = colors.get(cat, "#5DADE2")

        # Category label
        chart_canvas.create_text(10, y_pos + 10, anchor="w", text=cat, font=("Arial", 9, "bold"))
        # Bar rectangle
        chart_canvas.create_rectangle(105, y_pos, 105 + bar_width, y_pos + 20, fill=color, outline="")
        # Amount & Percentage label
        chart_canvas.create_text(
            110 + bar_width, y_pos + 10, anchor="w",
            text=f"Rs.{amt:.0f} ({pct:.1f}%)", font=("Arial", 9)
        )
        y_pos += 32


# =====================================================================
# MEMBER 7: Main GUI Layout & Dashboard Controller
# =====================================================================
def refresh_dashboard(*args):
    """Refreshes the table, analytics totals, and visual chart together."""
    records = load_expenses_to_table(filter_var.get())
    total_spent, category_totals = calculate_analytics(records)
    draw_chart(total_spent, category_totals)


# --- Main Window Setup ---
root = tk.Tk()
root.title("Personal Expense & Budget Tracker (Pure Python)")
root.geometry("880x540")
root.configure(padx=15, pady=15)

initialize_file()

# --- Top Input Frame ---
input_frame = tk.LabelFrame(root, text=" Add New Expense ", font=("Arial", 10, "bold"), padx=10, pady=10)
input_frame.pack(fill="x", pady=(0, 12))

tk.Label(input_frame, text="Category:").grid(row=0, column=0, padx=5, pady=5)
categories = ["Food", "Transport", "Books & Study", "Entertainment", "Rent & Bills", "Other"]
category_var = tk.StringVar(value=categories[0])
ttk.Combobox(input_frame, textvariable=category_var, values=categories, state="readonly", width=16).grid(row=0, column=1, padx=5)

tk.Label(input_frame, text="Description:").grid(row=0, column=2, padx=5, pady=5)
desc_entry = tk.Entry(input_frame, width=25)
desc_entry.grid(row=0, column=3, padx=5)

tk.Label(input_frame, text="Amount (Rs):").grid(row=0, column=4, padx=5, pady=5)
amount_entry = tk.Entry(input_frame, width=12)
amount_entry.grid(row=0, column=5, padx=5)

tk.Button(
    input_frame, text="+ Add Expense", command=add_expense,
    bg="#2ECC71", fg="white", font=("Arial", 9, "bold"), padx=10
).grid(row=0, column=6, padx=10)

# --- Middle Content Area (Left: Table | Right: Visual Chart) ---
middle_frame = tk.Frame(root)
middle_frame.pack(fill="both", expand=True)

# Left Table Frame
table_frame = tk.LabelFrame(middle_frame, text=" Expense History ", font=("Arial", 10, "bold"), padx=8, pady=8)
table_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

filter_bar = tk.Frame(table_frame)
filter_bar.pack(fill="x", pady=(0, 6))
tk.Label(filter_bar, text="Filter by Category:").pack(side="left")
filter_var = tk.StringVar(value="All")
filter_menu = ttk.Combobox(filter_bar, textvariable=filter_var, values=["All"] + categories, state="readonly", width=15)
filter_menu.pack(side="left", padx=6)
filter_menu.bind("<<ComboboxSelected>>", refresh_dashboard)

tk.Button(
    filter_bar, text="Delete Selected", command=delete_selected_expense,
    bg="#E74C3C", fg="white", font=("Arial", 8, "bold")
).pack(side="right")

columns = ("Date", "Category", "Description", "Amount")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=13)
for col, width in zip(columns, [90, 110, 150, 80]):
    tree.heading(col, text=col)
    tree.column(col, width=width, anchor="center" if col != "Description" else "w")
tree.pack(fill="both", expand=True)

# Right Analytics & Chart Frame
chart_frame = tk.LabelFrame(middle_frame, text=" Category Breakdown Chart ", font=("Arial", 10, "bold"), padx=10, pady=10)
chart_frame.pack(side="right", fill="both")

total_label = tk.Label(chart_frame, text="Total Spend: Rs. 0.00", font=("Arial", 13, "bold"), fg="#2C3E50")
total_label.pack(pady=(0, 10))

chart_canvas = tk.Canvas(chart_frame, width=380, height=230, bg="white", highlightthickness=1, highlightbackground="#CCCCCC")
chart_canvas.pack()

# Initial Load
refresh_dashboard()
root.mainloop()