from ..Qt import QtGui, QtCore
from .GraphicsObject import GraphicsObject
from .. import getConfigOption
from .. import functions as fn
import numpy as np


__all__ = ['StickPlotItem']
class StickPlotItem(GraphicsObject):
    """
    Provides a stick plot item that is based on the BarGraphItem from,
    but modified so that it knows about setData(), and only draws single
    lines instead of rectangles (much better performance).
    
    When initialized, the data must be supplied (even if only empty).
    The data must be named x and y (or height).
    
    Note that no widths/brushes are used, but a pen can be defined that
    may include an explicit width.
    """
    def __init__(self, **opts):
        """
        Valid keyword options are:
        x, y, y0, y1, height, pen
        
        x specifies the x-position of the center of the line.
            
        y specifies the y-position of the center of the line, which along
        with height, defines y0 & y1. If only height is specified, then
        y0 will be set to 0.
        
        Example uses:
        
            BarGraphItem(x=range(5), height=[1,5,2,4,3])
            
        
        """
        GraphicsObject.__init__(self)
        self.opts = dict(
            name=None,
            x=None,
            y=None,
            y0=None,
            y1=None,
            height=None,
            pen=None,
            pens=None,
        )
        self.boundingCorners = [0, 0, 0, 0]
        self.picture = None
        self.setOpts(**opts)
    
    def setOpts(self, **opts):
        self.opts.update(opts)
        self.picture = None
        self.update()
        self.informViewBoundsChanged()
    
    def drawPicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        
        pen = self.opts['pen']
        pens = self.opts['pens']
        
        if pen is None and pens is None:
            pen = getConfigOption('foreground')
        
        def asarray(x):
            if x is None or np.isscalar(x) or isinstance(x, np.ndarray):
                return x
            return np.array(x)
        
        x = asarray(self.opts.get('x'))
        y = asarray(self.opts.get('y'))
        y0 = asarray(self.opts.get('y0'))
        y1 = asarray(self.opts.get('y1'))
        height = asarray(self.opts.get('height'))
        
        if (y is not None) and (height is not None):
            y0 = y - height/2
            y1 = y + height/2
        elif (y is None) and (height is not None):
            y0 = 0
            y1 = height
        elif (y0 is None) and (y1 is None):
            raise Exception('You must specify x and one of these combinations: (y & height), (only height), or (y0 and y1).')
        
        self.boundingCorners = [0, 0, 0, 0]
        if (len(x) > 0):
            self.boundingCorners[0] = x.min()
            self.boundingCorners[0] = x.max()
        if (len(x) > 0):
            self.boundingCorners[1] = y0.min()
            self.boundingCorners[3] = y1.max()
        
        p.setPen(fn.mkPen(pen))
        for i in range(len(x)):
            if pens is not None:
                p.setPen(fn.mkPen(pens[i]))
            
            if np.isscalar(x):
                x0 = x
            else:
                x0 = x[i]
            if np.isscalar(y0):
                y_lo = y0
            else:
                y_lo = y0[i]
            if np.isscalar(y1):
                y_up = y1
            else:
                y_up = y1[i]
            
            p.drawLine(QtCore.QLineF(x0, y_lo, x0, y_up))
            
        p.end()
        self.prepareGeometryChange()
    
    
    def paint(self, p, *args):
        if self.picture is None:
            self.drawPicture()
        self.picture.play(p)
    
    def shape(self):
        if self.picture is None:
            self.drawPicture()
        return self._shape
    
    def setData(self, *args, **kargs):
        """
        Clears any data displayed by this item and displays new data.
        
        Note that this was taken directly from the PyQtGraph API code.
        See :func:`__init__() <pyqtgraph.PlotDataItem.__init__>` for details; it accepts the same arguments.
        """
        name = None
        x = None
        y = None
        y0 = None
        y1 = None
        height = None
        pen = None
        pens = None
        if 'x' in kargs:
            x = kargs['x']
        if 'y' in kargs:
            height = kargs['y']
        if 'y0' in kargs:
            height = kargs['y0']
        if 'y1' in kargs:
            height = kargs['y1']
        if 'height' in kargs:
            height = kargs['height']
        if 'pen' in kargs:
            height = kargs['pen']
        
        opts = dict(
            name=name,
            x=x,
            y=y,
            y0=y0,
            y1=y1,
            height=height,
            pen=pen,
            pens=pens)
        self.setOpts(**opts)
    
    def name(self):
        """
        Returns the name of the plot, as normally set during
        initialization. This provides compatibility with a normal pg
        PlotItem.
        """
        return self.opts.get('name')
            
    def boundingRect(self):
        """
        Returns a QRectF based on the bounding corners that are updated
        within drawPicture(). Note that this differs significantly from
        BarGraphItem, because it was found that very small ranges in the
        y-data round up to [0..1].
        """
        if self.picture is None:
            self.drawPicture()
        return QtCore.QRectF(
            self.boundingCorners[0],
            self.boundingCorners[1],
            self.boundingCorners[2],
            self.boundingCorners[3]
        )
