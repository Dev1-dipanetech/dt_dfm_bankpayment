from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in dt_dfm_bankpayment/__init__.py
from dt_dfm_bankpayment import __version__ as version

setup(
	name="dt_dfm_bankpayment",
	version=version,
	description="Bank Payment System",
	author="Dipane Technologies Pvt Ltd",
	author_email="contact@dipanetech.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
