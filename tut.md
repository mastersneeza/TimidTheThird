# A comprehensive guide to Timid

## Syntax

See ```syntax.txt``` for the formal grammar because I suck at explaining

## The actual tut

### Your first "Hello, world!" program

Timid is a dynamicaly-typed, semicolon free, block based language.
This means no need for typed variables, semicolons, and indentations to mark blocks.

To create a hello world program, create a file, call it anything you want but for this 'tutorial' we'll call it ```hw.timid```.<br/>
Store it wherever you like, but I'm going to put it in the ```Examples``` directory.

Now, on the first line, type in
```print "Hello, world!"```

To run it, go to the base directory and run

```python3 Python/Timid.py Examples/hw.timid```

It should print ```Hello, world!```. Well done! You have just run your first hello world program.

### Data types

Timid currently supports 5 simple data types:

- ```integer```
- ```float```
- ```bool```
- ```string```
- and ```nul```

Timid is dynamically typed, and is pretty lax on operations.

For example:

- ```"Hello " + 123``` yields ```Hello 123``` without any errors
- ```tru + 3``` yields ```4``` because ```bool``` can act like an ```integer```

Why did I do this? Because I don't have string interpolation or functions yet, and its also annoying not being able to easily construct ```string```s.

### Variables

To define a variable, you use the ```$``` sign.

Example:
```$ name = "Amongus"```

will create a variable called ```name``` that stores the value ```Amongus```.

To use variables, we simply reference their name. For example:

```print "My name is " + name```

will print ```My name is Amongus```.

We can store anything in a variable. We can also set a variable's value to the result of an expression.
e.g.

```timid
$ a = 3
$ b = 4
$ cSquared = a^2 + b^2
$ hypotenuse = cSquared ^ 0.5
print "Hypotenuse is " + hypotenuse
# Outputs Hypotenuse is 5
```

I will add constants using the ```const``` keyword in the future

### Comments

Single-line comments start with a ```#``` and span the rest of the line

```# I am a single line comment```

Multi-line comments start with a ```#~``` and span until another ```~``` is encountered

```timid
#~
    I
    am
    a
    multi
    line
    comment
~
```

Currently, nested multi-line comments are not supported
