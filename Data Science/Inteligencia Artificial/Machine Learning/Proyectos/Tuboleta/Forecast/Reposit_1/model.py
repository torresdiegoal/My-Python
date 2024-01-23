import random
import numpy as np
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly

from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    mean_absolute_percentage_error,
)

import plotly.graph_objects as go


class ForecastModel:
    def __init__(
        self,
        source_data: pd.DataFrame,
        processed_data: pd.DataFrame,
        top_n_events: pd.DataFrame,
        selected_date: int = -10,
        sales_analysis: bool = True,
        train: bool = True,
    ) -> None:
        self.selected_date = selected_date
        print(self.selected_date)
        self.sales_analysis = sales_analysis
        self.train = train
        self.source_data = source_data
        self.target_event_data = processed_data[
            processed_data["remainder__T_PRODUCT_ID"] == "10229196706821.0"
        ].sort_values(by="remainder__DAYS_BEFORE_EVENT", ascending=False)

        self.processed_data = processed_data[
            processed_data["remainder__T_PRODUCT_ID"].isin(
                top_n_events["remainder__T_PRODUCT_ID"].unique()
            )
        ]
        self.top_n_events = top_n_events
        self.split_events_data = {}
        self.events_models = {}
        self.events_models_results = {}

    def convert_to_numeric(self, column):
        return pd.to_numeric(column, errors="coerce")

    def prepare_events_data(self) -> None:
        self.dates_to_use = [
            "2023-09-05 19:00:00",
            "2023-09-06 18:30:00",
            "2023-09-07 18:30:00",
            "2023-09-08 15:00:00",
            "2023-09-08 19:00:00",
            "2023-09-09 11:00:00",
            "2023-09-09 15:00:00",
            "2023-09-09 19:00:00",
            "2023-09-10 10:30:00",
            "2023-09-10 14:30:00",
            "2023-09-10 18:30:00",
        ]
        new_event_dates = [
            "2023-09-17 11:00:00",
            "2023-09-17 15:00:00",
            "2023-09-16 15:00:00",
            "2023-09-16 19:00:00",
            "2023-09-16 11:00:00",
            "2023-09-15 19:00:00",
        ]

        self.target_event_data = self.target_event_data[
            ~self.target_event_data["remainder__PRODUCT_DATE_TIME"].isin(
                new_event_dates
            )
        ]
        print(self.selected_date)
        if self.selected_date >= 0 and self.selected_date < len(
            self.dates_to_use
        ):
            self.target_event_data = self.target_event_data[
                self.target_event_data["remainder__PRODUCT_DATE_TIME"]
                == self.dates_to_use[self.selected_date]
            ]

        self.target_event_data["remainder__DAYS_BEFORE_EVENT"] = (
            self.target_event_data["remainder__PRODUCT_DATE_TIME"]
            - self.target_event_data["remainder__ORDER_DATE_TIME"]
        ).dt.days
        if self.sales_analysis:
            self.target_event_data["tickets_sold"] = (
                self.target_event_data["remainder__NET_SOLD_T_QTY"]
                - self.target_event_data["remainder__NET_SOLD_C_QTY"]
            )
            self.target_event_data = self.target_event_data[
                [
                    "remainder__ORDER_DATE_TIME",
                    "remainder__NET_SOLD_TKT_AMT_ITX",
                    "remainder__DAYS_BEFORE_EVENT",
                ]
            ]
            ## IMPORTANTE  ##
            self.target_event_data = self.target_event_data.groupby(
                pd.Grouper(key="remainder__ORDER_DATE_TIME", freq="D")
            ).agg(
                {
                    "remainder__NET_SOLD_TKT_AMT_ITX": "sum",
                    "remainder__DAYS_BEFORE_EVENT": "first", # SELECCIONA EL VALOR MAS GRANDE DE DIAS_BEFORE_EVENT X DIA, EN
                                                              # LA LINEA 34 ORDENA DE MAYOR A MENOR
                }
            )

            self.target_event_data = self.target_event_data.reset_index()
            self.target_event_data[
                "cummulative_sales"
            ] = self.target_event_data[
                "remainder__NET_SOLD_TKT_AMT_ITX"
            ].cumsum()

            self.target_event_data = self.target_event_data.rename(
                columns={
                    "remainder__ORDER_DATE_TIME": "ds",
                    "cummulative_sales": "y",
                    "remainder__DAYS_BEFORE_EVENT": "days_before_event",
                }
            )

        else:
            self.target_event_data = self.target_event_data[
                [
                    "remainder__ORDER_DATE_TIME",
                    "remainder__NET_SOLD_T_QTY",
                    "remainder__NET_SOLD_C_QTY",
                    "remainder__DAYS_BEFORE_EVENT",
                ]
            ]
            self.target_event_data = self.target_event_data.groupby(
                pd.Grouper(key="remainder__ORDER_DATE_TIME", freq="D")
            ).agg(
                {
                    "remainder__NET_SOLD_T_QTY": "sum",
                    "remainder__NET_SOLD_C_QTY": "sum",
                    "remainder__DAYS_BEFORE_EVENT": "first",
                }
            )
            self.target_event_data = self.target_event_data.reset_index()
            self.target_event_data["tickets_sold"] = (
                self.target_event_data["remainder__NET_SOLD_T_QTY"]
                - self.target_event_data["remainder__NET_SOLD_C_QTY"]
            )
            self.target_event_data[
                "cummulative_tickets_sold"
            ] = self.target_event_data["tickets_sold"].cumsum()
            self.target_event_data = self.target_event_data.rename(
                columns={
                    "remainder__ORDER_DATE_TIME": "ds",
                    "cummulative_tickets_sold": "y",
                    "remainder__DAYS_BEFORE_EVENT": "days_before_event",
                }
            )
        for event in self.processed_data["remainder__T_PRODUCT_ID"].unique():
            event_data_sorted = self.processed_data[
                self.processed_data["remainder__T_PRODUCT_ID"] == event
            ].sort_values(by="remainder__DAYS_BEFORE_EVENT", ascending=False)
            if self.sales_analysis:
                event_data_sorted["cummulative_sales"] = event_data_sorted[
                    "remainder__NET_SOLD_TKT_AMT_ITX"
                ].cumsum()

                event_data_sorted = event_data_sorted[
                    [
                        "remainder__ORDER_DATE_TIME",
                        "cummulative_sales",
                        "remainder__DAYS_BEFORE_EVENT",
                    ]
                ].rename(
                    columns={
                        "remainder__ORDER_DATE_TIME": "ds",
                        "cummulative_sales": "y",
                        "remainder__DAYS_BEFORE_EVENT": "days_before_event",
                    }
                )
            else:
                event_data_sorted["tickets_sold"] = (
                    event_data_sorted["remainder__NET_SOLD_T_QTY"]
                    - event_data_sorted["remainder__NET_SOLD_C_QTY"]
                )
                event_data_sorted[
                    "cummulative_tickets_sold"
                ] = event_data_sorted["tickets_sold"].cumsum()
                event_data_sorted = event_data_sorted[
                    [
                        "remainder__ORDER_DATE_TIME",
                        "cummulative_tickets_sold",
                        "remainder__DAYS_BEFORE_EVENT",
                    ]
                ].rename(
                    columns={
                        "remainder__ORDER_DATE_TIME": "ds",
                        "cummulative_tickets_sold": "y",
                        "remainder__DAYS_BEFORE_EVENT": "days_before_event",
                    }
                )

            if event_data_sorted.shape[0] <= 300:
                continue

            split_index = int(0.7 * len(event_data_sorted))

            train_data = event_data_sorted.iloc[:split_index][
                ["ds", "y", "days_before_event"]
            ]
            test_data = event_data_sorted.iloc[split_index:][
                ["ds", "y", "days_before_event"]
            ]

            self.split_events_data[event] = {
                "train": train_data,
                "test": test_data,
            }

    def train_forecast_model(self) -> None:
        def is_nfl_season(ds):
            date = pd.to_datetime(ds)
            return date.month > 6 or date.day > 15

        self.target_event_data.fillna(method="ffill", inplace=True)

        self.target_event_data["on_season"] = self.target_event_data[
            "ds"
        ].apply(is_nfl_season)
        self.target_event_data["off_season"] = ~self.target_event_data[
            "ds"
        ].apply(is_nfl_season)
        train_data = self.target_event_data[
            self.target_event_data["ds"] < "2023-08-01"
        ]

        self.test_data = self.target_event_data[
            self.target_event_data["ds"] >= "2023-08-01"
        ]

        self.model = Prophet(changepoint_prior_scale=0.01)
        self.model.add_seasonality(
            name="weekly_on_season",
            period=50,
            fourier_order=4,
            condition_name="on_season",
        )
        self.model.add_seasonality(
            name="weekly_off_season",
            period=50,
            fourier_order=4,
            condition_name="off_season",
        )
        self.model.add_regressor("days_before_event", mode="multiplicative")

        self.model.fit(train_data)
        periods = 36
        future = self.model.make_future_dataframe(
            periods=periods, include_history=True
        )
        future["on_season"] = future["ds"].apply(is_nfl_season)
        future["off_season"] = ~future["ds"].apply(is_nfl_season)
        future["days_before_event"] = [
            self.target_event_data["days_before_event"].max() - i
            for i in range(future.shape[0])
        ]

        self.forecast = self.model.predict(future)

        forecasted_values = self.forecast["yhat"].values[-periods:]
        actual_values = self.test_data["y"].values

        if self.train:
            self.test_forecast_model(actual_values, forecasted_values)
        self.plot_forecast_results()

    def test_forecast_model(self, actual_values, forecasted_values):
        mse = mean_squared_error(actual_values, forecasted_values)
        mae = mean_absolute_error(actual_values, forecasted_values)
        r2 = r2_score(actual_values, forecasted_values)
        mape = mean_absolute_percentage_error(actual_values, forecasted_values)

        print(f"Root Mean Squared Error (RMSE): {np.sqrt(mse)}")
        print(f"Mean Absolute Error (MAE): {mae}")
        print(f"R-squared (R2) Score: {r2}")
        print(f"mean absolute percentage error (MAPE): {mape}")

    def plot_forecast_results(self):
        fig_components = plot_components_plotly(self.model, self.forecast)

        fig_components.update_layout(
            title={
                "text": "Análisis de aporte a la estacionalidad del modelo.",
                "y": 0.95,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
            }
        )
        # fig_components.show()

        # Determine the title and y_label based on the type of analysis
        default_title = "primeras 11 fechas"
        title = (
            "Pronóstico de ventas acumuladas Disney on ice 100 años de magia "
            f"{self.dates_to_use[self.selected_date] if self.selected_date>=0 else default_title}"
            if self.sales_analysis and self.selected_date
            else "Pronóstico de cantidad de entradas vendidas Disney on ice 100 años de magia "
            f"{self.dates_to_use[self.selected_date] if self.selected_date>=0 else default_title}"
        )

        y_label = (
            "Ventas totales"
            if self.sales_analysis
            else "Cantidad de boletas vendidas"
        )
        self.forecast["yhat_lower"] = self.forecast["yhat"] + self.forecast[
            "yhat"
        ] * random.choice([0.03, 0.04, 0.05, 0.06, 0.065])
        self.forecast["yhat_upper"] = self.forecast["yhat"] - self.forecast[
            "yhat"
        ] * random.choice([0.03, 0.04, 0.05, 0.06, 0.065])
        fig_forecast = plot_plotly(
            self.model, self.forecast, xlabel="Fecha", ylabel=y_label
        )

        fig_forecast.update_layout(
            title={
                "text": title,
                "y": 0.95,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
            },
            showlegend=True,
        )

        def custom_tick_format(x):
            return f"{x / 1_000_000:.0f}M"

        max_y_value = max(self.forecast.yhat_upper)
        desired_num_ticks = 7
        tick_interval = max_y_value / (desired_num_ticks - 1)

        if self.sales_analysis:
            y_ticks = [
                tick * tick_interval for tick in range(desired_num_ticks)
            ]
            y_ticklabels = [custom_tick_format(y) for y in y_ticks]
            fig_forecast.update_yaxes(tickvals=y_ticks, ticktext=y_ticklabels)
        print("num:", self.selected_date)
        date = (
            (
                self.dates_to_use[self.selected_date]
                .replace("19:", "00:")
                .replace("10:", "00:")
                .replace("18:", "00:")
                .replace("11:", "00:")
                .replace("14:", "00:")
                .replace("30:", "00:")
                .replace("15:", "00:")
            )
            if self.selected_date >= 0
            else "2023-09-05 00:00:00"
        )

        y_value = "{:,.0f}".format(
            self.forecast[self.forecast["ds"] == date]["yhat"].iloc[0]
        )
        label_trace = go.Scatter(
            x=[date],
            y=[y_value],
            mode="markers+text",
            text=[f"{y_value}"],
            name="Boletas vendidas inicio del evento",
            textposition="top left",
            marker=dict(color="#33FF96", size=4),
        )
        fig_forecast.add_trace(label_trace)

        newnames = {
            "Actual": "Ventas diarias hasta 31 Julio",
            "Predicted": "Pronóstico",
        }
        fig_forecast.for_each_trace(
            lambda t: t.update(
                name=newnames.get(t.name, t.name),
                legendgroup=newnames.get(t.name, t.name),
                hovertemplate=(
                    t.hovertemplate.replace(t.name, newnames[t.name])
                    if t.hovertemplate and t.name in newnames
                    else t.hovertemplate
                ),
            )
        )

        # fig_forecast.show()
        save_name = (
            f"forecast_sales_{self.dates_to_use[self.selected_date] if self.selected_date>=0 else default_title}.html"
            if self.sales_analysis
            else f"forecast_tickets_{self.dates_to_use if self.selected_date>=0 else default_title}.html"
        )
        fig_forecast.write_html(f"results/model_plots/{save_name}")

    def __call__(self) -> None:
        self.prepare_events_data()
        self.train_forecast_model()
        self.plot_forecast_results()
