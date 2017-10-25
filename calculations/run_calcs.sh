#!/bin/bash

cp ../data/mainshock_ruptures.csv mainshocks/
cp ../data/mainshock_gms.csv mainshocks/
cd mainshocks/
echo "=============================="
echo "Running mainshock calculations"
echo "=============================="
oq engine --run calc_losses_nw_wa.ini
oq export agg_loss_table
cd -

cp ../data/aftershock_ruptures.csv aftershocks/
cp ../data/aftershock_gms.csv aftershocks/
cd aftershocks/
echo "==============================="
echo "Running aftershock calculations"
echo "==============================="
oq engine --run calc_losses_nw_wa.ini
oq export agg_loss_table
cd -

python ../scripts/calc_puget_sequence_losses.py
