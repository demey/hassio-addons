#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: mbusreader
# ==============================================================================

bashio::log.info "Service mbusreader started"

mkdir -p /share/mbusreader
sleep=$(bashio::config 'update_interval')

main() {

  while true; do
    sleep "${sleep}"
  done
}
main "$@"
