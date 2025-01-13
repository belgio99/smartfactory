#!/bin/bash

# Configurazione degli endpoint e delle credenziali
SOURCE_ENDPOINT="http://localhost:19000"
SOURCE_ACCESS_KEY="minio_user"
SOURCE_SECRET_KEY="minio_password"

TARGET_ENDPOINT="http://localhost:29000"
TARGET_ACCESS_KEY="minio_user"
TARGET_SECRET_KEY="minio_password"

# Configurazione degli alias per MinIO Client (mc)
mc alias set source $SOURCE_ENDPOINT $SOURCE_ACCESS_KEY $SOURCE_SECRET_KEY
mc alias set target $TARGET_ENDPOINT $TARGET_ACCESS_KEY $TARGET_SECRET_KEY

# Ottenere la lista dei bucket sulla sorgente
echo "Recupero della lista dei bucket sulla sorgente..."
BUCKETS=$(mc ls source | awk '{print $5}' | sed 's:/*$::')

# Iterare su ogni bucket
for BUCKET in $BUCKETS; do
  echo "Elaborazione del bucket: $BUCKET"

  # Creare il bucket sul target se non esiste
  if ! mc ls target/$BUCKET > /dev/null 2>&1; then
    echo "Creazione del bucket $BUCKET sul target..."
    mc mb target/$BUCKET
  else
    echo "Il bucket $BUCKET esiste già sul target."
  fi

  # Abilitare il versioning (necessario per la replicazione)
  echo "Abilitazione del versioning per $BUCKET..."
  mc version enable source/$BUCKET
  mc version enable target/$BUCKET

  # Configurare la replicazione dal source al target
  echo "Configurazione della replicazione dal source al target per $BUCKET..."
  mc replicate add source/$BUCKET \
    --remote-bucket http://$TARGET_ACCESS_KEY:$TARGET_SECRET_KEY@minio-paris:9000/$BUCKET \
    --replicate "delete,delete-marker,existing-objects"

  # Configurare la replicazione dal target al source
  echo "Configurazione della replicazione dal target al source per $BUCKET..."
  mc replicate add target/$BUCKET \
    --remote-bucket http://$SOURCE_ACCESS_KEY:$SOURCE_SECRET_KEY@minio-milan:9000/$BUCKET \
    --replicate "delete,delete-marker,existing-objects"
done

echo "Tutti i bucket sono stati configurati per la replicazione bidirezionale con successo."
