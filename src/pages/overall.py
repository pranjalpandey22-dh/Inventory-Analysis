# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 13:41:35 2021

@author: pranjal.pandey
"""

# OVERALL PAGE

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

class Overall:
    
    def __init__(self, main_overall_lastmonth_df, main_overall_monthbefore_df):
        #self.client = service_account_client
        self.main_overall_lastmonth_df = main_overall_lastmonth_df
        self.main_overall_monthbefore_df = main_overall_monthbefore_df
        
    def main(self):
        
        # Global Variables ==========================================================================================================================
        
        ## CSS
        self.load_css("style/css/style.css")
        
        
        ## Metric Types
        self.valid_metric_types = ["vendors", "orders"]
                
        
        # vertical filter ===========================================================================================================================
        verticals = ["all", "food", "grocery", "cosmetics", "pet shop", 
                     "pharmacy", "flowers", "electronics"]
        
        # ===========================================================================================================================================
        
        # is_tgo filter =============================================================================================================================
        
        is_tgo = ["all", "TRUE", "FALSE"]
        
            
        # ===========================================================================================================================================
        
        # months filter =============================================================================================================================
        
        month_names = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 
                       7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}  
        
        lastmonth = month_names[self.main_overall_lastmonth_df['month'].max()]
        monthbefore = month_names[self.main_overall_monthbefore_df['month'].max()]

        ## Sidebar Filters ==========================================================================================================================
        
        with st.sidebar:
            
            plot_type = st.radio("Original values or Cumulative values?", 
                     ("Original", "Cumulative"), 
                     help="Original values v/s Cumulative values?")
            
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
                if 'overall_city' in st.session_state:
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
                if 'overall_country' in st.session_state:
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
                      
       
            ### Reset Button
            def reset_all():
                st.session_state.overall_vertical="all"
                st.session_state.overall_tgo="all"
                st.session_state.overall_active="all"
                st.session_state.overall_country="all"
                st.session_state.overall_city="all"
                st.session_state.overall_area="all"
                
                self.area_flag = 0
                self.city_flag = 0
                self.country_flag = 0
                self.vertical_flag = 0
                self.tgo_flag = 0
                
                st.session_state.countries = ["all"] + list(self.main_overall_lastmonth_df["country_name"].unique())
                st.session_state.cities = ["all"] + list(self.main_overall_lastmonth_df['city_name'].unique())
                st.session_state.areas = ["all"] + list(self.main_overall_lastmonth_df['area_name'].unique())
 
                st.session_state.countries_mb = ["all"] + list(self.main_overall_monthbefore_df["country_name"].unique())
                st.session_state.cities_mb = ["all"] + list(self.main_overall_monthbefore_df['city_name'].unique())
                st.session_state.areas_mb = ["all"] + list(self.main_overall_monthbefore_df['area_name'].unique())

            

            st.button('Reset filters', on_click=reset_all)

        # ===========================================================================================================================================
        
        ### The dataframe to be used for all the visuals
        overall_lastmonth_df = self.apply_sidebar_filter(self.main_overall_lastmonth_df)
        overall_monthbefore_df = self.apply_sidebar_filter(self.main_overall_monthbefore_df)

        # ===========================================================================================================================================
        ## Page Columns
        # ===========================================================================================================================================
        
        column1, column2 = st.columns(2)
        
        # ===========================================================================================================================================
        # ===========================================================================================================================================
        ## KPIs and Metrics
        # ===========================================================================================================================================
        
        ### Number of Vendors
                
        num_of_vendors_with_filters_lastmonth = len(overall_lastmonth_df["vendor_id"].unique())
        num_of_vendors_with_filters_monthbefore = len(overall_monthbefore_df["vendor_id"].unique())
        delta = num_of_vendors_with_filters_lastmonth - num_of_vendors_with_filters_monthbefore
        with column1: 
            st.metric(label="Active Vendors from " + lastmonth, 
                      value=prettify(num_of_vendors_with_filters_lastmonth), 
                      delta=prettify(delta) + " from " + monthbefore)
            
        
        # ===========================================================================================================================================
        
        ### Vendor Chains with 2 or more vendors
        vendor_chain_df = overall_lastmonth_df[["vendor_id", "chain_id"]]
        chains_with_2_or_more_vendors = sum(vendor_chain_df.groupby('chain_id').agg('nunique')['vendor_id']>=2)
        total_chains = len(vendor_chain_df.chain_id.unique())
        
        vendor_chain_df_monthbefore = overall_monthbefore_df[["vendor_id", "chain_id"]]
        chains_with_2_or_more_vendors_monthbefore = sum(vendor_chain_df_monthbefore.groupby('chain_id').agg('nunique')['vendor_id']>=2)
        
        delta = chains_with_2_or_more_vendors - chains_with_2_or_more_vendors_monthbefore
        
        def safe_divide(n, d):
            try:
                return n/d
            except ZeroDivisionError:
                return 0
            
        percent_ouput = safe_divide(chains_with_2_or_more_vendors, total_chains)*100
        
        with column2:
            st.metric(label="Chains with 2 or more vendors", 
                      value=prettify(chains_with_2_or_more_vendors) +" (" + str("{:.2f}".format(percent_ouput))+ "%) ", 
                      delta=prettify(delta) + " from " + monthbefore)
        
        # ===========================================================================================================================================     

        if plot_type=="Original":
                   
            # =======================================================================================================================================
            
            ### Successful Orders - LastMonth/MTD/YTD
            
            fig = px.histogram(data_frame=overall_lastmonth_df,  
                               x="successful_order_count", 
                               #nbins=100, 
                               title="Successful orders in " + lastmonth,
                               labels={
                                   "successful_order_count": "Successful Orders over " + lastmonth}, 
                               opacity=0.8, 
                               color_discrete_sequence=['#FF5A00'], 
                               range_x=(0, 2000))
            fig.update_layout(yaxis_title="Number of Vendors", height=500, title_font_family="sans-serif", title_font_size=18, title_font_color="black")
            fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
            fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
            fig.add_vline(x=overall_lastmonth_df['successful_order_count'].mean(), annotation_text="mean orders", line_dash="dash")
            st.plotly_chart(fig, height=500, use_container_width=True)
            
            # =======================================================================================================================================
    
            # =======================================================================================================================================
            
            ### GMV - GMV From Last Month
            
            #### Histogram / Cumulative Sum Plot  
            fig = px.histogram(data_frame=overall_lastmonth_df, 
                               x="agg_gmv_eur", 
                               opacity=0.75, 
                               range_x=(0, 50000), 
                               labels={
                                   "agg_gmv_eur": "GMV from " + lastmonth, 
                                   "count": "Number of Vendors"}, 
                               title="GMV contribution in " + lastmonth, )
                               #cumulative=True)
            
            fig.update_traces(marker=dict(color='#FF5A00'))
            fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
            fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
            fig.update_layout(yaxis_title="Number of Vendors", height=500, title_font_family="sans-serif", title_font_size=18, title_font_color="black")
            fig.add_vline(x=overall_lastmonth_df['agg_gmv_eur'].mean(), annotation_text="mean GMV", line_dash="dash")
        
            st.plotly_chart(fig, height=500, use_container_width=True)    
            # =======================================================================================================================================  
    
            # =======================================================================================================================================
            
            ### Session Distribution
            fig = go.Figure()
            fig.add_trace(go.Histogram( 
                               x=overall_lastmonth_df["session_count"], 
                               marker_color='#FF5A00', 
                               name='Sessions Distribution'))
            fig.update_xaxes(range=[0, 10000])
            fig.update_layout(#barmode='overlay', 
                              title_text="Sessions received from " + lastmonth, 
                              xaxis_title="Sessions over " + lastmonth, 
                              yaxis_title="Number of Vendors",
                              height=500, title_font_family="sans-serif", 
                              title_font_size=18, 
                              title_font_color="black")
            fig.update_traces(opacity=0.75)
            fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
            fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
            fig.add_vline(x=overall_lastmonth_df['session_count'].mean(), annotation_text="mean sessions", line_dash="dash")

            st.plotly_chart(fig, height=500, use_container_width=True)
    
            # =======================================================================================================================================
            
            ### CVR - LastMonth/MTD/YTD
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=overall_lastmonth_df["placed_CVR"],
                               marker_color='#FF5A00', 
                               name='Placed Order Placement CVR'))
            fig.update_xaxes(range=[0, 45])
            fig.update_layout(#barmode='overlay', 
                              title_text="CVR from "+ lastmonth, 
                              xaxis_title="CVR over " + lastmonth, 
                              yaxis_title="Number of Vendors",
                              height=500, 
                              title_font_family="sans-serif", 
                              title_font_size=18, 
                              title_font_color="black")
            fig.update_traces(opacity=0.75)
            fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
            fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
            fig.add_vline(x=overall_lastmonth_df['placed_CVR'].mean(), annotation_text="mean CVR", line_dash="dash")

            st.plotly_chart(fig, height=500, use_container_width=True)
            
            # =======================================================================================================================================
            ## Page Columns
            # =======================================================================================================================================
            
            ### Fail Rates 
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=overall_lastmonth_df["fail_rate"], #failrate_last6months_df["fail_rate"],
                                       xbins=dict(
                                           start=0.0, 
                                           size=0.5),
                                       opacity=0.8, 
                                       marker_color='#FF5A00'))
            fig.update_xaxes(range=[0, 40])
            fig.update_layout(title_text="Net Fail Rates from " + lastmonth, 
                              xaxis_title="Net Fail Rate over " + lastmonth, 
                              yaxis_title="Number of Vendors", 
                              height=500, 
                              title_font_family="sans-serif", 
                              title_font_size=18, 
                              title_font_color="black")
            fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
            fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5) 
            fig.add_vline(x=overall_lastmonth_df['fail_rate'].mean(), annotation_text="mean NFR", line_dash="dash")

            st.plotly_chart(fig, use_container_width=True, height=500)
            
            # ======================================================================================================================================= 
        
        if plot_type=="Cumulative":
            # =======================================================================================================================================
            ## KPIs and Metrics
            # =======================================================================================================================================
            ### Successful Orders - LastMonth/MTD/YTD
            
            fig = px.histogram(data_frame=overall_lastmonth_df, #order_lastmonth_df, 
                               x="successful_order_count", 
                               #nbins=100, 
                               title="Successful orders in " + lastmonth, 
                               labels={
                                   "successful_order_count": "Successful Orders over " + lastmonth}, 
                               opacity=0.8, 
                               color_discrete_sequence=['#FF5A00'], 
                               range_x=(0, 2000), 
                               cumulative=True)
            fig.update_layout(yaxis_title="Number of Vendors", height=500, title_font_family="sans-serif", title_font_size=18, title_font_color="black")
            fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
            fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
            st.plotly_chart(fig, height=500, use_container_width=True)
            
            # =======================================================================================================================================
                
            #### Histogram / Cumulative Sum Plot  
            """
            fig = px.ecdf(data_frame=overall_lastmonth_df, #v_gmv_df, 
                          x="cumulative_gmv_sum", 
                          ecdfnorm=None,
                          markers=True, 
                          labels={
                              "cumulative_gmv_sum": "Cumulative GMV from last month", 
                              "count": "Number of Vendors"}, 
                          title="How many vendors contributed to how much GMV last month?")
            """
            fig = px.histogram(data_frame=overall_lastmonth_df, 
                               x="agg_gmv_eur", 
                               opacity=0.75, 
                               range_x=(0, 50000), 
                               labels={
                                   "agg_gmv_eur": "GMV from " + lastmonth, 
                                   "count": "Number of Vendors"}, 
                               title="GMV contribution in" + lastmonth, 
                               cumulative=True)
                               #cumulative=True)
            
            fig.update_traces(marker=dict(color='#FF5A00'))
            fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
            fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
            fig.update_layout(yaxis_title="Number of Vendors", height=500, title_font_family="sans-serif", title_font_size=18, title_font_color="black")
                    
            st.plotly_chart(fig, height=500, use_container_width=True)    
            # =======================================================================================================================================
            
            ### Session Distribution
            fig = go.Figure()
            fig.add_trace(go.Histogram( 
                               x=overall_lastmonth_df["session_count"], 
                               marker_color='#FF5A00', 
                               name='Sessions Distribution', 
                               cumulative_enabled=True))
            fig.update_xaxes(range=[0, 10000])
            fig.update_layout(#barmode='overlay', 
                              title_text="Sessions received from " + lastmonth, 
                              xaxis_title="Sessions from " + lastmonth, 
                              yaxis_title="Number of Vendors",
                              height=500, 
                              title_font_family="sans-serif", 
                              title_font_size=18, 
                              title_font_color="black")
            fig.update_traces(opacity=0.75)
            fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
            fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
            
            st.plotly_chart(fig, height=500, use_container_width=True)
            # =======================================================================================================================================
    
            #### placed CVR
            fig = go.Figure()
            fig.add_trace(go.Histogram( 
                               x=overall_lastmonth_df["placed_CVR"],  
                               #title="Vendors and their CVR", 
                               #labels={
                               #    "placed_CVR": "Placed Order Placement CVR"}
                               #opacity=0.8,  
                               marker_color='#FF5A00', 
                               name='Placed Order Placement CVR', 
                               cumulative_enabled=True))
            fig.update_xaxes(range=[0, 45])
            fig.update_layout(#barmode='overlay', 
                              title_text="CVR from " + lastmonth, 
                              xaxis_title="CVR over " + lastmonth, 
                              yaxis_title="Number of Vendors",
                              height=500, 
                              title_font_family="sans-serif", 
                              title_font_size=18, 
                              title_font_color="black")
            fig.update_traces(opacity=0.75)
            fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
            fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
            
            st.plotly_chart(fig, height=500, use_container_width=True)
            
            # =======================================================================================================================================
            
            ### Fail Rates
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=overall_lastmonth_df["fail_rate"],
                                       xbins=dict(
                                           start=0.0, 
                                           size=0.5),
                                       opacity=0.8, 
                                       marker_color='#FF5A00', 
                                       cumulative_enabled=True))
            fig.update_xaxes(range=[0, 40])
            fig.update_layout(title_text="Net Fail Rates from " + lastmonth, 
                              xaxis_title="Net Fail Rate over " + lastmonth, 
                              yaxis_title="Number of Vendors", 
                              height=500, 
                              title_font_family="sans-serif", 
                              title_font_size=18, 
                              title_font_color="black")
            fig.update_xaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)
            fig.update_yaxes(showspikes=True, spikecolor="orange", showgrid=True, gridwidth=0.5)        
            st.plotly_chart(fig, use_container_width=True, height=500)
            

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
        selections = [self.area_flag, self.city_flag, self.country_flag, 
                      self.vertical_flag, self.tgo_flag]
        
        all_possible_combinations = [list(i) for i in itertools.product([0, 1], repeat=5)]
        
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
        
        
    def load_css(self, file_name):
        with open(file_name) as f:
            st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)