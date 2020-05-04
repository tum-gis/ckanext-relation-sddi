ckanext-relation
=====================

This extension provides an UI for creating, deleting and viewing relationships between datasets.

In this implementation which is specifically designed for the requirements of [HEF, TUM](http://www.hef.wzw.tum.de/).


------------
Requirements
------------

This extension is tested with CKAN 2.8.0.
You may have problem with the deleting if you use this version. You may need to upgrade / update the delete function to purge all deleted datasets.
Have a look at this: https://github.com/ckan/ckan/blob/ckan-2.8.0/ckan/controllers/package.py#L1024

Here is the correct code:
```
 def delete(self, id):

        if 'cancel' in request.params:
            h.redirect_to(controller='package', action='edit', id=id)

        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'auth_user_obj': c.userobj}

        try:
            if request.method == 'POST':
				# Newly added block to delete the relationship if there exists
                # It only includes three types of relationship 
				for rel in ['depends_on', 'links_to', 'child_of']: 
					print('test:'+ rel)
					rel_exist = []
					try:
						rel_exist = get_action('package_relationships_list')(data_dict={'id': id, 'rel':rel})
						print('done with action')
						print(rel_exist)
						if len(rel_exist)!=0:
							print(rel, 'exists')
							for ds in rel_exist:
								data_dict={"subject": id, "object": ds['object'], "type": rel}								
								get_action('package_relationship_delete')({}, data_dict)
								print('hier ist ds:')
					except:
						pass
                ####### till here############
				get_action('package_delete')(context, {'id': id})             
				h.flash_notice(_('Dataset has been deleted.'))
				h.redirect_to(controller='package', action='search')							
            c.pkg_dict = get_action('package_show')(context, {'id': id})
            dataset_type = c.pkg_dict['type'] or 'dataset'
        except NotAuthorized:
            abort(403, _('Unauthorized to delete package %s') % '')
        except NotFound:
            abort(404, _('Dataset not found'))
        return render('package/confirm_delete.html',
                      extra_vars={'dataset_type': dataset_type})
```

The javascript is also directly included in the main.min.js and not in this ckanext.
Here is the Javascript code used for this extension:

```
$(document).ready(function() {
    $(".glyphicon").click(function() {
        $(this).toggleClass("glyphicon-chevron-down").toggleClass("glyphicon-chevron-up")
    })
});
```

------------
Installation
------------

To install ckanext-relation:

1. Activate your CKAN virtual environment, for example::

       . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-relation Python package into your virtual environment::

       pip install -e 'git+https://github.com/MandanaMoshref/ckanext-relation.git#egg=ckanext-relation'

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

    git clone https://github.com/MandanaMoshref/ckanext-relation.git
    cd ckanext-relation
    python setup.py develop


--------
License
--------
The ckanext-relation is available as free and open source and is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0). 

