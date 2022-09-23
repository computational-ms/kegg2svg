import setuptools

setuptools.setup(
    use_scm_version={
        "root": ".",
        "relative_to": __file__,
        "local_scheme": "node-and-timestamp",
        # "tag_regex": r"^(?P<prefix>v)?(?P<version>[^\+]+)(?P<suffix>.*)?$",
    },
    setup_requires=["setuptools_scm"],
)
