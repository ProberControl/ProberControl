Updating the Documentation
==========================

Overview
--------
The documentation site is built on the Sphinx module, `Sphinx docs <http://www.sphinx-doc.org/en/stable/>`_ and is written using the `reStructuredText <http://docutils.sourceforge.net/docs/user/rst/cheatsheet.txt>`_ language. If you want to update the documentation, you can follow the guide below.

Step-by-step
------------

1. Decide on where you want to add documentation. Within the ``docs\`` directory, there are a few items that are critical to the documention.
    - ``index.rst`` is the root file, all of the ``.rst`` files branch from this file.
    - ``contents.rst`` is the file that lists all of the directories listed on the documentation homepage.
    - ``source\`` directory is where all of the documentation is housed. For example, you'll find files like ``addNewInstrument.rst`` where you'll find the written documention adding a new instrument class.
2. Once you've decided where to add/edit, you merely edit the ``.rst`` file corresponding to the documentation you want to edit.
    - Note that if you are adding a new section to the documentation site, you need to create a new ``.rst`` file, put it in ``source\``, and edit ``contents.rst`` in the appropriate location.
3. Finally, in the command-prompt at the present working directory of ``..\..\ProberControl\prober\docs\sphinx-docs\`` execute ``make clean``, then execute ``make html``

4. You'll now have an updated documentation site.

.. note::
    If you are using Windows PowerShell, you may need to execute ``./make.bat clean`` and ``./make.bat html`` in order to execute a batch file if your PATH variable is not set for running ``.bat``

.. note::
    When building the html after running ``make html`` or ``./make.bat html``, the builder may throw several warnings in red. Glance over them, but most of the them are trivial and do not effect the documentation site.
