#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: Proton Drive Folder Sync 
# ==============================================================================

main() {

  declare sync_interval

  sync_interval=$(bashio::config 'sync_interval')

  rm -f /var/run/monitor.pid

  while true; do
#    echo "processing..."
    if [ ! -f /var/run/monitor.pid ]; then
      result="$(python /usr/bin/monitor.py)"

      if [ ${#result} -gt 0 ]; then
        bashio::log.info "$result"
      fi
      
    fi
    sleep "${sync_interval}"
  done
}
main "$@"

