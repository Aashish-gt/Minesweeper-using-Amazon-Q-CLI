import pygame
import random
import time
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
GRID_SIZE = 10
CELL_SIZE = 35
GRID_WIDTH = GRID_SIZE * CELL_SIZE
GRID_HEIGHT = GRID_SIZE * CELL_SIZE
MARGIN_TOP = 80  # Space for timer, counter, restart button
MINES_COUNT = 15

# Calculate window size based on grid
WIDTH = GRID_WIDTH
HEIGHT = GRID_HEIGHT + MARGIN_TOP

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (192, 192, 192)
DARK_GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)
YELLOW = (255, 255, 0)
COLORS = [BLUE, GREEN, RED, (128, 0, 128), (128, 0, 0), (0, 128, 128), BLACK, GRAY]  # Better number colors

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Minesweeper')
font = pygame.font.SysFont('Arial', 20)
large_font = pygame.font.SysFont('Arial', 36)
icon = pygame.Surface((32, 32))
icon.fill(GRAY)
pygame.draw.circle(icon, BLACK, (16, 16), 8)
pygame.display.set_icon(icon)

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.neighbor_mines = 0
        
    def draw(self):
        rect = pygame.Rect(self.x * CELL_SIZE, MARGIN_TOP + self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        
        if self.is_revealed:
            pygame.draw.rect(screen, WHITE, rect)
            if self.is_mine:
                # Draw mine - improved mine graphic
                pygame.draw.circle(screen, BLACK, rect.center, CELL_SIZE // 3)
                # Add some details to the mine
                pygame.draw.line(screen, BLACK, 
                                (rect.centerx - CELL_SIZE//3, rect.centery),
                                (rect.centerx + CELL_SIZE//3, rect.centery), 2)
                pygame.draw.line(screen, BLACK, 
                                (rect.centerx, rect.centery - CELL_SIZE//3),
                                (rect.centerx, rect.centery + CELL_SIZE//3), 2)
                # Add shine to mine
                pygame.draw.circle(screen, WHITE, (rect.centerx - CELL_SIZE//8, rect.centery - CELL_SIZE//8), 3)
            elif self.neighbor_mines > 0:
                # Draw number
                text = font.render(str(self.neighbor_mines), True, COLORS[self.neighbor_mines - 1])
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
        else:
            # Draw unrevealed cell with 3D effect
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.line(screen, WHITE, rect.topleft, rect.topright, 2)
            pygame.draw.line(screen, WHITE, rect.topleft, rect.bottomleft, 2)
            pygame.draw.line(screen, DARK_GRAY, rect.bottomleft, rect.bottomright, 2)
            pygame.draw.line(screen, DARK_GRAY, rect.topright, rect.bottomright, 2)
            
        if self.is_flagged:
            # Draw better flag
            flag_pole = pygame.Rect(self.x * CELL_SIZE + CELL_SIZE // 2 - 1, 
                                  MARGIN_TOP + self.y * CELL_SIZE + CELL_SIZE // 5,
                                  2, CELL_SIZE // 1.5)
            pygame.draw.rect(screen, BLACK, flag_pole)
            
            # Triangle flag
            flag_points = [
                (self.x * CELL_SIZE + CELL_SIZE // 2, MARGIN_TOP + self.y * CELL_SIZE + CELL_SIZE // 5),
                (self.x * CELL_SIZE + CELL_SIZE // 2 + CELL_SIZE // 3, MARGIN_TOP + self.y * CELL_SIZE + CELL_SIZE // 3),
                (self.x * CELL_SIZE + CELL_SIZE // 2, MARGIN_TOP + self.y * CELL_SIZE + CELL_SIZE // 2)
            ]
            pygame.draw.polygon(screen, RED, flag_points)

class Game:
    def __init__(self):
        self.reset_game()
        
    def reset_game(self):
        self.board = [[Cell(x, y) for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
        self.game_over = False
        self.game_won = False
        self.mines_placed = False
        self.start_time = None
        self.elapsed_time = 0
        self.flags_used = 0
        
    def place_mines(self, first_click_x, first_click_y):
        # Place mines, but avoid the first clicked cell and its neighbors
        mines_placed = 0
        safe_cells = [(first_click_x, first_click_y)]
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = first_click_x + dx, first_click_y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    safe_cells.append((nx, ny))
        
        while mines_placed < MINES_COUNT:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if not self.board[x][y].is_mine and (x, y) not in safe_cells:
                self.board[x][y].is_mine = True
                mines_placed += 1
                
                # Update neighbor counts
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                            self.board[nx][ny].neighbor_mines += 1
        
        self.mines_placed = True
        self.start_time = time.time()
    
    def reveal_cell(self, x, y):
        if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
            return
            
        cell = self.board[x][y]
        
        if cell.is_revealed or cell.is_flagged:
            return
            
        if not self.mines_placed:
            self.place_mines(x, y)
            
        cell.is_revealed = True
        
        if cell.is_mine:
            self.game_over = True
            self.reveal_all_mines()
            return
            
        # If cell has no adjacent mines, reveal neighbors recursively
        if cell.neighbor_mines == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    self.reveal_cell(x + dx, y + dy)
                    
        # Check if game is won
        self.check_win()
    
    def toggle_flag(self, x, y):
        if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
            return
            
        cell = self.board[x][y]
        
        if not cell.is_revealed:
            if cell.is_flagged:
                cell.is_flagged = False
                self.flags_used -= 1
            else:
                cell.is_flagged = True
                self.flags_used += 1
    
    def reveal_all_mines(self):
        for row in self.board:
            for cell in row:
                if cell.is_mine:
                    cell.is_revealed = True
    
    def check_win(self):
        for row in self.board:
            for cell in row:
                if not cell.is_mine and not cell.is_revealed:
                    return False
        self.game_won = True
        self.game_over = True
        return True
    
    def draw(self):
        # Draw board
        for row in self.board:
            for cell in row:
                cell.draw()
        
        # Draw UI elements
        self.draw_ui()
    
    def draw_ui(self):
        # Background for UI - gradient effect
        for y in range(MARGIN_TOP):
            color_value = 100 + (y * 50 // MARGIN_TOP)
            color = (color_value, color_value, color_value + 30)
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))
        
        # Draw timer with icon
        if self.start_time:
            if not self.game_over:
                self.elapsed_time = int(time.time() - self.start_time)
            
            # Clock icon
            pygame.draw.circle(screen, WHITE, (20, 20), 12, 1)
            # Clock hands
            pygame.draw.line(screen, WHITE, (20, 20), (20, 12), 1)
            pygame.draw.line(screen, WHITE, (20, 20), (26, 20), 1)
            
            timer_text = font.render(f"{self.elapsed_time}s", True, WHITE)
            screen.blit(timer_text, (35, 10))
        
        # Draw mines counter with icon
        bomb_x, bomb_y = WIDTH - 90, 20
        pygame.draw.circle(screen, BLACK, (bomb_x, bomb_y), 10)
        pygame.draw.circle(screen, WHITE, (bomb_x - 3, bomb_y - 3), 2)  # Shine
        
        mines_text = font.render(f"{MINES_COUNT - self.flags_used}", True, WHITE)
        screen.blit(mines_text, (WIDTH - 70, 10))
        
        # Draw restart button with 3D effect
        restart_rect = pygame.Rect(WIDTH // 2 - 50, 40, 100, 30)
        
        # Button base
        pygame.draw.rect(screen, LIGHT_BLUE, restart_rect)
        
        # 3D effect
        pygame.draw.line(screen, WHITE, restart_rect.topleft, restart_rect.topright, 2)
        pygame.draw.line(screen, WHITE, restart_rect.topleft, restart_rect.bottomleft, 2)
        pygame.draw.line(screen, DARK_GRAY, restart_rect.bottomleft, restart_rect.bottomright, 2)
        pygame.draw.line(screen, DARK_GRAY, restart_rect.topright, restart_rect.bottomright, 2)
        
        restart_text = font.render("Restart", True, BLACK)
        text_rect = restart_text.get_rect(center=restart_rect.center)
        screen.blit(restart_text, text_rect)
        
        # Draw game over or win message with shadow effect
        if self.game_over:
            message = "YOU WIN!" if self.game_won else "GAME OVER"
            color = GREEN if self.game_won else RED
            
            # Shadow text
            shadow_text = large_font.render(message, True, BLACK)
            shadow_rect = shadow_text.get_rect(center=(WIDTH // 2 + 2, MARGIN_TOP // 2 + 2))
            screen.blit(shadow_text, shadow_rect)
            
            # Main text
            text = large_font.render(message, True, color)
            text_rect = text.get_rect(center=(WIDTH // 2, MARGIN_TOP // 2))
            screen.blit(text, text_rect)
    
    def handle_click(self, pos, right_click=False):
        # Check if click is on restart button
        restart_rect = pygame.Rect(WIDTH // 2 - 50, 40, 100, 40)
        if restart_rect.collidepoint(pos):
            self.reset_game()
            return
        
        # Check if click is on the grid
        if pos[1] < MARGIN_TOP:
            return
            
        grid_x = pos[0] // CELL_SIZE
        grid_y = (pos[1] - MARGIN_TOP) // CELL_SIZE
        
        if not (0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE):
            return
            
        if right_click:
            self.toggle_flag(grid_x, grid_y)
        else:
            self.reveal_cell(grid_x, grid_y)

def main():
    game = Game()
    running = True
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN and not game.game_over:
                if event.button == 1:  # Left click
                    game.handle_click(event.pos)
                elif event.button == 3:  # Right click
                    game.handle_click(event.pos, right_click=True)
            elif event.type == MOUSEBUTTONDOWN and game.game_over:
                # If game is over, only allow clicking restart
                game.handle_click(event.pos)
        
        # Draw everything
        screen.fill(LIGHT_BLUE)  # Changed background color
        game.draw()
        pygame.display.flip()
        clock.tick(30)  # Limit to 30 FPS
    
    pygame.quit()

if __name__ == "__main__":
    main()
