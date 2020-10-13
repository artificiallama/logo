# GAN for generation of logos.

A team project for Aggregate Intellect's workshop in May, 2020. The team consisted of three members (including myself).

The code of the gan is taken from 
https://github.com/eriklindernoren/PyTorch-GAN/blob/master/implementations/dcgan/dcgan.py
and then modified

For the dataset, we used the large logo dataset
https://data.vision.ee.ethz.ch/sagea/lld/
and used the icon dataset(i.e. image 32x32) and used only one of the cluster.

This is project is part of the 

The project wsd done with Vikram Khade (https://github.com/Gigajumper) and Adrian Perez Galvan (https://github.com/greenmossball).

To train the model run dcgan.py script

When the training is finish is finish, the model is package with mlflow. The app.py script is to create a small app to return an logo.

After the training of the gan, we train an encoder for the gan to learn an encoding to encode an image into the latent space of the gan.

The code for the deployement (mlflow packaging, flask api and dockerfile are mostly inspired by the course material)

https://www.youtube.com/watch?v=KCaFGCVnFfA
