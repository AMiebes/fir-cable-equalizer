# tb/utils/scoreboard.py
from collections import deque
from models.fir_model import FIRGoldenModel

class Scoreboard:
    def __init__(self, dut, monitor, coeffs):
        self.dut = dut
        self.monitor = monitor
        self.model = FIRGoldenModel(
            coeffs, 
            int(dut.FRAC_WIDTH.value), 
            int(dut.IN_WIDTH.value)
        )
        self.ntaps = int(dut.NTAPS.value)
        self.input_history = deque([0] * self.ntaps, maxlen=self.ntaps)
        self.count = 0
        self.errors = 0

    async def run(self):
        while True:
            data = await self.monitor.values.get()
            self.count += 1
            
            expected = self.model.compute(list(self.input_history))
            self.input_history.appendleft(data['in'])

            # Erst vergleichen, wenn gültige Daten am Ausgang anliegen
            if self.count > 1:
                actual = data['out']
                # Latenz-Check: Erst prüfen, wenn die Pipeline des Filters voll gelaufen ist (NTAPS + 1 Takte)
                if self.count > self.ntaps + 1:
                    if actual != expected:
                        self.dut._log.error(f"FAIL @ Takt {self.count}: Hardware={actual}, Modell={expected} (Diff={actual - expected})")
                        self.errors += 1