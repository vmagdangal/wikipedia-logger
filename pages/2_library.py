import streamlit as st  # type: ignore
import sqlite3
import pandas as pd # type: ignore
import wikipedia #type: ignore

st.set_page_config(page_title="Article Library", page_icon="📊")
st.markdown(f"**Articles**")
max_summary_length = 350

class Category:
  def __init__(self, category_id, category_name):
    self.category_id = category_id
    self.category_name = category_name

def switch_read(was_read, article_id):
    try:
        sqliteConnection = sqlite3.connect('./database/articles.db')
        cursor = sqliteConnection.cursor()
        cursor.execute("""
            UPDATE Articles
            SET was_read = ?
            WHERE article_id = ?
        """, (was_read, article_id))
        sqliteConnection.commit()
        cursor.close()
        st.rerun()
        return True

    except sqlite3.Error as error:
        return False
    
    finally:
        if sqliteConnection:
            sqliteConnection.close()

def delete_article(article_id):
    try:
        sqliteConnection = sqlite3.connect('./database/articles.db')
        sqliteConnection.execute("PRAGMA foreign_keys=ON;")
        cursor = sqliteConnection.cursor()
        cursor.execute("""
            DELETE FROM Articles
            WHERE article_id = ?
        """, (article_id,))
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

def update_categories(article_id, categories):
    try:
        sqliteConnection = sqlite3.connect('./database/articles.db')
        sqliteConnection.execute("PRAGMA foreign_keys=ON;")
        cursor = sqliteConnection.cursor()

        # Deletes all categories first before adding the new ones
        cursor.execute("DELETE FROM ArticleCategories WHERE article_id = ?", (article_id,))

        for category in categories:
            cursor.execute("""
                INSERT OR IGNORE INTO ArticleCategories(article_id, category_id)
                VALUES(?, ?)
            """, (article_id, category.category_id))
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

def update_date(article_id, new_date):
    try:
        sqliteConnection = sqlite3.connect('./database/articles.db')
        sqliteConnection.execute("PRAGMA foreign_keys=ON;")
        cursor = sqliteConnection.cursor()

        cursor.execute("""
            UPDATE Articles
            SET date_added = ?
            WHERE article_id = ?
        """, (new_date, article_id))

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

def grab_categories():
    categories = []
    try:
        sqliteConnection = sqlite3.connect('./database/articles.db')

        df = pd.read_sql_query("""
            SELECT *
            FROM Categories
            ORDER BY category_name
        """, sqliteConnection)
        
        for _,row in df.iterrows():
            categories.append(Category(row.category_id, row.category_name))


    except sqlite3.Error as error:
        print('Error grabbing categories -', error)

    finally:
        if sqliteConnection:
            sqliteConnection.close()
            return categories

try:
    sqliteConnection = sqlite3.connect('./database/articles.db')

    df = pd.read_sql_query("""
        SELECT 
            a.article_id,
            a.title, 
            CASE
                WHEN a.was_read = 0 THEN "False"
                ELSE "True"
            END as was_read,
            a.date_added, 
            a.link,
            GROUP_CONCAT(c.category_name, '|') AS categories
        FROM Articles a
        INNER JOIN ArticleCategories ac ON a.article_id = ac.article_id
        INNER JOIN Categories c ON ac.category_id = c.category_id
        GROUP BY a.article_id, a.title, a.was_read, a.date_added, a.link
    """, sqliteConnection)

    for index, row in df.iterrows():
        page = wikipedia.WikipediaPage(title=row.title)

        with st.container(border=True):
            title, link = st.columns([5, 1], vertical_alignment="center")
            title.markdown(f"**{row.title}**")
            link.link_button("Visit 🔗", row.link)

            category_markdown = ""
            lib_categories = row.categories.split("|")
            lib_categories.sort()
            for category in lib_categories:
                category_markdown += f":blue-background[{category}] "
            st.markdown(category_markdown)
            
            if(len(page.summary) > max_summary_length):
                st.write(page.summary[:max_summary_length - 3] + "...")
            else:
                st.write(page.summary)

            date_badge, empty, read_badge= st.columns([2, 4, 1], vertical_alignment="center")
            date_badge.badge(row.date_added, icon=":material/calendar_today:", color="blue")

            with st.expander("Edit Entry"):
                mark_read, delete = st.columns([1, 1], vertical_alignment="center")
                if(row.was_read == "True"):
                    read_badge.badge("Read", icon=":material/check:", color="green")
                    if mark_read.button("Mark as Want to Read", icon="⌛️", use_container_width=True, key=f"wantread_{row.article_id}"):
                        switch_read(0, row.article_id)
                else:
                    read_badge.badge("Unread", icon=":material/close:", color="orange")
                    if mark_read.button("Mark as Read", icon="✅", use_container_width=True, key=f"read_{row.article_id}"):
                        switch_read(1, row.article_id)
                if delete.button("Delete from Library", icon="🗑️", use_container_width=True, key=f"delete_{row.article_id}"):
                    delete_article(row.article_id)

                date_options, date_save = st.columns([4, 1], vertical_alignment="bottom")
                new_date = date_options.date_input("Date Read", row.date_added)
                if date_save.button("Update", icon="🔄", use_container_width=True, key=f"date_{row.article_id}"):
                    update_date(row.article_id, new_date)

                category_map = {c.category_name: c for c in grab_categories()}
                category_options, category_save = st.columns([4, 1], vertical_alignment="bottom")
                new_categories = category_options.multiselect("Select Categories", 
                                        list(category_map.keys()), 
                                        accept_new_options=False,
                                        default=row.categories.split('|'),
                                        key=f"categories_{row.article_id}")
                empty_categories = not new_categories
                if category_save.button("Update", icon="🔄", use_container_width=True, key=f"category_{row.article_id}", disabled=empty_categories):
                    selected_objects = [category_map[name] for name in new_categories]
                    update_categories(row.article_id, selected_objects)

except sqlite3.Error as error:
    print('Error occurred -', error)

finally:
    if sqliteConnection:
        sqliteConnection.close()