import click
import json
import os
from common import CheckEmptyParam
from common import validateTenantAccess
from common import CONFIG_FILE
from common import CheckAndGetConnection

@click.group()
@click.pass_context
def connection(ctx):
    pass

@connection.command('connect')
@click.option('--tenant', '-t', default='', help='Name of the tenant or workspace. You can find this at the top right in the DuploCloud UI')
@click.option('--url', '-c', default='', help='url of the duplocloud service you are subscribed to. For example https://portal.duplocloud.net')
@click.option('--key', '-k', default='', help='Api key to connect to duplocloud service you are subscribed to')
@click.option('--tenantid', '-i', default=None, help='Api key to connect to duplocloud service you are subscribed to')
@click.pass_obj
def set_connection(ctx, tenant, url, key, tenantid):

    CheckEmptyParam('tenant', tenant, "tenant name cannot be empty")
    CheckEmptyParam('url', url, "url cannot be empty")
    CheckEmptyParam('key', key, "token cannot be empty")
    
    validateTenantAccess(tenant, key, url, tenantId=tenantid)

    data = json.dumps({'DUPLO_TENANT_NAME': tenant, 'DUPLO_TOKEN': key, 'DUPLO_URL': url, 'DUPLO_TENANT_ID': tenantid})
    file = open(CONFIG_FILE, "w")
    file.write(data)
    file.close()

@connection.command('switch_tenant')
@click.option('--tenant', '-t', default='', help='Name of the tenant or workspace. You can find this at the top right in the DuploCloud UI')
@click.pass_obj
def set_connection(ctx, tenant):

    CheckEmptyParam('tenant', tenant, "tenant name cannot be empty")
    oldtenant, token, url, oldtenantId = CheckAndGetConnection()
    tenantid = validateTenantAccess(tenant, token, url, tenantId=None)

    data = json.dumps({'DUPLO_TENANT_NAME': tenant, 'DUPLO_TOKEN': token, 'DUPLO_URL': url, 'DUPLO_TENANT_ID': tenantid})
    file = open(CONFIG_FILE, "w")
    file.write(data)
    file.close()