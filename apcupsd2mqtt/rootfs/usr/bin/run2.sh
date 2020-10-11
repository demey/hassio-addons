#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: apcupsd2mqtt
# ==============================================================================

main() {
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
  local mqtthost
  local mqttport
  local username
  local password
  local topic2
  local mqttstate
  local router

  mqtthost=$(echo "$(bashio::config 'mqtt')" | jq -r '."host"')
  mqttport=$(echo "$(bashio::config 'mqtt')" | jq -r '."port"')
  username=$(echo "$(bashio::config 'mqtt')" | jq -r '."username"')
  password=$(echo "$(bashio::config 'mqtt')" | jq -r '."password"')
  topic2=$(echo "$(bashio::config 'router')" | jq -r '."mqtttopic"')

  bashio::log.info "Service router info started"

  while true; do
    mqttstate="$(nmap -n -p $mqttport $mqtthost | grep $mqttport | awk '{print $2}')"
    if [[ "$mqttstate" == "open" ]]; then
      router=$(get_router_info)
      mosquitto_pub -h "$mqtthost" -p "$mqttport" -u "$username" -P "$password" -t "${topic2}/state" -m "{\"RX\":\"${router%:*}\",\"TX\":\"${router#*:}\"}"
    else
      bashio::log.info "MQTT server port state: $mqttstate"
    fi  
    sleep 10
  done
}
main "$@"
