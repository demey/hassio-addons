#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: mbusreader
# ==============================================================================

bashio::log.info "Service mbusreader started"

if [ -d "/share/mbusreader" ]; then
  mkdir /share/mbusreader
fi

main() {

  while true; do
    sleep 60
  done
}
main "$@"
