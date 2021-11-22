app:
	mkdir app; \
	cp -r  requirements.txt local_lib *.py app/; \
	cd app; \
	pip3 install -t . -r requirements.txt; \
	rm -rf ./__pycache__ ./*.dist-info ./_distutils_hack ./setuptools; \
	cd ..; \
	mv app/cpak.py app/__main__.py; \
	python3 -m zipapp -c app -p '/usr/bin/env python3'
	#python3 ./app/cpak.py

