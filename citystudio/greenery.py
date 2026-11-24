"""Garden and street trees that grow up around new houses.

Every house (a "plot") gets a few trees planted in the open ground around it
a few years after it is built. A tree is only planted on ground that is not
yet built on, and it disappears when a building or street is later put on
its own small patch of land.
"""
import math


def garden_trees(plots, occupied, cell, is_land, rng, limit=110000, max_per_plot=3):
    """Returns a list of (x, y, radius, start_year, end_year)."""
    out = []
    if not plots:
        return out
    keep = min(1.0, limit / (len(plots) * (max_per_plot + 1) / 2.0))
    for x, y, year, size in plots:
        if rng.random() > keep:
            continue
        for _ in range(rng.randint(1, max_per_plot)):
            ang = rng.uniform(0, 2 * math.pi)
            d = size + rng.uniform(4.0, 11.0)
            px, py = x + math.cos(ang) * d, y + math.sin(ang) * d
            if not is_land(px, py):
                continue
            start = year + rng.uniform(2.0, 12.0)
            taken = occupied.get((int(px // cell), int(py // cell)), 99999)
            if taken < year - 0.5:
                continue                       # something older already stands on that spot
            out.append((px, py, rng.uniform(2.6, 4.6), start, taken if taken > start else 99999))
    return out
