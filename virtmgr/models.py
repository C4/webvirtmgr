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

class InstanceMetaData(models.Model):
    name = models.CharField(max_length=32)
    ip = models.IPAddressField()
    owner = models.CharField(max_length=32)
    team = models.CharField(max_length=32)
    project = models.CharField(max_length=32)
    def __unicode__(self):
        return self.hostname

class InstanceTypes(models.Model):
    itid = models.CharField(max_length=4)
    name = models.CharField(max_length=32)
    cpu = models.CharField(max_length=4)
    memory = models.CharField(max_length=16)
    disk = models.CharField(max_length=32)
    def __unicode__(self):
        return self.name

class OSTypes(models.Model):
    osid = models.CharField(max_length=4)
    name = models.CharField(max_length=32)
    version = models.CharField(max_length=12)
    description = models.CharField(max_length=64)
    def __unicode__(self):
        return self.name