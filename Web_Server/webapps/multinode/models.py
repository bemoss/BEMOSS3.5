from __future__ import unicode_literals

from django.db import models
from webapps.buildinginfos.models import Building_Zone


class NodeInfo(models.Model):
    node_id = models.AutoField(primary_key=True)
    node_name = models.CharField(max_length=20)
    node_type = models.CharField(max_length=20,blank=True,null=True)
    #node_model = models.CharField(max_length=20,blank=True,null=True)
    node_status = models.CharField(max_length=20,blank=True,null=True)
    #building_name = models.CharField(max_length=20,blank=True,null=True)
    ip_address = models.GenericIPAddressField(blank=True,null=True)
    #mac_address = models.CharField(max_length=50, null=True, blank=True)
    #associated_zone = models.ForeignKey(Building_Zone, null=True, blank=True, db_column="associated_zone")
    #date_added = models.DateTimeField(blank=True,null=True)
    #communication = models.CharField(max_length=20,blank=True,null=True)
    last_scanned_time = models.DateTimeField(null=True, blank=True)
    last_offline_time = models.DateTimeField(null=True, blank=True)
    last_sync_time = models.DateTimeField(null=True, blank=True)
    node_resources_score = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = "node_info"

    def __unicode__(self):
        return str(self.node_id)

    def network_status(self):
        return dict(
            node_id=self.node_id,
            device_name=self.node_name.encode('utf-8').title() if self.node_name else '',
            device_type=self.node_type.encode('utf-8').title() if self.node_type else '',
            #device_model=self.node_model.encode('utf-8').title() if self.node_model else '',
            device_status=self.node_status.encode('utf-8').title() if self.node_status else '',
            #associated_zone=self.associated_zone,
            #date_added=self.date_added,
            ip_address=self.ip_address,
            last_scanned=self.last_scanned_time,
            last_offline=self.last_offline_time,
            node_resources_score=self.node_resources_score
            )

    def data_dashboard(self):
        zone_req = Building_Zone.as_json(self.associated_zone)
        return dict(
            node_id=self.node_id,
            device_name=self.node_name.encode('utf-8').title() if self.node_name else '',
            #device_model=self.node_model.encode('utf-8').title() if self.node_model else '',
            device_type=self.node_type.encode('utf-8').title() if self.node_type else '',
            #mac_address=self.mac_address.encode('utf-8') if self.mac_address else '',
            device_status=self.node_status.encode('utf-8').title() if self.node_status else '',
            #associated_zone=zone_req,
            ip_address=self.ip_address,
            #date_added=self.date_added,
            last_scanned=self.last_scanned_time,
            last_offline=self.last_offline_time,
            node_resources_score=self.node_resources_score)

    def as_json(self):
        return dict(
            node_id=self.node_id,
            node_status=self.node_status,
            node_resources_score=self.node_resources_score

        )


class NodeDeviceStatus(models.Model):
    agent_id = models.CharField(primary_key=True, max_length=50)
    assigned_node = models.ForeignKey(NodeInfo, null=True, blank=True, related_name='NodeDevice_previous')
    current_node = models.ForeignKey(NodeInfo, null=True, blank=True, related_name='NodeDevice_current')
    date_move = models.DateTimeField(null=True,blank=True)
    class Meta:
        db_table = "node_device"

    def __unicode__(self):
        return self.agent_id