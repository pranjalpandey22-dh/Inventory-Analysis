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

class Details:
    
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
        
        # online_payment filter =====================================================================================================================
        
        is_online_payment_accepted = ["all", "TRUE", "FALSE"]
        
            
        # ===========================================================================================================================================
        
        # Sidebar ===================================================================================================================================
        
        with st.sidebar:
            self.vertical_filter = self.create_selectbox_filter("Vertical", verticals, "Select the Vertical to filter the data", key="details_vertical")
            
            if self.vertical_filter=="all":
                self.vertical_filter = ""
                self.vertical_flag = 0
            else:
                self.vertical_flag = 1
            
            self.is_active_filter = self.create_selectbox_filter("IS_ACTIVE", is_active, "Is the vendor active?", key="details_vertical")
            
            if self.is_active_filter=="all":
                self.is_active_filter = ""
                self.active_flag = 0
            else:
                self.active_flag=1
            
                
            self.is_tgo_filter = self.create_selectbox_filter("IS_TGO", is_tgo, "Is the delivery fulfilled by Talabat?", key="details_vertical")
            
            if self.is_tgo_filter=="all":
                self.is_tgo_filter = ""
                self.tgo_flag = 0
            else:
                self.tgo_flag=1
                
            
            self.is_online_payment_accepted_filter = self.create_selectbox_filter("Online Payment Accepted?", is_online_payment_accepted, "Is online payment accpeted?", key="details_vertical")
            
            if self.is_online_payment_accepted_filter=="all":
                self.is_online_payment_accepted_filter = ""
                self.is_online_payment_accepted_flag = 0
            else:
                self.is_online_payment_accepted_flag=1
        
        
        # ===========================================================================================================================================
        
        num_of_vendors_with_filters = self.run_query(self.apply_filter(self.sql_num_of_vendors()))
        
        st.write("Total Number of vendors with filters: ")
        st.write(num_of_vendors_with_filters)
        
        
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
                        
    
    def apply_filter(self, sql_query):
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
        is_online_payment_accepted_clause = "is_online_payment_accepted = " + self.is_online_payment_accepted_filter
        
        selected_filters = [self.vertical_filter, self.is_active_filter, self.is_tgo_filter, self.is_online_payment_accepted_filter]
        clause_flags = [self.vertical_flag, self.active_flag, self.tgo_flag, self.is_online_payment_accepted_flag]
        clauses = [vertical_clause, active_clause, tgo_clause, is_online_payment_accepted_clause]
        
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
        
    