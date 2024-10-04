ckanext-relation
=====================

Overview
------------

This extension provides an UI for creating, deleting and viewing relationships between datasets.
If the extension is used with [ckanext-grouphierarchy-sddi](https://github.com/tum-gis/ckanext-grouphierarchy-sddi) extension, the graphical representation will be in the colours of the groups defined in the [ckanext-grouphierarchy-sddi](https://github.com/tum-gis/ckanext-grouphierarchy-sddi) extension.

In this implementation which is specifically designed for the requirements of [HEF, TUM](http://www.hef.wzw.tum.de/).

In the following image is one example of the implementation:

![image](https://github.com/tum-gis/ckanext-relation-sddi/assets/93824048/5dcf7a0a-181c-48f2-be57-4f645be2a5a6)

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

