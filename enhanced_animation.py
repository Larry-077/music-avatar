"""
扩展版动画系统 - 口型 + 眼睛动画
Enhanced Animation System - Mouth + Eye Animation
"""

import json, time, pygame, random
from pathlib import Path

FPS = 24
VISEME_SET = ["Sil","A","D","E","F","L","M","O","R","S","U","W"]

# 眼睛状态列表（对应你的 eyes/ 文件夹）
EYE_VARIANTS = [
    "1_center", "1_left", "1_right", "1_up", "1_down",
    "1_leftup", "1_rightup", "1_leftdown", "1_rightdown",
    "2_center", "2_left", "2_right", "2_up", "2_down",
    "2_leftup", "2_rightup", "2_leftdown", "2_rightdown",
    "3_center", "3_left", "3_right", "3_up", "3_down",
    "3_leftup", "3_rightup", "3_leftdown", "3_rightdown",
    "close", "close2", "close3"
]

# ===== 辅助函数 =====
def clamp(x, lo=0.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x

def smoothstep(p: float) -> float:
    p = clamp(p)
    return 3*p*p - 2*p*p*p

def blit_with_alpha(screen, img, pos, alpha: float):
    if img is None: return
    a = int(255 * clamp(alpha))
    if a <= 0: return
    prev = img.get_alpha()
    img.set_alpha(a)
    screen.blit(img, pos)
    img.set_alpha(prev)

# ===== 新增：眼睛动画系统 =====
class EyeRig:
    """眼睛动画控制器"""
    
    def __init__(self, eye_dir, face_width):
        """
        初始化眼睛系统
        
        Args:
            eye_dir: 眼睛图片文件夹路径
            face_width: 脸部图片宽度（用于计算默认位置）
        """
        self.eyes = {}
        eye_path = Path(eye_dir)
        
        # 加载所有眼睛贴图
        if eye_path.exists():
            for variant in EYE_VARIANTS:
                p = eye_path / f"{variant}.png"
                if p.exists():
                    self.eyes[variant] = pygame.image.load(str(p)).convert_alpha()
        
        # 如果没有找到眼睛文件，创建占位符
        if not self.eyes:
            print("⚠️  Warning: No eye images found, using placeholder")
            self.eyes["1_center"] = pygame.Surface((80, 40), pygame.SRCALPHA)
            pygame.draw.ellipse(self.eyes["1_center"], (50, 50, 50), (0, 0, 80, 40))
        
        # 默认眼睛位置和锚点
        self.eye_anchor = (face_width // 2, 200)  # 默认在脸部中上方
        
        # 动画状态
        self.current_variant = "1_center"
        self.prev_variant = "1_center"
        self.next_variant = "1_center"
        self.blending = False
        self.blend_t0 = 0.0
        self.blend_ms = 100  # 眼睛切换速度（更快）
        
        # 眨眼系统
        self.blink_enabled = True
        self.last_blink_time = 0.0
        self.next_blink_interval = random.uniform(2.0, 5.0)  # 随机眨眼间隔
        self.blink_duration = 0.15  # 眨眼持续时间
        self.is_blinking = False
        self.blink_start_time = 0.0
        
        print(f"✅ Loaded {len(self.eyes)} eye variants")
    
    def update(self, target_variant: str, now_s: float):
        """
        更新眼睛动画
        
        Args:
            target_variant: 目标眼睛状态
            now_s: 当前时间（秒）
        """
        # 处理自动眨眼
        if self.blink_enabled and not self.is_blinking:
            if now_s - self.last_blink_time >= self.next_blink_interval:
                self.start_blink(now_s)
        
        # 处理眨眼动画
        if self.is_blinking:
            if now_s - self.blink_start_time >= self.blink_duration:
                self.is_blinking = False
                self.last_blink_time = now_s
                self.next_blink_interval = random.uniform(2.0, 5.0)
            else:
                # 眨眼时强制使用闭眼状态
                if not self.blending or self.next_variant not in ["close", "close2", "close3"]:
                    self.prev_variant = self.current_variant
                    self.next_variant = random.choice(["close", "close2", "close3"])
                    self.blending = True
                    self.blend_t0 = now_s
                return
        
        # 处理正常眼睛切换
        if target_variant not in self.eyes:
            target_variant = "1_center"
        
        if target_variant != self.next_variant and not self.is_blinking:
            self.prev_variant = self.current_variant if not self.blending else self.next_variant
            self.next_variant = target_variant
            self.blending = True
            self.blend_t0 = now_s
    
    def start_blink(self, now_s: float):
        """开始眨眼"""
        self.is_blinking = True
        self.blink_start_time = now_s
    
    def draw(self, screen, face_pos, show_guides=False, now_s: float = 0.0):
        """
        绘制眼睛
        
        Args:
            screen: Pygame 屏幕
            face_pos: 脸部位置
            show_guides: 是否显示辅助线
            now_s: 当前时间
        """
        if not self.eyes:
            return
        
        if self.blending:
            # 眼睛切换动画
            dur = self.blend_ms / 1000.0
            p = clamp((now_s - self.blend_t0) / dur) if dur > 0 else 1.0
            ease = smoothstep(p)
            
            img_prev = self.eyes.get(self.prev_variant, list(self.eyes.values())[0])
            img_next = self.eyes.get(self.next_variant, list(self.eyes.values())[0])
            
            eye_pos = self._calc_eye_pos(face_pos, img_prev)
            
            # 交叉淡入淡出
            blit_with_alpha(screen, img_prev, eye_pos, 1.0 - ease)
            blit_with_alpha(screen, img_next, eye_pos, ease)
            
            if p >= 1.0:
                self.current_variant = self.next_variant
                self.blending = False
        else:
            # 静止状态
            img = self.eyes.get(self.current_variant, list(self.eyes.values())[0])
            eye_pos = self._calc_eye_pos(face_pos, img)
            screen.blit(img, eye_pos)
        
        # 绘制辅助线
        if show_guides:
            ax = face_pos[0] + self.eye_anchor[0]
            ay = face_pos[1] + self.eye_anchor[1]
            pygame.draw.line(screen, (255, 0, 0), (ax-15, ay), (ax+15, ay), 2)
            pygame.draw.line(screen, (255, 0, 0), (ax, ay-15), (ax, ay+15), 2)
    
    def _calc_eye_pos(self, face_pos, img):
        """计算眼睛绘制位置"""
        ex = face_pos[0] + self.eye_anchor[0] - img.get_width() // 2
        ey = face_pos[1] + self.eye_anchor[1] - img.get_height() // 2
        return (ex, ey)
    
    def toggle_blink(self):
        """切换自动眨眼"""
        self.blink_enabled = not self.blink_enabled
        print(f"Auto-blink: {'ON' if self.blink_enabled else 'OFF'}")


# ===== 嘴巴动画系统（保持原有代码）=====
class MouthRig:
    def __init__(self, face_png, mouth_dir, rig_json=None, blend_ms=80):
        self.face = pygame.image.load(str(face_png)).convert_alpha()
        self.mouth_anchor = (self.face.get_width()//2, 300)
        self.mouth_scale = 1.0
        self.mouth_scale_map = {}
        
        if rig_json and Path(rig_json).exists():
            try:
                data = json.loads(Path(rig_json).read_text(encoding="utf-8"))
                if "mouth_anchor" in data: self.mouth_anchor = tuple(data["mouth_anchor"])
                if "mouth_scale" in data: self.mouth_scale = float(data["mouth_scale"])
                if "mouth_scale_map" in data: self.mouth_scale_map = {k: float(v) for k,v in data["mouth_scale_map"].items()}
            except Exception: pass

        self.mouth = {}
        mdir = Path(mouth_dir)
        for v in VISEME_SET:
            p = mdir / f"{v}.png"
            if p.exists(): self.mouth[v] = pygame.image.load(str(p)).convert_alpha()
        if "Sil" not in self.mouth and self.mouth: self.mouth["Sil"] = list(self.mouth.values())[0]

        self.mid = {}
        for a in VISEME_SET:
            for b in VISEME_SET:
                if a == b: continue
                for name in (f"{a}_{b}_mid.png", f"{b}_{a}_mid.png"):
                    p = mdir / name
                    if p.exists():
                        img = pygame.image.load(str(p)).convert_alpha()
                        self.mid[(a,b)] = img; self.mid[(b,a)] = img
                        break

        self.blend_ms = max(1, int(blend_ms))
        self.active = "Sil"
        self.prev_v = "Sil"
        self.next_v = "Sil"
        self.blending = False
        self.blend_t0 = 0.0
        
        self.scale_current = 1.0
        self.scale_target = 1.0
        self.scale_prev = 1.0
        self.scale_blending = False
        self.scale_blend_t0 = 0.0
        self.scale_blend_ms = 150

    def _scale_for(self, viseme: str) -> float:
        return float(self.mouth_scale_map.get(viseme, 1.0)) * float(self.mouth_scale)

    def _mouth_pos(self, pos, img):
        mx = pos[0] + self.mouth_anchor[0] - img.get_width() // 2
        my = pos[1] + self.mouth_anchor[1] - img.get_height() // 2
        return (mx, my)

    def _scaled(self, img, scale):
        return pygame.transform.rotozoom(img, 0, scale) if abs(scale - 1.0) > 1e-6 else img

    def _update_scale_animation(self, now_s: float):
        if self.scale_blending:
            dur = self.scale_blend_ms / 1000.0
            p = clamp((now_s - self.scale_blend_t0) / dur) if dur > 0 else 1.0
            ease = smoothstep(p)
            self.scale_current = self.scale_prev + (self.scale_target - self.scale_prev) * ease
            if p >= 1.0:
                self.scale_current = self.scale_target
                self.scale_blending = False
        else:
            self.scale_current = self.scale_target

    def update_target(self, target_viseme: str, timeline_scale: float, now_s: float):
        if target_viseme not in self.mouth: target_viseme = "Sil"
        
        if target_viseme != self.next_v:
            self.prev_v = self.active if not self.blending else self.next_v
            self.next_v = target_viseme
            self.blending = True
            self.blend_t0 = now_s
        
        if abs(timeline_scale - self.scale_target) > 0.001:
            self.scale_prev = self.scale_current
            self.scale_target = timeline_scale
            self.scale_blending = True
            self.scale_blend_t0 = now_s

    def draw(self, screen, pos, show_guides=False, now_s: float = 0.0):
        screen.blit(self.face, pos)
        if not self.mouth: return

        self._update_scale_animation(now_s)

        if self.blending:
            dur = self.blend_ms / 1000.0
            p = clamp((now_s - self.blend_t0) / dur) if dur > 0 else 1.0
            ease = smoothstep(p)

            img_prev = self.mouth.get(self.prev_v, self.mouth.get("Sil"))
            img_next = self.mouth.get(self.next_v, self.mouth.get("Sil"))
            mid_img = self.mid.get((self.prev_v, self.next_v))

            s_prev = self._scale_for(self.prev_v) * self.scale_current
            s_next = self._scale_for(self.next_v) * self.scale_current

            if mid_img is not None:
                s_mid = (s_prev + s_next) / 2.0
                if p < 0.5:
                    w = smoothstep(p*2.0)
                    prev_s = self._scaled(img_prev, s_prev); mid_s = self._scaled(mid_img, s_mid)
                    blit_with_alpha(screen, prev_s, self._mouth_pos(pos, prev_s), 1.0-w)
                    blit_with_alpha(screen, mid_s, self._mouth_pos(pos, mid_s), w)
                else:
                    w = smoothstep((p-0.5)*2.0)
                    mid_s = self._scaled(mid_img, s_mid); next_s = self._scaled(img_next, s_next)
                    blit_with_alpha(screen, mid_s, self._mouth_pos(pos, mid_s), 1.0-w)
                    blit_with_alpha(screen, next_s, self._mouth_pos(pos, next_s), w)
            else:
                prev_s = self._scaled(img_prev, s_prev); next_s = self._scaled(img_next, s_next)
                blit_with_alpha(screen, prev_s, self._mouth_pos(pos, prev_s), 1.0-ease)
                blit_with_alpha(screen, next_s, self._mouth_pos(pos, next_s), ease)

            if p >= 1.0:
                self.active = self.next_v
                self.blending = False
        else:
            img = self.mouth.get(self.active, self.mouth.get("Sil"))
            s = self._scale_for(self.active) * self.scale_current
            img_s = self._scaled(img, s)
            screen.blit(img_s, self._mouth_pos(pos, img_s))

        if show_guides:
            ax = pos[0] + self.mouth_anchor[0]; ay = pos[1] + self.mouth_anchor[1]
            pygame.draw.line(screen, (0,0,255), (ax-20, ay), (ax+20, ay), 2)
            pygame.draw.line(screen, (0,0,255), (ax, ay-20), (ax, ay+20), 2)

    def save_anchor(self, rig_json):
        with open(rig_json,"w",encoding="utf-8") as f:
            json.dump({
                "mouth_anchor":[int(self.mouth_anchor[0]), int(self.mouth_anchor[1])],
                "mouth_scale": round(self.mouth_scale, 4),
                "mouth_scale_map": self.mouth_scale_map
            }, f, indent=2)


# ===== 眼睛时间线生成 =====
def generate_eye_timeline(duration_seconds=30):
    """
    生成眼睛动作时间线
    
    返回格式: [{"variant": "1_center", "start": 0.0, "duration": 2.0}, ...]
    """
    timeline = []
    current_time = 0.0
    
    # 眼睛动作模式
    eye_patterns = [
        # 正常看（中心）
        {"variants": ["1_center", "2_center", "3_center"], "weight": 0.4, "duration": (1.5, 4.0)},
        # 左右看
        {"variants": ["1_left", "2_left", "3_left"], "weight": 0.15, "duration": (0.8, 2.0)},
        {"variants": ["1_right", "2_right", "3_right"], "weight": 0.15, "duration": (0.8, 2.0)},
        # 上下看
        {"variants": ["1_up", "2_up", "3_up"], "weight": 0.1, "duration": (0.5, 1.5)},
        {"variants": ["1_down", "2_down", "3_down"], "weight": 0.1, "duration": (0.5, 1.5)},
        # 斜向
        {"variants": ["1_leftup", "1_rightup", "1_leftdown", "1_rightdown"], "weight": 0.1, "duration": (0.5, 1.2)},
    ]
    
    while current_time < duration_seconds:
        # 随机选择眼睛模式
        pattern = random.choices(
            eye_patterns,
            weights=[p["weight"] for p in eye_patterns],
            k=1
        )[0]
        
        # 随机选择该模式下的变体
        variant = random.choice(pattern["variants"])
        
        # 随机持续时间
        duration = random.uniform(*pattern["duration"])
        
        # 确保不超过总时长
        if current_time + duration > duration_seconds:
            duration = duration_seconds - current_time
        
        timeline.append({
            "variant": variant,
            "start": round(current_time, 2),
            "duration": round(duration, 2)
        })
        
        current_time += duration
    
    return timeline


def current_eye_variant(eye_timeline, t):
    """根据当前时间获取眼睛状态"""
    for seg in eye_timeline:
        if seg["start"] <= t < seg["start"] + seg["duration"]:
            return seg["variant"]
    return "1_center"


# ===== Timeline 加载函数 =====
def load_timeline(json_path):
    with open(json_path, "r", encoding="utf-8") as f: raw = json.load(f)
    tl = sorted(raw, key=lambda x: x["start"])
    out = []
    for it in tl:
        s, e, v = max(0.0, float(it["start"])), float(it["end"]), it["viseme"]
        if e <= s: continue
        if out and out[-1]["viseme"]==v and abs(out[-1]["end"]-s)<1e-6 and "scale" not in it:
            out[-1]["end"] = e
        else:
            out.append({"viseme":v,"start":s,"end":e, "scale": float(it.get("scale", 1.0))})
    return out

def current_segment(timeline, t):
    for seg in timeline:
        if seg["start"] <= t < seg["end"]:
            return seg
    return {"viseme":"Sil","scale":1.0}


# ===== 主播放函数（扩展版）=====
def play(face_png, mouth_dir, eye_dir, timeline_json, rig_json, win_size=(700,700)):
    """
    播放口型+眼睛动画
    
    Args:
        face_png: 脸部图片
        mouth_dir: 嘴巴图片文件夹
        eye_dir: 眼睛图片文件夹
        timeline_json: Viseme 时间线 JSON
        rig_json: Rig 配置文件
        win_size: 窗口大小
    """
    pygame.init()
    screen = pygame.display.set_mode(win_size)
    pygame.display.set_caption("Enhanced Animation - Mouth + Eyes")
    clock = pygame.time.Clock()
    
    # 创建 Mouth Rig
    mouth_rig = MouthRig(face_png, mouth_dir, rig_json, blend_ms=80)
    mouth_timeline = load_timeline(timeline_json)
    
    # 创建 Eye Rig
    eye_rig = EyeRig(eye_dir, mouth_rig.face.get_width())
    eye_timeline = generate_eye_timeline(duration_seconds=30)
    
    running, paused, show_guides = True, False, True
    t0 = time.perf_counter(); t_pause_accum = 0.0; t_pause_start = None; last_t = 0.0

    fx = (win_size[0] - mouth_rig.face.get_width()) // 2
    fy = (win_size[1] - mouth_rig.face.get_height()) // 2

    print("\n" + "=" * 60)
    print("CONTROLS:")
    print("=" * 60)
    print("  SPACE      - Pause/Resume")
    print("  G          - Toggle guides")
    print("  B          - Toggle auto-blink")
    print("  E          - Manual blink")
    print("  S          - Save rig config")
    print("  ARROWS     - Adjust mouth anchor")
    print("  [ ]        - Adjust mouth scale")
    print("  , .        - Adjust viseme blend speed")
    print("  - =        - Adjust scale blend speed")
    print("  ESC        - Quit")
    print("=" * 60 + "\n")
    
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_SPACE:
                    paused = not paused
                    if paused:
                        t_pause_start = time.perf_counter()
                    else:
                        if t_pause_start is not None:
                            t_pause_accum += time.perf_counter() - t_pause_start
                            t_pause_start = None
                elif ev.key == pygame.K_g:
                    show_guides = not show_guides
                elif ev.key == pygame.K_b:
                    eye_rig.toggle_blink()
                elif ev.key == pygame.K_e:
                    eye_rig.start_blink(last_t)
                    print("👁️  Manual blink triggered")
                elif ev.key == pygame.K_s:
                    mouth_rig.save_anchor(rig_json)
                    print(f"Saved rig to {rig_json}")
                elif ev.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    step = 2
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_SHIFT: step = 10
                    x, y = mouth_rig.mouth_anchor
                    if ev.key == pygame.K_LEFT: x -= step
                    if ev.key == pygame.K_RIGHT: x += step
                    if ev.key == pygame.K_UP: y -= step
                    if ev.key == pygame.K_DOWN: y += step
                    mouth_rig.mouth_anchor = (x, y)
                    print("mouth_anchor:", mouth_rig.mouth_anchor)
                elif ev.key == pygame.K_LEFTBRACKET:
                    mouth_rig.mouth_scale *= 0.98
                    print("mouth_scale:", round(mouth_rig.mouth_scale, 3))
                elif ev.key == pygame.K_RIGHTBRACKET:
                    mouth_rig.mouth_scale *= 1.02
                    print("mouth_scale:", round(mouth_rig.mouth_scale, 3))
                elif ev.key == pygame.K_COMMA:
                    mouth_rig.blend_ms = max(20, mouth_rig.blend_ms - 10)
                    print("viseme blend_ms:", mouth_rig.blend_ms)
                elif ev.key == pygame.K_PERIOD:
                    mouth_rig.blend_ms = min(300, mouth_rig.blend_ms + 10)
                    print("viseme blend_ms:", mouth_rig.blend_ms)
                elif ev.key == pygame.K_MINUS:
                    mouth_rig.scale_blend_ms = max(50, mouth_rig.scale_blend_ms - 20)
                    print("scale blend_ms:", mouth_rig.scale_blend_ms)
                elif ev.key == pygame.K_EQUALS:
                    mouth_rig.scale_blend_ms = min(500, mouth_rig.scale_blend_ms + 20)
                    print("scale blend_ms:", mouth_rig.scale_blend_ms)

        # 更新时间
        t = (time.perf_counter() - t0 - t_pause_accum) if not paused else last_t
        last_t = t

        # 更新口型
        mouth_seg = current_segment(mouth_timeline, t)
        mouth_rig.update_target(mouth_seg["viseme"], mouth_seg.get("scale", 1.0), now_s=t)

        # 更新眼睛
        eye_variant = current_eye_variant(eye_timeline, t)
        eye_rig.update(eye_variant, now_s=t)

        # 渲染
        screen.fill((255, 255, 255))
        mouth_rig.draw(screen, (fx, fy), show_guides=show_guides, now_s=t)
        eye_rig.draw(screen, (fx, fy), show_guides=show_guides, now_s=t)
        
        # 显示时间和状态
        font = pygame.font.Font(None, 24)
        time_text = font.render(f"Time: {t:.2f}s", True, (0, 0, 0))
        screen.blit(time_text, (10, 10))
        
        status_text = font.render(
            f"Mouth: {mouth_rig.active} | Eye: {eye_rig.current_variant} | Blink: {'ON' if eye_rig.blink_enabled else 'OFF'}",
            True, (100, 100, 100)
        )
        screen.blit(status_text, (10, 40))
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    # 配置文件路径
    face_png = "assets/character/face.png"
    mouth_dir = "assets/character/mouth"
    eye_dir = "assets/character/eyes"
    timeline_json = "src/viseme_timeline_30s.json"  # 使用生成的 30 秒时间线
    rig_json = "rig.json"
    
    print("=" * 60)
    print("Enhanced Animation System - Mouth + Eyes")
    print("=" * 60)
    
    play(face_png, mouth_dir, eye_dir, timeline_json, rig_json)