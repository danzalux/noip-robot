## Script to auto confirm noip.com free hosts

Updated 12 Aug 2025

free hosts expire every month. This simplified script auto clicks web pages to renew the hosts, using Python/Selenium with Firefox headless mode.

## noip-robot

### =>> Clone this repo <<=

Go to your project-folder (or create) and type:

`git clone https://github.com/danzalux/noip-robot.git`

*Or just pull code from repository to get updates(Stay in project-folder):*

`git pull https://github.com/danzalux/noip-robot.git`

### Build docker-image (stay in cloned folder - you need Dockerfile):

`docker build . -t noip-robot`

### Start container:

`docker run --rm -it noip-robot NOIPusername password`

Or optional just start container with enhanced trace-output:

`docker run --rm -it noip-robot NOIPusername password trace`

(Just word "trace" as last parameter is enough)

With <code>--rm</code> the container will automatically remove when it exit.

`-it` is short for `--interactive` + `--tty`. When you docker run with this command it takes you straight inside the container.

## Linux-Cron (simple variant usage:"crontab -e" in Terminal):

`0 9 */3 * * docker run --rm noip-robot NOIPusername password`

Run at 09:00 on every 3rd day-of-month. (for every Day 9:00 just leave * - `0 9 * * * ...`)

Or run with output to file:

`0 9 */3 * * docker run --rm noip-robot NOIPusername password >> /directory/path/file.log`

`crontab -l` (view the contents of your crontab in Terminal)

[https://crontab.guru/#0_9_*/3_*_*](https://crontab.guru/#0_9_*/3_*_*)

[https://www.digitalocean.com/community/tutorials/how-to-use-cron-to-automate-tasks-ubuntu-1804](https://www.digitalocean.com/community/tutorials/how-to-use-cron-to-automate-tasks-ubuntu-1804)

__
### For deleting some images after tests:

`docker image rm noip-robot[:latest]`

`docker images` (to check existing)

`docker image ls` (it is the same)

### Note:
The script is not designed to renew/update the dynamic DNS records, but only to renew the hostnames expiring every 30 days due to the free tier. Check noip.com documentation for that purpose. Most wireless routers support noip.com .

This is an up-to-date mixed fork based on `loblab/noip-renew` and `simao-silva/noip-renewer` repository as it seems it's not anymore actively developed. Feel free to contribute!

___
