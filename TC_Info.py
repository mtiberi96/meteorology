# Script for querying tropical cyclones
# Gives information about trajectory, intensity, maximum intensity and ACE

# Libraries
import tropycal.tracks as tracks 
import warnings

warnings.filterwarnings('ignore')

def data(x,y):
     storm = hurdat_atl.get_storm((x,y)) # Looks for selected tropical cyclone and stores it in 'storm' variable
     storm.plot(map_prop={'dpi':90,'linewidth':1.0}) # Plot figure

v = ['north_atlantic','both','east_pacific','west_pacific','north_indian','south_indian'] # Basins list

print('==== TROPICAL CYCLONE QUERY TOOL (HURDAT/IBTRACS) ====')
print(' ')
print('<<Select a basin>>')  
print(' ')   
print('0 - North Atlantic') 
print('1 - North Atlantic + East/Central Pacific (2019 and older)')
print('2 - East/Central Pacific')
print('3 - West Pacific')
print('4 - North Indian Ocean')
print('5 - South Indian Ocean')
print(' ')
select = int(input('Choose an option:'))

for i in range(0,3):
	if select == i:
		hurdat_atl = tracks.TrackDataset(basin=v[i],source='hurdat',include_btk=True) # For options 0, 1 and 2
for n in range(3,6):
    if select == n:
        hurdat_atl = tracks.TrackDataset(basin=v[n],source='ibtracs',include_btk=True) # For options 3, 4 and 5

def repeat():
    data(input('Enter name:'),int(input('Enter year of ocurrence:'))) # User enters name and year of event and obtains the plot
while True:
    repeat()
