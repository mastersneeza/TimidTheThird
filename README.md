# Timid

### A small programming language that has no reason to be

The third repo
> RIP to the [first one](https://github.com/mastersneeza/Timid) - got too messy

> RIP to the second one - lasted 10 minutes before deletion

Timid is a (small?) language
Why does it exist? I dunno.
Do I want it to exist? Maybe.
Can it become useful? Possibly.

## What's new (no one asked)

- Removal of semicolon delimitter - Now you do not need to terminate statements with semicolons

## Features

- Arithmetic
- P R I N T I N G
- User input
- Simple types (int, float, bool, string, null)
- Control flow (why wouldn't it have it?)
- Assertions
- That's it

## Coming soon (or maybe never)

- Functions and lambdas (once I figure out how to represent them in bytecode)
- Classes and other OOP (going to be copypasted from Crafting Interpreters)
- Better error handling and static analysis
- String functions
- Collections (array, tuple, dictionary, stack)\
- More IO stuffs
- Imports and exports
- Typing and type annotations
- Coroutines
- Networking
- Graphics library
- Unicode strings

Quotes from the creator (me):
> sex
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

Help.
