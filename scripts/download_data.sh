#!/bin/bash
# Download reference datasets for STRATICA

echo "📥 Downloading reference datasets..."

# Create data directories
mkdir -p data/raw/sedimentary_basins
mkdir -p data/raw/iodp_cores
mkdir -p data/raw/ice_cores
mkdir -p data/reference

# Download GPTS2020
echo "Downloading Geomagnetic Polarity Time Scale..."
wget -O data/reference/GPTS2020.csv https://doi.org/10.1016/j.earscirev.2020.103249

# Download astronomical solutions
echo "Downloading La2010 astronomical solution..."
wget -O data/reference/La2010_astronomical.csv https://doi.org/10.1051/0004-6361/200936019

echo "✅ Download complete!"
