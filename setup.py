from setuptools import setup, find_packages

VERSION = "0.2.0"

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
    keywords="aiogram, steps, states, Telegram bot, asynchronous, aiostep",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "cachebox>=4.2.3"
    ],
    extras_require={
        "redis": ["redis>=5.1.1"],
    },
    license="MIT",
    license_files=["LICENSE"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
    ],
)
