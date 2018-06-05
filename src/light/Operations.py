from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

from PIL import Image, ImageOps
import math
from math import floor, ceil

import numpy as np
# from skimage import img_as_ubyte
# from skimage import transform

import os
import random
import warnings
import cv2

class Operation(object):
    """
    The class :class:`Operation` represents the base class for all operations
    that can be performed. Inherit from :class:`Operation`, overload 
    its methods, and instantiate super to create a new operation. See 
    the section on extending Augmentor with custom operations at 
    :ref:`extendingaugmentor`.
    """
    def __init__(self, probability):
        """
        All operations must at least have a :attr:`probability` which is 
        initialised when creating the operation's object.
        
        :param probability: Controls the probability that the operation is 
         performed when it is invoked in the pipeline. 
        :type probability: Float
        """
        self.probability = probability

    def __str__(self):
        """
        Used to display a string representation of the operation, which is 
        used by the :func:`Pipeline.status` to display the current pipeline's
        operations in a human readable way.
        
        :return: A string representation of the operation. Can be overridden 
         if required, for example as is done in the :class:`Rotate` class. 
        """
        return self.__class__.__name__

    def perform_operation(self, image):
        """
        Perform the operation on the image. Each operation must at least 
        have this function, which accepts an image of type PIL.Image, performs
        its operation, and returns an image of type PIL.Image.
        
        :param image: The image to transform.
        :type image: PIL.Image
        :return: The transformed image of type PIL.Image.
        """
        raise RuntimeError("Illegal call to base class.")
    
class Distort(Operation):
    """
    This class performs randomised, elastic distortions on images.
    """
    def __init__(self, probability, grid_width, grid_height, magnitude):
        """
        As well as the probability, the granularity of the distortions 
        produced by this class can be controlled using the width and
        height of the overlaying distortion grid. The larger the height
        and width of the grid, the smaller the distortions. This means
        that larger grid sizes can result in finer, less severe distortions.
        As well as this, the magnitude of the distortions vectors can 
        also be adjusted.
        
        :param probability: Controls the probability that the operation is 
         performed when it is invoked in the pipeline. 
        :param grid_width: The width of the gird overlay, which is used
         by the class to apply the transformations to the image.
        :param grid_height: The height of the gird overlay, which is used
         by the class to apply the transformations to the image.
        :param magnitude: Controls the degree to which each distortion is 
         applied to the overlaying distortion grid.
        :type probability: Float
        :type grid_width: Integer
        :type grid_height: Integer
        :type magnitude: Integer
        """
        Operation.__init__(self, probability)
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.magnitude = abs(magnitude)
        # TODO: Implement non-random magnitude.
        self.randomise_magnitude = True

    def perform_operation(self, image):
        """
        Distorts the passed image according to the parameters supplied during
        instantiation, returning the newly distorted image.
        
        :param image: The image to be distorted. 
        :type image: PIL.Image
        :return: The distorted image as type PIL.Image
        """
        w, h = image.size

        horizontal_tiles = self.grid_width
        vertical_tiles = self.grid_height

        width_of_square = int(floor(w / float(horizontal_tiles)))
        height_of_square = int(floor(h / float(vertical_tiles)))

        width_of_last_square = w - (width_of_square * (horizontal_tiles - 1))
        height_of_last_square = h - (height_of_square * (vertical_tiles - 1))

        dimensions = []

        for vertical_tile in range(vertical_tiles):
            for horizontal_tile in range(horizontal_tiles):
                if vertical_tile == (vertical_tiles - 1) and horizontal_tile == (horizontal_tiles - 1):
                    dimensions.append([horizontal_tile * width_of_square,
                                       vertical_tile * height_of_square,
                                       width_of_last_square + (horizontal_tile * width_of_square),
                                       height_of_last_square + (height_of_square * vertical_tile)])
                elif vertical_tile == (vertical_tiles - 1):
                    dimensions.append([horizontal_tile * width_of_square,
                                       vertical_tile * height_of_square,
                                       width_of_square + (horizontal_tile * width_of_square),
                                       height_of_last_square + (height_of_square * vertical_tile)])
                elif horizontal_tile == (horizontal_tiles - 1):
                    dimensions.append([horizontal_tile * width_of_square,
                                       vertical_tile * height_of_square,
                                       width_of_last_square + (horizontal_tile * width_of_square),
                                       height_of_square + (height_of_square * vertical_tile)])
                else:
                    dimensions.append([horizontal_tile * width_of_square,
                                       vertical_tile * height_of_square,
                                       width_of_square + (horizontal_tile * width_of_square),
                                       height_of_square + (height_of_square * vertical_tile)])

        # For loop that generates polygons could be rewritten, but maybe harder to read?
        # polygons = [x1,y1, x1,y2, x2,y2, x2,y1 for x1,y1, x2,y2 in dimensions]

        # last_column = [(horizontal_tiles - 1) + horizontal_tiles * i for i in range(vertical_tiles)]
        last_column = []
        for i in range(vertical_tiles):
            last_column.append((horizontal_tiles-1)+horizontal_tiles*i)

        last_row = range((horizontal_tiles * vertical_tiles) - horizontal_tiles, horizontal_tiles * vertical_tiles)

        polygons = []
        for x1, y1, x2, y2 in dimensions:
            polygons.append([x1, y1, x1, y2, x2, y2, x2, y1])

        polygon_indices = []
        for i in range((vertical_tiles * horizontal_tiles) - 1):
            if i not in last_row and i not in last_column:
                polygon_indices.append([i, i + 1, i + horizontal_tiles, i + 1 + horizontal_tiles])

        for a, b, c, d in polygon_indices:
            dx = random.randint(-self.magnitude, self.magnitude)
            dy = random.randint(-self.magnitude, self.magnitude)

            x1, y1, x2, y2, x3, y3, x4, y4 = polygons[a]
            polygons[a] = [x1, y1,
                           x2, y2,
                           x3 + dx, y3 + dy,
                           x4, y4]

            x1, y1, x2, y2, x3, y3, x4, y4 = polygons[b]
            polygons[b] = [x1, y1,
                           x2 + dx, y2 + dy,
                           x3, y3,
                           x4, y4]

            x1, y1, x2, y2, x3, y3, x4, y4 = polygons[c]
            polygons[c] = [x1, y1,
                           x2, y2,
                           x3, y3,
                           x4 + dx, y4 + dy]

            x1, y1, x2, y2, x3, y3, x4, y4 = polygons[d]
            polygons[d] = [x1 + dx, y1 + dy,
                           x2, y2,
                           x3, y3,
                           x4, y4]

        generated_mesh = []
        for i in range(len(dimensions)):
            generated_mesh.append([dimensions[i], polygons[i]])

        return image.transform(image.size, Image.MESH, generated_mesh, resample=Image.BICUBIC)
    
    

class GaussianDistortion(Operation):
    """
    This class performs randomised, elastic gaussian distortions on images.
    """
    def __init__(self, probability, grid_width, grid_height, magnitude, corner, method, mex, mey, sdx, sdy):
        """
        As well as the probability, the granularity of the distortions 
        produced by this class can be controlled using the width and
        height of the overlaying distortion grid. The larger the height
        and width of the grid, the smaller the distortions. This means
        that larger grid sizes can result in finer, less severe distortions.
        As well as this, the magnitude of the distortions vectors can 
        also be adjusted.
        
        :param probability: Controls the probability that the operation is 
         performed when it is invoked in the pipeline. 
        :param grid_width: The width of the gird overlay, which is used
         by the class to apply the transformations to the image.
        :param grid_height: The height of the gird overlay, which is used
         by the class to apply the transformations to the image.
        :param magnitude: Controls the degree to which each distortion is 
         applied to the overlaying distortion grid.
        :param corner: which corner of picture to distort. 
         Possible values: "bell"(circular surface applied), "ul"(upper left),
         "ur"(upper right), "dl"(down left), "dr"(down right).
        :param method: possible values: "in"(apply max magnitude to the chosen
         corner), "out"(inverse of method in).
        :param mex: used to generate 3d surface for similar distortions.
         Surface is based on normal distribution.
        :param mey: used to generate 3d surface for similar distortions.
         Surface is based on normal distribution.
        :param sdx: used to generate 3d surface for similar distortions.
         Surface is based on normal distribution.
        :param sdy: used to generate 3d surface for similar distortions.
         Surface is based on normal distribution.
        :type probability: Float
        :type grid_width: Integer
        :type grid_height: Integer
        :type magnitude: Integer
        :type corner: String
        :type method: String
        :type mex: Float
        :type mey: Float
        :type sdx: Float
        :type sdy: Float

        For values :attr:`mex`, :attr:`mey`, :attr:`sdx`, and :attr:`sdy` the
        surface is based on the normal distribution:

        .. math::

         e^{- \Big( \\frac{(x-\\text{mex})^2}{\\text{sdx}} + \\frac{(y-\\text{mey})^2}{\\text{sdy}} \Big) }
        """
        Operation.__init__(self, probability)
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.magnitude = abs(magnitude)
        # TODO: Implement non-random magnitude.
        self.randomise_magnitude = True
        self.corner = corner
        self.method = method
        self.mex = mex
        self.mey = mey
        self.sdx = sdx
        self.sdy = sdy

    def perform_operation(self, image):
        """
        Distorts the passed image according to the parameters supplied during
        instantiation, returning the newly distorted image.
        
        :param image: The image to be distorted. 
        :type image: PIL.Image
        :return: The distorted image as type PIL.Image
        """
        w, h = image.size

        horizontal_tiles = self.grid_width
        vertical_tiles = self.grid_height

        width_of_square = int(floor(w / float(horizontal_tiles)))
        height_of_square = int(floor(h / float(vertical_tiles)))

        width_of_last_square = w - (width_of_square * (horizontal_tiles - 1))
        height_of_last_square = h - (height_of_square * (vertical_tiles - 1))

        dimensions = []

        for vertical_tile in range(vertical_tiles):
            for horizontal_tile in range(horizontal_tiles):
                if vertical_tile == (vertical_tiles - 1) and horizontal_tile == (horizontal_tiles - 1):
                    dimensions.append([horizontal_tile * width_of_square,
                                       vertical_tile * height_of_square,
                                       width_of_last_square + (horizontal_tile * width_of_square),
                                       height_of_last_square + (height_of_square * vertical_tile)])
                elif vertical_tile == (vertical_tiles - 1):
                    dimensions.append([horizontal_tile * width_of_square,
                                       vertical_tile * height_of_square,
                                       width_of_square + (horizontal_tile * width_of_square),
                                       height_of_last_square + (height_of_square * vertical_tile)])
                elif horizontal_tile == (horizontal_tiles - 1):
                    dimensions.append([horizontal_tile * width_of_square,
                                       vertical_tile * height_of_square,
                                       width_of_last_square + (horizontal_tile * width_of_square),
                                       height_of_square + (height_of_square * vertical_tile)])
                else:
                    dimensions.append([horizontal_tile * width_of_square,
                                       vertical_tile * height_of_square,
                                       width_of_square + (horizontal_tile * width_of_square),
                                       height_of_square + (height_of_square * vertical_tile)])

        # For loop that generates polygons could be rewritten, but maybe harder to read?
        # polygons = [x1,y1, x1,y2, x2,y2, x2,y1 for x1,y1, x2,y2 in dimensions]

        # last_column = [(horizontal_tiles - 1) + horizontal_tiles * i for i in range(vertical_tiles)]
        last_column = []
        for i in range(vertical_tiles):
            last_column.append((horizontal_tiles-1)+horizontal_tiles*i)

        last_row = range((horizontal_tiles * vertical_tiles) - horizontal_tiles, horizontal_tiles * vertical_tiles)

        polygons = []
        for x1, y1, x2, y2 in dimensions:
            polygons.append([x1, y1, x1, y2, x2, y2, x2, y1])

        polygon_indices = []
        for i in range((vertical_tiles * horizontal_tiles) - 1):
            if i not in last_row and i not in last_column:
                polygon_indices.append([i, i + 1, i + horizontal_tiles, i + 1 + horizontal_tiles])
         
        def sigmoidf(x,y, sdx=0.05, sdy=0.05, mex=0.5, mey=0.5, const=1):
            #print(sdx, sdy, mex, mey, const)
            sigmoid = lambda x1, y1:  (const * (math.exp(-(((x1-mex)**2)/sdx + ((y1-mey)**2)/sdy) )) + max(0,-const) - max(0, const)) 
            xl = np.linspace(0,1)
            yl =  np.linspace(0, 1)
            X, Y = np.meshgrid(xl, yl)
        
            Z = np.vectorize(sigmoid)(X, Y)
            #res = (const * (math.exp(-((x-me)**2 + (y-me)**2)/sd )) + max(0,-const) - max(0, const)) 
            mino = np.amin(Z)
            maxo = np.amax(Z)
            res = sigmoid(x, y)
            res= max(((((res - mino) * (1 - 0)) / (maxo - mino)) + 0), 0.01)*self.magnitude
            return res

        def corner(x, y, corner="ul", method="out", sdx=0.05, sdy=0.05, mex=0.5, mey=0.5):
            #NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
            #x_min, x_max, y_min, y_max
            ll = {'dr':(0, 0.5, 0, 0.5),'dl':(0.5,1, 0, 0.5),'ur':(0, 0.5, 0.5, 1), 'ul':( 0.5,1, 0.5, 1), 'bell':(0,1, 0,1)}
            new_c = ll[corner]
            new_x= (((x - 0) * (new_c[1] - new_c[0])) / (1 - 0)) + new_c[0]
            new_y= (((y - 0) * (new_c[3] - new_c[2])) / (1 - 0)) + new_c[2]
            if method=="in":
                const=1
            else:
                if method=="out":
                   const=-1
                else: 
                   print('Mehtod can be "out" or "in", "in" used as default')
                   const=1
            res = sigmoidf(x=new_x, y=new_y,sdx=sdx, sdy=sdy, mex=mex, mey=mey, const=const)
            #print(x, y, new_x, new_y, self.magnitude,  res)
            return res

        
        for a, b, c, d in polygon_indices:
            #dx = random.randint(-self.magnitude, self.magnitude)
            #dy = random.randint(-self.magnitude, self.magnitude)
            x1, y1, x2, y2, x3, y3, x4, y4 = polygons[a]
            #sigmax = sigmoid(x3, y3)
            
            sigmax= corner(x=x3/w, y=y3/h, corner=self.corner, method=self.method, sdx=self.sdx, sdy=self.sdy, mex=self.mex, mey=self.mey)
            dx = np.random.normal(0, sigmax, 1)[0]
            dy = np.random.normal(0, sigmax, 1)[0]
            polygons[a] = [x1, y1,
                           x2, y2,
                           x3 + dx, y3 + dy,
                           x4, y4]

            x1, y1, x2, y2, x3, y3, x4, y4 = polygons[b]
            polygons[b] = [x1, y1,
                           x2 + dx, y2 + dy,
                           x3, y3,
                           x4, y4]

            x1, y1, x2, y2, x3, y3, x4, y4 = polygons[c]
            polygons[c] = [x1, y1,
                           x2, y2,
                           x3, y3,
                           x4 + dx, y4 + dy]

            x1, y1, x2, y2, x3, y3, x4, y4 = polygons[d]
            polygons[d] = [x1 + dx, y1 + dy,
                           x2, y2,
                           x3, y3,
                           x4, y4]

        generated_mesh = []
        for i in range(len(dimensions)):
            generated_mesh.append([dimensions[i], polygons[i]])

        return image.transform(image.size, Image.MESH, generated_mesh, resample=Image.BICUBIC)
    
class Shear(Operation):
    """
    This class is used to shear images, that is to tilt them in a certain
    direction. Tilting can occur along either the x- or y-axis and in both 
    directions (i.e. left or right along the x-axis, up or down along the 
    y-axis).
    
    Images are sheared **in place** and an image of the same size as the input 
    image is returned by this class. That is to say, that after a shear
    has been performed, the largest possible area of the same aspect ratio
    of the original image is cropped from the sheared image, and this is 
    then resized to match the original image size. The 
    :ref:`shearing` section describes this in detail.
    
    For sample code with image examples see :ref:`shearing`.
    """
    def __init__(self, probability, max_shear_left, max_shear_right):
        """
        The shearing is randomised in magnitude, from 0 to the 
        :attr:`max_shear_left` or 0 to :attr:`max_shear_right` where the 
        direction is randomised. The shear axis is also randomised
        i.e. if it shears up/down along the y-axis or 
        left/right along the x-axis. 

        :param probability: Controls the probability that the operation is 
         performed when it is invoked in the pipeline. 
        :param max_shear_left: The maximum shear to the left.
        :param max_shear_right: The maximum shear to the right.
        :type probability: Float
        :type max_shear_left: Integer
        :type max_shear_right: Integer
        """
        Operation.__init__(self, probability)
        self.max_shear_left = max_shear_left
        self.max_shear_right = max_shear_right

    def perform_operation(self, image):
        """
        Shears the passed image according to the parameters defined during 
        instantiation, and returns the sheared image.
        
        :param image: The image to shear.
        :type image: PIL.Image
        :return: The sheared image of type PIL.Image
        """
        ######################################################################
        # Old version which uses SciKit Image
        ######################################################################
        # We will use scikit-image for this so first convert to a matrix
        # using NumPy
        # amount_to_shear = round(random.uniform(self.max_shear_left, self.max_shear_right), 2)
        # image_array = np.array(image)
        # And here we are using SciKit Image's `transform` class.
        # shear_transformer = transform.AffineTransform(shear=amount_to_shear)
        # image_sheared = transform.warp(image_array, shear_transformer)
        #
        # Because of warnings
        # with warnings.catch_warnings():
        #     warnings.simplefilter("ignore")
        #     return Image.fromarray(img_as_ubyte(image_sheared))
        ######################################################################

        width, height = image.size

        # For testing.
        # max_shear_left = 20
        # max_shear_right = 20

        angle_to_shear = int(random.uniform((abs(self.max_shear_left)*-1) - 1, self.max_shear_right + 1))
        if angle_to_shear != -1: angle_to_shear += 1

        # We use the angle phi in radians later
        phi = math.tan(math.radians(angle_to_shear))

        # Alternative method
        # Calculate our offset when cropping
        # We know one angle, phi (angle_to_shear)
        # We known theta = 180-90-phi
        # We know one side, opposite (height of image)
        # Adjacent is therefore:
        # tan(theta) = opposite / adjacent
        # A = opposite / tan(theta)
        # theta = math.radians(180-90-angle_to_shear)
        # A = height / math.tan(theta)

        # Transformation matrices can be found here:
        # https://en.wikipedia.org/wiki/Transformation_matrix
        # The PIL affine transform expects the first two rows of
        # any of the affine transformation matrices, seen here:
        # https://en.wikipedia.org/wiki/Transformation_matrix#/media/File:2D_affine_transformation_matrix.svg

        directions = ["x", "y"]
        direction = random.choice(directions)

        if direction == "x":
            # Here we need the unknown b, where a is
            # the height of the image and phi is the
            # angle we want to shear (our knowns):
            # b = tan(phi) * a
            shift_in_pixels = phi * height

            if shift_in_pixels > 0:
                shift_in_pixels = math.ceil(shift_in_pixels)
            else:
                shift_in_pixels = math.floor(shift_in_pixels)

            # For negative tilts, we reverse phi and set offset to 0
            # Also matrix offset differs from pixel shift for neg
            # but not for pos so we will copy this value in case
            # we need to change it
            matrix_offset = shift_in_pixels
            if angle_to_shear <= 0:
                shift_in_pixels = abs(shift_in_pixels)
                matrix_offset = 0
                phi = abs(phi) * -1

            # Note: PIL expects the inverse scale, so 1/scale_factor for example.
            transform_matrix = (1, phi, -matrix_offset,
                                0, 1, 0)

            image = image.transform((int(round(width + shift_in_pixels)), height),
                                    Image.AFFINE,
                                    transform_matrix,
                                    Image.BICUBIC)

            image = image.crop((abs(shift_in_pixels), 0, width, height))

            return image.resize((width, height), resample=Image.BICUBIC)

        elif direction == "y":
            shift_in_pixels = phi * width

            matrix_offset = shift_in_pixels
            if angle_to_shear <= 0:
                shift_in_pixels = abs(shift_in_pixels)
                matrix_offset = 0
                phi = abs(phi) * -1

            transform_matrix = (1, 0, 0,
                                phi, 1, -matrix_offset)

            image = image.transform((width, int(round(height + shift_in_pixels))),
                                    Image.AFFINE,
                                    transform_matrix,
                                    Image.BICUBIC)

            image = image.crop((0, abs(shift_in_pixels), width, height))
            print(type(width), type(height))
            print(width, height)
            return image.resize((width, height), resample=Image.BICUBIC)
        
        
# class LoiTGRotate(Operation): 
#     def __init__(self, probability, angle_range=(-3,3)):
#         Operation.__init__(self, probability)
#     def perform_operation(self, image):
#         x = image.size[0]
#         y = image.size[1]
#         image = image.rotate(rotation, expand=True, resample=Image.BICUBIC)
    
      
class RotateRange(Operation):
    """
    This class is used to perform rotations on images by arbitrary numbers of
    degrees.

    Images are rotated **in place** and an image of the same size is
    returned by this function. That is to say, that after a rotation
    has been performed, the largest possible area of the same aspect ratio
    of the original image is cropped from the skewed image, and this is 
    then resized to match the original image size.

    The method by which this is performed is described as follows:

    .. math::

        E = \\frac{\\frac{\\sin{\\theta_{a}}}{\\sin{\\theta_{b}}}\\Big(X-\\frac{\\sin{\\theta_{a}}}{\\sin{\\theta_{b}}} Y\\Big)}{1-\\frac{(\\sin{\\theta_{a}})^2}{(\\sin{\\theta_{b}})^2}}

    which describes how :math:`E` is derived, and then follows
    :math:`B = Y - E` and :math:`A = \\frac{\\sin{\\theta_{a}}}{\\sin{\\theta_{b}}} B`.

    The :ref:`rotating` section describes this in detail and has example
    images to demonstrate this.
    """
    def __init__(self, probability, max_left_rotation, max_right_rotation):
        """
        As well as the required :attr:`probability` parameter, the 
        :attr:`max_left_rotation` parameter controls the maximum number of 
        degrees by which to rotate to the left, while the 
        :attr:`max_right_rotation` controls the maximum number of degrees to
        rotate to the right. 

        :param probability: Controls the probability that the operation is 
         performed when it is invoked in the pipeline. 
        :param max_left_rotation: The maximum number of degrees to rotate 
         the image anti-clockwise.
        :param max_right_rotation: The maximum number of degrees to rotate
         the image clockwise.
        :type probability: Float
        :type max_left_rotation: Integer
        :type max_right_rotation: Integer
        """
        Operation.__init__(self, probability)
        self.max_left_rotation = -abs(max_left_rotation)   # Ensure always negative
        self.max_right_rotation = abs(max_right_rotation)  # Ensure always positive

    def perform_operation(self, image):
        """
        Perform the rotation on the passed :attr:`image` and return
        the transformed image. Uses the :attr:`max_left_rotation` and 
        :attr:`max_right_rotation` passed into the constructor to control
        the amount of degrees to rotate by. Whether the image is rotated 
        clockwise or anti-clockwise is chosen at random.
        
        :param image: The image to rotate.
        :type image: PIL.Image
        :return: The rotated image as type PIL.Image
        """
        # TODO: Small rotations of 1 or 2 degrees sometimes results in black pixels in the corners. Fix.
        random_left = random.randint(self.max_left_rotation, 0)
        random_right = random.randint(0, self.max_right_rotation)

        left_or_right = random.randint(0, 1)

        rotation = 0

        if left_or_right == 0:
            rotation = random_left
        elif left_or_right == 1:
            rotation = random_right

        # Get size before we rotate
        x = image.size[0]
        y = image.size[1]

        # Rotate, while expanding the canvas size
        image = image.rotate(rotation, expand=True, resample=Image.BICUBIC)

        # Get size after rotation, which includes the empty space
        X = image.size[0]
        Y = image.size[1]

        # Get our two angles needed for the calculation of the largest area
        angle_a = abs(rotation)
        angle_b = 90 - angle_a

        # Python deals in radians so get our radians
        angle_a_rad = math.radians(angle_a)
        angle_b_rad = math.radians(angle_b)

        # Calculate the sins
        angle_a_sin = math.sin(angle_a_rad)
        angle_b_sin = math.sin(angle_b_rad)

        # Find the maximum area of the rectangle that could be cropped
        E = (math.sin(angle_a_rad)) / (math.sin(angle_b_rad)) * \
            (Y - X * (math.sin(angle_a_rad) / math.sin(angle_b_rad)))
        E = E / 1 - (math.sin(angle_a_rad) ** 2 / math.sin(angle_b_rad) ** 2)
        B = X - E
        A = (math.sin(angle_a_rad) / math.sin(angle_b_rad)) * B

        # Crop this area from the rotated image
        # image = image.crop((E, A, X - E, Y - A))
        image = image.crop((int(round(E)), int(round(A)), int(round(X - E)), int(round(Y - A))))

        # Return the image, re-sized to the size of the image passed originally
        return image.resize((x, y), resample=Image.BICUBIC)