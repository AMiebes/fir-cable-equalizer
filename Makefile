.PHONY: test clean

# Leitet den 'make test' Befehl in den tb/-Ordner weiter
test:
	$(MAKE) -C tb

clean:
	$(MAKE) -C tb clean