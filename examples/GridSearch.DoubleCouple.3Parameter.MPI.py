#!/usr/bin/env python

import os
import sys
import numpy as np

from os.path import basename, join
from mtuq.dataset import sac
from mtuq.greens_tensor import syngine
from mtuq.grid_search import DoubleCoupleGridRandom
from mtuq.grid_search import grid_search_mpi
from mtuq.misfit.cap import Misfit
from mtuq.process_data.cap import ProcessData
from mtuq.util.cap_util import remove_unused_stations, trapezoid_rise_time, Trapezoid
from mtuq.util.plot import plot_beachball, plot_data_greens_mt
from mtuq.util.util import cross, path_mtuq



if __name__=='__main__':
    #
    # Double-couple inversion example
    # 
    # Carries out grid search over 50,000 randomly chosen double-couple 
    # moment tensors
    #
    # USAGE
    #   mpirun -n <NPROC> python GridSearch.DoubleCouple.3Parameter.py
    #
    # For a slightly simpler example, see 
    # GridSearch.DoubleCouple.3Parameter.Serial.py, 
    # which runs the same inversion in serial rather than parallel
    #


    #
    # Here we specify the data used for the inversion. The event is an 
    # Mw~4 Alaska earthquake
    #

    path_data=    join(path_mtuq(), 'data/examples/20090407201255351')
    path_weights= join(path_mtuq(), 'data/examples/20090407201255351/weights.dat')
    path_picks=   join(path_mtuq(), 'data/examples/20090407201255351/picks.dat')
    event_name=   '20090407201255351'
    model=        'ak135f_2s'


    #
    # Body- and surface-wave data are processed separately and held separately 
    # in memory
    #

    process_bw = ProcessData(
        filter_type='Bandpass',
        freq_min= 0.1,
        freq_max= 0.333,
        pick_type='from_pick_file',
        pick_file=path_picks,
        window_type='cap_bw',
        window_length=15.,
        padding_length=2.,
        weight_type='cap_bw',
        cap_weight_file=path_weights,
        )

    process_sw = ProcessData(
        filter_type='Bandpass',
        freq_min=0.025,
        freq_max=0.0625,
        pick_type='from_pick_file',
        pick_file=path_picks,
        window_type='cap_sw',
        window_length=150.,
        padding_length=10.,
        weight_type='cap_sw',
        cap_weight_file=path_weights,
        )

    process_data = {
       'body_waves': process_bw,
       'surface_waves': process_sw,
       }


    #
    # We define misfit as a sum of indepedent body- and surface-wave 
    # contributions
    #

    misfit_bw = Misfit(
        time_shift_max=2.,
        time_shift_groups=['ZR'],
        )

    misfit_sw = Misfit(
        time_shift_max=10.,
        time_shift_groups=['ZR','T'],
        )

    misfit = {
        'body_waves': misfit_bw,
        'surface_waves': misfit_sw,
        }


    #
    # Next we specify the source parameter grid
    #

    grid = DoubleCoupleGridRandom(
        npts=50000,
        Mw=4.5)

    rise_time = trapezoid_rise_time(Mw=4.5)
    wavelet = Trapezoid(rise_time)



    from mpi4py import MPI
    comm = MPI.COMM_WORLD


    #
    # The main I/O work starts now
    #

    if comm.rank==0:
        print 'Reading data...\n'
        data = sac.reader(path_data, wildcard='*.[zrt]', id=event_name,
            tags=['cm', 'velocity']) 
        remove_unused_stations(data, path_weights)
        data.sort_by_distance()

        stations  = []
        for stream in data:
            stations += [stream.meta]
        origin = data.get_origin()

        print 'Processing data...\n'
        processed_data = {}
        for key in ['body_waves', 'surface_waves']:
            processed_data[key] = data.map(process_data[key])
        data = processed_data

        print 'Reading Greens functions...\n'
        factory = syngine.GreensTensorFactory(model)
        greens = factory(stations, origin)

        print 'Processing Greens functions...\n'
        greens.convolve(wavelet)
        processed_greens = {}
        for key in ['body_waves', 'surface_waves']:
            processed_greens[key] = greens.map(process_data[key])
        greens = processed_greens

    else:
        data = None
        greens = None

    data = comm.bcast(data, root=0)
    greens = comm.bcast(greens, root=0)


    #
    # The main computational work starts now
    #

    if comm.rank==0:
        print 'Carrying out grid search...\n'
    results = grid_search_mpi(data, greens, misfit, grid)
    results = comm.gather(results, root=0)


    if comm.rank==0:
        print 'Saving results...\n'
        results = np.concatenate(results)
        #grid.save(event_name+'.h5', {'misfit': results})
        best_mt = grid.get(results.argmin())


    if comm.rank==0:
        print 'Plotting waveforms...\n'
        plot_data_greens_mt(event_name+'.png', data, greens, best_mt, misfit)
        plot_beachball(event_name+'_beachball.png', best_mt)


