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
	@echo '<!DOCTYPE html><html><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width,initial-scale=1" /><meta http-equiv="refresh" content="2000"><style>html, body { font-family: sans-serif; font-size: 99%; }a.meta { color: inherit; }h1 { font-weight:normal; }p.fresh time { background-color: #d74; color: #ffc; padding: 0 2px; }p.yesterday a:link { color: #333; }.value { color: #ccc; }</style><title>News</title></head><body><ul>' > index.html

post:
	@echo '</ul></body></html>' >> index.html

%.html: %.yml
	python3 generate.py $< $@
	@printf '<li><a href="%s">%s</a></li>' $@ $@ >> index.html

clean:
	rm -f $(TARGETS)

.PHONY: help build pre post clean
