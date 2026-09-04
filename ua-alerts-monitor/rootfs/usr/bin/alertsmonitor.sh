#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: UA Alerts Monitor
# ==============================================================================

main() {
  declare sync_interval
  sync_interval=$(bashio::config 'sync_interval')

  while true; do
    python3 /usr/bin/monitor.py
#    sleep "${sync_interval}"
  done
}

main "$@"
