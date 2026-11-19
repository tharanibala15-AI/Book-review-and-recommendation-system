import os
from datetime import datetime

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "local-demo-key-change-before-deployment")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "book_review_db"),
    "charset": "utf8mb4",
    "use_unicode": True,
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def query_db(sql, params=(), one=False, commit=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        if commit:
            conn.commit()
            return cursor.lastrowid
        return cursor.fetchone() if one else cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@app.context_processor
def inject_globals():
    return {"current_year": datetime.now().year}

@app.route("/")
def dashboard():
    try:
        stats = query_db("""
            SELECT (SELECT COUNT(*) FROM books) AS book_count,
                   (SELECT COUNT(*) FROM authors) AS author_count,
                   (SELECT COUNT(*) FROM reviews) AS review_count,
                   (SELECT COUNT(DISTINCT reader_id) FROM reviews) AS reader_count
        """, one=True)
        top_books = query_db("""
            SELECT b.id, b.title, a.name AS author, g.name AS genre,
                   ROUND(AVG(r.rating), 1) AS avg_rating, COUNT(r.id) AS review_count
            FROM books b JOIN authors a ON a.id=b.author_id
            JOIN genres g ON g.id=b.genre_id
            LEFT JOIN reviews r ON r.book_id=b.id
            GROUP BY b.id, b.title, a.name, g.name
            ORDER BY (AVG(r.rating) IS NULL), AVG(r.rating) DESC, COUNT(r.id) DESC, b.title
            LIMIT 5
        """)
        recent_reviews = query_db("""
            SELECT r.id, r.rating, r.review_text, r.review_date,
                   b.id AS book_id, b.title, rd.name AS reader_name
            FROM reviews r JOIN books b ON b.id=r.book_id
            JOIN readers rd ON rd.id=r.reader_id
            ORDER BY r.review_date DESC, r.id DESC LIMIT 5
        """)
        return render_template("index.html", stats=stats, top_books=top_books,
                               recent_reviews=recent_reviews)
    except Error as exc:
        app.logger.error("Database connection failed: %s", exc)
        return render_template("setup_error.html"), 503

@app.route("/books")
def books():
    search = request.args.get("q", "").strip()
    genre_id = request.args.get("genre", "").strip()
    genres = query_db("SELECT id, name FROM genres ORDER BY name")
    like = f"%{search}%"
    rows = query_db("""
        SELECT b.id, b.title, b.isbn, b.publication_year, b.language,
               a.name AS author, g.name AS genre, g.id AS genre_id,
               ROUND(AVG(r.rating), 1) AS avg_rating, COUNT(r.id) AS review_count
        FROM books b JOIN authors a ON a.id=b.author_id
        JOIN genres g ON g.id=b.genre_id
        LEFT JOIN reviews r ON r.book_id=b.id
        WHERE (%s='' OR b.title LIKE %s OR a.name LIKE %s OR g.name LIKE %s)
          AND (%s='' OR g.id=%s)
        GROUP BY b.id, b.title, b.isbn, b.publication_year, b.language,
                 a.name, g.name, g.id
        ORDER BY b.title
    """, (search, like, like, like, genre_id, genre_id))
    return render_template("books.html", books=rows, genres=genres,
                           q=search, selected_genre=genre_id)

@app.route("/books/add", methods=["GET", "POST"])
def add_book():
    authors = query_db("SELECT id, name FROM authors ORDER BY name")
    genres = query_db("SELECT id, name FROM genres ORDER BY name")
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author_id = request.form.get("author_id", "").strip()
        genre_id = request.form.get("genre_id", "").strip()
        if not title or not author_id or not genre_id:
            flash("Title, author and genre are required.", "error")
        else:
            try:
                query_db("""
                    INSERT INTO books (title, isbn, publication_year, language,
                                       description, author_id, genre_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    title, request.form.get("isbn", "").strip() or None,
                    request.form.get("publication_year", "").strip() or None,
                    request.form.get("language", "English").strip() or "English",
                    request.form.get("description", "").strip(),
                    int(author_id), int(genre_id)
                ), commit=True)
                flash("Book added successfully.", "success")
                return redirect(url_for("books"))
            except (Error, ValueError):
                flash("Could not save the book. Check the fields and make sure ISBN is unique.", "error")
    return render_template("book_form.html", book=None, authors=authors, genres=genres,
                           page_title="Add a book")

@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id):
    book = query_db("SELECT * FROM books WHERE id=%s", (book_id,), one=True)
    if not book:
        flash("Book not found.", "error")
        return redirect(url_for("books"))
    authors = query_db("SELECT id, name FROM authors ORDER BY name")
    genres = query_db("SELECT id, name FROM genres ORDER BY name")
    if request.method == "POST":
        try:
            query_db("""
                UPDATE books SET title=%s, isbn=%s, publication_year=%s,
                    language=%s, description=%s, author_id=%s, genre_id=%s
                WHERE id=%s
            """, (
                request.form.get("title", "").strip(),
                request.form.get("isbn", "").strip() or None,
                request.form.get("publication_year", "").strip() or None,
                request.form.get("language", "English").strip() or "English",
                request.form.get("description", "").strip(),
                int(request.form["author_id"]), int(request.form["genre_id"]), book_id
            ), commit=True)
            flash("Book details updated.", "success")
            return redirect(url_for("books"))
        except (Error, ValueError, KeyError):
            flash("Could not update the book. Check the fields and unique ISBN.", "error")
    return render_template("book_form.html", book=book, authors=authors, genres=genres,
                           page_title="Edit book")

@app.route("/books/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    try:
        query_db("DELETE FROM books WHERE id=%s", (book_id,), commit=True)
        flash("Book and its reviews deleted.", "success")
    except Error:
        flash("This book could not be deleted.", "error")
    return redirect(url_for("books"))

@app.route("/books/<int:book_id>")
def book_detail(book_id):
    book = query_db("""
        SELECT b.*, a.name AS author, a.biography AS author_bio,
               g.name AS genre, ROUND(AVG(r.rating), 1) AS avg_rating,
               COUNT(r.id) AS review_count
        FROM books b JOIN authors a ON a.id=b.author_id
        JOIN genres g ON g.id=b.genre_id
        LEFT JOIN reviews r ON r.book_id=b.id
        WHERE b.id=%s GROUP BY b.id, a.name, a.biography, g.name
    """, (book_id,), one=True)
    if not book:
        flash("Book not found.", "error")
        return redirect(url_for("books"))
    reviews = query_db("""
        SELECT r.*, rd.name AS reader_name FROM reviews r
        JOIN readers rd ON rd.id=r.reader_id
        WHERE r.book_id=%s ORDER BY r.review_date DESC, r.id DESC
    """, (book_id,))
    return render_template("book_detail.html", book=book, reviews=reviews)

@app.route("/books/<int:book_id>/reviews/add", methods=["POST"])
def add_review(book_id):
    if not query_db("SELECT id FROM books WHERE id=%s", (book_id,), one=True):
        flash("Book not found.", "error")
        return redirect(url_for("books"))
    reader_name = request.form.get("reader_name", "").strip()
    review_text = request.form.get("review_text", "").strip()
    try:
        rating = int(request.form.get("rating", "0"))
        if not reader_name or not review_text or rating not in range(1, 6):
            raise ValueError()
        query_db("INSERT INTO readers (name) VALUES (%s) ON DUPLICATE KEY UPDATE name=VALUES(name)",
                 (reader_name,), commit=True)
        reader = query_db("SELECT id FROM readers WHERE name=%s", (reader_name,), one=True)
        query_db("""
            INSERT INTO reviews (book_id, reader_id, rating, review_text)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE rating=VALUES(rating),
              review_text=VALUES(review_text), review_date=CURRENT_TIMESTAMP
        """, (book_id, reader["id"], rating, review_text), commit=True)
        flash("Review saved. Your previous review for this book is updated if one existed.", "success")
    except (ValueError, Error):
        flash("Enter your name, review, and a rating from 1 to 5.", "error")
    return redirect(url_for("book_detail", book_id=book_id))

@app.route("/reviews")
def reviews_page():
    rows = query_db("""
        SELECT r.id, r.rating, r.review_text, r.review_date,
               b.id AS book_id, b.title, rd.name AS reader_name
        FROM reviews r JOIN books b ON b.id=r.book_id
        JOIN readers rd ON rd.id=r.reader_id
        ORDER BY r.review_date DESC, r.id DESC
    """)
    return render_template("reviews.html", reviews=rows)

@app.route("/reviews/<int:review_id>/delete", methods=["POST"])
def delete_review(review_id):
    row = query_db("SELECT id FROM reviews WHERE id=%s", (review_id,), one=True)
    if row:
        query_db("DELETE FROM reviews WHERE id=%s", (review_id,), commit=True)
        flash("Review deleted.", "success")
    else:
        flash("Review not found.", "error")
    return redirect(request.referrer or url_for("reviews_page"))

@app.route("/authors", methods=["GET", "POST"])
def authors_page():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        biography = request.form.get("biography", "").strip()
        nationality = request.form.get("nationality", "").strip()
        if not name:
            flash("Author name is required.", "error")
        else:
            try:
                query_db("INSERT INTO authors (name, biography, nationality) VALUES (%s,%s,%s)",
                         (name, biography, nationality), commit=True)
                flash("Author added.", "success")
                return redirect(url_for("authors_page"))
            except Error:
                flash("Author could not be added. The name may already exist.", "error")
    rows = query_db("""
        SELECT a.*, COUNT(b.id) AS book_count FROM authors a
        LEFT JOIN books b ON b.author_id=a.id GROUP BY a.id ORDER BY a.name
    """)
    return render_template("authors.html", authors=rows)

@app.route("/authors/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    try:
        query_db("DELETE FROM authors WHERE id=%s", (author_id,), commit=True)
        flash("Author deleted.", "success")
    except Error:
        flash("This author is linked to a book. Reassign or delete those books first.", "error")
    return redirect(url_for("authors_page"))

@app.route("/recommendations")
def recommendations():
    genre = request.args.get("genre", "").strip()
    genres = query_db("SELECT id, name FROM genres ORDER BY name")
    rows = query_db("""
        SELECT b.id, b.title, a.name AS author, g.name AS genre, g.id AS genre_id,
               b.description, ROUND(AVG(r.rating), 1) AS avg_rating,
               COUNT(r.id) AS review_count
        FROM books b JOIN authors a ON a.id=b.author_id
        JOIN genres g ON g.id=b.genre_id
        LEFT JOIN reviews r ON r.book_id=b.id
        WHERE (%s='' OR g.id=%s)
        GROUP BY b.id, b.title, a.name, g.name, g.id, b.description
        ORDER BY (AVG(r.rating) IS NULL), AVG(r.rating) DESC, COUNT(r.id) DESC, b.title
    """, (genre, genre))
    return render_template("recommendations.html", books=rows, genres=genres, selected_genre=genre)

@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
