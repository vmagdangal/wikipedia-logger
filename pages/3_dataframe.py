import streamlit as st  # type: ignore
import sqlite3
import pandas as pd # type: ignore

st.set_page_config(page_title="Article Library", page_icon="📊")
st.markdown(f"**Dataframes**")

try:
    sqliteConnection = sqlite3.connect('./database/articles.db')

    df_article_combo = pd.read_sql_query("""
        SELECT 
            a.article_id,
            a.title, 
            GROUP_CONCAT(c.category_name, ', ') AS categories,
            a.date_added,
            CASE
                WHEN a.was_read = 0 THEN "False"
                ELSE "True"
            END as was_read,
            r.interest_rating,
            r.quality_rating,
            a.link
        FROM Articles a
        INNER JOIN ArticleCategories ac ON a.article_id = ac.article_id
        INNER JOIN Categories c ON ac.category_id = c.category_id
        INNER JOIN Reviews r ON a.article_id = r.article_id
        GROUP BY a.article_id, a.title, a.was_read, a.date_added, r.interest_rating, r.quality_rating,  a.link
    """, sqliteConnection)

    st.write("Combined Data")
    st.write(df_article_combo)

    df_articles = pd.read_sql_query("""
        SELECT *
        FROM Articles
    """, sqliteConnection)

    st.write("Articles")
    st.write(df_articles)

    df_categories = pd.read_sql_query("""
        SELECT *
        FROM Categories
    """, sqliteConnection)

    st.write("Categories")
    st.write(df_categories)

    df_junction = pd.read_sql_query("""
        SELECT article_id, category_id
        FROM ArticleCategories
    """, sqliteConnection)

    st.write("ArticleCategories")
    st.write(df_junction)

except sqlite3.Error as error:
    print('Error occurred -', error)

finally:
    if sqliteConnection:
        sqliteConnection.close()