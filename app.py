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

## Pages
from pages import overall
from pages import details
from pages import insights

def main():
    
    # Create API client.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(credentials=credentials)

    
    #make it look nice from the start
    st.set_page_config(page_title="Inventory Intelligence", 
                       page_icon = "https://intranet.talabat.com/wp-content/uploads/2021/02/talabat-favicon-150x150.png", 
                       layout='wide', 
                       initial_sidebar_state='expanded',
                       menu_items={
                           'Get Help': 'https://confluence.deliveryhero.com/display/TLBTDTV2/VNII+-+Inventory+Intelligence',
                           'Report a bug': "https://confluence.deliveryhero.com/display/TLBTDTV2/VNII+-+Inventory+Intelligence",
                           'About': "This is an *extremely* cool product! \n\n Vendor Data Unit is the best - *SIIIIUUUUUUU!!!*"
     })
    
    menu_data = [
        {'id': "Overall", 'icon': 'fas fa-home', 'label': "Overall"}, 
        {'id': "Details", 'icon': 'far fa-chart-bar', 'label': "Details"}, 
        {'id': "Insights", 'icon': 'fa fa-flask', 'label': "Insights"}
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
    
    
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/b3/Talabat_logo.svg", use_column_width=True)
    
    #if st.sidebar.button('click me too'):
     # st.info('You clicked at: {}'.format(datetime.datetime.now()))
    
    #get the id of the menu item clicked
    st.info(f"{menu_id}")
    
    
    page = menu_id
    st.write(page)
    
    if 'page' not in st.session_state:
        st.session_state.page = page
    
    if page=="Overall":
        return display_overall_page(overall.Overall(client))
    elif page=="Details":
        return display_details_page(details.Details(client))
    else:
        return display_insights_page()
    

    
def display_overall_page(overall_page):
    return overall_page.main()

def display_details_page(details_page):
    """THIS IS THE DETAILS PAGE - UNDER CONSTRUCTION"""
    return details_page.main()

def display_insights_page():
    """THIS IS THE INSIGHTS PAGE - UNDER CONSTRUCTION"""
    return "insights"
  
    

if __name__ == "__main__":
   main()
 