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

class Overall:
    
    def __init__(self, service_account_client):
        self.client = service_account_client
        
    def main(self):
        
        # vertical filter ===========================================================================================================================
        verticals = ["all", "food", "grocery", "cosmetics", "pet shop", 
                     "pharmacy", "flowers", "electronics"]
        
        
        # ===========================================================================================================================================
        
        # is_active filter ==========================================================================================================================
        
        is_active = ["all", "TRUE", "FALSE"]
        
             
        # ===========================================================================================================================================
        
        # is_tgo filter =============================================================================================================================
        
        is_tgo = ["all", "TRUE", "FALSE"]
        
            
        # ===========================================================================================================================================
        
        ## Sidebar Filters ==========================================================================================================================
        
        with st.sidebar:
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
            
            
            ### Active Status
            self.is_active_filter = self.create_selectbox_filter("IS_ACTIVE", 
                                                                 is_active, 
                                                                 "Is the vendor active?", 
                                                                 key="overall_active")
            
            if self.is_active_filter=="all":
                self.is_active_filter = ""
                self.active_flag = 0
            else:
                self.active_flag=1
            
            
            ### TGO Status
            emp = st.empty()
            self.is_tgo_filter = self.create_selectbox_filter("IS_TGO", 
                                                              is_tgo, 
                                                              "Is the delivery fulfilled by Talabat?", 
                                                              key="overall_tgo")
            
            if self.is_tgo_filter=="all":
                self.is_tgo_filter = ""
                self.tgo_flag = 0
            else:
                #st.session_state.overall_tgo=self.is_tgo_filter
                self.tgo_flag=1
        
            
            ### Reset Button
            def reset_all():
                st.session_state.overall_vertical="all"
                st.session_state.overall_tgo="all"
                st.session_state.overall_active="all"
            

            st.button('Reset filters', on_click=reset_all)
            
            
        
        # ===========================================================================================================================================
        
        ## The in-page filters ======================================================================================================================
        
        filter1, filter2, filter3 = st.columns(3)
        
        ### Country
        countries_iso = ["all", "JO", "AE", "SA", "EG", "KW", "QA", "BH", "IQ", "OM", "LB"]
        countries = ["all", "Jordan", "United Arab Emirates", "Saudi Arabia", "Egypt", "Kuwait", 
                     "Qatar", "Bahrain", "IRQ", "Oman", "Lebanon"]
        
        with filter1:
            self.country_filter = self.create_selectbox_filter("Country", 
                                                               countries, 
                                                               "Filter by country", 
                                                               key="overall_country")
        
        if self.country_filter=="all":
            self.country_filter = ""
            self.country_flag = 0
        else:
            self.country_flag=1
        
        
        
        
        # ===========================================================================================================================================
        
        num_of_vendors_with_filters = self.run_query(self.apply_filter_sidebar(self.sql_num_of_vendors()))
        
        st.write("Total Number of vendors with filters: ")
        for row in num_of_vendors_with_filters:
            st.metric(label="Total number of Vendors", value=row["f0_"])
        
        
    def create_selectbox_filter(self, label, options, help_text, key):
        """
        This method creates a selectbox filter - dropdown
        """
        selectbox_filter = st.selectbox(label, 
                              options=options, 
                              help=help_text, 
                              key=key)
        return selectbox_filter
        
    
    def sql_num_of_vendors(self):
        """
        This method contains the SQL query -> Number of vendors
        """
        sql_query = (
            "SELECT "
            "COUNT(vendor_id) "
            "FROM `bta---talabat.data_platform.dim_vendor`")
        return str(sql_query)
                        
    
    
    
    
    def apply_filter_sidebar(self, sql_query):
        """
        This method adds the WHERE clause for filters

        Parameters
        ----------
        sql_query : TYPE string
            DESCRIPTION
            The query to which WHERE clause is appended to
        Returns
        -------
        Query with filters

        """
        vertical_clause = "vertical = " + "'"  + self.vertical_filter + "'" 
        active_clause = "is_active = " + self.is_active_filter
        tgo_clause = "is_tgo = " + self.is_tgo_filter
        
        clause_flags = [self.vertical_flag, self.active_flag, self.tgo_flag]
        clauses = [vertical_clause, active_clause, tgo_clause]
        
        ## Filtering logic
        self.where_clause = " WHERE "
        first_clause_added = False
        clause_count = 0
        for clause_flag, clause in zip(clause_flags, clauses):
            clause_count+=1
            if clause_flag==1:
                if first_clause_added==True:
                    self.where_clause = self.where_clause + " AND " + clause
                else:
                    self.where_clause = self.where_clause + " " + clause
                    first_clause_added = True
                if (clause_count==len(clauses)):
                    if (first_clause_added==True):
                        st.write(sql_query + self.where_clause)
                        return sql_query + self.where_clause
                    else:
                        return sql_query
                else:
                    continue
            else:
                if (clause_count==len(clauses)):
                    if (first_clause_added==True):
                        st.write(sql_query + self.where_clause)
                        return sql_query + self.where_clause
                    else:
                        return sql_query
                else:
                    continue
                
        # Just so that in case there is some error, the method returns something by default
        return sql_query
            
    
    def apply_filter_in_page(self, sql_query):
        """
        This method adds the WHERE clause for filters

        Parameters
        ----------
        sql_query : TYPE string
            DESCRIPTION
            The query to which WHERE clause is appended to
        Returns
        -------
        Query with filters

        """
        vertical_clause = "vertical = " + "'"  + self.vertical_filter + "'" 
        active_clause = "is_active = " + self.is_active_filter
        tgo_clause = "is_tgo = " + self.is_tgo_filter
        
        clause_flags = [self.vertical_flag, self.active_flag, self.tgo_flag]
        clauses = [vertical_clause, active_clause, tgo_clause]
        
        ## Filtering logic
        self.where_clause = " WHERE "
        first_clause_added = False
        clause_count = 0
        for clause_flag, clause in zip(clause_flags, clauses):
            clause_count+=1
            if clause_flag==1:
                if first_clause_added==True:
                    self.where_clause = self.where_clause + " AND " + clause
                else:
                    self.where_clause = self.where_clause + " " + clause
                    first_clause_added = True
                if (clause_count==len(clauses)):
                    if (first_clause_added==True):
                        st.write(sql_query + self.where_clause)
                        return sql_query + self.where_clause
                    else:
                        return sql_query
                else:
                    continue
            else:
                if (clause_count==len(clauses)):
                    if (first_clause_added==True):
                        st.write(sql_query + self.where_clause)
                        return sql_query + self.where_clause
                    else:
                        return sql_query
                else:
                    continue
                
        # Just so that in case there is some error, the method returns something by default
        return sql_query
                
    
    
    # Uses st.cache to only rerun when the query changes or after 10 min.
    @st.cache(ttl=600, hash_funcs={bigquery.client.Client: lambda _: None})
    def run_query(self, query):
        """
        This method runs SQL queries
        """
        query_job = self.client.query(query)
        rows_raw = query_job.result()
        # Convert to list of dicts. Required for st.cache to hash the return value.
        rows = [dict(row) for row in rows_raw]
        return rows
    
    @st.cache(ttl=600, hash_funcs={bigquery.client.Client: lambda _: None})
    def run_query_metric(self, query):
        """
        This method runs SQL queries
        """
        query_job = self.client.query(query)
        rows_raw = query_job.result()
        # Convert to list of dicts. Required for st.cache to hash the return value.
        #rows = [dict(row) for row in rows_raw]
        #return rows
        return rows_raw
        
    