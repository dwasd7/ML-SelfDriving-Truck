
import math
import random
import sys
import os

import neat
import pygame
WIDTH = 1920
HEIGHT = 1080

TRUCK_SIZE_X = 35    
TRUCK_SIZE_Y = 35

EDGE_COLOR = (255, 255, 255, 255) # Color WHEN TO Crash

current_cycle = 0 # Cycle counter which increments after all cars have crashed in that cycle

class Truck1:

    def __init__(self):
        #Load Truck in
        self.sprite = pygame.image.load('truck2.png')
        self.sprite = pygame.transform.scale(self.sprite, (TRUCK_SIZE_X, TRUCK_SIZE_Y))
        self.rotated_sprite = self.sprite 

        self.position =  [717,842] #Starting Position
        self.angle = 0
        self.speed = 0

        self.speed_set = False 

        self.center = [self.position[0] + TRUCK_SIZE_X / 2, self.position[1] + TRUCK_SIZE_Y / 2] # Calculate Center

        self.radars = [] # List For raders
        self.drawing_radars = [] # list of raders to draw

        self.on_track = True # Boolean To Check If Truck has Crashed or still on Track

        self.distance = 0 # Distance Driven
        self.time = 0 # Time Passed

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position) # Draw Sprite
        self.draw_radar(screen) #call draw radar on screen

    def draw_radar(self, screen):
        #Draw All Radars
        for radar in self.radars:
            pos = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, pos, 1)
            pygame.draw.circle(screen, (0, 255, 0), pos, 5)

    def check_collision(self, game_map):
        self.on_track = True
        for point in self.corners:
            # If Any Corner Touches Edge_Color(White in this case), It implies Truck Crash
            if game_map.get_at((int(point[0]), int(point[1]))) == EDGE_COLOR:
                self.on_track = False
                break

    def check_radar(self, degree, game_map):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # While We Don't Hit EDGE_COLOR AND length less than 300(max), this means the car keeps moving forward
        while not game_map.get_at((x, y)) == EDGE_COLOR and length < 300:
            length = length + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # Calculates the Distance To Edge And Appends it To the Radars List
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])
    

    #update the game map into the current info
    def update(self, game_map):
        #set Start speed to 20 if speed doesnt change up or down while testing 
        if not self.speed_set:
            self.speed = 20
            self.speed_set = True

        # Get the Rotated Sprite and also Move Into The Right X-Direction without allowing the Truck to go more than 20px To The Edge
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 20)
        self.position[0] = min(self.position[0], WIDTH - 120)

        # Same For Y-Direction without allowing the Truck to go more than 20px To The Edge
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], WIDTH - 120)

        # Increase Distance and Time
        self.distance += self.speed
        self.time += 1
        
        

        # Calculate the New Center
        self.center = [int(self.position[0]) + TRUCK_SIZE_X / 2, int(self.position[1]) + TRUCK_SIZE_Y / 2]

        #Set Length to Half of the TRUCK_SIZE_X and Calculate all Four Corners
        length = 0.5 * TRUCK_SIZE_X
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check Collisions And Clear Radars
        self.check_collision(game_map)
        self.radars.clear()

        # From -90 To 120 With Step-Size 45 Check Radar
        for d in range(-90, 120, 45):
            self.check_radar(d, game_map)

    def get_data(self):
        # Get the Distances from the edge of from all 5 Radar Points
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    def is_on_track(self):
        # Basic On_track Function
        return self.on_track

    def add_fitness(self):
        # return self.distance / Trucksize/2 to add the fitness
        return self.distance / (TRUCK_SIZE_X / 2)

    def rotate_center(self, image, angle):
        # Simply Rotate the Rectangle
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image
    


class Truck2:

    def __init__(self):
        #Load Truck in
        self.sprite = pygame.image.load('truck.png')
        self.sprite = pygame.transform.scale(self.sprite, (TRUCK_SIZE_X, TRUCK_SIZE_Y))
        self.rotated_sprite = self.sprite 

        self.position =  [717,842] #Starting Position
        self.angle = 0
        self.speed = 0

        self.speed_set = False 

        self.center = [self.position[0] + TRUCK_SIZE_X / 2, self.position[1] + TRUCK_SIZE_Y / 2] # Calculate Center

        self.radars = [] # List For raders
        self.drawing_radars = [] # list of raders to draw

        self.on_track = True # Boolean To Check If Truck has Crashed or still on Track

        self.distance = 0 # Distance Driven
        self.time = 0 # Time Passed

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position) # Draw Sprite
        self.draw_radar(screen) #call draw radar on screen

    def draw_radar(self, screen):
        #Draw All Radars
        for radar in self.radars:
            pos = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, pos, 1)
            pygame.draw.circle(screen, (0, 255, 0), pos, 5)

    def check_collision(self, game_map):
        self.on_track = True
        for point in self.corners:
            # If Any Corner Touches Edge_Color(White in this case), It implies Truck Crash
            if game_map.get_at((int(point[0]), int(point[1]))) == EDGE_COLOR:
                self.on_track = False
                break

    def check_radar(self, degree, game_map):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # While We Don't Hit EDGE_COLOR AND length less than 300(max), this means the car keeps moving forward
        while not game_map.get_at((x, y)) == EDGE_COLOR and length < 300:
            length = length + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # Calculates the Distance To Edge And Appends it To the Radars List
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])
    

    #update the game map into the current info
    def update(self, game_map):
        #set Start speed to 20 if speed doesnt change up or down while testing 
        if not self.speed_set:
            self.speed = 20
            self.speed_set = True

        # Get the Rotated Sprite and also Move Into The Right X-Direction without allowing the Truck to go more than 20px To The Edge
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 20)
        self.position[0] = min(self.position[0], WIDTH - 120)

        # Same For Y-Direction without allowing the Truck to go more than 20px To The Edge
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], WIDTH - 120)

        # Increase Distance and Time
        self.distance += self.speed
        self.time += 1
        
        

        # Calculate the New Center
        self.center = [int(self.position[0]) + TRUCK_SIZE_X / 2, int(self.position[1]) + TRUCK_SIZE_Y / 2]

        #Set Length to Half of the TRUCK_SIZE_X and Calculate all Four Corners
        length = 0.5 * TRUCK_SIZE_X
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check Collisions And Clear Radars
        self.check_collision(game_map)
        self.radars.clear()

        # From -90 To 120 With Step-Size 45 Check Radar
        for d in range(-90, 120, 45):
            self.check_radar(d, game_map)

    def get_data(self):
        # Get the Distances from the edge of from all 5 Radar Points
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    def is_on_track(self):
        # Basic On_track Function
        return self.on_track

    def add_fitness(self):
        # return self.distance / Trucksize/2 to add the fitness
        return self.distance / (TRUCK_SIZE_X / 2)

    def rotate_center(self, image, angle):
        # Simply Rotate the Rectangle
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image