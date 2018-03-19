
import setuptools

long_description = """
An Asynchronous IRC Library
===========================

AIRC is a implementation of the IRC protocol using Python's asyncio library.
It contains built in support for Twitch.tv IRC websockets as well.

AIRC is still in Alpha, so features may be added/removed/altered at any time."""

setuptools.setup(
    name="airc",
    version="1.0.0a1",
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
    keywords="irc asyncio twitch",
    project_urls={
        "Source": "https://github.com/CraftSpider/AIRC",
        "Tracker": "https://github.com/CraftSpider/AIRC/issues"
    },
    packages=setuptools.find_packages(),
    install_requires=["asyncio"],
    python_requires=">=3.5"
)