package=quickapp

include pypackage.mk

bump-upload:
	bumpversion patch
	git push --tags
	git push --all
	python setup.py sdist upload
