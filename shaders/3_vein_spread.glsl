// where the veins are lit: movement lights them up, and the light creeps outward along the veins
out vec4 fragColor;
uniform vec4 uV;   // x = time, y = movement amount

float vh(vec2 p){ uvec2 q = uvec2(ivec2(floor(p + 0.5)) + ivec2(10000)); q *= uvec2(1597334673u, 3812015801u); uint n = (q.x ^ q.y) * 1597334673u; return float(n) * (1.0 / 4294967295.0); }
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

void main(){
    vec2 uv = vUV.st;
    vec2 px = 1.0 / vec2(640.0, 360.0);
    float prev = texture(sTD2DInputs[0], uv).r;
    float nb = max(max(texture(sTD2DInputs[0], uv + vec2(px.x * 1.5, 0.0)).r, texture(sTD2DInputs[0], uv - vec2(px.x * 1.5, 0.0)).r),
                   max(texture(sTD2DInputs[0], uv + vec2(0.0, px.y * 1.5)).r, texture(sTD2DInputs[0], uv - vec2(0.0, px.y * 1.5)).r));
    vec2 p = (uv - 0.5) * vec2(16.0 / 9.0, 1.0) * 5.0;
    float vv = veins(p, uV.x);
    float creep = nb * smoothstep(0.6, 0.92, vv) * 0.975;   // light only travels along the veins
    float m = texture(sTD2DInputs[1], uv).r;
    float v = max(max(prev * 0.986, creep), m);
    fragColor = TDOutputSwizzle(vec4(v, v, v, 1.0));
}
