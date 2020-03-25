from setuptools import setup

with open("README.md", "r", encoding="utf8") as rm:
    readme = rm.read()

setup(
      name="pytholog",
      version="1.0.0", 
      description="write prolog in python",
      py_modules=["pytholog"],
      package_dir={"": "src"},
      long_description=readme,
      long_description_content_type="text/markdown",
      url="https://github.com/mnoorfawi/pytholog",
      author="Muhammad N. Fawi",
      author_email="m.noor.fawi@gmail.com",
      license="MIT",
      classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ]
      )
