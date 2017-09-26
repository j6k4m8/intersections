# intersections

Generate stylized maps of horrible intersections in your city.

## Inspiration
Check out [this amazing work](https://www.etsy.com/listing/540156360/intersections-of-seattle-minimalist-map?ref=shop_home_active_1) by Peter Gorman at BarelyMaps. This project is a poor emulation of this beautiful design!

## Demo
[![image](https://user-images.githubusercontent.com/693511/30840934-f681fac8-a247-11e7-9de0-610fce48ccc7.png)](https://jordan.matelsky.com/sketch/intersections/)

[Demo](https://jordan.matelsky.com/sketch/intersections/)

## Configuration

Install the requirements:

```shell
pip install -r requirements.txt
```

## Usage

    $ ./main.py [city [count]]

For example,

    $ ./main.py Boston 123

will generate 123 images of intersections in Boston.

    $ ./main.py Boston

will default 100. 

    $ ./main.py

with NO arguments will default to Baltimore.
