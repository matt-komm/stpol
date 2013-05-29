ipcontroller --log-to-file &> /dev/null &
ipcluster engines --log-to-file &> /dev/null &
ipython notebook --pylab=inline
#ipcluster start --n=16 &
#ipython notebook --profile=nbserver

