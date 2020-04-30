# BINGO!

A game we used to play all day long when we were
in schools, since fifth grade!

Visit the [site](https://bing-o.herokuapp.com/home "Play Bingo!")!

<!--images of the game-->


<!--history-->
## Installation

Honestly this is my first project that I've deployed on the web. Right now I don't know which is the best method to set this up and running in your machine, but I believe the following should just do fine:

Clone this repository:
```bash
git clone https://github.com/syed-saif/bing-o.git
```
I strongly recommend using a [virtual environment](https://pypi.org/project/virtualenv/ "Virtualenv"), which helps isolating different python environments for different projects. As a beginner myself, I found [Virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/ "Virtualenvwrapper") quite helpful as it helped me manage different virtualenvs easily.
Assuming you've installed [Virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/ "Virtualenvwrapper"), lets create a virtualenv that uses python 3.7. :
```bash
mkvirtualenv -p /path/to/python3.7 bingo
```
If this is confusing, take a look at this [thread](https://stackoverflow.com/questions/6401951/using-different-versions-of-python-with-virtualenvwrapper "Using different versions of python with virtualenvwrapper").  
 After setting up the virtualenv, `cd` to the directory where you cloned this repo. Then:
```bash
pip install -r requirements.txt
```
We're good to go! Before you run myapp.py
from your terminal, there is a small change to make.If you open the file in a text editor, you can that under the `if __name__ == '__main__':`  conditional,there is `app.run()`. Just change it to `socketio.run(app)` . Now if you run the myapp.py file from terminal, the application
should be hosted in the [localhost](http://localhost:5000)

Make sure you have the latest version of the browser you use!

## How you can contribute

Since this is my first project I've no idea how contributions work in Github. Also I don't have a clear picture of how I want the contributions to be. For now, making the site mobile responsive is challenging to me. So a little help there is appreciated! Also I would like to know how to simplify the installation for this app to get it up and running in others' local machines.

## A little back story :)

Back then, we used pen and paper to play this game. It was a simple turn-based game and the first one to finish would scream, "BINGO!!".
So first, we would create a 5X5 table and fill it with numbers starting from 1 to 25. The order didn't matter. Then each player would get a turn and in their turn, the player would stike off a number. Any number they wanted. Getting a row or a column or a diagonal of such striked numbers would result in a point. The first player to score five points would win and the next positions would be filled by other players. That was the game.

During this summer( a very strange one thanks to the pandemic ), my friends and I were in a group call and we tried to play the old-school Bingo with pen and paper. That didn't go so well as anyone could easily cheat and win. That day this idea came to my mind, "Why not try to build a similar game and make it online?". This is the result :)  

I went through a lot of struggle to get this thing running and still it has many flaws. But because of this project I learned a lot of web development
and now feel confident in this arena. If you see the previos commits, I actually used global variables in my script to store data, due to which the game didn't work at all :P .Then I realised that it was a bad system design and I had to re-design the system and store everything in a database. This is just one instance of how I screwed up. But it was fun. All of it.

Please do let me know some tips to present the README better. If you have trouble understanding the code do let me know. I'll update the Markdown as frequently as possible.

## My thanks
For this project, I used a quite a number of libraries/frameworks/technologies. This wouldn't have been possible if it wasn't for those amazing people who put in the time to create these libraries and frameworks and so on. So, here's a list of things I used:
* [Flask-socketio](https://flask-socketio.readthedocs.io/en/latest/ "Flask-socketio"), the backend framework.
* [Socket.io](https://socket.io/ "Socket.io"), the client-side JS library to work with WebSockets.
* [Redis](https://redis.io/ "Redis"), an amazing NoSQL DB which I used to store temporary values.
* [orjson](https://pypi.org/project/orjson/ "orjson"), the fastest python module to work with stringified JSONs.
* [Numpy](https://numpy.org/ "Numpy"),which greatly helped me with computations that involved 2d-lists.
* [Muuri JS](https://haltu.github.io/muuri/ "muuriJS"),an amazing JS library to create responsive, draggable grid layout, which I repurposed to contain buttons rather than images :P
* [Sweetalert](https://sweetalert.js.org/docs/ "Sweetalert"), for those sweet alerts as opposed to regular JS alerts!

If you came this far, I wanna thank you for taking the time to read this. Do star this repo :P
