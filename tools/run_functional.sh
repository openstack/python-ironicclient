#!/bin/bash

FUNC_TEST_DIR=$(dirname $0)/../ironicclient/tests/functional/
CONFIG_FILE=$FUNC_TEST_DIR/test.conf

if [[ -n "$OS_AUTH_TOKEN" ]] && [[ -n "$IRONIC_URL" ]]; then
cat <<END >$CONFIG_FILE
[functional]
api_version = 1
auth_strategy=noauth
os_auth_token=$OS_AUTH_TOKEN
ironic_url=$IRONIC_URL
END
else
cat <<END >$CONFIG_FILE
[functional]
api_version = 1
os_auth_url=$OS_AUTH_URL
os_identity_api_version = $OS_IDENTITY_API_VERSION
os_username=$OS_USERNAME
os_password=$OS_PASSWORD
os_project_name=$OS_PROJECT_NAME
os_user_domain_id=$OS_USER_DOMAIN_ID
os_project_domain_id=$OS_PROJECT_DOMAIN_ID
os_service_type=baremetal
os_endpoint_type=public
END
fi
tox -e functional
