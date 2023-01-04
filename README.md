# Short Cuts for Deep Neural models (2023)
*Smit, J.P. - TU Delft*


This repository contains code to accompany a Thesis Submitted to EEMCS Faculty Delft University of Technology, 
in Partial Fulfilment of the Requirements for the Bachelor of Computer Science and Engineering.

Notable credits should go to [JoshuaGhost](https://github.com/JoshuaGhost) for creating and maintaining [ExPred: the Deep Neural model](https://github.com/JoshuaGhost/expred) which we have studied for this thesis.
The model is an implementation of the paper [Explain and Predict, and then Predict Again](https://dl.acm.org/doi/abs/10.1145/3437963.3441758).

### Reproducing the Research

Here are the steps for those who are interested in reproducing the research.

1. Clone this repository
2. Install the requirements for the ``ExPred model`` by ``pip install -r requirements``
3. Run the provided Jupyter Notebooks

### Structure

This repository is a copy of the ExPred repository, with added Jupyter Notebooks.
It contains subsequences mined from the FeVer dataset, a big database (90.000 items) of fact queries containing a label 'Supported' or 'Refuted'.
The ExPred model draws evidence from Wikipedia pages to give queries those labels.

Interestingly, the ExPred model is not hundred percent fallible, it makes mistakes sometimes.
Yet the mistakes can be structural, meaning the model is biased.
We design an algorithm to point out the biggest biases of the ExPred model.

#### Algorithm
The algorithm was designed as follows:

Take the training dataset of FeVer as a dataset.
Take ExPred as a model.
Take DESQ as a subsequence mining tool.

1. Mine sequences from the 'Refuted' queries of the dataset.
2. Repeat with 'Supported' queries of the dataset.
3. XOR: Combine the two subsets of sequences and remove the duplicates.
4. Evaluate the mined sequences of both sides.
5. Confirm that the model output agrees with the training data
6. Propose 'Unseen claims': claims containing the subsequence, that the model has not yet observed
7. Perform 'Adverserial Attacks': swap the subsequence for a term that retains the meaning


### Results

| Query         | Most occurring label     | Correlation mined sequence-class | Percentage succesful Adverserial Attacks |
|--------------|-----------|------------| ------------|
| [is incapable of being](https://github.com/jpsmit/Short-Cuts-for-Deep-Neural-models/blob/master/is_incapable_of_being.ipynb) | REFUTED   | 100% | 78% |
| [has only ever been](https://github.com/jpsmit/Short-Cuts-for-Deep-Neural-models/blob/master/has_only_ever_been.ipynb) | REFUTED | 100% | 62% |
| [does not have](https://github.com/jpsmit/Short-Cuts-for-Deep-Neural-models/blob/master/does_not_have.ipynb) | REFUTED | 100% | 83% |
| [is exclusively](https://github.com/jpsmit/Short-Cuts-for-Deep-Neural-models/blob/master/is_exclusively.ipynb) | REFUTED | 100% |  40% |
| [is not a](https://github.com/jpsmit/Short-Cuts-for-Deep-Neural-models/blob/master/is_not_a.ipynb) | REFUTED |  |  |
| [is not an](https://github.com/jpsmit/Short-Cuts-for-Deep-Neural-models/blob/master/is_not_an.ipynb) | REFUTED |  |  |
| [has yet to](https://github.com/jpsmit/Short-Cuts-for-Deep-Neural-models/blob/master/has_yet_to.ipynb) | REFUTED |  |  |
| [is only a](https://github.com/jpsmit/Short-Cuts-for-Deep-Neural-models/blob/master/is_only_a.ipynb) | REFUTED |  |  |
| [was unable to](https://github.com/jpsmit/Short-Cuts-for-Deep-Neural-models/blob/master/was_unable_to.ipynb) | REFUTED | 100% | 76% |
| [There is a](https://github.com/jpsmit/Short-Cuts-for-Deep-Neural-models/blob/master/There_is_a.ipynb) | SUPPORTED |  |  |
| [was incapable of](https://github.com/jpsmit/Short-Cuts-for-Deep-Neural-models/blob/master/was_incapable_of.ipynb) | SUPPORTED | 100% |  89% |
| [making it the](https://github.com/jpsmit/Short-Cuts-for-Deep-Neural-models/blob/master/is_not_a.ipynb) | SUPPORTED | 75% | 100% |

