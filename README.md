# Timid

VERSION 002 (idk how to version stuff)

## A small programming language that has no reason to be

The third repo
> RIP to the [first one](https://github.com/mastersneeza/Timid) - got too messy<br/>
> RIP to the second one - lasted 10 minutes before deletion

Timid is a (small?) language.<br/>
Why does it exist? I dunno.<br/>
Do I want it to exist? Maybe.<br/>
Can it become useful? Possibly.<br/>

## Aim

To be able to quickly solve problems like tedious math homework in as little time as possible (as in runtime).<br/>
Also, to be able to compile once, and run anywhere using the Timid Runtime (like C# has its Common Language Runtime, or CLR) (what should I call it? TR? TIMIDR? TIRU?)

I NEED AN ICON OR LOGO HELP (see Development)

I NEED TESTERS THAT CAN FIND CRASHES (see Development)

## What's new (no one asked)

- Remove REPL (for now because screw the REPL)
- Automatic code execution after compilation
- Fixed assignment expressions
- Added syntax to ```syntax.txt``` for people who don't know Timid
- Move some files around
- Add special assignment operators ```+=```, ```-=```, ```*=```, ```/=```, ```%=```, ```^=```)
- Add makefile
- Add some more tests
- Add ```goto``` and ```labels:``` (still needs tweakin')
- Clean up command line interface, though it requires some more work
- Fix ```else if``` syntax
- Fix ```for``` statement in terms of leaving values on stack
- Expose null terminator string
- Fix floating point error for exponentiation (e.g. ```a ^ b```)
- Added ```continue``` statement
- Optimize strings using string interning
- Added ```break``` statement
- Added ```forever``` loop construct
- Added 'test' programs ( idk what sort of tests to make. just try them. )
- Added ```for``` loops
- Reworked string encoding in ```.timb``` binary files
- Removal of semicolon delimitter - Now you do not need to terminate statements with semicolons

## Features

- ```goto``` ( I love it )
- No semicolons (optional, they replace newlines)
- Arithmetic
- P R I N T I N G
- User input
- Simple types (int, float, bool, string, null)
- Block syntax and some scoping (```{}``` to surround statements)
- Control flow (```if```, ```while```, ```for```, ```forever```, ```break```, ```continue```)

## Coming soon (or maybe never)

- More restriction on types
- Functions and lambdas (once I figure out how to represent them in bytecode)
- Classes and other OOP (going to be copypasted from Crafting Interpreters)
- Better error handling and static analysis (```try``` and ```catch``` blocks, assertions ```|-```, user-accesible exceptions)
- More tests
- More static analysis
- String functions (sorting, searching, slicing)
- Collections (array, tuple, dictionary, stack) (strings kind of work like a collection. You can index them like ```string[index]```)
- More IO stuffs (file reading, idk)
- Imports and exports
- Typing and type annotations (maybe add ```const``` keyword too)
- A comprehensive guide to Timid
- Coroutines
- Networking
- Graphics library (what to use??? OpenGL? SDL?)
- UTF-8 encoded strings

Quotes from the creator (me):
> sex<br/>
> doit<br/>
> Quanlingling Dingle, Quandale Dingle, Dale Dingle, Quan Dingle, An Dingle

## References

I copypasted from

- [Crafting Interpreters](https://craftinginterpreters.com) - I'm too dumb
- [CodePulse](https://github.com/davidcallanan/py-myopl-code) - How I got into programming
- [Tsoding Daily's Porth](https://youtube.com/playlist?list=PLpM-Dvs8t0VbMZA7wW9aR3EtBqe2kinu4) - The decision to create bytecode
- A bunch of other people I've seen make languages 10000 times better

## Installation

```command
git clone https://github.com/mastersneeza/TimidTheThird
```

## Running

### Note

In order to run, you must have Python 3.10 or higher installed on your path

( I want to remove the dependency on Python in the future )

<s>CURRENTLY, TIMID MAKES A FILE CALLED ```mai1.timb``` THAT IS STORED IN YOUR WORKING DIRECTORY. I WILL CHANGE THIS SOON.</s>

### Compile a file

```command
$TimidTheThird~ python3 /Python/Timid.py -c path_to_file.timid
```

It will store the ```.timb``` file in the same directory as the ```.timid``` file

### Compile and run a file

```command
$TimidTheThird~ python3 /Python/Timid.py path_to_file.timid
```

### Make VM

To compile the vm just run

```command
make
```

### Execute a file on the C VM

```command
$TimidTheThird~ .\TimidRuntime path_to_file.timb
```

#### Example

Compile the ```goto.timid``` file:

```command
$TimidTheThird~ python3 Python\Timid.py -c Tests\goto.timid
```

Running it:

```command
$TimidTheThird~ .\TimidRuntime Tests\goto.timb
```

## Development

Timid wants logo. Timid wants power.<br/>

I need testers.<br/>
Help.
