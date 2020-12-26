SDIST := dist/$(shell python setup.py --fullname).tar.gz

.PHONY: default clean test upload

default: $(SDIST)

clean:
	rm -rf dist

test: coverage.xml

upload: $(SDIST)
	twine upload $<

$(SDIST): coverage.xml
	python setup.py sdist

coverage.xml: $(shell find fest tests -name '*.py')
	flake8 $^
	pytest || (rm $@ ; exit 1)
