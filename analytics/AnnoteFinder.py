import matplotlib
matplotlib.use('TkAgg')

import pylab
import math
from easygui import *
import copy


class AnnoteFinder:
    """
    callback for matplotlib to display an annotation when points are clicked on.  The
    point which is closest to the click and within xtol and ytol is identified.
      
    Register this function like this:
      
    scatter(xdata, ydata)
    af = AnnoteFinder(xdata, ydata, annotes)
    connect('button_press_event', af)
    """

    def __init__(self, xdata, ydata, annotes, axis=None, xtol=None, ytol=None):
        
        self.xdata = xdata
        self.ydata = ydata
        self.annotes = annotes
        self.data = zip(xdata, ydata, annotes)
        if xtol is None:
            xtol = ((max(xdata) - min(xdata))/float(len(xdata)))/2
        if ytol is None:
            ytol = ((max(ydata) - min(ydata))/float(len(ydata)))/2
        self.xtol = xtol
        self.ytol = ytol
        if axis is None:
            self.axis = pylab.gca()
        else:
            self.axis= axis
        self.drawnAnnotations = {}
        self.links = []
    
    def distance(self, x1, x2, y1, y2):
        """
        return the distance between two points
        """
        return math.hypot(x1 - x2, y1 - y2)

    def __call__(self, event):
        if event.inaxes:
            clickX = event.xdata
            clickY = event.ydata
            if self.axis is None or self.axis==event.inaxes:
                annotes = []
            for x,y,a in zip(self.xdata,self.ydata,self.annotes):
                if  clickX-self.xtol < x < clickX+self.xtol and  clickY-self.ytol < y < clickY+self.ytol :
                    annotes.append((self.distance(x,clickX,y,clickY),x,y, a) )
            if annotes:
                annotes.sort()
                distance, x, y, annote = annotes[0]
                self.drawAnnote(event.inaxes, x, y, annote)
            for l in self.links:
                l.drawSpecificAnnote(annote)
                
                
    def msg(self,m,t):
    
        textbox(text=m,title=t)
        

    def drawAnnote(self, axis, x, y, annote):
        """
        Draw the annotation on the plot
        """
        if (x,y) in self.drawnAnnotations:
            markers = self.drawnAnnotations[(x,y)]
            for m in markers:
                m.set_visible(not m.get_visible())
            self.axis.figure.canvas.draw()
           
        else:
            #t = axis.text(x,y, "(%3.2f, %3.2f) - %s"%(x,y,msg(annote)), )
            #m = axis.scatter([x],[y], marker='d', c='r', zorder=100)
            #self.drawnAnnotations[(x,y)] =(t,m)
            #self.axis.figure.canvas.draw()
            
            self.msg(annote,annote[-1])

    def drawSpecificAnnote(self, annote):
        annotesToDraw = [(x,y,a) for x,y,a in self.data if a==annote]
        for x,y,a in annotesToDraw:
            self.drawAnnote(self.axis, x, y, a)
    