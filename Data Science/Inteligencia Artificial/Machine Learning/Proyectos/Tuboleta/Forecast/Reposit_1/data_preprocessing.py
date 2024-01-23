import pandas as pd
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.neighbors import NearestNeighbors
import plotly.graph_objects as go

from utils import convert_gender, apply_PCA, improve_text_position


class ModelsDataPreprocessing:
    def __init__(self, data_path: str) -> None:
        """
        This class is responsible for processing the data file in order to
        generate an appropriate model input structure dataframe.

        It is mandatory to use the same structure used in the training data.

        Args:
            data_path (str): location of the data file to be processed
        """
        self.raw_data = pd.read_csv(data_path, sep=",", low_memory=False)
        self.raw_data["T_PRODUCT_ID"] = self.raw_data["T_PRODUCT_ID"].astype(
            str
        )
        self.source_data = self.raw_data.copy()
        self.data = self.raw_data[
            self.raw_data["ORDER_TYPE"].isin(["SALE", "REFUND_CLIENT"])
        ]
        self.unused_columns = [
            "PRODUCT",
            "PRODUCT_CODE",
            "PROMOTION",
            "LOGICAL_SEAT_CATEGORY",
            "SEAT_CATEGORY",
            "IP_ADDRESS",
            "NAT_NUMBER_CELLPHONE",
            "BIRTHDATE",
            "T_ORDER_CONTACT_ID",
            "TAX_RATE",
            "ADDRESS_SALUTATION",
            "FILE_NUMBER",
            "BASE",
            "T_CONTACT_ID",
            "FIRSTNAME",
            "LASTNAME",
            "MAIN_ADDR_TOWN",
            "MAIN_ADDR_COUNTRY",
            "MAIN_ADDR_ZIPCODE",
            "ORDER_NUMBER",
            "INSURED",
            "INSURED_AMT_ITX",
            "FULLNAME",
            "GROUPED_RATE",
            "TOWN",
            "ID_NUMBER",
            "EMAIL",
            "ORDER_TYPE",
            "FILE_STATE",
        ]
        self.continuous_columns = [
            "remainder__PERFORMANCE_QUOTA",
            "remainder__AGE",
            "remainder__NET_SOLD_C_QTY",
            "remainder__NET_SOLD_T_QTY",
            "remainder__UNIT_AMT_ETX",
        ]
        self.additional_category_columns = [
            "GROUPED_PROMOTION",
            "SSO_PROVIDER",
            "MAIN_ADDR_GEO_ZONE",
            "INVOICE_CONTACT_FMT_NAME",
        ]
        self.date_columns = [
            "BIRTHDATE",
            "ORDER_DATE_TIME",
            "PRODUCT_DATE_TIME",
        ]
        self.categorical_columns = [
            "GENDER",
            "ORGANIZATION",
            "INVOICE_CONTACT_FMT_NAME",
            "TOPIC",
            "SUB_TOPIC",
            "SALES_CHANNEL_TYPE",
            "SITE",
            "AUDIENCE_SUB_CATEGORY",
            "SALES_CHANNEL",
            "DN_QUOTA",
            "MAIN_ADDR_GEO_ZONE",
            "GROUPED_PROMOTION",
            "SSO_PROVIDER",
        ]
        self.convert_to_datetime()

    def convert_to_datetime(self):
        """
        Manages the conversion of a datetime columns to be used in the
        dataframe.
        """
        for column in self.date_columns:
            self.data[column].fillna(
                pd.Timestamp("01/01/1900 00:00:00"), inplace=True
            )
            self.data[column] = pd.to_datetime(
                self.data[column], format="%d/%m/%Y %H:%M:%S", errors="coerce"
            )
        current_date = datetime.now()
        if "BIRTHDATE" in self.data.columns:
            self.data.loc[:, "AGE"] = (
                current_date.year
                - self.data["BIRTHDATE"].dt.year
                - (
                    (current_date.month < self.data["BIRTHDATE"].dt.month)
                    | (
                        (current_date.month == self.data["BIRTHDATE"].dt.month)
                        & (current_date.day < self.data["BIRTHDATE"].dt.day)
                    )
                )
            )

    def prepare_quantitative_data(self) -> None:
        """
        Prepare the data by encoding categorical columns using a combination
        of Ordinal and One-Hot Encoders.
        """

        one_hot_encoder_columns = []
        ordinal_encoder_columns = []
        for column in self.categorical_columns:
            if len(self.data[column].unique()) > 15:
                ordinal_encoder_columns.append(column)
            else:
                one_hot_encoder_columns.append(column)

        categorical_columns_encoder = ColumnTransformer(
            transformers=[
                (
                    "OrdinalEncoder", 
                    OrdinalEncoder(), 
                    ordinal_encoder_columns),
                (
                    "OneHotEncoder",
                    OneHotEncoder(sparse=False, drop="first"),
                    one_hot_encoder_columns,
                ),
            ],
            remainder="passthrough",
        )

        encoded_data = categorical_columns_encoder.fit_transform(self.data)
        self.ordinal_encoder = categorical_columns_encoder.named_transformers_[
            "OrdinalEncoder"
        ]
        self.one_hot_encoder = categorical_columns_encoder.named_transformers_[
            "OneHotEncoder"
        ]
        self.data = pd.DataFrame(
            data=encoded_data,
            columns=categorical_columns_encoder.get_feature_names_out(),
        )

    def fill_continuous_null_values(self, column_names: list) -> None:
        """
        Fill missing values in specified continuous columns using Linear
        Regression imputation.

        Args:
            column_names (list): List of column names with missing values to be
            imputed.
        """
        new_data = self.data.copy()

        test_df = new_data[new_data[column_names].isnull().any(axis=1)]
        train_df = new_data[~new_data[column_names].isnull().any(axis=1)]
        for col in column_names:
            train_features = train_df.drop(
                columns=column_names
                + [
                    "remainder__ORDER_DATE_TIME",
                    "remainder__PRODUCT_DATE_TIME",
                ],
                axis=1,
            )
            train_target = train_df[col]
            test_features = test_df.drop(
                columns=column_names
                + [
                    "remainder__ORDER_DATE_TIME",
                    "remainder__PRODUCT_DATE_TIME",
                ],
                axis=1,
            )

            lr = LinearRegression()
            lr.fit(train_features, train_target)

            pred = lr.predict(test_features)

            self.data.loc[test_df.index, col] = pred

    def manage_null_values(self) -> None:
        """
        Apply the K-Nearest Neighbors (KNN) algorithm to find events similar
        to the target event based on selected features.

        Args:
            n_neighbors (int, optional): The number of nearest neighbors to
            consider in the KNN algorithm. Default is 5.
        """
        for column in self.additional_category_columns:
            if column in self.data.columns:
                self.data[column] = self.data[column].fillna("sin datos")

        self.data = self.data[self.data["DAYS_BEFORE_EVENT"].notna()]
        self.data["GENDER"] = self.data.apply(
            lambda row: convert_gender(
                row["GENDER"], row["ADDRESS_SALUTATION"]
            ),
            axis=1,
        )

        self.data.drop(columns=self.unused_columns, inplace=True)

        self.prepare_quantitative_data()

        for column in self.continuous_columns:
            if column not in self.data.columns:
                self.continuous_columns.remove(column)

        if self.continuous_columns:
            self.fill_continuous_null_values(self.continuous_columns)

    def apply_KNN_model(self, n_neighbors: int = 5) -> None:
        """
        Plot the KNN results, showing similar events and their characteristics
        in comparison to the target event.

        Args:
            x_column (str): The column to be plotted on the x-axis.
            y_column (str): The column to be plotted on the y-axis.

        Returns:
            None
        """
        columns_list = list(self.data.columns)
        columns_list.remove("remainder__T_PRODUCT_ID")
        columns_list.remove("remainder__ORDER_DATE_TIME")
        columns_list.remove("remainder__PRODUCT_DATE_TIME")
        self.target_event = (
            self.data[
                self.data["remainder__T_PRODUCT_ID"] == "10229196706821.0"
            ]
            .groupby("remainder__T_PRODUCT_ID")[columns_list]
            .mean()
        )
        other_events = (
            self.data[
                self.data["remainder__T_PRODUCT_ID"] != "10229196706821.0"
            ]
            .groupby("remainder__T_PRODUCT_ID")[columns_list]
            .mean()
        )

        scaled_data, scaled_target_data = apply_PCA(
            other_events, self.target_event
        )

        neighbors_model = NearestNeighbors(n_neighbors=n_neighbors)
        neighbors_model.fit(scaled_data)
        distances, indices = neighbors_model.kneighbors(scaled_target_data)

        top_n_indices = indices[0][:n_neighbors]
        self.top_n_events = other_events.iloc[top_n_indices]

        self.top_n_events.reset_index(inplace=True)
        self.top_n_events["distances"] = distances[0]

        # Columns to plot
        y_column = "remainder__PERFORMANCE_QUOTA"
        x_column = "remainder__UNIT_AMT_ITX"
        columns_names = ["Aforo promedio", "Precio promedio de entrada"]

        self.plot_knn_results(x_column, y_column, columns_names)

    def plot_knn_results(
        self, x_column: str, y_column: str, columns_names: list
    ):
        fig = go.Figure()
        annotations = []
        labels = []

        for i, row in self.top_n_events.iterrows():
            label = (
                self.source_data[
                    self.source_data["T_PRODUCT_ID"]
                    == row["remainder__T_PRODUCT_ID"]
                ]
                .iloc[0]["PRODUCT"]
                .lower()
            )
            labels.append(label)
            annotations.append(
                dict(
                    x=row[x_column],
                    y=row[y_column],
                    xref="x",
                    yref="y",
                    text=label,
                    showarrow=True,
                    arrowhead=2,
                    ax=0,
                    ay=-20,
                )
            )

        fig.update_layout(annotations=annotations)

        fig.add_trace(
            go.Scatter(
                x=self.top_n_events[x_column],
                y=self.top_n_events[y_column],
                mode="markers",
                name="Eventos similares",
                marker=dict(
                    color="red", symbol="x", size=12, line=dict(width=2)
                ),
                text=labels,
                hoverinfo="text",
            )
        )
        fig.update_traces(
            textposition=improve_text_position(self.top_n_events[x_column])
        )

        fig.add_trace(
            go.Scatter(
                x=self.target_event[x_column],
                y=self.target_event[y_column],
                mode="markers",
                name="Disney on ice 100 años de magia",
                marker=dict(
                    color="blue", symbol="circle", size=15, line=dict(width=2)
                ),
            )
        )
        fig.update_layout(
            title="Relación entre eventos más cercanos y Disney on ice 100 años de magia",
            title_x=0.5,
            yaxis_title=columns_names[0],
            xaxis_title=columns_names[1],
            font=dict(size=10),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            xaxis=dict(tickfont=dict(size=10)),
            yaxis=dict(tickfont=dict(size=10)),
            margin=dict(l=50, r=50, t=60, b=50),
        )

        # fig.show()
        fig.write_html("results/knn_results/aforo_vs_precio.html")

    def __call__(self) -> tuple:
        self.manage_null_values()
        self.apply_KNN_model()

        return self.data, self.top_n_events, self.raw_data


data_preprocessing = ModelsDataPreprocessing(data_path="data.csv")
processed_data, top_n_similar_events, data = data_preprocessing()
