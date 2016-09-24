# Websites Up

*Websites Up* checks a list of URLs by simply pulling them via urllib. Optionally you can send an email via SMTP to a specified address in case of errors. *Websites Up* uses click to work as a command line tool.

## Command Line Options

| Option                 | Description |
|---|---|
| --urls                 | Path to a file containing the list of URLs seperated by newlines |
| --seconds (default=3)  | Timeout parameter sent to urllib (i.e. seconds to wait after which the request is cancelled). |
| --settings             | Path to a file containing settings for the SMTP server. |
| --email                | E-Mail address that receives notifications in case of errors. |

## Examples

```sh
python websites_up.py --urls urls.txt
```
Pulls the URLs specified in *urls.txt* and prints the results in the terminal.

```sh
python websites_up.py --urls urls.txt --seconds 5
```
Pulls the URLs specified in *urls.txt* with a timeout of *5 seconds*.

```sh
python websites_up.py --urls urls.txt --settings ~/settings.txt --email me@email.com
```
Pulls the URLs specified in *urls.txt* and sends error notifications to *me@email.com* via an E-Mail address whose SMTP server settings and account credentials are stored in *~/settings.txt*.
