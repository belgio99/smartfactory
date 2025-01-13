#!/bin/bash


SOURCE_ENDPOINT="http://localhost:19000"
SOURCE_ACCESS_KEY="minio_user"
SOURCE_SECRET_KEY="minio_password"

TARGET_ENDPOINT="http://localhost:19002"
TARGET_ACCESS_KEY="minio_user"
TARGET_SECRET_KEY="minio_password"


mc alias set source $SOURCE_ENDPOINT $SOURCE_ACCESS_KEY $SOURCE_SECRET_KEY
mc alias set target $TARGET_ENDPOINT $TARGET_ACCESS_KEY $TARGET_SECRET_KEY


echo "Getting list of buckets on source..."
BUCKETS=$(mc ls source | awk '{print $5}' | sed 's:/*$::')


for BUCKET in $BUCKETS; do
  echo "Processing bucket: $BUCKET"

  # Create bucket on target if it doesn't exist
  if ! mc ls target/$BUCKET > /dev/null 2>&1; then
    echo "Creating bucket $BUCKET on target..."
    mc mb target/$BUCKET
  else
    echo "Bucket $BUCKET already exists on target."
  fi

  # Enable versioning (needed for replication)
  echo "Enabling versioning for $BUCKET..."
  mc version enable source/$BUCKET
  mc version enable target/$BUCKET

  # Configure replication
  echo "Configuring replication for $BUCKET..."
  mc replicate add source/$BUCKET                                   \
   --remote-bucket http://minio_user:minio_password@localhost:19002/$BUCKET
done

echo "All the buckets have been replicated successfully."
