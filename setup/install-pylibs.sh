#!/bin/bash
set -e
cd $STPOL_DIR/local
unset HTTP_PROXY
unset http_proxy

echo "Installing setuptools"
wget --no-check-certificate https://pypi.python.org/packages/source/s/setuptools/setuptools-0.7.7.tar.gz
tar xf setuptools-0.7.7.tar.gz
cd setuptools*
python setup.py install --prefix=$STPOL_DIR/local
cd ..

echo "Installing argparse"
wget http://argparse.googlecode.com/files/argparse-1.2.1.tar.gz &> /dev/null
tar xf argparse-1.2.1.tar.gz
cd argparse*
python setup.py install --prefix=$STPOL_DIR/local &> /dev/null
cd ..

python -c 'import argparse;print "Argparse version=",argparse.__version__'

echo "Installing sqlalchemy"
wget --no-check-certificate https://pypi.python.org/packages/source/S/SQLAlchemy/SQLAlchemy-0.8.1.tar.gz &> /dev/null
tar xf SQLAlchemy-0.8.1.tar.gz
cd SQLAlchemy-0.8.1
python setup.py install --prefix=$STPOL_DIR/local
