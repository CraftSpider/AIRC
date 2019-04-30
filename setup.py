
import setuptools
import re

long_description = """
An Asynchronous IRC Library
===========================

AIRC is a implementation of the IRC protocol using Python's asyncio library.
It contains built in support for Twitch.tv IRC websockets as well.

AIRC is still in Alpha, so features may be added/removed/altered at any time."""

with open("airc/__init__.py", "r") as file:
    try:
        version = re.search(r"^__version__\s*=\s*[\"']([^\"']*)[\"']", file.read(), re.MULTILINE).group(1)
    except Exception as e:
        raise RuntimeError("Version isn't set")

if version.endswith(("a", "b")):
    try:
        import subprocess as sp
        p = sp.Popen(["git", "rev-list", "--count", "HEAD"], stdout=sp.PIPE, stderr=sp.PIPE)
        out, err = p.communicate()
        if out:
            version += out.decode("utf-8").strip()
        p = sp.Popen(["git", "rev-parse", "--short", "HEAD"], stdout=sp.PIPE, stderr=sp.PIPE)
        out, err = p.communicate()
        if out:
            version += "+g" + out.decode("utf-8").strip()
    except Exception as e:
        raise RuntimeError("Failure to get current git commit")

setuptools.setup(
    name="airc",
    version=version,
    description="An asynchronous IRC implementation",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/CraftSpider/AIRC",
    author="CraftSpider",
    author_email="runetynan@gmail.com",
    license="MIT",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5'
    ],
    keywords="irc asyncio",
    project_urls={
        "Source": "https://github.com/CraftSpider/AIRC",
        "Tracker": "https://github.com/CraftSpider/AIRC/issues"
    },
    packages=setuptools.find_packages(),
    install_requires=[
        "asyncio",
        "websockets>=6.0"
    ],
    python_requires=">=3.5"
)
