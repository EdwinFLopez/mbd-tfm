#!/usr/bin/env bash
set -o errexit

# Get token for authentication
# tr -d '"': removes quotation marks from the curl response.
TOKEN=$(curl -s -L -X POST "https://magento.test/index.php/rest/V1/integration/admin/token/" --post301 \
-H "Content-Type: application/json" -d '{ "username": "john.smith", "password": "password123" }' | tr -d '"')

echo "$TOKEN"

# Create "Terror" Category
# https://developer.adobe.com/commerce/webapi/rest/quick-reference/
curl -s -X POST "https://magento.test/index.php/rest/V1/categories" \
-H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
-d '{
    "category": {
        "name": "Terror",
        "parentId": 2,
        "isActive": true,
        "position": 1,
        "level": 2
    }
}'
