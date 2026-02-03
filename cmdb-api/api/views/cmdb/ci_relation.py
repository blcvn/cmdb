# -*- coding:utf-8 -*- 


import time
from flask import abort
from flask import current_app
from flask import request

from api.lib.cmdb.cache import RelationTypeCache
from api.lib.cmdb.ci import CIRelationManager
from api.lib.cmdb.resp_format import ErrFormat
from api.lib.cmdb.search import SearchError
from api.lib.cmdb.search.ci_relation.search import Search
from api.lib.decorator import args_required
from api.lib.utils import get_page
from api.lib.utils import get_page_size
from api.lib.utils import handle_arg_list
from api.resource import APIView


class CIRelationSearchView(APIView):
    url_prefix = ("/ci_relations/s", "/ci_relations/search")

    def get(self):
        """@params: q: query statement
                    fl: filter by column
                    count: the number of ci
                    root_id: ci id
                    level: default is 1
                    facet: statistic
        """

        page = get_page(request.values.get("page", 1))
        count = get_page_size(request.values.get("count") or request.values.get("page_size"))

        root_id = request.values.get('root_id')
        ancestor_ids = request.values.get('ancestor_ids') or None  # only for many to many
        root_parent_path = handle_arg_list(request.values.get('root_parent_path') or '')
        descendant_ids = list(map(int, handle_arg_list(request.values.get('descendant_ids', []))))
        level = list(map(int, handle_arg_list(request.values.get('level', '1'))))

        query = request.values.get('q', "")
        fl = handle_arg_list(request.values.get('fl', ""))
        facet = handle_arg_list(request.values.get("facet", ""))
        sort = request.values.get("sort")
        reverse = request.values.get("reverse") in current_app.config.get('BOOL_TRUE')
        has_m2m = request.values.get("has_m2m") in current_app.config.get('BOOL_TRUE')

        start = time.time()
        s = Search(root_id, level, query, fl, facet, page, count, sort, reverse,
                   ancestor_ids=ancestor_ids, has_m2m=has_m2m, root_parent_path=root_parent_path,
                   descendant_ids=descendant_ids)
        try:
            response, counter, total, page, numfound, facet = s.search()
        except SearchError as e:
            return abort(400, str(e))
        current_app.logger.debug("search time is :{0}".format(time.time() - start))

        return self.jsonify(numfound=numfound,
                            total=total,
                            page=page,
                            facet=facet,
                            counter=counter,
                            result=response)


class CIRelationSearchPathView(APIView):
    url_prefix = ("/ci_relations/path/s", "/ci_relations/path/search")

    @args_required("source", "target", "path")
    def post(self):
        """@params: page: page number
                    page_size | count: page size
                    source: source CIType, e.g. {type_id: 1, q: `search expr`}
                    target: target CIType, e.g. {type_ids: [2], q: `search expr`}
                    path: Path from the Source CIType to the Target CIType, e.g. [1, ..., 2]
        """

        page = get_page(request.values.get("page", 1))
        count = get_page_size(request.values.get("count") or request.values.get("page_size"))

        source = request.values.get("source")
        target = request.values.get("target")
        path = request.values.get("path")

        s = Search(page=page, count=count)
        try:
            (response, counter, total, page, numfound, id2ci,
             relation_types, type2show_key) = s.search_by_path(source, target, path)
        except SearchError as e:
            return abort(400, str(e))

        return self.jsonify(numfound=numfound,
                            total=total,
                            page=page,
                            counter=counter,
                            paths=response,
                            id2ci=id2ci,
                            relation_types=relation_types,
                            type2show_key=type2show_key)


class CIRelationStatisticsView(APIView):
    url_prefix = "/ci_relations/statistics"

    def get(self):
        root_ids = list(map(int, handle_arg_list(request.values.get('root_ids'))))
        level = request.values.get('level', 1)
        type_ids = set(map(int, handle_arg_list(request.values.get('type_ids', []))))
        ancestor_ids = request.values.get('ancestor_ids') or None  # only for many to many
        descendant_ids = list(map(int, handle_arg_list(request.values.get('descendant_ids', []))))
        has_m2m = request.values.get("has_m2m") in current_app.config.get('BOOL_TRUE')

        start = time.time()
        s = Search(root_ids, level, ancestor_ids=ancestor_ids, descendant_ids=descendant_ids, has_m2m=has_m2m)
        try:
            result = s.statistics(type_ids)
        except SearchError as e:
            return abort(400, str(e))
        current_app.logger.debug("search time is :{0}".format(time.time() - start))

        return self.jsonify(result)


class CIRelationSearchFullView(APIView):
    url_prefix = "/ci_relations/search/full"

    def get(self):
        root_ids = list(map(int, handle_arg_list(request.values.get('root_ids'))))
        level = request.values.get('level', 1)
        type_ids = list(map(int, handle_arg_list(request.values.get('type_ids', []))))
        has_m2m = request.values.get("has_m2m") in current_app.config.get('BOOL_TRUE')

        start = time.time()
        s = Search(root_ids, level, has_m2m=has_m2m)
        try:
            result = s.search_full(type_ids)
        except SearchError as e:
            return abort(400, str(e))
        current_app.logger.debug("search time is :{0}".format(time.time() - start))

        return self.jsonify(result)


class GetSecondCIsView(APIView):
    url_prefix = "/ci_relations/<int:first_ci_id>/second_cis"

    def get(self, first_ci_id):
        page = get_page(request.values.get("page", 1))
        count = get_page_size(request.values.get("count"))
        relation_type = request.values.get("relation_type")
        try:
            relation_type_id = RelationTypeCache.get(relation_type).id if relation_type else None
        except AttributeError:
            return abort(400, ErrFormat.invalid_relation_type.format(relation_type))

        manager = CIRelationManager()
        numfound, total, second_cis = manager.get_second_cis(
            first_ci_id, page=page, per_page=count, relation_type_id=relation_type_id)

        return self.jsonify(numfound=numfound,
                            total=total,
                            page=page,
                            second_cis=second_cis)


class GetFirstCIsView(APIView):
    url_prefix = "/ci_relations/<int:second_ci_id>/first_cis"

    def get(self, second_ci_id):
        page = get_page(request.values.get("page", 1))
        count = get_page_size(request.values.get("count"))

        manager = CIRelationManager()
        numfound, total, first_cis = manager.get_first_cis(second_ci_id, per_page=count, page=page)

        return self.jsonify(numfound=numfound,
                            total=total,
                            page=page,
                            first_cis=first_cis)


class GetCIRelationsWithImpactView(APIView):
    url_prefix = "/ci_relations/<int:ci_id>/impact"

    def get(self, ci_id):
        """
        Get parents and children CIs with impact > 0.
        Returns:
        {
            "parents": [
                {"ci_id": 123, "relation_type_id": 5, "impact": 10},
                ...
            ],
            "children": [
                {"ci_id": 456, "relation_type_id": 6, "impact": 8},
                ...
            ]
        }
        """
        manager = CIRelationManager()
        
        # Get parents with impact > 0
        parents = manager.get_parents_with_impact(ci_id)
        
        # Get children with impact > 0
        children = manager.get_children_with_impact(ci_id)
        
        return self.jsonify(
            parents=parents,
            children=children
        )


class CIRelationView(APIView):
    url_prefix = "/ci_relations/<int:first_ci_id>/<int:second_ci_id>"

    def post(self, first_ci_id, second_ci_id):
        ancestor_ids = request.values.get('ancestor_ids') or None

        manager = CIRelationManager()
        res = manager.add(first_ci_id, second_ci_id, ancestor_ids=ancestor_ids)

        return self.jsonify(cr_id=res)

    def delete(self, first_ci_id, second_ci_id):
        ancestor_ids = request.values.get('ancestor_ids') or None

        manager = CIRelationManager()
        manager.delete_2(first_ci_id, second_ci_id, ancestor_ids=ancestor_ids)

        return self.jsonify(message="CIType Relation is deleted")


class DeleteCIRelationView(APIView):
    url_prefix = "/ci_relations/<int:cr_id>"

    def delete(self, cr_id):
        manager = CIRelationManager()
        manager.delete(cr_id)

        return self.jsonify(message="CIType Relation is deleted")


class BatchCreateOrUpdateCIRelationView(APIView):
    url_prefix = "/ci_relations/batch"

    @args_required('ci_ids')
    def post(self):
        ci_ids = list(map(int, request.values.get('ci_ids')))
        parents = list(map(int, request.values.get('parents', [])))
        children = list(map(int, request.values.get('children', [])))
        ancestor_ids = request.values.get('ancestor_ids') or None

        CIRelationManager.batch_update(ci_ids, parents, children, ancestor_ids=ancestor_ids)

        return self.jsonify(code=200)

    @args_required('ci_ids')
    @args_required('parents')
    def put(self):
        return self.post()

    @args_required('ci_ids')
    @args_required('parents')
    def delete(self):
        ci_ids = list(map(int, request.values.get('ci_ids')))
        parents = list(map(int, request.values.get('parents', [])))
        ancestor_ids = request.values.get('ancestor_ids') or None

        CIRelationManager.batch_delete(ci_ids, parents, ancestor_ids=ancestor_ids)

        return self.jsonify(code=200)


class CIGraphFilterView(APIView):
    url_prefix = "/ci_relations/<int:root_ci_id>/filtered_graph"

    def post(self, root_ci_id):
        """Get filtered CI graph based on filter conditions.
        @params:
            filter_rules: List of filter rules, e.g.:
                [
                    {
                        "type_id": 123,  # CI Type ID to filter
                        "filters": {
                            "attribute_name_1": ["value1", "value2"],
                            "attribute_name_2": ["valueA"]
                        }
                    },
                    ...
                ]
        """
        filter_rules = request.json.get('filter_rules', [])
        if not isinstance(filter_rules, list):
            return abort(400, "filter_rules must be a list")

        # Basic validation for filter_rules structure
        for rule in filter_rules:
            if not isinstance(rule, dict) or 'type_id' not in rule or 'filters' not in rule:
                return abort(400, "Each filter rule must be a dict with 'type_id' and 'filters'")
            if not isinstance(rule['type_id'], int):
                return abort(400, "type_id in filter_rules must be an integer")
            if not isinstance(rule['filters'], dict):
                return abort(400, "filters in filter_rules must be a dictionary")
            for attr_name, values in rule['filters'].items():
                if not isinstance(values, list):
                    return abort(400, f"Values for attribute '{attr_name}' must be a list")

        try:
            result = CIRelationManager.get_filtered_graph(root_ci_id, filter_rules)
        except SearchError as e:
            return abort(400, str(e))

        return self.jsonify(result)


class CIGraphStatsView(APIView):
    url_prefix = "/ci_relations/stats_by_type"
    
    @staticmethod
    def _format_ci_names(nodes):
        """Format CI names using show_key attribute from CI Type."""
        from api.lib.cmdb.cache import CITypeCache, AttributeCache
        
        result = []
        for node in nodes:
            ci_type_id = node.get('_type')
            ci_type_obj = CITypeCache.get(ci_type_id) if ci_type_id else None
            
            # Get show attribute name from show_id (avoid lazy load issue)
            show_attr_name = None
            if ci_type_obj and ci_type_obj.show_id:
                show_attr = AttributeCache.get(ci_type_obj.show_id)
                show_attr_name = show_attr.name if show_attr else None
            
            # Use show_key attribute if defined, otherwise fallback
            if show_attr_name and node.get(show_attr_name):
                ci_name = str(node.get(show_attr_name))
            else:
                ci_name = node.get('_name') or node.get('name') or node.get('hostname') or str(node.get('_id'))
            
            result.append({
                'ci_id': node.get('_id'),
                'ci_name': ci_name,
                'ci_type': node.get('ci_type'),
                'ci_type_id': ci_type_id
            })
        return result

    @args_required("type_id")
    def get(self):
        """Get CI statistics grouped by CI Type for all CIs in a given CI Type.
        @params:
            type_id: CI Type ID to get all CIs from
            page: Page number (default: 1)
            per_page: Items per page (default: 20, max: 100)
        Returns list of stats for each CI in the type.
        """
        type_id = request.values.get('type_id')
        page = request.values.get('page', 1)
        per_page = request.values.get('per_page', 20)
        
        try:
            type_id = int(type_id)
            page = int(page)
            per_page = min(int(per_page), 100)  # Max 100 per page
        except (ValueError, TypeError):
            return abort(400, "Invalid parameters")
        
        # Get all CIs of this type
        from api.lib.cmdb.ci import CIManager
        from api.lib.cmdb.cache import CITypeCache
        
        ci_type = CITypeCache.get(type_id)
        if not ci_type:
            return abort(404, f"CI Type {type_id} not found")
        
        # Get CIs of this type with pagination
        from api.models.cmdb import CI
        from api.extensions import db
        
        query = db.session.query(CI).filter(
            CI.type_id == type_id,
            CI.deleted.is_(False)
        )
        total = query.count()
        cis = query.offset((page - 1) * per_page).limit(per_page).all()
        
        result_list = []
        for ci in cis:
            try:
                # Use get_filtered_graph with empty filter rules to get all reachable CIs
                result = CIRelationManager.get_filtered_graph(ci.id, [])
                
                # Group by CI Type and count
                type_stats = {}
                ci_type_names = {}
                
                for node in result.get('nodes', []):
                    ci_type_id = node.get('_type')
                    ci_type_name = node.get('ci_type', 'Unknown')
                    
                    if ci_type_id:
                        if ci_type_id not in type_stats:
                            type_stats[ci_type_id] = 0
                            ci_type_names[ci_type_id] = ci_type_name
                        type_stats[ci_type_id] += 1
                
                # Format stats for this CI
                stats = []
                for tid, count in type_stats.items():
                    stats.append({
                        'type_id': tid,
                        'type_name': ci_type_names[tid],
                        'count': count
                    })
                
                # Sort by count descending
                stats.sort(key=lambda x: x['count'], reverse=True)
                
                # Get CI details and use CI Type's show_id attribute for display
                ci_dict = CIManager.get_ci_by_id(str(ci.id))
                
                # Get show_key (display attribute) from CI Type (avoid lazy load)
                from api.lib.cmdb.cache import CITypeCache, AttributeCache
                ci_type_obj = CITypeCache.get(ci.type_id)
                show_attr_name = None
                if ci_type_obj and ci_type_obj.show_id:
                    show_attr = AttributeCache.get(ci_type_obj.show_id)
                    show_attr_name = show_attr.name if show_attr else None
                
                # Use show_key attribute if defined, otherwise fallback to _name
                if show_attr_name and ci_dict.get(show_attr_name):
                    ci_name = str(ci_dict.get(show_attr_name))
                else:
                    ci_name = ci_dict.get('_name') or ci_dict.get('name') or ci_dict.get('hostname') or str(ci.id)
                
                # Enhance stats with CI names
                enhanced_stats = []
                for stat in stats:
                    enhanced_stats.append({
                        'type_id': stat['type_id'],
                        'type_name': stat['type_name'],
                        'count': stat['count'],
                        'ci_ids': []  # Can be populated if needed
                    })
                
                result_list.append({
                    'ci_id': ci.id,
                    'ci_name': ci_name,
                    'ci_type_id': ci.type_id,
                    'ci_type_name': ci_dict.get('ci_type', 'Unknown'),
                    'total_related_cis': len(result.get('nodes', [])) - 1,  # Exclude self
                    'stats': enhanced_stats,
                    # Add all related CI details for reference
                    'related_cis': self._format_ci_names(
                        [node for node in result.get('nodes', []) if node.get('_id') != ci.id]
                    )
                })
            except Exception as e:
                current_app.logger.error(f"Error getting stats for CI {ci.id}: {str(e)}")
                continue
        
        return self.jsonify({
            'type_id': type_id,
            'type_name': ci_type.name,
            'total_cis': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page,
            'results': result_list
        })
