import streamlit as st # type: ignore
import sqlite3
import sys
import wikipedia # type: ignore
import pandas as pd # type: ignore
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
st.set_page_config(page_title="Category Setup", page_icon="📊")

class Article:
  def __init__(self, title, lang, data, link):
    self.title = title
    self.lang = lang
    self.data = data
    self.link = link

def parse_title(url):
    split_url = url.split('/wiki/')
    return split_url[-1].split('#')[0].replace('_', ' ').replace('%27', '\'')

def parse_lang(url):
    lang = url.split('.wikipedia.org')[0].replace('https://', '')
    if(lang == 'www' or lang == ''):
        return 'en'
    else:
        return lang

def add_category(title):
    try:
        sqliteConnection = sqlite3.connect('./database/articles.db')
        cursor = sqliteConnection.cursor()

        cursor.execute("""
            INSERT INTO Categories (category_name)
            VALUES (?);
        """, (title,))


        print('Article added')
        sqliteConnection.commit()
        cursor.close()
        return True

    except sqlite3.Error as error:
        print('Error occurred -', error)
        return False

    finally:
        if sqliteConnection:
            sqliteConnection.close()

def delete_category(category_id):
    try:
        sqliteConnection = sqlite3.connect('./database/articles.db')
        sqliteConnection.execute("PRAGMA foreign_keys=ON;")
        cursor = sqliteConnection.cursor()
        cursor.execute("""
            DELETE FROM Categories
            WHERE category_id = ?
        """, (category_id,))
        cursor.execute("""
            DELETE FROM Articles
            WHERE NOT EXISTS (
                SELECT 1
                FROM ArticleCategories ac
                WHERE Articles.article_id = ac.article_id
            );
        """)
        sqliteConnection.commit()
        cursor.close()
        st.rerun()
        return True

    except sqlite3.Error as error:
        print('Error occurred -', error)
        return False
    
    finally:
        if sqliteConnection:
            sqliteConnection.close()

st.title("Category Setup")

category_name = st.text_input("Add New Category").strip()
if category_name:
    if st.button("Add Category", icon="✅", use_container_width=True):
        if add_category(category_name):
            st.success(f"Successfully added \"{category_name}\"", icon="✅")
        else:
            st.error(f"Could not add \"{category_name}\". Category already exists.", icon="⚠️")

try:
    sqliteConnection = sqlite3.connect('./database/articles.db')

    df = pd.read_sql_query("""
        SELECT *
        FROM Categories
        ORDER BY category_name
    """, sqliteConnection)

    st.divider()
    st.markdown(f"**Categories**")

    with st.container(border=True):
        if(df.empty):
            st.write("No categories exist. Create one to start logging articles!")
        else:
            for index, row in df.iterrows():
                if(index != 0):
                    st.divider()
                title, delete = st.columns([6, 2], vertical_alignment="center")
                title.markdown(f"**{row.category_name}**")
                if delete.button("Delete Category", icon="🗑️", key=f"delete_{row.category_id}"):
                    delete_category(row.category_id)

            

except sqlite3.Error as error:
    print('Error occurred -', error)

finally:
    if sqliteConnection:
        sqliteConnection.close()