# Field of view estimation

Field of view estimation for MRI experiments.

In the case you do an MRI experiment and you want to quickly estimate the field of view of your screen inside the bore, this code is what you need!

### What it does? 

It draws a polygon (a "circle" to begin) that you can easily modify moving every vertex, far or near the centre.
Before an experiment it should not take so much time to draw your field of view (take a look at `demo.mp4`).
 
Once finished, a B/W mask is saved as `png`, along with vertex coordinates in the `log` file.

The code allows you to change easily the number of verteces (`Points_polygon = 10`) and the intial positions respect to the centre (`Radius_polygon = 0.9`).

<p align="center">

<img src="https://github.com/rockNroll87q/Field-of-view-estimation/blob/master/demo.gif" width="306" height="191" />  

</p>

See the [video](https://github.com/rockNroll87q/Field-of-view-estimation/blob/master/demo.mp4) for a demo.

### How to use it

* Run with `python ./fow_finder.py` or IDE;
* With keyboard `left` and `right` you select the vertex you want to move (enlightened in red);
* Increase or decreare distance from center with `up` and `down` keys;
* Press `Esc` o `q` to finish.


### What you need to run it?

* Python2.x (3.x should work as well) 
* Psychopy ([link](http://www.psychopy.org/))
* a Keyboard :D
