## ----------------------------------------------------------------------------------------------------------

import sys
sys.path.append('../')

from Common_Libraries.p2_lib import *

import os
from Common_Libraries.repeating_timer_lib import repeating_timer
import random
import time

def update_sim ():
    try:
        arm.ping()
    except Exception as error_update_sim:
        print (error_update_sim)

arm = qarm()

update_thread = repeating_timer(2, update_sim)


def identify_bin_loc(container_id):
    if container_id == 1:
        # Small, Red
        bin_loc = [-0.5864, 0.2429, 0.4589]
    elif container_id == 2:
        # Small, Green
        bin_loc = [0.0, -0.6347, 0.4589]
    elif container_id == 3:
        # Small, Blue
        bin_loc = [0.0, 0.6347, 0.4589]
    elif container_id == 4:
        # Large, Red
        bin_loc = [-0.3787, 0.1569, 0.3979]
    elif container_id == 5:
        # Large, Green
        bin_loc =  [0.0, -0.4099, 0.3979]
    elif container_id == 6:
        # Large Blue
        bin_loc = [0.0, 0.4099, 0.3979]
    else:
        # not valid bin location, return home coordiates
        print('Invalid Container ID:', container_id)
        bin_loc = [0.4064, 0.0, 0.4826]
    return bin_loc


def control_gripper(amount, threshold=0.3):
    while True:
        # if left arm is above threshold and right arm is below threshold
        if arm.emg_right() < threshold and arm.emg_left() >= threshold:
            # control gripper by amount given and wait two seconds
            arm.control_gripper(amount)
            time.sleep(2)
            return
        else:
            # wait two seconds and check sensors again
            time.sleep(2)


def move_end_effector(loc, threshold=0.3):
    while True:
        # if left and right arms are above threshold
        if arm.emg_right() >= threshold and arm.emg_left() >= threshold:
            # move arm up and wait a second to avoid clipping objects
            arm.move_arm(0.4064, 0.0, 0.4826)
            time.sleep(1)
            # move arm to coordinate position and wait two seconds
            arm.move_arm(loc[0], loc[1], loc[2])
            time.sleep(2)
            return
        else:
            # wait two seconds and check sensors again
            time.sleep(2)


def open_autoclave_bin_drawer(container_id, open_autoclave, threshold=0.3):
    if container_id not in [4,5,6]:
        # do nothing if container is is not large type
        return
    while True:
        # if left arm is below threshold and right arm is above threshold
        if arm.emg_left() < threshold and arm.emg_right() >= threshold:
            if container_id == 4:
            # open/close Large, Red
                arm.open_red_autoclave(open_autoclave)
            elif container_id == 5:
                # open/close Large, Green
                arm.open_green_autoclave(open_autoclave)
            elif container_id == 6:
                # open/close Large, Blue
                arm.open_blue_autoclave(open_autoclave)
            return
        else:
            # wait two seconds and check sensors again
            time.sleep(2)


def continue_or_terminate():
    # initialize empty list for containers
    seen_containers = []
    while True:
        # generate a random container id to drop (number between 1 and 6)
        container_id = random.randint(1,6)
        # if container id has been placed
        if container_id in seen_containers:
            # try next random number
            continue
        # move arm to home position and wait four seconds
        arm.home()
        time.sleep(4)
        # drop new container and wait two seconds
        arm.spawn_cage(container_id)
        print('container id is:', container_id)
        time.sleep(2)
        # move to pickup position
        move_end_effector([0.5248, 0.0, 0.03])
        # grip object
        control_gripper(45)
        # identify dropoff location
        loc = identify_bin_loc(container_id)
        # move to dropoff position
        move_end_effector(loc)
        # open autoclave drawer
        open_autoclave_bin_drawer(container_id, open_autoclave=True)
        # open gripper
        control_gripper(-45)
        # close autoclave drawer
        open_autoclave_bin_drawer(container_id, open_autoclave=False)
        # add container to seen list
        seen_containers.append(container_id)
        # if all container types have been placed
        if len(seen_containers)==6:
            # print done and terminate the function
            print('Done.')
            arm.home()
            break

def main():
    continue_or_terminate()

main()



## ----------------------------------------------------------------------------------------------------------


