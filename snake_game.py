import pygame
import random
import numpy as np

class SnakeGame:
    def __init__(self, width=400, height=400, grid_size=20):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.reset()
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Snake Game AI')
        self.clock = pygame.time.Clock()
        
        # Load and scale images
        self.head_img = pygame.Surface((grid_size-2, grid_size-2))
        self.head_img.fill((50, 205, 50))  # Lighter green for head
        self.body_img = pygame.Surface((grid_size-2, grid_size-2))
        self.body_img.fill((34, 139, 34))  # Darker green for body
        
    def reset(self):
        # Initialize snake in the middle of the screen
        self.snake = [(self.width//(2*self.grid_size))*self.grid_size,
                      (self.height//(2*self.grid_size))*self.grid_size]
        self.snake_body = [self.snake.copy()]
        self.food = self._place_food()
        self.score = 0
        self.direction = [self.grid_size, 0]  # Start moving right
        self.frame_iteration = 0
        return self._get_state()
    
    def _place_food(self):
        while True:
            food = [random.randrange(0, self.width, self.grid_size),
                   random.randrange(0, self.height, self.grid_size)]
            if food not in self.snake_body:
                return food
    
    def _get_state(self):
        # Get state information for the AI agent
        head = self.snake_body[0]
        
        # Points around the head
        point_l = [head[0] - self.grid_size, head[1]]
        point_r = [head[0] + self.grid_size, head[1]]
        point_u = [head[0], head[1] - self.grid_size]
        point_d = [head[0], head[1] + self.grid_size]
        
        # Current direction
        dir_l = self.direction == [-self.grid_size, 0]
        dir_r = self.direction == [self.grid_size, 0]
        dir_u = self.direction == [0, -self.grid_size]
        dir_d = self.direction == [0, self.grid_size]
        
        state = [
            # Danger straight
            (dir_r and self._is_collision(point_r)) or
            (dir_l and self._is_collision(point_l)) or
            (dir_u and self._is_collision(point_u)) or
            (dir_d and self._is_collision(point_d)),
            
            # Danger right
            (dir_u and self._is_collision(point_r)) or
            (dir_d and self._is_collision(point_l)) or
            (dir_l and self._is_collision(point_u)) or
            (dir_r and self._is_collision(point_d)),
            
            # Danger left
            (dir_d and self._is_collision(point_r)) or
            (dir_u and self._is_collision(point_l)) or
            (dir_r and self._is_collision(point_u)) or
            (dir_l and self._is_collision(point_d)),
            
            # Move direction
            dir_l, dir_r, dir_u, dir_d,
            
            # Food location
            self.food[0] < head[0],  # food left
            self.food[0] > head[0],  # food right
            self.food[1] < head[1],  # food up
            self.food[1] > head[1]   # food down
        ]
        
        return np.array(state, dtype=int)
    
    def _is_collision(self, point):
        # Check if point collides with boundary or snake body
        if point[0] >= self.width or point[0] < 0 or \
           point[1] >= self.height or point[1] < 0:
            return True
        if point in self.snake_body[1:]:
            return True
        return False
    
    def step(self, action):
        self.frame_iteration += 1
        
        # Convert action [straight, right, left] to direction change
        clock_wise = [self.grid_size, 0], [0, self.grid_size], \
                     [-self.grid_size, 0], [0, -self.grid_size]
        idx = clock_wise.index(self.direction)
        
        if action == 1:  # right turn
            new_idx = (idx + 1) % 4
            self.direction = clock_wise[new_idx]
        elif action == 2:  # left turn
            new_idx = (idx - 1) % 4
            self.direction = clock_wise[new_idx]
        
        # Move snake
        self.snake[0] = self.snake[0] + self.direction[0]
        self.snake[1] = self.snake[1] + self.direction[1]
        
        # Check if game over
        reward = 0
        game_over = False
        if self._is_collision(self.snake) or self.frame_iteration > 100*len(self.snake_body):
            game_over = True
            reward = -10
            return reward, game_over, self.score
        
        # Update snake body
        self.snake_body.insert(0, self.snake.copy())
        
        # Check if snake got food
        if self.snake == self.food:
            self.score += 1
            reward = 10
            self.food = self._place_food()
        else:
            self.snake_body.pop()
        
        return reward, game_over, self.score
    
    def render(self):
        self.screen.fill((0, 0, 0))
        
        # Draw grid lines
        for x in range(0, self.width, self.grid_size):
            pygame.draw.line(self.screen, (40, 40, 40), (x, 0), (x, self.height))
        for y in range(0, self.height, self.grid_size):
            pygame.draw.line(self.screen, (40, 40, 40), (0, y), (self.width, y))
        
        # Draw snake body segments with gradient effect
        for i, segment in enumerate(self.snake_body):
            if i == 0:  # Head
                # Draw head
                pygame.draw.rect(self.screen, (50, 205, 50),
                               pygame.Rect(segment[0], segment[1],
                                         self.grid_size-2, self.grid_size-2))
                # Draw eyes
                eye_radius = 2
                if self.direction == [self.grid_size, 0]:  # Right
                    left_eye = (segment[0] + self.grid_size-8, segment[1] + 5)
                    right_eye = (segment[0] + self.grid_size-8, segment[1] + self.grid_size-7)
                elif self.direction == [-self.grid_size, 0]:  # Left
                    left_eye = (segment[0] + 6, segment[1] + 5)
                    right_eye = (segment[0] + 6, segment[1] + self.grid_size-7)
                elif self.direction == [0, -self.grid_size]:  # Up
                    left_eye = (segment[0] + 5, segment[1] + 6)
                    right_eye = (segment[0] + self.grid_size-7, segment[1] + 6)
                else:  # Down
                    left_eye = (segment[0] + 5, segment[1] + self.grid_size-8)
                    right_eye = (segment[0] + self.grid_size-7, segment[1] + self.grid_size-8)
                pygame.draw.circle(self.screen, (255, 255, 255), left_eye, eye_radius)
                pygame.draw.circle(self.screen, (255, 255, 255), right_eye, eye_radius)
            else:  # Body
                # Create gradient effect for body
                color_val = max(34, 139 - (i * 5))
                pygame.draw.rect(self.screen, (34, color_val, 34),
                               pygame.Rect(segment[0], segment[1],
                                         self.grid_size-2, self.grid_size-2))
        
        # Draw apple-like food
        food_center = (self.food[0] + self.grid_size//2, self.food[1] + self.grid_size//2)
        # Main apple body
        pygame.draw.circle(self.screen, (255, 0, 0),
                         food_center, (self.grid_size-4)//2)
        # Apple highlight
        highlight_pos = (food_center[0] - 2, food_center[1] - 2)
        pygame.draw.circle(self.screen, (255, 255, 255),
                         highlight_pos, 2)
        # Apple stem
        stem_start = (food_center[0], self.food[1] + 2)
        stem_end = (food_center[0] + 2, self.food[1])
        pygame.draw.line(self.screen, (101, 67, 33),
                        stem_start, stem_end, 2)
        
        pygame.display.flip()
        self.clock.tick(30)