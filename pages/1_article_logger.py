import streamlit as st # type: ignore
import sqlite3
import sys
import wikipedia # type: ignore
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
st.set_page_config(page_title="Wikipedia Logger", page_icon="📊")

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

def add_article(button, wasRead: bool, article: Article):
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

wiki_url = st.text_input("Url Goes Here")
page = grab_article(wiki_url)

if isinstance(page, Article):
    
    left, right = st.columns(2)
    if left.button("Add to Read", icon="✅", use_container_width=True):
        add_article(left, True, page)
    if right.button("Add to Want to Read", icon="⌛️", use_container_width=True):
        add_article(right, False, page)

    st.markdown(f"**Title:**\n\n{page.title}")
    st.markdown(f"**Summary:**\n\n{page.data.summary}")

else:
    if(page is not None):
        st.write("Invalid URL.")