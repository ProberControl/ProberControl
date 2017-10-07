import numpy as np
import cv2
import logging
import threading

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

    def __init__(self, cam_id, cam_ctrl = None):
        '''
         Constructor
         
         cam_id (int): the camera file descriptor
         cam_name : the name assigned to camera
         cam_ctrl (CameraController)
        '''
        
        # get feed from the specified camera
        self.cap = cv2.VideoCapture(int(cam_id))
        self.resolution = 0.1
        self.lines = []
        self.regions = []
        self.img = []
        self.split = 0
        self.script_running = False
        self.line_type = 'list'
        self.name = ''
        # bind the object to a controller (experimantal)
        if cam_ctrl is None:
            #logging.warning('No controller bound to camera object: disp() will not function properly.')
            pass
        else:
            self.ctrl = cam_ctrl
       
    def read(self):
        return self.cap.read()
    
    def whoAmI(self):
        return self.name
    
    def set_whoAmI(self, name):
        self.name = name
    
    def whatCanI(self):
        return self.name
        
    def _threadCamera(self, title):
        while(1):
            ret,frame = self.cap.read()
            cv2.imshow(title,frame)
            k = cv2.waitKey(5) & 0xFF
            if k == 27:
                break
        cv2.destroyWindow(title)
    
    def _threadCamera2(self, title):
        while(1):
            self.img = self.cap.read()[1]
            self.img = self.img[0:300,:]
            self._getImageLines(votes=100, filter=True)
            self._drawLines()
            cv2.imshow(title,self.img)
            k = cv2.waitKey(5) & 0xFF
            if k == 27:
                break
        cv2.destroyWindow(title)
    
    def showCamera(self):
        t = threading.Thread(target = self._threadCamera, args=(self.name + ': Press Esc to close',))
        t.start()
    
    def showCamera2(self):
        t = threading.Thread(target = self._threadCamera2, args=(self.name + ': Press Esc to close',))
        t.start()
    
    # HELPER FUNCTIONS
    
    def _beginScript(self):
        self.script_running = True
    
    def _endScript(self):
        self.script_running = False
    
    def _getIndex(self, lines):
        '''
            Returns the index of the line with lowest rho value generated
            by cv2.HoughLines 
        '''
        r = []
        for rho,theta in lines:
            r.append(rho)
        return min(range(len(r)), key=r.__getitem__)

    def _drawLines(self):
        '''
            Draws specified line in the output array of cv2.HoughLines
        '''
        if hasattr(self.lines, '__iter__'):
            if self.line_type=='list':
                for rho, theta in self.lines:
                    a = np.cos(theta)
                    b = np.sin(theta)
                    
                    x0 = a*rho
                    y0 = b*rho
                    
                    x1 = int(x0 + 1000*(-b))
                    y1 = int(y0 + 1000*(a))
                    x2 = int(x0 - 1000*(-b))
                    y2 = int(y0 - 1000*(a))

                    cv2.line(self.img,(x1,y1),(x2,y2),(0,0,255),2)
            
            if self.line_type == 'dict':
                for line in self.lines:
                    rho, theta = self.lines[line]
                    
                    a = np.cos(theta)
                    b = np.sin(theta)
                    
                    x0 = a*rho
                    y0 = b*rho
                    
                    if line == 'chip':
                        y0 += self.split
                    
                    x1 = int(x0 + 1000*(-b))
                    y1 = int(y0 + 1000*(a))
                    x2 = int(x0 - 1000*(-b))
                    y2 = int(y0 - 1000*(a))
                    
                    cv2.line(self.img,(x1,y1),(x2,y2),(0,0,255),2)
        
    def _filterLines(self, lines, max_theta):
        '''
            Takes the output of HoughLines and filters its results based on
            some pre-defined angle limits
        '''
        t = []
        i = []
        r = []
        for rho, theta in lines[0]:
            t.append(self._convertTheta(theta))
        for theta in t:
            if abs(theta) <= max_theta:
                i.append(t.index(theta))
        i = set(i)
        for index in i:
            rho, theta = lines[0][index]
            r.append([rho, theta])
        return r
        
    def _convertTheta(self, theta):
        '''
            Changes reference of the cv2.HoughLines line theta
        '''
        return theta*(180/np.pi) - 90

    def _getImageLines(self, img=None, votes=200, filter=False, max_theta=15):
        '''
            run cv2.HoughLines algorithm on specified region of frame
            returns array of lines
        '''
        if not np.any(img):
            img = self.read()[1]
        # converting BGR to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
         
        # define range of red color in HSV
        lower_red = np.array([30,150,50])
        upper_red = np.array([255,255,180])
         
        # create a red HSV colour boundary and 
        # threshold HSV image
        mask = cv2.inRange(hsv, lower_red, upper_red)
     
        # Bitwise-AND mask and original image
        res = cv2.bitwise_and(img,img, mask= mask)
        
        # finds edges in the input image image and
        # marks them in the output map edges
        edges = cv2.Canny(img,100,200)
        lines = cv2.HoughLines(edges,1,np.pi/180*self.resolution,votes)
        if hasattr(lines, '__iter__'):
            if filter:
                lines = self._filterLines(lines, max_theta)
                return lines
            elif self.line_type == 'list':
                self.lines = lines[0]
            elif self.line_type == 'dict':
                return lines[0]
    
    def _setRegVar(self, regions):
        self.regions = regions
    
    def getRegionLines(self):
        '''
            return the data for all lines gathered in each region of image
        '''
        for region in self.regions:
            if region[0] == 'fiber':
                lines = self._getImageLines(region[1],80,True)
            else:
                lines = self._getImageLines(region[1],filter=False)
            if hasattr(lines, '__iter__'):
                index = self._getIndex(lines)
                rho, theta = lines[index]
                self.lines[region[0]] = list((rho, theta))
    
    def _showRegionLines(self):
        '''
            Show the image with detected lines drawn. Used for detecting fiber
            and chip lines simultaneously.
        '''
        self.line_type = 'dict'
        self.lines = {}
        t = threading.Thread(target=self._showImg, args=('Running...',))
        t2 = threading.Thread(target=self._updateLineDict)
        t.start()
        t2.start()
    
    def _showImg(self,title):
        '''
            Used to display camera feed while scripts are running
        '''
        while(self.script_running):
            self.img = self.read()[1]
            self._drawLines()
            cv2.imshow(title,self.img)
            k = cv2.waitKey(5)
        cv2.destroyWindow(title)
        exit()
    
    def _updateLineList(self):
        '''
            Updates list of detected lines for the entire image
        '''
        while(self.script_running):
            self._getImageLines()
            index = self._getIndex(self.lines)
            self.lines = [list(self.lines[index])]

    def _updateLineDict(self):
        '''
            Updates dictionary of detected lines when more than one region
            being processed
        '''
        while(self.script_running):
            frame = self.read()[1]
            chip = frame[self.split:,:]
            fiber = frame[0:self.split-1,:]
            self.regions = [['chip', chip],['fiber',fiber]]
            self.getRegionLines()

    def _reset(self):
        '''
            Resets the parameters changed for running line detection
            scripts
        '''
        self.lines = []
        self.regions = []
        self.split = 0
        self.line_type='list'
        self.resolution = 0.1
    
    def _setRes(self, res):
        self.resolution = res
    
    def _showLines(self):
        '''
            Show the image with detected lines drawn. Used for detecting first 
            line drawn in an image.
        '''
        self.line_type='list'
        t = threading.Thread(target=self._showImg, args=('Running Script...',))
        t.start()
        t2 = threading.Thread(target=self._updateLineList)
        t2.start()
    
    def _setRegion(self):
        '''
            Takes user input on how to split the recieved image for fiber/chip
            alignment scripts
        '''
        title = 'Set Split'
        self.split = 0
        while(1):
            frame = self.cap.read()[1]
            cv2.namedWindow(title)
            cv2.setMouseCallback(title, self._setSplit)
            cv2.imshow(title,frame)
            cv2.waitKey(5)
            if self.split != 0:
                break
        cv2.destroyWindow(title)    
    
    def _setSplit(self,event,x,y,flags,param):
        '''
            Handler function for setting the split of an image
        '''
        if event == cv2.EVENT_LBUTTONDOWN:
            self.split = y
            
    # EXPERIMENTAL
    def _displ(self):
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
    def _get_coord(self, secs = 1, wait = False, boxCoor = False, thrd = None):
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
        
    
    def _get_from_map(self, image_filename):
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
