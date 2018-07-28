# AGE

# Age and Gender Estimation

<img src="AGE-03.gif">

Age estimation is the determination of a person’s age based on biometric features. 

Although age estimation can be accomplished using different biometric traits, this project is focused on facial age estimation that relies on biometric features extracted from a person’s face. 

In the area of computerized analysis of facial images for recognition, ethnicity classification, gender recognition, etc. the age estimation is a barely explored part. However recently the interest in this subject has significantly increased, due to its practical applications. 

For example there are age limitations for driving a car, buying alcohol, cigarettes, films, video games, etc. which should be obeyed, but the human skills of age estimation are very limited. So a computer system, which supports the responsible persons, would be helpful. 

It is well known that the human-computer interaction varies for different age groups, thus a system which automatically adapts its interface to the age of the current user would clear this problem. 

Face detection: To detect whether an image represent a face i.e. the general structure of face or not. General structure include forehead, eyes, nose, lips, chin etc.

In this version, I add the feature to calculate the generation, based on the the identified age. [8]
<img src="http://assets.pewresearch.org/wp-content/uploads/var/www/vhosts/cms.pewresearch.org/htdocs/wp-content/blogs.dir/12/files/2018/04/11093240/FT_18.04.02_generationsDefined2017_working-age.png">

## Implementation

This is a Keras implementation of a CNN for estimating age and gender from a face image [1, 2].

## Dependencies
- Python3.5+
- Keras2.0+
- scipy, numpy, Pandas, tqdm, tables, h5py
- dlib (for demo)
- OpenCV3

Tested on:
- macOS High Sierra, Python 3.6.1, Keras 2.2.0, Tensorflow 1.9.0, Theano 1.0.2


## Usage

### Use pretrained model for demo
Run demo the script (requires web cam)

```sh
python3 demo.py
```

The pretrained model for TensorFlow backend will be automatically downloaded to the `pretrained_models` directory.

### Create training data from the IMDB-WIKI dataset
First, download the dataset.
The dataset is downloaded and extracted to the `data` directory by:

```sh
./download.sh
```

Secondly, filter out noise data and serialize images and labels for training into `.mat` file.
Please check [check_dataset.ipynb](check_dataset.ipynb) for the details of the dataset.
The training data is created by:

```sh
python3 create_db.py --output data/imdb_db.mat --db imdb --img_size 64
```

```sh
usage: create_db.py [-h] --output OUTPUT [--db DB] [--img_size IMG_SIZE] [--min_score MIN_SCORE]

This script cleans-up noisy labels and creates database for training.

optional arguments:
  -h, --help                 show this help message and exit
  --output OUTPUT, -o OUTPUT path to output database mat file (default: None)
  --db DB                    dataset; wiki or imdb (default: wiki)
  --img_size IMG_SIZE        output image size (default: 32)
  --min_score MIN_SCORE      minimum face_score (default: 1.0)
```

### Create training data from the UTKFace dataset
Firstly, download images from [the website of the UTKFace dataset](https://susanqq.github.io/UTKFace/).
`UTKFace.tar.gz` can be downloaded from `Aligned&Cropped Faces` in Datasets section.
Then, extract the archive.

```sh
tar zxf UTKFace.tar.gz UTKFace
```

Finally, run the following script to create the training data:

```
python3 create_db_utkface.py -i UTKFace -o UTKFace.mat
```

[NOTE]: Because the face images in the UTKFace dataset is tightly cropped (there is no margin around the face region),
faces should also be cropped in `demo.py` if weights trained by the UTKFace dataset is used.
Please set the margin argument to 0 for tight cropping:

```sh
python3 demo.py --weight_file WEIGHT_FILE --margin 0
```

The pre-trained weights can be found [here](https://github.com/yu4u/age-gender-estimation/releases/download/v0.5/weights.29-3.76_utk.hdf5).

### Train network
Train the network using the training data created above.

```sh
python3 train.py --input data/imdb_db.mat
```

Trained weight files are stored as `checkpoints/weights.*.hdf5` for each epoch if the validation loss becomes minimum over previous epochs.

```sh
usage: train.py [-h] --input INPUT [--batch_size BATCH_SIZE]
                [--nb_epochs NB_EPOCHS] [--depth DEPTH] [--width WIDTH]
                [--validation_split VALIDATION_SPLIT] [--aug]

This script trains the CNN model for age and gender estimation.

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT, -i INPUT
                        path to input database mat file (default: None)
  --batch_size BATCH_SIZE
                        batch size (default: 32)
  --nb_epochs NB_EPOCHS
                        number of epochs (default: 30)
  --depth DEPTH         depth of network (should be 10, 16, 22, 28, ...)
                        (default: 16)
  --width WIDTH         width of network (default: 8)
  --validation_split VALIDATION_SPLIT
                        validation split ratio (default: 0.1)
  --aug                 use data augmentation if set true (default: False)
```

### Train network with recent data augmentation methods
Recent data augmentation methods, mixup [3] and Random Erasing [4],
can be used with standard data augmentation by `--aug` option in training:

```bash
python3 train.py --input data/imdb_db.mat --aug
```

Please refer to [this repository](https://github.com/yu4u/mixup-generator) for implementation details.

I confirmed that data augmentation enables us to avoid overfitting
and improves validation loss.


### Use the trained network

```sh
python3 demo.py
```

```sh
usage: demo.py [-h] [--weight_file WEIGHT_FILE] [--depth DEPTH] [--width WIDTH]

This script detects faces from web cam input, and estimates age and gender for
the detected faces.

optional arguments:
  -h, --help                show this help message and exit
  --weight_file WEIGHT_FILE path to weight file (e.g. weights.18-4.06.hdf5) (default: None)
  --depth DEPTH             depth of network (default: 16)
  --width WIDTH             width of network (default: 8)

```

Please use the best model among `checkpoints/weights.*.hdf5` for `WEIGHT_FILE` if you use your own trained models.

### Plot training curves from history file

```sh
python3 plot_history.py --input models/history_16_8.h5 
```

#### Results without data augmentation
<img src="https://github.com/yu4u/age-gender-estimation/wiki/images/loss.png" width="400px">

<img src="https://github.com/yu4u/age-gender-estimation/wiki/images/accuracy.png" width="400px">

#### Results with data augmentation
The best val_loss was improved from 3.969 to 3.731:
- Without data augmentation: 3.969
- With standard data augmentation: 3.799
- With mixup and random erasing: 3.731

<img src="fig/loss.png" width="480px">

We can see that, with data augmentation,
overfitting did not occur even at very small learning rates (epoch > 15).

### Network architecture
In [the original paper](https://www.vision.ee.ethz.ch/en/publications/papers/articles/eth_biwi_01299.pdf) [1, 2], the pretrained VGG network is adopted.
Here the Wide Residual Network (WideResNet) is trained from scratch.
I modified the @asmith26's implementation of the WideResNet; two classification layers (for age and gender estimation) are added on the top of the WideResNet.

Note that while age and gender are independently estimated by different two CNNs in [1, 2], in my implementation, they are simultaneously estimated using a single CNN.

### Estimated results
Trained on imdb, tested on wiki.
![](https://github.com/yu4u/age-gender-estimation/wiki/images/result.png)


### Evaluation

#### Evaluation on the APPA-REAL dataset
You can evaluate a trained model on the APPA-REAL (validation) dataset by:

```bash
python3 evaluate_appa_real.py
```

Please refer to [here](appa-real) for the details of the APPA-REAL dataset.

The results of pretrained model is:

```
MAE Apparent: 6.06
MAE Real: 7.38
```

The best result reported in [5] is:

```
MAE Apparent: 4.08
MAE Real: 5.30
```

Please note that the above result was achieved by finetuning the model using the training set of the APPA-REAL dataset,
while the pretrained model here is not and the size of images is small (64 vs. 224).

Anyway, I should do finetuning on the training set of the APPA-REAL...

## For further improvement
If you want better results, there would be several options:

- Use larger training images (e.g. --img_size 128).
- Use VGGFace as an initial model and finetune it (https://github.com/rcmalli/keras-vggface).
  - In this case, the size of training images should be (224, 224).
- Use more "clean" dataset (http://chalearnlap.cvc.uab.es/dataset/18/description/) (only for age estimation)


## License
This project is released under the MIT license.
However, [the IMDB-WIKI dataset](https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/) used in this project is originally provided under the following conditions.

> Please notice that this dataset is made available for academic research purpose only. All the images are collected from the Internet, and the copyright belongs to the original owners. If any of the images belongs to you and you would like it removed, please kindly inform us, we will remove it from our dataset immediately.

Therefore, the pretrained model(s) included in this repository is restricted by these conditions (available for academic research purpose only).


## References
[1] R. Rothe, R. Timofte, and L. V. Gool, "DEX: Deep EXpectation of apparent age from a single image," in Proc. of ICCV, 2015.

[2] R. Rothe, R. Timofte, and L. V. Gool, "Deep expectation of real and apparent age from a single image
without facial landmarks," in IJCV, 2016.

[3] H. Zhang, M. Cisse, Y. N. Dauphin, and D. Lopez-Paz, "mixup: Beyond Empirical Risk Minimization," in arXiv:1710.09412, 2017.

[4] Z. Zhong, L. Zheng, G. Kang, S. Li, and Y. Yang, "Random Erasing Data Augmentation," in arXiv:1708.04896, 2017.

[5] E. Agustsson, R. Timofte, S. Escalera, X. Baro, I. Guyon, and R. Rothe, "Apparent and real age estimation in still images with deep residual regressors on APPA-REAL database," in Proc. of FG, 2017.

[6] Age-gender-estimation project by Lav Solanki: https://github.com/lavsolanki/Age-Gender-estimation

[7] Age-gender-estimation project by Yu4u: https://github.com/yu4u/age-gender-estimation

[8] Generations: http://socialmarketing.org/archives/generations-xy-z-and-the-others/

<br>
<A Href="https://www.linkedin.com/in/jairribeiro/" target="_blank"><img src="https://raw.githubusercontent.com/gitliber/Basic_self_driving_car/master/LinkProf.jpeg" style="width: auto; height: auto; " /> <br>
</A>









