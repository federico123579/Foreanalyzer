# Foreanalyzer

> Personal algo analyzer for the Forecaster bot.
> The swap is calculated with the following formula: quantity * swap fee for long/short position * number of nights the position is open.
> By opening this link - https://www.trading212.com/en/Trading-Instruments  you can check the swap fees for long and short position.
> If you wish to avoid the fee you can close the trade before 9 pm GMT

> In order result to be converted a 0.5% fee of the value of the result is taken(this fee is already included in the result)

# Project Managment

What to buy:

- whiteboard

# Checklists

**~ New Plot**

- [ ] add to globals
- [ ] add supported feeders to globals

**~ New Feeder**

- [ ] add feeder support to plot in plot_hanlder
- [ ] add feeder support to plot in globals

**~ checklist add new indicator ~**
- [ ] add funtion below
- [ ] add to factory
- [ ] add to glob