import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ============================================================
# DATABASE SETUP
# ============================================================

def setup_database():
    """Create database and tables if they don't exist"""
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_number TEXT,
            total REAL,
            payment_method TEXT,
            date TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_number TEXT,
            product_name TEXT,
            price REAL,
            quantity INTEGER,
            subtotal REAL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ("Apple", 0.50, 100),
            ("Banana", 0.30, 150),
            ("Milk (1L)", 1.20, 50),
            ("Bread", 2.50, 40),
            ("Eggs (12)", 3.00, 60),
            ("Butter", 2.00, 30),
            ("Cheese", 4.50, 25),
            ("Orange Juice", 3.50, 35),
            ("Coffee", 8.00, 20),
            ("Tea Bags", 5.00, 45),
            ("Sugar (1kg)", 1.80, 55),
            ("Rice (2kg)", 4.00, 40),
            ("Pasta", 1.50, 70),
            ("Tomato Sauce", 2.20, 60),
            ("Water (1.5L)", 0.80, 200),
            ("Chicken Breast", 7.50, 30),
            ("Ground Beef", 9.00, 25),
            ("Salmon Fillet", 12.00, 15),
            ("Yogurt", 1.80, 40),
            ("Ice Cream", 5.50, 20),
            ("Chips", 3.00, 50),
            ("Cookies", 4.00, 35),
            ("Soap", 2.50, 60),
            ("Shampoo", 6.00, 30),
            ("Toothpaste", 3.50, 45),
        ]
        cursor.executemany(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
            sample_products
        )

    conn.commit()
    conn.close()


# ============================================================
# CUSTOM STYLES
# ============================================================

def setup_styles():
    """Configure ttk styles for a modern look"""
    style = ttk.Style()
    style.theme_use("clam")

    # Treeview (tables)
    style.configure("Treeview",
                    font=("Segoe UI", 11),
                    rowheight=30,
                    background="#ffffff",
                    fieldbackground="#ffffff",
                    foreground="#2c3e50")
    style.configure("Treeview.Heading",
                    font=("Segoe UI", 11, "bold"),
                    background="#3498db",
                    foreground="white",
                    padding=6)
    style.map("Treeview.Heading",
              background=[("active", "#2980b9")])
    style.map("Treeview",
              background=[("selected", "#3498db")],
              foreground=[("selected", "white")])

    # Separator
    style.configure("TSeparator", background="#bdc3c7")

    # PanedWindow sash
    style.configure("TPanedwindow", background="#f0f4f8")


# ============================================================
# MAIN APPLICATION
# ============================================================

class ShopCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shop Counter System")
        self.root.geometry("1200x750")
        self.root.minsize(600, 450)
        self.root.configure(bg="#f0f4f8")

        self.cart = {}
        self.receipt_counter = self.get_last_receipt_number()
        self.current_layout = None  # track layout: "horizontal" or "vertical"

        setup_styles()
        self.build_ui()
        self.search_products()

        # ── Responsive: listen to window resize ──
        self.root.bind("<Configure>", self.on_resize)

    # --------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------

    def get_last_receipt_number(self):
        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sales")
        count = cursor.fetchone()[0]
        conn.close()
        return count + 1

    def make_button(self, parent, text, command, bg_color, **kwargs):
        """Helper to create styled buttons that resize nicely"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 11, "bold"),
            bg=bg_color,
            fg="white",
            activebackground=bg_color,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            bd=0,
            padx=12,
            pady=6,
            **kwargs
        )
        return btn

    # --------------------------------------------------------
    # UI BUILDER
    # --------------------------------------------------------

    def build_ui(self):
        # ── Title Bar ──
        self.title_frame = tk.Frame(self.root, bg="#2c3e50")
        self.title_frame.pack(fill="x")

        self.title_label = tk.Label(
            self.title_frame,
            text="🛒  SHOP COUNTER SYSTEM",
            font=("Segoe UI", 20, "bold"),
            bg="#2c3e50", fg="white",
            pady=8
        )
        self.title_label.pack()

        self.date_label = tk.Label(
            self.title_frame,
            text=f"📅  {datetime.now().strftime('%A, %d %B %Y')}",
            font=("Segoe UI", 10),
            bg="#2c3e50", fg="#bdc3c7",
            pady=2
        )
        self.date_label.pack()

        # ── Main container that holds both panels ──
        self.main_container = tk.Frame(self.root, bg="#f0f4f8")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Build left and right panel frames
        self.left_panel = tk.Frame(self.main_container, bg="#ffffff",
                                   relief="flat", bd=0,
                                   highlightthickness=1,
                                   highlightbackground="#dce1e6")
        self.right_panel = tk.Frame(self.main_container, bg="#ffffff",
                                    relief="flat", bd=0,
                                    highlightthickness=1,
                                    highlightbackground="#dce1e6")

        self.build_search_panel(self.left_panel)
        self.build_receipt_panel(self.right_panel)

        # Initial layout will be set by on_resize
        self.current_layout = None

    # --------------------------------------------------------
    # RESPONSIVE LAYOUT MANAGER
    # --------------------------------------------------------

    def on_resize(self, event=None):
        """Rearrange panels based on window width — like CSS media queries"""
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # Adjust title font based on width
        if width < 700:
            self.title_label.config(font=("Segoe UI", 14, "bold"))
            self.date_label.config(font=("Segoe UI", 8))
        elif width < 900:
            self.title_label.config(font=("Segoe UI", 16, "bold"))
            self.date_label.config(font=("Segoe UI", 9))
        else:
            self.title_label.config(font=("Segoe UI", 20, "bold"))
            self.date_label.config(font=("Segoe UI", 10))

        # Decide layout: side-by-side or stacked
        if width >= 850:
            desired = "horizontal"
        else:
            desired = "vertical"

        # Only re-layout if changed (avoids flicker)
        if desired == self.current_layout:
            return

        self.current_layout = desired

        # Remove panels from current positions
        self.left_panel.pack_forget()
        self.right_panel.pack_forget()
        self.left_panel.grid_forget()
        self.right_panel.grid_forget()

        if desired == "horizontal":
            # Side by side using grid with weight
            self.main_container.columnconfigure(0, weight=1, uniform="panel")
            self.main_container.columnconfigure(1, weight=1, uniform="panel")
            self.main_container.rowconfigure(0, weight=1)

            self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
            self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        else:
            # Stacked vertically using grid
            self.main_container.columnconfigure(0, weight=1)
            self.main_container.rowconfigure(0, weight=1)
            self.main_container.rowconfigure(1, weight=1)

            self.left_panel.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
            self.right_panel.grid(row=1, column=0, sticky="nsew", pady=(5, 0))

    # --------------------------------------------------------
    # LEFT PANEL — Product Search
    # --------------------------------------------------------

    def build_search_panel(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)  # table row expands

        # Header
        header = tk.Frame(parent, bg="#ffffff", padx=12, pady=8)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        tk.Label(
            header,
            text="🔍  Search Products",
            font=("Segoe UI", 13, "bold"),
            bg="#ffffff", fg="#2c3e50"
        ).grid(row=0, column=0, sticky="w")

        # Search bar
        search_frame = tk.Frame(parent, bg="#ffffff", padx=12, pady=4)
        search_frame.grid(row=1, column=0, sticky="ew")
        search_frame.columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.search_products())

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 12),
            relief="flat",
            highlightthickness=2,
            highlightbackground="#3498db",
            highlightcolor="#2980b9"
        )
        search_entry.grid(row=0, column=0, sticky="ew", ipady=7, padx=(0, 8))
        search_entry.focus()

        search_btn = self.make_button(search_frame, "Search",
                                      self.search_products, "#3498db")
        search_btn.grid(row=0, column=1, sticky="e")

        # Product table
        table_frame = tk.Frame(parent, bg="#ffffff", padx=12)
        table_frame.grid(row=2, column=0, sticky="nsew", pady=4)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("ID", "Product Name", "Price ($)", "Stock")
        self.product_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        for col in columns:
            self.product_table.heading(col, text=col)

        self.product_table.column("ID", width=40, minwidth=35, anchor="center")
        self.product_table.column("Product Name", width=150, minwidth=100, anchor="w")
        self.product_table.column("Price ($)", width=80, minwidth=60, anchor="center")
        self.product_table.column("Stock", width=60, minwidth=50, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                  command=self.product_table.yview)
        self.product_table.configure(yscrollcommand=scrollbar.set)

        self.product_table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.product_table.bind("<Double-1>", lambda e: self.add_to_cart())

        # Add to cart row
        add_frame = tk.Frame(parent, bg="#ffffff", padx=12, pady=8)
        add_frame.grid(row=3, column=0, sticky="ew")
        add_frame.columnconfigure(2, weight=1)

        tk.Label(add_frame, text="Qty:", font=("Segoe UI", 11),
                 bg="#ffffff").grid(row=0, column=0, sticky="w")

        self.qty_var = tk.IntVar(value=1)
        qty_spin = tk.Spinbox(
            add_frame, from_=1, to=999,
            textvariable=self.qty_var,
            font=("Segoe UI", 11), width=5,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#3498db"
        )
        qty_spin.grid(row=0, column=1, padx=8, sticky="w")

        add_btn = self.make_button(add_frame, "➕ Add to Cart",
                                   self.add_to_cart, "#27ae60")
        add_btn.grid(row=0, column=2, sticky="e")

        # Tip
        tk.Label(
            parent,
            text="💡 Double-click a product to add it quickly",
            font=("Segoe UI", 9), bg="#ffffff", fg="#95a5a6",
            padx=12, pady=4
        ).grid(row=4, column=0, sticky="w")

    # --------------------------------------------------------
    # RIGHT PANEL — Receipt / Cart
    # --------------------------------------------------------

    def build_receipt_panel(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)  # cart table expands

        # Header
        header = tk.Frame(parent, bg="#ffffff", padx=12, pady=8)
        header.grid(row=0, column=0, sticky="ew")

        tk.Label(
            header,
            text="🧾  Receipt / Cart",
            font=("Segoe UI", 13, "bold"),
            bg="#ffffff", fg="#2c3e50"
        ).pack(anchor="w")

        # Cart table
        cart_frame = tk.Frame(parent, bg="#ffffff", padx=12)
        cart_frame.grid(row=1, column=0, sticky="nsew", pady=4)
        cart_frame.columnconfigure(0, weight=1)
        cart_frame.rowconfigure(0, weight=1)

        cart_columns = ("Product", "Price", "Qty", "Subtotal")
        self.cart_table = ttk.Treeview(
            cart_frame,
            columns=cart_columns,
            show="headings"
        )

        for col in cart_columns:
            self.cart_table.heading(col, text=col)

        self.cart_table.column("Product", width=140, minwidth=80, anchor="w")
        self.cart_table.column("Price", width=70, minwidth=50, anchor="center")
        self.cart_table.column("Qty", width=50, minwidth=40, anchor="center")
        self.cart_table.column("Subtotal", width=80, minwidth=60, anchor="center")

        cart_scroll = ttk.Scrollbar(cart_frame, orient="vertical",
                                    command=self.cart_table.yview)
        self.cart_table.configure(yscrollcommand=cart_scroll.set)

        self.cart_table.grid(row=0, column=0, sticky="nsew")
        cart_scroll.grid(row=0, column=1, sticky="ns")

        # Cart action buttons
        btn_frame = tk.Frame(parent, bg="#ffffff", padx=12, pady=4)
        btn_frame.grid(row=2, column=0, sticky="ew")
        btn_frame.columnconfigure(2, weight=1)

        remove_btn = self.make_button(btn_frame, "➖ Remove",
                                      self.remove_from_cart, "#e74c3c")
        remove_btn.grid(row=0, column=0, sticky="w", padx=(0, 6))

        clear_btn = self.make_button(btn_frame, "🗑️ Clear",
                                     self.clear_cart, "#e67e22")
        clear_btn.grid(row=0, column=1, sticky="w")

        # Totals area
        totals_frame = tk.Frame(parent, bg="#ecf0f1", padx=12, pady=8)
        totals_frame.grid(row=3, column=0, sticky="ew", padx=12, pady=6)
        totals_frame.columnconfigure(1, weight=1)

        self.subtotal_var = tk.StringVar(value="$0.00")
        self.tax_var = tk.StringVar(value="$0.00")
        self.total_var = tk.StringVar(value="$0.00")

        labels_data = [
            ("Subtotal:", self.subtotal_var, 11, "#2c3e50"),
            ("Tax (10%):", self.tax_var, 11, "#2c3e50"),
        ]

        for i, (label, var, size, color) in enumerate(labels_data):
            tk.Label(totals_frame, text=label, font=("Segoe UI", size),
                     bg="#ecf0f1", fg=color).grid(row=i, column=0, sticky="w")
            tk.Label(totals_frame, textvariable=var, font=("Segoe UI", size, "bold"),
                     bg="#ecf0f1", fg=color).grid(row=i, column=1, sticky="e")

        ttk.Separator(totals_frame, orient="horizontal").grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=4
        )

        tk.Label(totals_frame, text="TOTAL:", font=("Segoe UI", 14, "bold"),
                 bg="#ecf0f1", fg="#e74c3c").grid(row=3, column=0, sticky="w")
        tk.Label(totals_frame, textvariable=self.total_var,
                 font=("Segoe UI", 14, "bold"),
                 bg="#ecf0f1", fg="#e74c3c").grid(row=3, column=1, sticky="e")

        # Payment section
        pay_frame = tk.LabelFrame(
            parent,
            text="  💳 Payment Method  ",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff", fg="#2c3e50",
            padx=10, pady=6
        )
        pay_frame.grid(row=4, column=0, sticky="ew", padx=12, pady=4)
        pay_frame.columnconfigure(1, weight=1)

        self.payment_var = tk.StringVar(value="cash")

        # Cash row
        cash_radio = tk.Radiobutton(
            pay_frame, text="💵 Cash",
            variable=self.payment_var, value="cash",
            font=("Segoe UI", 11), bg="#ffffff", fg="#2c3e50",
            command=self.toggle_cash_input
        )
        cash_radio.grid(row=0, column=0, sticky="w", pady=2)

        cash_input_frame = tk.Frame(pay_frame, bg="#ffffff")
        cash_input_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        cash_input_frame.columnconfigure(0, weight=1)

        self.cash_given_var = tk.StringVar()
        self.cash_entry = tk.Entry(
            cash_input_frame,
            textvariable=self.cash_given_var,
            font=("Segoe UI", 11),
            relief="flat",
            highlightthickness=1,
            highlightbackground="#3498db"
        )
        self.cash_entry.grid(row=0, column=0, sticky="ew", ipady=4)

        tk.Label(cash_input_frame, text="  Amount",
                 font=("Segoe UI", 9), bg="#ffffff",
                 fg="#95a5a6").grid(row=0, column=1, sticky="w", padx=4)

        # Card row
        tk.Radiobutton(
            pay_frame, text="💳 Card (Debit / Credit)",
            variable=self.payment_var, value="card",
            font=("Segoe UI", 11), bg="#ffffff", fg="#2c3e50",
            command=self.toggle_cash_input
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=2)

        # Checkout button
        checkout_btn = tk.Button(
            parent,
            text="✅   CHECKOUT",
            command=self.checkout,
            font=("Segoe UI", 14, "bold"),
            bg="#2ecc71", fg="white",
            activebackground="#27ae60",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            bd=0,
            pady=10
        )
        checkout_btn.grid(row=5, column=0, sticky="ew", padx=12, pady=(6, 12))

    # --------------------------------------------------------
    # SEARCH PRODUCTS
    # --------------------------------------------------------

    def search_products(self, *args):
        keyword = self.search_var.get().strip()
        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()

        if keyword:
            cursor.execute(
                "SELECT id, name, price, stock FROM products "
                "WHERE name LIKE ? ORDER BY name",
                (f"%{keyword}%",)
            )
        else:
            cursor.execute(
                "SELECT id, name, price, stock FROM products ORDER BY name"
            )

        rows = cursor.fetchall()
        conn.close()

        for row in self.product_table.get_children():
            self.product_table.delete(row)

        for row in rows:
            pid, name, price, stock = row
            tag = "low_stock" if stock < 5 else ("even" if len(self.product_table.get_children()) % 2 == 0 else "odd")
            self.product_table.insert(
                "", "end",
                values=(pid, name, f"${price:.2f}", stock),
                tags=(tag,)
            )

        self.product_table.tag_configure("low_stock", foreground="#e74c3c",
                                         background="#fdf0f0")
        self.product_table.tag_configure("even", background="#f8f9fa")
        self.product_table.tag_configure("odd", background="#ffffff")

    # --------------------------------------------------------
    # CART OPERATIONS
    # --------------------------------------------------------

    def add_to_cart(self):
        selected = self.product_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product first!")
            return

        values = self.product_table.item(selected[0])["values"]
        product_id = int(values[0])
        name = values[1]
        price = float(str(values[2]).replace("$", ""))
        stock = int(values[3])
        qty = self.qty_var.get()

        already = self.cart.get(product_id, {}).get("quantity", 0)
        if already + qty > stock:
            messagebox.showerror(
                "Out of Stock",
                f"Only {stock} unit(s) of '{name}' available!\n"
                f"Already in cart: {already}"
            )
            return

        if product_id in self.cart:
            self.cart[product_id]["quantity"] += qty
        else:
            self.cart[product_id] = {
                "name": name,
                "price": price,
                "quantity": qty
            }

        self.refresh_cart()

    def remove_from_cart(self):
        selected = self.cart_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select an item to remove!")
            return

        values = self.cart_table.item(selected[0])["values"]
        product_name = values[0]
        for pid, data in list(self.cart.items()):
            if data["name"] == product_name:
                del self.cart[pid]
                break

        self.refresh_cart()

    def clear_cart(self):
        if not self.cart:
            return
        if messagebox.askyesno("Clear Cart", "Clear all items from cart?"):
            self.cart.clear()
            self.refresh_cart()

    def refresh_cart(self):
        for row in self.cart_table.get_children():
            self.cart_table.delete(row)

        subtotal = 0.0
        i = 0
        for pid, data in self.cart.items():
            item_sub = data["price"] * data["quantity"]
            subtotal += item_sub
            tag = "even" if i % 2 == 0 else "odd"
            self.cart_table.insert("", "end", values=(
                data["name"],
                f"${data['price']:.2f}",
                data["quantity"],
                f"${item_sub:.2f}"
            ), tags=(tag,))
            i += 1

        self.cart_table.tag_configure("even", background="#f8f9fa")
        self.cart_table.tag_configure("odd", background="#ffffff")

        tax = subtotal * 0.10
        total = subtotal + tax

        self.subtotal_var.set(f"${subtotal:.2f}")
        self.tax_var.set(f"${tax:.2f}")
        self.total_var.set(f"${total:.2f}")

    # --------------------------------------------------------
    # PAYMENT TOGGLE
    # --------------------------------------------------------

    def toggle_cash_input(self):
        if self.payment_var.get() == "cash":
            self.cash_entry.config(state="normal")
        else:
            self.cash_entry.config(state="disabled")
            self.cash_given_var.set("")

    # --------------------------------------------------------
    # CHECKOUT
    # --------------------------------------------------------

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Add items to the cart first!")
            return

        subtotal = sum(d["price"] * d["quantity"] for d in self.cart.values())
        tax = subtotal * 0.10
        total = subtotal + tax
        payment_method = self.payment_var.get()
        change = 0.0
        cash_given = total

        if payment_method == "cash":
            try:
                cash_given = float(self.cash_given_var.get())
            except ValueError:
                messagebox.showerror("Invalid Amount",
                                     "Enter the cash amount given by customer.")
                return
            if cash_given < total:
                messagebox.showerror(
                    "Insufficient Cash",
                    f"Total: ${total:.2f}\n"
                    f"Given: ${cash_given:.2f}\n"
                    f"Short: ${total - cash_given:.2f}"
                )
                return
            change = cash_given - total

        receipt_number = f"RCP-{self.receipt_counter:05d}"
        self.save_sale(receipt_number, total, payment_method)
        self.update_stock()
        self.show_receipt(receipt_number, subtotal, tax, total,
                          payment_method, cash_given, change)

        self.cart.clear()
        self.refresh_cart()
        self.cash_given_var.set("")
        self.receipt_counter += 1

    def save_sale(self, receipt_number, total, payment_method):
        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sales (receipt_number, total, payment_method, date) "
            "VALUES (?, ?, ?, ?)",
            (receipt_number, total, payment_method,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        for pid, data in self.cart.items():
            cursor.execute(
                "INSERT INTO sale_items (receipt_number, product_name, price, quantity, subtotal) "
                "VALUES (?, ?, ?, ?, ?)",
                (receipt_number, data["name"], data["price"],
                 data["quantity"], data["price"] * data["quantity"])
            )
        conn.commit()
        conn.close()

    def update_stock(self):
        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        for pid, data in self.cart.items():
            cursor.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (data["quantity"], pid)
            )
        conn.commit()
        conn.close()
        self.search_products()

    # --------------------------------------------------------
    # RECEIPT POPUP (also responsive)
    # --------------------------------------------------------

    def show_receipt(self, receipt_number, subtotal, tax, total,
                     payment_method, cash_given, change):
        win = tk.Toplevel(self.root)
        win.title("🧾 Receipt")
        win.configure(bg="white")
        win.minsize(350, 400)

        # Make it 40% of main window width, capped
        w = max(380, min(500, int(self.root.winfo_width() * 0.4)))
        h = max(500, min(700, int(self.root.winfo_height() * 0.85)))
        win.geometry(f"{w}x{h}")

        # Responsive receipt
        win.columnconfigure(0, weight=1)
        win.rowconfigure(0, weight=1)

        frame = tk.Frame(win, bg="white", padx=15, pady=15)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        # Build receipt text
        lines = []
        lines.append("=" * 44)
        lines.append("         SHOP COUNTER SYSTEM")
        lines.append("        Your Friendly Local Store")
        lines.append("=" * 44)
        lines.append(f" Receipt #: {receipt_number}")
        lines.append(f" Date:      {datetime.now().strftime('%d/%m/%Y  %H:%M:%S')}")
        lines.append("-" * 44)
        lines.append(f" {'ITEM':<18} {'QTY':>4} {'PRICE':>8} {'TOTAL':>8}")
        lines.append("-" * 44)

        for data in self.cart.values():
            name = data['name'][:18]
            lines.append(
                f" {name:<18} {data['quantity']:>4} "
                f"${data['price']:>7.2f} "
                f"${data['price']*data['quantity']:>7.2f}"
            )

        lines.append("-" * 44)
        lines.append(f"{'Subtotal:':>34} ${subtotal:>7.2f}")
        lines.append(f"{'Tax (10%):':>34} ${tax:>7.2f}")
        lines.append("=" * 44)
        lines.append(f"{'TOTAL:':>34} ${total:>7.2f}")
        lines.append("=" * 44)
        lines.append(f" Payment: {payment_method.upper()}")

        if payment_method == "cash":
            lines.append(f" Cash Given:  ${cash_given:.2f}")
            lines.append(f" Change:      ${change:.2f}")

        lines.append("-" * 44)
        lines.append("     Thank you for shopping with us!")
        lines.append("         Please come again! 😊")
        lines.append("=" * 44)

        receipt_str = "\n".join(lines)

        text_widget = tk.Text(
            frame,
            font=("Courier New", 10),
            bg="#fffff8",
            fg="#2c3e50",
            relief="flat",
            wrap="none",
            padx=10,
            pady=10
        )
        text_widget.insert("1.0", receipt_str)
        text_widget.config(state="disabled")
        text_widget.grid(row=0, column=0, sticky="nsew")

        # Scrollbar for receipt
        r_scroll = ttk.Scrollbar(frame, orient="vertical",
                                 command=text_widget.yview)
        text_widget.configure(yscrollcommand=r_scroll.set)
        r_scroll.grid(row=0, column=1, sticky="ns")

        # Close button
        close_btn = tk.Button(
            win,
            text="✅  Close Receipt",
            command=win.destroy,
            font=("Segoe UI", 12, "bold"),
            bg="#2ecc71", fg="white",
            activebackground="#27ae60",
            relief="flat",
            cursor="hand2",
            pady=8
        )
        close_btn.grid(row=1, column=0, sticky="ew", padx=15, pady=10)


# ============================================================
# RUN THE APP
# ============================================================

if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = ShopCounterApp(root)
    root.mainloop()
