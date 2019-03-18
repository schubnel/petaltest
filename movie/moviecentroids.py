import numpy as np
import mahotas as mh
import astropy.io.fits
from astropy.io import fits
from scipy.ndimage.measurements import center_of_mass
fname='/Users/michael/Downloads/all.fits'
img=fits.getdata(fname)
def remove_hot_pixels(image,nsigma=5):
	"""
	Remove isolated hot pixels in the image. The mean value of the original image is
	calculated and a mean + nsigma threshold cut is applied. Hot pixels receive a new value of
	the average of their 4 next neighbors.
	"""
	im_mean=np.mean(image)
	im_sig=np.std(image)
	hot_thresh=im_mean+nsigma*im_sig

	hp_img = np.copy(image)
	hp_img = hp_img.astype(np.uint32)
	low_values_indices = hp_img < hot_thresh  # Where values are low
	
	hp_img[low_values_indices] = 0
	ind = zip(*np.where(hp_img > hot_thresh))
	xlimit=len(hp_img[0])
	ylimit=len(hp_img)
		
	for i in ind:
		if i[0] == 0 or i[0]==ylimit-1 or i[1]==0 or i[1]==xlimit-1:
			print('Edge hot spot')
			image[i[0],i[1]] =np.median(image)
		else:
			neighborsum=hp_img[i[0]+1,i[1]] + hp_img[i[0]-1,i[1]] + hp_img[i[0],i[1]-1] + hp_img[i[0],i[1]+1]
			if neighborsum == 0:
				image[i[0],i[1]] = (image[i[0]+1,i[1]]+image[i[0]-1,i[1]]+image[i[0],i[1]-1]+image[i[0],i[1]+1])/4.
	del hp_img        
	return image
def im2bw(image,level):
	# M.Schubnell - faking the matlab im2bw function
	s = np.shape(image)
	bw=np.zeros(s,dtype=int)
	threshold_indices = image > level
	bw[threshold_indices] = 1
	return bw

img[img<0]=0
mg=remove_hot_pixels(img,7)
no_otsu=True
level_fraction_of_peak = 0.8
level_frac = int(level_fraction_of_peak*np.max(np.max(img)))
if no_otsu:
    level = level_frac
else:
    level_otsu = mh.thresholding.otsu(img)
    level = max(level_otsu,level_frac)
bw=im2bw(img,level)

#bwf=fits.PrimaryHDU(data=bw)
#bwf.writeto('bw.fits')
n_centroids_to_keep=30
labeled, nr_objects = mh.label(bw)
sizes = mh.labeled.labeled_size(labeled) # size[0] is the background size, sizes[1 and greater] are number of pixels in each region
sorted_sizes_indexes = np.argsort(sizes)[::-1] # return in descending order
good_spot_indexes = sorted_sizes_indexes[1:n_centroids_to_keep+1] # avoiding the background regions entry at the beginning

FWHMSub = []
xCenSub = []
yCenSub = []        
peaks = []
fluxes=[]
centers = center_of_mass(labeled, labels=labeled, index=[good_spot_indexes])


nbox = 20
for i,x in enumerate(centers):
    x=x[0]
    px=int(round(x[1]))
    py=int(round(x[0]))     
    data = img[py-nbox:py+nbox,px-nbox:px+nbox]
    params = fitgaussian(data)
    fwhm=abs(2.355*max(params[4],params[5]))
    if fwhm < .5:
        print(" fit failed - trying again with smaller fitbox")
        sbox=nbox-1
        data = img[py-sbox:py+sbox,px-sbox:px+sbox]
        params = fitgaussian(data)
        fwhm=abs(2.355*max(params[4],params[5]))
    xCenSub.append(float(px)-float(nbox)+params[3])
    yCenSub.append(float(py)-float(nbox)+params[2])
    FWHMSub.append(fwhm)

    #flux=np.sum(data)-len(data)*dbias
    #print("***",flux,dbias*len(data))
    #fluxes.append(flux)
    peak = params[1]
    peaks.append(peak)

sindex=sorted(range(len(peaks)), key=lambda k: peaks[k])

peaks_sorted=[peaks[i] for i in sindex]
x_sorted=[xCenSub[i] for i in sindex]
y_sorted=[yCenSub[i] for i in sindex]
fwhm_sorted=[FWHMSub[i] for i in sindex]

#return xCenSub, yCenSub, peaks, FWHMSub, fluxes, filename
with open('region.reg','w') as fp:
    for i, x in enumerate(x_sorted):
        #print("{:5d} {:9.3f} {:9.3f} {:7.3f}   {:9.3f} {:9.3f}   {:7.3f} ".format(i, x, yCenSub[i], FWHMSub[i], peaks[i], bias[i],magnitude(peaks[i],bias[i])))
        fp.write('circle '+ "{:9.3f} {:9.3f} {:7.3f} \n".format(x+1, y_sorted[i]+1, fwhm_sorted[i]/2.))
        text='"'+str(i)+'"'
        fp.write('text '+ "{:9.3f} {:9.3f} {:s} \n".format(x+1+5, y_sorted[i]+1+5, text))

print('done')