# -- General configuration ----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sphinxcontrib.apidoc',
              'sphinx.ext.viewcode',
              'openstackdocstheme',
              'cliff.sphinxext',
              ]

# sphinxcontrib.apidoc options
apidoc_module_dir = '../../ironicclient'
apidoc_output_dir = 'reference/api'
apidoc_excluded_paths = [
    'tests/functional/*',
    'tests']
apidoc_separate_modules = True


# openstackdocstheme options
openstackdocs_repo_name = 'openstack/python-ironicclient'
openstackdocs_pdf_link = True
openstackdocs_use_storyboard = True

# autodoc generation is a bit aggressive and a nuisance when doing heavy
# text edit cycles.
# execute "export SPHINX_DEBUG=1" in your terminal to disable

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
copyright = u'OpenStack Foundation'

# A list of ignored prefixes for module index sorting.
modindex_common_prefix = ['ironicclient.']

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'native'

# A list of glob-style patterns that should be excluded when looking for
# source files. They are matched against the source file names relative to the
# source directory, using slashes as directory separators on all platforms.
exclude_patterns = ['api/ironicclient.tests.functional.*']

# -- Options for HTML output --------------------------------------------------

# The theme to use for HTML and HTML Help pages. Major themes that come with
# Sphinx are currently 'default' and 'sphinxdoc'.
#html_theme_path = ["."]
#html_theme = '_theme'
#html_static_path = ['_static']
html_theme = 'openstackdocs'

# Output file base name for HTML help builder.
htmlhelp_basename = 'python-ironicclientdoc'

latex_use_xindy = False

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto/manual]).
latex_documents = [
    (
        'index',
        'doc-python-ironicclient.tex',
        u'Python Ironic Client Documentation',
        u'OpenStack LLC',
        'manual'
    ),
]

autoprogram_cliff_application = 'openstack'
