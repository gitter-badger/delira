import numpy as np
from . import DummyDataset

from delira.data_loading import BaseDataManager
from delira.data_loading import BaseDataLoader, SequentialSampler
from batchgenerators.dataloading import MultiThreadedAugmenter

def test_base_datamanager():

    batch_size = 16

    np.random.seed(1)
    dset = DummyDataset(600, [0.5, 0.3, 0.2])

    manager = BaseDataManager(dset, batch_size, n_process_augmentation=1, 
                            transforms=None)

    assert isinstance(manager.get_batchgen(), MultiThreadedAugmenter)

    # create batch manually
    data, labels = [], []
    for i in range(batch_size):
        data.append(dset[i]["data"])
        labels.append(dset[i]["label"])

    batch_dict = {"data": np.asarray(data), "label": np.asarray(labels)}

    for key, val in next(manager.get_batchgen()).items():
        assert (val == batch_dict[key]).all()
    for key, val in next(manager.get_batchgen()).items():
        assert len(val) == batch_size

if __name__ == '__main__':
    test_base_datamanager()