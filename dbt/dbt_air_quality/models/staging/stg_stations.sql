select 
    id_amat as station_id,
    nome as location,
    ST_GEOGPOINT(
        CAST(LONG_X_4326 AS FLOAT64),
        CAST(LAT_Y_4326 AS FLOAT64)
    ) as geopoint,
    inizio_operativita as active_from,
    fine_operativita as active_to,
    SPLIT(inquinanti) AS pollutant
from `milan-air-data.air_quality_data.raw_stations`