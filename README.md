## Script to auto confirm noip.com free hosts

free hosts expire every month. This simplified script auto clicks web pages to renew the hosts, using Python/Selenium with Firefox headless mode.

## noip-robot

### >> Clone this repo <<

`git clone https://github.com/danzalux/noip-robot.git`

### Build docker-image (stay in cloned folder - you need Dockerfile):

`docker build . -t noip-robot`

### Start container:

`docker run --rm -it noip-robot NOIPusername password`

## Linux-Cron (simple variant usage:"crontab -e"):

`0 9 */3 * * docker run --rm noip-robot NOIPusername password`

At 09:00 on every 3rd day-of-month.

Or run with output to file:

`0 9 */3 * * docker run --rm noip-robot NOIPusername password >> /directory/path/file.log`

`crontab -l` (view the contents of your crontab)

[https://crontab.guru/#0_9_*/3_*_*](https://crontab.guru/#0_9_*/3_*_*)

[https://www.digitalocean.com/community/tutorials/how-to-use-cron-to-automate-tasks-ubuntu-1804](https://www.digitalocean.com/community/tutorials/how-to-use-cron-to-automate-tasks-ubuntu-1804)

__
### For deleting some images after tests:

`docker image rm noip-robot[:latest]`

`docker images` (to check existing)

`docker image ls` (it is the same)

### Note:
The script is not designed to renew/update the dynamic DNS records, but only to renew the hostnames expiring every 30 days due to the free tier. Check noip.com documentation for that purpose. Most wireless routers support noip.com .

This is an up-to-date fork of loblab/noip-renew repository as it seems it's not anymore actively developed. Feel free to contribute!

___
