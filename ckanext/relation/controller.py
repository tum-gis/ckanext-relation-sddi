import logging
import ckan.plugins as plugins
from ckan.lib.base import BaseController
import ckan.lib.helpers as h
from ckan.common import OrderedDict, _, json, request, common, g, response, config
from urllib.parse import urlencode
import cgi
from paste.deploy.converters import asbool
import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model
import ckan.lib.plugins
import ckan.lib.render
import ckan.lib.navl.dictization_functions as dict_fns


log = logging.getLogger(__name__)

render = base.render
abort = base.abort
#redirect = base.redirect
redirect = h.redirect_to
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
flatten_to_string_key = logic.flatten_to_string_key
lookup_package_plugin = ckan.lib.plugins.lookup_package_plugin


class RelationController(BaseController):
    def _resource_form(self, package_type):
        # backwards compatibility with plugins not inheriting from
        # DefaultDatasetPlugin and not implmenting resource_form
        plugin = lookup_package_plugin(package_type)
        if hasattr(plugin, "resource_form"):
            result = plugin.resource_form()
            if result is not None:
                return result
        return lookup_package_plugin().resource_form()

    def finalrel(self, id, data=None, errors=None):
        if request.method == "POST":
            pass
        c.link = str("/dataset/relationship/edit/" + id)
        return render("package/new_data_relation.html", extra_vars={"package_id": id})

    def new_relation(self, id):
        c.link = str("/dataset/relationship/edit/" + id)
        if request.method == "POST":
            save_action = request.params.get("save")
            print("new data dictionary !!!!!!!!!!!!!!!!")
            context = {
                "model": model,
                "session": model.Session,
                "user": c.user or c.author,
                "auth_user_obj": c.userobj,
            }

            # Remove button in the edit page
            removed_rel = None
            type_rem = None
            for param in request.POST:
                if param.startswith("relation_remove"):
                    removed_rel = param.split(".")[-1]
                    type_rem = param.split(".")[-2]
                    break
            if removed_rel:
                data_dict = {"subject": id, "object": removed_rel, "type": type_rem}

                try:
                    get_action("package_relationship_delete")(context, data_dict)
                except NotFound:
                    abort(404, _("Relationship not found"))
                try:
                    check_access("package_relationship_create", context, data_dict)
                except NotAuthorized:
                    abort(
                        401, _("Unauthorized to create a relationship for this package")
                    )
                h.redirect_to("/dataset/relationship/edit/" + id)

            # add button in the edit page
            add_rel = None
            type_add = None
            for param in request.POST:
                if param.startswith("relation_add"):
                    add_rel = param.split(".")[-1]
                    type_add = param.split(".")[-2]
                    break

            if add_rel:
                # context={'ignore_auth': True}
                data_dict = {"subject": id, "object": add_rel, "type": type_add}

                try:
                    get_action("package_relationship_create")(context, data_dict)
                except NotFound:
                    abort(404, _("Relationship cannot be created"))

                # try:
                # 	check_access('package_relationship_create', context, {'object': add_rel, 'subject': id})#{"package_id": pkg_dict["id"]})
                # 	print('it is done')
                # except NotAuthorized:
                #    abort(401, _('Unauthorized to create a relationship for this package'))
                h.redirect_to("/dataset/relationship/edit/" + id)

            if save_action == "go-metadata":
                # XXX race condition if another user edits/deletes
                h.redirect_to(controller="package", action="read", id=id)

        redirect("/dataset/relationship/edit/" + id)

    def new_resource_ext(self, id, data=None, errors=None, error_summary=None):
        """ FIXME: This is a temporary action to allow styling of the
        forms. """
        linkResource = str("/dataset/new_resource/" + id)

        if request.method == "POST" and not data:
            save_action = request.params.get("save")
            # if save_action == 'go-datadict':
            # redirect(h.url_for(controller='package', action='addDictionary'))
            data = data or clean_dict(
                dict_fns.unflatten(tuplize_dict(parse_params(request.POST)))
            )
            # we don't want to include save as it is part of the form
            del data["save"]
            # if 'id' in data.keys()and save_action=="go-dataset-final":
            # print("Id found","and the path is: ",request.path)
            resource_id = data["id"]
            # redirect(h.url_for(controller='package',action='read',id=id))
            # request.path.split("/")[2]))
            # else:
            # print("In else part",id," and the request path is: ", request.path)
            # if save_action == 'go-dataset-final':
            # redirect(h.url_for(controller='package',action='new_resource',id=id))
            # request.path.split("/")[2]))

            del data["id"]

            context = {
                "model": model,
                "session": model.Session,
                "user": c.user or c.author,
                "auth_user_obj": c.userobj,
            }

            # see if we have any data that we are trying to save
            data_provided = False
            for key, value in data.items():
                if (
                    value or isinstance(value, cgi.FieldStorage)
                ) and key != "resource_type":
                    data_provided = True
                    break

            #            if save_action == 'go-datadict':
            #
            #                print('save action was go-datadict in the exntenstion NEEWWWW!!!!!!!!!!!')
            #                h.redirect_to("/dataset/relationship/add/" + id)

            if not data_provided and save_action != "go-dataset-complete":
                if save_action == "go-datadict":
                    data_dict = get_action("package_show")(context, {"id": id})
                    get_action("package_update")(
                        dict(context, allow_state_change=True),
                        dict(data_dict, state="active"),
                    )
                    # h.flash_notice(_('Dataset has been deleted.'))
                    print(
                        "save action was go-datadict in the exntenstion NEEWWWW!!!!!!!!!!!"
                    )
                    h.redirect_to("/dataset/relationship/edit/" + id)

                if save_action == "go-dataset":
                    # go to final stage of adddataset
                    redirect(h.url_for(controller="package", action="edit", id=id))
                # see if we have added any resources
                try:
                    data_dict = get_action("package_show")(context, {"id": id})
                except NotAuthorized:
                    abort(401, _("Unauthorized to update dataset"))
                except NotFound:
                    abort(404, _("The dataset {id} could not be found.").format(id=id))

                require_resources = asbool(
                    config.get("ckan.dataset.create_on_ui_requires_resources", "True")
                )
                if require_resources and not len(data_dict["resources"]):
                    # no data so keep on page
                    msg = _("You must add at least one data resource")
                    # On new templates do not use flash message

                    if asbool(config.get("ckan.legacy_templates")):
                        h.flash_error(msg)
                        h.redirect_to(
                            controller="package", action="new_resource", id=id
                        )
                    else:
                        errors = {}
                        error_summary = {_("Error"): msg}
                        return self.new_resource_ext(id, data, errors, error_summary)

                # XXX race condition if another user edits/deletes
                data_dict = get_action("package_show")(context, {"id": id})
                get_action("package_update")(
                    dict(context, allow_state_change=True),
                    dict(data_dict, state="active"),
                )
                redirect(h.url_for(controller="package", action="read", id=id))

            data["package_id"] = id
            try:
                if resource_id:
                    data["id"] = resource_id
                    get_action("resource_update")(context, data)
                else:
                    get_action("resource_create")(context, data)
            except ValidationError as e:
                errors = e.error_dict
                error_summary = e.error_summary
                return self.new_resource_ext(id, data, errors, error_summary)
            except NotAuthorized:
                abort(401, _("Unauthorized to create a resource"))
            except NotFound:
                abort(404, _("The dataset {id} could not be found.").format(id=id))
            if save_action == "go-metadata":
                # XXX race condition if another user edits/deletes
                data_dict = get_action("package_show")(context, {"id": id})
                get_action("package_update")(
                    dict(context, allow_state_change=True),
                    dict(data_dict, state="active"),
                )
                h.flash_notice(_("Dataset has been deleted."))
                h.redirect_to(controller="package", action="read", id=id)

            elif save_action == "go-datadict":
                data_dict = get_action("package_show")(context, {"id": id})
                get_action("package_update")(
                    dict(context, allow_state_change=True),
                    dict(data_dict, state="active"),
                )
                # h.flash_notice(_('Dataset has been deleted.'))
                print(
                    "save action was go-datadict in the exntenstion NEEWWWW!!!!!!!!!!!"
                )
                h.redirect_to("/dataset/relationship/edit/" + id)
            # redirect(h.url_for(controller='package', action='finaldict', id=id))
            elif save_action == "go-dataset":
                # go to first stage of add dataset
                h.redirect_to(controller="package", action="edit", id=id)
            elif save_action == "go-dataset-complete":
                # go to first stage of add dataset
                h.redirect_to(controller="package", action="read", id=id)
            else:
                # add more resources
                h.redirect_to(controller="package", action="new_resource", id=id)
        # get resources for sidebar
        context = {
            "model": model,
            "session": model.Session,
            "user": c.user or c.author,
            "auth_user_obj": c.userobj,
        }
        try:
            pkg_dict = get_action("package_show")(context, {"id": id})
        except NotFound:
            abort(404, _("The dataset {id} could not be found.").format(id=id))
        try:
            check_access("resource_create", context, {"package_id": pkg_dict["id"]})
        except NotAuthorized:
            abort(401, _("Unauthorized to create a resource for this package"))

        package_type = pkg_dict["type"] or "dataset"

        errors = errors or {}
        error_summary = error_summary or {}
        vars = {
            "data": data,
            "errors": errors,
            "error_summary": error_summary,
            "action": "new",
            "resource_form_snippet": self._resource_form(package_type),
            "dataset_type": package_type,
        }
        vars["pkg_name"] = id
        # required for nav menu
        vars["pkg_dict"] = pkg_dict
        template = "package/new_resource_not_draft.html"
        if pkg_dict["state"].startswith("draft"):
            vars["stage"] = ["complete", "active"]
            template = "package/new_resource.html"
        return render(template, extra_vars=vars)

    """ def delete_ext(self, id):

        # linkResource = str("/dataset/edit/" + id)
        print("here is delete ext")

        if "cancel" in request.params:
            h.redirect_to(controller="package", action="edit", id=id)

        context = {
            "model": model,
            "session": model.Session,
            "user": c.user,
            "auth_user_obj": c.userobj,
        }

        try:
            if request.method == "POST":
                # Added by mandana to solve the problem regarding
                for rel in ["depends_on", "links_to", "child_of"]:
                    print("test:" + rel)
                    rel_exist = []
                    try:
                        rel_exist = get_action("package_relationships_list")(
                            data_dict={"id": id, "rel": rel}
                        )
                        print("done with action")
                        print(rel_exist)
                        if len(rel_exist) != 0:
                            print(rel, "exists")
                            for ds in rel_exist:
                                data_dict = {
                                    "subject": id,
                                    "object": ds["object"],
                                    "type": rel,
                                }
                                get_action("package_relationship_delete")({}, data_dict)
                                print("hier ist ds:")
                    except:
                        print("faild:" + rel)
                        # pass
                        ####### till here############
                get_action("package_delete")(context, {"id": id})
                # 				print('finally deleted!')
                h.flash_notice(_("Dataset has been deleted."))
                h.redirect_to(controller="package", action="search")
            c.pkg_dict = get_action("package_show")(context, {"id": id})
            dataset_type = c.pkg_dict["type"] or "dataset"
        except NotAuthorized:
            abort(403, _("Unauthorized to delete package %s") % "")
        except NotFound:
            abort(404, _("Dataset not found"))
        return render(
            "package/confirm_delete.html", extra_vars={"dataset_type": dataset_type}
        )"""

    def edit_relation(self, id, data=None, errors=None):

        try:
            c.link = str("/dataset/relationship/new_relationship/" + id)
            """context = {
                "model": model,
                "session": model.Session,
                "user": c.user or c.author,
                "for_view": True,
                "auth_user_obj": c.userobj,
                "use_cache": False,
            }"""
            c.pkg_dict = get_action("package_show")({
                "model": model,
                "session": model.Session,
                "user": c.user or c.author,
                "for_view": True,
                "auth_user_obj": c.userobj,
                "use_cache": False,
            }, {"id": id})
           # c.pkg = context["package"]
        except NotFound:
            abort(404, _("Dataset not found"))
        except NotAuthorized:
            abort(401, _("Unauthorized to read dataset %s") % id)

        return render("package/edit_data_relation.html", extra_vars={"package_id": id})

    def relation(self, id):
        context = {
            "model": model,
            "session": model.Session,
            "user": c.user or c.author,
            "for_view": True,
            "auth_user_obj": c.userobj,
            "use_cache": False,
        }
        data_dict = {"id": id}
        try:
            c.pkg_dict = get_action("package_show")(context, data_dict)
            dataset_type = c.pkg_dict["type"] or "dataset"
        except NotFound:
            abort(404, _("Dataset not found"))
        except NotAuthorized:
            abort(401, _("Unauthorized to read dataset %s") % id)
        return p.toolkit.render(
            "package/snippets/relation_list.html", {"dataset_type": dataset_type}
        )
