wget http://ftp.gnu.org/gnu/parallel/parallel-latest.tar.bz2
tar xf parallel-latest.tar.bz2
cd parallel*
./configure --prefix=$STPOL_DIR/local
make
make install
