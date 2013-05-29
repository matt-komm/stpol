echo "sync step4"

echo "inclusive, mu"
python $STPOL_DIR/sync/sync.py inclusive mu

echo "inclusive, ele"
python $STPOL_DIR/sync/sync.py inclusive ele

echo "exclusive, mu"
python $STPOL_DIR/sync/sync.py exclusive mu

echo "exclusive, ele"
python $STPOL_DIR/sync/sync.py exclusive ele
