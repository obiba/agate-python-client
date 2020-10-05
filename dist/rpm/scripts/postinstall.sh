#!/bin/sh
set -e

# clean python2 install (agate symlink)
python2_lib=/usr/lib/python2.7/dist-packages

case "$1" in
  0)
    if [ -d $python2_lib ]; then
      rm -f $python2_lib/agate
    fi
  ;;

  [1-2])
    if [ -d $python2_lib ]; then
      rm -f $python2_lib/agate
    fi
  ;;

  *)
    echo "postinst called with unknown argument \`$1'" >&2
    exit 1
  ;;
esac
exit 0
