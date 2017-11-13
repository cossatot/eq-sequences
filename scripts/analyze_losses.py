import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

loss = pd.read_csv('../results/agg_losses-all_25.csv', index_col=0,
                   header=0, usecols=[0,4],
                   names=['eid', 'losses'])
events = pd.read_csv('../results/aftershock_ruptures.csv', index_col=0)


eqs = events.join(loss).fillna(0)

mains = eqs.loc[eqs.aid == 0,:]
mains.index = mains.mainshock
afts = eqs.loc[eqs.aid != 0,:]

mains['aft_loss_sum'] = afts.groupby('mainshock').losses.sum()
mains['loss_ratio'] = mains.aft_loss_sum / mains.losses

####
# time series analysis
####

eq_dates = pd.read_csv('../data/puget_lowland_mean_eq_ages.csv')






















plt.figure()
plt.title('Mainshock and aftershock losses, Puget Sound, WA USA')
plt.scatter(mains.mag, mains.losses * 1e-6, 
            #c='purple', 
            lw=0, s=70,
            alpha=0.6,
            label='mainshocks')

plt.scatter(afts.mag, afts.losses * 1e-6, 
            #c='purple', 
            lw=0, s=70,
            alpha=0.4,
            label='aftershocks')

plt.gca().set_yscale('log')

plt.legend(loc='upper left')

plt.xlabel('Mw')
plt.ylabel('losses (million USD)')



plt.figure()
plt.title('Mainshock and summed aftershock losses')

plt.plot([0,15000],[0,15000],
         'k--', lw=0.5)

plt.scatter(mains.losses * 1e-6, mains.aft_loss_sum * 1e-6,
            s=2 * (mains.mag**2),
            lw=0)

#plt.axis('equal')

plt.xlabel('Mainshock losses (million USD)')
plt.ylabel('Total aftershock losses (million USD)')

plt.show()


def year_bp_to_cal_year(year_bp):
    return 1950 - year_bp


def get_eq_days(eq_dates, year_bp=True):
    if year_bp == True:
        eq_dates['cal_year'] = year_bp_to_cal_year(eq_dates['year_bp'])

    eq_dates['day'] = np.int_(np.round(eq_dates.cal_year * 365.25))

    return eq_dates


def get_mainshock_days(main_df, eq_dates):
    
    for i, eq in eq_dates.iterrows():
        main_df.loc[eq.mainshock, 'day'] = eq.day
    
    main_df['day'] = np.int_(main_df.day)

    return main_df


def get_aftershock_days(aft_df, eq_dates):
    for i, eq in aft_df.iterrows():
        aft_df.loc[i, 'cal_day'] = int( np.round(mains.loc[eq.mainshock, 'day']
                                                 + eq.day) )
        
    return aft_df


def make_day_df(yr_start=-11000, yr_end=1700):
    day_df = pd.DataFrame(index=np.arange(int(yr_start * 365.25), 
                                          int(yr_end * 365.25)),
                          columns=['mainshock_losses', 'aftershock_losses'])
    
    day_df['mainshock_losses'] = 0.
    day_df['aftershock_losses'] = 0.

    return day_df


def calc_daily_losses(day_df, main_df, aft_df):
    for i, eq in main_df.iterrows():
        day_df.loc[eq.day, 'mainshock_losses'] += eq.losses

    for i, eq in aft_df.iterrows():
        day_df.loc[eq.ady, 'aftershock_losses'] += eq.losses

    day_df['daily_losses'] = day_df.mainshock_losses + day_df.aftershock_losses

    day_df.filna(0, inplace=True)

    return day_df


def rolling_losses(day_df, yrs=1,
                   cols=('daily_losses','mainshock_losses','aftershock_losses')):
    
    if 'daily_losses' in cols:
        day_df['total_{}_yr_sum'.format(yrs)] = day_df['daily_losses'].rolling(
                                             round(yrs*365.25).sum().fillna(0))
    
    if 'mainshock_losses' in cols:
        day_df['mainshock_{}_yr_sum'.format(yrs)] = \
            day_df['mainshock_losses'].rolling(
                                             round(yrs*365.25).sum().fillna(0))

    if 'aftershock_losses' in cols:
        day_df['aftershock_{}_yr_sum'.format(yrs)] = \
            day_df['aftershock_losses'].rolling(
                                             round(yrs*365.25).sum().fillna(0))

    return day_df



'''
1. get mainshock dates (yr -> day)
 - get yrs
 - convert to cal years
 - make days


2. get aftershock dates
 - add mainshock day
 - this may be the slowest part of the analysis; should optimize


3. Make day_df
 - make w/ long, empty index
 - fill mainshock, aftershock losses in for loop
 - calculate daily sum

4. Additional calcs
- cumulative sums
- rolling sums

5. final analysis
- Exceedence probabilities?

'''
