# -*- coding: utf-8 -*-
"""parkinsons first stage

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ar0vqeelYsZm4-2uxvIevxXA8hLhdkBR
"""

from __future__ import absolute_import, division, print_function, unicode_literals
import tensorflow as tf
device_name = tf.test.gpu_device_name()
if device_name != '/device:GPU:0':
  raise SystemError('GPU device not found')
print('Found GPU at: {}'.format(device_name))
from tensorflow import keras
import numpy as np
import cv2
import os
import random
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Convolution2D
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import TensorBoard,EarlyStopping
import datetime
import time
import math as m

from google.colab import drive
drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard

"""# *DATASET* preparation"""

#dataset preparartion class to make it easier to load the data
class DataSet:
    
    def __init__(me,location,categories,resize=True,
                 lheight=500,lwidth=500,grayscale=True,shuffled=False,
                 apply=None,count=1000,multiclass=False,enhance=False):
        me.categories=categories
        me.datadir=location
        me.lheight=lheight
        me.lwidth=lwidth
        me.grayscale=grayscale
        me.shuffled=shuffled
        me.multiclass=multiclass
        me.apply=apply
        me.count=count
        me.enhance=enhance
        me.dataset=me.create_traindata()
        if resize==True:
            me.dataset=me.resizeIt(me.dataset)

        
        
    
    def resizeIt(me,traindata_array):
        resized_traindata=[]
        resized_traindata_temp=[]
        for img in traindata_array[0]:
            
            new_image_array=cv2.resize(img,(me.lheight,me.lwidth))
            resized_traindata_temp.append(np.array(new_image_array))
        array=[np.array(resized_traindata_temp),np.array(traindata_array[1])]
        return(array)



    def create_traindata(me):
        traindata=[]
        for cats in me.categories:
            n=0
            path=os.path.join(me.datadir,cats)
            class_num=me.categories.index(cats)
            for img in os.listdir(path):
                if(me.grayscale==True and me.enhance==True):
                    y=cv2.imread(os.path.join(path,img),cv2.IMREAD_GRAYSCALE)

                    y=cv2.resize(y,(512,512))


                    clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(5,5))
                    img_array = clahe.apply(y)

                    img_array = cv2.GaussianBlur(y,(3,3),1)


                    n=n+1
                    print(str(n)+" images loaded successfully",end='')
                    if n>=me.count:
                      break
                
                elif(me.enhance==True):
                    img_array=cv2.imread(os.path.join(path,img))

                    img_array=cv2.resize(img_array,(512,512))

                    img_yuv_1 = cv2.cvtColor(img_array,cv2.COLOR_BGR2RGB)

                    
                    img_yuv = cv2.cvtColor(img_yuv_1,cv2.COLOR_RGB2YUV)

                    y,u,v = cv2.split(img_yuv)

                    

                    clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(5,5))
                    y = clahe.apply(y)

                    y = cv2.GaussianBlur(y,(3,3),1)

                    img_array_1 = cv2.merge((y,u,v))
                    img_array = cv2.cvtColor(img_array_1,cv2.COLOR_YUV2RGB)
                    
                    n=n+1
                    print(str(n)+" images loaded successfully",end='')
                    if n>=me.count:
                      break
                else:
                    img_array=cv2.imread(os.path.join(path,img))

                    n=n+1
                    print(str(n)+" images loaded successfully",end='')
                    if n>=me.count:
                      break
                if(me.multiclass==False):
                    traindata.append([img_array,class_num])
                else:
                    traindata.append([img_array,me.classes(class_num=class_num,classes=len(me.categories))])
            print(len(traindata))
            print()
            
        if(me.shuffled==True):
          random.shuffle(traindata)
          print("shuffled")
        traindata_img=[]
        traindata_lab=[]
        for sets in traindata:
            traindata_img.append(sets[0])
            traindata_lab.append(sets[1])
        traindata=[traindata_img,traindata_lab]
        return(traindata)

    def classes(me,class_num,classes):
        array = [0 for i in range(classes)]
        array[class_num]=1
        return(array)

"""# **Training Phase**"""

#path of the folder containing subfolder with images
path="/content/drive/My Drive/SN images/New folder (3)"

#names of the subfolders
class_names = ['nosn','sn']

#function to load the dataset into the variable dataset
dataset=DataSet(path,categories=class_names,lheight=512,
                lwidth=512,grayscale=False,apply=None,
                count=1000,shuffled=True,multiclass=True,enhance=True)


#data contains the numpy image array
data=dataset.dataset
#this returns a shuffled numpy array with the format [[images][labels]] to data

print(type(dataset))
print(len(data))
print(len(data[1]))
print(data[0].shape)
print(len(data[1][:20]))

x=len(data[0])
test_sample_size=int(0.001*x)
train_sample_size=x-test_sample_size

#splitting the data into training set and test set,with test_sample_size being the percentage of total dataset for test set
(tr_img,tr_lab),(te_img,te_lab)=(data[0][:train_sample_size],data[1][:train_sample_size]),(data[0][train_sample_size:],data[1][train_sample_size:])

print(tr_img.shape)
print(tr_lab.shape)
print(te_img.shape)
print(te_lab.shape)
print(tr_lab)
print(te_lab)
plt.imshow(tr_img[18],cmap='gray')
plt.show()
print(tr_lab[0])

"""Custom Model"""

tr_img = tr_img.reshape(-1,512,512,3)

#defining our model ,the description of the model is provided separately
from tensorflow.keras.layers import Dropout
lesion_Classifier=Sequential()
lesion_Classifier.add(Convolution2D(16,(3,3),input_shape=(512,512,3),activation='relu'))
lesion_Classifier.add(MaxPooling2D(pool_size=(2,2)))
lesion_Classifier.add(Convolution2D(32,(3,3),activation='relu'))
lesion_Classifier.add(MaxPooling2D(pool_size=(2,2)))
lesion_Classifier.add(Convolution2D(64,(3,3),activation='relu'))
lesion_Classifier.add(MaxPooling2D(pool_size=(2,2)))
lesion_Classifier.add(Convolution2D(64,(3,3),activation='relu'))
lesion_Classifier.add(MaxPooling2D(pool_size=(2,2)))
lesion_Classifier.add(Convolution2D(128,(3,3),activation='relu'))
lesion_Classifier.add(MaxPooling2D(pool_size=(2,2)))
lesion_Classifier.add(Convolution2D(128,(3,3),activation='relu'))
lesion_Classifier.add(MaxPooling2D(pool_size=(2,2)))

lesion_Classifier.add(Flatten())
lesion_Classifier.add(Dense(512,activation='relu'))
lesion_Classifier.add(Dense(256,activation='relu'))
lesion_Classifier.add(Dense(2,activation='softmax'))

lesion_Classifier.compile(optimizer='adam',loss='categorical_crossentropy',metrics=['accuracy'])

#create a tensorboard callback for our model's training,with log dir being the location of the logs
log_dir = os.path.join(
    "logs",
    "fit",
    datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),
)
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)
#name for the tensorboard logs
name="images_ewith-sn-1".format(int(time.time()))

es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=10)

#training the model for 25 epochs with a validation set ,10% of the training set,and mapping the progress to tensorboard
history=lesion_Classifier.fit(tr_img,tr_lab,epochs=50,validation_split=0.1,callbacks=[tensorboard_callback,es])

# Commented out IPython magic to ensure Python compatibility.
# %tensorboard --logdir logs

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs = range(1, len(acc) + 1)
plt.plot(epochs, acc, 'b', label='Training acc')
plt.plot(epochs, val_acc, 'r', label='Validation acc')
plt.title('Training and validation accuracy')
plt.legend()
plt.figure()
plt.plot(epochs, loss, 'b', label='Training loss')
plt.plot(epochs, val_loss, 'r', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()
plt.show()

#saving the weights to h5 format
lesion_Classifier.save("parkinson first stage99.h5")
#model.save("model_vgg16_mypd_acc90.h5")

"""Pre-trained VGG16 model"""

from keras.applications import VGG16,InceptionResNetV2,InceptionV3,ResNet152,ResNet50,MobileNet,NASNetLarge
from keras.layers import Input,Dense,Flatten
from keras.models import Model
from keras import models

vggmodel = VGG16(weights='imagenet',include_top=False,input_tensor=Input(shape=(512,512,3)),classes=8)

vggmodel.trainable=False

model = models.Sequential()
model.add(vggmodel)
model.add(Flatten())
#model.add(Dense(1024,activation='relu'))
#model.add(Dense(512,activation='relu'))
model.add(Dense(124,activation='relu'))
model.add(Dense(2,activation='sigmoid'))

model.compile(optimizer='adam',loss='binary_crossentropy',metrics=['accuracy'])

history = model.fit(tr_img,tr_lab,epochs=100,validation_split=0.1,callbacks=[es])

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs = range(1, len(acc) + 1)
plt.plot(epochs, acc, 'b', label='Training acc')
plt.plot(epochs, val_acc, 'r', label='Validation acc')
plt.title('Training and validation accuracy')
plt.legend()
plt.figure()
plt.plot(epochs, loss, 'b', label='Training loss')
plt.plot(epochs, val_loss, 'r', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()
plt.show()

from sklearn import metrics
predictions = lesion_Classifier.predict_classes(data[0])

label = [int(np.where(r==1)[0][0]) for r in data[1]]

print(label)
print(predictions)

report = lesion_Classifier.classification_report(label,predictions)
confusion = lesion_Classifier.confusion_matrix(label,predictions,labels=[0,1])

print(report)
print(confusion)

print(model.summary())



#the prediction of all the images in the test set 'te_img' using the trained CNN
y_pred=lesion_Classifier.predict_classes(te_img)

labs=[]
#the confusion matrix based on the prediction in y_preds and the true labels stored in the 'te_lab'
for i in range(len(te_lab)):
    if(1 in list(list(te_lab)[i])):
        labs.append(list(list(te_lab)[i]).index(1))
    else:
        labs.append(0)

con_mat = tf.math.confusion_matrix(labels=labs, predictions=y_pred)

#con is the confusion matrix in numpy array format
con=con_mat.numpy()

print(con)
#visualize the confusion matrix 
plt.imshow(con)
plt.show()

#accuracy measurement matrics for the test set using the confusion matrix 'con'
metrics = dict()
metrics['fn']=con[0][1]
metrics['tn']=con[1][1]
metrics['tp']=con[0][0]
metrics['fp']=con[1][0]
metrics['sen']=tp/(tp+fn)
metrics['spe']=tn/(tn+fp)
metrics['jac']=tp/(tp+fp+fn)
metrics['dice']=(2*tp)/((2*tp)+fp+fn)
metrics['acc']=(tp+tn)/(tp+fn+tn+fp)
metrics['mcc']=((tp*tn)-(fp*fn))/(((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn))**0.5)

print(metrics)

print(te_lab)

n=0
#0=lesion ,1=normal
for i in range(len(te_lab)):
    print(list(list(te_lab)[i]))
    if(1 in list(list(te_lab)[i])):
        if(list(list(te_lab)[i]).index(1)==y_pred[i]):
        #checking if the predicted label and the true label is the same
            n=n+1
            print(list(list(te_lab)[i]).index(1),'  -  ',y_pred[i])

        
        else:
        #plotting the images which are falsely identified by our model
            print(' / ',list(list(te_lab)[i]).index(1),'  -  ',y_pred[i])
            plt.imshow(te_img[i])
            plt.show()
print((n/len(te_lab))*100)

"""# **Testing phase**"""

img_array=cv2.imread('...\images\test images\raw_brain_mri_w_sn.jpg')


img_array=cv2.resize(img_array,(512,512))

img_yuv_1 = cv2.cvtColor(img_array,cv2.COLOR_BGR2RGB)
plt.imshow(img_yuv_1)
plt.show()
                    
img_yuv = cv2.cvtColor(img_yuv_1,cv2.COLOR_RGB2YUV)

y,u,v = cv2.split(img_yuv)

                    

clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(5,5))
y = clahe.apply(y)

y = cv2.GaussianBlur(y,(3,3),1)

img_array_1 = cv2.merge((y,u,v))
img_array = cv2.cvtColor(img_array_1,cv2.COLOR_YUV2RGB)
plt.imshow(img_array)
plt.show()
test_im = img_array.reshape(-1,512,512,3)
print(class_names[lesion_Classifier.predict_classes(test_im)[0]])
anp = img_array[230:200+130,200:200+110]
plt.imshow(anp)