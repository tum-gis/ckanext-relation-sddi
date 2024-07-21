import cgi

from flask import Blueprint
from flask.views import MethodView

import ckan.model as model
import ckan.logic as logic
import ckan.plugins.toolkit as tk
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.lib.base as base

from ckan.lib.plugins import lookup_package_plugin

relation = Blueprint('relation', __name__)

clean_dict = logic.clean_dict
tuplize_dict = logic.tuplize_dict
parse_params = logic.parse_params
NotFound = tk.ObjectNotFound
NotAuthorized = tk.NotAuthorized
ValidationError = tk.ValidationError


# class RelationAdd(MethodView):
#    def get(self):
#        pass

#    def post(self):
#        pass


def relations(id):
    context = {
        "model": model,
        "session": model.Session,
        "user": tk.g.user,
        "for_view": True,
        "auth_user_obj": tk.g.userobj,
        "use_cache": False,
    }
    data_dict = {"id": id}

    try:
        tk.g.pkg_dict = pkg_dict = tk.get_action("package_show")(context, data_dict)
        dataset_type = pkg_dict["type"] or "dataset"
    except NotFound:
        tk.abort(404, tk._("Dataset not found"))
    except NotAuthorized:
        tk.abort(401, tk._("Unauthorized to read dataset %s") % id)
    return tk.render("package/snippets/relation_list.html", {
        "dataset_type": dataset_type,
        "pkg_dict": pkg_dict}
    )


def new_relation(id):
    breakpoint()
    tk.g.link = str("/dataset/relationship/edit/" + id)

    if tk.request.method == "POST":
        data = clean_dict(
                dict_fns.unflatten(tuplize_dict(parse_params(tk.request.form)))
            )
        save_action = data.get("save")
        print("new data dictionary !!!!!!!!!!!!!!!!")
        context = {
            "model": model,
            "session": model.Session,
            "user": tk.g.user,
            "auth_user_obj": tk.g.userobj,
        }

        # Remove button in the edit page
        removed_rel = None
        type_rem = None
        for param in data:
            if param.startswith("relation_remove"):
                removed_rel = param.split(".")[-1]
                type_rem = param.split(".")[-2]
                break
        if removed_rel:
            data_dict = {"subject": id, "object": removed_rel, "type": type_rem}

            try:
                tk.get_action("package_relationship_delete")(context, data_dict)
            except NotFound:
                tk.abort(404, tk._("Relationship not found"))
            try:
                tk.check_access("package_relationship_create", context, data_dict)
            except NotAuthorized:
                tk.abort(
                    401, tk._("Unauthorized to create a relationship for this package")
                )
            return h.redirect_to("/dataset/relationship/edit/" + id)

        # add button in the edit page
        add_rel = None
        type_add = None
        for param in data:
            if param.startswith("relation_add"):
                add_rel = param.split(".")[-1]
                type_add = param.split(".")[-2]
                break

        if add_rel:
            # context={'ignore_auth': True}
            data_dict = {"subject": id, "object": add_rel, "type": type_add}

            try:
                tk.get_action("package_relationship_create")(context, data_dict)
            except NotFound:
                tk.abort(404, tk._("Relationship cannot be created"))

            # try:
            # 	check_access('package_relationship_create', context, {'object': add_rel, 'subject': id})#{"package_id": pkg_dict["id"]})
            # 	print('it is done')
            # except NotAuthorized:
            #    abort(401, _('Unauthorized to create a relationship for this package'))
            return h.redirect_to("/dataset/relationship/edit/" + id)

        if save_action == "go-metadata":
            # XXX race condition if another user edits/deletes
            return h.redirect_to('dataset.read', id=id)

    return h.redirect_to("/dataset/relationship/edit/" + id)


def _resource_form(package_type):
        # backwards compatibility with plugins not inheriting from
        # DefaultDatasetPlugin and not implmenting resource_form
        plugin = lookup_package_plugin(package_type)
        if hasattr(plugin, "resource_form"):
            result = plugin.resource_form()
            if result is not None:
                return result
        return lookup_package_plugin().resource_form()


class CreateResource(MethodView):

    def post(self, id, data=None, errors=None, error_summary=None):
            """ FIXME: This is a temporary action to allow styling of the
            forms. """
            # if save_action == 'go-datadict':
            # redirect(h.url_for(controller='package', action='addDictionary'))
            data = data or clean_dict(
                dict_fns.unflatten(tuplize_dict(parse_params(tk.request.form)))
            )
            data.update(clean_dict(
                dict_fns.unflatten(tuplize_dict(parse_params(tk.request.files)))
            ))
            # we don't want to include save as it is part of the form
            save_action = data.get('save')
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
                "user": tk.g.user,
                "auth_user_obj": tk.g.userobj,
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
                    data_dict = tk.get_action("package_show")(context, {"id": id})
                    tk.get_action("package_update")(
                        dict(context, allow_state_change=True),
                        dict(data_dict, state="active"),
                    )
                    # h.flash_notice(_('Dataset has been deleted.'))
                    print(
                        "save action was go-datadict in the exntenstion NEEWWWW!!!!!!!!!!!"
                    )
                    return h.redirect_to("/dataset/relationship/edit/" + id)

                if save_action == "go-dataset":
                    # go to final stage of adddataset
                    return h.redirect_to(h.url_for('dataset.edit', id=id))
                # see if we have added any resources
                try:
                    data_dict = tk.get_action("package_show")(context, {"id": id})
                except NotAuthorized:
                    tk.abort(401, tk._("Unauthorized to update dataset"))
                except NotFound:
                    tk.abort(404, tk._("The dataset {id} could not be found.").format(id=id))

                require_resources = tk.asbool(
                    tk.gonfig.get("ckan.dataset.create_on_ui_requires_resources", "True")
                )
                if require_resources and not len(data_dict["resources"]):
                    # no data so keep on page
                    msg = tk._("You must add at least one data resource")
                    # On new templates do not use flash message

                    if tk.asbool(tk.gonfig.get("ckan.legacy_templates")):
                        h.flash_error(msg)
                        return h.redirect_to('dataset.new', id=id)
                    else:
                        errors = {}
                        error_summary = {tk._("Error"): msg}
                        return self.get(id, data, errors, error_summary)

                # XXX race condition if another user edits/deletes
                data_dict = tk.get_action("package_show")(context, {"id": id})
                tk.get_action("package_update")(
                    dict(context, allow_state_change=True),
                    dict(data_dict, state="active"),
                )
                return h.redirect_to(h.url_for('dataset.read', id=id))

            data["package_id"] = id
            try:
                if resource_id:
                    data["id"] = resource_id
                    tk.get_action("resource_update")(context, data)
                else:
                    tk.get_action("resource_create")(context, data)
            except ValidationError as e:
                errors = e.error_dict
                error_summary = e.error_summary
                return self.get(id, data, errors, error_summary)
            except NotAuthorized:
                tk.abort(401, tk._("Unauthorized to create a resource"))
            except NotFound:
                tk.abort(404, tk._("The dataset {id} could not be found.").format(id=id))

            if save_action == "go-metadata":
                # XXX race condition if another user edits/deletes
                data_dict = tk.get_action("package_show")(context, {"id": id})
                tk.get_action("package_update")(
                    dict(context, allow_state_change=True),
                    dict(data_dict, state="active"),
                )
                return h.redirect_to('dataset.read', id=id)

            elif save_action == "go-datadict":
                data_dict = tk.get_action("package_show")(context, {"id": id})
                tk.get_action("package_update")(
                    dict(context, allow_state_change=True),
                    dict(data_dict, state="active"),
                )
                # h.flash_notice(_('Dataset has been deleted.'))
                print(
                    "save action was go-datadict in the exntenstion NEEWWWW!!!!!!!!!!!"
                )
                return h.redirect_to("relation.edit_relation", id=id)
            # redirect(h.url_for(controller='package', action='finaldict', id=id))
            elif save_action == "go-dataset":
                # go to first stage of add dataset
                return h.redirect_to('dataset.edit', id=id)
            elif save_action == "go-dataset-complete":
                # go to first stage of add dataset
                return h.redirect_to('dataset.edit', id=id)
            else:
                # add more resources
                return h.redirect_to('dataset.new', id=id)

    def get(self, id, data=None, errors=None, error_summary=None):
        # get resources for sidebar
        tk.g.linkResource = str("/dataset/new_resource/" + id)
        context = {
            "model": model,
            "session": model.Session,
            "user": tk.g.user,
            "auth_user_obj": tk.g.userobj,
        }

        try:
            pkg_dict = tk.get_action("package_show")(context, {"id": id})
        except NotFound:
            tk.abort(404, tk._("The dataset {id} could not be found.").format(id=id))
        try:
            tk.check_access("resource_create", context, {"package_id": pkg_dict["id"]})
        except NotAuthorized:
            tk.abort(401, tk._("Unauthorized to create a resource for this package"))

        package_type = pkg_dict["type"] or "dataset"

        errors = errors or {}
        error_summary = error_summary or {}
        vars = {
            "data": data,
            "errors": errors,
            "error_summary": error_summary,
            "action": "new",
            "resource_form_snippet": _resource_form(package_type),
            "dataset_type": package_type,
        }
        vars["pkg_name"] = id
        # required for nav menu
        vars["pkg_dict"] = pkg_dict
        template = "package/new_resource_not_draft.html"
        if pkg_dict["state"].startswith("draft"):
            vars["stage"] = ["complete", "active"]
            template = "package/new_resource.html"
        return tk.render(template, extra_vars=vars)


def finalrel(id, data=None, errors=None):
    if tk.request.method == "POST":
        pass
    tk.g.link = str("/dataset/relationship/edit/" + id)
    try:
        pkg_dict = tk.get_action("package_show")({
            "model": model,
            "session": model.Session,
            "user": tk.g.user,
            "for_view": True,
            "auth_user_obj": tk.g.userobj,
            "use_cache": False,
        }, {"id": id})
        tk.g.pkg_dict = tk.g.pkg = pkg_dict
    except NotFound:
        tk.abort(404, tk._("Dataset not found"))
    except NotAuthorized:
        tk.abort(401, tk._("Unauthorized to read dataset %s") % id)
    return tk.render("package/new_data_relation.html", extra_vars={"package_id": id, "pkg_dict": pkg_dict})


def edit_relation(id, data=None, errors=None):
    try:
        tk.g.link = str("/dataset/relationship/new_relationship/" + id)
        """context = {
            "model": model,
            "session": model.Session,
            "user": c.user or c.author,
            "for_view": True,
            "auth_user_obj": c.userobj,
            "use_cache": False,
        }"""
        pkg_dict = tk.get_action("package_show")({
            "model": model,
            "session": model.Session,
            "user": tk.g.user,
            "for_view": True,
            "auth_user_obj": tk.g.userobj,
            "use_cache": False,
        }, {"id": id})
        tk.g.pkg_dict = tk.g.pkg = pkg_dict
    except NotFound:
        tk.abort(404, tk._("Dataset not found"))
    except NotAuthorized:
        tk.abort(401, tk._("Unauthorized to read dataset %s") % id)

    return tk.render("package/edit_data_relation.html", extra_vars={"package_id": id, "pkg_dict": pkg_dict})


relation.add_url_rule("/dataset/relationship/<id>", view_func=relations),
relation.add_url_rule("/dataset/relationship/new_relationship/<id>", view_func=new_relation, methods=("GET", "POST")),
relation.add_url_rule("/dataset/<id>/resource/new", view_func=CreateResource.as_view(str(u'new_res'))),
relation.add_url_rule("/dataset/relationship/add/<id>", view_func=finalrel, methods=("GET", "POST")),
relation.add_url_rule("/dataset/relationship/edit/<id>", view_func=edit_relation, methods=("GET", "POST")),


def get_blueprints():
    return [relation]
