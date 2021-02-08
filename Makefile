PYFILES := $(shell find fest tests -name '*.py')
SDIST   := dist/$(shell python setup.py --fullname).tar.gz

all: $(SDIST)

clean:
	rm -rf dist

test: coverage.xml

upload: $(SDIST)
	twine upload $<

.PHONY: all clean test upload

$(SDIST): coverage.xml
	python setup.py sdist

coverage.xml: $(PYFILES)
	flake8 fest tests
	pytest || (rm $@ ; exit 1)
