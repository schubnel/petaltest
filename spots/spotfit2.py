#import multicens_v17 as multicens
# spotfitl for FLI fits files
#
import multicens2 
import pyfits
import time
import sys
import numpy as np
import matplotlib as plt

def magnitude(p,b):

	m=25.0 - 2.5*np.log10(p-b)
	return m


# the numbers below are from fvchandler
max_counts = 2**16 - 1 # SBIC camera ADU max
min_energy = 0.3 * 1.0 # this is the minimum allowed value for the product peak*fwhm for any given dot
#
arguments = sys.argv[1:]
nargs = len(arguments)
errexit=False
try:
	if nargs <1:
		errexit=True
	else:
		nspots=int(arguments[0])
	if nargs <2:
		errexit=True
	else:
		fname = arguments[1]
	if nargs >=3:
		fboxsize=int(arguments[2])
	else:
		fboxsize=7
except:
	errexit=True
if errexit:
	print("Proper use: python3 spotfit.py <n_centroids_expected> <fits_filename> <fitbox_size>")
	sys.exit()

fname_root=fname.lower()
fname_root=fname_root.rstrip('.fits')
fname_root=fname_root[-18:]		
#fname='peak_12548.4_fwhm_-0.338_sizefitbox_7.FITS'
img=pyfits.getdata(fname) 

#t0=time.time()
xCenSub, yCenSub, peaks, FWHMSub, flux, maxadu,filename =multicens2.multiCens(img, n_centroids_to_keep=nspots, verbose=False, write_fits=False,size_fitbox=fboxsize)
# we are calculating the quantity 'FWHM*peak' with peak normalized to the maximum peak level. This is
# esentially a linear light density. We will call this quantity 'energy' to match Joe's naming in fvchandler.
# We verified that the linear light density is insensitive to spot position whereas the measured peak is not.
energy=[FWHMSub[i]*(peaks[i]/max_counts) for i in range(len(peaks))]
print(" File: "+str(fname))
print(" Number of centroids requested: "+str(nspots))
print(" Fitboxsize: "+str(fboxsize))
print(" Centroid list:")  
print(" Spot  x         y          FWHM    Peak     flux  ")

# sort by peak value

sindex=sorted(range(len(peaks)), key=lambda k: peaks[k])

peaks_sorted=[peaks[i] for i in sindex]
x_sorted=[xCenSub[i] for i in sindex]
y_sorted=[yCenSub[i] for i in sindex]
fwhm_sorted=[FWHMSub[i] for i in sindex]
energy_sorted=[flux[i] for i in sindex]
maxadu_sorted=[maxadu[i] for i in sindex]
print(energy_sorted)
for i, x in enumerate(x_sorted):
	line=("{:5d} {:9.3f} {:9.3f} {:6.2f}  {:7.0f} {:7.2f} {:7.0f}".format(i, x, y_sorted[i], fwhm_sorted[i], peaks_sorted[i], energy_sorted[i], maxadu_sorted[i]))
	print(line)

print("Min peak   : {:8.2f} ".format(min(peaks_sorted)))
print("Max peak   : {:8.2f} ".format(max(peaks_sorted)))
print("Mean peak  : {:8.2f} ".format(np.mean(peaks_sorted)))
print("Sigma peak : {:8.2f} ".format(np.std(peaks_sorted)))

# write region file
with open(fname_root+'.reg','w') as fp:
	for i, x in enumerate(x_sorted):
		#print("{:5d} {:9.3f} {:9.3f} {:7.3f}   {:9.3f} {:9.3f}   {:7.3f} ".format(i, x, yCenSub[i], FWHMSub[i], peaks[i], bias[i],magnitude(peaks[i],bias[i])))
		fp.write('circle '+ "{:9.3f} {:9.3f} {:7.3f} \n".format(x+1, y_sorted[i]+1, fwhm_sorted[i]/2.))
		text='"'+str(i)+'"'
		fp.write('text '+ "{:9.3f} {:9.3f} {:s} \n".format(x+1+5, y_sorted[i]+1+5, text))
with open(fname_root+'.cen','w') as fp:
	for i, x in enumerate(x_sorted):
		line=("{:5d} {:9.3f} {:9.3f} {:6.2f}  {:7.0f} {:7.2f}  {:7.0f} ".format(i, x, y_sorted[i], fwhm_sorted[i], peaks_sorted[i], energy_sorted[i],maxadu_sorted[i]))
		fp.write(line+'\n')
#print("time: "+str(t))
