# this code creates a simulate which consists of a large grid road network and an adaptive signal control system.

# A video of the simualtion created by this code can be found at: https://www.youtube.com/watch?v=9e6TX1xMXc8&t

import time
import threading
from threading import *
from tkinter import *
import math
import statistics
import random
from statistics import mode
from statistics import mean
from fourxfour_map import four_by_four_map

tk = Tk()#initialises tk setup
canvas = Canvas(tk, width=600, height=600)
tk.title("Drawing")
canvas.pack() #create window show it on the screen
tk.update()
running_check = 1

#####
class Control_display:
    def __init__(self,x2, y2,lanes_test,id_num,lw_half):
        self.colour = "blank"
        lane_angle_from_vert = lanes_test[id_num].points_with_angles[-2][2] # angle leaving second last point, ie. the angle approaching the last point
        lane_end_x = lanes_test[id_num].points[-1][0]
        lane_end_y = lanes_test[id_num].points[-1][1]
        offset_dist = int(lw_half/2)
        x_offset = offset_dist*math.sin(lane_angle_from_vert)
        y_offset = offset_dist*math.cos(lane_angle_from_vert)
        light_centre_x = lane_end_x + x_offset
        light_centre_y = lane_end_y - y_offset

        light_angle_from_vert = lane_angle_from_vert - (math.pi/2)

        # light_length = int(lw_half/1)
        light_length = int(lw_half/1.5)
        # light_width = int(lw_half/2)
        light_width = int(lw_half/3)

        front_side_point_x = light_centre_x + light_length*math.sin(light_angle_from_vert)
        front_side_point_y = light_centre_y - light_length*math.cos(light_angle_from_vert)
        rear_side_point_x = light_centre_x - light_length*math.sin(light_angle_from_vert)
        rear_side_point_y = light_centre_y + light_length*math.cos(light_angle_from_vert)

        x1_corner = front_side_point_x + light_width*math.sin(light_angle_from_vert - (math.pi/2))
        y1_corner = front_side_point_y - light_width*math.cos(light_angle_from_vert - (math.pi/2))

        x2_corner = front_side_point_x - light_width*math.sin(light_angle_from_vert - (math.pi/2))
        y2_corner = front_side_point_y + light_width*math.cos(light_angle_from_vert - (math.pi/2))

        x3_corner = rear_side_point_x - light_width*math.sin(light_angle_from_vert - (math.pi/2))
        y3_corner = rear_side_point_y + light_width*math.cos(light_angle_from_vert - (math.pi/2))

        x4_corner = rear_side_point_x + light_width*math.sin(light_angle_from_vert - (math.pi/2))
        y4_corner = rear_side_point_y - light_width*math.cos(light_angle_from_vert - (math.pi/2))

        # canvas.coords(self.body, x1_corner,y1_corner, x2_corner,y2_corner, x3_corner,y3_corner, x4_corner,y4_corner)

        # self.light = canvas.create_oval(light_centre_x-2,light_centre_y-2,light_centre_x+2,light_centre_y+2)
        self.light = canvas.create_polygon(x1_corner,y1_corner, x2_corner,y2_corner, x3_corner,y3_corner, x4_corner,y4_corner)
        self.lane  = id_num
        # if lanes_test[id_num].orien == 3:#'l_to_r':
        #     self.light = canvas.create_rectangle(x2+int(lw/10),y2+int(lw/5),x2+(2*(int(lw/10))),y2+(lw)-int(lw/5),outline="")
        #     self.lane = id_num
        # if lanes_test[id_num].orien == 1:#'r_to_l':
        #     self.light = canvas.create_rectangle(x2-int(lw/10),y2+int(lw/5),x2-(2*(int(lw/10))),y2+(lw)-int(lw/5), outline="")
        #     self.lane = id_num
        # if lanes_test[id_num].orien == 0:#'t_to_b':
        #     self.light = canvas.create_rectangle(x2-int(lw/5),y2+int(lw/10),x2-(lw)+int(lw/5),y2+(2*(int(lw/10))),outline="")
        #     self.lane = id_num
        # if lanes_test[id_num].orien == 2:#'b_to_t':
        #     # print("running")
        #     self.light = canvas.create_rectangle(x2+int(lw/5),y2-int(lw/10),x2+(lw)-int(lw/5),y2-(2*(int(lw/10))),outline="")
        #     # canvas.create_rectangle(x2+7,y2+7,x2-7,y2-7,fill = "green")
        #     self.lane = id_num
    def turn_light_green(self):
        self.colour = "green"
        canvas.itemconfig(self.light, fill="green")
        canvas.itemconfig(self.light, outline="green")
    def turn_off_light(self):
        self.colour = "blank"
        canvas.itemconfig(self.light, fill="")
        canvas.itemconfig(self.light, outline="")
    def turn_light_red(self):
        self.colour = "red"
        canvas.itemconfig(self.light, fill="red")
        canvas.itemconfig(self.light, outline="red")
#####
class Car:
    def __init__(self, pos_x, pos_y,i):
        self.id = i
        self.time = 0
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.angle = 0
        self.pos_x_temp = pos_x
        self.pos_y_temp = pos_y
        self.coords = [pos_x, pos_y]
        self.coord_x_hist = []
        self.coord_y_hist = []
        self.current_lane = 9999
        self.previous_lane = 9999
        self.next_lane = 9999
        self.current_zone = 9999
        self.next_zone = 9999
        self.start_zone = 9999
        self.end_zone = 9999
        self.colour = random.choice(colour_choice)
        self.time_in_sys = 0
        self.wait_score = 0
        self.compass = random.uniform(0,math.pi)
        # self.perimeter = canvas.create_rectangle((pos_x-10),(pos_y-10),(pos_x+10),(pos_y+10),dash=(4, 2))
        # self.body = canvas.create_rectangle((pos_x - 1),(pos_y - 2),(pos_x + 1),(pos_y + 2),fill = self.colour)
        # self.body = canvas.create_rectangle((pos_x - 10),(pos_y - 20),(pos_x + 10),(pos_y + 20),fill = self.colour)
        # self.body = canvas.create_polygon((pos_x - 10),(pos_y - 20), (pos_x - 10),(pos_y + 20), (pos_x + 10),(pos_y + 20), (pos_x + 10),(pos_y - 20), fill = self.colour)
        self.body = canvas.create_polygon(100,200, 100,400, 200,400, 200,200, fill = self.colour)
        self.path_opt = 0# this is the path option the car will follow from the set paths
        self.g_zone = 9999
        self.g_avg_x = 0
        self.g_avg_y = 0
        self.path_step = 0
        self.potential_lanes = []
        self.potential_lanes_common = []
        self.potential_points = []
        self.potential_lanes_1 = []
        self.potential_points_1 = []
        self.potential_lanes_2 = []
        self.potential_points_2 = []
        self.potential_points_common = []
        self.loca_lane = 9999
        self.pot_next_points_with_lane_id = []
        self.move_check_store = []
        self.localised = 0 # if 0 = not localised, if 1 = localised, if 2 = trieed to localised but unable to so only need to run
        self.g_lane = 9999
        self.fut_pos = [] # 1st value is x coord, 2nd value is y coord, 3rd value is orientation (1 = vertical, 0 = horizontal)
        self.fut_pos_psuedo = []
        self.lane_history = [] #stores the path through the lanes the car has taken
        self.space_to_change_lane = 0 #if there is space for car in next lane this = 1, if no space = 0, if exiting = 2
        self.step = 0
        self.step_in_current_lane = 0
        self.step_tracker = []
        self.move_status = 0
        self.time_in_current_lane = 0
        self.time_in_g_lane = 0
        self.current_end_pos = []
        self.wait_time = 0
        self.move_time = 0
        self.time_in_system = 0
        self.car_in_system = 0 # 0 represents FALSE, 1 represents TRUE
        self.wait_time_to_enter_system = 0
        self.car_waiting_to_enter_system = 0 # 0 represents FALSE, 1 represents TRUE
        self.wait_time_in_queue = 0
        self.car_waiting_in_queue = 0 # 0 represents FALSE, 1 represents TRUE
        self.move_time = 0
        self.car_moving = 0 # 0 represents FALSE, 1 represents TRUE
        self.lane_step = 0
        self.path = []
        self.localised = 0
        self.localised_stage = 0
        self.orig_coords = []
        self.recent_coords = []
        self.g_track_path = []
        self.g_lane_line_tracker = []
        self.g_lane_temp = 9999
        self.g_wait_time = 0
        self.sampling_check = 0
        self.side_points_1 = []
        self.side_points_2 = []
        self.front_queue_check = 0
        self.current_end_step = 0
        self.current_end_step_tracker = []
        self.current_lane_end_step = 0
        self.updated_current_end_step = 0
        self.end_step_for_current_lane = 0
        self.move_status_tracker = []
        self.potential_lanes_lines_1 = []
        self.dist_lane_forward_points_1 = []
        self.potential_lanes_lines_2 = []
        self.localisation_lanes_common = []
        self.dist_lane_forward_points_lanes_common = []
        self.sampling_checker = 0


    def car_on_angle(self,pos_x,pos_y,car_width,car_length,car_angle_from_vert):
        #canvas.coords(self.body,(pos_x - 20),(pos_y - 10),(pos_x + 20),(pos_y + 10))
        # offset_store =
        side_1_point_x = pos_x - car_width*math.cos(car_angle_from_vert - (math.pi/2))
        side_1_point_y = pos_y - car_width*math.sin(car_angle_from_vert - (math.pi/2))
        side_2_point_x = pos_x + car_width*math.cos(car_angle_from_vert - (math.pi/2))
        side_2_point_y = pos_y + car_width*math.sin(car_angle_from_vert - (math.pi/2))

        x1 = side_1_point_x + car_length*math.sin(car_angle_from_vert)
        y1 = side_1_point_y + car_length*math.cos(car_angle_from_vert)
        x2 = side_1_point_x - car_length*math.sin(car_angle_from_vert)
        y2 = side_1_point_y - car_length*math.cos(car_angle_from_vert)
        x3 = side_2_point_x - car_length*math.sin(car_angle_from_vert)
        y3 = side_2_point_y - car_length*math.cos(car_angle_from_vert)
        x4 = side_2_point_x + car_length*math.sin(car_angle_from_vert)
        y4 = side_2_point_y + car_length*math.cos(car_angle_from_vert)

        x1t = pos_x + car_length*math.sin(car_angle_from_vert)
        y1t = pos_y - car_length*math.cos(car_angle_from_vert)


        front_side_point_x = pos_x + car_length*math.sin(car_angle_from_vert)
        front_side_point_y = pos_y - car_length*math.cos(car_angle_from_vert)
        rear_side_point_x = pos_x - car_length*math.sin(car_angle_from_vert)
        rear_side_point_y = pos_y + car_length*math.cos(car_angle_from_vert)

        x1_corner = front_side_point_x + car_width*math.sin(car_angle_from_vert - (math.pi/2))
        y1_corner = front_side_point_y - car_width*math.cos(car_angle_from_vert - (math.pi/2))

        x2_corner = front_side_point_x - car_width*math.sin(car_angle_from_vert - (math.pi/2))
        y2_corner = front_side_point_y + car_width*math.cos(car_angle_from_vert - (math.pi/2))

        x3_corner = rear_side_point_x - car_width*math.sin(car_angle_from_vert - (math.pi/2))
        y3_corner = rear_side_point_y + car_width*math.cos(car_angle_from_vert - (math.pi/2))

        x4_corner = rear_side_point_x + car_width*math.sin(car_angle_from_vert - (math.pi/2))
        y4_corner = rear_side_point_y - car_width*math.cos(car_angle_from_vert - (math.pi/2))

        points_test = [pos_x,pos_y,rear_side_point_x,rear_side_point_y]           # ,front_side_point_x,front_side_point_y] # ,rear_side_point_x,rear_side_point_y]
        points_test_1 = [pos_x,pos_y,front_side_point_x,front_side_point_y]
        points_test_corner_1 = [pos_x,pos_y,x1_corner,y1_corner]
        points_test_corner_2 = [pos_x,pos_y,x2_corner,y2_corner]
        points_test_corner_3 = [pos_x,pos_y,x3_corner,y3_corner]
        points_test_corner_4 = [pos_x,pos_y,x4_corner,y4_corner]
        points_new = [x1_corner,y1_corner,x2_corner,y2_corner,x3_corner,y3_corner,x4_corner,y4_corner]

        car_points = [x1_corner,y1_corner,x2_corner,y2_corner,x3_corner,y3_corner,x4_corner,y4_corner]
        # canvas.create_polygon(car_points, outline='#f11', fill='#1f1', width=2)
        # 315.0, 431.0, 315.0, 471.0, 315.0, 479.0, 315.0, 439.0]

        x_offset = car_length*math.sin(car_angle_from_vert)
        y_offset = car_length*math.cos(car_angle_from_vert)

        # print("coords: " + str(car_points))
        # canvas.coords(self.body, 315.0, 431.0, 315.0, 471.0, 315.0, 479.0, 315.0, 439.0)
        canvas.coords(self.body, x1_corner,y1_corner, x2_corner,y2_corner, x3_corner,y3_corner, x4_corner,y4_corner)

    def car_horz(self,pos_x,pos_y,car_width,car_length):
        #canvas.coords(self.body,(pos_x - 20),(pos_y - 10),(pos_x + 20),(pos_y + 10))
        canvas.coords(self.body,(pos_x - car_length),(pos_y - car_width),(pos_x + car_length),(pos_y + car_width))
    def car_vert(self,pos_x,pos_y,car_width,car_length):
        #canvas.coords(self.body,(pos_x - 10),(pos_y - 20),(pos_x + 10),(pos_y + 20))
        canvas.coords(self.body,(pos_x - car_width),(pos_y - car_length),(pos_x + car_width),(pos_y + car_length))
#####
class Zone:
    def __init__(self,x1,y1,x2,y2,zone_num,junc_num,zone_type,zone_orien,zone_num_tot,lanes_in_zone):
        #self.boundary = canvas.create_rectangle(x1, y1, x2, y2)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.zone_id = [zone_num,junc_num] #1st is junction, 2nd is zone number
        self.individ_num = zone_num_tot
        self.num_cars_in_zone = 0
        self.cars_in_zone_id = []
        self.next_zones = []
        self.good_zones = []
        self.bad_zones = []
        self.score = 0
        self.time_green = 0
        self.wait_score = 0
        self.type = 0 #if 0 is an exit zone, if 1 is a entry zone, if 2 is an internal zone
        self.orien = 0 #if top to bottom = 0,if right to left = 1, if b to top = 2, if r to left = 3 or use zone.id
        self.control_num  = 9999 #  the number of the control for this zone , 99 is control for exit zones
        self.lanes_in_zone = lanes_in_zone
        self.compass = 0
        self.g_num_cars_in_zone = 0
        self.g_cars_in_zone_id = []
        self.time_green = 0
#####
class Lane_test:
    # def __init__(self,junc_pos,points): # ,diff_x,diff_y,abs_diff_x,abs_diff_y,theta,line_grad,line_len,angle_from_vert,line_quadrant):
    def __init__(self,x1,y1,x2,y2,lane_num,zone_num,junc_num,lane_type,lane_orien,zone_individ_num,lane_reverse,lane_polar):
        #self.boundary = canvas.create_rectangle(x1, y1, x2, y2)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.type = lane_type #if 0 is an exit zone, if 1 is a entry zone, if 2 is an internal zone
        self.orien = lane_orien #if top to bottom = 0,if right to left = 1, if b to top = 2, if left to right = 3 or use zone.id
        self.lane_id = lane_num
        self.map_lane_id = lane_num # map_lane_id is the reference on the visual map, this will not always equal lane_id as certain numbers may be missed when creating the map and numbering the lanes
        self.junc_num = 9999
        self.junc_num_leaving = 9999
        self.points = [] # [x,y] point coordinates
        self.centre_line_end = []
        self.centre_line_start = []
        self.centre_line_x_list = []
        self.centre_line_y_list = []
        self.end_point = []
        self.junc_pos = [0,0] # 2 if enters junc from side, 1 if from top or bottom, 0 doesn'y entry as is an interior point
        self.points_with_info = [] # [x,y,status,junc_pos] if first point in lane status = 1, if interior point in lane status = 2, if last point in lane status = 3; junc_pos is the position in which lane enters the junction, if junc_pos = 1 lane top or bottom (horizontal lane end) entry/exit, if junc_pos = 2 lane side (vertical lane end) entry/exit, if internal ppoint junc_pos = 0
        self.lines_info = [] # [diff_x,diff_y,abs_diff_x,abs_diff_y,theta,line_grad,line_len,angle_from_vert,line_quadrant]
        self.lines = [] # [[p1x,p1y,p2x,p2y,angle_from_vert, quadrant, line_length],[p2x,p2y,p3x,p3y,angle_from_vert, quadrant, line_length]]
        self.draw = [] #[[p1x,p1y,angle_at_1,p2x,py2,angle_at_2,angle_from_vert,quadrant],[p2x,p2y,angle_at_2,p3x,py3,angle_at_3,angle_from_vert,quadrant]]
        self.points_min = [] # [[x1,y1,status,junc_pos,angle_from_vert_at_point], [x2,y2,...],...]
        # self.points_with_angles = [] # [[x1,y1,angle_from_vert_at_point,line_quadrant going from point, angle of line of side points], [x2,y2,...],...]
        self.points_with_angles = [] # [[x1,y1,angle_of line_leaving_point_from_vertical,line_quadrant going from point, angle of line of side points], [x2,y2,...],...]
        self.points_outer_line = []
        self.points_inner_line = []
        self.angle_side_points_on = []
        self.side_points = []
        self.upper_line_points = []
        self.lower_line_points = []
        self.points_info_min = [] # [[x1,y1,angle_of_line_leaving_point], [x2,y2,angle_of_line_leaving_point]]
        self.move_points = [] # stores all the points the cars will use to navigate along lins in lane
        self.cars_in_lane_id = []
        self.next_lanes = [] # lanes folllowing on from this lane
        self.next_map_lanes_id = []
        self.assoc_lanes = [] # lanes that run in conjuction with this Lane_test, ie. lanes in the same direction next to each other
        self.free_turn_next_lanes = [] # these are next_lanes that the car can move into freely, ie. no controlled by a traffic light, just a simple turn and move into lane if there is space
        self.free_turn_next_lanes_map_id = []
        self.end_point_for_free_turn_next_lanes = [] #[[next_Lane_test,x value for end_point_in_current_lane_for_moving_to_next_Lane_test,y value for end_point_in_current_lane_for_moving_to_next_lane],[...]]
        self.free_turn_next_lane_points = [] # [[next_Lane_test,point1x,point1y],[next_Lane_test,point2x,point2y]]
        self.free_turn_next_lane_points_with_angles = [] # [[next_Lane_test,[point1x,point1y,angle_line_leaving]],[..[...,...]]]
        self.free_turn_next_lane_move_points = [] # [[next_lane2,[move_point1x,move_point1y,angle_from_vert],[move_point2x,move_point2y,angle_from_vert],[...]],[next_lane2,[...,...]]]
        self.current_end_step = 0
        self.next_lanes_intersection = [] # [[next_lane_option,intersection_point_x,intersection_point_y],[next_lane_option,...]]
        self.next_lanes_transition_points = [] # [[next_lane_option,transition_point1_x, transition_point_1_y,angle_line_leaving_move_point],[next_lane_option,transition_point_2_x,transition_point_2_y,angle_leaving_move_point_2],...]         # used to find the transition_points between Lane_test, include last point of current Lane_test, intersction points, and first point of next lane
        self.move_points_next_lanes = [] # [[next_lane],[move_points....]]
        self.free_turn_next_lanes_intersection = []
        self.control_num = 0
        self.green_light = 0
        self.time_green = 0
        self.light_time_pause = 0
        self.g_lane_wait_time_total = 0
        self.g_cars_in_lane_id = []
        self.next_car_free_to_go = 0 # wait_offset
class Junc_test:
    # def __init__(self,junc_num,lanes_at_junc_map_id):
    def __init__(self,junc_num,centre_x,centre_y):
        self.junc_id = junc_num
        self.centre_x = centre_x
        self.centre_y = centre_y
        self.lanes_at_junc_map_id = [] #lanes_at_junc_map_id
        self.lanes_at_junc = []
        self.lanes_leaving_junc = []
        self.light_lanes_at_junc = []
        self.g_junc_total_points = 0
        self.g_cars_in_junc_id = []
        self.g_num_cars_in_junc = 0
        self.best_score = 0
        self.best_zone = 0
        self.num_cars_to_pass = 0
        self.time_green = 0
        self.lane_orien_temp = 0
        self.g_junc_wait_time_total = 0
        self.ready_for_green = 0
        self.green_lanes_at_junc = 0
        self.same_light_lanes_link_map_id = 0
        self.same_light_lanes_link = []
        self.light_times = []
        self.ready_for_new_light_times = 0
        self.light_times_index_to_make_green = 0

def create_coord(cars,car_id,rad_gps):
    theta = random.uniform(0,2*math.pi)
    r = round(random.uniform(0,rad_gps),3) # 8m is the assumed radius of gps uncertainty
    x_dev = r * math.cos(theta)
    y_dev = r * math.sin(theta)
    # cars[car_id].coords[0] = cars[car_id].pos_x_temp + x_dev
    cars[car_id].coords[0] = cars[car_id].pos_x + x_dev
    cars[car_id].coords[0] = int(cars[car_id].coords[0]) # set to integer to remove the decimal places
    # cars[car_id].coords[1] = cars[car_id].pos_y_temp + y_dev
    cars[car_id].coords[1] = cars[car_id].pos_y + y_dev
    cars[car_id].coords[1] = int(cars[car_id].coords[1]) # set to integrate to remove the decimal places
    cars[car_id].coord_x_hist.append(cars[car_id].coords[0])
    cars[car_id].coord_y_hist.append(cars[car_id].coords[1])

# set dimensions
scale_factor = 1
block_len_vertical = int(80/scale_factor)
block_len_horizontal = int(80/scale_factor) # int(80/scale_factor)
rad_gps = int(10/scale_factor)
car_length = int(4/scale_factor)
# car_length = int(10/scale_factor)
half_car_length = int(car_length/2)
car_width = int(2/scale_factor)
# lw = int(5/scale_factor)
lw = int(3/scale_factor)
lw_half = round(lw/2)
move_val = half_car_length # the size of each step
move_val = 2 # need to change this
move_val_transition = int(move_val/2)
move_val = 1
move_val_transition = 1
car_spacing = int(car_length/4)
time_interval = 0.12  # gives average speed through a lane to be 19.6 mph equal to 31 kph
sampling_time = time_interval * 50 # if in realtime will equal 5
sampling_time = 5

zones = []
controls = [] #stores control object data
lanes_test = []
juncs_test = []

colour_choice = [["black"],["black"]]

tdx = block_len_horizontal
tdy = block_len_vertical
stx = 0 #the min point in x direction
sty= 0 #the min point in y direction

jlx = block_len_horizontal#jl = join length in x direction, the length of road to the next junction
jly = block_len_vertical #jl = join length in y direction, the length of road to the next junction
junc_counter = 0
zone_counter = 0
lane_counter = 0
zone_num_tot = 0

def create_t_l_Junc_test(juncs_test,Junc_test,zones,Zone,lanes_test,Lane_test,tk,lw,canvas,Canvas,tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot):
    # junc_counter = 0
    ##########junction 0
    #top left corner juntion
    junc_num = junc_counter
    juncs_test.append(Junc_test(junc_counter,(tdx+lw),(tdy+lw)))
    junc_center = [tdx+lw,tdy+lw]
    # canvas.create_oval(junc_center[0] + 10,junc_center[1] + 10,junc_center[0] - 10,junc_center[1] - 10 )
    tk.update()
    print("junc_center[1]: " + str(junc_center[1]))
    lanes_at_junc_store = []
    num_lanes_to_create = 8
    centre_zone_0 = [junc_center[0],(junc_center[1] - lw)]
    # canvas.create_oval(centre_zone_0[0] + 10,centre_zone_0[1] + 10,centre_zone_0[0] - 10,centre_zone_0[1] - 10 )
    tk.update()
    lane_0_centreline_start = [(centre_zone_0[0] - lw_half),(centre_zone_0[1])]
    lane_0_centreline_end = [(centre_zone_0[0] - lw_half),(centre_zone_0[1] - jly)]
    lane_1_centreline_start = [(centre_zone_0[0] + lw_half),(centre_zone_0[1] - jly)]
    lane_1_centreline_end = [(centre_zone_0[0] + lw_half),(centre_zone_0[1])]
    centre_zone_1 = [(junc_center[0] + lw),(junc_center[1])]
    lane_2_centreline_start = [(centre_zone_1[0]),(centre_zone_1[1] - lw_half)]
    lane_2_centreline_end = [(centre_zone_1[0] + jlx),(centre_zone_1[1] - lw_half)]
    lane_3_centreline_start = [(centre_zone_1[0] + jlx),(centre_zone_1[1] + lw_half)]
    lane_3_centreline_end = [(centre_zone_1[0]),(centre_zone_1[1] + lw_half)]
    centre_zone_2 = [(junc_center[0]),(junc_center[1] + lw)]
    lane_4_centreline_start = [(centre_zone_2[0] + lw_half),(centre_zone_2[1])]
    lane_4_centreline_end = [(centre_zone_2[0] + lw_half),(centre_zone_2[1] + jly)]
    lane_5_centreline_start = [(centre_zone_2[0] - lw_half),(centre_zone_2[1] + jly)]
    lane_5_centreline_end = [(centre_zone_2[0]  - lw_half),(centre_zone_2[1])]
    centre_zone_3 = [(junc_center[0] - lw),(junc_center[1])]
    lane_6_centreline_start = [(centre_zone_3[0]),(centre_zone_3[1] + lw_half)]
    lane_6_centreline_end = [(centre_zone_3[0] - jlx),(centre_zone_3[1] + lw_half)]
    lane_7_centreline_start = [(centre_zone_3[0] - jlx),(centre_zone_3[1] - lw_half)]
    lane_7_centreline_end = [(centre_zone_3[0]),(centre_zone_3[1] - lw_half)]
    # for i in range(num_lanes_to_create):

        # lanes_at_junc_store.append()
    # lane_0_y_start = junc_center[1] - lw
    # lane_0_y_end = junc_center[1] - lw - jly
    # lane_1_y_start = junc_center[1] - lw
    # lane_1_y_end = junc_center[1] - lw - jly
    # lane_0_x_start = junc_center[0] - lw_half
    # lane_0_x_start = junc_center[0] - lw_half
    # lane_1_x_start = junc_center[0] + lw_half
    # lane_1_x_start = junc_center[0] + lw_half
    # zone_counter = 0
    # lane_counter = 0
    # zone_num_tot = 0
    # turn_info = 0
    junc_first_zone = zone_num_tot
    # zone 0
    # canvas.create_line(tdx,sty,tdx,tdy,width=2)
    # canvas.create_line(tdx+lw,sty,tdx+lw,tdy)
    # canvas.create_line(tdx+(2*lw),sty,tdx+(2*lw),tdy,width=2)
    # canvas.create_line(tdx+lw,tdy,tdx+(2*lw),tdy,dash=(4,1))

    zone_type = 1
    zone_orien = zone_counter
    lane_orien = zone_counter

    zones.append(Zone(tdx+(2*lw),sty,tdx,tdy,zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1])) # junc 0, zone 0
    # canvas.create_rectangle(zones[zone_counter].x2+5,zones[zone_counter].y2+5,zones[zone_counter].x2-5,zones[zone_counter].y2-5, fill = "green" )
    # canvas.create_rectangle(zones[zone_counter].x1+5,zones[zone_counter].y1+5,zones[zone_counter].x1-5,zones[zone_counter].y1-5, fill = "yellow" )
    zones[zone_num_tot].type = zone_type #set zone type to entry zone
    # zone_counter += 1
    lane_type = 0 #exit lane
    # lane 0
    lane_orien = 2
    lane_polar = 4
    lane_reverse = 1
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y2,zones[zone_num_tot].x2,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_0_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_0_centreline_end


    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    # canvas.create_rectangle(lanes_test[lane_counter].x2+5,lanes_test[lane_counter].y2+5,lanes_test[lane_counter].x2-5,lanes_test[lane_counter].y2-5, fill = "green" )
    # canvas.create_rectangle(lanes_test[lane_counter].x1+5,lanes_test[lane_counter].y1+5,lanes_test[lane_counter].x1-5,lanes_test[lane_counter].y1-5, fill = "yellow" )
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_start[0]+5,lanes_test[lane_counter].centre_line_start[1]+5,lanes_test[lane_counter].centre_line_start[0]-5,lanes_test[lane_counter].centre_line_start[1]-5, fill = "yellow" )
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_end[0]+5,lanes_test[lane_counter].centre_line_end[1]+5,lanes_test[lane_counter].centre_line_end[0]-5,lanes_test[lane_counter].centre_line_end[1]-5, fill = "green" )



    lane_counter += 1
    # lane 1
    lane_type = 1 #entry lane
    lane_orien = 0
    lane_polar = 4
    lane_reverse = 0
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2+lw,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,zones[zone_num_tot].x1,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # canvas.create_rectangle(lanes_test[lane_counter].x2+5,lanes_test[lane_counter].y2+5,lanes_test[lane_counter].x2-5,lanes_test[lane_counter].y2-5, fill = "green" )
    # canvas.create_rectangle(lanes_test[lane_counter].x1+5,lanes_test[lane_counter].y1+5,lanes_test[lane_counter].x1-5,lanes_test[lane_counter].y1-5, fill = "yellow" )
    lanes_test[lane_counter].centre_line_start = lane_1_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_1_centreline_end


    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 + (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1+ (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_start[0]+5,lanes_test[lane_counter].centre_line_start[1]+5,lanes_test[lane_counter].centre_line_start[0]-5,lanes_test[lane_counter].centre_line_start[1]-5, fill = "yellow" )
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_end[0]+5,lanes_test[lane_counter].centre_line_end[1]+5,lanes_test[lane_counter].centre_line_end[0]-5,lanes_test[lane_counter].centre_line_end[1]-5, fill = "green" )

    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1

    # zone 1
    # canvas.create_line(tdx+(2*lw),tdy,jlx+tdx+(2*lw),tdy,width=2)
    # canvas.create_line(tdx+(2*lw),tdy+lw,jlx+tdx+(2*lw),tdy+lw)
    # canvas.create_line(tdx+(2*lw),tdy+(2*lw),jlx+tdx+(2*lw),tdy+(2*lw),width=2)
    # canvas.create_line(tdx+(2*lw),tdy+lw,tdx+(2*lw),tdy+(2*lw),dash=(4,1))
    # canvas.create_line(jlx+tdx+(2*lw),tdy,jlx+tdx+(2*lw),tdy+(lw),dash=(4,1))
    zone_type = 2
    zone_orien = zone_counter
    lane_orien = zone_counter
    lane_orien = 3
    lane_polar = 5
    zones.append(Zone(jlx+tdx+(2*lw),tdy+(2*lw),tdx+(2*lw),tdy,zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1])) # junc 0, zone 1
    zones[zone_num_tot].type = zone_type #set zone type to internal zone
    # lane 2
    lane_type = zone_type
    lane_reverse = 1
    lanes_test.append(Lane_test(zones[zone_num_tot].x2,zones[zone_num_tot].y1 - lw,zones[zone_num_tot].x1,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_2_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_2_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))   ###############

    lane_counter += 1
    # lane 3
    lane_type = zone_type
    lane_polar = 5
    lane_orien = 1
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2 + lw,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_3_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_3_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1

    # zone 2
    # canvas.create_line(tdx,tdy+(2*lw),tdx,jly+tdy+(2*lw),width=2)
    # canvas.create_line(tdx+lw,tdy+(2*lw),tdx+lw,jly+tdy+(2*lw))
    # canvas.create_line(tdx+(2*lw),tdy+(2*lw),tdx+(2*lw),jly+tdy+(2*lw),width=2)
    # canvas.create_line(tdx,tdy+(2*lw),tdx+(lw),tdy+(2*lw),dash=(4,1))
    # canvas.create_line(tdx+(lw),tdy+(2*lw)+jlx,tdx+(2*lw),tdy+(2*lw)+jlx,dash=(4,1))
    zone_type = 2
    zone_orien = zone_counter
    lane_orien = zone_counter
    zones.append(Zone(tdx+(2*lw),jly+tdy+(2*lw),tdx,tdy+(2*lw),zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1]))# junc 0, zone 2
    zones[zone_num_tot].type = zone_type #set zone type to internal zone
    # zone_counter += 1
    # lane 4
    lane_type = zone_type
    lane_orien = 0
    lane_polar = 5
    lane_reverse = 1
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y2,zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2 + (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y2,zones[zone_num_tot].x1,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # canvas.create_rectangle(lanes_test[lane_counter].x2+5,lanes_test[lane_counter].y2+5,lanes_test[lane_counter].x2-5,lanes_test[lane_counter].y2-5, fill = "green" )
    # canvas.create_rectangle(lanes_test[lane_counter].x1+5,lanes_test[lane_counter].y1+5,lanes_test[lane_counter].x1-5,lanes_test[lane_counter].y1-5, fill = "yellow" )
    lanes_test[lane_counter].centre_line_start = lane_4_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_4_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 + (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1+ (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_start[0]+5,lanes_test[lane_counter].centre_line_start[1]+5,lanes_test[lane_counter].centre_line_start[0]-5,lanes_test[lane_counter].centre_line_start[1]-5, fill = "yellow" )
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_end[0]+5,lanes_test[lane_counter].centre_line_end[1]+5,lanes_test[lane_counter].centre_line_end[0]-5,lanes_test[lane_counter].centre_line_end[1]-5, fill = "green" )
    lane_counter += 1
    #lane 5
    lane_type = zone_type
    lane_orien = 2
    lane_polar = 5
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_5_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_5_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)

    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1

    #zone 3
    # canvas.create_line(stx,tdy,tdx,tdy,width=2)
    # canvas.create_line(stx,tdy+lw,tdx,tdy+lw)
    # canvas.create_line(stx,tdy+(2*lw),tdx,tdy+(2*lw),width=2)
    # canvas.create_line(tdx,tdy,tdx,tdy+(lw),dash=(4,1))
    # canvas.create_rectangle(stx,tdy+(2*lw),tdx,tdy) # zone 3
    zone_type = 1
    zone_orien = zone_counter
    lane_orien = zone_counter
    zones.append(Zone(stx,tdy+(2*lw),tdx,tdy,zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1]))# junc 0, zone 3
    zones[zone_num_tot].type = zone_type #set zone type to entry zone
    # zone_counter += 1
    # lane 6
    lane_type = 0 #exit lane
    lane_orien = 1
    lane_polar = 4
    lane_reverse = 1
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2+lw,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test.append(Lane_test(zones[zone_num_tot].x2,zones[zone_num_tot].y2 + lw,zones[zone_num_tot].x1,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # canvas.create_rectangle(zones[zone_num_tot].x2+5,zones[zone_num_tot].y2+5,zones[zone_num_tot].x2-5,zones[zone_num_tot].y2-5, fill = "green" )
    # canvas.create_rectangle(zones[zone_num_tot].x1+5,zones[zone_num_tot].y1+5,zones[zone_num_tot].x1-5,zones[zone_num_tot].y1-5, fill = "yellow" )
    # canvas.create_rectangle(lanes_test[lane_counter].x2+5,lanes_test[lane_counter].y2+5,lanes_test[lane_counter].x2-5,lanes_test[lane_counter].y2-5, fill = "green" )
    # canvas.create_rectangle(lanes_test[lane_counter].x1+5,lanes_test[lane_counter].y1+5,lanes_test[lane_counter].x1-5,lanes_test[lane_counter].y1-5, fill = "yellow" )
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))
    lanes_test.append(Lane_test(zones[zone_num_tot].x2,zones[zone_num_tot].y2 + lw,zones[zone_num_tot].x1,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_6_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_6_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 + (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 + (lw_half))


    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_end[0]+5,lanes_test[lane_counter].centre_line_end[1]+5,lanes_test[lane_counter].centre_line_end[0]-5,lanes_test[lane_counter].centre_line_end[1]-5, fill = "green")
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_start[0]+5,lanes_test[lane_counter].centre_line_start[1]+5,lanes_test[lane_counter].centre_line_start[0]-5,lanes_test[lane_counter].centre_line_start[1]-5, fill = "yellow")
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_start[0]+5,lanes/ne_counter].centre_line_end[1]+5,lanes_test[lane_counter].centre_line_end[0]-5,lanes_test[lane_counter].centre_line_end[1]-5, fill = "green" )
    lane_counter += 1
    # lane 7
    lane_type = 1 #entry lane
    lane_orien = 3
    lane_polar = 4
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1 - lw,zones[zone_num_tot].x2,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) #straight and left turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_7_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_7_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_end[0]+5,lanes_test[lane_counter].centre_line_end[1]+5,lanes_test[lane_counter].centre_line_end[0]-5,lanes_test[lane_counter].centre_line_end[1]-5, fill = "green")
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_start[0]+5,lanes_test[lane_counter].centre_line_start[1]+5,lanes_test[lane_counter].centre_line_start[0]-5,lanes_test[lane_counter].centre_line_start[1]-5, fill = "yellow")
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1
    ###########  end of junction 0
    junc_counter += 1
    return tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot
def create_t_m_Junc_test(juncs_test,Junc_test,zones,Zone,lanes_test,Lane_test,tk,lw,canvas,Canvas,tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot):
    junc_num = junc_counter
    tdx = tdx + (2*lw) + jlx
    tdy = tdy
    juncs_test.append(Junc_test(junc_counter,(tdx+lw),(tdy+lw)))
    junc_first_zone = zone_num_tot

    junc_center = [tdx+lw,tdy+lw]
    # canvas.create_oval(junc_center[0] + 10,junc_center[1] + 10,junc_center[0] - 10,junc_center[1] - 10 )
    tk.update()
    print("junc_center[1]: " + str(junc_center[1]))
    lanes_at_junc_store = []
    num_lanes_to_create = 8
    centre_zone_0 = [junc_center[0],(junc_center[1] - lw)]
    # canvas.create_oval(centre_zone_0[0] + 10,centre_zone_0[1] + 10,centre_zone_0[0] - 10,centre_zone_0[1] - 10 )
    tk.update()
    lane_0_centreline_start = [(centre_zone_0[0] - lw_half),(centre_zone_0[1])]
    lane_0_centreline_end = [(centre_zone_0[0] - lw_half),(centre_zone_0[1] - jly)]
    lane_1_centreline_start = [(centre_zone_0[0] + lw_half),(centre_zone_0[1] - jly)]
    lane_1_centreline_end = [(centre_zone_0[0] + lw_half),(centre_zone_0[1])]
    centre_zone_1 = [(junc_center[0] + lw),(junc_center[1])]
    lane_2_centreline_start = [(centre_zone_1[0]),(centre_zone_1[1] - lw_half)]
    lane_2_centreline_end = [(centre_zone_1[0] + jlx),(centre_zone_1[1] - lw_half)]
    lane_3_centreline_start = [(centre_zone_1[0] + jlx),(centre_zone_1[1] + lw_half)]
    lane_3_centreline_end = [(centre_zone_1[0]),(centre_zone_1[1] + lw_half)]
    centre_zone_2 = [(junc_center[0]),(junc_center[1] + lw)]
    lane_4_centreline_start = [(centre_zone_2[0] + lw_half),(centre_zone_2[1])]
    lane_4_centreline_end = [(centre_zone_2[0] + lw_half),(centre_zone_2[1] + jly)]
    lane_5_centreline_start = [(centre_zone_2[0] - lw_half),(centre_zone_2[1] + jly)]
    lane_5_centreline_end = [(centre_zone_2[0]  - lw_half),(centre_zone_2[1])]


    # zone 0
    # canvas.create_line(tdx,sty,tdx,tdy,width=2)
    # canvas.create_line(tdx+lw,sty,tdx+lw,tdy)
    # canvas.create_line(tdx+(2*lw),sty,tdx+(2*lw),tdy,width=2)
    # canvas.create_line(tdx+lw,tdy,tdx+(2*lw),tdy,dash=(4,1))

    zone_type = 1
    zone_orien = zone_counter
    lane_orien = zone_counter

    zones.append(Zone(tdx+(2*lw),sty,tdx,tdy,zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1])) # junc 0, zone 0
    zones[zone_num_tot].type = zone_type #set zone type to entry zone
    # zone_counter += 1
    lane_type = 0
    # lane 0
    lane_orien = 2
    lane_polar = 4
    lane_reverse = 1
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    # # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y2)
    # # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1)
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y2,zones[zone_num_tot].x2,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_0_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_0_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lane_counter += 1
    # lane 1
    lane_type = 1
    lane_orien = 0
    lane_polar = 4
    lane_reverse = 0
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2+lw,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,zones[zone_num_tot].x1,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # canvas.create_rectangle(lanes_test[lane_counter].x2+5,lanes_test[lane_counter].y2+5,lanes_test[lane_counter].x2-5,lanes_test[lane_counter].y2-5, fill = "green" )
    # canvas.create_rectangle(lanes_test[lane_counter].x1+5,lanes_test[lane_counter].y1+5,lanes_test[lane_counter].x1-5,lanes_test[lane_counter].y1-5, fill = "yellow" )
    lanes_test[lane_counter].centre_line_start = lane_1_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_1_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 + (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1+ (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_start[0]+5,lanes_test[lane_counter].centre_line_start[1]+5,lanes_test[lane_counter].centre_line_start[0]-5,lanes_test[lane_counter].centre_line_start[1]-5, fill = "yellow" )
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_end[0]+5,lanes_test[lane_counter].centre_line_end[1]+5,lanes_test[lane_counter].centre_line_end[0]-5,lanes_test[lane_counter].centre_line_end[1]-5, fill = "green" )
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1

    # zone 1
    # canvas.create_line(tdx+(2*lw),tdy,jlx+tdx+(2*lw),tdy,width=2)
    # canvas.create_line(tdx+(2*lw),tdy+lw,jlx+tdx+(2*lw),tdy+lw)
    # canvas.create_line(tdx+(2*lw),tdy+(2*lw),jlx+tdx+(2*lw),tdy+(2*lw),width=2)
    # canvas.create_line(tdx+(2*lw),tdy+lw,tdx+(2*lw),tdy+(2*lw),dash=(4,1))
    # canvas.create_line(jlx+tdx+(2*lw),tdy,jlx+tdx+(2*lw),tdy+(lw),dash=(4,1))
    zone_type = 2
    zone_orien = zone_counter
    lane_orien = zone_counter
    lane_orien = 3
    lane_polar = 5
    zones.append(Zone(jlx+tdx+(2*lw),tdy+(2*lw),tdx+(2*lw),tdy,zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1])) # junc 0, zone 1
    zones[zone_num_tot].type = zone_type #set zone type to internal zone
    # lane 2
    lane_type = zone_type
    lane_reverse = 1
    lanes_test.append(Lane_test(zones[zone_num_tot].x2,zones[zone_num_tot].y1 - lw,zones[zone_num_tot].x1,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_2_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_2_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))   ###############

    lane_counter += 1
    # lane 3
    lane_type = zone_type
    lane_polar = 5
    lane_orien = 1
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2 + lw,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_3_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_3_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1

    # zone 2
    # canvas.create_line(tdx,tdy+(2*lw),tdx,jly+tdy+(2*lw),width=2)
    # canvas.create_line(tdx+lw,tdy+(2*lw),tdx+lw,jly+tdy+(2*lw))
    # canvas.create_line(tdx+(2*lw),tdy+(2*lw),tdx+(2*lw),jly+tdy+(2*lw),width=2)
    # canvas.create_line(tdx,tdy+(2*lw),tdx+(lw),tdy+(2*lw),dash=(4,1))
    # canvas.create_line(tdx+(lw),tdy+(2*lw)+jlx,tdx+(2*lw),tdy+(2*lw)+jlx,dash=(4,1))
    zone_type = 2
    zone_orien = zone_counter
    lane_orien = zone_counter
    zones.append(Zone(tdx+(2*lw),jly+tdy+(2*lw),tdx,tdy+(2*lw),zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1]))# junc 0, zone 2
    zones[zone_num_tot].type = zone_type #set zone type to internal zone
    # zone_counter += 1
    # lane 4
    lane_type = zone_type
    lane_orien = 0
    lane_polar = 5
    lane_reverse = 1
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2 + lw,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1)
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y2,zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2 + (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)

    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y2,zones[zone_num_tot].x1,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # canvas.create_rectangle(lanes_test[lane_counter].x2+5,lanes_test[lane_counter].y2+5,lanes_test[lane_counter].x2-5,lanes_test[lane_counter].y2-5, fill = "green" )
    # canvas.create_rectangle(lanes_test[lane_counter].x1+5,lanes_test[lane_counter].y1+5,lanes_test[lane_counter].x1-5,lanes_test[lane_counter].y1-5, fill = "yellow" )
    lanes_test[lane_counter].centre_line_start = lane_4_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_4_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 + (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1+ (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_start[0]+5,lanes_test[lane_counter].centre_line_start[1]+5,lanes_test[lane_counter].centre_line_start[0]-5,lanes_test[lane_counter].centre_line_start[1]-5, fill = "yellow" )
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_end[0]+5,lanes_test[lane_counter].centre_line_end[1]+5,lanes_test[lane_counter].centre_line_end[0]-5,lanes_test[lane_counter].centre_line_end[1]-5, fill = "green" )

    lane_counter += 1
    #lane 5
    lane_type = zone_type
    lane_orien = 2
    lane_polar = 5
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_5_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_5_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1
    ##end of this junc
    junc_counter += 1
    return tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot
def create_t_r_Junc_test(juncs_test,Junc_test,zones,Zone,lanes_test,Lane_test,tk,lw,canvas,Canvas,tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot):
    junc_num = junc_counter
    tdx = tdx + (2*lw) + jlx
    tdy = tdy
    juncs_test.append(Junc_test(junc_counter,(tdx+lw),(tdy+lw)))

    junc_center = [tdx+lw,tdy+lw]
    # canvas.create_oval(junc_center[0] + 10,junc_center[1] + 10,junc_center[0] - 10,junc_center[1] - 10 )
    tk.update()
    print("junc_center[1]: " + str(junc_center[1]))
    lanes_at_junc_store = []
    num_lanes_to_create = 8
    centre_zone_0 = [junc_center[0],(junc_center[1] - lw)]
    # canvas.create_oval(centre_zone_0[0] + 10,centre_zone_0[1] + 10,centre_zone_0[0] - 10,centre_zone_0[1] - 10 )
    tk.update()
    lane_0_centreline_start = [(centre_zone_0[0] - lw_half),(centre_zone_0[1])]
    lane_0_centreline_end = [(centre_zone_0[0] - lw_half),(centre_zone_0[1] - jly)]
    lane_1_centreline_start = [(centre_zone_0[0] + lw_half),(centre_zone_0[1] - jly)]
    lane_1_centreline_end = [(centre_zone_0[0] + lw_half),(centre_zone_0[1])]
    centre_zone_1 = [(junc_center[0] + lw),(junc_center[1])]
    lane_2_centreline_start = [(centre_zone_1[0]),(centre_zone_1[1] - lw_half)]
    lane_2_centreline_end = [(centre_zone_1[0] + jlx),(centre_zone_1[1] - lw_half)]
    lane_3_centreline_start = [(centre_zone_1[0] + jlx),(centre_zone_1[1] + lw_half)]
    lane_3_centreline_end = [(centre_zone_1[0]),(centre_zone_1[1] + lw_half)]
    centre_zone_2 = [(junc_center[0]),(junc_center[1] + lw)]
    lane_4_centreline_start = [(centre_zone_2[0] + lw_half),(centre_zone_2[1])]
    lane_4_centreline_end = [(centre_zone_2[0] + lw_half),(centre_zone_2[1] + jly)]
    lane_5_centreline_start = [(centre_zone_2[0] - lw_half),(centre_zone_2[1] + jly)]
    lane_5_centreline_end = [(centre_zone_2[0]  - lw_half),(centre_zone_2[1])]

    junc_first_zone = zone_num_tot
    # zone 0
    # canvas.create_line(tdx,sty,tdx,tdy,width=2)
    # canvas.create_line(tdx+lw,sty,tdx+lw,tdy)
    # canvas.create_line(tdx+(2*lw),sty,tdx+(2*lw),tdy,width=2)
    # canvas.create_line(tdx+lw,tdy,tdx+(2*lw),tdy,dash=(4,1))

    zone_type = 1
    zone_orien = zone_counter
    lane_orien = zone_counter

    zones.append(Zone(tdx+(2*lw),sty,tdx,tdy,zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1])) # junc 0, zone 0
    zones[zone_num_tot].type = zone_type #set zone type to entry zone
    # zone_counter += 1
    lane_type = 0
    # lane 0
    lane_orien = 2
    lane_polar = 4
    lane_reverse = 1
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y2,zones[zone_num_tot].x2,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_0_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_0_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y2)
    # # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lane_counter += 1
    # lane 1
    lane_type = 1
    lane_orien = 0
    lane_polar = 4
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,zones[zone_num_tot].x1,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_1_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_1_centreline_end

    # canvas.create_rectangle(lanes_test[lane_counter].x2+5,lanes_test[lane_counter].y2+5,lanes_test[lane_counter].x2-5,lanes_test[lane_counter].y2-5, fill = "green" )
    # canvas.create_rectangle(lanes_test[lane_counter].x1+5,lanes_test[lane_counter].y1+5,lanes_test[lane_counter].x1-5,lanes_test[lane_counter].y1-5, fill = "yellow" )
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 + (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1+ (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_start[0]+5,lanes_test[lane_counter].centre_line_start[1]+5,lanes_test[lane_counter].centre_line_start[0]-5,lanes_test[lane_counter].centre_line_start[1]-5, fill = "yellow" )
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_end[0]+5,lanes_test[lane_counter].centre_line_end[1]+5,lanes_test[lane_counter].centre_line_end[0]-5,lanes_test[lane_counter].centre_line_end[1]-5, fill = "green" )
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2+lw,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_start[0]+5,lanes_test[lane_counter].centre_line_start[1]+5,lanes_test[lane_counter].centre_line_start[0]-5,lanes_test[lane_counter].centre_line_start[1]-5, fill = "yellow" )
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_end[0]+5,lanes_test[lane_counter].centre_line_end[1]+5,lanes_test[lane_counter].centre_line_end[0]-5,lanes_test[lane_counter].centre_line_end[1]-5, fill = "green" )
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1

    # zone 1
    # canvas.create_line(tdx+(2*lw),tdy,jlx+tdx+(2*lw),tdy,width=2)
    # canvas.create_line(tdx+(2*lw),tdy+lw,jlx+tdx+(2*lw),tdy+lw)
    # canvas.create_line(tdx+(2*lw),tdy+(2*lw),jlx+tdx+(2*lw),tdy+(2*lw),width=2)
    # canvas.create_line(tdx+(2*lw),tdy+lw,tdx+(2*lw),tdy+(2*lw),dash=(4,1))
    zone_type = 2
    zone_orien = zone_counter
    lane_orien = zone_counter
    lane_orien = 3
    lane_polar = 5
    zones.append(Zone(jlx+tdx+(2*lw),tdy+(2*lw),tdx+(2*lw),tdy,zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1])) # junc 0, zone 1
    zones[zone_num_tot].type = zone_type #set zone type to internal zone
    # lane 2
    lane_type = 0
    lane_reverse = 1
    lanes_test.append(Lane_test(zones[zone_num_tot].x2,zones[zone_num_tot].y1 - lw,zones[zone_num_tot].x1,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_2_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_2_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))   ###############

    lane_counter += 1
    # lane 3
    lane_type = 1
    lane_polar = 5
    lane_orien = 1
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2 + lw,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_3_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_3_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1

    # zone 2
    # canvas.create_line(tdx,tdy+(2*lw),tdx,jly+tdy+(2*lw),width=2)
    # canvas.create_line(tdx+lw,tdy+(2*lw),tdx+lw,jly+tdy+(2*lw))
    # canvas.create_line(tdx+(2*lw),tdy+(2*lw),tdx+(2*lw),jly+tdy+(2*lw),width=2)
    # canvas.create_line(tdx,tdy+(2*lw),tdx+(lw),tdy+(2*lw),dash=(4,1))
    # canvas.create_line(tdx+(lw),tdy+(2*lw)+jlx,tdx+(2*lw),tdy+(2*lw)+jlx,dash=(4,1))
    zone_type = 2
    zone_orien = zone_counter
    lane_orien = zone_counter
    zones.append(Zone(tdx+(2*lw),jly+tdy+(2*lw),tdx,tdy+(2*lw),zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1]))# junc 0, zone 2
    zones[zone_num_tot].type = zone_type #set zone type to internal zone
    # zone_counter += 1
    # lane 4
    lane_type = zone_type
    lane_orien = 0
    lane_polar = 5
    lane_reverse = 1
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2 + lw,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1)
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y2,zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2 + (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y2,zones[zone_num_tot].x1,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # canvas.create_rectangle(lanes_test[lane_counter].x2+5,lanes_test[lane_counter].y2+5,lanes_test[lane_counter].x2-5,lanes_test[lane_counter].y2-5, fill = "green" )
    # canvas.create_rectangle(lanes_test[lane_counter].x1+5,lanes_test[lane_counter].y1+5,lanes_test[lane_counter].x1-5,lanes_test[lane_counter].y1-5, fill = "yellow" )
    lanes_test[lane_counter].centre_line_start = lane_4_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_4_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 + (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1+ (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_start[0]+5,lanes_test[lane_counter].centre_line_start[1]+5,lanes_test[lane_counter].centre_line_start[0]-5,lanes_test[lane_counter].centre_line_start[1]-5, fill = "yellow" )
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_end[0]+5,lanes_test[lane_counter].centre_line_end[1]+5,lanes_test[lane_counter].centre_line_end[0]-5,lanes_test[lane_counter].centre_line_end[1]-5, fill = "green" )
    lane_counter += 1
    #lane 5
    lane_type = zone_type
    lane_orien = 2
    lane_polar = 5
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_5_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_5_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1
    ###########  end of this junction
    junc_counter += 1
    return tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot
def create_m_m_Junc_test(juncs_test,Junc_test,zones,Zone,lanes_test,Lane_test,tk,lw,canvas,Canvas,tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot):
    junc_num = junc_counter
    tdx = tdx + (2*lw) + jlx
    tdy = tdy
    juncs_test.append(Junc_test(junc_counter,(tdx+lw),(tdy+lw)))
    junc_first_zone = zone_num_tot
    junc_center = [tdx+lw,tdy+lw]
    # canvas.create_oval(junc_center[0] + 10,junc_center[1] + 10,junc_center[0] - 10,junc_center[1] - 10 )
    tk.update()
    print("junc_center[1]: " + str(junc_center[1]))
    lanes_at_junc_store = []
    num_lanes_to_create = 8
    centre_zone_0 = [junc_center[0],(junc_center[1] - lw)]
    # canvas.create_oval(centre_zone_0[0] + 10,centre_zone_0[1] + 10,centre_zone_0[0] - 10,centre_zone_0[1] - 10 )
    tk.update()
    centre_zone_1 = [(junc_center[0] + lw),(junc_center[1])]
    lane_2_centreline_start = [(centre_zone_1[0]),(centre_zone_1[1] - lw_half)]
    lane_2_centreline_end = [(centre_zone_1[0] + jlx),(centre_zone_1[1] - lw_half)]
    lane_3_centreline_start = [(centre_zone_1[0] + jlx),(centre_zone_1[1] + lw_half)]
    lane_3_centreline_end = [(centre_zone_1[0]),(centre_zone_1[1] + lw_half)]
    centre_zone_2 = [(junc_center[0]),(junc_center[1] + lw)]
    lane_4_centreline_start = [(centre_zone_2[0] + lw_half),(centre_zone_2[1])]
    lane_4_centreline_end = [(centre_zone_2[0] + lw_half),(centre_zone_2[1] + jly)]
    lane_5_centreline_start = [(centre_zone_2[0] - lw_half),(centre_zone_2[1] + jly)]
    lane_5_centreline_end = [(centre_zone_2[0]  - lw_half),(centre_zone_2[1])]

    # zone 1
    # canvas.create_line(tdx+(2*lw),tdy,jlx+tdx+(2*lw),tdy,width=2)
    # canvas.create_line(tdx+(2*lw),tdy+lw,jlx+tdx+(2*lw),tdy+lw)
    # canvas.create_line(tdx+(2*lw),tdy+(2*lw),jlx+tdx+(2*lw),tdy+(2*lw),width=2)
    # canvas.create_line(tdx+(2*lw),tdy+lw,tdx+(2*lw),tdy+(2*lw),dash=(4,1))
    # canvas.create_line(jlx+tdx+(2*lw),tdy,jlx+tdx+(2*lw),tdy+(lw),dash=(4,1))
    zone_type = 2
    zone_orien = zone_counter
    lane_orien = zone_counter
    lane_orien = 3
    lane_polar = 5
    zones.append(Zone(jlx+tdx+(2*lw),tdy+(2*lw),tdx+(2*lw),tdy,zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1])) # junc 0, zone 1
    zones[zone_num_tot].type = zone_type #set zone type to internal zone
    # lane 2
    lane_type = zone_type
    lane_reverse = 1
    lanes_test.append(Lane_test(zones[zone_num_tot].x2,zones[zone_num_tot].y1 - lw,zones[zone_num_tot].x1,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_2_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_2_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))   ###############

    lane_counter += 1
    # lane 3
    lane_type = zone_type
    lane_polar = 5
    lane_orien = 1
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2 + lw,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_3_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_3_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1

    # zone 2
    # canvas.create_line(tdx,tdy+(2*lw),tdx,jly+tdy+(2*lw),width=2)
    # canvas.create_line(tdx+lw,tdy+(2*lw),tdx+lw,jly+tdy+(2*lw))
    # canvas.create_line(tdx+(2*lw),tdy+(2*lw),tdx+(2*lw),jly+tdy+(2*lw),width=2)
    # canvas.create_line(tdx,tdy+(2*lw),tdx+(lw),tdy+(2*lw),dash=(4,1))
    # canvas.create_line(tdx+(lw),tdy+(2*lw)+jlx,tdx+(2*lw),tdy+(2*lw)+jlx,dash=(4,1))
    zone_type = 2
    zone_orien = zone_counter
    lane_orien = zone_counter
    zones.append(Zone(tdx+(2*lw),jly+tdy+(2*lw),tdx,tdy+(2*lw),zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1]))# junc 0, zone 2
    zones[zone_num_tot].type = zone_type #set zone type to internal zone
    # zone_counter += 1
    # lane 4
    lane_type = zone_type
    lane_orien = 0
    lane_polar = 5
    lane_reverse = 1
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2 + lw,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1)
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y2,zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2 + (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y2,zones[zone_num_tot].x1,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # canvas.create_rectangle(lanes_test[lane_counter].x2+5,lanes_test[lane_counter].y2+5,lanes_test[lane_counter].x2-5,lanes_test[lane_counter].y2-5, fill = "green" )
    # canvas.create_rectangle(lanes_test[lane_counter].x1+5,lanes_test[lane_counter].y1+5,lanes_test[lane_counter].x1-5,lanes_test[lane_counter].y1-5, fill = "yellow" )
    lanes_test[lane_counter].centre_line_start = lane_4_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_4_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 + (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1+ (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_start[0]+5,lanes_test[lane_counter].centre_line_start[1]+5,lanes_test[lane_counter].centre_line_start[0]-5,lanes_test[lane_counter].centre_line_start[1]-5, fill = "yellow" )
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_end[0]+5,lanes_test[lane_counter].centre_line_end[1]+5,lanes_test[lane_counter].centre_line_end[0]-5,lanes_test[lane_counter].centre_line_end[1]-5, fill = "green" )
    lane_counter += 1
    #lane 5
    lane_type = zone_type
    lane_orien = 2
    lane_polar = 5
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_5_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_5_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1
    ##end of this junc
    junc_counter += 1
    return tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot
def create_m_r_Junc_test(juncs_test,Junc_test,zones,Zone,lanes_test,Lane_test,tk,lw,canvas,Canvas,tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot):
    junc_num = junc_counter
    tdx = tdx + (2*lw) + jlx
    tdy = tdy
    juncs_test.append(Junc_test(junc_counter,(tdx+lw),(tdy+lw)))
    junc_first_zone = zone_num_tot
    junc_center = [tdx+lw,tdy+lw]
    # canvas.create_oval(junc_center[0] + 10,junc_center[1] + 10,junc_center[0] - 10,junc_center[1] - 10 )
    tk.update()
    print("junc_center[1]: " + str(junc_center[1]))
    lanes_at_junc_store = []
    num_lanes_to_create = 8
    centre_zone_0 = [junc_center[0],(junc_center[1] - lw)]
    # canvas.create_oval(centre_zone_0[0] + 10,centre_zone_0[1] + 10,centre_zone_0[0] - 10,centre_zone_0[1] - 10 )
    tk.update()
    centre_zone_1 = [(junc_center[0] + lw),(junc_center[1])]
    lane_2_centreline_start = [(centre_zone_1[0]),(centre_zone_1[1] - lw_half)]
    lane_2_centreline_end = [(centre_zone_1[0] + jlx),(centre_zone_1[1] - lw_half)]
    lane_3_centreline_start = [(centre_zone_1[0] + jlx),(centre_zone_1[1] + lw_half)]
    lane_3_centreline_end = [(centre_zone_1[0]),(centre_zone_1[1] + lw_half)]
    centre_zone_2 = [(junc_center[0]),(junc_center[1] + lw)]
    lane_4_centreline_start = [(centre_zone_2[0] + lw_half),(centre_zone_2[1])]
    lane_4_centreline_end = [(centre_zone_2[0] + lw_half),(centre_zone_2[1] + jly)]
    lane_5_centreline_start = [(centre_zone_2[0] - lw_half),(centre_zone_2[1] + jly)]
    lane_5_centreline_end = [(centre_zone_2[0]  - lw_half),(centre_zone_2[1])]

    # zone 1
    # canvas.create_line(tdx+(2*lw),tdy,jlx+tdx+(2*lw),tdy,width=2)
    # canvas.create_line(tdx+(2*lw),tdy+lw,jlx+tdx+(2*lw),tdy+lw)
    # canvas.create_line(tdx+(2*lw),tdy+(2*lw),jlx+tdx+(2*lw),tdy+(2*lw),width=2)
    # canvas.create_line(tdx+(2*lw),tdy+lw,tdx+(2*lw),tdy+(2*lw),dash=(4,1))
    zone_type = 2
    zone_orien = zone_counter
    lane_orien = zone_counter
    lane_orien = 3
    lane_polar = 5
    zones.append(Zone(jlx+tdx+(2*lw),tdy+(2*lw),tdx+(2*lw),tdy,zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1])) # junc 0, zone 1
    zones[zone_num_tot].type = zone_type #set zone type to internal zone
    # lane 2
    lane_type = 0
    lane_reverse = 1
    lanes_test.append(Lane_test(zones[zone_num_tot].x2,zones[zone_num_tot].y1 - lw,zones[zone_num_tot].x1,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_2_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_2_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))   ###############

    lane_counter += 1
    # lane 3
    lane_type = 1
    lane_polar = 5
    lane_orien = 1
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2 + lw,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_3_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_3_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1

    # zone 2
    # canvas.create_line(tdx,tdy+(2*lw),tdx,jly+tdy+(2*lw),width=2)
    # canvas.create_line(tdx+lw,tdy+(2*lw),tdx+lw,jly+tdy+(2*lw))
    # canvas.create_line(tdx+(2*lw),tdy+(2*lw),tdx+(2*lw),jly+tdy+(2*lw),width=2)
    # canvas.create_line(tdx,tdy+(2*lw),tdx+(lw),tdy+(2*lw),dash=(4,1))
    # canvas.create_line(tdx+(lw),tdy+(2*lw)+jlx,tdx+(2*lw),tdy+(2*lw)+jlx,dash=(4,1))
    zone_type = 2
    zone_orien = zone_counter
    lane_orien = zone_counter
    zones.append(Zone(tdx+(2*lw),jly+tdy+(2*lw),tdx,tdy+(2*lw),zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1]))# junc 0, zone 2
    zones[zone_num_tot].type = zone_type #set zone type to internal zone
    # zone_counter += 1
    # lane 4
    lane_type = zone_type
    lane_orien = 0
    lane_polar = 5
    lane_reverse = 1
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2 + lw,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1)
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y2,zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2 + (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y2,zones[zone_num_tot].x1,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # canvas.create_rectangle(lanes_test[lane_counter].x2+5,lanes_test[lane_counter].y2+5,lanes_test[lane_counter].x2-5,lanes_test[lane_counter].y2-5, fill = "green" )
    # canvas.create_rectangle(lanes_test[lane_counter].x1+5,lanes_test[lane_counter].y1+5,lanes_test[lane_counter].x1-5,lanes_test[lane_counter].y1-5, fill = "yellow" )
    lanes_test[lane_counter].centre_line_start = lane_4_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_4_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 + (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1+ (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_start[0]+5,lanes_test[lane_counter].centre_line_start[1]+5,lanes_test[lane_counter].centre_line_start[0]-5,lanes_test[lane_counter].centre_line_start[1]-5, fill = "yellow" )
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_end[0]+5,lanes_test[lane_counter].centre_line_end[1]+5,lanes_test[lane_counter].centre_line_end[0]-5,lanes_test[lane_counter].centre_line_end[1]-5, fill = "green" )
    lane_counter += 1
    #lane 5
    lane_type = zone_type
    lane_orien = 2
    lane_polar = 5
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_5_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_5_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1
    ##end of this junc
    junc_counter += 1
    return tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot
def create_b_l_Junc_test(juncs_test,Junc_test,zones,Zone,lanes_test,Lane_test,tk,lw,canvas,Canvas,tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot):

    junc_num = junc_counter
    junc_first_zone = zone_num_tot
    # tdx = 100
    tdx = block_len_horizontal
    tdy = tdy + (2*lw) + jly
    junc_first_zone = zone_num_tot
    juncs_test.append(Junc_test(junc_counter,(tdx+lw),(tdy+lw)))
    junc_center = [tdx+lw,tdy+lw]
    # canvas.create_oval(junc_center[0] + 10,junc_center[1] + 10,junc_center[0] - 10,junc_center[1] - 10 )
    tk.update()
    print("junc_center[1]: " + str(junc_center[1]))
    lanes_at_junc_store = []
    num_lanes_to_create = 8
    centre_zone_0 = [junc_center[0],(junc_center[1] - lw)]
    # canvas.create_oval(centre_zone_0[0] + 10,centre_zone_0[1] + 10,centre_zone_0[0] - 10,centre_zone_0[1] - 10 )
    tk.update()
    centre_zone_1 = [(junc_center[0] + lw),(junc_center[1])]
    lane_2_centreline_start = [(centre_zone_1[0]),(centre_zone_1[1] - lw_half)]
    lane_2_centreline_end = [(centre_zone_1[0] + jlx),(centre_zone_1[1] - lw_half)]
    lane_3_centreline_start = [(centre_zone_1[0] + jlx),(centre_zone_1[1] + lw_half)]
    lane_3_centreline_end = [(centre_zone_1[0]),(centre_zone_1[1] + lw_half)]
    centre_zone_2 = [(junc_center[0]),(junc_center[1] + lw)]
    lane_4_centreline_start = [(centre_zone_2[0] + lw_half),(centre_zone_2[1])]
    lane_4_centreline_end = [(centre_zone_2[0] + lw_half),(centre_zone_2[1] + jly)]
    lane_5_centreline_start = [(centre_zone_2[0] - lw_half),(centre_zone_2[1] + jly)]
    lane_5_centreline_end = [(centre_zone_2[0]  - lw_half),(centre_zone_2[1])]
    centre_zone_3 = [(junc_center[0] - lw),(junc_center[1])]
    lane_6_centreline_start = [(centre_zone_3[0]),(centre_zone_3[1] + lw_half)]
    lane_6_centreline_end = [(centre_zone_3[0] - jlx),(centre_zone_3[1] + lw_half)]
    lane_7_centreline_start = [(centre_zone_3[0] - jlx),(centre_zone_3[1] - lw_half)]
    lane_7_centreline_end = [(centre_zone_3[0]),(centre_zone_3[1] - lw_half)]

    # zone 1
    # canvas.create_line(tdx+(2*lw),tdy,jlx+tdx+(2*lw),tdy,width=2)
    # canvas.create_line(tdx+(2*lw),tdy+lw,jlx+tdx+(2*lw),tdy+lw)
    # canvas.create_line(tdx+(2*lw),tdy+(2*lw),jlx+tdx+(2*lw),tdy+(2*lw),width=2)
    # canvas.create_line(tdx+(2*lw),tdy+lw,tdx+(2*lw),tdy+(2*lw),dash=(4,1))
    # canvas.create_line(jlx+tdx+(2*lw),tdy,jlx+tdx+(2*lw),tdy+(lw),dash=(4,1))
    zone_type = 2
    zone_orien = zone_counter
    lane_orien = zone_counter
    lane_orien = 3
    lane_polar = 5
    zones.append(Zone(jlx+tdx+(2*lw),tdy+(2*lw),tdx+(2*lw),tdy,zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1])) # junc 0, zone 1
    zones[zone_num_tot].type = zone_type #set zone type to internal zone
    # lane 2
    lane_type = zone_type
    lane_reverse = 1
    lanes_test.append(Lane_test(zones[zone_num_tot].x2,zones[zone_num_tot].y1 - lw,zones[zone_num_tot].x1,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_2_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_2_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))   ###############

    lane_counter += 1
    # lane 3
    lane_type = zone_type
    lane_polar = 5
    lane_orien = 1
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2 + lw,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_3_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_3_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1

    # zone 2
    # canvas.create_line(tdx,tdy+(2*lw),tdx,jly+tdy+(2*lw),width=2)
    # canvas.create_line(tdx+lw,tdy+(2*lw),tdx+lw,jly+tdy+(2*lw))
    # canvas.create_line(tdx+(2*lw),tdy+(2*lw),tdx+(2*lw),jly+tdy+(2*lw),width=2)
    # canvas.create_line(tdx,tdy+(2*lw),tdx+(lw),tdy+(2*lw),dash=(4,1))
    # canvas.create_line(tdx+(lw),tdy+(2*lw)+jlx,tdx+(2*lw),tdy+(2*lw)+jlx,dash=(4,1))
    zone_type = 2
    zone_orien = zone_counter
    lane_orien = zone_counter
    zones.append(Zone(tdx+(2*lw),jly+tdy+(2*lw),tdx,tdy+(2*lw),zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1]))# junc 0, zone 2
    zones[zone_num_tot].type = zone_type #set zone type to internal zone
    # zone_counter += 1
    # lane 4
    lane_type = 0
    lane_orien = 0
    lane_polar = 5
    lane_reverse = 1
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2 + lw,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1)
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y2,zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2 + (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y2,zones[zone_num_tot].x1,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # canvas.create_rectangle(lanes_test[lane_counter].x2+5,lanes_test[lane_counter].y2+5,lanes_test[lane_counter].x2-5,lanes_test[lane_counter].y2-5, fill = "green" )
    # canvas.create_rectangle(lanes_test[lane_counter].x1+5,lanes_test[lane_counter].y1+5,lanes_test[lane_counter].x1-5,lanes_test[lane_counter].y1-5, fill = "yellow" )
    lanes_test[lane_counter].centre_line_start = lane_4_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_4_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 + (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1+ (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_start[0]+5,lanes_test[lane_counter].centre_line_start[1]+5,lanes_test[lane_counter].centre_line_start[0]-5,lanes_test[lane_counter].centre_line_start[1]-5, fill = "yellow" )
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_end[0]+5,lanes_test[lane_counter].centre_line_end[1]+5,lanes_test[lane_counter].centre_line_end[0]-5,lanes_test[lane_counter].centre_line_end[1]-5, fill = "green" )
    lane_counter += 1
    #lane 5
    lane_type = 1
    lane_orien = 2
    lane_polar = 5
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_5_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_5_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1

    #zone 3
    # canvas.create_line(stx,tdy,tdx,tdy,width=2)
    # canvas.create_line(stx,tdy+lw,tdx,tdy+lw)
    # canvas.create_line(stx,tdy+(2*lw),tdx,tdy+(2*lw),width=2)
    # canvas.create_line(tdx,tdy,tdx,tdy+(lw),dash=(4,1))
    # canvas.create_rectangle(stx,tdy+(2*lw),tdx,tdy) # zone 3
    zone_type = 1
    zone_orien = zone_counter
    lane_orien = zone_counter
    zones.append(Zone(stx,tdy+(2*lw),tdx,tdy,zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1]))# junc 0, zone 3
    zones[zone_num_tot].type = zone_type #set zone type to entry zone
    # zone_counter += 1
    # lane 6
    lane_type = 0
    lane_orien = 1
    lane_polar = 4
    lane_reverse = 1
    lanes_test.append(Lane_test(zones[zone_num_tot].x2,zones[zone_num_tot].y2 + lw,zones[zone_num_tot].x1,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_6_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_6_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 + (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 + (lw_half))
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_start[0]+5,lanes_test[lane_counter].centre_line_start[1]+5,lanes_test[lane_counter].centre_line_start[0]-5,lanes_test[lane_counter].centre_line_start[1]-5, fill = "yellow" )
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_end[0]+5,lanes_test[lane_counter].centre_line_end[1]+5,lanes_test[lane_counter].centre_line_end[0]-5,lanes_test[lane_counter].centre_line_end[1]-5, fill = "green" )
    lane_counter += 1
    # lane 7
    lane_type = 1
    lane_orien = 3
    lane_polar = 4
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1 - lw,zones[zone_num_tot].x2,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) #straight and left turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_7_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_7_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1
    ###########  end of junction 0
    junc_counter += 1
    return tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot
def create_b_m_Junc_test(juncs_test,Junc_test,zones,Zone,lanes_test,Lane_test,tk,lw,canvas,Canvas,tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot):
    junc_num = junc_counter
    tdx = tdx + (2*lw) + jlx
    tdy = tdy
    juncs_test.append(Junc_test(junc_counter,(tdx+lw),(tdy+lw)))
    junc_first_zone = zone_num_tot
    junc_center = [tdx+lw,tdy+lw]
    # canvas.create_oval(junc_center[0] + 10,junc_center[1] + 10,junc_center[0] - 10,junc_center[1] - 10 )
    tk.update()
    print("junc_center[1]: " + str(junc_center[1]))
    lanes_at_junc_store = []
    num_lanes_to_create = 8
    centre_zone_0 = [junc_center[0],(junc_center[1] - lw)]
    # canvas.create_oval(centre_zone_0[0] + 10,centre_zone_0[1] + 10,centre_zone_0[0] - 10,centre_zone_0[1] - 10 )
    tk.update()
    centre_zone_1 = [(junc_center[0] + lw),(junc_center[1])]
    lane_2_centreline_start = [(centre_zone_1[0]),(centre_zone_1[1] - lw_half)]
    lane_2_centreline_end = [(centre_zone_1[0] + jlx),(centre_zone_1[1] - lw_half)]
    lane_3_centreline_start = [(centre_zone_1[0] + jlx),(centre_zone_1[1] + lw_half)]
    lane_3_centreline_end = [(centre_zone_1[0]),(centre_zone_1[1] + lw_half)]
    centre_zone_2 = [(junc_center[0]),(junc_center[1] + lw)]
    lane_4_centreline_start = [(centre_zone_2[0] + lw_half),(centre_zone_2[1])]
    lane_4_centreline_end = [(centre_zone_2[0] + lw_half),(centre_zone_2[1] + jly)]
    lane_5_centreline_start = [(centre_zone_2[0] - lw_half),(centre_zone_2[1] + jly)]
    lane_5_centreline_end = [(centre_zone_2[0]  - lw_half),(centre_zone_2[1])]

    # zone 1
    # canvas.create_line(tdx+(2*lw),tdy,jlx+tdx+(2*lw),tdy,width=2)
    # canvas.create_line(tdx+(2*lw),tdy+lw,jlx+tdx+(2*lw),tdy+lw)
    # canvas.create_line(tdx+(2*lw),tdy+(2*lw),jlx+tdx+(2*lw),tdy+(2*lw),width=2)
    # canvas.create_line(tdx+(2*lw),tdy+lw,tdx+(2*lw),tdy+(2*lw),dash=(4,1))
    # canvas.create_line(jlx+tdx+(2*lw),tdy,jlx+tdx+(2*lw),tdy+(lw),dash=(4,1))
    zone_type = 2
    zone_orien = zone_counter
    lane_orien = zone_counter
    lane_orien = 3
    lane_polar = 5
    zones.append(Zone(jlx+tdx+(2*lw),tdy+(2*lw),tdx+(2*lw),tdy,zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1])) # junc 0, zone 1
    zones[zone_num_tot].type = zone_type #set zone type to internal zone
    # lane 2
    lane_type = zone_type
    lane_reverse = 1
    lanes_test.append(Lane_test(zones[zone_num_tot].x2,zones[zone_num_tot].y1 - lw,zones[zone_num_tot].x1,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_2_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_2_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))   ###############

    lane_counter += 1
    # lane 3
    lane_type = zone_type
    lane_polar = 5
    lane_orien = 1
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2 + lw,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_3_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_3_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1

    # zone 2
    # canvas.create_line(tdx,tdy+(2*lw),tdx,jly+tdy+(2*lw),width=2)
    # canvas.create_line(tdx+lw,tdy+(2*lw),tdx+lw,jly+tdy+(2*lw))
    # canvas.create_line(tdx+(2*lw),tdy+(2*lw),tdx+(2*lw),jly+tdy+(2*lw),width=2)
    # canvas.create_line(tdx,tdy+(2*lw),tdx+(lw),tdy+(2*lw),dash=(4,1))
    zone_type = 2
    zone_orien = zone_counter
    lane_orien = zone_counter
    zones.append(Zone(tdx+(2*lw),jly+tdy+(2*lw),tdx,tdy+(2*lw),zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1]))# junc 0, zone 2
    zones[zone_num_tot].type = zone_type #set zone type to internal zone
    # zone_counter += 1
    # lane 4
    lane_type = 0
    lane_orien = 0
    lane_polar = 5
    lane_reverse = 1
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2 + lw,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1)
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y2,zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2 + (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y2,zones[zone_num_tot].x1,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # canvas.create_rectangle(lanes_test[lane_counter].x2+5,lanes_test[lane_counter].y2+5,lanes_test[lane_counter].x2-5,lanes_test[lane_counter].y2-5, fill = "green" )
    # canvas.create_rectangle(lanes_test[lane_counter].x1+5,lanes_test[lane_counter].y1+5,lanes_test[lane_counter].x1-5,lanes_test[lane_counter].y1-5, fill = "yellow" )
    lanes_test[lane_counter].centre_line_start = lane_4_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_4_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 + (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1+ (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_start[0]+5,lanes_test[lane_counter].centre_line_start[1]+5,lanes_test[lane_counter].centre_line_start[0]-5,lanes_test[lane_counter].centre_line_start[1]-5, fill = "yellow" )
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_end[0]+5,lanes_test[lane_counter].centre_line_end[1]+5,lanes_test[lane_counter].centre_line_end[0]-5,lanes_test[lane_counter].centre_line_end[1]-5, fill = "green" )
    lane_counter += 1
    #lane 5
    lane_type = 1
    lane_orien = 2
    lane_polar = 5
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_5_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_5_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1
    ##end of this junc
    junc_counter += 1
    return tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot
def create_b_r_Junc_test(juncs_test,Junc_test,zones,Zone,lanes_test,Lane_test,tk,lw,canvas,Canvas,tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot):
    junc_num = junc_counter
    tdx = tdx + (2*lw) + jlx
    tdy = tdy
    juncs_test.append(Junc_test(junc_counter,(tdx+lw),(tdy+lw)))
    junc_first_zone = zone_num_tot
    junc_center = [tdx+lw,tdy+lw]
    # canvas.create_oval(junc_center[0] + 10,junc_center[1] + 10,junc_center[0] - 10,junc_center[1] - 10 )
    tk.update()
    print("junc_center[1]: " + str(junc_center[1]))
    lanes_at_junc_store = []
    num_lanes_to_create = 8
    centre_zone_0 = [junc_center[0],(junc_center[1] - lw)]
    # canvas.create_oval(centre_zone_0[0] + 10,centre_zone_0[1] + 10,centre_zone_0[0] - 10,centre_zone_0[1] - 10 )
    tk.update()
    centre_zone_1 = [(junc_center[0] + lw),(junc_center[1])]
    lane_2_centreline_start = [(centre_zone_1[0]),(centre_zone_1[1] - lw_half)]
    lane_2_centreline_end = [(centre_zone_1[0] + jlx),(centre_zone_1[1] - lw_half)]
    lane_3_centreline_start = [(centre_zone_1[0] + jlx),(centre_zone_1[1] + lw_half)]
    lane_3_centreline_end = [(centre_zone_1[0]),(centre_zone_1[1] + lw_half)]
    centre_zone_2 = [(junc_center[0]),(junc_center[1] + lw)]
    lane_4_centreline_start = [(centre_zone_2[0] + lw_half),(centre_zone_2[1])]
    lane_4_centreline_end = [(centre_zone_2[0] + lw_half),(centre_zone_2[1] + jly)]
    lane_5_centreline_start = [(centre_zone_2[0] - lw_half),(centre_zone_2[1] + jly)]
    lane_5_centreline_end = [(centre_zone_2[0]  - lw_half),(centre_zone_2[1])]

    # zone 1
    # canvas.create_line(tdx+(2*lw),tdy,jlx+tdx+(2*lw),tdy,width=2)
    # canvas.create_line(tdx+(2*lw),tdy+lw,jlx+tdx+(2*lw),tdy+lw)
    # canvas.create_line(tdx+(2*lw),tdy+(2*lw),jlx+tdx+(2*lw),tdy+(2*lw),width=2)
    # canvas.create_line(tdx+(2*lw),tdy+lw,tdx+(2*lw),tdy+(2*lw),dash=(4,1))
    zone_type = 2
    zone_orien = zone_counter
    lane_orien = zone_counter
    lane_orien = 3
    lane_polar = 5
    zones.append(Zone(jlx+tdx+(2*lw),tdy+(2*lw),tdx+(2*lw),tdy,zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1])) # junc 0, zone 1
    zones[zone_num_tot].type = zone_type #set zone type to internal zone
    # lane 2
    lane_type = 0
    lane_reverse = 1
    lanes_test.append(Lane_test(zones[zone_num_tot].x2,zones[zone_num_tot].y1 - lw,zones[zone_num_tot].x1,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_2_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_2_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))   ###############

    lane_counter += 1
    # lane 3
    lane_type = 1
    lane_polar = 5
    lane_orien = 1
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2 + lw,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_3_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_3_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1

    # zone 2
    # canvas.create_line(tdx,tdy+(2*lw),tdx,jly+tdy+(2*lw),width=2)
    # canvas.create_line(tdx+lw,tdy+(2*lw),tdx+lw,jly+tdy+(2*lw))
    # canvas.create_line(tdx+(2*lw),tdy+(2*lw),tdx+(2*lw),jly+tdy+(2*lw),width=2)
    # canvas.create_line(tdx,tdy+(2*lw),tdx+(lw),tdy+(2*lw),dash=(4,1))
    zone_type = 2
    zone_orien = zone_counter
    lane_orien = zone_counter
    zones.append(Zone(tdx+(2*lw),jly+tdy+(2*lw),tdx,tdy+(2*lw),zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1]))# junc 0, zone 2
    zones[zone_num_tot].type = zone_type #set zone type to internal zone
    # zone_counter += 1
    # lane 4
    lane_type = 0
    lane_orien = 0
    lane_polar = 5
    lane_reverse = 1
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2 + lw,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1)
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y2,zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2 + (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y2,zones[zone_num_tot].x1,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # canvas.create_rectangle(lanes_test[lane_counter].x2+5,lanes_test[lane_counter].y2+5,lanes_test[lane_counter].x2-5,lanes_test[lane_counter].y2-5, fill = "green" )
    # canvas.create_rectangle(lanes_test[lane_counter].x1+5,lanes_test[lane_counter].y1+5,lanes_test[lane_counter].x1-5,lanes_test[lane_counter].y1-5, fill = "yellow" )
    lanes_test[lane_counter].centre_line_start = lane_4_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_4_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 + (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1+ (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_start[0]+5,lanes_test[lane_counter].centre_line_start[1]+5,lanes_test[lane_counter].centre_line_start[0]-5,lanes_test[lane_counter].centre_line_start[1]-5, fill = "yellow" )
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_end[0]+5,lanes_test[lane_counter].centre_line_end[1]+5,lanes_test[lane_counter].centre_line_end[0]-5,lanes_test[lane_counter].centre_line_end[1]-5, fill = "green" )
    lane_counter += 1
    #lane 5
    lane_type = 1
    lane_orien = 2
    lane_polar = 5
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_5_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_5_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1
    ##end of this junc
    junc_counter += 1
    return tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot
def create_m_l_Junc_test(juncs_test,Junc_test,zones,Zone,lanes_test,Lane_test,tk,lw,canvas,Canvas,tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot):
    junc_num = junc_counter
    tdx = 100
    tdx = block_len_horizontal
    tdy = tdy + (2*lw) + jly
    juncs_test.append(Junc_test(junc_counter,(tdx+lw),(tdy+lw)))
    junc_first_zone = zone_num_tot
    junc_center = [tdx+lw,tdy+lw]
    # canvas.create_oval(junc_center[0] + 10,junc_center[1] + 10,junc_center[0] - 10,junc_center[1] - 10 )
    tk.update()
    print("junc_center[1]: " + str(junc_center[1]))
    lanes_at_junc_store = []
    num_lanes_to_create = 8
    centre_zone_0 = [junc_center[0],(junc_center[1] - lw)]
    # canvas.create_oval(centre_zone_0[0] + 10,centre_zone_0[1] + 10,centre_zone_0[0] - 10,centre_zone_0[1] - 10 )
    tk.update()
    centre_zone_1 = [(junc_center[0] + lw),(junc_center[1])]
    lane_2_centreline_start = [(centre_zone_1[0]),(centre_zone_1[1] - lw_half)]
    lane_2_centreline_end = [(centre_zone_1[0] + jlx),(centre_zone_1[1] - lw_half)]
    lane_3_centreline_start = [(centre_zone_1[0] + jlx),(centre_zone_1[1] + lw_half)]
    lane_3_centreline_end = [(centre_zone_1[0]),(centre_zone_1[1] + lw_half)]
    centre_zone_2 = [(junc_center[0]),(junc_center[1] + lw)]
    lane_4_centreline_start = [(centre_zone_2[0] + lw_half),(centre_zone_2[1])]
    lane_4_centreline_end = [(centre_zone_2[0] + lw_half),(centre_zone_2[1] + jly)]
    lane_5_centreline_start = [(centre_zone_2[0] - lw_half),(centre_zone_2[1] + jly)]
    lane_5_centreline_end = [(centre_zone_2[0]  - lw_half),(centre_zone_2[1])]
    centre_zone_3 = [(junc_center[0] - lw),(junc_center[1])]
    lane_6_centreline_start = [(centre_zone_3[0]),(centre_zone_3[1] + lw_half)]
    lane_6_centreline_end = [(centre_zone_3[0] - jlx),(centre_zone_3[1] + lw_half)]
    lane_7_centreline_start = [(centre_zone_3[0] - jlx),(centre_zone_3[1] - lw_half)]
    lane_7_centreline_end = [(centre_zone_3[0]),(centre_zone_3[1] - lw_half)]

    # zone 1
    # canvas.create_line(tdx+(2*lw),tdy,jlx+tdx+(2*lw),tdy,width=2)
    # canvas.create_line(tdx+(2*lw),tdy+lw,jlx+tdx+(2*lw),tdy+lw)
    # canvas.create_line(tdx+(2*lw),tdy+(2*lw),jlx+tdx+(2*lw),tdy+(2*lw),width=2)
    # canvas.create_line(tdx+(2*lw),tdy+lw,tdx+(2*lw),tdy+(2*lw),dash=(4,1))
    # canvas.create_line(jlx+tdx+(2*lw),tdy,jlx+tdx+(2*lw),tdy+(lw),dash=(4,1))
    zone_type = 2
    zone_orien = zone_counter
    lane_orien = zone_counter
    lane_orien = 3
    lane_polar = 5
    zones.append(Zone(jlx+tdx+(2*lw),tdy+(2*lw),tdx+(2*lw),tdy,zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1])) # junc 0, zone 1
    zones[zone_num_tot].type = zone_type #set zone type to internal zone
    # lane 2
    lane_type = zone_type
    lane_reverse = 1
    lanes_test.append(Lane_test(zones[zone_num_tot].x2,zones[zone_num_tot].y1 - lw,zones[zone_num_tot].x1,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_2_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_2_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))   ###############
    lane_counter += 1
    # lane 3
    lane_type = zone_type
    lane_polar = 5
    lane_orien = 1
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2 + lw,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_3_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_3_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1

    # zone 2
    # canvas.create_line(tdx,tdy+(2*lw),tdx,jly+tdy+(2*lw),width=2)
    # canvas.create_line(tdx+lw,tdy+(2*lw),tdx+lw,jly+tdy+(2*lw))
    # canvas.create_line(tdx+(2*lw),tdy+(2*lw),tdx+(2*lw),jly+tdy+(2*lw),width=2)
    # canvas.create_line(tdx,tdy+(2*lw),tdx+(lw),tdy+(2*lw),dash=(4,1))
    # canvas.create_line(tdx+(lw),tdy+(2*lw)+jlx,tdx+(2*lw),tdy+(2*lw)+jlx,dash=(4,1))
    zone_type = 2
    zone_orien = zone_counter
    lane_orien = zone_counter
    zones.append(Zone(tdx+(2*lw),jly+tdy+(2*lw),tdx,tdy+(2*lw),zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1]))# junc 0, zone 2
    zones[zone_num_tot].type = zone_type #set zone type to internal zone
    # zone_counter += 1
    # lane 4
    lane_type = zone_type
    lane_orien = 0
    lane_polar = 5
    lane_reverse = 1
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1,zones[zone_num_tot].x2 + lw,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1)
    # lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y2,zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2 + (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y2,zones[zone_num_tot].x1,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    # canvas.create_rectangle(lanes_test[lane_counter].x2+5,lanes_test[lane_counter].y2+5,lanes_test[lane_counter].x2-5,lanes_test[lane_counter].y2-5, fill = "green" )
    # canvas.create_rectangle(lanes_test[lane_counter].x1+5,lanes_test[lane_counter].y1+5,lanes_test[lane_counter].x1-5,lanes_test[lane_counter].y1-5, fill = "yellow" )
    lanes_test[lane_counter].centre_line_start = lane_4_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_4_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 + (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1+ (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_start[0]+5,lanes_test[lane_counter].centre_line_start[1]+5,lanes_test[lane_counter].centre_line_start[0]-5,lanes_test[lane_counter].centre_line_start[1]-5, fill = "yellow" )
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_end[0]+5,lanes_test[lane_counter].centre_line_end[1]+5,lanes_test[lane_counter].centre_line_end[0]-5,lanes_test[lane_counter].centre_line_end[1]-5, fill = "green" )
    lane_counter += 1
    #lane 5
    lane_type = zone_type
    lane_orien = 2
    lane_polar = 5
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1 - lw,zones[zone_num_tot].y1,zones[zone_num_tot].x2,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_5_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_5_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y2)
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1

    #zone 3
    # canvas.create_line(stx,tdy,tdx,tdy,width=2)
    # canvas.create_line(stx,tdy+lw,tdx,tdy+lw)
    # canvas.create_line(stx,tdy+(2*lw),tdx,tdy+(2*lw),width=2)
    # canvas.create_line(tdx,tdy,tdx,tdy+(lw),dash=(4,1))
    # canvas.create_rectangle(stx,tdy+(2*lw),tdx,tdy) # zone 3
    zone_type = 1
    zone_orien = zone_counter
    lane_orien = zone_counter
    zones.append(Zone(stx,tdy+(2*lw),tdx,tdy,zone_counter,junc_num,zone_type,zone_orien,zone_num_tot,[lane_counter,lane_counter+1]))# junc 0, zone 3
    zones[zone_num_tot].type = zone_type #set zone type to entry zone
    # zone_counter += 1
    # lane 6
    lane_type = 0
    lane_orien = 1
    lane_polar = 4
    lane_reverse = 1
    lanes_test.append(Lane_test(zones[zone_num_tot].x2,zones[zone_num_tot].y2 + lw,zones[zone_num_tot].x1,zones[zone_num_tot].y1,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) # right turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_6_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_6_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 + (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 + (lw_half))
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_start[0]+5,lanes_test[lane_counter].centre_line_start[1]+5,lanes_test[lane_counter].centre_line_start[0]-5,lanes_test[lane_counter].centre_line_start[1]-5, fill = "yellow" )
    # canvas.create_rectangle(lanes_test[lane_counter].centre_line_end[0]+5,lanes_test[lane_counter].centre_line_end[1]+5,lanes_test[lane_counter].centre_line_end[0]-5,lanes_test[lane_counter].centre_line_end[1]-5, fill = "green" )
    lane_counter += 1
    # lane 7
    lane_type = 1
    lane_orien = 3
    lane_polar = 4
    lane_reverse = 0
    lanes_test.append(Lane_test(zones[zone_num_tot].x1,zones[zone_num_tot].y1 - lw,zones[zone_num_tot].x2,zones[zone_num_tot].y2,lane_counter,zone_counter,junc_num,lane_type,lane_orien,zone_num_tot,lane_reverse,lane_polar)) #straight and left turn lane for zone 0
    lanes_test[lane_counter].centre_line_start = lane_7_centreline_start
    lanes_test[lane_counter].centre_line_end = lane_7_centreline_end

    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].x1)
    # lanes_test[lane_counter].centre_line_start.append(lanes_test[lane_counter].y1 - (lw_half))
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].x2)
    # lanes_test[lane_counter].centre_line_end.append(lanes_test[lane_counter].y1 - (lw_half))
    lane_counter += 1
    zone_counter += 1
    zone_num_tot += 1
    ###########  end of junction 0
    junc_counter += 1
    return tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot

#create map
num_columns = 5
num_rows = 5
tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot = create_t_l_Junc_test(juncs_test,Junc_test,zones,Zone,lanes_test,Lane_test,tk,lw,canvas,Canvas,tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot)
for i in range(0,num_columns - 2):
    tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot = create_t_m_Junc_test(juncs_test,Junc_test,zones,Zone,lanes_test,Lane_test,tk,lw,canvas,Canvas,tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot)
tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot = create_t_r_Junc_test(juncs_test,Junc_test,zones,Zone,lanes_test,Lane_test,tk,lw,canvas,Canvas,tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot)
for i in range(0,num_rows - 2):
    tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot = create_m_l_Junc_test(juncs_test,Junc_test,zones,Zone,lanes_test,Lane_test,tk,lw,canvas,Canvas,tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot)
    for i in range(0,num_columns - 2):
        tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot = create_m_m_Junc_test(juncs_test,Junc_test,zones,Zone,lanes_test,Lane_test,tk,lw,canvas,Canvas,tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot)
    tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot = create_m_r_Junc_test(juncs_test,Junc_test,zones,Zone,lanes_test,Lane_test,tk,lw,canvas,Canvas,tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot)
tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot = create_b_l_Junc_test(juncs_test,Junc_test,zones,Zone,lanes_test,Lane_test,tk,lw,canvas,Canvas,tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot)
for i in range(0,num_columns - 2):
    tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot = create_b_m_Junc_test(juncs_test,Junc_test,zones,Zone,lanes_test,Lane_test,tk,lw,canvas,Canvas,tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot)
tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot = create_b_r_Junc_test(juncs_test,Junc_test,zones,Zone,lanes_test,Lane_test,tk,lw,canvas,Canvas,tdx,tdy,stx,sty,jlx,jly,junc_counter,zone_counter,lane_counter,zone_num_tot)
####
# create the lanes_test[].points
def create_lane_points(lanes_test):
    for i in range(len(lanes_test)):
        lanes_test[i].points = [lanes_test[i].centre_line_start] + [lanes_test[i].centre_line_end]
create_lane_points(lanes_test)

# functions
def find_intersection_point_between_lines_for_next_lanes(line_1,line_2):       # ([[line_1_point_1_x,line_1_point_1_y],[line_1_point_2_x,line_1_point_2_y]],[[line_2_point_1_x,line_2_point_1_y],[line_2_point_2_x,line_2_point_2_y]]):
    # next_lane_first_point = lanes_test[j].points[0][0:2]
    # next_lane_second_point = lanes_test[j].points[1][0:2]
    # next_lane_points = [next_lane_first_point,next_lane_second_point]
    # print("j: " + str(j) + " next_lane_points: " + str(next_lane_points))
    # line_1 = [[line_1_point_1_x,line_1_point_1_y],[line_1_point_2_x,line_1_point_2_y]]
    # line_2 = [[line_2_point_1_x,line_2_point_1_y],[line_2_point_2_x,line_2_point_2_y]]

    xdiff = (line_1[0][0] - line_1[1][0], line_2[0][0] - line_2[1][0])
    ydiff = (line_1[0][1] - line_1[1][1], line_2[0][1] - line_2[1][1])

    # xdiff = (lane_points[0][0] - lane_points[1][0], next_lane_points[0][0] - next_lane_points[1][0])
    # ydiff = (lane_points[0][1] - lane_points[1][1], next_lane_points[0][1] - next_lane_points[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        intersection_cross = 0 # so do not cross, could be straight ahead or parallel

        # x = next_lane_first_point[0]
        # y = next_lane_first_point[1]
        # canvas.create_oval((x + 2),(y + 2),(x - 2),(y -2))
        # lanes_test[i].next_lanes_intersection.append([j,x,y])
       # raise Exception('lines do not intersect')
    else:
        # d = (det(*lane_points), det(*next_lane_points))
        d = (det(*line_1), det(*line_2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        x_round = round(x)
        y_round = round(y)
        intersection_cross = 1 # so do cross
        # canvas.create_oval((x + 2),(y + 2),(x - 2),(y -2))
        point_of_intersection = [x,y]
        # lanes_test[i].next_lanes_intersection.append([j,x,y])
        return point_of_intersection
def find_line_info(point_1,point_2):
    # find angle of line from vertical in clockwise rotation
    # print("point1: " + str(point_1) + " point_2: " + str(point_2))
    diff_x = point_2[0] - point_1[0] # point 2 is further down lane than point 1
    diff_y = point_2[1] - point_1[1]
    abs_diff_x = abs(diff_x)
    abs_diff_y = abs(diff_y)
    # initially set line_quadrant to 0
    line_quadrant = 0
    if (abs_diff_x  == 0) or (abs_diff_y == 0):
        theta = 0
    else:
        theta = math.atan(abs_diff_x/abs_diff_y)
    if diff_y == 0:
        line_grad = 0
    elif diff_x == 0 and diff_y > 0:
        line_grad = 1
    elif diff_x == 0 and diff_y < 0:
        line_grad = -1
    else:
        line_grad = diff_y / diff_x
    line_len = math.sqrt((diff_x**2) + (diff_y**2))
    if diff_x >= 0  and diff_y < 0 : # quadrant-1
        if (abs_diff_x  == 0) or (abs_diff_y == 0):
            theta = 0
        else:
            theta = math.atan(abs_diff_x/abs_diff_y)
        angle_from_vert = theta #
        line_quadrant = 1
        # print("quad1: "+ str(math.degrees(angle_from_vert)))
    if diff_x > 0 and diff_y >= 0: # quadrant-2
        if (abs_diff_x  == 0) or (abs_diff_y == 0):
            theta = 0
        else:
            theta = math.atan(abs_diff_y/abs_diff_x)
        angle_from_vert = (math.pi/2) +  theta    ############################## doesn't work for theta = 0, theta should be 90 degrees
        line_quadrant = 2
        # print("quad2: "+ str(math.degrees(angle_from_vert)))
    if diff_x <= 0 and diff_y > 0: # quadrant-3
        if (abs_diff_x  == 0) or (abs_diff_y == 0):
            theta = 0
        else:
            theta = math.atan(abs_diff_x/abs_diff_y)
        angle_from_vert = (math.pi + theta)
        line_quadrant = 3
        # print("quad3: "+ str(math.degrees(angle_from_vert)))
    if diff_x < 0 and diff_y <= 0: # quadrant-4
        if (abs_diff_x  == 0) or (abs_diff_y == 0):
            theta = 0
        else:
            theta = math.atan(abs_diff_y/abs_diff_x)
        angle_from_vert = (3*math.pi/2) + theta
        line_quadrant = 4
    # if diff_x == 0 and diff_y == 0:
    #     theta = 0
    #     angle_from_vert = theta

        # print("quad4: "+ str(math.degrees(angle_from_vert)))
    # return(diff_x,diff_y,abs_diff_x,abs_diff_y,theta,line_grad,line_len,angle_from_vert,line_quadrant)
    # return(point_1[0],point_1[1],point_2[0],point_2[1],angle_from_vert,line_quadrant,line_len)
    return(line_quadrant,angle_from_vert)
def populate_points_arrays_and_find_side_points(lanes_test):
    # create lanes_test[i].points_with_info
    for i in range(len(lanes_test)): # loop through all lanes
        for j in range(len(lanes_test[i].points)):
            if j == 0: # first point in lane, give status = 1
                status = 1
                junc_pos = lanes_test[i].junc_pos[0]
                # junc_pos = 2
                lanes_test[i].points[j].append(status)
                lanes_test[i].points[j].append(junc_pos)
                lanes_test[i].points_with_info.append(lanes_test[i].points[j])
                lanes_test[i].points[j] = lanes_test[i].points[j][:-2] # remove status and junc_pos from self.points
            elif j == (len(lanes_test[i].points) - 1): # last point in lane, give status = 3
                status = 3
                # junc_pos = 2
                junc_pos = lanes_test[i].junc_pos[1]
                lanes_test[i].points[j].append(status)
                lanes_test[i].points[j].append(junc_pos)
                lanes_test[i].points_with_info.append(lanes_test[i].points[j])
                # record = record[:-1]
                lanes_test[i].points[j] = lanes_test[i].points[j][:-2] # remove status and junc_pos from self.points
            else:  # interior point in lane, give status = 2
                status = 2
                junc_pos = 0
                # junc_pos = 2
                lanes_test[i].points[j].append(status)
                lanes_test[i].points[j].append(junc_pos)
                lanes_test[i].points_with_info.append(lanes_test[i].points[j])
                lanes_test[i].points[j] = lanes_test[i].points[j][:-2] # remove status and junc_pos from self.points
        # print("points: " + str(lanes_test[i].points))
        # print("points_with_info: " + str(lanes_test[i].points_with_info))

    for i in range(len(lanes_test)): # loop through all lane, to find the angle from vert of the line leaving each point
        for j in range(len(lanes_test[i].points)):
            if j == (len(lanes_test[i].points) - 1): # the last point is different as it doesn't have a line leaving it
                line_quadrant = 0
                angle_of_line_leaving_point = 0
                lanes_test[i].points_with_angles.append([lanes_test[i].points[j][0], lanes_test[i].points[j][1], angle_of_line_leaving_point,line_quadrant])
            else:
                point_1 = lanes_test[i].points[j]
                point_2 = lanes_test[i].points[j + 1]
                line_quadrant, angle_of_line_leaving_point = find_line_info(point_1,point_2)
                lanes_test[i].points_with_angles.append([lanes_test[i].points[j][0], lanes_test[i].points[j][1], angle_of_line_leaving_point,line_quadrant])

    # first find the points either side of the centre_line points
    # need the angle of line approaching point and angle of line leaving the point
    # self.points_with_angles = [] # [[x1,y1,angle_from_vert_at_point,line_quadrant going from point], [x2,y2,...],...]

    # find the angle of the end of the lane where it joins the junction
    for i in range(len(lanes_test)): # loop through all lanes
        for j in range(len(lanes_test[i].points)):
            if j == 0: # for first point
                if lanes_test[i].points_with_info[j][3] == 1: # check junc_pos, enters/exits at top or bottom of junction, hence line vetical
                    angle_from_vert_at_point = 0
                    angle_line_points_on = angle_from_vert_at_point + (math.pi/2)
                elif lanes_test[i].points_with_info[j][3] == 2: # check junc_pos, enters/exits at side of junction, hence line horizontal
                    angle_from_vert_at_point = (math.pi) / 2
                    angle_line_points_on = angle_from_vert_at_point - (math.pi/2)
                elif lanes_test[i].points_with_info[j][3] == 0: # if want to end or start lane perpendicular to lane
                    angle_line_leaving = lanes_test[i].points_with_angles[j][2]
                    angle_line_points_on = angle_line_leaving - (math.pi/2)
                    # print("angle_line_leaving: " + str(angle_line_leaving))
                    # print("angle_line_points_on: " + str(angle_line_points_on))
            elif j == (len(lanes_test[i].points) - 1): # for last
                if lanes_test[i].points_with_info[j][3] == 1: # check junc_pos, enters/exits at top or bottom of junction, hence line vetical
                    angle_from_vert_at_point = 0
                    angle_line_points_on = angle_from_vert_at_point + (math.pi/2)
                elif lanes_test[i].points_with_info[j][3] == 2: # check junc_pos, enters/exits at side of junction, hence line horizontal
                    angle_from_vert_at_point = (math.pi) / 2
                    angle_line_points_on = angle_from_vert_at_point - (math.pi/2)
                elif lanes_test[i].points_with_info[j][3] == 0: # if want to end or start lane perpendicular to lane
                    angle_line_approaching = lanes_test[i].points_with_angles[j - 1][2]
                    angle_line_points_on = angle_line_approaching - (math.pi/2)





            #
            #
            # if j == 0 or j == (len(lanes_test[i].points) - 1): # the first point or last point
            #     if lanes_test[i].points_with_info[j][3] == 1: # check junc_pos, enters/exits at top or bottom of junction, hence line vetical
            #         angle_from_vert_at_point = 0
            #         angle_line_points_on = angle_from_vert_at_point + (math.pi/2)
            #     elif lanes_test[i].points_with_info[j][3] == 2: # check junc_pos, enters/exits at side of junction, hence line horizontal
            #         angle_from_vert_at_point = (math.pi) / 2
            #         angle_line_points_on = angle_from_vert_at_point - (math.pi/2)
            #     elif lanes_test[i].points_with_info[j][3] == 0: # if want to end or start lane perpendicular to lane
            #         angle_line_leaving = lanes_test[i].points_with_angles[j][2]
            #         angle_line_points_on = angle_line_leaving - (math.pi/2)
            elif lanes_test[i].points_with_info[j][3] == 0: # interior point so angle_from_vert_at_point equals the angle_from_vert between it and the next point
                angle_line_approaching = lanes_test[i].points_with_angles[j - 1][2]
                angle_line_leaving = lanes_test[i].points_with_angles[j][2]
                avg_angle = (angle_line_approaching + angle_line_leaving)/ 2
                if angle_line_approaching > angle_line_leaving:
                    angle_line_points_on = avg_angle - (math.pi/2)
                else: # ie. angle_line_approaching <= angle_line_leaving
                    angle_line_points_on = avg_angle + (math.pi/2)
            # print("q j: " + str(j))
            # print("lanes_test[i].points_with_info[j][3]: " + str(lanes_test[i].points_with_info[j][3]))
            lanes_test[i].angle_side_points_on.append(angle_line_points_on)
            # print(" before: " + str(lanes_test[i].points_with_angles))
            lanes_test[i].points_with_angles[j].append(angle_line_points_on)
            # print(" after: " + str(lanes_test[i].points_with_angles))
        #     print("i: " + str(i) + " j: " + str(j) + " angle_line_points_on: " + str(lanes_test[i].angle_side_points_on))
        # print("points_with_angles: " + str(lanes_test[i].points_with_angles))

        for k in range(len(lanes_test[i].points)):
            line_quadrant  = lanes_test[i].points_with_angles[k][3]
            # print("lanes_test[i].points_with_angles[k]: " + str(lanes_test[i].points_with_angles[k]))
            x_offset = lw_half*math.sin(lanes_test[i].points_with_angles[k][4])
            y_offset = lw_half*math.cos(lanes_test[i].points_with_angles[k][4])
            # print("before x_offset: " + str(x_offset) + " y_offset: " + str(y_offset))
            larger_offset = max(abs(x_offset),abs(y_offset))
            factor = lw_half / larger_offset
            x_offset = x_offset * factor
            y_offset = y_offset * factor
            # print("after x_offset: " + str(x_offset) + " y_offset: " + str(y_offset))
            # print("larger_offset: " + str(larger_offset))
            modulus = math.sqrt((x_offset**2) + (y_offset**2))
            # print("modulus: " + str(modulus))
            x1 = lanes_test[i].points_with_angles[k][0] + x_offset
            y1 = lanes_test[i].points_with_angles[k][1] - y_offset
            x2 = lanes_test[i].points_with_angles[k][0] - x_offset
            y2 = lanes_test[i].points_with_angles[k][1] + y_offset
            lanes_test[i].side_points.append([x1,y1,x2,y2])
populate_points_arrays_and_find_side_points(lanes_test)
def find_next_upper_side_point(point_1,latest_upper_line_point,point_2,side_point_2_1,side_point_2_2,lanes_test,lane_of_interest):
    latest_upper_line_point = [latest_upper_line_point]
    side_point_options = [side_point_2_1,side_point_2_2]
    centre_line = [point_1,point_2]
    pair = []
    for i in range(len(latest_upper_line_point)):
        for j in range(len(side_point_options)):
            # print("new upper side point")
            # first check intersection between
            side_line_opt = [latest_upper_line_point[i],side_point_options[j]]
            # print("side_line_opt: " + str(side_line_opt))
            # print("centre_line: " + str(centre_line))
            # input("Press Enter to continue...")
            xdiff = (centre_line[0][0] - centre_line[1][0], side_line_opt[0][0] - side_line_opt[1][0])
            ydiff = (centre_line[0][1] - centre_line[1][1], side_line_opt[0][1] - side_line_opt[1][1])

            def det(a, b):
                return a[0] * b[1] - a[1] * b[0]

            div = det(xdiff, ydiff)
            if div == 0:
                x = 0
                y = 0
                intersection_cross = 0 # so do not cross
                # print(" parallel" + " latest_upper_line_point[i]: " + str(latest_upper_line_point[i]) + " side_point_options[j]: " + str(side_point_options[j]))
                pair.append([latest_upper_line_point[i], side_point_options[j]])
                lanes_test[lane_of_interest].upper_line_points.append(side_point_options[j])
                # input("Press Enter to continue...")

                # print("0: " + " upper_line_points: " + str(lanes_test[lane_of_interest].upper_line_points))
               # raise Exception('lines do not intersect')
            else:
               d = (det(*centre_line), det(*side_line_opt))
               x = det(d, xdiff) / div
               y = det(d, ydiff) / div
               x_round = round(x)
               y_round = round(y)
               centre_line_min_x = min(centre_line[0][0],centre_line[1][0])
               centre_line_max_x = max(centre_line[0][0],centre_line[1][0])
               centre_line_min_y = min(centre_line[0][1],centre_line[1][1])
               centre_line_max_y = max(centre_line[0][1],centre_line[1][1])
               # print("x: " + str(x) + " y: " + str(y))
               # print("x_round: " + str(x_round) + " y_round: " + str(y_round))
               # print("centre_line_min_x: " + str(centre_line_min_x) + " centre_line_max_x: " + str(str(centre_line_max_x))+ " centre_line_min_y: " + str(centre_line_min_y) + " centre_line_max_y: " + str(centre_line_max_y))
               # input("Press Enter to continue...")
               if x_round >= centre_line_min_x and x_round <= centre_line_max_x and y_round >= centre_line_min_y and y_round <= centre_line_max_y:
               # if x >= centre_line_min_x and x <= centre_line_max_x and y >= centre_line_min_y and y <= centre_line_max_y:
                   # print("x: " + str(x) + " y: " + str(y) + " intersects line_1")
                   # print("4")
                   intersection_cross = 1
               else:
                   # print("x: " + str(x) + " y: " + str(y) + " doesn't intersect line_1")
                   # print(" doesn't intersect line_1" + " latest_upper_line_point[i]: " + str(latest_upper_line_point[i]) + " side_point_options[j]: " + str(side_point_options[j]))
                   pair.append([latest_upper_line_point[i], side_point_options[j]])
                   lanes_test[lane_of_interest].upper_line_points.append(side_point_options[j])
                   print
def find_next_lower_side_point(point_1,latest_lower_line_point,point_2,side_point_2_1,side_point_2_2,lanes_test,lane_of_interest):
    latest_lower_line_point = [latest_lower_line_point]
    side_point_options = [side_point_2_1,side_point_2_2]
    centre_line = [point_1,point_2]
    pair = []
    for i in range(len(latest_lower_line_point)):
        for j in range(len(side_point_options)):
            # first check intersection between
            # print("new lower side point")
            side_line_opt = [latest_lower_line_point[i],side_point_options[j]]
            # print("side_line_opt: " + str(side_line_opt))
            xdiff = (centre_line[0][0] - centre_line[1][0], side_line_opt[0][0] - side_line_opt[1][0])
            ydiff = (centre_line[0][1] - centre_line[1][1], side_line_opt[0][1] - side_line_opt[1][1])

            def det(a, b):
                return a[0] * b[1] - a[1] * b[0]

            div = det(xdiff, ydiff)
            if div == 0:
                x = 0
                y = 0
                intersection_cross = 0 # so do not cross
                # print(" parallel" + " latest_lower_line_point[i]: " + str(latest_lower_line_point[i]) + " side_point_options[j]: " + str(side_point_options[j]))
                pair.append([latest_lower_line_point[i], side_point_options[j]])
                lanes_test[lane_of_interest].lower_line_points.append(side_point_options[j])

               # raise Exception('lines do not intersect')
            else:
               d = (det(*centre_line), det(*side_line_opt))
               x = det(d, xdiff) / div
               y = det(d, ydiff) / div
               x_round = round(x)
               y_round = round(y)
               centre_line_min_x = min(centre_line[0][0],centre_line[1][0])
               centre_line_max_x = max(centre_line[0][0],centre_line[1][0])
               centre_line_min_y = min(centre_line[0][1],centre_line[1][1])
               centre_line_max_y = max(centre_line[0][1],centre_line[1][1])
               if x_round >= centre_line_min_x and x_round <= centre_line_max_x and y_round >= centre_line_min_y and y_round <= centre_line_max_y:
               # if x >= centre_line_min_x and x <= centre_line_max_x and y >= centre_line_min_y and y <= centre_line_max_y:
                   # print("x: " + str(x) + " y: " + str(y) + " intersects line_1")
                   # print("5")
                   intersection_cross = 1
               else:
                   # print("x: " + str(x) + " y: " + str(y) + " doesn't intersect line_1")
                   # print(" doesn't intersect line_1" + " latest_lower_line_point[i]: " + str(latest_lower_line_point[i]) + " side_point_options[j]: " + str(side_point_options[j]))
                   pair.append([latest_lower_line_point[i], side_point_options[j]])
                   lanes_test[lane_of_interest].lower_line_points.append(side_point_options[j])
def define_and_draw_upper_line(lanes_test):
    #draw upper line
    for i in range(len(lanes_test)): # loop through all lanes
        for j in range(len(lanes_test[i].points)):
            if j == 0: # the first point defines the upper and lower point on that lane
                point = lanes_test[i].points[j]
                side_point_1 = lanes_test[i].side_points[j][0:2]
                side_point_2 = lanes_test[i].side_points[j][2:]
                # print("side_point_1 first: " + str(side_point_1))
                # print("side_point_2 first: " + str(side_point_2))
                if side_point_1[0] >= point[0] and side_point_1[1] <= point[1]:
                    lanes_test[i].upper_line_points.append(side_point_1)
                    lanes_test[i].lower_line_points.append(side_point_2)
                    # print("1")
                elif side_point_1[0] <= point[0] and side_point_1[1] < point[1]:
                    lanes_test[i].upper_line_points.append(side_point_1)
                    lanes_test[i].lower_line_points.append(side_point_2)
                    # print("2")
                elif side_point_1[0] >= point[0] and side_point_1[1] > point[1]:
                    lanes_test[i].upper_line_points.append(side_point_2)
                    lanes_test[i].lower_line_points.append(side_point_1)
                    # print("3")
                elif side_point_1[0] <= point[0] and side_point_1[1] >= point[1]:
                    lanes_test[i].upper_line_points.append(side_point_2)
                    lanes_test[i].lower_line_points.append(side_point_1)
                    # print("4")
            else:
                # print("here: " + str(lanes_test[i].upper_line_points))
                # print("here j: " + str(j))
                # print("lanes_test[i].points[j-1]: " + str(lanes_test[i].points[j-1]))
                # print("lanes_test[i].side_points: " + str(lanes_test[i].side_points))
                # print("lanes_test[i].upper_line_points: " + str(lanes_test[i].upper_line_points))
                # print("lanes_test[i].upper_line_points[j-1]: " + str(lanes_test[i].upper_line_points[j-1]))
                find_next_upper_side_point(lanes_test[i].points[j-1], lanes_test[i].upper_line_points[j-1],lanes_test[i].points[j],lanes_test[i].side_points[j][0:2],lanes_test[i].side_points[j][2:4],lanes_test,i)
                find_next_lower_side_point(lanes_test[i].points[j-1], lanes_test[i].lower_line_points[j-1],lanes_test[i].points[j],lanes_test[i].side_points[j][0:2],lanes_test[i].side_points[j][2:4],lanes_test,i)
define_and_draw_upper_line(lanes_test)
def define_and_draw_lower_line(lanes_test):
    # draw lower line
    for i in range(len(lanes_test)): # loop through all lanes
        # print("points: " + str(lanes_test[i].points))
        # print("side points: " + str(lanes_test[i].side_points))
        # print("upper_line_points: " + str(lanes_test[i].upper_line_points))
        # print("lower_line_points: " + str(lanes_test[i].lower_line_points))
        for j in range((len(lanes_test[i].points)) - 1 ):
            # print("j: " + str(j))
            x1 = lanes_test[i].points[j][0]
            y1 = lanes_test[i].points[j][1]
            x2 = lanes_test[i].points[j + 1][0]
            y2 = lanes_test[i].points[j + 1][1]
            # canvas.create_line(x1,y1,x2,y2,dash=(4,1))
            x1_upper = lanes_test[i].upper_line_points[j][0]
            y1_upper = lanes_test[i].upper_line_points[j][1]
            x2_upper = lanes_test[i].upper_line_points[j + 1][0]
            y2_upper = lanes_test[i].upper_line_points[j + 1][1]
            # canvas.create_line(x1_upper,y1_upper,x2_upper,y2_upper,width=2)
            canvas.create_line(x1_upper,y1_upper,x2_upper,y2_upper)
            x1_lower = lanes_test[i].lower_line_points[j][0]
            y1_lower = lanes_test[i].lower_line_points[j][1]
            x2_lower = lanes_test[i].lower_line_points[j + 1][0]
            y2_lower = lanes_test[i].lower_line_points[j + 1][1]
            canvas.create_line(x1_lower,y1_lower,x2_lower,y2_lower)
            if j == (len(lanes_test[i].points)) - 2:
                canvas.create_line(lanes_test[i].lower_line_points[j + 1][0],lanes_test[i].lower_line_points[j + 1][1],lanes_test[i].upper_line_points[j + 1][0],lanes_test[i].upper_line_points[j + 1][1],dash=(4,1))
define_and_draw_lower_line(lanes_test)
#####
def create_lanes_at_junc(juncs_test,lanes_test):
    for i in range(len(juncs_test)):
        for j in range(len(lanes_test)):
            # find distance between the last point in the lane and the centre of each junciton, if this distance is less than 2*lw the lane belongs to the lanes_at_junc
            x1 = juncs_test[i].centre_x
            y1 = juncs_test[i].centre_y
            x2 = lanes_test[j].points[-1][0] # the x value from the last point in the lane
            y2 = lanes_test[j].points[-1][1] # the y value from the last point in the lane
            dist = math.sqrt(((y2 - y1)**2) + ((x2 - x1)**2))
            if dist < (2*lw):
                # lane is belongs to junc, lanes_at_junc
                lanes_test[j].junc_num = i
                juncs_test[i].lanes_at_junc.append(j)
                juncs_test[i].light_lanes_at_junc.append(j)
                juncs_test[i].same_light_lanes_link.append(j)
        # juncs_test[i].green_lanes_at_junc = juncs_test[i].lanes_at_junc[0] # set the initial green_lanes_at_junc
create_lanes_at_junc(juncs_test,lanes_test)
def create_lanes_leaving_junc(juncs_test,lanes_test):
    for i in range(len(juncs_test)):
        for j in range(len(lanes_test)):
            # find distance between the first point in the lane and the centre of each junciton, if this distance is less than 2*lw the lane is moving away from junc so add it to lanes_leaving_junc
            x1 = juncs_test[i].centre_x
            y1 = juncs_test[i].centre_y
            x2 = lanes_test[j].points[0][0] # the x value from the first point in the lane
            y2 = lanes_test[j].points[0][1] # the y value from the first point in the lane
            dist = math.sqrt(((y2 - y1)**2) + ((x2 - x1)**2))
            if dist < (2*lw):
                # lane is belongs to junc, lanes_at_junc
                lanes_test[j].junc_num_leaving = i
                juncs_test[i].lanes_leaving_junc.append(j)
        print("junc:  "+ str(i) + " lanes_leaving_junc: " + str(juncs_test[i].lanes_leaving_junc))
create_lanes_leaving_junc(juncs_test,lanes_test)
def create_next_lanes(juncs_test,lanes_test):
    for i in range(len(lanes_test)):
        # print("lanes_test[i].junc_num: " + str(lanes_test[i].junc_num))
        if lanes_test[i].junc_num != 9999:
            junc_temp = lanes_test[i].junc_num
            for lane_temp in juncs_test[junc_temp].lanes_leaving_junc:
                # find point of interection between the lane_of_interest (i) and the lanes_leaving_junc
                point_of_intersection = find_intersection_point_between_lines_for_next_lanes(lanes_test[i].points, lanes_test[lane_temp].points)
                # print("point_of_intersection: " + str(point_of_intersection))
                # find distance between point_of_intersection and the centre of the junction
                if point_of_intersection == None:
                    # if lanes_test[].orien of the lanes are equal then they are in the same direction and parallel so add to next_lanes
                    if lanes_test[i].orien == lanes_test[lane_temp].orien:
                        lanes_test[i].next_lanes.append(lane_temp)
                else:
                    x1 = juncs_test[junc_temp].centre_x
                    y1 = juncs_test[junc_temp].centre_y
                    x2 = point_of_intersection[0] # the x value from the first point in the lane
                    y2 = point_of_intersection[1] # the y value from the first point in the lane
                    dist = math.sqrt(((y2 - y1)**2) + ((x2 - x1)**2))
                    if dist < (2*lw):
                        lanes_test[i].next_lanes.append(lane_temp)
        if len(lanes_test[i].next_lanes) == 0:
            lanes_test[i].next_lanes.append(9999)
create_next_lanes(juncs_test,lanes_test)
entry_lanes = []
exit_lanes = []
internal_lanes = []
def create_entry_exit_internal_lanes(entry_lanes,exit_lanes,internal_lanes,lanes_test):
    for i in range(len(lanes_test)):
        if lanes_test[i].junc_num_leaving == 9999:
            entry_lanes.append(i)
        elif lanes_test[i].next_lanes[0] == 9999:
            exit_lanes.append(i)
        else:
            internal_lanes.append(i)
create_entry_exit_internal_lanes(entry_lanes,exit_lanes,internal_lanes,lanes_test)
#####
# find point of intersection between lane and next lanes
def find_point_of_intersection_between_lane_and_next_lanes(lanes_test):
    for i in range(len(lanes_test)):
        lane_last_point = lanes_test[i].points[-1][0:2]
        lane_second_last_point = lanes_test[i].points[-2][0:2]
        lane_points = [lane_second_last_point,lane_last_point]
        # print("lane_last_point: " + str(lane_last_point) + " sec_last: " + str(lane_second_last_point))
        for j in lanes_test[i].next_lanes:
            #find lanes_test
            if j != 9999:
                next_lane_dealt_wth = 0
                # check to see if next_lane is in map_free_turn_next_lanes
                if j in lanes_test[i].free_turn_next_lanes:
                    # found true point_of_intersection between the lane, ie. find the lane line the point_of_intersection lies on
                    # find the point of intersection between the next_lane and every line in the current lane
                    # loop through lanes_test.points_with_angles
                    point_store_temp = []
                    point_store_temp.append(j)
                    num_lines_in_lane = len(lanes_test[i].points_with_angles) - 1
                    for k in range(num_lines_in_lane):
                        line_point_1_x = lanes_test[i].points_with_angles[k][0]
                        line_point_1_y = lanes_test[i].points_with_angles[k][1]
                        line_point_2_x = lanes_test[i].points_with_angles[k + 1][0]
                        line_point_2_y = lanes_test[i].points_with_angles[k + 1][1]
                        line_angle = lanes_test[i].points_with_angles[k][2]

                        # find point_of_intersection, if lies on the line then it is the true point_of_intersection, if it doesn't intersection any lane line treat it as a normal next_lane
                        lane_line_points = [[line_point_1_x,line_point_1_y],[line_point_2_x,line_point_2_y]]
                        next_lane_first_point = lanes_test[j].points[0][0:2]
                        next_lane_second_point = lanes_test[j].points[1][0:2]
                        next_lane_points = [next_lane_first_point,next_lane_second_point]
                        xdiff = (lane_line_points[0][0] - lane_line_points[1][0], next_lane_points[0][0] - next_lane_points[1][0])
                        ydiff = (lane_line_points[0][1] - lane_line_points[1][1], next_lane_points[0][1] - next_lane_points[1][1])
                        point_store_temp.append([line_point_1_x,line_point_1_y])

                        def det(a, b):
                            return a[0] * b[1] - a[1] * b[0]
                        div = det(xdiff, ydiff)
                        if div == 0:
                            intersection_cross = 0 # so do not cross, could be straight ahead or parallel
                            x = next_lane_first_point[0]
                            y = next_lane_first_point[1]
                        else:
                            d = (det(*lane_points), det(*next_lane_points))
                            x = det(d, xdiff) / div
                            y = det(d, ydiff) / div
                            x_round = round(x)
                            y_round = round(y)
                        # check if lies on lane line if dist between the ends of the line are equal to distance between the ends of line and point of intersection
                        dist_lane_line = math.sqrt(((line_point_2_y - line_point_1_y)**2) + ((line_point_2_x - line_point_1_x)**2))
                        dist_between_point_of_inters_and_start_of_lane_line = math.sqrt(((y - line_point_1_y)**2) + ((x - line_point_1_x)**2))
                        dist_between_point_of_inters_and_end_of_lane_line = math.sqrt(((line_point_2_y - y)**2) + ((line_point_2_x - x)**2))
                        if (dist_between_point_of_inters_and_start_of_lane_line + dist_between_point_of_inters_and_end_of_lane_line) == dist_lane_line:
                            # free_turn_next_lane turns off from curent lane at this lane line, thus this is the TRUE point_of_intersection
                            lanes_test[i].next_lanes_intersection.append([j,x,y])
                            lanes_test[i].free_turn_next_lanes_intersection.append([j,x,y])
                            lanes_test[i].end_point_for_free_turn_next_lanes.append([j,x,y])
                            point_store_temp.append([x,y])
                            next_lane_dealt_with = 1
                    if len(lanes_test[i].free_turn_next_lanes_intersection) == 0:
                        # this free_turn_next_lane does not turn off in the middle of the current lane, thus must turn off at the end. ie. a junction but not controlled by lights
                        # thus follow the same process if the free_turn_next_lane was a normal next_lane
                        next_lane_dealt_with = 0
                        # use the last points in the curent lane to find intersection at junction with free_turn_next_lane
                        xdiff = (lane_points[0][0] - lane_points[1][0], next_lane_points[0][0] - next_lane_points[1][0])
                        ydiff = (lane_points[0][1] - lane_points[1][1], next_lane_points[0][1] - next_lane_points[1][1])
                        def det(a, b):
                            return a[0] * b[1] - a[1] * b[0]
                        div = det(xdiff, ydiff)
                        if div == 0:
                            intersection_cross = 0 # so do not cross, could be straight ahead or parallel
                            x = next_lane_first_point[0]
                            y = next_lane_first_point[1]
                        else:
                            d = (det(*lane_points), det(*next_lane_points))
                            x = det(d, xdiff) / div
                            y = det(d, ydiff) / div
                            x_round = round(x)
                            y_round = round(y)
                            if x == lane_last_point[0] and y == lane_last_point[1]:
                                # if lanes aren't parallel but there is onlt a small angle difference, sometimes the point_of_intersection = lane_last_point which will cause an error when finding the move points between these two.
                                # therefore, change point_of_intersection to the first_point of the next_lane
                                x = next_lane_first_point[0]
                                y = next_lane_first_point[1]
                            intersection_cross = 1 # so do cross
                            # canvas.create_oval((x + 2),(y + 2),(x - 2),(y -2))
                            # lanes_test[i].next_lanes_intersection.append([j,next_lane_points[0][0],next_lane_points[0][1]])
                        dist_between_last_point_and_point_of_intersection = math.sqrt(((y - lane_last_point[1])**2) + ((x - lane_last_point[0])**2))
                        # check if point of intersection is accurate, could be miles away
                        if dist_between_last_point_and_point_of_intersection > (3*lw):
                            x = next_lane_first_point[0]
                            y = next_lane_first_point[1]
                        lanes_test[i].next_lanes_intersection.append([j,x,y])
                        lanes_test[i].free_turn_next_lanes_intersection.append([j,x,y])
                        x_end = lane_last_point[0]
                        y_end = lane_last_point[1]
                        lanes_test[i].end_point_for_free_turn_next_lanes.append([j,x_end,y_end])
                        point_store_temp.append([x_end,y_end])
                        next_lane_dealt_with = 1
                    lanes_test[i].free_turn_next_lane_points.append(point_store_temp)


                else: # the normal process for a next_lane
                    next_lane_first_point = lanes_test[j].points[0][0:2]
                    next_lane_second_point = lanes_test[j].points[1][0:2]
                    next_lane_points = [next_lane_first_point,next_lane_second_point]
                    # print("j: " + str(j) + " next_lane_points: " + str(next_lane_points))

                    xdiff = (lane_points[0][0] - lane_points[1][0], next_lane_points[0][0] - next_lane_points[1][0])
                    ydiff = (lane_points[0][1] - lane_points[1][1], next_lane_points[0][1] - next_lane_points[1][1])

                    def det(a, b):
                        return a[0] * b[1] - a[1] * b[0]

                    div = det(xdiff, ydiff)
                    if div == 0:
                        intersection_cross = 0 # so do not cross, could be straight ahead or parallel
                        x = next_lane_first_point[0]
                        y = next_lane_first_point[1]
                        # canvas.create_oval((x + 2),(y + 2),(x - 2),(y -2))
                        # lanes_test[i].next_lanes_intersection.append([j,x,y])
                       # raise Exception('lines do not intersect')
                    else:
                        d = (det(*lane_points), det(*next_lane_points))
                        x = det(d, xdiff) / div
                        y = det(d, ydiff) / div
                        x_round = round(x)
                        y_round = round(y)
                        if x == lane_last_point[0] and y == lane_last_point[1]:
                            # if lanes aren't parallel but there is onlt a small angle difference, sometimes the point_of_intersection = lane_last_point which will cause an error when finding the move points between these two.
                            # therefore, change point_of_intersection to the first_point of the next_lane
                            x = next_lane_first_point[0]
                            y = next_lane_first_point[1]
                        intersection_cross = 1 # so do cross
                        # canvas.create_oval((x + 2),(y + 2),(x - 2),(y -2))
                        # lanes_test[i].next_lanes_intersection.append([j,next_lane_points[0][0],next_lane_points[0][1]])
                    dist_between_last_point_and_point_of_intersection = math.sqrt(((y - lane_last_point[1])**2) + ((x - lane_last_point[0])**2))
                    # check if point of intersection is accurate, could be miles away
                    if dist_between_last_point_and_point_of_intersection > (3*lw):
                        x = next_lane_first_point[0]
                        y = next_lane_first_point[1]
                    lanes_test[i].next_lanes_intersection.append([j,x,y])
find_point_of_intersection_between_lane_and_next_lanes(lanes_test)
def create_and_populate_free_turn_next_lane_points_with_angles(lanes_test):
    for i in range(len(lanes_test)):
        if len (lanes_test[i].free_turn_next_lanes ) > 0:
            # find angle between points between lane line's and final point in free_turn_next_lane_points
            for j in range(len(lanes_test[i].free_turn_next_lane_points)): # this lops through all the free_turn_lanes options
                # lanes_test[i].free_turn_next_lane_points_with_angles.append(lanes_test[i].free_turn_next_lane_points[j][0])
                points_with_angles_temp = []
                points_with_angles_temp.append(lanes_test[i].free_turn_next_lane_points[j][0])
                for k in range(1,(len(lanes_test[i].free_turn_next_lane_points[j])) - 1): # this looops through all the points
                    next_lane = lanes_test[i].free_turn_next_lane_points[j][0]
                    point_1 = lanes_test[i].free_turn_next_lane_points[j][k]
                    point_1_x = lanes_test[i].free_turn_next_lane_points[j][k][0]
                    point_1_y = lanes_test[i].free_turn_next_lane_points[j][k][1]
                    point_2 = lanes_test[i].free_turn_next_lane_points[j][k + 1]
                    point_2_x = lanes_test[i].free_turn_next_lane_points[j][k + 1][0]
                    point_2_y = lanes_test[i].free_turn_next_lane_points[j][k + 1][1]
                    # canvas.create_oval(point_2_x-3,point_2_y-3,point_2_x+3,point_2_y+3,fill = 'green')
                    # tk.update()
                    # input("herhee")
                    line_quadrant, angle_from_vert = find_line_info(point_1,point_2)
                    # lanes_test[i].free_turn_next_lane_points_with_angles.append([point_1_x,point_1_y,angle_from_vert])
                    points_with_angles_temp.append([point_1_x,point_1_y,angle_from_vert])
                # lanes_test[i].free_turn_next_lane_points_with_angles.append([point_2_x,point_2_y,0])
                points_with_angles_temp.append([point_2_x,point_2_y,0])
                lanes_test[i].free_turn_next_lane_points_with_angles.append(points_with_angles_temp)
create_and_populate_free_turn_next_lane_points_with_angles(lanes_test)
def find_move_points_between_lanes_info(lanes_test):
    for i in range(len(lanes_test)):
        for j in range(len(lanes_test[i].next_lanes_intersection)):
            # print("i: " + str(i) + " j: " + str(j))
            # populate with transition points angles from vertical leaving each transition point
            current_lane = i
            next_lane = lanes_test[i].next_lanes_intersection[j][0]
            current_lane_last_point_x = lanes_test[i].points[-1][0]
            current_lane_last_point_y = lanes_test[i].points[-1][1]
            next_lane_first_point_x =  lanes_test[lanes_test[i].next_lanes_intersection[j][0]].points[0][0]
            next_lane_first_point_y =  lanes_test[lanes_test[i].next_lanes_intersection[j][0]].points[0][1]
            next_lane = lanes_test[i].next_lanes_intersection[j][0]
            intersection_point_x = lanes_test[i].next_lanes_intersection[j][1]
            intersection_point_y = lanes_test[i].next_lanes_intersection[j][2]
            # check if next_lane is actually in current_lane's free_turn_next_lanes
            if next_lane in lanes_test[i].free_turn_next_lanes:
                # set current_lane_lat_point to equal the point the free_turn_next_lane leaves the current_lane
                # find the next_lane in end_point_for_free_turn_next_lanes
                for p in range(len(lanes_test[i].end_point_for_free_turn_next_lanes)):
                    if next_lane == lanes_test[i].end_point_for_free_turn_next_lanes[p][0]:
                        current_lane_last_point_x = lanes_test[i].end_point_for_free_turn_next_lanes[p][1]
                        current_lane_last_point_y = lanes_test[i].end_point_for_free_turn_next_lanes[p][2]
                        next_lane_first_point_x =  lanes_test[lanes_test[i].next_lanes_intersection[j][0]].points[0][0]
                        next_lane_first_point_y =  lanes_test[lanes_test[i].next_lanes_intersection[j][0]].points[0][1]
                        next_lane = lanes_test[i].next_lanes_intersection[j][0]
                        intersection_point_x = next_lane_first_point_x
                        intersection_point_y = next_lane_first_point_y


            # next_lane_first_point_x =  lanes_test[lanes_test[i].next_lanes_intersection[j][0]].points[0][0]
            # next_lane_first_point_y =  lanes_test[lanes_test[i].next_lanes_intersection[j][0]].points[0][1]
            # next_lane = lanes_test[i].next_lanes_intersection[j][0]
            # intersection_point_x = lanes_test[i].next_lanes_intersection[j][1]
            # intersection_point_y = lanes_test[i].next_lanes_intersection[j][2]
            # print("i " + str(i))
            # print("current_lane_last_point_x: " + str(current_lane_last_point_x))
            # print("current_lane_last_point_y: " + str(current_lane_last_point_y))
            # print("intersection_point_x: " + str(intersection_point_x))
            # print("intersection_point_y: " + str(intersection_point_y))

            if (intersection_point_x == next_lane_first_point_x) and (intersection_point_y == next_lane_first_point_y):
                # print("here 1")
                # straight line transition so don't need to append to  next_lanes_transition_points again also used for free_turn_next_lanes
                line_quadrant, angle_last_to_intersect_point = find_line_info([current_lane_last_point_x,current_lane_last_point_y],[intersection_point_x,intersection_point_y])
                lanes_test[i].next_lanes_transition_points.append([current_lane,next_lane, current_lane_last_point_x,current_lane_last_point_y,angle_last_to_intersect_point])
            else:
                # print("here 2")
                line_quadrant, angle_last_to_intersect_point = find_line_info([current_lane_last_point_x,current_lane_last_point_y],[intersection_point_x,intersection_point_y])
                line_quadrant, angle_intersect_to_first_point = find_line_info([intersection_point_x,intersection_point_y],[next_lane_first_point_x,next_lane_first_point_y])
                lanes_test[i].next_lanes_transition_points.append([current_lane,next_lane,current_lane_last_point_x,current_lane_last_point_y,angle_last_to_intersect_point, intersection_point_x,intersection_point_y,angle_intersect_to_first_point])
            # if i == 30:
            #     print("next_lanes_transition_points: " + str(lanes_test[i].next_lanes_transition_points))
            #     input("pause 4")
        # print("next_lanes_transition_points: " + str(lanes_test[i].next_lanes_transition_points))
    ##### move pointe -transition here
    for i in range(len(lanes_test)):
        for j in range(len(lanes_test[i].next_lanes_transition_points)):
            # if i == 4:
            #     print("j: " + str(j))
            temp_move_points = []
            if len(lanes_test[i].next_lanes_transition_points[j]) == 5: # simple striaght line transition to next lane
                current_lane = lanes_test[i].next_lanes_transition_points[j][0]
                next_lane = lanes_test[i].next_lanes_transition_points[j][1]
                move_point_x = lanes_test[i].next_lanes_transition_points[j][2] # start at last point of current lane
                move_point_y = lanes_test[i].next_lanes_transition_points[j][3]
                # move_point_x  = lanes_test[i].points_info_min[j][0] # start at start point of first line in lane
                # move_point_y = lanes_test[i].points_info_min[j][1]
                temp_angle = lanes_test[i].next_lanes_transition_points[j][4] # angle of line leaving point
                # temp_angle = lanes_test[i].points_info_min[j][2]
                temp_line_end_point_x = lanes_test[next_lane].points[0][0]
                temp_line_end_point_y = lanes_test[next_lane].points[0][1]
                # temp_line_end_point_x = lanes_test[i].points_info_min[j + 1][0]
                # temp_line_end_point_y = lanes_test[i].points_info_min[j + 1][1]
                dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
                # if j == 0:
                #     lanes_test[i].move_points_next_lanes.append([move_point_x,move_point_y,temp_angle]) # inoput first point in line
                # if dist_to_end_point == 0: # just in case the first point is the same as the end point
                #     lanes_test[i].move_points.append([move_point_x,move_point_y,temp_angle])
                while dist_to_end_point > 0:
                    # print("1"   " i: " + str(i) + " j: " + str(j))
                    if dist_to_end_point < move_val: # set the move_point tpo the end_point
                        move_point_x = temp_line_end_point_x
                        move_point_y = temp_line_end_point_y

                    else:
                        move_point_x += move_val*math.sin(temp_angle)
                        move_point_y -= move_val*math.cos(temp_angle)
                        move_point_x_rounded = round(move_point_x)
                        move_point_y_rounded = round(move_point_y)
                        temp_move_points.append([move_point_x,move_point_y,temp_angle])
                    dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
                    # lanes_test[i].move_points_next_lanes.append([move_point_x,move_point_y,temp_angle])
                    # temp_move_points.append([move_point_x,move_point_y,temp_angle])
            else: # if there is an intersection point
                current_lane = lanes_test[i].next_lanes_transition_points[j][0]
                next_lane = lanes_test[i].next_lanes_transition_points[j][1]
                move_point_x = lanes_test[i].next_lanes_transition_points[j][2] # start at last point of current lane
                move_point_y = lanes_test[i].next_lanes_transition_points[j][3]
                angle_last_to_intersection = lanes_test[i].next_lanes_transition_points[j][4] # angle of line leaving point
                intersection_point_x = lanes_test[i].next_lanes_transition_points[j][5]
                intersection_point_y = lanes_test[i].next_lanes_transition_points[j][6]
                angle_intersection_to_first = lanes_test[i].next_lanes_transition_points[j][7] # angle of line leaving point

                next_lane_point_x = lanes_test[next_lane].points[0][0]
                next_lane_point_y = lanes_test[next_lane].points[0][1]
                # first run for last point to intersection
                temp_line_end_point_x = intersection_point_x
                temp_line_end_point_y = intersection_point_y
                temp_angle = angle_last_to_intersection # angle of line leaving point
                dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
                # if j == 0:
                #     lanes_test[i].move_points_next_lanes.append([move_point_x,move_point_y,temp_angle]) # inoput first point in line
                # if dist_to_end_point == 0: # just in case the first point is the same as the end point
                #     lanes_test[i].move_points.append([move_point_x,move_point_y,temp_angle])
                while dist_to_end_point > 0:
                    # print("2"  " i: " + str(i) + " j: " + str(j))
                    if dist_to_end_point < move_val: # set the move_point tpo the end_point
                        move_point_x = temp_line_end_point_x
                        move_point_y = temp_line_end_point_y
                    else:
                        # move_point_x += move_val*math.sin(temp_angle)
                        # move_point_y -= move_val*math.cos(temp_angle)
                        move_point_x += move_val_transition*math.sin(temp_angle)
                        move_point_y -= move_val_transition*math.cos(temp_angle)
                        move_point_x_rounded = round(move_point_x)
                        move_point_y_rounded = round(move_point_y)
                        temp_move_points.append([move_point_x,move_point_y,temp_angle])
                    dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
                    # lanes_test[i].move_points_next_lanes.append([move_point_x,move_point_y,temp_angle])
                    # temp_move_points.append([move_point_x,move_point_y,temp_angle])

                ##  now run from interseciton point (current move_point) to the next_lane_first point
                temp_line_end_point_x = next_lane_point_x
                temp_line_end_point_y = next_lane_point_y
                temp_angle = angle_intersection_to_first # angle of line leaving point
                dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
                # if j == 0:
                #     lanes_test[i].move_points_next_lanes.append([move_point_x,move_point_y,temp_angle]) # input first point in line

                while dist_to_end_point > 0:
                # int = 0
                # while int < 40:
                    # print("3"  " i: " + str(i) + " j: " + str(j))
                    # print("move_point_x: " + str(move_point_x) + " move_point_y: " + str(move_point_y))
                    # print("temp_line_end_point_x: " + str(temp_line_end_point_x) + " temp_line_end_point_y: " + str(temp_line_end_point_y))
                    if dist_to_end_point < move_val: # set the move_point tpo the end_point
                        move_point_x = temp_line_end_point_x
                        move_point_y = temp_line_end_point_y
                    else:
                        # move_point_x += move_val*math.sin(temp_angle)
                        # move_point_y -= move_val*math.cos(temp_angle)
                        move_point_x += move_val_transition*math.sin(temp_angle)
                        move_point_y -= move_val_transition*math.cos(temp_angle)
                        move_point_x_rounded = round(move_point_x)
                        move_point_y_rounded = round(move_point_y)
                        temp_move_points.append([move_point_x,move_point_y,temp_angle])
                    dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
                    # lanes_test[i].move_points_next_lanes.append([move_point_x,move_point_y,temp_angle])
                    # temp_move_points.append([move_point_x,move_point_y,temp_angle])
                    # int += 1
            lanes_test[i].move_points_next_lanes.append(temp_move_points)
find_move_points_between_lanes_info(lanes_test)
def find_move_points_in_each_lane(lanes_test):
    ###### create move_points which cars transition to for each lane by move_val
    # first create a store of point and angle of line leaving point
    for i in range(len(lanes_test)):
        for j in range(len(lanes_test[i].points)):
            lanes_test[i].points_info_min.append(lanes_test[i].points_with_angles[j][0:3])

    for i in range(len(lanes_test)):
        for j in range(len(lanes_test[i].points_info_min) - 1):
            move_point_x  = lanes_test[i].points_info_min[j][0] # start at start point of first line in lane
            move_point_y = lanes_test[i].points_info_min[j][1]
            temp_angle = lanes_test[i].points_info_min[j][2]
            temp_line_end_point_x = lanes_test[i].points_info_min[j + 1][0]
            temp_line_end_point_y = lanes_test[i].points_info_min[j + 1][1]
            dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
            if j == 0:
                lanes_test[i].move_points.append([move_point_x,move_point_y,temp_angle]) # inoput first point in line
            # if dist_to_end_point == 0: # just in case the first point is the same as the end point
            #     lanes_test[i].move_points.append([move_point_x,move_point_y,temp_angle])
            while dist_to_end_point > 0:
                if dist_to_end_point < move_val: # set the move_point tpo the end_point
                    move_point_x = temp_line_end_point_x
                    move_point_y = temp_line_end_point_y
                else:
                    move_point_x += move_val*math.sin(temp_angle)
                    move_point_y -= move_val*math.cos(temp_angle)
                    move_point_x_rounded = round(move_point_x)
                    move_point_y_rounded = round(move_point_y)
                dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
                lanes_test[i].move_points.append([move_point_x,move_point_y,temp_angle])
        if lanes_test[i].next_lanes[0] == 9999:
            lanes_test[i].move_points.append([50,50,temp_angle])
    for i in range(len(lanes_test)):
        for j in range(len(lanes_test[i].move_points)):
            # canvas.create_oval((lanes_test[i].move_points[j][0] + 2),(lanes_test[i].move_points[j][1] + 2),(lanes_test[i].move_points[j][0] - 2),(lanes_test[i].move_points[j][1] -2))
            if j < len(lanes_test[i].move_points) - 1:
                if (lanes_test[i].move_points[j][0] == lanes_test[i].move_points[j + 1][0]) and (lanes_test[i].move_points[j][1] == lanes_test[i].move_points[j + 1][1]):
                    print("duplicate    i: " + str(i) + " j: " + str(j))
find_move_points_in_each_lane(lanes_test)
def find_free_turn_next_lane_move_points_in_lane(lanes_test):
    for i in range(len(lanes_test)):
        if len(lanes_test[i].free_turn_next_lanes) > 0:
            for j in range(len(lanes_test[i].free_turn_next_lane_points_with_angles)): # loop through the next_lane options
                next_lane = lanes_test[i].free_turn_next_lane_points_with_angles[j][0]
                move_points_temp = []
                move_points_temp.append(next_lane)
                for k in range(1,(len(lanes_test[i].free_turn_next_lane_points_with_angles[j])) - 1):
                    next_lane = lanes_test[i].free_turn_next_lane_points_with_angles[j][0]
                    move_point_x = lanes_test[i].free_turn_next_lane_points_with_angles[j][k][0] # start at start point of first line in lane
                    move_point_y = lanes_test[i].free_turn_next_lane_points_with_angles[j][k][1]
                    temp_angle = lanes_test[i].free_turn_next_lane_points_with_angles[j][k][2]
                    temp_line_end_point_x = lanes_test[i].free_turn_next_lane_points_with_angles[j][k + 1][0]
                    temp_line_end_point_y = lanes_test[i].free_turn_next_lane_points_with_angles[j][k + 1][1]
                    # canvas.create_oval(move_point_x-3,move_point_y-3,move_point_x+3,move_point_y+3,fill = 'green')
                    # canvas.create_oval(temp_line_end_point_x-3,temp_line_end_point_y-3,temp_line_end_point_x+3,temp_line_end_point_y+3,fill = 'red')
                    # tk.update()
                    # input("herer")
                    dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
                    if k == 1:
                        move_points_temp.append([move_point_x,move_point_y,temp_angle])
                    while dist_to_end_point > 0:
                        if dist_to_end_point < move_val: # set the move_point tpo the end_point
                            move_point_x = temp_line_end_point_x
                            move_point_y = temp_line_end_point_y
                        else:
                            move_point_x += move_val*math.sin(temp_angle)
                            move_point_y -= move_val*math.cos(temp_angle)
                            move_point_x_rounded = round(move_point_x)
                            move_point_y_rounded = round(move_point_y)
                        dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
                        move_points_temp.append([move_point_x,move_point_y,temp_angle])
                    lanes_test[i].free_turn_next_lane_move_points.append(move_points_temp)
find_free_turn_next_lane_move_points_in_lane(lanes_test)

### create light signal control
def turn_light_red(light_num):
    Control_display.turn_light_red(controls[light_num])
def turn_light_green(light_num):
    Control_display.turn_light_green(controls[light_num])
def turn_off_light(light_num):
    Control_display.turn_off_light(controls[light_num])
def create_controls(lanes_test,controls,Control_display):
    control_num = 0
    for i in range(len(lanes_test)):
        lane_end_point = lanes_test[i].points[-1]
        controls.append(Control_display(lane_end_point[0],lane_end_point[1],lanes_test,i,lw_half))
        lanes_test[i].control_num = i
        turn_light_red(lanes_test[i].control_num)
        # print("i_next_lanes: " + str(lanes_test[i].next_lanes))
        if lanes_test[i].next_lanes[0] == 9999: # an exit lane
            # print("i: " + str(i))
            turn_off_light(lanes_test[i].control_num)
create_controls(lanes_test,controls,Control_display)

def internal_lane_car_path_options_full():
    internal_lane_car_path_options_store = [[47, 43, 19, 16, 24, 43, 44, 64, 70, 90, 96, 116, 9999], [64, 49, 25, 22, 26, 9999], [4, 32, 38, 44, 61, 41, 38, 19, 16, 24, 43, 19, 11, 12, 38, 42, 48, 68, 72, 9999], [56, 80, 9999], [91, 92, 109, 105, 85, 77, 57, 58, 9999], [93, 71, 68, 53, 47, 43, 19, 14, 9999], [39, 40, 55, 58, 9999], [79, 80, 9999], [70, 87, 88, 105, 99, 100, 9999], [90, 96, 113, 114, 9999], [45, 19, 16, 20, 9999], [99, 102, 9999], [39, 13, 10, 16, 22, 28, 9999], [109, 89, 86, 92, 112, 116, 9999], [61, 55, 35, 32, 13, 3, 4, 34, 58, 9999], [33, 5, 2, 12, 38, 19, 14, 9999], [104, 108, 114, 9999], [22, 26, 9999], [11, 12, 38, 42, 48, 68, 53, 50, 9999], [87, 83, 84, 104, 110, 9999], [57, 35, 32, 38, 19, 11, 3, 4, 34, 58, 9999], [48, 70, 92, 109, 110, 9999], [41, 38, 19, 16, 22, 26, 9999], [23, 20, 9999], [49, 43, 39, 13, 8, 9999], [16, 24, 48, 65, 45, 39, 40, 55, 35, 32, 38, 42, 25, 22, 28, 9999], [82, 88, 105, 106, 9999], [56, 76, 82, 67, 61, 41, 13, 3, 6, 9999], [82, 86, 71, 65, 66, 83, 77, 80, 9999], [75, 72, 9999], [74, 91, 71, 68, 74, 94, 9999], [25, 20, 9999], [61, 55, 58, 9999], [2, 10, 14, 9999], [40, 55, 56, 76, 82, 67, 61, 55, 35, 32, 38, 19, 14, 9999], [69, 49, 46, 52, 74, 91, 87, 83, 63, 60, 64, 70, 87, 88, 110, 9999], [90, 75, 69, 49, 43, 44, 61, 55, 56, 80, 9999], [24, 43, 39, 40, 55, 35, 5, 2, 10, 16, 24, 46, 50, 9999], [3, 4, 32, 38, 42, 25, 17, 11, 3, 4, 34, 58, 9999], [105, 106, 9999], [65, 66, 88, 110, 9999], [108, 114, 9999], [69, 49, 25, 17, 14, 9999], [67, 64, 68, 53, 50, 9999], [83, 84, 106, 9999], [19, 11, 12, 40, 55, 56, 80, 9999], [97, 91, 92, 114, 9999], [11, 12, 40, 55, 35, 36, 9999], [18, 42, 25, 22, 26, 9999], [17, 18, 44, 64, 68, 72, 9999], [22, 28, 9999], [30, 52, 69, 49, 43, 44, 61, 62, 82, 86, 90, 94, 9999], [25, 20, 9999], [43, 44, 66, 86, 71, 68, 53, 31, 28, 9999], [104, 89, 86, 71, 49, 43, 44, 66, 88, 110, 9999], [91, 71, 68, 53, 50, 9999], [98, 104, 89, 67, 64, 68, 74, 96, 118, 9999], [86, 71, 65, 61, 55, 35, 5, 6, 9999], [55, 56, 80, 9999], [10, 18, 44, 64, 70, 90, 75, 69, 70, 87, 67, 45, 42, 48, 70, 92, 109, 110, 9999], [105, 99, 100, 9999], [24, 48, 70, 92, 109, 110, 9999], [77, 80, 9999], [97, 91, 71, 68, 72, 9999], [33, 36, 9999], [53, 31, 26, 9999], [74, 91, 92, 114, 9999], [60, 45, 39, 13, 8, 9999], [112, 97, 91, 71, 49, 46, 31, 28, 9999], [66, 83, 84, 106, 9999], [82, 88, 105, 99, 102, 9999], [53, 47, 25, 22, 30, 47, 48, 65, 61, 55, 35, 36, 9999], [84, 99, 79, 80, 9999], [112, 116, 9999], [12, 38, 19, 11, 8, 9999], [108, 93, 90, 96, 113, 109, 89, 86, 71, 65, 45, 42, 48, 68, 53, 31, 23, 17, 11, 12, 38, 19, 16, 22, 26, 9999], [83, 63, 41, 38, 44, 61, 55, 58, 9999], [93, 87, 88, 110, 9999], [64, 49, 25, 20, 9999], [76, 84, 104, 108, 93, 87, 83, 63, 60, 45, 19, 16, 20, 9999], [30, 52, 72, 9999], [42, 48, 70, 87, 67, 61, 55, 56, 76, 84, 104, 110, 9999], [91, 71, 49, 43, 39, 13, 8, 9999], [53, 47, 43, 39, 33, 36, 9999], [31, 23, 20, 9999], [86, 90, 94, 9999], [68, 72, 9999], [62, 82, 67, 64, 70, 87, 88, 108, 93, 90, 94, 9999], [43, 39, 13, 10, 14, 9999], [70, 90, 75, 53, 50, 9999], [85, 63, 60, 66, 88, 110, 9999], [90, 94, 9999], [62, 84, 104, 108, 112, 116, 9999], [42, 46, 31, 28, 9999], [16, 22, 30, 47, 43, 19, 14, 9999], [63, 41, 13, 3, 0, 9999], [89, 67, 45, 39, 13, 3, 6, 9999], [43, 39, 33, 34, 54, 41, 13, 3, 0, 9999], [18, 39, 13, 10, 14, 9999], [42, 25, 17, 11, 8, 9999], [18, 39, 13, 3, 6, 9999], [60, 64, 49, 46, 31, 26, 9999], [74, 91, 71, 65, 66, 83, 77, 78, 102, 9999], [24, 43, 19, 16, 24, 43, 44, 64, 70, 87, 83, 84, 99, 100, 9999], [23, 17, 18, 44, 64, 68, 53, 50, 9999], [112, 97, 94, 9999], [45, 19, 11, 8, 9999], [38, 44, 64, 68, 72, 9999], [97, 94, 9999], [13, 10, 18, 44, 64, 70, 87, 67, 45, 19, 14, 9999], [2, 10, 14, 9999], [38, 44, 66, 88, 110, 9999], [46, 31, 26, 9999], [23, 20, 9999], [39, 40, 60, 45, 19, 14, 9999], [2, 12, 33, 5, 6, 9999], [48, 70, 87, 88, 105, 85, 77, 78, 100, 9999], [74, 96, 116, 9999], [93, 71, 65, 45, 39, 40, 55, 56, 78, 100, 9999], [16, 24, 43, 44, 66, 83, 63, 60, 45, 42, 25, 22, 28, 9999], [76, 63, 60, 45, 42, 46, 50, 9999], [19, 14, 9999], [22, 30, 50, 9999], [10, 16, 22, 26, 9999], [52, 74, 94, 9999], [62, 84, 104, 110, 9999], [84, 106, 9999], [89, 83, 77, 78, 102, 9999], [46, 52, 72, 9999], [91, 71, 68, 72, 9999], [47, 25, 20, 9999], [57, 35, 5, 0, 9999], [62, 77, 57, 54, 60, 66, 83, 63, 60, 45, 42, 25, 20, 9999], [93, 87, 67, 61, 62, 84, 99, 102, 9999], [19, 11, 3, 0, 9999], [40, 62, 82, 86, 71, 49, 43, 44, 66, 86, 92, 114, 9999], [18, 42, 48, 65, 45, 42, 48, 70, 87, 88, 105, 106, 9999], [104, 89, 86, 71, 65, 45, 19, 16, 20, 9999], [49, 46, 50, 9999], [79, 80, 9999], [11, 8, 9999], [33, 5, 2, 12, 38, 19, 16, 22, 28, 9999], [90, 94, 9999], [64, 70, 92, 109, 110, 9999], [49, 46, 31, 23, 20, 9999], [53, 31, 26, 9999], [13, 8, 9999], [65, 66, 88, 105, 99, 102, 9999], [79, 80, 9999], [60, 45, 42, 48, 68, 74, 94, 9999], [24, 48, 70, 87, 83, 63, 41, 33, 36, 9999], [45, 39, 13, 8, 9999], [67, 64, 68, 72, 9999], [18, 39, 40, 55, 35, 5, 6, 9999], [60, 64, 68, 74, 91, 87, 88, 110, 9999], [108, 93, 71, 68, 53, 50, 9999], [18, 39, 33, 5, 2, 12, 40, 55, 56, 76, 63, 60, 66, 88, 110, 9999], [22, 28, 9999], [33, 5, 6, 9999], [19, 16, 24, 43, 19, 16, 22, 26, 9999], [35, 5, 6, 9999], [10, 14, 9999], [10, 18, 42, 48, 70, 92, 114, 9999], [82, 67, 45, 39, 33, 34, 58, 9999], [32, 38, 44, 66, 83, 84, 106, 9999], [33, 36, 9999], [76, 63, 60, 45, 19, 14, 9999], [86, 92, 112, 116, 9999], [82, 67, 45, 19, 14, 9999], [79, 57, 35, 32, 38, 44, 66, 83, 63, 41, 13, 10, 16, 24, 43, 19, 11, 3, 4, 36, 9999], [104, 108, 112, 118, 9999], [78, 98, 106, 9999], [30, 47, 48, 70, 90, 94, 9999], [22, 30, 52, 72, 9999], [24, 46, 50, 9999], [33, 36, 9999], [87, 67, 45, 19, 16, 24, 48, 68, 72, 9999], [10, 16, 20, 9999], [23, 20, 9999], [42, 48, 65, 45, 39, 33, 5, 2, 12, 38, 19, 11, 12, 40, 62, 82, 86, 90, 96, 118, 9999], [54, 62, 77, 78, 100, 9999], [52, 74, 96, 118, 9999], [92, 109, 105, 99, 79, 80, 9999], [2, 10, 16, 24, 43, 44, 66, 83, 77, 80, 9999], [30, 50, 9999], [2, 10, 14, 9999], [98, 85, 63, 41, 38, 19, 11, 8, 9999], [30, 50, 9999], [5, 0, 9999], [65, 45, 42, 25, 22, 26, 9999], [112, 118, 9999], [4, 36, 9999], [2, 12, 40, 55, 56, 76, 63, 41, 38, 44, 64, 49, 43, 19, 16, 24, 43, 19, 14, 9999], [63, 60, 64, 49, 43, 39, 33, 5, 6, 9999], [82, 88, 105, 106, 9999], [79, 57, 35, 32, 40, 55, 58, 9999], [86, 90, 75, 72, 9999], [109, 105, 99, 102, 9999], [46, 50, 9999], [42, 25, 20, 9999], [70, 87, 83, 77, 57, 35, 36, 9999], [78, 100, 9999], [19, 14, 9999], [46, 52, 74, 96, 113, 114, 9999], [17, 11, 12, 40, 62, 82, 86, 71, 49, 43, 39, 33, 5, 0, 9999], [96, 118, 9999], [99, 79, 57, 35, 32, 40, 55, 56, 78, 100, 9999], [39, 13, 10, 14, 9999], [43, 44, 64, 49, 43, 44, 64, 68, 72, 9999], [66, 83, 84, 104, 89, 67, 64, 68, 74, 91, 87, 67, 61, 55, 56, 78, 102, 9999], [65, 61, 41, 33, 36, 9999], [18, 42, 46, 52, 74, 94, 9999], [16, 24, 48, 65, 45, 39, 13, 3, 0, 9999], [32, 13, 8, 9999], [105, 99, 102, 9999], [66, 83, 63, 55, 35, 32, 38, 42, 25, 22, 30, 50, 9999], [91, 87, 83, 63, 41, 13, 8, 9999], [68, 53, 31, 23, 20, 9999], [84, 99, 79, 80, 9999], [53, 47, 48, 70, 87, 83, 63, 41, 33, 34, 58, 9999], [85, 82, 86, 90, 75, 69, 65, 45, 42, 25, 22, 30, 50, 9999], [64, 70, 87, 67, 64, 68, 53, 31, 23, 20, 9999], [66, 83, 63, 60, 45, 42, 48, 70, 90, 94, 9999], [66, 83, 77, 80, 9999], [49, 43, 19, 11, 12, 40, 60, 64, 70, 92, 114, 9999], [56, 80, 9999], [39, 33, 36, 9999], [99, 79, 80, 9999], [39, 13, 3, 0, 9999], [11, 12, 40, 62, 84, 106, 9999], [87, 67, 61, 41, 33, 34, 56, 80, 9999], [16, 24, 48, 65, 61, 55, 56, 80, 9999], [75, 53, 47, 25, 20, 9999], [46, 50, 9999], [13, 3, 6, 9999], [57, 54, 41, 13, 3, 0, 9999], [105, 85, 82, 86, 71, 49, 25, 17, 11, 8, 9999], [61, 62, 82, 67, 61, 41, 13, 3, 6, 9999], [89, 83, 63, 41, 33, 5, 6, 9999], [63, 41, 38, 19, 14, 9999], [25, 22, 30, 52, 69, 65, 45, 19, 16, 20, 9999], [91, 92, 114, 9999], [3, 4, 32, 40, 55, 56, 78, 98, 104, 89, 67, 61, 41, 38, 19, 11, 12, 33, 34, 56, 78, 102, 9999], [43, 39, 40, 60, 45, 39, 40, 55, 58, 9999], [3, 4, 36, 9999], [52, 72, 9999], [2, 12, 40, 60, 66, 83, 84, 99, 102, 9999], [38, 42, 46, 50, 9999], [88, 110, 9999], [92, 114, 9999], [86, 71, 68, 53, 31, 28, 9999], [89, 83, 77, 78, 98, 106, 9999], [83, 63, 41, 33, 5, 0, 9999], [55, 35, 36, 9999], [56, 76, 82, 88, 108, 93, 90, 75, 72, 9999], [45, 42, 48, 65, 61, 62, 77, 57, 58, 9999], [53, 31, 26, 9999], [63, 60, 64, 70, 90, 96, 118, 9999], [90, 94, 9999], [52, 72, 9999], [68, 53, 31, 28, 9999], [79, 57, 54, 62, 77, 78, 98, 104, 108, 93, 71, 49, 25, 22, 28, 9999], [64, 68, 72, 9999], [108, 93, 90, 96, 113, 109, 105, 99, 79, 80, 9999], [10, 18, 44, 61, 62, 82, 67, 64, 68, 53, 31, 28, 9999], [57, 35, 36, 9999], [22, 26, 9999], [108, 93, 71, 65, 45, 39, 13, 10, 14, 9999], [3, 4, 36, 9999], [85, 82, 67, 64, 49, 46, 50, 9999], [78, 98, 106, 9999], [11, 8, 9999], [109, 89, 83, 84, 104, 108, 93, 71, 65, 45, 42, 48, 68, 74, 94, 9999], [63, 41, 38, 42, 25, 22, 30, 52, 69, 65, 66, 86, 90, 75, 72, 9999], [47, 25, 17, 18, 44, 64, 68, 72, 9999], [79, 76, 84, 106, 9999], [48, 65, 61, 62, 77, 80, 9999], [31, 26, 9999], [33, 5, 6, 9999], [104, 108, 112, 118, 9999], [38, 44, 61, 55, 35, 32, 13, 10, 14, 9999], [17, 11, 8, 9999], [16, 24, 48, 68, 74, 91, 92, 112, 97, 75, 69, 70, 92, 109, 89, 67, 64, 70, 87, 83, 84, 99, 100, 9999], [65, 61, 62, 84, 104, 108, 114, 9999], [22, 26, 9999], [2, 12, 33, 34, 56, 78, 100, 9999], [53, 31, 26, 9999], [56, 78, 102, 9999], [18, 39, 40, 62, 77, 80, 9999], [78, 100, 9999], [77, 78, 100, 9999], [97, 94, 9999], [12, 33, 5, 2, 10, 18, 42, 25, 17, 14, 9999], [52, 69, 49, 43, 44, 64, 49, 46, 50, 9999], [32, 38, 44, 64, 49, 46, 50, 9999], [43, 44, 61, 41, 33, 36, 9999], [48, 68, 74, 91, 71, 65, 61, 41, 38, 42, 25, 22, 26, 9999], [67, 64, 68, 74, 96, 116, 9999], [97, 94, 9999], [44, 61, 62, 77, 57, 54, 41, 38, 44, 64, 70, 87, 67, 61, 62, 84, 106, 9999], [54, 41, 13, 3, 0, 9999], [22, 26, 9999], [2, 10, 18, 42, 46, 52, 74, 96, 116, 9999], [32, 38, 19, 11, 12, 38, 44, 66, 88, 108, 112, 97, 94, 9999], [41, 33, 34, 58, 9999], [35, 32, 38, 19, 16, 20, 9999], [34, 56, 78, 102, 9999], [4, 36, 9999], [40, 62, 82, 88, 105, 106, 9999], [87, 83, 77, 78, 102, 9999], [55, 56, 78, 98, 104, 89, 86, 92, 109, 105, 99, 100, 9999], [2, 10, 14, 9999], [76, 84, 104, 89, 86, 92, 112, 97, 75, 69, 65, 45, 42, 25, 17, 14, 9999], [18, 42, 25, 22, 28, 9999], [88, 108, 93, 87, 83, 77, 78, 98, 85, 63, 41, 38, 44, 64, 49, 43, 44, 64, 70, 87, 88, 110, 9999], [91, 92, 114, 9999], [5, 0, 9999], [60, 45, 19, 14, 9999], [71, 68, 74, 91, 92, 109, 89, 83, 77, 80, 9999], [91, 87, 88, 105, 85, 77, 78, 100, 9999], [39, 40, 55, 56, 80, 9999], [12, 40, 60, 66, 86, 90, 94, 9999], [61, 62, 84, 99, 79, 76, 63, 41, 33, 5, 6, 9999], [78, 102, 9999], [82, 67, 64, 68, 53, 47, 25, 22, 30, 52, 69, 49, 46, 31, 23, 17, 18, 42, 25, 20, 9999], [97, 91, 92, 109, 110, 9999], [42, 25, 22, 30, 47, 48, 68, 72, 9999], [71, 68, 74, 94, 9999], [34, 54, 60, 64, 68, 74, 94, 9999], [45, 39, 40, 62, 82, 67, 61, 41, 33, 36, 9999], [108, 114, 9999], [78, 102, 9999], [41, 33, 5, 2, 12, 40, 55, 58, 9999], [96, 116, 9999], [18, 44, 66, 88, 110, 9999], [87, 67, 61, 62, 77, 78, 98, 85, 82, 86, 90, 96, 118, 9999], [24, 48, 70, 92, 112, 118, 9999], [43, 44, 64, 49, 43, 44, 66, 83, 84, 99, 79, 76, 84, 104, 108, 114, 9999], [76, 63, 60, 45, 19, 11, 3, 4, 36, 9999], [88, 108, 93, 71, 65, 61, 62, 77, 57, 58, 9999], [97, 91, 87, 83, 63, 60, 66, 83, 63, 55, 35, 32, 40, 60, 64, 68, 53, 47, 43, 44, 66, 83, 63, 60, 66, 83, 63, 55, 56, 76, 82, 88, 108, 112, 118, 9999], [42, 25, 20, 9999], [70, 92, 114, 9999], [69, 49, 46, 31, 28, 9999], [69, 65, 66, 86, 71, 65, 45, 19, 11, 8, 9999], [54, 60, 64, 70, 92, 109, 89, 86, 71, 49, 43, 19, 11, 12, 33, 5, 2, 10, 14, 9999], [54, 62, 82, 67, 45, 39, 40, 62, 84, 104, 110, 9999], [65, 45, 19, 16, 20, 9999], [5, 0, 9999], [32, 38, 44, 66, 86, 92, 109, 89, 86, 92, 109, 105, 85, 77, 57, 58, 9999], [68, 72, 9999], [5, 0, 9999], [22, 30, 52, 69, 70, 90, 94, 9999], [83, 63, 41, 38, 19, 14, 9999], [91, 71, 49, 25, 17, 11, 8, 9999], [31, 23, 20, 9999], [12, 33, 5, 0, 9999], [57, 58, 9999], [35, 36, 9999], [4, 36, 9999], [61, 62, 82, 88, 105, 99, 79, 80, 9999], [90, 94, 9999], [97, 75, 69, 49, 46, 31, 28, 9999], [48, 68, 72, 9999], [18, 42, 25, 17, 14, 9999], [90, 75, 72, 9999], [41, 13, 8, 9999], [54, 41, 33, 34, 54, 60, 66, 88, 105, 99, 100, 9999], [63, 60, 45, 42, 25, 22, 26, 9999], [45, 19, 16, 20, 9999], [57, 35, 5, 6, 9999], [67, 45, 39, 33, 5, 6, 9999], [61, 62, 77, 57, 54, 60, 45, 42, 46, 50, 9999], [70, 87, 88, 108, 114, 9999], [64, 68, 74, 91, 87, 88, 110, 9999], [71, 49, 43, 19, 11, 12, 38, 42, 25, 17, 14, 9999], [67, 61, 62, 84, 106, 9999], [41, 33, 36, 9999], [78, 98, 106, 9999], [109, 110, 9999], [33, 34, 58, 9999], [75, 72, 9999], [76, 84, 106, 9999], [38, 19, 16, 22, 28, 9999], [56, 76, 63, 60, 66, 86, 71, 49, 46, 50, 9999], [4, 32, 13, 10, 14, 9999], [49, 43, 19, 11, 12, 38, 19, 16, 22, 26, 9999], [52, 72, 9999], [64, 70, 87, 88, 105, 99, 79, 57, 54, 41, 38, 19, 14, 9999], [62, 82, 88, 105, 85, 63, 60, 66, 88, 110, 9999], [99, 100, 9999], [35, 5, 0, 9999], [76, 84, 99, 100, 9999], [70, 92, 114, 9999], [57, 58, 9999], [45, 39, 13, 3, 0, 9999], [17, 18, 42, 46, 31, 23, 20, 9999], [12, 33, 36, 9999], [79, 80, 9999], [46, 50, 9999], [44, 66, 88, 108, 93, 90, 75, 72, 9999], [48, 70, 92, 112, 97, 91, 87, 83, 77, 57, 58, 9999], [2, 12, 40, 60, 66, 83, 84, 104, 108, 112, 118, 9999], [57, 35, 36, 9999], [65, 66, 83, 77, 57, 35, 5, 2, 8, 9999], [62, 77, 78, 100, 9999], [66, 88, 108, 114, 9999], [112, 116, 9999], [55, 56, 78, 102, 9999], [78, 98, 106, 9999], [66, 83, 63, 60, 66, 83, 84, 104, 108, 93, 87, 83, 84, 99, 102, 9999], [92, 109, 105, 99, 100, 9999], [87, 88, 110, 9999], [43, 39, 33, 5, 2, 8, 9999], [77, 80, 9999], [17, 14, 9999], [32, 13, 3, 0, 9999], [105, 99, 100, 9999], [13, 10, 14, 9999], [83, 63, 41, 38, 19, 16, 24, 48, 70, 90, 94, 9999], [31, 28, 9999], [84, 104, 108, 93, 71, 65, 66, 83, 77, 78, 102, 9999], [2, 12, 40, 60, 45, 39, 13, 10, 16, 22, 30, 50, 9999], [99, 102, 9999], [3, 0, 9999], [75, 53, 31, 23, 24, 48, 68, 72, 9999], [53, 47, 25, 17, 11, 8, 9999], [23, 24, 46, 50, 9999], [46, 31, 28, 9999], [42, 25, 17, 11, 12, 38, 19, 14, 9999], [61, 41, 33, 36, 9999], [47, 48, 68, 74, 96, 116, 9999], [16, 24, 43, 19, 14, 9999], [52, 74, 91, 87, 88, 105, 99, 79, 57, 54, 60, 45, 42, 48, 68, 53, 50, 9999], [109, 110, 9999], [84, 106, 9999], [109, 110, 9999], [4, 32, 38, 44, 61, 55, 58, 9999], [93, 90, 96, 118, 9999], [66, 88, 108, 93, 71, 49, 46, 31, 26, 9999], [69, 70, 90, 94, 9999], [13, 8, 9999], [112, 116, 9999], [23, 24, 46, 31, 26, 9999], [31, 28, 9999], [25, 17, 18, 42, 46, 52, 69, 70, 92, 112, 97, 94, 9999], [55, 35, 32, 38, 44, 61, 55, 58, 9999], [98, 85, 82, 88, 108, 93, 87, 88, 105, 99, 79, 76, 84, 104, 110, 9999], [11, 8, 9999], [48, 70, 87, 83, 84, 106, 9999], [54, 41, 33, 36, 9999], [97, 94, 9999], [68, 74, 91, 87, 88, 105, 99, 100, 9999], [85, 63, 55, 35, 32, 38, 44, 61, 55, 58, 9999], [19, 11, 3, 6, 9999], [46, 52, 72, 9999], [65, 61, 41, 38, 19, 11, 12, 38, 42, 46, 50, 9999], [74, 91, 87, 83, 77, 57, 58, 9999], [69, 65, 61, 62, 82, 86, 90, 75, 69, 65, 61, 41, 38, 19, 16, 20, 9999], [90, 75, 72, 9999], [35, 32, 13, 8, 9999], [46, 31, 28, 9999], [97, 91, 71, 68, 74, 91, 87, 67, 61, 41, 38, 42, 46, 52, 69, 49, 46, 50, 9999], [17, 18, 39, 13, 3, 6, 9999], [33, 5, 0, 9999], [67, 61, 62, 84, 104, 89, 67, 45, 19, 14, 9999], [54, 60, 64, 70, 87, 67, 61, 55, 56, 80, 9999], [69, 65, 61, 62, 82, 88, 110, 9999], [53, 31, 23, 20, 9999], [92, 114, 9999], [75, 53, 50, 9999], [31, 26, 9999], [76, 63, 41, 13, 3, 4, 32, 40, 55, 35, 36, 9999], [46, 31, 23, 24, 48, 68, 72, 9999], [3, 0, 9999], [53, 31, 26, 9999], [13, 3, 0, 9999], [39, 33, 36, 9999], [52, 72, 9999], [38, 42, 46, 50, 9999], [99, 79, 57, 58, 9999], [99, 102, 9999], [5, 6, 9999], [75, 72, 9999], [46, 52, 69, 49, 43, 44, 61, 55, 35, 32, 13, 8, 9999], [109, 105, 106, 9999], [3, 6, 9999], [91, 87, 67, 61, 41, 38, 44, 66, 83, 63, 60, 66, 83, 63, 41, 33, 36, 9999], [85, 82, 67, 45, 42, 25, 20, 9999], [61, 55, 58, 9999], [25, 22, 30, 50, 9999], [71, 68, 53, 50, 9999], [17, 11, 8, 9999], [52, 74, 94, 9999], [46, 52, 69, 49, 43, 44, 66, 86, 92, 114, 9999], [16, 22, 30, 47, 25, 20, 9999], [93, 87, 88, 105, 99, 79, 57, 58, 9999], [99, 100, 9999], [83, 77, 57, 35, 36, 9999], [44, 64, 70, 92, 114, 9999]]
    return internal_lane_car_path_options_store
internal_lane_car_path_options_store = internal_lane_car_path_options_full()
def entry_lane_car_path_options_full():
    entry_lane_car_path_options_store =[[103, 98, 85, 63, 55, 58, 9999], [59, 35, 36, 9999], [1, 6, 9999], [21, 22, 28, 9999], [27, 23, 17, 11, 12, 40, 62, 84, 106, 9999], [111, 105, 99, 79, 76, 82, 67, 61, 62, 82, 88, 110, 9999], [37, 32, 13, 3, 4, 36, 9999], [21, 17, 14, 9999], [27, 30, 47, 48, 70, 87, 83, 63, 55, 56, 80, 9999], [73, 69, 65, 45, 19, 11, 3, 0, 9999], [81, 76, 63, 55, 58, 9999], [107, 85, 63, 55, 56, 76, 63, 55, 58, 9999], [81, 57, 54, 62, 77, 57, 58, 9999], [7, 4, 34, 54, 41, 33, 36, 9999], [119, 97, 75, 53, 31, 26, 9999], [15, 18, 44, 66, 88, 108, 112, 118, 9999], [21, 24, 43, 39, 40, 55, 35, 32, 40, 60, 45, 42, 48, 70, 90, 94, 9999], [27, 23, 24, 48, 65, 61, 55, 58, 9999], [107, 85, 82, 67, 64, 49, 43, 44, 64, 49, 25, 20, 9999], [51, 52, 72, 9999], [29, 23, 20, 9999], [95, 96, 118, 9999], [1, 4, 32, 40, 62, 84, 99, 100, 9999], [7, 0, 9999], [15, 16, 20, 9999], [115, 93, 90, 96, 116, 9999], [29, 23, 20, 9999], [29, 23, 20, 9999], [117, 113, 114, 9999], [7, 0, 9999], [111, 105, 106, 9999], [37, 34, 54, 60, 64, 70, 92, 114, 9999], [119, 116, 9999], [101, 98, 106, 9999], [81, 78, 102, 9999], [9, 10, 16, 20, 9999], [95, 96, 113, 93, 90, 75, 72, 9999], [103, 100, 9999], [9, 12, 33, 36, 9999], [37, 5, 2, 12, 40, 60, 66, 88, 105, 99, 102, 9999], [81, 78, 100, 9999], [15, 11, 3, 6, 9999], [101, 98, 104, 89, 86, 92, 112, 116, 9999], [29, 30, 52, 69, 65, 66, 86, 71, 49, 46, 50, 9999], [119, 113, 109, 89, 67, 64, 70, 92, 112, 118, 9999], [1, 4, 34, 56, 76, 82, 67, 61, 55, 58, 9999], [51, 31, 26, 9999], [37, 32, 13, 3, 6, 9999], [9, 3, 4, 32, 40, 60, 45, 42, 46, 31, 28, 9999], [59, 35, 5, 6, 9999], [29, 23, 20, 9999], [107, 85, 77, 78, 100, 9999], [73, 53, 47, 48, 65, 66, 88, 105, 106, 9999], [21, 17, 11, 3, 0, 9999], [27, 30, 52, 74, 94, 9999], [21, 17, 18, 42, 46, 31, 23, 17, 18, 39, 33, 36, 9999], [7, 2, 12, 33, 5, 2, 12, 40, 60, 66, 88, 108, 112, 97, 91, 87, 67, 61, 62, 77, 80, 9999], [27, 28, 9999], [37, 34, 58, 9999], [73, 69, 65, 45, 39, 40, 60, 45, 19, 14, 9999], [73, 74, 96, 118, 9999], [37, 5, 0, 9999], [9, 3, 0, 9999], [111, 89, 83, 84, 104, 89, 67, 64, 49, 43, 19, 14, 9999], [117, 97, 75, 53, 50, 9999], [1, 2, 8, 9999], [81, 76, 84, 106, 9999], [117, 118, 9999], [107, 104, 89, 86, 90, 94, 9999], [7, 0, 9999], [21, 17, 11, 8, 9999], [7, 2, 12, 33, 36, 9999], [7, 2, 12, 33, 5, 0, 9999], [103, 79, 80, 9999], [27, 30, 50, 9999], [115, 112, 97, 91, 92, 109, 110, 9999], [103, 79, 80, 9999], [119, 113, 93, 90, 94, 9999], [1, 6, 9999], [7, 2, 8, 9999], [37, 5, 6, 9999], [37, 34, 56, 76, 82, 86, 90, 75, 53, 47, 43, 44, 66, 83, 84, 99, 102, 9999], [1, 6, 9999], [1, 2, 10, 16, 20, 9999], [1, 4, 36, 9999], [1, 4, 32, 40, 60, 66, 88, 110, 9999], [9, 3, 4, 34, 58, 9999], [9, 10, 16, 20, 9999], [115, 109, 89, 83, 77, 80, 9999], [59, 56, 78, 102, 9999], [111, 89, 67, 45, 42, 46, 50, 9999], [107, 85, 82, 88, 105, 85, 77, 80, 9999], [51, 52, 74, 91, 87, 67, 61, 41, 38, 42, 25, 17, 18, 42, 48, 70, 92, 109, 105, 106, 9999], [27, 28, 9999], [95, 96, 118, 9999], [111, 108, 93, 90, 94, 9999], [51, 31, 23, 17, 11, 12, 40, 55, 35, 36, 9999], [103, 100, 9999], [51, 52, 69, 70, 90, 96, 116, 9999], [7, 2, 12, 33, 36, 9999], [73, 74, 94, 9999], [101, 102, 9999], [27, 28, 9999], [81, 57, 54, 41, 13, 8, 9999], [7, 4, 34, 58, 9999], [101, 98, 104, 108, 114, 9999], [37, 5, 2, 10, 18, 39, 13, 10, 18, 39, 13, 8, 9999], [7, 0, 9999], [107, 85, 63, 41, 33, 34, 54, 60, 66, 83, 63, 60, 45, 42, 46, 52, 74, 91, 87, 88, 110, 9999], [15, 11, 3, 0, 9999], [15, 11, 3, 4, 34, 58, 9999], [81, 78, 100, 9999], [29, 30, 50, 9999], [21, 24, 43, 19, 14, 9999], [73, 69, 49, 43, 39, 13, 3, 0, 9999], [81, 78, 98, 106, 9999], [115, 112, 97, 75, 69, 70, 87, 83, 84, 106, 9999], [117, 97, 94, 9999], [95, 91, 92, 112, 116, 9999], [9, 3, 0, 9999], [111, 105, 106, 9999], [51, 31, 23, 24, 43, 44, 61, 62, 77, 57, 35, 32, 40, 62, 77, 57, 35, 5, 6, 9999], [37, 34, 56, 76, 63, 55, 35, 5, 6, 9999], [21, 24, 46, 52, 72, 9999], [115, 109, 110, 9999], [59, 56, 76, 84, 104, 89, 86, 92, 112, 97, 94, 9999], [7, 0, 9999], [21, 24, 46, 31, 26, 9999], [73, 53, 47, 25, 17, 14, 9999], [37, 5, 2, 12, 38, 42, 25, 22, 28, 9999], [51, 52, 69, 70, 90, 75, 72, 9999], [59, 35, 5, 6, 9999], [115, 109, 105, 99, 100, 9999], [27, 28, 9999], [1, 2, 8, 9999], [107, 104, 108, 93, 87, 88, 108, 114, 9999], [27, 30, 52, 72, 9999], [9, 3, 6, 9999], [107, 99, 79, 76, 82, 86, 90, 94, 9999], [107, 104, 89, 86, 92, 114, 9999], [107, 85, 63, 60, 45, 42, 25, 20, 9999], [119, 113, 93, 87, 67, 45, 39, 13, 8, 9999], [107, 85, 63, 55, 35, 36, 9999], [103, 98, 85, 63, 55, 35, 32, 38, 19, 14, 9999], [81, 78, 100, 9999], [9, 12, 40, 60, 66, 88, 110, 9999], [29, 23, 17, 11, 12, 38, 42, 48, 68, 72, 9999], [51, 47, 48, 70, 87, 67, 64, 68, 74, 91, 92, 109, 105, 106, 9999], [9, 12, 33, 34, 54, 60, 66, 83, 63, 60, 45, 42, 46, 50, 9999], [117, 118, 9999], [119, 97, 75, 53, 31, 23, 24, 43, 44, 66, 83, 63, 41, 13, 8, 9999], [59, 35, 32, 38, 19, 11, 8, 9999], [51, 47, 25, 22, 28, 9999], [111, 89, 83, 77, 57, 58, 9999], [21, 24, 43, 44, 61, 55, 58, 9999], [37, 34, 54, 62, 84, 104, 110, 9999], [51, 52, 69, 49, 25, 20, 9999], [119, 113, 109, 105, 106, 9999], [81, 57, 35, 5, 2, 12, 40, 55, 56, 78, 102, 9999], [59, 54, 41, 33, 5, 2, 12, 38, 44, 61, 41, 38, 44, 61, 62, 77, 57, 54, 62, 84, 104, 89, 86, 90, 94, 9999], [101, 102, 9999], [15, 18, 42, 46, 31, 26, 9999], [95, 91, 92, 112, 116, 9999], [59, 35, 5, 2, 10, 16, 24, 43, 44, 64, 49, 46, 50, 9999], [7, 2, 10, 14, 9999], [73, 74, 96, 118, 9999], [115, 93, 71, 65, 66, 88, 110, 9999], [1, 4, 36, 9999], [51, 31, 28, 9999], [107, 85, 63, 41, 13, 8, 9999], [101, 79, 80, 9999], [107, 99, 79, 76, 63, 55, 56, 80, 9999], [27, 28, 9999], [29, 23, 24, 43, 39, 40, 62, 82, 67, 64, 70, 87, 83, 84, 106, 9999], [117, 118, 9999], [37, 5, 6, 9999], [1, 6, 9999], [81, 78, 102, 9999], [15, 18, 39, 40, 62, 82, 86, 90, 75, 53, 47, 43, 39, 33, 5, 6, 9999], [111, 105, 99, 100, 9999], [51, 47, 48, 65, 66, 83, 63, 60, 64, 70, 92, 109, 110, 9999], [27, 30, 50, 9999], [73, 53, 31, 28, 9999], [27, 23, 20, 9999], [119, 113, 109, 89, 86, 92, 112, 118, 9999], [9, 12, 38, 42, 46, 31, 26, 9999], [81, 78, 102, 9999], [7, 0, 9999], [95, 91, 92, 114, 9999], [21, 17, 14, 9999], [103, 79, 76, 84, 106, 9999], [29, 30, 50, 9999], [107, 85, 77, 57, 58, 9999], [81, 76, 63, 55, 56, 80, 9999], [37, 32, 38, 44, 66, 86, 71, 49, 46, 31, 23, 20, 9999], [59, 35, 5, 6, 9999], [27, 28, 9999], [37, 34, 54, 60, 66, 83, 77, 57, 35, 32, 13, 3, 4, 34, 54, 60, 64, 49, 25, 22, 30, 50, 9999], [21, 17, 11, 3, 0, 9999], [95, 96, 116, 9999], [59, 56, 76, 84, 104, 110, 9999], [29, 23, 24, 48, 70, 87, 88, 110, 9999], [59, 54, 62, 77, 78, 102, 9999], [117, 113, 93, 71, 68, 53, 31, 26, 9999], [107, 85, 77, 80, 9999], [117, 97, 94, 9999], [95, 91, 71, 49, 43, 39, 40, 62, 77, 80, 9999], [9, 12, 40, 62, 84, 106, 9999], [111, 105, 106, 9999], [9, 3, 6, 9999], [27, 28, 9999], [81, 78, 100, 9999], [107, 99, 100, 9999], [111, 89, 86, 92, 109, 110, 9999], [117, 113, 93, 71, 65, 66, 83, 84, 99, 100, 9999], [9, 12, 33, 5, 2, 10, 14, 9999], [27, 30, 50, 9999], [103, 79, 57, 35, 32, 40, 62, 84, 106, 9999], [117, 118, 9999], [103, 98, 104, 108, 93, 87, 67, 45, 19, 14, 9999], [95, 91, 92, 114, 9999], [37, 34, 56, 76, 84, 106, 9999], [29, 30, 47, 48, 68, 74, 94, 9999], [7, 4, 34, 58, 9999], [107, 104, 110, 9999], [1, 4, 32, 13, 3, 0, 9999], [119, 113, 93, 71, 49, 46, 50, 9999], [51, 47, 43, 44, 61, 55, 56, 80, 9999], [111, 89, 86, 90, 96, 113, 114, 9999], [27, 30, 50, 9999], [27, 23, 20, 9999], [21, 17, 11, 12, 33, 36, 9999], [117, 118, 9999], [81, 76, 63, 41, 13, 10, 16, 24, 43, 44, 64, 68, 72, 9999], [21, 17, 11, 12, 38, 19, 16, 24, 46, 31, 28, 9999], [59, 35, 32, 13, 3, 0, 9999], [73, 53, 31, 28, 9999], [95, 91, 87, 83, 84, 99, 79, 57, 35, 36, 9999], [21, 22, 28, 9999], [27, 30, 52, 69, 65, 45, 39, 13, 10, 18, 39, 13, 8, 9999], [95, 91, 71, 65, 61, 62, 84, 106, 9999], [9, 3, 0, 9999], [37, 5, 2, 8, 9999], [103, 100, 9999], [59, 54, 41, 33, 5, 6, 9999], [95, 75, 69, 65, 61, 41, 33, 34, 58, 9999], [9, 12, 40, 60, 45, 19, 16, 20, 9999], [101, 98, 85, 63, 41, 33, 5, 2, 10, 14, 9999], [95, 75, 69, 65, 45, 39, 40, 62, 84, 106, 9999], [1, 4, 36, 9999], [117, 113, 114, 9999], [37, 32, 13, 8, 9999], [7, 2, 10, 14, 9999], [9, 3, 6, 9999], [59, 35, 5, 2, 8, 9999], [59, 56, 78, 98, 85, 63, 41, 13, 3, 0, 9999], [1, 6, 9999], [9, 10, 18, 42, 46, 52, 72, 9999], [9, 3, 0, 9999], [107, 99, 102, 9999], [107, 85, 77, 57, 54, 41, 13, 3, 4, 34, 58, 9999], [29, 26, 9999], [29, 23, 20, 9999], [107, 99, 102, 9999], [7, 4, 34, 54, 60, 64, 49, 43, 19, 11, 8, 9999], [27, 23, 24, 43, 39, 13, 10, 14, 9999], [9, 3, 0, 9999], [7, 0, 9999], [15, 18, 42, 25, 17, 18, 44, 61, 55, 35, 36, 9999], [107, 85, 82, 88, 110, 9999], [101, 98, 85, 82, 86, 90, 75, 69, 65, 66, 88, 105, 106, 9999], [59, 54, 60, 66, 88, 110, 9999], [117, 97, 91, 71, 49, 43, 39, 13, 10, 16, 22, 26, 9999], [21, 17, 11, 12, 38, 42, 46, 52, 72, 9999], [1, 4, 32, 38, 19, 14, 9999], [107, 99, 79, 57, 35, 5, 6, 9999], [29, 30, 52, 69, 65, 45, 39, 13, 3, 6, 9999], [115, 109, 89, 86, 71, 65, 61, 62, 84, 106, 9999], [103, 98, 85, 63, 41, 13, 10, 14, 9999], [81, 78, 98, 106, 9999], [21, 24, 48, 70, 87, 88, 108, 112, 118, 9999], [29, 26, 9999], [37, 34, 54, 62, 82, 86, 71, 65, 66, 86, 90, 94, 9999], [101, 102, 9999], [27, 30, 47, 43, 19, 14, 9999], [59, 35, 36, 9999], [27, 23, 17, 11, 8, 9999], [9, 3, 6, 9999], [119, 97, 91, 92, 114, 9999], [9, 10, 16, 22, 30, 50, 9999], [103, 98, 104, 89, 83, 63, 55, 58, 9999], [29, 26, 9999], [81, 78, 100, 9999], [1, 6, 9999], [119, 97, 94, 9999], [73, 53, 47, 25, 22, 26, 9999], [107, 85, 63, 60, 64, 49, 46, 50, 9999], [7, 4, 36, 9999], [37, 32, 13, 8, 9999], [107, 85, 63, 60, 66, 88, 105, 85, 63, 41, 13, 10, 18, 44, 66, 83, 77, 78, 98, 104, 89, 86, 90, 94, 9999], [117, 97, 91, 87, 83, 77, 78, 100, 9999], [117, 97, 94, 9999], [15, 18, 44, 66, 86, 71, 65, 45, 39, 40, 55, 58, 9999], [117, 113, 114, 9999], [37, 5, 0, 9999], [59, 56, 80, 9999], [95, 96, 116, 9999], [73, 74, 94, 9999], [21, 22, 26, 9999], [73, 69, 49, 46, 31, 23, 24, 48, 68, 72, 9999], [81, 78, 100, 9999], [7, 0, 9999], [37, 5, 2, 10, 14, 9999], [117, 113, 93, 87, 88, 108, 112, 116, 9999], [27, 30, 50, 9999], [1, 6, 9999], [7, 2, 10, 18, 39, 33, 5, 6, 9999], [37, 32, 40, 60, 64, 68, 74, 96, 118, 9999], [119, 97, 91, 92, 114, 9999], [117, 118, 9999], [59, 35, 36, 9999], [115, 109, 89, 83, 63, 55, 35, 32, 40, 55, 35, 32, 13, 8, 9999], [29, 26, 9999], [111, 89, 83, 63, 55, 58, 9999], [1, 6, 9999], [27, 23, 20, 9999], [7, 2, 8, 9999], [1, 6, 9999], [119, 113, 114, 9999], [81, 76, 84, 104, 108, 112, 97, 91, 87, 88, 105, 85, 82, 88, 110, 9999], [59, 35, 5, 2, 10, 14, 9999], [15, 18, 44, 66, 88, 105, 106, 9999], [81, 57, 58, 9999], [103, 98, 104, 89, 86, 71, 68, 72, 9999], [81, 76, 82, 67, 61, 41, 38, 42, 48, 70, 87, 67, 45, 39, 13, 8, 9999], [81, 78, 102, 9999], [119, 113, 109, 110, 9999], [81, 76, 63, 55, 35, 36, 9999], [37, 5, 0, 9999], [21, 24, 46, 52, 69, 70, 90, 96, 118, 9999], [101, 102, 9999], [119, 113, 114, 9999], [115, 112, 116, 9999], [107, 85, 82, 88, 110, 9999], [59, 56, 80, 9999], [107, 104, 108, 112, 116, 9999], [117, 97, 94, 9999], [15, 18, 42, 46, 31, 28, 9999], [103, 100, 9999], [119, 97, 91, 92, 109, 110, 9999], [27, 23, 20, 9999], [81, 57, 54, 62, 77, 78, 102, 9999], [27, 23, 24, 46, 52, 74, 96, 118, 9999], [37, 34, 58, 9999], [15, 16, 22, 30, 52, 74, 91, 87, 83, 77, 57, 58, 9999], [73, 69, 70, 90, 75, 72, 9999], [7, 4, 34, 54, 60, 66, 86, 90, 94, 9999], [27, 30, 50, 9999], [1, 6, 9999], [15, 16, 20, 9999], [59, 56, 80, 9999], [115, 112, 97, 94, 9999], [1, 2, 10, 16, 22, 28, 9999], [103, 98, 104, 89, 86, 92, 114, 9999], [21, 22, 28, 9999], [111, 105, 99, 100, 9999], [107, 85, 63, 60, 64, 70, 92, 109, 89, 67, 45, 19, 14, 9999], [115, 112, 97, 75, 53, 31, 26, 9999], [95, 96, 116, 9999], [59, 56, 80, 9999], [111, 108, 114, 9999], [51, 47, 48, 70, 87, 88, 105, 106, 9999], [95, 75, 72, 9999], [1, 4, 36, 9999], [51, 52, 69, 49, 46, 50, 9999], [115, 109, 105, 99, 79, 76, 63, 41, 38, 42, 46, 31, 23, 17, 14, 9999], [107, 85, 82, 86, 71, 65, 61, 62, 77, 57, 35, 36, 9999], [107, 99, 100, 9999], [9, 10, 16, 24, 43, 19, 14, 9999], [37, 32, 40, 55, 35, 36, 9999], [81, 57, 54, 41, 33, 5, 0, 9999], [103, 79, 80, 9999], [107, 85, 77, 57, 54, 62, 82, 67, 64, 49, 46, 31, 28, 9999], [27, 28, 9999], [9, 10, 14, 9999], [119, 97, 91, 87, 67, 64, 70, 92, 112, 116, 9999], [27, 23, 20, 9999], [103, 100, 9999], [37, 34, 58, 9999], [1, 4, 34, 58, 9999], [119, 116, 9999], [73, 53, 47, 48, 70, 90, 75, 53, 31, 26, 9999], [73, 69, 65, 45, 39, 33, 5, 2, 8, 9999], [29, 30, 47, 25, 17, 18, 42, 25, 17, 18, 39, 33, 34, 58, 9999], [59, 56, 80, 9999], [111, 108, 93, 87, 88, 108, 114, 9999], [9, 12, 38, 19, 14, 9999], [51, 52, 72, 9999], [1, 4, 36, 9999], [15, 16, 20, 9999], [111, 89, 83, 84, 106, 9999], [15, 16, 24, 48, 68, 72, 9999], [9, 10, 14, 9999], [15, 11, 12, 40, 60, 64, 49, 43, 19, 11, 3, 4, 36, 9999], [1, 4, 32, 40, 55, 58, 9999], [73, 69, 65, 66, 83, 77, 80, 9999], [107, 99, 102, 9999], [107, 99, 102, 9999], [9, 12, 33, 34, 54, 41, 33, 36, 9999], [117, 97, 75, 53, 47, 48, 65, 61, 41, 13, 3, 6, 9999], [15, 16, 22, 28, 9999], [115, 93, 90, 75, 72, 9999], [95, 96, 113, 93, 71, 68, 74, 96, 116, 9999], [1, 6, 9999], [103, 100, 9999], [107, 85, 63, 41, 33, 36, 9999], [21, 22, 26, 9999], [1, 6, 9999], [101, 102, 9999], [51, 31, 28, 9999], [51, 47, 43, 39, 13, 10, 14, 9999], [7, 4, 34, 54, 60, 66, 88, 110, 9999], [51, 47, 25, 17, 11, 12, 33, 5, 6, 9999], [95, 75, 53, 47, 48, 68, 74, 96, 113, 114, 9999], [107, 85, 77, 78, 102, 9999], [51, 52, 74, 96, 113, 93, 90, 94, 9999], [81, 76, 82, 67, 45, 39, 33, 5, 0, 9999], [9, 10, 18, 44, 61, 41, 13, 8, 9999], [59, 56, 76, 82, 86, 90, 96, 113, 93, 90, 96, 118, 9999], [9, 3, 6, 9999], [15, 18, 39, 40, 62, 84, 106, 9999], [101, 102, 9999], [73, 69, 70, 90, 75, 72, 9999], [115, 93, 90, 94, 9999], [9, 12, 38, 19, 16, 22, 28, 9999], [21, 17, 14, 9999], [1, 4, 32, 13, 10, 16, 20, 9999], [117, 118, 9999], [81, 57, 35, 36, 9999], [81, 76, 63, 41, 33, 5, 0, 9999], [95, 96, 118, 9999], [15, 18, 39, 40, 60, 45, 42, 48, 70, 87, 83, 77, 78, 100, 9999], [21, 22, 30, 47, 48, 68, 74, 96, 113, 93, 87, 83, 63, 41, 13, 3, 4, 36, 9999], [95, 96, 113, 109, 105, 85, 82, 67, 45, 42, 25, 22, 28, 9999], [1, 4, 36, 9999], [59, 56, 76, 63, 55, 56, 76, 84, 106, 9999], [9, 12, 33, 34, 56, 78, 100, 9999], [1, 2, 10, 14, 9999], [95, 75, 72, 9999], [51, 52, 69, 70, 87, 88, 108, 93, 71, 49, 46, 52, 72, 9999], [9, 10, 14, 9999], [9, 3, 6, 9999], [111, 105, 99, 102, 9999], [111, 105, 99, 100, 9999], [107, 99, 100, 9999], [119, 97, 94, 9999], [107, 99, 100, 9999], [115, 93, 90, 96, 116, 9999], [111, 105, 85, 77, 57, 35, 36, 9999], [7, 0, 9999], [59, 35, 5, 2, 8, 9999], [73, 69, 70, 92, 114, 9999], [81, 78, 98, 85, 77, 80, 9999], [73, 74, 96, 118, 9999], [101, 98, 85, 82, 86, 90, 94, 9999], [73, 53, 31, 26, 9999], [119, 113, 109, 105, 106, 9999], [1, 4, 34, 56, 78, 98, 106, 9999], [15, 16, 24, 46, 31, 23, 24, 43, 39, 13, 10, 14, 9999], [29, 23, 17, 18, 39, 33, 36, 9999], [29, 30, 52, 72, 9999], [15, 18, 39, 33, 34, 58, 9999], [73, 74, 91, 92, 112, 118, 9999], [7, 4, 34, 56, 78, 102, 9999], [73, 53, 31, 23, 24, 43, 19, 11, 12, 33, 34, 58, 9999], [29, 23, 20, 9999], [115, 112, 118, 9999], [73, 53, 47, 25, 20, 9999], [111, 105, 99, 79, 57, 58, 9999], [1, 4, 32, 40, 60, 66, 88, 108, 93, 87, 88, 110, 9999], [7, 4, 34, 54, 60, 45, 19, 11, 3, 4, 32, 38, 42, 48, 70, 87, 67, 64, 68, 53, 47, 25, 20, 9999], [103, 79, 76, 84, 104, 89, 86, 92, 109, 89, 86, 71, 68, 53, 47, 43, 39, 33, 34, 56, 76, 82, 86, 90, 94, 9999], [95, 91, 71, 49, 46, 52, 74, 91, 71, 65, 66, 83, 84, 99, 100, 9999], [103, 100, 9999], [101, 102, 9999], [119, 116, 9999], [111, 108, 112, 118, 9999], [51, 31, 23, 24, 48, 70, 92, 112, 97, 75, 72, 9999], [15, 16, 20, 9999], [115, 93, 71, 68, 53, 50, 9999], [27, 30, 50, 9999], [95, 96, 118, 9999], [27, 23, 24, 43, 39, 13, 8, 9999], [1, 6, 9999], [1, 6, 9999], [15, 16, 20, 9999], [81, 57, 54, 60, 64, 70, 87, 83, 84, 104, 110, 9999], [51, 31, 26, 9999], [101, 79, 57, 35, 36, 9999], [27, 28, 9999]]
    return entry_lane_car_path_options_store
entry_lane_car_path_options_store = entry_lane_car_path_options_full()

# create cars
cars = []
cars_in_system = []
cars_entered_system = []
cars_exited_system = []
num_cars = 200
num_initial_internal_cars = 100
for i in range(num_cars):
    cars.append(Car(10,10,i))
    cars[i].id = i
    car_angle_from_vert = 0
    cars[i].angle = car_angle_from_vert
    Car.car_on_angle(cars[i],cars[i].pos_x,cars[i].pos_y,car_width,car_length,car_angle_from_vert)
    # cars[i].path = car_entry_path_options[i]
    # cars[i].path = entry_lane_car_path_options_store[i]
    if i < num_initial_internal_cars:
        cars[i].path = internal_lane_car_path_options_store[i]
        # cars[i].path = car_internal_path_start_options[i]
    else:
        t = 0
    #     # car path taken from the
        cars[i].path = entry_lane_car_path_options_store[i]
        # cars[i].path = car_entry_path_options[i]
    cars[i].path_step = 0
    cars[i].current_lane = cars[i].path[cars[i].path_step]
    cars[i].next_lane = cars[i].path[(cars[i].path_step + 1)]

def fut_pos_change_lane(car_id,lanes_test,cars,Car): # populate cars[car_id].fut_pos with the future points between current lane and next lane
    next_lane = cars[car_id].next_lane
    # current_lane = 0
    # next_lane_index = lanes_test[current_lane].next_lanes.index(next_lane)
    next_lane_index = lanes_test[cars[car_id].current_lane].next_lanes.index(next_lane)
    # temp_fut_pos_between_lanes = lanes_test[current_lane].move_points_next_lanes[next_lane_index]
    temp_fut_pos_between_lanes = lanes_test[cars[car_id].current_lane].move_points_next_lanes[next_lane_index]
    # print("temp_fut_pos_between_lanes: " + str(temp_fut_pos_between_lanes))
    for i in range(len(temp_fut_pos_between_lanes)):
        cars[car_id].fut_pos.append(temp_fut_pos_between_lanes[i])
        cars[car_id].fut_pos.append(temp_fut_pos_between_lanes[i])
        # cars[car_id].fut_pos.append(temp_fut_pos_between_lanes[i])
def fut_pos_current_lane(car_id,lanes_test,cars,Car): # populate cars[car_id].fut_pos with the future points from the start to the end of the current lane
    #cehck if next_lane in free_turn_next_lanes
    if cars[car_id].next_lane in lanes_test[cars[car_id].current_lane].free_turn_next_lanes:
        # find the fut_pos to the end of the lane and call it sometihing different
        cars[car_id].fut_pos_psuedo = cars[car_id].fut_pos[:]
        for j in range(len(lanes_test[cars[car_id].current_lane].move_points)):
            cars[car_id].fut_pos_psuedo.append(lanes_test[cars[car_id].current_lane].move_points[j]) # store the x and     y points and angle for the future pos in this lane, to take car to end of lane
        if lanes_test[cars[car_id].current_lane].next_lanes[0] == 9999:
            cars[car_id].fut_pos_psuedo.append([50,50,(math.pi/2)])
        # find index of next_lane in free_turn_next_lane_move_points
        for k in range(len(lanes_test[cars[car_id].current_lane].free_turn_next_lane_move_points)):
            if cars[car_id].next_lane == lanes_test[cars[car_id].current_lane].free_turn_next_lane_move_points[k][0]:
                for q in range(1,len(lanes_test[cars[car_id].current_lane].free_turn_next_lane_move_points[k])):
                    cars[car_id].fut_pos.append(lanes_test[cars[car_id].current_lane].free_turn_next_lane_move_points[k][q])
    else:
        for j in range(len(lanes_test[cars[car_id].current_lane].move_points)):
            cars[car_id].fut_pos.append(lanes_test[cars[car_id].current_lane].move_points[j]) # store the x and     y points and angle for the future pos in this lane, to take car to end of lane
        if lanes_test[cars[car_id].current_lane].next_lanes[0] == 9999:
            cars[car_id].fut_pos.append([50,50,(math.pi/2)])
def find_current_end_step(car_id,lanes_test,cars,Car): # find the step the car should move to in the current lane
    # car is going into a free_turn_next_lane use the samller of the two between fut_pos and fut_pos_psuedo
    if lanes_test[cars[car_id].current_lane].next_lanes[0] == 9999:
        cars[car_id].current_end_step = (len(cars[car_id].fut_pos)) - 1
    elif cars[car_id].next_lane in lanes_test[cars[car_id].current_lane].free_turn_next_lanes:
        pos_in_queue = lanes_test[cars[car_id].current_lane].cars_in_lane_id.index(cars[car_id].id)
        offset_first = 4
        offset_first = offset_first * 2
        offset = 6 #5
        offset = offset * 2
        # set the current_lane_end_step as the last step the in this lane for the car to take
        cars[car_id].current_lane_end_step = (len(cars[car_id].fut_pos)) - offset_first
        ###############
        if pos_in_queue == 0:
            cars[car_id].current_end_step = cars[car_id].current_lane_end_step
        else: # ie . pos_in_queue !=0
            car_in_front_id =  lanes_test[cars[car_id].current_lane].cars_in_lane_id[(pos_in_queue - 1)]
            car_in_front_current_end_step_move_point = cars[car_in_front_id].fut_pos[cars[car_in_front_id].current_end_step]
            if car_in_front_current_end_step_move_point in cars[car_id].fut_pos[cars[car_id].step:]: # check if car_in_front.current)end_step in the cars.fut_pos
                start_looking_after_value = cars[car_id].step
                index_step_temp = cars[car_id].fut_pos.index(car_in_front_current_end_step_move_point,start_looking_after_value)
                cars[car_id].current_end_step = index_step_temp - offset
            else:
                cars[car_id].current_end_step = cars[car_id].current_lane_end_step



        ###############
        # # now find the current_end_step accounting for cars in the lane
        # # current_end_step_from_fut_pos_psuedo = (len(cars[car_id].fut_pos_psuedo)) - (pos_in_queue * offset) - offset_first
        # current_end_step_from_fut_pos_psuedo = (len(cars[car_id].fut_pos_psuedo)) - offset_first
        # current_end_step_from_fut_pos = (len(cars[car_id].fut_pos)) - offset_first
        # if pos_in_queue != 0: # ie. pos_in_queue != 0
        #     offset = 6 #5 # for solution 2, was changed from offset = 6 #5
        #     #find current move_point of car in fornt
        #     car_in_front_id =  lanes_test[cars[car_id].current_lane].cars_in_lane_id[(pos_in_queue - 1)]
        #     car_in_front_move_point = cars[car_in_front_id].fut_pos[cars[car_in_front_id].step]
        #     # now find the index of car_in_front_move_point in cars[car_id].fut_pos
        #     if car_in_front_move_point in cars[car_id].fut_pos[cars[car_id].step:]: # in fut_pos between current step to the end
        #         start_looking_after_value = cars[car_id].step
        #         index_step_temp = cars[car_id].fut_pos.index(car_in_front_move_point,start_looking_after_value)
        #         updated_current_end_step_from_fut_pos_psuedo = index_step_temp - offset
        #         # cars[car_id].updated_current_end_step = index_step_temp - offset
        #         # if index_step_temp <= start_looking_after_value:
        #         if (updated_current_end_step_from_fut_pos_psuedo < current_end_step_from_fut_pos_psuedo) and (cars[car_in_front_id].step == cars[car_in_front_id].current_end_step): # ie. car_in_front has moved into lane  # solution 1
        #         # if (updated_current_end_step_from_fut_pos_psuedo < current_end_step_from_fut_pos_psuedo): # solution 2 reduce the offset value from 5 to 4
        #             current_end_step_from_fut_pos_psuedo = updated_current_end_step_from_fut_pos_psuedo
        #             if car_id == 20:
        #                 print("20 updated_psuedo: " + str(updated_current_end_step_from_fut_pos_psuedo) + " cur_psuedo: " + str(current_end_step_from_fut_pos_psuedo))
        #                 print("20 current_end_step_from_fut_pos: " + str(current_end_step_from_fut_pos) + " car_step: " + str(cars[car_id].step))
        #     else:
        #         updated_current_end_step_from_fut_pos_psuedo = current_end_step_from_fut_pos_psuedo
        # # do cmpareiosn between psuedo and other to set .current_end_step to the smaller step
        # if current_end_step_from_fut_pos_psuedo < current_end_step_from_fut_pos:
        #     cars[car_id].current_end_step = current_end_step_from_fut_pos_psuedo
        # else:
        #     cars[car_id].current_end_step = current_end_step_from_fut_pos
        ##########
    else:
        pos_in_queue = lanes_test[cars[car_id].current_lane].cars_in_lane_id.index(cars[car_id].id)
        # cars[car_id].current_end_step = ((len(cars[car_id].fut_pos)) - (pos_in_queue * 5))  - 1
        offset_first = 4
        offset_first = offset_first * 2
        cars[car_id].current_lane_end_step = (len(cars[car_id].fut_pos)) - offset_first
        if pos_in_queue == 0: # car at front
            # offset = int(half_car_length/move_val)
            # offset_first = 4
            # print("offset: " + str(offset))
            cars[car_id].current_end_step = (len(cars[car_id].fut_pos)) - offset_first
            # if car_id == 0:
            #     print("ran  pos_in_queue: " + str(pos_in_queue))
            #     print("current_end_step: " + str(cars[car_id].current_end_step))
            cars[car_id].end_step_for_current_lane = len(lanes_test[cars[car_id].current_lane].move_points) - offset_first
            cars[car_id].step_in_current_lane = cars[car_id].end_step_for_current_lane
            cars[car_id].front_queue_check = 1
            if lanes_test[cars[car_id].current_lane].next_lanes[0] == 9999:
                cars[car_id].current_end_step = (len(cars[car_id].fut_pos)) - 1

        # else:
        #     # position of car in front
        #     offset = 6 #5
        #     cars[car_id].current_end_step = (len(cars[car_id].fut_pos)) - (pos_in_queue * offset) - offset_first
        #     cars[car_id].end_step_for_current_lane = len(lanes_test[cars[car_id].current_lane].move_points) - (pos_in_queue * offset) - offset_first

        if lanes_test[cars[car_id].current_lane].next_lanes[0] == 9999:
            cars[car_id].current_end_step = (len(cars[car_id].fut_pos)) - 1
        # cars[car_id].current_end_step = ((len(cars[car_id].fut_pos)) - (pos_in_queue * 5))  - 1
        pos_in_queue = lanes_test[cars[car_id].current_lane].cars_in_lane_id.index(cars[car_id].id)
        if pos_in_queue != 0:
            offset = 6 #5
            offset = offset * 2
            # if (car_id == 308) or (car_id == 373) or (car_id == 425):
            #     print("     running find_current_end_step car_id: " + str(car_id))
            #find current move_point of car in fornt
            car_in_front_id =  lanes_test[cars[car_id].current_lane].cars_in_lane_id[(pos_in_queue - 1)]
            car_in_front_move_point = cars[car_in_front_id].fut_pos[cars[car_in_front_id].step]
            car_in_front_move_point_current_end_step = cars[car_in_front_id].fut_pos[cars[car_in_front_id].current_end_step]
            # now find the index of car_in_front_move_point in cars[car_id].fut_pos
            if car_in_front_move_point_current_end_step in cars[car_id].fut_pos[cars[car_id].step:]: # in fut_pos between current step to the end
                start_looking_after_value = cars[car_id].step
                index_step_temp = cars[car_id].fut_pos.index(car_in_front_move_point_current_end_step,start_looking_after_value)
                cars[car_id].updated_current_end_step = index_step_temp - offset

                # if index_step_temp <= start_looking_after_value:
                #     print("car: " + str())
                # if car_id == 89:
                #     print("inside 1     section updated_current_end_step: " + str(cars[car_id].updated_current_end_step))
                #     print("car_in_front_id: " + str(car_in_front_id))
                #     print("car_in_front_move_point: " + str(car_in_front_move_point))
                #     print("start_looking_after_value: " + str(start_looking_after_value))
                #     print("index_step_temp: " + str(index_step_temp))

                # if cars[car_id].updated_current_end_step < cars[car_id].current_end_step:
                #     cars[car_id].updated_current_end_step = cars[car_id].current_end_step
                # else:



                    # if cars[car_id].current_lane == 30:
                    #     print("find_current_end_step for lane 30")
                    #     print("car_id: " + str(car_id) + " nt_lane: " + str(cars[car_id].next_lane))
                    #     print("car_in_front_id: " + str(car_in_front_id) + " nt_lane: " + str(cars[car_in_front_id].next_lane))
                cars[car_id].current_end_step = cars[car_id].updated_current_end_step
            else:
                # car in front passed the current_lane_end_step, could be that the car is taking a free turn but car_in_front is not
                # or could be the car in front is taking the free turn lane and their fut_pos contains transition points that the car in question will not take, but don't see how this would be the case
                cars[car_id].current_end_step = cars[car_id].current_lane_end_step
                # if (cars[car_id].current_lane == 30) and (cars[car_id].next_lane == 34):
                #     # print("find_current_end_step for lane 30")
                    # print("car_id: " + str(car_id) + " nt_lane: " + str(cars[car_id].next_lane))
                    # print("cars_in_lane_id: " + str(lanes_test[30].cars_in_lane_id))
                    # print("car_id pos_in_queue: " + str(pos_in_queue))
                    # print("car_in_front: " + str(car_in_front_id) + " nt_lane: " + str(cars[car_in_front_id].next_lane))
                    # print("cars[car_id].step: " + str(cars[car_id].step) + "  cars[car_id].fut_pos: " + str(cars[car_id].fut_pos))
                    # print("car_in_front_move_point: " + str(car_in_front_move_point) + " car_in_front_move_point_current_end_step: " + str(car_in_front_move_point_current_end_step))
                    # print("cars[car_in_front_id].step: " + str(cars[car_in_front_id].step) + " cars[car_in_front_id].current_end_step: " + str(cars[car_in_front_id].current_end_step))
                    #
                    # canvas.itemconfig(cars[car_id].body, fill='red')
                    # canvas.itemconfig(cars[car_in_front_id].body, fill='yellow')
                    # tk.update()
                    # input("end it here 30")
                # if cars[car_id].current_lane == 30:
                #     print("find_current_end_step for lane 30")
                #     print("car_id: " + str(car_id) + " nt_lane: " + str(cars[car_id].next_lane))
                #     input("end it here 30")
    cars[car_id].current_end_step_tracker.append(cars[car_id].current_end_step)
def find_current_end_step_for_start_internal_lane(car_id,lanes_test,cars,Car): # find the step the car should move to in the current lane
    # if car_id == 51:
    #     print("51 through function ")
    #     input("51")
    for j in range(len(lanes_test[cars[car_id].current_lane].move_points)):
        cars[car_id].fut_pos.append(lanes_test[cars[car_id].current_lane].move_points[j])
    pos_in_queue = lanes_test[cars[car_id].current_lane].cars_in_lane_id.index(cars[car_id].id)
    offset_first = 4
    offset_first = offset_first * 2
    offset = 6 #5
    offset = offset * 2
    cars[car_id].current_lane_end_step = (len(cars[car_id].fut_pos)) - offset_first
    if pos_in_queue == 0: # car at front
        # offset = int(half_car_length/move_val)
        # offset_first = 4
        # print("offset: " + str(offset))
        cars[car_id].current_end_step = (len(cars[car_id].fut_pos)) - offset_first
        # if car_id == 0:
        #     print("ran  pos_in_queue: " + str(pos_in_queue))
        #     print("current_end_step: " + str(cars[car_id].current_end_step))
        cars[car_id].end_step_for_current_lane = len(lanes_test[cars[car_id].current_lane].move_points) - offset_first
        cars[car_id].step_in_current_lane = cars[car_id].end_step_for_current_lane
        cars[car_id].front_queue_check = 1
        if lanes_test[cars[car_id].current_lane].next_lanes[0] == 9999:
            cars[car_id].current_end_step = (len(cars[car_id].fut_pos)) - 1
    else:
        # position of car in front
        offset = 6 #5
        offset = offset * 2
        cars[car_id].current_end_step = (len(cars[car_id].fut_pos)) - (pos_in_queue * offset) - offset_first
        cars[car_id].end_step_for_current_lane = len(lanes_test[cars[car_id].current_lane].move_points) - (pos_in_queue * offset) - offset_first
        cars[car_id].step_in_current_lane = cars[car_id].end_step_for_current_lane
def find_updated_current_end_step(car_id,lanes_test,cars,Car): # find the step the car should move to in the current lane
    if cars[car_id].current_lane != 9999:
        if cars[car_id].id not in lanes_test[cars[car_id].current_lane].cars_in_lane_id:
            if car_id in cars_in_system:
                print("car in system")
            print("car_id: " + str(car_id) + " cars[car_id].id: " + str(cars[car_id].id) + " cur_lane: " + str(cars[car_id].current_lane) + " car_in_lane_id: " + str(lanes_test[cars[car_id].current_lane].cars_in_lane_id))
            print("cars_path: " + str(cars[car_id].path))
            print("cars_move_status_tracker: " + str(cars[car_id].move_status_tracker))
            print("car 76 move_status_tracker: " + str(cars[76].move_status_tracker))
            canvas.itemconfig(cars[car_id].body, fill='red')
            tk.update()
            input("         car not in current_lane")
        pos_in_queue = lanes_test[cars[car_id].current_lane].cars_in_lane_id.index(cars[car_id].id)
        # cars[car_id].current_end_step = ((len(cars[car_id].fut_pos)) - (pos_in_queue * 5))  - 1
        offset_first = 4
        offset_first = offset_first * 2
        # cars[car_id].current_lane_end_step = (len(cars[car_id].fut_pos)) - offset_first
        if pos_in_queue == 0: # car at front
            cars[car_id].updated_current_end_step = (len(cars[car_id].fut_pos)) - offset_first
            cars[car_id].end_step_for_current_lane = len(lanes_test[cars[car_id].current_lane].move_points) - offset_first
            if lanes_test[cars[car_id].current_lane].next_lanes[0] == 9999:
                cars[car_id].updated_current_end_step = (len(cars[car_id].fut_pos)) - 1
                cars[car_id].end_step_for_current_lane = len(lanes_test[cars[car_id].current_lane].move_points) - 1

        else:
            # position of car in front
            offset = 6 #5
            offset = offset * 2
            cars[car_id].updated_current_end_step = (len(cars[car_id].fut_pos)) - (pos_in_queue * offset) - offset_first

            if lanes_test[cars[car_id].current_lane].next_lanes[0] == 9999:
                cars[car_id].updated_current_end_step = (len(cars[car_id].fut_pos)) - 1
                cars[car_id].end_step_for_current_lane = (len(cars[car_id].fut_pos)) - 1
            # cars[car_id].current_end_step = ((len(cars[car_id].fut_pos)) - (pos_in_queue * 5))  - 1
            t = 1
            cars[car_id].end_step_for_current_lane = len(lanes_test[cars[car_id].current_lane].move_points) - (pos_in_queue * offset) - offset_first
        # if car_id == 89:
        #     print("first section updated_current_end_step: " + str(cars[car_id].updated_current_end_step))

        if pos_in_queue != 0:
            offset = 6 #5
            offset = offset * 2
            # if (car_id == 308) or (car_id == 373) or (car_id == 425):
            #     print("     running find_updated_current_end_step car_id: " + str(car_id))
            #find current move_point of car in fornt
            car_in_front_id =  lanes_test[cars[car_id].current_lane].cars_in_lane_id[(pos_in_queue - 1)]
            car_in_front_move_point = cars[car_in_front_id].fut_pos[cars[car_in_front_id].step] # could change to .current_end_step
            car_in_front_move_point_current_end_step = cars[car_in_front_id].fut_pos[cars[car_in_front_id].current_end_step]
            # now find the index of car_in_front_move_point in cars[car_id].fut_pos
            if car_in_front_move_point in cars[car_id].fut_pos[cars[car_id].step:]: # in fut_pos between current step to the end
                start_looking_after_value = cars[car_id].step
                index_step_temp = cars[car_id].fut_pos.index(car_in_front_move_point,start_looking_after_value)
                cars[car_id].updated_current_end_step = index_step_temp - offset
                # if index_step_temp <= start_looking_after_value:
                #     print("car: " + str())
                # if car_id == 89:
                #     print("inside 1     section updated_current_end_step: " + str(cars[car_id].updated_current_end_step))
                #     print("car_in_front_id: " + str(car_in_front_id))
                #     print("car_in_front_move_point: " + str(car_in_front_move_point))
                #     print("start_looking_after_value: " + str(start_looking_after_value))
                #     print("index_step_temp: " + str(index_step_temp))
                if cars[car_id].updated_current_end_step < cars[car_id].current_end_step:
                    cars[car_id].updated_current_end_step = cars[car_id].current_end_step
                # if car_id == 89:
                #     print("inside 2     section updated_current_end_step: " + str(cars[car_id].updated_current_end_step))
                #     print("car_in_front_id: " + str(car_in_front_id))
                #     print("car_in_front_move_point: " + str(car_in_front_move_point))
                #     print("start_looking_after_value: " + str(start_looking_after_value))
                #     print("index_step_temp: " + str(index_step_temp))

            else:
                # car in front passed the current_lane_end_step, could be that the car is taking a free turn but car_in_front is not
                cars[car_id].updated_current_end_step = cars[car_id].current_lane_end_step
def move_function_new(cars,lanes_test,Car,green_light_lanes):
    for i in cars_in_system:

        if cars[i].move_status == 3:
            # car is moving towards current end step so don't need to do anything
            t = 0
            cars[i].move_status = 3
            cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])

        else:
            # update current_end_step
            find_updated_current_end_step(cars[i].id,lanes_test,cars,Car)
            # print("79update_cur_end_step: " + str(cars[79].updated_current_end_step) + " cur_end_step: " + str(cars[79].current_end_step))
            if cars[i].updated_current_end_step < cars[i].current_end_step:
                cars[i].updated_current_end_step = cars[i].current_end_step

            if cars[i].updated_current_end_step != cars[i].current_end_step:
                # update current_end_step
                # print("updated_current_end_step: " + str(cars[i].updated_current_end_step))
                # print("current_end_step: " + str(cars[i].current_end_step))
                if i == 326:
                    print("updated_current_end_step_326: " + str(cars[i].updated_current_end_step) + " current_end_step: " + str(cars[i].current_end_step))
                # if i == 51:
                #     print("updated_current_end_step_51: " + str(cars[i].updated_current_end_step) + " current_end_step: " + str(cars[i].current_end_step))
                #     print("51 updated")

                cars[i].current_end_step = cars[i].updated_current_end_step
                cars[i].current_end_step_tracker.append(cars[i].current_end_step)
                cars[i].move_status = 3
                cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step,cars[i].updated_current_end_step])
            else:
                cars[i].car_waiting_in_queue = 1  # ie. TRUE as car has joined a queue
                cars[i].car_moving = 0 # ie. FALSE as car has come to a temporary stop


        if cars[i].move_status == 3:
            if cars[i].step > cars[i].current_end_step:
                # if this continues to be an issue, current_end_step equal tp len(fut_pos) or somthing like that
                # canvas.itemconfig(cars[i].body, fill='red')
                # print("move_status_tracker: " + str(cars[i].move_status_tracker))
                print("i: " + str(i))
                print("cars[i].current_lane: " + str(cars[i].current_lane))
                print("curret_lane_map_id: " + str(lanes_test[cars[i].current_lane].map_lane_id))
                print("cars[i].next_lane: " + str(cars[i].next_lane))
                print("next_lane_map_id: " + str(lanes_test[cars[i].next_lane].map_lane_id))
                pos_in_queue_test = lanes_test[cars[i].current_lane].cars_in_lane_id.index(i)
                print("car_pos_in_queue: " + str(pos_in_queue_test))
                print("cars[i].step_tracker: " + str(cars[i].step_tracker))
                print("cars[i].step: " + str(cars[i].step))
                print("cars[i].step_in_current_lane: " + str(cars[i].step_in_current_lane))
                print("cars[i].current_end_step: "+ str(cars[i].current_end_step))
                print("cars[i].current_end_step_tracker: "+ str(cars[i].current_end_step_tracker))
                print("cars[i].current_lane_end_step: " + str(cars[i].current_lane_end_step))
                print("cars[i].end_step_for_current_lane: " + str(cars[i].end_step_for_current_lane))
                print("curre_lane: " + str(cars[i].current_lane) + " next_lane: " + str(cars[i].next_lane))
                print("len(cars[i].fut_pos): " + str(len(cars[i].fut_pos)))

                print("car_in_lane_id: " + str(lanes_test[cars[i].current_lane].cars_in_lane_id))

                car_in_front = lanes_test[cars[i].current_lane].cars_in_lane_id[(pos_in_queue_test - 1)]
                print("car_in_front: " + str(car_in_front))
                print("cars[car_in_front].current_lane: " + str(cars[car_in_front].current_lane))
                print("curret_lane_map_id: " + str(lanes_test[cars[car_in_front].current_lane].map_lane_id))
                print("cars[car_in_front].next_lane: " + str(cars[car_in_front].next_lane))
                print("next_lane_map_id: " + str(lanes_test[cars[car_in_front].next_lane].map_lane_id))
                pos_in_queue_test = lanes_test[cars[car_in_front].current_lane].cars_in_lane_id.index(car_in_front)
                print("car_pos_in_queue: " + str(pos_in_queue_test))
                print("cars[car_in_front].step_tracker: " + str(cars[car_in_front].step_tracker))
                print("cars[car_in_front].step: " + str(cars[car_in_front].step))
                print("cars[car_in_front].step_in_current_lane: " + str(cars[car_in_front].step_in_current_lane))
                print("cars[car_in_front].current_end_step: "+ str(cars[car_in_front].current_end_step))
                print("cars[car_in_front].current_end_step_tracker: "+ str(cars[car_in_front].current_end_step_tracker))
                print("cars[car_in_front].current_lane_end_step: " + str(cars[car_in_front].current_lane_end_step))
                print("cars[car_in_front].end_step_for_current_lane: " + str(cars[car_in_front].end_step_for_current_lane))
                print("curre_lane: " + str(cars[car_in_front].current_lane) + " next_lane: " + str(cars[car_in_front].next_lane))
                print("len(cars[car_in_front].fut_pos): " + str(len(cars[car_in_front].fut_pos)))


                canvas.itemconfig(cars[i].body, fill='red')
                canvas.itemconfig(cars[car_in_front].body, fill='yellow')
                tk.update()
                input("Please press enter to continue...")
            # check to see if current step is equal to current_end_step
            if cars[i].step < cars[i].current_end_step:
                # keep move_sataus the same, car still in process of moving to new position
                cars[i].move_status = 3
                cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
            elif cars[i].step == cars[i].current_end_step:
                # set move_ stauts = 0, which will check if in a green_light_lane and at front of queue
                # car reached its temporary end step
                # cars[i].car_waiting_in_queue = 1  # ie. TRUE as car has joined a queue
                # cars[i].car_moving = 0 # ie. FALSE as car has come to a temporary stop
                cars[i].move_status = 0
                cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
            # elif cars[i].current_lane in green_light_lanes:
            #     # check to see if car is moving/ approacin the end of the queue in a lane which now has a green light
            #     cars[i].move_status = 1
            #     cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])

        if cars[i].move_status == 0:
            # we know car has reached the its current_end_step
            # check to see if car is at end of exit lane
            if lanes_test[cars[i].current_lane].next_lanes[0] == 9999:
                # car has left exit lane
                # remove car from system
                # cars_in_system.remove(cars[i].id)
                cars_in_system.remove(i)
                cars_exited_system.append(i)
                cars[i].car_in_system = 0
                # set all time checker parameters to zero
                cars[i].car_moving = 0
                cars[i].car_waiting_in_queue = 0
                cars[i].car_waiting_to_enter_system = 0
                # remove car from exot (current) lane
                # if i not in lanes_test[cars[i].current_lane].cars_in_lane_id:
                #     print("i: " + str(i) + " cur_lane: " + str(cars[i].current_lane) + " car_in_cur_lane_id: " + str(lanes_test[cars[i].current_lane].cars_in_lane_id))
                #     # print("")
                #     print("move_status_tracker: " + str(cars[i].move_status_tracker))
                #     print("move_status_tracker_car_17: " + str(cars[17].move_status_tracker))

                lanes_test[cars[i].current_lane].cars_in_lane_id.remove(i)
                # add to move_status_tracker a 9999
                cars[i].move_status = 9999
                cars[i].move_status_tracker.append(cars[i].move_status)
                cars[i].current_lane = 9999  #### new
                # print("g_lane: " + str(cars[i].g_lane))
                # print("g_lane_temp: " + str(cars[i].g_lane_temp))
                # print("car_id: " + str(i))
                # print("move_status_tracker: " + str(cars[i].move_status_tracker))
                # if (cars[i].g_lane != 9999) and (i in lanes_test[cars[i].g_lane].g_cars_in_lane_id):
                #     lanes_test[cars[i].g_lane].g_cars_in_lane_id.remove(i)
                # else:
                #     print("g_lane: " + str(cars[i].g_lane))
                #     print("g_lane_temp: " + str(cars[i].g_lane_temp))
                #     print("car_id: " + str(i))
                #     print("move_status_tracker: " + str(cars[i].move_status_tracker))
                #
                # # print("g_lane: " + str(cars[i].g_lane))
                # cars[i].g_lane = 9999
                # cars[i].potential_lanes_1 = []
                # cars[i].potential_lanes_2 = []
                # cars[i].potential_lanes_lines_1 = []
                # cars[i].potential_lanes_lines_2 = []
                #
            # check to see if the car is moving into free_turn_next_lane so current_lane doesn't need to be in green_light_lanes
            elif cars[i].next_lane in lanes_test[cars[i].current_lane].free_turn_next_lanes:
                # if cars[i].step == cars[i].current_lane_end_step: # this will confirm if the car is at the correct pointin current_lane to move to next_lane
                # check if there is space for car to move into next_lane
                pos_in_queue = lanes_test[cars[i].current_lane].cars_in_lane_id.index(i)
                if cars[i].step == cars[i].current_lane_end_step:
                # if cars[i].step == cars[i].current_end_step:   ###### here now
                    cars[i].move_status = 0 # initially assume car can't move (not enough space)
                    cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
                    #### assign cars next lane
                    if cars[i].next_lane in lanes_test[cars[i].current_lane].next_lanes: # car already has a next_lane
                        t = 1
                    else:
                        t = 0
                    #### check for space for the car to move into the next lane
                    space_check = 0 # initially assume there is NoT enough space for the car
                    # if car entering an exit lane there will always be space
                    if lanes_test[cars[i].next_lane].next_lanes[0] == 9999:
                        # car can enter next_lane
                        cars[i].move_status = 2
                        cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
                    # need more than 5 steps of space in the next lane, ie. need more than 5 move_points
                    # if car is entering a lane that is currently empty, there will obviously be space
                    elif len(lanes_test[cars[i].next_lane].cars_in_lane_id) == 0:
                        # car can enter next_lane
                        space_check = 1
                        cars[i].move_status = 2
                        cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
                    # all other cases check to see if there enough space in the next_lane
                    else:
                        # can the lane fit another car?
                        ## add here
                        car_id_back_of_queue_in_next_lane = lanes_test[cars[i].next_lane].cars_in_lane_id[-1]
                        # car_id_back_of_queue_in_next_lane_step = cars[car_id_back_of_queue_in_next_lane].step
                        # car_id_back_of_queue_in_next_lane_current_move_point = cars[car_id_back_of_queue_in_next_lane].fut_pos[cars[car_id_back_of_queue_in_next_lane].step]
                        car_id_back_of_queue_in_next_lane_step_current_end_step = cars[car_id_back_of_queue_in_next_lane].current_end_step
                        car_id_back_of_queue_in_next_lane_current_move_point = cars[car_id_back_of_queue_in_next_lane].fut_pos[car_id_back_of_queue_in_next_lane_step_current_end_step]
                        if car_id_back_of_queue_in_next_lane_current_move_point in lanes_test[cars[i].next_lane].move_points:
                            index_car_at_back_move_point_in_lane_move_point = lanes_test[cars[i].next_lane].move_points.index(car_id_back_of_queue_in_next_lane_current_move_point)
                            offset = 6 #5
                            offset = offset * 2
                            if index_car_at_back_move_point_in_lane_move_point > offset:
                                # room of next car to enter
                                space_check = 1 # not enough space so set space_check = 0
                                # car can enter next_lane
                                cars[i].move_status = 2
                                cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])



                        # lane_length = len(lanes_test[cars[i].next_lane].move_points)
                        # num_cars_in_next_lane = len(lanes_test[cars[i].next_lane].cars_in_lane_id)
                        # pos_in_queue = num_cars_in_next_lane + 1
                        # # assume each car needs/occupies 5 move_vals
                        # if (pos_in_queue * 5) < lane_length: # there IS enough space
                        # # if pos_in_queue < 5:
                        #     space_check = 1 # not enough space so set space_check = 0
                        #     # car can enter next_lane
                        #     cars[i].move_status = 2
                        #     cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])

            # check if car in a green light lane, then check position of car in lane
            elif cars[i].current_lane in green_light_lanes:
                cars[i].move_status = 1
                cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
                # check to see if car at first in lane, not necessarily at the end point of lane
                pos_in_queue = lanes_test[cars[i].current_lane].cars_in_lane_id.index(i)
                if cars[i].step == cars[i].current_lane_end_step: # this will confirm if the car is that the front position of the lane
                # if pos_in_queue == 0:
                    cars[i].move_status = 0 # initially assume car can't move (not enough space)
                    cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
                    #### assign cars next lane
                    if cars[i].next_lane in lanes_test[cars[i].current_lane].next_lanes: # car already has a next_lane
                        t = 1
                    else:
                        t = 0
                        # cars[i].next_lane = random.choice(lanes_test[cars[i].current_lane].next_lanes)   ##### changes this in the future
                    #### check for space for the car to move into the next lane
                    space_check = 0 # initially assume there is NOT enough space for the car
                    # if car entering an exit lane there will always be space
                    if lanes_test[cars[i].next_lane].next_lanes[0] == 9999:
                        offset = 6 #28 # 6
                        offset = offset * 2
                        # only move if the car in front has moved 12 steps
                        wait_offset = 24
                        # if (index_car_at_back_move_point_in_lane_move_point > offset) and (lanes_test[cars[i].current_lane].next_car_free_to_go >= wait_offset):
                        if lanes_test[cars[i].current_lane].next_car_free_to_go <= 0:
                            # reset the next_car_free_to_go to 0
                            # lanes_test[cars[i].current_lane].next_car_free_to_go = 0 # add 1 to this variable every loop
                            lanes_test[cars[i].current_lane].next_car_free_to_go = wait_offset  # subtract 1 from this variable every loop
                            # room of next car to enter
                            space_check = 1 # not enough space so set space_check = 0
                            # car can enter next_lane
                            cars[i].move_status = 2
                            cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
                        # # car can enter next_lane
                        # cars[i].move_status = 2
                        # cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
                    # need more than 5 steps of space in the next lane, ie. need more than 5 move_points
                    # if car is entering a lane that is currently empty, there will obviously be space
                    elif len(lanes_test[cars[i].next_lane].cars_in_lane_id) == 0:
                        # car can enter next_lane when the current_lane is ready to release next_car (next_car_free_to_go)
                        offset = 6 #28 # 6
                        offset = offset * 2
                        # only move if the car in front has moved 12 steps
                        wait_offset = 24
                        # if (index_car_at_back_move_point_in_lane_move_point > offset) and (lanes_test[cars[i].current_lane].next_car_free_to_go >= wait_offset):
                        if lanes_test[cars[i].current_lane].next_car_free_to_go <= 0:
                            # reset the next_car_free_to_go to 0
                            # lanes_test[cars[i].current_lane].next_car_free_to_go = 0 # add 1 to this variable every loop
                            lanes_test[cars[i].current_lane].next_car_free_to_go = wait_offset  # subtract 1 from this variable every loop
                            # room of next car to enter
                            space_check = 1 # not enough space so set space_check = 0
                            # car can enter next_lane
                            cars[i].move_status = 2
                            cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])

                        # # car can enter next_lane
                        # space_check = 1
                        # cars[i].move_status = 2
                        # cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
                    # all other cases check to see if there enough space in the next_lane
                    else:
                        # can the lane fit another car?
                        ##### add here
                        car_id_back_of_queue_in_next_lane = lanes_test[cars[i].next_lane].cars_in_lane_id[-1]
                        # car_id_back_of_queue_in_next_lane_step = cars[car_id_back_of_queue_in_next_lane].step
                        # car_id_back_of_queue_in_next_lane_current_move_point = cars[car_id_back_of_queue_in_next_lane].fut_pos[cars[car_id_back_of_queue_in_next_lane].step]
                        car_id_back_of_queue_in_next_lane_step_current_end_step = cars[car_id_back_of_queue_in_next_lane].current_end_step
                        car_id_back_of_queue_in_next_lane_current_move_point = cars[car_id_back_of_queue_in_next_lane].fut_pos[car_id_back_of_queue_in_next_lane_step_current_end_step]
                        if car_id_back_of_queue_in_next_lane_current_move_point in lanes_test[cars[i].next_lane].move_points:
                            index_car_at_back_move_point_in_lane_move_point = lanes_test[cars[i].next_lane].move_points.index(car_id_back_of_queue_in_next_lane_current_move_point)
                            offset = 6 #5
                            offset = offset * 2
                            wait_offset = 24
                            # if (index_car_at_back_move_point_in_lane_move_point > offset) and (lanes_test[cars[i].current_lane].next_car_free_to_go >= wait_offset):
                            if (index_car_at_back_move_point_in_lane_move_point > offset) and (lanes_test[cars[i].current_lane].next_car_free_to_go <= 0):
                                # reset the next_car_free_to_go to 0
                                # lanes_test[cars[i].current_lane].next_car_free_to_go = 0 # add 1 to this variable every loop
                                lanes_test[cars[i].current_lane].next_car_free_to_go = wait_offset  # subtract 1 from this variable every loop
                                # room of next car to enter
                                space_check = 1 # not enough space so set space_check = 0
                                # car can enter next_lane
                                cars[i].move_status = 2
                                cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])

                        # lane_length = len(lanes_test[cars[i].next_lane].move_points)
                        # num_cars_in_next_lane = len(lanes_test[cars[i].next_lane].cars_in_lane_id)
                        # pos_in_queue = num_cars_in_next_lane + 1
                        # # assume each car needs/occupies 5 move_vals
                        # if (pos_in_queue * 5) < lane_length: # there IS enough space
                        # # if pos_in_queue < 5:
                        #     space_check = 1 # not enough space so set space_check = 0
                        #     # car can enter next_lane
                        #     cars[i].move_status = 2
                        #     cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
            #check if the queue has moved forward since the car entered and starting moving towards current_end_step ie. does current_end_step need to be updated


        if cars[i].move_status == 2:
            # we know at this point that the car is going to change lane, so need to find fut_pos transition points,
            # and need to find fut_pos move_points for next_lane and the a end_step
            cars[i].car_waiting_in_queue = 0  # ie. FALSE
            cars[i].car_moving = 1 # ie. TRUE
            # find fut_pos for transition to next lane
            fut_pos_change_lane(cars[i].id,lanes_test,cars,Car)
            # should leave curent_lane here and enter next_lane
            lanes_test[cars[i].current_lane].cars_in_lane_id.remove(i)
            # if i == 76:
            #     print("76 path: " + str(cars[i].path))
            #     print("76 cur_lane: " + str(cars[i].current_lane)  + " next_lane: " + str(cars[i].next_lane))
            #     input("runngin")
            lanes_test[cars[i].next_lane].cars_in_lane_id.append(i)
            # cars[i].current_lane = cars[i].next_lane
            cars[i].path_step += 1
            cars[i].current_lane = cars[i].path[cars[i].path_step]
            cars[i].step_in_current_lane = 0
            cars[i].next_lane = []
            #### assign cars next lane
            if cars[i].next_lane in lanes_test[cars[i].current_lane].next_lanes: # car already has a next_lane
                t = 1
            else:
                t = 0
                # cars[i].next_lane = random.choice(lanes_test[cars[i].current_lane].next_lanes)   ##### changes this in the future
                # print("path: " + str(cars[i].path))
                # print("i: " + str(i) + " cur_lane: " + str(cars[i].current_lane) + " path_step: " + str(cars[i].path_step))
                cars[i].next_lane = cars[i].path[(cars[i].path_step + 1)]
                # cars[i].next_lane = cars[i].path[(cars[i].path_step)] # line 2175 the cars[i].path_step += 1
            # find fut_pos in new current_lane
            fut_pos_current_lane(cars[i].id,lanes_test,cars,Car)
            # find current end_step
            find_current_end_step(cars[i].id,lanes_test,cars,Car)
            # set move_status = 3, so the car will move a step forward
            cars[i].move_status = 3
            cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])

        if cars[i].move_status == 1:
            # we know car is in a lane with a green light BUT it is not at the front of the queue
            # so most update the end_step as cars in front be moving and hence this car's end step will need to change to keep up with cars in front
            ####
            # find_current_end_step(cars[i].id,lanes_test,cars,Car)
            # # set move_status = 3, so the car will move a step forward
            # cars[i].move_status = 3
            # cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
            ####
            find_updated_current_end_step(cars[i].id,lanes_test,cars,Car)
            if cars[i].updated_current_end_step != cars[i].current_end_step:
                # update current_end_step
                # print("updated_current_end_step2: " + str(cars[i].updated_current_end_step))
                # print("current_end_step2: " + str(cars[i].current_end_step))
                if i == 326:
                    print("updated_current_end_step_326: " + str(cars[i].updated_current_end_step) + " current_end_step: " + str(cars[i].current_end_step))
                if cars[i].updated_current_end_step < cars[i].current_end_step:
                    print("updated lower car: " + str(i) + " updated_current_end_step: " + str(cars[i].updated_current_end_step) + " current_end_step: " + str(cars[i].current_end_step))
                    print("car_current_lane: " + str(cars[i].current_lane) + " next_lane: " + str(cars[i].next_lane))
                else:
                    cars[i].current_end_step = cars[i].updated_current_end_step
                    cars[i].current_end_step_tracker.append(cars[i].current_end_step)
                    cars[i].move_status = 3
                    cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
            ####

        if cars[i].move_status == 3:
            # we know car is not at its current_end_step, so move car forward one step and draw new position
            # print("i: " + str(i))
            # print("cars[i].step: " + str(cars[i].step))
            # print("cars[i].current_end_step: "+ str(cars[i].current_end_step))
            # print("len(cars[i].fut_pos): " + str(len(cars[i].fut_pos)))
            cars[i].step += 1
            cars[i].step_tracker.append(cars[i].step)
            cars[i].step_in_current_lane += 1
            cars[i].pos_x = cars[i].fut_pos[cars[i].step][0]
            cars[i].pos_y = cars[i].fut_pos[cars[i].step][1]
            cars[i].angle = cars[i].fut_pos[cars[i].step][2]
            # draw car
            Car.car_on_angle(cars[i],cars[i].pos_x,cars[i].pos_y,car_width,car_length,cars[i].angle)
def car_entering_function(cars,lanes_test,Car,car_id,cars_in_system,cars_entered_system,cars_intending_to_enter,cars_to_wait_this_iter,cars_entering_this_iter):
    # space_check = 1 # initially assume there is sapce for the car/ previous car has moved forward enough in lane for new car to enter
    space_check = 0 # initially assume there is NO space for the car intending to enter
    car_intended_entry_lane = cars[car_id].current_lane
    if len(lanes_test[car_intended_entry_lane].cars_in_lane_id) == 0: # guaranteed space in the lane
        space_check = 1

    # need more than 5 steps of space in the entry lane, ie. need more than 5 move_points
    if len(lanes_test[car_intended_entry_lane].cars_in_lane_id) > 0: # ie. there are cars in the intended lane
        car_in_front = lanes_test[car_intended_entry_lane].cars_in_lane_id[-1]
        # print("cars[car_in_front].pos_x: " + str(cars[car_in_front].pos_x) + " cars[car_in_front].pos_y: " + str(cars[car_in_front].pos_y) + " cars[car_in_front].angle: " + str(cars[car_in_front].angle))
        # print("lanes_test[car_intended_entry_lane].move_points: " + str(lanes_test[car_intended_entry_lane].move_points))
        # print("lane: " + str(car_intended_entry_lane) + " cars_in_lane: " + str(lanes_test[car_intended_entry_lane].cars_in_lane_id))
        # print("map_lane: " + str(lanes_test[car_intended_entry_lane].map_lane_id))
        # print("car_id: " + str(car_id) + " car_in_front: " + str(car_in_front))
        # print("car_in_fron cut_lane: " + str(cars[car_in_front].current_lane))
        # car_in_front_index = lanes_test[car_intended_entry_lane].move_points.index([cars[car_in_front].pos_x,cars[car_in_front].pos_y,cars[car_in_front].angle])
        car_in_front_index = lanes_test[car_intended_entry_lane].cars_in_lane_id.index(car_in_front) # changed to this from the above
        # print("car_in_front_index: " + str(car_in_front_index))

        lane_length = len(lanes_test[car_intended_entry_lane].move_points)
        num_cars_in_intended_lane = len(lanes_test[car_intended_entry_lane].cars_in_lane_id)
        pos_in_queue = num_cars_in_intended_lane + 1

        #####
        # can the lane fit another car?
        ## add here
        car_id_back_of_queue_in_next_lane = lanes_test[car_intended_entry_lane].cars_in_lane_id[-1]
        # car_id_back_of_queue_in_next_lane_step = cars[car_id_back_of_queue_in_next_lane].step
        # car_id_back_of_queue_in_next_lane_current_move_point = cars[car_id_back_of_queue_in_next_lane].fut_pos[cars[car_id_back_of_queue_in_next_lane].step]
        car_id_back_of_queue_in_next_lane_step_current_end_step = cars[car_id_back_of_queue_in_next_lane].current_end_step
        car_id_back_of_queue_in_next_lane_current_move_point = cars[car_id_back_of_queue_in_next_lane].fut_pos[car_id_back_of_queue_in_next_lane_step_current_end_step]
        if car_id_back_of_queue_in_next_lane_current_move_point in lanes_test[car_intended_entry_lane].move_points:
            index_car_at_back_move_point_in_lane_move_point = lanes_test[car_intended_entry_lane].move_points.index(car_id_back_of_queue_in_next_lane_current_move_point)
            offset = 6 #5
            offset = offset * 2
            if index_car_at_back_move_point_in_lane_move_point > offset:
                # room of next car to enter
                space_check = 1 # not enough space so set space_check = 0
                # car can enter next_lane
        #####


        ############
        # # assume each car needs/occupies 5 move_vals
        # if (pos_in_queue * 5) > lane_length: # there IS NOT enough space
        # # if car_in_front_index > 6: # there is NO space of the car to enter the next_lane
        #     # print("cars_in_lane_id: " + str(lanes_test[car_intended_entry_lane].cars_in_lane_id))
        #     # print("car_id: " + str(car_id) + " car_in_front: " + str(car_in_front))
        #     # print("cars[car_in_front].pos_x: " + str(cars[car_in_front].pos_x) + " cars[car_in_front].pos_y: " + str(cars[car_in_front].pos_y) + " cars[car_in_front].angle: " + str(cars[car_in_front].angle))
        #     # car will not enter system this iteration and car will remain in cars_to_enter list
        #     cars[car_id].move_status = 0
        #     space_check = 0 # not enough space so set space_check = 0
        #     cars_to_wait_this_iter.append(car_id)
        #     # print("no_space_car_id: " + str(car_id) + "intended_lane: " + str(car_intended_entry_lane))
        ###############
    if space_check == 0:
        cars[car_id].move_status = 0
        space_check = 0 # not enough space so set space_check = 0
        cars_to_wait_this_iter.append(car_id)

    if space_check == 1: # space for car to enter into system
        cars_in_system.append(car_id)
        cars[car_id].car_in_system = 1
        cars[car_id].car_waiting_to_enter_system = 0
        cars_entered_system.append(car_id)
        cars_entering_this_iter.append(car_id)
        # add car to cars_in_lane_id store
        lanes_test[cars[car_id].current_lane].cars_in_lane_id.append(cars[car_id].id)
        # remove car from list of cars_intending_to_enter
        # temp_cars_intending_to_enter.remove(car_id)
        # find fut_pos for car
        fut_pos_current_lane(cars[car_id].id,lanes_test,cars,Car)
        # find current end step
        if (cars[car_id].current_lane == cars[car_id].path[0]) and (cars[car_id].current_lane not in entry_lanes): # car is going to start in an internal lane
            find_current_end_step_for_start_internal_lane(car_id,lanes_test,cars,Car)
        else:
            find_current_end_step(cars[car_id].id,lanes_test,cars,Car)
        # if car_id == 0:
        #     print("ran 3 current_end_step: " + str(cars[car_id].current_end_step))
        if cars[car_id].current_lane not in entry_lanes: # the car is starting in an internal lane
            # print("run")
            # set move_status to 1
            cars[car_id].move_status = 3
            cars[car_id].step = cars[car_id].current_end_step - 1
            # print("step: " + str(cars[car_id].step))
            cars[car_id].pos_x = cars[car_id].fut_pos[cars[car_id].step][0]
            cars[car_id].pos_y = cars[car_id].fut_pos[cars[car_id].step][1]
            cars[car_id].angle = cars[car_id].fut_pos[cars[car_id].step][2]
            # print("pos_x: " + str(cars[car_id].pos_x) + " pos_y: " + str(cars[car_id].pos_y) )
        else: # car is starting in an entry lane
            # print("not run")
            # set move_status to 3
            cars[car_id].move_status = 3
            # cars[car_id].step += 1
            cars[car_id].pos_x = cars[car_id].fut_pos[cars[car_id].step][0]
            cars[car_id].pos_y = cars[car_id].fut_pos[cars[car_id].step][1]
            cars[car_id].angle = cars[car_id].fut_pos[cars[car_id].step][2]
def light_control_function(juncs_test,lanes_test,green_light_lanes,time_interval,red_light_lanes_pause_temp):
    # red_light_lanes_pause_temp = []
    for t in range(len(lanes_test)):
        if (lanes_test[t].green_light == 1) and (t not in green_light_lanes):
            green_light_lanes.append(t)
            turn_light_green(t)

            for p in range(len(juncs_test)):
                if t in juncs_test[p].light_lanes_at_junc:
                    juncs_test[p].lane_at_junc_green = t
    # if 33 in green_light_lanes:
    #     print("33 " + " green_light_lanes: " + str(green_light_lanes))
    green_light_lanes_temp = green_light_lanes
    for k in green_light_lanes:
        # print("checking_1")
        if lanes_test[k].time_green <= 0: # ie one of the lights has run out of time
            # check if associated lane is also has time.green = 0
            turn_light_red(k)
            lanes_test[k].green_light = 0
            lanes_test[k].next_car_free_to_go = 0 # set this to zero as a reset
            green_light_lanes_temp.remove(k)
            lanes_test[k].light_time_pause = 2 #time_interval * 12 was set to 0.5
            red_light_lanes_pause_temp.append(k)
            # print("checking_2")

    # print("rrl :"  + str(red_light_lanes_pause_temp))
    red_light_lanes_pause = red_light_lanes_pause_temp
    # print("new_loop")
    # print("red_light_lanes_pause: " + str(red_light_lanes_pause))
    for k in red_light_lanes_pause:
        # print("rrl :"  + str(red_light_lanes_pause_temp))
        # print("rrl_t :"  + str(lanes_test[k].light_time_pause))
        if lanes_test[k].light_time_pause <= 0:  # red light pause has finshed and now llok for a new lane to turn green at the junction
            # print("checking_3")
            red_light_lanes_pause_temp.remove(k)
            lanes_test[k].light_time_pause = 0

            # find the next lane in the junction to turn green, by triggering the thread
            for t in range(len(juncs_test)):
                if k in juncs_test[t].light_lanes_at_junc:
                    juncs_test[t].ready_for_green = 1 # junction all reds and pause finsihed so so turn on (set to 1) ready_for_green, which will trigger the thread to act on this junction
            # print("ready for green")

    red_light_lanes_pause = red_light_lanes_pause_temp
    green_light_lanes = green_light_lanes_temp

    for k in green_light_lanes:
        lanes_test[k].time_green -= time_interval # new time step so subtract the time_interval
        # print("time_green: " + str(lanes_test[k].time_green))

    for k in red_light_lanes_pause:
        lanes_test[k].light_time_pause -= time_interval # new time step so subtract the time_interval

def find_potential_lane_1_angle_method(cars,lanes_test,car_id):
    cars[car_id].potential_lanes_1 = []
    potential_lane_temp = []
    potential_lane_line_temp = []
    for i in range(len(lanes_test)):
        # now loop thorugh all the lines in the lane
        num_lines_in_lane = len(lanes_test[i].points_with_angles) - 1
        for j in range(num_lines_in_lane):
            line_point_1_x = lanes_test[i].points_with_angles[j][0]
            line_point_1_y = lanes_test[i].points_with_angles[j][1]
            line_point_2_x = lanes_test[i].points_with_angles[j + 1][0]
            line_point_2_y = lanes_test[i].points_with_angles[j + 1][1]
            line_angle = lanes_test[i].points_with_angles[j][2]

            gps_line_angle = line_angle - (math.pi/2)
            gps_point_1_x = cars[car_id].coords[0]
            gps_point_1_y = cars[car_id].coords[1]
            gps_point_2_x = gps_point_1_x + rad_gps*math.sin(gps_line_angle)
            gps_point_2_y = gps_point_1_y - rad_gps*math.cos(gps_line_angle)
            #####
            line_in_lane = [[line_point_1_x,line_point_1_y],[line_point_2_x,line_point_2_y]]
            gps_line = [[gps_point_1_x,gps_point_1_y],[gps_point_2_x,gps_point_2_y]]
            # find point of interssection between lane lane and gps_line
            point_of_intersection = find_intersection_point_between_lines(line_in_lane,gps_line)
            # print("lane_line: " + str([i,j]))
            # print("point_of_intersection: " + str(point_of_intersection))

            # find distance between point_of_intersection and the gps coord
            dist = math.sqrt(((gps_point_1_y - point_of_intersection[1])**2) + ((gps_point_1_x - point_of_intersection[0])**2))
            # check if distance less than or equal to rad_gps
            if dist <= rad_gps:
                # check if point_of_intersection lies on the lane line
                # print("dist_criteria: " + str([i,j]))
                # print("point_of_intersection: " + str(point_of_intersection))
                # canvas.create_oval(point_of_intersection[0] - 3,point_of_intersection[1] - 3,point_of_intersection[0] + 3, point_of_intersection[1] + 3, fill = 'red')
                # tk.update()
                # input("press enter 1... ")
                length_of_lane_line = math.sqrt(((line_point_2_y - line_point_1_y)**2) + ((line_point_2_x - line_point_1_x)**2))
                length_of_lane_line_margin = length_of_lane_line + rad_gps #+ rad_gps
                dist_point_intersection_and_line_point_1 = math.sqrt(((line_point_1_y - point_of_intersection[1])**2) + ((line_point_1_x - point_of_intersection[0])**2))
                dist_point_intersection_and_line_point_2 = math.sqrt(((line_point_2_y - point_of_intersection[1])**2) + ((line_point_2_x - point_of_intersection[0])**2))

                tot_dist_with_point_of_intersection = dist_point_intersection_and_line_point_1 + dist_point_intersection_and_line_point_2

                # print("length_of_lane_line_margin: " + str(length_of_lane_line_margin))
                # print("dist_point_intersection_and_line_point_1: " +str(dist_point_intersection_and_line_point_1))
                # print("dist_point_intersection_and_line_point_2: " +str(dist_point_intersection_and_line_point_2))
                # print("tot_dist_with_point_of_intersection: " + str(tot_dist_with_point_of_intersection))
                # input("press enter 2...")
                # check if distance from line points to the point of intersceiton are with the margin for the length between the line points
                if tot_dist_with_point_of_intersection <= length_of_lane_line_margin:
                    # add rad_gps to this
                    # this confirms that the coord could be provided by a car of this line in lane
                    # add this lane and lane's line to potenial_lanes
                    potential_lane_temp.append(i)
                    potential_lane_line_temp.append([i,j,point_of_intersection])
                    # potential_lane_line_temp.append(point_of_intersection)
    temp_2 = []
    for val in potential_lane_temp:  # to remove duplicates in the potential lane list
           if val not in temp_2:
              temp_2.append(val)
    potential_lane_temp = temp_2
    ###
    temp_3 = []
    for val_line in potential_lane_line_temp:  # to remove duplicates in the potential lane list
           if val_line not in temp_3:
              temp_3.append(val_line)
    potential_lane_line_temp = temp_3
    ###
    # set the variables in the new class
    cars[car_id].potential_lanes_1 = potential_lane_temp
    cars[car_id].potential_lanes_lines_1 = potential_lane_line_temp
def find_potential_lane_2_angle_method(cars,lanes_test,car_id):
    cars[car_id].potential_lanes_2= []
    potential_lane_temp = []
    potential_lane_line_temp = []
    for i in range(len(lanes_test)):
        # now loop thorugh all the lines in the lane
        num_lines_in_lane = len(lanes_test[i].points_with_angles) - 1
        for j in range(num_lines_in_lane):
            line_point_1_x = lanes_test[i].points_with_angles[j][0]
            line_point_1_y = lanes_test[i].points_with_angles[j][1]
            line_point_2_x = lanes_test[i].points_with_angles[j + 1][0]
            line_point_2_y = lanes_test[i].points_with_angles[j + 1][1]
            line_angle = lanes_test[i].points_with_angles[j][2]

            gps_line_angle = line_angle - (math.pi/2)
            gps_point_1_x = cars[car_id].coords[0]
            gps_point_1_y = cars[car_id].coords[1]
            gps_point_2_x = gps_point_1_x + rad_gps*math.sin(gps_line_angle)
            gps_point_2_y = gps_point_1_y - rad_gps*math.cos(gps_line_angle)
            #####
            line_in_lane = [[line_point_1_x,line_point_1_y],[line_point_2_x,line_point_2_y]]
            gps_line = [[gps_point_1_x,gps_point_1_y],[gps_point_2_x,gps_point_2_y]]
            # find point of interssection between lane lane and gps_line
            point_of_intersection = find_intersection_point_between_lines(line_in_lane,gps_line)
            # print("lane_line: " + str([i,j]))
            # print("point_of_intersection: " + str(point_of_intersection))

            # find distance between point_of_intersection and the gps coord
            dist = math.sqrt(((gps_point_1_y - point_of_intersection[1])**2) + ((gps_point_1_x - point_of_intersection[0])**2))
            # check if distance less than or equal to rad_gps
            if dist <= rad_gps:
                # check if point_of_intersection lies on the lane line
                # print("dist_criteria: " + str([i,j]))
                # print("point_of_intersection: " + str(point_of_intersection))
                # canvas.create_oval(point_of_intersection[0] - 3,point_of_intersection[1] - 3,point_of_intersection[0] + 3, point_of_intersection[1] + 3, fill = 'green')
                # tk.update()
                # input("press enter 1... ")
                length_of_lane_line = math.sqrt(((line_point_2_y - line_point_1_y)**2) + ((line_point_2_x - line_point_1_x)**2))
                length_of_lane_line_margin = length_of_lane_line + rad_gps #+ rad_gps
                dist_point_intersection_and_line_point_1 = math.sqrt(((line_point_1_y - point_of_intersection[1])**2) + ((line_point_1_x - point_of_intersection[0])**2))
                dist_point_intersection_and_line_point_2 = math.sqrt(((line_point_2_y - point_of_intersection[1])**2) + ((line_point_2_x - point_of_intersection[0])**2))

                tot_dist_with_point_of_intersection = dist_point_intersection_and_line_point_1 + dist_point_intersection_and_line_point_2

                # print("length_of_lane_line_margin: " + str(length_of_lane_line_margin))
                # print("dist_point_intersection_and_line_point_1: " +str(dist_point_intersection_and_line_point_1))
                # print("dist_point_intersection_and_line_point_2: " +str(dist_point_intersection_and_line_point_2))
                # print("tot_dist_with_point_of_intersection: " + str(tot_dist_with_point_of_intersection))
                # input("press enter 2...")
                # check if distance from line points to the point of intersceiton are with the margin for the length between the line points
                if tot_dist_with_point_of_intersection <= length_of_lane_line_margin:
                    # add rad_gps to this
                    # this confirms that the coord could be provided by a car of this line in lane
                    # add this lane and lane's line to potenial_lanes
                    potential_lane_temp.append(i)
                    potential_lane_line_temp.append([i,j,point_of_intersection])
                    # potential_lane_line_temp.append(point_of_intersection)
    temp_2 = []
    for val in potential_lane_temp:  # to remove duplicates in the potential lane list
           if val not in temp_2:
              temp_2.append(val)
    potential_lane_temp = temp_2
    ###
    temp_3 = []
    for val_line in potential_lane_line_temp:  # to remove duplicates in the potential lane list
           if val_line not in temp_3:
              temp_3.append(val_line)
    potential_lane_line_temp = temp_3
    ###
    # set the variables in the new class
    cars[car_id].potential_lanes_2 = potential_lane_temp
    cars[car_id].potential_lanes_lines_2 = potential_lane_line_temp
def find_dist_to_lane_points_method_potential_lane_1(cars,lanes_test,car_id,rad_gps):
    cars[car_id].dist_lane_forward_points_1 = []
    for q in range(len(cars[car_id].potential_lanes_lines_1)):
        lane_of_int = cars[car_id].potential_lanes_lines_1[q][0]
        line_of_int = cars[car_id].potential_lanes_lines_1[q][1]
        point_of_intersection = cars[car_id].potential_lanes_lines_1[q][2]

        # print("line_of_int: " +str(line_of_int))
        first_point_of_int_index = line_of_int + 1  # this give the point at the end of the line_of_int
        num_of_points_in_lane = len(lanes_test[lane_of_int].points_with_angles)
        # print("first_point_of_int_index: " + str(first_point_of_int_index))
        # print("num_of_points_in_lane: " + str(num_of_points_in_lane))
        # input("press 3")
        temp_dist_lane_forward_points_1 = []
        temp_dist_lane_forward_points_1.append(lane_of_int)

        for k in range(first_point_of_int_index , num_of_points_in_lane): # loop through the first point and all points to the end of lane
            # print("runngins")
            point_index = k
            temp_lane_line_point = lanes_test[lane_of_int].points_with_angles[k][0:2]
            # print("temp_lane_line_point: " + str(temp_lane_line_point))
            # canvas.create_oval(temp_lane_line_point[0] - 2, temp_lane_line_point[1] - 2,temp_lane_line_point[0] + 2,temp_lane_line_point[1] + 2, fill = 'yellow')
            # tk.update()
            dist_to_point = math.sqrt(((temp_lane_line_point[1] - point_of_intersection[1])**2) + ((temp_lane_line_point[0] - point_of_intersection[0])**2))
            # temp_dist_lane_forward_points_1.append(lane_of_int)
            # temp_dist_lane_forward_points_1.append(line_of_int)
            # temp_dist_lane_forward_points_1.append(point_index)
            # temp_dist_lane_forward_points_1.append(dist_to_point)
            temp_dist_lane_forward_points_1.append([point_index,dist_to_point])
            # print("temp_dist_lane_forward_points_1: " + str(temp_dist_lane_forward_points_1))
            # cars[car_id].dist_lane_forward_points_1.append([lane_of_int,line_of_int,dist_to_point])
        # print("temp_dist_lane_forward_points_1_2: " + str(temp_dist_lane_forward_points_1))
        cars[car_id].dist_lane_forward_points_1.append(temp_dist_lane_forward_points_1)
def find_dist_to_lane_points_method_lanes_common(cars,lanes_test,car_id,rad_gps):
    for r in range(len(cars[car_id].potential_lanes_lines_2)):
        if cars[car_id].potential_lanes_lines_2[r][0] in cars[car_id].localisation_lanes_common:
            lane_of_int = cars[car_id].potential_lanes_lines_2[r][0]
            line_of_int = cars[car_id].potential_lanes_lines_2[r][1]
            point_of_intersection = cars[car_id].potential_lanes_lines_2[r][2]

            first_point_of_int_index = line_of_int + 1  # this give the point at the end of the line_of_int
            num_of_points_in_lane = len(lanes_test[lane_of_int].points_with_angles)

            temp_dist_lane_forward_points_lanes_common = []
            temp_dist_lane_forward_points_lanes_common.append(lane_of_int)

            for k in range(first_point_of_int_index , num_of_points_in_lane): # loop through the first point and all points to the end of lane
                point_index = k
                temp_lane_line_point = lanes_test[lane_of_int].points_with_angles[k][0:2]
                # print("temp_lane_line_point: " + str(temp_lane_line_point))
                # canvas.create_oval(temp_lane_line_point[0] - 2, temp_lane_line_point[1] - 2,temp_lane_line_point[0] + 2,temp_lane_line_point[1] + 2, fill = 'yellow')
                # tk.update()
                dist_to_point = math.sqrt(((temp_lane_line_point[1] - point_of_intersection[1])**2) + ((temp_lane_line_point[0] - point_of_intersection[0])**2))
                temp_dist_lane_forward_points_lanes_common.append([point_index,dist_to_point])
                # print("temp_dist_lane_forward_points_lanes_common: " + str(temp_dist_lane_forward_points_lanes_common))
                # cars[car_id].dist_lane_forward_points_1.append([lane_of_int,line_of_int,dist_to_point])
            # print("temp_dist_lane_forward_points_2: " + str(temp_dist_lane_forward_points_lanes_common))
            cars[car_id].dist_lane_forward_points_lanes_common.append(temp_dist_lane_forward_points_lanes_common)
def find_intersection_point_between_lines(line_1,line_2):       # ([[line_1_point_1_x,line_1_point_1_y],[line_1_point_2_x,line_1_point_2_y]],[[line_2_point_1_x,line_2_point_1_y],[line_2_point_2_x,line_2_point_2_y]]):
    # next_lane_first_point = lanes_test[j].points[0][0:2]
    # next_lane_second_point = lanes_test[j].points[1][0:2]
    # next_lane_points = [next_lane_first_point,next_lane_second_point]
    # print("j: " + str(j) + " next_lane_points: " + str(next_lane_points))
    # line_1 = [[line_1_point_1_x,line_1_point_1_y],[line_1_point_2_x,line_1_point_2_y]]
    # line_2 = [[line_2_point_1_x,line_2_point_1_y],[line_2_point_2_x,line_2_point_2_y]]

    xdiff = (line_1[0][0] - line_1[1][0], line_2[0][0] - line_2[1][0])
    ydiff = (line_1[0][1] - line_1[1][1], line_2[0][1] - line_2[1][1])

    # xdiff = (lane_points[0][0] - lane_points[1][0], next_lane_points[0][0] - next_lane_points[1][0])
    # ydiff = (lane_points[0][1] - lane_points[1][1], next_lane_points[0][1] - next_lane_points[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        intersection_cross = 0 # so do not cross, could be straight ahead or parallel
        # x = next_lane_first_point[0]
        # y = next_lane_first_point[1]
        # canvas.create_oval((x + 2),(y + 2),(x - 2),(y -2))
        # lanes_test[i].next_lanes_intersection.append([j,x,y])
       # raise Exception('lines do not intersect')
    else:
        # d = (det(*lane_points), det(*next_lane_points))
        d = (det(*line_1), det(*line_2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        x_round = round(x)
        y_round = round(y)
        intersection_cross = 1 # so do cross
        # canvas.create_oval((x + 2),(y + 2),(x - 2),(y -2))
        point_of_intersection = [x,y]
        # lanes_test[i].next_lanes_intersection.append([j,x,y])
        return point_of_intersection
############################

### GA function ---- OBVIOUS DETAIL HERE ####################################################################
def GA_as_function(juncs_test,lanes_test,junc_id):
    def create_initial_population(num_individuals,individ_options,individ_store,population,max_time,light_time_options,junc_id):
        #### create initial population
        for i in range(num_individuals):
            total_time = 0
            accepted = 0
            while accepted == 0:
                total_time = 0
                individ_store = []
                for j in range(len(juncs_test[junc_id].light_lanes_at_junc)):
                    # random_temp = random.uniform(0,30)
                    random_temp = random.randint(0,max_time) # 0 and 30 included
                    random_temp = random.choice(light_time_options)
                    individ_store.append(random_temp)
                total_time = sum(individ_store)
                if total_time <= max_time:
                    accepted = 1
            population.append(individ_store)
    def fitness_test_to_score_individuals(population_wait_time_reduction,population_wait_time_reduction_score,population,lanes_test,junc_id):
        for i in range(len(population)):
            individual_temp = population[i]
            junc_wait_time_reduction = 0
            individual_wait_time_reduction = []
            # for j in range(len(individual_temp)):
            # print("juncs[junc_id].lanes_at_junc: " + str(juncs[junc_id].lanes_at_junc))
            # for j in range(len(juncs_test[junc_id].lanes_at_junc)):
            for j in range(len(juncs_test[junc_id].light_lanes_at_junc)):
                time_green_temp = individual_temp[j]
                # print("time_green_temp: " + str(time_green_temp))
                lanes_controlled_by_light = juncs_test[junc_id].same_light_lanes_link[j]
                cars_id_to_leave_controlled_lane = []
                if type(lanes_controlled_by_light) is list:
                    # need to loop thorugh all lanes at this light to find sumg_time_in_lane for this light
                    cars_id_to_leave_lane_wait_time_sum = 0
                    lane_wait_time_reduction = 0
                    num_lanes_controlled_by_light = len(lanes_controlled_by_light)
                    num_cars_to_leave_lanes = int(time_green_temp/3) * num_lanes_controlled_by_light
                    num_cars_in_lanes_controlled = 0
                    # if junc_id == 9:
                    #     print("lanes_controlled_by_light: " + str(lanes_controlled_by_light))
                    #     print("num_cars_to_leave_lanes: " + str(num_cars_to_leave_lanes))
                    for t in range(len(lanes_controlled_by_light)):
                        # lane_of_int = lanes_controlled_by_light[t]
                        lane_of_int = lanes_controlled_by_light[t]
                        num_cars_in_lanes_controlled += len(lanes_test[lane_of_int].g_cars_in_lane_id)
                        # if junc_id == 9:
                        #     print("num_cars_in_lanes_controlled: " + str(num_cars_in_lanes_controlled))
                        if num_cars_to_leave_lanes > num_cars_in_lanes_controlled: # obviously the maximum number of cars that can leave a lane is equal to the number of cars in the lane
                            num_cars_to_leave_lanes = num_cars_in_lanes_controlled
                            # print("num_cars_to_leave_lane: " + str(num_cars_to_leave_lane))
                        # if junc_id == 9:
                        #     print("num_cars_to_leave_lanes: " + str(num_cars_to_leave_lanes))
                        cars_id_to_leave_controlled_lane = cars_id_to_leave_controlled_lane + lanes_test[lane_of_int].g_cars_in_lane_id[0:num_cars_to_leave_lanes] #####
                        # if junc_id == 9:
                        #     print("cars_id_to_leave_controlled_lane: " + str(cars_id_to_leave_controlled_lane))
                else:
                    lane_of_int = juncs_test[junc_id].lanes_at_junc[j]
                    lane_of_int = lanes_controlled_by_light
                    # print("time_green_temp: " + str(time_green_temp) + " lane_of_int: " + str(lane_of_int))
                    cars_id_to_leave_lane_wait_time_sum = 0
                    lane_wait_time_reduction = 0
                    num_cars_to_leave_per_lane = int(time_green_temp/3) # assumed cars able to leave a lane at a rate of 1 per every 3 seconds
                    num_cars_in_lanes_controlled = len(lanes_test[lane_of_int].g_cars_in_lane_id)
                    # print("num_cars_in_lane: " + str(num_cars_in_lane))
                    if num_cars_to_leave_per_lane > num_cars_in_lanes_controlled: # obviously the maximum number of cars that can leave a lane is equal to the number of cars in the lane
                        num_cars_to_leave_per_lane = num_cars_in_lanes_controlled
                        # print("num_cars_to_leave_lane: " + str(num_cars_to_leave_lane))
                    cars_id_to_leave_controlled_lane = lanes_test[lane_of_int].g_cars_in_lane_id[0:num_cars_to_leave_per_lane]
                    # print("cars_id_to_leave_lane: " + str(cars_id_to_leave_lane))
                    # now sum up the wait times of these cars
                for k in cars_id_to_leave_controlled_lane:
                    cars_id_to_leave_lane_wait_time_sum += cars[k].time_in_g_lane#cars[k].wait_time
                    # print("in GA time_in_g_lane: " + str(cars[k].time_in_g_lane))
                # print("cars_id_to_leave_lane_wait_time_sum: " + str(cars_id_to_leave_lane_wait_time_sum))
                lane_wait_time_reduction = cars_id_to_leave_lane_wait_time_sum
                individual_wait_time_reduction.append(lane_wait_time_reduction)
            individual_wait_time_reduction_score = sum(individual_wait_time_reduction)
            population_wait_time_reduction_score.append(individual_wait_time_reduction_score)
            # print("population_wait_time_reduction_score: " + str(population_wait_time_reduction_score))
            population_wait_time_reduction.append(individual_wait_time_reduction)
            # print("population_wait_time_reduction: " + str(population_wait_time_reduction))

        # print("population_wait_time_reduction: " + str(population_wait_time_reduction))
        # print("population_wait_time_reduction_score: " + str(population_wait_time_reduction_score))
        # print("best score: " + str(max(population_wait_time_reduction_score)))
        index_best = population_wait_time_reduction_score.index(max(population_wait_time_reduction_score))
        # print("best individual: " + str(population[index_best]))
    def creation_of_parents(parents, num_parents,population_wait_time_reduction_score,population,population_individuals_total_light_time,individuals_ordered):
        for i in range(len(population)):
            sum_light_time_temp = sum(population[i])
            population_individuals_total_light_time.append(sum_light_time_temp)

        # select individuals to become paretns based on their score
        population_wait_time_reduction_score_sorted = population_wait_time_reduction_score[:]
        population_wait_time_reduction_score_with_ids = [] # [individual_id,junc_wait_time_reduction_score,total_light_time]
        for i in range(len(population_wait_time_reduction_score)): # with id number
            population_wait_time_reduction_score_with_ids.append([i,population_wait_time_reduction_score[i],population_individuals_total_light_time[i]])
        # print("population_wait_time_reduction_score_with_ids: " + str(population_wait_time_reduction_score_with_ids))
        for i in range(len(population_wait_time_reduction_score_with_ids)):
            # order them by highest score first
            # print("before population_wait_time_reduction_score_sorted: " + str(population_wait_time_reduction_score_sorted))
            # population_wait_time_reduction_score_sorted = sorted(population_wait_time_reduction_score, reverse=True)
            population_wait_time_reduction_score_sorted_with_ids = sorted(population_wait_time_reduction_score_with_ids, key = lambda x: x[1], reverse = True)
            # print("after population_wait_time_reduction_score_sorted_with_ids: " + str(population_wait_time_reduction_score_sorted_with_ids))
            # input("gefnjfer")

        # then if highest score is the same then sub order by total time green (light_times)
        # find individuals with the highest score and sort them by
        # individuals_ordered = []
        population_wait_time_reduction_score_temp = population_wait_time_reduction_score[:]
        population_wait_time_reduction_score_temp_2 = population_wait_time_reduction_score_temp[:]
        population_wait_time_reduction_score_sorted_with_ids_temp = population_wait_time_reduction_score_sorted_with_ids[:]
        # for i in range(len(population_wait_time_reduction_score_sorted_with_ids)):
        truth_checker = 1
        while truth_checker == 1:
            # print("len: " + str(len(population_wait_time_reduction_score_temp)) + " population_wait_time_reduction_score_temp: " + str(population_wait_time_reduction_score_temp))
            population_wait_time_reduction_score_temp = population_wait_time_reduction_score_temp_2[:]
            # print("len: " + str(len(population_wait_time_reduction_score_temp)) + " population_wait_time_reduction_score_temp: " + str(population_wait_time_reduction_score_temp))
            population_wait_time_reduction_score_temp_2 = []
            if len(population_wait_time_reduction_score_temp) <= 0 :
                truth_checker = 0
            else:
                highest_score = max(population_wait_time_reduction_score_temp)
                # print("highest_score: " + str(highest_score))
                highest_score_individual_temp = []
                # print("len: " + str(len(population_wait_time_reduction_score_sorted_with_ids_temp)))
                # print("population_wait_time_reduction_score_sorted_with_ids_temp: " + str(population_wait_time_reduction_score_sorted_with_ids_temp))
                for j in range(len(population_wait_time_reduction_score_sorted_with_ids_temp)):
                    if population_wait_time_reduction_score_sorted_with_ids_temp[j][1] == highest_score:
                        highest_score_individual_temp.append(population_wait_time_reduction_score_sorted_with_ids[j])
                        # individual_highest_score = population_wait_time_reduction_score_sorted_with_ids.index(highest_score)
                # print("highest_score_individual_temp: " + str(highest_score_individual_temp))
                # order highest_score_individual_temp by the light_time
                highest_score_individual_temp = sorted(highest_score_individual_temp, key = lambda x: x[2])
                # print("sorted_highest_score_individual_temp: " + str(highest_score_individual_temp))
                for k in range(len(highest_score_individual_temp)):
                    individuals_ordered.append(highest_score_individual_temp[k])
                    # population_wait_time_reduction_score_sorted_with_ids_temp.remove(highest_score_individual_temp[k])
                for f in range(len(population_wait_time_reduction_score_temp)):
                    if population_wait_time_reduction_score_temp[f] != highest_score:
                        population_wait_time_reduction_score_temp_2.append(population_wait_time_reduction_score_temp[f])
                # print("individuals_ordered: " + str(individuals_ordered))
                # print("population_wait_time_reduction_score_sorted_with_ids: " + str(population_wait_time_reduction_score_sorted_with_ids))
                # print("len: " + str(len(population_wait_time_reduction_score_sorted_with_ids_temp)))
                # print("population_wait_time_reduction_score_sorted_with_ids_temp: " + str(population_wait_time_reduction_score_sorted_with_ids_temp))

                # input("gefnjfer")
        # print("individuals_ordered: " + str(individuals_ordered))
        # input("end section")


        parent_index_temp = []
        for i in range(num_parents):
            # pick the best number of individuals from the ordered list in individuals_ordered
            parent_index = individuals_ordered[i][0]
            # print("parent_selected: " + str(population[parent_index]))
            parents.append(population[parent_index])
    def create_new_offspring(offspring,num_new_offspring,num_individuals,crossover_point,parents,max_time):
        # print("parents_here: " + str(parents))
        # print("crossover_point: " + str(crossover_point))
        k = 0
        parent_1_options = parents[:]
        for i in range(num_new_offspring):
            # randomly pick a two parents, cannot pick the same parent twice
            # parent_1 = parent_1_options[0] # should randomly pick the parents NOT [0] pick the first one everytime
            parent_1 = random.choice(parent_1_options)
            # parent_1_options.remove(parent_1)
            accepted = 0
            parents_attempted = []
            parent_2_options = parents[:]
            parent_2_options.remove(parent_1)
            # should randomise the order of the parents in parent_2_options
            random.shuffle(parent_2_options)
            j = 0
            while j < len(parent_2_options):
                parent_2 = parent_2_options[j]
                offspring_half_1 = parent_1[0:crossover_point]
                offspring_half_2 = parent_2[crossover_point:]
                offspring_temp = offspring_half_1 + offspring_half_2
                offspring_use = []
                # check sum of offspring_temp is less than 30 seconds
                sum_check = sum(offspring_temp)
                if (sum_check <= max_time) and (len(offspring_use) == 0):
                    # accepted = 1
                    offspring_use = offspring_temp
                if (j == len(parent_2_options) - 1) and (len(offspring_use) == 0): # ie. the last loop and still no suitable value for offspring_use found
                    offspring_use = parent_1
                j += 1
            offspring.append(offspring_use)
    def add_mutaution_to_offspring(offspring,junc_id,max_time):
        # now add mutations to the offspring, add a mutaution to the first index of each offspring
        for i in range(len(offspring)):
            accepted = 0
            while accepted == 0:
                # num_lanes_at_junc = len(juncs_test[junc_id].lanes_at_junc)
                num_lanes_at_junc = len(juncs_test[junc_id].light_lanes_at_junc)
                # end_lane_options = num_lanes_at_junc - 1
                # lane_options = [0,1,2,3]
                lane_options = list(range(0, num_lanes_at_junc))
                # lane_options = juncs[junc_id].lanes_at_junc
                lane_1 = random.choice(lane_options)
                lane_2_options = lane_options[:]
                lane_2_options.remove(lane_1)
                lane_2 = random.choice(lane_2_options)
                # random_value_1 = random.uniform(-1,7) # mutation will change the value by an amount between -1 and 2
                # random_value_2 = random.uniform(-1,7) # mutation will change the value by an amount between -1 and 2
                # random_value_1 = random.randint(-1,7)
                # random_value_2 = random.randint(-1,7)
                random_value_1 = random.choice([-6,-3,0,3,6,9])
                random_value_2 = random.choice([-6,-3,0,3,6,9])
                # print("random_value: " + str(random_value))
                if (offspring[i][lane_1] + random_value_1) < 0:
                    amount_below_zero = (offspring[i][lane_1] + random_value_1)
                    amount_below_zero_abs = abs(amount_below_zero)
                    # print("before random_value_1: " + str(random_value_1))
                    # print("amount_below_zero: " + str(amount_below_zero))
                    # print("amount_below_zero_abs: " + str(amount_below_zero_abs))
                    # print("offspring[i][lane_1]: " + str(offspring[i][lane_1]))
                    if amount_below_zero_abs <= offspring[i][lane_1]:
                        random_value_1 -=  6 #3
                        # set the random value to be the negative of the offspring_value
                        # random_value_1 = - offspring[i][lane_1]
                    else:
                        random_value_1 = 0
                    # print("after random_value_1: " + str(random_value_1))
                    # input("[aused]")

                if (offspring[i][lane_2] + random_value_2) < 0:
                    amount_below_zero = (offspring[i][lane_2] + random_value_2)
                    amount_below_zero_abs = abs(amount_below_zero)
                    # print("amount_below_zero: " + str(amount_below_zero))
                    # print("amount_below_zero_abs: " + str(amount_below_zero_abs))
                    # print("offspring[i][lane_2]: " + str(offspring[i][lane_2]))
                    if amount_below_zero_abs <= offspring[i][lane_2]:
                        random_value_2 -= 6#3
                        # set the random value to be the negative of the offspring_value
                        # random_value_2 = - offspring[i][lane_1]

                    else:
                        random_value_2 = 0

                ############################################
                # if (offspring[i][lane_1] + random_value_1) < 0:
                #     random_value_diff = random_value_1 + 3
                #     if (random_value_diff < 0) and (offspring[i][lane_1] > 0):
                #         random_value_1 = 0
                #     else:
                #         random_value_1 = 0
                #     # random_value_1 = 0
                #     # print("lane_1: " + str(offspring[i][lane_1]) + " rv_1: " + str(random_value_1))
                # if (offspring[i][lane_2] + random_value_2) < 0:
                #     random_value_diff = random_value_2 + 3
                #     if (random_value_diff < 0) and (offspring[i][lane_1] > 0):
                #         random_value_2 = 0
                #     else:
                #         random_value_2 = 0
                    # random_value_2 = 0
                    # print("lane_2: " + str(offspring[i][lane_2]) + " rv_1: " + str(random_value_2))
                ###########################################
                # now check to make sure the sum time for the lights at the junciton remains less than 30 seconds
                sum_check = sum(offspring[i]) + random_value_1 + random_value_2
                # print("sum_check: " + str(sum_check))
                if sum_check <= max_time:
                    accepted = 1
                    offspring[i][lane_1] += random_value_1
                    offspring[i][lane_2] += random_value_2
    def add_best_parents_to_offspring(parents,offspring,num_parents_carried_on,individuals_ordered,population):
        # now add the two best parents to the offsprings
        for i in range(num_parents_carried_on):
            # offspring.append(parents[i])
            best_parent_index = individuals_ordered[i][0]
            offspring.append(population[best_parent_index])
        # now set the offspring to be the individuals in the population

    # for junc_id in range(1): # range(len(juncs_test):
    test_scores_all_iter_limits = []
    test_scores_avg_all_iter_limits = []
    iter_limit_options = [100] #[75] #[1,2]#,3,5,10]#,25,50] # ,100,200]
    for iter_lim_opt in iter_limit_options:
        sample_num = 0
        num_samples_limit = 1 # 10
        test_score = []
        max_time = (len(juncs_test[junc_id].lanes_at_junc)) * 15
        # max_time = (len(juncs_test[junc_id].lanes_at_junc)) * 6
        # max_time = (len(juncs_test[junc_id].light_lanes_at_junc)) * 3
        multiples_in_max_time = int(max_time / 3)
        # print("multiples_in_max_time: " + str(multiples_in_max_time))
        light_time_options = []
        for p in range(multiples_in_max_time + 1):
            light_time_options.append(p * 3)
            # light_time_options = [0,3,6,9,12,15,18,21,24,27,30]
        while sample_num < num_samples_limit:
            num_individuals = 25 # 10  # increasing this is most expensive in computational time
            individ_options = []
            individ_store = []
            population = []
            # max_time = (len(juncs_test[junc_id].lanes_at_junc)) * 6
            # print("population: " + str(population))
            create_initial_population(num_individuals,individ_options,individ_store,population,max_time,light_time_options,junc_id)
            # print("population: " + str(population))
            iter = 0
            iter_limit = iter_lim_opt
            end_iter = iter_limit - 1
            if junc_id == 19:
                for lane in juncs_test[junc_id].light_lanes_at_junc:
                    print("lane_id: " + str(lane) + " g_cars_in_lane_id: " + str(lanes_test[lane].g_cars_in_lane_id))
                    # num_cars_in_lanes_controlled = len(lanes_test[lane_of_int].g_cars_in_lane_id)
                    for cars_temp in lanes_test[lane].g_cars_in_lane_id:
                        print("car_id: " + str(cars_temp) + " time_in_g_lane: " + str(cars[cars_temp].time_in_g_lane))

            # if junc_id == 19:
            #     input("         paused here")
            while iter < iter_limit:
                # print("iter: " + str(iter))
                #### conduct fitness test to score how amny cars will be able to leave each lane (consider how many are actullay in the lane) and then the change in wait time
                population_wait_time_reduction = []
                population_wait_time_reduction_score = []
                fitness_test_to_score_individuals(population_wait_time_reduction,population_wait_time_reduction_score,population,lanes_test,junc_id)
                if iter == end_iter:
                    t = 0
                    # print("population_at_end: "+ str(population))
                    best_score_end = max(population_wait_time_reduction_score)
                    index_best = population_wait_time_reduction_score.index(best_score_end)
                    winner = population[index_best]
                    test_score.append(best_score_end)
                    # print("winner: " + str(winner))
                    # juncs_test[junc_id].light_times = winner
                    juncs_test[junc_id].light_times = []
                    for k in range(len(winner)):
                        # juncs_test[junc_id].light_times.append([juncs_test[junc_id].lanes_at_junc[k],winner[k]])
                        # juncs_test[junc_id].light_times.append([juncs_test[junc_id].light_lanes_at_junc[k],winner[k]])
                        juncs_test[junc_id].light_times.append([juncs_test[junc_id].same_light_lanes_link[k],winner[k]])
                    # print("junc_id: " + str(junc_id) + " light_times: " + str(juncs_test[junc_id].light_times) + " sum: " + str(sum(juncs_test[junc_id].light_times)) + " best_score_end: " + str(best_score_end))
                else:
                    ### now assess the individual_wait_time_reduction array to find individuals to take forward in the mating process
                    parents = []
                    # num_parents = int(len(population)/2)
                    num_parents = int(len(population)/15) # 10
                    if num_parents < 3:
                        num_parents = 3
                    # num_parents = 3
                    population_individuals_total_light_time = []
                    individuals_ordered = []
                    creation_of_parents(parents, num_parents,population_wait_time_reduction_score,population,population_individuals_total_light_time,individuals_ordered)
                    # print("parents: " + str(parents))
                    num_parents_carried_on = int(len(population)/10) # was 10
                    if num_parents_carried_on < 2:
                        num_parents_carried_on = 2
                    num_new_offspring = num_individuals - num_parents_carried_on # as the two best parents will automatically be carried forward to the next generation
                    offspring = []
                    crossover_point = int(len(population[0])/2) # the point in the junc light times options that the will split and join from either parent
                    create_new_offspring(offspring,num_new_offspring,num_individuals,crossover_point,parents,max_time)
                    # print("population: " + str(population))
                    # print("individuals_ordered: " + str(individuals_ordered))
                    # print("offspring raw: " + str(offspring))
                    add_mutaution_to_offspring(offspring, junc_id,max_time)
                    add_best_parents_to_offspring(parents,offspring,num_parents_carried_on,individuals_ordered,population)
                    # print("population: " + str(population))
                    # print("individuals_ordered: " + str(individuals_ordered))
                    # print("offspring mutuated: " + str(offspring))
                    # input("wait here")
                    population = offspring
                iter += 1
            sample_num +=1
        # print("test_score: " + str(test_score))
        avg_test_score = mean(test_score)
        test_score_end = test_score
        # print("avg test_score: " + str(avg_test_score))
        test_scores_all_iter_limits.append([[num_individuals,iter_lim_opt],test_score])
        # test_scores_all_iter_limits.append(test_score)
        # test_scores_avg_all_iter_limits.append(avg_test_score)
        if junc_id == 19:
            print("test_score_end: " + str(test_score_end))
            print("test_scores: " + str(test_scores_all_iter_limits))
            # print("test_score_avg: " + str(test_scores_avg_all_iter_limits))
            print("juncs_test[junc_id].light_times: " + str(juncs_test[junc_id].light_times))
            print("lanes_at_junc: " + str(juncs_test[junc_id].lanes_at_junc))
            print("light_lanes_at_junc: " + str(juncs_test[junc_id].light_lanes_at_junc))
### PA function
def PA_function(juncs_test,lanes_test,junc_id,lane_selected):
    # for the lane_selected find the g_cars_in_lane_id
    # and use the probabilty for actual cars to estimate the actual number of car in the lane and then mulitple this number by 3 seconds to give the time_green
    # prob = [[[0, 1866, 0.6817683595177201], [1, 512, 0.18706613080014614], [2, 216, 0.07891852393131166], [3, 119, 0.043478260869565216], [4, 16, 0.005845816587504567], [5, 8, 0.0029229082937522835]], [[0, 516, 0.3383606557377049], [1, 600, 0.39344262295081966], [2, 291, 0.19081967213114753], [3, 82, 0.05377049180327869], [4, 16, 0.010491803278688525], [5, 11, 0.007213114754098361], [6, 5, 0.003278688524590164], [7, 4, 0.002622950819672131]], [[0, 199, 0.21868131868131868], [1, 239, 0.26263736263736265], [2, 342, 0.3758241758241758], [3, 113, 0.12417582417582418], [4, 15, 0.016483516483516484], [5, 2, 0.002197802197802198]], [[0, 288, 0.2987551867219917], [1, 148, 0.15352697095435686], [2, 122, 0.12655601659751037], [3, 298, 0.3091286307053942], [4, 99, 0.10269709543568464], [5, 9, 0.00933609958506224]], [[0, 144, 0.20869565217391303], [1, 59, 0.08550724637681159], [2, 72, 0.10434782608695652], [3, 115, 0.16666666666666666], [4, 186, 0.26956521739130435], [5, 85, 0.12318840579710146], [6, 15, 0.021739130434782608], [7, 14, 0.020289855072463767]], [[0, 63, 0.22661870503597123], [1, 23, 0.08273381294964029], [2, 36, 0.12949640287769784], [3, 12, 0.04316546762589928], [4, 31, 0.11151079136690648], [5, 81, 0.29136690647482016], [6, 18, 0.06474820143884892], [7, 14, 0.050359712230215826]], [[0, 0, 0.0], [1, 0, 0.0], [2, 0, 0.0], [3, 0, 0.0], [4, 1, 0.029411764705882353], [5, 10, 0.29411764705882354], [6, 18, 0.5294117647058824], [7, 5, 0.14705882352941177]], [[0, 0, 0.0], [1, 0, 0.0], [2, 0, 0.0], [3, 0, 0.0], [4, 0, 0.0], [5, 0, 0.0], [6, 1, 1.0]]]
    # prob_scaled = [[0, 6817.683595177201, 1, 1870.6613080014615, 2, 789.1852393131165, 3, 434.7826086956522, 4, 58.45816587504567, 5, 29.229082937522836], [0, 3383.6065573770493, 1, 3934.4262295081967, 2, 1908.1967213114754, 3, 537.7049180327868, 4, 104.91803278688525, 5, 72.1311475409836, 6, 32.78688524590164, 7, 26.229508196721312], [0, 2186.813186813187, 1, 2626.3736263736264, 2, 3758.2417582417584, 3, 1241.7582417582419, 4, 164.83516483516485, 5, 21.978021978021978], [0, 2987.551867219917, 1, 1535.2697095435685, 2, 1265.5601659751037, 3, 3091.286307053942, 4, 1026.9709543568465, 5, 93.3609958506224], [0, 2086.9565217391305, 1, 855.0724637681159, 2, 1043.4782608695652, 3, 1666.6666666666665, 4, 2695.6521739130435, 5, 1231.8840579710145, 6, 217.3913043478261, 7, 202.89855072463766], [0, 2266.1870503597124, 1, 827.3381294964029, 2, 1294.9640287769785, 3, 431.6546762589928, 4, 1115.1079136690648, 5, 2913.6690647482014, 6, 647.4820143884892, 7, 503.59712230215825], [0, 0.0, 1, 0.0, 2, 0.0, 3, 0.0, 4, 294.11764705882354, 5, 2941.1764705882356, 6, 5294.117647058823, 7, 1470.5882352941178], [0, 0.0, 1, 0.0, 2, 0.0, 3, 0.0, 4, 0.0, 5, 0.0, 6, 10000.0]]
    prob_scaled = [[[0, 1, 2, 3, 4, 5], [682, 187, 79, 43, 6, 3]], [[0, 1, 2, 3, 4, 5, 6, 7], [338, 393, 191, 54, 10, 7, 3, 3]], [[0, 1, 2, 3, 4, 5], [219, 263, 376, 124, 16, 2]], [[0, 1, 2, 3, 4, 5], [299, 154, 127, 309, 103, 9]], [[0, 1, 2, 3, 4, 5, 6, 7], [209, 86, 104, 167, 270, 123, 22, 20]], [[0, 1, 2, 3, 4, 5, 6, 7], [227, 83, 129, 43, 112, 291, 65, 50]], [[0, 1, 2, 3, 4, 5, 6, 7], [0, 0, 0, 0, 29, 294, 529, 147]], [[0, 1, 2, 3, 4, 5, 6], [0, 0, 0, 0, 0, 0, 1000]]]

    g_num_cars_in_lane = len(lanes_test[lane_selected].g_cars_in_lane_id)
    if g_num_cars_in_lane >= len(prob_scaled):
        prob_guess_num_cars = g_num_cars_in_lane
    else:
        # print("prob_scaled_0_1: " + str(prob_scaled[0][1]))
        probability_ladder = []
        for i in range(len(prob_scaled[g_num_cars_in_lane][1])):
            prob_occurence = prob_scaled[g_num_cars_in_lane][1][i]
            for j in range(prob_occurence):
                probability_ladder.append(prob_scaled[g_num_cars_in_lane][0][i])
        # now pick one option from the probability ladder
        prob_guess_num_cars = random.choice(probability_ladder)
    # print("prob_guess_num_cars: " + str(prob_guess_num_cars))

    lanes_test[lane_selected].time_green = prob_guess_num_cars * 3
    if junc_id == 0:
        print("lane_selected: " + str(lane_selected) + " g_num_cars_in_lane: " + str(g_num_cars_in_lane) + " prob_guess_num_cars: " + str(prob_guess_num_cars) + " actual_num_cars: " + str(len(lanes_test[lane_selected].cars_in_lane_id)))
        print("time_green: " + str(lanes_test[lane_selected].time_green))
#####

###### Create threads , DETAIL STORED IN THE THREADS  ####################################################
class SetTimeLights(Thread):
    def run(self):
        while running_check == 1:
            # time.sleep(time_between_loops)
            time.sleep(1)
            for i in range(len(juncs_test)):
                if juncs_test[i].ready_for_green == 1: # junction ready for next green light
                    # print("junc: " + str(i) + " same_light_lanes_link: " + str(juncs_test[i].same_light_lanes_link) + " green_lanes_at_junc: " + str(juncs_test[i].green_lanes_at_junc))
                    # green_lane_index = juncs_test[i].same_light_lanes_link.index(juncs_test[i].green_lanes_at_junc)
                    # # green_lane_index = juncs_test[i].light_lanes_at_junc.index(juncs_test[i].green_lanes_at_junc)
                    # # green_lane_index = juncs_test[i].lanes_at_junc.index(juncs_test[i].green_lanes_at_junc)
                    # next_green_lane_index = green_lane_index + 1
                    # if next_green_lane_index == len(juncs_test[i].light_lanes_at_junc):
                    #     next_green_lane_index = 0
                    # next_green_lane = juncs_test[i].same_light_lanes_link[next_green_lane_index]
                    # print("time_between_loops: " + str(time_between_loops))
                    ########################

                    orien_of_next_green_lane = juncs_test[i].green_lane_at_junc_orien + 1
                    if orien_of_next_green_lane > 3:
                        orien_of_next_green_lane = 0
                    for k in juncs_test[i].light_lanes_at_junc:
                        if lanes_test[k].orien == orien_of_next_green_lane:
                            next_green_lane = k
                            juncs_test[i].green_lane_at_junc_orien = orien_of_next_green_lane
                    #########################

                    # next_green_lane = juncs_test[i].same_light_lanes_link[next_green_lane_index]
                    if type(next_green_lane) == int:
                        # ie. only one lane from this junction
                        lane_selected = next_green_lane
                        lanes_test[lane_selected].green_light = 1 # acts as indicator that this lane now has a green light
                        lanes_test[lane_selected].time_green = 30 #6


                    else:
                        # more than one lane from this junction, thus is a list
                        for p in next_green_lane:
                            lane_selected = p
                            lanes_test[lane_selected].green_light = 1 # acts as indicator that this lane now has a green light
                            lanes_test[lane_selected].time_green = 30 #6
                    juncs_test[i].green_lanes_at_junc = next_green_lane
                    juncs_test[i].ready_for_green = 0 # green light lane allocaated to junction so turn off (set to 0) ready_for_green, this cycles thorugh the lights at a junction giving a set time to each
class Find_Lane_Car_Position(Thread):
    def run(self):
        time.sleep(0.5)
        running_timer = 1
        sampling_counter = 0
        time_tracker = 0
        system_check_counter = 0
        # cars[0].sampling_checker = 0
        print_checker = 0
        sample = 0
        running_check = 1
        while running_check == 1:
            if running_timer == 1:
                for i in cars_in_system:  #(38,39):  #(cars_in_system): #(0,1) check this
                # for i in cars_entered_system:
                    # if (i in cars_in_system) or (cars[i].g_lane != 9999):
                    if i in cars_exited_system:
                        cars[i].g_lane = 9999
                        cars[i].potential_lanes_1 = []
                        cars[i].potential_lanes_lines_1 = []
                        cars[i].potential_lanes_2 = []
                        cars[i].potential_lanes_lines_2 = []
                    else:
                        cars[i].g_lane = cars[i].current_lane

            running_timer = 0
            time_tracker += time_interval
            print_checker += time_interval
            # print("print_checker: " + str(print_checker))
            if print_checker >= 60:
                print_checker = 0
                # print("car_store: " + str(car_store))
                # for t in range(len(car_store)):
                #     print("cars[t].id: " + str(cars[t].id))
                #     print("cars[t].userID: "+ str(cars[t].userID) + " car_id: " + str(cars[t].id))
                #     print("cars[t].coord_tracker: " + str(cars[t].coord_tracker))
                #     print("g_lane_line_tracker: " + str(cars[t].g_lane_line_tracker))
                #     print("traffic_light_store: " + str(traffic_light_store))
                # for q in range(len(juncs_test)):
                #     print("junc_id: " + str(q)  + " light_change_history: " + str(juncs_test[q].light_change_history))
            if time_tracker >= sampling_time:
                time_tracker = 0
                running_timer = 1
                print("print_checker: " + str(print_checker))
            time.sleep(time_interval) # not for testing
time_between_loops = 1
class ExtractCarInfo(Thread):
    def run(self):
        while running_check == 1:
            # print("runnung")
            time.sleep(time_between_loops)
            # print(cars[21].g_wait_time)
            for i in cars_exited_system:
                if cars[i].g_lane != 9999:
                    cars[i].g_lane = 9999
                    lanes_test[cars[i].g_lane_temp].g_cars_in_lane_id.remove(cars[i].id)
            for i in cars_in_system:
                if (cars[i].g_lane != cars[i].g_lane_temp): #and (cars[i].g_lane_temp != 9999): # g_lane_temp holds the previous g_lane of car
                    if (cars[i].g_lane == 9999) and (cars[i].g_lane_temp != 9999):
                        lanes_test[cars[i].g_lane_temp].g_cars_in_lane_id.remove(cars[i].id)
                    elif (cars[i].g_lane == 9999) and (cars[i].g_lane_temp == 9999):
                        # do nothing
                        t = 0
                    elif (cars[i].g_lane != 9999) and (cars[i].g_lane_temp == 9999):
                        lanes_test[cars[i].g_lane].g_cars_in_lane_id.append(cars[i].id)  # update g_cars_in_lane_id
                    else:
                        # if cars[i].g_lane_temp in lanes_test[cars[i].g_lane_temp].g_cars_in_lane_i:
                        # print("i: " + str(i) + " g_lane: " + str(cars[i].g_lane))
                        lanes_test[cars[i].g_lane].g_cars_in_lane_id.append(cars[i].id)  # update g_cars_in_lane_id
                        lanes_test[cars[i].g_lane_temp].g_cars_in_lane_id.remove(cars[i].id)  # remove g_cars_in_lane_id for previous g_lane (g_lane_temp)
                    cars[i].g_lane_temp = cars[i].g_lane # update g_lane_temp
class FindWaitTimeForLanes(Thread):    ################ need to check all these loops give the desired answer
    def run(self):
        # time.sleep(2)
        while running_check == 1:
            time.sleep(time_between_loops)
            # print("junc2_wtt: " + str(juncs[2].g_junc_wait_time_total))
            # print("lane2_wtt: " + str(lanes[2].g_lane_wait_time_total))
            # find the wait times for each lane and junction
            for i in range(len(juncs_test)):
                juncs_test[i].g_junc_wait_time_total = 0
                for k in juncs_test[i].lanes_at_junc:
                    lanes_test[k].g_lane_wait_time_total = 0
                    # g_tot_lane_wait_time = 0
                    for s in lanes_test[k].g_cars_in_lane_id:
                        lanes_test[k].g_lane_wait_time_total += cars[s].g_wait_time
                    juncs_test[i].g_junc_wait_time_total += lanes_test[k].g_lane_wait_time_total
class FindGreenLightLanes(Thread): # this is the algo for assign green light to lanes based on weighted
    def run(self):
        while running_check == 1:
            time.sleep(time_between_loops)
            for i in range(len(juncs_test)):
                if juncs_test[i].ready_for_green == 1: # junction ready for next green light
                    lane_selection_options = []
                    for k in juncs_test[i].light_lanes_at_junc:
                        if juncs_test[i].g_junc_wait_time_total > 0: # need this if statement as can't divide by zero
                            lane_freq = math.ceil((lanes_test[k].g_lane_wait_time_total / juncs_test[i].g_junc_wait_time_total) * 12) # num_times_lane_will_feature_in_selection_matrix
                        else:
                            lane_freq = 0
                        if lane_freq < 2: # want each to lane in the junc to appear, as can't be cetain there isn't a car there
                            lane_freq = 2
                        for t in range(lane_freq - 1):
                            lane_selection_options.append(k)  # store the lane number as many times as its frequency, so if lane[1] had a lane_freq of 4 the number 1  will appear 4 times in lane_selection
                            # lane_selection_options.append(lanes_test[k].lane_id[0])  # store the lane number as many times as its frequency, so if lane[1] had a lane_freq of 4 the number 1  will appear 4 times in lane_selection
                    lane_selected = random.choice(lane_selection_options)
                    lanes_test[lane_selected].green_light = 1 # acts as indicator that this lane now has a green light
                    lanes_test[lane_selected].time_green = 3
                    if len(lanes_test[lane_selected].assoc_lanes) > 0:
                        for k in lanes_test[lane_selected].assoc_lanes:
                            t = 0
                            lanes_test[k].green_light = 1
                            lanes_test[k].time_green = 3
                    # turn_light_green(lane_selected)
                    juncs_test[i].ready_for_green = 0 # green light lane allocaated to junction so turn off (set to 0) ready_for_green
class Update_Light_Times_for_GA(Thread):
    def run(self):
        while running_check == 1:
            time.sleep(1)
            # check if any junction needs to find/update new juncs_test.light_times
            juncs_ready_for_new_light_times = []
            for i in range(len(juncs_test)):
                # if i == 0:
                # print("start juncs_ready_for_new_light_times_0: " + str(juncs_test[i].ready_for_new_light_times))
                # print("start juncs_ready_for_new_light_times: " + str(juncs_ready_for_new_light_times))
                if (juncs_test[i].ready_for_new_light_times == 1) and (juncs_test[i].junc_id not in juncs_ready_for_new_light_times):
                    if i == 0:
                        t = 0
                        # print("inside juncs_ready_for_new_light_times_0: " + str(juncs_test[i].ready_for_new_light_times))
                    juncs_ready_for_new_light_times.append(juncs_test[i].junc_id)
                    # set juncs_test[i].ready_for_new_light_times back to 0
                    juncs_test[i].ready_for_new_light_times = 0
                # print("start juncs_ready_for_new_light_times: " + str(juncs_ready_for_new_light_times))

            # print("juncs_ready_for_new_light_times: " + str(juncs_ready_for_new_light_times))
            # if 0 in juncs_ready_for_new_light_times:
                # print("inside juncs_ready_for_new_light_times: " + str(juncs_ready_for_new_light_times))
            for i in range(len(juncs_ready_for_new_light_times)):
                # pass this junc_id off to the GA function
                junc_id = juncs_ready_for_new_light_times[i]
                if junc_id == 9:
                    print("sent_to_GA_9: ")
                GA_as_function(juncs_test,lanes_test,junc_id)
class Monitor_and_Control_Lights_for_GA(Thread):
    # monitor and change the lights at a juncion depending on their .time_green, introduce the pause between the change, once cycle complete set junc.ready_for_new_light_times = 1
    def run(self):
        while running_check == 1:
            time.sleep(1)
            for junc_id in range(len(juncs_test)):
                # check if any junction needs to when junc_test[junc_id].ready_for_green == 1
                # last known lane to be green is juncs_test[p].lane_at_junc_green, find it's index in .lanes_at_junc and make the next lane (index + 1) green
                # if junc_id == 0:
                #     print("light_times: " + str(juncs_test[junc_id].light_times))
                #     print("ready_for_green: " + str(juncs_test[junc_id].ready_for_green))
                if juncs_test[junc_id].ready_for_green == 1:
                    # if junc_id == 9:
                    #     print("ready_for_green_9: " + str(juncs_test[junc_id].ready_for_green))
                    #     print("light_times_index_to_make_green_9: " + str(juncs_test[junc_id].light_times_index_to_make_green))
                    # set ready_for_green back to 0
                    # juncs_test[junc_id].ready_for_green = 0
                    # move to next light to turn green or at end of last light so update all junc.light_times by triggering the GA
                    # juncs_test[junc_id].light_times_index_to_make_green += 1 # this loops through the times in light_times and needs to set this back to zero at some point
                    # index_next_green_lane = juncs_test[junc_id].num_lanes_accounted_for_to_be_green # based on the
                    # index_next_green_lane_at_junc = juncs_test[junc_id].light_times[juncs_test[junc_id].light_times_index_to_make_green][0]
                    # juncs_test[junc_id].light_times_index_to_make_green += 1
                    # print("light_times_index_to_make_green: " + str(juncs_test[junc_id].light_times_index_to_make_green))
                    if juncs_test[junc_id].light_times_index_to_make_green >= len(juncs_test[junc_id].light_times):
                        # junc has cycled through all the lanes_at_junc so now set junc.ready_for_new_light_times = 1
                        juncs_test[junc_id].ready_for_new_light_times = 1
                        juncs_test[junc_id].light_times_index_to_make_green = 0
                        # if junc_id == 9:
                        #     print("ready_for_new_light_times_9: " + str(juncs_test[junc_id].ready_for_new_light_times))
                    else:
                        # print("check runngin")
                        # juncs_test[junc_id].ready_for_green = 0
                        # index_next_green_lane_at_junc = juncs_test[junc_id].light_times[juncs_test[junc_id].light_times_index_to_make_green][0]
                        # set the next lane in the order to go green, ie. the next_lane in .
                        next_lane_not_zero_time_green = 0
                        # juncs_test[junc_id].light_times_index_to_make_green += 1
                        while next_lane_not_zero_time_green == 0:
                            next_time_green = juncs_test[junc_id].light_times[juncs_test[junc_id].light_times_index_to_make_green][1]
                            if next_time_green <= 0: # lane has a zero time_green
                                # print("skipped")
                                juncs_test[junc_id].light_times_index_to_make_green += 1
                                if juncs_test[junc_id].light_times_index_to_make_green >= len(juncs_test[junc_id].light_times):
                                    # junc has cycled through all the lanes_at_junc so now set junc.ready_for_new_light_times = 1
                                    # print("need new light_times")
                                    juncs_test[junc_id].ready_for_new_light_times = 1
                                    juncs_test[junc_id].light_times_index_to_make_green = 0
                                    next_lane_not_zero_time_green = 1
                            else:
                                next_lanes_to_turn_green = juncs_test[junc_id].light_times[juncs_test[junc_id].light_times_index_to_make_green][0]
                                if type(next_lanes_to_turn_green) is list:
                                    for q in range(len(next_lanes_to_turn_green)):
                                        lane_to_turn_green = next_lanes_to_turn_green[q]
                                        lanes_test[lane_to_turn_green].green_light = 1
                                        lanes_test[lane_to_turn_green].time_green = juncs_test[junc_id].light_times[juncs_test[junc_id].light_times_index_to_make_green][1]
                                        # if junc_id == 9:
                                        #     print("lane_to_turn_green_9: " + str(lane_to_turn_green))
                                else:
                                    lane_to_turn_green = next_lanes_to_turn_green
                                    # print("lane_to_turn_green: " + str(lane_to_turn_green))
                                    lanes_test[lane_to_turn_green].green_light = 1
                                    lanes_test[lane_to_turn_green].time_green = juncs_test[junc_id].light_times[juncs_test[junc_id].light_times_index_to_make_green][1]
                                    # if junc_id == 9:
                                    #     print("lane_to_turn_green_9: " + str(lane_to_turn_green))
                                # print("lane_to_turn_green: " + str(lane_to_turn_green) + " time_green: " + str(lanes_test[lane_to_turn_green].time_green))
                                # juncs_test[junc_id].light_times_index_to_make_green += 1 # this loops through the times in light_times and needs to set this back to zero at some point
                                # set next_time_green to 1 so the loop can move on
                                next_lane_not_zero_time_green = 1
                                juncs_test[junc_id].ready_for_green = 0
                                juncs_test[junc_id].light_times_index_to_make_green += 1
class Monitor_and_Control_Lights_for_PA(Thread):
    # monitor and change the lights at a juncion depending on their .time_green, introduce the pause between the change, once cycle complete set junc.ready_for_new_light_times = 1
    def run(self):
        while running_check == 1:
            # time.sleep(time_between_loops)
            time.sleep(1)
            for i in range(len(juncs_test)):
                # while lanes_test[juncs_test[i].green_lanes_at_junc].time_green <= 0.9:
                if juncs_test[i].ready_for_green == 1: # junction ready for next green light
                    if i == 0:
                        print("lanes_test[juncs_test[i].green_lanes_at_junc].time_green: " + str(lanes_test[juncs_test[i].green_lanes_at_junc].time_green))
                    while lanes_test[juncs_test[i].green_lanes_at_junc].time_green <= 3:
                        ########################
                        orien_of_next_green_lane = juncs_test[i].green_lane_at_junc_orien + 1
                        if orien_of_next_green_lane > 3:
                            orien_of_next_green_lane = 0
                        for k in juncs_test[i].light_lanes_at_junc:
                            if lanes_test[k].orien == orien_of_next_green_lane:
                                next_green_lane = k
                                juncs_test[i].green_lane_at_junc_orien = orien_of_next_green_lane
                        #########################
                        if type(next_green_lane) == int:
                            # ie. only one lane from this junction
                            lane_selected = next_green_lane
                            # lanes_test[lane_selected].green_light = 1 # acts as indicator that this lane now has a green light
                            # now use the PA_function to determine the time_green for this lane
                            PA_function(juncs_test,lanes_test,i,lane_selected)


                            # lanes_test[lane_selected].time_green = 30 #6
                        # else:
                        #     # more than one lane from this junction, thus is a list
                        #     for p in next_green_lane:
                        #         lane_selected = p
                        #         lanes_test[lane_selected].green_light = 1 # acts as indicator that this lane now has a green light
                        #         lanes_test[lane_selected].time_green = 30 #6
                        juncs_test[i].green_lanes_at_junc = next_green_lane
                        # if lanes_test[next_green_lane].time_green >= 3:
                    lanes_test[lane_selected].green_light = 1
                    juncs_test[i].ready_for_green = 0 # green light lane allocaated to junction so turn off (set to 0) ready_for_green, this cycles thorugh the lights at a junction giving a set time to each
class Best_Possible_Light_Times(Thread):
    def run(self):
        while running_check == 1:
            time.sleep(1)
            # check if any junction needs to find/update new juncs_test.light_times
            juncs_ready_for_new_light_times = []
            for i in range(len(juncs_test)):
                # if i == 0:
                # print("start juncs_ready_for_new_light_times_0: " + str(juncs_test[i].ready_for_new_light_times))
                # print("start juncs_ready_for_new_light_times: " + str(juncs_ready_for_new_light_times))
                if (juncs_test[i].ready_for_new_light_times == 1) and (juncs_test[i].junc_id not in juncs_ready_for_new_light_times):
                    if i == 0:
                        t = 0
                        # print("inside juncs_ready_for_new_light_times_0: " + str(juncs_test[i].ready_for_new_light_times))
                    juncs_ready_for_new_light_times.append(juncs_test[i].junc_id)
                    # set juncs_test[i].ready_for_new_light_times back to 0
                    juncs_test[i].ready_for_new_light_times = 0
                # print("start juncs_ready_for_new_light_times: " + str(juncs_ready_for_new_light_times))

            # print("juncs_ready_for_new_light_times: " + str(juncs_ready_for_new_light_times))
            # if 0 in juncs_ready_for_new_light_times:
                # print("inside juncs_ready_for_new_light_times: " + str(juncs_ready_for_new_light_times))
            # print("     juncs_ready_for_new_light_times: " + str(juncs_ready_for_new_light_times))
            for i in juncs_ready_for_new_light_times:
                juncs_test[i].light_times = []
                # best light_times found from the cars_in_lane_id
                for q in juncs_test[i].light_lanes_at_junc:
                    num_cars_in_lane_temp = len(lanes_test[q].cars_in_lane_id)
                    time_green_temp = num_cars_in_lane_temp * 3
                    juncs_test[i].light_times.append([q,time_green_temp])
                    if i == 0:
                        print("         num_cars_in_lane_temp: " + str(num_cars_in_lane_temp))
                if i == 0:
                    print("         light_times: " + str(juncs_test[i].light_times))
class Sample_Data(Thread):
    def run(self):
        data_store = []
        print_out = 0
        while running_check == 1:
            time.sleep(5)
            print_out += 5
            for i in range(len(lanes_test)):
                num_cars_in_lane_temp = len(lanes_test[i].cars_in_lane_id)
                num_g_cars_in_lane_temp = len(lanes_test[i].g_cars_in_lane_id)
                if num_g_cars_in_lane_temp >= 4:
                    data_store.append([i,num_cars_in_lane_temp,num_g_cars_in_lane_temp])
                if (num_g_cars_in_lane_temp == 6) and (num_cars_in_lane_temp == 0):
                    print("     6 lane: " + str(i) + " actual: " + str(num_cars_in_lane_temp))
                    print("g_cars_in_lane_id: " + str(lanes_test[i].g_cars_in_lane_id))
                    for t in lanes_test[i].g_cars_in_lane_id:
                        print("car: " + str(t) + " g_lane: " + str(cars[t].g_lane) + " g_lane_temp: " + str(cars[t].g_lane_temp))
                    input("     6")
            if print_out >= 20:
                # reset print_out
                print_out = 0
                print("data_store: " + str(data_store))

### Declare threads
t7 = ExtractCarInfo()
t8 = FindWaitTimeForLanes()
# t9 = FindGreenLightLanes()
# t10 = Find_Lane_Localisation_from_RealTest()
t10 = Find_Lane_Car_Position()
# t12 = Update_Light_Times_for_GA() # GA
# t13 = Monitor_and_Control_Lights_for_GA() #GA
# t14 = Best_Possible_Light_Times()
# t15 = Sample_Data() #GA
t16 = Monitor_and_Control_Lights_for_PA()

# t5.daemon = True
# t6.daemon = True
t7.daemon = True
t8.daemon = True
# t9.daemon = True
t10.daemon = True
# t11.daemon = True
# t12.daemon = True
# t13.daemon = True
# t14.daemon = True
# t15.daemon = True
t16.daemon = True

### Start threads
# t5.start()
# t6.start()  # this thread cycles through the lanes at junc to turn them green for a set time
t7.start() # extract car info
t8.start()
# t9.start() # this thread is the algoritm which selects the lane in the junc to turn green
t10.start()
# t11.start()
# t12.start()
# t13.start()
# t14.start()
# t15.start()
t16.start()

time_limit = 200
# time_interval = 0.05
time_current = 0
time_checker = 0
time_checker_2 = 4
green_light_lanes = []
red_light_lanes_pause_temp = []
for i in range(len(juncs_test)):
    for j in juncs_test[i].light_lanes_at_junc:
        if lanes_test[j].orien == 0:
            # lane_selected_temp = juncs_test[i].light_lanes_at_junc[0]
            lane_selected_temp = j
            lanes_test[lane_selected_temp].time_green = 1#30 #6
            lanes_test[lane_selected_temp].green_light = 1
            juncs_test[i].green_lanes_at_junc = lane_selected_temp
            juncs_test[i].green_lane_at_junc_orien = lanes_test[lane_selected_temp].orien

cars_intending_to_enter = []

starter_checker = 1
num_cars_entered_system = len(cars_entered_system)
new_cars_per_interval = 20
car_entry_interval_timer = 0
car_entry_interval_timer_limit = 3 # number of seconds between the arrival of a new batch of cars
for i in range(num_initial_internal_cars):
# for i in range(num_cars):
    cars_intending_to_enter.append(cars[i].id)
    cars[i].car_waiting_to_enter_system = 1

time_print_checker = 0
############## running loop

while time_current < time_limit:

    if car_entry_interval_timer >=  car_entry_interval_timer_limit:
        print("new arrivals")
        # input("new arrivals")
        car_entry_interval_timer = 0
        num_cars_entered_system = len(cars_entered_system)
        # print("num_cars_entered_system: " + str(num_cars_entered_system))
        # input("paused 1")
        # print("num_cars_entered_system = " + str(num_cars_entered_system))
        # print("car_in_lane_12: " + str(lanes_test[12].cars_in_lane_id))
        if num_cars_entered_system + new_cars_per_interval <= num_cars:
            for i in range(num_cars_entered_system,(num_cars_entered_system + new_cars_per_interval)):
                # an interval is every 10 seconds
                # add car_id to cars_to_intending_to_enter
                # check if car already in cars_intending_to_enter
                if (i not in cars_intending_to_enter) and (i not in cars_entered_system):
                    cars_intending_to_enter.append(cars[i].id)
                    cars[i].car_waiting_to_enter_system = 1
                    # if i in cars_entered_system:
                    #     print("cars_in_system: " + str(cars_in_system))
                    #     print("car_i: " + str(i) + " cur_lane: " + str(cars[i].current_lane))
                    #     print("cars_in_cur_lane: " + str(lanes_test[cars[i].current_lane].cars_in_lane_id))
                    #     # input("stop here")
                    #     cars_intending_to_enter.remove(i)
            # print("cars_intending_to_enter: "+ str(cars_intending_to_enter))
        if num_cars_entered_system + new_cars_per_interval > num_cars:
            diff_temp = num_cars - num_cars_entered_system
            # print("diff_temp: " + str(diff_temp))
            if diff_temp > 0:
                new_cars_per_interval_temp = diff_temp
                for i in range(num_cars_entered_system,(num_cars_entered_system + new_cars_per_interval_temp)):
                    # an interval is every 10 seconds
                    # add car_id to cars_to_intending_to_enter
                    # check if car already in cars_intending_to_enter
                    if i not in cars_intending_to_enter:
                        # print("i: " + str(i))
                        cars_intending_to_enter.append(cars[i].id)
                        cars[i].car_waiting_to_enter_system = 1
                # print("cars_intending_to_enter: "+ str(cars_intending_to_enter))



    light_control_function(juncs_test,lanes_test,green_light_lanes,time_interval,red_light_lanes_pause_temp)
    cars_to_wait_this_iter = []
    cars_entering_this_iter = []
    # print("car_in_lane_12: " + str(lanes_test[12].cars_in_lane_id))
    # print("cars_mstatus_79: " + str(cars[79].move_status))
    # print("cars")
    # print("cars_intending_to_enter: " + str(cars_intending_to_enter))
    for car_id in cars_intending_to_enter:
        car_entering_function(cars,lanes_test,Car,car_id,cars_in_system,cars_entered_system,cars_intending_to_enter,cars_to_wait_this_iter,cars_entering_this_iter)

    temp_cars_intending_to_enter = []
    for i in cars_intending_to_enter:
        if i in cars_to_wait_this_iter:
            temp_cars_intending_to_enter.append(i)
    cars_intending_to_enter = temp_cars_intending_to_enter

    # print("ran 4 end pos_in_queue: " + " current_end_step_0: " + str(cars[0].current_end_step))
    move_function_new(cars,lanes_test,Car,green_light_lanes)

    # canvas.itemconfig(cars[10].body, fill='orange')
    # if cars[10].localised_stage == 2:
    #     canvas.itemconfig(cars[10].body, fill='green')
    #
    # if cars[10].sampling_checker == 1:
    #     canvas.create_oval(cars[10].pos_x - rad_gps,cars[10].pos_y - rad_gps,cars[10].pos_x + rad_gps, cars[10].pos_y + rad_gps )
    #     canvas.create_oval(cars[10].coords[0] - 2,cars[10].coords[1] - 2,cars[10].coords[0] + 2, cars[10].coords[1] + 2, fill ='red' )
        # draw car
    # for i in range(len(juncs_test)):
    #     if i == 2:
    #         print("i: " + str(i) + " green_lanes_at_junc: " + str(juncs_test[i].green_lanes_at_junc))
    #         print("map_green_lane: " + str(lanes_test[juncs_test[i].green_lanes_at_junc].map_lane_id))
    # print("cars_in_lane_id 1: " + str(lanes_test[1].cars_in_lane_id))
    # print("g_cars_in_lane_id 1: " + str(lanes_test[1].g_cars_in_lane_id))
    for i in range(len(lanes_test)):
        # update the next_car_free_to_go variable for each lane_test, add one for each interation
        # lanes_test[i].next_car_free_to_go += 1
        lanes_test[i].next_car_free_to_go -= 1
        # print("junc_0 light_green: " + str(juncs_test[0].green_lanes_at_junc))
        # if (i in juncs_test[0].lanes_at_junc) and (lanes_test[i].green_light == 1):
        #     print("num_cars_in_lane: " + str(len(lanes_test[i].cars_in_lane_id)))
        #     print("green_light: " + str(i) + " time_green: " + str(lanes_test[i].time_green))
        #     print("next_car_free_to_go: "+ str(lanes_test[i].next_car_free_to_go))
        #     print("juncs_test[i].light_times: " + str(juncs_test[i].light_times))
        #     print("next_car_free_to_go: " + str(next_car_free_to_go)
    # print("lane_3 next_car_free_to_go: " + str(lanes_test[3].next_car_free_to_go))

    time_checker += time_interval
    time_checker_2 -= time_interval

    for car_temp in cars_in_system:
        cars[car_temp].time_in_g_lane += time_interval
        # if car_temp == 0:
        #     canvas.itemconfig(cars[car_temp].body, fill='green')

    # for car_temp in cars_in_system:
    #     if cars[car_temp].localised_stage == 1:
    #         canvas.itemconfig(cars[2].body, fill='orange')
    #     if cars[car_temp].localised_stage == 2:
    #         canvas.itemconfig(cars[2].body, fill='green')


    # if cars[0].localised_stage == 1:
    #     canvas.itemconfig(cars[0].body, fill='orange')
    # if cars[0].localised_stage == 2:
    #     canvas.itemconfig(cars[0].body, fill='green')

    # canvas.itemconfig(cars[7].body, fill='green')

    if cars[0].sampling_checker == 1:
        canvas.create_oval(cars[0].pos_x - rad_gps,cars[0].pos_y - rad_gps,cars[0].pos_x + rad_gps, cars[0].pos_y + rad_gps )
        canvas.create_oval(cars[0].coords[0] - 2,cars[0].coords[1] - 2,cars[0].coords[0] + 2, cars[0].coords[1] + 2, fill ='red' )

    # canvas.itemconfig(cars[79].body, fill='red')
    # print("car_57_step: " + str(cars[57].step))
    # print("cars_in_lane_id_5: " + str(lanes_test[5].cars_in_lane_id))



    for i in range(num_cars):
        if cars[i].current_lane != 9999:
            if (cars[i].current_lane == cars[i].g_lane) or (cars[i].g_lane in lanes_test[cars[i].current_lane].assoc_lanes):
                canvas.itemconfig(cars[i].body, fill='green')
            else:
                canvas.itemconfig(cars[i].body, fill='black')
        # if cars[i].next_lane in lanes_test[cars[i].current_lane].free_turn_next_lanes:
        #     # turne car to pink
        #     # print("turn pink car: "+ str(i))
        #     # print("current_end_step: " + str(cars[i].current_end_step) + " step: " + str(cars[i].step) + " current_lane_end_step: " + str(cars[i].current_lane_end_step))
        #     # print("pink lane: " + str(cars[i].current_lane) + " cars_in_lane_id: " + str(lanes_test[cars[i].current_lane].cars_in_lane_id))
        #     canvas.itemconfig(cars[i].body, fill='pink')
        # else:
        #     canvas.itemconfig(cars[i].body, fill='black')
        if cars[i].car_in_system == 1: # ie. TRUE
            cars[i].time_in_system += time_interval
        if cars[i].car_waiting_to_enter_system == 1: # ie. TRUE
            cars[i].wait_time_to_enter_system += time_interval
        if cars[i].car_waiting_in_queue == 1: # ie. TRUE
            cars[i].wait_time_in_queue += time_interval
        if cars[i].car_moving == 1: #ie. TRUE
            cars[i].move_time += time_interval

    # for i in range(len(lanes_test)):
    #     print("lane_i: " + str(i) + " junc_pos: " + str(lanes_test[i].junc_pos))
    # input("end it")


    # canvas.itemconfig(cars[486].body, fill='yellow')
    # canvas.itemconfig(cars[76].body, fill='yellow')
    # print("cars_in_lane_0: " + str(lanes_test[0].cars_in_lane_id))
    # print("cars_in_lane_59: " + str(lanes_test[59].cars_in_lane_id))
    # print("car 76_path: " + str(cars[76].path))
    # print("car_76_current_lane: " + str(cars[76].current_lane))
    # print("car_76 path: " + str(cars[76].path))
    # print("car_76 cur_lane: " + str(cars[76].current_lane) + " g_lane: " + str(cars[76].g_lane))
    # canvas.itemconfig(cars[76].body, fill='red')
    # print("move_status_tracker: " + str(cars[16].move_status_tracker))
    # print("pl1: " + str(cars[16].potential_lanes_1))
    # print("16 actual_lane: " + str(cars[16].current_lane) + " g_lane: " + str(cars[16].g_lane) + " g_lane_temp: " + str(cars[16].g_lane_temp))
    # canvas.itemconfig(cars[16].body, fill='red')
    tk.update()
    time_current += time_interval
    car_entry_interval_timer += time_interval
    # print("time_current: " + str(time_current))
    time_print_checker += time_interval
    if time_print_checker > 5:
        print("time_current: " + str(time_current))
        # print("     80 g_cars_in_lane_id: " + str(lanes_test[80].g_cars_in_lane_id))
        time_print_checker = 0
    # print("time_now: " + str(time_current))
    time.sleep(time_interval)

tk.update()
running_check = 0 # this should halt the threads
overall_wait_time_in_queue = 0
overall_move_time = 0
overall_wait_time_to_enter_system = 0
overall_time_in_system = 0
### Calculate performance parameters
for i in range(num_cars):
    overall_wait_time_in_queue += cars[i].wait_time_in_queue
    overall_move_time += cars[i].move_time
    overall_wait_time_to_enter_system += cars[i].wait_time_to_enter_system
    overall_time_in_system += cars[i].time_in_system

    print("car: " + str(i) + " wait_time_to_enter_system: " + str(cars[i].wait_time_to_enter_system))
    print("car: " + str(i) + " time_in_system: " + str(cars[i].time_in_system))
    print("car: " + str(i) + " wait_time_in_queue: " + str(cars[i].wait_time_in_queue))
    print("car: " + str(i) + " move_time: " + str(cars[i].move_time))

print("overall_wait_time_in_queue: " + str(overall_wait_time_in_queue))
print("overall_move_time: " + str(overall_move_time))
print("overall_wait_time_to_enter_system: " + str(overall_wait_time_to_enter_system))
print("overall_time_in_system: " + str(overall_time_in_system))
print("num_cars_entered_system: " + str(len(cars_entered_system)))
print("num_cars_exited_system: " + str(len(cars_exited_system)))
print("num_cars_in_system: " + str(len(cars_in_system)))
input("Press enter to end")
