

Imports="""
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
from mtuq.util.cap_util import trapezoid_rise_time, Trapezoid
from mtuq.util.plot import plot_beachball, plot_waveforms
from mtuq.util.util import cross, root


"""


DocstringDC3Serial="""
if __name__=='__main__':
    #
    # Double-couple inversion example
    # 
    # Carries out grid search over 50,000 randomly chosen double-couple 
    # moment tensors
    #
    # USAGE
    #   python GridSearch.DoubleCouple.3Parameter.Serial.py
    #
    # A typical runtime is about 60 minutes. For faster results try 
    # GridSearch.DoubleCouple.3Parameter.py,
    # which runs the same inversion in parallel rather than
    # serial
    #

"""


DocstringDC3="""
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

"""


DocstringDC5="""
if __name__=='__main__':
    #
    # Double-couple inversion example
    #   
    # Carries out grid search over source orientation, magnitude and depth
    #   
    # USAGE
    #   mpirun -n <NPROC> python GridSearch.DoubleCouple.5Parameter.py
    #   

"""


DocstringFMT5="""
if __name__=='__main__':
    #
    # Full moment tensor inversion example
    #   
    # Carries out grid search over all moment tensor parameters except
    # magnitude 
    #
    # USAGE
    #   mpirun -n <NPROC> python GridSearch.FullMomentTensor.5Parameter.py
    #   

"""


DocstringBenchmarkCAPFK="""
if __name__=='__main__':
    #
    # Given four "fundamental" moment tensor, generates MTUQ synthetics and
    # compares with corresponding CAP/FK synthetics
    #
    # This script is similar to examples/GridSearch.DoubleCouple3.Serial.py,
    # except here we consider only four grid points rather than an entire
    # grid, and here the final plots are a comparison of MTUQ and CAP/FK 
    # synthetics rather than a comparison of data and synthetics
    #
    # The CAP/FK synthetics used for the comparison were generated by the 
    # following commands
    #

    # explosion source:
    # cap.pl -H0.02 -P1/15/60 -p1 -S2/10/0 -T15/150 -D1/1/0.5 -C0.1/0.333/0.025/0.0625 -Y1 -Zweight_test.dat -Mscak_34 -m4.5 -I1 -R0/1.178/90/0.707/90 20090407201255351

    # double-couple source #1:
    # cap.pl -H0.02 -P1/15/60 -p1 -S2/10/0 -T15/150 -D1/1/0.5 -C0.1/0.333/0.025/0.0625 -Y1 -Zweight_test.dat -Mscak_34 -m4.5 -I1 -R0/0/90/0/90 20090407201255351

    # double-couple source #2:
    # cap.pl -H0.02 -P1/15/60 -p1 -S2/10/0 -T15/150 -D1/1/0.5 -C0.1/0.333/0.025/0.0625 -Y1 -Zweight_test.dat -Mscak_34 -m4.5 -I1 -R0/0/90/1/0 20090407201255351

    # double-couple source #3:
    # cap.pl -H0.02 -P1/15/60 -p1 -S2/10/0 -T15/150 -D1/1/0.5 -C0.1/0.333/0.025/0.0625 -Y1 -Zweight_test.dat -Mscak_34 -m4.5 -I1 -R0/0/0/0/180 2009040720125535


    path_ref = []
    path_ref += '/home/rmodrak/projects/mtuq/OUTPUT_DIR0'
    path_ref += '/home/rmodrak/projects/mtuq/OUTPUT_DIR1'
    path_ref += '/home/rmodrak/projects/mtuq/OUTPUT_DIR2'
    path_ref += '/home/rmodrak/projects/mtuq/OUTPUT_DIR3'
"""


DocstringIntegrationTest="""
if __name__=='__main__':
    #
    #
    # This script is similar to examples/GridSearch.DoubleCouple3.Serial.py,
    # except here we use a coarser grid, and at the end we assert that the test
    # result equals the expected result
    #
    # The compare against CAP/FK:
    # cap.pl -H0.02 -P1/15/60 -p1 -S2/10/0 -T15/150 -D1/1/0.5 -C0.1/0.333/0.025/0.0625 -Y1 -Zweight_test.dat -Mscak_34 -m4.3 -I20 -R0/0/0/0/0/360/0/1/-90/90 20090407201255351

"""


PathsComments="""
    #
    # Here we specify the data used for the inversion. The event is an 
    # Mw~4 Alaska earthquake
    #
"""


PathsDefinitions="""
    path_data=    join(root(), 'data/examples/20090407201255351')
    path_weights= join(root(), 'data/examples/20090407201255351/weights.dat')
    # Fow now this path exists only in my personal environment.  Eventually, 
    # we need to include it in the repository or make it available for download
    path_greens=  join(os.getenv('CENTER1'), 'data/wf/FK_SYNTHETICS/scak')
    event_name = '20090407201255351'

"""


DataProcessingComments="""
    #
    # Body- and surface-wave data are processed separately and held separately 
    # in memory
    #
"""


DataProcessingDefinitions="""
    process_bw = ProcessData(
        filter_type='Bandpass',
        freq_min= 0.1,
        freq_max= 0.333,
        pick_type='from_fk_database',
        fk_database=path_greens,
        window_type='cap_bw',
        window_length=15.,
        padding_length=2.,
        weight_type='cap_bw',
        weight_file=path_weights,
        )

    process_sw = ProcessData(
        filter_type='Bandpass',
        freq_min=0.025,
        freq_max=0.0625,
        pick_type='from_fk_database',
        fk_database=path_greens,
        window_type='cap_sw',
        window_length=150.,
        padding_length=10.,
        weight_type='cap_sw',
        weight_file=path_weights,
        )

    process_data = {
       'body_waves': process_bw,
       'surface_waves': process_sw,
       }

"""


MisfitComments="""
    #
    # We define misfit as a sum of indepedent body- and surface-wave 
    # contributions
    #
"""


MisfitDefinitions="""
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

"""


GridDC3="""
    #
    # Next we specify the source parameter grid
    #

    grid = DoubleCoupleGridRandom(
        npts=50000,
        Mw=4.5)

    rise_time = trapezoid_rise_time(Mw=4.5)
    wavelet = Trapezoid(rise_time)


"""


GridDC5="""
    #
    # Next we specify the source parameter grid
    #

    grid = DoubleCoupleGridRandom(
        npts=50000,
        Mw=4.5)

    origins = OriginGrid(depth=np.arange(2500.,20000.,2500.),
        latitude=origin.latitude,
        longitude=origin.longitude)

    rise_time = trapezoid_rise_time(Mw=4.5)
    wavelet = Trapezoid(rise_time)

"""


GridFMT5="""
    #
    # Next we specify the source parameter grid
    #

    grid = FullMomentTensorGridRandom(
        npts=1000000,
        Mw=4.5)

    rise_time = trapezoid_rise_time(Mw=4.5)
    wavelet = Trapezoid(rise_time)

"""


GridBenchmarkCAPFK="""
    #
    # Next we specify the source parameter grid
    #

    grid = [
       # Mrr, Mtt, Mpp, Mrt, Mrp, Mtp
       np.array([1., 1., 1., 0., 0., 0.]), # explosion
       np.array([0., 0., 0., 1., 0., 0.])  # double-couple #1
       np.array([0., 0., 0., 0., 1., 0.])  # double-couple #2
       np.array([0., 0., 0., 0., 0., 1.])  # double-couple #2
       ]

    rise_time = trapezoid_rise_time(Mw=4.5)
    wavelet = Trapezoid(rise_time)

"""


GridIntegrationTest="""
    grid = DoubleCoupleGridRegular(Mw=4.5, npts_per_axis=10)
    rise_time = trapezoid_rise_time(Mw=4.5)
    wavelet = Trapezoid(rise_time)
"""




GridSearchSerial="""
    #
    # The main I/O work starts now
    #

    print 'Reading data...\\n'
    data = sac.reader(path_data, wildcard='*.[zrt]')
    data.add_tag('velocity')
    data.sort_by_distance()

    stations  = []
    for stream in data:
        stations += [stream.meta]
    origin = data.get_origin()


    print 'Processing data...\\n'
    processed_data = {}
    for key in ['body_waves', 'surface_waves']:
        processed_data[key] = data.map(process_data[key])
    data = processed_data


    print 'Reading Greens functions...\\n'
    factory = syngine.GreensTensorFactory('ak135f_5s')
    greens = factory(stations, origin)


    print 'Processing Greens functions...\\n'
    greens.convolve(wavelet)
    processed_greens = {}
    for key in ['body_waves', 'surface_waves']:
        processed_greens[key] = greens.map(process_data[key])
    greens = processed_greens


    #
    # The main computational work starts nows
    #

    print 'Carrying out grid search...\\n'
    results = grid_search_serial(data, greens, misfit, grid)


    print 'Saving results...\\n'
    #grid.save(event_name+'.h5', {'misfit': results})
    best_mt = grid.get(results.argmin())


    print 'Plotting waveforms...\\n'
    synthetics = {}
    for key in ['body_waves', 'surface_waves']:
        synthetics[key] = greens[key].get_synthetics(best_mt)
    plot_waveforms(event_name+'.png', data, synthetics, misfit)
    plot_beachball(event_name+'_beachball.png', best_mt)


"""



GridSearchMPI="""
    from mpi4py import MPI
    comm = MPI.COMM_WORLD


    #
    # The main I/O work starts now
    #

    if comm.rank==0:
        print 'Reading data...\\n'
        data = sac.reader(path_data, wildcard='*.[zrt]')
        data.add_tag('velocity')
        data.sort_by_distance()

        stations  = []
        for stream in data:
            stations += [stream.meta]
        origin = data.get_origin()

        print 'Processing data...\\n'
        processed_data = {}
        for key in ['body_waves', 'surface_waves']:
            processed_data[key] = data.map(process_data[key])
        data = processed_data

        print 'Reading Greens functions...\\n'
        factory = syngine.GreensTensorFactory('ak135f_5s')
        greens = factory(stations, origin)

        print 'Processing Greens functions...\\n'
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
        print 'Carrying out grid search...\\n'
    results = grid_search_mpi(data, greens, misfit, grid)
    results = comm.gather(results, root=0)


    if comm.rank==0:
        print 'Saving results...\\n'
        results = np.concatenate(results)
        #grid.save(event_name+'.h5', {'misfit': results})
        best_mt = grid.get(results.argmin())


    if comm.rank==0:
        print 'Plotting waveforms...\\n'
        synthetics = {}
        for key in ['body_waves', 'surface_waves']:
            synthetics[key] = greens[key].get_synthetics(best_mt)
        plot_waveforms(event_name+'.png', data, synthetics, misfit)
        plot_beachball(event_name+'_beachball.png', best_mt)


"""



GridSearchMPI2="""
    #
    # The main work of the grid search starts now
    #
    from mpi4py import MPI
    comm = MPI.COMM_WORLD


    if comm.rank==0:
        print 'Reading data...\\n'
        data = sac.reader(path_data, wildcard='*.[zrt]')
        data.add_tag('velocity')
        data.sort_by_distance()

        stations  = []
        for stream in data:
            stations += [stream.meta]
        origin = data.get_origin()

        print 'Processing data...\\n'
        processed_data = {}
        for key in ['body_waves', 'surface_waves']:
            processed_data[key] = data.map(process_data[key])
        data = processed_data
    else:
        data = None

    data = comm.bcast(data, root=0)


   for origin, magnitude in cross(origins, magnitudes):
        if comm.rank==0:
            print 'Reading Greens functions...\\n'
            factory = syngine.GreensTensorFactory('ak135f_5s')
            greens = factory(stations, origin)

            print 'Processing Greens functions...\\n'
            rise_time = trapezoid_rise_time(magnitude)
            wavelet = Trapezoid(rise_time)
            greens.convolve(wavelet)

            processed_greens = {}
            for key in ['body_waves', 'surface_waves']:
                processed_greens[key] = greens.map(process_data[key])
            greens = processed_greens

        else:
            greens = None

        greens = comm.bcast(greens, root=0)


        if comm.rank==0:
            print 'Carrying out grid search...\\n'
        results = grid_search_mpi(data, greens, misfit, grid)
        results = comm.gather(results, root=0)


        if comm.rank==0:
            print 'Saving results...\\n'
            results = np.concatenate(results)
            #grid.save(event_name+'.h5', {'misfit': results})


        if comm.rank==0:
            print 'Plotting waveforms...\\n'
            synthetics = {}
            for key in ['body_waves', 'surface_waves']:
                synthetics[key] = greens[key].get_synthetics(best_mt)
            plot_waveforms(event_name+'.png', data, synthetics, misfit)
            plot_beachball(event_name+'_beachball.png', best_mt)



"""


RunBenchmarkCAPFK="""
    #
    # The benchmark starts now
    #

    print 'Reading data...\\n'
    data = sac.reader(path_data, wildcard='*.[zrt]')
    data.add_tag('velocity')
    data.sort_by_distance()

    stations  = []
    for stream in data:
        stations += [stream.meta]
    origin = data.get_origin()


    print 'Processing data...\\n'
    processed_data = {}
    for key in ['body_waves', 'surface_waves']:
        processed_data[key] = data.map(process_data[key])
    data = processed_data


    print 'Reading Greens functions...\\n'
    factory = syngine.GreensTensorFactory('ak135f_5s')
    greens = factory(stations, origin)

    print 'Processing Greens functions...\\n'
    greens.convolve(wavelet)
    processed_greens = {}
    for key in ['body_waves', 'surface_waves']:
        processed_greens[key] = greens.map(process_data[key])
    greens = processed_greens

    print 'Plotting waveforms...'
    from copy import deepcopy
    from mtuq.util.cap_util import get_synthetics_cap, get_synthetics_mtuq
    from mtuq.util.cap_util import get_data_cap

    for _i, mt in enumerate(grid):
        print ' %d of %d' % (_i+1, grid.size+1)
        synthetics_cap = get_synthetics_cap(deepcopy(data), path_ref[_i])
        synthetics_mtuq = get_synthetics_mtuq(greens, mt)
        filename = 'cap_fk_'+str(_i)+'.png'
        plot_waveforms(filename, synthetics_cap, synthetics_mtuq)

    print ' %d of %d' % (_i+2, grid.size+1)
    data_mtuq = data
    data_cap = get_data_cap(deepcopy(data), path_ref[0])
    filename = 'cap_fk_data.png'
    plot_waveforms(filename, data_cap, data_mtuq, normalize=False)


"""



if __name__=='__main__':
    import os
    import re

    from mtuq.util.util import root
    os.chdir(root())


    with open('examples/GridSearch.DoubleCouple.3Parameter.MPI.py', 'w') as file:
        file.write(Imports)
        file.write(DocstringDC3)
        file.write(PathsComments)
        file.write(PathsDefinitions)
        file.write(DataProcessingComments)
        file.write(DataProcessingDefinitions)
        file.write(MisfitComments)
        file.write(MisfitDefinitions)
        file.write(GridDC3)
        file.write(GridSearchMPI)


    with open('examples/GridSearch.DoubleCouple.5Parameter.MPI.py', 'w') as file:
        file.write(Imports)
        file.write(DocstringDC5)
        file.write(PathsComments)
        file.write(PathsDefinitions)
        file.write(DataProcessingComments)
        file.write(DataProcessingDefinitions)
        file.write(MisfitDefinitions)
        file.write(GridDC5)
        file.write(GridSearchMPI2)


    with open('examples/GridSearch.FullMomentTensor.5Parameter.MPI.py', 'w') as file:
        file.write(Imports)
        file.write(DocstringFMT5)
        file.write(PathsDefinitions)
        file.write(DataProcessingComments)
        file.write(DataProcessingDefinitions)
        file.write(MisfitComments)
        file.write(MisfitDefinitions)
        file.write(GridFMT5)
        file.write(GridSearchMPI)


    with open('examples/GridSearch.DoubleCouple.3Parameter.Serial.py', 'w') as file:
        file.write(
            re.sub(
            'grid_search_mpi',
            'grid_search_serial',
            Imports))
        file.write(DocstringDC3Serial)
        file.write(PathsComments)
        file.write(PathsDefinitions)
        file.write(DataProcessingComments)
        file.write(DataProcessingDefinitions)
        file.write(MisfitComments)
        file.write(MisfitDefinitions)
        file.write(GridDC3)
        file.write(GridSearchSerial)


    with open('tests/test_grid_search.py', 'w') as file:
        file.write(
            re.sub(
            'grid_search_mpi',
            'grid_search_serial',
            re.sub(
            'DoubleCoupleGridRandom',
            'DoubleCoupleGridRegular',
            Imports)))
        file.write(DocstringIntegrationTest)
        file.write(PathsDefinitions)
        file.write(DataProcessingDefinitions)
        file.write(MisfitDefinitions)
        file.write(GridIntegrationTest)
        file.write(GridSearchSerial)


    with open('tests/benchmark_cap_fk.py', 'w') as file:
        file.write(
            re.sub(
            'grid_search_mpi',
            'grid_search_serial',
            re.sub(
            'syngine',
            'fk',
            Imports)))
        file.write(DocstringBenchmarkCAPFK)
        file.write(PathsDefinitions)
        file.write(
            re.sub(
            'padding_length=.*',
            'padding_length=0,',
            DataProcessingDefinitions))
        file.write(
            re.sub(
            'time_shift_max=.*',
            'time_shift_max=0.,',
            MisfitDefinitions))
        file.write(GridBenchmarkCAPFK)
        file.write(RunBenchmarkCAPFK)








