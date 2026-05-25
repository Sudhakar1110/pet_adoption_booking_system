from setuptools import setup, find_packages

setup(
    name='pet_adoption_booking',
    version='0.0.1',
    description='Pet Adoption Booking App',
    author='Sudhakar',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=['frappe']
)
