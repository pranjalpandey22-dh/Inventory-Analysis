# -*- coding: utf-8 -*-
"""
Created on Thu Dec 23 15:18:41 2021

@author: pranjal.pandey
"""

# INSIGHTS PAGE

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

class Insights:
    
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
        monthbefore = month_names[self.main_overall_monthbefore_df['month'].max()]
        
        # ===========================================================================================================================================

        
        def safe_divide(n, d):
            try:
                return n/d
            except ZeroDivisionError:
                return 0
            
        # Sidebar ===================================================================================================================================
        
        with st.sidebar:
            ### last month from across the dashboard
            if 'countries' not in st.session_state:
                st.session_state.countries = ["all"] + list(self.main_overall_lastmonth_df["country_name"].unique())
            if 'cities' not in st.session_state:
                st.session_state.cities = ["all"] + list(self.main_overall_lastmonth_df['city_name'].unique())
            if 'areas' not in st.session_state:
                st.session_state.areas = ["all"] + list(self.main_overall_lastmonth_df['area_name'].unique())
            
            ### month before
            if 'countries_mb' not in st.session_state:
                st.session_state.countries_mb = ["all"] + list(self.main_overall_monthbefore_df["country_name"].unique())
            if 'cities_mb' not in st.session_state:
                st.session_state.cities_mb = ["all"] + list(self.main_overall_monthbefore_df['city_name'].unique())
            if 'areas_mb' not in st.session_state:
                st.session_state.areas_mb = ["all"] + list(self.main_overall_monthbefore_df['area_name'].unique())

            
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
                
                st.session_state.cities_mb = ["all"] + list(self.main_overall_monthbefore_df[self.main_overall_monthbefore_df["country_name"]==st.session_state.overall_country]['city_name'].unique())
                st.session_state.areas_mb = ["all"] + list(self.main_overall_monthbefore_df[self.main_overall_monthbefore_df["country_name"]==st.session_state.overall_country]['area_name'].unique())
              
            ### Country
            self.country_filter = self.create_selectbox_filter("Country", 
                                                               st.session_state.countries, 
                                                               "Filter by country", 
                                                               key="overall_country", 
                                                               on_change_function=filter_location_country)
            
            if self.country_filter=="all":
                self.country_filter = ""
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
                self.city_filter = ""
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
                self.area_filter = ""
                self.area_flag = 0
            else:
                self.area_flag=1
                
            ### Vertical
            self.vertical_filter = self.create_selectbox_filter("Vertical", 
                                                                verticals, 
                                                                "Select the Vertical to filter the data", 
                                                                key="overall_vertical")
            
            if self.vertical_filter=="all":
                self.vertical_filter = ""
                self.vertical_flag = 0
            else:
                self.vertical_flag = 1
                
            
            ### TGO Status 
            self.is_tgo_filter = self.create_selectbox_filter("IS_TGO", 
                                                              is_tgo, 
                                                              "Is the delivery fulfilled by Talabat?", 
                                                              key="overall_tgo")
            
            if self.is_tgo_filter=="all":
                self.is_tgo_filter = ""
                self.tgo_flag = 0
            else:
                self.tgo_flag=1
                      
            
            ### Ratings 
            self.ratings_filter = self.create_selectbox_filter("User Ratings", rating_labels, "User ratings 0-5", key="details_rating")
            
            if self.ratings_filter=="all":
                self.ratings_filter = ""
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
                
                st.session_state.countries_mb = ["all"] + list(self.main_overall_monthbefore_df["country_name"].unique())
                st.session_state.cities_mb = ["all"] + list(self.main_overall_monthbefore_df['city_name'].unique())
                st.session_state.areas_mb = ["all"] + list(self.main_overall_monthbefore_df['area_name'].unique())

            

            st.button('Reset filters', on_click=reset_all)
            
        
        # ===========================================================================================================================================

        ### The datafranme to be used for all the visuals
        overall_lastmonth_df = self.apply_sidebar_filter(self.main_overall_lastmonth_df)
        overall_monthbefore_df = self.apply_sidebar_filter(self.main_overall_monthbefore_df)

        
        
        ### Total Vendors
        total_vendors_lastmonth = len(self.main_overall_lastmonth_df['vendor_id'].unique())
        total_vendors_monthbefore = len(self.main_overall_monthbefore_df['vendor_id'].unique())
        def safe_divide(n, d):
            try:
                return n/d
            except ZeroDivisionError:
                return 0
        
        # ===========================================================================================================================================
        
        ### merged dataframe to be used for comparison
        merged_df = overall_lastmonth_df.merge(overall_monthbefore_df, 
                                               on='vendor_id', 
                                               how='left', 
                                               suffixes=('_lm', '_mb'))
        total_vendors = len(merged_df['vendor_id'].unique())
        
        
        # ===========================================================================================================================================

        ## Successful Orders
        st.subheader("Trend in successful orders: " + monthbefore + " to " + lastmonth)
        with st.container():
            merged_df['monthly_difference_orders'] = merged_df['successful_order_count_lm'] - merged_df['successful_order_count_mb'] 
            merged_df['monthly_difference_orders_percent'] = safe_divide(merged_df['monthly_difference_orders'], merged_df['successful_order_count_mb'])*100
            vendors_positive = len(merged_df[merged_df['monthly_difference_orders']>0]['vendor_id'].unique())
            vendors_negative = len(merged_df[merged_df['monthly_difference_orders']<0]['vendor_id'].unique())
            vendors_positive_percent = safe_divide(vendors_positive, total_vendors)*100
            vendors_negative_percent = safe_divide(vendors_negative, total_vendors)*100
            
            vendors_equal = merged_df[(merged_df['monthly_difference_orders']==0) & (merged_df['successful_order_count_lm']!=0)]
            
            no_activity_lm = merged_df['successful_order_count_lm']==0
            activity_mb = merged_df['successful_order_count_mb']>0
            vendors_no_activity_lm_but_activity_mb = len(merged_df[no_activity_lm & activity_mb]['vendor_id'].unique())
            
            total_successful_order_lastmonth = sum(overall_lastmonth_df['successful_order_count']) 
            total_successful_order_monthbefore = sum(overall_monthbefore_df['successful_order_count'])
        
            delta = total_successful_order_lastmonth - total_successful_order_monthbefore
            
            column1, column2 = st.columns([1, 3])
            with column1:
                st.write("Vendors with an increase in successful orders from " + monthbefore + " to " + lastmonth + " -")
                st.metric(label = "Vendor % with increase", 
                          value = "{:.2f}".format(vendors_positive_percent) + "%", 
                          delta=vendors_positive)
                st.write("Vendors with a decrease in successful orders -")
                st.metric(label = "Vendor % with decrease", 
                          value = "{:.2f}".format(vendors_negative_percent) + "%", 
                          delta=vendors_negative, 
                          delta_color="inverse")
                if vendors_no_activity_lm_but_activity_mb>0:
                    st.error("Vendors with activity in " + monthbefore + " but not in " + lastmonth + ": " + str(vendors_no_activity_lm_but_activity_mb))
                
            with column2:
                fig = px.histogram(data_frame=merged_df, 
                                   x="monthly_difference_orders_percent", 
                                   nbins=20000, 
                                   opacity=0.75, 
                                   range_x=(-200, 300), 
                                   labels={
                                       "monthly_difference_orders_percent": "Successful orders % change"}, 
                                   title="Successful orders % change: " + monthbefore + " to " + lastmonth)
                
                fig.update_traces(marker=dict(color='#FF5A00'))
                fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_layout(yaxis_title="Number of Vendors", height=500)
                        
                st.plotly_chart(fig, height=500, use_container_width=True)
            
            line = "--------------------------------------------------------------"
            st.markdown(line)
        # ===========================================================================================================================================

        ## GMV Comparison
        st.subheader("Trend in GMV: " + monthbefore + " to " + lastmonth)
        with st.container():
            merged_df['monthly_difference_gmv'] = merged_df['agg_gmv_eur_lm'] - merged_df['agg_gmv_eur_mb']
            merged_df['monthly_difference_gmv_percent'] = safe_divide(merged_df['monthly_difference_gmv'], merged_df['agg_gmv_eur_mb'])*100
            vendors_positive = len(merged_df[merged_df['monthly_difference_gmv']>0]['vendor_id'].unique())
            vendors_negative = len(merged_df[merged_df['monthly_difference_gmv']<0]['vendor_id'].unique())
            vendors_positive_percent = safe_divide(vendors_positive, total_vendors)*100
            vendors_negative_percent = safe_divide(vendors_negative, total_vendors)*100

            total_gmv_lastmonth = sum(overall_lastmonth_df['agg_gmv_eur']) 
            total_gmv_monthbefore = sum(overall_monthbefore_df['agg_gmv_eur'])
        
            delta = total_gmv_lastmonth - total_gmv_monthbefore
            
            column1, column2 = st.columns([1, 3])
            with column1:
                st.write("Vendors with an increase in GMV from " + monthbefore + " to " + lastmonth + " -")
                st.metric(label = "Vendor % with increase", 
                          value = "{:.2f}".format(vendors_positive_percent) + "%", 
                          delta=vendors_positive)
                st.write("Vendors with a decrease in GMV -")
                st.metric(label = "Vendor % with decrease", 
                          value = "{:.2f}".format(vendors_negative_percent) + "%", 
                          delta=vendors_negative, 
                          delta_color="inverse")
                if delta>0:
                    st.success("There is an increase in net GMV by " + prettify(millify(abs(delta), precision=2)) + " EUR.")
                else:
                    st.error("There is a decrease in net GMV by " + prettify(millify(abs(delta), precision=2)) + " EUR.")                  
            with column2:
                
                fig = px.histogram(data_frame=merged_df, 
                                   x="monthly_difference_gmv_percent", 
                                   nbins=20000,
                                   opacity=0.75, 
                                   range_x=(-200, 300), 
                                   labels={
                                       "monthly_difference_gmv_percent": "GMV % change"}, 
                                   title="GMV % change: " + monthbefore + " to " + lastmonth)
                
                fig.update_traces(marker=dict(color='#FF5A00'))
                fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_layout(yaxis_title="Number of Vendors", height=500)
                        
                st.plotly_chart(fig, height=500, use_container_width=True)
            
            line = "--------------------------------------------------------------"
            st.markdown(line)
        # ===========================================================================================================================================

        ## Sessions Comparison
        st.subheader("Trend in Sessions: " + monthbefore + " to " + lastmonth)
        with st.container():
            merged_df['monthly_difference_sessions'] = merged_df['session_count_lm'] - merged_df['session_count_mb']
            merged_df['monthly_difference_sessions_percent'] = safe_divide(merged_df['monthly_difference_sessions'], merged_df['session_count_mb'])*100
            vendors_positive = len(merged_df[merged_df['monthly_difference_sessions']>0]['vendor_id'].unique())
            vendors_negative = len(merged_df[merged_df['monthly_difference_sessions']<0]['vendor_id'].unique())
            vendors_positive_percent = safe_divide(vendors_positive, total_vendors)*100
            vendors_negative_percent = safe_divide(vendors_negative, total_vendors)*100

            total_sessions_lastmonth = sum(overall_lastmonth_df['session_count']) 
            total_sessions_monthbefore = sum(overall_monthbefore_df['session_count'])
        
            delta = total_sessions_lastmonth - total_sessions_monthbefore
            
            column1, column2 = st.columns([1, 3])
            with column1:
                st.write("Vendors with an increase in sessions from " + monthbefore + " to " + lastmonth + " -")
                st.metric(label = "Vendor % with increase", 
                          value = "{:.2f}".format(vendors_positive_percent) + "%", 
                          delta=vendors_positive)
                st.write("Vendors with a decrease in sessions -")
                st.metric(label = "Vendor % with decrease", 
                          value = "{:.2f}".format(vendors_negative_percent) + "%", 
                          delta=vendors_negative, 
                          delta_color="inverse")
                if delta>0:
                    st.success("There is an increase in net app sesions by " + prettify(millify(abs(delta), precision=2)) + ".")
                else:
                    st.error("There is a decrease in net app sessions by " + prettify(millify(abs(delta), precision=2)) + ".")             
            with column2:
                fig = px.histogram(data_frame=merged_df, 
                                   x="monthly_difference_sessions_percent", 
                                   nbins=20000,
                                   opacity=0.75, 
                                   range_x=(-300, 500), 
                                   labels={
                                       "monthly_difference_sessions_percent": "Sessions % change"}, 
                                   title="Sessions % change: " + monthbefore + " to " + lastmonth)
                
                fig.update_traces(marker=dict(color='#FF5A00'))
                fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_layout(yaxis_title="Number of Vendors", height=500)
                        
                st.plotly_chart(fig, height=500, use_container_width=True)
                
            line = "--------------------------------------------------------------"
            st.markdown(line)
        # ===========================================================================================================================================

        ## CVR Comparison
        st.subheader("Trend in CVR: " + monthbefore + " to " + lastmonth)
        with st.container():
            monthly_difference_cvr = merged_df['placed_CVR_lm'] - merged_df['placed_CVR_mb']
            merged_df['monthly_difference_cvr_percent'] = safe_divide(monthly_difference_cvr, merged_df['placed_CVR_mb'])*100
            vendors_positive = len(merged_df[merged_df['monthly_difference_cvr_percent']>0]['vendor_id'].unique())
            vendors_negative = len(merged_df[merged_df['monthly_difference_cvr_percent']<0]['vendor_id'].unique())
            vendors_positive_percent = safe_divide(vendors_positive, total_vendors)*100
            vendors_negative_percent = safe_divide(vendors_negative, total_vendors)*100

            cvr_lastmonth = overall_lastmonth_df['placed_CVR'].median()
            cvr_monthbefore = overall_monthbefore_df['placed_CVR'].median()
        
            delta = safe_divide((cvr_lastmonth - cvr_monthbefore), cvr_monthbefore)*100
            
            column1, column2 = st.columns([1, 3])
            with column1:
                st.write("Vendors with an increase in CVR from " + monthbefore + " to " + lastmonth + " -")
                st.metric(label = "Vendor % with increase", 
                          value = "{:.2f}".format(vendors_positive_percent) + "%", 
                          delta=vendors_positive)
                st.write("Vendors with a decrease in CVR -")
                st.metric(label = "Vendor % with decrease", 
                          value = "{:.2f}".format(vendors_negative_percent) + "%", 
                          delta=vendors_negative, 
                          delta_color="inverse")
                if delta>0:
                    st.success("There is an increase in median CVR by " + prettify(millify(abs(delta), precision=2)) + "%.")
                else:
                    st.error("There is a decrease in median CVR by " + prettify(millify(abs(delta), precision=2)) + "%.")             
            with column2:
                fig = px.histogram(data_frame=merged_df, 
                                   x="monthly_difference_cvr_percent", 
                                   nbins=20000,
                                   opacity=0.75, 
                                   range_x=(-150, 500), 
                                   labels={
                                       "monthly_difference_cvr_percent": "CVR % change"}, 
                                   title="CVR % change: " + monthbefore + " to " + lastmonth)
                
                fig.update_traces(marker=dict(color='#FF5A00'))
                fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_layout(yaxis_title="Number of Vendors", height=500)
                        
                st.plotly_chart(fig, height=500, use_container_width=True)
        
            line = "--------------------------------------------------------------"
            st.markdown(line)
        # ===========================================================================================================================================

        ## Fail Rate Comparison
        st.subheader("Trend in Net Fail Rate: " + monthbefore + " to " + lastmonth)
        with st.container():
            monthly_difference_fail_rate = merged_df['fail_rate_lm'] - merged_df['fail_rate_mb']
            merged_df['monthly_difference_fail_rate_percent'] = safe_divide(monthly_difference_cvr, merged_df['fail_rate_mb'])*100
            vendors_positive = len(merged_df[merged_df['monthly_difference_fail_rate_percent']>0]['vendor_id'].unique())
            vendors_negative = len(merged_df[merged_df['monthly_difference_fail_rate_percent']<0]['vendor_id'].unique())
            vendors_positive_percent = safe_divide(vendors_positive, total_vendors)*100
            vendors_negative_percent = safe_divide(vendors_negative, total_vendors)*100

            fail_rate_lastmonth = overall_lastmonth_df['fail_rate'].median()
            fail_rate_monthbefore = overall_monthbefore_df['fail_rate'].median()
        
            delta = safe_divide((fail_rate_lastmonth - fail_rate_monthbefore), fail_rate_monthbefore)*100
            
            column1, column2 = st.columns([1, 3])
            with column1:
                st.write("Vendors with an increase in Net Fail Rate from " + monthbefore + " to " + lastmonth + " -")
                st.metric(label = "Vendor % with increase", 
                          value = "{:.2f}".format(vendors_positive_percent) + "%", 
                          delta=vendors_positive, 
                          delta_color="inverse")
                st.write("Vendors with a decrease in Net Fail Rate -")
                st.metric(label = "Vendor % with decrease", 
                          value = "{:.2f}".format(vendors_negative_percent) + "%", 
                          delta=vendors_negative)
                if delta>0:
                    st.error("There is an increase in median Net Fail Rate by " + prettify(millify(abs(delta), precision=2)) + "%.")
                else:
                    st.success("There is a decrease in median Net Fail Rate by " + prettify(millify(abs(delta), precision=2)) + "%.")             
            with column2:
                fig = px.histogram(data_frame=merged_df, 
                                   x="monthly_difference_fail_rate_percent", 
                                   nbins=20000,
                                   opacity=0.75, 
                                   range_x=(-500, 500), 
                                   labels={
                                       "monthly_difference_fail_rate_percent": "Net Fail Rate % change"}, 
                                   title="Net Fail Rate % change: " + monthbefore + " to " + lastmonth)
                
                fig.update_traces(marker=dict(color='#FF5A00'))
                fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
                fig.update_layout(yaxis_title="Number of Vendors", height=500)
                        
                st.plotly_chart(fig, height=500, use_container_width=True)
   
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
    
    def apply_sidebar_filter(self, overall_df):
        """
        This method applies sidebar filter to the main sql result

        Parameters
        ----------
        overall_df : TYPE main sql result - pandas dataframe
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
        
        selected_combination = []
        for combination in all_possible_combinations:
            product = [ele1*ele2 for ele1, ele2 in zip(selections, combination)]
            if sum(product)==5:
                selected_combination = combination
        
        if selections==all_possible_combinations[0]: 
            return overall_df
        elif selections==all_possible_combinations[1]:
            return overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
        elif selections==all_possible_combinations[2]:
            return overall_df[overall_df["vertical"]==self.vertical_filter]
        elif selections==all_possible_combinations[3]: 
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            return overall_df
        elif selections==all_possible_combinations[4]: 
            return overall_df[overall_df["country_name"]==self.country_filter]
        elif selections==all_possible_combinations[5]:
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            return overall_df
        elif selections==all_possible_combinations[6]:
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            return overall_df
        elif selections==all_possible_combinations[7]:
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            return overall_df
        elif selections==all_possible_combinations[8]:
            return overall_df[overall_df["city_name"]==self.city_filter]
        elif selections==all_possible_combinations[9]:
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            return overall_df 
        elif selections==all_possible_combinations[10]:
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            return overall_df
        elif selections==all_possible_combinations[11]:
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            return overall_df
        elif selections==all_possible_combinations[12]:
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            return overall_df
        elif selections==all_possible_combinations[13]:
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            return overall_df
        elif selections==all_possible_combinations[14]:
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            return overall_df
        elif selections==all_possible_combinations[15]:
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            return overall_df
        elif selections==all_possible_combinations[16]:
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[17]:
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[18]:
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[19]:
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[20]:
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[21]:
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[22]:
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[23]:
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[24]:
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[25]:
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[26]:
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[27]:
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[28]:
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[29]:
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[30]:
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[31]:
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[32]: 
            return overall_df[overall_df["rating_label"]==self.ratings_filter]
        elif selections==all_possible_combinations[33]:
            overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            return overall_df
        elif selections==all_possible_combinations[34]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            return overall_df
        elif selections==all_possible_combinations[35]: 
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            return overall_df
        elif selections==all_possible_combinations[36]: 
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            return overall_df
        elif selections==all_possible_combinations[37]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            return overall_df
        elif selections==all_possible_combinations[38]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            return overall_df
        elif selections==all_possible_combinations[39]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            return overall_df
        elif selections==all_possible_combinations[40]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df[overall_df["city_name"]==self.city_filter]
            return overall_df
        elif selections==all_possible_combinations[41]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            return overall_df 
        elif selections==all_possible_combinations[42]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            return overall_df
        elif selections==all_possible_combinations[43]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            return overall_df
        elif selections==all_possible_combinations[44]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            return overall_df
        elif selections==all_possible_combinations[45]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            return overall_df
        elif selections==all_possible_combinations[46]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            return overall_df
        elif selections==all_possible_combinations[47]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            return overall_df
        elif selections==all_possible_combinations[48]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[49]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[50]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[51]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[52]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[53]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[54]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[55]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[56]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[57]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[58]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[59]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[60]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[61]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[62]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
        elif selections==all_possible_combinations[63]:
            overall_df = overall_df[overall_df["rating_label"]==self.ratings_filter]
            overall_df = overall_df[overall_df["is_tgo"]==boolean_mask[self.is_tgo_filter]]
            overall_df = overall_df[overall_df["vertical"]==self.vertical_filter]
            overall_df = overall_df[overall_df["country_name"]==self.country_filter]
            overall_df = overall_df[overall_df["city_name"]==self.city_filter]
            overall_df = overall_df[overall_df["area_name"]==self.area_filter]
            return overall_df
 
    
    def load_css(self, file_name):
        with open(file_name) as f:
            st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)   