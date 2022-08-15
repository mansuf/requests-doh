# Installation

## Stable version

### With PyPI

```shell
# For Windows
py -3 -m pip install requests-doh

# For Linux / Mac OS
python3 -m pip install requests-doh
```

## Development version

```{warning}
This version is not stable and may crash during run.
```

### With PyPI & Git

**NOTE:** You must have git installed. If you don't have it, install it from here https://git-scm.com/.

```shell
# For Windows
py -3 -m pip install git+https://github.com/mansuf/requests-doh.git

# For Linux / Mac OS
python3 -m pip install git+https://github.com/mansuf/requests-doh.git
```

### With Git only

**NOTE:** You must have git installed. If you don't have it, install it from here https://git-scm.com/.

```shell
git clone https://github.com/mansuf/requests-doh.git
cd requests-doh
python setup.py install
```