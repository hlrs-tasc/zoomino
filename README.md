# Zoomino
**Note: zoomino.py is deprecated, since all JWT apps have been deactivated by ZOOM. You may find more information [here](/https://developers.zoom.us/docs/internal-apps/jwt-app-migration/).**

----

Zoomino is a Python script to easily manage Zoom licenses in a joint Zoom
account, where there are fewer licenses available than users. This works only
with a Zoom account with at least one paid license and multiple users (free or paid).
Additionally, basic meeting management is available.

**Note:** Zoomino is based on *cooperative* use. Since there are no
authorization mechanisms beyond basic authentication, it relies on users not
abusing their powers.

**Update 2022-09-01:** Due to a restriction in the Zoom API, it is not possible
to retrieve a user's host key via the API anymore. See also
[here](https://devforum.zoom.us/t/alternatives-to-using-the-host-key/74422) for
more information.


## Usage
After completing the [installation instructions](#installation), just execute
the `zoomino.py` script:
```shell
zoomino.py
```
If everything is set up correctly, it will by default show the status of your
user, i.e., something like this:
```
name:     Michael Schlottke-Lakemper
email:    michael@example.com
type:     Basic
```
There are two user types supported: *Basic* users with a free license
and *Licensed* users with a paid license.

Zoomino provides several commands:
* [**show**](#command-show): Show information about a single user (default: yourself).
* [**list**](#command-list): List all users in the Zoom account.
* [**assign**](#command-assign): Assign a license to another user (default: to yourself).
* [**unassign**](#command-unassign): Release the license currently assigned to a user (default: from yourself).
* [**list-meetings**](#command-list-meetings): List all upcoming and recurring meetings.

### Command `show`
Show basic information on a user, i.e., their name, email address, and license
type. By default, information about oneself is shown (useful to check if one is
is already assigned a paid license). Optionally, another user's information can
be shown by giving their email as a second positional argument, e.g.,
```shell
zoomino.py show walter@example.com
```
which gives you an output similar to the following:
```
name:     Walter White
email:    walter@example.com
type:     Licensed
```

### Command `list`
List basic information for all users in the account by executing
```shell
zoomino.py list
```

### Command `assign`
Assign a paid license to a given user. By default, a license is assigned to
yourself, i.e., the user identified by the email address in the credentials
file. Optionally, you can also specify a user who should be assigned a license
by providing their email address as a second positional argument, e.g.,
```shell
zoomino.py assign walter@example.com
```
If no license is currently unassigned, you also need to specify from which
user you want to transfer the license. For example, to transfer the license from
`michael@example.com` to `walter@example.com`, execute
```bash
zoomino.py --from michael@example.com assign walter@example.com
```
Upon success, the basic information of the user with the newly assigned license
will be shown:
```
name:     Walter White
email:    walter@example.com
type:     Licensed
```

### Command `unassign`
Release the paid license currently assigned to a given user. By default, the
license is released from yourself, i.e., the user identified by the email
address in the credentials file. Optionally, you can also specify a user whose
license should be released by providing their email address as a second
positional argument, e.g.,
```shell
zoomino.py unassign walter@example.com
```
Upon success, the basic information of the user with the removed license
will be shown:
```
name:     Walter White
email:    walter@example.com
type:     Basic
```

### Command `list-meetings`
List basic information for all *upcoming* meetings in the account by executing
```shell
zoomino.py list-meetings
```
This will show the meetings for *all users* in ascending order, e.g.,
```
topic:    Test-Meeting
start:    2022-04-28T08:00:00Z
duration: 01:00h
user:     Walter White (walter@example.com, 123456, Basic)
url:      https://us06web.zoom.us/j/12345678901?pwd=12345678901234567890123456789012

topic:    Indefinitely
start:    Recurring meeting
duration: -
user:     Walter White (walter@example.com, 123456, Basic)
url:      https://us06web.zoom.us/j/23456789012?pwd=23456789012345678901234567890123
```
Meetings without starting time (e.g., recurring meetings without fixed time)
will be listed last. The meeting information also contains information on the user who
created the meeting, including their email address and current
license type.


## Installation

Zoomino requires at least Python 3.6 and uses the Zoomus and PyJWT packages,
which can be installed via `pip3` using
```shell
pip3 install zoomus PyJWT
```
On some systems, PyJWT is installed with an older version, even though Zoomus requires
at least v2.0.0 to work correctly. Zoomino will try to detect an older version
and warn you about it; in this case, you can upgrade your PyJWT package to the
latest version by executing
```shell
pip3 install --upgrade PyJWT
```

Next, create a credentials file with the Zoom API key and secret, which you
can obtain by creating a JWT Zoom app following the instructions
[here](https://devforum.zoom.us/t/finding-your-api-key-secret-credentials-in-marketplace/3471).
Create a file named `.zoomino_credentials.json` in your home directory with the following content
```json
{"API_KEY": "YOUR_API_KEY", "API_SECRET": "YOUR_API_SECRET", "USER_EMAIL": "YOUR_EMAIL_ADDRESS"}
```
where you replace `YOUR_API_KEY` and `YOUR_API_SECRET` with the actual key and
secret, respectively, and `YOUR_EMAIL_ADDRESS` with the email address of
**your personal Zoom account**.

Finally, get the `zoomino.py` file, e.g., by cloning this repository
```shell
git clone git@github.com:hlrs-tasc/zoomino.git
```
or use `curl`
```shell
curl -JLO https://github.com/hlrs-tasc/zoomino/raw/main/zoomino.py
```
and put the file somewhere on your `PATH`.


## Authors
Zoomino was initiated by
[Michael Schlottke-Lakemper](https://www.hlrs.de/people/michael-schlottke-lakemper)
and is based on ideas in a previous implementation by
[Oleksandr Shcherbakov](https://www.hlrs.de/people/oleksandr-shcherbakov)
(both from HLRS, University of Stuttgart).


## License
Zoomino is licensed under the MIT license (see [LICENSE](LICENSE)).


## Disclaimer

Everything is provided as is and without warranty. Use at your own risk!
