# Builds "rainbow veins": glowing rainbow veins that spread out across the wall from wherever someone moves.
# They creep along branching vein paths, pulse with light, and slowly fade when everything is still.
import td

pt = op('/project1/people_trails')
base = pt.op('final_mix')


def mk(typ, name, x, y):
    n = pt.op(name) or pt.create(typ, name)
    n.nodeX = base.nodeX - 900 + x
    n.nodeY = base.nodeY - 2000 - y
    return n


def wire(n, ins):
    for cn in n.inputConnectors:
        for _ in range(4):
            if cn.connections:
                cn.disconnect()
    for i, s in enumerate(ins):
        n.inputConnectors[i].connect(s)


move = pt.op('liq_move') or pt.op('motion_soft')
small = pt.op('liq_move_small') or pt.op('dog_move_small') or pt.op('flower_move_small')

VEIN = '''
float vh(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float vnoise(vec2 p){
    vec2 i = floor(p), f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(vh(i), vh(i + vec2(1.0, 0.0)), f.x), mix(vh(i + vec2(0.0, 1.0)), vh(i + vec2(1.0, 1.0)), f.x), f.y);
}
// strength of the vein pattern at p: 1 right on a vein, 0 between veins
float veins(vec2 p, float t){
    vec2 w = vec2(vnoise(p * 1.3 + t * 0.03), vnoise(p * 1.3 + 17.0 - t * 0.03));
    p += (w - 0.5) * 0.9;
    float v = 0.0, amp = 1.0, sum = 0.0;
    for (int o = 0; o < 3; o++){
        float n = vnoise(p);
        float ridge = 1.0 - abs(n * 2.0 - 1.0);
        v += pow(ridge, 10.0 + 6.0 * float(o)) * amp;
        sum += amp;
        p = p * 2.07 + vec2(3.1, 1.7);
        amp *= 0.6;
    }
    return clamp(v / sum * 1.6, 0.0, 1.0);
}
'''

MASK = '''// where the veins are lit: movement lights them up, and the light creeps outward along the veins
out vec4 fragColor;
uniform vec4 uV;   // x = time, y = movement amount
''' + VEIN + '''
void main(){
    vec2 uv = vUV.st;
    vec2 px = 1.0 / vec2(640.0, 360.0);
    float prev = texture(sTD2DInputs[0], uv).r;
    float nb = max(max(texture(sTD2DInputs[0], uv + vec2(px.x * 1.5, 0.0)).r, texture(sTD2DInputs[0], uv - vec2(px.x * 1.5, 0.0)).r),
                   max(texture(sTD2DInputs[0], uv + vec2(0.0, px.y * 1.5)).r, texture(sTD2DInputs[0], uv - vec2(0.0, px.y * 1.5)).r));
    vec2 p = (uv - 0.5) * vec2(16.0 / 9.0, 1.0) * 5.0;
    float vv = veins(p, uV.x);
    float creep = nb * smoothstep(0.25, 0.7, vv) * 0.985;   // light only travels along the veins
    float m = texture(sTD2DInputs[1], uv).r;
    float v = max(max(prev * 0.986, creep), m);
    fragColor = TDOutputSwizzle(vec4(v, v, v, 1.0));
}
'''

SHOW = '''// draws the glowing rainbow veins, lit wherever the light has spread
out vec4 fragColor;
uniform vec4 uV;   // x = time, y = movement amount
''' + VEIN + '''
vec3 pal(float t){ return 0.5 + 0.5 * cos(6.28318 * (t + vec3(0.0, 0.33, 0.67))); }
void main(){
    vec2 uv = vUV.st;
    float t = uV.x, E = uV.y;
    vec2 p = (uv - 0.5) * vec2(16.0 / 9.0, 1.0) * 5.0;
    float vv = veins(p, t);
    float lit = texture(sTD2DInputs[0], uv).r;
    float line = smoothstep(0.35, 0.95, vv);
    float glow = smoothstep(0.1, 0.9, vv) * 0.35;
    // pulses of light flowing along the veins
    float pulse = 0.6 + 0.4 * sin(vv * 9.0 + (p.x + p.y) * 2.0 - t * (2.0 + 4.0 * E));
    vec3 c = pal(t * 0.05 + p.x * 0.18 + p.y * 0.12 + vv * 0.5);
    vec3 col = c * (line + glow) * pulse * lit * (1.0 + 0.8 * E);
    col += vec3(1.0) * pow(line, 4.0) * lit * 0.35;     // bright white cores
    col = 1.0 - exp(-col * 1.6);
    vec2 e = abs(uv - 0.5) * 2.0;
    float edge = pow(pow(e.x, 4.0) + pow(e.y, 4.0), 0.25);
    col *= smoothstep(1.02, 0.7, edge);
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
'''

SIM = '''# feeds time and the amount of movement to the rainbow veins
SRC = '@SRC@'
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
'''.replace('@SRC@', small.name if small is not None else 'liq_move_small')

seed = mk(td.constantTOP, 'rv_black', -150, 0)
seed.par.colorr = 0; seed.par.colorg = 0; seed.par.colorb = 0
seed.par.outputresolution = 'custom'; seed.par.resolutionw = 640; seed.par.resolutionh = 360
fb = mk(td.feedbackTOP, 'rv_fb', 0, 0)
wire(fb, [seed])
md = mk(td.textDAT, 'rv_mask_pixel', 150, 150)
md.text = MASK
mask = mk(td.glslTOP, 'rv_mask', 150, 0)
mask.par.pixeldat = md.name
mask.par.outputresolution = 'custom'; mask.par.resolutionw = 640; mask.par.resolutionh = 360
mask.par.format = 'r16float'
mask.par.vec0name = 'uV'
wire(mask, [fb, move])
fb.par.top = mask.name

sd = mk(td.textDAT, 'rainbow_veins_pixel', 300, 150)
sd.text = SHOW
show = mk(td.glslTOP, 'rainbow_veins', 300, 0)
show.par.pixeldat = sd.name
show.par.outputresolution = 'custom'; show.par.resolutionw = 1280; show.par.resolutionh = 720
show.par.vec0name = 'uV'
wire(show, [mask])

sim = mk(td.executeDAT, 'rv_sim', 450, 150)
sim.text = SIM
sim.par.framestart = True

for name in ('sound_dog_sim', 'flower_sim', 'dog2_sim', 'kt_sim', 'spider_sim', 'swarm_sim', 'creature_sim', 'liq_sim', 'dog_sim'):
    o = pt.op(name)
    if o is not None:
        o.par.active = False
pt.unstore('rveins')
sim.par.active = True
fb.par.resetpulse.pulse()

fm = pt.op('final_mix')
for _ in range(10):
    for cn in fm.inputConnectors:
        if cn.connections:
            cn.disconnect()
fm.inputConnectors[0].connect(show)

w = op('/project1/projector_window')
if w is not None and not w.isOpen:
    w.par.winopen.pulse()

td.project.save(td.project.folder + '/rainbow_veins.toe')
print('Rainbow veins ready. Errors:', [(n.name, n.errors()) for n in (fb, mask, show, sim) if n.errors()])
