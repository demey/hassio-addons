#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: Proton Drive Folder Sync 
# ==============================================================================

main() {

  declare used
  declare days
  declare oldest
  declare result
  declare local_folder
  declare remote_folder
  declare rclone_config

  days=$(bashio::config 'days')
  sleep=$(bashio::config 'sync_interval')
  rclone_config=$(bashio::config 'rclone_config')

  RCLONE_CONFIG=${rclone_config}
  export RCLONE_CONFIG

  while true; do
    used=`rclone about protondrive: | grep Used: | awk '{print $2}'`
    curl -s \
      -H "Authorization: Bearer $SUPERVISOR_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"state": ${used}, "attributes": {"friendly_name": "Proton Drive used space", "unit_of_measurement": "Gb", "icon": "mdi:cloud-upload"}}' \
      http://supervisor/api/states/sensor.pdrive_used_space \
    /
#    bashio::log.info "Space used on drive: ${used} Gb"

    for folder in $(bashio::config 'folders|keys'); do
      local_folder=$(bashio::config "folders[${folder}].local_folder")
      remote_folder=$(bashio::config "folders[${folder}].remote_folder")

      oldest=`ls -tcr $local_folder | head -1`
      bashio::log.info "Oldest folder is ${local_folder}/${oldest}"

     while [ `ls -1 | wc -l` -gt $days ]; do
       oldest=`ls -tcr $local_folder | head -1`
       bashio::log.info "Removing oldest folder ${local_folder}/${oldest}"
       rm -rf "${local_folder}/${oldest}"
     done

      bashio::log.info "Syncing ${local_folder} with ${remote_folder}"
      result=`rclone sync --protondrive-replace-existing-draft=true $local_folder protondrive:$remote_folder`

      if [ $? -ne 0 ]; then
        bashio::log.warn ${result}
      else
        bashio::log.info "Successful sync"
      fi
    done
    sleep "${sleep}"
  done
}
main "$@"

