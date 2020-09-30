import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ucs-exporter", # Replace with your own username
    version="0.0.1",
    author="Mithun Gore",
    author_email="mithungore@gmail.com",
    description="Interface to access ucs metrics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sapcc/ucs-exporter",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'master_password',
        'ucsmsdk',
        'ucscsdk',
        'prometheus_client',
        'scrypt'
    ],
    python_requires='>=3.6',
)