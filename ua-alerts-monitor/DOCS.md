# Home Assistant Private Add-on: UA Alerts Monitor

This add-on allows you to collect Telegram messages from defined channels 
to your Home Assistant instance (for example during Air Attack) and use 
those data as TTS messages on the speakers.

## Installation

* Go to your Home Assistant Add-on store and add this
  repository: [`https://github.com/demey/hassio-addons`](https://github.com/demey/hassio-addons)
  [![Open your Home Assistant instance and show the dashboard of a Supervisor add-on.](https://my.home-assistant.io/badges/supervisor_addon.svg)](https://my.home-assistant.io/redirect/supervisor_addon/?addon=2af0a32d_batmon&repository_url=https%3A%2F%2Fgithub.com%2Ffl4p%2Fhome-assistant-addons)
* Install UA Alerts Monitor add-on

## Configuration

### Option: `max_message_length` - maximum length of message that will be sent in Home Assistant.
### Option: `channels` - a list of channels to collect messages: 2-3 is enought (speaker will not be able to broadcast updates on more channels at the same time). Value without leading '@' sign.
### Option: `skip_key_words` - a list of words that will indicate that this message should be skipped.
### Option: `delete_key_words` - alist of words that will be extracted from messages.
### Option: `ritical_key_words` - a list of words that will indicate that this message is critical.
### Option: `sync_interval` - interval between requests to Telegram channels

## Using

Launching the addon will create a sensor `sensor.radar_status` with following attributes:
`state`, `message`, `critical`, `friendly_name`, `icon` which you can use in Home Assisstant automations as you wish.

Sensor will not update in two cases:
* message length more that value of `max_message_length`.
* message age is older than 60 seconds.

