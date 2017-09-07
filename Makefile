package=quickapp

include pypackage.mk

bump-upload:
	bumpversion patch
	git push --tags
	git push --all
	rm dist/*
	python setup.py sdist
	twine upload dist/*
