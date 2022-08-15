import pathlib
import re
from setuptools import setup, find_packages

# Root directory
# (README.md, requests_doh/__init__.py)
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
init_file = (HERE / "requests_doh/__init__.py").read_text()

def get_version():
    """Get version of the app"""
    re_version = r'__version__ = \"([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3})\"'
    _version = re.search(re_version, init_file)

    if _version is None:
        raise RuntimeError("Version is not set")

    return _version.group(1)

def get_value_var(var_name):
    """Get value of `__{var_name}__` from `requests_doh/__init__.py`"""
    var = f'__{var_name}__'
    regex = '%s = "(.{1,})"' % var

    found = re.search(regex, init_file)

    if found is None:
        raise RuntimeError(f'{var} is not set in "requests_doh/__init__.py"')
    
    return found.group(1)

def get_requirements():
    """Return tuple of library needed for app to run"""
    main = []
    try:
        with open('./requirements.txt', 'r') as r:
            main = r.read().splitlines()
    except FileNotFoundError:
        raise RuntimeError("requirements.txt is needed to build requests-doh")

    if not main:
        raise RuntimeError("requirements.txt have no necessary libraries inside of it")

    docs = []
    try:
        with open('./requirements-docs.txt', 'r') as r:
            docs = r.read().splitlines()
    except FileNotFoundError:
        # There is no docs requirements
        # Developers can ignore this error and continue to install without any problem.
        # However, this is needed if developers want to create documentation in readthedocs.org or local device.
        pass

    return main, {
        "docs": docs,
    }

# Get requirements needed to build app
requires_main, extras_require = get_requirements()

# Get all modules
packages = find_packages('.')

# Get repository
repo = get_value_var('repository')

# Finally run main setup
setup(
    name = 'requests-doh',         
    packages = packages,   
    version = get_version(),
    license=get_value_var('license'),
    description = get_value_var('description'),
    long_description= README,
    long_description_content_type= 'text/markdown',
    author = get_value_var('author'),
    author_email = get_value_var('author_email'),
    url = f'https://github.com/{repo}',
    keywords = [
        'requests',
        'doh',
        'dns',
        'https',
        'dns-over-https'
    ], 
    install_requires=requires_main,
    extras_require=extras_require,
    classifiers=[
        'Development Status :: 5 - Production/Stable',  
        'Intended Audience :: Developers',
        'Topic :: Internet :: Name Service (DNS)',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: MIT License',  
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
    python_requires='>=3.8'
)
