# tb/tests/test_fir.py
import cocotb
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock
import random

from utils.fir_helpers import set_coeffs, reset_dut
from utils.monitor import Monitor
from utils.scoreboard import Scoreboard

#Reproduzierbare Zufallstests
random.seed(42)

@cocotb.test()
async def test_impulse_response(dut):
    """ Test 1: Impulsantwort synchron über Monitor & Scoreboard prüfen """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    ntaps = int(dut.NTAPS.value)
    
    coeffs = [random.randint(-8000, 8000) for _ in range(ntaps)]
    set_coeffs(dut, coeffs)
    await reset_dut(dut)

    mon = Monitor(dut)
    scb = Scoreboard(dut, mon, coeffs)
    cocotb.start_soon(mon.run())
    cocotb.start_soon(scb.run())

    # Ein einzelner Impuls am Eingang
    impulse_val = 1 << 14
    await RisingEdge(dut.clk)
    dut.signal_in.value = impulse_val
    await RisingEdge(dut.clk)
    dut.signal_in.value = 0

    # Ausklingen lassen (NTAPS + Pipeline-Flush)
    for _ in range(ntaps + 3):
        await RisingEdge(dut.clk)

    assert scb.errors == 0, f"Impulsantwort schlug mit {scb.errors} Fehlern fehl!"

@cocotb.test()
async def test_alternating_extremes(dut):
    """ Test 5: Wechselnde Extrema (+MAX / -MAX) belasten Akkumulator und Sättigung """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    ntaps = int(dut.NTAPS.value)
    in_width = int(dut.IN_WIDTH.value)
    
    max_pos = (1 << (in_width - 1)) - 1
    max_neg = -(1 << (in_width - 1))
    
    # Koeffizienten abwechselnd positiv und negativ setzen
    coeffs = [max_pos if i % 2 == 0 else max_neg for i in range(ntaps)]
    set_coeffs(dut, coeffs)
    await reset_dut(dut)

    mon = Monitor(dut)
    scb = Scoreboard(dut, mon, coeffs)
    cocotb.start_soon(mon.run())
    cocotb.start_soon(scb.run())

    # Abwechselnde Extrema einspeisen
    pattern = [max_pos, max_neg] * 20
    for val in pattern:
        await RisingEdge(dut.clk)
        dut.signal_in.value = val

    for _ in range(ntaps + 2):
        await RisingEdge(dut.clk)

    assert scb.errors == 0, f"Alternating Extremes Test schlug mit {scb.errors} Fehlern fehl!"

@cocotb.test()
async def test_overflow_saturation(dut):
    """ Test 2: Positiver Überlauf muss auf MAX_POS (Sättigung) begrenzen """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    ntaps = int(dut.NTAPS.value)
    in_width = int(dut.IN_WIDTH.value)
    
    max_pos = (1 << (in_width - 1)) - 1
    
    set_coeffs(dut, [max_pos] * ntaps)
    await reset_dut(dut)
    
    dut.signal_in.value = max_pos
    for _ in range(ntaps * 2):
        await RisingEdge(dut.clk)
    
    actual = int(dut.signal_out.value.to_signed())
    assert actual == max_pos, f"Überlauf-Sättigung fehlgeschlagen: Erwartet {max_pos}, bekommen {actual}"

@cocotb.test()
async def test_underflow_saturation(dut):
    """ Test 3: Negativer Überlauf muss auf MAX_NEG (Sättigung) begrenzen """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    ntaps = int(dut.NTAPS.value)
    in_width = int(dut.IN_WIDTH.value)
    
    max_pos = (1 << (in_width - 1)) - 1
    max_neg = -(1 << (in_width - 1))
    
    set_coeffs(dut, [max_pos] * ntaps)
    await reset_dut(dut)
    
    dut.signal_in.value = max_neg
    for _ in range(ntaps * 2):
        await RisingEdge(dut.clk)
    
    actual = int(dut.signal_out.value.to_signed())
    assert actual == max_neg, f"Unterlauf-Sättigung fehlgeschlagen: Erwartet {max_neg}, bekommen {actual}"

@cocotb.test()
async def test_exact_half_rounding(dut):
    """ Test 6: Exakter Half-Boundary Test (Prüfung der Round-to-Nearest Logik) """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    ntaps = int(dut.NTAPS.value)
    frac = int(dut.FRAC_WIDTH.value)
    
    # Setze Koeffizienten so, dass ein einfacher Multiplikator entsteht
    coeffs = [1 << frac] + [0] * (ntaps - 1)
    set_coeffs(dut, coeffs)
    await reset_dut(dut)

    mon = Monitor(dut)
    scb = Scoreboard(dut, mon, coeffs)
    cocotb.start_soon(mon.run())
    scb_task = cocotb.start_soon(scb.run())

    # Erzeuge Akkumulationsergebnisse mit exakt 0.5 Offset
    # (Wert shiften, sodass Nachkommateil exakt (1 << (frac - 1)) entspricht)
    exact_half_val = 1 << (frac - 1)
    
    await RisingEdge(dut.clk)
    dut.signal_in.value = exact_half_val
    await RisingEdge(dut.clk)
    dut.signal_in.value = -exact_half_val

    for _ in range(ntaps + 4):
        await RisingEdge(dut.clk)

    assert scb.errors == 0, f"Rundungstest (.5 Boundary) schlug mit {scb.errors} Fehlern fehl!"

@cocotb.test()
async def test_mid_stream_reset(dut):
    """ Test 4: Reset während laufendem Datenstrom muss Ausgang sofort auf 0 setzen """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    ntaps = int(dut.NTAPS.value)
    
    set_coeffs(dut, [1000] * ntaps)
    await reset_dut(dut)
    
    # Signale anlegen
    dut.signal_in.value = 5000
    for _ in range(5):
        await RisingEdge(dut.clk)
        
    # Mitten im Betrieb Reset auslösen
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    
    actual = int(dut.signal_out.value.to_signed())
    assert actual == 0, f"Reset schlug fehl: Erwartet 0, bekommen {actual}"

# --- Dynamische Generierung von Zufallstests für Waveform-Traces ---
async def run_filter_test(dut, test_id):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    ntaps = int(dut.NTAPS.value)
    coeffs = [random.randint(-8000, 8000) for _ in range(ntaps)]
    
    set_coeffs(dut, coeffs)
    await reset_dut(dut)

    mon = Monitor(dut)
    scb = Scoreboard(dut, mon, coeffs)
    cocotb.start_soon(mon.run())
    cocotb.start_soon(scb.run())
    
    for _ in range(100):
        await RisingEdge(dut.clk)
        dut.signal_in.value = random.randint(-16000, 16000)
        
    for _ in range(ntaps + 2):
        await RisingEdge(dut.clk)

    assert scb.errors == 0, f"Test {test_id} schlug mit {scb.errors} Fehlern fehl!"

for i in range(100):
    test_name = f"test_random_filter_{i:03d}"
    def make_test(t_id):
        async def _t(dut): await run_filter_test(dut, t_id)
        _t.__name__ = f"test_random_filter_{t_id:03d}"
        _t.__doc__ = f"Zufallstest Nr. {t_id}"
        return cocotb.test(name=_t.__name__)(_t)
    globals()[test_name] = make_test(i)