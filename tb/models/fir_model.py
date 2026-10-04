class FIRGoldenModel:
    def __init__(self, coeffs, frac, width):
        self.coeffs = coeffs
        self.frac = frac
        self.width = width
        self.out_reg = 0
        self.ntaps = len(coeffs)

    def compute(self, input_history):
        """Berechnet den nächsten Zustand des Filters."""
        accu = sum([i * c for i, c in zip(input_history, self.coeffs)])
        
        # Rundung
        round_const = 1 << (self.frac - 1)
        res = (accu + round_const) >> self.frac
        
        # Sättigung (Saturation)
        max_p = (1 << (self.width - 1)) - 1
        max_n = -(1 << (self.width - 1))
        saturated = max(min(res, max_p), max_n)

        current_output = self.out_reg
        self.out_reg = saturated
        
        return current_output