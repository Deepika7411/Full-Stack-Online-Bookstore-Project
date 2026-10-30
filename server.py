"""
Online Bookstore - Backend Server (Spring REST API Compatible)
Provides identical REST API endpoints as the Spring Boot Web MVC backend:
  - GET  /books & GET /api/books
  - GET  /books/<id> & GET /api/books/<id>
  - POST /cart & POST /api/cart
  - GET  /cart & GET /api/cart
  - DELETE /cart/<id> & DELETE /api/cart/<id>
  - POST /checkout & POST /api/checkout
  - POST /auth/login
  - POST /auth/signup
  - POST /books/<id>/reviews
Serves static frontend files from src/main/resources/static
"""

import http.server
import socketserver
import json
import sqlite3
import os
import re
import uuid

PORT = 8080
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "main", "resources", "static")
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bookstore.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        price REAL NOT NULL,
        description TEXT,
        category TEXT,
        image_url TEXT,
        rating REAL DEFAULT 4.5,
        stock INTEGER DEFAULT 50
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        reviewer_name TEXT NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (book_id) REFERENCES books(id)
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS cart_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cart_id TEXT NOT NULL,
        book_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (book_id) REFERENCES books(id)
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT NOT NULL UNIQUE,
        customer_name TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        shipping_address TEXT NOT NULL,
        total_amount REAL NOT NULL,
        payment_method TEXT DEFAULT 'Credit Card',
        status TEXT DEFAULT 'CONFIRMED',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        book_title TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id)
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        full_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    # Check if books exist
    c.execute("SELECT COUNT(*) FROM books")
    if c.fetchone()[0] == 0:
        books_data = [
            ("The Pragmatic Programmer", "David Thomas, Andrew Hunt", 44.99,
             "Your journey to mastery. One of the most significant books in computer science, filled with classic and modern software engineering philosophies.",
             "Technology", "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=80", 4.9, 25),
            ("Clean Code: A Handbook of Agile Software Craftsmanship", "Robert C. Martin", 39.50,
             "Even bad code can function. But if code isn't clean, it can bring a development organization to its knees. Learn how to write clean, robust code in Java and beyond.",
             "Technology", "https://images.unsplash.com/photo-1532012164546-f432f2e3777a?w=600&auto=format&fit=crop&q=80", 4.8, 30),
            ("Atomic Habits", "James Clear", 19.99,
             "An easy and proven way to build good habits and break bad ones. Tiny changes, remarkable results for productivity and life mastery.",
             "Self-Help", "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600&auto=format&fit=crop&q=80", 4.9, 60),
            ("Designing Data-Intensive Applications", "Martin Kleppmann", 52.00,
             "The big ideas behind reliable, scalable, and maintainable systems. Key principles of databases, distributed systems, and real-time streaming architectures.",
             "Technology", "https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=600&auto=format&fit=crop&q=80", 4.9, 18),
            ("Spring Boot: Up and Running", "Mark Heckler", 42.75,
             "Building cloud-native Java and Kotlin applications. Comprehensive guide for developers wanting to master Spring Web MVC, Spring Data, and microservices.",
             "Technology", "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=600&auto=format&fit=crop&q=80", 4.7, 22),
            ("The Psychology of Money", "Morgan Housel", 21.50,
             "Timeless lessons on wealth, greed, and happiness doing well with money isn't necessarily about what you know. It's about how you behave.",
             "Finance", "https://images.unsplash.com/photo-1554774853-aae0a22c8aa4?w=600&auto=format&fit=crop&q=80", 4.8, 45),
            ("To Kill a Mockingbird", "Harper Lee", 14.99,
             "A gripping, heart-wrenching, and wholly remarkable tale of coming-of-age in a South poisoned by virulent prejudice.",
             "Fiction", "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=600&auto=format&fit=crop&q=80", 4.8, 40),
            ("Deep Work", "Cal Newport", 23.95,
             "Rules for focused success in a distracted world. Deep work is the ability to focus without distraction on a cognitively demanding task.",
             "Productivity", "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=600&auto=format&fit=crop&q=80", 4.7, 35)
        ]
        c.executemany("INSERT INTO books (title, author, price, description, category, image_url, rating, stock) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", books_data)

        # Preload reviews
        reviews_data = [
            (1, "Alice Smith", 5, "A must-read classic for every developer! Completely transformed how I think about refactoring and pragmatic solutions."),
            (1, "Bob Johnson", 5, "Filled with pragmatic wisdom. The tips on debugging and automation saved me countless hours."),
            (2, "Charlie Davis", 5, "Clean code standards are essential in our team now. Excellent examples and clear reasoning."),
            (3, "Emily Watson", 5, "Atomic Habits made building routines effortless. Highly recommended for students and professionals alike."),
            (4, "Michael Lee", 5, "The bible of distributed systems and modern database architectures. Clear, thorough, and insightful."),
            (5, "David Kim", 5, "Clear practical walk-through of Spring Boot and REST controller patterns. Best guide available.")
        ]
        c.executemany("INSERT INTO reviews (book_id, reviewer_name, rating, comment) VALUES (?, ?, ?, ?)", reviews_data)

        # Preload demo user
        c.execute("INSERT INTO users (username, email, password, full_name) VALUES (?, ?, ?, ?)",
                  ("reader1", "reader@bookstore.com", "password123", "John Reader"))

    conn.commit()
    conn.close()

class BookstoreHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Cart-Id')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def parse_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            raw = self.rfile.read(content_length).decode('utf-8')
            try:
                return json.loads(raw)
            except Exception:
                return {}
        return {}

    def get_cart_id(self):
        cart_id = self.headers.get('X-Cart-Id')
        if not cart_id:
            # Check query param
            if 'cartId=' in self.path:
                match = re.search(r'cartId=([^&]+)', self.path)
                if match:
                    cart_id = match.group(1)
        return cart_id or 'default-cart'

    def do_GET(self):
        path = self.path.split('?')[0]
        query = ''
        if '?' in self.path:
            query = self.path.split('?')[1]

        # GET /books & GET /api/books
        if path in ['/books', '/api/books']:
            search = ''
            if 'search=' in query:
                m = re.search(r'search=([^&]+)', query)
                if m:
                    from urllib.parse import unquote
                    search = unquote(m.group(1)).lower()

            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            if search:
                pattern = f"%{search}%"
                c.execute("SELECT id, title, author, price, description, category, image_url, rating, stock FROM books WHERE LOWER(title) LIKE ? OR LOWER(author) LIKE ? OR LOWER(category) LIKE ? ORDER BY id ASC", (pattern, pattern, pattern))
            else:
                c.execute("SELECT id, title, author, price, description, category, image_url, rating, stock FROM books ORDER BY id ASC")
            
            rows = c.fetchall()
            books = []
            for r in rows:
                books.append({
                    "id": r[0], "title": r[1], "author": r[2], "price": r[3],
                    "description": r[4], "category": r[5], "imageUrl": r[6],
                    "rating": r[7], "stock": r[8]
                })
            conn.close()
            return self.send_json(books)

        # GET /books/:id & GET /api/books/:id
        m = re.match(r'^(?:/api)?/books/(\d+)$', path)
        if m:
            book_id = int(m.group(1))
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT id, title, author, price, description, category, image_url, rating, stock FROM books WHERE id = ?", (book_id,))
            r = c.fetchone()
            if not r:
                conn.close()
                return self.send_json({"error": "Book not found"}, status=404)

            # fetch reviews
            c.execute("SELECT id, book_id, reviewer_name, rating, comment, created_at FROM reviews WHERE book_id = ? ORDER BY id DESC", (book_id,))
            rev_rows = c.fetchall()
            reviews = []
            for rev in rev_rows:
                reviews.append({
                    "id": rev[0], "bookId": rev[1], "reviewerName": rev[2],
                    "rating": rev[3], "comment": rev[4], "createdAt": rev[5]
                })

            book = {
                "id": r[0], "title": r[1], "author": r[2], "price": r[3],
                "description": r[4], "category": r[5], "imageUrl": r[6],
                "rating": r[7], "stock": r[8], "reviews": reviews
            }
            conn.close()
            return self.send_json(book)

        # GET /cart & GET /api/cart
        if path in ['/cart', '/api/cart']:
            cart_id = self.get_cart_id()
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("""
                SELECT c.id, c.cart_id, c.book_id, c.quantity, b.title, b.author, b.price, b.image_url
                FROM cart_items c
                JOIN books b ON c.book_id = b.id
                WHERE c.cart_id = ?
            """, (cart_id,))
            rows = c.fetchall()
            items = []
            total_price = 0.0
            total_items = 0
            for r in rows:
                subtotal = round(r[3] * r[6], 2)
                total_price += subtotal
                total_items += r[3]
                items.append({
                    "id": r[0], "cartId": r[1], "bookId": r[2], "quantity": r[3],
                    "bookTitle": r[4], "bookAuthor": r[5], "bookPrice": r[6],
                    "bookImageUrl": r[7], "subtotal": subtotal
                })
            conn.close()
            return self.send_json({
                "cartId": cart_id,
                "items": items,
                "totalPrice": round(total_price, 2),
                "totalItems": total_items
            })

        # Static file fallback
        super().do_GET()

    def do_POST(self):
        path = self.path.split('?')[0]
        body = self.parse_body()

        # POST /cart & POST /api/cart
        if path in ['/cart', '/api/cart']:
            cart_id = body.get('cartId') or self.get_cart_id()
            book_id = body.get('bookId')
            quantity = int(body.get('quantity', 1))

            if not book_id:
                return self.send_json({"error": "bookId required"}, status=400)

            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT id, quantity FROM cart_items WHERE cart_id = ? AND book_id = ?", (cart_id, book_id))
            existing = c.fetchone()
            if existing:
                c.execute("UPDATE cart_items SET quantity = quantity + ? WHERE id = ?", (quantity, existing[0]))
            else:
                c.execute("INSERT INTO cart_items (cart_id, book_id, quantity) VALUES (?, ?, ?)", (cart_id, book_id, quantity))
            conn.commit()

            # Return updated cart
            c.execute("""
                SELECT c.id, c.cart_id, c.book_id, c.quantity, b.title, b.author, b.price, b.image_url
                FROM cart_items c
                JOIN books b ON c.book_id = b.id
                WHERE c.cart_id = ?
            """, (cart_id,))
            rows = c.fetchall()
            items = []
            total_price = 0.0
            total_items = 0
            for r in rows:
                subtotal = round(r[3] * r[6], 2)
                total_price += subtotal
                total_items += r[3]
                items.append({
                    "id": r[0], "cartId": r[1], "bookId": r[2], "quantity": r[3],
                    "bookTitle": r[4], "bookAuthor": r[5], "bookPrice": r[6],
                    "bookImageUrl": r[7], "subtotal": subtotal
                })
            conn.close()
            return self.send_json({
                "cartId": cart_id,
                "items": items,
                "totalPrice": round(total_price, 2),
                "totalItems": total_items
            })

        # POST /checkout & POST /api/checkout
        if path in ['/checkout', '/api/checkout']:
            cart_id = body.get('cartId') or self.get_cart_id()
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("""
                SELECT c.book_id, c.quantity, b.title, b.price
                FROM cart_items c
                JOIN books b ON c.book_id = b.id
                WHERE c.cart_id = ?
            """, (cart_id,))
            cart_rows = c.fetchall()
            if not cart_rows:
                conn.close()
                return self.send_json({"success": False, "message": "Cart is empty"}, status=400)

            total_amount = sum(r[1] * r[3] for r in cart_rows)
            order_number = "ORD-" + str(uuid.uuid4())[:8].upper()

            c.execute("""
                INSERT INTO orders (order_number, customer_name, customer_email, shipping_address, total_amount, payment_method, status)
                VALUES (?, ?, ?, ?, ?, ?, 'CONFIRMED')
            """, (
                order_number,
                body.get('customerName', 'Valued Customer'),
                body.get('customerEmail', 'customer@example.com'),
                body.get('shippingAddress', 'Default Address'),
                round(total_amount, 2),
                body.get('paymentMethod', 'Credit Card')
            ))
            order_id = c.lastrowid

            for item in cart_rows:
                c.execute("INSERT INTO order_items (order_id, book_id, book_title, quantity, unit_price) VALUES (?, ?, ?, ?, ?)",
                          (order_id, item[0], item[2], item[1], item[3]))

            # Clear cart
            c.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart_id,))
            conn.commit()
            conn.close()

            order_data = {
                "id": order_id,
                "orderNumber": order_number,
                "customerName": body.get('customerName', 'Valued Customer'),
                "customerEmail": body.get('customerEmail', 'customer@example.com'),
                "shippingAddress": body.get('shippingAddress', 'Default Address'),
                "totalAmount": round(total_amount, 2),
                "status": "CONFIRMED"
            }
            return self.send_json({
                "success": True,
                "message": f"Order placed successfully! Order ID: {order_number}",
                "order": order_data
            })

        # POST /books/:id/reviews
        m = re.match(r'^(?:/api)?/books/(\d+)/reviews$', path)
        if m:
            book_id = int(m.group(1))
            name = body.get('reviewerName', 'Anonymous')
            rating = int(body.get('rating', 5))
            comment = body.get('comment', '')

            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO reviews (book_id, reviewer_name, rating, comment) VALUES (?, ?, ?, ?)",
                      (book_id, name, rating, comment))
            conn.commit()
            conn.close()
            return self.send_json({"message": "Review added successfully"}, status=201)

        # POST /auth/login
        if path == '/auth/login':
            username = body.get('username')
            password = body.get('password')
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT id, username, email, full_name FROM users WHERE username = ? AND password = ?", (username, password))
            row = c.fetchone()
            conn.close()
            if row:
                return self.send_json({
                    "success": True,
                    "message": "Login successful",
                    "user": {"id": row[0], "username": row[1], "email": row[2], "fullName": row[3]}
                })
            return self.send_json({"success": False, "message": "Invalid username or password"}, status=401)

        # POST /auth/signup
        if path == '/auth/signup':
            username = body.get('username')
            email = body.get('email')
            password = body.get('password')
            full_name = body.get('fullName', username)

            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (username, email, password, full_name) VALUES (?, ?, ?, ?)",
                          (username, email, password, full_name))
                conn.commit()
                user_id = c.lastrowid
                conn.close()
                return self.send_json({
                    "success": True,
                    "message": "User registered successfully",
                    "user": {"id": user_id, "username": username, "email": email, "fullName": full_name}
                }, status=201)
            except sqlite3.IntegrityError:
                conn.close()
                return self.send_json({"success": False, "message": "Username or email already exists"}, status=400)

        self.send_response(404)
        self.end_headers()

    def do_DELETE(self):
        path = self.path.split('?')[0]

        # DELETE /cart/:id
        m = re.match(r'^(?:/api)?/cart/(\d+)$', path)
        if m:
            item_or_book_id = int(m.group(1))
            cart_id = self.get_cart_id()

            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("DELETE FROM cart_items WHERE cart_id = ? AND (id = ? OR book_id = ?)", (cart_id, item_or_book_id, item_or_book_id))
            conn.commit()

            # Return updated cart
            c.execute("""
                SELECT c.id, c.cart_id, c.book_id, c.quantity, b.title, b.author, b.price, b.image_url
                FROM cart_items c
                JOIN books b ON c.book_id = b.id
                WHERE c.cart_id = ?
            """, (cart_id,))
            rows = c.fetchall()
            items = []
            total_price = 0.0
            total_items = 0
            for r in rows:
                subtotal = round(r[3] * r[6], 2)
                total_price += subtotal
                total_items += r[3]
                items.append({
                    "id": r[0], "cartId": r[1], "bookId": r[2], "quantity": r[3],
                    "bookTitle": r[4], "bookAuthor": r[5], "bookPrice": r[6],
                    "bookImageUrl": r[7], "subtotal": subtotal
                })
            conn.close()
            return self.send_json({
                "cartId": cart_id,
                "items": items,
                "totalPrice": round(total_price, 2),
                "totalItems": total_items
            })

        self.send_response(404)
        self.end_headers()

class ReusableThreadingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == '__main__':
    init_db()
    server = ReusableThreadingServer(('0.0.0.0', PORT), BookstoreHandler)
    print(f"=================================================")
    print(f" PageTurner Bookstore is running on http://localhost:{PORT}")
    print(f" REST API and Static UI active!")
    print(f" Press Ctrl+C to stop.")
    print(f"=================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
