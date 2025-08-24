import pandas as pd
import os 
import csv
from astropy.timeseries import LombScargle
import numpy as np
class group_inverse:
	def __init__(self):	
		self.base_directory='/home/perkeys/inverse_index/1_5KZTFlc/'
		self.df_ZTF_quas=[]	
		self.periodogram_sep=[]
		self.period_sorted_percsv=[]
		self.list_full=[]

	def read_in_csv(self):
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
		# I lowkey think we dont even need this but lets just put it here for now: data_file_tup=(self.df_ZTF_quas,self.list_clean)

	def create_indexed_csv(self):	

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
				# do this later
			except Exception as e:
				print(f'Error processing {self.all_files[i]}: {str(e)}' )
		print(freq)
		path_clean_g15=[strng for i,strng in enumerate(list_clean) if i not in indeces_to_remove]
		file_clean_g15=[os.path.basename(path) for path in path_clean_g15]
		second_dec_4tpwr=[[round(x,2) for x in sublist] for sublist in self.period_sorted_percsv]	
		# we have discretized it to the second decimal place
		transpose_write=list(zip(*self.period_sorted_percsv))
		rows=[file_clean_g15]+[list(row) for row in transpose_write]
		with open('rounded_power_ZTF.csv','w',newline='')as csvfile:
			writer=csv.writer(csvfile)
			writer.writerows(rows)

Group=group_inverse()
#I.read_in_csv()	
#Inverse.create_indexed_csv()
