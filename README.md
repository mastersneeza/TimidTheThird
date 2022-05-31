# Timid

### A small programming language that has no reason to be

The third repo
> RIP to the [first one](https://github.com/mastersneeza/Timid) - got too messy<br/>
> RIP to the second one - lasted 10 minutes before deletion

Timid is a (small?) language.<br/>
Why does it exist? I dunno.<br/>
Do I want it to exist? Maybe.<br/>
Can it become useful? Possibly.<br/>

I NEED AN ICON OR LOGO HELP (see Development)

## What's new (no one asked)

- Added ```for``` loops
- Reworked string encoding in ```.timb``` files
- Removal of semicolon delimitter - Now you do not need to terminate statements with semicolons

## Features

- Arithmetic
- P R I N T I N G
- User input
- Simple types (int, float, bool, string, null)
- Block syntax (```{}``` to surround statements)
- Control flow (```if```, ```while```, ```for```) (I might add a ```forever``` block)
- Assertions (```|- condition error_msg```)
- That's it (what???)

## Coming soon (or maybe never)

- Better command line interface (options, flags, lists of files to run, where to save the ```.timb``` file, etc)
- Functions and lambdas (once I figure out how to represent them in bytecode)
- Classes and other OOP (going to be copypasted from Crafting Interpreters)
- Better error handling and static analysis
- String functions
- Collections (array, tuple, dictionary, stack)
- More IO stuffs (file reading, idk)
- Imports and exports
- Typing and type annotations (maybe add ```const``` keyword too)
- Coroutines
- Networking
- Graphics library (what to use???)
- UTF-8 encoded strings

Quotes from the creator (me):
> sex<br/>
> doit

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
Help.
