#!/bin/bash

rm -f mainshock/agg*.csv
rm -f aftershocks/agg*.csv

cp ../results/mainshock_ruptures.csv mainshocks/
cp ../results/mainshock_gms.csv mainshocks/
cd mainshocks/
echo "=============================="
echo "Running mainshock calculations"
echo "=============================="
oq engine --run calc_losses_nw_wa.ini
oq export agg_loss_table
cd -

cp ../results/aftershock_ruptures.csv aftershocks/
cp ../results/aftershock_gms.csv aftershocks/
cd aftershocks/
echo "==============================="
echo "Running aftershock calculations"
echo "==============================="
oq engine --run calc_losses_nw_wa.ini
oq export agg_loss_table
cd -

#python ../scripts/calc_puget_sequence_losses.py

