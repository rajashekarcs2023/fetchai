from setuptools import setup, find_packages

setup(
    name="fetchai",
    version="0.1.12",
    packages=find_packages(),  # Automatically find all packages in the folder
    install_requires=[
        "bech32>=1.2.0,<2.0",
        "ecdsa>=0.19.0,<1.0",
        "pydantic>=2.7.4,<3.0",
        "requests>=2.32.3,<3.0",
        "httpx>=0.27.2,<1.0",
    ],
    extras_require={
        "dev": [
            "black",
        ],
    },
    description="Find the right AI at the right time and register your AI to be discovered.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/flockx-official/fetchai",
    author="Devon Bleibtrey",
    author_email="bleib1dj@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
