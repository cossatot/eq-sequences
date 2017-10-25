import pandas as pd

mainshock_output_file = "../calcs/mainshocks/agg_losses-rlz-000_1.csv"
aftershock_output_file = "../calcs/aftershocks/agg_losses-rlz-000_2.csv"
mainshock_ruptures_file = "../calcs/mainshocks/mainshock_ruptures.csv"
aftershock_ruptures_file = "../calcs/aftershocks/aftershock_ruptures.csv"
mainshock_losses_file = "../calcs/mainshocks/mainshock_losses.csv"
aftershock_losses_file = "../calcs/aftershocks/aftershock_losses.csv"

mainshock_ruptures_df = pd.read_csv(mainshock_ruptures_file, index_col=0)
aftershock_ruptures_df = pd.read_csv(aftershock_ruptures_file, index_col=0)
mainshock_output_df = pd.read_csv(mainshock_output_file, index_col=0,
                                  header=0, usecols=[0, 3],
                                  names=['eid', 'losses'])
aftershock_output_df = pd.read_csv(aftershock_output_file, index_col=0,
                                  header=0, usecols=[0, 3],
                                  names=['eid', 'losses'])

mainshock_losses_df = mainshock_ruptures_df.join(mainshock_output_df).fillna(0)
aftershock_losses_df = aftershock_ruptures_df.join(aftershock_output_df).fillna(0)
mainshock_losses_df.to_csv(mainshock_losses_file)
aftershock_losses_df.to_csv(aftershock_losses_file)

mainshock_losses = mainshock_losses_df.losses.values.sum()
aftershock_losses = aftershock_losses_df.losses.values.sum()

print("Mainshock losses: ${0:.2f} M".format(mainshock_losses/1e6))
print("Aftershock losses: ${0:.2f} M".format(aftershock_losses/1e6))
print("Difference: {0:.1%}".format(
    (aftershock_losses - mainshock_losses)/mainshock_losses))
