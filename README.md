# badconga

# Home Assistant configuration

```
badconga:
  sessionId: '<session id>'
  userId: <user id>
  deviceId: <device id>

vacuum:
  - platform: badconga

camera:
  - platform: badconga
```

# Lint project

```
$ pylint --ignore=schema_pb2.py badconga
```

# Dump Android packets

```
$ adb shell
$ su
# tcpdump -i wlan0 -s0 -w - | nc -l -p 11111
```

# Listen for packets on host

```
$ adb forward tcp:11111 tcp:11111
$ nc localhost 11111 | tcpflow -o flow -r - "port 4020 or port 4030"
```

# Read app logs

```
$ adb logcat -c && adb logcat es.cecotec.s3590:V > flow.log
```

# Compile protobuf schemas

```
$ protoc --python_out=. app/schema.proto
```

# Parse flow

```
$ python3 parse.py flow/*~*.xml
```
