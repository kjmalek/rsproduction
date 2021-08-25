from setuptools import setup

setup (
    name="rsproduction",
    version="0.1.0",
    author="Kellen Malek",
    author_email="kellenmalek@hotmail.com",
    description="An internal tool used by RavenSpace for batch ingestion/processing tasks",
    url="https://github.com/kjmalek/ravenspace_production_tool",
    packages=['rsproduction'],
    install_requires=[
        'pypandoc==1.5',
        'requests==2.25.1',
        'beautifulsoup4==4.9.3'
    ]

)