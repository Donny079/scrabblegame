import pygame
import random
import time

# --- Initialize pygame ---
pygame.init()

# --- Window setup ---
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Word Scramble Game")

# --- Load background image ---
BG = pygame.transform.scale(pygame.image.load("BG.jpeg"), (WIDTH, HEIGHT))

# --- Fonts ---
FONT_BIG = pygame.font.Font(None, 90)
FONT_MED = pygame.font.Font(None, 60)
FONT_SMALL = pygame.font.Font(None, 36)

# --- Game data ---
WORDS = [
    "python", "keyboard", "computer", "laptop", "science", "learning",
    "education", "coding", "flask", "variable", "function", "module",
    "package", "development", "algorithm", "database", "internet",
    "network", "software", "hardware"
]

def scramble_word(word):
    word_list = list(word)
    random.shuffle(word_list)
    return ''.join(word_list)

def draw_centered_text(surface, text, font, color, y):
    """Helper to draw text centered on screen"""
    txt = font.render(text, True, color)
    rect = txt.get_rect(center=(WIDTH // 2, y))
    surface.blit(txt, rect)

def animate_correct(message):
    """Bounce/Zoom animation for correct answer"""
    for scale in range(20, 80, 10):
        WIN.blit(BG, (0, 0))
        msg_font = pygame.font.Font(None, scale + 40)
        msg_text = msg_font.render(message, True, (0, 255, 0))
        text_rect = msg_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        WIN.blit(msg_text, text_rect)
        pygame.display.update()
        pygame.time.delay(30)

    # Fade out
    for alpha in range(255, 0, -40):
        WIN.blit(BG, (0, 0))
        msg_font = pygame.font.Font(None, 80)
        msg_text = msg_font.render(message, True, (0, alpha, 0))
        text_rect = msg_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        WIN.blit(msg_text, text_rect)
        pygame.display.update()
        pygame.time.delay(25)


def animate_wrong(message):
    """Shake animation for wrong answer"""
    msg_font = pygame.font.Font(None, 80)
    msg_text = msg_font.render(message, True, (255, 0, 0))
    text_rect = msg_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    # Shake left-right quickly
    for offset in [-10, 10, -15, 15, -8, 8, 0]:
        WIN.blit(BG, (0, 0))
        WIN.blit(msg_text, (text_rect.x + offset, text_rect.y))
        pygame.display.update()
        pygame.time.delay(40)

    # Quick fade-out
    for alpha in range(255, 0, -40):
        WIN.blit(BG, (0, 0))
        faded_text = msg_font.render(message, True, (255, alpha, alpha))
        WIN.blit(faded_text, text_rect)
        pygame.display.update()
        pygame.time.delay(25)

def animate_text_effect(scrambled_word, color, effect_type):
    if effect_type == "bounce":
        animate_correct("✅ Correct!")
    elif effect_type == "shake":
        animate_wrong("❌ Wrong!")
        
def draw(scrambled_word, user_input, score, message, color):
    WIN.blit(BG, (0, 0))

    # Title with shadow
    shadow = FONT_BIG.render("WORD SCRAMBLE", True, (0, 0, 0))
    WIN.blit(shadow, (WIDTH // 2 - shadow.get_width() // 2 + 4, 54))
    title_text = FONT_BIG.render("WORD SCRAMBLE", True, (255, 215, 0))
    WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

    # Scrambled word with glowing look
    glow = FONT_BIG.render(scrambled_word, True, (50, 50, 50))
    WIN.blit(glow, (WIDTH // 2 - glow.get_width() // 2 + 3, 203))
    word_text = FONT_BIG.render(scrambled_word, True, color)
    WIN.blit(word_text, (WIDTH // 2 - word_text.get_width() // 2, 200))

    # Input
    input_text = FONT_SMALL.render(f"Your Answer: {user_input}", True, (255, 255, 255))
    WIN.blit(input_text, (WIDTH // 2 - input_text.get_width() // 2, 360))

    # Score
    score_text = FONT_SMALL.render(f"Score: {score}", True, (0, 255, 0))
    WIN.blit(score_text, (30, 20))

    # Message
    if message:
        msg_text = FONT_MED.render(message, True, (255, 180, 180))
        WIN.blit(msg_text, (WIDTH // 2 - msg_text.get_width() // 2, 470))

    pygame.display.update()

def show_game_over(score, total):
    WIN.blit(BG, (0, 0))
    draw_centered_text(WIN, "🎉 GAME OVER 🎉", FONT_BIG, (255, 215, 0), 200)
    draw_centered_text(WIN, f"Your Final Score: {score}/{total}", FONT_MED, (0, 255, 0), 300)
    draw_centered_text(WIN, "Press ESC to Exit", FONT_SMALL, (255, 255, 255), 400)
    pygame.display.update()

def main():
    run = True
    clock = pygame.time.Clock()

    used_words = []
    score = 0
    user_input = ""
    message = ""
    message_color = (255, 255, 0)

    # First word
    current_word = random.choice(WORDS)
    used_words.append(current_word)
    scrambled_word = scramble_word(current_word)

    while run:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

                elif event.key == pygame.K_RETURN:
                    if user_input.lower() == current_word.lower():
                        score += 1
                        message = "✅ Correct!"
                        message_color = (0, 255, 0)
                        animate_text_effect(scrambled_word, (0, 255, 0), "bounce")
                    else:
                        message = f"❌ Wrong! It was '{current_word}'"
                        message_color = (255, 50, 50)
                        animate_text_effect(scrambled_word, (255, 50, 50), "shake")

                    # Next word
                    if len(used_words) == len(WORDS):
                        show_game_over(score, len(WORDS))
                        waiting = True
                        while waiting:
                            for e in pygame.event.get():
                                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                                    run = False
                                    waiting = False
                            pygame.time.delay(100)
                        break

                    current_word = random.choice([w for w in WORDS if w not in used_words])
                    used_words.append(current_word)
                    scrambled_word = scramble_word(current_word)
                    user_input = ""

                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    if event.unicode.isalpha():
                        user_input += event.unicode

        draw(scrambled_word, user_input, score, message, message_color)

    pygame.quit()

if __name__ == "__main__":
    main()
