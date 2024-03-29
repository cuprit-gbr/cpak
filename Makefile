build:

    # start dirs
	rm -rf build; \
	mkdir build; \
	mkdir cpak; \

	# build python project
	cp -r requirements.txt local_lib *.py cpak/; \
	cd cpak; \
	pip3 install -t . -r requirements.txt; \
	pip3 install --upgrade setuptools; \
	pip3 install --upgrade pip; \
	rm -rf ./__pycache__ ./*.dist-info ./_distutils_hack ./setuptools; \
	cd ..; \

	# package
	mv cpak/cpak.py cpak/__main__.py; \
	echo "__version__ = 'ckanapi-4.7'" > cpak/ckanapi/version.py; \
	python3 -m zipapp -c cpak -p '/usr/bin/env python3'; \
	chmod +x cpak.pyz; \

    # clean up
	rm -rf cpak; \
	mv cpak.pyz build/cpak;
	reset; \

	python3 ./build/cpak

test:
	python3 -m pytest --exitfirst --verbose  --failed-first

coverage:
	coverage run --source local_lib -m pytest
	coverage report -m

upload:
	./cpak.py upload-package --folder_path=./data
