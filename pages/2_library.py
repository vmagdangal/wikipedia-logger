import streamlit as st  # type: ignore
import sqlite3
import pandas as pd # type: ignore
import wikipedia #type: ignore

st.set_page_config(page_title="Article Library", page_icon="📊")
st.markdown(f"**Articles**")
max_summary_length = 350

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
            GROUP_CONCAT(c.category_name, ', ') AS categories
        FROM Articles a
        INNER JOIN ArticleCategories ac ON a.article_id = ac.article_id
        INNER JOIN Categories c ON ac.category_id = c.category_id
        GROUP BY a.article_id, a.title, a.was_read, a.date_added, a.link
    """, sqliteConnection)

    for index, row in df.iterrows():
        page = wikipedia.WikipediaPage(title=row.title)

        with st.container(height=290, border=True):
            title, link = st.columns([5.9, 1], vertical_alignment="center")
            title.markdown(f"**{row.title}**")
            link.link_button("Visit 🔗", row.link)
            if(len(page.summary) > max_summary_length):
                st.write(page.summary[:max_summary_length - 3] + "...")
            else:
                st.write(page.summary)

            st.markdown(f":blue-background[*{row.categories}*]")

            date_badge, read_badge, empty, options = st.columns([1.1, 1, 4, 1], vertical_alignment="center")
            date_badge.badge(row.date_added, icon=":material/calendar_today:", color="blue")
            more_options = options.popover("...")
            
            if(row.was_read == "True"):
                read_badge.badge("Read", icon=":material/check:", color="green")
                if more_options.button("Mark as Want to Read", icon="⌛️", use_container_width=True, key=f"wantread_{row.article_id}"):
                    switch_read(0, row.article_id)
            else:
                read_badge.badge("Unread", icon=":material/close:", color="orange")
                if more_options.button("Mark as Read", icon="✅", use_container_width=True, key=f"read_{row.article_id}"):
                    switch_read(1, row.article_id)
            if more_options.button("Delete from Library", icon="🗑️", use_container_width=True, key=f"delete_{row.article_id}"):
                delete_article(row.article_id)

except sqlite3.Error as error:
    print('Error occurred -', error)

finally:
    if sqliteConnection:
        sqliteConnection.close()