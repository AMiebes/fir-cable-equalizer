# tb/utils/fir_helpers.py
from cocotb.triggers import RisingEdge

def set_coeffs(dut, coeff_list):
    # Dynamisches Auslesen des Verilog-Parameters (Fallback auf 16 Bit)
    coeff_width = int(dut.COEFF_WIDTH.value) if hasattr(dut, "COEFF_WIDTH") else 16
    mask = (1 << coeff_width) - 1
    
    flat_val = 0
    for i, c in enumerate(coeff_list):
        c_val = c & mask
        flat_val |= (c_val << (i * coeff_width))
    dut.coeffs_flat.value = flat_val

async def reset_dut(dut):
    dut.rst_n.value = 0
    dut.signal_in.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)