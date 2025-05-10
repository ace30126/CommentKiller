# CommentKiller

CommentKiller is a user-friendly desktop application designed to remove comments from source code. It provides a simple graphical interface to paste your code, select the programming language, and get a cleaned version without comments. The tool supports multiple languages through an external JSON configuration and includes a handy backup feature for your original code.

## Features

* Graphical User Interface (GUI): Easy-to-use interface with side-by-side text areas for input (original code) and output (comment-free code).
* Multi-Language Support: Handles various programming languages. Language definitions, including regular expressions for comments and string literals, are configurable via an external `languages.json` file.
* Smart Comment Removal: Attempts to preserve comment-like syntax within string literals, focusing on removing actual code comments.
* Automatic Backups: Automatically saves the original code (from the input text area) to a `.txt.back` file in the `comment_killer_backups` directory before any processing. Backup filenames include a timestamp and the selected language.
* Processing Log: Keeps a log of all processing operations, including the timestamp, selected language, and the name of the created backup file. This log is stored as `comment_killer_processing_log.txt` in the `comment_killer_backups` directory.

## Prerequisites
* Python 3.x
* Dev environment : Python 3.13.3

## Running the Application

1.  Ensure you have Python 3 installed on your system.
2.  Clone this repository or download the `comment_killer.py` script and the `languages.json` file.
3.  Place `CommentKiller.py` and `languages.json` in the same directory.
4.  The application will automatically create a `comment_killer_backups` subdirectory in this location when it first runs (if it doesn't already exist).
5.  Run the script from your terminal:
    ```bash
    python CommentKiller.py
    ```

## Using the Interface

1.  Language Selection: Choose the programming language of your source code from the dropdown menu at the top. The available languages are populated from the `languages.json` file.
2.  Input Code: Paste your source code into the left-hand text area ("주석이 있는 원본 코드" / "Original Code with Comments").
3.  Remove Comments: Click the "주석 제거 실행!" ("Remove Comments!") button.
4.  View Output: The code with comments removed will appear in the right-hand text area ("주석 제거된 코드" / "Comment-Free Code"). This area is read-only.
5.  Backups & Log:
    * Each time you click "Remove Comments!", the original content from the input text area is backed up.
    * Backup files are named with a timestamp and language (e.g., `backup_YYYYMMDD_HHMMSS_MS_Python.txt.back`).
    * You can find these backups and the `comment_killer_processing_log.txt` in the `comment_killer_backups` directory, located in the same folder as the script.
    * A confirmation message will appear after processing, indicating the result and backup status.

## Configuring Language Support (`languages.json`)

CommentKiller's power and flexibility in handling different languages come from the `languages.json` file. This file allows you to define or modify how comments and strings are identified for each language using regular expressions.

### Structure

The `languages.json` file is a JSON object where:
* Each top-level key is a language name (e.g., "Python", "React (JSX)"). This name appears in the application's dropdown menu.
* The value for each language key is an object containing two main properties:
    * `"strings"`: An array of strings, where each string is a regular expression pattern designed to identify string literals in that language. The order of patterns in this array can be important (e.g., patterns for multi-line strings or strings with specific prefixes should often come before more general string patterns).
    * `"comments"`: An array of arrays. Each inner array represents a comment type and should contain two strings:
        1.  A descriptive name for the comment type (e.g., "single_line", "jsx_specific_comment").
        2.  A regular expression pattern string to identify that type of comment.
        The comment patterns are applied in the order they appear in this list.

### Example Snippet:

```json
{
  "Python": {
    "strings": [
      "r\\\"\\\"\\\"[\\s\\S]*?\\\"\\\"\\\"",
      "r'''[\\s\\S]*?'''",
      "\\\"(?:\\\\.|[^\\\"\\\\])*?\\\"",
      "'(?:\\\\.|[^'\\\\])*?'"
    ],
    "comments": [
      ["docstring_comment", "(\\\"\\\"\\\"[\\s\\S]*?\\\"\\\"\\\"|'''[\\s\\S]*?''')"],
      ["single_line", "#.*"]
    ]
  },
  "React (JSX)": {
    "strings": [
      "\\\"(?:\\\\.|[^\\\"\\\\])*?\\\"",
      "'(?:\\\\.|[^'\\\\])*?'",
      "`(?:\\\\.|[^`\\\\])*?`"
    ],
    "comments": [
      ["jsx_specific_comment", "\\{\\/\\*[\\s\\S]*?\\*\\/\\}"],
      ["multi_line_js", "/\\*[\\s\\S]*?\\*/"],
      ["single_line_js", "//.*"]
    ]
  }
}
