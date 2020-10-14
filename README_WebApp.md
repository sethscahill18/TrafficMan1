# Web Application
> Permit a user to share their location in real-time with the traffic management system. 

This project aims to create a method which allows road users to share their location with a traffic management system throughout the journey. The Web App was created as a tool to faciliate this action. The Web App achieved this by performing the following functionality:
1. Web App can be opened on any mobile device which possesses GPS capability.
2. The user must register an account. The Web App enables the user to input their details and sends the information to Firebase for authenification.
3. The user must select the road user option as they wish to share their GPS location. The Web App provides this option to the user and requests access from the user's device to use its GPS capability.
4. The user must commence the sharing of GPS location by confirming the trip has begun. The Web App displays this option to the user and once trip has commenced the Web App will connect to the firebase realtime database and will continuously push the user's GPS location data.
5. At the end of the trip, or at any desired moment, the user must stop sharing location. The Web App displays the option to end the trip during the trip. When slected by the user the Web App will stop sending GPS location data to the firebase realtime database adn will send a signal to the database that the trip has finished.

## Getting started

Download the code associated with Web App, this consists of two javascript and one HTML script. 
Open in the code editor which supports Javascript and HTML.
To view the User Interface of the Web App simply run the html script.

To activate the full functionality of the Web App an established Google firebase account is required. Firebase possesses features that enable the creation of a live Web App. The features nesscessary in this case are: user authenification, web hosting service and access to a real-time cloud database. The unique details corresponding to the created firebase account must be input into the HTML script under the section titled "Web app's Firebase configuration unique codes" this will connect the Web App to teh firebase features/services.

## Developing

## Features

---

The functionality of the program is to simulate different traffic scenarios and calculate the value of performance parameters to assess the system. The programs enable a high level of customisation. The layout of the road network can be altered to mimic any desired layout. The traffic which passes through the road network can be can fully defined prior to the simualtion as the route taken by each vehicle can be specified. The traffic light signal control system, which permits vehicles to progress through the road network, can be fully customised.

## Configuration
The user can enter simple argument changes to alter the input to the simulation and thus permit experimentation to find the affect on the performance of the system. These arguments include: the total number of cars which will participate in the simulation (num_cars); the number of cars that will start in the system (num_initial_internal_cars); the time interval between a set of new cars entering the system (car_entry_interval_timer_limit); the number of cars in each set which enter the simulation (new_cars_per_interval) and the length of the time the simulation will run (time_limit). Changing the value of these arguments 

# Links

In the repository of this project (link to repository) there are three scripts of code which simulate different traffic scenarios. The first of which, traffic_code_1.py, simulates a complex road network which consists of atypical junctions and layouts inspired from a street map of New York. This script demonstrates the high level of customisability of the road network afforded to the user by the program. This enables the user to assess the impact on traffic flow of different road networks. (basically allowing the user to design and simulate any road layout that they wish.)
A video displaying the simulation created from this script can be found at the following link: https://www.youtube.com/watch?v=CfFbRqDhEjk

The following two scripts, traffic_code_2.py and traffic_code_3.py, share the same road network such that the two can be compared to assess the impact of different sign control systems. The road network used in both simualtions is a simple grid system which consists of a predetermined number of equally spaced junctions. The traffic_code_2 script implements a set timer cyclical control system. This means that each traffic signal at a junction will be green for the same amount of time, hence being referred to as a "set timer". Furthermore, the order of which the traffic signals at a junction turn green follows a preset sequence and as time passes the traffic signals will continuously loop through this sequence, this is described as the "cyclical" nature of the control system. The second script, traffic_code_3, employs at adaptive control system which varies the length of time a traffic signal is green and once the green period for a traffic signal has ended any traffic signal at the junction could be selected to turn green next, hence the control system does not follow a predefined sequence. This program is thus adaptable and not predefined. (tempted not to mention that it is repsonsive to the current traffic situation.) Once both sample codes are completed the traffic flow performance parameters are calculated and displayed. This allows for a comparison to be made between the different signal control systems.

A video displaying the simulation generated by sample code stage_16_1, set timer control system, can be found at the following link: https://www.youtube.com/watch?v=igwDY0FWk_w

A video displaying the simulation generated by sample code stage_16_2, adaptive control system, can be found at the following link: https://www.youtube.com/watch?v=9e6TX1xMXc8&t=41s


