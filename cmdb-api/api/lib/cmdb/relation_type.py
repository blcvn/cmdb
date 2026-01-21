# -*- coding:utf-8 -*-


from flask import abort

from api.lib.cmdb.resp_format import ErrFormat
from api.models.cmdb import RelationType


class RelationTypeManager(object):
    cls = RelationType

    @staticmethod
    def get_all():
        return RelationType.get_by(to_dict=False)

    @classmethod
    def get_names(cls):
        return [i.name for i in cls.get_all()]

    @classmethod
    def get_pairs(cls):
        return [(i.id, i.name) for i in cls.get_all()]

    @staticmethod
    def add(name, description=None, first_ci_to_second_ci_impact=0, second_ci_to_first_ci_impact=0):
        RelationType.get_by(name=name, first=True, to_dict=False) and abort(
            400, ErrFormat.relation_type_exists.format(name))

        return RelationType.create(
            name=name,
            description=description,
            first_ci_to_second_ci_impact=first_ci_to_second_ci_impact,
            second_ci_to_first_ci_impact=second_ci_to_first_ci_impact
        )

    @staticmethod
    def update(rel_id, name=None, description=None, first_ci_to_second_ci_impact=None, second_ci_to_first_ci_impact=None):
        existed = RelationType.get_by_id(rel_id) or abort(
            404, ErrFormat.relation_type_not_found.format("id={}".format(rel_id)))

        update_data = {}
        if name is not None:
            update_data['name'] = name
        if description is not None:
            update_data['description'] = description
        if first_ci_to_second_ci_impact is not None:
            update_data['first_ci_to_second_ci_impact'] = first_ci_to_second_ci_impact
        if second_ci_to_first_ci_impact is not None:
            update_data['second_ci_to_first_ci_impact'] = second_ci_to_first_ci_impact

        return existed.update(**update_data)

    @staticmethod
    def delete(rel_id):
        existed = RelationType.get_by_id(rel_id) or abort(
            404, ErrFormat.relation_type_not_found.format("id={}".format(rel_id)))

        existed.soft_delete()
