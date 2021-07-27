#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: ha2gd
# ==============================================================================

main() {

  local sleep

  sleep=$(bashio::config 'sync_interval')
  bashio::log.info "Service ha2gd started"

  while true; do
    bashio::log.info "Service ha2gd started"
#    upload="$(python3 /share/ha2gd/upload.py)"
    sleep "${sleep}"
  done
}
main "$@"