ckanext-relation
=====================

Overview
------------

This extension provides an UI for creating, deleting and viewing relationships between datasets.
If the extension is used with [ckanext-grouphierarchy-sddi](https://github.com/tum-gis/ckanext-grouphierarchy-sddi) extension, the graphical representation will be in the colours of the groups defined in the [ckanext-grouphierarchy-sddi](https://github.com/tum-gis/ckanext-grouphierarchy-sddi) extension.

In this implementation which is specifically designed for the requirements of [HEF, TUM](http://www.hef.wzw.tum.de/).

In the following image is one example of the implementation:

![image](https://github.com/tum-gis/ckanext-relation-sddi/assets/93824048/5dcf7a0a-181c-48f2-be57-4f645be2a5a6)

------------------
Relationship types
------------------

Relationships are edited on the **Edit Relationship** tab of a catalog entry. There are three types:

| Type | Shown as | Meaning | Colour |
|---|---|---|---|
| `child_of` | **Part of** | This entry is part of another entry, e.g. a sub-project of a project. | green |
| `depends_on` | **Depends on** | This entry needs another entry, e.g. input data or a method. | red |
| `links_to` | **Related to** | This entry is related to another entry, but not part of a hierarchy. | black |

CKAN also stores each relationship in the opposite direction (`parent_of`, `dependency_of`, `linked_from`). These incoming relationships are shown in the graph, and the rules below apply to them as well.

------------------
Relationship rules
------------------

Which relationships are allowed depends on the **main category** of the catalog entries, e.g. *Projekt* or *Digitaler Zwilling* (the child groups of the `main-categories` group). The rules come from OCL invariants of the SDDI data model.

### `ChildOfMeansSubprojectToParent` (Project)

A Project can only be **Part of** another Project. A sub-project always belongs to a parent project, never to another kind of entry.

```
context Project
inv ChildOfMeansSubprojectToParent:
  self.relation
    ->select(r | r.oclIsKindOf(InternalLink))
    ->select(r | r.type = RelType::child_of)
    ->forAll(r |
      let l : InternalLink = r.oclAsType(InternalLink) in
        l.target.oclIsKindOf(Project) and l.target <> self
    )
```

### `ProjectToProjectOnlyChildOf` (Project)

Two Projects can only be connected with **Part of**. **Depends on** and **Related to** between two Projects are not allowed. A Project can still depend on or be related to entries of other categories.

```
context Project
inv ProjectToProjectOnlyChildOf:
  self.relation
    ->select(r | r.oclIsKindOf(InternalLink))
    ->forAll(r |
      let l : InternalLink = r.oclAsType(InternalLink) in
        l.target.oclIsKindOf(Project) implies l.type = RelType::child_of
    )
```

### `OutgoingConstraints` (Digital Twin)

A Digital Twin:

- can **depend on** entries of any category,
- can be **related to** Digital Twins and Projects only,
- can never be **part of** another entry.

```
context DigitalTwin
inv OutgoingConstraints:
  self.relation->select(r | r.oclIsKindOf(InternalLink))
    ->forAll(r |
      let il : InternalLink = r.oclAsType(InternalLink) in
        -- no self-loop
        il.target <> self and
        (
          (il.target.oclIsKindOf(DigitalTwin) implies
              (il.type = RelType::links_to or il.type = RelType::depends_on))
          and
          (il.target.oclIsKindOf(Project) implies
              (il.type = RelType::links_to or il.type = RelType::depends_on))
          and
          ((not il.target.oclIsKindOf(DigitalTwin) and not il.target.oclIsKindOf(Project)) implies
              il.type = RelType::depends_on)
        )
    )
```

### No self-relationships (all categories)

An entry cannot be connected to itself (`l.target <> self` in the invariants above). This applies to all main categories.

### Overview

| From \ To | Project | Digital Twin | Other categories |
|---|---|---|---|
| **Project** | Part of | Depends on, Related to | Depends on, Related to |
| **Digital Twin** | Depends on, Related to | Depends on, Related to | Depends on |
| **Other categories** | all types | all types | all types |

### How the rules are applied

- **On save:** every new relationship is checked, whether it is created on the Edit Relationship tab or through the API (`package_relationship_create`). A relationship that breaks a rule is rejected with a message, for example: *Entries of the category “Projekt” can only be part of entries of the category: “Projekt”.*
- **In the search:** when adding a connection, the search only offers entries that are allowed.
- **On the page:** each section of the Edit Relationship tab shows the rule that applies to the entry. If a type is not allowed at all, its *Add* button is hidden.
- **Several main categories:** if an entry has more than one main category, it must follow the rules of all of them. A target matches a rule if any of its main categories matches.
- **Existing relationships** are not changed. The rules only apply when a relationship is created.

### Adding or changing rules

The rules are defined in [`ckanext/relation/helpers.py`](ckanext/relation/helpers.py), using the main category names (e.g. `project`, `digital-twin`):

```python
# subject category -> relation type -> main categories the target MUST have
RELATION_RULES = {
    "project": {"child_of": {"project"}},
    "digital-twin": {"child_of": set(), "links_to": {"digital-twin", "project"}},
}

# subject category -> relation type -> main categories the target must NOT have
EXCLUDED_TARGETS = {
    "project": {"depends_on": {"project"}, "links_to": {"project"}},
}
```

- A relation type that is not listed is allowed to any target.
- An empty set (`set()`) in `RELATION_RULES` means the type is not allowed for that category.

The check itself is in `relation_violation()`. It is called from the `package_relationship_create` action in [`ckanext/relation/actions.py`](ckanext/relation/actions.py).

------------
Requirements
------------

This extension is tested with CKAN 2.11.0.

------------
Installation
------------

To install ckanext-relation:

1. Activate your CKAN virtual environment, for example::

       . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-relation Python package into your virtual environment::

       pip install -e 'git+https://github.com/tum-gis/ckanext-relation-sddi.git#egg=ckanext-relation-sddi'

3. Add ``relation`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

       sudo service apache2 reload


---------------
Config settings
---------------

None at present


----------------------
Developer installation
----------------------

To install ckanext-relation for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/tum-gis/ckanext-relation-sddi.git
    cd ckanext-relation
    python setup.py develop


--------
License
--------
The ckanext-relation is available as free and open source and is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0). 

