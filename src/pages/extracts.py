# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 18:40:19 2022

@author: pranjal.pandey
"""

# EXTRACTS PAGE

## Importing libraries
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import hydralit_components as hc

import os

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from plotly import graph_objects as go
import mplcursors
from millify import millify, prettify
import itertools


plt.style.use('seaborn-darkgrid')

class Extracts:
    
    def __init__(self, main_overall_lastmonth_df, main_overall_monthbefore_df):
        #self.client = service_account_client
        self.main_overall_lastmonth_df = main_overall_lastmonth_df
        self.main_overall_monthbefore_df = main_overall_monthbefore_df
        
    def main(self):
        
        ## CSS
        self.load_css("style/css/style.css")
        
        
        # vertical filter ===========================================================================================================================
        verticals = ["all", "food", "grocery", "cosmetics", "pet shop", 
                     "pharmacy", "flowers", "electronics"]
        
        # is_active filter ==========================================================================================================================
        
        is_active = ["all", "TRUE", "FALSE"]
        
        # is_tgo filter =============================================================================================================================
        
        is_tgo = ["all", "TRUE", "FALSE"]
        
        # ratings filter ============================================================================================================================
        
        rating_labels = ["all", "<1", "1-2", "2-3", "3-4", "4+"]  

        # months filter =============================================================================================================================
        
        month_names = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 
                       9: "September", 10: "October", 11: "November", 12: "December"}  
        
        lastmonth = month_names[self.main_overall_lastmonth_df['month'].max()]
        
        # ===========================================================================================================================================
        # Sidebar ===================================================================================================================================
        
        with st.sidebar:
            if 'countries' not in st.session_state:
                st.session_state.countries = ["all"] + list(self.main_overall_lastmonth_df["country_name"].unique())
            if 'cities' not in st.session_state:
                st.session_state.cities = ["all"] + list(self.main_overall_lastmonth_df['city_name'].unique())
            if 'areas' not in st.session_state:
                st.session_state.areas = ["all"] + list(self.main_overall_lastmonth_df['area_name'].unique())
            
            def filter_location_area():
                if 'overall_city' in st.session_state:
                    st.session_state.cities = [self.city_filter, "all"]
                else:
                    st.session_state.cities = ["all"] + list(self.main_overall_lastmonth_df[self.main_overall_lastmonth_df["area_name"]==st.session_state.overall_area]['city_name'].unique())
                
                if 'overall_country' in st.session_state:
                    st.session_state.countries = [self.country_filter, "all"]
                else:
                    st.session_state.countries = ["all"] + list(self.main_overall_lastmonth_df[self.main_overall_lastmonth_df["area_name"]==st.session_state.overall_area]['country_name'].unique())
                
                if st.session_state.overall_area=="all":
                    if self.country_filter:
                        city_options = list(self.main_overall_lastmonth_df[self.main_overall_lastmonth_df['country_name']==self.country_filter]['city_name'].unique())
                        if self.city_filter in city_options:
                            city_options.remove(self.city_filter)
                        st.session_state.cities = [self.city_filter, "all"] + city_options
                    else:
                        city_options = list(self.main_overall_lastmonth_df['city_name'].unique())
                        if self.city_filter in city_options:
                            city_options.remove(self.city_filter)
                        st.session_state.cities = [self.city_filter, "all"] + city_options
                
            def filter_location_city():
                st.session_state.areas = ["all"] + list(self.main_overall_lastmonth_df[self.main_overall_lastmonth_df["city_name"]==st.session_state.overall_city]['area_name'].unique())
                
                if 'overall_country' in st.session_state:
                    st.session_state.countries = [self.country_filter, "all"]
                else:
                    st.session_state.countries = ["all"] + list(self.main_overall_lastmonth_df[self.main_overall_lastmonth_df["city_name"]==st.session_state.overall_city]['country_name'].unique())
                
                if st.session_state.overall_city=="all":
                    country_list = list(self.main_overall_lastmonth_df['country_name'].unique())
                    if self.country_filter in country_list:
                        country_list.remove(self.country_filter)
                    st.session_state.countries = [self.country_filter, "all"] + country_list
                    
                
            def filter_location_country():
                st.session_state.cities = ["all"] + list(self.main_overall_lastmonth_df[self.main_overall_lastmonth_df["country_name"]==st.session_state.overall_country]['city_name'].unique())
                st.session_state.areas = ["all"] + list(self.main_overall_lastmonth_df[self.main_overall_lastmonth_df["country_name"]==st.session_state.overall_country]['area_name'].unique())
                
            ### Country
            self.country_filter = self.create_selectbox_filter("Country", 
                                                               st.session_state.countries, 
                                                               "Filter by country", 
                                                               key="overall_country", 
                                                               on_change_function=filter_location_country)
            
            if self.country_filter=="all":
                #self.country_filter = ""
                self.country_flag = 0
            else:
                self.country_flag=1

            ### City
            self.city_filter = self.create_selectbox_filter("City", 
                                                               st.session_state.cities, 
                                                               "Filter by city", 
                                                               key="overall_city", 
                                                               on_change_function=filter_location_city)
            
            if self.city_filter=="all":
                #self.city_filter = ""
                self.city_flag = 0
            else:
                self.city_flag=1  

            ### Area
            self.area_filter = self.create_selectbox_filter("Area", 
                                                               st.session_state.areas, 
                                                               "Filter by area", 
                                                               key="overall_area", 
                                                               on_change_function=filter_location_area)           
            if self.area_filter=="all":
                #self.area_filter = ""
                self.area_flag = 0
            else:
                self.area_flag=1

                
            ### Vertical
            self.vertical_filter = self.create_selectbox_filter("Vertical", 
                                                                verticals, 
                                                                "Select the Vertical to filter the data", 
                                                                key="overall_vertical")
            
            if self.vertical_filter=="all":
                #self.vertical_filter = ""
                self.vertical_flag = 0
            else:
                self.vertical_flag = 1
                
            
            ### TGO Status 
            self.is_tgo_filter = self.create_selectbox_filter("IS_TGO", 
                                                              is_tgo, 
                                                              "Is the delivery fulfilled by Talabat?", 
                                                              key="overall_tgo")
            
            if self.is_tgo_filter=="all":
                #self.is_tgo_filter = ""
                self.tgo_flag = 0
            else:
                self.tgo_flag=1
                      
            
            ### Ratings 
            self.ratings_filter = self.create_selectbox_filter("User Ratings", 
                                                               rating_labels, 
                                                               "User ratings 0-5", 
                                                               key="details_rating")
            
            if self.ratings_filter=="all":
                #self.ratings_filter = ""
                self.ratings_flag = 0
            else:
                self.ratings_flag=1

            
       
            ### Reset Button
            def reset_all():
                st.session_state.overall_vertical="all"
                st.session_state.overall_tgo="all"
                st.session_state.overall_country="all"
                st.session_state.overall_city="all"
                st.session_state.overall_area="all"
                st.session_state.details_rating="all"
                
                self.area_flag = 0
                self.city_flag = 0
                self.country_flag = 0
                self.vertical_flag = 0
                self.tgo_flag = 0
                self.ratings_flag = 0
                
                st.session_state.countries = ["all"] + list(self.main_overall_lastmonth_df["country_name"].unique())
                st.session_state.cities = ["all"] + list(self.main_overall_lastmonth_df['city_name'].unique())
                st.session_state.areas = ["all"] + list(self.main_overall_lastmonth_df['area_name'].unique())

            

            st.button('Reset filters', on_click=reset_all)
            
        
        # ===========================================================================================================================================

        ### The datafranme to be used for all the visuals
        overall_lastmonth_df = self.apply_sidebar_filter(self.main_overall_lastmonth_df)
        overall_monthbefore_df = self.apply_sidebar_filter(self.main_overall_monthbefore_df)

        
        
        ### Total Vendors
        total_vendors_lastmonth = len(self.main_overall_lastmonth_df['vendor_id'].unique())
        total_vendors_monthbefore = len(self.main_overall_monthbefore_df['vendor_id'].unique())

        ### Total Vendors
        total_vendors_lastmonth = len(self.main_overall_lastmonth_df['vendor_id'].unique())
        total_orders_lastmonth = sum(self.main_overall_lastmonth_df['successful_order_count'])
        total_gmv_lastmonth = sum(self.main_overall_lastmonth_df['agg_gmv_eur'])
        total_sessions_lastmonth = sum(self.main_overall_lastmonth_df['session_count'])
        
        total_vendors_monthbefore = len(self.main_overall_monthbefore_df['vendor_id'].unique())
        total_orders_monthbefore = sum(self.main_overall_monthbefore_df['successful_order_count'])
        total_gmv_monthbefore = sum(self.main_overall_monthbefore_df['agg_gmv_eur'])
        total_sessions_monthbefore = sum(self.main_overall_monthbefore_df['session_count'])
        
        
        def safe_divide(n, d):
            try:
                return n/d
            except ZeroDivisionError:
                return 0
        
        # ===========================================================================================================================================
        
        ### Multi-filter Page visual - Extraction
        
        st.subheader("Data Extraction Point")
        col1, col2, col3 = st.columns([1, 1, 1])
   
        max_orders = overall_lastmonth_df['successful_order_count'].max()
        max_sessions = overall_lastmonth_df['session_count'].max()
        max_gmv = int(overall_lastmonth_df['agg_gmv_eur'].max())
        with col1:
            orders_limits_min = st.number_input(label="Show vendors with orders >=",
                                                 max_value=max_orders, 
                                                 value=0, 
                                                 step=1, 
                                                 key="detailed_orders")
        with col2:    
            gmv_limits_min = st.number_input(label="Show vendors with GMV >=",
                                             max_value=max_gmv, 
                                             value=0, 
                                             step=1, 
                                             key="detailed_gmv")
        with col3:    
            sessions_limits_min = st.number_input(label="Show vendors with sessions >=",
                                                  max_value=max_sessions, 
                                                  value=0, 
                                                  step=1, 
                                                  key="detailed_sessions")
        
        col1, col2 = st.columns([1, 1])
        max_cvr = int(overall_lastmonth_df['placed_CVR'].max())
        max_fr = int(overall_lastmonth_df['fail_rate'].max())
        with col1:
            cvr_limits_min = st.number_input(label="Show vendors with CVR >=",
                                             max_value=max_cvr, 
                                             value=0, 
                                             step=1, 
                                             key="detailed_cvr")
        with col2:    
            fr_limits_min = st.number_input(label="Show vendors with NFR >=",
                                            max_value=max_fr, 
                                            value=0, 
                                            step=1, 
                                            key="detailed_fr")
            
        
        orders_condition = overall_lastmonth_df['successful_order_count']>=orders_limits_min
        gmv_condition = overall_lastmonth_df['agg_gmv_eur']>=gmv_limits_min
        sessions_condition = overall_lastmonth_df['session_count']>=sessions_limits_min
        cvr_condition = overall_lastmonth_df['placed_CVR']>=cvr_limits_min
        fr_condition = overall_lastmonth_df['fail_rate']>=fr_limits_min
        
        df = overall_lastmonth_df[orders_condition & gmv_condition & sessions_condition & cvr_condition & fr_condition]
        st.caption("Vendors satisfying these conditions - " + str(len(df)))   

        funnel_df = {
            'filter': [
                'Total Vendors',
                'With successful orders greater than or equal to ' + str(orders_limits_min), 
                'With GMV greater greater than or equal to ' + str(gmv_limits_min), 
                'With sessions greater than or equal to ' + str(sessions_limits_min), 
                'With CVR greater than or equal to ' + str(cvr_limits_min), 
                'With Net Fail Rate greater than or equal to ' + str(fr_limits_min)],
            'value': [
                len(overall_lastmonth_df['vendor_id'].unique()),
                len(overall_lastmonth_df[orders_condition]['vendor_id'].unique()), 
                len(overall_lastmonth_df[orders_condition & gmv_condition]['vendor_id'].unique()), 
                len(overall_lastmonth_df[orders_condition & gmv_condition & sessions_condition]['vendor_id'].unique()), 
                len(overall_lastmonth_df[orders_condition & gmv_condition & sessions_condition & cvr_condition]['vendor_id'].unique()), 
                len(overall_lastmonth_df[orders_condition & gmv_condition & sessions_condition & cvr_condition & fr_condition]['vendor_id'].unique())]
            }
        
        fig = go.Figure()
        fig.add_trace(go.Funnel(
            y = funnel_df['filter'],
            x = funnel_df['value'], 
            
            textposition = "inside", 
            textinfo = "value+percent initial",
            textfont={"color": "white"},
            opacity = 0.7, 
            marker = {"color": ["orangered", "coral", "coral", "coral", "coral" , 'coral'],}))
                                      #"line": {"width": [4, 2, 2, 3, 1, 1], "color": ["lightsalmon", "lightsalmon", "lightsalmon", "lightsalmon", "lightsalmon" , "lightsalmon"]}},))))
        fig.update_layout(
            legend=dict(
                yanchor="bottom",
                xanchor="center"), 
            height=450,
            title= "Vendors as per conditions")
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3 = st.columns([1, 0.63, 1])
        with col1:
            st.empty()
        with col2:
            import csv
            df['rating_label'] = df['rating_label'].apply(lambda rating: str(rating) + "\t")
            #df = df.astype({'rating_label': 'str'})
            st.download_button(label="Download Vendor List", data=df.to_csv(), file_name="vendor_list.csv")
        with col3:
            st.empty()
        
        
        
        # ===========================================================================================================================================
    
    
    # ===========================================================================================================================================
    ## HELPER METHODS
    # ===========================================================================================================================================

     
    def create_selectbox_filter(self, label, options, help_text, key, on_change_function=None, args=None):
        """
        This method creates a selectbox filter - dropdown
        """
        selectbox_filter = st.selectbox(label, 
                              options=options, 
                              help=help_text, 
                              key=key, 
                              on_change=on_change_function, args=args)
        return selectbox_filter
        
    def apply_sidebar_filter(self, overall_lastmonth_df):
        """
        This method applies sidebar filter to the main sql result

        Parameters
        ----------
        overall_lastmonth_df : TYPE main sql result - pandas dataframe
            DESCRIPTION. pandas dataframe 

        Returns
        -------
        pandas dataframe with filters
        
        """
        boolean_mask = {
                "TRUE": True, 
                "FALSE": False
            }
        
        # BE VERY CAREFUL WITH THE ORDER HERE - ANY NEW FLAG NEEDS TO BE ADDED 
        # AT THE BEGINNING OF THIS LIST 
        # THEN INCREMENT THE NUMBER OF ITERTOOLS PRODUCT
        selections = [self.ratings_flag, self.area_flag, self.city_flag, self.country_flag, 
                      self.vertical_flag, self.tgo_flag]
        
        all_possible_combinations = [list(i) for i in itertools.product([0, 1], repeat=6)]
        
        if selections==all_possible_combinations[0]: 
            return overall_lastmonth_df
        elif selections==all_possible_combinations[1]:
            return overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
        elif selections==all_possible_combinations[2]:
            return overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
        elif selections==all_possible_combinations[3]: 
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[4]: 
            return overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
        elif selections==all_possible_combinations[5]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[6]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[7]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[8]:
            return overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
        elif selections==all_possible_combinations[9]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            return overall_lastmonth_df 
        elif selections==all_possible_combinations[10]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[11]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[12]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[13]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[14]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[15]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[16]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[17]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[18]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[19]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[20]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[21]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[22]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[23]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[24]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[25]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[26]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[27]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[28]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[29]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[30]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[31]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[32]: 
            return overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
        elif selections==all_possible_combinations[33]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[34]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[35]: 
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[36]: 
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[37]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[38]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[39]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[40]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[41]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            return overall_lastmonth_df 
        elif selections==all_possible_combinations[42]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[43]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[44]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[45]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[46]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[47]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[48]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[49]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[50]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[51]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[52]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[53]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[54]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[55]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[56]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[57]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[58]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[59]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[60]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[61]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[62]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
        elif selections==all_possible_combinations[63]:
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["rating_label"]==self.ratings_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["vertical"]==self.vertical_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["country_name"]==self.country_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["city_name"]==self.city_filter]
            overall_lastmonth_df = overall_lastmonth_df[overall_lastmonth_df["area_name"]==self.area_filter]
            return overall_lastmonth_df
    

        
    def load_css(self, file_name):
        with open(file_name) as f:
            st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)