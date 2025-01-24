#!/usr/bin/env bash
set -o errexit

DOMAIN=${1:-magento.test}
VERSION=${2:-2.4.8}
EDITION=${3:-community}

echo "Installing: Magento @$DOMAIN $EDITION v$VERSION"
curl -s https://raw.githubusercontent.com/edwinflopez/docker-magento/master/lib/onelinesetup | bash -s -- "$DOMAIN" "$VERSION" "$EDITION"

# #####################################################################
# TODO: Test using wget + unzip to download directly,
#       instead of git commands to avoid breaking current repo.
# #####################################################################
# 0. Move to ecommerce folder:
#   cd ./ecommerce
# 1. Download repo magento setup scripts (skip https errors):
#   wget --no-check-certificate --content-disposition https://github.com/EdwinFLopez/docker-magento/archive/refs/heads/master.zip -q
# 2. Unzip compose folder only:
#   unzip docker-magento-master.zip 'docker-magento-master/compose/*' -d ./
# 3. Move contents to current ./ecommerce folder:
#   mv ./docker-magento-master/compose/* ./
# 4. Remove compose folder:
#   rm -rf ./docker-magento-master
# 5. Ensure these are created so Docker doesn't create them as root
#   mkdir -p ~/.composer ~/.ssh
# #####################################################################
