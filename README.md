# rofimem

A wrapper around [rofi](https://github.com/DaveDavenport/rofi)
to maintain a manually chosen list of items.

*Rofi* is called with the `-dmenu` option,
but has three new options `* new`, `* delete`, and `* edit`
that can be used to respectively add, remove, and modify entries

# Installation

```
pip install 
```

# Usage

```
# Select an item from the default list
rofimem

# Select an item from a list called command
rofimem command
```
