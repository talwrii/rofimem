# rofimem

A wrapper around [rofi](https://github.com/DaveDavenport/rofi)
to maintain a manually chosen list of items.

*Rofi* is called with the `-dmenu` option,
but has three new options `* new`, `* delete`, and `* edit`
that can be used to respectively add, remove, and modify entries

This projects is compatible with both Python2 and Python3.

# Installation

```
pip install git+https://github.com/talwrii/rofimem#egg=rofimem
```

# Usage

```
# Select an item from the default list
rofimem

# Select an item from a list called command
rofimem command
```
