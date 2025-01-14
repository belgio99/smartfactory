#!/bin/bash


SOURCE_ENDPOINT="http://localhost:19000"
SOURCE_ACCESS_KEY="minio_user"
SOURCE_SECRET_KEY="minio_password"

TARGET_ENDPOINT="http://localhost:29000"
TARGET_ACCESS_KEY="minio_user"
TARGET_SECRET_KEY="minio_password"


mc alias set source $SOURCE_ENDPOINT $SOURCE_ACCESS_KEY $SOURCE_SECRET_KEY
mc alias set target $TARGET_ENDPOINT $TARGET_ACCESS_KEY $TARGET_SECRET_KEY


echo "Getting buckets from source..."
BUCKETS=$(mc ls source | awk '{print $5}' | sed 's:/*$::')


for BUCKET in $BUCKETS; do
  echo "Working on bucket $BUCKET..."


  if ! mc ls target/$BUCKET > /dev/null 2>&1; then
    echo "Creating bucket $BUCKET on target..."
    mc mb target/$BUCKET
  else
    echo "Bucket $BUCKET already exists on target."
  fi


  echo "Enabling versioning for $BUCKET..."
  mc version enable source/$BUCKET
  mc version enable target/$BUCKET


  echo "Setting up replication from source to target for $BUCKET..."
  mc replicate add source/$BUCKET \
    --remote-bucket http://$TARGET_ACCESS_KEY:$TARGET_SECRET_KEY@minio-paris:9000/$BUCKET \
    --replicate "delete,delete-marker,existing-objects"


  echo "Setting up replication from target to source for $BUCKET..."
  mc replicate add target/$BUCKET \
    --remote-bucket http://$SOURCE_ACCESS_KEY:$SOURCE_SECRET_KEY@minio-milan:9000/$BUCKET \
    --replicate "delete,delete-marker,existing-objects"
done

echo "Replication setup complete."
