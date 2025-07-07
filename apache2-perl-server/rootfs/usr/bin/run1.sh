#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: Apache HTTP Server
# ==============================================================================

mkdir -p /share/apache2
mkdir -p /share/apache2/logs
mkdir -p /share/apache2/html
mkdir -p /share/apache2/cgi-bin
cp -r /var/www/modules /share/apache2
/usr/sbin/httpd -k start

main() {
  while true; do
    echo ${SUPERVISOR_TOKEN} > /tmp/token.txt
    chmod 0644 /tmp/token.txt
    sleep 100
  done
}
main "$@"