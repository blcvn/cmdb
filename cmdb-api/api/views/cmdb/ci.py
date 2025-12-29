# -*- coding:utf-8 -*- 

import time

import six
from flask import abort
from flask import current_app
from flask import request

from api.lib.cmdb.cache import AttributeCache, CITypeCache
from api.lib.cmdb.ci import CIManager
from api.lib.cmdb.ci import CIRelationManager
from api.lib.cmdb.const import ExistPolicy
from api.lib.cmdb.const import ResourceTypeEnum, PermEnum
from api.lib.cmdb.const import RetKey
from api.lib.cmdb.perms import has_perm_for_ci
from api.lib.cmdb.search import SearchError
from api.lib.cmdb.search.ci import search as ci_search
from api.lib.cmdb.utils import TableMap, ValueTypeMap
from api.lib.decorator import args_required
from api.lib.perm.acl.acl import has_perm_from_args
from api.lib.utils import get_page
from api.lib.utils import get_page_size
from api.lib.utils import handle_arg_list
from api.models.cmdb import CI
from api.resource import APIView
from api.extensions import db
from sqlalchemy import text


class CIsByTypeView(APIView):
    url_prefix = "/ci/type/<int:type_id>"

    def get(self, type_id):
        fields = handle_arg_list(request.values.get("fields", ""))

        ret_key = request.values.get("ret_key", RetKey.NAME)
        if ret_key not in (RetKey.NAME, RetKey.ALIAS, RetKey.ID):
            ret_key = RetKey.NAME

        page = get_page(request.values.get("page", 1))
        count = get_page_size(request.values.get("count"))

        manager = CIManager()
        res = manager.get_cis_by_type(type_id,
                                      ret_key=ret_key,
                                      fields=fields,
                                      page=page,
                                      per_page=count)

        return self.jsonify(type_id=type_id,
                            numfound=res[0],
                            total=len(res[2]),
                            page=res[1],
                            cis=res[2])


class CIView(APIView):
    url_prefix = ("/ci/<int:ci_id>", "/ci")

    def get(self, ci_id):
        fields = handle_arg_list(request.values.get("fields", ""))

        ret_key = request.values.get("ret_key", RetKey.NAME)
        if ret_key not in (RetKey.NAME, RetKey.ALIAS, RetKey.ID):
            ret_key = RetKey.NAME

        manager = CIManager()
        ci = manager.get_ci_by_id_from_db(ci_id, ret_key=ret_key, fields=fields, valid=True)

        return self.jsonify(ci_id=ci_id, ci=ci)

    @staticmethod
    def _wrap_ci_dict():
        ci_dict = {k: v.strip() if isinstance(v, six.string_types) else v for k, v in request.values.items()
                   if k != "ci_type" and not k.startswith("_")}

        return ci_dict

    @has_perm_for_ci("ci_type", ResourceTypeEnum.CI, PermEnum.ADD, lambda x: CITypeCache.get(x))
    def post(self):
        ci_type = request.values.get("ci_type")
        ticket_id = request.values.pop("ticket_id", None)
        _no_attribute_policy = request.values.get("no_attribute_policy", ExistPolicy.IGNORE)

        exist_policy = request.values.pop('exist_policy', None)

        ci_dict = self._wrap_ci_dict()

        manager = CIManager()
        ci_id = manager.add(ci_type,
                            exist_policy=exist_policy or ExistPolicy.REJECT,
                            _no_attribute_policy=_no_attribute_policy,
                            _is_admin=request.values.pop('__is_admin', None) or False,
                            ticket_id=ticket_id,
                            **ci_dict)

        return self.jsonify(ci_id=ci_id)

    @has_perm_for_ci("ci_id", ResourceTypeEnum.CI, PermEnum.UPDATE, CIManager.get_type)
    def put(self, ci_id=None):
        args = request.values
        ci_type = args.get("ci_type")
        ticket_id = request.values.pop("ticket_id", None)
        _no_attribute_policy = args.get("no_attribute_policy", ExistPolicy.IGNORE)

        ci_dict = self._wrap_ci_dict()
        manager = CIManager()
        if ci_id is not None:
            manager.update(ci_id,
                           _is_admin=request.values.pop('__is_admin', None) or False,
                           ticket_id=ticket_id,
                           **ci_dict)
        else:
            request.values.pop('exist_policy', None)
            ci_id = manager.add(ci_type,
                                exist_policy=ExistPolicy.REPLACE,
                                _no_attribute_policy=_no_attribute_policy,
                                _is_admin=request.values.pop('__is_admin', None) or False,
                                ticket_id=ticket_id,
                                **ci_dict)

        return self.jsonify(ci_id=ci_id)

    @has_perm_for_ci("ci_id", ResourceTypeEnum.CI, PermEnum.DELETE, CIManager.get_type)
    def delete(self, ci_id):
        manager = CIManager()
        manager.delete(ci_id)

        return self.jsonify(message="ok")


class CIDetailView(APIView):
    url_prefix = "/ci/<int:ci_id>/detail"

    def get(self, ci_id):
        _ci = CI.get_by_id(ci_id).to_dict()

        return self.jsonify(**_ci)


class CISearchView(APIView):
    url_prefix = ("/ci/s", "/ci/search")

    def get(self):
        """@params: q: query statement
                    fl: filter by column
                    count/page_size: the number of ci
                    ret_key: id, name, alias
                    facet: statistic
        """
        page = get_page(request.values.get("page", 1))
        count = get_page_size(request.values.get("count") or request.values.get("page_size"))

        query = request.values.get('q', "")
        fl = handle_arg_list(request.values.get('fl', ""))
        excludes = handle_arg_list(request.values.get('excludes', ""))
        ret_key = request.values.get('ret_key', RetKey.NAME)
        if ret_key not in (RetKey.NAME, RetKey.ALIAS, RetKey.ID):
            ret_key = RetKey.NAME
        facet = handle_arg_list(request.values.get("facet", ""))
        sort = request.values.get("sort")
        use_id_filter = request.values.get("use_id_filter", False) in current_app.config.get('BOOL_TRUE')

        start = time.time()
        s = ci_search(query, fl, facet, page, ret_key, count, sort, excludes, use_id_filter=use_id_filter)
        try:
            response, counter, total, page, numfound, facet = s.search()
        except SearchError as e:
            return abort(400, str(e))

        if request.values.get('need_children') in current_app.config.get('BOOL_TRUE') and len(response) == 1:
            children = CIRelationManager.get_children(response[0]['_id'], ret_key=ret_key)  # one floor
            response[0].update(children)

        current_app.logger.debug("search time is: {0}".format(time.time() - start))

        return self.jsonify(numfound=numfound,
                            total=total,
                            page=page,
                            facet=facet,
                            counter=counter,
                            result=response)

    def post(self):
        return self.get()


class CIUnique(APIView):
    url_prefix = "/ci/<int:ci_id>/unique"

    @has_perm_from_args("ci_id", ResourceTypeEnum.CI, PermEnum.UPDATE, CIManager.get_type_name)
    def put(self, ci_id):
        params = request.values
        unique_name = list(params.keys())[0]
        unique_value = list(params.values())[0]

        CIManager.update_unique_value(ci_id, unique_name, unique_value)

        return self.jsonify(ci_id=ci_id)


class CIHeartbeatView(APIView):
    url_prefix = ("/ci/heartbeat", "/ci/heartbeat/<string:ci_type>/<string:unique>")

    def get(self):
        page = get_page(request.values.get("page", 1))
        ci_type = request.values.get("ci_type", "").strip()
        try:
            type_id = CITypeCache.get(ci_type).type_id
        except AttributeError:
            return self.jsonify(numfound=0, result=[])
        agent_status = request.values.get("agent_status")
        if agent_status:
            agent_status = int(agent_status)

        numfound, result = CIManager.get_heartbeat(page, type_id, agent_status=agent_status)

        return self.jsonify(numfound=numfound, result=result)

    def post(self, ci_type, unique):
        if not unique or not ci_type:
            return self.jsonify(message="error")

        msg, cmd = CIManager().add_heartbeat(ci_type, unique)

        return self.jsonify(message=msg, cmd=cmd)


class CIFlushView(APIView):
    url_prefix = ("/ci/flush", "/ci/<int:ci_id>/flush")

    def get(self, ci_id=None):
        from api.tasks.cmdb import ci_cache
        from api.lib.cmdb.const import CMDB_QUEUE
        if ci_id is not None:
            ci_cache.apply_async(args=(ci_id, None, None), queue=CMDB_QUEUE)
        else:
            cis = CI.get_by(to_dict=False)
            for ci in cis:
                ci_cache.apply_async(args=(ci.id, None, None), queue=CMDB_QUEUE)

        return self.jsonify(code=200)


class CIAutoDiscoveryStatisticsView(APIView):
    url_prefix = "/ci/adc/statistics"

    def get(self):
        return self.jsonify(CIManager.get_ad_statistics())


class CIPasswordView(APIView):
    url_prefix = "/ci/<int:ci_id>/attributes/<int:attr_id>/password"

    def get(self, ci_id, attr_id):
        return self.jsonify(ci_id=ci_id, attr_id=attr_id, value=CIManager.load_password(ci_id, attr_id))

    def post(self, ci_id, attr_id):
        return self.get(ci_id, attr_id)


class CIBaselineView(APIView):
    url_prefix = ("/ci/baseline", "/ci/<int:ci_id>/baseline/rollback")

    @args_required("before_date")
    def get(self):
        ci_ids = handle_arg_list(request.values.get('ci_ids'))
        before_date = request.values.get('before_date')

        return self.jsonify(CIManager().baseline(list(map(int, ci_ids)), before_date))

    @args_required("before_date")
    @has_perm_for_ci("ci_id", ResourceTypeEnum.CI, PermEnum.UPDATE, CIManager.get_type)
    def post(self, ci_id):
        if 'rollback' in request.url:
            before_date = request.values.get('before_date')

            return self.jsonify(**CIManager().rollback(ci_id, before_date))

        return self.get(ci_id)


class CIDistinctValuesView(APIView):
    url_prefix = "/ci/distinct_values"

    @args_required("type_id", "attr_name")
    def get(self):
        """Get distinct values for an attribute of a CI Type
        @params:
            type_id: CI Type ID
            attr_name: Attribute name
        """
        type_id = request.values.get('type_id')
        attr_name = request.values.get('attr_name')

        try:
            type_id = int(type_id)
        except (ValueError, TypeError):
            return abort(400, "Invalid type_id")

        # Get attribute
        attr = AttributeCache.get(attr_name)
        if not attr:
            return abort(404, f"Attribute '{attr_name}' not found")

        # Get CI Type
        ci_type = CITypeCache.get(type_id)
        if not ci_type:
            return abort(404, f"CI Type ID {type_id} not found")

        # Build query to get distinct values
        table_map = TableMap(attr=attr)
        table_name = table_map.table_name
        
        # Validate table name for security
        allowed_tables = {
            'c_value_0', 'c_value_1', 'c_value_2', 'c_value_3', 
            'c_value_4', 'c_value_5', 'c_value_6', 'c_value_texts',
            'c_value_index_texts', 'c_value_index_integers', 
            'c_value_index_floats', 'c_value_index_datetime', 'c_value_json'
        }
        if table_name not in allowed_tables:
            return abort(400, "Invalid table name: {}".format(table_name))

        # Query distinct values for this attribute and CI Type
        # Use format() instead of f-string for table_name (validated above)
        distinct_query = """
            SELECT DISTINCT {}.value
            FROM {}
            INNER JOIN c_cis ON {}.ci_id = c_cis.id
            WHERE {}.attr_id = :attr_id
              AND c_cis.type_id = :type_id
              AND c_cis.deleted = 0
              AND {}.value IS NOT NULL
              AND {}.value != ''
            ORDER BY {}.value
        """.format(table_name, table_name, table_name, table_name, table_name, table_name, table_name)

        try:
            result = db.session.execute(
                text(distinct_query),
                {'attr_id': attr.id, 'type_id': type_id}
            ).fetchall()
            
            # Serialize values based on value type
            distinct_values = []
            seen_values = set()
            for row in result:
                value = row[0]
                if value is not None:
                    serialized_value = ValueTypeMap.serialize[attr.value_type](value)
                    # Convert to string for comparison to avoid duplicates
                    value_str = str(serialized_value)
                    if value_str not in seen_values:
                        seen_values.add(value_str)
                        distinct_values.append(serialized_value)
            
            return self.jsonify(
                type_id=type_id,
                attr_name=attr_name,
                values=sorted(distinct_values, key=lambda x: str(x))
            )
        except Exception as e:
            current_app.logger.error("Error getting distinct values: {}".format(str(e)))
            return abort(500, "Error getting distinct values: {}".format(str(e)))
