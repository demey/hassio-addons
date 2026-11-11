#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: UA Alerts Monitor
# ==============================================================================

main() {
  exec python3 /usr/bin/http-client.py
}

main "$@"
