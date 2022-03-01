/* Vendors and their cumulative GMV from last Month */
/* Vendor CVR from last month */
/* Vendor Chains with 2 or more vendors */
/* How many vendors contribute to how many successful orders Last Month */
/* Vendors and their Net Fail Rate over the last month */

WITH vendor_daily_performance AS (
    SELECT
      SAFE_CAST(vendor_id AS INT64) AS vendor_id, 
      EXTRACT(MONTH FROM date) as month,
      SUM(gmv_value_sum_eur) AS agg_gmv_eur, 
      SUM(viewed_menu_session_count) AS session_count, 
      SUM(attempted_placed_order_session_count) AS attempted_order, 
      SUM(placed_order_session_count) AS placed_order, 
      SUM(successful_order_count) AS successful_order_count,
      SUM(net_fail_order_count) AS net_fail_order_count, 
      SUM(net_order_count) AS net_order_count,
      SUM(orders_vendor_delay_v2_count) as vendor_delay, 
    FROM 
      `bta---talabat.data_platform.agg_vendor_performance_summarised_daily`
    WHERE 
      date BETWEEN DATE_SUB(DATE_TRUNC(CURRENT_DATE(), MONTH), INTERVAL 2 MONTH)
      AND LAST_DAY(DATE_SUB(DATE_TRUNC(CURRENT_DATE(), MONTH), INTERVAL 1 MONTH), MONTH)
    GROUP BY  
      vendor_id, 
      month
),

total_successful_orders AS (
    SELECT 
      SUM(successful_order_count) AS total_successful_order_count
    FROM 
      `bta---talabat.data_platform.agg_vendor_performance_summarised_daily`
    WHERE 
      date BETWEEN DATE_SUB(DATE_TRUNC(CURRENT_DATE(), MONTH), INTERVAL 2 MONTH)
      AND LAST_DAY(DATE_SUB(DATE_TRUNC(CURRENT_DATE(), MONTH), INTERVAL 1 MONTH), MONTH)
), 

active_vendors AS 
(
    SELECT 
      v.vendor_id,
      v.chain_id,
      v.is_tgo, 
      v.is_key_vip_account, 
      c.vertical, 
      l.area_name, 
      l.city_name, 
      l.country_name, 
      v.rating_display,
      v.is_active
    FROM 
      `bta---talabat.data_platform.dim_vendor_info`  AS v
      LEFT JOIN `bta---talabat.data_platform.dim_chain` AS c USING(chain_id)
      LEFT JOIN `bta---talabat.data_platform.dim_location_info` as l USING(location_id)
    WHERE 
      is_active=TRUE 
)

SELECT 
  month, 
  vendor_id,
  chain_id, 
  is_tgo, 
  is_key_vip_account, 
  vertical,
  area_name, 
  city_name, 
  country_name, 
  rating_display,
  agg_gmv_eur,
  session_count,
  attempted_order,
  placed_order,
  successful_order_count,
  SAFE_DIVIDE(attempted_order, session_count) * 100 AS attempted_CVR, 
  SAFE_DIVIDE(placed_order, session_count) * 100 AS placed_CVR,
  net_fail_order_count,
  net_order_count,
  vendor_delay,
  SAFE_DIVIDE(net_fail_order_count, net_order_count) * 100 AS fail_rate
FROM 
  active_vendors 
  RIGHT JOIN vendor_daily_performance USING(vendor_id)
WHERE 
  is_active=TRUE

