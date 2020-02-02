#!/bin/sh

usage() {
  echo "usage: $0 obtain|renewal|manual|deploy [options]"
  echo
  echo "example: $0 obtain -d domain.com *.domain.com"
}

bin_path="`dirname $(realpath $0)`"
PATH="$bin_path:$PATH"

action="$1"
shift

case $action in
  obtain)
    obtain.py $@
    ;;
  renewal)
    renewal.py $@
    ;;
  manual)
    manual.py $@
    ;;
  deploy)
    deploy.py $@
    ;;
  *)
    usage
    ;;
esac