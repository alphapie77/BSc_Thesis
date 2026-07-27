# Notebooks are RUNNERS, not code.

A Kaggle/Colab notebook in this project contains ~4 lines:

```python
!git clone https://github.com/<you>/thesis.git && cd thesis
!pip install -q -r requirements.lock.txt
!python src/common/env_snapshot.py
!python src/cluster/pilot_trapcheck.py --config configs/s2_pilot.yaml
```

Then download `results/*.json` and commit them from your laptop.
If logic lives in a cell instead of `src/`, it cannot enter the paper.
