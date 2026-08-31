from setuptools import setup, find_packages

setup(
    name="lit-contradict",
    version="0.1.0",
    packages=find_packages(),
    py_modules=["cli"],
    install_requires=[
        "typer[all]",
        "rich",
        "pymupdf",
        "openai",
        "pydantic",
    ],
    entry_points={
        "console_scripts": [
            "lit-contradict=cli:app",
        ],
    },
)