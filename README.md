# Stability Analysis and Design of Local Control Schemes in Active Distribution Grids

This repository accompanies the paper:

> **"Stability Analysis and Design of Local Control Schemes in Active Distribution Grids"**  
> André Eggli, Stavros Karagiannopoulos, Saverio Bolognani, Gabriela Hug  
> *IEEE Transactions on Smart Grid*  
> [PDF](./StabilityAnalysis_TPS_2020.pdf)

## 📌 Overview

This project investigates the stability of local Volt/VAr control schemes for Distributed Energy Resources (DERs) in active distribution grids. It demonstrates that even standardized droop curves can result in unstable behaviors and proposes design guidelines for stability through incremental control and proper filter tuning.

Key contributions:
- Existence and uniqueness of equilibrium under general droop curves
- Global asymptotic stability guarantees based on closed-loop discrete-time models
- Trade-off analysis between droop steepness and convergence speed
- Case study based on the Cigre LV benchmark grid

## 📁 Repository Structure

```
.
├── README.md                             # This file
├── StabilityAnalysis_TPS_2020.pdf        # Published paper
├── code/                                 # Source code (from CodeOcean)
│   ├── cigre_19bus/
│   ├── ieee_1547/
│   ├── stability/
│   ├── test/
│   └── main.py
├── environment/                          # Environment/Docker setup
│   └── Dockerfile
├── metadata/                             # Metadata and cover image
│   ├── cover.png
│   └── metadata.yml
```

> Source code is based on the capsule hosted at [CodeOcean](https://codeocean.com/capsule/4870905/tree/v1)  
> DOI: [10.24433/CO.2842084.v1](https://doi.org/10.24433/CO.2842084.v1)

## ⚙️ Requirements

- Python 3.8+
- NumPy
- SciPy
- Matplotlib
- NetworkX

You can install dependencies via:

```bash
pip install -r requirements.txt
```

## 🚀 How to Run

Clone the repository and navigate to the root directory:

```bash
git clone https://github.com/your-username/distribution-grid-stability.git
cd distribution-grid-stability
```

To reproduce the main case study:

```bash
python code/stability/analyse.py  # or code/main.py if that's the main entry point
```

To visualize convergence under different filter parameters:

```bash
# (Update this to the correct script if needed)
python code/stability/analyse.py --convergence
```

To simulate the CIGRE LV grid scenario:

```bash
# (Update this to the correct script if needed)
python code/cigre_19bus/grid.py
```

## 📈 Results

The simulations reproduce the results from the paper, including:
- Oscillatory behavior under steep static droop curves
- Convergence to stable equilibria using low-pass filtered incremental control
- Influence of saturation and droop slope on dynamic performance

Plots will be saved in the `results/` directory.

## 📄 Citation

If you use this work, please cite:

```bibtex
@article{Eggli2021Stability,
  title={Stability Analysis and Design of Local Control Schemes in Active Distribution Grids},
  author={Eggli, André and Karagiannopoulos, Stavros and Bolognani, Saverio and Hug, Gabriela},
  journal={IEEE Transactions on Smart Grid},
  year={2021}
}
```

## 🧑‍💼 Authors

- André Eggli – ETH Zurich, Lucerne University of Applied Sciences
- Stavros Karagiannopoulos – ETH Zurich, MIT LIDS
- Saverio Bolognani – ETH Zurich
- Gabriela Hug – ETH Zurich

## 📬 Contact

For questions or collaborations, please contact:
- `karagiannopoulos [at] eeh.ee.ethz.ch`

---

*This repository is intended as a reference implementation for researchers and practitioners studying control and stability in distribution grids with high DER penetration.*