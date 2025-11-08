import numpy as np
import numpy.typing as npt


class Node:
    def __init__(
        self,
        left=None,
        right=None,
        treshold: float | None = None,
        feature: int | None = None,
        value: int | None = None,
    ) -> None:
        """
        class reprezenting a tree node

        left: left subtree
        right: right subtree
        treshold: splitting value of a node
        featutre: id of a feature we are comparing
        value: only leafs have a value, 0 - means healthy, 1 - means sick
        """
        self.left = left
        self.right = right
        self.treshold = treshold
        self.feature = feature
        self.value = value


class DecisionTreeClassifier:
    def __init__(self, max_depth: int = 64, min_sample: int = 1) -> None:
        """
        We initialize a Decision Tree with max_depth and min_sample, and create a root
        max_depth : maximal depth a tree can reach
        min_sample : minimal sample a node can have
        """
        self.root = None
        self.max_depth = max_depth
        self.min_sample = min_sample

    def fit(self, data: npt.NDArray) -> None:
        """
        fit the data to the model by crafting a tree with given data
        """
        self.root = self.craftTree(data)

    def is_leaf(self, Y: list) -> bool:
        """
        checks wheter data consists of only one result(in that case it is a leaf)
        """
        i = Y[0]
        for val in Y:
            if i != val:
                return False
        return True

    def craftTree(self, data: npt.NDArray, depth: int = 0) -> Node | None:
        """
        crafts a tree recursively by finding best split and spliting until we get only leafs or reach maximum depth, or sample is smaller than minimal sample
        """
        Y = [point[-1] for point in data]
        if depth > self.max_depth or self.min_sample > len(data) or self.is_leaf(Y):
            if len(data) == 0:
                return None
            return Node(value=self.most_common_label(Y))

        best_value = self.get_best_value(data)
        left = self.craftTree(best_value["left_data"], depth + 1)
        right = self.craftTree(best_value["right_data"], depth + 1)

        return Node(
            left,
            right,
            best_value["treshold"],
            best_value["feature"],
        )

    def most_common_label(self, Y: list) -> int:
        """
        choses most common number(between 1 and 0)
        """
        return round(sum(Y) / len(Y))

    def get_best_value(self, data: npt.NDArray) -> dict:
        """
        choses the best treshold and feature to split the data using gini impurity
        """
        samples, features = data.shape
        max_score = 0
        max_sample_feature = (0, 1)
        sick, healthy = self.count_states(data)
        Gini_before_split = self.Gini_Impurity(
            sick, healthy
        )  # calculating gini impurity before split
        for feature in range(0, features - 1):
            for sample in range(samples):
                treshold = data[sample][feature]
                left0 = 0
                left1 = 0
                right0 = 0
                right1 = 0
                for patient in data:
                    if patient[feature] <= treshold:
                        if patient[0] == 0:
                            left0 += 1
                        else:
                            left1 += 1
                    else:
                        if patient[0] == 0:
                            right0 += 1
                        else:
                            right1 += 1
                if left1 + left0 == 0 or right1 + right0 == 0:
                    continue
                score = self.info_gain(
                    Gini_before_split,
                    self.Gini_Impurity(left0, left1),
                    self.Gini_Impurity(right0, right1),
                )
                if score >= max_score:
                    # chosing the best scoring split
                    max_score = score
                    max_sample_feature = (sample, feature)

        # splitting the data with best split
        sample, feature = max_sample_feature
        treshold = data[sample][feature]
        right_data = []
        left_data = []
        for patient in data:
            if patient[feature] <= treshold:
                left_data.append(patient)
            else:
                right_data.append(patient)

        return {
            "treshold": treshold,
            "right_data": np.array(right_data),
            "left_data": np.array(left_data),
            "feature": feature,
        }

    def count_states(self, data: npt.NDArray) -> tuple:
        """
        counts the amount of sick and healthy patients
        """
        healthy, sick = 0, 0
        for patient in data:
            if patient[-1] == 0:
                healthy += 1
            else:
                sick += 1
        return healthy, sick

    def info_gain(self, G: float, G1: float, G2: float) -> float:
        """
        calculates final score for a split
        """
        return G - ((G1 + G2) / 2)

    def Gini_Impurity(self, y1: int, y2: int) -> float:
        """
        calculates gini impurity for a given split(only one side)
        """
        return 1 - (y1 / (y1 + y2)) ** 2 - (y2 / (y1 + y2)) ** 2

    def predict(self, patient: npt.NDArray) -> int:
        """
        returns prediction made by a model
        """
        return self.traverse_tree(patient)

    def traverse_tree(self, patient: npt.NDArray) -> int:
        """
        traverses the tree and upon encountering a leaf return a prediction
        """
        node = self.root
        if node is None:
            raise TypeError("root is None!")

        while node.value is None:
            if patient[node.feature] <= node.treshold:
                node = node.left
            else:
                node = node.right
            if node is None:
                raise TypeError("node is None!")

        return node.value
