'''
Created on Jan 17, 2018

@author: loitg
'''
import numpy as np 
from poisson_reconstruct import blit_images


def sample_weighted(p_dict):
    ps = p_dict.keys()
    return ps[np.random.choice(len(ps),p=p_dict.values())]

class Layer(object):

    def __init__(self,alpha,color):

        # alpha for the whole image:
        assert alpha.ndim==2
        self.alpha = alpha
        [n,m] = alpha.shape[:2]

        color=np.atleast_1d(np.array(color)).astype('uint8')
        # color for the image:
        if color.ndim==1: # constant color for whole layer
            ncol = color.size
            if ncol == 1 : #grayscale layer
                self.color = color * np.ones((n,m,3),'uint8')
            if ncol == 3 : 
                self.color = np.ones((n,m,3),'uint8') * color[None,None,:]
        elif color.ndim==2: # grayscale image
            self.color = np.repeat(color[:,:,None],repeats=3,axis=2).copy().astype('uint8')
        elif color.ndim==3: #rgb image
            self.color = color.copy().astype('uint8')
        else:
            print color.shape
            raise Exception("color datatype not understood")



class Colorize(object):

    def __init__(self):
        pass

    def blend(self,cf,cb,mode='normal'):
        return cf

    def merge_two(self,fore,back,blend_type=None):
        """
        merge two FOREground and BACKground layers.
        ref: https://en.wikipedia.org/wiki/Alpha_compositing
        ref: Chapter 7 (pg. 440 and pg. 444):
             http://partners.adobe.com/public/developer/en/pdf/PDFReference.pdf
        """
        a_f = fore.alpha/255.0
        a_b = back.alpha/255.0
        c_f = fore.color
        c_b = back.color

        a_r = a_f + a_b - a_f*a_b
        if blend_type != None:
            c_blend = self.blend(c_f, c_b, blend_type)
            c_r = (   ((1-a_f)*a_b)[:,:,None] * c_b
                    + ((1-a_b)*a_f)[:,:,None] * c_f
                    + (a_f*a_b)[:,:,None] * c_blend   )
        else:
            c_r = (   ((1-a_f)*a_b)[:,:,None] * c_b
                    + a_f[:,:,None]*c_f    )

        return Layer((255*a_r).astype('uint8'), c_r.astype('uint8'))

    def merge_down(self, layers, blends=None):
        """
        layers  : [l1,l2,...ln] : a list of LAYER objects.
                 l1 is on the top, ln is the bottom-most layer.
        blend   : the type of blend to use. Should be n-1.
                 use None for plain alpha blending.
        Note    : (1) it assumes that all the layers are of the SAME SIZE.
        @return : a single LAYER type object representing the merged-down image
        """
        nlayers = len(layers)
        if nlayers > 1:
            [n,m] = layers[0].alpha.shape[:2]
            out_layer = layers[-1]
            for i in range(-2,-nlayers-1,-1):
                blend=None
                if blends is not None:
                    blend = blends[i+1]
                    out_layer = self.merge_two(fore=layers[i], back=out_layer,blend_type=blend)
            return out_layer
        else:
            return layers[0]



    def process(self, text_arr, bg_arr, min_h):
        """
        text_arr : one alpha mask : nxm, uint8
        bg_arr   : background image: nxmx3, uint8
        min_h    : height of the smallest character (px)

        return text_arr blit onto bg_arr.
        """
        # decide on a color for the text:
        l_text, fg_col, bg_col = self.color_text(text_arr, min_h, bg_arr)
        bg_col = np.mean(np.mean(bg_arr,axis=0),axis=0)
        l_bg = Layer(alpha=255*np.ones_like(text_arr,'uint8'),color=bg_col)

        l_text.alpha = l_text.alpha * np.clip(0.88 + 0.1*np.random.randn(), 0.72, 1.0)
        layers = [l_text]
        blends = []

        # add border:
        if np.random.rand() < self.p_border:
            if min_h <= 15 : bsz = 1
            elif 15 < min_h < 30: bsz = 3
            else: bsz = 5
            border_a = self.border(l_text.alpha, size=bsz)
            l_border = Layer(border_a, self.color_border(l_text.color,l_bg.color))
            layers.append(l_border)
            blends.append('normal')

        # add shadow:
        if np.random.rand() < self.p_drop_shadow:
            # shadow gaussian size:
            if min_h <= 15 : bsz = 1
            elif 15 < min_h < 30: bsz = 3
            else: bsz = 5

            # shadow angle:
            theta = np.pi/4 * np.random.choice([1,3,5,7]) + 0.5*np.random.randn()

            # shadow shift:
            if min_h <= 15 : shift = 2
            elif 15 < min_h < 30: shift = 7+np.random.randn()
            else: shift = 15 + 3*np.random.randn()

            # opacity:
            op = 0.50 + 0.1*np.random.randn()

            shadow = self.drop_shadow(l_text.alpha, theta, shift, 3*bsz, op)
            l_shadow = Layer(shadow, 0)
            layers.append(l_shadow)
            blends.append('normal')
        

        l_bg = Layer(alpha=255*np.ones_like(text_arr,'uint8'), color=bg_col)
        layers.append(l_bg)
        blends.append('normal')
        l_normal = self.merge_down(layers,blends)
        # now do poisson image editing:
        l_bg = Layer(alpha=255*np.ones_like(text_arr,'uint8'), color=bg_arr)
        l_out =  blit_images(l_normal.color,l_bg.color.copy())
        
        # plt.subplot(1,3,1)
        # plt.imshow(l_normal.color)
        # plt.subplot(1,3,2)
        # plt.imshow(l_bg.color)
        # plt.subplot(1,3,3)
        # plt.imshow(l_out)
        # plt.show()
        
        if l_out is None:
            # poisson recontruction produced
            # imperceptible text. In this case,
            # just do a normal blend:
            layers[-1] = l_bg
            return self.merge_down(layers,blends).color

        return l_out
