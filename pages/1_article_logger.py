import streamlit as st # type: ignore
import sqlite3
import sys
import wikipedia # type: ignore
import pandas as pd # type: ignore
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
st.set_page_config(page_title="Wikipedia Logger", page_icon="📊")

class Article:
  def __init__(self, title, lang, data, link):
    self.title = title
    self.lang = lang
    self.data = data
    self.link = link

class Category:
  def __init__(self, category_id, category_name):
    self.category_id = category_id
    self.category_name = category_name

def parse_title(url):
    split_url = url.split('/wiki/')
    return split_url[-1].split('#')[0].replace('_', ' ').replace('%27', '\'')

def parse_lang(url):
    lang = url.split('.wikipedia.org')[0].replace('https://', '')
    if(lang == 'www' or lang == ''):
        return 'en'
    else:
        return lang

def grab_article(url):
    pageLang = parse_lang(url)
    pageTitle = parse_title(url)

    wikipedia.set_lang(pageLang)
    try:
        page = wikipedia.WikipediaPage(title=pageTitle)
        return Article(pageTitle, pageLang, page, url)
    except Exception as e:
        print(f"Error fetching page '{pageTitle}': {e}")
        return None

def grab_categories():
    categories = []
    try:
        sqliteConnection = sqlite3.connect('./database/articles.db')

        df = pd.read_sql_query("""
            SELECT *
            FROM Categories
        """, sqliteConnection)
        
        for _,row in df.iterrows():
            categories.append(Category(row.category_id, row.category_name))


    except sqlite3.Error as error:
        print('Error grabbing categories -', error)

    finally:
        if sqliteConnection:
            sqliteConnection.close()
            return categories


def add_article(button, wasRead: bool, article: Article, categories):
    try:
        sqliteConnection = sqlite3.connect('./database/articles.db')
        cursor = sqliteConnection.cursor()

        cursor.execute("""
            INSERT INTO Articles (title, link, date_added, was_read)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(title) DO UPDATE SET
                link = excluded.link,
                date_added = excluded.date_added,
                was_read = excluded.was_read;
        """, (article.title, article.link, datetime.now().astimezone().date().isoformat(), wasRead))

        cursor.execute("SELECT article_id FROM Articles WHERE title = ?", (article.title,))
        article_id = cursor.fetchone()[0]

        cursor.execute("DELETE FROM ArticleCategories WHERE article_id = ?", (article_id,))

        for category in categories:
            cursor.execute("""
                INSERT OR IGNORE INTO ArticleCategories(article_id, category_id)
                VALUES(?, ?)
            """, (article_id, category.category_id))

        print('Article added')
        sqliteConnection.commit()
        cursor.close()

        if(wasRead):
            button.markdown("Article added to read list.")
        else:
            button.markdown("Article added to want-to-read list.")

    except sqlite3.Error as error:
        print('Error occurred -', error)

    finally:
        if sqliteConnection:
            sqliteConnection.close()

st.title("Wikipedia Logger")

categories = grab_categories()
if not categories:
    with st.container(border=True):
        st.write("No categories exist. Create one in Category Setup to start logging articles!")
else:
    wiki_url = st.text_input("Url Goes Here")
    page = grab_article(wiki_url)

    if isinstance(page, Article) and categories:
        category_map = {c.category_name: c for c in categories}
        selected_categories = st.multiselect("Select Categories", list(category_map.keys()), accept_new_options=False,)
        selected_objects = [category_map[name] for name in selected_categories]

        left, right = st.columns(2)
        if left.button("Add to Read", icon="✅", use_container_width=True):
            if not selected_objects:
                st.error(f"Please select at least 1 category.", icon="⚠️")
            else:
                add_article(left, True, page, selected_objects)
        if right.button("Add to Want to Read", icon="⌛️", use_container_width=True):
            if not selected_objects:
                st.error(f"Please select at least 1 category.", icon="⚠️")
            else:
                add_article(right, False, page, selected_objects)

        st.markdown(f"**Title:**\n\n{page.title}")
        st.markdown(f"**Summary:**\n\n{page.data.summary}")

    else:
        if(page is not None):
            st.write("Invalid URL.")