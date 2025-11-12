"""
UI Components - 图形化界面组件
================================
提供按钮、滑块、面板等 UI 组件
"""

import pygame


class Button:
    """可点击的按钮"""
    
    def __init__(self, x, y, width, height, text, 
                 color=(70, 130, 180), hover_color=(100, 160, 210),
                 text_color=(255, 255, 255), font_size=20):
        """
        创建按钮
        
        Args:
            x, y: 按钮位置
            width, height: 按钮尺寸
            text: 按钮文字
            color: 正常颜色
            hover_color: 悬停颜色
            text_color: 文字颜色
            font_size: 字体大小
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        
        self.is_hovered = False
        self.is_pressed = False
        self.enabled = True
        
        # 圆角半径
        self.border_radius = 8
    
    def handle_event(self, event):
        """
        处理鼠标事件
        
        Returns:
            bool: 如果按钮被点击返回 True
        """
        if not self.enabled:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                self.is_pressed = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_pressed and self.is_hovered:
                self.is_pressed = False
                return True  # 按钮被点击！
            self.is_pressed = False
        
        return False
    
    def draw(self, screen):
        """绘制按钮"""
        # 选择颜色
        if not self.enabled:
            color = (100, 100, 100)
        elif self.is_pressed:
            color = tuple(max(0, c - 30) for c in self.hover_color)
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.color
        
        # 绘制按钮背景（圆角矩形）
        pygame.draw.rect(screen, color, self.rect, border_radius=self.border_radius)
        
        # 绘制边框
        border_color = (255, 255, 255, 100) if self.is_hovered else (200, 200, 200, 50)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=self.border_radius)
        
        # 绘制文字
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


class ToggleButton(Button):
    """开关按钮（可切换状态）"""
    
    def __init__(self, x, y, width, height, text, initial_state=False,
                 on_color=(50, 180, 100), off_color=(180, 50, 50), **kwargs):
        """
        创建开关按钮
        
        Args:
            x, y: 位置
            width, height: 尺寸
            text: 文字
            initial_state: 初始状态（True=ON, False=OFF）
            on_color: ON 状态颜色
            off_color: OFF 状态颜色
            **kwargs: 传递给 Button 的其他参数
        """
        # 调用父类初始化（不传递 on_color 和 off_color）
        super().__init__(x, y, width, height, text, **kwargs)
        self.is_on = initial_state
        self.on_color = on_color
        self.off_color = off_color
    
    def handle_event(self, event):
        """处理事件并切换状态"""
        if super().handle_event(event):
            self.is_on = not self.is_on
            return True
        return False
    
    def draw(self, screen):
        """绘制开关按钮"""
        # 根据状态改变颜色
        if self.is_on:
            self.color = self.on_color
            self.hover_color = tuple(min(255, c + 30) for c in self.on_color)
        else:
            self.color = self.off_color
            self.hover_color = tuple(min(255, c + 30) for c in self.off_color)
        
        super().draw(screen)
        
        # 添加状态指示器
        indicator_x = self.rect.right - 15
        indicator_y = self.rect.centery
        indicator_color = (100, 255, 100) if self.is_on else (255, 100, 100)
        pygame.draw.circle(screen, indicator_color, (indicator_x, indicator_y), 5)


class Slider:
    """滑动条"""
    
    def __init__(self, x, y, width, min_val, max_val, initial_val, label="", height=20):
        """
        创建滑动条
        
        Args:
            x, y: 位置
            width: 宽度
            min_val, max_val: 值范围
            initial_val: 初始值
            label: 标签文字
            height: 高度
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        
        self.dragging = False
        self.enabled = True
        
        # 样式
        self.bar_color = (100, 100, 100)
        self.fill_color = (70, 130, 180)
        self.handle_color = (200, 200, 200)
        self.handle_hover_color = (255, 255, 255)
        
        self.font = pygame.font.Font(None, 18)
        
        self.handle_rect = pygame.Rect(0, 0, 12, height + 6)
        self._update_handle_position()
    
    def _update_handle_position(self):
        """更新滑块手柄位置"""
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + int(ratio * self.rect.width)
        self.handle_rect.centerx = handle_x
        self.handle_rect.centery = self.rect.centery
    
    def handle_event(self, event):
        """
        处理鼠标事件
        
        Returns:
            bool: 如果值改变返回 True
        """
        if not self.enabled:
            return False
        
        changed = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # 点击滑块或滑条
                if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                    self.dragging = True
                    changed = self._update_value_from_pos(event.pos[0])
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                changed = self._update_value_from_pos(event.pos[0])
        
        return changed
    
    def _update_value_from_pos(self, mouse_x):
        """根据鼠标位置更新值"""
        # 限制在滑条范围内
        mouse_x = max(self.rect.x, min(self.rect.right, mouse_x))
        
        # 计算新值
        ratio = (mouse_x - self.rect.x) / self.rect.width
        new_value = self.min_val + ratio * (self.max_val - self.min_val)
        
        if new_value != self.value:
            self.value = new_value
            self._update_handle_position()
            return True
        return False
    
    def draw(self, screen):
        """绘制滑动条"""
        # 绘制标签
        if self.label:
            label_surf = self.font.render(f"{self.label}: {self.value:.2f}", True, (200, 200, 200))
            screen.blit(label_surf, (self.rect.x, self.rect.y - 20))
        
        # 绘制滑条背景
        pygame.draw.rect(screen, self.bar_color, self.rect, border_radius=self.rect.height // 2)
        
        # 绘制填充部分
        fill_width = int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(screen, self.fill_color, fill_rect, border_radius=self.rect.height // 2)
        
        # 绘制手柄
        handle_color = self.handle_hover_color if self.dragging else self.handle_color
        pygame.draw.circle(screen, handle_color, self.handle_rect.center, self.handle_rect.width // 2)
        pygame.draw.circle(screen, (50, 50, 50), self.handle_rect.center, self.handle_rect.width // 2, 2)


class Panel:
    """UI 面板容器"""
    
    def __init__(self, x, y, width, height, title="", 
                 bg_color=(40, 45, 50, 200), border_color=(100, 100, 100)):
        """
        创建面板
        
        Args:
            x, y: 位置
            width, height: 尺寸
            title: 标题
            bg_color: 背景颜色（支持透明度）
            border_color: 边框颜色
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.bg_color = bg_color
        self.border_color = border_color
        
        self.visible = True
        self.draggable = False
        self.dragging = False
        self.drag_offset = (0, 0)
        
        self.font = pygame.font.Font(None, 24)
        self.title_height = 30
        
        # 子组件
        self.components = []
    
    def add_component(self, component):
        """添加子组件"""
        self.components.append(component)
    
    def handle_event(self, event):
        """处理事件"""
        if not self.visible:
            return False
        
        # 处理拖拽
        if self.draggable:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    title_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.title_height)
                    if title_rect.collidepoint(event.pos):
                        self.dragging = True
                        self.drag_offset = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    self.rect.x = event.pos[0] - self.drag_offset[0]
                    self.rect.y = event.pos[1] - self.drag_offset[1]
        
        # 传递事件给子组件
        for component in self.components:
            if hasattr(component, 'handle_event'):
                if component.handle_event(event):
                    return True
        
        return False
    
    def draw(self, screen):
        """绘制面板"""
        if not self.visible:
            return
        
        # 创建半透明表面
        if len(self.bg_color) == 4:
            surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            surface.fill(self.bg_color)
            screen.blit(surface, self.rect.topleft)
        else:
            pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=10)
        
        # 绘制边框
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=10)
        
        # 绘制标题
        if self.title:
            title_surf = self.font.render(self.title, True, (255, 255, 255))
            title_rect = title_surf.get_rect(midleft=(self.rect.x + 15, self.rect.y + self.title_height // 2))
            screen.blit(title_surf, title_rect)
            
            # 标题下划线
            line_y = self.rect.y + self.title_height
            pygame.draw.line(screen, self.border_color, 
                           (self.rect.x + 10, line_y), 
                           (self.rect.right - 10, line_y), 1)
        
        # 绘制子组件
        for component in self.components:
            if hasattr(component, 'draw'):
                component.draw(screen)


class Label:
    """文本标签"""
    
    def __init__(self, x, y, text, color=(255, 255, 255), font_size=20):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, font_size)
    
    def set_text(self, text):
        """更新文本"""
        self.text = text
    
    def draw(self, screen):
        """绘制标签"""
        surf = self.font.render(str(self.text), True, self.color)
        screen.blit(surf, (self.x, self.y))


# --- 测试代码 ---
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # 创建测试组件
    panel = Panel(50, 50, 300, 400, "Test Panel", draggable=True)
    
    button1 = Button(70, 100, 120, 40, "Click Me")
    button2 = ToggleButton(210, 100, 120, 40, "Toggle", initial_state=True)
    slider = Slider(70, 180, 260, 0, 100, 50, "Value")
    label = Label(70, 250, "Click buttons or drag slider!", (200, 200, 200))
    
    panel.add_component(button1)
    panel.add_component(button2)
    panel.add_component(slider)
    panel.add_component(label)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # 处理面板事件
            panel.handle_event(event)
            
            # 检查按钮点击
            if button1.handle_event(event):
                print("Button 1 clicked!")
            
            if button2.handle_event(event):
                print(f"Toggle: {'ON' if button2.is_on else 'OFF'}")
            
            if slider.handle_event(event):
                label.set_text(f"Slider value: {slider.value:.1f}")
        
        screen.fill((30, 30, 35))
        panel.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()