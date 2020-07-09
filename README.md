# badconga

![CI](https://github.com/adrigzr/badconga/workflows/CI/badge.svg)

Work in progress plugin for Home Assistant for Cecotec Conga Vacuums.

All data has been reverse-engineered from Android app [Conga 3000](https://play.google.com/store/apps/details?id=es.cecotec.s3590&hl=es).

Compatible models: Conga 3290, 3390, 3490, 3590, 3690 and 3790.

Currently only tested on: Conga 3490.

## Features

- [x] Vacuum entity

<img src="./images/vacuum.png" width="300"/>

- [x] Camera entity

<img src="./images/camera.png" width="300"/>

## Home Assistant

### Installation

Copy or link [`badconga`](./badconga) subfolder to `config/custom_components`.

### Configuration

Create a new account on the app and link the device to it.

Currently, it does not support having the same account on the app and Home Assistant at the same time. One login will disable the other. If you use the same account as in the app, the app will be logged out.

```
badconga:
  email: '<email>'
  password: '<password>'

vacuum:
  - platform: badconga

camera:
  - platform: badconga

# enable debug for now...
logger:
  default: info
  logs:
    custom_components.badconga: debug
```

## Snippets

### Lint project

```
$ pylint --ignore=schema_pb2.py badconga
```

### Dump Android packets

```
$ adb shell
$ su
# tcpdump -i wlan0 -s0 -w - | nc -l -p 11111
```

### Listen for packets on host

```
$ adb forward tcp:11111 tcp:11111
$ nc localhost 11111 | tcpflow -o flow -r - "port 4020 or port 4030"
```

### Read app logs

```
$ adb logcat -c && adb logcat es.cecotec.s3590:V > flow.log
```

### Compile protobuf schemas

```
$ protoc --python_out=. app/schema.proto
```

### Parse flow

```
$ python3 parse.py flow/*~*.xml
```

### Inspect hex string as protobuf

```
$ git clone https://github.com/mildsunrise/protobuf-inspector.git
$ echo "<hex string>" | xxd -r -p | ./protobuf-inspector/main.py
```
