#!/bin/bash
if [[ -z "${__TANOS_APP_PATH__}" ]]; then
  export __TANOS_APP_PATH__="./app"
  export __TANOS_CORE_PATH__="./core"
fi

docker-compose -f docker-compose-local.yml up -d