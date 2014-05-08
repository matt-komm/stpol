#!/bin/bash

read -p "Removing $STPOL_DIR/local, continue with install (y/n)?" choice
case "$choice" in 
  y|Y ) echo "Installing python libraries";;
  n|N ) exit 0;;
    * ) exit 0;;
esac

rm -Rf $STPOL_DIR/local
mkdir -p $STPOL_DIR/local/lib/python2.6/site-packages/
mkdir -p $STPOL_DIR/local/lib/python2.7/site-packages/

cd $STPOL_DIR/local
set -e
unset HTTP_PROXY
unset http_proxy

echo "Installing setuptools"
curl -kO https://pypi.python.org/packages/source/s/setuptools/setuptools-0.9.5.tar.gz > /dev/null
tar xf setuptools-0.9.5.tar.gz
cd setuptools-0.9.5
python setup.py install --prefix=$STPOL_DIR/local
cd $STPOL_DIR/local
python -c 'import setuptools;print "setuptools version=",setuptools.__version__'

echo "Installing pip"
curl -kO https://pypi.python.org/packages/source/p/pip/pip-1.4.tar.gz
tar xf pip-1.4.tar.gz 
cd pip-1.4
python setup.py install --prefix=$STPOL_DIR/local
cd $STPOL_DIR/local


$STPOL_DIR/local/bin/pip install --install-option="--prefix=$STPOL_DIR/local" shortuuid
$STPOL_DIR/local/bin/pip install --install-option="--prefix=$STPOL_DIR/local" argparse
$STPOL_DIR/local/bin/pip install --install-option="--prefix=$STPOL_DIR/local" python-xmp-toolkit
$STPOL_DIR/local/bin/pip install --install-option="--prefix=$STPOL_DIR/local" networkx

cd $STPOL_DIR/local
echo "Installing rootpy"
git clone git://github.com/rootpy/rootpy.git > /dev/null
cd rootpy
python setup.py install --prefix=$STPOL_DIR/local > /dev/null
python -c 'import rootpy;print "rootpy version=",rootpy.__version__'
cd $STPOL_DIR/local
