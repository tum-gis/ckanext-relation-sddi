import ckan.plugins as p


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IRoutes, inherit=True)

    # IRoutes

    def before_map(self, map):

        map.connect(
            "temp",
            "/demp/demo",
            controller="ckanext.relation.controller:RelationController",
            action="index",
        )

        map.connect(
            "data_relation_add",  # name of path route
            "/dataset/relationship/add/{id}",  # url to map path to
            controller="ckanext.relation.controller:RelationController",  # controller
            action="finalrel",  # controller action (method)
        )

        map.connect(
            "/dataset/new_resource/{id}",
            controller="ckanext.relation.controller:RelationController",
            action="new_resource_ext",
        )

        # map.connect('delete_ext', '/dataset/edit/{id}',controller='ckanext.relation.controller:RelationController', action='delete_ext')
        # print('here8')

        map.connect(
            "dataset_edit_relation",
            "/dataset/relationship/edit/{id}",
            controller="ckanext.relation.controller:RelationController",
            action="edit_relation",
            ckan_icon="edit",
        )

        map.connect(
            "data dict button",
            "/dataset/relationship/new_relationship/{id}",
            controller="ckanext.relation.controller:RelationController",
            action="new_relation",
        )

        map.connect(
            "relation",
            "/dataset/relationship/{id}",
            controller="ckanext.relation.controller:RelationController",
            action="relation",
            ckan_icon="link",
        )
        return map

    def after_map(self, map):

        map.connect(
            "temp",
            "/demp/demo",
            controller="ckanext.relation.controller:RelationController",
            action="index",
        )

        map.connect(
            "data_relation_add",
            "/dataset/relationship/add/{id}",
            controller="ckanext.relation.controller:RelationController",
            action="finalrel",
        )

        map.connect(
            "/dataset/new_resource/{id}",
            controller="ckanext.relation.controller:RelationController",
            action="new_resource_ext",
        )

        # map.connect('delete_ext','/dataset/edit/{id}',controller='ckanext.relation.controller:RelationController', action='delete_ext')
        # print('here8')

        map.connect(
            "dataset_edit_relation",
            "/dataset/relationship/edit/{id}",
            controller="ckanext.relation.controller:RelationController",
            action="edit_relation",
            ckan_icon="edit",
        )

        map.connect(
            "data dict button",
            "/dataset/relationship/new_relationship/{id}",
            controller="ckanext.relation.controller:RelationController",
            action="new_relation",
        )

        map.connect(
            "relation",
            "/dataset/relationship/{id}",
            controller="ckanext.relation.controller:RelationController",
            action="relation",
            ckan_icon="link",
        )

        return map
