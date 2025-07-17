import streamlit as st  # type: ignore
import sqlite3
import pandas as pd # type: ignore

st.set_page_config(page_title="Article Library", page_icon="📊")
st.markdown(f"**Dataframe**")

try:
    sqliteConnection = sqlite3.connect('./database/articles.db')

    df = pd.read_sql_query("""
        SELECT article_id,
            title, 
            CASE
                WHEN was_read = 0 THEN "False"
                ELSE "True"
            END as was_read,
            date_added, 
            link
        FROM Articles
    """, sqliteConnection)

    st.write(df.iloc[:, 1:])

except sqlite3.Error as error:
    print('Error occurred -', error)

finally:
    if sqliteConnection:
        sqliteConnection.close()