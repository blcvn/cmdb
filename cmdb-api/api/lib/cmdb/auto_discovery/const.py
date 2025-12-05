# -*- coding:utf-8 -*-

from api.lib.cmdb.const import AutoDiscoveryType

PRIVILEGED_USERS = ("cmdb_agent", "worker", "admin")

NET_DEVICE_NAMES = {"switch", 'router', 'firewall', 'printer'}

DEFAULT_INNER = []

CLOUD_MAP = {
    "aliyun": [
        {
            "category": "Compute",
            "items": ["ECS", "ECS Disk"],
            "map": {
                "ECS": {"template": "templates/aliyun_ecs.json", "mapping": "ecs"},
                "ECS Disk": {"template": "templates/aliyun_ecs_disk.json", "mapping": "evs"},
            },
            "collect_key_map": {
                "ECS": "ali.ecs",
                "ECS Disk": "ali.ecs_disk",
            },
        },
        {
            "category": "Network & CDN",
            "items": [
                "CDN",
                "SLB Load Balancer",
                "VPC",
                "Switch",
            ],
            "map": {
                "CDN": {"template": "templates/aliyun_cdn.json", "mapping": "CDN"},
                "SLB Load Balancer": {"template": "templates/aliyun_slb.json", "mapping": "loadbalancer"},
                "VPC": {"template": "templates/aliyun_vpc.json", "mapping": "vpc"},
                "Switch": {"template": "templates/aliyun_switch.json", "mapping": "vswitch"},
            },
            "collect_key_map": {
                "CDN": "ali.cdn",
                "SLB Load Balancer": "ali.slb",
                "VPC": "ali.vpc",
                "Switch": "ali.switch",
            },
        },
        {
            "category": "Storage",
            "items": ["EBS", "OSS"],
            "map": {
                "EBS": {"template": "templates/aliyun_ebs.json", "mapping": "evs"},
                "OSS": {"template": "templates/aliyun_oss.json", "mapping": "objectStorage"},
            },
            "collect_key_map": {
                "EBS": "ali.ebs",
                "OSS": "ali.oss",
            },
        },
        {
            "category": "Database",
            "items": ["RDS MySQL", "RDS PostgreSQL", "Redis"],
            "map": {
                "RDS MySQL": {"template": "templates/aliyun_rds_mysql.json", "mapping": "mysql"},
                "RDS PostgreSQL": {"template": "templates/aliyun_rds_postgre.json", "mapping": "postgresql"},
                "Redis": {"template": "templates/aliyun_redis.json", "mapping": "redis"},
            },
            "collect_key_map": {
                "RDS MySQL": "ali.rds_mysql",
                "RDS PostgreSQL": "ali.rds_postgre",
                "Redis": "ali.redis",
            },
        },
    ],
    "tencentcloud": [
        {
            "category": "Compute",
            "items": ["CVM"],
            "map": {
                "CVM": {"template": "templates/tencent_cvm.json", "mapping": "ecs"},
            },
            "collect_key_map": {
                "CVM": "tencent.cvm",
            },
        },
        {
            "category": "CDN & Edge",
            "items": ["CDN"],
            "map": {
                "CDN": {"template": "templates/tencent_cdn.json", "mapping": "CDN"},
            },
            "collect_key_map": {
                "CDN": "tencent.cdn",
            },
        },
        {
            "category": "Network",
            "items": ["CLB", "VPC", "Subnet"],
            "map": {
                "CLB": {"template": "templates/tencent_clb.json", "mapping": "loadbalancer"},
                "VPC": {"template": "templates/tencent_vpc.json", "mapping": "vpc"},
                "Subnet": {"template": "templates/tencent_subnet.json", "mapping": "vswitch"},
            },
            "collect_key_map": {
                "CLB": "tencent.clb",
                "VPC": "tencent.vpc",
                "Subnet": "tencent.subnet",
            },
        },
        {
            "category": "Storage",
            "items": ["CBS", "COS"],
            "map": {
                "CBS": {"template": "templates/tencent_cbs.json", "mapping": "evs"},
                "COS": {"template": "templates/tencent_cos.json", "mapping": "objectStorage"},
            },
            "collect_key_map": {
                "CBS": "tencent.cbs",
                "COS": "tencent.cos",
            },
        },
        {
            "category": "Database",
            "items": ["RDS MySQL", "RDS PostgreSQL", "Redis"],
            "map": {
                "RDS MySQL": {"template": "templates/tencent_rdb.json", "mapping": "mysql"},
                "RDS PostgreSQL": {"template": "templates/tencent_postgres.json", "mapping": "postgresql"},
                "Redis": {"template": "templates/tencent_redis.json", "mapping": "redis"},
            },
            "collect_key_map": {
                "RDS MySQL": "tencent.rdb",
                "RDS PostgreSQL": "tencent.rds_postgres",
                "Redis": "tencent.redis",
            },
        },
    ],
    "huaweicloud": [
        {
            "category": "Compute",
            "items": ["ECS"],
            "map": {
                "ECS": {"template": "templates/huaweicloud_ecs.json", "mapping": "ecs"},
            },
            "collect_key_map": {
                "ECS": "huawei.ecs",
            },
        },
        {
            "category": "CDN & Edge",
            "items": ["CDN"],
            "map": {
                "CDN": {"template": "templates/huawei_cdn.json", "mapping": "CDN"},
            },
            "collect_key_map": {
                "CDN": "huawei.cdn",
            },
        },
        {
            "category": "Network",
            "items": ["ELB", "VPC", "Subnet"],
            "map": {
                "ELB": {"template": "templates/huawei_elb.json", "mapping": "loadbalancer"},
                "VPC": {"template": "templates/huawei_vpc.json", "mapping": "vpc"},
                "Subnet": {"template": "templates/huawei_subnet.json", "mapping": "vswitch"},
            },
            "collect_key_map": {
                "ELB": "huawei.elb",
                "VPC": "huawei.vpc",
                "Subnet": "huawei.subnet",
            },
        },
        {
            "category": "Storage",
            "items": ["EVS", "OBS"],
            "map": {
                "EVS": {"template": "templates/huawei_evs.json", "mapping": "evs"},
                "OBS": {"template": "templates/huawei_obs.json", "mapping": "objectStorage"},
            },
            "collect_key_map": {
                "EVS": "huawei.evs",
                "OBS": "huawei.obs",
            },
        },
        {
            "category": "Database",
            "items": ["RDS MySQL", "RDS PostgreSQL"],
            "map": {
                "RDS MySQL": {"template": "templates/huawei_rds_mysql.json", "mapping": "mysql"},
                "RDS PostgreSQL": {"template": "templates/huawei_rds_postgre.json", "mapping": "postgresql"},
            },
            "collect_key_map": {
                "RDS MySQL": "huawei.rds_mysql",
                "RDS PostgreSQL": "huawei.rds_postgre",
            },
        },
        {
            "category": "Middleware",
            "items": ["Redis"],
            "map": {
                "Redis": {"template": "templates/huawei_dcs.json", "mapping": "redis"},
            },
            "collect_key_map": {
                "Redis": "huawei.dcs",
            },
        },
    ],
    "aws": [
        {
            "category": "Compute",
            "items": ["EC2"],
            "map": {
                "EC2": {"template": "templates/aws_ec2.json", "mapping": "ecs"},
            },
            "collect_key_map": {
                "EC2": "aws.ec2",
            },
        },
        {"category": "Network & CDN", "items": [], "map": {}, "collect_key_map": {}},
    ],
    "vcenter": [
        {
            "category": "Compute",
            "items": [
                "Host",
                "Virtual Machine",
                "Host Cluster"
            ],
            "map": {
                "Host": "templates/vsphere_host.json",
                "Virtual Machine": "templates/vsphere_vm.json",
                "Host Cluster": "templates/vsphere_cluster.json",
            },
            "collect_key_map": {
                "Host": "vsphere.host",
                "Virtual Machine": "vsphere.vm",
                "Host Cluster": "vsphere.cluster",
            },
        },
        {
            "category": "Network",
            "items": [
                "Network",
                "Standard Switch",
                "Distributed Switch",
            ],
            "map": {
                "Network": "templates/vsphere_network.json",
                "Standard Switch": "templates/vsphere_standard_switch.json",
                "Distributed Switch": "templates/vsphere_distributed_switch.json",
            },
            "collect_key_map": {
                "Network": "vsphere.network",
                "Standard Switch": "vsphere.standard_switch",
                "Distributed Switch": "vsphere.distributed_switch",
            },
        },
        {
            "category": "Storage",
            "items": ["Datastore", "Datastore Cluster"],
            "map": {
                "Datastore": "templates/vsphere_datastore.json",
                "Datastore Cluster": "templates/vsphere_storage_pod.json",
            },
            "collect_key_map": {
                "Datastore": "vsphere.datastore",
                "Datastore Cluster": "vsphere.storage_pod",
            },
        },
        {
            "category": "Others",
            "items": ["Resource Pool", "Datacenter", "Folder"],
            "map": {
                "Resource Pool": "templates/vsphere_pool.json",
                "Datacenter": "templates/vsphere_datacenter.json",
                "Folder": "templates/vsphere_folder.json",
            },
            "collect_key_map": {
                "Resource Pool": "vsphere.pool",
                "Datacenter": "vsphere.datacenter",
                "Folder": "vsphere.folder",
            },
        },
    ],
    "kvm": [
        {
            "category": "Compute",
            "items": ["Virtual Machine"],
            "map": {
                "Virtual Machine": "templates/kvm_vm.json",
            },
            "collect_key_map": {
                "Virtual Machine": "kvm.vm",
            },
        },
        {
            "category": "Storage",
            "items": ["Storage"],
            "map": {
                "Storage": "templates/kvm_storage.json",
            },
            "collect_key_map": {
                "Storage": "kvm.storage",
            },
        },
        {
            "category": "network",
            "items": ["Network"],
            "map": {
                "Network": "templates/kvm_network.json",
            },
            "collect_key_map": {
                "Network": "kvm.network",
            },
        },
    ],
}
