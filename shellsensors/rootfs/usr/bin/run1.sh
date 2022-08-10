#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: mbusreader
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
    sleep "${SLEEP}"
  done
}
main "$@"
