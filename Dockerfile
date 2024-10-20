# Use Ubuntu 14.04 with GCC 5 as the base image
FROM holbertonschool/ubuntu-1404-gcc5

# Set environment variables
ENV LC_ALL=C
ENV CXX=/usr/bin/g++
ENV ALPS_DIR=/project/alps/share/alps/
ENV BOOST_PATH=/project/boost_1_63_0
ENV PROJECT_DIR=/project
ENV PARALLEL_BUILD=8

# Switch to root to install dependencies
USER root

# Install dependencies and set up the project
RUN apt-get update -y && \
    apt-get install -y zip cmake wget libboost-dev build-essential gfortran cmake \
    libhdf5-serial-dev libfftw3-dev gfortran python-matplotlib \
    python-scipy liblapack-dev xsltproc python-dev libboost-all-dev && \
    mkdir -p $PROJECT_DIR && cd $PROJECT_DIR && \
    wget https://github.com/qiyang-ustc/ALPS_SIF/archive/refs/heads/master.zip && \
    unzip master.zip && rm master.zip && mv ./ALPS_SIF-master/* ./ && rmdir ALPS_SIF-master && \
    wget https://boostorg.jfrog.io/artifactory/main/release/1.63.0/source/boost_1_63_0.zip && \
    unzip boost_1_63_0.zip && \
    rm boost_1_63_0.zip && \
    echo "Install Boost finished" && \
    mkdir -p /project/alps-2.3.0-src/alps/build && \
    cd /project/alps-2.3.0-src/alps/build && \
    cmake -DALPS_BUILD_FORTRAN=ON \
    -DALPS_ENABLE_OPENMP=ON \
    -DCMAKE_CXX_COMPILER=/usr/bin/g++ \
    -DCMAKE_C_COMPILER=/usr/bin/gcc \
    -DCMAKE_INSTALL_PREFIX=/project/alps \
    -DBoost_ROOT_DIR:PATH=/project/boost_1_63_0 \
    -DHDF5_LIBRARIES=/usr/lib/x86_64-linux-gnu/libhdf5.so \
    /project/alps-2.3.0-src/alps && \
    make -j$PARALLEL_BUILD && make install -j$PARALLEL_BUILD

# Set labels
LABEL maintainer="QiYang" \
      os_version="ubuntu-14" \
      gcc_version="5.x" \
      alps_version="2.3.0" \
      boost_version="1.63.0"

# Set the default command
CMD ["/bin/bash"]