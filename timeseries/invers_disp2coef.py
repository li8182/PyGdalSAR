#!/usr/bin/env python3
# -*- coding: utf-8 -*-
############################################
#
# PyGdalSAR: An InSAR post-processing package 
# written in Python-Gdal
#
############################################
# Author        : Simon DAOUT (Oxford)
############################################

"""\
invers_disp2coef.py
-------------
Spatial and temporal inversions of the time series delay maps (used depl_cumule (BIP format) and images_retenues, output of invers_pixel), based on an iteration procedure.
At each iteration, (1) estimation of spatial ramps, (2) linear decomposition in time based on a library of temporal functions (linear, heaviside, logarithm, seasonal),
(3) estimation of RMS that will be then used as weight for the next iteration. Possibility to also to correct for a term proportional to the topography.

Usage: invers_disp2coef.py  [--cube=<path>] [--lectfile=<path>] [--list_images=<path>] [--aps=<path>] [--ref=<jstart,jend,istart,iend> ] [--refstart=<value>] [--refend=<value>] [--linear=<yes/no>]  \
[--coseismic=<values>] [--postseismic=<values>]  [--seasonal=<yes/no>] [--slowslip=<values>] [--semianual=<yes/no>]  [--dem=<yes/no>] [--vector=<path>] \
[--flat=<0/1/2/3/4/5/6/7/8/9>] [--nfit=<0/1>] [--ivar=<0/1>] [--niter=<value>]  [--spatialiter=<yes/no>]  [--sampling=<value>] [--imref=<value>] [--mask=<path>] \
[--rampmask=<yes/no>] [--threshold_mask=<value>] [--scale_mask=<value>] [--topofile=<path>] [--aspect=<path>] [--perc_topo=<value>] [--perc_los=<value>] \
[--tempmask=<yes/no>] [--cond=<value>] [--ineq=<value>] [--rmspixel=<path>] [--threshold_rms=<path>] \
[--crop=<values>] [--crop_emp=<values>] [--fulloutput=<yes/no>] [--geotiff=<path>] [--plot=<yes/no>] \
[--dateslim=<values_min,value_max>]  [--nproc=<nb_cores>] \
[<ibeg>] [<iend>] [<jbeg>] [<jend>] 

invers_disp2coef.py -h | --help

Options:
-h --help               Show this screen
--cube PATH             Path to displacement file [default: depl_cumul]
--lectfile PATH         Path to the lect.in file (output of invers_pixel) [default: lect.in]
--list_images PATH      Path to list images file made of 5 columns containing for each images 1) number 2) Doppler freq (not read) 3) date in YYYYMMDD format 4) numerical date 5) perpendicular baseline [default: images_retenues]
--aps PATH              Path to the APS file giving an input error to each dates [default: No weigthing if no spatial estimation or misfit spatial estimation used as input uncertianties]
--rmspixel PATH         Path to the RMS map that gives an error for each pixel (e.g RMSpixel, output of invers_pixel) [default: None]
--threshold_rms VALUE   Threshold on rmsmap for spatial estimations [default: 1.]
--linear YES/NO         Add a linear function in the inversion [default:yes]
--coseismic PATH        Add heaviside functions to the inversion, indicate coseismic time (e.g 2004.,2006.)
--postseismic PATH      Add logarithmic transients to each coseismic step, indicate characteristic time of the log function, must be a serie of values of the same lenght than coseismic (e.g 1.,1.). To not associate postseismic function to a give coseismic step, put None (e.g None,1.)
--slowslip   VALUE      Add slow-slip function in the inversion (as defined by Larson et al., 2004). Indicate median and characteristic time of the events (e.g. 2004.,1,2006,0.5), [default: None]
--vector PATH           Path to the vector text files containing a value for each dates
--seasonal YES/NO       If yes, add seasonal terms in the inversion
--semianual YES/NO      If yes, add semianual terms in the inversion
--dem Yes/No            If yes, add term proportional to the perpendicular baseline in the inversion
--ivar VALUE            Define phase/elevation relationship: ivar=0 function of elevation, ivar=1 crossed function of azimuth and elevation
--nfit VALUE            Fit degree in azimuth or in elevation [0:linear (default), 1: quadratic]
--flat PATH             Remove a spatial ramp at each iteration.
0: ref frame [default], 1: range ramp ax+b , 2: azimutal ramp ay+b, 3: ax+by+c,
4: ax+by+cxy+d 5: ax**2+bx+cy+d, 6: ay**2+by+cx+d, 7: ay**2+by+cx**2+dx+e,
8: ay**2+by+cx**3+dx**2+ex+f, 9: ax+by+cxy**2+dxy+e
--niter VALUE           Number of iterations. At the first iteration, image uncertainties is given by aps file or misfit spatial iteration, while for the next itarations, uncertainties are equals to the global RMS of the previous iteration for each map [default: 1]
--spatialiter  YES/NO   If yes iterate the spatial estimations at each iterations (defined by niter) on the maps minus the temporal terms (ie. linear, coseismic...) [default: no]
--sampling VALUE        Downsampling factor [default: 1]
--imref VALUE           Reference image number [default: 1]
--mask PATH             Path to mask file in r4 or tif format for the spatial estimations (Keep only values > threshold_mask for ramp estimation).
--rampmask YES/NO       Remove a quadratic ramp in range a linear in azimuth on the mask before computing threshold [default: no]
--threshold_mask VALUE  Threshold on mask: take only > values (use scale factor for convenience) [default: 0]
--scale_mask  VALUE     Scale factor to apply on mask
--tempmask YES/NO       If yes, also use the spatial mask for the temporal inversion [default: no]
--topofile PATH         Path to topographic file in r4 or tif format. If not None, add a phase-elevation relationship in the saptial estimation.
--aspect PATH           Path to aspect file in r4 or tif format: take into account the slope orientation in the phase/topo relationship [default: None].
--perc_los VALUE        Percentile of hidden LOS pixel for the spatial estimations to clean outliers [default:98.]
--perc_topo VALUE       Percentile of topography ranges for the spatial estimations to remove some very low valleys or peaks [default:90.]
--cond VALUE            Condition value for optimization: Singular value smaller than cond are considered zero [default: 1e-3]
--ineq VALUE            If yes, add ineguality constraints in the inversion: use least square result without post-seismic functions as a first guess to iterate the inversion. Force postseismic to be the same sign and inferior than coseismic steps of the first guess [default: no].
--fulloutput YES/NO     If yes produce maps of models, residuals, ramps, as well as flatten cube without seasonal and linear term [default: no]
--geotiff PATH          Path to Geotiff to save outputs in tif format. If None save output are saved as .r4 files [default: .r4]
--plot YES/NO           Display plots [default: yes]
--refstart VALUE        Depricate - Stating line number of the area where phase is set to zero [default: None] 
--refend VALUE          Depricate - Ending line number of the area where phase is set to zero [default: None]
--ref=<lin_start,lin_end,col_start,col_end> Starting and ending lines and col numbers where phase is set to zero - Overwrite refstart/refend [default: None] 
--dateslim              Datemin,Datemax time series  
--crop VALUE            Define a region of interest for the temporal decomposition [default: 0,nlines,0,ncol]
--crop_emp VALUE    Define a region of interest for the spatial estimatiom (ramp+phase/topo) [default: 0,nlines,0,ncol]
--nproc=<nb_cores>    Use <nb_cores> local cores to create delay maps [Default: 4]
"""

print()
print('# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #')
print('#'                                                                 '#')
print('#         Linear Inversion of InSAR time series displacements       #')
print('#         with a decomposition in time                              #')
print('#'                                                                 '#')
print('# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #')
print()

import numpy as np
from numpy.lib.stride_tricks import as_strided
import scipy as sp
import scipy.optimize as opt
import scipy.linalg as lst
import gdal, osr
import math,sys,getopt
from os import path, environ
import os
import matplotlib
if environ["TERM"].startswith("screen"):
    matplotlib.use('Agg')
#matplotlib.use('TkAgg') # Must be before importing matplotlib.pyplot or pylab!
# from pylab import *
import matplotlib.cm as cm
import matplotlib.dates as mdates
from datetime import datetime as datetimes
from pylab import date2num

try:
    from nsbas import docopt
except:
    import docopt

from contextlib import contextmanager
from functools import wraps, partial
import multiprocessing
import logging

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning) 

# logging.basicConfig(level=logging.INFO,\
logging.basicConfig(level=logging.INFO,\
        format='line %(lineno)s -- %(levelname)s -- %(message)s')
logger = logging.getLogger('invers_disp2coef.log')


################################
# Create lib of wavelet functions
################################

class pattern:
    def __init__(self,name,reduction,date):
        self.name=name
        self.reduction=reduction
        self.date=date

    def info(self):
        print(self.name, self.date)

### BASIS FUNCTIONS: function of time

def Heaviside(t):
        h=np.zeros((len(t)))
        h[t>=0]=1.0
        return h

def Box(t):
        return Heaviside(t+0.5)-Heaviside(t-0.5)

class coseismic(pattern):
      def __init__(self,name,reduction,date):
          pattern.__init__(self,name,reduction,date)
          self.to=date

      def g(self,t):
        return Heaviside(t-self.to)

class postseismic(pattern):
      def __init__(self,name,reduction,date,tcar=1):
          pattern.__init__(self,name,reduction,date)
          self.to=date
          self.tcar=tcar

      def g(self,t):
        t=(t-self.to)/self.tcar
        t[t<=0] = 0
        g = np.log10(1+t)
        return g

class reference(pattern):
    def __init__(self,name,reduction,date):
        pattern.__init__(self,name,reduction,date)
    def g(self,t):
        return np.ones((t.size))

class interseismic(pattern):
    def __init__(self,name,reduction,date):
        pattern.__init__(self,name,reduction,date)
        self.to=date

    def g(self,t):
        func=(t-self.to)
        return func

class sin2var(pattern):
     def __init__(self,name,reduction,date):
         pattern.__init__(self,name,reduction,date)
         self.to=date

     def g(self,t):
         func=np.zeros(t.size)
         for i in range(t.size):
             func[i]=math.sin(4*math.pi*(t[i]-self.to))
         return func

class cos2var(pattern):
     def __init__(self,name,reduction,date):
         pattern.__init__(self,name,reduction,date)
         self.to=date

     def g(self,t):
         func=np.zeros(t.size)
         for i in range(t.size):
             func[i]=math.cos(4*math.pi*(t[i]-self.to))
         return func

class sinvar(pattern):
    def __init__(self,name,reduction,date):
        pattern.__init__(self,name,reduction,date)
        self.to=date

    def g(self,t):
        func=np.zeros(t.size)
        for i in range(t.size):
            func[i]=math.sin(2*math.pi*(t[i]-self.to))
        return func

class cosvar(pattern):
    def __init__(self,name,reduction,date):
        pattern.__init__(self,name,reduction,date)
        self.to=date

    def g(self,t):
        func=np.zeros(t.size)
        for i in range(t.size):
            func[i]=math.cos(2*math.pi*(t[i]-self.to))
        return func

class slowslip(pattern):
      def __init__(self,name,reduction,date,tcar=1):
          pattern.__init__(self,name,reduction,date)
          self.to=date
          self.tcar=tcar

      def g(self,t):
          t=(t-self.to)/self.tcar
          funct = 0.5*(np.tanh(t)-1) + 1
          return funct

### KERNEL FUNCTIONS: not function of time
class corrdem(pattern):
    def __init__(self,name,reduction,bp0,bp):
        self.name = name
        self.reduction = reduction
        self.bpo=bp0
        self.bp=bp

    def info(self):
        print(self.name)

    def g(self,index):
        func = (self.bp-self.bpo)
        return func[index]

class vector(pattern):
    def __init__(self,name,reduction,vect):
        self.name = name
        self.reduction = reduction
        self.func=vect

    def info(self):
        print(self.name)

    def g(self,index):
        return self.func[index]

def date2dec(dates):
    dates  = np.atleast_1d(dates)
    times = []
    for date in dates:
        x = datetimes.strptime('{}'.format(date),'%Y%m%d')
        dec = float(x.strftime('%j'))/365.1
        year = float(x.strftime('%Y'))
        times.append(year + dec)
    return times


##################################################################################
###  Extras functions and context maganers
##################################################################################

# Timer for all the functions
class ContextDecorator(object):
    def __call__(self, f):
        @wraps(f)
        def decorated(*args, **kwds):
            with self:
                try:
                    return f(*args, **kwds)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except:
                    Exception('{0} Failed !'.format(f))
                    raise
        return decorated

class TimeIt(ContextDecorator):
    def __enter__(self):
        self.start = datetimes.now()
        logger.info('Starting time process: {0}'.format(self.start))
    def __exit__(self, type, value, traceback):
        logger.info('Time process: {0}s'.format((datetimes.now() - self.start).total_seconds()))


def checkinfile(file):
    if path.exists(file) is False:
        logger.critical("File: {0} not found, Exit !".format(file))
        logger.info("File: {0} not found in {1}, Exit !".format(file,getcwd()))

# create generator for pool
@contextmanager
def poolcontext(*arg, **kargs):
    pool = multiprocessing.Pool(*arg, **kargs)
    yield pool
    pool.terminate()
    pool.join()

################################
# Initialization
################################


# read arguments
arguments = docopt.docopt(__doc__)
if arguments["--lectfile"] ==  None:
    infile = "lect.in"
else:
    infile = arguments["--lectfile"]
if arguments["--list_images"] ==  None:
    listim = "images_retenues"
else:
    listim = arguments["--list_images"]
if arguments["--aps"] ==  None:
    apsf = 'no'
else:
    apsf = arguments["--aps"]
if arguments["--linear"] ==  None:
    inter = 'yes'
else:
    inter = arguments["--linear"]
if arguments["--seasonal"] ==  None:
    seasonal = 'no'
else:
    seasonal = arguments["--seasonal"]
if arguments["--semianual"] ==  None:
    semianual = 'no'
else:
    semianual = arguments["--semianual"]
if arguments["--dem"] ==  None:
    dem = 'no'
else:
    dem = arguments["--dem"]
if arguments["--coseismic"] ==  None:
    cos = []
else:
    cos = list(map(float,arguments["--coseismic"].replace(',',' ').split()))

if arguments["--postseismic"] ==  None:
    pos = []
else:
    pos = list(map(float,arguments["--postseismic"].replace('None','-1').replace(',',' ').split()))

if len(pos)>0 and len(cos) != len(pos):
    raise Exception("coseimic and postseismic lists are not the same size")

if arguments["--slowslip"] == None:
    sse, sse_time, sse_car = [], [], []
else:
    try:
        sse = list(map(float,arguments["--slowslip"].replace(',',' ').split()))
        sse_time = sse[::2]
        sse_car = sse[1::2]
    except:
        sse_time, sse_car = [], []

if arguments["--vector"] != None:
    vectf = arguments["--vector"].replace(',',' ').split()
else:
    vectf = []
    vect = None

# read lect.in
ncol, nlines = list(map(int, open(infile).readline().split(None, 2)[0:2]))

if arguments["--refstart"] == None:
    lin_start = None
else:
    lin_start = int(arguments["--refstart"])
if arguments["--refend"] == None:
    lin_end = None
else:
    lin_end = int(arguments["--refend"])

if arguments["--ref"] == None:
    lin_start, lin_jend, col_start, col_end = None,None,None,None
else:
    ref = list(map(int,arguments["--ref"].replace(',',' ').split()))
    try:
        lin_start,lin_end, col_start, col_end = ref[0], ref[1], ref[2], ref[3]
    except:
        lin_start,lin_end = ref[0], ref[1]
        col_start, col_end = 0, ncol

if arguments["--niter"] ==  None:
    niter = 1
else:
    niter = int(arguments["--niter"])
if arguments["--spatialiter"] ==  None:
    spatialiter = 'no'
else:
    spatialiter = arguments["--spatialiter"]
if arguments["--flat"] == None:
    flat = 0
elif int(arguments["--flat"]) <  10:
    flat = int(arguments["--flat"])
else:
    flat = 0
if arguments["--sampling"] ==  None:
    sampling = 1
else:
    sampling = int(arguments["--sampling"])
if arguments["--mask"] ==  None:
    maskfile = None
else:
    maskfile = arguments["--mask"]
if arguments["--rampmask"] ==  None:
    rampmask = 'no'
else:
    rampmask = arguments["--rampmask"]
if arguments["--threshold_mask"] ==  None:
    seuil = 0.
else:
    seuil = float(arguments["--threshold_mask"])
if arguments["--threshold_rms"] ==  None:
    threshold_rms = 1.
else:
    threshold_rms = float(arguments["--threshold_rms"])
if arguments["--tempmask"] ==  None:
    tempmask = 'no'
else:
    tempmask = arguments["--tempmask"]
if arguments["--scale_mask"] ==  None:
    scale = 1
else:
    scale = float(arguments["--scale_mask"])
if arguments["--topofile"] ==  None:
   radar = None
else:
   radar = arguments["--topofile"]

if arguments["--aspect"] ==  None:
   aspect = None
else:
   aspect = arguments["--aspect"]

if arguments["--imref"] ==  None:
    imref = 0
elif arguments["--imref"] < 1:
    logger.warning('--imref must be between 1 and Nimages')
else:
    imref = int(arguments["--imref"]) - 1

if arguments["--cond"] ==  None:
    rcond = 1e-3
else:
    rcond = float(arguments["--cond"])
if arguments["--rmspixel"] ==  None:
    rmsf = None
else:
    rmsf = arguments["--rmspixel"]
if arguments["--ineq"] ==  None:
    ineq = 'no'
else:
    ineq = arguments["--ineq"]

if arguments["--fulloutput"] ==  None:
    fulloutput = 'no'
else:
    fulloutput = arguments["--fulloutput"]

if arguments["--cube"] ==  None:
    cubef = "depl_cumule"
else:
    cubef = arguments["--cube"]

if arguments["--geotiff"] ==  None:
    geotiff = None
else:
    geotiff = arguments["--geotiff"]
    georef = gdal.Open(geotiff)
    gt = georef.GetGeoTransform()
    proj = georef.GetProjection()
    driver = gdal.GetDriverByName('GTiff')

if arguments["--ivar"] == None:
    ivar = 0
elif int(arguments["--ivar"]) <  2:
    ivar = int(arguments["--ivar"])
else:
    logger.warning('Error: ivar > 1, set ivar to 0')
    ivar = 0

if arguments["--nfit"] == None:
    nfit = 0
elif int(arguments["--nfit"]) <  2:
    nfit = int(arguments["--nfit"])
else:
    logger.warning('Error: nfit > 1, set nfit to 0')
    nfit = 0

if arguments["--perc_topo"] ==  None:
    perc_topo = 90.
else:
    perc_topo = float(arguments["--perc_topo"])

if arguments["--perc_los"] ==  None:
    perc_los = 98.
else:
    perc_los = float(arguments["--perc_los"])

if arguments["--nproc"] ==  None:
    nproc = 4
else:
    nproc = int(arguments["--nproc"])

if arguments["--plot"] ==  'yes':
    plot = 'yes'
    logger.warning('plot is yes. Set nproc to 1')
    nproc = 1
    if environ["TERM"].startswith("screen"):
        matplotlib.use('Agg') # Must be before importing matplotlib.pyplot or pylab!
    import matplotlib.pyplot as plt
else:
    plot = 'no'
    matplotlib.use('Agg') # Must be before importing matplotlib.pyplot or pylab!
    import matplotlib.pyplot as plt

if arguments["--crop"] ==  None:
    crop = [0,nlines,0,ncol]
else:
    crop = list(map(float,arguments["--crop"].replace(',',' ').split()))
    logger.warning('Crop time series data between lines {}-{} and cols:{}'.format(int(crop[0]),int(crop[1]),int(crop[2]),int(crop[3])))
ibeg,iend,jbeg,jend = int(crop[0]),int(crop[1]),int(crop[2]),int(crop[3])

if arguments["--crop_emp"] ==  None:
    crop_emp = [0,iend-ibeg,0,jend-jbeg]
else:
    crop_emp = list(map(float,arguments["--crop_emp"].replace(',',' ').split()))
    logger.warning('Crop empirical estimation between lines {}-{} and cols:{}'.format(int(crop_emp[0]),int(crop_emp[1]),int(crop_emp[2]),int(crop_emp[3])))
ibeg_emp,iend_emp,jbeg_emp,jend_emp = int(crop_emp[0]),int(crop_emp[1]),int(crop_emp[2]),int(crop_emp[3])

#####################################################################################
# INITIALISATION
#####################################################################################

# cm
cmap = cm.jet
cmap.set_bad('white')

# load images_retenues file
checkinfile(listim)
nb,idates,dates,base=np.loadtxt(listim, comments='#', usecols=(0,1,3,5), unpack=True,dtype='i,i,f,f')
N = len(dates)
baseref = base[imref]

if arguments["--dateslim"] is not  None:
    dmin,dmax = arguments["--dateslim"].replace(',',' ').split()
    datemin = date2dec(dmin)
    datemax = date2dec(dmax)
else:
    datemin, datemax = np.int(np.min(dates)), np.int(np.max(dates))+1
    dmax = str(datemax) + '0101'
    dmin = str(datemin) + '0101'

# clean dates
indexd = np.flatnonzero(np.logical_and(dates<datemax,dates>datemin))
nb,idates,dates,base = nb[indexd],idates[indexd],dates[indexd],base[indexd]

# lect cube
checkinfile(cubef)
cubei = np.fromfile(cubef,dtype=np.float32)
# extract
cube = as_strided(cubei[:nlines*ncol*N])
logger.info('Load time series cube: {0}, with length: {1}'.format(cubef, len(cube)))
kk = np.flatnonzero(cube>9990)
cube[kk] = float('NaN')
maps_temp = cube.reshape((nlines,ncol,N))
# set at NaN zero values for all dates
# kk = np.nonzero(maps_temp[:,:,-1]==0)
cst = np.copy(maps_temp[:,:,imref])
for l in range((N)):
    maps_temp[:,:,l] = maps_temp[:,:,l] - cst
    if l != imref:
        index = np.nonzero(maps_temp[:,:,l]==0.0)
        maps_temp[:,:,l][index] = np.float('NaN')

N=len(dates)
maps = np.copy(maps_temp[ibeg:iend,jbeg:jend,indexd])
logger.info('Number images between {0} and {1}: {2}'.format(dmin,dmax,N))
logger.info('Reshape cube: {}'.format(maps.shape))

# clean
del cube, cubei, maps_temp

# fig = plt.figure(0)
# plt.imshow(cst,vmax=1,vmin=-1)
# fig = plt.figure(1)
# plt.imshow(maps[ibeg:iend,jbeg:jend,imref],vmax=1,vmin=-1)
# plt.show()
# sys.exit()

fig = plt.figure(12)
nfigure=0

# open mask file
if maskfile is not None:
    extension = os.path.splitext(maskfile)[1]
    checkinfile(maskfile)
    if extension == ".tif":
      ds = gdal.Open(maskfile, gdal.GA_ReadOnly)
      band = ds.GetRasterBand(1)
      maski = band.ReadAsArray().flatten()*scale
      del ds
    else:
      fid = open(maskfile,'r')
      maski = np.fromfile(fid,dtype=np.float32)*scale
      fid.close()
    mask = maski.reshape((nlines,ncol))[ibeg:iend,jbeg:jend]
    maski = mask.flatten()
else:
    mask_flat = np.ones((iend-ibeg,jend-jbeg))
    mask = np.ones((iend-ibeg,jend-jbeg))
    maski = mask.flatten()

# open elevation map
if radar is not None:
    extension = os.path.splitext(radar)[1]
    checkinfile(radar)
    if extension == ".tif":
      ds = gdal.Open(radar, gdal.GA_ReadOnly)
      band = ds.GetRasterBand(1)
      elevi = band.ReadAsArray().flatten()
      del ds
    else:
      fid = open(radar,'r')
      elevi = np.fromfile(fid,dtype=np.float32)
      fid.close()

    elevi = elevi[:nlines*ncols]
    # fig = plt.figure(10)
    # plt.imshow(elevi.reshape(iend-ibeg,jend-jbeg)[ibeg:iend,jbeg:jend])
    elev = elevi.reshape((nlines,ncol))[ibeg:iend,jbeg:jend]
    elev[np.isnan(maps[:,:,-1])] = float('NaN')
    kk = np.nonzero(abs(elev)>9999.)
    elev[kk] = float('NaN')
    elevi = elev.flatten()
    # fig = plt.figure(11)
    # plt.imshow(elev[ibeg:iend,jbeg:jend])
    # plt.show()
    # sys.exit()
else:
   elev = np.ones((iend-ibeg,jend-jbeg))
   elevi = elev.flatten()

if aspect is not None:
    extension = os.path.splitext(aspect)[1]
    checkinfile(aspect)
    if extension == ".tif":
      ds = gdal.Open(aspect, gdal.GA_ReadOnly)
      band = ds.GetRasterBand(1)
      aspecti = band.ReadAsArray().flatten()
      del ds
    else:
      fid = open(aspect,'r')
      aspecti = np.fromfile(fid,dtype=np.float32)
      fid.close()
    aspecti = aspecti[:nlines*ncols]
    slope = aspecti.reshape((nlines,ncol))[ibeg:iend,jbeg:jend]
    slope[np.isnan(maps[:,:,-1])] = float('NaN')
    kk = np.nonzero(abs(slope>9999.))
    slope[kk] = float('NaN')
    aspecti = slope.flatten()
    # print slope[slope<0]
    # fig = plt.figure(11)
    # plt.imshow(elev[ibeg:iend,jbeg:jend])
    # plt.show()
    # sys.exit()
else:
    slope = np.ones((iend-ibeg,jend-jbeg))
    aspecti = slope.flatten()

if rmsf is not None:
    checkinfile(rmsf)
    rmsmap = np.fromfile(rmsf,dtype=np.float32).reshape((nlines,ncol))[ibeg:iend,jbeg:jend]
    kk = np.nonzero(np.logical_or(rmsmap==0.0, rmsmap>999.))
    rmsmap[kk] = float('NaN')
    kk = np.nonzero(rmsmap>threshold_rms)
    spacial_mask = np.copy(rmsmap)
    spacial_mask[kk] = float('NaN')
    fig = plt.figure(nfigure,figsize=(9,4))
    nfigure = nfigure + 1
    ax = fig.add_subplot(1,1,1)
    cax = ax.imshow(spacial_mask,cmap=cmap)
    ax.set_title('Mask on spatial estimation based on RMSpixel')
    plt.setp( ax.get_xticklabels(), visible=False)
    fig.colorbar(cax, orientation='vertical',aspect=10)
    del spacial_mask
    # if plot=='yes':
    #    plt.show()
else:
    rmsmap = np.ones((iend-ibeg,jend-jbeg))
    spacial_mask = np.ones((iend-ibeg,jend-jbeg))
    threshold_rms = 2.

# plot bperp vs time
fig = plt.figure(nfigure,figsize=(10,4))
nfigure = nfigure + 1
ax = fig.add_subplot(1,2,1)
# convert idates to num
x = [date2num(datetimes.strptime('{}'.format(d),'%Y%m%d')) for d in idates]
# format the ticks
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y/%m/%d"))
ax.plot(x,base,"ro",label='Baseline history of the {} images'.format(N))
ax.plot(x,base,"green")
# rotates and right aligns the x labels, and moves the bottom of the
# axes up to make room for them
fig.autofmt_xdate()
ax.set_xlabel('Time (Year/month/day)')
ax.set_ylabel('Perpendicular Baseline')
plt.legend(loc='best')

ax = fig.add_subplot(1,2,2)
ax.plot(np.mod(dates,1),base,"ro",label='Baseline seasonality of the {} images'.format(N))
plt.legend(loc='best')

fig.savefig('baseline.eps', format='EPS',dpi=150)
np.savetxt('bp_t.in', np.vstack([dates,base]).T, fmt='%.6f')

if maskfile is not None:
    los_temp = as_strided(mask[ibeg_emp:iend_emp,jbeg_emp:jend_emp]).flatten()

    if rampmask=='yes':
        logger.info('Flatten mask...')
        temp = [(i,j) for i in range(iend_emp-ibeg_emp) for j in range(jend_emp-jbeg_emp) \
        if np.logical_and((math.isnan(los_temp[i*(jend_emp-jbeg_emp)+j]) is False), \
            (los_temp[i*(jend_emp-jbeg_emp)+j]>seuil))]

        temp2 = np.array(temp)
        x = temp2[:,0]; y = temp2[:,1]
        los_clean = los_temp[x*(jend-jbeg)+y]
        G=np.zeros((len(los_clean),4))
        G[:,0], G[:,1], G[:,2], G[:,3] = y**2, y, x, 1
        # ramp inversion
        pars = np.dot(np.dot(np.linalg.inv(np.dot(G.T,G)),G.T),los_clean)
        a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]
        logger.info('Remove ramp mask %f x**2 %f x  + %f y + %f for : %s'%(a,b,c,d,maskfile))

        # remove 0 values
        kk = np.flatnonzero(np.logical_or(maski==0, maski==9999))
        #kk = np.flatnonzero(los==9999)
        maski[kk] = float('NaN')

        G=np.zeros((len(maski),4))
        for i in range(nlines):
            G[i*ncol:(i+1)*ncol,0] = (np.arange((ncol)) - jbeg_emp)**2
            G[i*ncol:(i+1)*ncol,1] = np.arange((ncol)) - jbeg_emp
            G[i*ncol:(i+1)*ncol,2] = i - ibeg_emp
        G[:,3] = 1
        mask_flat = (maski - np.dot(G,pars)).reshape(iend-ibeg,jend-jbeg)
        mask_flat = mask_flat - np.nanmean(mask_flat)

    else:

        # remove 0 values
        kk = np.flatnonzero(np.logical_or(np.logical_or(maski==0, maski==9999),np.isnan(los_temp)))
        #kk = np.flatnonzero(los==9999)
        maski[kk] = float('NaN')
        mask_flat = maski.reshape(iend-ibeg,jend-jbeg)

    del maski

    # check seuil
    kk = np.flatnonzero(mask_flat<seuil)
    mask_flat_clean=np.copy(mask_flat.flatten())
    mask_flat_clean[kk]=float('NaN')
    mask_flat_clean = mask_flat_clean.reshape(iend-ibeg,jend-jbeg)

    # mask maps if necessary for temporal inversion
    if tempmask=='yes':
        kk = np.nonzero(mask_flat[ibeg_emp:iend_emp,jbeg_emp:jend_emp]<seuil)
        for l in range((N)):
            # clean only selected area
            d = as_strided(maps[ibeg_emp:iend_emp,jbeg_emp:jend_emp,l])
            d[kk] = np.float('NaN')

    # plots
    nfigure+=1
    fig = plt.figure(nfigure,figsize=(7,6))
    vmax = np.abs([np.nanmedian(mask_flat) + np.nanstd(mask_flat),\
        np.nanmedian(mask_flat) - np.nanstd(mask_flat)]).max()
    vmin = -vmax

    ax = fig.add_subplot(1,3,1)
    cax = ax.imshow(mask,cmap=cmap,vmax=vmax,vmin=vmin)
    ax.set_title('Original Mask')
    plt.setp( ax.get_xticklabels(), visible=False)

    ax = fig.add_subplot(1,3,2)
    cax = ax.imshow(mask_flat,cmap=cmap,vmax=vmax,vmin=vmin)
    ax.set_title('Flat Mask')
    plt.setp( ax.get_xticklabels(), visible=False)
    #cbar = fig.colorbar(cax, orientation='vertical',aspect=10)

    ax = fig.add_subplot(1,3,3)
    cax = ax.imshow(mask_flat_clean,cmap=cmap,vmax=vmax,vmin=vmin)
    ax.set_title('Final Mask')
    plt.setp( ax.get_xticklabels(), visible=False)
    #cbar = fig.colorbar(cax, orientation='vertical',aspect=10)
    fig.savefig('mask.eps', format='EPS',dpi=150)
    del mask_flat_clean

    if plot=='yes':
        plt.show()
    # sys.exit()

# plot diplacements maps
nfigure+=1
fig = plt.figure(nfigure,figsize=(14,10))
fig.subplots_adjust(wspace=0.001)
vmax = np.nanpercentile(maps[:,:,-1],99.8)
vmin = np.nanpercentile(maps[:,:,-1],.2)
# vmax = np.abs([np.nanmedian(maps[:,:,-1]) + 1.*np.nanstd(maps[:,:,-1]),\
#     np.nanmedian(maps[:,:,-1]) - 1.*np.nanstd(maps[:,:,-1])]).max()
# vmin = -vmax

for l in range((N)):
    d = as_strided(maps[:,:,l])
    #ax = fig.add_subplot(1,N,l+1)
    ax = fig.add_subplot(4,int(N/4)+1,l+1)
    #cax = ax.imshow(d,cmap=cmap,vmax=vmax,vmin=vmin)ftem
    cax = ax.imshow(d,cmap=cmap,vmax=vmax,vmin=vmin)
    ax.set_title(idates[l],fontsize=6)
    plt.setp( ax.get_xticklabels(), visible=False)
    plt.setp( ax.get_yticklabels(), visible=False)

plt.suptitle('Time series maps')
fig.colorbar(cax, orientation='vertical',aspect=10)
fig.tight_layout()
fig.savefig('maps.eps', format='EPS',dpi=150)

# plt.show()
#sys.exit()

#######################################################
# Save new lect.in file
#######################################################

fid = open('lect_ts.in','w')
np.savetxt(fid, (jend-jbeg,iend-ibeg),fmt='%6i',newline='\t')
fid.close()

#######################################################
# Create functions of decomposition
######################################################

basis=[
    reference(name='reference',date=datemin,reduction='ref'),
    ]
index = len(basis)

# initialise iteration with interseismic alone
iteration=False

if inter=='yes':
    indexinter=index
    basis.append(interseismic(name='interseismic',reduction='lin',date=datemin))
    index = index + 1

if seasonal=='yes':
    indexseas = index
    basis.append(cosvar(name='seas. var (cos)',reduction='coswt',date=datemin))
    basis.append(sinvar(name='seas. var (sin)',reduction='sinwt',date=datemin))
    index = index + 2

if semianual=='yes':
     indexsemi = index
     basis.append(cos2var(name='semi-anual var (cos)',reduction='cosw2t',date=datemin))
     basis.append(sin2var(name='semi-anual var (sin)',reduction='sinw2t',date=datemin))
     index = index + 2

indexco = np.zeros(len(cos))
for i in range(len(cos)):
    basis.append(coseismic(name='coseismic {}'.format(i),reduction='cos{}'.format(i),date=cos[i])),
    indexco[i] = index
    index = index + 1
    iteration=True


indexpo,indexpofull = [],[]
for i in range(len(pos)):
  if pos[i] > 0. :
    basis.append(postseismic(name='postseismic {}'.format(i),reduction='post{}'.format(i),date=cos[i],tcar=pos[i])),
    indexpo.append(int(index))
    indexpofull.append(int(index))
    index = index + 1
  else:
    indexpofull.append(0)
indexpo = np.array(indexpo)
indexpofull = np.array(indexpofull)


indexsse = np.zeros(len(sse_time))
for i in range(len(sse_time)):
    basis.append(slowslip(name='sse {}'.format(i),reduction='sse{}'.format(i),date=sse_time[i],tcar=sse_car[i])),
    indexsse[i] = int(index)
    index = index + 1
    iteration=True

kernels=[]

if dem=='yes':
   kernels.append(corrdem(name='dem correction',reduction='corrdem',bp0=baseref,bp=base))
   indexdem = index
   index = index + 1

if arguments["--vector"] != None:
    fig = plt.figure(nfigure,figsize=(6,4))
    nfigure = nfigure + 1
    indexvect = np.zeros(len(vectf))
    for i in range(len(vectf)):
      ax = fig.add_subplot(i+1,1,len(vectf))
      v = np.loadtxt(vectf[i], comments='#', unpack = False, dtype='f')
      kernels.append(vector(name=vectf[i],reduction='vector_{}'.format(i),vect=v))
      ax.plot(v,label='Vector')
      plt.legend(loc='best')
      indexvect[i] = index
      index = index + 1    
    indexvect = indexvect.astype(int)
    if plot=='yes':
      plt.show()
    # sys.exit()

indexpo = indexpo.astype(int)
indexco = indexco.astype(int)
indexsse = indexsse.astype(int)

print()
Mbasis=len(basis)
logger.info('Number of basis functions: {}'.format(Mbasis))
Mker=len(kernels)
logger.info('Number of kernel functions: {}'.format(Mker))
M = Mbasis + Mker

print('Basis functions, Time:')
for i in range((Mbasis)):
    basis[i].info()
if Mker > 1:
  print('Kernels functions, Time:')
for i in range((Mker)):
    kernels[i].info()

# initialize matrix model to NaN
for l in range((Mbasis)):
    basis[l].m = np.ones((iend-ibeg,jend-jbeg))*np.float('NaN')
    basis[l].sigmam = np.ones((iend-ibeg,jend-jbeg))*np.float('NaN')
for l in range((Mker)):
    kernels[l].m = np.ones((iend-ibeg,jend-jbeg))*np.float('NaN')
    kernels[l].sigmam = np.ones((iend-ibeg,jend-jbeg))*np.float('NaN')

# initialize qual
if apsf=='no':
    inaps=np.ones((N)) # no weigthing for the first itertion
else:
    fimages=apsf
    inaps=np.loadtxt(fimages, comments='#', dtype='f')
    logger.info('Input uncertainties: {}'.format(inaps))
    logger.info('Scale input uncertainties between 0 and 1 and set very low values to the 2 \
      percentile to avoid overweighting...')
    # maxinaps = np.nanmax(inaps)
    # inaps= inaps/maxinaps
    minaps= np.nanpercentile(inaps,2)
    index = np.flatnonzero(inaps<minaps)
    inaps[index] = minaps
    logger.info('Output uncertainties for first iteration: {}'.format(inaps))
    print

# SVD inversion with cut-off eigenvalues
def invSVD(A,b,cond):
    try:
        U,eignv,V = lst.svd(A, full_matrices=False)
        s = np.diag(eignv)
        index = np.nonzero(s<cond)
        inv = lst.inv(s)
        inv[index] = 0.
        fsoln = np.dot( V.T, np.dot( inv , np.dot(U.T, b) ))
    except:
        fsoln = lst.lstsq(A,b)[0]
        #fsoln = lst.lstsq(A,b,rcond=cond)[0]
    
    return fsoln

## inversion procedure 
def consInvert(A,b,sigmad,ineq='no',cond=1.0e-3, iter=2000,acc=1e-12):
    '''Solves the constrained inversion problem.

    Minimize:
    
    ||Ax-b||^2

    Subject to:
    mmin < m < mmax
    '''

    if A.shape[0] != len(b):
        raise ValueError('Incompatible dimensions for A and b')

    if ineq == 'no':
        
        fsoln = invSVD(A,b,cond)
        
    else:

        # prior solution without postseismic 
        Ain = np.delete(A,indexpo,1)
        mtemp = invSVD(Ain,b,cond)
       
        # rebuild full vector
        for z in range(len(indexpo)):
            mtemp = np.insert(mtemp,indexpo[z],0)
        minit = np.copy(mtemp)

        # # initialize bounds
        mmin,mmax = -np.ones(M)*np.inf, np.ones(M)*np.inf 

        # We here define bounds for postseismic to be the same sign than coseismic
        # and coseismic inferior or egual to the coseimic initial 
        for i in range(len(indexco)):
            if (pos[i] > 0.) and (minit[int(indexco[i])]>0.):
                mmin[int(indexpofull[i])], mmax[int(indexpofull[i])] = 0, np.inf 
                mmin[int(indexco[i])], mmax[int(indexco[i])] = 0, minit[int(indexco[i])] 
            if (pos[i] > 0.) and (minit[int(indexco[i])]<0.):
                mmin[int(indexpofull[i])], mmax[int(indexpofull[i])] = -np.inf , 0
                mmin[int(indexco[i])], mmax[int(indexco[i])] = minit[int(indexco[i])], 0
        
        ####Objective function and derivative
        _func = lambda x: np.sum(((np.dot(A,x)-b)/sigmad)**2)
        _fprime = lambda x: 2*np.dot(A.T/sigmad, (np.dot(A,x)-b)/sigmad)
        
        bounds=zip(mmin,mmax)
        res = opt.fmin_slsqp(_func,minit,bounds=bounds,fprime=_fprime, \
            iter=iter,full_output=True,iprint=0,acc=acc)  
        fsoln = res[0]
  
    # tarantola:
    # Cm = (Gt.Cov.G)-1 --> si sigma=1 problems
    # sigma m **2 =  misfit**2 * diag([G.TG]-1)
    try:
       varx = np.linalg.inv(np.dot(A.T,A))
       res2 = np.sum(pow((b-np.dot(A,fsoln)),2))
       scale = 1./(A.shape[0]-A.shape[1])
       # scale = 1./A.shape[0]
       sigmam = np.sqrt(scale*res2*np.diag(varx))
    except:
       sigmam = np.ones((A.shape[1]))*float('NaN')

    return fsoln,sigmam

def estim_ramp(los,los_clean,topo_clean,x,y,order,rms,nfit,ivar,l):

      # initialize topo
      topo = np.zeros((iend-ibeg,jend-jbeg))
      ramp = np.zeros((iend-ibeg,jend-jbeg))      
      data = np.copy(los_clean)

      # y: range, x: azimuth
      if radar is None:
          topobins = topo_clean
          rgbins, azbins = y, x

      else:
          # lets try to digitize to improve the fit
          # digitize data in bins, compute median and std
          bins = np.arange(mintopo,maxtopo,abs(maxtopo-mintopo)/500.)
          inds = np.digitize(topo_clean,bins)
          topobins = []
          losbins = []
          losstd = []
          azbins, rgbins = [], []
          for j in range(len(bins)-1):
                  uu = np.flatnonzero(inds == j)
                  if len(uu)>100:
                      topobins.append(bins[j] + (bins[j+1] - bins[j])/2.)

                      # do a small clean within the bin
                      indice = np.flatnonzero(np.logical_and(los_clean[uu]>np.percentile(\
                          los_clean[uu],2.),los_clean[uu]<np.percentile(los_clean[uu],98.)))

                      losstd.append(np.std(los_clean[uu][indice]))
                      losbins.append(np.median(los_clean[uu][indice]))
                      azbins.append(np.median(x[uu][indice]))
                      rgbins.append(np.median(y[uu][indice]))

          data = np.array(losbins)
          rms = np.array(losstd)
          topobins = np.array(topobins)
          rgbins, azbins = np.array(rgbins),np.array(azbins)
    
      if order==0:

        if radar is None:

            a = 0.
            ramp = np.zeros((iend-ibeg,jend-jbeg))
            rms = np.sqrt(np.nanmean((los)**2))
            logger.info('RMS dates %i: %f'%(idates[l], rms))

        else:

            if (ivar==0 and nfit==0):
                G=np.zeros((len(data),2))
                G[:,0] = 1
                G[:,1] = topobins

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]
                logger.info('Remove ref frame %f + %f z for date: %i'%(a,b,idates[l]))

                # plot phase/elev
                funct = a
                funcbins = a
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,b*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),2))
                G[:,0] = 1
                G[:,1] = elevi

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                topo = np.dot(G,pars).reshape(iend-ibeg,jend-jbeg)


            elif (ivar==0 and nfit==1):
                G=np.zeros((len(data),3))
                G[:,0] = 1
                G[:,1] = topobins
                G[:,2] = topobins**2

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c=pars[2]
                print ('Remove ref frame %f + %f z + %f z**2 for date: %i'%(a,b,c,idates[l]))

                # plot phase/elev
                funct = a
                funcbins = a
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,b*x+c*x**2,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),3))
                G[:,0] = 1
                G[:,1] = elevi
                G[:,2] = elevi**2

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                topo = np.dot(G,pars).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==1 and nfit==0):
                G=np.zeros((len(data),3))
                G[:,0] = 1
                G[:,1] = topobins
                G[:,2] = azbins*topobins

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]
                print ('Remove ref frame %f + %f z + %f az*z for date: %i'%(a,b,c,idates[l]))

                # plot phase/elev
                funct = a + c*topo_clean*x
                funcbins = a + c*topobins*azbins
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,b*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),3))
                G[:,0] = 1
                G[:,1] = elevi
                G[:,2] = elevi
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,2] *= (i - ibeg_emp)

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                topo = np.dot(G,pars).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==1 and nfit==1):
                G=np.zeros((len(data),4))
                G[:,0] = 1
                G[:,1] = azbins*topobins
                G[:,2] = topobins
                G[:,3] = topobins**2

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,acc=1.e-9,iprint=0)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]
                print ('Remove ref frame %f + %f az*z + %f z + %f z**2 for date: %i'%(a,b,c,d,idates[l]))

                # plot phase/elev
                funct = a + b*topo_clean*x
                funcbins = a + b*topobins*azbins
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,c*x+d*x**2,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),4))
                G[:,0] = 1
                G[:,1] = elevi
                G[:,2] = elevi
                G[:,3] = elevi**2
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,1] *= (i - ibeg_emp)

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                topo = np.dot(G,pars).reshape(iend-ibeg,jend-jbeg)

      elif order==1: # Remove a range ramp ay+b for each maps (y = col)

        if radar is None:
            G=np.zeros((len(data),2))
            G[:,0] = rgbins
            G[:,1] = 1

            # ramp inversion
            x0 = lst.lstsq(G,data)[0]
            _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
            _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
            pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
            a = pars[0]; b = pars[1]
            print ('Remove ramp %f r + %f for date: %i'%(a,b,idates[l]))

            # build total G matrix
            G=np.zeros((len(los),2))
            for i in range(nlines):
                G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
            G[:,1] = 1

            res = los - np.dot(G,pars)
            rms = np.sqrt(np.nanmean(res**2))
            logger.info('RMS dates %i: %f'%(idates[l], rms))

            ramp = np.dot(G,pars).reshape(iend-ibeg,jend-jbeg)

        else:
            if (ivar==0 and nfit==0):
                G=np.zeros((len(data),3))
                G[:,0] = rgbins
                G[:,1] = 1
                G[:,2] = topobins

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]
                print ('Remove ramp %f r + %f + %f z for date: %i'%(a,b,c,idates[l]))

                # plot phase/elev
                funct = a*y + b
                funcbins = a*rgbins + b
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,c*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),3))
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
                G[:,1] = 1
                G[:,2] = elevi

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-1)],pars[:nparam-1]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-1):],pars[(nparam-1):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==0 and nfit==1):
                G=np.zeros((len(data),4))
                G[:,0] = rgbins
                G[:,1] = 1
                G[:,2] = topobins
                G[:,3] = topobins**2

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d=pars[3]
                print ('Remove ramp %f r + %f + %f z + %f z**2 for date: %i'%(a,b,c,d,idates[l]))

                # plot phase/elev
                funct = a*y+ b
                funcbins = a*rgbins+ b
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,c*x+d*x**2,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),4))
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
                G[:,1] = 1
                G[:,2] = elevi
                G[:,3] = elevi**2

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-2)],pars[:nparam-2]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-2):],pars[(nparam-2):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==1 and nfit==0):
                G=np.zeros((len(data),4))
                G[:,0] = rgbins
                G[:,1] = 1
                G[:,2] = topobins
                G[:,3] = topobins*azbins

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]
                print ('Remove ramp %f r + %f + %f z + %f z*az for date: %i'%(a,b,c,d,idates[l]))

                # plot phase/elev
                funct = a*y+ b + d*topo_clean*x
                funcbins = a*rgbins+ b + d*topobins*azbins
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,c*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),4))
                G[:,1] = 1
                G[:,2] = elevi
                G[:,3] = elevi
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,3] *= (i - ibeg_emp)


                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-2)],pars[:nparam-2]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-2):],pars[(nparam-2):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==1 and nfit==1):
                G=np.zeros((len(data),5))
                G[:,0] = rgbins
                G[:,1] = 1
                G[:,2] = topobins*azbins
                G[:,3] = topobins
                G[:,4] = topobins**2

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]
                print ('Remove ramp %f r + %f +  %f z*az + %f z + %f z**2 for date: %i'%(a,b,c,d,e,idates[l]))

                # plot phase/elev
                funct = a*y+ b + c*topo_clean*x
                funcbins = a*rgbins+ b + c*topobins*azbins
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,d*x+e*x**2,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),5))
                G[:,1] = 1
                G[:,2] = elevi
                G[:,3] = elevi
                G[:,4] = elevi**2
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,2] *= (i - ibeg_emp)

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-3)],pars[:nparam-3]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-3):],pars[(nparam-3):]).reshape(iend-ibeg,jend-jbeg)


      elif order==2: # Remove a azimutal ramp ax+b for each maps (x is lign)
        if radar is None:
            G=np.zeros((len(data),2))
            G[:,0] = azbins
            G[:,1] = 1

            # ramp inversion
            x0 = lst.lstsq(G,data)[0]
            _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
            _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
            pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
            a = pars[0]; b = pars[1]
            print ('Remove ramp %f az + %f for date: %i'%(a,b,idates[l]))

            # build total G matrix
            G=np.zeros((len(los),2))
            for i in range(nlines):
                G[i*ncol:(i+1)*ncol,0] =(i - ibeg_emp)
            G[:,1] = 1


            res = los - np.dot(G,pars)
            rms = np.sqrt(np.nanmean(res**2))
            logger.info('RMS dates %i: %f'%(idates[l], rms))

            ramp = np.dot(G,pars).reshape(iend-ibeg,jend-jbeg)

        else:
            if (ivar==0 and nfit==0):
                G=np.zeros((len(data),3))
                G[:,0] = azbins
                G[:,1] = 1
                G[:,2] = topobins

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]
                print ('Remove ramp %f az + %f + %f z for date: %i'%(a,b,c,idates[l]))

                # plot phase/elev
                funct = a*x + b
                funcbins = a*azbins + b
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,c*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),3))
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] =(i - ibeg_emp)
                G[:,1] = 1
                G[:,2] = elevi


                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-1)],pars[:nparam-1]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-1):],pars[(nparam-1):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==0 and nfit==1):
                G=np.zeros((len(data),4))
                G[:,0] = azbins
                G[:,1] = 1
                G[:,2] = topobins
                G[:,3] = topobins**2

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]
                print ('Remove ramp %f az + %f + %f z + %f z**2 for date: %i'%(a,b,c,d,idates[l]))

                # plot phase/elev
                funct = a*x + b
                funcbins = a*azbins + b
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,c*x + d*x**2,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),4))
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] =(i - ibeg_emp)
                G[:,1] = 1
                G[:,2] = elevi
                G[:,3] = elevi**2

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-2)],pars[:nparam-2]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-2):],pars[(nparam-2):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==1 and nfit==0):
                G=np.zeros((len(data),4))
                G[:,0] = azbins
                G[:,1] = 1
                G[:,2] = topobins
                G[:,3] = topobins*azbins

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]
                print ('Remove ramp %f az + %f + %f z + %f z*az for date: %i'%(a,b,c,d,idates[l]))

                # plot phase/elev
                funct = a*x + b + d*topo_clean*x
                funcbins = a*azbins + b + d*topobins*azbins
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,c*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),4))
                G[:,1] = 1
                G[:,2] = elevi
                G[:,3] = elevi
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = i - ibeg_emp
                    G[i*ncol:(i+1)*ncol,3] *= (i - ibeg_emp)


                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-2)],pars[:nparam-2]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-2):],pars[(nparam-2):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==1 and nfit==1):
                G=np.zeros((len(data),5))
                G[:,0] = azbins
                G[:,1] = 1
                G[:,2] = topobins*azbins
                G[:,3] = topobins
                G[:,4] = topobins**2

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]
                print ('Remove ramp %f az + %f + %f z*az + %f z + %f z**2 for date: %i'%(a,b,c,d,e,idates[l]))

                # plot phase/elev
                funct = a*x + b + c*topo_clean*x
                funcbins = a*azbins + b + c*topobins*azbins
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,d*x+e*x**2,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),5))
                G[:,1] = 1
                G[:,2] = elevi
                G[:,3] = elevi
                G[:,4] = elevi**2
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = i - ibeg_emp
                    G[i*ncol:(i+1)*ncol,2] *= (i - ibeg_emp)

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-3)],pars[:nparam-3]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-3):],pars[(nparam-3):]).reshape(iend-ibeg,jend-jbeg)

      elif order==3: # Remove a ramp ay+bx+c for each maps
        if radar is None:
            G=np.zeros((len(data),3))
            G[:,0] = rgbins
            G[:,1] = azbins
            G[:,2] = 1

            # ramp inversion
            x0 = lst.lstsq(G,data)[0]
            # print x0
            # x0 = np.zeros((3))
            _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
            _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
            pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
            a = pars[0]; b = pars[1]; c = pars[2]
            print ('Remove ramp %f r  + %f az + %f for date: %i'%(a,b,c,idates[l]))

            # build total G matrix
            G=np.zeros((len(los),3))
            for i in range(nlines):
                G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
                G[i*ncol:(i+1)*ncol,1] = (i - ibeg_emp)
            G[:,2] = 1

            res = los - np.dot(G,pars)
            rms = np.sqrt(np.nanmean(res**2))
            logger.info('RMS dates %i: %f'%(idates[l], rms))

            ramp = np.dot(G,pars).reshape(iend-ibeg,jend-jbeg)

        else:
            if (ivar==0 and nfit==0):
                G=np.zeros((len(data),4))
                G[:,0] = rgbins
                G[:,1] = azbins
                G[:,2] = 1
                G[:,3] = topobins

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]
                print ('Remove ramp %f r  + %f az + %f + %f z for date: %i'%(a,b,c,d,idates[l]))

                # plot phase/elev
                funct = a*y+ b*x + c
                funcbins = a*rgbins+ b*azbins + c
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,d*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),4))
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,1] =(i - ibeg_emp)
                G[:,2] = 1
                G[:,3] = elevi


                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-1)],pars[:nparam-1]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-1):],pars[(nparam-1):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==0 and nfit==1):
                G=np.zeros((len(data),5))
                G[:-1,0] = rgbins
                G[:-1,1] = azbins
                G[:,2] = 1
                G[:-1,3] = topobins
                G[:-1,4] = topobins**2

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]

                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]
                print ('Remove ramp %f r  + %f az + %f + %f z + %f z**2 for date: %i'%(a,b,c,d,e,idates[l]))

                # plot phase/elev
                funct = a*y+ b*x + c
                funcbins = a*rgbins+ b*azbins + c
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,d*x+e*x**2,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),5))
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,1] =(i - ibeg_emp)
                G[:,2] = 1
                G[:,3] = elevi
                G[:,4] = elevi**2

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-2)],pars[:nparam-2]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-2):],pars[(nparam-2):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==1 and nfit==0):
                G=np.zeros((len(data),5))
                G[:,0] = rgbins
                G[:,1] = azbins
                G[:,2] = 1
                G[:,3] = topobins
                G[:,4] = topobins*azbins

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                # print x0
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                # print pars - x0
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e=pars[4]
                print ('Remove ramp %f r  + %f az + %f + %f z +  %f z*az for date: %i'%(a,b,c,d,e,idates[l]))

                # plot phase/elev
                funct = a*y+ b*x + c + e*topo_clean*x
                funcbins = a*rgbins+ b*azbins + c + e*topobins*azbins
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,d*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),5))
                G[:,2] = 1
                G[:,3] = elevi
                G[:,4] = elevi
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,1] =(i - ibeg_emp)
                    G[i*ncol:(i+1)*ncol,4] *= (i - ibeg_emp)


                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-2)],pars[:nparam-2]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-2):],pars[(nparam-2):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==1 and nfit==1):
                G=np.zeros((len(data),6))
                G[:,0] = rgbins
                G[:,1] = azbins
                G[:,2] = 1
                G[:,3] = topobins*azbins
                G[:,4] = topobins
                G[:,5] = topobins**2

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e=pars[4]; f=pars[5]
                print ('Remove ramp %f r  + %f az + %f +  %f z*az + %f z + %f z**2 for date: %i'%(a,b,c,d,e,f,idates[l]))

                # plot phase/elev
                funct = a*y+ b*x + c + d*topo_clean*x
                funcbins = a*rgbins+ b*azbins + c + d*topobins*azbins
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.1, alpha=0.01, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,e*x+f*x**2,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),6))
                G[:,2] = 1
                G[:,3] = elevi
                G[:,4] = elevi
                G[:,5] = elevi**2
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,1] =(i - ibeg_emp)
                    G[i*ncol:(i+1)*ncol,3] *= (i - ibeg_emp)

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-3)],pars[:nparam-3]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-3):],pars[(nparam-3):]).reshape(iend-ibeg,jend-jbeg)

      elif order==4:
        if radar is None:
            G=np.zeros((len(data),4))
            G[:,0] = rgbins
            G[:,1] = azbins
            G[:,2] = rgbins*azbins
            G[:,3] = 1

            # ramp inversion
            x0 = lst.lstsq(G,data)[0]
            _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
            _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
            pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
            a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]
            print ('Remove ramp %f r %f az  + %f r*az + %f for date: %i'%(a,b,c,d,idates[l]))

            # build total G matrix
            G=np.zeros((len(los),4))
            for i in range(nlines):
                G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
                G[i*ncol:(i+1)*ncol,1] = i - ibeg_emp
                G[i*ncol:(i+1)*ncol,2] = (i-ibeg_emp) * (np.arange((ncol))-jbeg_emp)
            G[:,3] = 1

            res = los - np.dot(G,pars)
            rms = np.sqrt(np.nanmean(res**2))
            logger.info('RMS dates %i: %f'%(idates[l], rms))

            ramp = np.dot(G,pars).reshape(iend-ibeg,jend-jbeg)

        else:
            if (ivar==0 and nfit==0):
                G=np.zeros((len(data),5))
                G[:,0] = rgbins
                G[:,1] = azbins
                G[:,2] = rgbins*azbins
                G[:,3] = 1
                G[:,4] = topobins

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]

                print ('Remove ramp %f r, %f az  + %f r*az + %f + %f z for date: %i'%(a,b,c,d,e,idates[l]))

                # plot phase/elev
                funct = a*y+ b*x + c*x*y+ d
                funcbins = a*rgbins+ b*azbins + c*azbins*rgbins+ d
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,e*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),5))
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,1] = i - ibeg_emp
                    G[i*ncol:(i+1)*ncol,2] = (i-ibeg_emp) * (np.arange((ncol))-jbeg_emp)
                G[:,3] = 1
                G[:,4] = elevi


                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-1)],pars[:nparam-1]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-1):],pars[(nparam-1):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==0 and nfit==1):
                G=np.zeros((len(data),6))
                G[:,0] = rgbins
                G[:,1] = azbins
                G[:,2] = rgbins*azbins
                G[:,3] = 1
                G[:,4] = topobins
                G[:,5] = topobins**2

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]

                print ('Remove ramp %f r, %f az  + %f r*az + %f + %f z + %f z**2 for date: %i'%(a,b,c,d,e,f,idates[l]))

                # plot phase/elev
                funct = a*y+ b*x + c*x*y+ d
                funcbins = a*rgbins+ b*azbins + c*azbins*rgbins+ d
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,e*x+f*x**2,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),5))
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,1] = i - ibeg_emp
                    G[i*ncol:(i+1)*ncol,2] = (i-ibeg_emp) * (np.arange((ncol))-jbeg_emp)
                G[:,3] = 1
                G[:,4] = elevi
                G[:,5] = elevi**2

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-2)],pars[:nparam-2]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-2):],pars[(nparam-2):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==1 and nfit==0):
                G=np.zeros((len(data),6))
                G[:,0] = rgbins
                G[:,1] = azbins
                G[:,2] = rgbins*azbins
                G[:,3] = 1
                G[:,4] = topobins
                G[:,5] = topobins*azbins

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]

                print ('Remove ramp %f r, %f az  + %f r*az + %f + %f z + %f az*z for date: %i'%(a,b,c,d,e,f,idates[l]))

                # plot phase/elev
                funct = a*y+ b*x + c*x*y+ d + f*topo_clean*x
                funcbins = a*rgbins+ b*azbins + c*azbins*rgbins+ d + f*topobins*azbins
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,e*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),6))
                G[:,3] = 1
                G[:,4] = elevi
                G[:,5] = elevi
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,1] = i - ibeg_emp
                    G[i*ncol:(i+1)*ncol,2] = (i-ibeg_emp) * (np.arange((ncol))-jbeg_emp)
                    G[i*ncol:(i+1)*ncol,5] *=  (i - ibeg_emp)


                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-2)],pars[:nparam-2]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-2):],pars[(nparam-2):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==1 and nfit==1):
                G=np.zeros((len(data),6))
                G[:,0] = rgbins
                G[:,1] = azbins
                G[:,2] = rgbins*azbins
                G[:,3] = 1
                G[:,4] = topobins*azbins
                G[:,5] = topobins
                G[:,6] = topobins**2

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]; g = pars[6]

                print ('Remove ramp %f r, %f az  + %f r*az + %f + + %f az*z +  %f z + %f z**2  for date: %i'%(a,b,c,d,e,f,g,idates[l]))

                # plot phase/elev
                funct = a*y+ b*x + c*x*y+ d + e*topo_clean*x
                funcbins = a*rgbins+ b*azbins + c*azbins*rgbins+ d + e*topobins*azbins
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,f*x+g*x**2,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),7))
                G[:,3] = 1
                G[:,4] = elevi
                G[:,5] = elevi
                G[:,6] = elevi**2
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,1] = i - ibeg_emp
                    G[i*ncol:(i+1)*ncol,2] = (i-ibeg_emp) * (np.arange((ncol))-jbeg_emp)
                    G[i*ncol:(i+1)*ncol,4] *=  (i - ibeg_emp)

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-3)],pars[:nparam-3]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-3):],pars[(nparam-3):]).reshape(iend-ibeg,jend-jbeg)

      elif order==5:

        if radar is None:
            G=np.zeros((len(data),4))
            G[:,0] = rgbins**2
            G[:,1] = rgbins
            G[:,2] = azbins
            G[:,3] = 1

            # ramp inversion
            x0 = lst.lstsq(G,data)[0]
            _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
            _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
            pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
            a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]
            print ('Remove ramp %f r**2 %f r  + %f az + %f for date: %i'%(a,b,c,d,idates[l]))

            # build total G matrix
            G=np.zeros((len(los),4))
            for i in range(nlines):
                G[i*ncol:(i+1)*ncol,0] = (np.arange((ncol)) - jbeg_emp)**2
                G[i*ncol:(i+1)*ncol,1] = np.arange((ncol)) - jbeg_emp
                G[i*ncol:(i+1)*ncol,2] =(i - ibeg_emp)
            G[:,3] = 1


            res = los - np.dot(G,pars)
            rms = np.sqrt(np.nanmean(res**2))
            logger.info('RMS dates %i: %f'%(idates[l], rms))

            ramp = np.dot(G,pars).reshape(iend-ibeg,jend-jbeg)

        else:

            if (ivar==0 and nfit==0):

                G=np.zeros((len(data),5))
                G[:,0] = rgbins**2
                G[:,1] = rgbins
                G[:,2] = azbins
                G[:,3] = 1
                G[:,4] = topobins

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]
                print ('Remove ramp %f r**2, %f r  + %f az + %f + %f z for date: %i'%(a,b,c,d,e,idates[l]))

                # plot phase/elev
                funct = a*y**2 + b*y+ c*x + d
                funcbins = a*rgbins**2 + b*rgbins+ c*azbins + d
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,e*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),5))
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = (np.arange((ncol)) - jbeg_emp)**2
                    G[i*ncol:(i+1)*ncol,1] = np.arange((ncol)) -  jbeg_emp
                    G[i*ncol:(i+1)*ncol,2] =(i - ibeg_emp)
                G[:,3] = 1
                G[:,4] = elevi


                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-1)],pars[:nparam-1]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-1):],pars[(nparam-1):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==0 and nfit==1):
                G=np.zeros((len(data),6))
                G[:,0] = rgbins**2
                G[:,1] = rgbins
                G[:,2] = azbins
                G[:,3] = 1
                G[:,4] = topobins
                G[:,5] = topobins**2

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]
                print ('Remove ramp %f r**2, %f r  + %f az + %f + %f z + %f z**2 for date: %i'%(a,b,c,d,e,f,idates[l]))

                # plot phase/elev
                funct = a*y**2 + b*y+ c*x + d
                funcbins = a*rgbins**2 + b*rgbins+ c*azbins + d
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,e*x+f*x**2,'-r', lw =4.)


                # build total G matrix
                G=np.zeros((len(los),6))
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = (np.arange((ncol)) - jbeg_emp)**2
                    G[i*ncol:(i+1)*ncol,1] = np.arange((ncol)) -  jbeg_emp
                    G[i*ncol:(i+1)*ncol,2] =(i - ibeg_emp)
                G[:,3] = 1
                G[:,4] = elevi
                G[:,5] = elevi**2

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-2)],pars[:nparam-2]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-2):],pars[(nparam-2):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==1 and nfit==0):

                G=np.zeros((len(data),6))
                G[:,0] = rgbins**2
                G[:,1] = rgbins
                G[:,2] = azbins
                G[:,3] = 1
                G[:,4] = topobins
                G[:,5] = topobins*azbins

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]
                print ('Remove ramp %f r**2, %f r  + %f az + %f + %f z + %f z*az for date: %i'%(a,b,c,d,e,f,idates[l]))

                # plot phase/elev
                funct = a*y**2 + b*y+ c*x + d + f*topo_clean*x
                funcbins = a*rgbins**2 + b*rgbins+ c*azbins + d + f*topobins*azbins
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,e*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),6))
                G[:,3] = 1
                G[:,4] = elevi
                G[:,5] = elevi
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = (np.arange((ncol)) - jbeg_emp)**2
                    G[i*ncol:(i+1)*ncol,1] = np.arange((ncol)) -  jbeg_emp
                    G[i*ncol:(i+1)*ncol,2] =(i - ibeg_emp)
                    G[i*ncol:(i+1)*ncol,5] *= (i - ibeg_emp)

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-2)],pars[:nparam-2]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-2):],pars[(nparam-2):]).reshape(iend-ibeg,jend-jbeg)


            elif (ivar==1 and nfit==1):

                G=np.zeros((len(data),7))
                G[:,0] = rgbins**2
                G[:,1] = rgbins
                G[:,2] = azbins
                G[:,3] = 1
                G[:,4] = topobins*azbins
                G[:,5] = topobins
                G[:,6] = topobins**2

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]; g = pars[6]
                print ('Remove ramp %f r**2, %f r  + %f az + %f + + %f z*az + %f z +%f z**2 for date: %i'%(a,b,c,d,e,f,g,idates[l]))

                # plot phase/elev
                funct = a*y**2 + b*y+ c*x + d + e*topo_clean*x
                funcbins = a*rgbins**2 + b*rgbins+ c*azbins + d + e*topobins*azbins
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,f*x+g*x**2,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),7))
                G[:,3] = 1
                G[:,4] = elevi
                G[:,5] = elevi
                G[:,6] = elevi**2
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = (np.arange((ncol)) - jbeg_emp)**2
                    G[i*ncol:(i+1)*ncol,1] = np.arange((ncol)) -  jbeg_emp
                    G[i*ncol:(i+1)*ncol,2] =(i - ibeg_emp)
                    G[i*ncol:(i+1)*ncol,4] *= (i - ibeg_emp)

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-3)],pars[:nparam-3]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-3):],pars[(nparam-3):]).reshape(iend-ibeg,jend-jbeg)

            else:
                pass

      elif order==6:
        if radar is None:
            G=np.zeros((len(data),4))
            G[:,0] = azbins**2
            G[:,1] = azbins
            G[:,2] = rgbins
            G[:,3] = 1

            # ramp inversion
            x0 = lst.lstsq(G,data)[0]
            _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
            _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
            pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
            a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]
            print ('Remove ramp %f az**2 %f az  + %f r + %f for date: %i'%(a,b,c,d,idates[l]))

            # build total G matrix
            G=np.zeros((len(los),4))
            for i in range(nlines):
                G[i*ncol:(i+1)*ncol,0] = (i - ibeg_emp)**2
                G[i*ncol:(i+1)*ncol,1] = (i - ibeg_emp)
                G[i*ncol:(i+1)*ncol,2] = np.arange((ncol)) - jbeg_emp
            G[:,3] = 1


            res = los - np.dot(G,pars)
            rms = np.sqrt(np.nanmean(res**2))
            logger.info('RMS dates %i: %f'%(idates[l], rms))

            ramp = np.dot(G,pars).reshape(iend-ibeg,jend-jbeg)

        else:
            if (ivar==0 and nfit==0) :
                G=np.zeros((len(data),5))
                G[:,0] = azbins**2
                G[:,1] = azbins
                G[:,2] = rgbins
                G[:,3] = 1
                G[:,4] = topobins

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]
                print ('Remove ramp %f az**2, %f az  + %f r + %f + %f z for date: %i'%(a,b,c,d,e,idates[l]))

                # plot phase/elev
                funct = a*x**2 + b*x + c*y+ d
                funcbins = a*azbins**2 + b*azbins + c*rgbins+ d
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,e*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),5))
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = (i - ibeg_emp)**2
                    G[i*ncol:(i+1)*ncol,1] = i -  ibeg_emp
                    G[i*ncol:(i+1)*ncol,2] = np.arange((ncol)) - jbeg_emp
                G[:,3] = 1
                G[:,4] = elevi


                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-1)],pars[:nparam-1]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-1):],pars[(nparam-1):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==0 and nfit==1):
                G=np.zeros((len(data),6))
                G[:,0] = azbins**2
                G[:,1] = azbins
                G[:,2] = rgbins
                G[:,3] = 1
                G[:,4] = topobins
                G[:,5] = topobins**2

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]
                print ('Remove ramp %f az**2, %f az  + %f r + %f + %f z + %f z**2 for date: %i'%(a,b,c,d,e,f,idates[l]))

                # plot phase/elev
                funct = a*x**2 + b*x + c*y+ d
                funcbins = a*azbins**2 + b*azbins + c*rgbins+ d
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,e*x+f*x**2,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),6))
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = (i - ibeg_emp)**2
                    G[i*ncol:(i+1)*ncol,1] = i -  ibeg_emp
                    G[i*ncol:(i+1)*ncol,2] = np.arange((ncol)) - jbeg_emp
                G[:,3] = 1
                G[:,4] = elevi
                G[:,5] = elevi**2

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-2)],pars[:nparam-2]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-2):],pars[(nparam-2):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==1 and nfit==0):
                G=np.zeros((len(data),6))
                G[:,0] = azbins**2
                G[:,1] = azbins
                G[:,2] = rgbins
                G[:,3] = 1
                G[:,4] = topobins
                G[:,5] = topobins*azbins

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]
                print ('Remove ramp %f az**2, %f az  + %f r + %f + %f z + %f z*az for date: %i'%(a,b,c,d,e,f,idates[l]))

                # plot phase/elev
                funct = a*x**2 + b*x + c*y+ d + f*topo_clean*x
                funcbins = a*azbins**2 + b*azbins + c*rgbins+ d + f*topobins*azbins
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,e*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),6))
                G[:,3] = 1
                G[:,4] = elevi
                G[:,5] = elevi
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = (i - ibeg_emp)**2
                    G[i*ncol:(i+1)*ncol,1] = i -  ibeg_emp
                    G[i*ncol:(i+1)*ncol,2] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,5] *= (i - ibeg_emp)


                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-2)],pars[:nparam-2]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-2):],pars[(nparam-2):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==1 and nfit==1):
                G=np.zeros((len(data),8))
                G[:,0] = azbins**2
                G[:,1] = azbins
                G[:,2] = rgbins
                G[:,3] = 1
                G[:,4] = topobins*azbins
                G[:,5] = topobins
                G[:,6] = topobins**2
                G[:,7] = (topobins*azbins)**2

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]; g=pars[6]; h = pars[7]
                print ('Remove ramp %f az**2, %f az  + %f r + %f + %f z*az + %f z + %f z**2 + %f (z*az)**2 for date: %i'%(a,b,c,d,e,f,g,h,idates[l]))

                # plot phase/elev
                funct = a*x**2 + b*x + c*y+ d + e*topo_clean*x + h*(topo_clean*x)**2
                funcbins = a*azbins**2 + b*azbins + c*rgbins+ d + e*topobins*azbins + h*(topobins*azbins)**2
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,f*x+g*x**2,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),8))
                G[:,3] = 1
                G[:,4] = elevi
                G[:,5] = elevi
                G[:,6] = elevi**2
                G[:,7] = elevi**2
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = (i - ibeg_emp)**2
                    G[i*ncol:(i+1)*ncol,1] = i -  ibeg_emp
                    G[i*ncol:(i+1)*ncol,2] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,4] *= (i - ibeg_emp)
                    G[i*ncol:(i+1)*ncol,7] *= (i - ibeg_emp)**2

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-3)],pars[:nparam-3]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-3):],pars[(nparam-3):]).reshape(iend-ibeg,jend-jbeg)


      elif order==7:
        if radar is None:
            G=np.zeros((len(data),5))
            G[:,0] = azbins**2
            G[:,1] = azbins
            G[:,2] = rgbins**2
            G[:,3] = rgbins
            G[:,4] = 1

            # ramp inversion
            x0 = lst.lstsq(G,data)[0]
            _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
            _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
            pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
            a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]
            print ('Remove ramp %f az**2 %f az  + %f r**2 + %f r + %f for date: %i'%(a,b,c,d,e,idates[l]))

            # build total G matrix
            G=np.zeros((len(los),5))
            for i in range(nlines):
                G[i*ncol:(i+1)*ncol,0] = (i - ibeg_emp)**2
                G[i*ncol:(i+1)*ncol,1] = i - ibeg_emp
                G[i*ncol:(i+1)*ncol,2] = (np.arange((ncol)) - jbeg_emp)**2
                G[i*ncol:(i+1)*ncol,3] = np.arange((ncol)) - jbeg_emp
            G[:,4] = 1


            res = los - np.dot(G,pars)
            rms = np.sqrt(np.nanmean(res**2))
            logger.info('RMS dates %i: %f'%(idates[l], rms))

            ramp = np.dot(G,pars).reshape(iend-ibeg,jend-jbeg)

        else:
            if (ivar==0 and nfit ==0):
                G=np.zeros((len(data),6))
                G[:,0] = azbins**2
                G[:,1] = azbins
                G[:,2] = rgbins**2
                G[:,3] = rgbins
                G[:,4] = 1
                G[:,5] = topobins

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]
                print ('Remove ramp %f az**2, %f az  + %f r**2 + %f r + %f + %f z for date: %i'%(a,b,c,d,e,f,idates[l]))

                # plot phase/elev
                funct = a*x**2 + b*x + c*y**2 + d*x+ e
                funcbins = a*azbins**2 + b*azbins + c*rgbins**2 + d*rgbins+ e
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,f*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),6))
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = (i - ibeg_emp)**2
                    G[i*ncol:(i+1)*ncol,1] = i - ibeg_emp
                    G[i*ncol:(i+1)*ncol,2] = (np.arange((ncol)) - jbeg_emp)**2
                    G[i*ncol:(i+1)*ncol,3] = np.arange((ncol)) - jbeg_emp
                G[:,4] = 1
                G[:,5] = elevi


                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-1)],pars[:nparam-1]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-1):],pars[(nparam-1):]).reshape(iend-ibeg,jend-jbeg)

            if (ivar==0 and nfit ==1):
                G=np.zeros((len(data),7))
                G[:,0] = azbins**2
                G[:,1] = azbins
                G[:,2] = rgbins**2
                G[:,3] = rgbins
                G[:,4] = 1
                G[:,5] = topobins
                G[:,6] = topobins**2

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]; g = pars[6]
                print ('Remove ramp %f az**2, %f az  + %f r**2 + %f r + %f + %f z + %f z**2  for date: %i'%(a,b,c,d,e,f,g,idates[l]))

                # plot phase/elev
                funct = a*x**2 + b*x + c*y**2 + d*y+ e
                funcbins = a*azbins**2 + b*azbins + c*rgbins**2 + d*rgbins+ e
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,f*x+g*x**2,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),7))
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = (i - ibeg_emp)**2
                    G[i*ncol:(i+1)*ncol,1] = i - ibeg_emp
                    G[i*ncol:(i+1)*ncol,2] = (np.arange((ncol)) - jbeg_emp)**2
                    G[i*ncol:(i+1)*ncol,3] = np.arange((ncol)) - jbeg_emp
                G[:,4] = 1
                G[:,5] = elevi
                G[:,6] = elevi**2

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-2)],pars[:nparam-2]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-2):],pars[(nparam-2):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==1 and nfit ==0):
                G=np.zeros((len(data),7))
                G[:,0] = azbins**2
                G[:,1] = azbins
                G[:,2] = rgbins**2
                G[:,3] = rgbins
                G[:,4] = 1
                G[:,5] = topobins
                G[:,6] = topobins*azbins

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]; g=pars[6]
                print ('Remove ramp %f az**2, %f az  + %f r**2 + %f r + %f + %f z + %f az*z for date: %i'%(a,b,c,d,e,f,g,idates[l]))

                # plot phase/elev
                funct = a*x**2 + b*x + c*y**2 + d*y+ e + g*topo_clean*x
                funcbins = a*azbins**2 + b*azbins + c*rgbins**2 + d*rgbins+ e + g*topobins*azbins
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,f*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),7))
                G[:,4] = 1
                G[:,5] = elevi
                G[:,6] = elevi
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = (i - ibeg_emp)**2
                    G[i*ncol:(i+1)*ncol,1] = i - ibeg_emp
                    G[i*ncol:(i+1)*ncol,2] = (np.arange((ncol)) - jbeg_emp)**2
                    G[i*ncol:(i+1)*ncol,3] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,6] *= (i - ibeg_emp)


                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-2)],pars[:nparam-2]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-2):],pars[(nparam-2):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==1 and nfit==1):
                G=np.zeros((len(data),8))
                G[:,0] = azbins**2
                G[:,1] = azbins
                G[:,2] = rgbins**2
                G[:,3] = rgbins
                G[:,4] = 1
                G[:,5] = topobins*azbins
                G[:,6] = topobins
                G[:,7] = topobins**2

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]; g=pars[6]; h=pars[7]
                print ('Remove ramp %f az**2, %f az  + %f r**2 + %f r + %f +  %f az*z + %f z + %f z**2 for date: %i'%(a,b,c,d,e,f,g,h,idates[l]))

                # plot phase/elev
                funct = a*x**2 + b*x + c*y**2 + d*y+ e + f*topo_clean*x
                funcbins = a*azbins**2 + b*azbins + c*rgbins**2 + d*rgbins+ e + f*topobins*azbins
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,g*x+h*x**2,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),8))
                G[:,4] = 1
                G[:,5] = elevi
                G[:,6] = elevi
                G[:,7] = elevi**2
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = (i - ibeg_emp)**2
                    G[i*ncol:(i+1)*ncol,1] = i - ibeg_emp
                    G[i*ncol:(i+1)*ncol,2] = (np.arange((ncol)) - jbeg_emp)**2
                    G[i*ncol:(i+1)*ncol,3] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,5] *= (i - ibeg_emp)

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-3)],pars[:nparam-3]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-3):],pars[(nparam-3):]).reshape(iend-ibeg,jend-jbeg)

      elif order==8:
        if radar is None:
            G=np.zeros((len(data),6))
            G[:,0] = azbins**3
            G[:,1] = azbins**2
            G[:,2] = azbins
            G[:,3] = rgbins**2
            G[:,4] = rgbins
            G[:,5] = 1

            # ramp inversion
            x0 = lst.lstsq(G,data)[0]
            _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
            _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
            pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
            a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]
            print ('Remove ramp %f az**3 %f az**2  + %f az + %f r**2 + %f r + %f for date: %i'%(a,b,c,d,e,f,idates[l]))

            # build total G matrix
            G=np.zeros((len(los),6))
            for i in range(nlines):
                G[i*ncol:(i+1)*ncol,0] = (i - ibeg_emp)**3
                G[i*ncol:(i+1)*ncol,1] = (i - ibeg_emp)**2
                G[i*ncol:(i+1)*ncol,2] =(i - ibeg_emp)
                G[i*ncol:(i+1)*ncol,3] = (np.arange((ncol)) - jbeg_emp)**2
                G[i*ncol:(i+1)*ncol,4] = (np.arange((ncol)) - jbeg_emp)
            G[:,5] = 1


            res = los - np.dot(G,pars)
            rms = np.sqrt(np.nanmean(res**2))
            logger.info('RMS dates %i: %f'%(idates[l], rms))

            ramp = np.dot(G,pars).reshape(iend-ibeg,jend-jbeg)

        else:
            if (ivar==0 and nfit==0):
                G=np.zeros((len(data),7))
                G[:,0] = azbins**3
                G[:,1] = azbins**2
                G[:,2] = azbins
                G[:,3] = rgbins**2
                G[:,4] = rgbins
                G[:,5] = 1
                G[:,6] = topobins

                # ramp inversion1
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]; g = pars[6]
                print ('Remove ramp %f az**3, %f az**2  + %f az + %f r**2 + %f r + %f + %f z for date: %i'%(a,b,c,d,e,f,g,idates[l]))

                # plot phase/elev
                funct = a*x**3 + b*x**2 + c*x + d*y**2 + e*y+ f
                funcbins = a*azbins**3 + b*azbins**2 + c*azbins + d*rgbins**2 + e*rgbins+ f
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,g*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),7))
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = (i - ibeg_emp)**3
                    G[i*ncol:(i+1)*ncol,1] = (i - ibeg_emp)**2
                    G[i*ncol:(i+1)*ncol,2] =(i - ibeg_emp)
                    G[i*ncol:(i+1)*ncol,3] = (np.arange((ncol)) - jbeg_emp)**2
                    G[i*ncol:(i+1)*ncol,4] = np.arange((ncol)) - jbeg_emp
                G[:,5] = 1
                G[:,6] = elevi


                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-1)],pars[:nparam-1]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-1):],pars[(nparam-1):]).reshape(iend-ibeg,jend-jbeg)

            if (ivar==0 and nfit==1):
                G=np.zeros((len(data),8))
                G[:,0] = azbins**3
                G[:,1] = azbins**2
                G[:,2] = azbins
                G[:,3] = rgbins**2
                G[:,4] = rgbins
                G[:,5] = 1
                G[:,6] = topobins
                G[:,7] = topobins**2

                # ramp inversion1
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]; g = pars[6]; h = pars[7]
                print ('Remove ramp %f az**3, %f az**2  + %f az + %f r**2 + %f r + %f + %f z + %f z**2 for date: %i'%(a,b,c,d,e,f,g,h,idates[l]))

                # plot phase/elev
                funct = a*x**3 + b*x**2 + c*x + d*y**2 + e*y+ f
                funcbins = a*azbins**3 + b*azbins**2 + c*azbins + d*rgbins**2 + e*rgbins+ f
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,g*x+h*x**2,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),8))
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = (i - ibeg_emp)**3
                    G[i*ncol:(i+1)*ncol,1] = (i - ibeg_emp)**2
                    G[i*ncol:(i+1)*ncol,2] =(i - ibeg_emp)
                    G[i*ncol:(i+1)*ncol,3] = (np.arange((ncol)) - jbeg_emp)**2
                    G[i*ncol:(i+1)*ncol,4] = np.arange((ncol)) - jbeg_emp
                G[:,5] = 1
                G[:,6] = elevi
                G[:,7] = elevi**2

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-2)],pars[:nparam-2]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-2):],pars[(nparam-2):]).reshape(iend-ibeg,jend-jbeg)


            elif (ivar==1 and nfit==0):
                G=np.zeros((len(data),8))
                G[:,0] = azbins**3
                G[:,1] = azbins**2
                G[:,2] = azbins
                G[:,3] = rgbins**2
                G[:,4] = rgbins
                G[:,5] = 1
                G[:,6] = topobins
                G[:,7] = topobins*azbins

                # ramp inversion1
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]; g = pars[6]; h=pars[7]
                print ('Remove ramp %f az**3, %f az**2  + %f az + %f r**2 + %f r + %f + %f z + %f z*az for date: %i'%(a,b,c,d,e,f,g,h,idates[l]))

                # plot phase/elev
                funct = a*x**3 + b*x**2 + c*x + d*y**2 + e*y+ f + h*topo_clean*x
                funcbins = a*azbins**3 + b*azbins**2 + c*azbins + d*rgbins**2 + e*rgbins+ f + h*topobins*azbins
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,g*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),8))
                G[:,5] = 1
                G[:,6] = elevi
                G[:,7] = elevi
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = (i - ibeg_emp)**3
                    G[i*ncol:(i+1)*ncol,1] = (i - ibeg_emp)**2
                    G[i*ncol:(i+1)*ncol,2] =(i - ibeg_emp)
                    G[i*ncol:(i+1)*ncol,3] = (np.arange((ncol)) - jbeg_emp)**2
                    G[i*ncol:(i+1)*ncol,4] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,7] *= (i - ibeg_emp)


                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-2)],pars[:nparam-2]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-2):],pars[(nparam-2):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==1 and nfit==1):
                G=np.zeros((len(data),10))
                G[:,0] = azbins**3
                G[:,1] = azbins**2
                G[:,2] = azbins
                G[:,3] = rgbins**2
                G[:,4] = rgbins
                G[:,5] = 1
                G[:,6] = topobins*azbins
                G[:,7] = topobins
                G[:,8] = topobins**2
                G[:,9] = (topobins*azbins)**2

                # ramp inversion1
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]; g = pars[6]; h=pars[7]; i=pars[8]; k=pars[9]
                print ('Remove ramp %f az**3, %f az**2  + %f az + %f r**2 + %f r + %f z*az + %f + %f z + %f z**2 + %f (z*az)**2 for date: %i'%(a,b,c,d,e,f,g,h,i,k,idates[l]))

                # plot phase/elev
                funct = a*x**3 + b*x**2 + c*x + d*y**2 + e*y+ f + g*topo_clean*x + k*(topo_clean*x)**2
                funcbins = a*azbins**3 + b*azbins**2 + c*azbins + d*rgbins**2 + e*rgbins+ f + g*topobins*azbins + k*(topobins*azbins)**2
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,h*x+i*x**2,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),10))
                G[:,5] = 1
                G[:,6] = elevi
                G[:,7] = elevi
                G[:,8] = elevi**2
                G[:,9] = elevi**2
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = (i - ibeg_emp)**3
                    G[i*ncol:(i+1)*ncol,1] = (i - ibeg_emp)**2
                    G[i*ncol:(i+1)*ncol,2] =(i - ibeg_emp)
                    G[i*ncol:(i+1)*ncol,3] = (np.arange((ncol)) - jbeg_emp)**2
                    G[i*ncol:(i+1)*ncol,4] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,6] *= (i - ibeg_emp)
                    G[i*ncol:(i+1)*ncol,9] *= (i - ibeg_emp)**2

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-3)],pars[:nparam-3]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-3):],pars[(nparam-3):]).reshape(iend-ibeg,jend-jbeg)

      elif order==9:
        if radar is None:
            G=np.zeros((len(data),5))
            G[:,0] = rgbins
            G[:,1] = azbins
            G[:,2] = (rgbins*azbins)**2
            G[:,3] = rgbins*azbins
            G[:,4] = 1

            # ramp inversion
            x0 = lst.lstsq(G,data)[0]
            _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
            _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
            pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
            a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]
            print ('Remove ramp %f r %f az  + %f r*az**2 + %f r*az + %f for date: %i'%(a,b,c,d,e,idates[l]))

            # build total G matrix
            G=np.zeros((len(los),5))
            for i in range(nlines):
                G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
                G[i*ncol:(i+1)*ncol,1] = i - ibeg_emp
                G[i*ncol:(i+1)*ncol,2] = ((i-ibeg_emp) * (np.arange((ncol))-jbeg_emp))**2
                G[i*ncol:(i+1)*ncol,3] = (i-ibeg_emp) * (np.arange((ncol))-jbeg_emp)
            G[:,4] = 1

            res = los - np.dot(G,pars)
            rms = np.sqrt(np.nanmean(res**2))
            logger.info('RMS dates %i: %f'%(idates[l], rms))

            ramp = np.dot(G,pars).reshape(iend-ibeg,jend-jbeg)

        else:
            if (ivar==0 and nfit==0):
                G=np.zeros((len(data),6))
                G[:,0] = rgbins
                G[:,1] = azbins
                G[:,2] = (rgbins*azbins)**2
                G[:,3] = rgbins*azbins
                G[:,4] = 1
                G[:,5] = topobins

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]

                print ('Remove ramp %f r, %f az  + %f (r*az)**2 + %f r*az + %f + %f z for date: %i'%(a,b,c,d,e,f,idates[l]))

                # plot phase/elev
                funcbins = a*y+ b*x + c*(x*y)**2 + d*x*y+ e
                funct = a*rgbins+ b*azbins + c*(azbins*rgbins)**2 + d*azbins*rgbins+ e
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,e*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),6))
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,1] = i - ibeg_emp
                    G[i*ncol:(i+1)*ncol,2] = ((i-ibeg_emp) * (np.arange((ncol))-jbeg_emp))**2
                    G[i*ncol:(i+1)*ncol,3] = (i-ibeg_emp) * (np.arange((ncol))-jbeg_emp)
                G[:,4] = 1
                G[:,5] = elevi

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-1)],pars[:nparam-1]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-1):],pars[(nparam-1):]).reshape(iend-ibeg,jend-jbeg)

            if (ivar==0 and nfit==1):
                G=np.zeros((len(data),7))
                G[:,0] = rgbins
                G[:,1] = azbins
                G[:,2] = (rgbins*azbins)**2
                G[:,3] = rgbins*azbins
                G[:,4] = 1
                G[:,5] = topobins
                G[:,6] = topobins**2

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5]; g = pars[6]

                print ('Remove ramp %f r, %f az  + %f (r*az)**2 + %f r*az + %f + %f z + %f z**2  for date: %i'%(a,b,c,d,e,f,g,idates[l]))

                # plot phase/elev
                funct = a*y+ b*x + c*(x*y)**2 + d*x*y+ e
                funcbins = a*rgbins+ b*azbins + c*(azbins*rgbins)**2 + d*azbins*rgbins+ e
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,f*x+g*x**2,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),7))
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,1] = i - ibeg_emp
                    G[i*ncol:(i+1)*ncol,2] = ((i-ibeg_emp) * (np.arange((ncol))-jbeg_emp))**2
                    G[i*ncol:(i+1)*ncol,3] = (i-ibeg_emp) * (np.arange((ncol))-jbeg_emp)
                G[:,4] = 1
                G[:,5] = elevi
                G[:,6] = elevi**2

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-2)],pars[:nparam-2]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-2):],pars[(nparam-2):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==1 and nfit==0):
                G=np.zeros((len(data),7))
                G[:,0] = rgbins
                G[:,1] = azbins
                G[:,2] = (rgbins*azbins)**2
                G[:,3] = rgbins*azbins
                G[:,4] = 1
                G[:,5] = topobins
                G[:,6] = topobins*azbins

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5] ; g = pars[6]

                print ('Remove ramp %f r, %f az  + %f (r*az)**2 + %f r*az + %f + %f z + %f az*z for date: %i'%(a,b,c,d,e,f,g,idates[l]))

                # plot phase/elev
                funct = a*y+ b*x + c*(x*y)**2 + d*x*y+ e + g*topo_clean*x
                funcbins = a*rgbins+ b*azbins + c*(azbins*rgbins)**2 + d*azbins*rgbins+ e + g*topobins*azbins
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,f*x,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),7))
                G[:,4] = 1
                G[:,5] = elevi
                G[:,6] = elevi
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,1] = i - ibeg_emp
                    G[i*ncol:(i+1)*ncol,2] = ((i-ibeg_emp) * (np.arange((ncol))-jbeg_emp))**2
                    G[i*ncol:(i+1)*ncol,3] = (i-ibeg_emp) * (np.arange((ncol))-jbeg_emp)
                    G[i*ncol:(i+1)*ncol,6] *= (i - ibeg_emp)

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-2)],pars[:nparam-2]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-2):],pars[(nparam-2):]).reshape(iend-ibeg,jend-jbeg)

            elif (ivar==1 and nfit==1):
                G=np.zeros((len(data),8))
                G[:,0] = rgbins
                G[:,1] = azbins
                G[:,2] = (rgbins*azbins)**2
                G[:,3] = rgbins*azbins
                G[:,4] = 1
                G[:,5] = topobins*azbins
                G[:,6] = topobins
                G[:,7] = topobins**2

                # ramp inversion
                x0 = lst.lstsq(G,data)[0]
                _func = lambda x: np.sum(((np.dot(G,x)-data)/rms)**2)
                _fprime = lambda x: 2*np.dot(G.T/rms, (np.dot(G,x)-data)/rms)
                pars = opt.fmin_slsqp(_func,x0,fprime=_fprime,iter=2000,full_output=True,iprint=0,acc=1.e-9)[0]
                a = pars[0]; b = pars[1]; c = pars[2]; d = pars[3]; e = pars[4]; f = pars[5] ; g = pars[6]; h=pars[7]

                print ('Remove ramp %f r, %f az  + %f (r*az)**2 + %f r*az + %f + %f az*z + %f z + %f z**2  for date: %i'%(a,b,c,d,e,f,g,h,idates[l]))

                # plot phase/elev
                funct = a*y+ b*x + c*(x*y)**2 + d*x*y+ e + f*topo_clean*x
                funcbins = a*rgbins+ b*azbins + c*(azbins*rgbins)**2 + d*azbins*rgbins+ e + f*topobins*azbins
                x = np.linspace(mintopo, maxtopo, 100)
                ax.scatter(topo_clean,los_clean-funct, s=0.01, alpha=0.3, rasterized=True)
                ax.plot(topobins,losbins - funcbins,'-r', lw =1., label='sliding median')
                ax.plot(x,g*x+h*x**2,'-r', lw =4.)

                # build total G matrix
                G=np.zeros((len(los),8))
                G[:,4] = 1
                G[:,5] = elevi
                G[:,6] = elevi
                G[:,7] = elevi**2
                for i in range(nlines):
                    G[i*ncol:(i+1)*ncol,0] = np.arange((ncol)) - jbeg_emp
                    G[i*ncol:(i+1)*ncol,1] = i - ibeg_emp
                    G[i*ncol:(i+1)*ncol,2] = ((i-ibeg_emp) * (np.arange((ncol))-jbeg_emp))**2
                    G[i*ncol:(i+1)*ncol,3] = (i-ibeg_emp) * (np.arange((ncol))-jbeg_emp)
                    G[i*ncol:(i+1)*ncol,5] *= (i - ibeg_emp)

                res = los - np.dot(G,pars)
                rms = np.sqrt(np.nanmean(res**2))
                logger.info('RMS dates %i: %f'%(idates[l], rms))

                nparam = G.shape[1]
                ramp = np.dot(G[:,:(nparam-3)],pars[:nparam-3]).reshape(iend-ibeg,jend-jbeg)
                topo = np.dot(G[:,(nparam-3):],pars[(nparam-3):]).reshape(iend-ibeg,jend-jbeg)

      # flata = (los - np.dot(G,pars)).reshape(iend-ibeg,jend-jbeg)
      flata = los.reshape(iend-ibeg,jend-jbeg) - ramp - topo
      noramps = los.reshape(iend-ibeg,jend-jbeg) - ramp

      return ramp, flata, topo, rms, noramps
 
def empirical_cor(l):
  """
  Function that preapare and run empirical estimaton for each interferogram kk
  """
  
  # global maps, models, elev, perc_topo, maxtopo, mintopo
  # global mask_flat, seuil, rmsmap, threshold_rms, slope, radar
  # global flat, iend_emp, ibeg_emp, ivar, nfit
  # global lin_start, lin_end, col_start,col_end

  # first clean los
  maps_temp = np.matrix.copy(maps[:,:,l]) - np.matrix.copy(models[:,:,l])

  # no estimation on the ref image set to zero 
  if np.nansum(maps[:,:,l]) != 0:

    maxlos,minlos=np.nanpercentile(maps_temp[ibeg_emp:iend_emp,jbeg_emp:jend_emp],perc_los),np.nanpercentile(maps_temp[ibeg_emp:iend_emp,jbeg_emp:jend_emp],100-perc_los)
    kk = np.nonzero(np.logical_or(maps_temp==0.,np.logical_or((maps_temp>maxlos),(maps_temp<minlos))))
    maps_temp[kk] = np.float('NaN')

    itemp = ibeg_emp
    for lign in range(ibeg_emp,iend_emp,10):
        if np.isnan(np.nanmean(maps[lign:lign+10,:,l])):
            itemp = lign
        else:
            break
    logger.debug('Begining of the image: {}'.format(itemp))

    if radar is not None:
        maxtopo,mintopo = np.nanpercentile(elev,perc_topo),np.nanpercentile(elev,100-perc_topo)
        ax = fig.add_subplot(4,int(N/4)+1,l+1)
    else:
        maxtopo,mintopo = 2, 0
    logger.debug('Max-Min topo: {0}-{1}'.format(maxtopo,mintopo))

    logger.debug('Threshold RMS: {}'.format(threshold_rms))

    # selection pixels
    index = np.nonzero(np.logical_and(elev<maxtopo,
        np.logical_and(elev>mintopo,
            np.logical_and(mask_flat>seuil,
            np.logical_and(~np.isnan(maps_temp),
                np.logical_and(~np.isnan(rmsmap),
                np.logical_and(~np.isnan(elev),
                np.logical_and(rmsmap<threshold_rms,
                np.logical_and(rmsmap>1.e-6,
                np.logical_and(~np.isnan(maps_temp),
                np.logical_and(pix_az>ibeg,
                np.logical_and(pix_az<iend,
                np.logical_and(pix_rg>jbeg,
                np.logical_and(pix_rg<jend, 
                    slope>0.,
                    ))))))))
                ))))))

    # extract coordinates for estimation
    temp = np.array(index).T
    x = temp[:,0]; y = temp[:,1]
    # clean maps
    los_clean = maps_temp[index].flatten()
    topo_clean = elev[index].flatten()
    rms_clean = rmsmap[index].flatten()
    
    # print itemp, iend_emp
    if flat>5 and iend_emp-itemp < .6*(iend_emp-ibeg_emp):
        logger.warning('Image too short in comparison to master, set flat to 5')
        temp_flat=5
    else:
        temp_flat=flat

    if ivar>0 and iend_emp-itemp < .6*(iend_emp-ibeg_emp):
      logger.warning('Image too short in comparison to master, set ivar to 0')
      ivar_temp=0
      nfit_temp=0
    else:
      ivar_temp=ivar
      nfit_temp=nfit

    # call ramp estim
    los = as_strided(maps[:,:,l]).flatten()
    samp = 1

    map_ramp, map_flata, map_topo, rms, map_noramps = estim_ramp(los,los_clean[::samp],topo_clean[::samp],x[::samp],\
      y[::samp],temp_flat,rms_clean[::samp],nfit_temp, ivar_temp, l)

    if (lin_start is not None) and (lin_end is not None):
      try:
        indexref = np.nonzero(np.logical_and(elev<maxtopo,
        np.logical_and(elev>mintopo,
            np.logical_and(mask_flat>seuil,
            np.logical_and(~np.isnan(maps_temp),
                np.logical_and(~np.isnan(rmsmap),
                np.logical_and(~np.isnan(elev),
                np.logical_and(rmsmap<threshold_rms,
                np.logical_and(rmsmap>1.e-6,
                np.logical_and(~np.isnan(maps_temp),
                np.logical_and(pix_az>lin_start,
                np.logical_and(pix_az<lin_end,
                np.logical_and(pix_rg>col_start,
                np.logical_and(pix_rg<col_end, 
                    slope>0.,
                ))))))))))))
                ))
        
        ## Set data to zero in the ref area
        zone = as_strided(map_flata[:,:,l])
        los_ref2 = zone[indexref].flatten()
        rms_ref = rmsmap[indexref].flatten()
        amp_ref = 1./rms_ref
        amp_ref = amp_ref/np.nanmax(amp_ref)
        # weigth avera of the phase
        cst = np.nansum(los_ref2*amp_ref) / np.nansum(amp_ref)
        logger.info('Re-estimation of a constant within lines {0}-{1} and cols {2}-{3}'.format(lin_start,lin_end,col_start,col_end))
        logger.info('Average phase within ref area: {0}:'.format(cst))
        if np.isnan(cst):
          cst = 0.
        map_ramp, map_flata, map_noramps = map_ramp + cst, map_flata - cst, maps_noramps - cst 
        del zone
      except:
        pass

      del los_clean
      del rms_clean
      del topo_clean
      del maps_temp
  
  else:
    map_flata, map_noramps = np.copy(maps[:,:,l]),np.copy(maps[:,:,l])
    map_ramp, map_topo  = np.zeros(np.shape(map_flata)), np.zeros(np.shape(map_flata))
    rms = 1

  # set ramp to NaN to have ramp of the size of the images
  kk = np.nonzero(np.isnan(map_flata))
  ramp = as_strided(map_ramp)
  ramp[kk] = float('NaN')
  topo = as_strided(map_topo)
  topo[kk] = float('NaN')

  return map_ramp, map_flata, map_topo, rms, map_noramps 

def temporal_decomp(pix):
    j = pix  % (jend-jbeg)
    i = int(pix/(jend-jbeg))

    # Initialisation
    mdisp=np.ones((N))*float('NaN')
    mlin=np.ones((N))*float('NaN')
    mseas=np.ones((N))*float('NaN')
    mvect=np.ones((N))*float('NaN')
    disp = as_strided(maps_flata[i,j,:])
    k = np.flatnonzero(~np.isnan(disp)) # invers of isnan
    # do not take into account NaN data
    kk = len(k)
    tabx = dates[k]
    taby = disp[k]
    bp = base[k]

    naps_tmp = np.zeros((N))
    aps_tmp = np.zeros((N))

    # Inisilize m to zero
    m = np.zeros((M))
    sigmam = np.ones((M))*float('NaN')

    if kk > N/6:
        G=np.zeros((kk,M))
        # Build G family of function k1(t),k2(t),...,kn(t): #
        #                                                   #
        #           |k1(0) .. kM(0)|                        #
        # Gfamily = |k1(1) .. kM(1)|                        #
        #           |..    ..  ..  |                        #
        #           |k1(N) .. kM(N)|                        #
        #                                                   #

        G=np.zeros((kk,M))
        for l in range((Mbasis)):
            G[:,l]=basis[l].g(tabx)
        for l in range((Mker)):
            G[:,Mbasis+l]=kernels[l].g(k)

        # inversion
        m,sigmam = consInvert(G,taby,inaps[k],cond=rcond,ineq=ineq)

        # forward model in original order
        mdisp[k] = np.dot(G,m)

        # compute aps for each dates
        # aps_tmp = pow((disp[k]-mdisp[k])/inaps[k],2)
        # dont weight by inaps to be consistent from one iteration to the other
        aps_tmp[k] = abs((disp[k]-mdisp[k]))

        # # # remove NaN value for next iterations (but normally no NaN?)
        # index = np.flatnonzero(np.logical_or(np.isnan(aps_tmp),aps_tmp==0))
        # aps_tmp[index] = 1.0 # 1 is a bad misfit

        # count number of pixels per dates
        naps_tmp[k] = naps_tmp[k] + 1.0

        # Build seasonal and linear models
        if inter=='yes':
            mlin[k] = np.dot(G[:,indexinter],m[indexinter])
        if seasonal=='yes':
            mseas[k] = np.dot(G[:,indexseas:indexseas+2],m[indexseas:indexseas+2])
        if arguments["--vector"] != None:
            mvect[k] = np.dot(G[:,indexvect],m[indexvect])

    return m, sigmam, mdisp, mlin, mseas, mvect, aps_tmp, naps_tmp


# initialization
maps_flata = np.copy(maps)
models = np.zeros((iend-ibeg,jend-jbeg,N))

# prepare flatten maps
maps_ramp = np.zeros((iend-ibeg,jend-jbeg,N))
maps_topo = np.zeros((iend-ibeg,jend-jbeg,N))
maps_noramps = np.zeros((iend-ibeg,jend-jbeg,N))
rms = np.zeros((N))

for ii in range(niter):
    print()
    print('---------------')
    print('iteration: {}'.format(ii))
    print('---------------')

    #############################
    # SPATIAL ITERATION N  ######
    #############################

    pix_az, pix_rg = np.indices((iend-ibeg,jend-jbeg))
    # if radar file just initialise figure
    if radar is not None:
      nfigure +=1
      fig = plt.figure(nfigure,figsize=(14,10))
    
    # if iteration = 0 or spatialiter==yes, then spatial estimation
    if (ii==0) or (spatialiter=='yes') :

      print() 
      #########################################
      print('---------------')
      print('Empirical estimations')
      print('---------------')
      #########################################
      print()
    
      # # Loop over the dates
      # for l in range((N)):
      #   maps_ramp[:,:,l], maps_flata[:,:,l], maps_topo[:,:,l], rms[l], maps_noramps[:,:,l] = empirical_cor(l)

      output = []
      with TimeIt():
          # for kk in range(Nifg):
          work = range(N)
          with poolcontext(processes=nproc) as pool:
              results = pool.map(empirical_cor, work)
              # maps_ramp[:,:,l], maps_flata[:,:,l], maps_topo[:,:,l], rms[l], maps_noramps[:,:,l] = results[0][l]
              # TypeError: cannot unpack non-iterable int object
          output.append(results)

          # fetch results
          for l in range(N):
              maps_ramp[:,:,l], maps_flata[:,:,l], maps_topo[:,:,l], rms[l], maps_noramps[:,:,l] = output[0][l]
          del output

      # plot corrected ts
      nfigure +=1
      figd = plt.figure(nfigure,figsize=(14,10))
      figd.subplots_adjust(hspace=0.001,wspace=0.001)
      for l in range((N)):
          axd = figd.add_subplot(4,int(N/4)+1,l+1)
          caxd = axd.imshow(maps_flata[:,:,l],cmap=cmap,vmax=vmax,vmin=vmin)
          axd.set_title(idates[l],fontsize=6)
          plt.setp(axd.get_xticklabels(), visible=False)
          plt.setp(axd.get_yticklabels(), visible=False)
      plt.setp(axd.get_xticklabels(), visible=False)
      plt.setp(axd.get_yticklabels(), visible=False)
      figd.colorbar(caxd, orientation='vertical',aspect=10)
      figd.suptitle('Corrected time series maps')
      fig.tight_layout()
      figd.savefig('maps_flat.eps', format='EPS',dpi=150)

      if radar is not None:
          fig.savefig('phase-topo.eps', format='EPS',dpi=150)
          nfigure +=1
          figtopo = plt.figure(nfigure,figsize=(14,10))
          figtopo.subplots_adjust(hspace=.001,wspace=0.001)
          for l in range((N)):
              axtopo = figtopo.add_subplot(4,int(N/4)+1,l+1)
              caxtopo = axtopo.imshow(maps_topo[:,:,l]+maps_ramp[:,:,l],cmap=cmap,vmax=vmax,vmin=vmin)
              axtopo.set_title(idates[l],fontsize=6)
              plt.setp(axtopo.get_xticklabels(), visible=False)
              plt.setp(axtopo.get_yticklabels(), visible=False)
              plt.setp(axtopo.get_xticklabels(), visible=False)
              plt.setp(axtopo.get_yticklabels(), visible=False)
          figtopo.colorbar(caxtopo, orientation='vertical',aspect=10)
          figtopo.suptitle('Time series RAMPS+TOPO')
          fig.tight_layout()
          figtopo.savefig('tropo.eps', format='EPS',dpi=150)
          

      else:
          # plot corrected ts
          nfigure +=1
          figref = plt.figure(nfigure,figsize=(14,10))
          figref.subplots_adjust(hspace=0.001,wspace=0.001)
          for l in range((N)):
              axref = figref.add_subplot(4,int(N/4)+1,l+1)
              caxref = axref.imshow(maps_ramp[:,:,l],cmap=cmap,vmax=vmax,vmin=vmin)
              axref.set_title(idates[l],fontsize=6)
              plt.setp(axref.get_xticklabels(), visible=False)
              plt.setp(axref.get_yticklabels(), visible=False)
          plt.setp(axref.get_xticklabels(), visible=False)
          plt.setp(axref.get_yticklabels(), visible=False)
          figref.suptitle('Time series RAMPS')
          figref.colorbar(caxref, orientation='vertical',aspect=10)
          fig.tight_layout()
          figref.savefig('maps_ramps.eps', format='EPS',dpi=150)
          

    if plot=='yes':
        plt.show()
    plt.close('all')

    # save rms
    if (apsf=='no' and ii==0):
        # aps from rms
        logger.info('Use RMS empirical estimation as uncertainties for time decomposition')
        inaps = np.copy(rms)
        logger.info('Set very low values to the 2 percentile to avoid overweighting...')
        # scale between 0 and 1 
        maxaps = np.nanmax(inaps)
        inaps = inaps/maxaps
        minaps= np.nanpercentile(inaps,2)
        index = np.flatnonzero(inaps<minaps)
        inaps[index] = minaps
        np.savetxt('rms_empcor.txt', inaps.T)
        del rms

    ########################
    # TEMPORAL ITERATION N #
    ########################

    print() 
    #########################################
    print('---------------')
    print('Time Decomposition')
    print('---------------')
    #########################################
    print()

    # initialize aps for each images to 1
    aps = np.ones((N))
    n_aps = np.ones((N)).astype(int)
    logger.debug('Input uncertainties: {}'.format(inaps))

    # reiinitialize maps models
    models = np.zeros((iend-ibeg,jend-jbeg,N))
    models_trends = np.zeros((iend-ibeg,jend-jbeg,N))
    models_seas = np.zeros((iend-ibeg,jend-jbeg,N))
    models_lin = np.zeros((iend-ibeg,jend-jbeg,N))
    models_vect = np.zeros((iend-ibeg,jend-jbeg,N))

    output = []
    with TimeIt():
        work = range(0,(iend-ibeg)*(jend-jbeg),sampling)
        with poolcontext(processes=nproc) as pool:
            results = pool.map(temporal_decomp, work)
        output.append(results)

        # fetch results
        for pix in range(0,(iend-ibeg)*(jend-jbeg),sampling):
            j = pix  % (jend-jbeg)
            i = int(pix/(jend-jbeg))
            
            # m, sigmam, models[i,j,:], models_lin[i,j,:], models_seas[i,j,:], models_vect, aps_pix, naps_pix = temporal_decomp(pix)
            m, sigmam, models[i,j,:], models_lin[i,j,:], models_seas[i,j,:], models_vect, aps_pix, naps_pix = output[0][pix]
          
            aps = aps + aps_pix
            n_aps = n_aps + naps_pix

            # save m
            for l in range((Mbasis)):
                basis[l].m[i,j] = m[l]
                basis[l].sigmam[i,j] = sigmam[l]

            for l in range((Mker)):
                kernels[l].m[i,j] = m[Mbasis+l]
                kernels[l].sigmam[i,j] = sigmam[Mbasis+l]

        del output

    # convert aps in rad
    aps = aps/n_aps
    # aps = np.sqrt(abs(aps/n_aps))

    # remove low aps to avoid over-fitting in next iter
    minaps= np.nanpercentile(aps,2)
    index = np.flatnonzero(aps<minaps)
    aps[index] = minaps

    print('Dates      APS     # of points')
    for l in range(N):
        print (idates[l], aps[l], np.int(n_aps[l]))
    np.savetxt('aps_{}.txt'.format(ii), aps.T, fmt=('%.6f'))
    # set apsf is yes for iteration
    apsf=='yes'
    # update aps for next iterations
    inaps = np.copy(aps)

#######################################################
# Save new cubes
#######################################################

# create new cube
logger.info('Save flatten time series cube: {}'.format('depl_cumule_flat'))
cube_flata = maps_flata[:,:,:].flatten()
cube_noramps = maps_noramps[:,:,:].flatten()

fid = open('depl_cumule_flat', 'wb')
cube_flata.flatten().astype('float32').tofile(fid)
fid.close()

if fulloutput=='yes':
    if (seasonal=='yes'):
        logger.info('Save time series cube without seasonality: {}'.format('depl_cumule_dseas'))
        fid = open('depl_cumule_dseas', 'wb')
        (maps_flata - models_seas).flatten().astype('float32').tofile(fid)
        fid.close()

    if inter=='yes':
        fid = open('depl_cumule_dtrend', 'wb')
        logger.info('Save de-trended time series cube: {}'.format('depl_cumule_dtrend'))
        (maps_flata - models_lin).flatten().astype('float32').tofile(fid)
        fid.close()

    if arguments["--vector"] != None:
        fid = open('depl_cumule_dvect', 'wb')
        logger.info('Save time series cube without vector component: {}'.format('depl_cumule_dvect'))
        (maps_flata - models_vect).flatten().astype('float32').tofile(fid)
        fid.close()

    if flat>0:
        fid = open('depl_cumule_noramps', 'wb')
        logger.info('Save time series cube without ramps only: {}'.format('depl_cumule_noramps'))
        cube_noramps.flatten().astype('float32').tofile(fid)
        fid.close()

# clean memory
try:
  del cube_flata, cube_noramps
except:
  pass

# create MAPS directory to save .r4
if fulloutput=='yes':
    outdir = './MAPS/'
    logger.info('Save time series maps in: {}'.format(outdir))
    if not os.path.exists(outdir):
        os.makedirs(outdir)

# plot displacements models and residuals
nfigure +=1
figres = plt.figure(nfigure,figsize=(14,10))
figres.subplots_adjust(hspace=.001,wspace=0.001)

nfigure +=1
fig = plt.figure(nfigure,figsize=(14,10))
fig.subplots_adjust(hspace=.001,wspace=0.01)

# nfigure +=1
# figall = plt.figure(nfigure,figsize=(20,9))
# figall.subplots_adjust(hspace=0.00001,wspace=0.001)

nfigure +=1
figclr = plt.figure(nfigure)
# plot color map
ax = figclr.add_subplot(1,1,1)
cax = ax.imshow(maps[:,:,-1],cmap=cmap,vmax=vmax,vmin=vmin)
plt.setp( ax.get_xticklabels(), visible=False)
cbar = figclr.colorbar(cax, orientation='horizontal',aspect=5)
figclr.savefig('colorscale.eps', format='EPS',dpi=150)

for l in range((N)):
    data = as_strided(maps[:,:,l])
    if Mker>0:
        data_flat = as_strided(maps_flata[:,:,l])- as_strided(kernels[0].m[:,:]) - as_strided(basis[0].m[:,:])
        model = as_strided(models[:,:,l]) - as_strided(basis[0].m[:,:]) - as_strided(kernels[0].m[:,:])
    else:
        data_flat = as_strided(maps_flata[:,:,l]) - as_strided(basis[0].m[:,:])
        model = as_strided(models[:,:,l]) - as_strided(basis[0].m[:,:])

    res = data_flat - model
    ramp = as_strided(maps_ramp[:,:,l])
    tropo = as_strided(maps_topo[:,:,l])

    ax = fig.add_subplot(4,int(N/4)+1,l+1)
    axres = figres.add_subplot(4,int(N/4)+1,l+1)

    # axall = figall.add_subplot(6,N,l+1)
    # axall.imshow(data,cmap=cmap,vmax=vmax,vmin=vmin)
    # axall.set_title(idates[l],fontsize=6)
    # plt.setp(axall.get_xticklabels(), visible=False)
    # plt.setp(axall.get_yticklabels(), visible=False)
    # if l==0:
    #     axall.set_ylabel('DATA')
    # axall = figall.add_subplot(6,N,l+1+N)
    # axall.imshow(ramp,cmap=cmap,vmax=vmax,vmin=vmin)
    # plt.setp(axall.get_xticklabels(), visible=False)
    # plt.setp(axall.get_yticklabels(), visible=False)
    # if l==0:
    #     axall.set_ylabel('RAMP')
    # axall = figall.add_subplot(6,N,l+1+2*N)
    # axall.imshow(tropo,cmap=cmap,vmax=vmax,vmin=vmin)
    # plt.setp(axall.get_xticklabels(), visible=False)
    # plt.setp(axall.get_yticklabels(), visible=False)
    # if l==0:
    #     axall.set_ylabel('TROP0')
    # axall = figall.add_subplot(6,N,l+1+3*N)
    # axall.imshow(data_flat,cmap=cmap,vmax=vmax,vmin=vmin)
    # plt.setp(axall.get_xticklabels(), visible=False)
    # plt.setp(axall.get_yticklabels(), visible=False)
    # if l==0:
    #     axall.set_ylabel('FLATTEN DATA')
    # axall = figall.add_subplot(6,N,l+1+4*N)
    # axall.imshow(model,cmap=cmap,vmax=vmax,vmin=vmin)
    # plt.setp(axall.get_xticklabels(), visible=False)
    # plt.setp(axall.get_yticklabels(), visible=False)
    # if l==0:
    #     axall.set_ylabel('MODEL')
    # axall = figall.add_subplot(6,N,l+1+5*N)
    # axall.imshow(res,cmap=cmap,vmax=vmax,vmin=vmin)
    # plt.setp(axall.get_xticklabels(), visible=False)
    # plt.setp(axall.get_yticklabels(), visible=False)
    # if l==0:
    #     axall.set_ylabel('RES')

    cax = ax.imshow(model,cmap=cmap,vmax=vmax,vmin=vmin)
    caxres = axres.imshow(res,cmap=cmap,vmax=vmax,vmin=vmin)

    ax.set_title(idates[l],fontsize=6)
    axres.set_title(idates[l],fontsize=6)

    plt.setp(ax.get_xticklabels(), visible=False)
    plt.setp(ax.get_yticklabels(), visible=False)

    plt.setp(axres.get_xticklabels(), visible=False)
    plt.setp(axres.get_yticklabels(), visible=False)

    fig.tight_layout()

    # ############
    # # SAVE .R4 #
    # ############

    # save flatten maps
    if fulloutput=='yes':

        if geotiff is not None:

            ds = driver.Create(outdir+'{}_flat.tif'.format(idates[l]), jend-jbeg, iend-ibeg, 1, gdal.GDT_Float32)
            band = ds.GetRasterBand(1)
            band.WriteArray(data_flat)
            ds.SetGeoTransform(gt)
            ds.plt.setprojection(proj)
            band.FlushCache()

            ds = driver.Create(outdir+'{}_ramp_tropo.tif'.format(idates[l]), jend-jbeg, iend-ibeg, 1, gdal.GDT_Float32)
            band = ds.GetRasterBand(1)
            band.WriteArray(ramp+tropo)
            ds.SetGeoTransform(gt)
            ds.plt.setprojection(proj)
            band.FlushCache()

            ds = driver.Create(outdir+'{}_model.tif'.format(idates[l]), jend-jbeg, iend-ibeg, 1, gdal.GDT_Float32)
            band = ds.GetRasterBand(1)
            band.WriteArray(model)
            ds.SetGeoTransform(gt)
            ds.plt.setprojection(proj)
            band.FlushCache()

            # ds = driver.Create(outdir+'{}_res.tif'.format(idates[l]), jend-jbeg, iend-ibeg, 1, gdal.GDT_Float32)
            # band = ds.GetRasterBand(1)
            # band.WriteArray(res)
            # ds.SetGeoTransform(gt)
            # ds.plt.setprojection(proj)
            # band.FlushCache()

        else:

            fid = open(outdir+'{}_flat.r4'.format(idates[l]), 'wb')
            data_flat.flatten().astype('float32').tofile(fid)
            fid.close()

            # save ramp maps
            fid = open(outdir+'{}_ramp_tropo.r4'.format(idates[l]), 'wb')
            (ramp+tropo).flatten().astype('float32').tofile(fid)
            fid.close()

            # save model maps
            fid = open(outdir+'{}_model.r4'.format(idates[l]), 'wb')
            model.flatten().astype('float32').tofile(fid)
            fid.close()

            # save residual maps
            fid = open(outdir+'{}_res.r4'.format(idates[l]), 'wb')
            res.flatten().astype('float32').tofile(fid)
            # fid.close()


fig.suptitle('Time series models')
figres.suptitle('Time series residuals')
# figall.suptitle('Time series inversion')
fig.savefig('models.eps', format='EPS',dpi=150)
figres.savefig('residuals.eps', format='EPS',dpi=150)
# figall.savefig('timeseries.eps', format='EPS',dpi=150)
if plot=='yes':
    plt.show()
plt.close('all')

# clean memory
del maps_ramp, maps_flata, maps_topo, maps_noramps
try:
  del models_trends, model_seas
except:
  pass 

#######################################################
# Save functions in binary file
#######################################################

if geotiff is not None:
    for l in range((Mbasis)):
        outname = '{}_coeff.tif'.format(basis[l].reduction)
        logger.info('Save: {}'.format(outname))
        ds = driver.Create(outname, jend-jbeg, iend-ibeg, 1, gdal.GDT_Float32)
        band = ds.GetRasterBand(1)
        band.WriteArray(basis[l].m)
        ds.SetGeoTransform(gt)
        ds.plt.setprojection(proj)
        band.FlushCache()
        del ds

        outname = '{}_sigcoeff.tif'.format(basis[l].reduction)
        logger.info('Save: {}'.format(outname))
        ds = driver.Create(outname, jend-jbeg, iend-ibeg, 1, gdal.GDT_Float32)
        band = ds.GetRasterBand(1)
        band.WriteArray(basis[l].sigmam)
        ds.SetGeoTransform(gt)
        ds.plt.setprojection(proj)
        band.FlushCache()
        del ds

    for l in range((Mker)):
        outname = '{}_coeff.tif'.format(kernels[l].reduction)
        logger.info('Save: {}'.format(outname))
        ds = driver.Create(outname, jend-jbeg, iend-ibeg, 1, gdal.GDT_Float32)
        band = ds.GetRasterBand(1)
        band.WriteArray(kernels[l].m)
        ds.SetGeoTransform(gt)
        ds.plt.setprojection(proj)
        band.FlushCache()
        del ds

        outname = '{}_sigcoeff.tif'.format(kernels[l].reduction)
        logger.info('Save: {}'.format(outname))
        ds = driver.Create(outname, jend-jbeg, iend-ibeg, 1, gdal.GDT_Float32)
        band = ds.GetRasterBand(1)
        band.WriteArray(kernels[l].sigmam)
        ds.SetGeoTransform(gt)
        ds.plt.setprojection(proj)
        band.FlushCache()
        del ds

else:
    for l in range((Mbasis)):
        outname = '{}_coeff.r4'.format(basis[l].reduction)
        logger.info('Save: {}'.format(outname))
        fid = open(outname, 'wb')
        basis[l].m.flatten().astype('float32').tofile(fid)
        fid.close()
        outname = '{}_sigcoeff.r4'.format(basis[l].reduction)
        logger.info('Save: {}'.format(outname))
        fid = open(outname, 'wb')
        basis[l].sigmam.flatten().astype('float32').tofile(fid)
        fid.close()
    for l in range((Mker)):
        outname = '{}_coeff.r4'.format(kernels[l].reduction)
        logger.info('Save: {}'.format(outname))
        fid = open('{}_coeff.r4'.format(kernels[l].reduction), 'wb')
        kernels[l].m.flatten().astype('float32').tofile(fid)
        fid.close()
        outname = '{}_sigcoeff.r4'.format(kernels[l].reduction)
        logger.info('Save: {}'.format(outname))
        fid = open('{}_sigcoeff.r4'.format(kernels[l].reduction), 'wb')
        kernels[l].sigmam.flatten().astype('float32').tofile(fid)
        fid.close()


#######################################################
# Compute Amplitude and phase seasonal
#######################################################

if seasonal == 'yes':
    cosine = as_strided(basis[indexseas].m)
    sine = as_strided(basis[indexseas+1].m)
    amp = np.sqrt(cosine**2+sine**2)
    phi = np.arctan2(sine,cosine)

    sigcosine = as_strided(basis[indexseas].sigmam)
    sigsine = as_strided(basis[indexseas+1].sigmam)
    sigamp = np.sqrt(sigcosine**2+sigsine**2)
    sigphi = (sigcosine*abs(sine)+sigsine*abs(cosine))/(sigcosine**2+sigsine**2)

    if geotiff is not None:
        logger.info('Save: {}'.format(outname))
        ds = driver.Create('ampwt_coeff.tif', jend-jbeg, iend-ibeg, 1, gdal.GDT_Float32)
        band = ds.GetRasterBand(1)
        band.WriteArray(amp)
        ds.SetGeoTransform(gt)
        ds.plt.setprojection(proj)
        band.FlushCache()
        del ds

        logger.info('Save: {}'.format('ampwt_sigcoeff.tif'))
        ds = driver.Create('ampwt_sigcoeff.tif', jend-jbeg, iend-ibeg, 1, gdal.GDT_Float32)
        band = ds.GetRasterBand(1)
        band.WriteArray(sigamp)
        ds.SetGeoTransform(gt)
        ds.plt.setprojection(proj)
        band.FlushCache()
        del ds

    else:
        logger.info('Save: {}'.format('ampwt_coeff.r4'))
        fid = open('ampwt_coeff.r4', 'wb')
        amp.flatten().astype('float32').tofile(fid)
        fid.close()

        logger.info('Save: {}'.format('ampwt_sigcoeff.r4'))
        fid = open('ampwt_sigcoeff.r4', 'wb')
        sigamp.flatten().astype('float32').tofile(fid)
        fid.close()

    if geotiff is not None:
        logger.info('Save: {}'.format('phiwt_coeff.tif'))
        ds = driver.Create('phiwt_coeff.tif', jend-jbeg, iend-ibeg, 1, gdal.GDT_Float32)
        band = ds.GetRasterBand(1)
        band.WriteArray(phi)
        ds.SetGeoTransform(gt)
        ds.plt.setprojection(proj)
        band.FlushCache()
        del ds

        logger.info('Save: {}'.format('phiwt_sigcoeff.tif'))
        ds = driver.Create('phiwt_sigcoeff.tif', jend-jbeg, iend-ibeg, 1, gdal.GDT_Float32)
        band = ds.GetRasterBand(1)
        band.WriteArray(sigphi)
        ds.SetGeoTransform(gt)
        ds.plt.setprojection(proj)
        band.FlushCache()
        del ds

    else:
        logger.info('Save: {}'.format('phiwt_coeff.r4'))
        fid = open('phiwt_coeff.r4', 'wb')
        phi.flatten().astype('float32').tofile(fid)
        fid.close()

        logger.info('Save: {}'.format('phiwt_sigcoeff.r4'))
        fid = open('phiwt_sigcoeff.r4', 'wb')
        sigphi.flatten().astype('float32').tofile(fid)
        fid.close()

if semianual == 'yes':
    cosine = as_strided(basis[indexsemi].m)
    sine = as_strided(basis[indexsemi+1].m)
    amp = np.sqrt(cosine**2+sine**2)
    phi = np.arctan2(sine,cosine)

    sigcosine = as_strided(basis[indexseas].sigmam)
    sigsine = as_strided(basis[indexseas+1].sigmam)
    sigamp = np.sqrt(sigcosine**2+sigsine**2)
    sigphi = (sigcosine*abs(sine)+sigsine*abs(cosine))/(sigcosine**2+sigsine**2)

    if geotiff is not None:
        logger.info('Save: {}'.format('ampw2t_coeff.tif'))
        ds = driver.Create('ampw2t_coeff.tif', jend-jbeg, iend-ibeg, 1, gdal.GDT_Float32)
        band = ds.GetRasterBand(1)
        band.WriteArray(amp)
        ds.SetGeoTransform(gt)
        ds.plt.setprojection(proj)
        band.FlushCache()
        del ds

        logger.info('Save: {}'.format('ampw2t_sigcoeff.tif'))
        ds = driver.Create('ampw2t_sigcoeff.tif', jend-jbeg, iend-ibeg, 1, gdal.GDT_Float32)
        band = ds.GetRasterBand(1)
        band.WriteArray(sigamp)
        ds.SetGeoTransform(gt)
        ds.plt.setprojection(proj)
        band.FlushCache()
        del ds

    else:
        logger.info('Save: {}'.format('ampw2t_coeff.r4'))
        fid = open('ampw2t_coeff.r4', 'wb')
        amp.flatten().astype('float32').tofile(fid)
        fid.close()

        logger.info('Save: {}'.format('ampw2t_sigcoeff.r4'))
        fid = open('ampw2t_sigcoeff.r4', 'wb')
        sigamp.flatten().astype('float32').tofile(fid)
        fid.close()

    if geotiff is not None:
        logger.info('Save: {}'.format('phiw2t_coeff.tif'))
        ds = driver.Create('phiw2t_coeff.tif', jend-jbeg, iend-ibeg, 1, gdal.GDT_Float32)
        band.WriteArray(phi)
        ds.SetGeoTransform(gt)
        ds.plt.setprojection(proj)
        band.FlushCache()
        del ds

        logger.info('Save: {}'.format('phiw2t_sigcoeff.tif'))
        ds = driver.Create('phiw2t_sigcoeff.tif', jend-jbeg, iend-ibeg, 1, gdal.GDT_Float32)
        band.WriteArray(sigphi)
        ds.SetGeoTransform(gt)
        ds.plt.setprojection(proj)
        band.FlushCache()
        del ds

    else:
        logger.info('Save: {}'.format('phiw2t_coeff.r4'))
        fid = open('phiw2t_coeff.r4', 'wb')
        phi.flatten().astype('float32').tofile(fid)
        fid.close()

        logger.info('Save: {}'.format('phiw2t_sigcoeff.r4'))
        fid = open('phiw2t_sigcoeff.r4', 'wb')
        sigphi.flatten().astype('float32').tofile(fid)
        fid.close()


#######################################################
# Plot
#######################################################

# plot ref term
vmax = np.abs([np.nanpercentile(basis[0].m,98.),np.nanpercentile(basis[0].m,2.)]).max()
vmin = -vmax

nfigure +=1
fig=plt.figure(nfigure,figsize=(14,12))

ax = fig.add_subplot(1,M,1)
cax = ax.imshow(basis[0].m,cmap=cmap,vmax=vmax,vmin=vmin)
cbar = fig.colorbar(cax, orientation='vertical',shrink=0.2)
plt.setp(ax.get_xticklabels(), visible=False)
plt.setp(ax.get_yticklabels(), visible=False)

# plot linear term
vmax = np.abs([np.nanpercentile(basis[1].m,98.),np.nanpercentile(basis[1].m,2.)]).max()
vmin = -vmax

ax = fig.add_subplot(1,M,2)
cax = ax.imshow(basis[1].m,cmap=cmap,vmax=vmax,vmin=vmin)
ax.set_title(basis[1].reduction)
cbar = fig.colorbar(cax, orientation='vertical',shrink=0.2)
plt.setp(ax.get_xticklabels(), visible=False)
plt.setp(ax.get_yticklabels(), visible=False)

# plot others
for l in range(2,Mbasis):
    vmax = np.abs([np.nanpercentile(basis[l].m,98.),np.nanpercentile(basis[l].m,2.)]).max()
    vmin = -vmax

    ax = fig.add_subplot(1,M,l+1)
    cax = ax.imshow(basis[l].m,cmap=cmap,vmax=vmax,vmin=vmin)
    ax.set_title(basis[l].reduction)
    # add colorbar
    cbar = fig.colorbar(cax, orientation='vertical',shrink=0.2)
    plt.setp(ax.get_xticklabels(), visible=False)
    plt.setp(ax.get_yticklabels(), visible=False)

for l in range(Mker):
    vmax = np.abs([np.nanpercentile(kernels[l].m,98.),np.nanpercentile(kernels[l].m,2.)]).max()
    vmin = -vmax

    ax = fig.add_subplot(1,M,Mbasis+l+1)
    cax = ax.imshow(kernels[l].m,cmap=cmap,vmax=vmax,vmin=vmin)
    ax.set_title(kernels[l].reduction)
    plt.setp(ax.get_xticklabels(), visible=False)
    plt.setp(ax.get_yticklabels(), visible=False)
    cbar = fig.colorbar(cax, orientation='vertical',shrink=0.2)

plt.suptitle('Time series decomposition')

nfigure += 1
fig.tight_layout()
fig.savefig('inversion.eps', format='EPS',dpi=150)

if plot=='yes':
    plt.show()
