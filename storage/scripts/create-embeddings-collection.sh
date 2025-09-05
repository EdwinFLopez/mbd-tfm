#!/bin/bash

# Configurable variables
DB_NAME="mbdtfmdb"
MONGO_URI="mongodb://mongodb-atlas:27017/$DB_NAME"
TARGET_COLLECTION="mbdtfm_magento_catalog_products_embeddings"

# JSON Schema validator + Vector Index + Text Index definitions
# Vector search index on field `product_embeddings`
# Full-text search index on `product_properties`
/usr/bin/mongosh "$MONGO_URI" --eval "$(cat << EOF
  db.getSiblingDB('$DB_NAME').createCollection(
    '$TARGET_COLLECTION', {
      validator: {
        \$jsonSchema: {
          bsonType: 'object',
          required: ['_id', 'product_sku', 'product_name', 'product_properties', 'product_created_at'],
          properties: {
            _id: {
              bsonType: 'object',
              required: ['product_id'],
              properties: {
                product_id: { bsonType: 'long', description: 'must be a long and is required' }
              }
            },
            product_sku: { bsonType: 'string', description: 'must be a string and is required' },
            product_name: { bsonType: 'string', description: 'must be a string and is required' },
            product_properties: { bsonType: 'string', description: 'must be an object (JSON)' },
            product_flat_props: { bsonType: 'string', description: 'must be an object (JSON)' },
            product_embeddings: {
              bsonType: 'array',
              items: { bsonType: 'double' },
              description: 'vector embeddings for similarity search (nullable)'
            },
            product_created_at: { bsonType: 'date', description: 'must be a timestamp and is required' },
            product_updated_at: { bsonType: 'date', description: 'must be a timestamp if present' },
            product_deleted_at: { bsonType: 'date', description: 'must be a timestamp if present' },
            embeddings_updated_at: { bsonType: 'date', description: 'last processing of embeddings timestamp (nullable)' }
          }
        }
      }
  });
EOF
)"
echo "Embeddings collection '${TARGET_COLLECTION}' has been created."
echo "======================================="

/usr/bin/mongosh "$MONGO_URI" --eval "$(cat << EOF
db.getSiblingDB('$DB_NAME').${TARGET_COLLECTION}.insertOne({
    _id: { product_id: new NumberLong('0') },
    product_sku: '0',
    product_name: '0',
    product_properties: '{}',
    product_flat_props: '{}',
    product_embeddings: [0.1],
    product_updated_at: new ISODate(3000,12,31,0,0,0),
    product_created_at: new ISODate(3000,12,31,0,0,0),
    product_deleted_at: new ISODate(3000,12,31,0,0,0),
    embeddings_updated_at: new ISODate(3000,12,31,0,0,0)
});
EOF
)"
echo "Inserting dummy record into '${TARGET_COLLECTION}' for structure."
echo "======================================="

/usr/bin/mongosh "$MONGO_URI" --eval "$(cat << EOF
  db.getSiblingDB('$DB_NAME').${TARGET_COLLECTION}.createSearchIndex(
    '${TARGET_COLLECTION}_product_flat_props_idx', {
      mappings: {
        dynamic: false,
        fields: {
          product_flat_props: {
            type: 'string'
          }
        }
      }
  });
EOF
)"
echo "Full-Text search index '${TARGET_COLLECTION}_product_flat_properties_idx' created."
echo "======================================="

/usr/bin/mongosh "$MONGO_URI" --eval "$(cat << EOF
  db.getSiblingDB('$DB_NAME').$TARGET_COLLECTION.createSearchIndex(
    '${TARGET_COLLECTION}_product_embeddings_vector_idx',
    'vectorSearch',
    {
      fields: [{
        type: 'vector',
        path: 'product_embeddings',
        numDimensions: 128,
        similarity: 'cosine',
        quantization: 'scalar'
      }]
  });
EOF
)"
echo "Vector search index '${TARGET_COLLECTION}_product_embeddings_vector_idx' created."
echo "======================================="

