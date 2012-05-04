"""Sample code for calculating the ACIS FP Xija model.
"""

import xija
import Ska.engarchive.fetch_eng as fetch_eng
from Ska.Matplotlib import plot_cxctime

start = '2012:001'
stop = '2012:005'

model = xija.XijaModel('acisfp', model_spec='acisfp_spec.json',
                       start=start, stop=stop)

# Use MSID FPTEMP_11 (ACIS FP temperature DEGC) to initialize
model.comp['fptemp'].set_data(-120.0)

# These two should be initialized to the given values.  No
# direct analog is available in telemetry.  Ideally one should
# propagate the model for at least 24 hours from these starting
# points to remove startup transients.
model.comp['1cbat'].set_data(-55.0)
model.comp['sim_px'].set_data(-110.0)

# All the usual values here
model.comp['pitch'].set_data(130)
model.comp['eclipse'].set_data(False)
model.comp['sim_z'].set_data(75000)
model.comp['ccd_count'].set_data(6)
model.comp['fep_count'].set_data(6)
model.comp['vid_board'].set_data(1)
model.comp['clocking'].set_data(1)
model.comp['dpa_power'].set_data(0.0)

model.make()
model.calc()

# Note the telemetry MSID is fptemp_11 but the Node name is fptemp
fptemp_11 = fetch_eng.Msid('fptemp_11', start, stop)  # DEGC

plot_cxctime(model.times, model.comp['fptemp'].mvals, 'r-')
plot_cxctime(fptemp_11.times, fptemp_11.vals, 'b-')