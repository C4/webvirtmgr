from django.db import models


class Host(models.Model):
    hostname = models.CharField(max_length=20)
    ipaddr = models.IPAddressField()
    login = models.CharField(max_length=12)
    passwd = models.CharField(max_length=20)
    connection_type = models.CharField(max_length=20)
    def __unicode__(self):
        return self.hostname


class Vm(models.Model):
    host = models.ForeignKey(Host)
    vname = models.CharField(max_length=12)
    vnc_passwd = models.CharField(max_length=12)
    def __unicode__(self):
        return self.vname

class Instance(models.Model):
    hostname = models.CharField(max_length=20)
    ipaddr = models.IPAddressField()
    architecture = models.CharField(max_length=8)
    instanceid = models.CharField(max_length=12)
    fqdn = models.CharField(max_length=64)
    cpu = models.CharField(max_length=8)
    mem = models.CharField(max_length=16)
    state = models.CharField(max_length=16)
    location = models.CharField(max_length=32)
    connection_type = models.CharField(max_length=20)
    def __unicode__(self):
        return self.vname