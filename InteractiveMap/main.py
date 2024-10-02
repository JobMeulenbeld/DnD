import os
import cv2
import numpy as np
import pygame

# Initialize Pygame
pygame.init()

# Define the directory containing the maps
MAPS_DIR = './Maps'

# Get full screen dimensions
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h

# Create the Pygame screen with full screen dimensions
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Map Selection Menu")

# Fonts for displaying text
font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 30)

# Colors
BLACK = (0, 0, 0)
GREY = (150, 150, 150)
WHITE = (255, 255, 255)
PLAYER_COLOR = (0, 0, 255)

# Define player starting position
player_x, player_y = 1, 1  # Starting on a path



# List all available maps in the ./Maps folder
def list_maps(directory):
    # List all image files (png, jpg) in the directory
    return [f for f in os.listdir(directory) if f.endswith(('.png', '.jpg', '.jpeg'))]

# Display the selection menu and check for hover and clicks
def display_menu(maps):
    screen.fill(WHITE)  # White background
    title_text = font.render("Select a Map:", True, BLACK)
    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 50))

    mouse_x, mouse_y = pygame.mouse.get_pos()  # Get mouse position
    clicked_map = None  # This will store the clicked map if any

    for idx, map_file in enumerate(maps):
        map_y = 150 + idx * 50  # Calculate the Y position of each map item

        # Check if the mouse is hovering over this map item
        if 150 + idx * 50 <= mouse_y <= 150 + idx * 50 + 40 and screen_width // 2 - 200 <= mouse_x <= screen_width // 2 + 200:
            map_color = GREY  # Change color to grey if hovered
            if pygame.mouse.get_pressed()[0]:  # If the left mouse button is clicked
                clicked_map = map_file
        else:
            map_color = BLACK  # Default color

        # Render the map item
        map_text = small_font.render(map_file, True, map_color)
        screen.blit(map_text, (screen_width // 2 - map_text.get_width() // 2, map_y))

    pygame.display.flip()
    return clicked_map  # Return the clicked map if any

# Function to load and display the selected map with the grid
def load_and_display_map(map_path):
    global player_x, player_y
    # Load the image using OpenCV
    img = cv2.imread(map_path)
    
    # Check if the image is loaded properly
    if img is None:
        print(f"Error: Could not load map {map_path}")
        return
    
    # Convert OpenCV image from BGR to RGB for Pygame
    image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Get original image dimensions
    image_height, image_width, _ = image_rgb.shape

    # Calculate the aspect ratio of the image
    aspect_ratio = image_width / image_height

    # Snap the number of columns to an integer (choose between 65 or 66)
    NUM_GRID_COLUMNS = 66

    # Calculate the grid size based on the number of columns
    GRID_SIZE_X = screen_width / NUM_GRID_COLUMNS
    new_width = int(GRID_SIZE_X * NUM_GRID_COLUMNS)  # Width that matches the integer grid columns
    new_height = int(new_width / aspect_ratio)  # Adjust the height to maintain aspect ratio

    # Check if the new dimensions fit within the screen, adjust if necessary
    if new_height > screen_height:
        # If the height is too large to fit the screen, adjust the grid size to fit height
        new_height = screen_height
        new_width = int(new_height * aspect_ratio)
        GRID_SIZE_X = new_width / NUM_GRID_COLUMNS

    # Resize the image while maintaining the aspect ratio and fitting the snapped grid size
    image_resized = cv2.resize(image_rgb, (new_width, new_height))

    # Convert the resized OpenCV image to a Pygame surface
    image_surface = pygame.surfarray.make_surface(np.flipud(np.rot90(image_resized)))

    # Center the image on the screen
    image_x = (screen_width - new_width) // 2
    image_y = (screen_height - new_height) // 2

    # Define grid color
    GRID_COLOR = (0, 0, 0)  # Black grid lines

    # Game loop to display the map and grid
    running = True
    while running:
        for event in pygame.event.get():
            new_x, new_y = player_x, player_y  # Track potential new position

            if event.type == pygame.QUIT:
                running = False
                return "quit"  # Return "quit" when closing

            # Check if the escape key is pressed to go back to menu
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"  # Return "menu" to go back to the menu
                if event.key == pygame.K_LEFT:
                    new_x -= 1
                elif event.key == pygame.K_RIGHT:
                    new_x += 1
                elif event.key == pygame.K_UP:
                    new_y -= 1
                elif event.key == pygame.K_DOWN:
                    new_y += 1
            
            player_x, player_y = new_x, new_y

        # Clear the screen and draw the resized image centered on the screen
        screen.fill((255, 255, 255))  # Fill the background with white
        screen.blit(image_surface, (image_x, image_y))

        # Draw the grid on top of the image, now aligned with integer columns
        for i in range(NUM_GRID_COLUMNS + 1):  # +1 to draw the rightmost line
            x = image_x + i * GRID_SIZE_X
            pygame.draw.line(screen, GRID_COLOR, (round(x), image_y), (round(x), image_y + new_height), 1)  # Vertical grid lines
        for j in range(int(new_height / GRID_SIZE_X) + 1):  # +1 to draw the bottom line
            y = image_y + j * GRID_SIZE_X  # Use GRID_SIZE_X for square cells
            pygame.draw.line(screen, GRID_COLOR, (image_x, round(y)), (image_x + new_width, round(y)), 1)  # Horizontal grid lines

        # Draw the player
        # Calculate player's actual position on the screen relative to the grid
        player_screen_x = image_x + player_x * GRID_SIZE_X + 1
        player_screen_y = image_y + player_y * GRID_SIZE_X + 1

        player_rect = pygame.Rect(player_screen_x, player_screen_y, GRID_SIZE_X, GRID_SIZE_X)
        pygame.draw.rect(screen, PLAYER_COLOR, player_rect)

        # Update the display
        pygame.display.flip()

# Main program
def main():
    while True:
        # Get the list of available maps
        available_maps = list_maps(MAPS_DIR)

        if not available_maps:
            print("No maps found in the ./Maps folder.")
            return

        # Map selection loop
        selected_map = None
        while selected_map is None:
            selected_map = display_menu(available_maps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

        # Once a map is selected, load and display the map with the grid
        result = load_and_display_map(os.path.join(MAPS_DIR, selected_map))

        # If result is "menu", go back to menu, otherwise quit
        if result == "quit":
            pygame.quit()
            return

# Run the main program
if __name__ == "__main__":
    main()
