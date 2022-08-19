# Libraries
from datetime import datetime
from metpy.units import units
from siphon.simplewebservice.wyoming import WyomingUpperAir
import matplotlib.pyplot as plt
from matplotlib import gridspec
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import pandas as pd
import numpy as np
import warnings
import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.plots import Hodograph, SkewT
from metpy.units import units

warnings.filterwarnings('ignore')


print('==== WYOMING SOUNDINGS SEARCH TOOL ====')

def main():
    # User input is stored in 'date' and 'station' variables
    u = str(input('Enter station:'))
    f = str(input('Enter date (DD-MM-YYYY):'))
    t = int(input('Enter time (XXz):'))
    
    date = datetime(int(f[6:10]), int(f[3:5]), int(f[0:2]), t)  
    station = u

    df = WyomingUpperAir.request_data(date, station) # Search for sounding (output class is data frame)
    df = df.dropna(subset=('temperature', 'dewpoint', 'direction', 'speed'), how='all').reset_index(drop=True) # NA removal

# Data extraction and units assignment
    p = df['pressure'].values * units.hPa
    T = df['temperature'].values * units.degC
    Td = df['dewpoint'].values * units.degC
    wind_speed = df['speed'].values * units.knots
    wind_dir = df['direction'].values * units.degrees
    u, v = mpcalc.wind_components(wind_speed, wind_dir)
    z = df['height'].values * units.meters

# Parcel trajectory calculation
    parcel_prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')

# Levels and parameters
    lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], Td[0])
    lfc_pressure, lfc_temperature = mpcalc.lfc(p,T,Td)
    lel_pressure, lel_temperature = mpcalc.el(p,T,Td)
    sb_cape, sb_cin = mpcalc.surface_based_cape_cin(p, T, Td)
    ml_cape, ml_cin = mpcalc.mixed_layer_cape_cin(p, T, Td)
    mu_cape, mu_cin = mpcalc.most_unstable_cape_cin(p, T, Td)
    mu_parcel = mpcalc.most_unstable_parcel(p,T,Td)
    pwat = mpcalc.precipitable_water(p,Td)

# Wind shear
    u_shear01, v_shear01 = mpcalc.bulk_shear(p, u, v, depth = 1000 * units.meter)
    shear01 = np.round((np.sqrt(u_shear01**2 + v_shear01**2)), 1)
    u_shear06, v_shear06 = mpcalc.bulk_shear(p, u, v, depth = 6000 * units.meter)
    shear06 = np.round((np.sqrt(u_shear06**2 + v_shear06**2)), 1)

# Hide wind barbs above 105 hPa (to avoid overlapping w/title)
    mask = p > 105*units.hPa

# Figure
    fig = plt.figure(figsize=(11,11))
    gs = gridspec.GridSpec(3,3)
    skew = SkewT(fig, rotation=45, subplot=gs[:,:2])

    skew.plot(p, T, 'r')
    skew.plot(p, Td, 'g')
    skew.plot_barbs(p[mask], u[mask], v[mask], y_clip_radius = 0.03)
    skew.ax.set_ylim(1020, 100)
    skew.ax.set_xlim(-50, 50)
    skew.ax.set_ylabel('Pressure [hPa]')
    skew.ax.set_xlabel('Temperature [deg_c]')

# Titles
    plt.title('{} Sounding'.format(station), loc='left', size = 'medium')
    plt.title('Valid Time: {}'.format(date), loc='right',size = 'medium')

# Plot levels and parcel trajectory 
    skew.plot(p, parcel_prof, 'k', linewidth=2)
    skew.plot(lcl_pressure, lcl_temperature, 'ko', markerfacecolor='black')
    skew.plot(lfc_pressure, lfc_temperature, 'ko', markerfacecolor='black')
    skew.plot(lel_pressure, lel_temperature, 'ko', markerfacecolor='black')

# Plot zero degree isotherm (dashed line)
    skew.ax.axvline(0, color='c', linestyle='--', linewidth=2)

# Contour lines (dry and moist adiabats, mixing ratio)
    skew.plot_dry_adiabats(alpha=0.25, color = 'orangered')
    skew.plot_moist_adiabats(alpha=0.25, color = 'tab:green')
    skew.plot_mixing_lines(linestyle='dotted', color = 'tab:blue')

# Hodograph parameters 
    mask_2 = z < 10*units.km # Heights lower than 10 km 
    intervals = np.array([0, 1, 3, 5, 10]) * units.km # Intervals
    colors = ['red', 'lime', 'green', 'darkviolet'] # Color scale

# Hodograph
    ax1 = fig.add_subplot(gs[0,-1])
    h = Hodograph(ax1, component_range=50.)
    h.add_grid(increment=10)
    h.plot_colormapped(u[mask_2], v[mask_2], z[mask_2], intervals = intervals, colors = colors)

# Weather station info
    lat = float(np.unique(df['latitude']))
    lon = float(np.unique(df['longitude']))
    elv = float(np.unique(df['elevation']))* units.meters

# Show sounding info
    plt.figtext( 0.65, 0.58, 'Latitude:',size = 'small')
    plt.figtext( 0.8, 0.58, f'{lat}',size = 'small')
    plt.figtext( 0.65, 0.56, 'Longitude:',size = 'small')
    plt.figtext( 0.8, 0.56, f'{lon}',size = 'small')
    plt.figtext( 0.65, 0.54, 'Height ASL:',size = 'small')
    plt.figtext( 0.8, 0.54, f'{elv}',size = 'small')
    plt.figtext( 0.65, 0.52, 'LCL:', size = 'small')
    plt.figtext( 0.8, 0.52, f'{np.round(lcl_pressure,1):~P}',size = 'small')
    plt.figtext( 0.65, 0.50, 'LFC:', size = 'small')
    plt.figtext( 0.8, 0.50, f'{np.round(lfc_pressure,1):~P}',size = 'small')
    plt.figtext( 0.65, 0.48, 'EL:',size = 'small')
    plt.figtext( 0.8, 0.48, f'{np.round(lel_pressure,1):~P}',size = 'small')
    plt.figtext( 0.65, 0.46, 'Most unstable parcel:',size = 'small')
    plt.figtext( 0.8, 0.46, f'{np.round(mu_parcel[0],1):~P}',size = 'small')
    plt.figtext( 0.65, 0.44, 'MUCAPE:',size = 'small')
    plt.figtext( 0.8, 0.44, f'{np.round(mu_cape,1):~P}',size = 'small')
    plt.figtext( 0.65, 0.42, 'MUCIN:',size = 'small')
    plt.figtext( 0.8, 0.42, f'{np.round(mu_cin,1):~P}',size = 'small')
    plt.figtext( 0.649, 0.40, 'SBCAPE:',size = 'small')
    plt.figtext( 0.8, 0.40, f'{np.round(sb_cape,1):~P}',size = 'small')
    plt.figtext( 0.649, 0.38, 'SBCIN:',size = 'small')
    plt.figtext( 0.8, 0.38, f'{np.round(sb_cin,1):~P}',size = 'small')
    plt.figtext( 0.65, 0.36, 'MLCAPE:',size = 'small')
    plt.figtext( 0.8, 0.36, f'{np.round(ml_cape,1):~P}',size = 'small')
    plt.figtext( 0.65, 0.34, 'MLCIN:',size = 'small')
    plt.figtext( 0.8, 0.34, f'{np.round(ml_cin,1):~P}',size = 'small')
    plt.figtext( 0.65, 0.32, 'Shear (0-1 km):',size = 'small')
    plt.figtext( 0.8, 0.32, f'{np.round(shear01,1):~P}',size = 'small')
    plt.figtext( 0.65, 0.30, 'Shear (0-6 km):',size = 'small')
    plt.figtext( 0.8, 0.30, f'{np.round(shear06,1):~P}',size = 'small')
    plt.figtext( 0.65, 0.28, 'Precipitable water:',size = 'small')
    plt.figtext( 0.8, 0.28, f'{np.round(pwat,1):~P}',size = 'small')

# Plot sounding
    plt.show()

while True: # Prevents script from closing after execution has finished (user must terminate manually with Ctrl-C)
    print(' ')
    main()