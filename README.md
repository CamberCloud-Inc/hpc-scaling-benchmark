# Camber HPC Scaling Benchmarks

## Background

High-performance computing (HPC) is essential for large-scale scientific simulations, but optimizing performance requires benchmarking and scaling tests. Camber supports researchers by providing cloud-based HPC solutions that simplify access to compute resources. This guide outlines how to run a weak scaling test with the AthenaK astrophysical fluid dynamics code using MPI on a parallel system.

## AthenaK Scaling Test

### Obtaining and Compiling the Code

This section will help you build AthenaK, configure it for an MPI build with CUDA support for A100 GPUs, and compile the binary. AthenaK build requires cmake (version 3.0 or later).



```bash
git clone --recursive https://github.com/IAS-Astrophysics/athenak.git
cd athenak
mkdir build
cd build
cmake [options] ../
make all
```

Note that the `[options]` will depend on the choice of architecture and problem under consideration. The scaling test we would like to run is the radiation linear wave problem, which is part of the default build so the options we need to choose are primarily related to the architecture of the parallel system. As an example, a minimal MPI build on a parallel system with A100 GPUs would have the following make command

```
cmake -DAthena_ENABLE_MPI=ON -DKokkos_ENABLE_CUDA=On -DKokkos_ARCH_AMPERE80=On ../
```

More detailed build options and examples for specific clusters can be found in the [AthenaK Wiki](https://github.com/IAS-Astrophysics/athenak/wiki/Notes-for-Specific-Machines).

If the build is successful, one can proceed to compiling the binary by invoking:

```
make all
```

The resulting binary will be located in `build/src/athena`.

### Running AthenaK

To execute the radiation linear wave test using 4 MPI processes.

```
cd ..
mpirun -np 4 build/src/athena -i /athenak/inputs/tests/rad_linwave.athinput
```

### Perform the Weak Scaling Test

AthenaK has been tested on many platforms and generally performs well on either CPU or GPU enabled architectures. Due to the interleaving of communication and computation, the code has also demonstrated excellent week scaling on a number of large computing cluster. See e.g. section 5 of https://arxiv.org/pdf/2302.04283.

The default radiation linear wave input file is for a 2D run and is not a good proxy for 3D simulations, which usually has a larger communication to computation ratio due to the domain decomposition parallelization strategy. Therefore we provide the rad_linwave.athinput file. This is setup to match the scaling test reported in the referenced article. It would be invoked with mpirun as:

```
mpirun -np X [path to athena...]/athena -i rad_linwave.athinput
```

Replace `X` with the desired number of MPI processes, ensuring that the input file `rad_linwave.athinput` is in the run directory.

The test setup includes:

* A computational grid of 512x512x256 simulation cells.
* Partitioning into 32 subdomains (meshblocks) of 128x128x128 cells.
* Optimized for 8 A100 GPUs with 97%+ utilization.
* To maximize performance on different architectures, adjust nx1, nx2, and nx3 in the <mesh> and <meshblock> sections of the input file. Ensure the domain is evenly divided into integer meshblocks.

The run duration is controlled by `nlim` and `tlim` in the `<time>` block of the `athinput` file. The default setup runs for 1000 cycles: `nlim = 1000`. If reduced, the `tlim` value may need to be increased to avoid ending on the time limit.

Performance metrics such as `zone-cycles/cpu_second` will be reported at the end of the run. This value should be maximized for single-node runs and scale linearly with increasing node counts.

As the code runs, diagnostic information will be reported on each time step and performance information will be reported at the end. We recommend retaining this performance information, but the key diagnostic is the `zone-cycles/cpu_second`. This is a measure how many simulation cells were updated in total per second. This is the quantity that should ideally be maximized on a single node and also scale linearly when the number of CPU cores or GPUs is increased if weak scaling is efficient.

Once an optimal (one that maximizes utilization and zone-cycles/cpu_second) single node configuration is achieved, weak scaling should proceed by increasing the number of simulations cells (e.g. by increasing `nx1`, `nx2`, `nx3` in `<mesh>`) while keeping the `<meshblock>` dimensions fixed. For example, a two node run might start by doubling `nx1`. A four node run might then further double `nx2`, etc.

### Generating Results

We have also provided `plot_scaling.py` in the `scripts` directory for plotting the results. One must first create a three column text file with columns corresponding to node count, core/GPU count, and performance, respectively. Here, performance should be the cell-updates/sec returned at the end of the AthenaK run. Example files `cpu_scaling` and `gpu_scaling` are provided in the `scripts` directory.

For example, a plot of a CPU scaling test could be generated by the following command
```
python plot_scaling.py cpu_scaling -annotate
```
This will produce a file `cpu_scaling.png` with a two panel plot showing performance and weak scaling efficiency. The `-annotate` flag is an optional argument to provide the core/GPU count for each symbol in the scaling test. The default y-axis range for efficiency is `(95,105)` but this can be reset with the optional `--emin` and `--emax` parameters.

For example, our GPU scaling might use:
```
python plot_scaling.py gpu_scaling -annotate --emin 50
```

