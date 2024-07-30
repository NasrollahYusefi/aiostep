from setuptools import setup

VERSION = "0.1.1"

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setup(
    name="aiostep",
    version=VERSION,
    description="A Python library to handle steps in aiogram framework.",
    author="Nasrollah Yusefi",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url="https://github.com/NasrollahYusefi/aiostep/",
    packages=["aiostep"],
    install_requires=[
        "cachebox"
    ],
    license="MIT",
    license_files=["LICENSE"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
