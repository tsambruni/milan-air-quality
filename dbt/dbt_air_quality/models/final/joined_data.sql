{{
    config(
        materialized='incremental'
    )
}}

SELECT
  aq.date,
  aq.station_id,
  st.location,
  st.geopoint,
  aq.pollutant,
FROM
  {{ ref("stg_air_quality") }} aq
INNER JOIN
  {{ ref("stg_stations") }} st
ON
  aq.station_id = st.station_id
  AND aq.date BETWEEN st.active_from AND st.active_to
ORDER BY 1 desc, 2 asc

{% if is_incremental() %}

  -- this filter will only be applied on an incremental run
  where date > (select max(date) from {{ this }})

{% endif %}