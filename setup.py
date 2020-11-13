from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='kam-ttn-explore',
    version='1.0',
    packages=['utils', 'models', 'sensors'],
    package_dir={'': 'src'},
    url='https://github.com/yotFEIG17907/ttn-explore',
    author='kam',
    author_email='kamstdby@comcast.net',
    description='Grabs sensor data from TTN via MQTT',
    long_description = long_description,
    long_description_content_type  = "text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Public License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=required
)
