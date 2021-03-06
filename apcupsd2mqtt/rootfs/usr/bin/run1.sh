#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: apcupsd2mqtt
# ==============================================================================

main() {

  local sleep
  local mqtthost
  local mqttport
  local username
  local password
  local topic
  local mqttstate
  local apchost
  local apcname
  local upsstate
  local message
  local router
  local routertopic

  sleep=$(bashio::config 'update_interval')
  mqtthost=$(echo "$(bashio::config 'mqtt')" | jq -r '."host"')
  mqttport=$(echo "$(bashio::config 'mqtt')" | jq -r '."port"')
  username=$(echo "$(bashio::config 'mqtt')" | jq -r '."username"')
  password=$(echo "$(bashio::config 'mqtt')" | jq -r '."password"')
  topic=$(echo "$(bashio::config 'mqtt')" | jq -r '."topic"')
  topic2=$(echo "$(bashio::config 'router')" | jq -r '."mqtttopic"')

  bashio::log.info "Service apcupsd2mqtt started"

  while true; do
    mqttstate="$(nmap -n -p $mqttport $mqtthost | grep $mqttport | awk '{print $2}')"
    if [[ "$mqttstate" == "open" ]]; then

      for k in $(echo "$(bashio::config 'network_upses')")
      do
        apchost=$(echo "$k" | jq -r '."url"')
        apcname=$(echo "$k" | jq -r '."name"')
        fulltopic="${topic}${apcname}/status"

        upsstate="$(nmap -n -p ${apchost#*:} ${apchost%:*} | grep ${apchost#*:} | awk '{print $2}')"

        if [[ "$upsstate" == "open" ]]; then
          readarray -t array <<< $(apcaccess -h "$apchost")

          if [[ "${array[0]}" =~ "refused" ]]; then
            message=$(echo "{\"STATUS\":\"OFFLINE\"}")
            bashio::log.info "APC host $apchost unavailable"
          else  
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
          fi
        else
          bashio::log.info "Apcupsd service is not available on $apchost"
        fi
        mosquitto_pub -h "$mqtthost" -p "$mqttport" -u "$username" -P "$password" -t "$fulltopic" -m "$message"
      done
    fi  
    sleep "${sleep}"
  done
}
main "$@"
