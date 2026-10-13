import ckan.plugins.toolkit as tk

import ckanext.relation.helpers as h


@tk.chained_action
def package_relationship_create(original_action, context, data_dict):
    """Reject relationships that break the main category rules (helpers.RELATION_RULES).

    Applies to the Edit Relationship page and to the API.
    """
    subject_id = data_dict.get("subject")
    object_id = data_dict.get("object")
    rel_type = data_dict.get("type")

    if subject_id and object_id and rel_type:
        show = tk.get_action("package_show")
        try:
            subject = show({"user": context.get("user")}, {"id": subject_id})
            target = show({"user": context.get("user")}, {"id": object_id})
        except (tk.ObjectNotFound, tk.NotAuthorized):
            # let the original action report missing or inaccessible datasets
            return original_action(context, data_dict)

        message = h.relation_violation(subject, target, rel_type)
        if message:
            raise tk.ValidationError({"type": [message]})

    return original_action(context, data_dict)
