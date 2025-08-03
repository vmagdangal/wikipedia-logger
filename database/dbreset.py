import sqlite3

DB_PATH = './database/articles.db'

try:
    # Connect to SQLite Database and create a cursor
    sqliteConnection = sqlite3.connect(DB_PATH)
    cursor = sqliteConnection.cursor()
    print('Resetting Database')

    drop_queries = [
        "DROP TABLE IF EXISTS ArticleCategories;",
        "DROP TABLE IF EXISTS Categories;",
        "DROP TABLE IF EXISTS Articles;",
        "DROP TABLE IF EXISTS Reviews;"
    ]

    for query in drop_queries:
        cursor.execute(query)

    article_table_setup = ["""
    CREATE TABLE IF NOT EXISTS Articles (
        article_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE,
        link TEXT UNIQUE,
        date_added DATE DEFAULT CURRENT_DATE,
        was_read BOOLEAN DEFAULT 0
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS Categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT UNIQUE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS ArticleCategories (
        article_id INTEGER,
        category_id INTEGER,
        PRIMARY KEY (article_id, category_id),
        FOREIGN KEY(article_id) REFERENCES Articles(article_id) ON DELETE CASCADE,
        FOREIGN KEY(category_id) REFERENCES Categories(category_id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS Reviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        article_id INTEGER,
        interest_rating INTEGER,
        quality_rating INTEGER,
        FOREIGN KEY(article_id) REFERENCES Articles(article_id) ON DELETE CASCADE
    );
    """]

    for query in article_table_setup:
        cursor.execute(query)

    # Close the cursor after use
    cursor.close()

except sqlite3.Error as error:
    print('Error occurred -', error)

finally:
    # Ensure the database connection is closed
    if sqliteConnection:
        sqliteConnection.close()
        print('Reset Complete')