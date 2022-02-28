# -*- coding: utf-8 -*-
"""
Created on Sun Dec 19 16:45:20 2021

@author: pranjal.pandey
"""

# app.py

## Importing libraries
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import hydralit_components as hc
import datetime
import base64
import os
import pandas as pd
from itertools import cycle

## Pages
from src.pages import overall
from src.pages import details
from src.pages import insights
from src.pages import extracts

# make it look nice from the start
st.set_page_config(page_title="Inventory Intelligence", 
                   page_icon = "https://intranet.talabat.com/wp-content/uploads/2021/02/talabat-favicon-150x150.png", 
                   layout='wide', 
                   initial_sidebar_state='expanded',
                   menu_items={
                       'Get Help': 'https://confluence.deliveryhero.com/display/TLBTDTV2/VNII+-+Inventory+Intelligence',
                       'Report a bug': "https://confluence.deliveryhero.com/display/TLBTDTV2/VNII+-+Inventory+Intelligence",
                       'About': "The aim of Inventory Intelligence is to answer all questions which are related to finding out the number of vendors pertaining to certain specific conditions. This product aims to answer all the queries which begin with “How many vendors…?”."
 })

def read_sql_file(filename):
    """
    This method reads SQL from files

    Parameters
    ----------
    filename : TYPE *.sql file
        DESCRIPTION The sql for the streamlit component

    Returns
    SQL 

    """
    
    f = open(os.path.join("sql", filename), 'r')
    sqlQuery = f.read()
    f.close()
    
    return sqlQuery


# Uses st.cache to only rerun when the query changes or after 10 min.
@st.cache(ttl=600, hash_funcs={bigquery.client.Client: lambda _: None}, show_spinner=False)
def run_query(client, query):
    """
    This method runs SQL queries
    """
    query_job = client.query(query)
    rows_raw = query_job.result()
    # Convert to list of dicts. Required for st.cache to hash the return value.
    rows = [dict(row) for row in rows_raw]
    return rows

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# ===========================================================================================================================================

## Tha Main Query for Overall page ==========================================================================================================
"""
with st.spinner("Mixing all the packs and potions..!"):
    
    if 'overall_lastmonth_results' not in st.session_state:
        st.session_state.overall_lastmonth_results = run_query(
            client, 
            read_sql_file(
                'main_query.sql')
            )
"""
if 'overall_lastmonth_results' not in st.session_state:
    
    with st.spinner("Mixing all the packs and potions..!"):
        st.session_state.overall_lastmonth_results = run_query(
            client, 
            read_sql_file(
                'main_query.sql')
            )        
        st.session_state.main_overall_df = pd.DataFrame(st.session_state.overall_lastmonth_results)
        
        int_columns = ['month', 'vendor_id', 'chain_id', 
                       'session_count', 'attempted_order', 'placed_order', 
                       'successful_order_count', 'net_fail_order_count', 
                       'net_order_count', 'vendor_delay']
        
        float_columns = ['agg_gmv_eur', 'attempted_CVR', 'placed_CVR', 
                         'fail_rate', 'rating_display']
        
        for col in int_columns:
            st.session_state.main_overall_df[col] = st.session_state.main_overall_df[col].fillna(0)
            st.session_state.main_overall_df[col] = st.session_state.main_overall_df[col].apply(lambda x: int(x))
        
        for col in float_columns:
            st.session_state.main_overall_df[col] = st.session_state.main_overall_df[col].fillna(0.0)
            st.session_state.main_overall_df[col] = st.session_state.main_overall_df[col].apply(lambda x: float(x))
        
        ### Remove vendor_id NULLS
        st.session_state.main_overall_df.dropna(subset=['vendor_id'], inplace=True)
        
        ### Ratings display
        #ratings_df = overall_lastmonth_df[['vendor_id', 'rating_display']]
        def apply_rating_label(rating):
            if 1<=rating<2:
                return "1-2"
            elif 2<=rating<3:
                return "2-3"
            elif 3<=rating<4:
                return "3-4"
            elif 4<=rating:
                return "4+"
            else:
                return "<1"
        
        st.session_state.main_overall_df["rating_label"] = st.session_state.main_overall_df["rating_display"].apply(lambda rating: apply_rating_label(rating))

        # Splitting by month
        months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        cycled_months = cycle(months)
        currentMonth = datetime.datetime.now().month
        lastMonth_index = 0
        monthBefore_index = 0
        
        for index, month in enumerate(cycled_months, start=0):
            if month==currentMonth:
                lastMonth_index = index-1
                monthBefore_index = lastMonth_index - 1
                break
        
        lastMonth = months[lastMonth_index]
        monthBefore = months[monthBefore_index]
        
        st.session_state.main_overall_lastmonth_df = st.session_state.main_overall_df[st.session_state.main_overall_df["month"]==lastMonth]
        st.session_state.main_overall_monthbefore_df = st.session_state.main_overall_df[st.session_state.main_overall_df["month"]==monthBefore]
        
        
def refresh_data():
    for key in st.session_state:
        del st.session_state[key]

# ===========================================================================================================================================

class App():
    
    def __init__(self, main_overall_lastmonth_df, main_overall_monthbefore_df):
        
        self.main_overall_lastmonth_df = main_overall_lastmonth_df
        self.main_overall_monthbefore_df = main_overall_monthbefore_df
    
            
    def main(self):
        
        menu_data = [
            {'id': "Overall", 'icon': 'fas fa-home', 'label': "Overall"}, 
            {'id': "Details", 'icon': 'far fa-chart-bar', 'label': "Details"}, 
            {'id': "Insights", 'icon': 'fa fa-flask', 'label': "Insights"},
            {'id': "Extracts", 'icon': 'fa fa-download', 'label': 'Extracts'}
            ]
    
        over_theme = {'txc_inactive': '#FFFFFF', 
                      'menu_background': '#FF5A00', 
                      'txc_active': '#000FFF'}
        
        menu_id = hc.nav_bar(
            menu_definition=menu_data,
            override_theme=over_theme,
            #home_name='Overall',
            #login_name='Logout',
            hide_streamlit_markers=False, #will show the st hamburger as well as the navbar now!
            sticky_nav=True, #at the top or not
            sticky_mode='sticky', #jumpy or not-jumpy, but sticky or pinned
        )    
        
        st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/b3/Talabat_logo.svg", 
                         use_column_width=True)
        
        st.sidebar.markdown("<h1 style='text-align: center; color: black;'>Inventory Intelligence</h1>", 
                            unsafe_allow_html=True)
        
        st.sidebar.button(label="Refresh Data", 
                          key="refresh_data_button", 
                          help="Click this button to refresh the entire dashboard", 
                          on_click=refresh_data)        
        
        page = menu_id
        
        if 'page' not in st.session_state:
            st.session_state.page = page
        
        if page=="Overall":
            return self.display_overall_page(overall.Overall(self.main_overall_lastmonth_df, 
                                                             self.main_overall_monthbefore_df))
        elif page=="Details":
            return self.display_details_page(details.Details(self.main_overall_lastmonth_df))
        elif page=="Insights":
            return self.display_insights_page(insights.Insights(self.main_overall_lastmonth_df, 
                                                                self.main_overall_monthbefore_df))
        else:
            return self.display_extracts_page(extracts.Extracts(self.main_overall_lastmonth_df, 
                                                                self.main_overall_monthbefore_df))
        
        
    def display_overall_page(self, overall_page):
        return overall_page.main()
    
    def display_details_page(self, details_page):
        return details_page.main()
    
    def display_insights_page(self, insights_page):
        return insights_page.main()
    
    def display_extracts_page(self, extracts_page):
        return extracts_page.main()
      
    @st.cache(allow_output_mutation=True)
    def get_base64_of_bin_file(self, bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    
    def set_png_as_page_bg(self, png_file):
        bin_str = self.get_base64_of_bin_file(png_file)
        page_bg_img = '''
        <style>
        body {
        background-image: url("data:image/png;base64,%s");
        background-size: cover;
        }
        </style>
        ''' % bin_str
        
        st.markdown(page_bg_img, unsafe_allow_html=True)
        return
        

if __name__ == "__main__":
    appObject = App(st.session_state.main_overall_lastmonth_df, 
                    st.session_state.main_overall_monthbefore_df)
    appObject.main()
 