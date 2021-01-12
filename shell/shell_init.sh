#!/bin/bash -e
/shell/shellinabox/shellinaboxd -t -d --port=9000 --disable-ssl --disable-peer-check --css /shell/custom.css --service "/:root:root:/home:AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION EXPORT_BUCKET=$EXPORT_BUCKET  AZURE_SUBSCRIPTION_ID=$AZURE_SUBSCRIPTION_ID AZURE_CLIENT_ID=$AZURE_CLIENT_ID AZURE_CLIENT_SECRET=$AZURE_CLIENT_SECRET AZURE_TENANT_ID=$AZURE_TENANT_ID JEEVA=KUMAR /shell/shell.sh \${url}"
