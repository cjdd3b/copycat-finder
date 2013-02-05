from django.db import models

class State(models.Model):
    name = models.CharField(max_length=25)

    def __unicode__(self):
        return self.name


class Session(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Bill(models.Model):
    state = models.ForeignKey(State)
    session = models.ForeignKey(Session)
    chamber = models.CharField(max_length=255)
    bill_id = models.CharField(max_length=255)
    title = models.CharField(max_length=1000)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return '%s: %s %s' % (self.state.name, self.bill_id, self.title)