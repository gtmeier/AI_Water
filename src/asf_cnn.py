"""
Alaska Satellite Facility
Convolutional Neural Network
McKade Sorensen (Douglas)
05/16/2019

Detects water within a SAR image.

Part 1: Creating the CNN
Step 1: Convolution
Step 2: Max Pooling
Step 3: Flattening
Step 4: Full Connection - ANN

Part 2: Fitting the CNN to the image
"""

from typing import Any, Dict, List

# import pandas as pd
from keras.models import Model

from .dataset import load_dataset
from .model import save_model
from .typing import History


def train_model(
    model: Model,
    model_history: History,
    dataset: str,
    epochs: int,
    verbose: int = 1
) -> None:
    if verbose > 0:
        model.summary()

    training_set, test_set = load_dataset(dataset)

    step_size_training = len(training_set)
    step_size_vaild = len(test_set)

    if not step_size_training:
        if verbose > 0:
            print("No training data! Aborting...")
            return

    # Get the number of existing entries in the history
    epoch_prev = len(next(iter(model_history.values())))

    for epoch in range(epochs):
        epoch += 1

        if verbose > 0:
            print(f"Epoch {epoch}/{epochs}")

        history = model.fit_generator(
            training_set,
            steps_per_epoch=step_size_training,
            epochs=1,
            validation_data=test_set,
            validation_steps=step_size_vaild,
            verbose=verbose
        )

        for key in model_history.keys():
            model_history[key] += history.history[key]

        save_model(model, f"e{epoch + epoch_prev}", history=model_history)

    save_model(model, 'latest')


def test_model(model: Model, dataset: str,
               verbose: int = 1) -> Dict[str, List[Any]]:
    if verbose > 0:
        model.summary()

    _, test_iter = load_dataset(dataset)

    predictions = model.predict_generator(
        test_iter, steps=len(test_iter), verbose=verbose
    )
    test_iter.reset()

    total = 0
    total_correct = 0
    num_to_labels = {0: "not_water", 1: "water"}
    details = {"Image": [], "Label": [], "Prediction": [], "Percent": []}

    # Test iter needs to have batch size of 1
    for prediction, (_, [label]) in zip(predictions, test_iter):
        total += 1
        prediction = prediction[0]
        if label == round(prediction):
            total_correct += 1

        # TODO: Get image name
        details["Image"].append('image_name')
        details["Label"].append(num_to_labels[label])
        details["Prediction"].append(num_to_labels[round(prediction)])
        details["Percent"].append(prediction)

    print(f"Computed accuracy: {total_correct/total}")

    return details
