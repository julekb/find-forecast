import os

from matplotlib import pyplot as plt
from seaborn import objects as so

from constants import PLOTS_DIR
from domain.models import WeatherData, WeatherParams


def plot_weather_data_as_jpg(
    weather_data: WeatherData, x_key: WeatherParams, filename: str
) -> None:
    output_dir = os.path.join(PLOTS_DIR, filename)

    # sns.set_style("darkgrid", {"axes.facecolor": ".9"})
    # sns.set_context("paper")
    #
    # sns.relplot(
    # data=weather_data.data, x=WeatherParams.TIMESTAMP, y=x_key, kind="line", hue="type")
    # plt.xticks(rotation=90)
    # plt.savefig(output_dir, format="jpg", dpi=300)
    fig, ax = plt.subplots()
    ax.xaxis.set_tick_params(rotation=90)

    p = so.Plot(data=weather_data.data, x=WeatherParams.TIMESTAMP, y=x_key, color="type")
    p = p.add(so.Line()).on(ax)
    p.save(output_dir, format="jpg")
