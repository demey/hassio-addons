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
UPTIME=$(date -d "$(stat /proc/1/cmdline | grep 'Change' | sed "s/.000000000//" | awk '{print $2" "$3}')" +"%s")

main() {
  while true; do

    MIN=$(date +"%M")
    NOW=$(date +"%s")
    DIFF=$(($NOW-$UPTIME))
    echo $DIFF >> $LOG_FILE
    UVI_TIME=("00" "20" "40")

    if [[ "${UVI_TIME[*]}" =~ "${MIN}" ]] || [[ $DIFF -lt 29 ]]; then 

      SENSOR_NAME="sensor.uvi_current"
      UVI_VALUE=$(/share/shellsensors/uvi.pl)
      SENSOR_DATA='{"state": "'"$UVI_VALUE"'", "attributes": {"friendly_name":"'"УФ Індекс"'","icon":"mdi:sun-wireless","state_class":"measurement"}}'

      send_sensor_data
    
    fi

    FORECAST_TIME=("00" "10" "20" "30" "40" "50")

    if [[ "${FORECAST_TIME[*]}" =~ "${MIN}" ]] || [[ $DIFF -lt 29 ]]; then 

      SENSOR_NAME="sensor.openweather_current"
      UFORECAST_VALUE=$(/share/shellsensors/weather.pl)
      SENSOR_DATA='{"state": "'"$UFORECAST_VALUE"'", "attributes": {"friendly_name":"'"Прогноз погоди"'","icon":"mdi:weather-partly-cloudy"}}'

      send_sensor_data

    fi

    sleep "${SLEEP}"
  done
}

send_sensor_data() {

  RESPONSE=$(curl -X POST -H "Authorization: Bearer ${SUPERVISOR_TOKEN}" -s -o /dev/null -H "Content-Type: application/json" d "$SENSOR_DATA" -w "[$(date)][INFO] $SENSOR_NAME update response code: %{http_code}\n" http://supervisor/core/api/states/${SENSOR_NAME})
  echo $RESPONSE >> $LOG_FILE

}

main "$@"
