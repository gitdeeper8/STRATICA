.. STRATICA documentation master file

STRATICA Documentation
======================

Welcome to **STRATICA** — Stratigraphic Pattern Recognition & Paleoclimatic Temporal Reconstruction.

A Physics-Informed AI Framework for Deep-Time Earth System Reconstruction, Stratigraphic Layer Intelligence, and Paleoclimatic Cycle Decoding via the Temporal Climate Integrity Index (TCI).

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.18851076.svg
   :target: https://doi.org/10.5281/zenodo.18851076

.. image:: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg
   :target: https://creativecommons.org/licenses/by/4.0/

.. image:: https://img.shields.io/badge/python-3.10%2B-blue
   :target: https://www.python.org/downloads/

Quick Links
-----------

- **GitHub Repository:** https://github.com/gitdeeper8/STRATICA
- **GitLab Mirror:** https://gitlab.com/gitdeeper8/STRATICA
- **Live Dashboard:** https://stratica.netlify.app
- **PyPI Package:** https://pypi.org/project/stratica/
- **Research Paper DOI:** 10.5281/zenodo.18851076

What is STRATICA?
-----------------

STRATICA presents the first unified, multi-parameter Physics-Informed AI framework for the systematic reconstruction, computational modeling, and temporal interpretation of Earth's stratigraphic record across **4.5 billion years**.

The framework integrates **nine analytically independent stratigraphic and geochemical parameters** into a single **Temporal Climate Integrity Index (TCI)** , achieving paleoclimate classification accuracy of **96.2%** across 47 sedimentary basins on 6 continents.

Key Features
~~~~~~~~~~~~

✓ **Temporal Back-Casting** — Transformer-LSTM hybrid architectures reconstruct missing geological records  
✓ **Nine-Parameter TCI** — Integrated composite metric balancing all paleoclimate proxy types  
✓ **Physics-Informed Neural Network** — Hard constraints enforce stratigraphic, thermodynamic, and orbital coherence  
✓ **Extensive Validation** — 47 sedimentary basins, 12 IODP drill cores, 8 ice core records (800,000 years)  
✓ **Real-Time Dashboard** — Interactive paleoclimate exploration and analysis platform  

Performance at a Glance
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 20 20 20

   * - Metric
     - STRATICA
     - Previous
     - Improvement
   * - TCI Classification Accuracy
     - 96.2%
     - 81.4%
     - +14.8 pp
   * - δ¹⁸O Back-cast RMSD
     - 0.0018 ‰
     - 0.0063 ‰
     - 71% reduction
   * - Milankovitch Cycle Detection
     - ±1,200 yr
     - ±8,500 yr
     - 7x improvement
   * - Magnetostratigraphy Age Accuracy
     - ±3.4%
     - ±11.2%
     - 3.3x improvement
   * - Microfossil Classification (CNN)
     - 93.4%
     - 71.8%
     - +21.6 pp
   * - Drill Core Processing Speed
     - 4 hrs/200m
     - 6-12 months
     - 500-2000x faster

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quick_start

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/core
   api/parameters

.. toctree::
   :maxdepth: 2
   :caption: Case Studies

   case_studies/petm

.. toctree::
   :maxdepth: 1
   :caption: Reference

   glossary
   contact

The Nine TCI Parameters
-----------------------

.. list-table::
   :header-rows: 1
   :widths: 15 10 10 65

   * - Parameter
     - Symbol
     - Weight
     - Description
   * - Lithological Deposition Rate
     - LDR
     - 20%
     - Rate of sediment accumulation as function of basin subsidence and compaction
   * - Stable Isotope Fractionation
     - ISO
     - 15%
     - δ¹⁸O / δ¹³C ratios encoding palaeotemperature and carbon cycle state
   * - Micro-Fossil Assemblage
     - MFA
     - 12%
     - AI-classified foraminifera, nannofossils, and palynomorphs
   * - Magnetic Susceptibility
     - MAG
     - 11%
     - Ferrimagnetic mineral content recording geomagnetic reversals
   * - Geochemical Anomaly Index
     - GCH
     - 10%
     - Trace element signatures detecting bolide impacts and anoxic events
   * - Palynological Yield Score
     - PYS
     - 9%
     - Pollen and spore assemblage diversity encoding vegetation history
   * - Varve Sedimentary Integrity
     - VSI
     - 8%
     - Annual lamination preservation in lacustrine sediments
   * - Thermal Diffusion Model
     - TDM
     - 8%
     - Subsurface heat flow modeling quantifying burial depth and maturity
   * - Cyclostratigraphic Energy Cycle
     - CEC
     - 7%
     - Spectral power at Milankovitch orbital periods for astronomical calibration

Citation
--------

If you use STRATICA in your research, please cite:

**BibTeX:**

.. code-block:: bibtex

   @software{baladi2026stratica,
     author = {Baladi, Samir},
     title = {STRATICA: Stratigraphic Pattern Recognition & Paleoclimatic Temporal Reconstruction},
     year = {2026},
     publisher = {Zenodo},
     doi = {10.5281/zenodo.18851076},
     url = {https://github.com/gitdeeper8/STRATICA}
   }

**APA:**

.. code-block:: text

   Baladi, S. (2026). STRATICA: Stratigraphic Pattern Recognition & Paleoclimatic Temporal Reconstruction [Software]. Zenodo. https://doi.org/10.5281/zenodo.18851076

License
-------

This project is licensed under the **Creative Commons Attribution 4.0 International License (CC-BY-4.0)**.

See `LICENSE <https://creativecommons.org/licenses/by/4.0/>`_ for details.

Contact & Support
-----------------

**Principal Investigator:** Samir Baladi

- Email: gitdeeper@gmail.com
- ORCID: `0009-0003-8903-0029 <https://orcid.org/0009-0003-8903-0029>`_
- Phone: +16142642074

**Affiliation:** Ronin Institute for Independent Scholarship  
**Division:** Geological Deep-Time & Geospatial Intelligence Division

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. raw:: html

   <div class="footer-section">
     <p style="text-align: center; margin-top: 40px; color: #666;">
       <strong>In the layers of the Earth, time is not lost — it is stored.</strong><br>
       <em>Every stratum is a sentence; every basin is a book.</em><br>
       <strong>STRATICA is the language in which that book was always waiting to be read.</strong>
     </p>
   </div>
