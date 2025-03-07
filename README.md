# VHDL93 Docset for Zeal & Dash

https://var7600.github.io/VHDL93-Docset/



https://github.com/user-attachments/assets/4097d2e2-9abb-433d-81b7-eed21985d89c



## Overview

The **VHDL93 Docset** provides offline access to VHDL-93 documentation for users of [Zeal](https://zealdocs.org/) and [Dash](https://kapeli.com/dash). This docset includes **syntax references, examples, and explanations of key VHDL concepts.**

## Features

- 📚 **Comprehensive Documentation**: Covers VHDL-93 syntax and usage.
- 🔍 **Fast Search**: Easily find definitions and references.
- 🎨 **Syntax Highlighting**: Uses Prism.js for improved readability.
- ⚡ **Offline Access**: Works seamlessly within Zeal and Dash.

## Installation

### **Zeal Users**

1. Open Zeal and go to `Edit > Preferences > Docsets > User Contributions`.

2. Click `Add Feed` and enter the following URL:
   
   ```
   https://Var7600.github.io/VHDL93-Docset/VHDL93.xml
   ```
   
   

3. Click `OK` and then `Download` the docset.

### **Dash Users**

1. Open Dash and go to `Preferences > Downloads > User-Contributed`.

2. Click the `+` button and add the following feed:
   
   ```
   https://Var7600.github.io/VHDL93-Docset/VHDL93.xml
   ```
   
   

3. Download the docset and start using it.

## Manual Installation

Alternatively, you can download the docset manually:

1. Download the latest `.zip` file from the [Releases](https://github.com/Var7600/VHDL93-Docset/releases).
2. Extract the `.zip` file and move `VHDL93.docset`**to Zeal’s or Dash’s docsets directory.**

## Building the Docset

To build the docset yourself:

```bash
website2docset.py -n VHDL93 -v 0.0 -i icon.png HDL-Docs\

    # VHDL93: the name for the Docset to create
    # 0.0: the Docset version
    # icong.png: the icon to add to the Docset
    # HDL-Docs: the HTML,CSS,JS directory

## it will generate the VHDL93.docset
```

## after you can build the .zip

```bash
# with zip in Linux
zip -r VHDL93.zip VHDL93.docset
# OR with 7zip in Windows
7z a -tzip VHDL93.zip VHDL93.docset
```

## Contributing

Contributions are welcome! Feel free to submit issues, pull requests, or suggestions.

## License

This project is licensed under the MIT License.

---

📢 **Follow the project for updates and improvements!** 🚀
