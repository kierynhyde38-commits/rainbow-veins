// all movement in one picture: infrared movement plus the depth camera's movement
out vec4 fragColor;
uniform float uIR;   // 1 when the camera is plugged in and working, 0 when it is not
void main(){
    vec2 uv = vUV.st;
    float m = max(texture(sTD2DInputs[0], uv).r * 1.6 * uIR, max(texture(sTD2DInputs[1], uv).r - 0.15, 0.0) * 2.4);
    m = clamp(m, 0.0, 1.0);
    fragColor = TDOutputSwizzle(vec4(m, m, m, 1.0));
}
