# battery-dash
interactive visualization of battery cycling data

newaredash creates a local dash interface based on data generated from a neware battery cycler (example.csv)

in order, the dash displays plots of:
1) charge/discharge capacity/energy vs. cycle
2) voltage/current vs. unix time for a hovered cycle from plot 1
3) charge/discharge capacity vs. voltage for a hovered cycle from plot 1
4) dQ/dV vs. voltage for a hovered cycle from plot 1
