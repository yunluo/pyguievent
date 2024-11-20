from setuptools import setup

with open("README.md", "rt") as arq:
    readme = arq.read()

keywords = [
    "pyguievent",
    "PySimpleEvent",
    "PySimpleGUI",
    "FreeSimpleGUI",
    "GUI",
    "events for simplegui",
]

setup(
    name="pyguievent",
    url="https://github.com/yunluo/pyguievent",
    version="0.0.3",
    license="GPL-3.0 license",
    author="yunluo",
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email="sp91@qq.com",
    keywords=keywords,
    description="A simple tool to create events to PySimpleGUI or FreeSimpleGUI",
    packages=["pyguievent"],
    install_requires=["PySimpleGUI"],
    python_requires=">=3",
    project_urls={
        "Source": "https://github.com/yunluo/pyguievent",
    },
)
