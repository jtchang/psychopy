from setuptools import setup


setup(
    name="fitzpsychopy",
    version="1.0.0",
    description="Fitzlab Helper Functions for Psychopy",
    packages=["triggers", "fitzhelpers"],
    install_requires=["psychopy",
                      "mcculw",
                      "numpy"]
)
