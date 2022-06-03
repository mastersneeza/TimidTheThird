# Timid

VERSION 001 (idk how to version stuff)

### A small programming language that has no reason to be

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

- No semicolons (optional, they replace newlines)
- Arithmetic
- P R I N T I N G
- User input
- Simple types (int, float, bool, string, null)
- Block syntax (```{}``` to surround statements)
- Control flow (```if```, ```while```, ```for```, ```forever```, ```break```, ```continue```)
- Assertions (```|- condition error_msg```) (only in the Python version because I cant do C)
- That's it (what???)

## Coming soon (or maybe never)

- Better command line interface (options, flags, lists of files to run, where to save the ```.timb``` file, etc)
- G O T O
- Functions and lambdas (once I figure out how to represent them in bytecode)
- Classes and other OOP (going to be copypasted from Crafting Interpreters)
- Better error handling and static analysis (```try``` and ```catch``` blocks, user-accesible exceptions)
- More tests
- String functions (sorting, searching, slicing)
- Collections (array, tuple, dictionary, stack) (strings kind of work like a collection. You can index them like ```string[index]```)
- More IO stuffs (file reading, idk)
- Imports and exports
- Typing and type annotations (maybe add ```const``` keyword too)
- A comprehensive guide to Timid
- Coroutines
- Networking
- Graphics library (what to use???)
- UTF-8 encoded strings

Quotes from the creator (me):
> sex<br/>
> doit<br/>
> "Quandale Dingle is my lord an saviour. He allowed me to see all the things you are not allowed to see. I also found my father, and gained 1 000 000 000 dollars"<br/>
> sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus sus 

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

### Run the REPL

### Note

In order to run, you must have Python 3.10 or higher installed on your path

( I want to remove the dependancy on Python in the future )

CURRENTLY, TIMID MAKES A FILE CALLED ```mai1.timb``` THAT IS STORED IN YOUR WORKING DIRECTORY. I WILL CHANGE THIS SOON.

```python
py TimidTheThird/Python/Timid.py
```

### Compile a file

```python
py TimidTheThird/Python/Timid.py path_to_file.timid
```

### Make VM

I will add a Makefile sometime in the future

```command
gcc TimidTheThird/C/*.c -o Timid
```

### Execute a file on the C VM

```command
.\Timid path_to_file.timb
```

## Development

Timid wants logo. Timid wants power.<br/>

I need testers.<br/>
Help.
