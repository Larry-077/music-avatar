import pygame
import math
FONT_NAME = "Helvetica"

# --- Color Palette ---
COLOR_BG = (231, 236, 239)       # Platinum
COLOR_PANEL_BG = (255, 255, 255) # White 
COLOR_SHADOW = (139, 140, 137)   # Grey Olive

# Button Colors
COLOR_BTN_NORMAL = (163, 206, 241)  # Icy Blue
COLOR_BTN_HOVER = (96, 150, 186)    # Steel Blue
COLOR_BTN_ACTIVE = (39, 76, 119)    # Dusk Blue

# Text and Lines
COLOR_TEXT_MAIN = (39, 76, 119)
COLOR_TEXT_SUB = (139, 140, 137)
COLOR_TEXT_LIGHT = (255, 255, 255)
COLOR_LINE = (96, 150, 186)

class Button:
    def __init__(self, x, y, width, height, text, font_size=18):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont(FONT_NAME, font_size, bold=True)
        
        self.is_hovered = False
        self.is_pressed = False
        self.selected = False 
        self.active = False   
        
        self.radius = 15

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_pressed and self.is_hovered:
                self.is_pressed = False
                return True
            self.is_pressed = False
        return False
    
    def draw(self, screen):
        text_col = COLOR_TEXT_MAIN
        
        if self.selected or self.active:
            color = COLOR_BTN_ACTIVE
            text_col = COLOR_TEXT_LIGHT
        elif self.is_pressed:
            color = (80, 130, 160)
            text_col = COLOR_TEXT_LIGHT
        elif self.is_hovered:
            color = COLOR_BTN_HOVER
            text_col = COLOR_TEXT_LIGHT
        else:
            color = COLOR_BTN_NORMAL
            text_col = COLOR_TEXT_MAIN

        # Draw soft shadow
        if not (self.selected or self.active):
            shadow_rect = self.rect.copy()
            shadow_rect.y += 4
            s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (*COLOR_SHADOW, 80), s.get_rect(), border_radius=self.radius)
            screen.blit(s, shadow_rect.topleft)

        # Draw button body
        pygame.draw.rect(screen, color, self.rect, border_radius=self.radius)
        
        # Highlight border if selected
        if self.selected:
            pygame.draw.rect(screen, (255, 255, 255), self.rect, 3, border_radius=self.radius)
            pygame.draw.rect(screen, COLOR_BTN_HOVER, self.rect, 1, border_radius=self.radius)

        # Draw text
        text_surf = self.font.render(self.text, True, text_col)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

class SourceButton(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signal_id = ""
        self.is_trigger = False

class EffectorButton(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.effector_id = ""
        self.is_trigger = False

class ConnectionLine:
    def __init__(self, start_btn, end_btn):
        self.start_btn = start_btn
        self.end_btn = end_btn
        self.color = COLOR_LINE
        self.width = 4

    def draw(self, screen):
        start_pos = (self.start_btn.rect.right, self.start_btn.rect.centery)
        end_pos = (self.end_btn.rect.left, self.end_btn.rect.centery)
        
        self.draw_bezier(screen, start_pos, end_pos)
        
        # Draw endpoints
        pygame.draw.circle(screen, self.color, start_pos, 6)
        pygame.draw.circle(screen, (255,255,255), start_pos, 3)
        
        pygame.draw.circle(screen, self.color, end_pos, 6)
        pygame.draw.circle(screen, (255,255,255), end_pos, 3)

    def draw_bezier(self, screen, p0, p3):
        dist = abs(p3[0] - p0[0]) / 2
        p1 = (p0[0] + dist, p0[1])
        p2 = (p3[0] - dist, p3[1])
        
        points = []
        steps = 25
        for t in range(steps + 1):
            t /= steps
            x = (1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3*p3[0]
            y = (1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3*p3[1]
            points.append((x, y))
            
        if len(points) > 1:
            pygame.draw.lines(screen, self.color, False, points, self.width)

class Label:
    def __init__(self, x, y, text, size=20, color=COLOR_TEXT_MAIN, bold=False):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont(FONT_NAME, size, bold=bold)

    def set_text(self, text):
        self.text = text

    def draw(self, screen):
        surf = self.font.render(self.text, True, self.color)
        screen.blit(surf, (self.x, self.y))

class Panel:
    def __init__(self, x, y, width, height, title=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.font = pygame.font.SysFont(FONT_NAME, 24, bold=True)

    def draw(self, screen):
        # Draw white card background
        pygame.draw.rect(screen, COLOR_PANEL_BG, self.rect, border_radius=20)
        
        # Draw light border/shadow for depth
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=20)
        
        if self.title:
            title_surf = self.font.render(self.title, True, COLOR_TEXT_MAIN)
            # Center the title
            title_rect = title_surf.get_rect(centerx=self.rect.centerx, top=self.rect.y + 25)
            screen.blit(title_surf, title_rect)
            
            # Separator line
            line_y = self.rect.y + 60
            pygame.draw.line(screen, COLOR_BTN_HOVER, 
                           (self.rect.x + 40, line_y), 
                           (self.rect.right - 40, line_y), 2)