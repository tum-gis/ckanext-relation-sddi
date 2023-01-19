import os
import sys
import ckan as ckan
import ckan.plugins as p
from ckan.common import c, request
import ckan.model as model
import logging
from ckan.lib.plugins import DefaultTranslation

log = logging.getLogger(__name__)

HERE = os.path.abspath(os.path.dirname(__file__))
I18N_DIR = os.path.join(HERE, "i18n")

def outgoing_relationship(id):
    """Return true if the dataset has any relationship, false otherwise."""
    type = ["depends_on", "child_of" ,"links_to"]
    for i in type:
        try:
            relationship = p.toolkit.get_action("package_relationships_list")(data_dict={"id": id, "rel": i})                
            rel = bool(relationship)
            break
        except:
            rel = 0
    return rel

def has_relationship(id):
    """Return true if the dataset has any relationship, false otherwise."""

    relationship = p.toolkit.get_action("package_relationships_list")(
        data_dict={"id": id}
    )
    if relationship:
        rel = bool(relationship)
    else:
        rel = 0
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
    except Exception as e:
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
    except Exception as e:
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
    except Exception as e:
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
    except Exception as e:
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
    except Exception as e:
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
    except Exception as e:
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
    p.implements(p.ITranslation)                                
    p.implements(p.IConfigurable)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IBlueprint, inherit=True)

    package_link = "/dataset/"

    def configure(self, config):
        # Get values from ckan config
        site_url = config.get("ckan.site_url", None)

        if site_url is not None:
            RelationPlugin.package_link = site_url + "/dataset/"

    def update_config(self, config):

        # add our templates
        p.toolkit.add_template_directory(config, "templates")
        p.toolkit.add_public_directory(config, "public")
        p.toolkit.add_resource("fanstatic", "relation")

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
            "outgoing_relationship": outgoing_relationship,
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

    # def i18n_directory(self):
        # '''Change the directory of the *.mo translation files
        # The default implementation assumes the plugin is
        # ckanext/myplugin/plugin.py and the translations are stored in
        # i18n/
        # '''
        # # assume plugin is called ckanext.<myplugin>.<...>.PluginClass
        # extension_module_name = '.'.join(self.__module__.split('.')[0:2])
        # module = sys.modules[extension_module_name]
        # return os.path.join(os.path.dirname(module.__file__), 'i18n')

    def i18n_directory(self):
        return I18N_DIR

    def i18n_locales(self):
        '''Change the list of locales that this plugin handles
        By default the will assume any directory in subdirectory in the
        directory defined by self.directory() is a locale handled by this
        plugin
        '''
        directory = self.i18n_directory()
        return [d for
                d in os.listdir(directory)
                if os.path.isdir(os.path.join(directory, d))]

    def i18n_domain(self):
        '''Change the gettext domain handled by this plugin
        This implementation assumes the gettext domain is
        ckanext-{extension name}, hence your pot, po and mo files should be
        named ckanext-{extension name}.mo'''
        return 'ckanext-{name}'.format(name=self.name)
