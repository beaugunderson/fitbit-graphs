#!/usr/bin/env python
# encoding: utf8

from __future__ import division

from collections import defaultdict
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy
import pandas
import scipy
import seaborn

from matplotlib.ticker import FuncFormatter


def shorten_date(x, position):
    x_time = datetime(2000, 1, 15) + timedelta(minutes=int(x))

    return x_time.strftime('%I:%M%p').lower().lstrip('0').replace(':00', '')

ShorterDateFormatter = FuncFormatter(shorten_date)

SIZE = (30, 7)


def graph_fitbit(filename):
    try:
        print 'Reading pickle file...'
        data = pandas.io.pickle.read_pickle('./ernesto.pickle')
    except:
        print 'Falling back to CSV...'
        print 'Reading file...'
        data = pandas.io.parsers.read_csv(filename,
                                          parse_dates=[0],
                                          index_col='ActivityMinute',
                                          infer_datetime_format=True)

        print 'Writing pickle file...'
        data.to_pickle('./ernesto.pickle')

    print 'Grouping...'
    groups = data.groupby(pandas.Grouper(freq='24h'))

    stacked_values = []
    week_values = defaultdict(list)

    print 'Generating by-minute arrays...'

    for start_time, group in groups:
        timestamp = start_time

        if not len(group.index):
            continue

        values = []

        for _ in xrange(0, 1440):
            timestamp = timestamp + timedelta(minutes=1)

            try:
                values.append(group.Steps[timestamp])
            except KeyError:
                values.append(numpy.NaN)

        ten_minute_mean_values = pandas.rolling_mean(numpy.array(values), 10)

        stacked_values.append(ten_minute_mean_values)
        week_values[timestamp.weekday()].append(ten_minute_mean_values)

    print 'Plotting all data...'

    fig = plt.figure(figsize=SIZE)
    fig.set_dpi(300)

    ax = seaborn.tsplot(stacked_values,
                        value='Steps per Minute',
                        linewidth=1.0,
                        ci=50,
                        # err_style='unit_traces',
                        estimator=scipy.stats.nanmean)

    ax.xaxis.set_ticks(numpy.arange(0, 1440, 1440 / 24))
    ax.xaxis.set_major_formatter(ShorterDateFormatter)

    fig.tight_layout()

    print 'Saving...'
    plt.savefig('all', bbox_inches='tight')

    print 'Plotting by day data...'

    fig = plt.figure(figsize=SIZE)
    fig.set_dpi(300)

    palette = seaborn.color_palette('hls', 8)

    good_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                   'Saturday', 'Sunday']

    for day, values in week_values.items():
        ax = seaborn.tsplot(values,
                            value='Steps per Minute',
                            linewidth=1.0,
                            color=palette[day],
                            ci=50,
                            estimator=scipy.stats.nanmean)

        ax.xaxis.set_ticks(numpy.arange(0, 1440, 1440 / 24))
        ax.xaxis.set_major_formatter(ShorterDateFormatter)

    # Add legend to last axis
    for day in xrange(0, 6):
        p = plt.Rectangle((0, 0), 0, 0,
                          label=good_labels[day],
                          color=palette[day])

        ax.add_patch(p)

    handles, labels = ax.get_legend_handles_labels()

    # Easier way to filter these?
    handles, labels = zip(*[(h, l) for h, l in zip(handles, labels)
                            if l in good_labels])

    legend = ax.legend(handles, labels, frameon=1, bbox_to_anchor=(1.01, 1),
                       loc=2, borderaxespad=0.0)

    frame = legend.get_frame()
    frame.set_facecolor('white')

    fig.tight_layout()

    print 'Saving...'
    plt.savefig('by-day', bbox_inches='tight')


if __name__ == '__main__':
    fitbit_file = './ernesto-unique.csv'

    graph_fitbit(fitbit_file)
