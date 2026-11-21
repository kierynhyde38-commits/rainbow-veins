// draws the glowing rainbow veins, lit wherever the light has spread
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

vec3 pal(float t){ return 0.5 + 0.5 * cos(6.28318 * (t + vec3(0.0, 0.33, 0.67))); }
void main(){
    vec2 uv = vUV.st;
    float t = uV.x, E = uV.y;
    vec2 p = (uv - 0.5) * vec2(16.0 / 9.0, 1.0) * 5.0;
    float vv = veins(p, t);
    float lit = texture(sTD2DInputs[0], uv).r;
    float line = smoothstep(0.35, 0.95, vv);
    float glow = smoothstep(0.3, 0.9, vv) * 0.22;
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
