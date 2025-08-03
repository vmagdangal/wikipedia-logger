import streamlit as st # type: ignore
import sqlite3
import sys
import pandas as pd #type: ignore
import altair as alt
import wikipedia # type: ignore

sys.stdout.reconfigure(encoding='utf-8')
st.set_page_config(page_title="Dashboard", page_icon="📊")
DB_PATH = './database/articles.db'

st.title("Dashboard")

try:
    sqliteConnection = sqlite3.connect(DB_PATH)

    df_articles = pd.read_sql_query("""
        SELECT *
        FROM Articles
    """, sqliteConnection)

    df_categories = pd.read_sql_query("""
        SELECT *
        FROM Categories
    """, sqliteConnection)

    df_junction = pd.read_sql_query("""
        SELECT article_id, category_id
        FROM ArticleCategories
    """, sqliteConnection)

except sqlite3.Error as error:
    print('Error occurred -', error)

finally:
    if sqliteConnection:
        sqliteConnection.close()

if (df_articles.empty):
    with st.container(border=True):
        st.write("No articles have been logged yet.")
else:

    with st.container():
        top_categories = (df_junction
            .groupby("category_id")
            .size()
            .reset_index(name="num_categories")
            .merge(df_categories, on="category_id", how="right")
            .fillna(0)
            .sort_values(by=["num_categories", "category_name"], ascending=[False, True])
            .head(10)
            .rename(columns={"category_name": "Category Name"})
            .rename(columns={"num_categories": "Number of Categories"})
        )

        top_categories_chart = alt.Chart(top_categories).mark_bar().encode(
            x=alt.X("Category Name",
                sort="-y"
            ),
            y=alt.Y("Number of Categories",
                sort="ascending",
                axis=alt.Axis(tickMinStep=1),
            )
        )

        st.altair_chart(top_categories_chart, theme=None, use_container_width=True)
        st.write("Top Categories")
        with st.expander("View Dataframe"):
            st.write(top_categories)