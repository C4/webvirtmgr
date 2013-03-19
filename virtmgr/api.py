from tastypie import fields, utils
from tastypie.resources import ModelResource
from tastypie.resources import Resource
from webvirtmgr.virtmgr.models import *



class HostsResource(ModelResource):
    def determine_format(self, request):
        return 'application/json'
    class Meta:
        queryset = Host.objects.all()
        resource_name = 'hosts'
        excludes = ['passwd','login','hostname','ipaddr']
        include_resource_uri = False

    # Changing some field names
    login_user = fields.CharField(attribute='login')
    name = fields.CharField(attribute='hostname')
    ip_address = fields.CharField(attribute='ipaddr')


class InstanceTypesResource(ModelResource):
    def determine_format(self, request):
        return 'application/json'
    class Meta:
        queryset = InstanceTypes.objects.all()
        resource_name = 'instance_types'
        excludes = ['disk','cpu']
        include_resource_uri = False
    # Changing some field names
    disk_size = fields.CharField(attribute='disk')
    cpu_number = fields.CharField(attribute='cpu')

class OSTypesResource(ModelResource):
    def determine_format(self, request):
        return 'application/json'
    class Meta:
        queryset = OSTypes.objects.all()
        resource_name = 'os_types'
        include_resource_uri = False


def libvirt_conn(host):
    """
    Function for connect to libvirt host.
    Create exceptions and return if not connnected.

    """

    import libvirt

    def creds(credentials, user_data):
        for credential in credentials:
            if credential[0] == libvirt.VIR_CRED_AUTHNAME:
                credential[4] = host.login
                if len(credential[4]) == 0:
                    credential[4] = credential[3]
            elif credential[0] == libvirt.VIR_CRED_PASSPHRASE:
                credential[4] = host.passwd
            else:
                return -1
        return 0

    flags = [libvirt.VIR_CRED_AUTHNAME, libvirt.VIR_CRED_PASSPHRASE]
    auth = [flags, creds, None]
    if host.connection_type == "tcp":
        uri = 'qemu+tcp://%s/system' % host.ipaddr
        try:
            conn = libvirt.openAuth(uri, auth, 0)
            return conn
        except libvirt.libvirtError as e:
            return {'error': e.message}
    if host.connection_type == "ssh":
        uri = 'qemu+ssh://%s@%s/system' % (host.login, host.ipaddr)
        try:
            conn = libvirt.open(uri)
            return conn
        except libvirt.libvirtError as e:
            return {'error': e.message}

def get_all_vm_info(conn, host):
    """

    Get a list of all VMs with info

    """

    import libvirt
    import virtinst.util as util
    import string

    states = {
        libvirt.VIR_DOMAIN_NOSTATE: 'no state',
        libvirt.VIR_DOMAIN_RUNNING: 'running',
        libvirt.VIR_DOMAIN_BLOCKED: 'blocked on resource',
        libvirt.VIR_DOMAIN_PAUSED: 'paused by user',
        libvirt.VIR_DOMAIN_SHUTDOWN: 'being shut down',
        libvirt.VIR_DOMAIN_SHUTOFF: 'shut off',
        libvirt.VIR_DOMAIN_CRASHED: 'crashed',
    }

    info = []
    try:
        for id in conn.listDomainsID():
            id = int(id)
            dom = conn.lookupByID(id)
            a = {"name":dom.name(),"hostid":host.id, "instanceid":dom.UUIDString(), "hypervisor":str(dom.OSType()), "ip":'', "fqdn":'', "cpu":str(dom.info()[3]),"mem":str(int(dom.info()[2]/1024)),"state":str(states.get(dom.info()[0])),"location":str(host)}
            info.append(a)
        for id in conn.listDefinedDomains():
            dom = conn.lookupByName(id)
            a = {"name":dom.name(),"hostid":host.id, "instanceid":dom.UUIDString(), "hypervisor":str(dom.OSType()), "ip":'', "fqdn":'', "cpu":str(dom.info()[3]),"mem":str(int(dom.info()[2]/1024)),"state":str(states.get(dom.info()[0])),"location":str(host)}
            info.append(a)
        return info
    except libvirt.libvirtError as e:
        add_error(e, 'libvirt')
        return "error"

class Instance(object):
    id = None
    instance_id = ''
    host_id = ''
    name = ''   
    ip = ''
    state = ''
    memory = ''
    cpu_number = ''
    location = ''
    virtualization_type = ''
    dns_name = ''

class InstancesResource(Resource):
    def determine_format(self, request):
        return 'application/json'

    class Meta:
        resource_name = 'instances'
        object_class = Instance
        include_resource_uri = False
        limit = 0

    id = fields.CharField(attribute='id')
    name = fields.CharField(attribute='name')
    instance_id = fields.CharField(attribute='instance_id')
    host_id = fields.CharField(attribute='host_id')
    ip = fields.CharField(attribute='ip')
    state = fields.CharField(attribute='state')
    memory = fields.IntegerField(attribute='memory')
    cpu_number = fields.IntegerField(attribute='cpu_number')
    location = fields.CharField(attribute='location')
    virtualization_type = fields.CharField(attribute='virtualization_type')
    dns_name = fields.CharField(attribute='dns_name')

    def obj_get_list(self, request = None, **kwargs):
        hosts = Host.objects.all()
        instance_list = []
        for host in hosts:
            conn = libvirt_conn(host)
            instances = get_all_vm_info(conn,host)
            if type(instances) is list:
                for index,instance in enumerate(instances):
                    i = Instance()
                    i.id = index
                    i.instance_id = instance['instanceid']
                    i.host_id = instance['hostid']
                    i.name = instance['name']
                    i.ip = instance['ip']
                    i.state = instance['state']
                    i.memory = instance['mem']
                    i.cpu_number = instance['cpu']
                    i.location = instance['location']
                    i.virtualization_type = instance['hypervisor']
                    i.dns_name = instance['fqdn']
                    instance_list.append(i)
        return instance_list


