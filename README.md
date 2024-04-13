## Kaleidoscope: Automated, Distributed, Online Rotoscoping
ECE49595OSS Senior Design Project

Cole Kingery, Will Stonebridge, Connor Hise

Rotoscoping is a popular yet expensive and tedious method to animate live video. Using a famous Neural Style Transfer Algorithm known as CycleGAN, we have automated this process and made it available to anyone who visits our website.

There are three main components to our project: 
  - Automated Rotoscoping
  - WebApp
  - Kubernetes

Automated Rotoscoping is effectively an altered version of the CycleGAN repository. We have made three main adjustments. We have introduced a dataloader that scales and preprocesses videos. We have introduced functions that split the video into its component sounds and frames for stylization and then stitch it back together. Lastly, we have introduced a function "stylize_video" that loads in a CycleGAN model with our configuration and then uses our other introductions to automate rotoscoping.  #####TRAIN ON THE VIDEO!!!!!!!!

The web app is a Django API. In addition to integration with stylized video, there are three other connections at work: Firebase, s3, and Kubernetes. Firebase is used for authentication and video queueing. s3 stores video and passes it between our Web (the API) and ML instances. Finally, Kubernetes is used to manage the Instances that stylize the actual video. 

Kubernetes is our solution to the problem that Video queueing is extremely computationally (and financially) expensive. It would be infeasible for us to afford constant hosting on a single AWS GPU instance (costs are upwards of $50 a month). Additionally, doing all of our processing on a single instance creates a bottleneck if, say, multiple users desire to stylize a video at the same time. Kubernetes allows us to sidestep this problem by creating instances only when they are needed. The resulting scripts in our Directory allow us to do exactly that. 
