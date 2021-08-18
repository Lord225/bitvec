import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pybytes-Lord225",
    version="0.0.1",
    author="Lord225",
    author_email="zlotymaciej@gmail.com",
    description="Tools for working with binary numbers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Lord225/PyBytes",
    package_dir={"": "pybytes"},
    packages=setuptools.find_packages(where="pybytes"),
    python_requires=">=3.9",
)