# -*- coding:utf-8 -*-

from datetime import date, datetime

from api.extensions import db
from api.lib.database import Model


class CIGrowthSnapshot(Model):
    """CI Growth Snapshot - Daily snapshot of CI counts by type"""
    __tablename__ = "r_ci_growth_snapshots"

    snapshot_date = db.Column(db.Date, nullable=False, index=True)
    ci_type_id = db.Column(db.Integer, nullable=False, index=True)
    ci_type_name = db.Column(db.String(32), nullable=False)
    total_count = db.Column(db.Integer, nullable=False, default=0)
    created_count = db.Column(db.Integer, default=0)  # New CIs created in period
    deleted_count = db.Column(db.Integer, default=0)  # CIs deleted in period

    __table_args__ = (
        db.UniqueConstraint('snapshot_date', 'ci_type_id', name='uq_growth_snapshot'),
    )


class CIGrowthConfig(Model):
    """CI Growth Configuration"""
    __tablename__ = "r_ci_growth_config"

    name = db.Column(db.String(128), nullable=False)
    ci_type_ids = db.Column(db.JSON)  # NULL = all types
    period = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly
    enabled = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer)


class AppModelSnapshot(Model):
    """Application Model Snapshot"""
    __tablename__ = "r_app_model_snapshots"

    snapshot_date = db.Column(db.Date, nullable=False, index=True)
    app_id = db.Column(db.Integer, index=True)  # CI ID of Application
    app_name = db.Column(db.String(128), nullable=False)
    environment = db.Column(db.String(20))  # DC, DR, UAT
    site = db.Column(db.String(64))  # VNPAY, GDS, HCM, etc.
    layer = db.Column(db.String(20))  # Application, Middleware, System, etc.
    component_count = db.Column(db.Integer, default=0)
    relation_count = db.Column(db.Integer, default=0)
    health_status = db.Column(db.String(20))  # healthy, warning, critical


class AppModelRelation(Model):
    """Application Model Relations"""
    __tablename__ = "r_app_model_relations"

    snapshot_date = db.Column(db.Date, nullable=False, index=True)
    app_id = db.Column(db.Integer, nullable=False, index=True)
    from_ci_id = db.Column(db.Integer, nullable=False)
    from_ci_type = db.Column(db.String(32))
    from_layer = db.Column(db.String(20))
    to_ci_id = db.Column(db.Integer, nullable=False)
    to_ci_type = db.Column(db.String(32))
    to_layer = db.Column(db.String(20))
    relation_type = db.Column(db.String(32))


class PhysicalSnapshot(Model):
    """Physical Infrastructure Snapshot"""
    __tablename__ = "r_physical_snapshots"

    snapshot_date = db.Column(db.Date, nullable=False, index=True)
    datacenter_id = db.Column(db.Integer, index=True)
    datacenter_name = db.Column(db.String(128))
    server_room_id = db.Column(db.Integer, index=True)
    server_room_name = db.Column(db.String(128))
    rack_id = db.Column(db.Integer, index=True)
    rack_name = db.Column(db.String(128))
    total_u = db.Column(db.Integer, default=42)
    used_u = db.Column(db.Integer, default=0)
    free_u = db.Column(db.Integer, default=42)
    server_count = db.Column(db.Integer, default=0)
    network_device_count = db.Column(db.Integer, default=0)
    storage_count = db.Column(db.Integer, default=0)
    power_consumption_kw = db.Column(db.Numeric(10, 2))


class PhysicalAsset(Model):
    """Physical Assets"""
    __tablename__ = "r_physical_assets"

    snapshot_date = db.Column(db.Date, nullable=False, index=True)
    asset_type = db.Column(db.String(32))  # server, network_device, storage
    asset_id = db.Column(db.Integer, index=True)  # CI ID
    asset_name = db.Column(db.String(128))
    datacenter_id = db.Column(db.Integer, index=True)
    rack_id = db.Column(db.Integer, index=True)
    rack_u_start = db.Column(db.Integer)
    rack_u_end = db.Column(db.Integer)
    status = db.Column(db.String(20))  # active, decommissioned, maintenance


class ResourceStatsSnapshot(Model):
    """Resource Statistics Snapshot"""
    __tablename__ = "r_resource_stats_snapshots"

    snapshot_date = db.Column(db.Date, nullable=False, index=True)
    resource_type = db.Column(db.String(32), nullable=False, index=True)  # server, network, storage
    ci_type_id = db.Column(db.Integer, index=True)
    ci_type_name = db.Column(db.String(32))
    total_count = db.Column(db.Integer, default=0)
    total_cpu_cores = db.Column(db.Integer, default=0)
    total_memory_gb = db.Column(db.Integer, default=0)
    total_storage_tb = db.Column(db.Numeric(10, 2), default=0)
    used_storage_tb = db.Column(db.Numeric(10, 2), default=0)
    free_storage_tb = db.Column(db.Numeric(10, 2), default=0)
    environment = db.Column(db.String(20))  # DC, DR, UAT
    site = db.Column(db.String(64))









