import setuptools

setuptools.setup(
    name="prenotazione-unimi",
    version="2.0.3",
    author="Mroik",
    author_email="mroik@delayed.space",
    description="Command line program that handles booking for lessons at UNIMI",
    readme="README.md",
    url="https://github.com/Mroik/prenotazione_unimi",
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: Other/Proprietary License",
    ],
    python_requires=">=3.10",
    install_requires=[
        "beautifulsoup4==4.11.1",
        "requests==2.28.1",
        "lxml==4.9.1",
    ],
)
