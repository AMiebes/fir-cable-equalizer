# tb/utils/monitor.py
from cocotb.triggers import RisingEdge, ReadOnly
from cocotb.queue import Queue

class Monitor:
    def __init__(self, dut):
        self.dut = dut
        self.values = Queue()

    async def run(self):
        while True:
            await RisingEdge(self.dut.clk)
            await ReadOnly()
            
            if self.dut.rst_n.value == 1:
                data = {
                    'in': int(self.dut.signal_in.value.to_signed()),
                    'out': int(self.dut.signal_out.value.to_signed())
                }
                self.values.put_nowait(data)