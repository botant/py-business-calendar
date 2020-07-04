import os

from setuptools import find_packages, setup


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), "r") as f:
        return f.read()


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
    name="business_calendar",
    version="1.0",
    description="Business days including custom work week and holidays.",
    long_description=(read("README.rst") + "\n\n" + read("HISTORY.rst")),
    url="https://github.com/botant/py-business-calendar/",
    license="MIT",
    author="Antonio Botelho",
    author_email="antonio@inhames.com",
    packages=find_packages(),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
)
