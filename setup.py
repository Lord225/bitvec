import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

PACKAGES = setuptools.find_packages(where="src")

# python setup.py bdist_egg
# python setup.py bdist_wininst

print(f'Found: {PACKAGES}')

setuptools.setup(
    name="pybytes-Lord225",
    version="0.0.9",
    author="Lord225",
    author_email="zlotymaciej@gmail.com",
    description="Tools for working with binary numbers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Lord225/PyBytes",
    package_dir={"": "src"},
    packages=PACKAGES,
    python_requires=">=3.9",
    install_requires=[
        "xxhash>=2.0.2",
        "numpy>=1.19.0",
        "numba>=0.54.0"
    ]
)