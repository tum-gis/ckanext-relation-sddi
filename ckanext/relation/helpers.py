import ckan.plugins.toolkit as tk


def outgoing_relationship(id):
    """Return true if the dataset has any relationship, false otherwise."""
    type = ["depends_on", "child_of" ,"links_to"]
    for i in type:
        try:
            relationship = tk.get_action("package_relationships_list")(data_dict={"id": id, "rel": i})                
            rel = bool(relationship)
            break
        except:
            rel = 0
    return rel


def has_relationship(id):
    """Return true if the dataset has any relationship, false otherwise."""
    relationship = tk.get_action("package_relationships_list")(
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

    query = q.get('q')
    datasets = tk.get_action("package_search")(
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
        relationships = tk.get_action("package_relationships_list")(
            data_dict={"id": id, "rel": "parent_of"}
        )
    except Exception as e:
        return {}

    children = []
    if relationships:
        for rel in relationships:
            try:
                access = tk.check_access(
                    "package_show",
                    context={"user": tk.c.user},
                    data_dict={"id": rel["object"]},
                )
                child = tk.get_action("package_show")(
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
        relationships = tk.get_action("package_relationships_list")(
            data_dict={"id": id, "rel": "child_of"}
        )
    except Exception as e:
        return {}

    parents = []
    if relationships:
        for rel in relationships:
            parent = tk.get_action("package_show")(data_dict={"id": rel["object"]})
            parents.append(parent)
    return parents


def get_dependency_package(id):
    """ Returns a list of packages that are the subjects of dependency_of relationships."""

    relationships = []
    try:
        relationships = tk.get_action("package_relationships_list")(
            data_dict={"id": id, "rel": "depends_on"}
        )
    except Exception as e:
        return {}

    dependencies = []
    if relationships:
        for rel in relationships:
            dependency = tk.get_action("package_show")(
                data_dict={"id": rel["object"]}
            )
            dependencies.append(dependency)
    return dependencies


def get_depend_package(id):
    """ Returns a list of packages that are the subjects of depends_on relationships."""

    relationships = []
    try:
        relationships = tk.get_action("package_relationships_list")(
            data_dict={"id": id, "rel": "dependency_of"}
        )
    except Exception as e:
        return {}

    depend = []
    if relationships:
        for rel in relationships:
            try:
                access = tk.check_access(
                    "package_show",
                    context={"user": tk.c.user},
                    data_dict={"id": rel["object"]},
                )
                dep = tk.get_action("package_show")(
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
        relationships = tk.get_action("package_relationships_list")(
            data_dict={"id": id, "rel": "links_to"}
        )
    except Exception as e:
        return {}

    linked = []
    if relationships:
        for rel in relationships:
            lnk = tk.get_action("package_show")(
                data_dict={"id": rel["object"]}
            )
            linked.append(lnk)

    return linked


def get_links_package(id):
    """ Returns a list of packages that are the subjects of links_to relationships."""

    relationships = []
    try:
        relationships = tk.get_action("package_relationships_list")(
            data_dict={"id": id, "rel": "linked_from"}
        )
    except Exception as e:
        return {}

    links = []
    if relationships:
        for rel in relationships:
            try:
                tk.check_access(
                    "package_show",
                    context={"user": tk.c.user},
                    data_dict={"id": rel["object"]},
                )
                link = tk.get_action("package_show")(
                    data_dict={"id": rel["object"]}
                )
                links.append(link)
            except:
                pass
    return links
