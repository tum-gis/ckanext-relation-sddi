import ckan as ckan
import ckan.plugins as p
from ckan.common import c, request
import ckan.model as model
import logging

log = logging.getLogger(__name__)


def has_relationship(id):
    """Return true if the dataset has any relationship, false otherwise."""

    relationship = p.toolkit.get_action("package_relationships_list")(
        data_dict={"id": id}
    )
    if relationship:
        rel = bool(relationship)
    return rel


def rel_id_list(rel_list):
    """Return a list of already added datasets with relationships"""

    rel_ids = []
    for i in range(0, len(rel_list)):
        rel_id = rel_list[i]["id"]
        rel_ids.append(rel_id)
    return rel_ids


def package_all(q):
    """Return a list of all datasets searched for with value 'q'."""

    query = (q.dict_of_lists())["q"][0]
    datasets = p.toolkit.get_action("package_search")(
        {}, data_dict={"q": query, "include_private": True}
    )

    result = datasets["results"]
    results = []
    for res in result:
        results.append(res)
    return results


def get_child_package(id):
    """ Returns a list of packages that are the subjects of child_of relationships."""

    relationships = []
    try:
        relationships = p.toolkit.get_action("package_relationships_list")(
            data_dict={"id": id, "rel": "parent_of"}
        )
    except Exception, e:
        return {}

    children = []
    if relationships:
        for rel in relationships:
            try:
                access = p.toolkit.check_access(
                    "package_show",
                    context={"user": c.user},
                    data_dict={"id": rel["object"]},
                )
                child = p.toolkit.get_action("package_show")(
                    data_dict={"id": rel["object"]}
                )
                children.append(child)
            except:
                pass
    return children


def get_parent_package(id):
    """ Returns a list of packages that are the subjects of parent_of relationships."""

    relationships = []
    try:
        relationships = p.toolkit.get_action("package_relationships_list")(
            data_dict={"id": id, "rel": "child_of"}
        )
    except Exception, e:
        return {}

    parents = []
    if relationships:
        for rel in relationships:
            parent = p.toolkit.get_action("package_show")(data_dict={"id": rel["object"]})
            parents.append(parent)
    return parents


def get_dependency_package(id):
    """ Returns a list of packages that are the subjects of dependency_of relationships."""

    relationships = []
    try:
        relationships = p.toolkit.get_action("package_relationships_list")(
            data_dict={"id": id, "rel": "depends_on"}
        )
    except Exception, e:
        return {}

    dependencies = []
    if relationships:
        for rel in relationships:
            dependency = p.toolkit.get_action("package_show")(
                data_dict={"id": rel["object"]}
            )
            dependencies.append(dependency)
    return dependencies


def get_depend_package(id):
    """ Returns a list of packages that are the subjects of depends_on relationships."""

    relationships = []
    try:
        relationships = p.toolkit.get_action("package_relationships_list")(
            data_dict={"id": id, "rel": "dependency_of"}
        )
    except Exception, e:
        return {}

    depend = []
    if relationships:
        for rel in relationships:
            try:
                access = p.toolkit.check_access(
                    "package_show",
                    context={"user": c.user},
                    data_dict={"id": rel["object"]},
                )
                dep = p.toolkit.get_action("package_show")(
                    data_dict={"id": rel["object"]}
                )
                depend.append(dep)
            except:
                pass
    return depend


def get_linked_package(id):
    """ Returns a list of packages that are the subjects of linked_from relationships."""

    relationships = []
    try:
        relationships = p.toolkit.get_action("package_relationships_list")(
            data_dict={"id": id, "rel": "links_to"}
        )
    except Exception, e:
        return {}

    linked = []
    if relationships:
        for rel in relationships:
            lnk = p.toolkit.get_action("package_show")(
                data_dict={"id": rel["object"]}
            )
            linked.append(lnk)

    return linked


def get_links_package(id):
    """ Returns a list of packages that are the subjects of links_to relationships."""

    relationships = []
    try:
        relationships = p.toolkit.get_action("package_relationships_list")(
            data_dict={"id": id, "rel": "linked_from"}
        )
    except Exception, e:
        return {}

    links = []
    if relationships:
        for rel in relationships:
            try:
                access = p.toolkit.check_access(
                    "package_show",
                    context={"user": c.user},
                    data_dict={"id": rel["object"]},
                )
                link = p.toolkit.get_action("package_show")(
                    data_dict={"id": rel["object"]}
                )
                links.append(link)
            except:
                pass
    return links


class RelationPlugin(p.SingletonPlugin):
    """
    Plugin for creating, deleting and viewing relationships
    """

    p.implements(p.IConfigurer)
    p.implements(p.IConfigurable)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IRoutes, inherit=True)

    package_link = "/dataset/"

    def configure(self, config):
        # Get values from ckan config
        site_url = config.get("ckan.site_url", None)

        if site_url is not None:
            RelationPlugin.package_link = site_url + "/dataset/"

    def update_config(self, config):

        # add our templates
        p.toolkit.add_template_directory(config, "templates")
        #p.toolkit.add_public_directory(config, "public")
        #p.toolkit.add_resource("fanstatic", "ckanext-relation")

    def get_helpers(self):
        """Register the functions above as template helper functions.
        """
        # Template helper function names should begin with the name of the
        # extension they belong to, to avoid clashing with functions from
        # other extensions.
        print("something1")
        return {
            "rel_get_child_package": get_child_package,
            "rel_get_parent_package": get_parent_package,
            "rel_get_dependency_package": get_dependency_package,
            "rel_get_depend_package": get_depend_package,
            "rel_get_links_package": get_links_package,
            "rel_get_linked_package": get_linked_package,
            "package_all": package_all,
            "rel_id_list": rel_id_list,
            "has_relationship": has_relationship,
        }

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
