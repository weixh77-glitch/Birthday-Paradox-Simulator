# Birthday Paradox Simulator

This Python desktop app demonstrates the probability that at least two people in a group share a birthday. Enter a group size to generate random birthdays, see which dates repeat, and compare theoretical and simulated probabilities on a chart.

## Run the app

You need Python 3 with Tkinter. No third-party packages are required. Run this command from the project directory:

```bash
python birthday_paradox.py
```

When prompted, enter a group size from 1 to 10,000. The main window displays the randomly generated birthdays and marks any shared dates. To draw a fresh sample, edit the group size if needed and click the generate button. The app interface is in Chinese.

## How the probabilities are calculated

The model assumes that birthdays are independent and uniformly distributed across 365 days, excluding February 29. For a group of `n` people, the probability of at least one shared birthday is one minus the probability that all birthdays are different:

```text
P(at least one shared birthday) = 1 - (365/365) x (364/365) x ... x ((366 - n)/365)
```

With **23 people**, the theoretical probability is about **50.73%**. With **366 or more people**, a shared birthday is guaranteed.

The simulation runs 10,000 trials. Each trial records the group size at which the first shared birthday appears. For any group size, the simulated probability is the fraction of trials in which a shared birthday has appeared by that size. The birthdays shown in the table come from a separate random sample.
