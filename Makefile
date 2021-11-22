app:
	mkdir cpak; \
	cp -r requirements.txt local_lib *.py cpak/; \
	cd cpak; \
	pip3 install -t . -r requirements.txt; \
	rm -rf ./__pycache__ ./*.dist-info ./_distutils_hack ./setuptools; \
	cd ..; \
	mv cpak/cpak.py cpak/__main__.py; \
	python3 -m zipapp -c cpak -p '/usr/bin/env python3'; \
	chmod +x cpak.pyz; \
    rm -rf cpak; \
	mv cpak.pyz cpak;

	#python3 ./app/cpak.py

