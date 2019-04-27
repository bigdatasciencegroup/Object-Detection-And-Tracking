import torch
from torch import nn, optim

from torch.autograd import Variable
from torch.utils.data import DataLoader
from torchvision import transforms
from torchvision import datasets

batch_size = 32
lr = 1e-2
num_epoches = 50

train_dataset = datasets.MNIST(
    root = './data', train=True, transform=transforms.ToTensor(), download=True)

test_dataset = datasets.MNIST(
    root='./data', transform=transforms.ToTensor(), train=False)

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

class Neuralnetwork(nn.Module):
    def __init__(self, in_dim, n_hidden_1, n_hidden_2, out_dim):
        super(Neuralnetwork, self).__init__()
        self.layer1 = nn.Linear(in_dim, n_hidden_1)
        self.layer2 = nn.Linear(n_hidden_1, n_hidden_2)
        self.layer3 = nn.Linear(n_hidden_2, out_dim)

    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        return x

model = Neuralnetwork(28*28, 300, 100, 10)
if torch.cuda.is_available():
    model.cuda()

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=lr)
for epoch in range(num_epoches):
    print('epoch {}'.format(epoch+1))
    print('*' * 10)
    running_loss = 0.0
    # running_acc = torch.Tensor(0.0, required_grad = True)
    running_acc = 0.0
    # running_acc.require_grad = True
    for i, data in enumerate(train_loader, 1):
        img, label = data
        img = img.view(img.size(0), -1)
        if torch.cuda.is_available():
            img = Variable(img).cuda()
            label = Variable(label).cuda()

        out = model(img)
        loss = criterion(out, label)
        running_loss = loss * label.size(0)
        _, pred = torch.max(out, 1)
        num_correct = (pred == label).sum()
        running_acc += num_correct

        # backward
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if i % 300 == 0:
            print('[{} / {}] Loss : {:.6f}, Acc : {:.6f}'.format(
                epoch + 1, num_epoches, running_loss/ (batch_size * i),
                running_acc.item() / (batch_size * i)
            ))


model.eval()
eval_loss = 0.
eval_acc = 0.
for data in test_loader:
    img, label = data
    img = img.view(img.size(0), -1)
    if torch.cuda.is_available():
        img = Variable(img).cuda()
        label = Variable(label).cuda()

    out = model(img)
    loss = criterion(out, label)
    eval_loss += loss * label.size(0)
    _, pred = torch.max(out, 1)
    num_correct = (pred == label).sum()
    eval_loss = num_correct.item()
    eval_acc += num_correct.item()
    print(eval_acc / len(test_dataset))

torch.save(model.state_dict(), './mnist_model.pth')