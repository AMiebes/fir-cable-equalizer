`timescale 1ns / 1ps

module FIR #(
    parameter NTAPS = 8,
    parameter IN_WIDTH = 16,
    parameter COEFF_WIDTH = 16,
    parameter FRAC_WIDTH = 14 // Anteil der Nachkommastellen in COEFF
)(
    input  wire clk,
    input  wire rst_n,
    input  wire signed [IN_WIDTH-1:0] signal_in,
    input  wire signed [(NTAPS*COEFF_WIDTH)-1:0] coeffs_flat,
    output reg signed [IN_WIDTH-1:0] signal_out
);

    // Internes Bit-Wachstum: Produkt (IN+COEFF) + Summen-Bit (log2 NTAPS)
    localparam ACCU_WIDTH = IN_WIDTH + COEFF_WIDTH + $clog2(NTAPS);
    localparam SHIFT_AMOUNT = FRAC_WIDTH;
    
    // Definition der Grenzwerte für Saturation (auf ACCU_WIDTH erweitert für sauberen Vergleich)
    localparam signed [ACCU_WIDTH-1:0] MAX_POS = $signed({ {(ACCU_WIDTH-IN_WIDTH+1){1'b0}}, {(IN_WIDTH-1){1'b1}} });
    localparam signed [ACCU_WIDTH-1:0] MAX_NEG = $signed({ {(ACCU_WIDTH-IN_WIDTH+1){1'b1}}, {(IN_WIDTH-1){1'b0}} });

    reg signed [ACCU_WIDTH-1:0] pipeline_reg [0:NTAPS-1];
    wire signed [COEFF_WIDTH-1:0] coeff [0:NTAPS-1];

    // Entpacken der Koeffizienten aus dem flachen Vektor
    genvar i;
    generate
        for (i = 0; i < NTAPS; i = i + 1) begin : coeff_gen
            assign coeff[i] = coeffs_flat[i*COEFF_WIDTH +: COEFF_WIDTH];
        end
    endgenerate

    // Die transponierte FIR-Struktur
    integer j;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (j = 0; j < NTAPS; j = j + 1) begin
                pipeline_reg[j] <= {ACCU_WIDTH{1'b0}};
            end
        end else begin
            // Letzte Stufe der Kette
            pipeline_reg[NTAPS-1] <= signal_in * coeff[NTAPS-1];
            
            // Rekursive Berechnung: y_i = (x * h_i) + y_{i+1}
            for (j = NTAPS-2; j >= 0; j = j - 1) begin
                pipeline_reg[j] <= (signal_in * coeff[j]) + pipeline_reg[j+1];
            end
        end
    end

// --- Output Assignment (Truncation) ---
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            signal_out <= {IN_WIDTH{1'b0}};
        end else begin
            // Arithmetic right shift (Truncation)
            signal_out <= pipeline_reg[0] >>> SHIFT_AMOUNT;
        end
    end

endmodule