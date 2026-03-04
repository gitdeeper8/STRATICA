PETM Case Study
===============

Paleocene-Eocene Thermal Maximum
--------------------------------

The Paleocene-Eocene Thermal Maximum (PETM, ~55.9 Ma) represents the most geologically rapid carbon cycle perturbation of the past 66 million years.

ODP Site 1209B (Shatsky Rise)
------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Parameter
     - Pre-PETM
     - Peak PETM
   * - TCI Score
     - 0.78
     - 0.31
   * - δ¹³C (‰)
     - 2.1
     - -1.5
   * - Temperature (°C)
     - 18
     - 23
   * - Carbonate Content
     - 85%
     - 45%

Key Results
-----------

.. code-block:: python

   from stratica.datasets import load_petm_site_1209b
   from stratica import StratigraphicAnalyzer

   # Load PETM data
   data = load_petm_site_1209b()
   analyzer = StratigraphicAnalyzer()
   results = analyzer.compute_tci(data)

   print(f"TCI trajectory: {results.tci_pre_petm:.2f} → "
         f"{results.tci_peak_petm:.2f} → {results.tci_post_petm:.2f}")
   print(f"Carbon release: {results.carbon_release_gtc} GtC")
   print(f"Earth System Sensitivity: {results.ess:.2f}°C per CO₂ doubling")

Scientific Significance
-----------------------

The PETM reconstruction demonstrates STRATICA's capability to:

- Detect rapid climate transitions
- Quantify carbon cycle perturbations
- Constrain Earth System Sensitivity
- Validate against independent proxy data
