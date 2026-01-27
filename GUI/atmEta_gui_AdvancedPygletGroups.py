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
        if (self.parentCameraGroup is not None): self.parentCameraGroup.registerChildCameraGroup(self)

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
        if (projection_x0 is not None): self.projection_x0 = projection_x0
        if (projection_x1 is not None): self.projection_x1 = projection_x1
        if (projection_y0 is not None): self.projection_y0 = projection_y0
        if (projection_y1 is not None): self.projection_y1 = projection_y1
        if (projection_z0 is not None): self.projection_z0 = projection_z0
        if (projection_z1 is not None): self.projection_z1 = projection_z1
        self.__updateEffectiveProjection()

    def updateViewport(self, viewport_x = None, viewport_y = None, viewport_width = None, viewport_height = None):
        if (viewport_x      is not None): self.viewport_x      = viewport_x
        if (viewport_y      is not None): self.viewport_y      = viewport_y
        if (viewport_width  is not None): self.viewport_width  = viewport_width
        if (viewport_height is not None): self.viewport_height = viewport_height
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
        if (self.parentCameraGroup is None):
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
        if (self.parentCameraGroup is None):
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
        print(f"1. Viewport:             ({str(self.viewport_x)}, {str(self.viewport_y)}, {str(self.viewport_width)}, {str(self.viewport_height)})\
              \n2. Viewport_Effective:   ({str(self.viewport_x_effective)}, {str(self.viewport_y_effective)}, {str(self.viewport_width_effective)}, {str(self.viewport_height_effective)})\
              \n3. Viewport_onScreen:    ({str(self.viewport_x_onScreen)}, {str(self.viewport_y_onScreen)}, {str(self.viewport_width_onScreen)}, {str(self.viewport_height_onScreen)})\
              \n4. Projection:           ({str(self.projection_x0)}, {str(self.projection_x1)}, {str(self.projection_y0)}, {str(self.projection_y1)})\
              \n5. Projeciton_Effective: ({str(self.projection_x0_effective)}, {str(self.projection_x1_effective)}, {str(self.projection_y0_effective)}, {str(self.projection_y1_effective)})")



class layeredCameraGroup:
    def __init__(self, window, viewport_x = 0, viewport_y = 0, viewport_width = 1, viewport_height = 1, projection_x0 = 0, projection_x1 = 1, projection_y0 = 0, projection_y1 = 1, projection_z0 = 0, projection_z1 = 1, order = None, parentCameraGroup = None):
        #Window
        self.window = window
        
        #Parent & Child cameraGroup
        if (order is None): self.order = parentCameraGroup.order+1
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
        for index, groupNumber in enumerate(range(groupRange0, groupRange1+1)): groupInstances[f"group_{index}"] = self.__getGroup(groupNumber)
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
        for gIndex, group in enumerate(self.groups.values()):
            print(f"[{gIndex}] - Viewport: ({group.viewport_x}, {group.viewport_y}, {group.viewport_width}, {group.viewport_height}), Projection: ({group.projection_x0}, {group.projection_x1}, {group.projection_y0}, {group.projection_y1}), Visibility: {group.visible}")



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
_RCLCG_MAXNSIZES = 3
class resolutionControlledLayeredCameraGroup:
    def __init__(self, 
                 window, 
                 batch, 
                 viewport_x, 
                 viewport_y, 
                 viewport_width, 
                 viewport_height, 
                 projection_x0 = 0, 
                 projection_x1 = 1, 
                 projection_y0 = 0, 
                 projection_y1 = 1, 
                 projection_z0 = 0, 
                 projection_z1 = 1, 
                 precision_x = 0, 
                 precision_y = 0,
                 fsdResolution_x = 10, 
                 fsdResolution_y = 10,
                 order = None, 
                 parentCameraGroup = None):
        self.window = window
        self.batch  = batch
        if (order is None): self.order = parentCameraGroup.order+1
        else:               self.order = order
        
        #Resolution Control
        self.resMultiplier_x = 1/pow(10, precision_x)
        self.resMultiplier_y = 1/pow(10, precision_y)

        #Group Setup
        self.mainCamGroup = cameraGroup(self.window, viewport_x, viewport_y, viewport_width, viewport_height, projection_x0, projection_x1, projection_y0, projection_y1, projection_z0, projection_z1, parentCameraGroup = parentCameraGroup, order = self.order)
        self.mainCamGroup.registerChildCameraGroup(self)
        
        #LCG Control
        self.LCGs         = dict()
        self.LCGSizes     = list()
        self.LCGSizeTable = dict()
        self.activeLCGSize = None
        self.shapeDescriptions_ungrouped = dict()
        self.shapeDescriptions_grouped   = dict()

        self.LCG_FSDRESOLUTION_X = fsdResolution_x
        self.LCG_FSDRESOLUTION_Y = fsdResolution_y

        #Functions
        self.__psgq_gsiFuncs = {_RCLCG_SHAPETYPE_LINE:              self.__processShapeGenerationQueue_generateShapeInstance_LINE,
                                _RCLCG_SHAPETYPE_BEZIERCURVE:       self.__processShapeGenerationQueue_generateShapeInstance_BEZIERCURVE,
                                _RCLCG_SHAPETYPE_ARC:               self.__processShapeGenerationQueue_generateShapeInstance_ARC,
                                _RCLCG_SHAPETYPE_TRIANGLE:          self.__processShapeGenerationQueue_generateShapeInstance_TRIANGLE,
                                _RCLCG_SHAPETYPE_RECTANGLE:         self.__processShapeGenerationQueue_generateShapeInstance_RECTANGLE,
                                _RCLCG_SHAPETYPE_BORDEREDRECTANGLE: self.__processShapeGenerationQueue_generateShapeInstance_BORDEREDRECTANGLE,
                                _RCLCG_SHAPETYPE_BOX:               self.__processShapeGenerationQueue_generateShapeInstance_BOX,
                                _RCLCG_SHAPETYPE_CIRCLE:            self.__processShapeGenerationQueue_generateShapeInstance_CIRCLE,
                                _RCLCG_SHAPETYPE_ELLIPSE:           self.__processShapeGenerationQueue_generateShapeInstance_ELLIPSE,
                                _RCLCG_SHAPETYPE_SECTOR:            self.__processShapeGenerationQueue_generateShapeInstance_SECTOR,
                                _RCLCG_SHAPETYPE_POLYGON:           self.__processShapeGenerationQueue_generateShapeInstance_POLYGON}
        self.__cstnls_adtsFuncs = {_RCLCG_SHAPETYPE_LINE:              self.__copyShapeToNewLCGSize_addToShapeDescriptions_LINE,
                                   _RCLCG_SHAPETYPE_BEZIERCURVE:       self.__copyShapeToNewLCGSize_addToShapeDescriptions_BEZIERCURVE,
                                   _RCLCG_SHAPETYPE_ARC:               self.__copyShapeToNewLCGSize_addToShapeDescriptions_ARC,
                                   _RCLCG_SHAPETYPE_TRIANGLE:          self.__copyShapeToNewLCGSize_addToShapeDescriptions_TRIANGLE,
                                   _RCLCG_SHAPETYPE_RECTANGLE:         self.__copyShapeToNewLCGSize_addToShapeDescriptions_RECTANGLE,
                                   _RCLCG_SHAPETYPE_BORDEREDRECTANGLE: self.__copyShapeToNewLCGSize_addToShapeDescriptions_BORDEREDRECTANGLE,
                                   _RCLCG_SHAPETYPE_BOX:               self.__copyShapeToNewLCGSize_addToShapeDescriptions_BOX,
                                   _RCLCG_SHAPETYPE_CIRCLE:            self.__copyShapeToNewLCGSize_addToShapeDescriptions_CIRCLE,
                                   _RCLCG_SHAPETYPE_ELLIPSE:           self.__copyShapeToNewLCGSize_addToShapeDescriptions_ELLIPSE,
                                   _RCLCG_SHAPETYPE_SECTOR:            self.__copyShapeToNewLCGSize_addToShapeDescriptions_SECTOR,
                                   _RCLCG_SHAPETYPE_POLYGON:           self.__copyShapeToNewLCGSize_addToShapeDescriptions_POLYGON}
        
    def processShapeGenerationQueue(self, timeout_ns, currentFocusOnly = False):
        timer_processBeg_ns = time.perf_counter_ns()

        _func_perf_counter_ns       = time.perf_counter_ns
        _func_searchTargetWithinLCG = self.__processShapeGenerationQueue_searchTargetWithinLCG
        _func_generateShapeInstance = self.__processShapeGenerationQueue_generateShapeInstance

        #[1]: Process only within the current focus
        if (currentFocusOnly == True):
            aLCGSize = self.activeLCGSize
            if (aLCGSize is None): return False
            #Find positions within the current projection area
            eProj_x0, eProj_x1 = self.mainCamGroup.projection_x0_effective, self.mainCamGroup.projection_x1_effective
            eProj_y0, eProj_y1 = self.mainCamGroup.projection_y0_effective, self.mainCamGroup.projection_y1_effective
            lcgSize_full = self.LCGSizeTable[aLCGSize]
            lcgSize_x, lcgSize_y = lcgSize_full[4], lcgSize_full[5]
            lcgPosition_leftmost   = int(eProj_x0//lcgSize_x)
            lcgPosition_rightmost  = int(eProj_x1//lcgSize_x)
            lcgPosition_bottommost = int(eProj_y0//lcgSize_y)
            lcgPosition_topmost    = int(eProj_y1//lcgSize_y)
            lcgs_active = self.LCGs[aLCGSize]
            lcgPositionsInVR = [lcgPos 
                                for lcgPosition_x in range (lcgPosition_leftmost,   lcgPosition_rightmost+1) 
                                for lcgPosition_y in range (lcgPosition_bottommost, lcgPosition_topmost  +1) 
                                if (lcgPos := (lcgPosition_x, lcgPosition_y)) in lcgs_active]
            #Until Timeout Occurs, process shape generation queues
            while (_func_perf_counter_ns()-timer_processBeg_ns < timeout_ns):
                #Loop through LCGs within the current focus until a target is found
                target = None
                while (lcgPositionsInVR):
                    position = lcgPositionsInVR[-1]
                    target = _func_searchTargetWithinLCG(lcgSize = aLCGSize, position = position)
                    if (target is None): lcgPositionsInVR.pop(-1)
                    else: break
                #If no target is found, return False to indicate there exist no shape generation queues to process within the current focus
                if (target is None): return False
                #If a target is found, process it and repeat the loop
                _func_generateShapeInstance(target[0], target[1], target[2], target[3])
            return True

        #[2]: Process within the entire space
        else:
            lcgs = self.LCGs
            lcgTargets = [(lcgSize, lcgPos)
                          for lcgSize, lcgDesc in lcgs.items()
                          for lcgPos           in lcgDesc]
            #Until Timeout Occurs, process shape generation queues
            while (_func_perf_counter_ns()-timer_processBeg_ns < timeout_ns):
                #Loop through LCGs within the current focus until a target is found
                target = None
                while (lcgTargets):
                    lcgSize, lcgPos = lcgTargets[-1]
                    target = _func_searchTargetWithinLCG(lcgSize = lcgSize, position = lcgPos)
                    if (target is None): lcgTargets.pop(-1)
                    else: break
                #If no target is found, return False to indicate there exist no shape generation queues to process within the current focus
                if (target is None): return False
                #If a target is found, process it and repeat the loop
                _func_generateShapeInstance(target[0], target[1], target[2], target[3])
            return True
        
    def __processShapeGenerationQueue_searchTargetWithinLCG(self, lcgSize, position):
        tLCG = self.LCGs[lcgSize][position]
        #Ungrouped Target Search
        for shapeName in tLCG['toProcess_shapes_ungrouped']: return (lcgSize, position, None, shapeName)
        #Grouped Target Search
        for groupName, groupDesc in tLCG['toProcess_shapes_grouped'].items():
            for shapeName in groupDesc: return (lcgSize, position, groupName, shapeName)
        #No Target Found
        return None

    def __processShapeGenerationQueue_generateShapeInstance(self, lcgSize, position, shapeGroupName, shapeName):
        tLCG  = self.LCGs[lcgSize][position]
        lcgID = (lcgSize, position)
        if (shapeGroupName is None): sigp = tLCG['toProcess_shapes_ungrouped'].pop(shapeName)
        else:                        
            sigp = tLCG['toProcess_shapes_grouped'][shapeGroupName].pop(shapeName)
            if not(tLCG['toProcess_shapes_grouped'][shapeGroupName]): del tLCG['toProcess_shapes_grouped'][shapeGroupName]
        shapeInstance = self.__psgq_gsiFuncs[sigp['_shapeType']](sigp = sigp, lcg = tLCG)
        if (shapeGroupName is None):
            tLCG['shapes_ungrouped'][shapeName] = shapeInstance
            shapeDesc = self.shapeDescriptions_ungrouped[shapeName]
        else:
            lcg_sg = tLCG['shapes_grouped']
            if (shapeGroupName in lcg_sg): lcg_sg[shapeGroupName][shapeName] = shapeInstance
            else:                          lcg_sg[shapeGroupName] = {shapeName: shapeInstance}
            shapeDesc = self.shapeDescriptions_grouped[shapeGroupName][shapeName]
        shapeDesc['allocatedLCGs'].add(lcgID)
        shapeDesc['allocatedLCGs_toProcess'].remove(lcgID)

    def __processShapeGenerationQueue_generateShapeInstance_LINE(self, sigp, lcg):
        return pyglet.shapes.Polygon(*sigp['coordinates'], color = sigp['color'], batch = self.batch, group = lcg['LCG'].getGroups(sigp['layerNumber'], sigp['layerNumber'])['group_0'])
    def __processShapeGenerationQueue_generateShapeInstance_BEZIERCURVE(self, sigp, lcg):
        return
    def __processShapeGenerationQueue_generateShapeInstance_ARC(self, sigp, lcg):
        return
    def __processShapeGenerationQueue_generateShapeInstance_TRIANGLE(self, sigp, lcg):
        return
    def __processShapeGenerationQueue_generateShapeInstance_RECTANGLE(self, sigp, lcg):
        return pyglet.shapes.Rectangle(x = sigp['x'], y = sigp['y'], width = sigp['width'], height = sigp['height'], color = sigp['color'], batch = self.batch, group = lcg['LCG'].getGroups(sigp['layerNumber'], sigp['layerNumber'])['group_0'])
    def __processShapeGenerationQueue_generateShapeInstance_BORDEREDRECTANGLE(self, sigp, lcg):
        return
    def __processShapeGenerationQueue_generateShapeInstance_BOX(self, sigp, lcg):
        return
    def __processShapeGenerationQueue_generateShapeInstance_CIRCLE(self, sigp, lcg):
        return
    def __processShapeGenerationQueue_generateShapeInstance_ELLIPSE(self, sigp, lcg):
        return
    def __processShapeGenerationQueue_generateShapeInstance_SECTOR(self, sigp, lcg):
        return
    def __processShapeGenerationQueue_generateShapeInstance_POLYGON(self, sigp, lcg):
        return pyglet.shapes.Polygon(*sigp['coordinates'], color = sigp['color'], batch = self.batch, group = lcg['LCG'].getGroups(sigp['layerNumber'], sigp['layerNumber'])['group_0'])
            
    def setPrecision(self, precision_x, precision_y, transferObjects = False):
        resMultiplier_x_previous = self.resMultiplier_x
        resMultiplier_y_previous = self.resMultiplier_y
        self.resMultiplier_x = 10**-precision_x
        self.resMultiplier_y = 10**-precision_y
        if (transferObjects == True):
            aLCGSize = self.activeLCGSize
            if (aLCGSize is not None):
                self.LCGs = {aLCGSize: dict()}
                self.LCGSizeTable = {aLCGSize: self.LCGSizeTable[aLCGSize]}
                _func_copyShapeToNewLCGSize = self.__copyShapeToNewLCGSize
                for shapeName, shapeDesc in self.shapeDescriptions_ungrouped.items():
                    shapeDesc['allocatedLCGs'] = list()
                    _func_copyShapeToNewLCGSize(aLCGSize, shapeDesc, shapeName, None)
                for groupName, groupDesc in self.shapeDescriptions_grouped.items():
                    for shapeName, shapeDesc in groupDesc.items(): 
                        shapeDesc['allocatedLCGs'] = list()
                        _func_copyShapeToNewLCGSize(aLCGSize, shapeDesc, shapeName, groupName)
        else: self.clearAll()
        ratio_x = self.resMultiplier_x/resMultiplier_x_previous
        ratio_y = self.resMultiplier_y/resMultiplier_y_previous
        self.mainCamGroup.updateProjection(self.mainCamGroup.projection_x0*ratio_x,
                                           self.mainCamGroup.projection_x1*ratio_x,
                                           self.mainCamGroup.projection_y0*ratio_y,
                                           self.mainCamGroup.projection_y1*ratio_y)

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
        if (self.activeLCGSize in self.LCGs):
            lcg_active = self.LCGs[self.activeLCGSize]
            for position in lcg_active:
                lcg_active[position]['LCG'].activate()
                lcg_active[position]['LCG'].show()
    
    def hide(self): 
        self.mainCamGroup.hide()
        if (self.activeLCGSize in self.LCGs):
            lcg_active = self.LCGs[self.activeLCGSize]
            for position in lcg_active:
                lcg_active[position]['LCG'].deactivate()
                lcg_active[position]['LCG'].hide()

    def updateProjection(self, projection_x0 = None, projection_x1 = None, projection_y0 = None, projection_y1 = None, projection_z0 = None, projection_z1 = None):
        if (projection_x0 is not None): projection_x0 = projection_x0*self.resMultiplier_x
        if (projection_x1 is not None): projection_x1 = projection_x1*self.resMultiplier_x
        if (projection_y0 is not None): projection_y0 = projection_y0*self.resMultiplier_y
        if (projection_y1 is not None): projection_y1 = projection_y1*self.resMultiplier_y
        self.mainCamGroup.updateProjection(projection_x0, projection_x1, projection_y0, projection_y1, projection_z0, projection_z1)

    def updateViewport(self, viewport_x, viewport_y, viewport_width, viewport_height): 
        self.mainCamGroup.updateViewport(viewport_x, viewport_y, viewport_width, viewport_height)

    def __onLCGSizeUpdate(self, newLCGSize):
        #Deactivate and hide the current size LCGs
        if self.activeLCGSize is not None:
            lcg_active = self.LCGs[self.activeLCGSize]
            for lcg_active_position in lcg_active.values():
                lcg_active_position_lcg = lcg_active_position['LCG']
                lcg_active_position_lcg.deactivate()
                lcg_active_position_lcg.hide()

        #If the new size LCGs did previously exist, simply reactivate the new size LCGs
        self.activeLCGSize = newLCGSize
        if newLCGSize in self.LCGs:
            lcg_active = self.LCGs[newLCGSize]
            for lcg_active_position in lcg_active.values():
                lcg_active_position_lcg = lcg_active_position['LCG']
                lcg_active_position_lcg.activate()
                lcg_active_position_lcg.show()
            self.LCGSizes.remove(newLCGSize)
            self.LCGSizes.append(newLCGSize)
        #If the new LCGSize did not previously exist, generate shapes for the new LCGSize
        else:
            self.LCGs[newLCGSize] = dict()
            self.LCGSizes.append(newLCGSize)
            self.LCGSizeTable[newLCGSize] = (newLCGSize[0], newLCGSize[1], newLCGSize[4], newLCGSize[5],
                                             newLCGSize[0]*(10**newLCGSize[1]),
                                             newLCGSize[4]*(10**newLCGSize[5]),
                                             newLCGSize[2]*(10**(newLCGSize[3]-6)),
                                             newLCGSize[6]*(10**(newLCGSize[7]-6)))
            _func_copyShapeToNewLCGSize = self.__cstnls_adtsFuncs
            for shapeName, shapeDesc in self.shapeDescriptions_ungrouped.items(): _func_copyShapeToNewLCGSize[shapeDesc['shapeType']](newLCGSize, shapeDesc, shapeName, None)
            for groupName, groupDesc in self.shapeDescriptions_grouped.items():
                for shapeName, shapeDesc in groupDesc.items(): _func_copyShapeToNewLCGSize[shapeDesc['shapeType']](newLCGSize, shapeDesc, shapeName, groupName)

        #Number of LCG Sizes Limiting
        sd_ungrouped = self.shapeDescriptions_ungrouped
        sd_grouped   = self.shapeDescriptions_grouped
        while _RCLCG_MAXNSIZES < len(self.LCGSizes):
            lcgSize = self.LCGSizes[0]
            tLCG    = self.LCGs[lcgSize]
            for position, tLCG_position in tLCG.items():
                lcgID = (lcgSize, position)
                for shapeName in tLCG_position['shapes_ungrouped']:           sd_ungrouped[shapeName]['allocatedLCGs'].remove(lcgID)
                for shapeName in tLCG_position['toProcess_shapes_ungrouped']: sd_ungrouped[shapeName]['allocatedLCGs_toProcess'].remove(lcgID)
                for groupName, group in tLCG_position['shapes_grouped'].items():
                    sd_grouped_group = sd_grouped[groupName]
                    for shapeName in group: sd_grouped_group[shapeName]['allocatedLCGs'].remove(lcgID)
                for groupName, group in tLCG_position['toProcess_shapes_grouped'].items():
                    sd_grouped_group = sd_grouped[groupName]
                    for shapeName in group: sd_grouped_group[shapeName]['allocatedLCGs_toProcess'].remove(lcgID)
            del self.LCGs[lcgSize]
            self.LCGSizes.pop(0)
            del self.LCGSizeTable[lcgSize]

    def __generateLCG(self, lcgSize, position):
        lcgSize_full = self.LCGSizeTable[lcgSize]
        lcgSize_x = lcgSize_full[4]
        lcgSize_y = lcgSize_full[5]
        
        position_x, position_y = position
        lcgPosition_x = lcgSize_x*int(position_x)
        lcgPosition_y = lcgSize_y*int(position_y)
        lcgDesc = {'LCG': layeredCameraGroup(self.window, 
                                             order = self.order, 
                                             parentCameraGroup = self.mainCamGroup,
                                             viewport_x      = lcgPosition_x, 
                                             viewport_y      = lcgPosition_y, 
                                             viewport_width  = lcgSize_x, 
                                             viewport_height = lcgSize_y,
                                             projection_x0 = 0, 
                                             projection_x1 = lcgSize_x, 
                                             projection_y0 = 0, 
                                             projection_y1 = lcgSize_y),
                   'LCGPosition_x': lcgPosition_x, 
                   'LCGPosition_y': lcgPosition_y,
                   'shapes_ungrouped': dict(), 
                   'shapes_grouped':   dict(),
                   'toProcess_shapes_ungrouped': dict(), 
                   'toProcess_shapes_grouped':   dict()}
        if (lcgSize != self.activeLCGSize):
            lcgDesc['LCG'].deactivate()
            lcgDesc['LCG'].hide()

        self.LCGs[lcgSize][position] = lcgDesc
    #ADDSHAPES ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def addShape_Line(self, x, y, x2, y2, color, shapeName, width = None, width_x = None, width_y = None, shapeGroupName = None, layerNumber = 0):
        lcgs         = self.LCGs
        lcgSizeTable = self.LCGSizeTable
        rm_x = self.resMultiplier_x
        rm_y = self.resMultiplier_y
        _func_generateLCG              = self.__generateLCG
        _func_addShapeGenerationParams = self.__addShape_addShapeGenerationParams

        #[1]: Shape Removal
        self.removeShape(shapeName, shapeGroupName)
        
        #[2]: Coordinate Determination
        polygonPoints = dict()
        shapeBoundaries_x0, shapeBoundaries_x1, shapeBoundaries_y0, shapeBoundaries_y1 = dict(), dict(), dict(), dict()
        rclcg_wmsq = _RCLCG_WIDTHMULTIPLIER*0.707106781186 #sqrt(2)/2
        rm_x_x  = x *rm_x
        rm_x_x2 = x2*rm_x
        rm_y_y  = y *rm_y
        rm_y_y2 = y2*rm_y
        lineAngle = math.atan2(y2-y, x2-x)
        ppAngle0, ppAngle1, ppAngle2, ppAngle3                 = math.pi*5/4+lineAngle, math.pi*7/4+lineAngle, math.pi*1/4+lineAngle, math.pi*3/4+lineAngle
        ppAngle_cos0, ppAngle_cos1, ppAngle_cos2, ppAngle_cos3 = math.cos(ppAngle0), math.cos(ppAngle1), math.cos(ppAngle2), math.cos(ppAngle3)
        ppAngle_sin0, ppAngle_sin1, ppAngle_sin2, ppAngle_sin3 = math.sin(ppAngle0), math.sin(ppAngle1), math.sin(ppAngle2), math.sin(ppAngle3)

        for lcgSize in lcgs:
            lcgSize_full = lcgSizeTable[lcgSize]
            lcgBaseSize_x, lcgBaseSize_y = lcgSize_full[6], lcgSize_full[7]
            if (width is None):
                baseCircleRadius_x = 0 if width_x is None else width_x*lcgBaseSize_x*rclcg_wmsq
                baseCircleRadius_y = 0 if width_y is None else width_y*lcgBaseSize_y*rclcg_wmsq
            else:
                baseCircleRadius_x = width*lcgBaseSize_x*rclcg_wmsq
                baseCircleRadius_y = width*lcgBaseSize_y*rclcg_wmsq
            pps = (rm_x_x +baseCircleRadius_x*ppAngle_cos0,
                   rm_x_x2+baseCircleRadius_x*ppAngle_cos1,
                   rm_x_x2+baseCircleRadius_x*ppAngle_cos2,
                   rm_x_x +baseCircleRadius_x*ppAngle_cos3,
                   rm_y_y +baseCircleRadius_y*ppAngle_sin0,
                   rm_y_y2+baseCircleRadius_y*ppAngle_sin1,
                   rm_y_y2+baseCircleRadius_y*ppAngle_sin2,
                   rm_y_y +baseCircleRadius_y*ppAngle_sin3)
            polygonPoints[lcgSize] = pps
            pps_x, pps_y = pps[0:4], pps[4:8]
            shapeBoundaries_x0[lcgSize] = min(pps_x)
            shapeBoundaries_x1[lcgSize] = max(pps_x)
            shapeBoundaries_y0[lcgSize] = min(pps_y)
            shapeBoundaries_y1[lcgSize] = max(pps_y)

        #[3]: LCG Allocation
        allocatedLCGs = self.__addShape_getAllocatedLCGs(shapeBoundaries_x0, shapeBoundaries_x1, shapeBoundaries_y0, shapeBoundaries_y1, lcgSizeDependent = True)
        
        #[4]: Graphics Object Generation Queue Appending - Inactive LCG Sizes
        shapeInstanceGenerationParams_base = {'_shapeType': _RCLCG_SHAPETYPE_LINE, 
                                              'layerNumber': layerNumber,
                                              'coordinates': None, 
                                              'color': color}
        for lcgSize, position in allocatedLCGs:
            lcg_size = lcgs[lcgSize]
            if (position not in lcg_size): _func_generateLCG(lcgSize, position)
            lcg_pos = lcg_size[position]
            (px0, px1, px2, px3, py0, py1, py2, py3) = polygonPoints[lcgSize]
            lcg_pos_x = lcg_pos['LCGPosition_x']
            lcg_pos_y = lcg_pos['LCGPosition_y']
            shapeInstanceGenerationParams = shapeInstanceGenerationParams_base.copy()
            shapeInstanceGenerationParams['coordinates'] = ((px0-lcg_pos_x, py0-lcg_pos_y), 
                                                            (px1-lcg_pos_x, py1-lcg_pos_y), 
                                                            (px2-lcg_pos_x, py2-lcg_pos_y), 
                                                            (px3-lcg_pos_x, py3-lcg_pos_y))
            _func_addShapeGenerationParams(lcgSize, position, shapeGroupName, shapeName, shapeInstanceGenerationParams)
                
        #[6]: Shape Description Generation & Appending
        shapeDescription = {'shapeType':               _RCLCG_SHAPETYPE_LINE, 
                            'allocatedLCGs':           set(), 
                            'allocatedLCGs_toProcess': allocatedLCGs,
                            'x': x, 
                            'y': y, 
                            'x2': x2, 
                            'y2': y2, 
                            'width': width, 
                            'width_x': width_x, 
                            'width_y': width_y, 
                            'color': color, 
                            'layerNumber': layerNumber}
        self.__addShape_addShapeDescription(shapeGroupName, shapeName, shapeDescription)
    def addShape_BezierCurve(self, shapeInstance): 
        pyglet.shapes.BezierCurve()
    def addShape_Arc(self, shapeInstance): 
        pyglet.shapes.Arc()
    def addShape_Triangle(self, shapeInstance): 
        pyglet.shapes.Triangle()
    def addShape_Rectangle(self, x, y, width, height, color, shapeName, shapeGroupName = None, layerNumber = 0):
        lcgs         = self.LCGs
        lcgSizeTable = self.LCGSizeTable
        rm_x = self.resMultiplier_x
        rm_y = self.resMultiplier_y
        _func_generateLCG              = self.__generateLCG
        _func_addShapeGenerationParams = self.__addShape_addShapeGenerationParams

        #[1]: Shape Removal
        self.removeShape(shapeName, shapeGroupName)

        #[2]: Coordinate Determination
        x_scaled = x*rm_x; width_scaled  = width *rm_x
        y_scaled = y*rm_y; height_scaled = height*rm_y
        shapeBoundary_x0 = x_scaled
        shapeBoundary_x1 = x_scaled+width_scaled
        shapeBoundary_y0 = y_scaled
        shapeBoundary_y1 = y_scaled+height_scaled

        #[3]: LCG Allocation
        allocatedLCGs = self.__addShape_getAllocatedLCGs(shapeBoundary_x0, shapeBoundary_x1, shapeBoundary_y0, shapeBoundary_y1, lcgSizeDependent = False)
        
        #[4]: Graphics Object Generation Queue Appending - Inactive LCG Sizes
        shapeInstanceGenerationParams_base = {'_shapeType': _RCLCG_SHAPETYPE_RECTANGLE, 
                                              'layerNumber': layerNumber,
                                              'x': None, 
                                              'y': None, 
                                              'width':  width_scaled, 
                                              'height': height_scaled, 
                                              'color': color}
        for lcgSize, position in allocatedLCGs:
            lcg_size = lcgs[lcgSize]
            if (position not in lcg_size): _func_generateLCG(lcgSize, position)
            lcg_pos = lcg_size[position]
            shapeInstanceGenerationParams = shapeInstanceGenerationParams_base.copy()
            shapeInstanceGenerationParams['x'] = x_scaled-lcg_pos['LCGPosition_x']
            shapeInstanceGenerationParams['y'] = y_scaled-lcg_pos['LCGPosition_y']
            _func_addShapeGenerationParams(lcgSize, position, shapeGroupName, shapeName, shapeInstanceGenerationParams)

        #[5]: Shape Description Generation & Appending
        shapeDescription = {'shapeType':               _RCLCG_SHAPETYPE_RECTANGLE, 
                            'allocatedLCGs':           set(), 
                            'allocatedLCGs_toProcess': allocatedLCGs,
                            'x': x, 
                            'y': y, 
                            'width': width, 
                            'height': height, 
                            'color': color, 
                            'layerNumber': layerNumber}
        self.__addShape_addShapeDescription(shapeGroupName, shapeName, shapeDescription)
    def addShape_BorderedRectangle(self, shapeInstance): 
        pyglet.shapes.BorderedRectangle()
    def addShape_Box(self, shapeInstance): 
        pyglet.shapes.Box()
    def addShape_Circle(self, shapeInstance): 
        pyglet.shapes.Circle()
    def addShape_Ellipse(self, shapeInstance): 
        pyglet.shapes.Ellipse()
    def addShape_Sector(self, shapeInstance): 
        pyglet.shapes.Sector()
    def addShape_Polygon(self, coordinates, color, shapeName, shapeGroupName = None, layerNumber = 0):
        lcgs         = self.LCGs
        lcgSizeTable = self.LCGSizeTable
        rm_x = self.resMultiplier_x
        rm_y = self.resMultiplier_y
        _func_generateLCG              = self.__generateLCG
        _func_addShapeGenerationParams = self.__addShape_addShapeGenerationParams

        #[1]: Shape Removal
        self.removeShape(shapeName, shapeGroupName)
        
        #[2]: Coordinate Determination
        coordinates_resolutionScaled = [(coord_x*rm_x, coord_y*rm_y) for coord_x, coord_y in coordinates]
        xs, ys = zip(*coordinates_resolutionScaled)
        boundaries = (min(xs), max(xs), min(ys), max(ys))

        #[3]: LCG Allocation
        allocatedLCGs = self.__addShape_getAllocatedLCGs(*boundaries, lcgSizeDependent = False)
        
        #[4]: Graphics Object Generation Queue Appending - Inactive LCG Sizes
        shapeInstanceGenerationParams_base = {'_shapeType': _RCLCG_SHAPETYPE_POLYGON, 
                                              'layerNumber': layerNumber,
                                              'coordinates': None, 
                                              'color': color}
        for lcgSize, position in allocatedLCGs:
            lcg_size = lcgs[lcgSize]
            if (position not in lcg_size): _func_generateLCG(lcgSize, position)
            lcg_pos = lcg_size[position]
            shapeInstanceGenerationParams = shapeInstanceGenerationParams_base.copy()
            shapeInstanceGenerationParams['coordinates'] = [(c_rs_x-lcg_pos['LCGPosition_x'], c_rs_y-lcg_pos['LCGPosition_y']) for c_rs_x, c_rs_y in coordinates_resolutionScaled]
            _func_addShapeGenerationParams(lcgSize, position, shapeGroupName, shapeName, shapeInstanceGenerationParams)

        #[5]: Shape Description Generation & Appending
        shapeDescription = {'shapeType':               _RCLCG_SHAPETYPE_POLYGON, 
                            'allocatedLCGs':           set(), 
                            'allocatedLCGs_toProcess': allocatedLCGs,
                            'coordinates': coordinates, 
                            'color': color, 
                            'layerNumber': layerNumber}
        self.__addShape_addShapeDescription(shapeGroupName, shapeName, shapeDescription)

    def __addShape_getAllocatedLCGs(self, shapeBoundary_x0, shapeBoundary_x1, shapeBoundary_y0, shapeBoundary_y1, lcgSizeDependent = False):
        allocatedLCGs        = []
        allocatedLCGs_extend = allocatedLCGs.extend
        lcgSizeTable = self.LCGSizeTable
        for lcgSize in self.LCGs:
            lcgSize_full = lcgSizeTable[lcgSize]
            lcgSize_x = lcgSize_full[4]
            lcgSize_y = lcgSize_full[5]
            if (lcgSizeDependent == True):
                _sbx0, _sbx1 = shapeBoundary_x0[lcgSize], shapeBoundary_x1[lcgSize]
                _sby0, _sby1 = shapeBoundary_y0[lcgSize], shapeBoundary_y1[lcgSize]
            else:
                _sbx0, _sbx1 = shapeBoundary_x0, shapeBoundary_x1
                _sby0, _sby1 = shapeBoundary_y0, shapeBoundary_y1
            lcgPosition_leftmost   = int(_sbx0//lcgSize_x)
            lcgPosition_rightmost  = int(_sbx1//lcgSize_x)
            lcgPosition_bottommost = int(_sby0//lcgSize_y)
            lcgPosition_topmost    = int(_sby1//lcgSize_y)
            allocatedLCGs_extend((lcgSize, (lcgPosition_x, lcgPosition_y))
                                 for lcgPosition_x in range (lcgPosition_leftmost,   lcgPosition_rightmost+1)
                                 for lcgPosition_y in range (lcgPosition_bottommost, lcgPosition_topmost  +1))
        return set(allocatedLCGs)

    def __addShape_addShapeGenerationParams(self, lcgSize, position, shapeGroupName, shapeName, shapeInstanceGenerationParams):
        lcg = self.LCGs[lcgSize][position]
        if (shapeGroupName is None): lcg['toProcess_shapes_ungrouped'][shapeName] = shapeInstanceGenerationParams
        else: 
            desc = lcg['toProcess_shapes_grouped']
            if (shapeGroupName in desc): desc[shapeGroupName][shapeName] = shapeInstanceGenerationParams
            else:                        desc[shapeGroupName] = {shapeName: shapeInstanceGenerationParams}

    def __addShape_addShapeDescription(self, shapeGroupName, shapeName, shapeDescription):
        if (shapeGroupName is None): self.shapeDescriptions_ungrouped[shapeName] = shapeDescription
        else:
            if (shapeGroupName in self.shapeDescriptions_grouped): self.shapeDescriptions_grouped[shapeGroupName][shapeName] = shapeDescription
            else:                                                  self.shapeDescriptions_grouped[shapeGroupName] = {shapeName: shapeDescription}
    #ADDSHAPES END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------










    #COPYSHAPESTONEWLCGSIZE -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __copyShapeToNewLCGSize_addToShapeDescriptions_LINE(self, newLCGSize, shapeDescription, shapeName, shapeGroupName = None):
        lcgs         = self.LCGs
        lcgSizeTable = self.LCGSizeTable
        rm_x = self.resMultiplier_x
        rm_y = self.resMultiplier_y
        _func_generateLCG              = self.__generateLCG
        _func_addShapeGenerationParams = self.__addShape_addShapeGenerationParams
        
        #[1]: ShapeDescription Localization
        x = shapeDescription['x']; x2 = shapeDescription['x2']
        y = shapeDescription['y']; y2 = shapeDescription['y2']
        width       = shapeDescription['width']
        width_x     = shapeDescription['width_x']
        width_y     = shapeDescription['width_y']
        color       = shapeDescription['color']
        layerNumber = shapeDescription['layerNumber']

        #[2]: Coordinate Determination
        rclcg_wmsq = _RCLCG_WIDTHMULTIPLIER*0.707106781186 #sqrt(2)/2
        rm_x_x  = x *rm_x
        rm_x_x2 = x2*rm_x
        rm_y_y  = y *rm_y
        rm_y_y2 = y2*rm_y
        lineAngle = math.atan2(y2-y, x2-x)
        ppAngle0, ppAngle1, ppAngle2, ppAngle3                 = math.pi*5/4+lineAngle, math.pi*7/4+lineAngle, math.pi*1/4+lineAngle, math.pi*3/4+lineAngle
        ppAngle_cos0, ppAngle_cos1, ppAngle_cos2, ppAngle_cos3 = math.cos(ppAngle0), math.cos(ppAngle1), math.cos(ppAngle2), math.cos(ppAngle3)
        ppAngle_sin0, ppAngle_sin1, ppAngle_sin2, ppAngle_sin3 = math.sin(ppAngle0), math.sin(ppAngle1), math.sin(ppAngle2), math.sin(ppAngle3)
        lcgSize_full = lcgSizeTable[newLCGSize]
        lcgBaseSize_x, lcgBaseSize_y = lcgSize_full[6], lcgSize_full[7]
        if (width is None):
            baseCircleRadius_x = 0 if width_x is None else width_x*lcgBaseSize_x*rclcg_wmsq
            baseCircleRadius_y = 0 if width_y is None else width_y*lcgBaseSize_y*rclcg_wmsq
        else:
            baseCircleRadius_x = width*lcgBaseSize_x*rclcg_wmsq
            baseCircleRadius_y = width*lcgBaseSize_y*rclcg_wmsq
        pps = (rm_x_x +baseCircleRadius_x*ppAngle_cos0,
               rm_x_x2+baseCircleRadius_x*ppAngle_cos1,
               rm_x_x2+baseCircleRadius_x*ppAngle_cos2,
               rm_x_x +baseCircleRadius_x*ppAngle_cos3,
               rm_y_y +baseCircleRadius_y*ppAngle_sin0,
               rm_y_y2+baseCircleRadius_y*ppAngle_sin1,
               rm_y_y2+baseCircleRadius_y*ppAngle_sin2,
               rm_y_y +baseCircleRadius_y*ppAngle_sin3)
        pps_x, pps_y = pps[0:4], pps[4:8]
        shapeBoundary_x0 = min(pps_x)
        shapeBoundary_x1 = max(pps_x)
        shapeBoundary_y0 = min(pps_y)
        shapeBoundary_y1 = max(pps_y)
        
        #[3]: LCG Allocation
        allocatedLCGPositions = self.__copyShapeToNewLCGSize_getAllocatedLCGPositions(newLCGSize, shapeBoundary_x0, shapeBoundary_x1, shapeBoundary_y0, shapeBoundary_y1)
        
        #[4]: Graphics Object Generation Queue Appending - Inactive LCG Sizes
        shapeInstanceGenerationParams_base = {'_shapeType': _RCLCG_SHAPETYPE_LINE, 
                                              'layerNumber': layerNumber,
                                              'coordinates': None, 
                                              'color': color}
        for position in allocatedLCGPositions:
            lcg_size = lcgs[newLCGSize]
            if (position not in lcg_size): _func_generateLCG(newLCGSize, position)
            lcg_pos = lcg_size[position]
            (px0, px1, px2, px3, py0, py1, py2, py3) = pps
            lcg_pos_x = lcg_pos['LCGPosition_x']
            lcg_pos_y = lcg_pos['LCGPosition_y']
            shapeInstanceGenerationParams = shapeInstanceGenerationParams_base.copy()
            shapeInstanceGenerationParams['coordinates'] = ((px0-lcg_pos_x, py0-lcg_pos_y), 
                                                            (px1-lcg_pos_x, py1-lcg_pos_y), 
                                                            (px2-lcg_pos_x, py2-lcg_pos_y), 
                                                            (px3-lcg_pos_x, py3-lcg_pos_y))
            _func_addShapeGenerationParams(newLCGSize, position, shapeGroupName, shapeName, shapeInstanceGenerationParams)
            
        #[5]: Add the drawing queue to the shape description
        self.__copyShapeToNewLCGSize_addToShapeDescriptions(newLCGSize, allocatedLCGPositions, shapeGroupName, shapeName)
    def __copyShapeToNewLCGSize_addToShapeDescriptions_BEZIERCURVE(self, newLCGSize, shapeDescription, shapeName, shapeGroupName = None):
        pass
    def __copyShapeToNewLCGSize_addToShapeDescriptions_ARC(self, newLCGSize, shapeDescription, shapeName, shapeGroupName = None):
        pass
    def __copyShapeToNewLCGSize_addToShapeDescriptions_TRIANGLE(self, newLCGSize, shapeDescription, shapeName, shapeGroupName = None):
        pass
    def __copyShapeToNewLCGSize_addToShapeDescriptions_RECTANGLE(self, newLCGSize, shapeDescription, shapeName, shapeGroupName = None):
        lcgs         = self.LCGs
        lcgSizeTable = self.LCGSizeTable
        rm_x = self.resMultiplier_x
        rm_y = self.resMultiplier_y
        _func_generateLCG              = self.__generateLCG
        _func_addShapeGenerationParams = self.__addShape_addShapeGenerationParams
        
        #[1]: ShapeDescription Localization
        x = shapeDescription['x']; width  = shapeDescription['width']
        y = shapeDescription['y']; height = shapeDescription['height']
        color       = shapeDescription['color']
        layerNumber = shapeDescription['layerNumber']
        
        #[2]: Coordinate Determination
        x_scaled = x*rm_x; width_scaled  = width *rm_x
        y_scaled = y*rm_y; height_scaled = height*rm_y
        shapeBoundary_x0 = x_scaled
        shapeBoundary_x1 = x_scaled+width_scaled
        shapeBoundary_y0 = y_scaled
        shapeBoundary_y1 = y_scaled+height_scaled

        #[3]: LCG Allocation
        allocatedLCGPositions = self.__copyShapeToNewLCGSize_getAllocatedLCGPositions(newLCGSize, shapeBoundary_x0, shapeBoundary_x1, shapeBoundary_y0, shapeBoundary_y1)
        
        #[4]: Graphics Object Generation Queue Appending - Inactive LCG Sizes
        shapeInstanceGenerationParams_base = {'_shapeType': _RCLCG_SHAPETYPE_RECTANGLE, 
                                              'layerNumber': layerNumber,
                                              'x': None, 
                                              'y': None, 
                                              'width':  width_scaled, 
                                              'height': height_scaled, 
                                              'color': color}
        for position in allocatedLCGPositions:
            lcg_size = lcgs[newLCGSize]
            if (position not in lcg_size): _func_generateLCG(newLCGSize, position)
            lcg_pos = lcg_size[position]
            shapeInstanceGenerationParams = shapeInstanceGenerationParams_base.copy()
            shapeInstanceGenerationParams['x'] = x_scaled-lcg_pos['LCGPosition_x']
            shapeInstanceGenerationParams['y'] = y_scaled-lcg_pos['LCGPosition_y']
            _func_addShapeGenerationParams(newLCGSize, position, shapeGroupName, shapeName, shapeInstanceGenerationParams)
            
        #[5]: Add the drawing queue to the shape description
        self.__copyShapeToNewLCGSize_addToShapeDescriptions(newLCGSize, allocatedLCGPositions, shapeGroupName, shapeName)
    def __copyShapeToNewLCGSize_addToShapeDescriptions_BORDEREDRECTANGLE(self, newLCGSize, shapeDescription, shapeName, shapeGroupName = None):
        pass
    def __copyShapeToNewLCGSize_addToShapeDescriptions_BOX(self, newLCGSize, shapeDescription, shapeName, shapeGroupName = None):
        pass
    def __copyShapeToNewLCGSize_addToShapeDescriptions_CIRCLE(self, newLCGSize, shapeDescription, shapeName, shapeGroupName = None):
        pass
    def __copyShapeToNewLCGSize_addToShapeDescriptions_ELLIPSE(self, newLCGSize, shapeDescription, shapeName, shapeGroupName = None):
        pass
    def __copyShapeToNewLCGSize_addToShapeDescriptions_SECTOR(self, newLCGSize, shapeDescription, shapeName, shapeGroupName = None):
        pass
    def __copyShapeToNewLCGSize_addToShapeDescriptions_POLYGON(self, newLCGSize, shapeDescription, shapeName, shapeGroupName = None):
        lcgs         = self.LCGs
        lcgSizeTable = self.LCGSizeTable
        rm_x = self.resMultiplier_x
        rm_y = self.resMultiplier_y
        _func_generateLCG              = self.__generateLCG
        _func_addShapeGenerationParams = self.__addShape_addShapeGenerationParams
        
        #[1]: ShapeDescription Localization
        coordinates = shapeDescription['coordinates']
        color       = shapeDescription['color']
        layerNumber = shapeDescription['layerNumber']

        #[2]: Coordinate Determination
        coordinates_resolutionScaled = [(coord_x*rm_x, coord_y*rm_y) for coord_x, coord_y in coordinates]
        xs, ys = zip(*coordinates_resolutionScaled)
        boundaries = (min(xs), max(xs), min(ys), max(ys))

        #[3]: LCG Allocation
        allocatedLCGPositions = self.__copyShapeToNewLCGSize_getAllocatedLCGPositions(newLCGSize, *boundaries)
        
        #[4]: Graphics Object Generation Queue Appending - Inactive LCG Sizes
        shapeInstanceGenerationParams_base = {'_shapeType': _RCLCG_SHAPETYPE_POLYGON, 
                                              'layerNumber': layerNumber,
                                              'coordinates': None, 
                                              'color': color}
        for position in allocatedLCGPositions:
            lcg_size = lcgs[newLCGSize]
            if (position not in lcg_size): _func_generateLCG(newLCGSize, position)
            lcg_pos = lcg_size[position]
            shapeInstanceGenerationParams = shapeInstanceGenerationParams_base.copy()
            shapeInstanceGenerationParams['coordinates'] = [(c_rs_x-lcg_pos['LCGPosition_x'], c_rs_y-lcg_pos['LCGPosition_y']) for c_rs_x, c_rs_y in coordinates_resolutionScaled]
            _func_addShapeGenerationParams(newLCGSize, position, shapeGroupName, shapeName, shapeInstanceGenerationParams)
            
        #[5]: Add the drawing queue to the shape description
        self.__copyShapeToNewLCGSize_addToShapeDescriptions(newLCGSize, allocatedLCGPositions, shapeGroupName, shapeName)

    def __copyShapeToNewLCGSize_getAllocatedLCGPositions(self, newLCGSize, shapeBoundary_x0, shapeBoundary_x1, shapeBoundary_y0, shapeBoundary_y1):
        lcgSize_full = self.LCGSizeTable[newLCGSize]
        lcgSize_x, lcgSize_y = lcgSize_full[4], lcgSize_full[5]
        lcgPosition_leftmost   = int(shapeBoundary_x0//lcgSize_x)
        lcgPosition_rightmost  = int(shapeBoundary_x1//lcgSize_x)
        lcgPosition_bottommost = int(shapeBoundary_y0//lcgSize_y)
        lcgPosition_topmost    = int(shapeBoundary_y1//lcgSize_y)
        allocatedLCGPositions = set((lcgPosition_x, lcgPosition_y)
                                    for lcgPosition_x in range (lcgPosition_leftmost,   lcgPosition_rightmost+1)
                                    for lcgPosition_y in range (lcgPosition_bottommost, lcgPosition_topmost  +1))
        return allocatedLCGPositions
    
    def __copyShapeToNewLCGSize_addToShapeDescriptions(self, newLCGSize, allocatedLCGPositions, shapeGroupName, shapeName):
        allocatedLCGs = set((newLCGSize, allocatedLCGPosition) for allocatedLCGPosition in allocatedLCGPositions)
        if (shapeGroupName is None): self.shapeDescriptions_ungrouped[shapeName]['allocatedLCGs_toProcess']               |= allocatedLCGs
        else:                        self.shapeDescriptions_grouped[shapeGroupName][shapeName]['allocatedLCGs_toProcess'] |= allocatedLCGs
    #COPYSHAPESTONEWLCGSIZE END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------










    #Shape Data Getters ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def getShapeNames(self, groupName = None):
        if groupName is None:
            sd_ungrouped = self.shapeDescriptions_ungrouped
            return list(sd_ungrouped)
        else:
            sd_grouped = self.shapeDescriptions_grouped
            if groupName in sd_grouped: return list(sd_grouped)
            else:                       return []
    #Shape Data Getters END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------










    #Shape Removal & RCLCG Clearing ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def removeShape(self, shapeName, groupName = None):
        sd_ungrouped = self.shapeDescriptions_ungrouped
        sd_grouped   = self.shapeDescriptions_grouped
        if groupName is None:
            if shapeName in sd_ungrouped: 
                lcgs = self.LCGs
                for lcgSize, position in sd_ungrouped[shapeName]['allocatedLCGs']:           lcgs[lcgSize][position]['shapes_ungrouped'].pop(shapeName)
                for lcgSize, position in sd_ungrouped[shapeName]['allocatedLCGs_toProcess']: lcgs[lcgSize][position]['toProcess_shapes_ungrouped'].pop(shapeName)
                sd_ungrouped.pop(shapeName, None)
                return True
            else: return False
        else:
            if (groupName in sd_grouped) and (shapeName in sd_grouped[groupName]):
                lcgs = self.LCGs
                for lcgSize, position in sd_grouped[groupName][shapeName]['allocatedLCGs']:   
                    lcgs_pos_sGrouped = lcgs[lcgSize][position]['shapes_grouped'][groupName]
                    lcgs_pos_sGrouped.pop(shapeName)
                    if not lcgs_pos_sGrouped: del lcgs[lcgSize][position]['shapes_grouped'][groupName]
                for lcgSize, position in sd_grouped[groupName][shapeName]['allocatedLCGs_toProcess']: 
                    lcgs_pos_tpsGrouped = lcgs[lcgSize][position]['toProcess_shapes_grouped'][groupName]
                    lcgs_pos_tpsGrouped.pop(shapeName)
                    if not lcgs_pos_tpsGrouped: del lcgs[lcgSize][position]['toProcess_shapes_grouped'][groupName]
                sd_grouped[groupName].pop(shapeName)
                if not sd_grouped[groupName]: del sd_grouped[groupName]
                return True
            else: return False

    def removeGroup(self, groupName):
        if (groupName not in self.shapeDescriptions_grouped): return False
        tLocs_grouped   = set()
        tLocs_toProcess = set()
        for shapeDesc in self.shapeDescriptions_grouped[groupName].values():
            tLocs_grouped   |= shapeDesc['allocatedLCGs']
            tLocs_toProcess |= shapeDesc['allocatedLCGs_toProcess']
        lcgs = self.LCGs
        for lcgSize, position in tLocs_grouped:   lcgs[lcgSize][position]['shapes_grouped'].pop(groupName)
        for lcgSize, position in tLocs_toProcess: lcgs[lcgSize][position]['toProcess_shapes_grouped'].pop(groupName)
        self.shapeDescriptions_grouped.pop(groupName)
        return True

    def removeAllUngrouped(self):
        lcgs = self.LCGs
        for lcgSize in lcgs:
            for position in lcgs[lcgSize]:
                lcgs[lcgSize][position]['shapes_ungrouped'].clear()
                lcgs[lcgSize][position]['toProcess_shapes_ungrouped'].clear()
        self.shapeDescriptions_ungrouped.clear()

    def clearAll(self):
        self.LCGs = dict()
        self.LCGSizes     = list()
        self.LCGSizeTable = dict()
        self.activeLCGSize = None
        self.shapeDescriptions_ungrouped = dict()
        self.shapeDescriptions_grouped   = dict()
    #Shape Removal & RCLCG Clearing END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------