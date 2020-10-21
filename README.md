
# Traffic Management
> Understanding/quanityfing the impact of traffic system variables and thier subsequent management to enchance traffic flow. 

This project aims to explore the impact of the road network, control signal programming and the behaviour of vehicles on traffic flow.  The creation and customisation of realistic simulations provide accurate information regarding traffic flow performance parameters. This information can be used to improve decision making to increase traffic flow efficiency.

## Getting started

Download the code for the simulation of your choice. 

Open in a code editor which supports Python.

Install necessary Python packages as listed at the top of the Python script.

Execute the code to initiate the simulation and a graphic window will pop up displaying the vehicles in the road network.

## Developing

## Features

The functionality of the program is to simulate different traffic scenarios and calculate the value of performance parameters to assess the system. The programs enable a high level of customisation. The layout of the road network can be altered to mimic any desired layout. The traffic which passes through the road network can be can fully defined prior to the simulation as the route taken by each vehicle can be specified. The traffic light signal control system, which permits vehicles to progress through the road network, can be fully customised.

## Configuration
The user can change simple variable arguments to alter the input to the simulation. Experimentation of these arguments allows the user to derive their affect on the traffic system performance. These arguments include: the total number of cars which will participate in the simulation (num_cars); the number of cars that will intiialy be present in the system (num_initial_internal_cars); the time interval between sets of new cars entering the system (car_entry_interval_timer_limit); the number of cars in each set which enters the system (new_cars_per_interval) and the length of the time the simulation will run (time_limit). Changing the value of these arguments will alter the behaviour of the traffic in the system. 

# Further Information & Links

In the repository of this project (https://github.com/sethscahill18/TrafficMan1) there are three scripts of code which simulate different traffic scenarios. The first of these, traffic_code_1.py, simulates a complex road network which consists of atypical junctions and layouts inspired by a street map of New York. This script demonstrates the high level of customisability of the road network afforded to the user by the program. This enables the user to assess the impact of different road networks on traffic flow.

A video showing the simulation created from this script can be found at the following link: https://www.youtube.com/watch?v=CfFbRqDhEjk

The following two scripts, traffic_code_2.py and traffic_code_3.py, share the same road network such that they can be compared to assess the impact of different traffic signal control methods. The road network used in both simulations is a simple grid system which consists of a predetermined number of equally spaced junctions. The traffic_code_2 script implements a set timer cyclical control method which here means that each traffic signal will show green for the same amount of time, hence referred to as a "set timer". Furthermore, the traffic signals at any given junction show green according to a preset, repeated sequence thereby generating the "cyclical" nature of the control method. The second script, traffic_code_3, employs an adaptive control system which selects the most appropriate traffic signal at the junction to show green and determines the amount of time it will remain in this setting. The traffic flow performance parameters are calculated and displayed when both sample codes are finished. This allows for a comparison to be made between the different traffic signal control methods.

A video showing the simulation generated by sample code traffic_code_2, the set timer cyclical control method, can be found at the following link: https://www.youtube.com/watch?v=igwDY0FWk_w

A video showing the simulation generated by sample code traffic_code_3, the adaptive control method, can be found at the following link: https://www.youtube.com/watch?v=9e6TX1xMXc8&t
