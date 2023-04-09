# Makefile

all: install run

install: venv
	: # Activate venv and install smthing inside
	( \
		pip install --upgrade pip; \
		pip --version; \
	)
	. chattier/bin/activate && pip install -r requirements.txt
	: # Other commands here

venv:
	: # Create venv if it doesn't exist
	: # test -d venv || virtualenv -p python3 --no-site-packages venv
	test -d venv || python3 -m venv venv

run:
	: # Run your app here, e.g
	: # determine if we are in venv,
	: # see https://stackoverflow.com/q/1871549
	. chattier/bin/activate && pip -V

	: # Or see @wizurd's answer to exec multiple commands
	. chattier/bin/activate && (\
		python3 -c 'import sys; print(sys.prefix)'; \
		pip3 -V \
	)

clean:
	rm -rf chattier
	find -iname "*.pyc" -delete

git:
	( \
		git add .; \
		git commit -m "$m"; \
		git push -u origin master; \
	) 

resume:
	( \
		git pull; \
		source chattier/bin/activate; \
		pip install -r requirements.txt; \
	)