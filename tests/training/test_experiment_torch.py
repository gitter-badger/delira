import pytest

import numpy as np

from delira.training import PyTorchExperiment, Parameters
from delira.training.callbacks import ReduceLROnPlateauCallbackPyTorch
from delira.models.classification import ClassificationNetworkBasePyTorch
from delira.data_loading import AbstractDataset, BaseDataManager
import torch


@pytest.mark.parametrize("params,dataset_length_train,dataset_length_test",
                         [
                             (
                                 Parameters(fixed_params={
                                     "model": {},
                                     "training": {
                                         "criterions": {"CE":
                                                        torch.nn.CrossEntropyLoss()},
                                         "optimizer_cls": torch.optim.Adam,
                                         "optimizer_params": {"lr": 1e-3},
                                         "num_epochs": 2,
                                         "metrics": {},
                                         "lr_sched_cls": ReduceLROnPlateauCallbackPyTorch,
                                         "lr_sched_params": {}
                                        }
                                 }
                                 ),
                                 500,
                                 50)
                         ])
def test_experiment(params, dataset_length_train, dataset_length_test):
    class DummyNetwork(ClassificationNetworkBasePyTorch):
        def __init__(self):
            super().__init__(32, 1)

        def forward(self, x):
            return self.module(x)

        @staticmethod
        def _build_model(in_channels, n_outputs):
            return torch.nn.Sequential(
                torch.nn.Linear(in_channels, 64),
                torch.nn.ReLU(),
                torch.nn.Linear(64, n_outputs)
            )

        @staticmethod
        def prepare_batch(batch_dict, input_device, output_device):
            return {"data": torch.from_numpy(batch_dict["data"]
                                             ).to(input_device, torch.float),
                    "label": torch.from_numpy(batch_dict["label"]
                                              ).to(output_device, torch.long)}

    class DummyDataset(AbstractDataset):
        def __init__(self, length):
            super().__init__(None, None, None, None)
            self.length = length

        def __getitem__(self, index):
            return {"data": np.random.rand(1, 32),
                    "label": np.random.randint(0, 1, size=1)}

        def __len__(self):
            return self.length

        def get_sample_from_index(self, index):
            return self.__getitem__(index)

    exp = PyTorchExperiment(params, DummyNetwork, val_score_key="val_CE")
    dset_train = DummyDataset(dataset_length_train)
    dset_test = DummyDataset(dataset_length_test)

    dmgr_train = BaseDataManager(dset_train, 16, 4, None)
    dmgr_test = BaseDataManager(dset_test, 16, 1, None)

    net = exp.run(dmgr_train, dmgr_test)
    exp.test(params=params,
             network=net,
             datamgr_test=dmgr_test,)

    exp.kfold(2, dmgr_train, num_splits=2)
    exp.stratified_kfold(2, dmgr_train, num_splits=2)
    exp.stratified_kfold_predict(2, dmgr_train, num_splits=2)


if __name__ == '__main__':
    test_experiment()
