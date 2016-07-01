package=quickapp

include pypackage.mk

bump-upload:
	bumpversion patch
	python setup.py sdist upload


