#!/bin/bash

# Start and stop mjpg-streamer - assuming it is installed

MJPG=/usr/local/bin/mjpg_streamer

echo You said $1

if [ -x $MJPG ] ; then
  case "$1" in
    start) echo Starting streamer...
      $MJPG -o "output_http.so -w /usr/local/share/mjpg-streamer/www" -i "input_raspicam.so -x 640 -y 480 -fps=10" \
         >/dev/null 2>&1 &
      ;;
    stop) echo Stopping streamer...
      killall -9 mjpg_streamer
      ;;
    *)
      echo "Usage: stream.sh start|stop"
      exit 1
      ;;
  esac

else
  echo MJPG Streamer not installed, see https://github.com/jacksonliam/mjpg-streamer
  exit 1
fi

exit 0
