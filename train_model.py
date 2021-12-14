import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from YoloVer1.dataset.MNISTDataset import MNISTDataset, GenerateRandMNIST
from YoloVer1.grids.YoloGrids import YoloGrids
from YoloVer1.model.YoloNetwork import YoloV1Network
from YoloVer1.tools.Normalizer import *


# global variables
epochs = 10
batch_size = 4
grids_size = (8, 8)
confidences = 1
bounding_boxes = 1
object_categories = 10

data_dir = 'YoloVer1/data/MNIST'

# training dataset
train_dataset = MNISTDataset(root=data_dir, train=True, download=True,
                             rand_mnist=GenerateRandMNIST(),
                             grids_system=YoloGrids(),
                             norm_data=generic_normalize)

# training loader
train_loader = DataLoader(train_dataset,
                          shuffle=True,
                          batch_size=batch_size)

# test dataset
test_dataset = MNISTDataset(root=data_dir, train=False, download=True,
                            rand_mnist=GenerateRandMNIST(),
                            grids_system=YoloGrids(),
                            norm_data=generic_normalize)

# test loader
test_loader = DataLoader(test_dataset,
                         shuffle=False,
                         batch_size=batch_size)


# define training function
def train(model, device, loader, optimizer, epoch):
    # train parameters
    model.train()  # set model to train mode

    # criterion and device auto-chosen
    model = model.to(device)
    criterion = nn.MSELoss().to(device)

    # train the model
    for batch_idx, (data, target) in enumerate(loader):
        data, target = data.to(device), target.to(device)

        # clear the gradients
        optimizer.zero_grad()

        # forward, backward, update
        outputs = model(data)
        loss = criterion(outputs, target)
        loss.backward()
        optimizer.step()

        if batch_idx % 30 == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(loader.dataset), 100. * batch_idx / len(loader), loss.item()))


# define test function
def test(model, device, loader):
    # test parameters
    model.eval()  # set model to test mode
    test_loss = 0
    correct = 0

    # criterion and device auto-chosen
    model = model.to(device)

    # test the model
    with torch.no_grad():
        for data, target in loader:
            data, target = data.to(device), target.to(device)

            # forward only
            output = model(data)

            # derive the confidences and ground truth
            pred_conf = output[:, confidences, :]
            true_conf = target[:, confidences, :]

            # derive bounding boxes from output and target
            pred_bboxes = output[:, confidences:, confidences + bounding_boxes * 4 :]
            true_bboxes = target[:, confidences:, confidences + bounding_boxes * 4 :]

            # derive the object categories from output and target
            pred_categories = output[:, confidences + bounding_boxes * 4:, :]
            true_categories = target[:, confidences + bounding_boxes * 4:, :]

            # derive the bounding box loss
            iou_scroes = compute_iou(pred_bboxes, true_bboxes) * true_conf * pred_conf

            # derive the object category loss
            category_loss = (true_categories - pred_categories) ** 2

            _, predicated = torch.max(output.data, dim=1)
            correct += (predicated == target).sum().item()
            test_loss += criterion(output, target).item()

    test_loss /= len(loader.dataset)

    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        test_loss, correct, len(loader.dataset),
        100. * correct / len(loader.dataset)))


def run_train_and_test_demo():
    # define model
    model = YoloV1Network(grids_size=grids_size,
                          confidences=confidences,
                          bounding_boxes=bounding_boxes,
                          object_categories=object_categories)

    # define optimizer
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.5)

    # define device
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # train model
    for epoch in range(1, epochs + 1):
        train(model, device, train_loader, optimizer, epoch)
        test(model, device, test_loader)

    # save model
    torch.save(model.state_dict(), '{}/saved_model.pt'.format(data_dir))
    print('Model saved!')
    print('Done!')


if __name__ == '__main__':
    run_train_and_test_demo()