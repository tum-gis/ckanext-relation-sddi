import ckan.plugins.toolkit as tk

# Relationship types that can be edited from the "Edit Relationship" tab
RELATION_TYPES = ("child_of", "depends_on", "links_to")

# Same order as the marker classes in group_label.css / marker.html
MARKER_CLASSES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight"]


def _attr(obj, key):
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


def marker_info(pkg):
    """Return {"cls": marker class (zero..eight or free), "title": main category title}."""
    try:
        categories = tk.h.get_allowable_children_groups("main-categories") or []
        main_groups = tk.h.get_selected_group(pkg.get("groups", []), "main-categories") or []
    except Exception:
        return {"cls": "free", "title": None}

    names = [_attr(c, "name") for c in categories[:len(MARKER_CLASSES)]]
    # marker.html keeps the colour of the last matching group, do the same here
    for group in reversed(list(main_groups)):
        name = _attr(group, "name")
        if name in names:
            return {
                "cls": MARKER_CLASSES[names.index(name)],
                "title": _attr(group, "display_name") or _attr(group, "title") or name,
            }
    return {"cls": "free", "title": None}


def marker_class(pkg):
    """Return the marker class (zero..eight or free) of the dataset's main category."""
    return marker_info(pkg)["cls"]


def related_packages(id, rel_type):
    """Return the packages connected to this dataset with the given relationship type.

    child_of / depends_on / links_to are outgoing (this dataset points to them),
    parent_of / dependency_of / linked_from are incoming (they point to this dataset).
    """
    getters = {
        "child_of": get_parent_package,
        "depends_on": get_dependency_package,
        "links_to": get_linked_package,
        "parent_of": get_child_package,
        "dependency_of": get_depend_package,
        "linked_from": get_links_package,
    }
    packages = getters[rel_type](id) or []
    return [p for p in packages if p.get("state") != "deleted"]


def relation_candidates(id, rel_type, q, rows=20):
    """Return datasets matching 'q' that can still be connected to dataset 'id'."""
    if rel_type not in RELATION_TYPES or not q:
        return []

    existing = set(rel_id_list(related_packages(id, rel_type)))
    pkg = tk.get_action("package_show")(data_dict={"id": id})

    datasets = tk.get_action("package_search")(
        {}, data_dict={"q": q, "rows": rows, "include_private": True}
    )
    return [
        res for res in datasets["results"]
        if res["id"] != pkg["id"] and res["id"] not in existing and res.get("organization")
    ]


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
