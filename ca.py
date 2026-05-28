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

    style.configure("TSeparator", background="#bdc3c7")
    style.configure("TPanedwindow", background="#f0f4f8")

    # Notebook (tabs) style
    style.configure("TNotebook", background="#f0f4f8", borderwidth=0)
    style.configure("TNotebook.Tab",
                    font=("Segoe UI", 12, "bold"),
                    padding=[20, 8],
                    background="#dce1e6",
                    foreground="#2c3e50")
    style.map("TNotebook.Tab",
              background=[("selected", "#3498db")],
              foreground=[("selected", "white")],
              expand=[("selected", [1, 1, 1, 0])])


# ============================================================
# MAIN APPLICATION
# ============================================================

class ShopCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shop Counter System")
        self.root.geometry("1200x750")
        self.root.minsize(600, 500)
        self.root.configure(bg="#f0f4f8")

        self.cart = {}
        self.receipt_counter = self.get_last_receipt_number()
        self.current_layout = None

        setup_styles()
        self.build_ui()
        self.search_products()

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
            bg="#2c3e50", fg="white", pady=8
        )
        self.title_label.pack()

        self.date_label = tk.Label(
            self.title_frame,
            text=f"📅  {datetime.now().strftime('%A, %d %B %Y')}",
            font=("Segoe UI", 10),
            bg="#2c3e50", fg="#bdc3c7", pady=2
        )
        self.date_label.pack()

        # ── Notebook (Tabs) ──
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Counter (main POS)
        self.counter_tab = tk.Frame(self.notebook, bg="#f0f4f8")
        self.notebook.add(self.counter_tab, text="  🛒 Counter  ")

        # Tab 2: Product Management
        self.product_mgmt_tab = tk.Frame(self.notebook, bg="#f0f4f8")
        self.notebook.add(self.product_mgmt_tab, text="  📦 Manage Products  ")

        # Tab 3: Receipt History
        self.history_tab = tk.Frame(self.notebook, bg="#f0f4f8")
        self.notebook.add(self.history_tab, text="  📋 Receipt History  ")

        # Build each tab
        self.build_counter_tab()
        self.build_product_mgmt_tab()
        self.build_history_tab()

        # Refresh history when tab is selected
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    # --------------------------------------------------------
    # TAB CHANGE HANDLER
    # --------------------------------------------------------

    def on_tab_changed(self, event=None):
        selected = self.notebook.index(self.notebook.select())
        if selected == 1:
            self.load_all_products_mgmt()
        elif selected == 2:
            self.load_receipt_history()

    # ============================================================
    # TAB 1: COUNTER (MAIN POS)
    # ============================================================

    def build_counter_tab(self):
        self.main_container = tk.Frame(self.counter_tab, bg="#f0f4f8")
        self.main_container.pack(fill="both", expand=True)

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

        self.current_layout = None

    # --------------------------------------------------------
    # RESPONSIVE LAYOUT
    # --------------------------------------------------------

    def on_resize(self, event=None):
        width = self.root.winfo_width()

        if width < 700:
            self.title_label.config(font=("Segoe UI", 14, "bold"))
            self.date_label.config(font=("Segoe UI", 8))
        elif width < 900:
            self.title_label.config(font=("Segoe UI", 16, "bold"))
            self.date_label.config(font=("Segoe UI", 9))
        else:
            self.title_label.config(font=("Segoe UI", 20, "bold"))
            self.date_label.config(font=("Segoe UI", 10))

        desired = "horizontal" if width >= 850 else "vertical"

        if desired == self.current_layout:
            return

        self.current_layout = desired

        self.left_panel.pack_forget()
        self.right_panel.pack_forget()
        self.left_panel.grid_forget()
        self.right_panel.grid_forget()

        if desired == "horizontal":
            self.main_container.columnconfigure(0, weight=1, uniform="panel")
            self.main_container.columnconfigure(1, weight=1, uniform="panel")
            self.main_container.rowconfigure(0, weight=1)

            self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
            self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        else:
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
        parent.rowconfigure(2, weight=1)

        header = tk.Frame(parent, bg="#ffffff", padx=12, pady=8)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        tk.Label(header, text="🔍  Search Products",
                 font=("Segoe UI", 13, "bold"),
                 bg="#ffffff", fg="#2c3e50").grid(row=0, column=0, sticky="w")

        search_frame = tk.Frame(parent, bg="#ffffff", padx=12, pady=4)
        search_frame.grid(row=1, column=0, sticky="ew")
        search_frame.columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.search_products())

        search_entry = tk.Entry(
            search_frame, textvariable=self.search_var,
            font=("Segoe UI", 12), relief="flat",
            highlightthickness=2, highlightbackground="#3498db",
            highlightcolor="#2980b9"
        )
        search_entry.grid(row=0, column=0, sticky="ew", ipady=7, padx=(0, 8))
        search_entry.focus()

        search_btn = self.make_button(search_frame, "Search",
                                      self.search_products, "#3498db")
        search_btn.grid(row=0, column=1, sticky="e")

        table_frame = tk.Frame(parent, bg="#ffffff", padx=12)
        table_frame.grid(row=2, column=0, sticky="nsew", pady=4)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("ID", "Product Name", "Price ($)", "Stock")
        self.product_table = ttk.Treeview(
            table_frame, columns=columns,
            show="headings", selectmode="browse"
        )

        for col in columns:
            self.product_table.heading(col, text=col)

        self.product_table.column("ID", width=40, minwidth=35, anchor="center")
        self.product_table.column("Product Name", width=150, minwidth=100, anchor="w")
        self.product_table.column("Price ($)", width=80, minwidth=60, anchor="center")
        self.product_table.column("Stock", width=60, minwidth=50, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",  command=self.product_table.yview)
        self.product_table.configure(yscrollcommand=scrollbar.set)

        self.product_table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.product_table.bind("<Double-1>", lambda e: self.add_to_cart())

        add_frame = tk.Frame(parent, bg="#ffffff", padx=12, pady=8)
        add_frame.grid(row=3, column=0, sticky="ew")
        add_frame.columnconfigure(2, weight=1)

        tk.Label(add_frame, text="Qty:", font=("Segoe UI", 11), bg="#ffffff").grid(row=0, column=0, sticky="w")

        self.qty_var = tk.IntVar(value=1)
        qty_spin = tk.Spinbox(
            add_frame, from_=1, to=999,
            textvariable=self.qty_var,
            font=("Segoe UI", 11), width=5,
            relief="flat", highlightthickness=1,
            highlightbackground="#3498db"
        )
        qty_spin.grid(row=0, column=1, padx=8, sticky="w")

        add_btn = self.make_button(add_frame, "➕ Add to Cart",       self.add_to_cart, "#27ae60")
        add_btn.grid(row=0, column=2, sticky="e")

        tk.Label(parent, text="💡 Double-click a product to add it quickly", font=("Segoe UI", 9), bg="#ffffff", fg="#95a5a6", padx=12, pady=4).grid(row=4, column=0, sticky="w")

    # --------------------------------------------------------
    # RIGHT PANEL — Receipt / Cart
    # --------------------------------------------------------

    def build_receipt_panel(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        header = tk.Frame(parent, bg="#ffffff", padx=12, pady=8)
        header.grid(row=0, column=0, sticky="ew")

        tk.Label(header, text="🧾  Receipt / Cart", font=("Segoe UI", 13, "bold"), bg="#ffffff", fg="#2c3e50").pack(anchor="w")

        cart_frame = tk.Frame(parent, bg="#ffffff", padx=12)
        cart_frame.grid(row=1, column=0, sticky="nsew", pady=4)
        cart_frame.columnconfigure(0, weight=1)
        cart_frame.rowconfigure(0, weight=1)

        cart_columns = ("Product", "Price", "Qty", "Subtotal")
        self.cart_table = ttk.Treeview(
            cart_frame, columns=cart_columns, show="headings"
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

        btn_frame = tk.Frame(parent, bg="#ffffff", padx=12, pady=4)
        btn_frame.grid(row=2, column=0, sticky="ew")
        btn_frame.columnconfigure(2, weight=1)

        remove_btn = self.make_button(btn_frame, "➖ Remove",      self.remove_from_cart, "#e74c3c")
        remove_btn.grid(row=0, column=0, sticky="w", padx=(0, 6))

        clear_btn = self.make_button(btn_frame, "🗑️ Clear",     self.clear_cart, "#e67e22")
        clear_btn.grid(row=0, column=1, sticky="w")

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
            tk.Label(totals_frame, text=label, font=("Segoe UI", size), bg="#ecf0f1", fg=color).grid(row=i, column=0, sticky="w")
            tk.Label(totals_frame, textvariable=var, font=("Segoe UI", size, "bold"),     bg="#ecf0f1", fg=color).grid(row=i, column=1, sticky="e")

        ttk.Separator(totals_frame, orient="horizontal").grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=4
        )

        tk.Label(totals_frame, text="TOTAL:", font=("Segoe UI", 14, "bold"), bg="#ecf0f1", fg="#e74c3c").grid(row=3, column=0, sticky="w")
        tk.Label(totals_frame, textvariable=self.total_var, font=("Segoe UI", 14, "bold"), bg="#ecf0f1", fg="#e74c3c").grid(row=3, column=1, sticky="e")

        pay_frame = tk.LabelFrame(
            parent, text="  💳 Payment Method  ",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff", fg="#2c3e50", padx=10, pady=6
        )
        pay_frame.grid(row=4, column=0, sticky="ew", padx=12, pady=4)
        pay_frame.columnconfigure(1, weight=1)

        self.payment_var = tk.StringVar(value="cash")

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
            cash_input_frame, textvariable=self.cash_given_var,
            font=("Segoe UI", 11), relief="flat",
            highlightthickness=1, highlightbackground="#3498db"
        )
        self.cash_entry.grid(row=0, column=0, sticky="ew", ipady=4)

        tk.Label(cash_input_frame, text="  Amount", font=("Segoe UI", 9), bg="#ffffff", fg="#95a5a6").grid(row=0, column=1, sticky="w", padx=4)

        tk.Radiobutton(
            pay_frame, text="💳 Card (Debit / Credit)",
            variable=self.payment_var, value="card",
            font=("Segoe UI", 11), bg="#ffffff", fg="#2c3e50",
            command=self.toggle_cash_input
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=2)

        checkout_btn = tk.Button(
            parent, text="✅   CHECKOUT",
            command=self.checkout,
            font=("Segoe UI", 14, "bold"),
            bg="#2ecc71", fg="white",
            activebackground="#27ae60", activeforeground="white",
            relief="flat", cursor="hand2", bd=0, pady=10
        )
        checkout_btn.grid(row=5, column=0, sticky="ew", padx=12, pady=(6, 12))

    # ============================================================
    # TAB 2: PRODUCT MANAGEMENT
    # ============================================================

    def build_product_mgmt_tab(self):
        self.product_mgmt_tab.columnconfigure(0, weight=1)
        self.product_mgmt_tab.rowconfigure(1, weight=1)

        # ── Top: Add / Edit Product Form ──
        form_frame = tk.LabelFrame(
            self.product_mgmt_tab,
            text="  ➕ Add / Edit Product  ",
            font=("Segoe UI", 12, "bold"),
            bg="#ffffff", fg="#2c3e50",
            padx=15, pady=12
        )
        form_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)
        form_frame.columnconfigure(5, weight=1)

        # Product Name
        tk.Label(form_frame, text="Product Name:", font=("Segoe UI", 11), bg="#ffffff", fg="#2c3e50").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=5)

        self.mgmt_name_var = tk.StringVar()
        name_entry = tk.Entry(
            form_frame, textvariable=self.mgmt_name_var,
            font=("Segoe UI", 12), relief="flat",
            highlightthickness=2, highlightbackground="#3498db"
        )
        name_entry.grid(row=0, column=1, sticky="ew", ipady=5, padx=(0, 15), pady=5)

        # Price
        tk.Label(form_frame, text="Price ($):", font=("Segoe UI", 11), bg="#ffffff", fg="#2c3e50").grid(row=0, column=2, sticky="w", padx=(0, 8), pady=5)

        self.mgmt_price_var = tk.StringVar()
        price_entry = tk.Entry(
            form_frame, textvariable=self.mgmt_price_var,
            font=("Segoe UI", 12), relief="flat", width=10,
            highlightthickness=2, highlightbackground="#3498db"
        )
        price_entry.grid(row=0, column=3, sticky="ew", ipady=5, padx=(0, 15), pady=5)

        # Stock
        tk.Label(form_frame, text="Stock:", font=("Segoe UI", 11), bg="#ffffff",     fg="#2c3e50").grid(row=0, column=4, sticky="w", padx=(0, 8), pady=5)

        self.mgmt_stock_var = tk.StringVar()
        stock_entry = tk.Entry(
            form_frame, textvariable=self.mgmt_stock_var,
            font=("Segoe UI", 12), relief="flat", width=8,
            highlightthickness=2, highlightbackground="#3498db"
        )
        stock_entry.grid(row=0, column=5, sticky="ew", ipady=5, padx=(0, 15), pady=5)

        # Buttons row
        btn_row = tk.Frame(form_frame, bg="#ffffff")
        btn_row.grid(row=1, column=0, columnspan=6, sticky="ew", pady=(8, 0))

        self.make_button(btn_row, "➕ Add Product", self.add_product, "#27ae60").pack(side="left", padx=(0, 8))
        self.make_button(btn_row, "✏️ Update Product", self.update_product, "#f39c12").pack(side="left", padx=(0, 8))
        self.make_button(btn_row, "🗑️ Delete Product", self.delete_product, "#e74c3c").pack(side="left", padx=(0, 8))
        self.make_button(btn_row, "🔄 Clear Form",     self.clear_mgmt_form, "#95a5a6").pack(side="left", padx=(0, 8))

        # ── Search bar for management ──
        search_mgmt_frame = tk.Frame(self.product_mgmt_tab, bg="#f0f4f8", padx=10)
        search_mgmt_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(180, 0))
        search_mgmt_frame.columnconfigure(1, weight=1)

        tk.Label(search_mgmt_frame, text="🔍 Filter:", font=("Segoe UI", 11), bg="#f0f4f8",fg="#2c3e50").grid(row=0, column=0, sticky="w", padx=(0, 8))

        self.mgmt_search_var = tk.StringVar()
        self.mgmt_search_var.trace("w", lambda *a: self.load_all_products_mgmt())

        mgmt_search_entry = tk.Entry(
            search_mgmt_frame, textvariable=self.mgmt_search_var,
            font=("Segoe UI", 11), relief="flat",
            highlightthickness=2, highlightbackground="#3498db"
        )
        mgmt_search_entry.grid(row=0, column=1, sticky="ew", ipady=5)

        # ── Bottom: Product List ──
        list_frame = tk.Frame(self.product_mgmt_tab, bg="#f0f4f8", padx=10)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        mgmt_columns = ("ID", "Product Name", "Price ($)", "Stock")
        self.mgmt_table = ttk.Treeview(
            list_frame, columns=mgmt_columns,
            show="headings", selectmode="browse"
        )

        for col in mgmt_columns:
            self.mgmt_table.heading(col, text=col)

        self.mgmt_table.column("ID", width=50, minwidth=40, anchor="center")
        self.mgmt_table.column("Product Name", width=250, minwidth=120, anchor="w")
        self.mgmt_table.column("Price ($)", width=100, minwidth=70, anchor="center")
        self.mgmt_table.column("Stock", width=80, minwidth=60, anchor="center")

        mgmt_scroll = ttk.Scrollbar(list_frame, orient="vertical",
                                    command=self.mgmt_table.yview)
        self.mgmt_table.configure(yscrollcommand=mgmt_scroll.set)

        self.mgmt_table.grid(row=0, column=0, sticky="nsew")
        mgmt_scroll.grid(row=0, column=1, sticky="ns")

        # Click to fill form
        self.mgmt_table.bind("<<TreeviewSelect>>", self.on_mgmt_select)

        # Status label
        self.mgmt_status_var = tk.StringVar(value="")
        self.mgmt_status = tk.Label(
            self.product_mgmt_tab,
            textvariable=self.mgmt_status_var,
            font=("Segoe UI", 10, "bold"),
            bg="#f0f4f8", fg="#27ae60"
        )
        self.mgmt_status.grid(row=2, column=0, sticky="w", padx=15, pady=(0, 5))

    # ── Product Management Functions ──

    def load_all_products_mgmt(self):
        """Load products into management table"""
        keyword = self.mgmt_search_var.get().strip()
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

        for row in self.mgmt_table.get_children():
            self.mgmt_table.delete(row)

        for i, row in enumerate(rows):
            pid, name, price, stock = row
            tag = "low" if stock < 5 else ("even" if i % 2 == 0 else "odd")
            self.mgmt_table.insert("", "end",   values=(pid, name, f"${price:.2f}", stock),  tags=(tag,))

        self.mgmt_table.tag_configure("low", foreground="#e74c3c", background="#fdf0f0")
        self.mgmt_table.tag_configure("even", background="#f8f9fa")
        self.mgmt_table.tag_configure("odd", background="#ffffff")

    def on_mgmt_select(self, event=None):
        """Fill form when a product is selected"""
        selected = self.mgmt_table.selection()
        if not selected:
            return

        values = self.mgmt_table.item(selected[0])["values"]
        self.mgmt_name_var.set(values[1])
        self.mgmt_price_var.set(str(values[2]).replace("$", ""))
        self.mgmt_stock_var.set(values[3])

    def add_product(self):
        """Add a new product to database"""
        name = self.mgmt_name_var.get().strip()
        price_str = self.mgmt_price_var.get().strip()
        stock_str = self.mgmt_stock_var.get().strip()

        if not name:
            messagebox.showerror("Error", "Product name is required!")
            return

        try:
            price = float(price_str)
            if price < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter a valid positive price!")
            return

        try:
            stock = int(stock_str)
            if stock < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter a valid positive stock quantity!")
            return

        # Check if product already exists
        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM products WHERE LOWER(name) = LOWER(?)", (name,))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            messagebox.showerror("Error",     f"Product '{name}' already exists!\nUse 'Update' instead.")
            return

        cursor.execute(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
            (name, price, stock)
        )
        conn.commit()
        conn.close()

        self.mgmt_status_var.set(f"✅ '{name}' added successfully!")
        self.clear_mgmt_form()
        self.load_all_products_mgmt()
        self.search_products()  # Refresh counter tab too

        self.root.after(3000, lambda: self.mgmt_status_var.set(""))

    def update_product(self):
        """Update selected product"""
        selected = self.mgmt_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a product to update!")
            return

        product_id = self.mgmt_table.item(selected[0])["values"][0]
        name = self.mgmt_name_var.get().strip()
        price_str = self.mgmt_price_var.get().strip()
        stock_str = self.mgmt_stock_var.get().strip()

        if not name:
            messagebox.showerror("Error", "Product name is required!")
            return

        try:
            price = float(price_str)
            if price < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter a valid positive price!")
            return

        try:
            stock = int(stock_str)
            if stock < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter a valid positive stock quantity!")
            return

        confirm = messagebox.askyesno(
            "Confirm Update",
            f"Update product #{product_id}?\n\n"
            f"Name: {name}\nPrice: ${price:.2f}\nStock: {stock}"
        )

        if not confirm:
            return

        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE products SET name = ?, price = ?, stock = ? WHERE id = ?",
            (name, price, stock, product_id)
        )
        conn.commit()
        conn.close()

        self.mgmt_status_var.set(f"✅ '{name}' updated successfully!")
        self.load_all_products_mgmt()
        self.search_products()

        self.root.after(3000, lambda: self.mgmt_status_var.set(""))

    def delete_product(self):
        """Delete selected product"""
        selected = self.mgmt_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a product to delete!")
            return

        values = self.mgmt_table.item(selected[0])["values"]
        product_id = values[0]
        product_name = values[1]

        confirm = messagebox.askyesno(
            "⚠️ Confirm Delete",
            f"Are you sure you want to DELETE:\n\n"
            f"#{product_id} - {product_name}\n\n"
            f"This action cannot be undone!"
        )

        if not confirm:
            return

        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()

        self.mgmt_status_var.set(f"🗑️ '{product_name}' deleted successfully!")
        self.clear_mgmt_form()
        self.load_all_products_mgmt()
        self.search_products()

        # Also remove from cart if it was there
        if product_id in self.cart:
            del self.cart[product_id]
            self.refresh_cart()

        self.root.after(3000, lambda: self.mgmt_status_var.set(""))

    def clear_mgmt_form(self):
        """Clear the product management form"""
        self.mgmt_name_var.set("")
        self.mgmt_price_var.set("")
        self.mgmt_stock_var.set("")
        # Deselect table
        for item in self.mgmt_table.selection():
            self.mgmt_table.selection_remove(item)

    # ============================================================
    # TAB 3: RECEIPT HISTORY
    # ============================================================

    def build_history_tab(self):
        self.history_tab.columnconfigure(0, weight=1)
        self.history_tab.rowconfigure(1, weight=1)

        # ── Top: Controls ──
        control_frame = tk.Frame(self.history_tab, bg="#f0f4f8", padx=10, pady=8)
        control_frame.grid(row=0, column=0, sticky="ew")
        control_frame.columnconfigure(2, weight=1)

        tk.Label(control_frame, text="📋  Receipt History", font=("Segoe UI", 14, "bold"), bg="#f0f4f8", fg="#2c3e50").grid(row=0, column=0, sticky="w")

        # Filter by date
        tk.Label(control_frame, text="   🔍 Filter:", font=("Segoe UI", 11),bg="#f0f4f8", fg="#2c3e50").grid(row=0, column=1, sticky="w", padx=(20, 5))

        self.history_search_var = tk.StringVar()
        self.history_search_var.trace("w", lambda *a: self.load_receipt_history())

        history_search = tk.Entry(
            control_frame, textvariable=self.history_search_var,
            font=("Segoe UI", 11), relief="flat", width=20,
            highlightthickness=2, highlightbackground="#3498db"
        )
        history_search.grid(row=0, column=2, sticky="w", ipady=5, padx=(0, 10))

        self.make_button(control_frame, "🔄 Refresh", self.load_receipt_history, "#3498db" ).grid(row=0, column=3, sticky="e", padx=(0, 5))

        self.make_button(control_frame, "🗑️ Delete Selected",     self.delete_receipt, "#e74c3c" ).grid(row=0, column=4, sticky="e")

        # ── Main content: Split into receipts list and detail ──
        content_frame = tk.Frame(self.history_tab, bg="#f0f4f8")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # Left: Receipts list
        receipts_frame = tk.LabelFrame(
            content_frame, text="  📄 All Receipts  ",
            font=("Segoe UI", 11, "bold"),
            bg="#ffffff", fg="#2c3e50", padx=8, pady=8
        )
        receipts_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        receipts_frame.columnconfigure(0, weight=1)
        receipts_frame.rowconfigure(0, weight=1)

        hist_columns = ("Receipt #", "Date", "Total", "Payment")
        self.history_table = ttk.Treeview(
            receipts_frame, columns=hist_columns,
            show="headings", selectmode="browse"
        )

        for col in hist_columns:
            self.history_table.heading(col, text=col)

        self.history_table.column("Receipt #", width=100, minwidth=80, anchor="center")
        self.history_table.column("Date", width=150, minwidth=100, anchor="center")
        self.history_table.column("Total", width=80, minwidth=60, anchor="center")
        self.history_table.column("Payment", width=80, minwidth=60, anchor="center")

        hist_scroll = ttk.Scrollbar(receipts_frame, orient="vertical",
                                    command=self.history_table.yview)
        self.history_table.configure(yscrollcommand=hist_scroll.set)

        self.history_table.grid(row=0, column=0, sticky="nsew")
        hist_scroll.grid(row=0, column=1, sticky="ns")

        self.history_table.bind("<<TreeviewSelect>>", self.show_receipt_detail)

        # Right: Receipt detail view
        detail_frame = tk.LabelFrame(
            content_frame, text="  🧾 Receipt Detail  ",
            font=("Segoe UI", 11, "bold"),
            bg="#ffffff", fg="#2c3e50", padx=8, pady=8
        )
        detail_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)

        self.detail_text = tk.Text(
            detail_frame,
            font=("Courier New", 10),
            bg="#fffff8", fg="#2c3e50",
            relief="flat", wrap="none",
            padx=10, pady=10
        )
        self.detail_text.grid(row=0, column=0, sticky="nsew")

        detail_scroll = ttk.Scrollbar(detail_frame, orient="vertical", command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=detail_scroll.set)
        detail_scroll.grid(row=0, column=1, sticky="ns")

        self.detail_text.insert("1.0", "  Select a receipt to view details...")
        self.detail_text.config(state="disabled")

        # Summary bar at bottom
        self.history_summary_var = tk.StringVar(value="")
        tk.Label(
            self.history_tab,
            textvariable=self.history_summary_var,
            font=("Segoe UI", 11, "bold"),
            bg="#ecf0f1", fg="#2c3e50",
            padx=15, pady=8
        ).grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 5))

    # ── History Functions ──

    def load_receipt_history(self):
        """Load all receipts from database"""
        keyword = self.history_search_var.get().strip()

        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()

        if keyword:
            cursor.execute(
                "SELECT receipt_number, date, total, payment_method FROM sales "
                "WHERE receipt_number LIKE ? OR date LIKE ? OR payment_method LIKE ? "
                "ORDER BY id DESC",
                (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
            )
        else:
            cursor.execute(
                "SELECT receipt_number, date, total, payment_method FROM sales "
                "ORDER BY id DESC"
            )

        rows = cursor.fetchall()
        conn.close()

        for row in self.history_table.get_children():
            self.history_table.delete(row)

        total_sales = 0.0
        cash_count = 0
        card_count = 0

        for i, row in enumerate(rows):
            receipt_num, date, total, payment = row
            total_sales += total
            if payment == "cash":
                cash_count += 1
            else:
                card_count += 1

            tag = "even" if i % 2 == 0 else "odd"
            self.history_table.insert("", "end",  values=(receipt_num, date,  f"${total:.2f}", payment.upper()),tags=(tag,))

        self.history_table.tag_configure("even", background="#f8f9fa")
        self.history_table.tag_configure("odd", background="#ffffff")

        # Update summary
        self.history_summary_var.set(
            f"📊  Total Receipts: {len(rows)}  |  "
            f"Total Sales: ${total_sales:.2f}  |  "
            f"💵 Cash: {cash_count}  |  💳 Card: {card_count}"
        )

        # Clear detail
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", "  Select a receipt to view details...")
        self.detail_text.config(state="disabled")

    def show_receipt_detail(self, event=None):
        """Show full receipt detail when selected"""
        selected = self.history_table.selection()
        if not selected:
            return

        values = self.history_table.item(selected[0])["values"]
        receipt_num = values[0]
        date = values[1]
        total = float(str(values[2]).replace("$", ""))
        payment = values[3]

        # Get items for this receipt
        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT product_name, price, quantity, subtotal "
            "FROM sale_items WHERE receipt_number = ?",
            (receipt_num,)
        )
        items = cursor.fetchall()
        conn.close()

        # Build receipt text
        lines = []
        lines.append("=" * 44)
        lines.append("         SHOP COUNTER SYSTEM")
        lines.append("        Your Friendly Local Store")
        lines.append("=" * 44)
        lines.append(f" Receipt #: {receipt_num}")
        lines.append(f" Date:      {date}")
        lines.append("-" * 44)
        lines.append(f" {'ITEM':<18} {'QTY':>4} {'PRICE':>8} {'TOTAL':>8}")
        lines.append("-" * 44)

        items_subtotal = 0.0
        for item in items:
            name, price, qty, sub = item
            items_subtotal += sub
            name_short = name[:18]
            lines.append(
                f" {name_short:<18} {qty:>4} "
                f"${price:>7.2f} ${sub:>7.2f}"
            )

        if not items:
            lines.append("  (No item details available)")
            items_subtotal = total / 1.10

        tax = items_subtotal * 0.10

        lines.append("-" * 44)
        lines.append(f"{'Subtotal:':>34} ${items_subtotal:>7.2f}")
        lines.append(f"{'Tax (10%):':>34} ${tax:>7.2f}")
        lines.append("=" * 44)
        lines.append(f"{'TOTAL:':>34} ${total:>7.2f}")
        lines.append("=" * 44)
        lines.append(f" Payment: {payment}")
        lines.append("-" * 44)
        lines.append("     Thank you for shopping with us!")
        lines.append("         Please come again! 😊")
        lines.append("=" * 44)

        receipt_str = "\n".join(lines)

        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", receipt_str)
        self.detail_text.config(state="disabled")

    def delete_receipt(self):
        """Delete a receipt from history"""
        selected = self.history_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a receipt to delete!")
            return

        values = self.history_table.item(selected[0])["values"]
        receipt_num = values[0]

        confirm = messagebox.askyesno(
            "⚠️ Delete Receipt",
            f"Delete receipt {receipt_num}?\n\n"
            f"This will permanently remove it from history."
        )

        if not confirm:
            return

        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sales WHERE receipt_number = ?", (receipt_num,))
        cursor.execute("DELETE FROM sale_items WHERE receipt_number = ?", (receipt_num,))
        conn.commit()
        conn.close()

        self.load_receipt_history()
        messagebox.showinfo("Deleted", f"Receipt {receipt_num} deleted successfully!")

    # ============================================================
    # COUNTER TAB FUNCTIONS (same as before)
    # ============================================================

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

        for i, row in enumerate(rows):
            pid, name, price, stock = row
            tag = "low_stock" if stock < 5 else ("even" if i % 2 == 0 else "odd")
            self.product_table.insert(
                "", "end",
                values=(pid, name, f"${price:.2f}", stock),
                tags=(tag,)
            )

        self.product_table.tag_configure("low_stock", foreground="#e74c3c", background="#fdf0f0")
        self.product_table.tag_configure("even", background="#f8f9fa")
        self.product_table.tag_configure("odd", background="#ffffff")

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

    def toggle_cash_input(self):
        if self.payment_var.get() == "cash":
            self.cash_entry.config(state="normal")
        else:
            self.cash_entry.config(state="disabled")
            self.cash_given_var.set("")

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
                messagebox.showerror("Invalid Amount","Enter the cash amount given by customer.")
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
        self.show_receipt_popup(receipt_number, subtotal, tax, total,
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
            (receipt_number, total, payment_method, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
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

    def show_receipt_popup(self, receipt_number, subtotal, tax, total,  payment_method, cash_given, change):
        win = tk.Toplevel(self.root)
        win.title("🧾 Receipt")
        win.configure(bg="white")
        win.minsize(350, 400)

        w = max(380, min(500, int(self.root.winfo_width() * 0.4)))
        h = max(500, min(700, int(self.root.winfo_height() * 0.85)))
        win.geometry(f"{w}x{h}")

        win.columnconfigure(0, weight=1)
        win.rowconfigure(0, weight=1)

        frame = tk.Frame(win, bg="white", padx=15, pady=15)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

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
                f"${data['price'] * data['quantity']:>7.2f}"
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
            frame, font=("Courier New", 10),
            bg="#fffff8", fg="#2c3e50",
            relief="flat", wrap="none", padx=10, pady=10
        )
        text_widget.insert("1.0", receipt_str)
        text_widget.config(state="disabled")
        text_widget.grid(row=0, column=0, sticky="nsew")

        r_scroll = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=r_scroll.set)
        r_scroll.grid(row=0, column=1, sticky="ns")

        close_btn = tk.Button(
            win, text="✅  Close Receipt",
            command=win.destroy,
            font=("Segoe UI", 12, "bold"),
            bg="#2ecc71", fg="white",
            activebackground="#27ae60",
            relief="flat", cursor="hand2", pady=8
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
