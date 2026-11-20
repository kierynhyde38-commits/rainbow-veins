// movement seen by the infrared camera: compares now with a moment ago
out vec4 fragColor;
void main(){
    vec2 uv = vUV.st;
    float a = texture(sTD2DInputs[0], uv).r, b = texture(sTD2DInputs[1], uv).r;
    float avg = 0.5 * (a + b);
    float ok = step(0.0008, avg) * step(avg, 0.08);
    float m = ok * smoothstep(0.10, 0.35, abs(a - b) / (avg + 0.002));
    fragColor = TDOutputSwizzle(vec4(m, m, m, 1.0));
}
