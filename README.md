# PageTurner — Book Review & Recommendation Management System

A student-friendly Flask + MySQL web application based on the project proposal.

## Features
- Dashboard statistics and top-rated books
- Add, edit, delete and search books
- Filter books by genre
- Author directory with add/delete
- Reader ratings and written reviews
- Average rating calculated from MySQL review data
- Genre-filtered recommendations ranked by average rating and review count
- Responsive custom CSS layout

## Requirements
- Python 3.10 or newer
- MySQL Server 8.x (or compatible MySQL server)
- VS Code

## Setup on Windows (VS Code)

1. Extract the ZIP file and open the `book_review_recommendation_system` folder in VS Code.
2. Start MySQL Server. Open MySQL Workbench and connect to your local server.
3. Open `schema.sql` in Workbench and execute it (lightning icon). It creates `book_review_db` and inserts sample authors, genres, books and reviews.
4. In VS Code, open Terminal → New Terminal. Run:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

   If PowerShell blocks activation, use Command Prompt terminal and run:
   ```bat
   .venv\Scripts\activate.bat
   ```

5. Copy `.env.example` to a new file named `.env`. Put your real MySQL password in `DB_PASSWORD`. If your MySQL username is not `root`, change `DB_USER` too. Do not include quote marks around values.
6. Start the app:

   ```powershell
   python app.py
   ```

7. Open `http://127.0.0.1:5000` in your browser. Keep the terminal running while demonstrating.

## Demo flow
1. Dashboard: show book, author, review and reader counts.
2. Books library: search `Malgudi`, then filter by `Fiction`.
3. Add a book: enter a title, choose an existing author and genre, then save.
4. Open a book and add a review with a rating from 1–5.
5. Return to the dashboard and show the review count / average rating changed.
6. Open Authors and add an author. To use a new author for a book, add them first.
7. Discover books: filter by genre and explain that results are ranked by average rating and review count.
8. Edit a book, then demonstrate delete only with a disposable test book.

## Expected initial data
- 4 sample books: Malgudi Days, Harry Potter and the Philosopher's Stone, Animal Farm, Wings of Fire
- 4 sample authors
- 7 genres
- 2 sample reviews
- Dashboard numbers should initially show 4 books, 4 authors, 2 reviews, and 2 reviewers. If the schema is run repeatedly, `INSERT IGNORE` avoids duplicate sample records.

## Troubleshooting
- **Can't connect to MySQL / dashboard setup screen:** verify MySQL Server is running, `.env` exists, DB password is correct, and the SQL script ran successfully.
- **`ModuleNotFoundError`:** activate `.venv`, then run `pip install -r requirements.txt`.
- **Access denied:** correct `DB_USER` and `DB_PASSWORD` in `.env`.
- **Unknown database:** execute `schema.sql` in MySQL Workbench.
- **Port 5000 is busy:** close the other Flask process or change `app.run(debug=True, port=5001)` at the bottom of `app.py`, then open port 5001.
- This is a local academic demo. It does not include login/authentication or production deployment security. Keep debug mode for local development only.

## Project structure
```text
book_review_recommendation_system/
├── app.py
├── schema.sql
├── requirements.txt
├── .env.example
├── README.md
├── static/
│   └── style.css
└── templates/
    ├── base.html
    ├── index.html
    ├── books.html
    ├── book_form.html
    ├── book_detail.html
    ├── reviews.html
    ├── authors.html
    ├── recommendations.html
    ├── setup_error.html
    └── 404.html
```
