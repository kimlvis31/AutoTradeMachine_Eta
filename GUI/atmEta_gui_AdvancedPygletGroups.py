import math
import time

import pyglet

class cameraGroup(pyglet.graphics.Group):
    def __init__(self, window, viewport_x = 0, viewport_y = 0, viewport_width = 1, viewport_height = 1, projection_x0 = 0, projection_x1 = 1, projection_y0 = 0, projection_y1 = 1, projection_z0 = 0, projection_z1 = 1, parentCameraGroup = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #Unique Identifier
        self.__objectID = id(self)

        #Window
        self.window = window
        self.projectionMatrix_Default = self.window.projection
        self.viewport_Default         = self.window.viewport

        #Viewport Parameters
        self.viewport_x      = viewport_x;      self.viewport_x_effective      = viewport_x;      self.viewport_x_onScreen      = viewport_x
        self.viewport_y      = viewport_y;      self.viewport_y_effective      = viewport_y;      self.viewport_y_onScreen      = viewport_y
        self.viewport_width  = viewport_width;  self.viewport_width_effective  = viewport_width;  self.viewport_width_onScreen  = viewport_width
        self.viewport_height = viewport_height; self.viewport_height_effective = viewport_height; self.viewport_height_onScreen = viewport_height
        self.viewport_onScreen = (self.viewport_x_onScreen, self.viewport_y_onScreen, self.viewport_width_onScreen, self.viewport_height_onScreen)
        self.viewport_effectiveHide = False

        #Projection Matrix
        self.projection_x0 = projection_x0; self.projection_x1 = projection_x1; self.projection_x0_effective = self.projection_x0; self.projection_x1_effective = self.projection_x1
        self.projection_y0 = projection_y0; self.projection_y1 = projection_y1; self.projection_y0_effective = self.projection_y0; self.projection_y1_effective = self.projection_y1
        self.projection_z0 = projection_z0; self.projection_z1 = projection_z1; self.projection_z0_effective = self.projection_z0; self.projection_z1_effective = self.projection_z1
        self.projectionMatrix = pyglet.math.Mat4.orthogonal_projection(self.projection_x0_effective, self.projection_x1_effective, self.projection_y0_effective, self.projection_y1_effective, self.projection_z0_effective, self.projection_z1_effective)

        #CameraGroup Conneciton
        self.parentCameraGroup = parentCameraGroup
        self.childCameraGroups = list()
        self.followerCameraGroups = list()
        if (self.parentCameraGroup != None): self.parentCameraGroup.registerChildCameraGroup(self)

        #Object Status
        self.hidden = False
        self.visible = True
        self.deactivated = False

        self.__updateEffectiveViewport()
        
    def show(self):
        if (self.viewport_effectiveHide == False): self.visible = True
        self.hidden = False

    def hide(self):
        self.visible = False
        self.hidden = True

    def activate(self):
        self.deactivated = False

    def deactivate(self):
        self.deactivated = True

    def set_state(self):
        self.window.projection = self.projectionMatrix
        self.window.viewport = self.viewport_onScreen

    def unset_state(self):
        self.window.projection = self.projectionMatrix_Default
        self.window.viewport   = self.viewport_Default

    def followCamGroup(self, leaderCamGroup):
        if (self.deactivated == False):
            #Viewport Parameters
            self.viewport_x      = leaderCamGroup.viewport_x;      self.viewport_x_effective      = leaderCamGroup.viewport_x_effective;      self.viewport_x_onScreen      = leaderCamGroup.viewport_x_onScreen
            self.viewport_y      = leaderCamGroup.viewport_y;      self.viewport_y_effective      = leaderCamGroup.viewport_y_effective;      self.viewport_y_onScreen      = leaderCamGroup.viewport_y_onScreen
            self.viewport_width  = leaderCamGroup.viewport_width;  self.viewport_width_effective  = leaderCamGroup.viewport_width_effective;  self.viewport_width_onScreen  = leaderCamGroup.viewport_width_onScreen
            self.viewport_height = leaderCamGroup.viewport_height; self.viewport_height_effective = leaderCamGroup.viewport_height_effective; self.viewport_height_onScreen = leaderCamGroup.viewport_height_onScreen
            self.viewport_onScreen = leaderCamGroup.viewport_onScreen
            self.viewport_effectiveHide = leaderCamGroup.viewport_effectiveHide; self.visible = leaderCamGroup.visible; self.hidden = leaderCamGroup.hidden

            #Projection Matrix
            self.projection_x0 = leaderCamGroup.projection_x0; self.projection_x1 = leaderCamGroup.projection_x1; self.projection_x0_effective = leaderCamGroup.projection_x0_effective; self.projection_x1_effective = leaderCamGroup.projection_x1_effective
            self.projection_y0 = leaderCamGroup.projection_y0; self.projection_y1 = leaderCamGroup.projection_y1; self.projection_y0_effective = leaderCamGroup.projection_y0_effective; self.projection_y1_effective = leaderCamGroup.projection_y1_effective
            self.projection_z0 = leaderCamGroup.projection_z0; self.projection_z1 = leaderCamGroup.projection_z1; self.projection_z0_effective = leaderCamGroup.projection_z0_effective; self.projection_z1_effective = leaderCamGroup.projection_z1_effective
            self.projectionMatrix = leaderCamGroup.projectionMatrix

            for childCameraGroup in self.childCameraGroups: childCameraGroup.onParentCamGroupUpdate()

    def updateProjection(self, projection_x0 = None, projection_x1 = None, projection_y0 = None, projection_y1 = None, projection_z0 = None, projection_z1 = None):
        if (projection_x0 != None): self.projection_x0 = projection_x0
        if (projection_x1 != None): self.projection_x1 = projection_x1
        if (projection_y0 != None): self.projection_y0 = projection_y0
        if (projection_y1 != None): self.projection_y1 = projection_y1
        if (projection_z0 != None): self.projection_z0 = projection_z0
        if (projection_z1 != None): self.projection_z1 = projection_z1
        self.__updateEffectiveProjection()

    def updateViewport(self, viewport_x = None, viewport_y = None, viewport_width = None, viewport_height = None):
        if (viewport_x      != None): self.viewport_x      = viewport_x
        if (viewport_y      != None): self.viewport_y      = viewport_y
        if (viewport_width  != None): self.viewport_width  = viewport_width
        if (viewport_height != None): self.viewport_height = viewport_height
        self.__updateEffectiveViewport()

    def isTouched(self, xInViewportSpace, yInViewportSpace):
        if ((self.viewport_x_effective <= xInViewportSpace)                                        and
            (xInViewportSpace          <= self.viewport_x_effective+self.viewport_width_effective) and
            (self.viewport_y_effective <= yInViewportSpace)                                        and
            (yInViewportSpace          <= self.viewport_y_effective+self.viewport_height_effective)): return True
        else: return False

    def registerChildCameraGroup(self, childCameraGroup):
        self.childCameraGroups.append(childCameraGroup)

    def registerFollowerCameraGroup(self, followerCameraGroup):
        self.followerCameraGroups.append(followerCameraGroup)

    def onParentCamGroupUpdate(self):
        if (self.deactivated == False): self.__updateEffectiveViewport()

    def __updateEffectiveProjection(self):
        if (self.parentCameraGroup == None):
            self.projection_x0_effective = self.projection_x0
            self.projection_x1_effective = self.projection_x1
            self.projection_y0_effective = self.projection_y0
            self.projection_y1_effective = self.projection_y1
            self.projection_z0_effective = self.projection_z0
            self.projection_z1_effective = self.projection_z1
            self.projectionMatrix = pyglet.math.Mat4.orthogonal_projection(self.projection_x0_effective, self.projection_x1_effective, self.projection_y0_effective, self.projection_y1_effective, self.projection_z0_effective, self.projection_z1_effective)
            for followerCameraGroup in self.followerCameraGroups: followerCameraGroup.followCamGroup(self)
            for childCameraGroup in self.childCameraGroups: childCameraGroup.onParentCamGroupUpdate()
        else: self.__updateEffectiveViewport()
        
    def __updateEffectiveViewport(self):
        if (self.parentCameraGroup == None):
            self.viewport_x_effective      = self.viewport_x;      self.viewport_x_onScreen      = self.viewport_x_effective
            self.viewport_y_effective      = self.viewport_y;      self.viewport_y_onScreen      = self.viewport_y_effective
            self.viewport_width_effective  = self.viewport_width;  self.viewport_width_onScreen  = self.viewport_width_effective
            self.viewport_height_effective = self.viewport_height; self.viewport_height_onScreen = self.viewport_height_effective
            self.viewport_onScreen = (self.viewport_x_onScreen, self.viewport_y_onScreen, self.viewport_width_onScreen, self.viewport_height_onScreen)
        else:
            # -----------------------------------------------------------------------------#
            # *** My Viewport and Parent's Projection are in the same coordinate space *** #
            # -----------------------------------------------------------------------------#
            # Effective Viewport Represents clipped & resolution scaled (is in pixels) position and width

            #Coordinate Delta Classification
            deltaX_class = 0
            deltaX_c0p0 = self.viewport_x                         - self.parentCameraGroup.projection_x0_effective; deltaX_class += 0b1000*(0 <= deltaX_c0p0)
            deltaX_c0p1 = self.viewport_x                         - self.parentCameraGroup.projection_x1_effective; deltaX_class += 0b0100*(0 <= deltaX_c0p1)
            deltaX_c1p0 = (self.viewport_x + self.viewport_width) - self.parentCameraGroup.projection_x0_effective; deltaX_class += 0b0010*(0 <  deltaX_c1p0)
            deltaX_c1p1 = (self.viewport_x + self.viewport_width) - self.parentCameraGroup.projection_x1_effective; deltaX_class += 0b0001*(0 <  deltaX_c1p1)
            
            deltaY_class = 0
            deltaY_c0p0 = self.viewport_y                          - self.parentCameraGroup.projection_y0_effective; deltaY_class += 0b1000*(0 <= deltaY_c0p0)
            deltaY_c0p1 = self.viewport_y                          - self.parentCameraGroup.projection_y1_effective; deltaY_class += 0b0100*(0 <= deltaY_c0p1)
            deltaY_c1p0 = (self.viewport_y + self.viewport_height) - self.parentCameraGroup.projection_y0_effective; deltaY_class += 0b0010*(0 <  deltaY_c1p0)
            deltaY_c1p1 = (self.viewport_y + self.viewport_height) - self.parentCameraGroup.projection_y1_effective; deltaY_class += 0b0001*(0 <  deltaY_c1p1)
            
            deltaZ_class = 0
            deltaZ_c0p0 = self.projection_z0 - self.parentCameraGroup.projection_z0_effective; deltaZ_class += 0b1000*(0 <= deltaZ_c0p0)
            deltaZ_c0p1 = self.projection_z0 - self.parentCameraGroup.projection_z1_effective; deltaZ_class += 0b0100*(0 <= deltaZ_c0p1)
            deltaZ_c1p0 = self.projection_z1 - self.parentCameraGroup.projection_z0_effective; deltaZ_class += 0b0010*(0 <  deltaZ_c1p0)
            deltaZ_c1p1 = self.projection_z1 - self.parentCameraGroup.projection_z1_effective; deltaZ_class += 0b0001*(0 <  deltaZ_c1p1)

            if ((deltaX_class == 0b0000) or (deltaX_class == 0b1111) or (deltaY_class == 0b0000) or (deltaY_class == 0b1111) or (deltaZ_class == 0b0000) or (deltaZ_class == 0b1111)): 
                if (self.viewport_effectiveHide == False): self.visible = False; self.viewport_effectiveHide = True
            else:
                #<X>
                #Show all
                if (deltaX_class == 0b1010):
                    #Viewport
                    self.viewport_x_effective     = self.viewport_x
                    self.viewport_width_effective = self.viewport_width
                    #Effective Projection
                    self.projection_x0_effective = self.projection_x0
                    self.projection_x1_effective = self.projection_x1

                #Left Clipped
                elif (deltaX_class == 0b0010):
                    clippedViewportWidth   = -deltaX_c0p0
                    clippedProjectionWidth = (self.projection_x1-self.projection_x0) * clippedViewportWidth / self.viewport_width
                    #Viewport
                    self.viewport_x_effective     = self.parentCameraGroup.projection_x0_effective
                    self.viewport_width_effective = self.viewport_width-clippedViewportWidth
                    #Effective Projection
                    self.projection_x0_effective = self.projection_x0 + clippedProjectionWidth
                    self.projection_x1_effective = self.projection_x1

                #Right Clipped
                elif (deltaX_class == 0b1011):
                    clippedViewportWidth   = deltaX_c1p1
                    clippedProjectionWidth = (self.projection_x1-self.projection_x0) * clippedViewportWidth / self.viewport_width
                    #Viewport
                    self.viewport_width_effective = self.viewport_width-clippedViewportWidth
                    self.viewport_x_effective     = self.parentCameraGroup.projection_x1_effective - self.viewport_width_effective
                    #Effective Projection
                    self.projection_x0_effective = self.projection_x0
                    self.projection_x1_effective = self.projection_x1 - clippedProjectionWidth

                #Left&Right Clipped
                elif (deltaX_class == 0b0011):
                    clippedViewportWidth_left  = -deltaX_c0p0
                    clippedViewportWidth_right =  deltaX_c1p1
                    clippedProjectionWidth_left  = (self.projection_x1-self.projection_x0) * clippedViewportWidth_left  / self.viewport_width
                    clippedProjectionWidth_right = (self.projection_x1-self.projection_x0) * clippedViewportWidth_right / self.viewport_width
                    #Viewport
                    self.viewport_x_effective     = self.parentCameraGroup.projection_x0_effective
                    self.viewport_width_effective = self.parentCameraGroup.projection_x1_effective-self.parentCameraGroup.projection_x0_effective
                    #Effective Projection
                    self.projection_x0_effective = self.projection_x0 + clippedProjectionWidth_left
                    self.projection_x1_effective = self.projection_x1 - clippedProjectionWidth_right
                #<X>
                #Show all
                if (deltaY_class == 0b1010):
                    #Viewport
                    self.viewport_y_effective      = self.viewport_y
                    self.viewport_height_effective = self.viewport_height
                    #Effective Projection
                    self.projection_y0_effective = self.projection_y0
                    self.projection_y1_effective = self.projection_y1

                #Bottom Clipped
                elif (deltaY_class == 0b0010):
                    clippedViewportHeight   = -deltaY_c0p0
                    clippedProjectionHeight = (self.projection_y1-self.projection_y0) * clippedViewportHeight / self.viewport_height
                    #Viewport
                    self.viewport_y_effective      = self.parentCameraGroup.projection_y0_effective
                    self.viewport_height_effective = self.viewport_height-clippedViewportHeight
                    #Effective Projection
                    self.projection_y0_effective = self.projection_y0 + clippedProjectionHeight
                    self.projection_y1_effective = self.projection_y1

                #Right Clipped
                elif (deltaY_class == 0b1011):
                    clippedViewportHeight   = deltaY_c1p1
                    clippedProjectionHeight = (self.projection_y1-self.projection_y0) * clippedViewportHeight / self.viewport_height
                    #Viewport
                    self.viewport_height_effective = self.viewport_height-clippedViewportHeight
                    self.viewport_y_effective      = self.parentCameraGroup.projection_y1_effective - self.viewport_height_effective
                    #Effective Projection
                    self.projection_y0_effective = self.projection_y0
                    self.projection_y1_effective = self.projection_y1 - clippedProjectionHeight

                #Bottom&Top Clipped
                elif (deltaY_class == 0b0011):
                    clippedViewportHeight_bottom = -deltaY_c0p0
                    clippedViewportHeight_top    =  deltaY_c1p1
                    clippedProjectionHeight_bottom = (self.projection_y1-self.projection_y0) * clippedViewportHeight_bottom  / self.viewport_height
                    clippedProjectionHeight_top    = (self.projection_y1-self.projection_y0) * clippedViewportHeight_top     / self.viewport_height
                    #Viewport
                    self.viewport_y_effective      = self.parentCameraGroup.projection_y0_effective
                    self.viewport_height_effective = self.parentCameraGroup.projection_y1_effective-self.parentCameraGroup.projection_y0_effective
                    #Effective Projection
                    self.projection_y0_effective = self.projection_y0 + clippedProjectionHeight_bottom
                    self.projection_y1_effective = self.projection_y1 - clippedProjectionHeight_top
                #<Z>
                #Show all
                if (deltaZ_class == 0b1010):
                    self.projection_z0_effective = self.projection_z0
                    self.projection_z1_effective = self.projection_z1
                #Bottom Clipped
                elif (deltaZ_class == 0b0010):
                    clippedProjectionWidth = -deltaZ_c0p0
                    self.projection_z0_effective = self.projection_z0 + clippedProjectionWidth
                    self.projection_z1_effective = self.projection_z1
                #Top Clipped
                elif (deltaZ_class == 0b1011):
                    clippedProjectionWidth = deltaZ_c1p1
                    self.projection_z0_effective = self.projection_z0
                    self.projection_z1_effective = self.projection_z1 - clippedProjectionWidth
                #Bottom&Top Clipped
                elif (deltaZ_class == 0b0011):
                    clippedProjectionWidth_near = -deltaZ_c0p0
                    clippedProjectionWidth_far  =  deltaZ_c1p1
                    self.projection_z0_effective = self.projection_z0 + clippedProjectionWidth_near
                    self.projection_z1_effective = self.projection_z1 - clippedProjectionWidth_far
                 
                if (self.hidden == False): self.visible = True
                self.viewport_effectiveHide = False
                
                resolutionScaleMultiplier_x = self.parentCameraGroup.viewport_width_onScreen  / (self.parentCameraGroup.projection_x1_effective-self.parentCameraGroup.projection_x0_effective)
                resolutionScaleMultiplier_y = self.parentCameraGroup.viewport_height_onScreen / (self.parentCameraGroup.projection_y1_effective-self.parentCameraGroup.projection_y0_effective)

                self.viewport_x_onScreen      = self.parentCameraGroup.viewport_x_onScreen + (self.viewport_x_effective-self.parentCameraGroup.projection_x0_effective)*resolutionScaleMultiplier_x
                self.viewport_y_onScreen      = self.parentCameraGroup.viewport_y_onScreen + (self.viewport_y_effective-self.parentCameraGroup.projection_y0_effective)*resolutionScaleMultiplier_y
                self.viewport_width_onScreen  = self.viewport_width_effective *resolutionScaleMultiplier_x
                self.viewport_height_onScreen = self.viewport_height_effective*resolutionScaleMultiplier_y
                
                self.viewport_onScreen = (self.viewport_x_onScreen, self.viewport_y_onScreen, self.viewport_width_onScreen, self.viewport_height_onScreen)
                self.projectionMatrix = pyglet.math.Mat4.orthogonal_projection(self.projection_x0_effective, self.projection_x1_effective, self.projection_y0_effective, self.projection_y1_effective, self.projection_z0_effective, self.projection_z1_effective)
        for followerCameraGroup in self.followerCameraGroups: followerCameraGroup.followCamGroup(self)
        for childCameraGroup in self.childCameraGroups: childCameraGroup.onParentCamGroupUpdate()
                
    def __eq__(self, other):
        try:    return (super().__eq__(other) and self.__objectID == other.__objectID)
        except: return False
    
    def __hash__(self):
        return hash((self._order, self.parent))

    def printInfo(self):
        print("1. Viewport:             ({:s}, {:s}, {:s}, {:s})\
               \n2. Viewport_Effective:   ({:s}, {:s}, {:s}, {:s})\
               \n3. Viewport_onScreen:    ({:s}, {:s}, {:s}, {:s})\
               \n4. Projection:           ({:s}, {:s}, {:s}, {:s})\
               \n5. Projeciton_Effective: ({:s}, {:s}, {:s}, {:s})".format(str(self.viewport_x),              str(self.viewport_y),              str(self.viewport_width),           str(self.viewport_height),
                                                                           str(self.viewport_x_effective),    str(self.viewport_y_effective),    str(self.viewport_width_effective), str(self.viewport_height_effective),
                                                                           str(self.viewport_x_onScreen),     str(self.viewport_y_onScreen),     str(self.viewport_width_onScreen),  str(self.viewport_height_onScreen),
                                                                           str(self.projection_x0),           str(self.projection_x1),           str(self.projection_y0),            str(self.projection_y1),
                                                                           str(self.projection_x0_effective), str(self.projection_x1_effective), str(self.projection_y0_effective),  str(self.projection_y1_effective)))



class layeredCameraGroup:
    def __init__(self, window, viewport_x = 0, viewport_y = 0, viewport_width = 1, viewport_height = 1, projection_x0 = 0, projection_x1 = 1, projection_y0 = 0, projection_y1 = 1, projection_z0 = 0, projection_z1 = 1, order = None, parentCameraGroup = None):
        #Window
        self.window = window
        
        #Parent & Child cameraGroup
        if (order == None): self.order = parentCameraGroup.order+1
        else:               self.order = order

        self.groups = {0: cameraGroup(window = self.window, viewport_x = viewport_x, viewport_y = viewport_y, viewport_width = viewport_width, viewport_height = viewport_height, order = self.order, parentCameraGroup = parentCameraGroup,
                                      projection_x0 = projection_x0, projection_x1 = projection_x1, projection_y0 = projection_y0, projection_y1 = projection_y1, projection_z0 = projection_z0, projection_z1 = projection_z1)}

        #Object Status
        self.hidden = False

    def show(self):
        self.hidden = False
        for group in self.groups.values(): group.show()

    def hide(self):
        self.hidden = True
        for group in self.groups.values(): group.hide()

    def activate(self):
        self.groups[0].activate()

    def deactivate(self):
        self.groups[0].deactivate()

    def isTouched(self, xInViewportSpace, yInViewportSpace):
        return self.groups[0].isTouched(xInViewportSpace, yInViewportSpace)

    def updateProjection(self, projection_x0 = None, projection_x1 = None, projection_y0 = None, projection_y1 = None, projection_z0 = None, projection_z1 = None):
        self.groups[0].updateProjection(projection_x0, projection_x1, projection_y0, projection_y1, projection_z0, projection_z1)

    def updateViewport(self, viewport_x = None, viewport_y = None, viewport_width = None, viewport_height = None):
        self.groups[0].updateViewport(viewport_x, viewport_y, viewport_width, viewport_height)

    def getGroups(self, groupRange0, groupRange1):
        groupInstances = dict()
        for index, groupNumber in enumerate(range(groupRange0, groupRange1+1)): groupInstances["group_{:d}".format(index)] = self.__getGroup(groupNumber)
        return groupInstances

    def getProjectionSpaceCoordinate(self, xInViewportSpace, yInViewportSpace):
        leaderGroup = self.groups[0]
        xInProjectionSpace = leaderGroup.projection_x0_effective+(xInViewportSpace-leaderGroup.viewport_x_effective)*(leaderGroup.projection_x1_effective-leaderGroup.projection_x0_effective)/leaderGroup.viewport_width_effective
        yInProjectionSpace = leaderGroup.projection_y0_effective+(yInViewportSpace-leaderGroup.viewport_y_effective)*(leaderGroup.projection_y1_effective-leaderGroup.projection_y0_effective)/leaderGroup.viewport_height_effective
        return (xInProjectionSpace, yInProjectionSpace)

    def getOnScreenViewport(self):
        return (self.groups[0].viewport_x_onScreen, self.groups[0].viewport_y_onScreen, self.groups[0].viewport_width_onScreen, self.groups[0].viewport_height_onScreen)

    def __getGroup(self, groupNumber):
        if (groupNumber in self.groups): return self.groups[groupNumber]
        else:
            self.groups[groupNumber] = cameraGroup(window = self.window, order = self.order+groupNumber)
            self.groups[groupNumber].followCamGroup(leaderCamGroup=self.groups[0])
            self.groups[0].registerFollowerCameraGroup(self.groups[groupNumber])
            return self.groups[groupNumber]

    def printGroupInfo(self):
        visibilities = []
        for index, group in enumerate(self.groups.values()): visibilities.append(group.visible)
        print("[{:d}] - Viewport: {:s}, Projection: {:s},".format(index, str((self.groups[0].viewport_x, self.groups[0].viewport_y, self.groups[0].viewport_width, self.groups[0].viewport_height)), str((self.groups[0].projection_x0, self.groups[0].projection_x1, self.groups[0].projection_y0, self.groups[0].projection_y1))))
        print("    - Visibilities: {:s}".format(str(visibilities)))
        


_RCLCG_SHAPETYPE_LINE              =  0
_RCLCG_SHAPETYPE_BEZIERCURVE       =  1
_RCLCG_SHAPETYPE_ARC               =  2
_RCLCG_SHAPETYPE_TRIANGLE          =  3
_RCLCG_SHAPETYPE_RECTANGLE         =  4
_RCLCG_SHAPETYPE_BORDEREDRECTANGLE =  5
_RCLCG_SHAPETYPE_BOX               =  6
_RCLCG_SHAPETYPE_CIRCLE            =  7
_RCLCG_SHAPETYPE_ELLIPSE           =  8
_RCLCG_SHAPETYPE_SECTOR            =  9
_RCLCG_SHAPETYPE_POLYGON           = 10
_RCLCG_WIDTHMULTIPLIER = 1e3
class resolutionControlledLayeredCameraGroup:
    def __init__(self, window, batch, 
                 viewport_x, viewport_y, viewport_width, viewport_height, 
                 projection_x0 = 0, projection_x1 = 1, projection_y0 = 0, projection_y1 = 1, projection_z0 = 0, projection_z1 = 1, 
                 precision_x = 0, precision_y = 0,
                 fsdResolution_x = 10, fsdResolution_y = 10,
                 order = None, parentCameraGroup = None):
        self.window = window
        self.batch  = batch
        if (order == None): self.order = parentCameraGroup.order+1
        else:               self.order = order
        
        #Resolution Control
        self.resMultiplier_x = 1/pow(10, precision_x)
        self.resMultiplier_y = 1/pow(10, precision_y)

        #Group Setup
        self.mainCamGroup = cameraGroup(self.window, viewport_x, viewport_y, viewport_width, viewport_height, projection_x0, projection_x1, projection_y0, projection_y1, projection_z0, projection_z1, parentCameraGroup = parentCameraGroup, order = self.order)
        self.mainCamGroup.registerChildCameraGroup(self)
        
        #LCG Control
        self.LCGs = dict()
        self.LCGSizeTable = dict()
        self.activeLCGSize   = None
        self.activeLCGSizeID = None
        self.shapeDescriptions_ungrouped = dict()
        self.shapeDescriptions_grouped   = dict()

        self.LCG_FSDRESOLUTION_X = fsdResolution_x
        self.LCG_FSDRESOLUTION_Y = fsdResolution_y
        
    def processShapeGenerationQueue(self, timeout_ns, currentFocusOnly = False):
        timer_processBeg_ns = time.perf_counter_ns()
        #[1]: Process only within the current focus
        if (currentFocusOnly == True):
            if (self.activeLCGSizeID != None):
                #Find positionIDs within the current projection area
                eProj_x0 = self.mainCamGroup.projection_x0_effective
                eProj_x1 = self.mainCamGroup.projection_x1_effective
                eProj_y0 = self.mainCamGroup.projection_y0_effective
                eProj_y1 = self.mainCamGroup.projection_y1_effective
                lcgSize_x = self.LCGSizeTable[self.activeLCGSizeID][4]
                lcgSize_y = self.LCGSizeTable[self.activeLCGSizeID][5]
                if (0 <= eProj_x0): lcgPosition_leftmost   = int(eProj_x0/lcgSize_x)
                else:               lcgPosition_leftmost   = int(eProj_x0/lcgSize_x)-1
                if (0 <= eProj_x1): lcgPosition_rightmost  = int(eProj_x1/lcgSize_x)
                else:               lcgPosition_rightmost  = int(eProj_x1/lcgSize_x)-1
                if (0 <= eProj_y0): lcgPosition_bottommost = int(eProj_y0/lcgSize_y)
                else:               lcgPosition_bottommost = int(eProj_y0/lcgSize_y)-1
                if (0 <= eProj_y1): lcgPosition_topmost    = int(eProj_y1/lcgSize_y)
                else:               lcgPosition_topmost    = int(eProj_y1/lcgSize_y)-1
                lcgPositionIDsInVR = list()
                for lcgPosition_x in range (lcgPosition_leftmost, lcgPosition_rightmost+1):
                    for lcgPosition_y in range (lcgPosition_bottommost, lcgPosition_topmost+1):
                        lcgPositionIDInVR = "{:d}_{:d}".format(lcgPosition_x, lcgPosition_y)
                        if (lcgPositionIDInVR in self.LCGs[self.activeLCGSizeID]): lcgPositionIDsInVR.append(lcgPositionIDInVR)
                #Until Timeout Occurs, process shape generation queues
                while (time.perf_counter_ns()-timer_processBeg_ns < timeout_ns):
                    target = None
                    #Loop through LCGs within the current focus until a target is found
                    for positionID in lcgPositionIDsInVR:
                        target = self.__processShapeGenerationQueue_searchTargetWithinLCG(lcgSizeID = self.activeLCGSizeID, positionID = positionID)
                        if (target != None): break
                    if (target != None): self.__processShapeGenerationQueue_generateShapeInstance(target[0], target[1], target[2], target[3]) #If a target is found, process it and repeat the loop
                    else: return False                                                                                                        #If no target is found, return False to indicate there exist no shape generation queues to process within the current focus
                return True
            else: return False
        #[2]: Process within the entire space
        else:
            #Until Timeout Occurs, process shape generation queues
            while (time.perf_counter_ns()-timer_processBeg_ns < timeout_ns):
                target = None
                #Loop through LCGs within the current focus until a target is found
                for lcgSizeID in self.LCGs:
                    for positionID in self.LCGs[lcgSizeID]:
                        target = self.__processShapeGenerationQueue_searchTargetWithinLCG(lcgSizeID = lcgSizeID, positionID = positionID)
                        if (target != None): break
                    if (target != None): break
                if (target != None): self.__processShapeGenerationQueue_generateShapeInstance(target[0], target[1], target[2], target[3]) #If a target is found, process it and repeat the loop
                else: return False                                                                                                        #If no target is found, return False to indicate there exist no shape generation queues to process within the current focus
            return True
        
    def __processShapeGenerationQueue_searchTargetWithinLCG(self, lcgSizeID, positionID):
        targetLCG = self.LCGs[lcgSizeID][positionID]
        for shapeName in targetLCG['toProcess_shapes_ungrouped']: return (None, shapeName)
        for shapeGroupName in targetLCG['toProcess_shapes_grouped']:
            for shapeName in targetLCG['toProcess_shapes_grouped'][shapeGroupName]: return (lcgSizeID, positionID, shapeGroupName, shapeName)
        return None

    def __processShapeGenerationQueue_generateShapeInstance(self, lcgSizeID, positionID, shapeGroupName, shapeName):
        if (shapeGroupName == None): sigp = self.LCGs[lcgSizeID][positionID]['toProcess_shapes_ungrouped'][shapeGroupName];          del self.LCGs[lcgSizeID][positionID]['toProcess_shapes_ungrouped'][shapeGroupName]
        else:                        sigp = self.LCGs[lcgSizeID][positionID]['toProcess_shapes_grouped'][shapeGroupName][shapeName]; del self.LCGs[lcgSizeID][positionID]['toProcess_shapes_grouped'][shapeGroupName][shapeName]
        _shapeType = sigp['_shapeType']
        if   (_shapeType == _RCLCG_SHAPETYPE_LINE):              shapeInstance = pyglet.shapes.Polygon(*sigp['coordinates'], color = sigp['color'], batch = self.batch, group = self.LCGs[lcgSizeID][positionID]['LCG'].getGroups(sigp['layerNumber'], sigp['layerNumber'])['group_0'])
        elif (_shapeType == _RCLCG_SHAPETYPE_BEZIERCURVE):       return
        elif (_shapeType == _RCLCG_SHAPETYPE_ARC):               return
        elif (_shapeType == _RCLCG_SHAPETYPE_TRIANGLE):          return
        elif (_shapeType == _RCLCG_SHAPETYPE_RECTANGLE):         shapeInstance = pyglet.shapes.Rectangle(x = sigp['x'], y = sigp['y'], width = sigp['width'], height = sigp['height'], color = sigp['color'], 
                                                                                                         batch = self.batch, group = self.LCGs[lcgSizeID][positionID]['LCG'].getGroups(sigp['layerNumber'], sigp['layerNumber'])['group_0'])
        elif (_shapeType == _RCLCG_SHAPETYPE_BORDEREDRECTANGLE): return
        elif (_shapeType == _RCLCG_SHAPETYPE_BOX):               return
        elif (_shapeType == _RCLCG_SHAPETYPE_CIRCLE):            return
        elif (_shapeType == _RCLCG_SHAPETYPE_ELLIPSE):           return
        elif (_shapeType == _RCLCG_SHAPETYPE_SECTOR):            return
        elif (_shapeType == _RCLCG_SHAPETYPE_POLYGON):           shapeInstance = pyglet.shapes.Polygon(*sigp['coordinates'], color = sigp['color'], batch = self.batch, group = self.LCGs[lcgSizeID][positionID]['LCG'].getGroups(sigp['layerNumber'], sigp['layerNumber'])['group_0'])
        if (shapeGroupName == None):
            self.LCGs[lcgSizeID][positionID]['shapes_ungrouped'][shapeName] = shapeInstance
            self.shapeDescriptions_ungrouped[shapeName]['allocatedLCGs'].append((lcgSizeID, positionID))
            self.shapeDescriptions_ungrouped[shapeName]['allocatedLCGs_toProcess'].remove((lcgSizeID, positionID))
        else:
            if (shapeGroupName in self.LCGs[lcgSizeID][positionID]['shapes_grouped']): self.LCGs[lcgSizeID][positionID]['shapes_grouped'][shapeGroupName][shapeName] = shapeInstance
            else:                                                                      self.LCGs[lcgSizeID][positionID]['shapes_grouped'][shapeGroupName] = {shapeName: shapeInstance}
            self.shapeDescriptions_grouped[shapeGroupName][shapeName]['allocatedLCGs'].append((lcgSizeID, positionID))
            self.shapeDescriptions_grouped[shapeGroupName][shapeName]['allocatedLCGs_toProcess'].remove((lcgSizeID, positionID))
            

    def setPrecision(self, precision_x, precision_y, transferObjects = False):
        resMultiplier_x_previous = self.resMultiplier_x
        resMultiplier_y_previous = self.resMultiplier_y
        self.resMultiplier_x = 1/pow(10, precision_x)
        self.resMultiplier_y = 1/pow(10, precision_y)
        if (transferObjects == True):
            if (self.activeLCGSizeID != None):
                self.LCGs = {self.activeLCGSizeID: dict()}
                self.LCGSizeTable = {self.activeLCGSizeID: self.LCGSizeTable[self.activeLCGSizeID]}
                for shapeName in self.shapeDescriptions_ungrouped:
                    self.shapeDescriptions_ungrouped[shapeName]['allocatedLCGs'] = list()
                    self.__copyShapeToNewLCGSize(self.activeLCGSizeID, self.shapeDescriptions_ungrouped[shapeName], shapeName, None)
                for groupName in self.shapeDescriptions_grouped:
                    for shapeName in self.shapeDescriptions_grouped[groupName]: 
                        self.shapeDescriptions_grouped[groupName][shapeName]['allocatedLCGs'] = list()
                        self.__copyShapeToNewLCGSize(self.activeLCGSizeID, self.shapeDescriptions_grouped[groupName][shapeName], shapeName, groupName)
        else: self.clearAll()
        self.mainCamGroup.updateProjection(self.mainCamGroup.projection_x0/resMultiplier_x_previous*self.resMultiplier_x,
                                           self.mainCamGroup.projection_x1/resMultiplier_x_previous*self.resMultiplier_x,
                                           self.mainCamGroup.projection_y0/resMultiplier_y_previous*self.resMultiplier_y,
                                           self.mainCamGroup.projection_y1/resMultiplier_y_previous*self.resMultiplier_y)

    def onParentCamGroupUpdate(self):
        #X
        projectionWidth = self.mainCamGroup.projection_x1_effective-self.mainCamGroup.projection_x0_effective
        projectionWidth_OOM = math.floor(math.log(projectionWidth, 10))
        projectionWidth_MSD = int(projectionWidth/pow(10, projectionWidth_OOM))
        if (projectionWidth_MSD == 10): projectionWidth_MSD = 1; projectionWidth_OOM += 1
        newLCGSize_WidthMSD = (int(projectionWidth_MSD/self.LCG_FSDRESOLUTION_X)+1)*self.LCG_FSDRESOLUTION_X
        if (newLCGSize_WidthMSD == 10): newLCGSize_WidthMSD = 1;                   newLCGSize_WidthOOM = projectionWidth_OOM+1
        else:                           newLCGSize_WidthMSD = newLCGSize_WidthMSD; newLCGSize_WidthOOM = projectionWidth_OOM
        baseSize_x_MSD = newLCGSize_WidthMSD; baseSize_x_OOM = newLCGSize_WidthOOM
        if (newLCGSize_WidthOOM < 4): newLCGSize_HeightMSD = 1; newLCGSize_WidthOOM = 4
        
        #Y
        projectionHeight = self.mainCamGroup.projection_y1_effective-self.mainCamGroup.projection_y0_effective
        projectionHeight_OOM = math.floor(math.log(projectionHeight, 10))
        projectionHeight_MSD = int(projectionHeight/pow(10, projectionHeight_OOM))
        if (projectionHeight_MSD == 10): projectionHeight_MSD = 1; projectionHeight_OOM += 1
        newLCGSize_HeightMSD = (int(projectionHeight_MSD/self.LCG_FSDRESOLUTION_Y)+1)*self.LCG_FSDRESOLUTION_Y
        if (newLCGSize_HeightMSD == 10): newLCGSize_HeightMSD = 1;                    newLCGSize_HeightOOM = projectionHeight_OOM+1
        else:                            newLCGSize_HeightMSD = newLCGSize_HeightMSD; newLCGSize_HeightOOM = projectionHeight_OOM
        baseSize_y_MSD = newLCGSize_HeightMSD; baseSize_y_OOM = newLCGSize_HeightOOM
        if (newLCGSize_HeightOOM < 4): newLCGSize_HeightMSD = 1; newLCGSize_HeightOOM = 4

        #Tuple Format Construction
        newLCGSize = (newLCGSize_WidthMSD, newLCGSize_WidthOOM, baseSize_x_MSD, baseSize_x_OOM, newLCGSize_HeightMSD, newLCGSize_HeightOOM, baseSize_y_MSD, baseSize_y_OOM)

        #LCGSize Comparison & LCGSize Update Handler Call
        if (newLCGSize != self.activeLCGSize): self.__onLCGSizeUpdate(newLCGSize)
        
    def show(self): 
        self.mainCamGroup.show()
        if (self.activeLCGSizeID in self.LCGs):
            for positionID in self.LCGs[self.activeLCGSizeID]:
                self.LCGs[self.activeLCGSizeID][positionID]['LCG'].activate()
                self.LCGs[self.activeLCGSizeID][positionID]['LCG'].show()
    def hide(self): 
        self.mainCamGroup.hide()
        if (self.activeLCGSizeID in self.LCGs):
            for positionID in self.LCGs[self.activeLCGSizeID]:
                self.LCGs[self.activeLCGSizeID][positionID]['LCG'].deactivate()
                self.LCGs[self.activeLCGSizeID][positionID]['LCG'].hide()

    def updateProjection(self, projection_x0 = None, projection_x1 = None, projection_y0 = None, projection_y1 = None, projection_z0 = None, projection_z1 = None):
        if (projection_x0 != None): projection_x0 = projection_x0*self.resMultiplier_x
        if (projection_x1 != None): projection_x1 = projection_x1*self.resMultiplier_x
        if (projection_y0 != None): projection_y0 = projection_y0*self.resMultiplier_y
        if (projection_y1 != None): projection_y1 = projection_y1*self.resMultiplier_y
        self.mainCamGroup.updateProjection(projection_x0, projection_x1, projection_y0, projection_y1, projection_z0, projection_z1)

    def updateViewport(self, viewport_x, viewport_y, viewport_width, viewport_height): 
        self.mainCamGroup.updateViewport(viewport_x, viewport_y, viewport_width, viewport_height)





    def __onLCGSizeUpdate(self, newLCGSize):
        #Deactivate and hide the current size LCGs
        if (self.activeLCGSizeID != None):
            for positionID in self.LCGs[self.activeLCGSizeID]:
                self.LCGs[self.activeLCGSizeID][positionID]['LCG'].deactivate()
                self.LCGs[self.activeLCGSizeID][positionID]['LCG'].hide()

        #If the new size LCGs did previously exist, simply reactivate the new size LCGs
        self.activeLCGSize   = newLCGSize
        self.activeLCGSizeID = "{:d}_{:d}_{:d}_{:d}_{:d}_{:d}_{:d}_{:d}".format(newLCGSize[0], newLCGSize[1], newLCGSize[2], newLCGSize[3], newLCGSize[4], newLCGSize[5], newLCGSize[6], newLCGSize[7])
        if (self.activeLCGSizeID in self.LCGs):
            for positionID in self.LCGs[self.activeLCGSizeID]:
                self.LCGs[self.activeLCGSizeID][positionID]['LCG'].activate()
                self.LCGs[self.activeLCGSizeID][positionID]['LCG'].show()

        #If the new LCGSize did not previously exist, generate shapes for the new LCGSize
        else:
            self.LCGs[self.activeLCGSizeID] = dict()
            self.LCGSizeTable[self.activeLCGSizeID] = (self.activeLCGSize[0], self.activeLCGSize[1],           self.activeLCGSize[4], self.activeLCGSize[5],
                                                       self.activeLCGSize[0]*pow(10, self.activeLCGSize[1]),   self.activeLCGSize[4]*pow(10, self.activeLCGSize[5]),
                                                       self.activeLCGSize[2]*pow(10, self.activeLCGSize[3]-6), self.activeLCGSize[6]*pow(10, self.activeLCGSize[7]-6))
            for shapeName in self.shapeDescriptions_ungrouped: self.__copyShapeToNewLCGSize(self.activeLCGSizeID, self.shapeDescriptions_ungrouped[shapeName], shapeName, None)
            for groupName in self.shapeDescriptions_grouped:
                for shapeName in self.shapeDescriptions_grouped[groupName]: self.__copyShapeToNewLCGSize(self.activeLCGSizeID, self.shapeDescriptions_grouped[groupName][shapeName], shapeName, groupName)

    def __generateLCG(self, lcgSizeID, positionID):
        positionIDSplit = positionID.split("_")
        lcgSize_x = self.LCGSizeTable[lcgSizeID][4]; lcgPosition_x = lcgSize_x*int(positionIDSplit[0])
        lcgSize_y = self.LCGSizeTable[lcgSizeID][5]; lcgPosition_y = lcgSize_y*int(positionIDSplit[1])
        self.LCGs[lcgSizeID][positionID] = {'LCG': layeredCameraGroup(self.window, order = self.order, parentCameraGroup = self.mainCamGroup,
                                                                      viewport_x = lcgPosition_x, viewport_y = lcgPosition_y, viewport_width = lcgSize_x, viewport_height = lcgSize_y,
                                                                      projection_x0 = 0, projection_x1 = lcgSize_x, projection_y0 = 0, projection_y1 = lcgSize_y),
                                            'LCGPosition_x': lcgPosition_x, 'LCGPosition_y': lcgPosition_y,
                                            'shapes_ungrouped': dict(), 'shapes_grouped':   dict(),
                                            'toProcess_shapes_ungrouped': dict(), 'toProcess_shapes_grouped': dict()}
        if (lcgSizeID != self.activeLCGSizeID):
            self.LCGs[lcgSizeID][positionID]['LCG'].deactivate()
            self.LCGs[lcgSizeID][positionID]['LCG'].hide()

    #ADDSHAPES ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def addShape_Line(self, x, y, x2, y2, color, shapeName, width = None, width_x = None, width_y = None, shapeGroupName = None, layerNumber = 0):
        #[1]: Shape Removal
        self.removeShape(shapeName, shapeGroupName)
        
        #[2]: Coordinate Determination
        polygonPoints = dict()
        shapeBoundaries_x0 = dict()
        shapeBoundaries_x1 = dict()
        shapeBoundaries_y0 = dict()
        shapeBoundaries_y1 = dict()
        for lcgSizeID in self.LCGs:
            lcgBaseSize_x = self.LCGSizeTable[lcgSizeID][6]
            lcgBaseSize_y = self.LCGSizeTable[lcgSizeID][7]
            lineAngle = math.atan2(y2-y, x2-x)
            ppAngle0 = math.pi*5/4+lineAngle
            ppAngle1 = math.pi*7/4+lineAngle
            ppAngle2 = math.pi*1/4+lineAngle
            ppAngle3 = math.pi*3/4+lineAngle
            if (width == None):
                if (width_x == None):
                    baseCircleRadius_x = 0
                    baseCircleRadius_y = width_y*lcgBaseSize_y*_RCLCG_WIDTHMULTIPLIER/2*math.sqrt(2)
                elif (width_y == None):
                    baseCircleRadius_x = width_x*lcgBaseSize_x*_RCLCG_WIDTHMULTIPLIER/2*math.sqrt(2)
                    baseCircleRadius_y = 0
                else:
                    baseCircleRadius_x = width_x*lcgBaseSize_x*_RCLCG_WIDTHMULTIPLIER/2*math.sqrt(2)
                    baseCircleRadius_y = width_y*lcgBaseSize_y*_RCLCG_WIDTHMULTIPLIER/2*math.sqrt(2)
            else:
                baseCircleRadius_x = width*lcgBaseSize_x*_RCLCG_WIDTHMULTIPLIER/2*math.sqrt(2)
                baseCircleRadius_y = width*lcgBaseSize_y*_RCLCG_WIDTHMULTIPLIER/2*math.sqrt(2)
            pp0_x = x *self.resMultiplier_x+baseCircleRadius_x*math.cos(ppAngle0); pp0_y = y *self.resMultiplier_y+baseCircleRadius_y*math.sin(ppAngle0)
            pp1_x = x2*self.resMultiplier_x+baseCircleRadius_x*math.cos(ppAngle1); pp1_y = y2*self.resMultiplier_y+baseCircleRadius_y*math.sin(ppAngle1)
            pp2_x = x2*self.resMultiplier_x+baseCircleRadius_x*math.cos(ppAngle2); pp2_y = y2*self.resMultiplier_y+baseCircleRadius_y*math.sin(ppAngle2)
            pp3_x = x *self.resMultiplier_x+baseCircleRadius_x*math.cos(ppAngle3); pp3_y = y *self.resMultiplier_y+baseCircleRadius_y*math.sin(ppAngle3)
            polygonPoints[lcgSizeID] = (pp0_x, pp1_x, pp2_x, pp3_x, pp0_y, pp1_y, pp2_y, pp3_y)
            shapeBoundaries_x0[lcgSizeID] = min([pp0_x, pp1_x, pp2_x, pp3_x])
            shapeBoundaries_x1[lcgSizeID] = max([pp0_x, pp1_x, pp2_x, pp3_x])
            shapeBoundaries_y0[lcgSizeID] = min([pp0_y, pp1_y, pp2_y, pp3_y])
            shapeBoundaries_y1[lcgSizeID] = max([pp0_y, pp1_y, pp2_y, pp3_y])

        #[3]: LCG Allocation
        allocatedLCGs = self.__addShape_getAllocatedLCGs(shapeBoundaries_x0, shapeBoundaries_x1, shapeBoundaries_y0, shapeBoundaries_y1, lcgSizeDependent = True)
        
        #[4]: Graphics Object Generation Queue Appending - Inactive LCG Sizes
        for lcgSizeID, positionID in allocatedLCGs:
            if (positionID not in self.LCGs[lcgSizeID]): self.__generateLCG(lcgSizeID, positionID)
            polygonPoints_currentLCGSize = polygonPoints[lcgSizeID]
            coordinates = [[polygonPoints_currentLCGSize[0]-self.LCGs[lcgSizeID][positionID]['LCGPosition_x'], polygonPoints_currentLCGSize[4]-self.LCGs[lcgSizeID][positionID]['LCGPosition_y']], 
                           [polygonPoints_currentLCGSize[1]-self.LCGs[lcgSizeID][positionID]['LCGPosition_x'], polygonPoints_currentLCGSize[5]-self.LCGs[lcgSizeID][positionID]['LCGPosition_y']], 
                           [polygonPoints_currentLCGSize[2]-self.LCGs[lcgSizeID][positionID]['LCGPosition_x'], polygonPoints_currentLCGSize[6]-self.LCGs[lcgSizeID][positionID]['LCGPosition_y']], 
                           [polygonPoints_currentLCGSize[3]-self.LCGs[lcgSizeID][positionID]['LCGPosition_x'], polygonPoints_currentLCGSize[7]-self.LCGs[lcgSizeID][positionID]['LCGPosition_y']]]
            shapeInstanceGenerationParams = {'_shapeType': _RCLCG_SHAPETYPE_LINE, 'layerNumber': layerNumber,
                                             'coordinates': coordinates, 'color': color}
            self.__addShape_addShapeGenerationParams(lcgSizeID, positionID, shapeGroupName, shapeName, shapeInstanceGenerationParams)
                
        #[6]: Shape Description Generation & Appending
        shapeDescription = {'shapeType': _RCLCG_SHAPETYPE_LINE, 'allocatedLCGs': list(), 'allocatedLCGs_toProcess': allocatedLCGs,
                            'x': x, 'y': y, 'x2': x2, 'y2': y2, 'width': width, 'width_x': width_x, 'width_y': width_y, 'color': color, 'layerNumber': layerNumber}
        self.__addShape_addShapeDescription(shapeGroupName, shapeName, shapeDescription)

    def addShape_BezierCurve(self, shapeInstance): pyglet.shapes.BezierCurve()

    def addShape_Arc(self, shapeInstance): pyglet.shapes.Arc()

    def addShape_Triangle(self, shapeInstance): pyglet.shapes.Triangle()

    def addShape_Rectangle(self, x, y, width, height, color, shapeName, shapeGroupName = None, layerNumber = 0):
        #[1]: Shape Removal
        self.removeShape(shapeName, shapeGroupName)

        #[2]: Coordinate Determination
        x_scaled = x*self.resMultiplier_x; width_scaled  = width *self.resMultiplier_x
        y_scaled = y*self.resMultiplier_y; height_scaled = height*self.resMultiplier_y
        shapeBoundary_x0 = x_scaled
        shapeBoundary_x1 = x_scaled+width_scaled
        shapeBoundary_y0 = y_scaled
        shapeBoundary_y1 = y_scaled+height_scaled

        #[3]: LCG Allocation
        allocatedLCGs = self.__addShape_getAllocatedLCGs(shapeBoundary_x0, shapeBoundary_x1, shapeBoundary_y0, shapeBoundary_y1, lcgSizeDependent = False)
        #[4]: Graphics Object Generation Queue Appending - Inactive LCG Sizes
        for lcgSizeID, positionID in allocatedLCGs:
            if (positionID not in self.LCGs[lcgSizeID]): self.__generateLCG(lcgSizeID, positionID)
            shapeInstanceGenerationParams = {'_shapeType': _RCLCG_SHAPETYPE_RECTANGLE, 'layerNumber': layerNumber,
                                             'x': x_scaled-self.LCGs[lcgSizeID][positionID]['LCGPosition_x'], 'y': y_scaled-self.LCGs[lcgSizeID][positionID]['LCGPosition_y'], 'width': width_scaled, 'height': height_scaled, 'color': color}
            self.__addShape_addShapeGenerationParams(lcgSizeID, positionID, shapeGroupName, shapeName, shapeInstanceGenerationParams)

        #[5]: Shape Description Generation & Appending
        shapeDescription = {'shapeType': _RCLCG_SHAPETYPE_RECTANGLE, 'allocatedLCGs': list(), 'allocatedLCGs_toProcess': allocatedLCGs,
                            'x': x, 'y': y, 'width': width, 'height': height, 'color': color, 'layerNumber': layerNumber}
        self.__addShape_addShapeDescription(shapeGroupName, shapeName, shapeDescription)

    def addShape_BorderedRectangle(self, shapeInstance): pyglet.shapes.BorderedRectangle()

    def addShape_Box(self, shapeInstance): pyglet.shapes.Box()

    def addShape_Circle(self, shapeInstance): pyglet.shapes.Circle()

    def addShape_Ellipse(self, shapeInstance): pyglet.shapes.Ellipse()

    def addShape_Sector(self, shapeInstance): pyglet.shapes.Sector()

    def addShape_Polygon(self, coordinates, color, shapeName, shapeGroupName = None, layerNumber = 0):
        #[1]: Shape Removal
        self.removeShape(shapeName, shapeGroupName)
        
        #[2]: Coordinate Determination
        shapeBoundary_x0 = None
        shapeBoundary_x1 = None
        shapeBoundary_y0 = None
        shapeBoundary_y1 = None
        coordinates_resolutionScaled = list()
        for coordinate in coordinates:
            c_x_rs = coordinate[0]*self.resMultiplier_x
            c_y_rs = coordinate[1]*self.resMultiplier_y
            if ((shapeBoundary_x0 == None) or (c_x_rs < shapeBoundary_x0)): shapeBoundary_x0 = c_x_rs
            if ((shapeBoundary_x1 == None) or (shapeBoundary_x1 < c_x_rs)): shapeBoundary_x1 = c_x_rs
            if ((shapeBoundary_y0 == None) or (c_y_rs < shapeBoundary_y0)): shapeBoundary_y0 = c_y_rs
            if ((shapeBoundary_y1 == None) or (shapeBoundary_y1 < c_y_rs)): shapeBoundary_y1 = c_y_rs
            coordinates_resolutionScaled.append([c_x_rs, c_y_rs])

        #[3]: LCG Allocation
        allocatedLCGs = self.__addShape_getAllocatedLCGs(shapeBoundary_x0, shapeBoundary_x1, shapeBoundary_y0, shapeBoundary_y1, lcgSizeDependent = False)
        
        #[4]: Graphics Object Generation Queue Appending - Inactive LCG Sizes
        for lcgSizeID, positionID in allocatedLCGs:
            if (positionID not in self.LCGs[lcgSizeID]): self.__generateLCG(lcgSizeID, positionID)
            coordinates_localRS = [[c_rs[0]-self.LCGs[lcgSizeID][positionID]['LCGPosition_x'], c_rs[1]-self.LCGs[lcgSizeID][positionID]['LCGPosition_y']] for c_rs in coordinates_resolutionScaled]
            shapeInstanceGenerationParams = {'_shapeType': _RCLCG_SHAPETYPE_POLYGON, 'layerNumber': layerNumber,
                                             'coordinates': coordinates_localRS, 'color': color}
            self.__addShape_addShapeGenerationParams(lcgSizeID, positionID, shapeGroupName, shapeName, shapeInstanceGenerationParams)

        #[5]: Shape Description Generation & Appending
        shapeDescription = {'shapeType': _RCLCG_SHAPETYPE_POLYGON, 'allocatedLCGs': list(), 'allocatedLCGs_toProcess': allocatedLCGs,
                            'coordinates': coordinates, 'color': color, 'layerNumber': layerNumber}
        self.__addShape_addShapeDescription(shapeGroupName, shapeName, shapeDescription)





    def __addShape_getAllocatedLCGs(self, shapeBoundary_x0, shapeBoundary_x1, shapeBoundary_y0, shapeBoundary_y1, lcgSizeDependent = False):
        allocatedLCGs = list()
        for lcgSizeID in self.LCGs:
            lcgSize_x = self.LCGSizeTable[lcgSizeID][4]
            lcgSize_y = self.LCGSizeTable[lcgSizeID][5]
            if (lcgSizeDependent == True):
                _shapeBoundary_x0 = shapeBoundary_x0[lcgSizeID]
                _shapeBoundary_x1 = shapeBoundary_x1[lcgSizeID]
                _shapeBoundary_y0 = shapeBoundary_y0[lcgSizeID]
                _shapeBoundary_y1 = shapeBoundary_y1[lcgSizeID]
            else:
                _shapeBoundary_x0 = shapeBoundary_x0
                _shapeBoundary_x1 = shapeBoundary_x1
                _shapeBoundary_y0 = shapeBoundary_y0
                _shapeBoundary_y1 = shapeBoundary_y1
            if (0 <= _shapeBoundary_x0): lcgPosition_leftmost   = int(_shapeBoundary_x0/lcgSize_x)
            else:                        lcgPosition_leftmost   = int(_shapeBoundary_x0/lcgSize_x)-1
            if (0 <= _shapeBoundary_x1): lcgPosition_rightmost  = int(_shapeBoundary_x1/lcgSize_x)
            else:                        lcgPosition_rightmost  = int(_shapeBoundary_x1/lcgSize_x)-1
            if (0 <= _shapeBoundary_y0): lcgPosition_bottommost = int(_shapeBoundary_y0/lcgSize_y)
            else:                        lcgPosition_bottommost = int(_shapeBoundary_y0/lcgSize_y)-1
            if (0 <= _shapeBoundary_y1): lcgPosition_topmost    = int(_shapeBoundary_y1/lcgSize_y)
            else:                        lcgPosition_topmost    = int(_shapeBoundary_y1/lcgSize_y)-1
            for lcgPosition_x in range (lcgPosition_leftmost, lcgPosition_rightmost+1):
                for lcgPosition_y in range (lcgPosition_bottommost, lcgPosition_topmost+1): allocatedLCGs.append((lcgSizeID, "{:d}_{:d}".format(lcgPosition_x, lcgPosition_y)))
        return allocatedLCGs

    def __addShape_addShapeDescription(self, shapeGroupName, shapeName, shapeDescription):
        if (shapeGroupName == None): self.shapeDescriptions_ungrouped[shapeName] = shapeDescription
        else:
            if (shapeGroupName in self.shapeDescriptions_grouped): self.shapeDescriptions_grouped[shapeGroupName][shapeName] = shapeDescription
            else:                                                  self.shapeDescriptions_grouped[shapeGroupName] = {shapeName: shapeDescription}
            
    def __addShape_addShapeGenerationParams(self, lcgSizeID, positionID, shapeGroupName, shapeName, shapeInstanceGenerationParams):
        if (shapeGroupName == None): self.LCGs[lcgSizeID][positionID]['toProcess_shapes_ungrouped'][shapeName] = shapeInstanceGenerationParams
        else: 
            if (shapeGroupName in self.LCGs[lcgSizeID][positionID]['toProcess_shapes_grouped']): self.LCGs[lcgSizeID][positionID]['toProcess_shapes_grouped'][shapeGroupName][shapeName] = shapeInstanceGenerationParams
            else:                                                                                self.LCGs[lcgSizeID][positionID]['toProcess_shapes_grouped'][shapeGroupName] = {shapeName: shapeInstanceGenerationParams}

    #ADDSHAPES END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------










    #COPYSHAPESTONEWLCGSIZE -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __copyShapeToNewLCGSize(self, newLCGSizeID, shapeDescription, shapeName, shapeGroupName = None):
        shapeType = shapeDescription['shapeType']
        
        if (shapeType == _RCLCG_SHAPETYPE_LINE):
            #[1]: ShapeDescription Localization
            x = shapeDescription['x']; x2 = shapeDescription['x2']
            y = shapeDescription['y']; y2 = shapeDescription['y2']
            width       = shapeDescription['width']
            width_x     = shapeDescription['width_x']
            width_y     = shapeDescription['width_y']
            color       = shapeDescription['color']
            layerNumber = shapeDescription['layerNumber']

            #[2]: Coordinate Determination
            lcgBaseSize_x = self.LCGSizeTable[newLCGSizeID][6]
            lcgBaseSize_y = self.LCGSizeTable[newLCGSizeID][7]
            lineAngle = math.atan2(y2-y, x2-x)
            ppAngle0 = math.pi*5/4+lineAngle
            ppAngle1 = math.pi*7/4+lineAngle
            ppAngle2 = math.pi*1/4+lineAngle
            ppAngle3 = math.pi*3/4+lineAngle
            if (width == None):
                if (width_x == None):
                    baseCircleRadius_x = 0
                    baseCircleRadius_y = width_y*lcgBaseSize_y*_RCLCG_WIDTHMULTIPLIER/2*math.sqrt(2)
                elif (width_y == None):
                    baseCircleRadius_x = width_x*lcgBaseSize_x*_RCLCG_WIDTHMULTIPLIER/2*math.sqrt(2)
                    baseCircleRadius_y = 0
                else:
                    baseCircleRadius_x = width_x*lcgBaseSize_x*_RCLCG_WIDTHMULTIPLIER/2*math.sqrt(2)
                    baseCircleRadius_y = width_y*lcgBaseSize_y*_RCLCG_WIDTHMULTIPLIER/2*math.sqrt(2)
            else:
                baseCircleRadius_x = width*lcgBaseSize_x*_RCLCG_WIDTHMULTIPLIER/2*math.sqrt(2)
                baseCircleRadius_y = width*lcgBaseSize_y*_RCLCG_WIDTHMULTIPLIER/2*math.sqrt(2)
            pp0_x = x *self.resMultiplier_x+baseCircleRadius_x*math.cos(ppAngle0); pp0_y = y *self.resMultiplier_y+baseCircleRadius_y*math.sin(ppAngle0)
            pp1_x = x2*self.resMultiplier_x+baseCircleRadius_x*math.cos(ppAngle1); pp1_y = y2*self.resMultiplier_y+baseCircleRadius_y*math.sin(ppAngle1)
            pp2_x = x2*self.resMultiplier_x+baseCircleRadius_x*math.cos(ppAngle2); pp2_y = y2*self.resMultiplier_y+baseCircleRadius_y*math.sin(ppAngle2)
            pp3_x = x *self.resMultiplier_x+baseCircleRadius_x*math.cos(ppAngle3); pp3_y = y *self.resMultiplier_y+baseCircleRadius_y*math.sin(ppAngle3)
            shapeBoundary_x0 = min([pp0_x, pp1_x, pp2_x, pp3_x])
            shapeBoundary_x1 = max([pp0_x, pp1_x, pp2_x, pp3_x])
            shapeBoundary_y0 = min([pp0_y, pp1_y, pp2_y, pp3_y])
            shapeBoundary_y1 = max([pp0_y, pp1_y, pp2_y, pp3_y])
            
            #[3]: LCG Allocation
            allocatedLCGPositionIDs = self.__copyShapeToNewLCGSize_getAllocatedLCGPositionIDs(newLCGSizeID, shapeBoundary_x0, shapeBoundary_x1, shapeBoundary_y0, shapeBoundary_y1)
            
            #[4]: Graphics Object Generation Queue Appending - Inactive LCG Sizes
            for positionID in allocatedLCGPositionIDs:
                if (positionID not in self.LCGs[newLCGSizeID]): self.__generateLCG(newLCGSizeID, positionID)
                coordinates = [[pp0_x-self.LCGs[newLCGSizeID][positionID]['LCGPosition_x'], pp0_y-self.LCGs[newLCGSizeID][positionID]['LCGPosition_y']], 
                               [pp1_x-self.LCGs[newLCGSizeID][positionID]['LCGPosition_x'], pp1_y-self.LCGs[newLCGSizeID][positionID]['LCGPosition_y']], 
                               [pp2_x-self.LCGs[newLCGSizeID][positionID]['LCGPosition_x'], pp2_y-self.LCGs[newLCGSizeID][positionID]['LCGPosition_y']], 
                               [pp3_x-self.LCGs[newLCGSizeID][positionID]['LCGPosition_x'], pp3_y-self.LCGs[newLCGSizeID][positionID]['LCGPosition_y']]]
                shapeInstanceGenerationParams = {'_shapeType': _RCLCG_SHAPETYPE_LINE, 'layerNumber': layerNumber,
                                                 'coordinates': coordinates, 'color': color}
                self.__addShape_addShapeGenerationParams(newLCGSizeID, positionID, shapeGroupName, shapeName, shapeInstanceGenerationParams)
                
            #[5]: Add the drawing queue to the shape description
            self.__copyShapeToNewLCGSize_addToShapeDescriptions(newLCGSizeID, allocatedLCGPositionIDs, shapeGroupName, shapeName)
        
        elif (shapeType == _RCLCG_SHAPETYPE_BEZIERCURVE):
            pass
        
        elif (shapeType == _RCLCG_SHAPETYPE_ARC):
            pass
        
        elif (shapeType == _RCLCG_SHAPETYPE_TRIANGLE):
            pass

        elif (shapeType == _RCLCG_SHAPETYPE_RECTANGLE):
            #[1]: ShapeDescription Localization
            x = shapeDescription['x']; width  = shapeDescription['width']
            y = shapeDescription['y']; height = shapeDescription['height']
            color       = shapeDescription['color']
            layerNumber = shapeDescription['layerNumber']
            
            #[2]: Coordinate Determination
            x_scaled = x*self.resMultiplier_x; width_scaled  = width *self.resMultiplier_x
            y_scaled = y*self.resMultiplier_y; height_scaled = height*self.resMultiplier_y
            shapeBoundary_x0 = x_scaled
            shapeBoundary_x1 = x_scaled+width_scaled
            shapeBoundary_y0 = y_scaled
            shapeBoundary_y1 = y_scaled+height_scaled

            #[3]: LCG Allocation
            allocatedLCGPositionIDs = self.__copyShapeToNewLCGSize_getAllocatedLCGPositionIDs(newLCGSizeID, shapeBoundary_x0, shapeBoundary_x1, shapeBoundary_y0, shapeBoundary_y1)
            
            #[4]: Graphics Object Generation Queue Appending - Inactive LCG Sizes
            for positionID in allocatedLCGPositionIDs:
                if (positionID not in self.LCGs[newLCGSizeID]): self.__generateLCG(newLCGSizeID, positionID)
                shapeInstanceGenerationParams = {'_shapeType': _RCLCG_SHAPETYPE_RECTANGLE, 'layerNumber': layerNumber,
                                                 'x': x_scaled-self.LCGs[newLCGSizeID][positionID]['LCGPosition_x'], 'y': y_scaled-self.LCGs[newLCGSizeID][positionID]['LCGPosition_y'], 'width': width_scaled, 'height': height_scaled, 'color': color}
                self.__addShape_addShapeGenerationParams(newLCGSizeID, positionID, shapeGroupName, shapeName, shapeInstanceGenerationParams)
                
            #[5]: Add the drawing queue to the shape description
            self.__copyShapeToNewLCGSize_addToShapeDescriptions(newLCGSizeID, allocatedLCGPositionIDs, shapeGroupName, shapeName)
        
        elif (shapeType == _RCLCG_SHAPETYPE_BORDEREDRECTANGLE):
            pass
        
        elif (shapeType == _RCLCG_SHAPETYPE_BOX):
            pass
        
        elif (shapeType == _RCLCG_SHAPETYPE_CIRCLE):
            pass
        
        elif (shapeType == _RCLCG_SHAPETYPE_ELLIPSE):
            pass
        
        elif (shapeType == _RCLCG_SHAPETYPE_SECTOR):
            pass
        
        elif (shapeType == _RCLCG_SHAPETYPE_POLYGON):
            #[1]: ShapeDescription Localization
            coordinates = shapeDescription['coordinates']
            color       = shapeDescription['color']
            layerNumber = shapeDescription['layerNumber']

            #[2]: Coordinate Determination
            shapeBoundary_x0 = None
            shapeBoundary_x1 = None
            shapeBoundary_y0 = None
            shapeBoundary_y1 = None
            coordinates_resolutionScaled = list()
            for coordinate in coordinates:
                c_x_rs = coordinate[0]*self.resMultiplier_x
                c_y_rs = coordinate[1]*self.resMultiplier_y
                if ((shapeBoundary_x0 == None) or (c_x_rs < shapeBoundary_x0)): shapeBoundary_x0 = c_x_rs
                if ((shapeBoundary_x1 == None) or (shapeBoundary_x1 < c_x_rs)): shapeBoundary_x1 = c_x_rs
                if ((shapeBoundary_y0 == None) or (c_y_rs < shapeBoundary_y0)): shapeBoundary_y0 = c_y_rs
                if ((shapeBoundary_y1 == None) or (shapeBoundary_y1 < c_y_rs)): shapeBoundary_y1 = c_y_rs
                coordinates_resolutionScaled.append([c_x_rs, c_y_rs])

            #[3]: LCG Allocation
            allocatedLCGPositionIDs = self.__copyShapeToNewLCGSize_getAllocatedLCGPositionIDs(newLCGSizeID, shapeBoundary_x0, shapeBoundary_x1, shapeBoundary_y0, shapeBoundary_y1)
            
            #[4]: Graphics Object Generation Queue Appending - Inactive LCG Sizes
            for positionID in allocatedLCGPositionIDs:
                if (positionID not in self.LCGs[newLCGSizeID]): self.__generateLCG(newLCGSizeID, positionID)
                coordinates_localRS = [[c_rs[0]-self.LCGs[newLCGSizeID][positionID]['LCGPosition_x'], c_rs[1]-self.LCGs[newLCGSizeID][positionID]['LCGPosition_y']] for c_rs in coordinates_resolutionScaled]
                shapeInstanceGenerationParams = {'_shapeType': _RCLCG_SHAPETYPE_POLYGON, 'layerNumber': layerNumber,
                                                 'coordinates': coordinates_localRS, 'color': color}
                self.__addShape_addShapeGenerationParams(newLCGSizeID, positionID, shapeGroupName, shapeName, shapeInstanceGenerationParams)
                
            #[5]: Add the drawing queue to the shape description
            self.__copyShapeToNewLCGSize_addToShapeDescriptions(newLCGSizeID, allocatedLCGPositionIDs, shapeGroupName, shapeName)





    def __copyShapeToNewLCGSize_getAllocatedLCGPositionIDs(self, newLCGSizeID, shapeBoundary_x0, shapeBoundary_x1, shapeBoundary_y0, shapeBoundary_y1):
        allocatedLCGPositionIDs = list()
        lcgSize_x = self.LCGSizeTable[newLCGSizeID][4]
        lcgSize_y = self.LCGSizeTable[newLCGSizeID][5]
        if (0 <= shapeBoundary_x0): lcgPosition_leftmost   = int(shapeBoundary_x0/lcgSize_x)
        else:                       lcgPosition_leftmost   = int(shapeBoundary_x0/lcgSize_x)-1
        if (0 <= shapeBoundary_x1): lcgPosition_rightmost  = int(shapeBoundary_x1/lcgSize_x)
        else:                       lcgPosition_rightmost  = int(shapeBoundary_x1/lcgSize_x)-1
        if (0 <= shapeBoundary_y0): lcgPosition_bottommost = int(shapeBoundary_y0/lcgSize_y)
        else:                       lcgPosition_bottommost = int(shapeBoundary_y0/lcgSize_y)-1
        if (0 <= shapeBoundary_y1): lcgPosition_topmost    = int(shapeBoundary_y1/lcgSize_y)
        else:                       lcgPosition_topmost    = int(shapeBoundary_y1/lcgSize_y)-1
        for lcgPosition_x in range (lcgPosition_leftmost, lcgPosition_rightmost+1):
            for lcgPosition_y in range (lcgPosition_bottommost, lcgPosition_topmost+1): allocatedLCGPositionIDs.append("{:d}_{:d}".format(lcgPosition_x, lcgPosition_y))
        return allocatedLCGPositionIDs
    
    def __copyShapeToNewLCGSize_addToShapeDescriptions(self, newLCGSizeID, allocatedLCGPositionIDs, shapeGroupName, shapeName):
        allocatedLCGs = [(newLCGSizeID, allocatedLCGPositionID) for allocatedLCGPositionID in allocatedLCGPositionIDs]
        if (shapeGroupName == None): self.shapeDescriptions_ungrouped[shapeName]['allocatedLCGs_toProcess'] += allocatedLCGs
        else:                        self.shapeDescriptions_grouped[shapeGroupName][shapeName]['allocatedLCGs_toProcess'] += allocatedLCGs

    #COPYSHAPESTONEWLCGSIZE END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------










    #Shape Removal & RCLCG Clearing ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def removeShape(self, shapeName, groupName = None):
        if (groupName == None):
            if (shapeName in self.shapeDescriptions_ungrouped): 
                for lcgSizeID, positionID in self.shapeDescriptions_ungrouped[shapeName]['allocatedLCGs']:           del self.LCGs[lcgSizeID][positionID]['shapes_ungrouped'][shapeName]
                for lcgSizeID, positionID in self.shapeDescriptions_ungrouped[shapeName]['allocatedLCGs_toProcess']: del self.LCGs[lcgSizeID][positionID]['toProcess_shapes_ungrouped'][shapeName]
                del self.shapeDescriptions_ungrouped[shapeName]
                return True
            else: return False
        else:
            if (groupName in self.shapeDescriptions_grouped):
                if (shapeName in self.shapeDescriptions_grouped[groupName]):
                    for lcgSizeID, positionID in self.shapeDescriptions_grouped[groupName][shapeName]['allocatedLCGs']:           del self.LCGs[lcgSizeID][positionID]['shapes_grouped'][groupName][shapeName]
                    for lcgSizeID, positionID in self.shapeDescriptions_grouped[groupName][shapeName]['allocatedLCGs_toProcess']: del self.LCGs[lcgSizeID][positionID]['toProcess_shapes_grouped'][groupName][shapeName]
                    del self.shapeDescriptions_grouped[groupName][shapeName]
                    return True
                else: return False
            else: return False

    def removeGroup(self, groupName):
        if (groupName in self.shapeDescriptions_grouped):
            for shapeName in self.shapeDescriptions_grouped[groupName]:
                for lcgSizeID, positionID in self.shapeDescriptions_grouped[groupName][shapeName]['allocatedLCGs']:
                    if (groupName in self.LCGs[lcgSizeID][positionID]['shapes_grouped']): del self.LCGs[lcgSizeID][positionID]['shapes_grouped'][groupName]
                for lcgSizeID, positionID in self.shapeDescriptions_grouped[groupName][shapeName]['allocatedLCGs_toProcess']:
                    if (groupName in self.LCGs[lcgSizeID][positionID]['toProcess_shapes_grouped']): del self.LCGs[lcgSizeID][positionID]['toProcess_shapes_grouped'][groupName]
            del self.shapeDescriptions_grouped[groupName]
            return True
        else: return False

    def removeAllUngrouped(self):
        for shapeName in self.shapeDescriptions_ungrouped:
            for lcgSizeID, positionID in self.shapeDescriptions_ungrouped[shapeName]['allocatedLCGs']:           del self.LCGs[lcgSizeID][positionID]['shapes_ungrouped'][shapeName]
            for lcgSizeID, positionID in self.shapeDescriptions_ungrouped[shapeName]['allocatedLCGs_toProcess']: del self.LCGs[lcgSizeID][positionID]['toProcess_shapes_ungrouped'][shapeName]
        self.shapeDescriptions_ungrouped.clear()

    def clearAll(self):
        self.LCGs = dict()
        self.LCGSizeTable = dict()
        self.activeLCGSize   = None
        self.activeLCGSizeID = None
        self.shapeDescriptions_ungrouped = dict()
        self.shapeDescriptions_grouped   = dict()
    #Shape Removal & RCLCG Clearing END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------