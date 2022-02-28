# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 15:51:37 2021

@author: pranjal.pandey
"""

# DETAILS PAGE

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

class Details:
    
    def __init__(self, main_overall_lastmonth_df):
        #self.client = service_account_client
        self.main_overall_lastmonth_df = main_overall_lastmonth_df
        
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
        
        ### Total Vendors
        total_vendors = len(self.main_overall_lastmonth_df['vendor_id'].unique())
        total_orders = sum(self.main_overall_lastmonth_df['successful_order_count'])
        total_gmv = sum(self.main_overall_lastmonth_df['agg_gmv_eur'])
        total_sessions = sum(self.main_overall_lastmonth_df['session_count'])
        
        
        def safe_divide(n, d):
            try:
                return n/d
            except ZeroDivisionError:
                return 0
        
        # ===========================================================================================================================================
        ### Vendors with custom successful orders
        st.subheader("Vendors and successful orders - " + lastmonth)
        with st.container():
            df = overall_lastmonth_df[["vendor_id", "attempted_order", "placed_order", "successful_order_count", "rating_label"]]
            rating_df = overall_lastmonth_df[["vendor_id", "attempted_order", "placed_order", "successful_order_count", "rating_label"]]
                
            
            column1, column2 = st.columns([1, 1])
            with column1:
                lower_bound_orders = st.number_input(label='Select the minimum successful orders', 
                                              min_value=0.0, 
                                              max_value=3000.0, 
                                              #value=0.0,
                                              step=1.0,
                                              key="details_lower_bound_orders", 
                                              format="%.0f")
            with column2:
                if 'details_upper_bound_orders' in st.session_state:
                    upper_bound_orders = st.number_input(label='Select the maximum successful orders', 
                                              min_value=st.session_state.details_lower_bound_orders, 
                                              value=max(st.session_state.details_lower_bound_orders+1.0, 100.0),
                                              max_value=3000.0,
                                              step=1.0,
                                              key='details_upper_bound_orders', 
                                              format="%.0f")
                else:
                    upper_bound_orders = st.number_input(label='Select the maximum successful orders', 
                                              min_value=st.session_state.details_lower_bound_orders, 
                                              value=max(st.session_state.details_lower_bound_orders+1.0, 100.0),
                                              max_value=3000.0,
                                              step=1.0,
                                              key='details_upper_bound_orders', 
                                              format="%.0f")
            
            if 'details_lower_bound_orders' in st.session_state:
                min_value_slider_orders = st.session_state.details_lower_bound_orders
            if 'details_upper_bound_orders' in st.session_state:
                max_value_slider_orders = st.session_state.details_upper_bound_orders
            
            def update_numeric_inputs_orders():
                st.session_state.details_lower_bound_orders = st.session_state.details_silder_orders[0]
                st.session_state.details_upper_bound_orders = st.session_state.details_silder_orders[1]
            # slider for the min_orders
            min_orders = st.slider(label="Number of successful orders from " + lastmonth, 
                                        min_value=0.0, 
                                        max_value=3000.0, 
                                        value=[min_value_slider_orders, max_value_slider_orders], 
                                        step=10.0, 
                                        key='details_silder_orders',
                                        on_change=update_numeric_inputs_orders, 
                                        format="%.0f")
            #self.min_orders = 10
            column1, column2 = st.columns([1, 3])
            with column1:
                #st.write("How many vendors got these many orders in " + lastmonth + "?")
                subheading = '<p style="font-family:Sans-serif; color:Black; font-size: 16px;text-transform:uppercase;">Vendor information from ' + lastmonth + '</p>'
                st.markdown(subheading, unsafe_allow_html=True)
                num_vendors_without_sliders = len(df['vendor_id'].unique())
                st.caption("Number of vendors in contention after sidebar selections: " + str(num_vendors_without_sliders))
                min_vendors = df["successful_order_count"]>=min_orders[0]
                max_vendors = df["successful_order_count"]<min_orders[1]
                unique_vendors = df[min_vendors & max_vendors]["vendor_id"].unique()
                num_of_vendors = len(unique_vendors)
                percent_vendors = safe_divide(num_of_vendors, total_vendors)*100
                percent_vendors_filter = safe_divide(num_of_vendors, num_vendors_without_sliders)*100
                st.metric(label="Vendor orders in " + "[" + str(int(min_orders[0])) + ", " + str(int(min_orders[1])) + ")", 
                          value=prettify(num_of_vendors))
                st.metric(label="% of total vendors in selection", 
                          value="{:.2f}".format(percent_vendors_filter) + "%")
                st.metric(label="% of total vendors", 
                          value="{:.2f}".format(percent_vendors) + "%")
                
                these_orders = sum(df[df['vendor_id'].isin(unique_vendors)]['successful_order_count'])
                these_orders_percent = safe_divide(these_orders, total_orders)*100
                #st.write("These " + "{:.2f}".format(percent_vendors) + "% " + "vendors contributed to " + "{:.2f}".format(these_orders_percent) + "% of net orders.")
                st.download_button(label="Download Vendor List", data=df[min_vendors & max_vendors].to_csv(), file_name="vendor_list_successful_orders.csv")

            with column2:
                fig = px.histogram(data_frame=df[min_vendors], 
                                   x="successful_order_count", 
                                   opacity=0.75, 
                                   range_x=[min_orders[0]-300, 10000],
                                   #range_y=(0, num_of_vendors),
                                   labels={
                                       "successful_order_count": "Number of orders from " + lastmonth}, )
                                   #title="Vendors and successful orders from " + lastmonth)
                
                fig.update_traces(marker=dict(color='#FF5A00'))
                fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_layout(yaxis_title="Number of Vendors", height=500)
                fig.add_vline(x=df[min_vendors]['successful_order_count'].mean(), annotation_text="mean orders", line_dash="dash")
        
                st.plotly_chart(fig, height=500, use_container_width=True)   
            """
            sorted_df = self.main_overall_lastmonth_df.sort_values(by='successful_order_count', ascending=False)
            st.write("In total, how many vendors contributed to exactly this much successful orders in the month of " + lastmonth +"?")
            order_percent_input = st.number_input(label='Select the minimum successful orders %', 
                                          value=30.0, 
                                          min_value=0.0, 
                                          max_value=100.0, 
                                          #value=0.0,
                                          step=1.0,
                                          key="details_order_percent_input", 
                                          format="%.0f")
            exact_number_orders = int((order_percent_input*total_orders)/100)
            num_qualifying_vendors_orders = len(sorted_df[sorted_df['successful_order_count'].cumsum()<=exact_number_orders]['vendor_id'].unique())
            num_qualifying_vendors_orders_percent = safe_divide(num_qualifying_vendors_orders, total_vendors)*100
            st.write("In total, top " + "{:.2f}".format(num_qualifying_vendors_orders_percent) + "% " + "vendors by successful orders contributed to " + "{:.2f}".format(order_percent_input) + "% orders in the month of " + lastmonth + ".")
            st.caption("(Not capturing zero/null order vendors)")
            """
            
            line = "--------------------------------------------------------------"
            st.markdown(line)
        # ===========================================================================================================================================
        
        ### Vendors and their GMVs
        st.subheader("Vendors and GMV - " + lastmonth)
        with st.container():
            column1, column2 = st.columns([1, 1])
            with column1:
                lower_bound_gmv = st.number_input(label='Select the minimum GMV', 
                                              min_value=0.0, 
                                              max_value=100000.0, 
                                              #value=0.0,
                                              step=1.0,
                                              key="details_lower_bound_gmv", 
                                              format="%.0f")
            with column2:
                if 'details_upper_bound_gmv' in st.session_state:
                    upper_bound_gmv = st.number_input(label='Select the maximum GMV', 
                                              min_value=st.session_state.details_lower_bound_gmv, 
                                              value=max(st.session_state.details_lower_bound_gmv+1.0, 1000.0),
                                              max_value=100000.0,
                                              step=1.0,
                                              key='details_upper_bound_gmv', 
                                              format="%.0f")
                else:
                    upper_bound_gmv = st.number_input(label='Select the maximum GMV', 
                                              min_value=st.session_state.details_lower_bound_gmv, 
                                              value=max(st.session_state.details_lower_bound_gmv+1.0, 1000.0),
                                              max_value=100000.0,
                                              step=1.0,
                                              key='details_upper_bound_gmv', 
                                              format="%.0f")
            
            if 'details_lower_bound_gmv' in st.session_state:
                min_value_slider_gmv = st.session_state.details_lower_bound_gmv
            if 'details_upper_bound_gmv' in st.session_state:
                max_value_slider_gmv = st.session_state.details_upper_bound_gmv
            
            def update_numeric_inputs_gmv():
                st.session_state.details_lower_bound_gmv = st.session_state.details_silder_gmv[0]
                st.session_state.details_upper_bound_gmv = st.session_state.details_silder_gmv[1]
            # slider for the min_orders
            min_gmv = st.slider(label="GMV from last month", 
                                        min_value=0.0, 
                                        max_value=100000.0, 
                                        value=[min_value_slider_gmv, max_value_slider_gmv], 
                                        step=10.0, 
                                        key='details_silder_gmv',
                                        on_change=update_numeric_inputs_gmv, 
                                        format="%.0f")
            
            column1, column2 = st.columns([1, 3])
            with column1:
                #st.write("How many vendors had this much GMV in " + lastmonth + "?")
                subheading = '<p style="font-family:Sans-serif; color:Black; font-size: 16px;text-transform:uppercase;">Vendor information from ' + lastmonth + '</p>'
                st.markdown(subheading, unsafe_allow_html=True)
                num_vendors_without_sliders = len(overall_lastmonth_df['vendor_id'].unique())
                st.caption("Number of vendors in contention after sidebar selections: " + str(num_vendors_without_sliders))
                min_vendors = (overall_lastmonth_df["agg_gmv_eur"]>=min_gmv[0])
                max_vendors = (overall_lastmonth_df["agg_gmv_eur"]<min_gmv[1])
                unique_vendors = overall_lastmonth_df[min_vendors & max_vendors]["vendor_id"].unique()
                num_of_vendors = len(unique_vendors)
                percent_vendors = safe_divide(num_of_vendors, total_vendors)*100
                percent_vendors_filter = safe_divide(num_of_vendors, num_vendors_without_sliders)*100
                st.metric(label="Vendor GMV in " + "[" + str(int(min_gmv[0])) + ", " + str(int(min_gmv[1])) + ")", 
                          value=prettify(num_of_vendors))
                st.metric(label="% of total vendors in selection", 
                          value="{:.2f}".format(percent_vendors_filter) + "%")
                st.metric(label="% of total vendors", 
                          value="{:.2f}".format(percent_vendors) + "%")
                
                this_gmv = sum(overall_lastmonth_df[overall_lastmonth_df['vendor_id'].isin(unique_vendors)]['agg_gmv_eur'])
                this_gmv_percent = safe_divide(this_gmv, total_gmv)*100
                #st.write("These " + "{:.2f}".format(percent_vendors) + "% " + "vendors contributed to " + "{:.2f}".format(this_gmv_percent) + "% of net GMV.")
                st.download_button(label="Download Vendor List", data=overall_lastmonth_df[min_vendors & max_vendors].to_csv(), file_name="vendor_list_gmv.csv")
            with column2:
                fig = px.histogram(data_frame=overall_lastmonth_df[min_vendors], 
                                   x="agg_gmv_eur", 
                                   opacity=0.75, 
                                   range_x=(min_gmv[0]-3000, 100000), 
                                   labels={
                                       "agg_gmv_eur": "GMV from " + lastmonth}, )
                                   #title="Vendors and their GMV from " + lastmonth)
                
                fig.update_traces(marker=dict(color='#FF5A00'))
                fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_layout(yaxis_title="Number of Vendors", height=500)
                fig.add_vline(x=overall_lastmonth_df[min_vendors]['agg_gmv_eur'].mean(), annotation_text="mean GMV", line_dash="dash")
        
                st.plotly_chart(fig, height=500, use_container_width=True)
            """
            sorted_df = self.main_overall_lastmonth_df.sort_values(by='agg_gmv_eur', ascending=False)
            st.write("In total, how many vendors contributed to exactly this much GMV % in the month of " + lastmonth +"?")
            #st.markdown("Country: " + self.country_filter + "&emsp;&emsp; City: " + self.city_filter + "&emsp;&emsp; Area:" + self.area_filter)
            gmv_percent_input = st.number_input(label='Select the minimum GMV %', 
                                          value=30.0, 
                                          min_value=0.0, 
                                          max_value=100.0, 
                                          #value=0.0,
                                          step=1.0,
                                          key="details_gmv_percent_input", 
                                          format="%.0f")
            exact_number_gmv = int((gmv_percent_input*total_gmv)/100)
            num_qualifying_vendors = len(sorted_df[sorted_df['agg_gmv_eur'].cumsum()<=exact_number_gmv]['vendor_id'].unique())
            num_qualifying_vendors_percent = safe_divide((num_qualifying_vendors), total_vendors)*100
            st.write("In total, top " + "{:.2f}".format(num_qualifying_vendors_percent) + "% " + "vendors by GMV contributed to " + "{:.2f}".format(gmv_percent_input) + "% GMV in the month of " + lastmonth + ".")
            """
            """
            zero_vendors = len(sorted_df[sorted_df['agg_gmv_eur']==0]['vendor_id'].unique())
            zero_vendors_percent = safe_divide((zero_vendors), total_vendors)*100
            st.caption("In total, " + "{:.2f}".format(zero_vendors_percent) + "% " + "vendors by GMV contributed to zero GMV in the month of " + lastmonth + ".")
            """
            #st.caption("(Not capturing zero/null GMV vendors)")

            line = "--------------------------------------------------------------"
            st.markdown(line)
        # ===========================================================================================================================================

        ### Vendors and their sessions
        st.subheader("Vendors and sessions - " + lastmonth)
        with st.container():
            column1, column2 = st.columns([1, 1])
            with column1:
                lower_bound_sessions = st.number_input(label='Select the minimum number of sessions', 
                                              min_value=0.0, 
                                              max_value=20000.0, 
                                              #value=0.0,
                                              step=1.0,
                                              key="details_lower_bound_sessions", 
                                              format="%.0f")
            with column2:
                if 'details_upper_bound_sessions' in st.session_state:
                    upper_bound_sessions = st.number_input(label='Select the maximum number of sessions', 
                                              min_value=st.session_state.details_lower_bound_sessions, 
                                              value=max(st.session_state.details_lower_bound_sessions+1.0, 3000.0),
                                              max_value=20000.0,
                                              step=1.0,
                                              key='details_upper_bound_sessions', 
                                              format="%.0f")
                else:
                    upper_bound_sessions = st.number_input(label='Select the maximum number of sessions', 
                                              min_value=st.session_state.details_lower_bound_sessions, 
                                              value=max(st.session_state.details_lower_bound_sessions+1.0, 3000.0),
                                              max_value=20000.0,
                                              step=1.0,
                                              key='details_upper_bound_sessions', 
                                              format="%.0f")
            
            if 'details_lower_bound_sessions' in st.session_state:
                min_value_slider_sessions = st.session_state.details_lower_bound_sessions
            if 'details_upper_bound_sessions' in st.session_state:
                max_value_slider_sessions = st.session_state.details_upper_bound_sessions
            
            def update_numeric_inputs_sessions():
                st.session_state.details_lower_bound_sessions = st.session_state.details_silder_sessions[0]
                st.session_state.details_upper_bound_sessions= st.session_state.details_silder_sessions[1]
            # slider for the min_orders
            min_sessions = st.slider(label="Sessions from " + lastmonth, 
                                        min_value=0.0, 
                                        max_value=20000.0, 
                                        value=[min_value_slider_sessions, max_value_slider_sessions], 
                                        step=10.0, 
                                        key='details_silder_sessions',
                                        on_change=update_numeric_inputs_sessions, 
                                        format="%.0f")
            
            column1, column2 = st.columns([1, 3])
            with column1:
                #st.write("How many vendors had these many sessions in " + lastmonth + "?")
                subheading = '<p style="font-family:Sans-serif; color:Black; font-size: 16px;text-transform:uppercase;">Vendor information from ' + lastmonth + '</p>'
                st.markdown(subheading, unsafe_allow_html=True)
                num_vendors_without_sliders = len(overall_lastmonth_df['vendor_id'].unique())
                st.caption("Number of vendors in contention after sidebar selections: " + str(num_vendors_without_sliders))
                min_vendors = (overall_lastmonth_df["session_count"]>=min_sessions[0])
                max_vendors = (overall_lastmonth_df["session_count"]<min_sessions[1])
                unique_vendors = overall_lastmonth_df[min_vendors & max_vendors]["vendor_id"].unique()
                num_of_vendors = len(unique_vendors)
                percent_vendors = safe_divide(num_of_vendors, total_vendors)*100
                percent_vendors_filter = safe_divide(num_of_vendors, num_vendors_without_sliders)*100
                st.metric(label="Vendors sessions in " + "[" + str(int(min_sessions[0])) + ", " + str(int(min_sessions[1])) + ")", 
                          value=prettify(num_of_vendors))
                st.metric(label="% of total vendors in selection", 
                          value="{:.2f}".format(percent_vendors_filter) + "%")
                st.metric(label="% of total vendors", 
                          value="{:.2f}".format(percent_vendors) + "%")
                
                these_sessions = sum(overall_lastmonth_df[overall_lastmonth_df['vendor_id'].isin(unique_vendors)]['session_count'])
                these_sessions_percent = safe_divide(these_sessions, total_sessions)*100
                #st.write("These " + "{:.2f}".format(percent_vendors) + "% " + "vendors contributed to " + "{:.2f}".format(these_sessions_percent) + "% of net sessions.")
                st.download_button(label="Download Vendor List", data=overall_lastmonth_df[min_vendors & max_vendors].to_csv(), file_name="vendor_list_sessions.csv")

            with column2:
                fig = px.histogram(data_frame=overall_lastmonth_df[min_vendors], 
                                   x="session_count", 
                                   opacity=0.75, 
                                   range_x=(min_sessions[0]-500, 20000), 
                                   labels={
                                       "session_count": "Sessions from " + lastmonth}, )
                                   #title="Vendors and their Sessions received over " + lastmonth)
                
                fig.update_traces(marker=dict(color='#FF5A00'))
                fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_layout(yaxis_title="Number of Vendors", height=500)
                fig.add_vline(x=overall_lastmonth_df[min_vendors]['session_count'].mean(), annotation_text="mean sessions", line_dash="dash")
        
                st.plotly_chart(fig, height=500, use_container_width=True)
            """
            sorted_df = self.main_overall_lastmonth_df.sort_values(by='session_count', ascending=False)
            st.write("In total, how many vendors contributed to exactly this much session % in the month of " + lastmonth +"?")
            #st.markdown("Country: " + self.country_filter + "&emsp;&emsp; City: " + self.city_filter + "&emsp;&emsp; Area:" + self.area_filter)
            session_percent_input = st.number_input(label='Select the minimum session %', 
                                          value=30.0, 
                                          min_value=0.0, 
                                          max_value=100.0, 
                                          #value=0.0,
                                          step=1.0,
                                          key="details_session_percent_input", 
                                          format="%.0f")
            exact_number_session = int((session_percent_input*total_sessions)/100)
            num_qualifying_vendors = len(sorted_df[sorted_df['session_count'].cumsum()<=exact_number_session]['vendor_id'].unique())
            num_qualifying_vendors_percent = safe_divide(num_qualifying_vendors, total_vendors)*100
            st.write("In total, top " + "{:.2f}".format(num_qualifying_vendors_percent) + "% " + "vendors by sessions contributed to " + "{:.2f}".format(session_percent_input) + "% sessions in the month of " + lastmonth + ".")
            """
            """
            zero_vendors = len(sorted_df[sorted_df['session_count']==0]['vendor_id'].unique())
            zero_vendors_percent = safe_divide((zero_vendors), total_vendors)*100
            st.caption("In total, " + "{:.2f}".format(zero_vendors_percent) + "% " + "vendors by session contributed to zero sessions in the month of " + lastmonth + ".")
            """
            #st.caption("(Not capturing zero/null session vendors)")
            
            line = "--------------------------------------------------------------"
            st.markdown(line)       
        # ===========================================================================================================================================

        ### Vendors and their CVR
        st.subheader("Vendors and CVR - " + lastmonth)
        with st.container():
            column1, column2 = st.columns([1, 1])
            with column1:
                lower_bound_cvr = st.number_input(label='Select the minimum CVR', 
                                              min_value=0.0, 
                                              max_value=100.0, 
                                              #value=0.0,
                                              step=1.0,
                                              key="details_lower_bound_cvr", 
                                              format="%.0f")
            with column2:
                if 'details_upper_bound_cvr' in st.session_state:
                    upper_bound_cvr = st.number_input(label='Select the maximum CVR', 
                                              min_value=st.session_state.details_lower_bound_cvr, 
                                              value=max(st.session_state.details_lower_bound_cvr+1.0, 5.0),
                                              max_value=100.0,
                                              step=1.0,
                                              key='details_upper_bound_cvr', 
                                              format="%.0f")
                else:
                    upper_bound_cvr = st.number_input(label='Select the maximum CVR', 
                                              min_value=st.session_state.details_lower_bound_cvr, 
                                              value=max(st.session_state.details_lower_bound_cvr+1.0, 5.0),
                                              max_value=100.0,
                                              step=1.0,
                                              key='details_upper_bound_cvr', 
                                              format="%.0f")
            
            if 'details_lower_bound_cvr' in st.session_state:
                min_value_slider_cvr = st.session_state.details_lower_bound_cvr
            if 'details_upper_bound_cvr' in st.session_state:
                max_value_slider_cvr = st.session_state.details_upper_bound_cvr
            
            def update_numeric_inputs_cvr():
                st.session_state.details_lower_bound_cvr = st.session_state.details_silder_cvr[0]
                st.session_state.details_upper_bound_cvr= st.session_state.details_silder_cvr[1]
            # slider for the min_orders
            min_cvr = st.slider(label="CVR from last month", 
                                        min_value=0.0, 
                                        max_value=100.0, 
                                        value=[min_value_slider_cvr, max_value_slider_cvr], 
                                        step=1.0, 
                                        key='details_silder_cvr',
                                        on_change=update_numeric_inputs_cvr, 
                                        format="%.0f")
            
            #self.min_orders = 10
            column1, column2 = st.columns([1, 3])
            with column1:
                #st.write("How many vendors had this much CVR in " + lastmonth + "?")
                subheading = '<p style="font-family:Sans-serif; color:Black; font-size: 16px;text-transform:uppercase;">Vendor information from ' + lastmonth + '</p>'
                st.markdown(subheading, unsafe_allow_html=True)
                num_vendors_without_sliders = len(overall_lastmonth_df['vendor_id'].unique())
                st.caption("Number of vendors in contention after sidebar selections: " + str(num_vendors_without_sliders))
                min_vendors = (overall_lastmonth_df["placed_CVR"]>=min_cvr[0])
                max_vendors = (overall_lastmonth_df["placed_CVR"]<min_cvr[1])
                num_of_vendors = len(overall_lastmonth_df[min_vendors & max_vendors]["vendor_id"].unique())
                percent_vendors = safe_divide(num_of_vendors, total_vendors)*100
                percent_vendors_filter = safe_divide(num_of_vendors, num_vendors_without_sliders)*100
                st.metric(label="Vendors CVR in " + "[" + str(int(min_cvr[0])) + ", " + str(int(min_cvr[1])) + ")", 
                          value=prettify(num_of_vendors))
                st.metric(label="% of total vendors in selection", 
                          value="{:.2f}".format(percent_vendors_filter) + "%")
                st.metric(label="% of total vendors", 
                          value="{:.2f}".format(percent_vendors) + "%")
                st.download_button(label="Download Vendor List", data=overall_lastmonth_df[min_vendors & max_vendors].to_csv(), file_name="vendor_list_cvr.csv")

                """
                cvr_max_df = overall_lastmonth_df[overall_lastmonth_df['placed_CVR']==min_cvr[1]]
                cvr_max_vendors = len(cvr_max_df['vendor_id'].unique())
                cvr_max_vendors_percent = safe_divide(cvr_max_vendors, total_vendors)*100
                st.write("{:.2f}".format(cvr_max_vendors_percent) + "% vendors had exactly " + "{:.2f}".format(min_cvr[1]) + "% CVR.")
                """
            with column2:
                fig = px.histogram(data_frame=overall_lastmonth_df[min_vendors], 
                                   x="placed_CVR", 
                                   opacity=0.75, 
                                   range_x=(min_sessions[0]-3, 100), 
                                   labels={
                                       "placed_CVR": "CVR from " + lastmonth}, )
                                   #title="Vendors and their CVR over " + lastmonth)
                
                fig.update_traces(marker=dict(color='#FF5A00'))
                fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_layout(yaxis_title="Number of Vendors", height=500)
                fig.add_vline(x=overall_lastmonth_df[min_vendors]['placed_CVR'].mean(), annotation_text="mean CVR", line_dash="dash")
        
                st.plotly_chart(fig, height=500, use_container_width=True)
            
            line = "--------------------------------------------------------------"
            st.markdown(line)
        
        # ===========================================================================================================================================

        ### Vendors and their fail rates
        st.subheader("Vendors and Net Fail Rate - " + lastmonth)
        with st.container():
            column1, column2 = st.columns([1, 1])
            with column1:
                lower_bound_fr = st.number_input(label='Select the minimum Net Fail Rate', 
                                              min_value=0.0, 
                                              max_value=100.0, 
                                              #value=0.0,
                                              step=1.0,
                                              key="details_lower_bound_fr", 
                                              format="%.0f")
            with column2:
                if 'details_upper_bound_fr' in st.session_state:
                    upper_bound_fr = st.number_input(label='Select the maximum Net Fail Rate', 
                                              min_value=st.session_state.details_lower_bound_fr, 
                                              value=max(st.session_state.details_lower_bound_fr+1.0, 5.0),
                                              max_value=100.0,
                                              step=1.0,
                                              key='details_upper_bound_fr', 
                                              format="%.0f")
                else:
                    upper_bound_fr = st.number_input(label='Select the maximum Net Fail Rate', 
                                              min_value=st.session_state.details_lower_bound_fr, 
                                              value=max(st.session_state.details_lower_bound_fr+1.0, 5.0),
                                              max_value=100.0,
                                              step=1.0,
                                              key='details_upper_bound_fr', 
                                              format="%.0f")
            
            if 'details_lower_bound_fr' in st.session_state:
                min_value_slider_fr = st.session_state.details_lower_bound_fr
            if 'details_upper_bound_fr' in st.session_state:
                max_value_slider_fr = st.session_state.details_upper_bound_fr
            
            def update_numeric_inputs_fr():
                st.session_state.details_lower_bound_fr = st.session_state.details_silder_fr[0]
                st.session_state.details_upper_bound_fr= st.session_state.details_silder_fr[1]
            # slider for the min_orders
            min_fail_rate = st.slider(label="Net Fail Rate from last month", 
                                        min_value=0.0, 
                                        max_value=100.0, 
                                        value=[min_value_slider_fr, max_value_slider_fr], 
                                        step=1.0, 
                                        key='details_silder_fr',
                                        on_change=update_numeric_inputs_fr, 
                                        format="%.0f")
            
            column1, column2 = st.columns([1, 3])
            with column1:
                #st.write("How many vendors had this fail rate in " + lastmonth + "?")
                subheading = '<p style="font-family:Sans-serif; color:Black; font-size: 16px;text-transform:uppercase;">Vendor information from ' + lastmonth + '</p>'
                st.markdown(subheading, unsafe_allow_html=True)
                num_vendors_without_sliders = len(overall_lastmonth_df['vendor_id'].unique())
                st.caption("Number of vendors in contention after sidebar selections: " + str(num_vendors_without_sliders))
                min_vendors = (overall_lastmonth_df["fail_rate"]>=min_fail_rate[0])
                max_vendors = (overall_lastmonth_df["fail_rate"]<min_fail_rate[1])
                num_of_vendors = len(overall_lastmonth_df[min_vendors & max_vendors]["vendor_id"].unique())
                percent_vendors = safe_divide(num_of_vendors, total_vendors)*100
                percent_vendors_filter = safe_divide(num_of_vendors, num_vendors_without_sliders)*100
                st.metric(label="Vendor Fail Rate in " + "[" + str(int(min_fail_rate[0])) + ", " + str(int(min_fail_rate[1])) + ")", 
                          value=prettify(num_of_vendors))
                st.metric(label="% of total vendors in selection", 
                          value="{:.2f}".format(percent_vendors_filter) + "%")
                st.metric(label="% of total vendors", 
                          value="{:.2f}".format(percent_vendors) + "%")
                st.download_button(label="Download Vendor List", data=overall_lastmonth_df[min_vendors & max_vendors].to_csv(), file_name="vendor_list_fr.csv")

                """
                fr_max_df = overall_lastmonth_df[overall_lastmonth_df['fail_rate']==min_fail_rate[1]]
                fr_max_vendors = len(fr_max_df['vendor_id'].unique())
                fr_max_vendors_percent = safe_divide(fr_max_vendors, total_vendors)*100
                st.write("{:.2f}".format(fr_max_vendors_percent) + "% vendors had exactly " + "{:.2f}".format(min_fail_rate[1]) + "% Fail Rate.")
                """
            with column2:
                fig = px.histogram(data_frame=overall_lastmonth_df[min_vendors], 
                                   x="fail_rate", 
                                   opacity=0.75, 
                                   range_x=(min_fail_rate[0]-3, 100), 
                                   labels={
                                       "fail_rate": "Net Fail Rates from " + lastmonth}, )
                                   #title="Vendors and their Net Fail Rates from " + lastmonth)
                
                fig.update_traces(marker=dict(color='#FF5A00'))
                fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_layout(yaxis_title="Number of Vendors", height=500)
                fig.add_vline(x=overall_lastmonth_df[min_vendors]['fail_rate'].mean(), annotation_text="mean FR", line_dash="dash")
        
                st.plotly_chart(fig, height=500, use_container_width=True)
        # ===========================================================================================================================================
        line = "--------------------------------------------------------------"
        st.markdown(line)
        # ===========================================================================================================================================       
        """
        # ===========================================================================================================================================

        ### The dataframe to be used for multi-filter visual 
        lastmonth_df = self.main_overall_lastmonth_df      
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        if 'detailed_countries' not in st.session_state:
            st.session_state.detailed_countries = ["all"] + list(lastmonth_df["country_name"].unique())
        if 'detailed_cities' not in st.session_state:
            st.session_state.detailed_cities = ["all"] + list(lastmonth_df['city_name'].unique())
        if 'detailed_areas' not in st.session_state:
            st.session_state.detailed_areas = ["all"] + list(lastmonth_df['area_name'].unique())
        
        def detailed_location_area():
            if 'detailed_city' in st.session_state:
                st.session_state.detailed_cities = [city_option, "all"]
            else:
                st.session_state.detailed_cities = ["all"] + list(lastmonth_df[lastmonth_df["area_name"]==st.session_state.detailed_area]['city_name'].unique())
            
            if 'detailed_country' in st.session_state:
                st.session_state.detailed_countries = [country_option, "all"]
            else:
                st.session_state.detailed_countries = ["all"] + list(lastmonth_df[lastmonth_df["area_name"]==st.session_state.detailed_area]['country_name'].unique())
            
            if st.session_state.detailed_area=="all":
                if country_option:
                    city_options = list(lastmonth_df[lastmonth_df['country_name']==country_option]['city_name'].unique())
                    if city_option in city_options:
                        city_options.remove(city_option)
                    st.session_state.detailed_cities = [city_option, "all"] + city_options
                else:
                    city_options = list(lastmonth_df['city_name'].unique())
                    if city_option in city_options:
                        city_options.remove(city_option)
                    st.session_state.detailed_cities = [city_option, "all"] + city_options
            
        def detailed_location_city():
            st.session_state.detailed_areas = ["all"] + list(lastmonth_df[lastmonth_df["city_name"]==st.session_state.detailed_city]['area_name'].unique())
            
            if 'detailed_country' in st.session_state:
                st.session_state.detailed_countries = [country_option, "all"]
            else:
                st.session_state.detailed_countries = ["all"] + list(lastmonth_df[lastmonth_df["city_name"]==st.session_state.detailed_city]['country_name'].unique())
            
            if st.session_state.detailed_city=="all":
                country_list = list(lastmonth_df['country_name'].unique())
                if country_option in country_list:
                    country_list.remove(country_option)
                st.session_state.countries = [country_option, "all"] + country_list
                
            
        def detailed_location_country():
            st.session_state.detailed_cities = ["all"] + list(lastmonth_df[lastmonth_df["country_name"]==st.session_state.detailed_country]['city_name'].unique())
            st.session_state.detailed_areas = ["all"] + list(lastmonth_df[lastmonth_df["country_name"]==st.session_state.detailed_country]['area_name'].unique())

        
        with col1:
            country_option = self.create_selectbox_filter("Select Country", 
                                                           st.session_state.detailed_countries, 
                                                           "Select country for this visual", 
                                                           "detailed_country", on_change_function=detailed_location_country)
            if country_option=="all":
                country_option_flag = 0
            else:
                country_option_flag=1
            
            city_option = self.create_selectbox_filter("Select City", 
                                                        st.session_state.detailed_cities, 
                                                        "Select city for this visual", 
                                                        "detailed_city", on_change_function=detailed_location_city)
            if city_option=="all":
                city_option_flag = 0
            else:
                city_option_flag=1
            
            area_option = self.create_selectbox_filter("Select Area", 
                                                        st.session_state.detailed_areas, 
                                                        "Select area for this visual", 
                                                        "detailed_area", on_change_function=detailed_location_area)
            if area_option=="all":
                area_option_flag = 0
            else:
                area_option_flag=1
        
        max_orders = lastmonth_df['successful_order_count'].max()
        max_sessions = lastmonth_df['session_count'].max()
        max_gmv = int(lastmonth_df['agg_gmv_eur'].max())
        with col2:
            orders_limits_min = st.number_input(label="Show vendors with orders >=",
                                                 max_value=max_orders, 
                                                 value=0, 
                                                 step=1, 
                                                 key="detailed_orders")
            
            gmv_limits_min = st.number_input(label="Show vendors with GMV >=",
                                             max_value=max_gmv, 
                                             value=0, 
                                             step=1, 
                                             key="detailed_gmv")
            
            sessions_limits_min = st.number_input(label="Show vendors with sessions >=",
                                                  max_value=max_sessions, 
                                                  value=0, 
                                                  step=1, 
                                                  key="detailed_sessions")
            
        max_cvr = int(lastmonth_df['placed_CVR'].max())
        max_fr = int(lastmonth_df['fail_rate'].max())
        with col3:
            cvr_limits_min = st.number_input(label="Show vendors with CVR >=",
                                             max_value=max_cvr, 
                                             value=0, 
                                             step=1, 
                                             key="detailed_cvr")
            
            fr_limits_min = st.number_input(label="Show vendors with FR >=",
                                            max_value=max_fr, 
                                            value=0, 
                                            step=1, 
                                            key="detailed_fr")
            
            ratings_option = self.create_selectbox_filter("User Ratings", 
                                                           rating_labels, 
                                                           "User ratings 0-5", 
                                                           key="detailed_ratings")
            if ratings_option=="all":
                ratings_option_flag = 0
            else:
                ratings_option_flag=1
        
        
        detailed_selections = [ratings_option_flag, area_option_flag, city_option_flag, country_option_flag]
        selection_combinations = [list(i) for i in itertools.product([0, 1], repeat=4)]
        
        if detailed_selections==selection_combinations[0]:
            df = lastmonth_df
        elif detailed_selections==selection_combinations[1]:
            df = lastmonth_df[lastmonth_df['country_name']==country_option]
        elif detailed_selections==selection_combinations[2]:
            df = lastmonth_df[lastmonth_df['city_name']==city_option]
        elif detailed_selections==selection_combinations[3]:
            df = lastmonth_df[lastmonth_df['country_name']==country_option]
            df = df[df['city_name']==city_option]
        elif detailed_selections==selection_combinations[4]:
            df = lastmonth_df[lastmonth_df['area_name']==area_option]
        elif detailed_selections==selection_combinations[5]:
            df = lastmonth_df[lastmonth_df['country_name']==country_option]
            df = df[df['area_name']==area_option]
        elif detailed_selections==selection_combinations[6]:
            df = lastmonth_df[lastmonth_df['city_name']==city_option]
            df = df[df['area_name']==area_option]
        elif detailed_selections==selection_combinations[7]:
            df = lastmonth_df[lastmonth_df['country_name']==country_option]
            df = df[df['city_name']==city_option]
            df = df[df['area_name']==area_option]
        elif detailed_selections==selection_combinations[8]:
            df = lastmonth_df[lastmonth_df['rating_label']==ratings_option]
        elif detailed_selections==selection_combinations[9]:
            df = lastmonth_df[lastmonth_df['country_name']==country_option]
            df = df[df['rating_label']==ratings_option]
        elif detailed_selections==selection_combinations[10]:
            df = lastmonth_df[lastmonth_df['city_name']==city_option]
            df = df[df['rating_label']==ratings_option]
        elif detailed_selections==selection_combinations[11]:
            df = lastmonth_df[lastmonth_df['country_name']==country_option]
            df = df[df['city_name']==city_option]
            df = df[df['rating_label']==ratings_option]
        elif detailed_selections==selection_combinations[12]:
            df = lastmonth_df[lastmonth_df['area_name']==area_option]
            df = df[df['rating_label']==ratings_option]
        elif detailed_selections==selection_combinations[13]:
            df = lastmonth_df[lastmonth_df['country_name']==country_option]
            df = df[df['area_name']==area_option]
            df = df[df['rating_label']==ratings_option]
        elif detailed_selections==selection_combinations[14]:
            df = lastmonth_df[lastmonth_df['city_name']==city_option]
            df = df[df['area_name']==area_option]
            df = df[df['rating_label']==ratings_option]
        elif detailed_selections==selection_combinations[15]:
            df = lastmonth_df[lastmonth_df['country_name']==country_option]
            df = df[df['city_name']==city_option]
            df = df[df['area_name']==area_option]
            df = df[df['rating_label']==ratings_option]
            
        
        orders_condition = df['successful_order_count']>=orders_limits_min
        gmv_condition = df['agg_gmv_eur']>=gmv_limits_min
        sessions_condition = df['session_count']>=sessions_limits_min
        cvr_condition = df['placed_CVR']>=cvr_limits_min
        fr_condition = df['fail_rate']>=fr_limits_min
        
        df = df[orders_condition & gmv_condition & sessions_condition & cvr_condition & fr_condition]
        
        st.write("Vendors satisfying these conditions - " + str(len(df)))   
        st.dataframe(df)
        st.download_button(label="Download Vendor List", data=df.to_csv(), file_name="vendor_list.csv")
            
        
        
        # ===========================================================================================================================================
    
    """
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