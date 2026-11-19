CREATE DATABASE IF NOT EXISTS book_review_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE book_review_db;

CREATE TABLE IF NOT EXISTS authors (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL UNIQUE,
  biography TEXT NULL,
  nationality VARCHAR(100) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS genres (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS books (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  isbn VARCHAR(20) NULL UNIQUE,
  publication_year SMALLINT NULL,
  language VARCHAR(60) NOT NULL DEFAULT 'English',
  description TEXT NULL,
  author_id INT NOT NULL,
  genre_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_books_author FOREIGN KEY (author_id) REFERENCES authors(id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_books_genre FOREIGN KEY (genre_id) REFERENCES genres(id)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS readers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reviews (
  id INT AUTO_INCREMENT PRIMARY KEY,
  book_id INT NOT NULL,
  reader_id INT NOT NULL,
  rating TINYINT NOT NULL,
  review_text TEXT NOT NULL,
  review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT chk_rating CHECK (rating BETWEEN 1 AND 5),
  CONSTRAINT fk_reviews_book FOREIGN KEY (book_id) REFERENCES books(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_reviews_reader FOREIGN KEY (reader_id) REFERENCES readers(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT uq_reader_book UNIQUE (book_id, reader_id)
);

INSERT IGNORE INTO authors (name, biography, nationality) VALUES
('R. K. Narayan', 'Indian author known for stories set in Malgudi.', 'Indian'),
('J. K. Rowling', 'British author best known for the Harry Potter series.', 'British'),
('George Orwell', 'English novelist and essayist.', 'British'),
('A. P. J. Abdul Kalam', 'Indian aerospace scientist and former President of India.', 'Indian');

INSERT IGNORE INTO genres (name) VALUES
('Fiction'), ('Fantasy'), ('Dystopian'), ('Biography'), ('Science'), ('Mystery'), ('Self-help');

INSERT IGNORE INTO books (title, isbn, publication_year, language, description, author_id, genre_id)
SELECT 'Malgudi Days', '9788185986173', 1943, 'English',
       'Short stories set in the fictional South Indian town of Malgudi.', a.id, g.id
FROM authors a, genres g WHERE a.name='R. K. Narayan' AND g.name='Fiction';

INSERT IGNORE INTO books (title, isbn, publication_year, language, description, author_id, genre_id)
SELECT 'Harry Potter and the Philosopher''s Stone', '9780747532699', 1997, 'English',
       'A young wizard begins his journey at Hogwarts.', a.id, g.id
FROM authors a, genres g WHERE a.name='J. K. Rowling' AND g.name='Fantasy';

INSERT IGNORE INTO books (title, isbn, publication_year, language, description, author_id, genre_id)
SELECT 'Animal Farm', '9780451526342', 1945, 'English',
       'A political satire told through the story of farm animals.', a.id, g.id
FROM authors a, genres g WHERE a.name='George Orwell' AND g.name='Dystopian';

INSERT IGNORE INTO books (title, isbn, publication_year, language, description, author_id, genre_id)
SELECT 'Wings of Fire', '9788173711466', 1999, 'English',
       'An autobiography reflecting on A. P. J. Abdul Kalam’s life.', a.id, g.id
FROM authors a, genres g WHERE a.name='A. P. J. Abdul Kalam' AND g.name='Biography';

INSERT IGNORE INTO readers (name) VALUES ('Demo Reader'), ('Arun'), ('Priya');

INSERT IGNORE INTO reviews (book_id, reader_id, rating, review_text)
SELECT b.id, r.id, 5, 'An engaging read with memorable characters.'
FROM books b, readers r WHERE b.title='Malgudi Days' AND r.name='Demo Reader';

INSERT IGNORE INTO reviews (book_id, reader_id, rating, review_text)
SELECT b.id, r.id, 4, 'Interesting story and easy to recommend.'
FROM books b, readers r WHERE b.title='Animal Farm' AND r.name='Arun';
