import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="prenotazione-unimi",
    version="1.1.1",
    author="Mroik",
    author_email="mroik@delayed.space",
    description="Command line program that handles booking for lessons at UNIMI and other stuff.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mroik/Prenotazione-Automatica-Unimi",
    project_urls={
        "Bug Tracker": "https://github.com/Mroik/Prenotazione-Automatica-Unimi/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: Other/Proprietary License",
    ],
    package_dir={"": "./"},
    packages=setuptools.find_packages(where="./"),
    python_requires=">=3.9",
    install_requires=[
        "beautifulsoup4>=4.9.3",
        "requests>=2.25.1"
    ],
    entry_points={
        "console_scripts": [
            "prenotazione-unimi=prenotazione_unimi:main"
        ],
    },
)
