#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: mbusreader
# ==============================================================================

bashio::log.info "Service mbusreader started"

mkdir -p /share/mbusreader
ADDRESS_FILE=/share/mbusreader/addresses.txt
LOG_FILE=/share/mbusreader/log.txt

if [ -f $LOG_FILE ]; then
    mv -f $LOG_FILE "${LOG_FILE}.1"
fi 

SLEEP=$(bashio::config 'update_interval')
BAUDRATE=$(bashio::config 'baudrate')
DEVICE=$(bashio::config 'device')
MQTT_HOST=$(echo "$(bashio::config 'mqtt')" | jq -r '."host"')
MQTT_PORT=$(echo "$(bashio::config 'mqtt')" | jq -r '."port"')
MQTT_USER=$(echo "$(bashio::config 'mqtt')" | jq -r '."username"')
MQTT_PASS=$(echo "$(bashio::config 'mqtt')" | jq -r '."password"')
MQTT_TOPIC=$(echo "$(bashio::config 'mqtt')" | jq -r '."topic"')

if [ ! -f $ADDRESS_FILE ]; then
    mbus-serial-scan-secondary -b $BAUDRATE $DEVICE | sed -e 's/^.*y address \([0-9A-Fa-f]\+\) .*$/\1/' > $ADDRESS_FILE
fi

main() {

  while true; do
    while read mbusmeters; do
      echo "$(date '+%Y-%m-%d %H:%M:%S') Getting data from $mbusmeters ... " >> $LOG_FILE
      # The sed is for replacing the @ with _ to be able to match on it in HASS templates
      METER_DATA=$(mbus-serial-request-data-multi-reply -b $BAUDRATE $DEVICE $mbusmeters | jc --xml | jq | sed -e "s/@/_/")
      echo "$(date '+%Y-%m-%d %H:%M:%S') $METER_DATA" >> $LOG_FILE
      mosquitto_pub -h $MQTT_HOST -p $MQTT_PORT -u $MQTT_USER -P $MQTT_PASS -t $MQTT_TOPIC/$mbusmeters -r -m "${METER_DATA}"
      BYTCNT=$(echo "$METER_DATA" | wc -c)
      echo "$(date '+%Y-%m-%d %H:%M:%S') $BYTCNT bytes sent" >> $LOG_FILE
    done < <(cat $ADDRESS_FILE)
    sleep "${SLEEP}"
  done
}
main "$@"
