# Cloudmare

Cloudmare is a simple tool to find the origin servers of websites protected by Cloudflare, Sucuri, or Incapsula with a misconfiguration DNS.

For more detail about this common misconfiguration and how Cloudmare works, send me a private message.

Here's what Cloudmare looks like in action.

![Example usage](https://i.imgur.com/pSzOXFG.png "Example usage")

(_The websites and the IP addresses in this example have been obfuscated_)

## Setup

1) Clone the repository

```
git clone https://github.com/splitsploit/cloudmare.git
```

2) Go to the folder

```
cd Cloudmare
python Cloudmare.py -h or python Cloudmare.py -hh
```

3) Run Cloudmare (see [Usage](#usage) below for more detail)

```
python Cloudmare.py -u target.site --bruter -sC -sSh -sSt --host verified.site
```

(Remember to view -hh for more info about the arguments)

## Termux users

1) pkg upgrade && pkg update
2) pkg install git python libxml2 libxslt dnsutils
3) git clone [https://github.com/splitsploit/cloudmare.git](https://github.com/splitsploit/cloudmare.git)
4) cd Cloudmare
5) python Cloudmare.py -h or python Cloudmare.py -hh

```
Note: Be patient if the script requires to install modules.
```

## Usage

![Help options](https://i.imgur.com/9pmF1ol.png "Help options")

## Compatibility

Tested on Python=<3.7 (don't use Python 2 more), working on Linux and Windows. Feel free to [open an issue] if you have bug reports or questions. If you want to collaborate, you're welcome.

### Im not own this tools, i just cloned from mrh0wl. Big thanks to owner
