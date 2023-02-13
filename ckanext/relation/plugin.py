import os
import logging

import ckan.plugins as p
from ckan.common import config, request

import ckanext.relation.helpers as h

if p.toolkit.check_ckan_version(min_version='2.9.0'):
    from ckanext.relation.flask_plugin import MixinPlugin
else:
    from ckanext.relation.pylons_plugin import MixinPlugin


log = logging.getLogger(__name__)

HERE = os.path.abspath(os.path.dirname(__file__))
I18N_DIR = os.path.join(HERE, "i18n")


class RelationPlugin(MixinPlugin, p.SingletonPlugin):
    """
    Plugin for creating, deleting and viewing relationships
    """
    p.implements(p.IConfigurer)
    p.implements(p.ITranslation)                                
    p.implements(p.IConfigurable)
    p.implements(p.ITemplateHelpers)

    package_link = "/dataset/"

    def configure(self, config):
        # Get values from ckan config
        site_url = config.get("ckan.site_url", None)

        if site_url is not None:
            RelationPlugin.package_link = site_url + "/dataset/"

    def update_config(self, _config):

        # add our templates
        p.toolkit.add_template_directory(_config, "templates")
        p.toolkit.add_public_directory(_config, "public")
        p.toolkit.add_resource("resources", "relation")

    def get_helpers(self):
        """Register the functions above as template helper functions.
        """
        # Template helper function names should begin with the name of the
        # extension they belong to, to avoid clashing with functions from
        # other extensions.
        return {
            "rel_get_child_package": h.get_child_package,
            "rel_get_parent_package": h.get_parent_package,
            "rel_get_dependency_package": h.get_dependency_package,
            "rel_get_depend_package": h.get_depend_package,
            "rel_get_links_package": h.get_links_package,
            "rel_get_linked_package": h.get_linked_package,
            "package_all": h.package_all,
            "rel_id_list": h.rel_id_list,
            "has_relationship": h.has_relationship,
            "outgoing_relationship": h.outgoing_relationship,
        }

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
