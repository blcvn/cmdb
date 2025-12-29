# -*- coding:utf-8 -*-

import json

from flask import abort
from flask import current_app
from flask_login import current_user
from werkzeug.exceptions import BadRequest

from api.extensions import rd
from api.lib.cmdb.cache import AttributeCache
from api.lib.cmdb.cache import CITypeCache
from api.lib.cmdb.ci import CIRelationManager
from api.lib.cmdb.ci_type import CITypeRelationManager
from api.lib.cmdb.const import REDIS_PREFIX_CI_RELATION
from api.lib.cmdb.const import ResourceTypeEnum
from api.lib.cmdb.resp_format import ErrFormat
from api.lib.cmdb.search import SearchError
from api.lib.cmdb.search.ci import search as ci_search
from api.lib.perm.acl.acl import ACLManager
from api.lib.perm.acl.acl import is_app_admin
from api.models.cmdb import TopologyView
from api.models.cmdb import TopologyViewGroup


class TopologyViewManager(object):
    group_cls = TopologyViewGroup
    cls = TopologyView

    @classmethod
    def get_name_by_id(cls, _id):
        res = cls.cls.get_by_id(_id)
        return res and res.name

    def get_view_by_id(self, _id):
        res = self.cls.get_by_id(_id)

        return res and res.to_dict() or {}

    @classmethod
    def add_group(cls, name, order):
        if order is None:
            cur_max_order = cls.group_cls.get_by(only_query=True).order_by(cls.group_cls.order.desc()).first()
            cur_max_order = cur_max_order and cur_max_order.order or 0
            order = cur_max_order + 1

        cls.group_cls.get_by(name=name, first=True, to_dict=False) and abort(
            400, ErrFormat.topology_group_exists.format(name))

        result = cls.group_cls.create(name=name, order=order)
        
        # Invalidate cache
        cls._invalidate_get_all_cache()
        
        return result

    def update_group(self, group_id, name, view_ids):
        existed = self.group_cls.get_by_id(group_id) or abort(404, ErrFormat.not_found)
        if name is not None and name != existed.name:
            existed.update(name=name)

        for idx, view_id in enumerate(view_ids):
            view = self.cls.get_by_id(view_id)
            if view is not None:
                view.update(group_id=group_id, order=idx)

        # Invalidate cache
        self._invalidate_get_all_cache()

        return existed.to_dict()

    @classmethod
    def delete_group(cls, _id):
        existed = cls.group_cls.get_by_id(_id) or abort(404, ErrFormat.not_found)

        if cls.cls.get_by(group_id=_id, first=True):
            return abort(400, ErrFormat.topo_view_exists_cannot_delete_group)

        existed.soft_delete()
        
        # Invalidate cache
        cls._invalidate_get_all_cache()

    @classmethod
    def group_order(cls, group_ids):
        for idx, group_id in enumerate(group_ids):
            group = cls.group_cls.get_by_id(group_id)
            group.update(order=idx + 1)
        
        # Invalidate cache
        cls._invalidate_get_all_cache()

    @classmethod
    def add(cls, name, group_id, option, order=None, **kwargs):
        cls.cls.get_by(name=name, first=True) and abort(400, ErrFormat.topology_exists.format(name))
        if order is None:
            cur_max_order = cls.cls.get_by(group_id=group_id, only_query=True).order_by(
                cls.cls.order.desc()).first()
            cur_max_order = cur_max_order and cur_max_order.order or 0
            order = cur_max_order + 1

        inst = cls.cls.create(name=name, group_id=group_id, option=option, order=order, **kwargs).to_dict()
        if current_app.config.get('USE_ACL'):
            try:
                ACLManager().add_resource(name, ResourceTypeEnum.TOPOLOGY_VIEW)
            except BadRequest:
                pass

            ACLManager().grant_resource_to_role(name,
                                                current_user.username,
                                                ResourceTypeEnum.TOPOLOGY_VIEW)

        # Invalidate cache
        cls._invalidate_get_all_cache()
        cls._invalidate_topology_view_cache()  # Invalidate all view result caches

        return inst

    @classmethod
    def update(cls, _id, **kwargs):
        existed = cls.cls.get_by_id(_id) or abort(404, ErrFormat.not_found)
        existed_name = existed.name

        inst = existed.update(filter_none=False, **kwargs).to_dict()
        if current_app.config.get('USE_ACL') and existed_name != kwargs.get('name') and kwargs.get('name'):
            try:
                ACLManager().update_resource(existed_name, kwargs['name'], ResourceTypeEnum.TOPOLOGY_VIEW)
            except BadRequest:
                pass

        # Invalidate cache
        cls._invalidate_get_all_cache()
        cls._invalidate_topology_view_cache(_id)  # Invalidate specific view result cache

        return inst

    @classmethod
    def delete(cls, _id):
        existed = cls.cls.get_by_id(_id) or abort(404, ErrFormat.not_found)

        existed.soft_delete()
        
        # Invalidate cache
        cls._invalidate_get_all_cache()
        cls._invalidate_topology_view_cache(_id)  # Invalidate specific view result cache
        if current_app.config.get("USE_ACL"):
            ACLManager().del_resource(existed.name, ResourceTypeEnum.TOPOLOGY_VIEW)

    @classmethod
    def group_inner_order(cls, _ids):
        for idx, _id in enumerate(_ids):
            topology = cls.cls.get_by_id(_id)
            topology.update(order=idx + 1)
        
        # Invalidate cache
        cls._invalidate_get_all_cache()

    @classmethod
    def _invalidate_get_all_cache(cls):
        """Invalidate all topology_views cache (for all users)"""
        try:
            # Delete base cache key
            rd.r.delete("TOPOLOGY_VIEWS:topology_views:all")
            
            # Try to delete user-specific keys using Redis SCAN
            try:
                pattern = "TOPOLOGY_VIEWS:topology_views:all:user:*"
                cursor = 0
                deleted_count = 0
                while True:
                    cursor, keys = rd.r.scan(cursor, match=pattern, count=100)
                    if keys:
                        for key in keys:
                            rd.r.delete(key)
                            deleted_count += 1
                    if cursor == 0:
                        break
                if deleted_count > 0:
                    current_app.logger.debug(f"Deleted {deleted_count} user-specific topology_views cache keys")
            except Exception as scan_error:
                # If SCAN fails, log warning but continue
                current_app.logger.debug(f"Could not scan keys for topology_views cache: {str(scan_error)}")
            
            current_app.logger.debug("Invalidated topology_views cache")
        except Exception as e:
            current_app.logger.warning(f"Failed to invalidate topology_views cache: {str(e)}")

    @classmethod
    def _invalidate_topology_view_cache(cls, view_id=None):
        """Invalidate topology view result cache for a specific view or all views"""
        try:
            if view_id:
                # Delete specific view cache
                cache_key = f"TOPOLOGY_VIEW_RESULT:topology_view:result:{view_id}"
                rd.r.delete(cache_key)
                current_app.logger.debug(f"Invalidated topology_view result cache for view {view_id}")
            else:
                # Delete all topology view result caches using Redis SCAN
                try:
                    pattern = "TOPOLOGY_VIEW_RESULT:topology_view:result:*"
                    cursor = 0
                    deleted_count = 0
                    while True:
                        cursor, keys = rd.r.scan(cursor, match=pattern, count=100)
                        if keys:
                            for key in keys:
                                rd.r.delete(key)
                                deleted_count += 1
                        if cursor == 0:
                            break
                    if deleted_count > 0:
                        current_app.logger.debug(f"Invalidated {deleted_count} topology_view result caches")
                except Exception as scan_error:
                    current_app.logger.debug(f"Could not scan keys for topology_view result cache: {str(scan_error)}")
        except Exception as e:
            current_app.logger.warning(f"Failed to invalidate topology_view result cache: {str(e)}")

    @classmethod
    def get_all(cls):
        # Cache key includes user info because ACL filtering is user-specific
        cache_key = f"TOPOLOGY_VIEWS:topology_views:all"
        if current_app.config.get('USE_ACL') and not is_app_admin('cmdb'):
            user_id = getattr(current_user, 'uid', None) or getattr(current_user, 'id', None) or 'anonymous'
            cache_key = f"TOPOLOGY_VIEWS:topology_views:all:user:{user_id}"
        
        # Try to get from cache
        cached = rd.get_str(cache_key)
        if cached:
            try:
                # Handle bytes response from Redis
                if isinstance(cached, bytes):
                    cached = cached.decode('utf-8')
                result = json.loads(cached)
                current_app.logger.debug(f"Cache hit for topology_views:all")
                return result
            except (json.JSONDecodeError, TypeError, UnicodeDecodeError):
                current_app.logger.warning(f"Failed to parse cached topology_views, fetching from DB")
        
        current_app.logger.debug(f"Cache not hit for topology_views:all, fetching from DB")
        
        resources = None
        if current_app.config.get('USE_ACL') and not is_app_admin('cmdb'):
            resources = set([i.get('name') for i in ACLManager().get_resources(ResourceTypeEnum.TOPOLOGY_VIEW)])

        groups = cls.group_cls.get_by(to_dict=True)
        groups = sorted(groups, key=lambda x: x['order'])
        group2pos = {group['id']: idx for idx, group in enumerate(groups)}

        topo_views = sorted(cls.cls.get_by(to_dict=True), key=lambda x: x['order'])
        other_group = dict(views=[])
        for view in topo_views:
            if resources is not None and view['name'] not in resources:
                continue

            if view['group_id']:
                groups[group2pos[view['group_id']]].setdefault('views', []).append(view)
            else:
                other_group['views'].append(view)

        if other_group['views']:
            groups.append(other_group)

        # Cache the result (TTL: 5 minutes)
        try:
            rd.set_str(cache_key, json.dumps(groups), expired=300)
        except Exception as e:
            current_app.logger.warning(f"Failed to cache topology_views: {str(e)}")

        return groups

    @staticmethod
    def relation_from_ci_type(type_id):
        nodes, edges = CITypeRelationManager.get_relations_by_type_id(type_id)

        return dict(nodes=nodes, edges=edges)

    def topology_view(self, view_id=None, preview=None):
        # Cache key for topology view result
        cache_key = None
        if view_id is not None:
            # Cache by view_id
            cache_key = f"TOPOLOGY_VIEW_RESULT:topology_view:result:{view_id}"
            # Try to get from cache
            cached = rd.get_str(cache_key)
            if cached:
                try:
                    # Handle bytes response from Redis
                    if isinstance(cached, bytes):
                        cached = cached.decode('utf-8')
                    result = json.loads(cached)
                    current_app.logger.debug(f"Cache hit for topology_view:{view_id}")
                    return result
                except (json.JSONDecodeError, TypeError, UnicodeDecodeError):
                    current_app.logger.warning(f"Failed to parse cached topology_view result, fetching from DB")
            
            current_app.logger.debug(f"Cache not hit for topology_view:{view_id}, fetching from DB")
            
            view = self.cls.get_by_id(view_id) or abort(404, ErrFormat.not_found)
            central_node_type, central_node_instances, path = (view.central_node_type,
                                                               view.central_node_instances, view.path)
        else:
            # Preview mode - don't cache (dynamic query)
            central_node_type = preview.get('central_node_type')
            central_node_instances = preview.get('central_node_instances')
            path = preview.get('path')

        nodes, links = [], []
        _type = CITypeCache.get(central_node_type)
        if not _type:
            return dict(nodes=nodes, links=links)
        type2meta = {_type.id: _type.icon}
        root_ids = []
        show_key = AttributeCache.get(_type.show_id or _type.unique_id)

        q = (central_node_instances[2:] if central_node_instances.startswith('q=') else
             central_node_instances)
        s = ci_search(q, fl=['_id', show_key.name], use_id_filter=False, use_ci_filter=False, count=1000000)
        try:
            response, _, _, _, _, _ = s.search()
        except SearchError as e:
            current_app.logger.info(e)
            return dict(nodes=nodes, links=links)
        for i in response:
            root_ids.append(i['_id'])
            nodes.append(dict(id=str(i['_id']), name=i[show_key.name], type_id=central_node_type))
        if not root_ids:
            return dict(nodes=nodes, links=links)

        prefix = REDIS_PREFIX_CI_RELATION
        key = list(map(str, root_ids))
        id2node = {}
        for level in sorted([i for i in path.keys() if int(i) > 0]):
            type_ids = {int(i) for i in path[level]}

            res = [json.loads(x).items() for x in [i or '{}' for i in rd.get(key, prefix) or []]]
            new_key = []
            for idx, from_id in enumerate(key):
                for to_id, type_id in res[idx]:
                    if type_id in type_ids:
                        links.append({'from': from_id, 'to': to_id})
                        id2node[to_id] = {'id': to_id, 'type_id': type_id}
                        new_key.append(to_id)
                        if type_id not in type2meta:
                            type2meta[type_id] = CITypeCache.get(type_id).icon

            key = new_key

        ci_ids = list(map(int, root_ids))
        for level in sorted([i for i in path.keys() if int(i) < 0]):
            type_ids = {int(i) for i in path[level]}
            res = CIRelationManager.get_parent_ids(ci_ids)
            _ci_ids = []
            for to_id in res:
                for from_id, type_id in res[to_id]:
                    if type_id in type_ids:
                        from_id, to_id = str(from_id), str(to_id)
                        links.append({'from': from_id, 'to': to_id})
                        id2node[from_id] = {'id': str(from_id), 'type_id': type_id}
                        _ci_ids.append(from_id)
                        if type_id not in type2meta:
                            type2meta[type_id] = CITypeCache.get(type_id).icon

            ci_ids = _ci_ids

        fl = set()
        type_ids = {t for lv in path if lv != '0' for t in path[lv]}
        type2show = {}
        for type_id in type_ids:
            ci_type = CITypeCache.get(type_id)
            if ci_type:
                attr = AttributeCache.get(ci_type.show_id or ci_type.unique_id)
                if attr:
                    fl.add(attr.name)
                    type2show[type_id] = attr.name

        if id2node:
            s = ci_search("_id:({})".format(';'.join(id2node.keys())), fl=list(fl),
                       use_id_filter=False, use_ci_filter=False, count=1000000)
            try:
                response, _, _, _, _, _ = s.search()
            except SearchError:
                return dict(nodes=nodes, links=links)
            for i in response:
                id2node[str(i['_id'])]['name'] = i[type2show[str(i['_type'])]]
            nodes.extend(id2node.values())

        result = dict(nodes=nodes, links=links, type2meta=type2meta)
        
        # Cache the result if view_id is provided (not preview mode)
        if cache_key:
            try:
                rd.set_str(cache_key, json.dumps(result), expired=120)
                current_app.logger.debug(f"Cached topology_view result for {view_id}")
            except Exception as e:
                current_app.logger.warning(f"Failed to cache topology_view result: {str(e)}")
        
        return result
