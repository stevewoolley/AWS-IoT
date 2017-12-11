# Smart Home via Raspberry Pies and AWS IoT

My goal is to secure, automate, and smartify my home with a bevy of Raspberry Pies,
 Amazon's Internet of Things (IoT) cloud, and some (relatively) cheap electronic parts.
 Since python seems to be the language of choice when dealing with Raspberry Pies, I'll be using it and
 some bash scripting to make it work.
 
##### Why Raspberry Pi? Couldn't I just pay some company do make my house a 'Smart Home'?
Probably could pay some company like Time Warner to do the work but...
* don't want to pay Time Warner one more penny than I have to
* I like to tinker. Many times, I'll show my wife that I can turn on an LED via a Pi or the Internet. She'll reply, so you spent a $100 on parts and you are now able to turn on that little light, congrats!
 
##### Why [Amazon IoT](https://aws.amazon.com/iot)?
Although there are a number of IoT services out there, I use [Amazon AWS](https://aws.amazon.com) services in my day job so I'll stick with that.
 
##### Deployment
I'll be using [Ansible](https://www.ansible.com) to automate deployment of my code. I've used it before....no reason to change here.

## Defaults
Not that you can't use other technologies and versions in your solution, but compatibility and functionality may vary.
* [Python 2.7](https://www.python.org)
* [Raspberry Pi Hardware: B+/2/3/Zero](https://www.raspberrypi.org)
* [Raspberry Pi OS: Raspbian Jessie Lite](https://www.raspberrypi.org/downloads/raspbian)

## Overarching Goals
* Control/View everything via the Internet or mobile app
* Adding control does not take away manual methods (additive not replacement). In other words, allowing a Raspberry Pi to control the garage door does not remove the existing manual control of the garage door opening remotes or switch.

## Smart Garage

###### Goals
* Display garage door status (up or down)
* Control opening and closing garage door
* Sense if garage door is open or closed. Store results in Amazon DynamoDB. 
* Notification if garage door up after 9:00pm (one of us forgot to close it)
* Detect movement in garage and turn on light
* Record video of movement. Store video files in Amazon S3.
* Electronic Tennis Ball: Visual alarm when car is too close to front of garage. 

## Security

###### Goals
* Turn on/off security monitoring remotely
* Provide multiple types of alerting (SMS, email, lights, etc.)
* Provide ability to 'chirp' on door open
* Tie into existing cabling for existing alarm system/wiring
* Use loud alarm horn

## Video Monitor

###### Goals
* Record video triggered by movement
* Store videos on Amazon S3
* Generate a 'summary' snapshot of a video for publishing on a web page
* Allow a remote user to take a snapshot on demand
* Turn on/off recording via a schedule or remotely


## Pi Monitor

###### Goals
* Record Raspberry Pi hardware and network metrics including:
  * CPU Utilization
  * Memory Utilization
  * Wireless and Ethernet network/IP Address
  * CPU temperature
  * Disk space utilization
  * uptime
  * process count
* Store information in Amazon DynamoDB
* Graph long term metrics
* Periodica cleanup old data values from DynamoDB
