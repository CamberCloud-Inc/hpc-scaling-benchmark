import matplotlib.pyplot as plt
import numpy as np
import argparse

def read_file(infile):
    ''' Read three column scaling input files'''
    data = np.loadtxt(infile)
    return data[:,0], data[:,1], data[:,2]

def main(**kwargs):
    
    # read scaling file
    nc, cc, pc = read_file(kwargs['infile'])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

    ax1.scatter(nc, pc, marker='s')
    ax1.set_ylabel('Performance (cell updates/sec)')

    if (kwargs['annotate']):
        for i, lab in enumerate(cc):
            ax1.annotate(str(int(lab)), xy=(nc[i], pc[i]), xytext=(0, 6), textcoords='offset points')
    ax1.set_yscale('log')
    ax1.set_xscale('log')

    eff = 100*pc*nc[0] / (pc[0]*nc)
    ax2.scatter(nc, eff, marker='s')
    ax2.set_ylabel('Efficiency (%)')
    ax2.set_xlabel('Node Count')
    ax2.set_ylim([kwargs['emin'], kwargs['emax']])
    ax2.set_xscale('log')
    
    plt.savefig(kwargs['infile'] + '.png')

    
# Execute main function
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('infile',
                        default = None,
                        help = 'input filename')
    parser.add_argument('-annotate',
                        action='store_true',
                        help = 'turn on annotations')
    parser.add_argument('--emin',
                        default = 95,
                        type = float,
                        help = 'minimum efficiency')
    parser.add_argument('--emax',
                        default = 105,
                        type = float,
                        help = 'maximum efficiency')
    args = parser.parse_args()
    main(**vars(args))
