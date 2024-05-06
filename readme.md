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
- -s: A stylesheet containing css to be inserted in-line into the HTML parsed from the markdown. Multiple stylesheets are inserted in the order they are given on the command line and can be specified like so:<br>`marksocket -s style1.css -s style2.css readme.md`
- -j: A file containing JavaScript to be inserted in-line into the head tags of the HTML document. Multiple files are inserted in the order they are given on the command line and can be specified like so:<br>`marksocket -j script1.js -j script2.js readme.md`

## Extensions

If the [markdown-mermaid](https://github.com/rauaap/markdown-mermaid) extension is found it is loaded automatically. Note that the extension itself will not render the Mermaid graphs. Include the Mermaid JavaScript library and an additional script that runs Mermaid when the document is reloaded.

### Example

Assume we have downloaded `mermaid.min.js` from a [CDN](https://cdn.jsdelivr.net/npm/mermaid/dist/) and also created a file `reload-mermaid.js` with the following contents:

```javascript
window.addEventListener('load', () => {
    const observer = new MutationObserver(() => mermaid.run());
    observer.observe(document.body, {childList: true});
});
```

Now marksocket could be called with said files to enable Mermaid graph rendering:<br>
`marksocket -j mermaid.min.js -j reload-mermaid.js readme.md`
