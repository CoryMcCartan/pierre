from setuptools import setup, find_packages

setup(
    name = "pierre",
    version = "0.0.1",
    py_modules = ["pierre"],
    install_requires = ["Click"],
    package_dir = {"": "pierre"},
    entry_points = {
        "console_scripts": [
            "pierre  =  pierre:main"
        ]
    },
)
        
