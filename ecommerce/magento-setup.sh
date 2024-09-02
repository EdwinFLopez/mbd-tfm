#!/usr/bin/env bash
set -o errexit

DOMAIN=${1:-magento.test}
VERSION=${2:-2.4.7}
EDITION=${3:-community}

echo "Installing: Magento @$DOMAIN $EDITION v$VERSION"
curl -s https://raw.githubusercontent.com/edwinflopez/docker-magento/master/lib/onelinesetup | bash -s -- "$DOMAIN" "$VERSION" "$EDITION"
