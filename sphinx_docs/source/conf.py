# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import os
import sys
sys.path.insert(0, os.path.abspath('../../app'))


# -- Project information -----------------------------------------------------

project = 'AusteniteCalculator'
copyright = 'Pursuant to Title 17 United States Code § 105, works of the United States Government are not subject to copyright protection within the United States.'
author = 'Adam Creuziger, David Newton, Max Garman, Caleb Schenck'

# The full version, including alpha/beta/rc tags
release = '0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.napoleon', 'sphinx.ext.autodoc']

# Added so that Google Style comments with mulitple return values behaves
# https://github.com/sphinx-doc/sphinx/issues/9119
napoleon_custom_sections = [('Returns', 'params_style')]

autodoc_default_flags = ['members']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.

exclude_patterns = []

autodoc_mock_imports = ["GSASIIscriptable","GSASIIpath", "plotly", "pandas", "numpy", "math", "atmdata", "json", "secrets", "tempfile","zipfile", "flask", "_tkinter", "scipy", "cmdstanpy", "xarray" ,"sys", "platform", "os", "io", "base64", "re", "pickle","time", "logging","cProfile","enum","copy","base64","matplotlib" ]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
#html_theme = 'alabaster'
html_theme = 'classic'


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# Seems to only apply for the 'alabaster' html_theme
# html_static_path = ['_static']
