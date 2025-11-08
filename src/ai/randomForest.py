from decisionTree import DecisionTreeClassifier
import numpy as np
import numpy.typing as npt
import random


class RandomForest:
    def __init__(self, num_trees: int = 6) -> None:
        """
        initialize Random Forest algorithm with the amount of trees it is going to create
        """
        self.num_trees = num_trees
        self.trees = []
        self.tree_features = []

    def fit(self, data: npt.NDArray) -> None:
        """
        Fit the model with data, by creating trees with randomized samples and features
        """
        samples, features = data.shape
        num_features = round(
            (features - 1) ** 0.5
        )  # the square roots proved to be the most effective
        for _ in range(self.num_trees):
            dT = DecisionTreeClassifier()
            dT.fit(self.get_random_data(data, num_features, samples, features))
            self.trees.append(dT)

    def get_random_data(
        self, data: npt.NDArray, num_features: int, samples: int, features: int
    ) -> npt.NDArray:
        """
        returns randomized samples with randomized features.
        """
        new_data = []
        for _ in range(len(data)):
            new_data.append(data[random.randint(0, samples - 1)])

        random_features = [random.randint(0, features - 2) for _ in range(num_features)]
        random_features.append(num_features)
        self.tree_features.append(random_features)
        for idx, patient in enumerate(new_data):
            new_data[idx] = [
                value for idx, value in enumerate(patient) if idx in random_features
            ]

        return np.array(new_data)

    def predict(self, patient: npt.NDArray) -> int:
        """
        traverse all the trees with patient and calculate the result
        """
        predictions = []
        for features, tree in zip(self.tree_features, self.trees):
            new_patient = [
                value for idx, value in enumerate(patient) if idx in features
            ]
            predictions.append(tree.traverse_tree(np.array(new_patient)))

        return round(sum(predictions) / len(predictions))
