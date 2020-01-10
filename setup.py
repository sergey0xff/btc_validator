import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="btc_validator",
    version="1.0.2",
    description="Bitcoin address validator",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/sergey-tikhonov/btc_validator",
    author="Sergey Tikhonov",
    author_email="srg.tikhonov@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["btc_validator"],
    include_package_data=True,
)
