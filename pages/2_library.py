import streamlit as st  # type: ignore
import sqlite3
import pandas as pd # type: ignore
import wikipedia #type: ignore

st.set_page_config(page_title="Article Library", page_icon="📊", layout="wide")
MAX_SUMMARY_LENGTH = 350
WIDTH_SORT = [4, 2, 1]
WIDTH_FILTER = [4, 1, 1]
WIDTH_ARTICLE_BADGE = [4, 4, 1]
WIDTH_EDIT_ENTRY = [4, 1]
WIDTH_2COL_EVEN = [1, 1]

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

    category_map = {c.category_name: c for c in grab_categories()}
    
    st.title("Library")

    with st.expander("Sort & Filter", icon=":material/sort:"):
        if "df_using" not in st.session_state:
            st.session_state.df_using = df.copy()

        SORT_COLUMNS = {
            "Title": "title",
            "Date": "date_added"
        }
        
        sort_options, sort_dir_options, sort_confirm = st.columns(WIDTH_SORT, vertical_alignment="bottom")
        sort_selection = sort_options.selectbox(
            "Sort By",
            ("Title", "Date"),
        )
        sort_direction = sort_dir_options.radio(
            "Order",
            ["Ascending", "Descending"],
            key="sort_direction"
        )
        if sort_confirm.button("Sort", use_container_width=True, key=f"sort_confirm"):
            st.session_state.df_using = (df
                .copy()
                .sort_values(by=SORT_COLUMNS[sort_selection], ascending=(sort_direction == "Ascending"))
            )

        st.divider()
        filter_options, filter_confirm, reset_filter = st.columns(WIDTH_FILTER, vertical_alignment="bottom")
        filter_selection = filter_options.selectbox(
            "Filter Category",
            list(category_map.keys()),
        )
        if filter_confirm.button("Filter", use_container_width=True, key=f"filter_confirm"):
            st.session_state.df_using = df.copy()[df["categories"].str.contains(f"{filter_selection}", na=False)]
        if reset_filter.button("Reset", use_container_width=True, key=f"filter_reset"):
            st.session_state.df_using = df.copy()

        df_using = st.session_state.df_using

    st.markdown(f"**Articles** (Size: {len(df_using)})")
    with st.container(border=True):
        for index, row in df_using.iterrows():
            page = wikipedia.WikipediaPage(title=row.title)
            with st.expander(f"{row.title}"):

                st.divider()
                st.subheader(f"{row.title}")
                category_markdown = ""
                lib_categories = row.categories.split("|")
                lib_categories.sort()
                for category in lib_categories:
                    category_markdown += f":blue-background[{category}] "
                st.markdown(category_markdown)
                
                if(len(page.summary) > MAX_SUMMARY_LENGTH):
                    st.write(page.summary[:MAX_SUMMARY_LENGTH - 3] + "...")
                else:
                    st.write(page.summary)

                date_badge, link, read_badge= st.columns(WIDTH_ARTICLE_BADGE, vertical_alignment="center")
                date_badge.badge(row.date_added, icon=":material/calendar_today:", color="blue")
                link.link_button("Visit 🔗", row.link)

                st.divider()
                st.markdown("**Edit Entry**")
                mark_read, delete = st.columns(WIDTH_2COL_EVEN, vertical_alignment="center")
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

                date_options, date_save = st.columns(WIDTH_EDIT_ENTRY, vertical_alignment="bottom")
                new_date = date_options.date_input("Date Read", row.date_added)
                if date_save.button("Update", icon="🔄", use_container_width=True, key=f"date_{row.article_id}"):
                    update_date(row.article_id, new_date)

                category_options, category_save = st.columns(WIDTH_EDIT_ENTRY, vertical_alignment="bottom")
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