# FIR Cable Equalizer

A parameterized Verilog implementation of a **transposed FIR Filter** designed to compensate for high-frequency signal attenuation, dispersion, and line reflection effects in transmission cables.

---

## 📌 Application Scope

High-speed physical transmission lines act as low-pass filters:
* **Attenuation & Dispersion:** High-frequency components suffer higher losses over distance, leading to Inter-Symbol Interference (ISI).
* **Echoes & Reflections:** Impedance mismatches along the cable generate signal reflections.

This digital FIR equalizer serves as an inverse filter to flatten the frequency response and restore signal integrity for cable communication links.

---

## 🏗 Hardware Architecture

The module (`hdl/FIR.v`) uses a transposed FIR topology to maximize performance:

* **Transposed Structure:** Replaces long adder chains with pipelined registers, enabling high clock frequencies.
* **Fully Parameterized:** Configurable bit-widths for input data (`IN_WIDTH`), coefficients (`COEFF_WIDTH`), and fixed-point fraction alignment (`FRAC_WIDTH`).
* **Bit-Growth Internal Accumulation:** Internal registers automatically scale with $N_{\text{taps}}$ to prevent intermediate bit-overflow during multiply-accumulate (MAC) operations.
* **Bit-Exact Rounding:** Implements symmetric round-to-nearest logic via arithmetic offset (`1 << (SHIFT_AMOUNT - 1)`) prior to bit-shifting.
* **Overflow Protection (Saturation):** Output logic automatically clamps signals to `MAX_POS` or `MAX_NEG` upon arithmetic overflow/underflow instead of severe signal wrapping.
* **Flattened Coefficient Interface:** Vectors are passed via a single flat input bus (`coeffs_flat`) for simplified top-level routing.