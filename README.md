Goals
-----

1. **Composability** simple commands can be put together
2. **Transparency** all data has to be transparent to the user
3. **Usefulness** has to provide an advantage


Command Execution Mechanics
---------------------------

### Generate input
In this step the commands arguments are created.
E.g. autocompletion etc. can be done here.
Retunred value is a Python-Dict (in case of `.py` file)
or a JSON-string (in case of `.sh` file)

first try to find
`[command]-input.py`

if not found use: `[command]-input.sh`

### Execution
`[command]-execute.py` or `[command]-execute.sh` will
get the input-data generated in the previous step as a single
input argument.

### Output-Display


`[command]-display.py` or `[command]-display.sh` can
be used for giving a custom renderer of the output-data from
the previous step. The returned data can be:
* a glade-xml like file or string: glade-content will be build and displayed
* html file or string: yTerm will use WebKit to render it
* image file or buffer: yTerm will render the image

when using a `.py` file it is also possible to:
* return a `GtkWidget`: the Widget will be rendered
* return a `Cairo-Frame`?????

this stage should only display data and *never* manipulate it.
(This is necessary for the goal of transparency)

Command Discovery
-----------------

A new environment-variable `YPATH` is used to find all commands
that support yTerm natively.

If not found, a Bash-Shell is started and the command is
executed there.

Compatabiliy
------------

since the yTerm command structure adds a lot of semantics
it is accually quite easy the make it backwards-compatible

The `ascii-format`-command can convert the given input
into an ascii-art type representation. E.g. data-format table
will be converted so tabbed, newlined text) and a tree-stucture
will be converted to something like the output of `tree`.

Pipeing
-------

For composability it is crucial to have a solid system for pipeing.
yTerm uses the following:

if one command is piped into a nother like
```bash
$ first | second
```

yTerm would expand it into:
```bash
$ first-input | first-execute | first-display
| second-input | second-execute | second-display
```

`first-display` and `second-input` are unneccesary so they are ommited..
This will give the following command:
```bash
$ first-input | first-execute | second-execute | second-display
```

In general the following holds true: the first one will do -input and the last one will do -display

the `>` and `<` operators work similarily:
they will parse the output, but will omit the displaying-stage at the end.


Alternative Renderers
---------------------

sometimes to commands default renderer is not the wanted one.

Alternative Renderes a commands with the following properties:
```
[command]-input = id
[command]-execute = id
[command]-display = [something interesting here]
```

### Example

Let's say we want to display the output of `foo` in a different manner
using the alternative renderer `altrenderer`. This would look like this

```bash
$ foo | altrenderer
```

will expand to:


```bash
$ foo-input | foo-execute | altrenderer-execute | altrenderer-display
```

since `altrenderer-execute` does not do anything:

```bash
$ foo-input | foo-execute | altrenderer-display
```

as you can see, we basically replaced the foo-display
 with altrenderer-display.

### Raw-Renderer

For the goal of transparency the user needs to see *all* data, that is
created by the execution-stage. Since the graphical representation can
omit data or display it poorly, the user need a second way to see all data.

#### Definition of raw:
```
raw-display x = encode_as_text(x)
```

