import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


def convert_gender(gender: str, address_salutation: str) -> str:
    """
    This function takes a gender string and an address salutation string as
    input and returns the corresponding gender in Spanish.

    Args:
        gender (str): A string representing the gender, which can be "MALE",
        "FEMALE", "UNKNOWN", or an empty string.
        address_salutation (str): A string representing the address salutation,
        which can include titles like "Mr", "Mrs", "Miss", "Señor", "Señora",
        "Señorita", "Don", and more.

    Returns:
        str: The corresponding gender in Spanish, which can be "HOMBRE" for
        male, "MUJER" for female, or "SIN DATO" for unknown or missing data.
    """
    if gender == "MALE":
        return "HOMBRE"
    elif gender == "FEMALE":
        return "MUJER"
    elif gender == "UNKNOWN" and address_salutation in (
        "Mr",
        "Señor",
        "Señor,",
        "Don",
    ):
        return "HOMBRE"
    elif gender == "UNKNOWN" and address_salutation in (
        "Ms",
        "Mrs",
        "Miss",
        "Señora",
        "Señorita",
    ):
        return "MUJER"
    elif gender == "" and address_salutation in (
        "Mr",
        "Señor",
        "Señor,",
        "Don",
    ):
        return "HOMBRE"
    elif gender == "" and address_salutation in (
        "Ms",
        "Mrs",
        "Miss",
        "Señora",
        "Señorita",
    ):
        return "MUJER"
    elif (gender is None or gender == "") and address_salutation in (
        "Mr",
        "Señor",
        "Señor,",
        "Don",
    ):
        return "HOMBRE"
    elif (gender is None or gender == "") and address_salutation in (
        "Ms",
        "Mrs",
        "Miss",
        "Señora",
        "Señorita",
    ):
        return "MUJER"
    elif gender is None and address_salutation in (
        "Mr",
        "Señor",
        "Señor,",
        "Don",
    ):
        return "HOMBRE"
    elif gender is None and address_salutation in (
        "Ms",
        "Mrs",
        "Miss",
        "Señora",
        "Señorita",
    ):
        return "MUJER"
    else:
        return "SIN DATO"


def apply_PCA(
    input_data: pd.DataFrame, target: pd.DataFrame, variance_ratio=0.95
):
    """
    Apply Principal Component Analysis (PCA) to reduce the dimensionality of
    input data and target data.

    Args:
        input_data (pd.DataFrame): The input data to which PCA will be applied.
        target (pd.DataFrame): The target data to which PCA will be applied.
        variance_ratio (float, optional): The desired variance ratio to retain
        during PCA, typically between 0 and 1. Default is 0.95.

    Returns:
        pd.DataFrame, pd.DataFrame: Transformed input_data and target data
        after PCA.
    """

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(input_data)

    pca = PCA(n_components=variance_ratio)
    data_pca = pca.fit_transform(scaled_data)

    scaled_target_data = scaler.transform(target)
    target_pca = pca.transform(scaled_target_data)

    return data_pca, target_pca


def improve_text_position(x):
    positions = ["top center", "bottom center"]

    return [positions[i % len(positions)] for i in range(len(x))]
