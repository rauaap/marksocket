# Marksocket

![](logo.svg)

## What

A python script to parse and serve markdown documents to a browser with live reload.

## Why

Because people are out there importing entire HTTP servers and 300 npm packages just to have a markdown document reload in their browsers. I'm not about that life.

## How

- One external dependency: The markdown parser.<br>
`sudo apt install python3-markdown`
- Only ~140 lines of python powered by the standard library.
- Uses sockets, no HTTP server needed.
- It even serves the images!
- Doesn't work on Windows though. Not my problem.

## Usage

`marksocket [-h] [-p PORT] [-s STYLESHEET]... markdown_file`

### Example

`marksocket -p 8001 -s style.css readme.md`

### Options

- -h: Help.
- -p: The port to serve at. Defaults to 44444.
- -s: A stylesheet containing css to be inserted into the HTML parsed from the markdown. Multiple stylesheets are supported like so:<br>`marksocket -s style1.css -s style2.css readme.md`
