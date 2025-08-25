import pandas as pd
import os 
import csv
from astropy.timeseries import LombScargle
import numpy as np
class inverse:
	def __init__(self):	
		"""
		Inverse index for ZTF quasar light curves.
		
		This class is made such that ZTF (Zwicky Transient Facility) quasar data is process and binned based off of Lomb-Scargle periodogram power values.

		Attributes:
			base_directory (str): Path to directory containing ZTF CSV files
			df_ZTF_quas (list): List of loaded DataFrame objects
			periodogram_sep (list): Storage for frequency and power arrays (unused)
			period_sorted_percsv (list): Top 4 power values for each light curve
			list_full (list): List of all successfully processed file paths
				
		"""
		self.base_directory='/home/perkeys/inverse_index/1_5KZTFlc/'
		self.df_ZTF_quas=[]	
		self.periodogram_sep=[]
		self.period_sorted_percsv=[]
		self.list_full=[]

	def read_in_csv(self):
		"""	
		Read and validate all CSV files in the base directory.
		Iterates through all CSV files in the specified directory, attempts to read each one as a pandas DataFrame, and stores valid files for further processing.
		Skips empty files and files that cannot be parsed.
		Raises:
			pd.errors.EmptyDataError: If a CSV file is empty
			Exception: For any other file reading errors
		"""
		ztf_csv=os.listdir(self.base_directory)
		self.all_files=[self.base_directory+x for x in ztf_csv ] 
		for file in self.all_files:
			try: 
				df=pd.read_csv(file)
				if not df.empty:
					self.list_full.append(file)
					self.df_ZTF_quas.append(df)
			except (pd.errors.EmptyDataError, Exception) as e:
				print(f'Skipping {file}; {str(e)}')
				continue

	def create_indexed_csv(self):	
		"""
		Create indexed CSV with Lomb-Scargle periodogram analysis results.
		Processes each light curve to compute Lomb-Scargle periodograms and extracts the top 4 power values. Filters out light curves with insufficient data points (<15 measurements). Outputs a CSV file with discretized power values.
		Output File: rounded_power_ZTF.csv
        	File Format: First row contains filenames, subsequent rows contain top 4 power values
		Raises:
			Exception: If Lomb-Scargle computation fails for any file
		"""
		mask=[i for i,df in enumerate(self.df_ZTF_quas) if not df.empty]	
		list_clean=[self.list_full[i] for i in mask]
		indeces_to_remove=[]	
		for i in mask: 
			try:
				
				current_df=self.df_ZTF_quas[i]
				time=current_df['mjd'].values			
				magnitude=current_df['mag'].values
				

				if len(time)<15:
					print(f'Skipping {self.list_full[i]}, at index {i}, because there is less than 15 measurements to analyze')
					indeces_to_remove.append(i)
					continue
				ls=LombScargle(time,magnitude)
				freq,power=ls.autopower()
				top4_power=sorted(power,reverse=True)[:4]
				self.period_sorted_percsv.append(top4_power)
				#self.periodogram_sep.append((freq,power))
				# above is if for whateve reason we want to keep the frequency and power for plotting
			except Exception as e:
				print(f'Error processing {self.all_files[i]}: {str(e)}' )
		path_clean_g15=[strng for i,strng in enumerate(list_clean) if i not in indeces_to_remove]
		file_clean_g15=[os.path.basename(path) for path in path_clean_g15]
		second_dec_4tpwr=[[round(x,2) for x in sublist] for sublist in self.period_sorted_percsv]	
		# we have discretized it to the second decimal place
		
		transpose_write=list(zip(*second_dec_4tpwr))
		rows=[file_clean_g15]+[list(row) for row in transpose_write]
		with open('rounded_power_ZTF.csv','w',newline='')as csvfile:
			writer=csv.writer(csvfile)
			writer.writerows(rows)

	def create_binned_csv(self):
		"""
		Create binned inverse index based on discretized power values.
		Reads the output from create_indexed_csv() and creates an inverse index that groups files by their power values. Each bin contains all files that share the same discretized power value.

		Output File: binned_inverse_index.csv
		File Format: Each row contains a power value and list of files with that value

		Note: It is not tolerance based, it is just matching indeces 


		"""
		all_data=pd.read_csv('rounded_power_ZTF.csv')
		file_names=all_data.columns
		power_values=all_data.values
		power_per_col=list(zip(*power_values))	

		flattened_pv=power_values.flatten()
		singular_fpv=np.unique(flattened_pv)
	
		tolerance=1e-10
		all_indeces_vals=[]
		for val in singular_fpv:

			#matching_indeces=[idx for idx, tup in enumerate(power_per_col) if any(abs(x-val)<tolerance for x in tup)]
			all_indeces_vals.append([idx for idx, tup in enumerate(power_per_col) if any(abs(x-val)<tolerance for x in tup)])
	
		#below gives the index using enumerate that gives us the 
		#binned_filesnames gives us the binned within the matching index following the target_value

		full_binned_files=[]
		for l_list in all_indeces_vals: 
			full_binned_files.append([file_names[x] for x in l_list])	

		full_bcsv = list(zip(*(singular_fpv,full_binned_files)))
		# this is per rows binning

		with open('binned_inverse_index.csv','w',newline='') as csvfile:
			writer=csv.writer(csvfile)
			writer.writerows(full_bcsv)
	
Inverse=inverse()
Inverse.read_in_csv()	
Inverse.create_indexed_csv()
Inverse.create_binned_csv()
#TODO: like a million things, there is many ways this can be improved but I like it for what it is now in terms of a first go.
