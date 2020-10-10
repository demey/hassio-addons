#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: apcupsd2mqtt
# ==============================================================================

get_router_info() {
  local host
  local username
  local password
  local topic
  local cmd
  local rx
  local tx

  cmd=$(echo "show interface ISP stat") 
  host=$(echo "$(bashio::config 'router')" | jq -r '."host"')
  username=$(echo "$(bashio::config 'router')" | jq -r '."username"')
  password=$(echo "$(bashio::config 'router')" | jq -r '."password"')

  routerstate="$(nmap -n -p 22 $host | grep '22/tcp' | awk '{print $2}')"
  if [[ "$routerstate" == "open" ]]; then
    output=$((
    sleep 2
    echo "$cmd"
    sleep 2
    echo "exit"
    ) | sshpass -p "$password" ssh -T -o StrictHostKeyChecking=no "$username"@"$host")

    while read -r line; do
    if grep -q 'rxspeed' <<< "$line"; then
      rx=$(echo -e "${line#*: }")
    fi
    if grep -q 'txspeed' <<< "$line"; then
      tx=$(echo -e "${line#*: }")
    fi
    done <<< "$output"
    echo -e "${rx}:${tx}"
  else
    echo -e "0:0"
  fi
}

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

  mqttstate="$(nmap -n -p $mqttport $mqtthost | grep $mqttport | awk '{print $2}')"
  
  while true; do
    if [[ "$mqttstate" == "open" ]]; then
      bashio::log.info "MQTT server port state: $mqttstate"
      router=$(get_router_info)
      
      mosquitto_pub -h "$mqtthost" -p "$mqttport" -u "$username" -P "$password" -t "${topic2}/state" -m "{\"RX\":\"${router%:*}\",\"TX\":\"${router#*:}\"}"

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
    else
      bashio::log.info "MQTT server port state: $mqttstate"
    fi  
    sleep "${sleep}"
  done
}
main "$@"
