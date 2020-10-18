import os

from setuptools import setup

# Get the long description from the README file
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "readme.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="todo_curses",
    version="0.1.0",
    author="Pyunghyuk Yoo",
    author_email="yoophi@gmail.com",
    description="",
    entry_points={"console_scripts": ["todo=todo_curses:main"]},
    install_requires=[
        "appdirs",
        "faker",
    ],
    license="MIT",
    packages=["todo_curses"],
    python_requires=">=3.6",
    url="https://github.com/yoophi/todo_curses",
)
