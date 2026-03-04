Quick Start Guide
=================

This guide will help you get started with STRATICA in just a few minutes.

Basic Workflow
--------------

Here's a simple example to analyze stratigraphic data:

.. code-block:: python

   from stratica import StratigraphicAnalyzer
   import numpy as np

   # Initialize analyzer
   analyzer = StratigraphicAnalyzer()

   # Load sample data
   data = analyzer.load_core('path/to/your/core_data.csv')

   # Compute TCI
   results = analyzer.compute_tci(data)

   # View results
   print(f"TCI Score: {results.tci_composite:.3f}")
   print(f"Classification: {results.classification}")

Command Line Interface
----------------------

STRATICA also provides a command-line interface:

.. code-block:: bash

   # Analyze a single core
   stratica process --input data/core.csv --output results/

   # Launch the interactive dashboard
   stratica dashboard --port 8501

   # Run validation tests
   stratica validate --dataset validation/

Jupyter Notebooks
-----------------

Explore the included Jupyter notebooks:

.. code-block:: bash

   jupyter notebook notebooks/01_getting_started.ipynb

Sample Data
-----------

Test STRATICA with sample data from the repository:

.. code-block:: python

   from stratica import StratigraphicAnalyzer
   from stratica.datasets import load_petm_sample

   # Load PETM sample data
   data = load_petm_sample()
   analyzer = StratigraphicAnalyzer()
   results = analyzer.compute_tci(data)
   print(results.tci_composite)
