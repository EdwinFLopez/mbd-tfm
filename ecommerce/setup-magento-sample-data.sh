#!/usr/bin/env bash
set -o errexit

echo "######################################################################"
echo "Loading sample data for Magento eCommerce..."

bin/magento sampledata:reset && bin/magento sampledata:deploy && bin/magento setup:upgrade

# Disable 2FA modules to ease work with front-end
echo "Disabling 2FA for local development..."
bin/magento module:disable Magento_TwoFactorAuth Magento_AdminAdobeImsTwoFactorAuth --clear-static-content

# Rebuild the eCommerce
bin/magento setup:di:compile

echo "Magento eCommerce sample data deployed..."
echo "######################################################################"
echo ""
