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

`marksocket [-h] [-c CONFIG_FILE] [-p PORT] [-s STYLESHEET]... [-j JAVASCRIPT]... markdown_file`

### Example

`marksocket -p 8001 -s style.css readme.md`

### Options

- -h: Help.
- -c: Configuration file.
- -p: The port to serve at. Command line argument takes precedence over the port specified in the configuration file. Defaults to 44444 if not specified on the command line or in the configuration file.
- -x: A [Python-Markdown extension](https://python-markdown.github.io/extensions/) to be loaded by the markdown parser. Multiple extensions can be specified like so:<br>
`marksocket -x fenced_code -x codehilite -x markdown_mermaid readme.md`
- -s: A stylesheet containing css to be inserted in-line into the HTML parsed from the markdown. Multiple stylesheets are inserted in the order they are given on the command line and can be specified like so:<br>`marksocket -s style1.css -s style2.css readme.md`
- -j: A file containing JavaScript to be inserted in-line into the head tags of the HTML document. Multiple files are inserted in the order they are given on the command line and can be specified like so:<br>`marksocket -j script1.js -j script2.js readme.md`

## Configuration file

Allows specifying the port, stylesheet and javascript options. If the path to a configuration file is not given as a command line argument with the `-c` option, `~/.config/marksocket/config.toml` is looked for one. However both are optional and no configuration file is required to use the program. The command line option takes precedence over the default location, so the default configuration file in `~/.config/marksocket/config.toml` will not be loaded if the configuration file option `-c` is specified.

The configuration file is written in TOML. All values in it are optional. You can specify any or none of them. It has the following schema:

```
port = int
javascript = [ str ]
stylesheet = [ str ]
```

Example:

```toml
port = 8000
javascript = [ 'mermaid.min.js', 'reload-mermaid.js' ]
stylesheet = [ 'style.css' ]
```

### Order of the javascript and stylesheet files

Command line options for loading javascript files (`-j`) and stylesheet files (`-s`) can both be used simultaneously with `javascript` and `stylesheet` options in the configuration file. The order the files are loaded in is as follows:

1. JavaScript files specified in the configuration file, in the order they are specified.
2. JavaScript files specified on the command line, in the order they are specified.
3. Stylesheet files specified in the configuration file, in the order they are specified.
4. Stylesheet files specified on the command line, in the order they are specified.

## Extensions

If the [markdown-mermaid](https://github.com/rauaap/markdown-mermaid) extension is found it is loaded automatically. Note that the extension itself will not render the Mermaid graphs. Include the Mermaid JavaScript library and an additional script that runs Mermaid when the document is reloaded.

### Example

Assume we have downloaded `mermaid.min.js` from a [CDN](https://cdn.jsdelivr.net/npm/mermaid/dist/) and also created a file `reload-mermaid.js` with the following contents:

```javascript
let scrollPos;

window.addEventListener('scroll', (e) => {
    // Only save on user initiated scrolls
    if (!e.isTrusted) {
        return;
    }

    scrollPos = window.scrollY;
});

window.addEventListener('load', () => {
    const observer = new MutationObserver(async () => {
        await mermaid.run();
        window.scrollTo(0, scrollPos);
    });

    observer.observe(document.body, {childList: true});
});
```

Now marksocket could be called with said files to enable Mermaid graph rendering:<br>
`marksocket -j mermaid.min.js -j reload-mermaid.js readme.md`
