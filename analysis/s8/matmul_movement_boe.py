#!/usr/bin/env python3
"""S8 back-of-envelope: data-movement energy per MAC for n x n x n matmul
under three organizations, using the plan's energy constants.

Question (Matthew, 2026-08-05): is a fully spatially unrolled matmul that
maximally reuses data-movement wires actually worse than the RAM-as-
interconnect organization, under our energy assumptions?

Organizations
  1. systolic  - n^2 PEs, same-op reuse (folded). Each operand advances one
                 PE pitch per MAC that consumes it. Movement/MAC =
                 2 * w * e_wire * pitch. (Output-stationary; accumulator
                 traffic local, ignored - favors nobody.)
  2. unrolled  - n^3 MAC sites; tile (i,j) holds the n-deep k-reduction
                 (local tree, counted); a_ik / b_kj broadcast on shared
                 tapped buses spanning a row/column of tiles: ONE transaction
                 charges the whole bus (length n * sqrt(n * a_pe)) and serves
                 all n taps. Movement/MAC/operand = w * e_wire *
                 sqrt(a_pe) * sqrt(n)  [= n^2 elements * bus / n^3 MACs].
                 Reduction tree adds ~2 * w * e_wire * sqrt(a_pe) per MAC
                 (H-tree total wirelength ~ 2 * sqrt(n * a_pe) * sqrt(n) per
                 tile of n leaves) - included, subdominant.
  3. ram       - monolithic SRAM holds A and B (2 * n^2 words); each MAC
                 reads both operands: movement/MAC = 2 * w * e_bit(C) where
                 e_bit(C) = alpha * sqrt(C_bits), alpha calibrated to
                 Horowitz ISSCC 2014 (10 pJ / 64b @ 8 KB -> 0.156 pJ/bit at
                 65,536 bits; the 1 MB point, 1.56 pJ/bit, confirms ~sqrt(C)
                 scaling: predicted 11.3x, observed 10x).
  4. ram_blocked - Hong-Kung-optimal blocking with a local store of M words:
                 big-RAM traffic ~ 2 n^3 / sqrt(M) words total; plus 2 local
                 reads per MAC from the M-word buffer. The classical
                 hierarchy, for reference against the spatial options.

Constants (sources: plan section 2.5; cite each to its own node, these are
45 nm-era Horowitz/Keckler values used consistently)
  e_wire = 0.2 pJ/bit/mm   (Keckler et al. IEEE Micro 2011: 240 fJ @ 40nm)
  e_mac  = 4.6 pJ          (Horowitz ISSCC 2014: FP32 mult 3.7 + add 0.9)
  w      = 32 bits
  alpha  = 6.09e-4 pJ/bit per sqrt(bit)  (calibrated above)
  a_pe   = PE area - THE SHAKY ASSUMPTION. TPU v1: 65,536 8b MACs in
           ~80 mm^2 @ 28nm -> 1.2e-3 mm^2; FP32 @ 45nm taken 10x larger,
           0.012 mm^2 (pitch ~110 um). Swept 4x both ways below.

Honest limits: no leakage, no clocking, no port-conflict/serialization
model (favors the RAM), broadcast assumes full-swing tapped bus (segmenting
or low-swing signaling would cut it - favors unrolled), C-output traffic
ignored everywhere. Design-guidance numbers, not paper numbers.
"""

import math

E_WIRE = 0.2      # pJ / bit / mm
E_MAC = 4.6       # pJ
W = 32            # bits
ALPHA = 10.0 / 64.0 / math.sqrt(8 * 1024 * 8)   # pJ/bit per sqrt(bits)


def e_sram_bit(c_bits):
    return ALPHA * math.sqrt(c_bits)


def systolic(n, a_pe):
    pitch = math.sqrt(a_pe)
    return 2 * W * E_WIRE * pitch


def unrolled(n, a_pe):
    pitch = math.sqrt(a_pe)
    broadcast = 2 * W * E_WIRE * pitch * math.sqrt(n)   # A and B buses
    reduction = 2 * W * E_WIRE * pitch                  # in-tile H-tree
    return broadcast + reduction


def ram(n, a_pe):
    c_bits = 2 * n * n * W
    return 2 * W * e_sram_bit(c_bits)


def ram_blocked(n, a_pe, m_words=8 * 1024 // 4):        # 8 KB local buffer
    c_bits = 2 * n * n * W
    big = 2.0 / math.sqrt(m_words) * W * e_sram_bit(c_bits)
    local = 2 * W * e_sram_bit(m_words * W)
    return big + local


if __name__ == "__main__":
    print(f"{'n':>6} {'a_pe mm^2':>10} | {'systolic':>9} {'unrolled':>9} "
          f"{'ram':>9} {'ram_blk':>9} | pJ movement per MAC (e_mac=4.6)")
    for a_pe in (0.003, 0.012, 0.048):
        for n in (256, 1024, 4096):
            print(f"{n:>6} {a_pe:>10} | {systolic(n, a_pe):>9.2f} "
                  f"{unrolled(n, a_pe):>9.2f} {ram(n, a_pe):>9.1f} "
                  f"{ram_blocked(n, a_pe):>9.1f} |")
    print("\nscaling per MAC: systolic ~const | unrolled ~sqrt(n) | "
          "ram ~n (e_bit ~ sqrt(capacity) ~ n) | ram_blocked ~n/sqrt(M)+const")
