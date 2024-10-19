# ALPS Setup Manual

## Initialize
mkpath ALPSLib

## Dependencies

### MPI

Load provided version. For personal macOS laptop:

```bash
brew install open-mpi
```

Then it will automatic work.

### Boost

Building Boost is tricky on macOS, since `clang` is in principle different. Thus, if you want to build boost, try

```bash
# Only if You are using mac
./bootstrap --with-toolset=clang
./b2 toolset=clang cxxflags="-std=c++11 -stdlib=libc++" linkflags="-stdlib=libc++" 
```

[Warning]: **If you have to build Boost, always make sure the configuration is exactly the same to the version in `setup_alps.py`.** 

### HDF5

Binary is not enough. Especially when you do not have ROOT on a computing cluster, you might need compile it directly. 

```bash
cd ALPSLib
wget https://support.hdfgroup.org/releases/hdf5/v1_14/v1_14_5/downloads/hdf5-1.14.5.tar.gz
tar -xzvf hdf5-1.14.5.tar.gz
cd hdf5-1.14.5
./configure
make & make install 
cd ..
```

In general, this will let cmake find HDF5.

### FFTW

```bash
cd ALPSLib
wget https://www.fftw.org/fftw-3.3.10.tar.gz
tar -xzvf fftw-3.3.10.tar.gz
cd fftw-3.3.10
./configure
make & make install 
cd ..
```


## Reference

For any potential fallback, please review: https://alps.comp-phys.com/install/

For Singularity Imgae, see: https://github.com/qiyang-ustc/ALPS_SIF
