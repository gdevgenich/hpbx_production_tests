#!/bin/bash

set -e 
set -x

DEB_USER="jenkins"
DEB_GROUP="jenkins"
DEB_DATA="resources settings tests __main__.py plan.txt logging.yaml"
DEB_DIRECTORY="opt/smoke_production"
DEB_PACKAGE_NAME="hpbx-smoke-tests"
DEB_PACKAGE_VERSION="$(cat version)"
DEB_DEVEMAIL="dgirdyuk@intermedia.net"
DEB_PACKAGE_DESC="HPBX smoke test"
DEB_OS_PREFIX='deb10'
DEB_ARCH='amd64'

if [ ! -z "$BUILD_NUMBER" ] && [ ! -z "$SOURCE_GIT_BRANCH" ]
then
    DEB_BUILD_NUMBER="${DEB_PACKAGE_VERSION}.${BUILD_NUMBER}-$(echo ${SOURCE_GIT_BRANCH}|sed 's|_|-|g')+${DEB_OS_PREFIX}"
elif [ ! -z "$CI_PIPELINE_IID" ] && [ ! -z "$CI_COMMIT_REF_NAME" ]
then
    DEB_BUILD_NUMBER="${DEB_PACKAGE_VERSION}.${CI_PIPELINE_IID}-$(echo ${CI_COMMIT_REF_NAME}|sed 's|_|-|g')+${DEB_OS_PREFIX}"
else
    echo "NO BUILD_NUMBER and SOURCE_GIT_BRANCH or CI_PIPELINE_ID and CI_COMMIT_REF_NAME"
    exit 1
fi

if [ -d "$DEB_DIRECTORY" ]
  then rm -r $DEB_DIRECTORY
fi

mkdir -p $DEB_DIRECTORY/
mkdir -p var/tmp/pjlog

for i in $DEB_DATA
  do cp -r $i $DEB_DIRECTORY/
done

ls|grep "${DEB_ARCH}.deb"|while read l
  do echo "Removing $l"
  rm $l;
done

CONFIG_FILES="--config-files $DEB_DIRECTORY/logging.yaml"

fpm   --name "$DEB_PACKAGE_NAME" \
      --version "$DEB_BUILD_NUMBER" \
      --architecture "${DEB_ARCH}" \
      --maintainer "${DEB_DEVEMAIL}" \
      --depends 'python3-anymeeting-client = 0.2' \
      --depends 'python3-audio-functions = 2.1' \
      --depends 'python3-base-callfunc = 1.2' \
      --depends 'python3-blf-parser = 1.2' \
      --depends 'python3-call-functions = 7.6' \
      --depends 'python3-configparser2 = 2.2' \
      --depends 'python3-context = 1.4' \
      --depends 'python3-future-comparators = 1.0.1' \
      --depends 'python3-hpbx-base = 2.86' \
      --depends 'python3-hpbx-dm = 7.36' \
      --depends 'python3-ips-client = 4.14' \
      --depends 'python3-ips-control = 1.24' \
      --depends 'python3-log-functions = 1.0' \
      --depends 'python3-mailbox-functions = 2.6' \
      --depends 'python3-mailcc = 2.0' \
      --depends 'python3-msg-util = 1.0.0' \
      --depends 'python3-mwi-parser = 1.0' \
      --depends 'python3-pbxut = 4.5.0' \
      --depends 'python3-pbxut-plugin-alert-case = 1.0' \
      --depends 'python3-pbxut-plugin-classic-reporter = 1.0.0' \
      --depends 'python3-pbxut-plugin-context = 1.0.0' \
      --depends 'python3-pbxut-plugin-context-reader = 1.0.2' \
      --depends 'python3-pbxut-plugin-hpbx-version = 1.0.0' \
      --depends 'python3-pbxut-plugin-mail-reporter = 1.1.0' \
      --depends 'python3-pbxut-plugin-simple-filter = 1.0.0' \
      --depends 'python3-pbxut-plugin-summary-case = 1.0.0' \
      --depends 'python3-pbxut-plugin-testlink = 1.0.0' \
      --depends 'python3-pbxut-plugin-verbose-reporter = 1.0.1' \
      --depends 'python3-pbxut-util = 4.5.0' \
      --depends 'python3-pynetwork = 2.2' \
      --depends 'python3-pytz' \
      --depends 'python3-reactor = 3.0' \
      --depends 'python3-rmq-client = 1.8' \
      --depends 'python3-robert2 = 2.0' \
      --depends 'python3-rpclient = 1.2' \
      --depends 'python3-sdplib = 1.0' \
      --depends 'python3-sipde-client = 2.4.1' \
      --depends 'python3-siplib = 4.0' \
      --depends 'python3-sipne = 3.5.1' \
      --depends 'python3-soap-client = 1.1' \
      --depends 'python3-step-manager = 2.12' \
      --depends 'python3-testlink = 3.0' \
      --depends 'python3-umsctl-client = 1.10' \
      --depends 'python3-unison-cp-client = 1.22' \
      --depends 'python3-waveproc = 2.11' \
      --depends 'libpjproject = 2.11-2' \
      --depends 'sipde = 1.2.3' \
      --depends 'sipmon = 2.4.14' \
      --depends 'nodejs = 12.20.1-1nodesource1' \
      --deb-user $DEB_USER \
      --deb-group $DEB_GROUP \
      --description "${DEB_PACKAGE_DESC}" \
      --description "HPBX smoke test" \
      --deb-no-default-config-files \
      ${CONFIG_FILES} \
      -t deb -s dir opt/ var/