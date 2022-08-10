#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: shellsensors
# ==============================================================================

bashio::log.info "Service shellsensors started"

mkdir -p /share/shellsensors
LOG_FILE=/share/shellsensors/log.txt

if [ -f $LOG_FILE ]; then
    mv -f $LOG_FILE "${LOG_FILE}.1"
fi 

SLEEP=$(bashio::config 'update_interval')

main() {
  while true; do

    MIN=$(date +"%M")
    UVI_TIME=("00" "20" "40")

    if [[ "${UVI_TIME[*]}" =~ "${MIN}" ]]; then 

      SENSOR_NAME="sensor.uvi_current"
      UVI_VALUE=$(/share/shellsensors/uvi.pl)
      SENSOR_DATA='{"state": "'"$UVI_VALUE"'", "attributes": {"friendly_name":"'"УФ Індекс"'","icon":"mdi:sun-wireless","state_class":"measurement"}}'

      curl -X POST -H "Authorization: Bearer ${SUPERVISOR_TOKEN}" \
         -s \
         -o /dev/null \
         -H "Content-Type: application/json" \
         -d "$SENSOR_DATA" \
         -w "[$(date)][INFO] Sensor update response code: %{http_code}\n" \
         http://supervisor/core/api/states/${SENSOR_NAME}
    fi

    FORECAST_TIME=("00" "10" "20" "30" "40" "50")

    if [[ "${FORECAST_TIME[*]}" =~ "${MIN}" ]]; then 

      SENSOR_NAME="sensoropenweather_current"
      UFORECAST_VALUE=$(/share/shellsensors/weather.pl)
      SENSOR_DATA='{"state": "'"$UFORECAST_VALUE"'", "attributes": {"friendly_name":"'"Прогноз погоди"'","icon":"mdi:weather-partly-cloudy"}}'

      curl -X POST -H "Authorization: Bearer ${SUPERVISOR_TOKEN}" \
         -s \
         -o /dev/null \
         -H "Content-Type: application/json" \
         -d "$SENSOR_DATA" \
         -w "[$(date)][INFO] Sensor update response code: %{http_code}\n" \
         http://supervisor/core/api/states/${SENSOR_NAME}
    fi

    sleep "${SLEEP}"
  done
}
main "$@"
