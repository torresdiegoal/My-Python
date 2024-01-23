from data_preprocessing import data, processed_data, top_n_similar_events
from model import ForecastModel

if __name__ == "__main__":
    model_execution = ForecastModel(
        data,
        processed_data,
        top_n_similar_events,
        sales_analysis=True,
    )
    model_execution()
