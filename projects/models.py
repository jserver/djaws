from django.db import models


# Create your models here.
class Address(models.Model):
    public_ip = models.CharField(max_length=15)

    class Meta:
        ordering = ('public_ip',)
        verbose_name_plural = 'addresses'

    def __unicode__(self):
        return self.publc_ip


class Build(models.Model):
    SIZE_CHOICES = (
        ('m', 't1.micro'),
        ('S', 'm1.small'),
        ('M', 'm1.medium'),
        ('L', 'm1.large'),
        ('XL','m1.xlarge'),
    )
    UPGRADE_CHOICES = (
        ('up', 'upgrade'),
        ('du', 'dist-upgrade'),
    )
    ZONE_CHOICES = (
        ('a', 'us-east-1a'),
        ('b', 'us-east-1b'),
        ('c', 'us-east-1c'),
        ('d', 'us-east-1d'),
    )
    name = models.CharField(max_length=20)
    size = models.CharField(max_length=2, choices=SIZE_CHOICES)
    image = models.ForeignKey('Image')
    key = models.ForeignKey('Key', null=True, on_delete=models.SET_NULL)
    zone = models.CharField(max_length=1, choices=ZONE_CHOICES, blank=True)
    security_groups = models.ManyToManyField('SecurityGroup')
    group = models.ForeignKey('Group')
    python_bundle = models.ForeignKey('PythonBundle')
    user_data = models.ForeignKey('Script')
    upgrade = models.CharField(max_length=2, choices=UPGRADE_CHOICES, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class Bundle(models.Model):
    name = models.CharField(max_length=20)
    packages = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class GroupItem(models.Model):
    group = models.ForeignKey('Group', null=True, blank=True)
    bundle = models.ForeignKey('Bundle', null=True, blank=True)
    packages = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        if self.group_id:
            return "Group: %s" % self.group.name
        elif self.bundle_id:
            return "Bundle: %s" % self.bundle.name
        elif self.packages:
            return "Package: %s" % self.packages

        return "Unknown GroupItem"


class GroupOrder(models.Model):
    group = models.ForeignKey('Group')
    group_item = models.ForeignKey('GroupItem')
    order = models.IntegerField(default=0)


class Group(models.Model):
    name = models.CharField(max_length=20)
    items = models.ManyToManyField('GroupItem', through='GroupOrder', related_name='parent')

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class Image(models.Model):
    image_id = models.CharField(max_length=20)
    name = models.CharField(max_length=20)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class Instance(models.Model):
    inst_id = models.CharField(max_length=10)
    name = models.CharField(max_length=20)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class Key(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class LinuxUser(models.Model):
    name = models.CharField(max_length=40)
    full_name = models.CharField(max_length=40)
    password = models.CharField(max_length=40)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=20)
    build = models.ForeignKey('Build')
    count = models.IntegerField(default=1)
    linux_user = models.ForeignKey('LinuxUser')
    user_script = models.ForeignKey('Script')

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class PythonBundle(models.Model):
    name = models.CharField(max_length=20)
    packages = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class Script(models.Model):
    name = models.CharField(max_length=20)
    data = models.TextField()

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class SecurityGroup(models.Model):
    id = models.CharField(max_length=11, primary_key=True)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name
