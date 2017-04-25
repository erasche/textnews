TARGETS:=$(wildcard *.yml)
TARGETS:=$(TARGETS:.yml=.html)

help:
	@echo 'Run make build'

build:
	git pull > /dev/null
	$(MAKE) pre
	$(MAKE) $(TARGETS)
	$(MAKE) post

pre:
	@echo '<!DOCTYPE html><html><head><title>News</title></head><body><ul>' > index.html

post:
	@echo '</ul></body></html>' >> index.html

%.html: %.yml
	python3 generate.py $< $@
	@printf '<li><a href="%s">%s</a></li>' $@ $@ >> index.html

clean:
	rm -f $(TARGETS)

.PHONY: help build pre post clean
