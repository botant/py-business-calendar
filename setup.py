import os

from setuptools import find_packages, setup


def read(*paths):
    """Builds a file path from *paths* and returns the contents."""
    with open(os.path.join(*paths), "r") as f:
        return f.read()


#
# Setup information.
#
VERSION = "1.0"

AUTHOR = "Antonio Botelho"
AUTHOR_EMAIL = "antonio@inhames.com"
LICENSE = "MIT"

NAME = "business_calendar"
KEYWORDS = ["date", "datetime"]
PROJECT_URLS = {
    "Bug Tracker": "https://github.com/botant/py-business-calendar/issues",
    "Source Code": "https://github.com/botant/py-business-calendar",
}

DESCRIPTION = "Business days including custom work week and holidays."

LONG_DESCRIPTION = read("README.rst") + "\n\n" + read("HISTORY.rst")

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

INSTALL_REQUIRES = []
EXTRAS_REQUIRE = {
    "all": ["python-dateutil"],
    "docs": ["sphinx", "sphinx-rtd-theme"],
    "tests": ["coverage[toml]>=5.0", "pytest>=4.3.0", "python-dateutil"],
}
EXTRAS_REQUIRE["dev"] = (
    EXTRAS_REQUIRE["tests"] + EXTRAS_REQUIRE["docs"] + ["pre-commit", "tox"]
)


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url=PROJECT_URLS["Source Code"],
    project_urls=PROJECT_URLS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    classifiers=CLASSIFIERS,
    options={"bdist_wheel": {"universal": "1"}},
)
