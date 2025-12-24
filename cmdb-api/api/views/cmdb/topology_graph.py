# -*- coding:utf-8 -*-

import json
from flask import current_app, request
from api.resource import APIView
from api.lib.cmdb.search.ci import search as ci_search
from api.lib.cmdb.const import RetKey
from api.lib.cmdb.cache import AttributeCache, CITypeCache, RelationTypeCache
from api.lib.cmdb.ci import CIManager
from api.models.cmdb import CIRelation, CITypeGroup, CITypeGroupItem
from api.extensions import db
from api.lib.cmdb.search.ci_relation.search import Search
from api.lib.cmdb.ci_type import CITypeRelationManager
from api.extensions import rd

# Default configuration for topology fetching
DEFAULT_MAX_DEPTH = 10  # Maximum levels to traverse
DEFAULT_MAX_NODES = 500  # Maximum number of nodes to fetch
DEFAULT_CACHE_TTL = 1200  # Cache TTL in seconds (20 minutes)


class TopologyGraphView(APIView):
    url_prefix = ("/topology/graph",)
    
    # Cache for layer mapping to avoid repeated database queries
    _layer_mapping_cache = None

    def _build_layer_mapping(self):
        """
        Build mapping from CI type name to group name (layer)
        
        :return: Dictionary mapping ci_type.name to group.name
        """
        layer_mapping = {}
        
        # Query all CITypeGroup and CITypeGroupItem relationships
        query_result = db.session.query(CITypeGroupItem, CITypeGroup).join(
            CITypeGroup, CITypeGroup.id == CITypeGroupItem.group_id
        ).filter(
            CITypeGroup.deleted.is_(False)
        ).filter(
            CITypeGroupItem.deleted.is_(False)
        ).all()
        
        # Build mapping: ci_type.name -> group.name
        for item, group in query_result:
            ci_type = CITypeCache.get(item.type_id)
            if ci_type:
                # Map by ci_type.name (not alias) as per user requirement
                layer_mapping[ci_type.name] = group.name
        
        return layer_mapping

    def _get_layer_mapping(self):
        """
        Get layer mapping, using cache if available
        
        :return: Dictionary mapping ci_type.name to group.name
        """
        if TopologyGraphView._layer_mapping_cache is None:
            TopologyGraphView._layer_mapping_cache = self._build_layer_mapping()
        return TopologyGraphView._layer_mapping_cache

    def _get_layer_from_ci_type(self, ci_type_alias):
        """
        Map CI type alias to topology layer using dynamic mapping from CITypeGroup
        
        :param ci_type_alias: CI type alias string
        :return: Layer name (from group name, or 'Application' as fallback)
        """
        # Get CI type by alias (CITypeCache.get can handle alias, name, or id)
        ci_type = CITypeCache.get(ci_type_alias) if ci_type_alias else None
        
        if not ci_type:
            return 'Application'  # Default fallback
        
        # Get dynamic layer mapping
        layer_mapping = self._get_layer_mapping()
        
        # Map by ci_type.name (as per user requirement: ci_types[].name maps to group.name)
        layer = layer_mapping.get(ci_type.name, 'Application')
        
        return layer

    def _transform_ci_to_node(self, ci_data):
        """
        Transform CI data from database into topology graph node format
        
        :param ci_data: Dictionary containing CI attributes from database
        :return: Dictionary in node format for topology graph
        """
        # Get CI type information
        ci_type = CITypeCache.get(ci_data.get('_type'))
        
        # Determine layer based on CI type
        layer = self._get_layer_from_ci_type(ci_type.alias if ci_type else 'application')
        
        # Build metadata from relevant CI attributes
        metadata = {}
        metadata_fields = ['namespace', 'platform', 'lifecycle_status', 'cluster_dc', 
                          'cluster_dr', 'cluster_uat', 'go_live_date', 'version']
        for field in metadata_fields:
            if field in ci_data and ci_data[field]:
                metadata[field] = ci_data[field]
        
        # Determine alias - prefer show_name from CI type, then unique_name, finally fallback to namespace/app_code/name
        alias = ''
        
        # Priority 1: Use show_name from CI type if available
        if ci_type and ci_type.show_id:
            show_attr = AttributeCache.get(ci_type.show_id)
            if show_attr and show_attr.name in ci_data and ci_data[show_attr.name]:
                alias = str(ci_data[show_attr.name]).lower().replace(' ', '-')
        
        # Priority 2: Use unique_name from CI type if show_name not available
        if not alias and ci_type and ci_type.unique_id:
            unique_attr = AttributeCache.get(ci_type.unique_id)
            if unique_attr and unique_attr.name in ci_data and ci_data[unique_attr.name]:
                alias = str(ci_data[unique_attr.name]).lower().replace(' ', '-')
        
        # Priority 3: Fallback to namespace, app_code, or name
        if not alias:
            alias = ci_data.get('namespace', '') or ci_data.get('app_code', '') or ci_data.get('name', '')
            alias = alias.lower().replace(' ', '-')
        
        # Determine display name - prefer show_name from CI type, then unique_name, finally fallback to app_code/name
        name = ''
        
        # Priority 1: Use show_name from CI type if available
        if ci_type and ci_type.show_id:
            show_attr = AttributeCache.get(ci_type.show_id)
            if show_attr and show_attr.name in ci_data and ci_data[show_attr.name]:
                name = str(ci_data[show_attr.name])
        
        # Priority 2: Use unique_name from CI type if show_name not available
        if not name and ci_type and ci_type.unique_id:
            unique_attr = AttributeCache.get(ci_type.unique_id)
            if unique_attr and unique_attr.name in ci_data and ci_data[unique_attr.name]:
                name = str(ci_data[unique_attr.name])
        
        # Priority 3: Fallback to app_code or name
        if not name:
            name = ci_data.get('app_code', '') or ci_data.get('name', '')
        
        # Build the node structure
        node = {
            "name": name,
            "alias": alias,
            "layer": layer,
            "site": ci_data.get('data_center'),
            "metadata": metadata,
            "ci_type": {
                "ci_name": ci_type.name if ci_type else "Unknown",
                "ci_alias": ci_type.alias if ci_type else "unknown",
                "ci_icon": ci_type.icon if ci_type and ci_type.icon else "caise-default",
                "ci_color": "#000000"  # Default color
            }
        }
        
        return node

    def _fetch_ci_topology_with_search(self, root_ci_id, max_depth=None, max_nodes=None):
        """
        Fetch CI and downstream relationships using Search class (like relationMixin)
        Optimized version with pre-built lookup maps to reduce cache hits
        
        :param root_ci_id: Root CI ID (application)
        :param max_depth: Maximum depth to traverse (None = use default)
        :param max_nodes: Maximum nodes to fetch (None = use default)
        :return: Tuple of (all_nodes, all_edges)
        """
        if max_depth is None:
            max_depth = DEFAULT_MAX_DEPTH
        if max_nodes is None:
            max_nodes = DEFAULT_MAX_NODES
        
        all_nodes = []
        all_edges = []
        visited_ci_ids = set()
        node_map = {}  # Map ci_id to node
        
        # Pre-build lookup maps to reduce cache hits
        ci_type_map = {}      # type_id -> CIType object
        attr_map = {}         # attr_id -> Attribute object
        type_display_attrs = {}  # type_id -> (show_attr_name, unique_attr_name)
        
        def _get_or_cache_ci_type(type_id):
            """Get CI type from local map or cache once"""
            if type_id not in ci_type_map:
                ci_type_map[type_id] = CITypeCache.get(type_id)
            return ci_type_map[type_id]
        
        def _get_type_display_attrs(type_id):
            """Get show/unique attribute names for a type (cached)"""
            if type_id not in type_display_attrs:
                ci_type = _get_or_cache_ci_type(type_id)
                show_name = None
                unique_name = None
                
                if ci_type and ci_type.show_id:
                    if ci_type.show_id not in attr_map:
                        attr_map[ci_type.show_id] = AttributeCache.get(ci_type.show_id)
                    show_attr = attr_map[ci_type.show_id]
                    show_name = show_attr.name if show_attr else None
                
                if ci_type and ci_type.unique_id:
                    if ci_type.unique_id not in attr_map:
                        attr_map[ci_type.unique_id] = AttributeCache.get(ci_type.unique_id)
                    unique_attr = attr_map[ci_type.unique_id]
                    unique_name = unique_attr.name if unique_attr else None
                
                type_display_attrs[type_id] = (show_name, unique_name)
            
            return type_display_attrs[type_id]
        
        def _transform_ci_optimized(ci_data):
            """Optimized transform using pre-built maps"""
            type_id = ci_data.get('_type')
            ci_type = _get_or_cache_ci_type(type_id)
            
            # Determine layer
            layer = self._get_layer_from_ci_type(ci_type.alias if ci_type else 'application')
            
            # Build metadata
            metadata = {}
            metadata_fields = ['namespace', 'platform', 'lifecycle_status', 'cluster_dc',
                              'cluster_dr', 'cluster_uat', 'go_live_date', 'version']
            for field in metadata_fields:
                if field in ci_data and ci_data[field]:
                    metadata[field] = ci_data[field]
            
            # Get display attribute names from cache
            show_name, unique_name = _get_type_display_attrs(type_id)
            
            # Determine alias and name
            alias = ''
            name = ''
            
            # Try show_name first
            if show_name and show_name in ci_data and ci_data[show_name]:
                alias = str(ci_data[show_name]).lower().replace(' ', '-')
                name = str(ci_data[show_name])
            # Then unique_name
            elif unique_name and unique_name in ci_data and ci_data[unique_name]:
                alias = str(ci_data[unique_name]).lower().replace(' ', '-')
                name = str(ci_data[unique_name])
            # Fallback
            else:
                fallback = ci_data.get('namespace', '') or ci_data.get('app_code', '') or ci_data.get('name', '')
                alias = fallback.lower().replace(' ', '-')
                name = ci_data.get('app_code', '') or ci_data.get('name', '')
            
            return {
                "name": name,
                "alias": alias,
                "layer": layer,
                "site": ci_data.get('data_center'),
                "metadata": metadata,
                "ci_type": {
                    "ci_name": ci_type.name if ci_type else "Unknown",
                    "ci_alias": ci_type.alias if ci_type else "unknown",
                    "ci_icon": ci_type.icon if ci_type and ci_type.icon else "caise-default",
                    "ci_color": "#000000"
                }
            }
        
        # Get root CI
        root_cis = CIManager.get_cis_by_ids([str(root_ci_id)], ret_key=RetKey.NAME)
        if not root_cis:
            current_app.logger.warning(f"Root CI {root_ci_id} not found")
            return [], []
        
        root_node = _transform_ci_optimized(root_cis[0])
        all_nodes.append(root_node)
        node_map[root_ci_id] = root_node
        visited_ci_ids.add(root_ci_id)
        
        current_app.logger.info(f"Starting topology search from CI {root_ci_id} ({root_node['name']})")
        
        # Fetch each level using Search class
        current_level_ids = [root_ci_id]
        
        for level in range(1, max_depth + 1):
            if not current_level_ids:
                break
            
            if len(all_nodes) >= max_nodes:
                current_app.logger.warning(f"Reached max nodes limit {max_nodes} at level {level}")
                break
            
            next_level_ids = []
            
            # For each CI in current level, fetch its children
            for parent_ci_id in current_level_ids:
                try:
                    # Use Search class to get children (reverse=False)
                    s = Search(
                        root_id=parent_ci_id,
                        level=[1],  # Only direct children
                        reverse=False,  # Get children (downstream)
                        count=max_nodes
                    )
                    
                    response, counter, total, page, numfound, facet = s.search()
                    
                    current_app.logger.info(
                        f"Level {level}: CI {parent_ci_id} has {numfound} children"
                    )
                
                    # Process each child CI
                    for child_ci in response:
                        child_ci_id = child_ci.get('_id')
                        
                        if child_ci_id in visited_ci_ids:
                            continue  # Skip already visited (avoid circular)
                        
                        if len(all_nodes) >= max_nodes:
                            break
                    
                        # Use optimized transform
                        child_node = _transform_ci_optimized(child_ci)
                        all_nodes.append(child_node)
                        node_map[child_ci_id] = child_node
                        visited_ci_ids.add(child_ci_id)
                        next_level_ids.append(child_ci_id)
                    
                        # Create edge from parent to child
                        # Get relation type from child_ci metadata if available
                        relation_type_name = child_ci.get('relation_type', 'Related to')
                        
                        edge = {
                            "from": node_map[parent_ci_id]["alias"],
                            "to": child_node["alias"],
                            "text": relation_type_name,
                            "disableDefaultClickEffect": False
                        }
                        all_edges.append(edge)
                        
                        current_app.logger.debug(
                            f"  Added: {node_map[parent_ci_id]['alias']} -> {child_node['alias']}"
                        )
            
                except Exception as e:
                    current_app.logger.error(f"Error searching children for CI {parent_ci_id}: {str(e)}")
                    continue
        
            current_level_ids = next_level_ids
            current_app.logger.info(f"Level {level} complete: {len(current_level_ids)} CIs to process in next level")
        
        current_app.logger.info(
            f"Search completed: {len(all_nodes)} nodes, {len(all_edges)} edges "
            f"(cached {len(ci_type_map)} CI types, {len(attr_map)} attributes)"
        )
        return all_nodes, all_edges

    def get(self):
        """
        Get topology graph data for infrastructure visualization
        
        Query params:
        - max_depth: Maximum depth to traverse (default: 10)
        - max_nodes: Maximum nodes to fetch (default: 500)
        - app_code: Application code to fetch (default: VNPCHIHO)
        
        Returns nodes, edges, layers, and sites
        """
        try:
            # Get parameters from query string
            max_depth = request.args.get('max_depth', type=int)
            max_nodes = request.args.get('max_nodes', type=int)
            app_code = request.args.get('app_code', 'VNPCHIHO')
            
            # Generate cache key
            cache_key = (
                f"topology_graph:v1:{app_code}:"
                f"{max_depth or DEFAULT_MAX_DEPTH}:"
                f"{max_nodes or DEFAULT_MAX_NODES}"
            )
            
            # Try to get from cache first
            try:
                cached_result = rd.get_str(cache_key)
                if cached_result:
                    current_app.logger.info(f"Topology cache HIT for {app_code}")
                    return self.jsonify(json.loads(cached_result))
            except Exception as cache_error:
                current_app.logger.warning(f"Cache read error: {cache_error}")
            
            current_app.logger.info(f"Topology cache MISS for {app_code}, fetching from database")
            
            # Try to fetch application and recursive relationships
            all_nodes = []
            all_edges = []
            app_found = False
            app_ci_data = None
            
            try:
                # Search for application
                s = ci_search(query=f"app_code:{app_code}", count=1, ret_key=RetKey.NAME)
                response, _, _, _, numfound, _ = s.search()
                
                if response and len(response) > 0:
                    app_found = True
                    app_ci_data = response[0]  # Store the app CI data
                    app_ci_id = app_ci_data['_id']
                    all_nodes, all_edges = self._fetch_ci_topology_with_search(
                        app_ci_id, 
                        max_depth=max_depth, 
                        max_nodes=max_nodes
                    )
                    current_app.logger.info(
                        f"Fetched {len(all_nodes)} nodes and {len(all_edges)} edges "
                        f"for {app_code} (depth: {max_depth or DEFAULT_MAX_DEPTH})"
                    )
                else:
                    current_app.logger.info(f"Application '{app_code}' not found in database")
            except Exception as search_error:
                current_app.logger.error(f"Error fetching topology: {str(search_error)}")
            
            # If app was found but nodes are empty, at least show the app node
            if not all_nodes and app_found and app_ci_data:
                current_app.logger.warning(
                    f"Application '{app_code}' found but no topology data. Showing app node only."
                )
                app_node = self._transform_ci_to_node(app_ci_data)
                all_nodes = [app_node]
                all_edges = []
            
            # Only return "not found" if app truly doesn't exist
            if not all_nodes:
                return self.jsonify({
                    "node": [],
                    "edges": [],
                    "layer": [
                        "Application",
                        "Middleware",
                        "System",
                        "Infrastructure",
                        "Network"
                    ],
                    "site": [
                        "VNPAY",
                        "GDS",
                        "CMC"
                    ],
                    "metadata": {
                        "total_nodes": 0,
                        "total_edges": 0,
                        "max_depth_used": max_depth or DEFAULT_MAX_DEPTH,
                        "max_nodes_limit": max_nodes or DEFAULT_MAX_NODES,
                        "app_code": app_code,
                        "message": f"Application '{app_code}' not found in database"
                    }
                })
            
            # Build result
            result = {
                "node": all_nodes,
                "edges": all_edges,
                "layer": [
                    "Application",
                    "Middleware",
                    "System",
                    "Infrastructure",
                    "Network"
                ],
                "site": [
                    "VNPAY",
                    "GDS",
                    "CMC"
                ],
                "metadata": {
                    "total_nodes": len(all_nodes),
                    "total_edges": len(all_edges),
                    "max_depth_used": max_depth or DEFAULT_MAX_DEPTH,
                    "max_nodes_limit": max_nodes or DEFAULT_MAX_NODES,
                    "app_code": app_code,
                    "message": "Success"
                }
            }
            
            # Cache the result
            try:
                rd.set_str(cache_key, json.dumps(result), expired=DEFAULT_CACHE_TTL)
                current_app.logger.info(
                    f"Cached topology for {app_code} (TTL: {DEFAULT_CACHE_TTL}s)"
                )
            except Exception as cache_error:
                current_app.logger.warning(f"Cache write error: {cache_error}")
            
            # Return actual data from database
            return self.jsonify(result)
        
        except Exception as e:
            current_app.logger.error(f"Error fetching topology graph: {str(e)}")
            return self.jsonify({"error": str(e)}), 500

    @staticmethod
    def invalidate_cache(app_code):
        """
        Invalidate topology graph cache for a specific app_code
        Call this when CI data is updated/deleted
        
        :param app_code: Application code to invalidate cache for
        """
        try:
            pattern = f"topology_graph:v1:{app_code}:*"
            keys = rd.r.keys(pattern)
            if keys:
                rd.r.delete(*keys)
                current_app.logger.info(
                    f"Invalidated {len(keys)} topology cache entries for {app_code}"
                )
                return len(keys)
            return 0
        except Exception as e:
            current_app.logger.error(f"Cache invalidation error: {e}")
            return 0

