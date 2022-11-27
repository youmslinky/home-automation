
subscribe to all topics on mqtt server 192.168.1.2:
`mosquitto_sub -v -h 192.168.1.2 -t "#"`

send a command for status of all tasmota devices in topic "tasmotas":
`mosquitto_pub -h 192.168.1.2 -t cmnd/tasmotas/status -m 5`

there are multiple statuses for tasmota, with different info in each, just send the message to get the status of that index
`mosquitto_pub -h 192.168.1.2 -t cmnd/tasmotas/status -m 4`
`mosquitto_pub -h 192.168.1.2 -t cmnd/tasmotas/status -m 3`
etc.

request power switch state of each tasmota device in "tasmotas" topic:
`mosquitto_pub -h 192.168.1.2 -t cmnd/tasmotas/power -m ""`

Sun 06/13/2021 12:17:50 PM
can change the mqtt publish period with teleperiod
easy way to do it is go to web interface console, and type `teleperiod xxx`
type just `teleperiod` to get current value

can set [latitude and longitude](https://tasmota.github.io/docs/Timers/?query=latitude) in order to have sunset and sunrise times be correct

its important to set the timezone properly as well

I'm using chicago timezone on all devices now.
`Backlog0 Timezone 99; TimeStd 0,1,11,1,2,-360; TimeDst 0,2,3,1,2,-300`

but It may actually be better to just stick wihtout switching for DST, as animals don't care about that

`backlog0` allows multiple commands strung together, without restarting at everyone.

