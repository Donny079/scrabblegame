"""
🎮 Word Scrabble Arena - Enhanced Edition
A modern, visually appealing word puzzle game with smooth animations and intuitive UI.

Features:
- Modern menu system with settings
- Animated transitions and particle effects
- Score tracking with accuracy statistics
- Interactive buttons with hover effects
- Responsive UI elements
- Progress tracking and difficulty levels
- Interactive letter tiles with animations
- Smooth fade transitions between screens
- Blinking text cursor for input
"""

import pygame
import random
import time
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional, Callable

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

# --- Window Settings ---
WIDTH, HEIGHT = 1000, 700
GAME_TITLE = "🎮 Word Scrabble Arena 🎮"
FPS = 60

# --- Modern Color Palette ---
C_PRIMARY = (41, 128, 185)      # Soft blue
C_SECONDARY = (52, 152, 219)    # Brighter blue
C_ACCENT = (230, 126, 34)       # Orange
C_SUCCESS = (46, 204, 113)      # Green
C_ERROR = (231, 76, 60)         # Red
C_WHITE = (255, 255, 255)
C_BLACK = (20, 20, 30)          # Dark navy
C_LIGHT_BG = (240, 240, 245)    # Light background
C_DARK_BG = (30, 40, 60)        # Dark background
C_SHADOW = (0, 0, 0, 50)        # Transparent shadow
C_TEXT_PRIMARY = (50, 50, 70)
C_BORDER = (100, 120, 150)
C_DISABLED = (150, 150, 160)

# --- Game States ---
STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER = "GAME_OVER"
STATE_PAUSED = "PAUSED"
STATE_SETTINGS = "SETTINGS"

# --- Difficulty Levels ---
DIFFICULTY_EASY = "EASY"
DIFFICULTY_MEDIUM = "MEDIUM"
DIFFICULTY_HARD = "HARD"

# --- Game Data ---
WORDS_EASY = [
    "python", "coding", "computer", "learning", "education",
    "keyboard", "science", "function", "module", "software"
]
WORDS_MEDIUM = [
    "algorithm", "database", "interface", "framework", "protocol",
    "variable", "package", "development", "internet", "network"
]
WORDS_HARD = [
    "cryptocurrency", "synchronization", "architecture", "optimization",
    "authentication", "virtualization", "parallelization", "segmentation",
    "compression", "decompression"
]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def draw_rounded_rect(surface, rect, color, border_radius):
    """
    Draw a rectangle with rounded corners.
    We just pass the rect, color and radius
    """
    pygame.draw.rect(surface, color, rect, border_radius=border_radius)

def draw_text(surface: pygame.Surface, text: str, font: pygame.font.Font,
              color: Tuple[int, int, int], pos: Tuple[int, int],
              align: str = "topleft"):
    """
    Flexible text drawing function with alignment.
    Align can be: 'topleft', 'center', 'topright', 'midright', etc.
    """
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    setattr(text_rect, align, pos) # e.g., text_rect.center = pos
    surface.blit(text_surface, text_rect)


# ============================================================================
# UTILITY CLASSES & DATA STRUCTURES
# ============================================================================

@dataclass
class GameStats:
    """Track game statistics"""
    total_words: int = 0
    correct_answers: int = 0
    incorrect_answers: int = 0
    current_streak: int = 0
    best_streak: int = 0
    
    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage"""
        if self.total_words == 0:
            return 0.0
        return (self.correct_answers / self.total_words) * 100

class Button:
    """Interactive button with hover effects"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str, font: pygame.font.Font,
                 color: Tuple[int, int, int],
                 hover_color: Tuple[int, int, int],
                 action: Optional[Callable] = None,
                 text_color: Tuple[int, int, int] = C_WHITE,
                 border_radius: int = 12):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action
        self.border_radius = border_radius
        self.is_hovered = False
        
    def update(self, mouse_pos: Tuple[int, int]):
        """Update button state (hover detection)"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def draw(self, surface: pygame.Surface):
        """Draw button with modern styling"""
        current_color = self.hover_color if self.is_hovered else self.color
        
        # Draw rounded rectangle
        draw_rounded_rect(surface, self.rect, current_color, self.border_radius)
        
        # Draw text
        draw_text(surface, self.text, self.font, self.text_color,
                  self.rect.center, align="center")
        
    def is_clicked(self) -> bool:
        """Check if button was clicked"""
        return self.is_hovered
    
    def on_click(self):
        """Execute button action"""
        if self.action:
            # Play a click sound if you have one
            self.action()

class ParticleEffect:
    """Simple particle effect for animations"""
    
    def __init__(self, x: float, y: float, vx: float, vy: float,
                 lifetime: int, color: Tuple[int, int, int], size: int = 5):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.age = 0
        self.color = color
        self.size = size
        
    def update(self):
        """Update particle position and age"""
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Simple gravity
        self.age += 1
        
    def draw(self, surface: pygame.Surface):
        """Draw particle with fade effect"""
        alpha = max(0, 255 * (1 - self.age / self.lifetime))
        if alpha > 0:
            # Create a temporary surface for alpha drawing
            part_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(part_surf, self.color, (self.size, self.size), self.size)
            part_surf.set_alpha(alpha)
            surface.blit(part_surf, (int(self.x) - self.size, int(self.y) - self.size))
    
    def is_alive(self) -> bool:
        """Check if particle is still alive"""
        return self.age < self.lifetime

class LetterTile:
    """A single letter tile for the scrambled word"""
    
    def __init__(self, char: str, x: int, y: int, font: pygame.font.Font):
        self.char = char.upper()
        self.x = x
        self.y = y
        self.font = font
        self.color = C_WHITE
        self.bg_color = C_PRIMARY
        
        # Animation properties
        self.y_offset = 0
        self.y_velocity = 0
        self.scale = 1.0
        self.target_scale = 1.0
        
        # Calculate size based on font
        self.size = self.font.size(self.char)[0] + 20
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

    def update(self):
        """Update animation state"""
        # Gravity for jump
        if self.y_velocity != 0 or self.y_offset > 0:
            self.y_offset += self.y_velocity
            self.y_velocity += 0.5 # Gravity
            if self.y_offset >= 0:
                self.y_offset = 0
                self.y_velocity = 0
        
        # Scale interpolation (for popping in)
        if self.scale != self.target_scale:
            self.scale += (self.target_scale - self.scale) * 0.2

    def draw(self, surface: pygame.Surface):
        """Draw the tile"""
        # Calculate rect based on animation
        anim_y = self.y + self.y_offset
        center_x, center_y = self.x + self.size // 2, anim_y + self.size // 2
        
        # Draw tile background
        draw_rounded_rect(surface, pygame.Rect(self.x, anim_y, self.size, self.size),
                          self.bg_color, border_radius=8)
        
        # Draw shadow
        draw_rounded_rect(surface, pygame.Rect(self.x + 2, anim_y + 2, self.size, self.size),
                          C_SHADOW, border_radius=8)
        
        # Draw letter
        draw_text(surface, self.char, self.font, self.color,
                  (center_x, center_y), align="center")

    def jump(self):
        """Trigger a jump animation"""
        self.y_velocity = -6 # Initial upward velocity

class Transition:
    """Manages fade-in/fade-out transitions"""
    
    def __init__(self, speed: int = 15):
        self.alpha = 0
        self.speed = speed
        self.fading_out = False
        self.fading_in = False
        self.callback: Optional[Callable] = None
        self.overlay = pygame.Surface((WIDTH, HEIGHT))
        self.overlay.fill(C_DARK_BG)

    def start_fade_out(self, callback: Optional[Callable] = None):
        """Start fading out to black"""
        self.fading_out = True
        self.fading_in = False
        self.callback = callback

    def start_fade_in(self):
        """Start fading in from black"""
        self.fading_in = True
        self.fading_out = False
        self.alpha = 255

    def update(self):
        if self.fading_out:
            self.alpha += self.speed
            if self.alpha >= 255:
                self.alpha = 255
                self.fading_out = False
                if self.callback:
                    self.callback()
                self.start_fade_in() # Automatically fade back in
        
        elif self.fading_in:
            self.alpha -= self.speed
            if self.alpha <= 0:
                self.alpha = 0
                self.fading_in = False

    def draw(self, surface: pygame.Surface):
        if self.alpha > 0:
            self.overlay.set_alpha(self.alpha)
            surface.blit(self.overlay, (0, 0))

    @property
    def is_active(self) -> bool:
        return self.fading_in or self.fading_out

# ============================================================================
# MAIN GAME CLASS
# ============================================================================

class WordScrabbleGame:
    """
    Enhanced Word Scrabble Game with modern UI/UX.
    Manages game logic, rendering, and user interaction.
    """
    
    def __init__(self):
        """Initialize the game"""
        pygame.init()
        
        # --- Window Setup ---
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # --- Load Assets ---
        self._load_assets()
        
        # --- Fonts (Modern sans-serif style) ---
        self.font_title = pygame.font.Font(None, 72)      # Large titles
        self.font_heading = pygame.font.Font(None, 48)    # Headings
        self.font_large = pygame.font.Font(None, 40)      # Large text
        self.font_medium = pygame.font.Font(None, 32)     # Medium text
        self.font_small = pygame.font.Font(None, 24)      # Small text
        self.font_tiny = pygame.font.Font(None, 18)       # Tiny text
        
        # --- Game State ---
        self.state = STATE_MENU
        self.difficulty = DIFFICULTY_MEDIUM
        self.score = 0
        self.current_word_index = 0
        self.user_input = ""
        self.current_word = ""
        self.words_list: List[str] = []
        
        # --- Statistics ---
        self.stats = GameStats()
        
        # --- UI Elements ---
        self.buttons: List[Button] = []
        self.particles: List[ParticleEffect] = []
        self.letter_tiles: List[LetterTile] = []
        self.transition = Transition(speed=20)
        
        # --- Animation Variables ---
        self.input_shake = 0
        self.animation_timer = 0
        
        # --- Setup Menu ---
        self.show_menu() # Start by showing the menu
        self.transition.start_fade_in() # Initial fade-in
    
    def _load_assets(self):
        """Load background image or create a gradient background"""
        try:
            bg_image = pygame.image.load("BG.jpeg")
            self.bg = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
        except (pygame.error, FileNotFoundError):
            # Create a gradient-like background
            self.bg = pygame.Surface((WIDTH, HEIGHT))
            self.bg.fill(C_DARK_BG)
    
    def _setup_menu_buttons(self):
        """Setup main menu buttons"""
        self.buttons.clear() # <--- Crucial fix: Clear buttons before adding new ones
        button_width, button_height = 280, 60
        center_x = WIDTH // 2 - button_width // 2
        
        self.buttons.append(Button(
            center_x, 250, button_width, button_height,
            "Start Game", self.font_large, C_PRIMARY, C_SECONDARY,
            action=lambda: self.transition.start_fade_out(self.show_settings) # show_settings now leads to difficulty
        ))
        
        self.buttons.append(Button(
            center_x, 340, button_width, button_height,
            "Settings", self.font_large, C_ACCENT, (250, 150, 60), # Re-added Settings button
            action=lambda: self.transition.start_fade_out(self.show_settings) # Settings leads to difficulty as well
        ))

        self.buttons.append(Button(
            center_x, 430, button_width, button_height, # Adjusted position for Exit Game
            "Exit Game", self.font_large, C_ERROR, (255, 100, 80),
            action=self.quit_game
        ))
    
    def _setup_difficulty_buttons(self):
        """Setup difficulty selection buttons"""
        self.buttons.clear() # <--- ENSURE THIS IS CALLED FIRST
        button_width, button_height = 220, 55
        start_y = 250
        spacing = 90
        
        difficulties = [
            (DIFFICULTY_EASY, "Easy"),
            (DIFFICULTY_MEDIUM, "Medium"),
            (DIFFICULTY_HARD, "Hard")
        ]
        
        for i, (diff, label) in enumerate(difficulties):
            self.buttons.append(Button(
                WIDTH // 2 - button_width // 2, start_y + i * spacing,
                button_width, button_height,
                label, self.font_medium, C_PRIMARY, C_SECONDARY,
                action=lambda d=diff: self.transition.start_fade_out(lambda: self.set_difficulty(d))
            ))
        
        self.buttons.append(Button(
            WIDTH // 2 - button_width // 2, start_y + (3 * spacing) + 20, # Added extra spacing
            button_width, button_height,
            "Back", self.font_medium, C_ERROR, (255, 100, 80),
            action=lambda: self.transition.start_fade_out(self.show_menu)
        ))
    
    def _setup_game_over_buttons(self):
        """Setup game over buttons"""
        self.buttons.clear() # <--- ENSURE THIS IS CALLED FIRST
        button_width, button_height = 280, 55
        
        # Play Again
        self.buttons.append(Button(
            WIDTH // 2 - button_width // 2, HEIGHT // 2 + 180,
            button_width, button_height,
            "Play Again", self.font_medium, C_SUCCESS, (76, 234, 143),
            action=lambda: self.transition.start_fade_out(self.show_settings) # Go to diff select
        ))
        
        # Main Menu
        self.buttons.append(Button(
            WIDTH // 2 - button_width // 2, HEIGHT // 2 + 250,
            button_width, button_height,
            "Main Menu", self.font_medium, C_PRIMARY, C_SECONDARY,
            action=lambda: self.transition.start_fade_out(self.show_menu)
        ))

    def set_difficulty(self, difficulty: str):
        """Set game difficulty and start"""
        self.difficulty = difficulty
        self.state = STATE_PLAYING
        self._init_game()
    
    def _init_game(self):
        """Initialize a new game"""
        self.buttons.clear() # No buttons in playing state
        
        if self.difficulty == DIFFICULTY_EASY:
            self.words_list = WORDS_EASY[:]
        elif self.difficulty == DIFFICULTY_MEDIUM:
            self.words_list = WORDS_MEDIUM[:]
        else: # HARD
            self.words_list = WORDS_HARD[:]
        
        random.shuffle(self.words_list)
        self.current_word_index = 0
        self.user_input = ""
        self.score = 0
        self.stats = GameStats()
        self.stats.total_words = len(self.words_list)
        
        self.next_word()
    
    def start_game(self):
        """Show difficulty selection"""
        self.state = STATE_SETTINGS
        self._setup_difficulty_buttons()
    
    def show_settings(self):
        """Show settings screen"""
        self.state = STATE_SETTINGS
        self._setup_difficulty_buttons()
    
    def show_menu(self):
        """Return to main menu"""
        self.state = STATE_MENU
        self._setup_menu_buttons()
    
    def quit_game(self):
        """Quit the game"""
        self.running = False
    
    def next_word(self):
        """Move to next word or trigger game over"""
        if self.current_word_index >= len(self.words_list):
            self.state = STATE_GAME_OVER
            self._setup_game_over_buttons()
            return
        
        self.current_word = self.words_list[self.current_word_index]
        self.scrambled_word = self.scramble_word(self.current_word)
        self.user_input = ""
        self.current_word_index += 1
        self.input_shake = 0
        
        # Create new letter tiles
        self.letter_tiles.clear()
        total_width = sum(self.font_heading.size(c.upper())[0] + 20 for c in self.scrambled_word)
        start_x = (WIDTH - total_width) // 2
        
        for char in self.scrambled_word:
            tile_font_size = self.font_heading.size(char.upper())[0] + 20
            tile = LetterTile(char, start_x, HEIGHT // 2 - 100, self.font_heading)
            self.letter_tiles.append(tile)
            start_x += tile.size + 10 # 10px spacing
    
    def scramble_word(self, word: str) -> str:
        """Scramble a word, ensuring it's different from original"""
        word_list = list(word)
        scrambled = list(word)
        while ''.join(scrambled) == word and len(word) > 1:
            random.shuffle(scrambled)
        return ''.join(scrambled)
    
    def check_answer(self):
        """Check user answer and provide feedback"""
        if self.user_input.lower() == self.current_word.lower():
            self.score += 1
            self.stats.correct_answers += 1
            self.stats.current_streak += 1
            self.stats.best_streak = max(self.stats.best_streak, self.stats.current_streak)
            self.create_success_particles()
            self.animate_correct()
        else:
            self.stats.incorrect_answers += 1
            self.stats.current_streak = 0
            self.input_shake = 15 # Stronger shake
            self.create_error_particles()
            self.animate_error()
        
        # Move to next word (after a short delay for animations to be seen)
        # We can use the animation_timer for this
        
    def create_success_particles(self):
        """Create particle effects for correct answer"""
        for _ in range(25):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            self.particles.append(ParticleEffect(
                WIDTH // 2, HEIGHT // 2, vx, vy,
                lifetime=50, color=C_SUCCESS, size=random.randint(3, 6)
            ))
    
    def create_error_particles(self):
        """Create particle effects for wrong answer"""
        for _ in range(15):
            angle = random.uniform(0.75 * math.pi, 1.25 * math.pi) # Downward burst
            speed = random.uniform(1, 4)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            self.particles.append(ParticleEffect(
                WIDTH // 2, HEIGHT // 2 + 60, vx, vy,
                lifetime=40, color=C_ERROR, size=random.randint(2, 4)
            ))
    
    def animate_correct(self):
        """Animation for correct answer"""
        self.animation_timer = 60 # Set timer for 1 second
        for tile in self.letter_tiles:
            tile.jump()
            tile.bg_color = C_SUCCESS
    
    def animate_error(self):
        """Animation for wrong answer"""
        self.animation_timer = 40 # Shorter timer
        for tile in self.letter_tiles:
            tile.bg_color = C_ERROR
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()
    
    def handle_events(self):
        """Handle user input"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hover states only if not transitioning
        if not self.transition.is_active:
            for btn in self.buttons:
                btn.update(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Block input during transitions
            if self.transition.is_active:
                continue
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_PLAYING:
                        self.transition.start_fade_out(self.show_menu)
                    elif self.state == STATE_SETTINGS:
                        self.transition.start_fade_out(self.show_menu)
                    elif self.state == STATE_GAME_OVER:
                        self.transition.start_fade_out(self.show_menu)
                    elif self.state == STATE_MENU:
                        self.quit_game()
                
                elif self.state == STATE_PLAYING:
                    if event.key == pygame.K_RETURN:
                        if self.user_input and self.animation_timer == 0:
                            self.check_answer()
                    elif event.key == pygame.K_BACKSPACE:
                        self.user_input = self.user_input[:-1]
                    elif event.unicode.isalpha():
                        self.user_input += event.unicode.lower()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    for btn in self.buttons:
                        if btn.is_clicked():
                            btn.on_click()
    
    def update(self):
        """Update game state"""
        # Update particles
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()
        
        # Update letter tiles
        for tile in self.letter_tiles:
            tile.update()
            
        # Update animations
        if self.animation_timer > 0:
            self.animation_timer -= 1
            if self.animation_timer == 0:
                # Timer finished, load next word
                if self.state == STATE_PLAYING:
                    self.next_word()
        
        if self.input_shake > 0:
            self.input_shake -= 1
            
        # Update transition
        self.transition.update()
    
    def draw(self):
        """Draw everything to screen"""
        self.win.blit(self.bg, (0, 0))
        
        # Draw particles (underneath UI)
        for particle in self.particles:
            particle.draw(self.win)
            
        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_PLAYING:
            self.draw_game()
        elif self.state == STATE_GAME_OVER:
            self.draw_game_over()
        elif self.state == STATE_SETTINGS:
            self.draw_settings()
        
        # Draw buttons (on top of state UI)
        for btn in self.buttons:
            btn.draw(self.win)
            
        # Draw transition (on top of everything)
        self.transition.draw(self.win)
        
        pygame.display.update()
    
    def draw_menu(self):
        """Draw main menu"""
        draw_text(self.win, "WORD SCRABBLE", self.font_title, C_ACCENT,
                  (WIDTH // 2, HEIGHT // 6), align="center")
        draw_text(self.win, "ARENA", self.font_heading, C_SECONDARY,
                  (WIDTH // 2, HEIGHT // 6 + 80), align="center")
        
        # MOVED THIS TEXT UP: Changed y-coordinate
        draw_text(self.win, "Test your word unscrambling skills!", self.font_small, C_WHITE,
                  (WIDTH // 2, 160), align="center")
    
    def draw_settings(self):
        """Draw settings/difficulty selection screen"""
        draw_text(self.win, "Select Difficulty", self.font_heading, C_PRIMARY,
                  (WIDTH // 2, 100), align="center")
        
        descriptions = {
            DIFFICULTY_EASY: "Easy - 10 simple words",
            DIFFICULTY_MEDIUM: "Medium - 10 intermediate words",
            DIFFICULTY_HARD: "Hard - 10 challenging words"
        }
        
        # CORRECTED Y-COORDINATES: Placed text 20px above each button
        # Button Y-coords are 250, 340, 430.
        text_positions = [
            ("EASY", 230),  # Above Easy button (y=250)
            ("MEDIUM", 320), # Above Medium button (y=340)
            ("HARD", 410)   # Above Hard button (y=430)
        ]
        
        for i, (diff, y_pos) in enumerate(text_positions):
            draw_text(self.win, descriptions[diff], self.font_small, C_LIGHT_BG,
                      (WIDTH // 2, y_pos), align="center")
    
    def draw_game(self):
        """Draw main game screen"""
        self.draw_header()
        self.draw_game_content()
        self.draw_footer()
    
    def draw_header(self):
        """Draw game header with stats"""
        header_height = 80
        header_rect = pygame.Rect(0, 0, WIDTH, header_height)
        draw_rounded_rect(self.win, header_rect, C_PRIMARY, 0) # No radius for top bar
        
        draw_text(self.win, f"Score: {self.score}", self.font_medium, C_WHITE,
                  (30, header_height // 2), align="midleft")
        
        progress_text = f"{self.current_word_index}/{len(self.words_list)}"
        draw_text(self.win, progress_text, self.font_medium, C_WHITE,
                  (WIDTH - 30, header_height // 2), align="midright")
        
        # Progress bar
        progress = (self.current_word_index - 1) / len(self.words_list)
        progress_width = int((WIDTH - 200) * progress)
        progress_bar_bg = pygame.Rect(100, 55, WIDTH - 200, 10)
        progress_bar = pygame.Rect(100, 55, progress_width, 10)
        
        draw_rounded_rect(self.win, progress_bar_bg, C_DARK_BG, 5)
        draw_rounded_rect(self.win, progress_bar, C_SUCCESS, 5)
    
    def draw_game_content(self):
        """Draw main game content"""
        # Scrambled word display
        draw_text(self.win, "Unscramble this word:", self.font_small, C_LIGHT_BG,
                  (WIDTH // 2, HEIGHT // 2 - 160), align="center")
        
        # Draw letter tiles
        for tile in self.letter_tiles:
            tile.draw(self.win)
        
        # User input display
        input_y = HEIGHT // 2 + 60
        input_box_rect = pygame.Rect(WIDTH // 2 - 200, input_y - 30, 400, 60)
        
        # Add shake effect
        shake_offset = random.randint(-self.input_shake, self.input_shake)
        input_box_rect.x += shake_offset
        
        # Draw input box
        draw_rounded_rect(self.win, input_box_rect, C_DARK_BG, 10)
        border_color = C_ACCENT if self.input_shake == 0 else C_ERROR
        pygame.draw.rect(self.win, border_color, input_box_rect, 2, border_radius=10)
        
        # Draw input text
        input_text_str = self.user_input.upper() if self.user_input else ""
        input_color = C_WHITE if self.user_input else C_DISABLED
        
        text_surf = self.font_large.render(input_text_str, True, input_color)
        text_rect = text_surf.get_rect(midleft = (input_box_rect.x + 20, input_box_rect.centery))
        self.win.blit(text_surf, text_rect)
        
        # Draw blinking cursor
        if pygame.time.get_ticks() % 1000 < 500: # Blink every 500ms
            cursor_x = text_rect.right + 5 if self.user_input else input_box_rect.x + 20
            cursor_y = input_box_rect.centery
            pygame.draw.line(self.win, C_WHITE, (cursor_x, cursor_y - 12),
                             (cursor_x, cursor_y + 12), 2)
        
        # Instructions
        draw_text(self.win, "Press ENTER to submit | ESC to go back", self.font_tiny, C_LIGHT_BG,
                  (WIDTH // 2, input_y + 50), align="center")
    
    def draw_footer(self):
        """Draw game footer with statistics"""
        footer_y = HEIGHT - 60
        footer_rect = pygame.Rect(0, footer_y, WIDTH, 60)
        draw_rounded_rect(self.win, footer_rect, C_DARK_BG, 0)
        
        # Statistics
        accuracy = self.stats.accuracy
        streak_text = f"Streak: {self.stats.current_streak} (Best: {self.stats.best_streak})"
        accuracy_text = f"Accuracy: {accuracy:.1f}%"
        
        draw_text(self.win, streak_text, self.font_small, C_SUCCESS,
                  (30, footer_y + 30), align="midleft")
        
        draw_text(self.win, accuracy_text, self.font_small, C_SECONDARY,
                  (WIDTH // 2, footer_y + 30), align="center")
        
        difficulty_text = f"Difficulty: {self.difficulty}"
        draw_text(self.win, difficulty_text, self.font_small, C_ACCENT,
                  (WIDTH - 30, footer_y + 30), align="midright")
    
    def draw_game_over(self):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((C_DARK_BG[0], C_DARK_BG[1], C_DARK_BG[2], 220))
        self.win.blit(overlay, (0, 0))
        
        draw_text(self.win, "🎉 GAME OVER 🎉", self.font_title, C_ACCENT,
                  (WIDTH // 2, HEIGHT // 2 - 150), align="center")
        
        score_text = f"Final Score: {self.score}/{len(self.words_list)}"
        draw_text(self.win, score_text, self.font_heading, C_SUCCESS,
                  (WIDTH // 2, HEIGHT // 2 - 40), align="center")
        
        accuracy = self.stats.accuracy
        stats_text = f"Accuracy: {accuracy:.1f}% | Best Streak: {self.stats.best_streak}"
        draw_text(self.win, stats_text, self.font_medium, C_WHITE,
                  (WIDTH // 2, HEIGHT // 2 + 40), align="center")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    game = WordScrabbleGame()
    game.run()