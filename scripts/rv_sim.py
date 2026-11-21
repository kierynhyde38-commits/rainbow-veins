# feeds time and the amount of movement to the rainbow veins
SRC = 'liq_move_small'
def onFrameStart(frame):
    b = parent()
    s = b.fetch('rveins', None) or {'t': 0.0, 'E': 0.0}
    dt = 1.0 / max(project.cookRate, 1.0)
    try:
        raw = min(max(float(b.op(SRC).numpyArray()[:, :, 0].mean()) * 25.0 - 0.03, 0.0), 1.0)
    except Exception:
        raw = 0.0
    s['E'] += (raw - s['E']) * (0.1 if raw > s['E'] else 0.02)
    s['t'] += dt
    for n in ('rv_mask', 'rainbow_veins'):
        g = b.op(n)
        g.par.vec0valuex = s['t'] % 3600.0
        g.par.vec0valuey = s['E']
    b.store('rveins', s)
    return
