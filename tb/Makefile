SIM ?= icarus
TOPLEVEL_LANG = verilog

# 1. Pfad zur Verilog-Datei (eins höher in hdl/ springen)
VERILOG_SOURCES += ../hdl/FIR.v

TOPLEVEL = FIR

# 2. Modulpfad zu deiner Testdatei
MODULE = tests.test_fir

# 3. PYTHONPATH muss sowohl tb/ als auch das Root-Verzeichnis kennen, 
# damit 'tests', 'models' und 'utils' sauber importiert werden können
export PYTHONPATH := $(PWD):$(PWD)/..:$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim