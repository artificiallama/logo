from dcgan_model import Encoder
import torch
from dcgan_dataset import SimpleDataset
from os.path import join
import torch.nn as nn
from torchvision.utils import save_image
import torchvision.transforms as transforms
from torch.autograd import Variable
import matplotlib.pyplot as plt
import pandas as pd

def get_dataloader(opt):

    transformation = transforms.Compose(
        [transforms.Resize(opt.img_size), transforms.ToTensor(), transforms.Normalize([0.5], [0.5])]
    )

    train_logo = SimpleDataset(join('data', 'cluster', str(opt.cluster)), transformation, split = 'train')
    valid_logo = SimpleDataset(join('data', 'cluster', str(opt.cluster)), transformation, split = 'valid')

    train_dataloader = torch.utils.data.DataLoader(
            train_logo,
            batch_size=opt.batch_size,
            shuffle=True,
        )

    valid_dataloader = torch.utils.data.DataLoader(
            valid_logo,
            batch_size=opt.batch_size,
            shuffle=True,
        )

    return train_logo, valid_logo, train_dataloader, valid_dataloader

def save_loss_plot(batches_list, train_loss_list, valid_loss_list, experiment_path):
    plt.scatter(batches_list, train_loss_list, label="train loss")
    plt.scatter(batches_list, valid_loss_list, label="valid loss")
    plt.legend(loc="upper left")
    plt.xlabel('epoch')
    plt.ylabel('loss')
    plt.savefig(join(experiment_path, 'loss_encoder.png'))
    plt.close()

def train_encoder(opt, generator, experiment_path):
    generator.eval()
    cuda = True if torch.cuda.is_available() else False

    train_logo, valid_logo, train_dataloader, valid_dataloader = get_dataloader(opt)

    nb_train_element = train_logo.__len__()
    nb_valid_element = valid_logo.__len__()

    encoder = Encoder(opt)
    optimizer_E = torch.optim.Adam(encoder.parameters(), lr=opt.lr, betas=(opt.b1, opt.b2))

    Tensor = torch.cuda.FloatTensor if cuda else torch.FloatTensor

    L2_loss = nn.MSELoss()

    if cuda:
        encoder.cuda()
        L2_loss.cuda()

    train_loss_list = []
    valid_loss_list = []
    epoch_list = []
    best_valid_loss = None
    best_epoch = None

    for epoch in range(opt.n_epochs_encoder):
        loss_calculation = 0
        for i, data in enumerate(train_dataloader):
            imgs, _ = data
            real_imgs = Variable(imgs.type(Tensor))
            batch_size = imgs.shape[0]
            z = encoder(real_imgs)
            new_imgs = generator(z)

            encoder_loss = L2_loss(new_imgs, real_imgs)

            encoder_loss.backward()
            optimizer_E.step()

            loss_calculation += encoder_loss.item()*batch_size/nb_train_element
            print('train epoch '+str(epoch)+' batch '+str(i)+' loss '+str(encoder_loss.item()))
            df = pd.DataFrame(z.data.cpu().numpy())
            df.to_csv(join('experiments', 'encoding_training_data.csv'))

        train_loss_list.append(loss_calculation)
        loss_calculation=0
        for i, data in enumerate(valid_dataloader):
            imgs, _ = data
            real_imgs = Variable(imgs.type(Tensor))
            batch_size = imgs.shape[0]
            z = encoder(real_imgs)
            new_imgs = generator(z)

            encoder_loss = L2_loss(new_imgs, real_imgs)

            loss_calculation += encoder_loss.item()*batch_size/nb_valid_element
            print('valid epoch ' + str(epoch) + ' batch ' + str(i) + ' loss ' + str(encoder_loss.item()))

        valid_loss_list.append(loss_calculation)
        imgs_show = torch.cat((real_imgs[:5], new_imgs[:5]), 0)
        if best_valid_loss is not None:
            if loss_calculation < best_valid_loss:
                best_valid_loss = loss_calculation
                best_epoch = epoch
                torch.save(encoder.state_dict(), join(experiment_path, 'E.pth'))
                save_image(imgs_show, join(experiment_path, "encoding_image.png" ), nrow=5,
                           normalize=True)
        else:
            best_valid_loss = loss_calculation
            best_epoch = epoch
            torch.save(encoder.state_dict(), join(experiment_path, 'E.pth'))
            save_image(imgs_show, join(experiment_path, "encoding_image.png" ), nrow=5,
                       normalize=True)
        epoch_list.append(epoch)
        torch.save(encoder.state_dict(), join(experiment_path,'model', 'E%d.pth' % epoch))

        save_image(imgs_show, join(experiment_path, 'images', "encoding_epoch%d.png" % epoch), nrow=5, normalize=True)
        save_loss_plot(epoch_list, train_loss_list, valid_loss_list, experiment_path)

    return encoder



