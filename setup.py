from setuptools import setup

with open('README.md', 'rb') as f:
    readme = f.read().decode('utf-8')

keywords = [
    "pyguievent",
    "PySimpleEvent",
    "PySimpleGUI",
    "PySimpleGUI4",
    "FreeSimpleGUI",
    "GUI",
    "events for simplegui",
]
import pyguievent

setup(
    name="pyguievent",
    url="https://github.com/yunluo/pyguievent",
    version=pyguievent.__version__,
    license="GPL-3.0 license",
    author=pyguievent.__author__,
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email="sp91@qq.com",
    keywords=keywords,
    description="A simple tool to create events to PySimpleGUI or PySimpleGUI4",
    py_modules=["pyguievent"],
    python_requires=">=3",
    project_urls={
        "Source": "https://github.com/yunluo/pyguievent",
    },
)
