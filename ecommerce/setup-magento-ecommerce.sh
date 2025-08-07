#!/usr/bin/env bash
set -o errexit

DOMAIN=${1:-magento.test}
VERSION=${2:-2.4.7-p4}
EDITION=${3:-community}

echo "######################################################################"
echo "Installing: Magento @$DOMAIN $EDITION v$VERSION..."
# Old download command using curl and git.
#curl -s https://raw.githubusercontent.com/edwinflopez/docker-magento/master/lib/onelinesetup | bash -s -- "$DOMAIN" "$VERSION" "$EDITION"
#echo "######################################################################"

# #####################################################################
# Instead of git commands to avoid breaking current repo.
# #####################################################################
# 1. Download repo magento setup scripts (skip https errors):
echo "Downloading package and unzipping..."
wget --no-check-certificate --content-disposition https://github.com/edwinflopez/docker-magento/archive/refs/heads/master.zip -q

# 2. Unzip compose folder only:
unzip ./docker-magento-master.zip 'docker-magento-master/compose/*' -d ./

# 3. Move contents to current ./ecommerce folder:
echo "Moving installation scripts to ecommerce folder..."
mv ./docker-magento-master/compose/* ./
mv ./docker-magento-master/compose/.vscode ./

# 4. Remove folder and zip:
echo "Removing temp files and folders..."
rm -rf ./docker-magento-master
rm -rf ./docker-magento-master.zip

# 5. Ensure these are created so Docker doesn't create them as root
mkdir -p ~/.composer ~/.ssh

# #####################################################################
# Proceed to install magento
echo "Executing Magento setup scripts..."
bin/download "${VERSION}" "${EDITION}" && bin/setup "${DOMAIN}"

echo "######################################################################"
echo "Magento eCommerce has been installed..."
echo "######################################################################"
echo ""
