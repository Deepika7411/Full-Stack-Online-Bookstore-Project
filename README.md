# 📚 PageTurner — Online Bookstore (Full Stack Focused)

A complete, modern Full-Stack Online Bookstore built with **Java, Spring Web MVC, JDBC, HTML5, CSS3, and JavaScript**.

---

## 🎯 Project Overview & Objective
PageTurner provides a complete e-commerce bookstore experience where users can:
- **Browse & Search Books**: Instant keyword search by title, author, or category.
- **Inspect Book Details**: View synopsis, pricing, stock, star ratings, and community reviews.
- **Cart Management**: Add items with custom quantities, view real-time subtotals, and remove items.
- **Checkout & Order Placement**: Submit shipping and payment details, receive an official order confirmation receipt.
- **User Authentication**: Sign In and Sign Up with basic validation and state persistence.
- **Book Reviews & Ratings (Bonus)**: Community review section allowing users to rate and write comments on books.
- **Modern Responsive Visuals**: Clean card-based design with realistic book covers and smooth transitions.

---

## 🛠️ Tech Stack & Architecture

| Layer | Technology | Details |
|---|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+) | Vanilla SPA architecture, responsive layout, CSS variables, modal dialogs, toast notifications |
| **Backend** | Java 17+, Spring Boot 3.2.x | Spring Web MVC for RESTful endpoints, dependency injection, service layer |
| **Database & Persistence** | JDBC (`JdbcTemplate`), H2 Database | Embedded in-memory SQL database with schema pre-loaded and auto-initialization. Zero external configuration required! |
| **Build Tool** | Apache Maven | Standard Maven project structure (`pom.xml`) |

---

## 📁 Project Directory Structure

```text
online-bookstore/
├── pom.xml                               # Maven project configuration
├── README.md                             # Comprehensive project documentation
├── run-preview.bat                       # Instant 1-click frontend preview script
├── run-backend.bat                       # Spring Boot launch script
├── src/
│   ├── main/
│   │   ├── java/com/bookstore/
│   │   │   ├── BookstoreApplication.java # Spring Boot entry point
│   │   │   ├── controller/               # Spring Web MVC REST Controllers
│   │   │   │   ├── BookController.java   # /books & /books/{id}
│   │   │   │   ├── CartController.java   # /cart & /cart/{id}
│   │   │   │   ├── CheckoutController.java # /checkout
│   │   │   │   └── AuthController.java   # /auth/login & /auth/signup
│   │   │   ├── model/                    # Data Entities
│   │   │   │   ├── Book.java
│   │   │   │   ├── Cart.java
│   │   │   │   ├── CartItem.java
│   │   │   │   ├── Order.java
│   │   │   │   ├── OrderItem.java
│   │   │   │   ├── Review.java
│   │   │   │   └── User.java
│   │   │   ├── dto/                      # Data Transfer Objects
│   │   │   │   ├── AddToCartRequest.java
│   │   │   │   ├── CheckoutRequest.java
│   │   │   │   ├── OrderResponse.java
│   │   │   │   ├── LoginRequest.java
│   │   │   │   ├── SignupRequest.java
│   │   │   │   └── ReviewRequest.java
│   │   │   ├── repository/               # JDBC Data Repositories (JdbcTemplate)
│   │   │   │   ├── BookRepository.java
│   │   │   │   ├── CartRepository.java
│   │   │   │   ├── OrderRepository.java
│   │   │   │   └── UserRepository.java
│   │   │   └── service/                  # Business Logic Services
│   │   │       ├── BookService.java
│   │   │       ├── CartService.java
│   │   │       ├── OrderService.java
│   │   │       └── UserService.java
│   │   └── resources/
│   │       ├── application.properties    # Server and H2 JDBC properties
│   │       ├── schema.sql                # Table definitions (DDL)
│   │       ├── data.sql                  # Initial catalog data (DML)
│   │       └── static/                   # Web MVC Static UI Assets
│   │           ├── index.html            # Main UI Single Page Application
│   │           ├── css/
│   │           │   └── style.css         # Responsive stylesheets
│   │           └── js/
│   │               ├── api.js            # REST API client & offline fallback
│   │               └── app.js            # UI interaction & view state management
```

---

## 🚀 API Endpoints Specification

| Method | Endpoint | Description | Request Body / Parameters |
|---|---|---|---|
| `GET` | `/books` | Fetch all books (with optional search) | Query param: `?search={query}` |
| `GET` | `/books/{id}` | Fetch book details by ID + reviews | Path param: `id` (e.g. `/books/1`) |
| `POST` | `/cart` | Add a book to user's cart | `{"bookId": 1, "quantity": 1}` |
| `GET` | `/cart` | Get cart contents & total price | Header or param: `X-Cart-Id` |
| `DELETE` | `/cart/{id}` | Remove book/item from cart | Path param: `id` |
| `POST` | `/checkout` | Submit order & clear cart | `{"customerName": "...", "shippingAddress": "...", ...}` |
| `POST` | `/books/{id}/reviews` | Add review with rating & comment | `{"reviewerName": "...", "rating": 5, "comment": "..."}` |
| `POST` | `/auth/login` | User login | `{"username": "reader1", "password": "password123"}` |
| `POST` | `/auth/signup` | User registration | `{"username": "...", "email": "...", "password": "..."}` |

*(Note: Every endpoint is also aliased under `/api/*`, e.g. `/api/books`, `/api/cart`)*

---

## 🗄️ Database Design (JDBC & H2)

The database schema initializes automatically from `schema.sql` and `data.sql`:

1. **`books`**: Stores `id`, `title`, `author`, `price`, `description`, `category`, `image_url`, `rating`, and `stock`.
2. **`reviews`**: Stores user reviews with foreign key reference `book_id -> books(id)`.
3. **`cart_items`**: Persists cart items by `cart_id` and `book_id`.
4. **`orders`**: Stores order receipts, total amounts, shipping address, and confirmation numbers.
5. **`order_items`**: Line items for each order referencing `order_id`.
6. **`users`**: User authentication records (`username`, `email`, `password`, `full_name`).

### H2 Web Console:
When running Spring Boot, access the interactive database console:
- URL: `http://localhost:8080/h2-console`
- JDBC URL: `jdbc:h2:mem:bookstoredb`
- Username: `sa`
- Password: *(leave blank)*

---

## 🏃 How to Run the Project

### Option 1: Instant Frontend Preview (Zero-Install)
If you'd like to test and explore the UI immediately:
1. Double click `run-preview.bat`, or run in PowerShell:
   ```powershell
   python -m http.server 8080 --directory src/main/resources/static
   ```
2. Open your browser at **`http://localhost:8080`**.
3. The frontend has a smart client fallback that lets you test searching, cart additions, removals, checkout, reviews, and authentication right away!

### Option 2: Full Spring Boot Backend (Recommended for Java Learning)
1. Ensure **Java 17 or higher** is installed.
   - You can download free OpenJDK from [Adoptium Eclipse Temurin](https://adoptium.net/).
2. Run via Maven CLI:
   ```bash
   mvn spring-boot:run
   ```
   *or open the project folder in **VS Code**, **IntelliJ IDEA**, or **Eclipse** and run `BookstoreApplication.java` directly.*
3. Visit **`http://localhost:8080`** in your browser. Spring Boot serves both the REST API and the frontend automatically!

---

## 💡 Learning Outcomes Achieved
1. **Frontend Architecture**: Building modular HTML5, modern responsive CSS3 layouts, and asynchronous JavaScript `fetch()` API calls.
2. **Spring Web MVC**: Designing clean `@RestController` classes, mapping HTTP verbs (`GET`, `POST`, `DELETE`), request bodies, path variables, and status codes.
3. **JDBC Fundamentals**: Writing explicit SQL queries, prepared statements, `RowMapper` implementations, and transactional operations using Spring's `JdbcTemplate`.
4. **State Management**: Managing cart sessions, user credentials, and reactive UI badge updates.
