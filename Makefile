.PHONY: test clean

# Leitet den 'make test' Befehl in den tb/-Ordner weiter
test:
	$(MAKE) -C tb
	python3 -c "import xml.etree.ElementTree as ET; t=ET.parse('tb/results.xml'); ET.indent(t, space='  '); t.write('tb/results.xml')"

clean:
	$(MAKE) -C tb clean