Sun 06/13/2021 05:34:51 PM
show debug info of device:
	`esphome aquarium.yaml logs`

compile by itself:
	`esphome aquarium.yaml compile`

upload without uploading:
	`esphome aquarium.yaml upload`

compile+run:
	`esphome aquarium.yaml run`


lambdas in esphome speak are just c++ code.
you can get values from esphome world by using `id(<yaml_var>)`
such as from a binary sensor: `id(binary_sensor_id).state`

TODO put ip address on screen for TTGO:
https://esphome.io/components/text_sensor/wifi_info.html
need to set it as internal component if I don't want it to show up in home assistant


looks like the display loop only runs every time sensors update, so in the case of aquarium.yaml as of now, 5s.
