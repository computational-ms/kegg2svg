import setuptools
from loguru import logger


def branch_dependent_version():
    import setuptools_scm

    def void(version):
        return ""

    def version_scheme(version):
        if version.branch in ["main", "master"]:
            _v = str(version.tag)
        else:
            _v = setuptools_scm.get_version(local_scheme=void)
        return _v

    def local_scheme(version):
        if version.branch in ["main", "master"]:
            _v = ""
        else:
            _v = setuptools_scm.get_version(version_scheme=void)
        return _v

    scm_version = {
        "root": ".",
        "relative_to": __file__,
        "version_scheme": version_scheme,
        "local_scheme": local_scheme
        # >> "no-local-version" not quit good enough
        # >> on dev "node-and-timestamp",  # version_scheme,
    }
    return scm_version


setuptools.setup(
    use_scm_version=branch_dependent_version,
    setup_requires=["setuptools_scm"],
)
