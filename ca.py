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

    # Create products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)

    # Create sales table to save receipts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_number TEXT,
            total REAL,
            payment_method TEXT,
            date TEXT
        )
    """)

    # Add sample products if table is empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ("Apple",        0.50,  100),
            ("Banana",       0.30,  150),
            ("Milk (1L)",    1.20,   50),
            ("Bread",        2.50,   40),
            ("Eggs (12)",    3.00,   60),
            ("Butter",       2.00,   30),
            ("Cheese",       4.50,   25),
            ("Orange Juice", 3.50,   35),
            ("Coffee",       8.00,   20),
            ("Tea Bags",     5.00,   45),
            ("Sugar (1kg)",  1.80,   55),
            ("Rice (2kg)",   4.00,   40),
            ("Pasta",        1.50,   70),
            ("Tomato Sauce", 2.20,   60),
            ("Water (1.5L)", 0.80,  200),
        ]
        cursor.executemany(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
            sample_products
        )

    conn.commit()
    conn.close()

# ============================================================
# MAIN APPLICATION CLASS
# ============================================================

class ShopCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🛒 Shop Counter System")
        self.root.geometry("1100x700")
        self.root.configure(bg="#f0f4f8")

        # Cart stores items: { product_id: {name, price, quantity} }
        self.cart = {}
        self.receipt_counter = self.get_last_receipt_number()

        # Build the UI
        self.build_ui()

        # Load all products at start
        self.search_products()

    # --------------------------------------------------------
    # RECEIPT NUMBER HELPER
    # --------------------------------------------------------

    def get_last_receipt_number(self):
        """Get last receipt number from DB to continue counting"""
        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sales")
        count = cursor.fetchone()[0]
        conn.close()
        return count + 1

    # --------------------------------------------------------
    # UI BUILDER
    # --------------------------------------------------------

    def build_ui(self):
        """Build the entire user interface"""

        # ── Title Bar ──────────────────────────────────────
        title_frame = tk.Frame(self.root, bg="#2c3e50", pady=10)
        title_frame.pack(fill="x")

        tk.Label(
            title_frame,
            text="🛒  SHOP COUNTER SYSTEM",
            font=("Arial", 22, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack()

        tk.Label(
            title_frame,
            text=f"📅  {datetime.now().strftime('%A, %d %B %Y')}",
            font=("Arial", 11),
            bg="#2c3e50",
            fg="#bdc3c7"
        ).pack()

        # ── Main Content Frame ──────────────────────────────
        main_frame = tk.Frame(self.root, bg="#f0f4f8")
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Left Panel  → Product Search
        left_panel = tk.Frame(main_frame, bg="#f0f4f8")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Right Panel → Receipt / Cart
        right_panel = tk.Frame(main_frame, bg="#f0f4f8")
        right_panel.pack(side="right", fill="both", expand=True, padx=(8, 0))

        self.build_search_panel(left_panel)
        self.build_receipt_panel(right_panel)

    # --------------------------------------------------------
    # LEFT PANEL – Product Search
    # --------------------------------------------------------

    def build_search_panel(self, parent):
        """Build the product search section"""

        # Section title
        tk.Label(
            parent,
            text="🔍  Search Products",
            font=("Arial", 14, "bold"),
            bg="#f0f4f8",
            fg="#2c3e50"
        ).pack(anchor="w", pady=(0, 5))

        # Search bar frame
        search_frame = tk.Frame(parent, bg="#f0f4f8")
        search_frame.pack(fill="x", pady=(0, 8))

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.search_products())  # live search

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 13),
            relief="flat",
            bd=0,
            highlightthickness=2,
            highlightbackground="#3498db",
            highlightcolor="#3498db"
        )
        search_entry.pack(side="left", fill="x", expand=True,
                          ipady=8, padx=(0, 8))
        search_entry.focus()

        tk.Button(
            search_frame,
            text="Search",
            command=self.search_products,
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            relief="flat",
            padx=15,
            cursor="hand2"
        ).pack(side="left")

        # Product list with scrollbar
        list_frame = tk.Frame(parent, bg="#f0f4f8")
        list_frame.pack(fill="both", expand=True)

        columns = ("ID", "Product Name", "Price ($)", "Stock")
        self.product_table = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=15
        )

        # Column settings
        col_widths = {"ID": 50, "Product Name": 220, "Price ($)": 90, "Stock": 80}
        for col in columns:
            self.product_table.heading(col, text=col)
            self.product_table.column(col, width=col_widths[col], anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.product_table.yview
        )
        self.product_table.configure(yscrollcommand=scrollbar.set)

        self.product_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Double-click to add item
        self.product_table.bind("<Double-1>", lambda e: self.add_to_cart())

        # Quantity + Add Button row
        add_frame = tk.Frame(parent, bg="#f0f4f8", pady=8)
        add_frame.pack(fill="x")

        tk.Label(
            add_frame,
            text="Qty:",
            font=("Arial", 12),
            bg="#f0f4f8"
        ).pack(side="left")

        self.qty_var = tk.IntVar(value=1)
        qty_spinbox = tk.Spinbox(
            add_frame,
            from_=1,
            to=100,
            textvariable=self.qty_var,
            font=("Arial", 12),
            width=5,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#3498db"
        )
        qty_spinbox.pack(side="left", padx=8)

        tk.Button(
            add_frame,
            text="➕  Add to Cart",
            command=self.add_to_cart,
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            relief="flat",
            padx=20,
            pady=5,
            cursor="hand2"
        ).pack(side="left")

        # Hint label
        tk.Label(
            parent,
            text="💡 Tip: Double-click a product to add it quickly",
            font=("Arial", 9),
            bg="#f0f4f8",
            fg="#95a5a6"
        ).pack(anchor="w")

    # --------------------------------------------------------
    # RIGHT PANEL – Receipt / Cart
    # --------------------------------------------------------

    def build_receipt_panel(self, parent):
        """Build the receipt/cart section"""

        tk.Label(
            parent,
            text="🧾  Receipt",
            font=("Arial", 14, "bold"),
            bg="#f0f4f8",
            fg="#2c3e50"
        ).pack(anchor="w", pady=(0, 5))

        # Cart table
        cart_frame = tk.Frame(parent, bg="#f0f4f8")
        cart_frame.pack(fill="both", expand=True)

        cart_columns = ("Product", "Price", "Qty", "Subtotal")
        self.cart_table = ttk.Treeview(
            cart_frame,
            columns=cart_columns,
            show="headings",
            height=12
        )

        cart_col_widths = {"Product": 180, "Price": 80, "Qty": 60, "Subtotal": 90}
        for col in cart_columns:
            self.cart_table.heading(col, text=col)
            self.cart_table.column(col, width=cart_col_widths[col], anchor="center")

        cart_scroll = ttk.Scrollbar(
            cart_frame,
            orient="vertical",
            command=self.cart_table.yview
        )
        self.cart_table.configure(yscrollcommand=cart_scroll.set)
        self.cart_table.pack(side="left", fill="both", expand=True)
        cart_scroll.pack(side="right", fill="y")

        # Cart action buttons
        btn_frame = tk.Frame(parent, bg="#f0f4f8", pady=5)
        btn_frame.pack(fill="x")

        tk.Button(
            btn_frame,
            text="➖  Remove Item",
            command=self.remove_from_cart,
            font=("Arial", 10, "bold"),
            bg="#e74c3c",
            fg="white",
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2"
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_frame,
            text="🗑️  Clear Cart",
            command=self.clear_cart,
            font=("Arial", 10, "bold"),
            bg="#e67e22",
            fg="white",
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2"
        ).pack(side="left")

        # ── Totals Section ──────────────────────────────────
        totals_frame = tk.Frame(parent, bg="#ecf0f1", relief="flat", bd=1)
        totals_frame.pack(fill="x", pady=8)

        def total_row(label, var, large=False):
            row = tk.Frame(totals_frame, bg="#ecf0f1")
            row.pack(fill="x", padx=10, pady=3)
            font_size = 14 if large else 11
            tk.Label(
                row, text=label,
                font=("Arial", font_size, "bold" if large else "normal"),
                bg="#ecf0f1", fg="#2c3e50"
            ).pack(side="left")
            tk.Label(
                row, textvariable=var,
                font=("Arial", font_size, "bold"),
                bg="#ecf0f1",
                fg="#e74c3c" if large else "#2c3e50"
            ).pack(side="right")

        self.subtotal_var = tk.StringVar(value="$0.00")
        self.tax_var      = tk.StringVar(value="$0.00")
        self.total_var    = tk.StringVar(value="$0.00")

        total_row("Subtotal:",    self.subtotal_var)
        total_row("Tax (10%):",   self.tax_var)
        ttk.Separator(totals_frame, orient="horizontal").pack(fill="x", padx=10, pady=2)
        total_row("TOTAL:",       self.total_var, large=True)

        # ── Payment Section ─────────────────────────────────
        pay_frame = tk.LabelFrame(
            parent,
            text="  💳  Payment Method  ",
            font=("Arial", 11, "bold"),
            bg="#f0f4f8",
            fg="#2c3e50",
            pady=10,
            padx=10
        )
        pay_frame.pack(fill="x", pady=(5, 8))

        self.payment_var = tk.StringVar(value="cash")

        # Cash option
        cash_frame = tk.Frame(pay_frame, bg="#f0f4f8")
        cash_frame.pack(fill="x", pady=4)

        tk.Radiobutton(
            cash_frame,
            text="💵  Cash Payment",
            variable=self.payment_var,
            value="cash",
            font=("Arial", 12),
            bg="#f0f4f8",
            fg="#2c3e50",
            command=self.toggle_cash_input
        ).pack(side="left")

        self.cash_given_var = tk.StringVar()
        self.cash_entry = tk.Entry(
            cash_frame,
            textvariable=self.cash_given_var,
            font=("Arial", 12),
            width=10,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#3498db"
        )
        self.cash_entry.pack(side="left", padx=(15, 5))
        tk.Label(
            cash_frame,
            text="Amount given",
            font=("Arial", 10),
            bg="#f0f4f8",
            fg="#7f8c8d"
        ).pack(side="left")

        # Card option
        tk.Radiobutton(
            pay_frame,
            text="💳  Card Payment (Debit / Credit)",
            variable=self.payment_var,
            value="card",
            font=("Arial", 12),
            bg="#f0f4f8",
            fg="#2c3e50",
            command=self.toggle_cash_input
        ).pack(anchor="w", pady=4)

        # Checkout button
        tk.Button(
            parent,
            text="✅   CHECKOUT",
            command=self.checkout,
            font=("Arial", 15, "bold"),
            bg="#2ecc71",
            fg="white",
            relief="flat",
            pady=10,
            cursor="hand2"
        ).pack(fill="x")

    # --------------------------------------------------------
    # PRODUCT SEARCH
    # --------------------------------------------------------

    def search_products(self, *args):
        """Search products in database and display results"""
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

        # Clear old results
        for row in self.product_table.get_children():
            self.product_table.delete(row)

        # Insert new results
        for row in rows:
            product_id, name, price, stock = row
            tag = "low_stock" if stock < 5 else ""
            self.product_table.insert(
                "", "end",
                values=(product_id, name, f"${price:.2f}", stock),
                tags=(tag,)
            )

        # Highlight low-stock items in red
        self.product_table.tag_configure("low_stock", foreground="#e74c3c")

    # --------------------------------------------------------
    # CART OPERATIONS
    # --------------------------------------------------------

    def add_to_cart(self):
        """Add selected product to cart"""
        selected = self.product_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product first!")
            return

        # Get product data from the selected row
        values = self.product_table.item(selected[0])["values"]
        product_id = int(values[0])
        name       = values[1]
        price      = float(str(values[2]).replace("$", ""))
        stock      = int(values[3])
        qty        = self.qty_var.get()

        # Check stock
        already_in_cart = self.cart.get(product_id, {}).get("quantity", 0)
        if already_in_cart + qty > stock:
            messagebox.showerror(
                "Out of Stock",
                f"Only {stock} unit(s) of '{name}' available!\n"
                f"You already have {already_in_cart} in the cart."
            )
            return

        # Add or update cart
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
        """Remove selected item from cart"""
        selected = self.cart_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an item to remove!")
            return

        values = self.cart_table.item(selected[0])["values"]
        # Find the product_id matching this cart row
        product_name = values[0]
        for pid, data in list(self.cart.items()):
            if data["name"] == product_name:
                del self.cart[pid]
                break

        self.refresh_cart()

    def clear_cart(self):
        """Clear all items from cart"""
        if not self.cart:
            return
        confirm = messagebox.askyesno("Clear Cart", "Are you sure you want to clear the cart?")
        if confirm:
            self.cart.clear()
            self.refresh_cart()

    def refresh_cart(self):
        """Refresh the cart display and recalculate totals"""
        # Clear cart table
        for row in self.cart_table.get_children():
            self.cart_table.delete(row)

        subtotal = 0.0

        for product_id, data in self.cart.items():
            item_subtotal = data["price"] * data["quantity"]
            subtotal += item_subtotal
            self.cart_table.insert("", "end", values=(
                data["name"],
                f"${data['price']:.2f}",
                data["quantity"],
                f"${item_subtotal:.2f}"
            ))

        tax   = subtotal * 0.10
        total = subtotal + tax

        self.subtotal_var.set(f"${subtotal:.2f}")
        self.tax_var.set(f"${tax:.2f}")
        self.total_var.set(f"${total:.2f}")

    # --------------------------------------------------------
    # PAYMENT TOGGLE
    # --------------------------------------------------------

    def toggle_cash_input(self):
        """Enable cash entry only when cash payment is selected"""
        if self.payment_var.get() == "cash":
            self.cash_entry.config(state="normal")
        else:
            self.cash_entry.config(state="disabled")
            self.cash_given_var.set("")

    # --------------------------------------------------------
    # CHECKOUT
    # --------------------------------------------------------

    def checkout(self):
        """Process the checkout"""
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Please add items to the cart first!")
            return

        # Calculate totals
        subtotal = sum(d["price"] * d["quantity"] for d in self.cart.values())
        tax      = subtotal * 0.10
        total    = subtotal + tax

        payment_method = self.payment_var.get()
        change = 0.0

        # Validate cash payment
        if payment_method == "cash":
            try:
                cash_given = float(self.cash_given_var.get())
            except ValueError:
                messagebox.showerror(
                    "Invalid Amount",
                    "Please enter the cash amount given by the customer."
                )
                return

            if cash_given < total:
                messagebox.showerror(
                    "Insufficient Cash",
                    f"Total is ${total:.2f}\n"
                    f"Cash given is ${cash_given:.2f}\n"
                    f"Need ${total - cash_given:.2f} more."
                )
                return

            change = cash_given - total

        # Save sale to database
        receipt_number = f"RCP-{self.receipt_counter:05d}"
        self.save_sale(receipt_number, total, payment_method)

        # Update stock in database
        self.update_stock()

        # Show receipt window
        self.show_receipt(receipt_number, subtotal, tax, total,
                          payment_method, change)

        # Reset for next customer
        self.cart.clear()
        self.refresh_cart()
        self.cash_given_var.set("")
        self.receipt_counter += 1

    def save_sale(self, receipt_number, total, payment_method):
        """Save sale record to the database"""
        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sales (receipt_number, total, payment_method, date) "
            "VALUES (?, ?, ?, ?)",
            (receipt_number, total, payment_method,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        conn.close()

    def update_stock(self):
        """Reduce stock for sold items"""
        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        for product_id, data in self.cart.items():
            cursor.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (data["quantity"], product_id)
            )
        conn.commit()
        conn.close()
        self.search_products()   # Refresh product list to show updated stock

    # --------------------------------------------------------
    # RECEIPT WINDOW
    # --------------------------------------------------------

    def show_receipt(self, receipt_number, subtotal, tax, total,
                     payment_method, change):
        """Show a receipt popup window"""
        win = tk.Toplevel(self.root)
        win.title("🧾 Receipt")
        win.geometry("420x600")
        win.configure(bg="white")
        win.resizable(False, False)

        # Receipt content as text
        receipt_text = []
        receipt_text.append("=" * 42)
        receipt_text.append("          SHOP COUNTER SYSTEM")
        receipt_text.append("         Your Friendly Local Store")
        receipt_text.append("=" * 42)
        receipt_text.append(f"Receipt #: {receipt_number}")
        receipt_text.append(f"Date:      {datetime.now().strftime('%d/%m/%Y  %H:%M:%S')}")
        receipt_text.append("-" * 42)
        receipt_text.append(f"{'ITEM':<20} {'QTY':>4} {'PRICE':>8} {'TOTAL':>8}")
        receipt_text.append("-" * 42)

        for data in self.cart.values():
            line = (f"{data['name']:<20} "
                    f"{data['quantity']:>4} "
                    f"${data['price']:>7.2f} "
                    f"${data['price']*data['quantity']:>7.2f}")
            receipt_text.append(line)

        receipt_text.append("-" * 42)
        receipt_text.append(f"{'Subtotal:':>33} ${subtotal:>7.2f}")
        receipt_text.append(f"{'Tax (10%):':>33} ${tax:>7.2f}")
        receipt_text.append("=" * 42)
        receipt_text.append(f"{'TOTAL:':>33} ${total:>7.2f}")
        receipt_text.append("=" * 42)
        receipt_text.append(f"Payment:   {payment_method.upper()}")

        if payment_method == "cash":
            try:
                cash_given = float(self.cash_given_var.get())
            except Exception:
                cash_given = total
            receipt_text.append(f"Cash Given: ${cash_given:.2f}")
            receipt_text.append(f"Change:     ${change:.2f}")

        receipt_text.append("-" * 42)
        receipt_text.append("      Thank you for shopping with us!")
        receipt_text.append("          Please come again! 😊")
        receipt_text.append("=" * 42)

        full_receipt = "\n".join(receipt_text)

        # Display receipt in a Text widget
        frame = tk.Frame(win, bg="white", padx=15, pady=15)
        frame.pack(fill="both", expand=True)

        text_box = tk.Text(
            frame,
            font=("Courier", 10),
            bg="white",
            relief="flat",
            state="normal",
            wrap="none"
        )
        text_box.insert("1.0", full_receipt)
        text_box.config(state="disabled")
        text_box.pack(fill="both", expand=True)

        # Close button
        tk.Button(
            win,
            text="✅  Close Receipt",
            command=win.destroy,
            font=("Arial", 12, "bold"),
            bg="#2ecc71",
            fg="white",
            relief="flat",
            pady=8,
            cursor="hand2"
        ).pack(fill="x", padx=15, pady=10)

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    setup_database()                  # Ensure DB exists and is seeded
    root = tk.Tk()
    app = ShopCounterApp(root)
    root.mainloop()
