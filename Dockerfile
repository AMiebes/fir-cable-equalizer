# Basis-Image mit Python
FROM python:3.10-slim

# Installiere Simulatoren (z.B. Icarus Verilog) und Build-Tools
RUN apt-get update && apt-get install -y \
    iverilog \
    gtkwave \
    make \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Installiere cocotb und pytest
RUN pip install --no-cache-dir cocotb cocotb-test pytest

# Arbeitsverzeichnis setzen
WORKDIR /work