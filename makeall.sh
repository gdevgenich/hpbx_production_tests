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

# read dependencies from file resource/requirements.txt
DEB_PYTHON_LIBS_DEPENDENSIES=$(awk -F '/' '!/^$/ {print $NF}' settings/requirements.txt | sed 's|.git||g;s|_|-|g'|while read l;do echo -n " --depends python3-${l}";done)

# extra dependencies
DEB_COMMON_DEPENDENSIES_PKG_NAMES="python3 ffmpeg libpjproject bcg729 sipde sipmon"
DEB_COMMON_DEPENDENSIES=$(for i in $DEB_COMMON_DEPENDENSIES_PKG_NAMES;do echo -n " --depends $i"; done)

CONFIG_FILES="--config-files $DEB_DIRECTORY/resources 
--config-files $DEB_DIRECTORY/settings 
--config-files $DEB_DIRECTORY/logging.yaml"

fpm   --name "$DEB_PACKAGE_NAME" \
      --version "$DEB_BUILD_NUMBER" \
      --architecture "${DEB_ARCH}" \
      --maintainer "${DEB_DEVEMAIL}" \
      ${DEB_COMMON_DEPENDENSIES} \
      ${DEB_PYTHON_LIBS_DEPENDENSIES} \
      --depends 'python3-hpbx-dm = 7.33' \
      --depends 'nodejs = 12.20.1-1nodesource1' \
      --deb-user $DEB_USER \
      --deb-group $DEB_GROUP \
      --description "${DEB_PACKAGE_DESC}" \
      --description "HPBX smoke test" \
      --deb-no-default-config-files \
      ${CONFIG_FILES} \
      -t deb -s dir opt/=/opt var/tmp/pjlog=/var/tmp/pjlog 