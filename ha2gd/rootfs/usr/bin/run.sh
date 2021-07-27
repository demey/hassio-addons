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
  
  if [ -f "$uploader" ]; then
    while true; do
      cd /share/ha2gd/
      result="$(python3 ${uploader})"
      bashio::log.info "{$result}"
    done
  else
    bashio::log.warning "File ${uploader} does not exist"
  fi
}
main "$@"
