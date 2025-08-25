# inverse-index-astr
This python script allows the user to take in light curve data and create an inverse index of said light curves. This binning process is based off of the highest associated peaks taken from the lomb-scargle ACF.

## Python Requirementes 
This code was run using command python3.7. It has not been tested on any other version of python although using python3 should suffice. Astropy is needed for the Lomb-Scargle method used.  

## Notes
This script uses the top 4 peaks associated with its Lomb-Scargle ACF. It is discretized to the hundredth decimal point. This can be changed to third if desired for further binning. 
