#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: apcupsd2mqtt
# ==============================================================================

main() {

  local sleep
  sleep=$(bashio::config 'update_interval')
  mqtthost=$(echo "$(bashio::config 'mqtt')" | jq -r '."host"')
  mqttport=$(echo "$(bashio::config 'mqtt')" | jq -r '."port"')
  username=$(echo "$(bashio::config 'mqtt')" | jq -r '."username"')
  password=$(echo "$(bashio::config 'mqtt')" | jq -r '."password"')
  topic=$(echo "$(bashio::config 'mqtt')" | jq -r '."topic"')

  bashio::log.info "Service apcupsd2mqtt started"
  
  while true; do

    for k in $(echo "$(bashio::config 'network_upses')")
    do
      apchost=$(echo "$k" | jq -r '."url"')
      apcname=$(echo "$k" | jq -r '."name"')
      
      readarray -t array <<< $(apcaccess -h "$apchost") || bashio::log.error "Connection to $apchost filed"

      declare -A upsmap
      for i in "${array[@]}"
      do
        IFS=': ' read -ra line <<< "$i"
        key="$(echo -e "${line[0]}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
        value="$(echo -e "${line[1]}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
        upsmap["$key"]=$value
      done
      message=$(for key in "${!upsmap[@]}"; do
        printf '%s\0%s\0' "$key" "${upsmap[$key]}"
      done |
      jq -Rs '
        split("\u0000")
        | . as $a
        | reduce range(0; length/2) as $i 
          ({}; . + {($a[2*$i]): ($a[2*$i + 1]|fromjson? // .)})')
      
      fulltopic="${topic}${apcname}/status"

      mosquitto_pub -h "$mqtthost" -p "$mqttport" -u "$username" -P "$password" -t "$fulltopic" -m "$message"
    done
      
    sleep "${sleep}"
  done
}
main "$@"
