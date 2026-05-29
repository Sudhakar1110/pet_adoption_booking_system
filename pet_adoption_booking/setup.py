from setuptools import setup, find_packages

import os

with open(os.path.join(os.path.dirname(__file__), "requirements.txt")) as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="pet_adoption_booking",
    version="0.0.1",
    description="Frappe + ERPNext v15 based Pet Adoption Application",
    author="Sudhakar",
    author_email="sudhakar@gmail.com",
    license="MIT",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
    python_requires=">=3.10",
)
