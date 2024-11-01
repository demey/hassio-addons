#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: ha2gd 
# ==============================================================================

main() {

  local sleep
  local result
  local uploader
  
  uploader="/share/ha2gd/upload.py"
  sleep=$(bashio::config 'sync_interval')
  bashio::log.info "Service ha2gd started"
  
  while true; do
    if [ -f "$uploader" ]; then
      cd /share/ha2gd/
      result="$(python3 ${uploader})"
      len=${#result}
      if [ "$len" -gt 0 ]; then
        bashio::log.info "$result"
      fi
    else
      bashio::log.warning "File $uploader does not exist"
    fi
    sleep "${sleep}"
  done
}
main "$@"
