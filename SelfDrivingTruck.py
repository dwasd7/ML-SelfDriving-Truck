
import sys
import neat
import pygame
from Trucks import Truck2
from Trucks import Truck1

WIDTH = 1920
HEIGHT = 1080

TRUCK_SIZE_X = 30    
TRUCK_SIZE_Y = 30

EDGE_COLOR = (255, 255, 255, 255) # Color WHEN TO Crash
RIGHT,LEFT,FAST,SLOW = 0,1,2,3

current_cycle = 0 # Cycle count_time which increments after all cars have crashed in that cycle


#creates genomes with the size of the population of truck
def run_test(genomes, config):
    #Initialize PyGame and Diaply the screen with the given Width and Height
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

    # Setup Pygame Clock Settings, Font Settings & Load My test Map
    clock = pygame.time.Clock()
    cycle_font = pygame.font.SysFont("Arial", 30)
    on_track_font = pygame.font.SysFont("Arial", 20)
    game_map = pygame.image.load('map_with_holes.png')
 

    #Use for collections of Nets and Trucks
    nets = []
    trucks = []

    # For All Genomes(AI Truck in this case) Passed Create A New Neural Network and Initialize genomes fitness within nets
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        #append 2 types of trucks
        if i%2 == 0:
            trucks.append(Truck1())#append Truck1 Object
        else:
            trucks.append(Truck2())#append Truck2 Object

    

    global current_cycle
    current_cycle += 1

    # Simple Count_time To Roughly Limit Time (Not Good Practice)
    count_time = 0

    while True:
        # Exit the system on Quit Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        #For each truck, get the next improvement it makes
        for i, truck in enumerate(trucks):
            output = nets[i].activate(truck.get_data())#puts data or state into network (the result of that specific truck)
            truckres = output.index(max(output))#get the truck result on what happen to change what could be improved for that truck to preform that on the next Cycle

            #For the result of each truck, what ever one needs to be improved for that specific truck, it increments or decrements angle or speed accordingly accordingly
            if truckres == RIGHT:
                truck.angle += 10 # Go Left Next Time
            elif truckres == LEFT:
                truck.angle -= 10 # Go Right Next Time
            elif truckres == FAST:
                if(truck.speed - 2 >= 12):
                    truck.speed -= 2 # Slow Down Next Time
            else:
                truck.speed += 2 # Speed Up Next Time
        
        # Increment the amount of Truck still on the Track
        # For each truck, if it is still on the Track, increase its Fitness
        cars_left = 0
        for i, truck in enumerate(trucks):
            if truck.is_on_track():
                cars_left += 1
                truck.update(game_map)
                genomes[i][1].fitness += truck.add_fitness()#if the truck is on right track increase its fitness by calling add_fitness

        #get the Fitness of the Truck on the right Track with most amount of Reward in that Round       
        fit = 0
        for i, truck in enumerate(trucks):
            fit = max(fit,genomes[i][1].fitness)

        #after, if all truck has crashed, break out of the loop
        if cars_left == 0:
            break

        #Stop the loop after 30 Seconds so it doesnt continue once it finds the right path forever
        count_time += 1
        if count_time == 60 * 40: 
            break   

        #Render the Truck on the screen if truck is still on the Track
        screen.blit(game_map, (0, 0))
        for truck in trucks:
            if truck.is_on_track():
                truck.draw(screen)
        

        # Display Test Stats
        text = cycle_font.render("Current Cycle: " + str(current_cycle), True, (200, 10, 0))
        text_rect = text.get_rect()
        text_rect.center = (95, 20)
        screen.blit(text, text_rect)

        text = on_track_font.render("Cars Left: " + str(cars_left), True, (50, 50, 0))
        text_rect = text.get_rect()
        text_rect.center = (53, 50)
        screen.blit(text, text_rect)
        
        text = on_track_font.render("Highest Fitness: " + str(fit), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (150, 75)
        screen.blit(text, text_rect)



        pygame.display.update()#updates the whole screen since no arguement passed in
        clock.tick(60) 


         

#Main fucntion
if __name__ == "__main__":
    
    # Setting up Configuritation
    config_path = "./config.txt"
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    # Create NEAT Population Class with the amount of trucks in using Config Population value
    pop = neat.Population(config)

    #Add Reporters for result of the Simulation
    #A Simulation lasts max given Fitness Threshold
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    
    # Run For A Maximum of 500 Cycles or Maximum Fitness Threshold
    pop.run(run_test, 500)
