---
title: Hello, world — starting this blog
date: 2026-06-18
summary: A short first post on why I'm starting a research blog and what to expect here.
lang: en
---

Welcome! This is the first post on my new research blog. I plan to write here about
**LiDAR sensing**, autonomous driving perception, and sensor security — the topics I work on
day to day.

## What to expect

- Notes from papers I'm reading and writing
- Practical write-ups on LiDAR data, point clouds, and full-waveform processing
- Short experiments and things I wish I'd known earlier

## A quick code example

Here is a tiny snippet to show that code blocks render:

```python
import numpy as np

def to_spherical(points: np.ndarray) -> np.ndarray:
    x, y, z = points[:, 0], points[:, 1], points[:, 2]
    r = np.sqrt(x**2 + y**2 + z**2)
    azimuth = np.arctan2(y, x)
    elevation = np.arcsin(z / np.clip(r, 1e-9, None))
    return np.stack([r, azimuth, elevation], axis=-1)
```

> The goal isn't polished tutorials — it's a running lab notebook in public.

Thanks for reading. More soon.
