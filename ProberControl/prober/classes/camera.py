import numpy as np
import cv2
import logging

MAIN_CAM = 0
DEBUG_MODE = True

def im_match_err(im1, im2):
    # matching images for Camera.get_from_map()
    L2_err = cv2.norm(im1, im2, cv2.NORM_L2)
    error = L2_err / (float)(im1.shape[0] * im1.shape[1])
    return error
    
def im_rot(im, ang, im_w, im_h):
    # rotation data
    center = (im.shape[0] / 2, im.shape[1] / 2)
    scale = 1.0
    angle = -1 * ang
    rot_matrix = cv2.getRotationMatrix2D(center, angle, scale)
    #apply rotation
    im = cv2.warpAffine(im, rot_matrix, (im.shape[1], im.shape[0]))
    # resize
    im = cv2.resize(im, (im_w, im_h))
    
    return im
    

class Camera(object):

    def __init__(self, cam_desc, cam_ctrl = None):
        '''
         Constructor
         
         cam_desc (int): the camera file descriptor
         cam_ctrl (CameraController)
        '''
        
        # get feed from the specified camera
        self.cap = cv2.VideoCapture(cam_desc)
        # bind the object to a controller (experimantal)
        if cam_ctrl is None:
            logging.warning('No controller bound to camera object: disp() will not function properly.')
        else:
            self.ctrl = cam_ctrl
        
    # EXPERIMENTAL
    def displ(self):
        '''
         Display camera feed until thread is done
         
         thrd (threading.Thread): thread to be done
         hud (String): HUD to display on screen
        '''
        
        kernel = np.ones((20,20),np.uint8)    # for cv2.morphologyEx() 
        
        while(True):
            ret, frame = self.cap.read()
            if ret == False:
                print 'problem reading from camera'
                exit()
                
            if self.ctrl.hudMsg != '' and self.ctrl.hudON:
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, self.ctrl.hudMsg, (10,20), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            
            if self.ctrl.t_rects:
                # convert to greyscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # apply blur
                blur = cv2.GaussianBlur(gray,(5,5), 0)
                # Otsu mask
                ret, thr = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                ## cv2.imshow('thresh', thr)
                
                # morphology closing : eliminate noise inside main shape
                clo = cv2.morphologyEx(thr, cv2.MORPH_CLOSE, kernel)
                ## cv2.imshow('closing', clo)
                
                # find contours 
                im2, contours, hierarchy = cv2.findContours(clo, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                # select contour <- subject to change
                cnt = None
                
                for ct in contours:
                    if len(ct) > 75 and cv2.contourArea(ct) > 30000:    # probably found main shape
                        cnt = ct
                        break
                
                if cnt is None:
                    continue
                    
                # draw the selected contour
                ## cv2.drawContours(frame, [cnt], 0, (255,0,0), 3)
                
                # find the corresponding straight rectangle
                x,y,w,h = cv2.boundingRect(cnt)
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                
                # find the minimum area rect    angle i.e. the rotated rectangle
                # if not wait:        
                r_rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(r_rect)
                box = np.int0(box)
                cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
                
            cv2.imshow('cam', frame)
            cv2.waitKey(1)
            if self.ctrl.t_rects:
                t_curr = cv2.getTickCount()
                if (t_curr - self.ctrl.t_init) / cv2.getTickFrequency() >= self.ctrl.secs :
                    self.ctrl.box_data = box
                    self.ctrl.t_rects = False
            if self.ctrl.quit() and not self.ctrl.t_rects:
                break
        
    
    # The wait functionallity of the following method is depricated,
    # because the function is too heavy.
    # It should only be used when its really needed.
    def get_coord(self, secs = 1, wait = False, boxCoor = False, thrd = None):
        '''
         Find the orientation of the chip and return the coordinates
         of the rectangle surrounding it
         
         secs (unsigned int): the time, in seconds we give the camera
         to compute the coordinates
         wait (boolean): wait mode -> quit with 'q'
         boxCoor (boolean): the return value is the right rectangle's coordinates
                            instead of the slanted's
         thrd (object): for externally controlled observation (i.e. to see motor movements)
                          - must have a boolean running() method
        '''
        
        kernel = np.ones((20,20),np.uint8)    # for cv2.morphologyEx() 
        
        # keep track of time
        t_init = cv2.getTickCount()

        while(True):
            ret, frame = self.cap.read()
            if ret == False:
                print 'problem reading from camera'
                exit()
            
            # convert to greyscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # apply blur
            blur = cv2.GaussianBlur(gray,(5,5), 0)
            # Otsu mask
            ret, thr = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            ## cv2.imshow('thresh', thr)
            
            # morphology closing : eliminate noise inside main shape
            clo = cv2.morphologyEx(thr, cv2.MORPH_CLOSE, kernel)
            ## cv2.imshow('closing', clo)
            
            # find contours 
            im2, contours, hierarchy = cv2.findContours(clo, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            # select contour <- subject to change
            cnt = None
            
            for ct in contours:
                if len(ct) > 75 and cv2.contourArea(ct) > 30000:    # probably found main shape
                    cnt = ct
                    break
            
            if cnt is None:
                continue
                
            # draw the selected contour
            ## cv2.drawContours(frame, [cnt], 0, (255,0,0), 3)
            
            if DEBUG_MODE:
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, str(len(cnt)), (10,20), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            # find the corresponding straight rectangle
            x,y,w,h = cv2.boundingRect(cnt)
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            
            if DEBUG_MODE:
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, 'area: ' + str(w * h), (10,40), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(frame, 'cnt area: ' + str(cv2.contourArea(cnt)), (10,60), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            
            # find the minimum area rect    angle i.e. the rotated rectangle
            # if not wait:        
            r_rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(r_rect)
            box = np.int0(box)
            cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
                
            
            cv2.imshow('cam', frame)
            key = cv2.waitKey(1) & 0xFF == ord('q')
            # check if this function is running on parallel
            threaded = (thrd is not None) and (not thrd.is_alive())
            if wait and (key or threaded) :
                break
            
            # see if enough time has passed
            if not wait:
                t_curr = cv2.getTickCount()
                if (t_curr - t_init) / cv2.getTickFrequency() >= secs :
                    break
            

        # self.cap.release()
        # cv2.destroyAllWindows()
        
        if boxCoor:
            return (x, y, w, h)
            
        return box
        
    
    def get_from_map(self, image_filename):
        '''
         Finds which side the chip has to turn to according to the map
         provided. The user makes the selection.
         
         - Should be run complementary to get_coord()
         
         image_filename (string): the filepath of the map
        '''
        
        map = cv2.imread(image_filename)

        # extract the ROI of the map that has the chip
        grey_map = cv2.cvtColor(map, cv2.COLOR_BGR2GRAY)
        ret1, map_mask = cv2.threshold(grey_map, 0, 255, cv2.THRESH_BINARY)
        _, contours, hierarchy = cv2.findContours(map_mask, 
                                                  cv2.RETR_TREE, 
                                                  cv2.CHAIN_APPROX_SIMPLE)
        map_x, map_y, map_w, map_h = cv2.boundingRect(contours[0])

        map_roi = map[map_y : map_y+map_h , map_x : map_x+map_w]
        ## cv2.imshow('masked map', map_roi)
        ## cv2.waitKey()

        # locate th chip in the live feed
        x,y,w,h = self.get_coord(boxCoor = True)
        # resize map_roi according to live size
        map_roi = cv2.resize(map_roi, (w, h))
        
        final_angle = 0.0
        
        # suggest the correct orientation
        ret, frame = self.cap.read()
        min = im_match_err(frame[y:y+h, x:x+w], map_roi)
        print min
        temp_ang = 0.0
        for i in xrange(3):
            temp_ang += 90.0
            map_roi = im_rot(map_roi, 90, w, h)
            error = im_match_err(frame[y:y+h, x:x+w], map_roi)
            print error
            if error < min:
                min = error
                final_angle = temp_ang
            
        map_roi = im_rot(map_roi, final_angle - 270.0, w, h)    

        if final_angle == 270:
            final_angle == -90

        # manual control
        while(True):
            ret, frame = self.cap.read()
            
            frame[y:y+h, x:x+w] = cv2.addWeighted(frame[y:y+h, x:x+w], 1, map_roi, 0.6, 0)
            
            cv2.imshow('cam', frame)
            # input handling - user selects orientation
            key_pressed = cv2.waitKey(1) & 0xFF
            if key_pressed == ord('q'):
                break
            elif key_pressed == ord('m') or key_pressed == ord('n'):    # right/left arrow
                print 'here'
                # rotation data
                center = (map_roi.shape[0] / 2, map_roi.shape[1] / 2)
                scale = 1.0
                if key_pressed == ord('m'):     # right
                    angle = -1 * 90.0
                    final_angle += 90.0
                else:                            # left
                    angle = 90.0
                    final_angle -= 90.0
                if abs(final_angle) == 270:
                    final_angle /= -3
                
                rot_matrix = cv2.getRotationMatrix2D(center, angle, scale)
                #apply rotation
                map_roi = cv2.warpAffine(map_roi, rot_matrix, (map_roi.shape[1], map_roi.shape[0]))
                # resize
                map_roi = cv2.resize(map_roi, (w, h))
            elif key_pressed == 13:
                return -final_angle
                
    
    def close(self):
        self.cap.release()
        cv2.destroyAllWindows()
        
        
# Still on experimantal stage        
class CameraController(object):
    def __init__(self):
        self.killed = False
        self.hudON = False
        self.t_rects = False    # to retrieve box coordinates
        self.t_init = None        # to start counting time for box coordinates
        self.box_data = None    # to store the box coordinates
        self.secs = 1            # how long to wait to get box coords
        self.hudMsg = ''
        
    def kill(self):    # User
        self.killed = True
        
    def quit(self):
        return self.killed
        
    def toggleHUD(self):    # User
        self.hudON = not self.hudON
        
    def setHUD(self, msg):    # User
        self.hudMsg = msg
        
    def enRects(self, secs = 1):    # User
        self.secs = secs
        self.box_data = []
        self.t_init = cv2.getTickCount()
        self.t_rects = True
        
        while self.t_rects:
            cv2.waitKey(1)
            
        return self.box_data
            

'''
Copyright (C) 2017  Robert Polster
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
