#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 13:51:41 2018

@author: Michele Svanera, PhD
University of Glasgow

Code to find field of view of every subject

"""

################################################################################################################
## Imports 

from __future__ import division, print_function

from psychopy import visual, event, core, logging
from psychopy import prefs as pyschopy_prefs
import psychopy 

import numpy as np
import os, sys
from datetime import datetime as dt
from time import localtime, strftime
import math
from PIL import Image


################################################################################################################
## Paths and Constants

EPSILON = 1e-5
serif = ['Times', 'Times New Roman']
sans = ['Gill Sans MT', 'Arial', 'Helvetica', 'Verdana']

# Experiment details
Fullscreen = False   #True-False
Screen_dimensions = (500,500)            #(1920,1080)
#Dir_save = '../out/'
Dir_save = 'D:/Mucklis_lab/Movie_feedback/out/'
Log_name = 'LogFile.log'
Frames_durations_name = 'frames_durations.npy'
Fps_update_rate = 1                             # sec

# Polygon details
Radius_polygon = 0.9
Points_polygon = 10             # They are the double


################################################################################################################
## Functions and Classes


def logEveryPackageLoad(log):
    log.data('%10s : %s' % ('Python', sys.version.split('\n')[0]))
    log.data('%10s : %s' % ('Numpy', np.__version__))
    log.data('%10s : %s\n' % ('Psychopy', psychopy.__version__))
    
    
def screenCorrection(mywin,x):
    resX = mywin.size[0]
    resY = mywin.size[1]
    aspect = float(resX) / float(resY)
    return(x / aspect)

    
def createOutFolder(path_out):
    if not os.path.exists(path_out):
        try:
            os.makedirs(path_out)
        except Exception as e:
            print('Problem with creating an *out* folder, check permissions: '+e)
    else:
        n_folder_name = 1
        path_out_new = path_out + "_" + str(n_folder_name)
        while(os.path.exists(path_out_new) is True):
            n_folder_name += 1
            path_out_new = path_out + "_" + str(n_folder_name)
        try:
            os.makedirs(path_out_new)
        except Exception as e:
            print('Problem with creating an *out* folder, check permissions: '+e)
        path_out = path_out_new
    path_out += '/'
    
    return path_out


def circleSampling(n, r=1):       # r = radius, n = sampling

    th = np.arange(0, 2 * np.pi, np.pi / n)
    xunit = r * np.cos(th)
    yunit = r * np.sin(th)
    
    return list(zip(xunit,yunit))


def cartesian(r, theta):
    """theta in degrees

    returns tuple; (float, float); (x,y)
    """
    x = r * math.cos(math.radians(theta))
    y = r * math.sin(math.radians(theta))
    return x,y


def polar(x, y):
    """returns r, theta(degrees)
    """
    r = (x ** 2 + y ** 2) ** .5
    if y == 0:
        theta = 180 if x < 0 else 0
    elif x == 0:
        theta = 90 if y > 0 else 270
    else:
#        theta = math.degrees(math.atan(float(y) / x))
        theta = np.arctan2(float(y), float(x)) * 180 / np.pi
    return r, theta


################################################################################################################
## Main

def main(win, globalClock):

    ################################ Stimuli prepation ################################

    # a target polygon (starting from 0 degree):
    polygon_vertices = circleSampling(Points_polygon, r = Radius_polygon)
    polygon = visual.ShapeStim(win, fillColor='yellow', lineWidth=5, lineColor='white', opacity=0.75,
                               vertices=polygon_vertices)
    
    # Markers and labels
    all_circles = []
    all_labels = []
    for i,i_vertex in enumerate(polygon_vertices):
        
        # Maker
        i_circle = visual.Circle(win, radius=(screenCorrection(win,0.03),0.03), pos=i_vertex, 
                                 fillColor='green', lineWidth=1, lineColor='white', opacity=1)
        all_circles.append(i_circle)
        
        # Label
        r,t = polar(i_vertex[0],i_vertex[1])
        x,y = cartesian(r-.05, t)
        i_labels = visual.TextStim(win, text=str(i+1), pos=(x,y), height=0.05, font='Helvetica', 
                                   color='black')
        all_labels.append(i_labels)
    

    # DEBUG stimuli
    if DEBUG_MODE:
        fps_text = visual.TextStim(win, units='norm', height=0.05,pos=(-0.98, +0.93), text='starting...',
                                  font=sans, alignHoriz='left', alignVert='bottom', color='yellow')    
        fps_text.autoDraw = True
        
        orientation_details_string = visual.TextStim(win, text = u"Orientation..", units='norm', height=0.05,
                                             pos=(0.95, +0.93), alignHoriz='right', alignVert='bottom', 
                                             font=sans, color='yellow')
        orientation_details_string.autoDraw = True        


    ################################ Definitions/Functions ################################    
    
    ## handle key presses each frame
    def keyPressCondition(i_vertex, r_vertex):

        for key in event.getKeys():
            
            if key in ['escape', 'q']:
                i_vertex = np.NaN
                
            if key in ['right']:
                i_vertex -= 1
            if key in ['left']:
                i_vertex += 1   
                
            if i_vertex < 0:
                i_vertex += len(polygon_vertices)
            if i_vertex >= len(polygon_vertices):# or i_vertex<=-len(polygon_vertices):
                i_vertex = 0

            if key in ['up']:
                r_vertex *= 1.1
            if key in ['down']:
                r_vertex /= 1.1
            
#            r_vertex = min(0.99,r_vertex)
            r_vertex = max(.05,r_vertex)
            
        return i_vertex, r_vertex


    ################################ Animation starts ################################        
    # Display instructions and wait
 
    message1 = visual.TextStim(win, pos=[0,0.5],text='Hit a key when ready.')
    message1.draw()
    win.flip()
    event.waitKeys()    #pause until there's a keypress
   
    all_theta = []
    for indx, i in enumerate(polygon.vertices):
        x, y = i
        r, theta = polar(x, y)
        all_theta.append(theta)
    
    starting_time = globalClock.getTime()
    
    i_vertex = 0; i_vertex_up = 0;
    while(1):

        # Retrieve r to modify it (if needed)
        x, y = polygon.vertices[i_vertex]
        r, theta = polar(x, y)
        
        # Keys
        i_vertex_up, r = keyPressCondition(i_vertex, r)
        if np.isnan(i_vertex_up): break

        # Update vertex 'i_vertex_up'
        x, y = polygon.vertices[i_vertex_up]
        if i_vertex_up != i_vertex:         # change of vertex in this iteration
            r, theta = polar(x, y)
        else:                               # change of r
            _, theta = polar(x, y)

        polygon_vertices[i_vertex_up] = cartesian(r, theta)#all_theta[i_vertex_up])

        polygon.vertices = polygon_vertices
        polygon.draw()

        # Update circles and indeces
        for i,x_circles in enumerate(all_circles):
            if i != i_vertex_up:
                x_circles.fillColor = 'green'
            else:
                x_circles.fillColor = 'red'
                x_circles.pos = cartesian(r, theta)
                all_labels[i].pos = cartesian(r-0.05, theta)

            x_circles.draw()
            all_labels[i].draw()

        # Update screen                
        win.flip()
        i_vertex = i_vertex_up
        

    # Show final in order to save it
    polygon.fillColor = 'white'
    polygon.opacity = 1.    
    polygon.draw()
    win.flip()
    
    # Save frame
    last_frame_changed = np.array(win.getMovieFrame())
    last_frame_changed = Image.fromarray(last_frame_changed)#.convert('LA')
    last_frame_changed.save(path_out+'last_frame.png')
    
    logging.data('** Vertices obtained: **\n\n')
    logging.data(polygon_vertices)
    print(polygon_vertices  )
    logging.data('\n\n\n')
    logging.data('Total time spent: %.6f' % (globalClock.getTime() - starting_time))
    logging.data('Every frame duration saved in %s' % (path_out+Frames_durations_name))

    if DEBUG_MODE:
        orientation_details_string.text = 'Ended at %.3f (sec.)' % (globalClock.getTime())    
    
    return


if __name__ == "__main__":  
    
    # Experiment variables
    today_date = dt.today().strftime('%Y-%m-%d')        # Date (mm/dd/yy)
    operator = 'MS'                                     # Operator
    DEBUG_MODE = False                                  # Debug mode
    subject_code = 'test'                               # Subject-code
    subject_age = 99                                    # Age
    subject_gender = 'female'                           # Gender

    # Prepare out folder
    path_out = Dir_save + today_date + '_' + subject_code + '_fow_7T'
    path_out = createOutFolder(path_out)

    if not os.path.exists(Dir_save):
        os.makedirs(Dir_save)
    globalClock = core.Clock()
    
    # Set the log module to report warnings to the standard output window
    logging.setDefaultClock(globalClock)
    logging.console.setLevel(logging.WARNING)
    lastLog=logging.LogFile(path_out+Log_name,level=logging.DATA,filemode='w',encoding='utf8')
    logging.data("------------- " + strftime("%Y-%m-%d %H:%M:%S", localtime()) + " -------------\n")
    logEveryPackageLoad(logging)
    logging.data(pyschopy_prefs)
    logging.data("Saving in folder: " + path_out)
    logging.data("Operator: " + operator + "\n")    
    logging.data("Subject. Code: " + subject_code + " - Age: " + str(subject_age) + " - Gender: " + subject_gender) 
    logging.data('***** Starting *****')

    # Start window
    win = visual.Window(Screen_dimensions, monitor="mon", screen=0, units="norm", fullscr=Fullscreen,
                        allowStencil=True, color='black') # norm
    resX,resY = win.size
    logging.data('Resolution of the screen: %d, %d.' % (resX,resY))
    win.recordFrameIntervals = True

    # Main stimulation
    try:
        main(win, globalClock)
    except Exception as e:
        logging.log(e,level=logging.ERROR)

        
    logging.data('Overall, %i frames were dropped.' % win.nDroppedFrames)
    np.save(path_out+Frames_durations_name,win.frameIntervals[1:])
        
    logging.data('***** End *****')
    
    win.close()
    core.quit()








