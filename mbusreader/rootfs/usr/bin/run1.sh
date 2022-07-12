#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: mbusreader
# ==============================================================================

bashio::log.info "Service mbusreader started"

mkdir -p /share/mbusreader
sleep=$(bashio::config 'update_interval')
mqtthost=$(echo "$(bashio::config 'mqtt')" | jq -r '."host"')
mqttport=$(echo "$(bashio::config 'mqtt')" | jq -r '."port"')
username=$(echo "$(bashio::config 'mqtt')" | jq -r '."username"')
password=$(echo "$(bashio::config 'mqtt')" | jq -r '."password"')
topic=$(echo "$(bashio::config 'mqtt')" | jq -r '."topic"')

main() {

  while true; do
    sleep "${sleep}"
  done
}
main "$@"
