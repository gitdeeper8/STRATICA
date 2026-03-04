# 🪨 STRATICA Shell Completion

STRATICA provides shell completion for bash, zsh, and fish shells.

---

## Installation

### Bash
```bash
eval "$(_STRATICA_COMPLETE=bash_source stratica)"
```

Zsh

```zsh
eval "$(_STRATICA_COMPLETE=zsh_source stratica)"
```

Fish

```fish
eval (env _STRATICA_COMPLETE=fish_source stratica)
```

---

Available Commands

Core Commands

Command Description
stratica analyze Run TCI analysis on sedimentary data
stratica tci Calculate Temporal Climate Integrity Index
stratica back-cast Reconstruct missing paleoclimate data
stratica dashboard Launch interactive dashboard
stratica basins List sedimentary basins
stratica alerts Check paleoclimate anomaly alerts

Parameter Commands

```bash
stratica analyze ldr          # Lithological Deposition Rate
stratica analyze iso          # Stable Isotope Fractionation
stratica analyze mfa          # Micro-Fossil Assemblage Score
stratica analyze mag          # Magnetic Susceptibility
stratica analyze gch          # Geochemical Anomaly Index
stratica analyze pys          # Palynological Yield Score
stratica analyze vsi          # Varve Sedimentary Integrity
stratica analyze tdm          # Thermal Diffusion Model
stratica analyze cec          # Cyclostratigraphic Energy Cycle
stratica analyze tci          # Composite TCI Score
```

Basin Commands

```bash
stratica basins list                          # List all 47 basins
stratica basins show --id shatsky-rise        # Show basin details
stratica basins compare --b1 a --b2 b         # Compare two basins
stratica basins region --ocean pacific         # Filter by ocean/region
```

TCI Thresholds

```bash
stratica tci --status optimal      # TCI > 0.88
stratica tci --status good         # TCI 0.72-0.88
stratica tci --status moderate     # TCI 0.55-0.72
stratica tci --status marginal     # TCI 0.38-0.55
stratica tci --status dysfunctional # TCI < 0.38
```

Geomagnetic Monitoring

```bash
stratica mag status                # Current geomagnetic reversal status
stratica mag map --region global   # Show polarity map
stratica mag predict --depth 100m  # Predict polarity at depth
```

---

Examples

```bash
# Analyze PETM at Shatsky Rise
stratica analyze --basin shatsky-rise --site 1209B --parameters all

# Monitor isotope fractionation
stratica monitor iso --basin walvis-ridge --duration 72h

# Check active paleoclimate anomalies
stratica alerts --status anomaly --region atlantic

# List all basins with TCI > 0.80
stratica basins list --tci-min 0.80 --details

# Calculate TCI for specific dataset
stratica tci --dataset iodp-369-001 --verbose

# Run back-casting reconstruction
stratica back-cast --site 1209B --depth 150-200m --parameters iso,mfa

# Launch dashboard
stratica dashboard --port 8501

# Simulate deposition rate
stratica simulate --basin-type passive-margin --rate 5.2 --compaction athy
```

---

Tab Completion Features

Basin Name Completion

· Auto-completes from 47 sedimentary basins
· Groups by ocean/continent

Parameter Completion

· All 9 TCI parameters
· Parameter groups (lithological, geochemical, biological, physical)

Region Completion

· pacific-ocean
· atlantic-ocean
· indian-ocean
· southern-ocean
· north-america
· south-america
· europe
· africa
· asia
· australia
· antarctica

TCI Status Colors

· 🟢 OPTIMAL      (TCI > 0.88)
· 🔵 GOOD         (TCI 0.72-0.88)
· 🟡 MODERATE     (TCI 0.55-0.72)
· 🟠 MARGINAL     (TCI 0.38-0.55)
· 🔴 DYSFUNCTIONAL (TCI < 0.38)

---

Environment Variables

```bash
export STRATICA_CONFIG=~/.stratica/config.yaml
export STRATICA_DATA_DIR=/data/stratica
export STRATICA_PANGAEA_KEY=your_key_here
export STRATICA_IODP_TOKEN=your_token_here
export STRATICA_NOAA_KEY=your_key_here
```

---

Live Resources

· Dashboard: https://stratica.netlify.app
· Documentation: https://stratica.readthedocs.io
· PANGAEA: https://pangaea.de
· IODP: https://iodp.org
· NOAA Paleoclimate: https://ncei.noaa.gov/products/paleoclimatology

---

🪨 The Earth's stratigraphic column is a 4.5-billion-year journal written in rock. STRATICA decodes.
