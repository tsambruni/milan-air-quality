select 
    stazione_id as station_id,
    data as date,
    ARRAY_AGG(STRUCT(inquinante as pollutant, valore as level)) as pollutant
    from `milan-air-data.air_quality_data.raw_air_quality`
group by 
    stazione_id,
    data