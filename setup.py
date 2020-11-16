import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="energeasy-egguy",  # Replace with your own username
    version="0.0.1",
    author="Etienne \"PoPs\" G.",
    author_email="crazypops@gmail.com",
    description="An API for the eanergeasy platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/egguy/EnergEasyAPI",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=requirements,
)
