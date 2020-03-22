import setuptools

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="evds",
    version="0.1.0",
    author="Fatih Mete",
    author_email="fatihmete@live.com",
    description="EVDS python wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fatihmete/evds",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
   install_requires=[
          'pandas', 'requests',
   ],
   python_requires='>=3.6',
)
