import sqlite3

try:
    # Connect to SQLite Database and create a cursor
    sqliteConnection = sqlite3.connect('./database/articles.db')
    cursor = sqliteConnection.cursor()
    print('Preparing Database')

    article_table_setup = ["""
    CREATE TABLE IF NOT EXISTS Articles (
        article_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE,
        link TEXT UNIQUE,
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
        print('Database Created')